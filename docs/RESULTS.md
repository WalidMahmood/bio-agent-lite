# BioAgent-Lite â€” Complete Experiment Dossier

**What this document is:** the complete inventory of every experiment actually run in this project, with **provenance labels** so any number can be cited correctly. Built so a reviewer, examiner, or future user can move from *headline* â†’ *table* â†’ *trace* â†’ *raw command* without guessing.

## Provenance legend

| Label | Meaning | How to verify |
|---|---|---|
| **MEASURED** | Produced by an actual run that wrote its own trace/log | `outputs/traces/*.json`, `git log` |
| **GENERATED** | Written by a script from programmatic constants (convenience/reporting artifact) | Read the generating script cited per section |
| **REPLAYED** | Web/API serving of a recorded audited run (numbers genuine, latency recorded) | `backend/main.py` routing logic |

---

## 1. Experimental setup

| Item | Value |
|---|---|
| Hardware | NVIDIA RTX 5050 Laptop (8 GB VRAM), 16 GB RAM, Windows 11, **zero cloud APIs** |
| Inference runtime | llama.cpp CUDA 12.4 (`llama-server.exe`, build b10819), OpenAI-compatible endpoint on `127.0.0.1:8080` |
| Primary model | Gemma 3 4B IT â€” Q8_K_XL GGUF, 4.81 GB, ctx 8192, **38.5 tok/s** (peak VRAM 4,919 MB â‰ˆ 60.1% of budget) |
| Comparison models | MedGemma 4B IT Q8_K_XL (32.7 tok/s), Qwen3 8B Q4_K_M (44.7 tok/s) |
| Statistics | PyDESeq2 0.5.4 (NB Wald GLM, BH-FDR) + GSEApy 1.3.1 (GO/Reactome/KEGG), scipy Welch for live uploads â€” LLMs never compute numbers |
| Frozen thresholds | `padj < 0.05`, strong-effect \|log2FC\| â‰¥ 1.0, low-count filter â‰¥ 10, enrichment FDR < 0.05, critic â‰¤ 2 correction iterations (configs/thresholds.yaml, seeds 42) |
| Design | 4 GEO datasets (dev / held-out / external / smoke) Ã— architecture baselines Ã— ablations Ã— robustness suite |

---

## 2. Does role specialization beat simpler systems? (Master Table 3 â€” **MEASURED**)

Source: `evaluation/baselines/run_all_baselines.py` â†’ `outputs/tables/architecture_comparison.csv` (trace-backed: `baseline_llm_only_GSE202768_20260906T181002Z.json` et al.).

| System | DE Precision | DE Recall | DE F1 | Statistical claim accuracy | Evidence Support Rate | Hallucination rate |
|---|---:|---:|---:|---:|---:|---:|
| LLM-only (no tools, no critic) | 0.20 | 0.04 | 0.067 | 0.125 | 0.000 | **1.40** (140%) |
| Single tool-agent | 1.00 | 0.60 | 0.750 | 1.000 | 0.500 | 0.0 |
| **Full 5-agent BioAgent-Lite** | **1.00** | **1.00** | **1.000** | **1.000** | **0.556** | **0.0** |

Key readings (all five-or-six-metric rows measured on the same reference table):

* The **LLM-only baseline hallucinated genes at a rate of 140%** â€” it named 4 fake top-genes for every 5 real ones (7 invented of 8 gene claims in the preserved trace, with fabricated log2FC/padj numbers for `PRRX1/CDK6/MYC/CCND1/GAPDH`). This is the failure mode the whole architecture exists to prevent.
* Tool use alone (single-agent) is already a huge jump (deterministic tools remove arithmetic hallucination, F1 0.75), but **recall is only 0.6** â€” one agent writes summaries that miss much of the true DE panel.
* Specialization + verification closes the gap to **F1 = 1.0 with zero hallucinations**. Note the honest detail: full-system **E**vidence **S**upport **R**ate is **0.556 on GSE202768** (not the 100% the old README claimed) â€” see Â§10 for the cross-run range and why that varies.

---

## 3. Does it generalize to unseen experiments? (**MEASURED**)

Source: `evaluation/run_all_datasets.py` â†’ `outputs/tables/dataset_generalization.csv` â€” the full 5-agent LangGraph invoked live on four datasets with frozen prompts:

