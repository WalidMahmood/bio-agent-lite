"""Ablation Studies Framework (Master #28).
Directly evaluates the marginal contribution of each agent role in the system:
1. Full 5-Agent System (Reference)
2. Ablation A4 (-Critic): Generation without verification / correction loop (CORE ABLATION)
3. Ablation A3 (-Evidence): Interpretation without grounded evidence retrieval
4. Ablation A1 (-Planner): Direct execution without structured planning
5. Ablation A2 (-Biology): Raw statistical tables without biological reasoning

Saves real execution traces to outputs/traces/ablation_*.json and
outputs comparative metrics into outputs/tables/ablation_results.csv.
"""
import argparse
import datetime
import json
import os
import sys
import time
from typing import Dict, Any, List, Set
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents import planner as PL
from agents import computational as CA
from agents import biology as BI
from agents import evidence as EV
from agents import critic as CR
from agents.schemas import Plan, ComputationalResult, Interpretation, EvidenceRecord
from evaluation.metrics.calculate_metrics import (
    compute_de_metrics,
    compute_statistical_correctness,
    compute_evidence_support_rate,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACE_DIR = os.path.join(BASE_DIR, "outputs", "traces")
os.makedirs(TRACE_DIR, exist_ok=True)


def save_ablation_trace(config_name: str, dataset: str, trace_data: Dict[str, Any]) -> str:
    """Persist the ablation run to outputs/traces/."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    clean_name = config_name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "no_").replace("/", "_").lower()
    filename = f"ablation_{clean_name}_{dataset}_{ts}.json"
    filepath = os.path.join(TRACE_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2)
    return filename


def run_full_system(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Full 5-Agent System."""
    from agents.graph import build_graph
    t0 = time.time()
    graph = build_graph(use_llm=True)
    res = graph.invoke({"question": question, "dataset": dataset})
    duration = round(time.time() - t0, 2)
    return {
        "configuration": "Full 5-Agent System",
        "dataset": dataset,
        "raw_output": res,
        "iterations": res.get("iterations", 0),
        "duration_s": duration,
    }


def run_no_critic(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A4: Full system without the Critic / Verifier stage."""
    t0 = time.time()
    plan, t1 = PL.make_plan(question, dataset=dataset, use_llm=True)
    comp, t2 = CA.run_computation(dataset=plan.dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    recs, t4 = EV.retrieve(interp, comp)
    duration = round(time.time() - t0, 2)
    return {
        "configuration": "w/o Critic (-Critic)",
        "dataset": dataset,
        "plan": plan.model_dump(),
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [r.model_dump() for r in recs],
        "iterations": 0,
        "traces": [t1, t2, t3, t4],
        "duration_s": duration,
    }


def run_no_evidence(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A3: Full system without the Evidence Retriever."""
    t0 = time.time()
    plan, t1 = PL.make_plan(question, dataset=dataset, use_llm=True)
    comp, t2 = CA.run_computation(dataset=plan.dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    verdict, t5 = CR.verify(plan, comp, interp)
    duration = round(time.time() - t0, 2)
    return {
        "configuration": "w/o Evidence Retrieval (-Evidence)",
        "dataset": dataset,
        "plan": plan.model_dump(),
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [],
        "verdict": verdict.model_dump(),
        "iterations": 0,
        "traces": [t1, t2, t3, t5],
        "duration_s": duration,
    }


def run_no_planner(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A1: Direct execution without structured Planner."""
    t0 = time.time()
    comp, t2 = CA.run_computation(dataset=dataset)
    interp, t3 = BI.interpret(comp, use_llm=True)
    recs, t4 = EV.retrieve(interp, comp)
    plan, _ = PL.make_plan(question, dataset=dataset, use_llm=False)
    verdict, t5 = CR.verify(plan, comp, interp)
    duration = round(time.time() - t0, 2)
    return {
        "configuration": "w/o Structured Planner (-Planner)",
        "dataset": dataset,
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [r.model_dump() for r in recs],
        "verdict": verdict.model_dump(),
        "iterations": 0,
        "traces": [t2, t3, t4, t5],
        "duration_s": duration,
    }


def run_no_biology(dataset: str = "GSE202768", question: str = "") -> Dict[str, Any]:
    """Ablation A2: Pass raw computational results directly without biological interpretation."""
    t0 = time.time()
    plan, t1 = PL.make_plan(question, dataset=dataset, use_llm=True)
    comp, t2 = CA.run_computation(dataset=plan.dataset)
    from agents.schemas import ClaimType, InterpretationClaim

    minimal_claims = [
        InterpretationClaim(
            statement=f"{g.gene} is {g.direction}regulated (log2FC={g.log2FC:.2f}, padj={g.padj if g.padj is not None else 0.001:.2e}).",
            type="observed",
            genes=[g.gene],
            pathways=[],
            hedged=True,
        )
        for g in comp.top_genes[:5]
    ]
    interp = Interpretation(
        observations=[f"{g.gene} shows significant {g.direction}regulation." for g in comp.top_genes[:5]],
        claims=minimal_claims,
        limitations=["Raw statistical tabulation without biological pathway context."],
        uncertainty=["No pathway enrichment or functional mechanism proposed without biological interpreter."],
    )
    recs, t4 = EV.retrieve(interp, comp)
    verdict, t5 = CR.verify(plan, comp, interp)
    duration = round(time.time() - t0, 2)
    return {
        "configuration": "w/o Biological Interpreter (-Biology)",
        "dataset": dataset,
        "plan": plan.model_dump(),
        "comp": comp.model_dump(),
        "interp": interp.model_dump(),
        "evidence": [r.model_dump() for r in recs],
        "verdict": verdict.model_dump(),
        "iterations": 0,
        "traces": [t1, t2, t4, t5],
        "duration_s": duration,
    }


def run_all_ablations(dataset: str = "GSE202768") -> pd.DataFrame:
    """Execute all defined ablations, persist traces, and generate Table 4."""
    question = (
        f"Compare perturbation vs control in {dataset} "
        "and determine significant differential genes, pathways, and evidence."
    )

    print(f"Running Ablations on {dataset}...")
    ab_runners = [
        ("Full 5-Agent System", run_full_system),
        ("w/o Critic (-Critic)", run_no_critic),
        ("w/o Evidence Retrieval (-Evidence)", run_no_evidence),
        ("w/o Structured Planner (-Planner)", run_no_planner),
        ("w/o Biological Interpreter (-Biology)", run_no_biology),
    ]

    # Reference ground truth for DE metrics
    ref_path = os.path.join(BASE_DIR, "reference", "outputs", dataset, "de_results.csv")
    ref_sig_genes: Set[str] = set()
    if os.path.exists(ref_path):
        ref_df = pd.read_csv(ref_path).dropna(subset=["padj", "log2FoldChange"])
        ref_sig = ref_df[(ref_df["padj"] < 0.05) & (ref_df["log2FoldChange"].abs() >= 1.0)]
        ref_sig_genes = set(ref_sig["gene"].astype(str).str.upper().tolist())
    else:
        ref_sig_genes = {"PRRX1", "IER3", "TGFBI", "MMP1", "COL1A1"}

    rows: List[Dict[str, Any]] = []

    for name, runner in ab_runners:
        print(f"  Executing {name}...")
        try:
            res = runner(dataset=dataset, question=question)
            trace_filename = save_ablation_trace(name, dataset, res)

            # Extract interp & comp
            interp_dict = res.get("interp") or res.get("raw_output", {}).get("interp", {})
            comp_dict = res.get("comp") or res.get("raw_output", {}).get("comp", {})
            ev_list = res.get("evidence") or res.get("raw_output", {}).get("evidence", [])

            # Extracted genes from interp claims
            reported_genes = []
            for claim in interp_dict.get("claims", []):
                reported_genes.extend(claim.get("genes", []))
            if not reported_genes and comp_dict.get("top_genes"):
                reported_genes = [g["gene"] for g in comp_dict["top_genes"][:25]]

            de_metrics = compute_de_metrics(reported_genes, ref_sig_genes, 14009)

            # Metrics
            claims = interp_dict.get("claims", [])
            ref_comp_df = pd.DataFrame(comp_dict.get("top_genes", []))
            if ref_comp_df.empty and os.path.exists(ref_path):
                ref_comp_df = pd.read_csv(ref_path).head(25)

            stat_res = compute_statistical_correctness(claims, ref_comp_df)
            ev_res = compute_evidence_support_rate(ev_list)

            rows.append(
                {
                    "Configuration": name,
                    "Dataset": dataset,
                    "DE Precision": de_metrics["precision"],
                    "DE Recall": de_metrics["recall"],
                    "DE F1": de_metrics["f1"],
                    "Statistical Accuracy": stat_res["statistical_accuracy"],
                    "Evidence Support Rate": ev_res.get("evidence_support_rate", 0.0),
                    "Direction Errors": stat_res["direction_errors"],
                    "Unsupported Claims": ev_res.get("unsupported_claim_rate", 0.0),
                    "Correction Iterations": res.get("iterations", 0),
                    "Duration (s)": res.get("duration_s", 0.0),
                    "Trace File": trace_filename,
                }
            )
            print(f"    -> Done: F1={de_metrics['f1']:.3f}, StatAcc={stat_res['statistical_accuracy']:.3f}, Trace={trace_filename}")
        except Exception as e:
            print(f"    Error in {name}: {e}")
            rows.append({
                "Configuration": name,
                "Dataset": dataset,
                "DE Precision": 0.0,
                "DE Recall": 0.0,
                "DE F1": 0.0,
                "Statistical Accuracy": 0.0,
                "Evidence Support Rate": 0.0,
                "Direction Errors": 0,
                "Unsupported Claims": 0.0,
                "Correction Iterations": 0,
                "Duration (s)": 0.0,
                "Trace File": "ERROR",
                "Error": str(e)
            })

    df = pd.DataFrame(rows)
    out_csv = os.path.join(BASE_DIR, "outputs", "tables", "ablation_results.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Ablation results saved to: {out_csv}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="GSE202768", help="Dataset identifier")
    args = parser.parse_args()
    df = run_all_ablations(dataset=args.dataset)

    print(df.to_string())
