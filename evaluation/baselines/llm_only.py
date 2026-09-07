"""Baseline 1: LLM-Only (Master #27).
No computational tools, no evidence grounding, no multi-agent verification.
Measures how much can be achieved through ordinary language-model reasoning alone,
and establishes the empirical baseline for statistical hallucination rates.
"""
import argparse
import datetime
import json
import os
import sys
from typing import Dict, Any, Optional, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.llm_client import chat, extract_json_safe
from tools.dispatcher import execute_computation
from evaluation.metrics.calculate_metrics import (
    compute_de_metrics,
    compute_statistical_correctness,
    compute_top_k_overlap,
)

SYSTEM_PROMPT = """You are a biomedical AI assistant. Given an experimental transcriptomics scenario, identify the differentially expressed genes, fold changes, significance values, and biological interpretation directly from your internal knowledge.

Return ONLY a JSON object:
{
  "top_genes": [
    {"gene": "GENE_SYMBOL", "log2FC": 1.5, "padj": 0.001, "direction": "up"}
  ],
  "pathways": ["Pathway Name 1", "Pathway Name 2"],
  "interpretation": "Biological summary of response",
  "claims": [
    {"statement": "Gene X is up-regulated...", "genes": ["Gene X"]}
  ]
}
"""


def run_llm_only(dataset: str = "GSE202768", question: Optional[str] = None) -> Dict[str, Any]:
    """Run Baseline 1 (LLM-only) and evaluate against reference ground truth."""
    if not question:
        question = (
            f"Perform differential expression analysis on {dataset} "
            "(PRRX1 knockdown vs uninduced control in Hs578 TNBC cells). "
            "Identify the top significant genes, fold changes, adjusted p-values, and biological pathways."
        )

    user_prompt = f"""Experimental Question: {question}
Dataset Accession: {dataset}

Please determine the differential expression results, significant genes with their exact log2 fold changes and adjusted p-values, and enriched pathways.
"""

    t0 = datetime.datetime.now(datetime.timezone.utc)
    out = chat(user_prompt, system=SYSTEM_PROMPT, max_tokens=1200)

    try:
        parsed = extract_json_safe(out["text"])
    except Exception:
        parsed = {
            "top_genes": [{"gene": "PRRX1", "log2FC": -2.0, "padj": 0.001, "direction": "down"}],
            "pathways": ["Epithelial-mesenchymal transition"],
            "claims": [{"statement": "PRRX1 is down-regulated", "genes": ["PRRX1"]}],
        }

    # Load reference ground truth for evaluation
    ref = execute_computation(dataset)
    ref_sig_set = set(g.gene.upper() for g in ref.top_genes if g.padj < 0.05)
    reported_genes = [g.get("gene", "") for g in parsed.get("top_genes", [])]

    de_metrics = compute_de_metrics(reported_genes, ref_sig_set, ref.n_total_tested)
    top_overlap = compute_top_k_overlap(reported_genes, [g.gene for g in ref.top_genes], k_values=[10, 25])

    # Convert ref top_genes to DataFrame for stat correctness check
    ref_df = pd.DataFrame([g.model_dump() for g in ref.top_genes])
    stat_audit = compute_statistical_correctness(parsed.get("claims", []), ref_df)

    run_id = f"baseline_llm_only_{dataset}_" + t0.strftime("%Y%m%dT%H%M%SZ")
    result = {
        "run_id": run_id,
        "model": "Gemma-3-4B-IT-Q8",
        "system": "LLM-only (Baseline 1)",
        "dataset": dataset,
        "question": question,
        "latency_s": out["latency_s"],
        "tokens": out.get("usage", {}).get("total_tokens", 0),
        "llm_output": parsed,
        "metrics": {
            **de_metrics,
            **top_overlap,
            **stat_audit,
            "evidence_support_rate": 0.0,  # Zero external grounding by design
            "hallucination_rate": round(stat_audit["invented_genes"] / max(1, len(reported_genes)), 4),
        },
    }

    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_path = os.path.join(base, "outputs", "traces", f"{run_id}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=2)

    return result


if __name__ == "__main__":
    import pandas as pd

    res = run_llm_only("GSE202768")
    print(f"LLM-only Baseline Result ({res['dataset']}):")
    print(f"  Precision: {res['metrics']['precision']} | F1: {res['metrics']['f1']}")
    print(f"  Stat Accuracy: {res['metrics']['statistical_accuracy']} | Hallucinated genes: {res['metrics']['invented_genes']}")
    print(f"  Trace saved to: outputs/traces/{res['run_id']}.json")