| Dataset | Role | Data type | Genes tested | Significant | DE F1 | Statistical accuracy | Evidence support | Critic verdict |
|---|---|---|---:|---:|---|---:|---:|---|
| GSE202768 | Development | counts (PyDESeq2) | 14,009 | 3,946 | 1.0 | 1.0 | 0.579 | PASS (1 iter) |
| GSE113650 | External validation | CuffDiff study reference | 14,817 | 990 | 1.0 | 1.0 | 1.0 | PASS (0 iter) |
| GSE95304 | **Held-out** (never tuned on) | FPKM â€” refusal guard active | 14,387 | 2,063 | N/A (descriptive) | 1.0 | 1.0 | PASS (1 iter) |
| GSE336903 | Smoke | Mouse FPKM | 54,289 | 3,014 | N/A | 1.0 | 1.0 | PASS (0 iter) |

Biological discoveries preserved in the traces and reference outputs:

* **GSE202768 â€” the knockdown experiment.** PRRX1 (mesenchymal repressor) confirmed down: `log2FC âˆ’2.28, padj 1.28e-29`. Top responders: `TGFBI +1.95 (padj 4.7e-37)`, `COL1A1 +2.08 (6.7e-30)`, `COL5A1 +1.21`, `TNC +1.89`; drops: `IGFBP1 âˆ’2.50`, `PDP1 âˆ’1.07`. Enrichment: **Extracellular Matrix Organization** (Reactome adjP **2.2e-07**, overlap 25/291), KEGG ECM-receptor interaction (2.3e-06). Directions coherent: PRRX1 suppression â‡’ matrix/collagen program shifts.
* **GSE113650 â€” TNBC marker validation.** 990 markers discriminate TNBC vs non-TNBC (e.g. `IER3 log2FC 2.43`, padj 2.5e-03); enrichment ECM organization adjP 9.4e-09; study-level markers ESR1/PGR suppressed in TNBC (classic biology reproduced).
* **GSE95304 â€” held-out + guard demo.** FPKM-only data: the pipeline **refused DESeq2 and answered with a ranking of 2,063 genes whose padj is honestly `N/A`** â€” no fabricated p-values per Master Â§13. Perturbation effects preserved (shMyc âˆ’2.15, `SNORD78` +11.05), enrichment run on the descriptive list (KEGG allograft rejection adjP 1.5e-14, HLA cluster).
* **GSE336903 â€” cross-species smoke.** Ensembl-mouse detection active (`ENSMUSG*`), mouse-aware pathway handling, `Mirlet7a-1 +5.54` top mover.

---

## 4. Robustness under adversarial inputs (**MEASURED**)

Source: `evaluation/robustness/run_robustness.py` â†’ `outputs/tables/robustness_results.csv` (deterministic critic/kernel tests):

| Perturbation | What the system did | Detected | Safe completion |
|---|---|---|---|
| R1 missing required metadata | Halted with validation error â€” no unannotated analysis | âœ… | âœ… |
| R2 identical intervention/control groups | Critic flagged the circular comparison â€” FAIL before output | âœ… | âœ… |
| R3 fabricated decoy gene in claims | Flagged as absent/invented gene (correction issued) | âœ… | âœ… |
| R4 statistical trap (big log2FC +3.5, padj 0.31) | Flagged as padj-confusion/statistical trap â€” not sold as significant | âœ… | âœ… |

**4/4 detection, 4/4 safe completion.** (R5 conflicting-evidence / R6 prompt-bloat were specified in the Master Plan but not implemented â€” listed in Â§11 as known scope gaps.)

---

## 5. Live computational validation â€” PDAC gemcitabine (**MEASURED statistics; controlled synthetic data**)

`data/test_datasets/PDAC_gemcitabine_counts.csv` (2,000 genes Ã— 6 samples) is a **seeded synthetic matrix** generated by `scripts/generate_pdac_dataset.py` (seed 42) with 20 curated chemoresistance markers pinned to mathematically known directions â€” used to validate the live engine end-to-end at request time:

* **Real Welch's t-test + Benjamini-Hochberg computed on the fly** (`backend/realtime_engine.py`): 56 significant DEGs (26 up / 30 down) at `padj < 0.05, |log2FC| â‰¥ 0.5`.
* Known markers recovered in the correct directions: `CDA +3.32` (drug-destroying enzyme), `RRM1 +2.88` (drug target amplification), `ABCB1 +3.17` (efflux pump) up; `DCK âˆ’2.78` (prodrug-activation kinase) and `SLC29A1 âˆ’2.45` (nucleoside transporter) down â‡’ a complete, mechanistically coherent resistance fingerprint.
* The adversarial critic narrative caught the draft's DCK direction inversion (iteration-0 FAIL â†’ iteration-1 PASS).
* In this live engine, the **statistics/figures are computed at request time**, while the surrounding narrative, pathway context and literature citations are **pre-baked demo text** (see Â§10 and [EXPLAINABILITY Â§8](EXPLAINABILITY.md)).

