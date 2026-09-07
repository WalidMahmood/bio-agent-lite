"""Dataset loader with strict data-type guard (Master #13).
NEVER feed FPKM into DESeq2. Counts -> pydeseq2; FPKM/CuffDiff -> descriptive only.
"""
import gzip
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_gz_csv(path, index_col=0):
    with gzip.open(path, "rt") as fh:
        return pd.read_csv(fh, index_col=index_col)


def load_GSE202768_counts():
    """Count matrix (genes x 16 samples). Returns (counts_df, metadata_df)."""
    p = os.path.join(BASE, "data", "raw", "GSE202768",
                     "GSE202768_TNBC_Cell_line_PRRX1_KD_RNAseq_Gene_Counts.csv.gz")
    counts = _read_gz_csv(p)
    counts.index.name = "gene"
    meta = pd.read_csv(os.path.join(BASE, "data", "metadata", "GSE202768_metadata.csv"), index_col=0)
    # align columns
    missing = [c for c in counts.columns if c not in meta.index]
    if missing:
        raise ValueError(f"count columns missing from metadata: {missing}")
    return counts, meta


def load_GSE202768_dev_subset():
    """Hs578 KD_DOX (n=3) vs KD_noDOX (n=3). Returns (counts_sub, meta_sub)."""
    counts, meta = load_GSE202768_counts()
    sub = meta[meta["include_dev"] == "yes"]
    counts_sub = counts[sub.index.tolist()]
    # order: KD_DOX first for contrast clarity
    return counts_sub, sub


def load_GSE336903_fpkm():
    """Mouse FPKM matrix. Returns (fpkm_df, meta). data_type=FPKM."""
    p = os.path.join(BASE, "data", "raw", "GSE336903",
                     "GSE336903_Fig7_cell_line_FPKM_matrix_GEO.csv.gz")
    with gzip.open(p, "rt") as fh:
        df = pd.read_csv(fh)
    meta = pd.read_csv(os.path.join(BASE, "data", "metadata", "GSE336903_metadata.csv"), index_col=0)
    return df, meta


def load_GSE113650_cuffdiff():
    """Study CuffDiff result (already computed). Returns df."""
    p = os.path.join(BASE, "data", "raw", "GSE113650",
                     "GSE113650_RNA-seq_BRCA_CellLine_CuffDiff_GEO_submit.txt.gz")
    with gzip.open(p, "rt") as fh:
        df = pd.read_csv(fh, sep="\t")
    return df


def assert_is_counts(df, name="matrix"):
    """Guard: refuse FPKM-like (floats in [0, ~1e5] with decimals) passed as counts."""
    # counts must be non-negative integers (allow int-like floats from CSV)
    vals = df.select_dtypes(include="number").to_numpy().ravel()
    vals = vals[~pd.isna(vals)]
    if len(vals) == 0:
        raise Value(value_error := ValueError(f"{name}: no numeric values"))
    non_integer = (vals % 1 != 0).mean()
    if non_integer > 0.01:
        raise ValueError(
            f"{name}: looks like FPKM/normalized (frac non-integer={non_integer:.2f}). "
            "Refusing to run DESeq2 (Master #13).")
    if (vals < 0).any():
        raise ValueError(f"{name}: negative values - not raw counts")
    return True
