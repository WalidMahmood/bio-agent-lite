"""Metadata + input validation (Master #11, robustness R1-R3).
Returns (ok: bool, errors: list, warnings: list). R1: missing field -> hard fail.
"""
import pandas as pd


def validate_metadata(meta, required=("group_dev",), sample_ids=None):
    errors, warnings = [], []
    for col in required:
        if col not in meta.columns:
            errors.append(f"missing required metadata field: {col} (R1: stop, do not continue)")
    if meta.index.duplicated().any():
        errors.append("duplicated sample identifiers")
    if meta.isna().any().any():
        bad = meta.isna().sum()
        warnings.append(f"missing values: {bad[bad > 0].to_dict()}")
    if sample_ids is not None:
        missing = [s for s in sample_ids if s not in meta.index]
        extra = [s for s in meta.index if s not in sample_ids]
        if missing:
            errors.append(f"expression columns missing from metadata: {missing}")
        if extra:
            warnings.append(f"metadata samples without expression data: {extra}")
    return (len(errors) == 0), errors, warnings


def validate_groups(meta, group_col, group_a, group_b, min_n=2):
    errors, warnings = [], []
    if group_col not in meta.columns:
        return False, [f"group column {group_col} absent (R2: flag comparison)"], []
    groups = meta[group_col]
    for g in (group_a, group_b):
        n = int((groups == g).sum())
        if n < min_n:
            errors.append(f"group {g}: n={n} < min_n={min_n}")
    if group_a == group_b:
        errors.append("group_a == group_b (R2: incorrect comparison)")
    return (len(errors) == 0), errors, warnings


def check_decoy_gene(gene_list, result_genes):
    """R3: decoy/fabricated gene must not be treated as evidence."""
    decoys = [g for g in gene_list if g not in set(result_genes)]
    return decoys


def check_stat_trap(log2fc, padj, padj_thresh=0.05):
    """R4: large |log2FC| but padj>=thresh is NOT significant."""
    return bool(abs(log2fc) >= 1.0 and padj >= padj_thresh)
