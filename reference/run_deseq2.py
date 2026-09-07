"""Reference DE: pydeseq2 on GSE202768 Hs578 KD_DOX (n=3) vs KD_noDOX (n=3).
Design: ~group_dev. Contrast: KD_DOX vs KD_noDOX (DOX-induced PRRX1 knockdown effect).
Outputs: reference/outputs/GSE202768/de_results.csv + qc_summary.json
"""
import json
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.expression import load_GSE202768_dev_subset, assert_is_counts
from tools.validation import validate_metadata, validate_groups

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "reference", "outputs", "GSE202768")
os.makedirs(OUT, exist_ok=True)
PADJ = 0.05

def main():
    t0 = time.time()
    counts_sub, meta_sub = load_GSE202768_dev_subset()
    assert_is_counts(counts_sub, "GSE202768 dev counts")
    ok, errs, warns = validate_metadata(meta_sub, required=("group_dev",), sample_ids=list(counts_sub.columns))
    if not ok:
        raise SystemExit(f"metadata invalid: {errs}")
    ok2, e2, w2 = validate_groups(meta_sub, "group_dev", "KD_DOX", "KD_noDOX")
    if not ok2:
        raise SystemExit(f"groups invalid: {e2}")

    # pydeseq2 wants samples x genes counts + metadata with design column
    counts_t = counts_sub.T  # samples x genes
    # low-count filter: keep genes with total >= 10
    keep = counts_t.sum(axis=0) >= 10
    print(f"genes: {counts_t.shape[1]} -> {int(keep.sum())} after low-count filter (>=10)")
    counts_f = counts_t.loc[:, keep]
    metadata = meta_sub.loc[counts_f.index, ["group_dev"]].copy()
    metadata["group_dev"] = metadata["group_dev"].astype(str)

    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats

    dds = DeseqDataSet(counts=counts_f, metadata=metadata, design="~group_dev",
                       refit_cooks=True, n_cpus=4)
    dds.deseq2()
    stat_res = DeseqStats(dds, contrast=("group_dev", "KD_DOX", "KD_noDOX"))
    stat_res.summary()
    res = stat_res.results_df.copy()
    res.index.name = "gene"
    res = res.reset_index().sort_values("padj")
    res.to_csv(os.path.join(OUT, "de_results.csv"), index=False)

    sig = res[res["padj"] < PADJ]
    up = sig[sig["log2FoldChange"] > 0]
    dn = sig[sig["log2FoldChange"] < 0]
    top = res.head(10)[["gene", "log2FoldChange", "pvalue", "padj"]].to_dict("records")
    qc = {
        "dataset": "GSE202768",
        "contrast": "KD_DOX (n=3) vs KD_noDOX (n=3), Hs578 only, design ~group_dev",
        "genes_total": int(counts_sub.shape[0]),
        "genes_tested": int(len(res)),
        "padj_threshold": PADJ,
        "n_sig": int(len(sig)),
        "n_up": int(len(up)),
        "n_down": int(len(dn)),
        "top10": top,
        "runtime_s": round(time.time() - t0, 1),
        "pipeline": "pydeseq2 0.5.4 (Python DESeq2 port)",
    }
    with open(os.path.join(OUT, "qc_summary.json"), "w") as fh:
        json.dump(qc, fh, indent=2)
    print(json.dumps({k: v for k, v in qc.items() if k != "top10"}, indent=2))
    print("top10:")
    for r in top:
        print(f"  {r['gene']}: log2FC={r['log2FoldChange']:.2f} padj={r['padj']:.2e}")

if __name__ == "__main__":
    main()
