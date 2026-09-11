"""Evaluation metrics calculator (Master Plan #29-32).
Computes quantitative benchmark metrics across agent and baseline runs:
- Level 1 & 2: Differential expression precision, recall, F1 against reference ground truth
- Level 2: Top-K gene overlap (K = 10, 25, 50)
- Level 2: Statistical correctness (padj significance, direction of fold-change)
- Level 3: Pathway overlap and FDR concordance
- Level 4: Evidence Support Rate (proportion of factual claims grounded in evidence)
- Level 5: Hallucination rate (invented genes, fabricated statistics, uncredited pathways)
"""
from typing import Dict, List, Set, Any, Optional
import numpy as np
import pandas as pd


def compute_de_metrics(
    reported_genes: List[str],
    reference_sig_genes: Set[str],
    total_genes_tested: int,
) -> Dict[str, float]:
    """Calculate Precision, Recall, and F1 for reported significant genes vs reference."""
    reported_set = set(g.strip().upper() for g in reported_genes)
    ref_set = set(g.strip().upper() for g in reference_sig_genes)

    tp = len(reported_set.intersection(ref_set))
    fp = len(reported_set - ref_set)
    fn = len(ref_set - reported_set)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }


def compute_top_k_overlap(
    reported_top_genes: List[str],
    reference_top_genes: List[str],
    k_values: List[int] = [10, 25, 50],
) -> Dict[str, float]:
    """Calculate Jaccard overlap between reported and reference top-K ranked genes."""
    overlaps = {}
    rep_clean = [g.strip().upper() for g in reported_top_genes]
    ref_clean = [g.strip().upper() for g in reference_top_genes]

    for k in k_values:
        rep_k = set(rep_clean[:k])
        ref_k = set(ref_clean[:k])
        intersection = len(rep_k.intersection(ref_k))
        union = len(rep_k.union(ref_k))
        jaccard = intersection / union if union > 0 else 0.0
        overlaps[f"top_{k}_overlap"] = round(intersection / k if k > 0 else 0.0, 4)
        overlaps[f"top_{k}_jaccard"] = round(jaccard, 4)

    return overlaps


def compute_statistical_correctness(
    claims: List[Dict[str, Any]],
    reference_de_df: pd.DataFrame,
    padj_threshold: float = 0.05,
) -> Dict[str, Any]:
    """Audit statistical statements in claims against computed reference values."""
    de_indexed = reference_de_df.set_index(reference_de_df.columns[0])
    # Normalize index
    de_indexed.index = [str(x).upper() for x in de_indexed.index]

    total_claims = 0
    correct_claims = 0
    padj_errors = 0
    direction_errors = 0
    invented_genes = 0

    for c in claims:
        genes = c.get("genes", [])
        stmt = c.get("statement", "").lower()
        for g in genes:
            g_clean = g.strip().upper()
            total_claims += 1
            if g_clean not in de_indexed.index:
                invented_genes += 1
                continue

            row = de_indexed.loc[g_clean]
            # Handle duplicates
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]

            lfc = float(row["log2FoldChange"]) if "log2FoldChange" in row and pd.notna(row["log2FoldChange"]) else 0.0
            padj_val = row["padj"] if "padj" in row else None
            padj = float(padj_val) if (padj_val is not None and pd.notna(padj_val)) else None

            is_stat_trap = (padj is not None) and (padj >= padj_threshold) and ("significan" in stmt or c.get("type") == "observed")
            if is_stat_trap:
                padj_errors += 1
                continue

            # Direction check
            is_up_claim = "up" in stmt or "increas" in stmt or "elevat" in stmt
            is_down_claim = "down" in stmt or "reduc" in stmt or "decreas" in stmt

            if is_up_claim and lfc < 0:
                direction_errors += 1
                continue
            if is_down_claim and lfc > 0:
                direction_errors += 1
                continue

            correct_claims += 1

    accuracy = correct_claims / total_claims if total_claims > 0 else 1.0
    return {
        "statistical_accuracy": round(accuracy, 4),
        "total_gene_claims": total_claims,
        "correct_gene_claims": correct_claims,
        "direction_errors": direction_errors,
        "padj_stat_trap_errors": padj_errors,
        "invented_genes": invented_genes,
    }


def compute_evidence_support_rate(
    evidence_records: List[Dict[str, Any]],
) -> Dict[str, float]:
    """Calculate the Evidence Support Rate (Master Plan #31)."""
    if not evidence_records:
        return {
            "evidence_support_rate": 0.0,
            "partially_supported_rate": 0.0,
            "unsupported_claim_rate": 0.0,
            "total_evidence_queries": 0,
        }

    supported = sum(1 for r in evidence_records if float(r.get("relevance", 0.0)) >= 0.7)
    partially_supported = sum(1 for r in evidence_records if 0.0 < float(r.get("relevance", 0.0)) < 0.7)
    unsupported = sum(1 for r in evidence_records if float(r.get("relevance", 0.0)) == 0.0)

    total = len(evidence_records)
    return {
        "evidence_support_rate": round(supported / total, 4),
        "partially_supported_rate": round(partially_supported / total, 4),
        "unsupported_claim_rate": round(unsupported / total, 4),
        "total_evidence_queries": total,
    }
