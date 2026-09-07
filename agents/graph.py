"""LangGraph stateful workflow for BioAgent-Lite (Master #9, #10-17).
Sequential execution: Planner -> Computational -> Biology -> Evidence -> Critic -> PASS/CORRECT.
Bounded correction loop (max 2 iterations).
Preserves full trajectory trace for Master #35 evaluation.
"""
import copy
import operator
import os
import sys
from typing import Any, Dict, List
from typing_extensions import Annotated, TypedDict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langgraph.graph import StateGraph, END

from agents import planner as PL
from agents import computational as CA
from agents import biology as BI
from agents import evidence as EV
from agents import critic as CR
from agents.schemas import Plan, ComputationalResult, Interpretation, CriticVerdict

MAX_CORRECTIONS = 2


class BioState(TypedDict, total=False):
    question: str
    dataset: str
    plan: dict
    comp: dict
    interp: dict
    evidence: list
    verdict: dict
    traces: Annotated[list, operator.add]
    iterations: int


def _apply_correction(state: BioState) -> dict:
    """Apply targeted critic corrections to claims: remove error-flagged genes and hedge strong assertions."""
    verdict = state["verdict"]
    interp = copy.deepcopy(state["interp"])

    # Collect bad genes identified in errors
    bad_genes = set()
    for err in verdict.get("errors", []):
        tokens = err.split()
        if tokens:
            candidate = tokens[0].strip(":.,")
            if candidate.isupper() or "_" in candidate:
                bad_genes.add(candidate)

    # Filter bad genes out of claims
    for claim in interp.get("claims", []):
        claim["genes"] = [g for g in claim.get("genes", []) if g not in bad_genes]

        # Hedge unscientific certainty words
        stmt = claim.get("statement", "")
        for word in ["proves", "proven", "definitively demonstrates", "certainly causes"]:
            if word in stmt.lower():
                claim["statement"] = stmt.replace(word, "is consistent with the observation that").replace(
                    word.capitalize(), "Is consistent with the observation that"
                )
                claim["hedged"] = True

    return interp


def build_graph(use_llm: bool = True):
    g = StateGraph(BioState)

    def n_planner(state: BioState):
        ds = state.get("dataset", "auto")
        plan, t = PL.make_plan(state["question"], dataset=ds, use_llm=use_llm)
        return {"plan": plan.model_dump(), "traces": [t]}

    def n_compute(state: BioState):
        plan_dict = state["plan"]
        ds = plan_dict.get("dataset", "GSE202768")
        comp = plan_dict.get("comparison", {})
        contrast_str = f"{comp.get('group_a', 'treatment')} vs {comp.get('group_b', 'control')}"
        comp_res, t = CA.run_computation(dataset=ds, contrast=contrast_str)
        return {"comp": comp_res.model_dump(), "traces": [t]}

    def n_biology(state: BioState):
        comp_res = ComputationalResult(**state["comp"])
        interp, t = BI.interpret(comp_res, use_llm=use_llm)
        return {"interp": interp.model_dump(), "traces": [t]}

    def n_evidence(state: BioState):
        interp = Interpretation(**state["interp"])
        comp_res = ComputationalResult(**state["comp"])
        recs, t = EV.retrieve(interp, comp_res)
        return {"evidence": [r.model_dump() for r in recs], "traces": [t]}

    def n_critic(state: BioState):
        plan = Plan(**state["plan"])
        comp_res = ComputationalResult(**state["comp"])
        interp = Interpretation(**state["interp"])
        verdict, t = CR.verify(plan, comp_res, interp)

        t = dict(t)
        t["verdict_snapshot"] = verdict.model_dump()
        t["iteration"] = state.get("iterations", 0)
        return {"verdict": verdict.model_dump(), "traces": [t]}

    def n_correct(state: BioState):
        interp = _apply_correction(state)
        current_iter = state.get("iterations", 0)
        return {"interp": interp, "iterations": current_iter + 1}

    def route_condition(state: BioState):
        if state["verdict"]["status"] == "PASS":
            return "pass"
        if state.get("iterations", 0) >= MAX_CORRECTIONS:
            return "giveup"
        return "correct"

    g.add_node("planner", n_planner)
    g.add_node("compute", n_compute)
    g.add_node("biology", n_biology)
    g.add_node("evidence", n_evidence)
    g.add_node("critic", n_critic)
    g.add_node("correct", n_correct)

    g.set_entry_point("planner")
    g.add_edge("planner", "compute")
    g.add_edge("compute", "biology")
    g.add_edge("biology", "evidence")
    g.add_edge("evidence", "critic")
    g.add_conditional_edges(
        "critic",
        route_condition,
        {"pass": END, "giveup": END, "correct": "correct"},
    )
    g.add_edge("correct", "evidence")

    return g.compile()
