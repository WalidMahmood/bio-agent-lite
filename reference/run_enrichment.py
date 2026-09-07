"""Enrichment via gseapy Enrichr (human, Hs578). Gene list: padj<0.05 & |log2FC|>=1.
Outputs: reference/outputs/GSE202768/enrichment_*.csv
"""
import os
import sys
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "reference", "outputs", "GSE202768")

def main():
    de = pd.read_csv(os.path.join(OUT, "de_results.csv"))
    sig = de[(de["padj"] < 0.05) & (de["log2FoldChange"].abs() >= 1.0)].copy()
    print(f"sig genes for enrichment: {len(sig)} (|LFC|>=1, padj<0.05)")
    genes = sig["gene"].tolist()
    import gseapy as gp
    for lib in ["GO_Biological_Process_2023", "Reactome_2022", "KEGG_2021_Human"]:
        try:
            en = gp.enrichr(gene_list=genes, gene_sets=lib, organism="human",
                            outdir=os.path.join(OUT, "enrich_tmp"), cutoff=0.05)
            df = en.results.copy()
            df = df.sort_values("Adjusted P-value")
            tag = lib.split("_")[0]
            df.to_csv(os.path.join(OUT, f"enrichment_{tag}.csv"), index=False)
            print(f"== {lib}: {len(df)} terms, top3:")
            for _, r in df.head(3).iterrows():
                print(f"  {r['Term']}: adjP={r['Adjusted P-value']:.2e} overlap={r['Overlap']}")
        except Exception as e:
            print(f"FAIL {lib}: {e}")

if __name__ == "__main__":
    main()
