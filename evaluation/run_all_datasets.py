"""Multi-Dataset Generalization Suite (Master Plan #23, RQ6).
Evaluates the BioAgent-Lite multi-agent pipeline across diverse transcriptomic benchmarks:
1. GSE202768 (Development): Perturbation shPRRX1 counts in TNBC (pydeseq2)
2. GSE113650 (External Validation): Cell line TNBC vs non-TNBC (CuffDiff reference)
3. GSE95304 (Held-Out Evaluation): Multi-target perturbation shMyc vs shSCR (FPKM tracking)
Outputs summary into outputs/tables/dataset_generalization.csv.
"""
import datetime
import json
import os
import sys
from typing import Dict, Any, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.graph import build_graph
from tools.dispatcher import execute_computation
from evaluation.metrics.calculate_metrics import (
    compute_de_metrics,
    compute_statistical_correctness,
    compute_evidence_support_rate,
)

DATASET_EXPERIMENTS = [
    {
        "dataset": "GSE202768",
        "question": (
            "Compare DOX-induced PRRX1 knockdown (KD_DOX) against uninduced control (KD_noDOX) "
            "in Hs578 TNBC cells and identify key regulated genes and pathways."
        ),
        "role": "Development",
    },
    {
        "dataset": "GSE113650",
        "question": (
            "Evaluate differential expression comparing triple-negative breast cancer (TNBC) "
            "cell lines against non-TNBC receptor-positive lines and determine enriched pathways."
        ),
        "role": "External Validation",
    },
    {
        "dataset": "GSE95304",
        "question": (
            "Analyze transcriptomic changes upon shMyc oncogenic perturbation compared to "
            "scrambled controls (shSCR) in breast cancer and evaluate cell-cycle effects."
        ),
        "role": "Held-Out Evaluation",
    },
    {
        "dataset": "GSE336903",
        "question": (
            "Perform smoke test validation on mouse mammary perturbation data comparing "
            "treatment against control replicates with Mus musculus annotation."
        ),
        "role": "Smoke Test",
    },
]


def run_generalization_benchmark() -> pd.DataFrame:
    print("Executing Multi-Dataset Generalization Benchmark (RQ6)...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    graph = build_graph(use_llm=True)

    rows: List[Dict[str, Any]] = []

    for exp in DATASET_EXPERIMENTS:
        ds = exp["dataset"]
        q = exp["question"]
        role = exp["role"]
        print(f"\n--- Running {ds} ({role}) on GPU ---")

        t0 = datetime.datetime.now(datetime.timezone.utc)
        final = graph.invoke({"question": q, "dataset": ds})
        t1 = datetime.datetime.now(datetime.timezone.utc)
        duration_s = (t1 - t0).total_seconds()

        # Save actual on-disk trace
        ts = t0.strftime("%Y%m%dT%H%M%SZ")
        trace_path = os.path.join(base_dir, "outputs", "traces", f"eval_{ds}_{ts}.json")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as tf:
            json.dump(final, tf, indent=2, default=str)
        print(f"Saved real execution trace: {trace_path} ({duration_s:.1f}s)")

        comp_dict = final.get("comp", {})
        interp_dict = final.get("interp", {})
        evidence_list = final.get("evidence", [])
        verdict_dict = final.get("verdict", {})

        ref = execute_computation(ds)
        
        # Check if dataset has true padj or is descriptive FPKM
        is_descriptive = ("FPKM" in str(comp_dict.get("data_type", "")) and "no fake" in str(comp_dict.get("data_type", ""))) or (ref.top_genes and ref.top_genes[0].padj is None)

        if is_descriptive:
            de_prec = "N/A (Descriptive FPKM)"
            de_f1 = "N/A (Descriptive FPKM)"
        else:
            ref_sig_set = set(g.gene.upper() for g in ref.top_genes if g.padj is not None and g.padj < 0.05)
            reported_genes = [g["gene"] for g in comp_dict.get("top_genes", [])]
            de_res = compute_de_metrics(reported_genes, ref_sig_set, ref.n_total_tested)
            de_prec = de_res["precision"]
            de_f1 = de_res["f1"]

        ref_df = pd.DataFrame(comp_dict.get("top_genes", []))
        stat_res = compute_statistical_correctness(interp_dict.get("claims", []), ref_df)
        ev_res = compute_evidence_support_rate(evidence_list)

        rows.append(
            {
                "Dataset": ds,
                "Benchmark Role": role,
                "Data Type": comp_dict.get("data_type", "counts"),
                "Genes Tested": comp_dict.get("n_total_tested", 0),
                "Significant Genes": comp_dict.get("n_sig", 0),
                "DE Precision": de_prec,
                "DE F1": de_f1,
                "Statistical Accuracy": stat_res["statistical_accuracy"],
                "Evidence Support Rate": ev_res["evidence_support_rate"],
                "Critic Verdict": verdict_dict.get("status", "PASS"),
                "Iterations": final.get("iterations", 0),
                "Trace File": os.path.basename(trace_path),
            }
        )

    df = pd.DataFrame(rows)
    out_csv = os.path.join(base_dir, "outputs", "tables", "dataset_generalization.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"\nGeneralization results saved to: {out_csv}")
    print(df.to_string())
    return df


if __name__ == "__main__":
    df = run_generalization_benchmark()
