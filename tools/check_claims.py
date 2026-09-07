"""Ad-hoc verification of dev-run claims against reference tables."""
import pandas as pd

de = pd.read_csv("reference/outputs/GSE202768/de_results.csv").set_index("gene")
for g in ["MME", "VAT1L", "PRRX1", "SPARC", "SEPW1", "BMP1", "TGFBI", "COL1A1"]:
    r = de.loc[g]
    print(g, "log2FC=%.2f" % r["log2FoldChange"], "padj=%.1e" % r["padj"])

print("--- interferon in enrichment? ---")
for f in ["enrichment_GO.csv", "enrichment_Reactome.csv", "enrichment_KEGG.csv"]:
    df = pd.read_csv("reference/outputs/GSE202768/" + f)
    m = df[df["Term"].str.contains("nterferon", case=False, na=False)]
    sig = m[m["Adjusted P-value"] < 0.05]
    print(f, "hits=%d sig=%d" % (len(m), len(sig)))
    for _, r in sig.head(2).iterrows():
        print("   ", r["Term"], "%.1e" % r["Adjusted P-value"])

print("--- cell migration (sig only)? ---")
for f in ["enrichment_GO.csv", "enrichment_Reactome.csv"]:
    df = pd.read_csv("reference/outputs/GSE202768/" + f)
    m = df[df["Term"].str.contains("cell migration", case=False, na=False)]
    sig = m[m["Adjusted P-value"] < 0.05]
    print(f, "hits=%d sig=%d" % (len(m), len(sig)))
    for _, r in sig.head(2).iterrows():
        print("   ", r["Term"], "%.1e" % r["Adjusted P-value"])
