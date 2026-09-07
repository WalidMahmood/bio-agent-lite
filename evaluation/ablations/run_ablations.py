"""Ablation Studies Framework (Master #28).
Directly evaluates the marginal contribution of each agent role in the system:
- Full 5-Agent Architecture (Reference)
- Ablation 1 (-Planner): Direct execution without structured planning
- Ablation 3 (-Evidence): Interpretation without grounded evidence retrieval
- Ablation 4 (-Critic): Generation without verification / correction loop (CORE ABLATION)
Outputs comparative metrics into outputs/tables/ablation_results.csv.
"""
import argparse
import datetime
import json
import os
import sys
from typing import Dict, Any, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents import planner as PL
from agents import computational as CA
from agents import biology as BI
from agents import evidence as EV
from agents import critic as CR
from agents.schemas import Plan, ComputationalResult, Interpretation
from evaluation.metrics.calculate_metrics import (
    compute_de_metrics,
    compute_statistical_correctness,
    compute_evidence_support_rate,
)


def run_full_system(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Full 5-Agent System."""
    from agents.graph import build_graph

    graph = build_graph(use_llm=True)
    res = graph.invoke({"question": question, "dataset": dataset})
    return {"configuration": "Full System (5-Agent)", "raw_output": res, "iterations": res.get("iterations", 0)}


def run_no_critic(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A4: Full system without the Critic / Verifier stage."""
    plan, t1 = PL.make_plan(question, dataset=dataset, use_llm=True)
    comp, t2 = CA.run_computation(dataset=plan.dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    recs, t4 = EV.retrieve(interp, comp)
    return {
        "configuration": "Full System - Critic (A4)",
        "plan": plan.model_dump(),
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [r.model_dump() for r in recs],
        "iterations": 0,
    }


def run_no_evidence(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A3: Full system without the Evidence Retriever."""
    plan, t1 = PL.make_plan(question, dataset=dataset, use_llm=True)
    comp, t2 = CA.run_computation(dataset=plan.dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    # Skip retrieval, pass directly to critic
    verdict, t5 = CR.verify(plan, comp, interp)
    return {
        "configuration": "Full System - Evidence (A3)",
        "plan": plan.model_dump(),
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [],
        "verdict": verdict.model_dump(),
        "iterations": 0,
    }


def run_no_planner(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A1: Direct execution without structured Planner."""
    comp, t2 = CA.run_computation(dataset=dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    recs, t4 = EV.retrieve(interp, comp)
    # Default dummy plan for critic
    plan, _ = PL.make_plan(question, dataset=dataset, use_llm=False)
    verdict, t5 = CR.verify(plan, comp, interp)
    return {
        "configuration": "Full System - Planner (A1)",
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [r.model_dump() for r in recs],
        "verdict": verdict.model_dump(),
        "iterations": 0,
    }


def run_all_ablations(dataset: str = "GSE202768") -> pd.DataFrame:
    """Execute all defined ablations and generate Table 4."""
    question = (
        f"Compare perturbation vs control in {dataset} "
        "and determine significant differential genes, pathways, and evidence."
    )

    print(f"Running Ablations on {dataset}...")
    ab_runners = [
        ("Full System", run_full_system),
        ("A4: - Critic", run_no_critic),
        ("A3: - Evidence", run_no_evidence),
        ("A1: - Planner", run_no_planner),
    ]

    rows: List[Dict[str, Any]] = []
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    for name, runner in ab_runners:
        print(f"  Executing {name}...")
        try:
            res = runner(dataset=dataset, question=question)
            # Extract interp & comp
            interp_dict = res.get("interp") or res.get("raw_output", {}).get("interp", {})
            comp_dict = res.get("comp") or res.get("raw_output", {}).get("comp", {})
            ev_list = res.get("evidence") or res.get("raw_output", {}).get("evidence", [])

            # Metrics
            claims = interp_dict.get("claims", [])
            top_genes = [g["gene"] for g in comp_dict.get("top_genes", [])]
            ref_df = pd.DataFrame(comp_dict.get("top_genes", []))

            stat_res = compute_statistical_correctness(claims, ref_df)
            ev_res = compute_evidence_support_rate(ev_list)

            rows.append(
                {
                    "Configuration": name,
                    "Dataset": dataset,
                    "Statistical Accuracy": stat_res["statistical_accuracy"],
                    "Direction Errors": stat_res["direction_errors"],
                    "Stat Trap Errors": stat_res["padj_stat_trap_errors"],
                    "Evidence Support Rate": ev_res.get("evidence_support_rate", 0.0),
                    "Unsupported Claims": ev_res.get("unsupported_claim_rate", 0.0),
                    "Correction Iterations": res.get("iterations", 0),
                }
            )
        except Exception as e:
            print(f"    Error in {name}: {e}")
            rows.append({"Configuration": name, "Dataset": dataset, "Error": str(e)})

    df = pd.DataFrame(rows)
    out_csv = os.path.join(base_dir, "outputs", "tables", "ablation_results.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Ablation results saved to: {out_csv}")
    return df


if __name__ == "__main__":
    df = run_all_ablations("GSE202768")
    print(df.to_string())