---

## 6. Ablations â€” do the roles earn their keep? (**MEASURED, multi-batch**)

Source: `evaluation/ablations/run_ablations.py` â†’ `outputs/tables/ablation_results.csv` (latest batch, 2026-09-07T1007) + 9 ablation traces in `outputs/traces/`.

| Configuration | DE F1 | Statistical accuracy | Evidence Support Rate | Correction iterations | Duration |
|---|---:|---:|---:|---:|---:|
| Full 5-agent | 0.016* | 1.0 | **1.0** | 0 | 4.1 s |
| w/o Critic | 0.016* | 1.0 | 1.0 | 0 | 4.1 s |
| **w/o Evidence Retrieval** | 0.016* | 1.0 | **0.0** | 0 | 4.1 s |
| w/o Planner | 0.016* | 1.0 | 1.0 | 0 | 2.1 s |
| w/o Biology | 0.026* | 1.0 | 1.0 | 0 | 2.1 s |
*F1 in this batch is computed against the |log2FC|â‰¥1.0 strong-reference set, so recall is tiny in all rows â€” the contrast that matters across configurations is **Evidence Support Rate: 1.0 â†’ 0.0 when evidence retrieval is removed**, and the duration/behavior changes.

**Honest multi-batch note (read before citing ablations):** three measurement generations exist and they disagree in detail:
1. **First batch** (traces `20260907T0737â€“38Z`, live LLM): Full ESR 0.667 (10/15), âˆ’Critic 0.70, âˆ’Planner 0.80, with the critic proving value via real catches elsewhere.
2. **Second batch** (traces `20260907T1007Z`, CSV above): LLM fallback used (2â€“4 s durations), so only the âˆ’Evidence contrast (ESR 1.0 â†’ 0.0) is visible.
3. **Report figure** (`ablation_impact_breakdown.png` values 0.625/0.625/0.0/0.714): originates from a hard-coded array in `evaluation/metrics/generate_real_roc_and_ml_plots.py:222` â€” **GENERATED, not measured**.

**Recommendation:** cite `outputs/tables/ablation_results.csv` + first-batch traces (they are the MEASURED numbers). A future run with a live LLM should regenerate the ablation table (one command: `python evaluation\ablations\run_ablations.py --dataset GSE202768`).

---

## 7. Model comparison â€” Gemma vs MedGemma vs Qwen3 (**mixed provenance**)

| Model | Throughput (tok/s) | Peak VRAM (MB) | Schema adherence | Statistical accuracy (with system) | Verdict |
|---|---:|---:|---|---:|---|
| **Gemma 3 4B IT Q8_K_XL** | 38.5 | 4,919 | 100% (zero JSON parse errors) | 100 | **WINNER â€” optimal speed/VRAM/schema trade-off** |
| MedGemma 4B IT Q8_K_XL | 32.7 | 4,919 | 98.2% (1â€“2 repair loops, clinical drift observed) | 95 | Clinical specialist, needs stricter non-clinical guard |
| Qwen3 8B Q4_K_M | 44.7 | 5,120 | 99.1% (requires `/no_think`) | 100 | Faster tokens, highest VRAM, thinking-token overhead |

Provenance split (**be precise when citing**):
* Throughput & VRAM: **MEASURED** in smoke benchmarks (llama.cpp server logs; e.g. 35/35 CUDA layers offloaded, 4,919 MB peak).
* Schema adherence / accuracy / behavioral claims: **GENERATED** from `evaluation/models/compare_models.py` + `evaluate_all_models_datasets.py` constants; only the Gemma full-system rows have direct trace backing (`outputs/traces/eval_GSE*.json`); the MedGemma/Qwen "with system" accuracy rows are asserted replication of the measured schema behavior.
* Naive (without-system) panels across 24 conditions (4 datasets Ã— 3 models Ã— with/without, 50-gene panels): **GENERATED** from per-model naive constants (e.g., Gemma naive F1 0.000â€“0.067 with hallucination rates 95â€“180% across datasets; naive direction errors 25â€“37.5%).

---

## 8. Genome-wide ranking quality (ROC / PR) (**MEASURED with a caveat**)

`roc_auc_curves.png` was computed **empirically from the real 14,009-gene DE table** (ranking score `âˆ’log10(padj) Â· |log2FC|`; N = 12,651 without NaN mask):

| System | ROC-AUC | PR-AUC (no-skill baseline 0.030) |
|---|---:|---:|
| BioAgent-Lite ranking | **0.967** | **0.637** |
| Single tool-agent proxy | 0.774 | 0.344 |
| LLM-only proxy | 0.518 | 0.039 (at chance) |

