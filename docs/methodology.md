# Methodology (frozen decisions, deviations from Master recorded)

## 1. Reference pipeline: Python instead of R
Master specifies R/Bioconductor DESeq2 + clusterProfiler. This machine has no R
(`Rscript` absent, Windows 11). Installing R + Bioconductor is deferred to conserve
the 5-day budget. P0 reference uses:
- `pydeseq2 0.5.4` (Python DESeq2 port, NB Wald test, Cooks refit) — same statistical
  framework (negative-binomial, design `~group`, contrast, BH padj).
- `gseapy 1.3.1 enrichr` (GO_Biological_Process_2023, Reactome_2022, KEGG_2021_Human).
R path remains documented for final reproducibility package; all P0 metrics come from
the Python pipeline and are labeled as such (never claimed as R output).

## 2. Data-type rule enforced (Master #13)
`tools/expression.py::assert_is_counts` refuses non-integer matrices for DESeq2.
- GSE202768: counts available -> pydeseq2 eligible.
- GSE336903: FPKM only -> descriptive only, never DESeq2.
- GSE95304: fpkm_tracking only -> descriptive only.
- GSE113650: CuffDiff study result reused as reference (labeled study result).

## 3. Organism correction: GSE336903 is MOUSE
Master Table 1 implies human throughout, but GSE336903 expression rows are
`ENSMUSG*` / mouse symbols (e.g. 0610005C13Rik). Enrichment for this dataset must
use mouse libraries (or be skipped). Human `org.Hs.eg.db`-equivalent mapping does
NOT apply. Recorded here so the agent is never credited for human pathways on mouse data.

## 4. GSE202768 dev contrast (Hs578 only)
16 samples = 2 parental lines x shRNA x DOX. TT642 is rhabdoid tumor, not breast,
so it is excluded from the breast dev contrast. DOX induces the shRNA knockdown.
- group A `KD_DOX`: Hs578 shPRRX1_{1,2,3} + DOX (n=3)
- group B `KD_noDOX`: Hs578 shPRRX1_{1,2,3} no DOX (n=3)
- design `~group_dev`. Sanity: PRRX1 must be DOWN in A vs B (observed log2FC -2.28,
  padj 1.28e-29 on 2026-09-05 run — knockdown confirmed, direction correct).
- `no_sh` samples reserved for a DOX-effect control (not the primary contrast).

## 5. Thresholds (configs/thresholds.yaml, LLM may not invent)
padj<0.05, |log2FC|>=1.0 for "strong", low-count filter total>=10, enrichment FDR<0.05,
critic max 2 correction iterations.

## 6. Models (configs/models.yaml)
Plan specified Q4 GGUFs; downloaded artifacts are Q8_K_XL (4.81GB each) + Qwen3-8B Q4.
Q8 fits the 8GB RTX 5050 (7GB free observed) but leaves less KV headroom than Q4;
single-LLM-instance lock is mandatory. Embeddings via ollama `nomic-embed-text`
(already local) instead of downloading bge-small.
