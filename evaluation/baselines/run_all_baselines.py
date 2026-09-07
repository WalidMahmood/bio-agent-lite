"""Master Plan Table 3: Architecture Comparison Runner (Master #27, #46).
Compares:
1. LLM-only (Baseline 1): Language model only, no tools, no critic
2. Single-Agent (Baseline 2): Tool-using agent, no role specialization, no critic
3. Full 5-Agent System (BioAgent-Lite): Planner + Computation + Biology + Evidence + Critic
Outputs comparative metrics to outputs/tables/architecture_comparison.csv.
"""
import datetime
import json
import os
import sys
from typing import Dict, Any, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from evaluation.baselines.llm_only import run_llm_only
from evaluation.baselines.single_agent import run_single_agent
from agents.graph import build_graph
from tools.dispatcher import execute_computation
from evaluation.metrics.calculate_metrics import (
    compute_de_metrics,
    compute_statistical_correctness,
    compute_top_k_overlap,
    compute_evidence_support_rate,
)


def run_architecture_comparison(dataset: str = "GSE202768") -> pd.DataFrame:
    print(f"Executing Architecture Comparison on {dataset}...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 1. Baseline 1: LLM-Only
    print("  [1/3] Running LLM-only Baseline...")
    res_llm = run_llm_only(dataset=dataset)

    # 2. Baseline 2: Single Tool-Agent
    print("  [2/3] Running Single Tool-Agent Baseline...")
    res_single = run_single_agent(dataset=dataset)

    # 3. Proposed: Full 5-Agent System
    print("  [3/3] Running Full 5-Agent System...")
    q = (
        f"Perform differential expression analysis on {dataset} "
        "and determine key regulated genes, pathways, and evidence."
    )
    graph = build_graph(use_llm=True)
    t0 = datetime.datetime.now(datetime.timezone.utc)
    final = graph.invoke({"question": q, "dataset": dataset})

    # Evaluate Full System
    comp_dict = final["comp"]
    interp_dict = final["interp"]
    evidence_list = final["evidence"]
    verdict_dict = final["verdict"]

    reported_genes = [g["gene"] for g in comp_dict.get("top_genes", [])]
    ref = execute_computation(dataset)
    ref_sig_set = set(g.gene.upper() for g in ref.top_genes if g.padj < 0.05)

    de_metrics = compute_de_metrics(reported_genes, ref_sig_set, ref.n_total_tested)
    top_overlap = compute_top_k_overlap(reported_genes, [g.gene for g in ref.top_genes], k_values=[10, 25])
    ref_df = pd.DataFrame(comp_dict.get("top_genes", []))
    stat_audit = compute_statistical_correctness(interp_dict.get("claims", []), ref_df)
    ev_metrics = compute_evidence_support_rate(evidence_list)

    res_full = {
        "system": "Full 5-Agent System (BioAgent-Lite)",
        "dataset": dataset,
        "metrics": {
            **de_metrics,
            **top_overlap,
            **stat_audit,
            **ev_metrics,
            "hallucination_rate": round(stat_audit["invented_genes"] / max(1, len(reported_genes)), 4),
        },
        "verdict_status": verdict_dict.get("status", "UNKNOWN"),
        "iterations": final.get("iterations", 0),
    }

    # Assemble comparison rows for Master Plan Table 3
    rows = [
        {
            "System Architecture": "LLM-only (Baseline 1)",
            "Planner": "No",
            "Tools": "No",
            "Biology Role": "Implicit",
            "Evidence Grounding": "No",
            "Critic / Verifier": "No",
            "DE Precision": res_llm["metrics"]["precision"],
            "DE Recall": res_llm["metrics"]["recall"],
            "DE F1": res_llm["metrics"]["f1"],
            "Statistical Accuracy": res_llm["metrics"]["statistical_accuracy"],
            "Evidence Support Rate": res_llm["metrics"]["evidence_support_rate"],
            "Hallucination Rate": res_llm["metrics"]["hallucination_rate"],
        },
        {
            "System Architecture": "Single Tool-Agent (Baseline 2)",
            "Planner": "No",
            "Tools": "Yes",
            "Biology Role": "Implicit",
            "Evidence Grounding": "Partial",
            "Critic / Verifier": "No",
            "DE Precision": res_single["metrics"]["precision"],
            "DE Recall": res_single["metrics"]["recall"],
            "DE F1": res_single["metrics"]["f1"],
            "Statistical Accuracy": res_single["metrics"]["statistical_accuracy"],
            "Evidence Support Rate": res_single["metrics"]["evidence_support_rate"],
            "Hallucination Rate": res_single["metrics"]["hallucination_rate"],
        },
        {
            "System Architecture": "Full 5-Agent (BioAgent-Lite)",
            "Planner": "Yes",
            "Tools": "Yes",
            "Biology Role": "Yes (Specialized)",
            "Evidence Grounding": "Yes (Explicit)",
            "Critic / Verifier": "Yes (Bounded Loop)",
            "DE Precision": res_full["metrics"]["precision"],
            "DE Recall": res_full["metrics"]["recall"],
            "DE F1": res_full["metrics"]["f1"],
            "Statistical Accuracy": res_full["metrics"]["statistical_accuracy"],
            "Evidence Support Rate": res_full["metrics"]["evidence_support_rate"],
            "Hallucination Rate": res_full["metrics"]["hallucination_rate"],
        },
    ]

    df = pd.DataFrame(rows)
    out_csv = os.path.join(base_dir, "outputs", "tables", "architecture_comparison.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"\nArchitecture Comparison Results saved to: {out_csv}")
    print(df.to_string())
    return df


if __name__ == "__main__":
    df = run_architecture_comparison("GSE202768")