The demo notebook re-derives the same computation on a slightly different mask (12,651) as **ROC-AUC 0.9798 / PR-AUC 0.6647** â€” i.e. empirical estimates cluster at â‰ˆ0.97/0.65.

âš ï¸ **Known artifact (documented, un-fixed):** `outputs/manifest.json` states `roc_auc: 1.0, pr_auc: 1.0`. Both empirical computations contradict that; the manifest values should not be cited. Treat **0.967â€“0.980 / 0.637â€“0.665** as the defensible figure.

---

## 9. Artifact index (what exists on disk)

| Artifact | Count | Where |
|---|---|---|
| Result tables (CSV) | 10 | `outputs/tables/` |
| Figures (PNG, incl. 4-dataset volcano/pathway pairs, ROC/PR, confusion mats, radar, Pareto frontier, waterfall) | 24 | `outputs/figures/` |
| Agent traces (dev / eval / baseline / ablation) | **27** | `outputs/traces/` |
| Per-dataset PDF lab reports | 5 (+ term report PDFs) | `outputs/reports/`, repo root |
| Reference statistical outputs | 3 datasets | `reference/outputs/` |
| Demonstration notebooks (clean + executed, 44 cells) | 2 | `notebooks/` |
| Reproducibility manifest (JSON) | 1 | `outputs/manifest.json` |

---

## 10. Cross-run metric variance table (the honest summary)

The same quantity measured on different runs/datasets/batches (all real):

| Metric | Range seen | Where each value lives |
|---|---|---|
| Evidence Support Rate (full system, GSE202768) | 0.556 (architecture CSV) Â· 0.579 (generalization CSV) Â· 0.667 (first ablation batch) | each row trace-backed; varies with LLM nondeterminism & claim mix |
| Evidence Support Rate (full system, other 3 datasets) | 1.0 | `dataset_generalization.csv` |
| Hallucination rate (LLM-only baseline, GSE202768) | 1.40 | `architecture_comparison.csv` + trace |
| Hallucination rate (naive panels, per model) | 0.95â€“1.80 | `all_models_4datasets_comparison.csv` (**GENERATED**) |
| ROC-AUC | 0.967 (figure) / 0.980 (notebook) / 1.0 (manifest â€” artifact) | Â§8 |
| Full-system runtime | 24.5 s PyDESeq2 Â· 24.8â€“4.1 s agent runs (LLM vs fallback batch) | traces |
| Peak VRAM | 4,919 MB (60.1% of the 8 GB budget) | server logs + telemetry |

---

## 11. Known discrepancies & scope gaps (the reviewer's checklist)

1. README's earlier "Evidence Grounding 100%" row was an overstatement â€” measured GSE202768 ESR is **0.556 / 0.579** (README updated to cite measured values).
2. Final-report ablation table (Table 4 ESR 0.625/0.714) comes from a hard-coded array, not `ablation_results.csv` (Â§6).
3. `manifest.json` ROC/PR = 1.0 is unsupported by both empirical computations (Â§8).
4. `model_comparison.csv`, `model_systems_tradeoffs.csv`, `resource_usage.csv`, `dataset_summary.csv`, and the naive-panel halves of the 24-condition tables are **GENERATED** (Â§7); trace-level latencies differ (e.g., LLM-only actual 9.44 s / 720 tokens vs table's 12.4 s / 520).
5. Robustness R5 (conflicting evidence) and R6 (context bloat) were designed but **not implemented**; R1â€“R4 are MEASURED.
6. ChromaDB / PubMed / ollama-embedder appear in requirements/config/narrative but have **zero runtime calls** â€” grounding is deterministic claim-to-artifact lineage (see EXPLAINABILITY Â§3/Â§8).
7. `use_critic` API field is accepted but unread (critic always on in traces); `agents/computational.py` ignores tuning kwargs; the web benchmark path replays recorded traces.
8. Only the GSE202768 reference analysis was re-run from `reference/` scripts; the other datasets' reference numbers live in the `data/raw/` study artifacts (CuffDiff / FPKM tar / FPKM matrix).

---

## 12. Reproducing everything

Step-by-step commands (llama-server â†’ reference â†’ baselines â†’ ablations â†’ robustness â†’ multi-dataset â†’ plots â†’ services) are in **[docs/reproducibility.md](reproducibility.md)**. Methodological decisions and deviations (Python-vs-R, mouse correction, contrast freeze) are in **[docs/methodology.md](methodology.md)**.
