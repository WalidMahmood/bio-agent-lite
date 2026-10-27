# BioAgent-Lite: Resource-Efficient Multi-Agent Transcriptomic Intelligence

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi.tiangolo&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Hardware](https://img.shields.io/badge/Edge%20Hardware-RTX%205050%20(8GB%20VRAM)-76B900.svg?logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Adversarial Critic](https://img.shields.io/badge/Critic%20Audit-0%20Hallucinations-10B981.svg)](#-measured-results)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**BioAgent-Lite** runs a reliable gene-expression analysis workflow — differential expression → pathway enrichment → biological interpretation → evidence grounding → adversarial verification — on **consumer edge hardware** (an 8 GB RTX 5050, zero cloud APIs) by delegating *every* number to deterministic software (PyDESeq2, scipy, GSEApy) and using a 5-agent LangGraph (local Gemma 3 4B / MedGemma 4B / Qwen3 8B GGUF models) for planning and interpretation only. An **Adversarial Critic** audits each claim against the raw computed matrices and forces self-correction (bounded at 2 iterations) before results reach you.

Research question (Master Plan): *does role specialization + deterministic tool use + evidence grounding + explicit verification make a small local model measurably more reliable at bioinformatics than LLM-only or single-agent baselines?* Measured answer in [`docs/RESULTS.md`](docs/RESULTS.md): yes — near-perfect DE recovery on all four benchmark datasets with **zero hallucinated genes**, against an LLM-only baseline at 140% hallucination.

---

## 🎯 What it takes in, what it gives out

| **INPUT** | |
|---|---|
| **Expression matrix** (CSV/TSV, rows = genes, columns = samples) | `Gene, Chr1, Chr2, Chr3, Control1, Control2, Control3` — group membership auto-detected from column names (`res/treat/kd/dox/sh/mut` vs `sens/ctrl/con/nodox/scr/wt/parental`) |
| **Raw counts** | PyDESeq2 negative-binomial GLM (Wald test) + Benjamini-Hochberg FDR |
| **FPKM / TPM / normalized** | §13 **refusal guard** fires: no DESeq2, no fake p-values — safe reroute to descriptive log2FC ranking + Welch's t-test, padj honestly `N/A` |
| **Biological question** (free text) | Planner turns it into a frozen analysis contract |
| **Optionally your own uploaded matrix** | drag-and-drop in the UI or `POST /api/upload` — inspected on arrival |
| **OUTPUT** | |
| **Differential genes with direction** | `top_genes[]`: gene, **log2FC** (up/down vs control), **padj** (FDR), direction — *"which genes changed, and are they higher or lower in disease/treatment"* |
| **Pathways that shifted** | GO / Reactome / KEGG enrichment with overlap counts (e.g. `25/291`) |
| **Interpretation with honesty stamps** | claims typed `observed` / `supported` / `hypothesis`; absolute verbs forbidden; limitations + non-clinical disclaimer attached |
| **Evidence lineage per claim** | every claim linked to its exact source artifact (`GSE202768:top_differential_genes#TGFBI`) |
| **Critic audit verdict** | `PASS/FAIL` + errors caught + corrections forced — e.g. "CD82 claimed down but log2FC=+1.14 → corrected" |
| **Plots & deliverables** | publication-grade volcano + pathway figures, interactive web trace, **PDF laboratory report**, gene-table CSV, full JSON trace |

Typical use cases the system is built for: **which genes drive drug resistance** (resistant vs sensitive cells), **what happens when a cancer gene is switched off** (shRNA/knockdown vs control — the downstream program and whether the knockdown itself verified), **subtype-discriminating biomarkers** (TNBC vs non-TNBC), and **trust checking** (does the evidence support the interpretation).

---

## 🔬 Core innovations

1. **Zero arithmetic by LLMs (Deterministic Sandbox)** — models never calculate fold changes, statistics, or p-values; all numbers come from verified bioinformatics code.
2. **5-agent LangGraph architecture** — 🧭 Planner (frozen analysis contract, no arbitrary code) → ⚡ Computational Analyst (deterministic) → 🧬 Biological Interpreter (hedged claims only) → 🔍 Evidence Retriever (claim-to-artifact lineage) → 🛡️ Adversarial Critic (bounded self-correction loop, max 2 iterations).
3. **§13 Data-Type Refusal Guard** — detects FPKM/TPM matrices and *refuses* to fit a count model; reroutes to descriptive statistics instead of generating spurious p-values. (Demonstrated on FPKM-only held-out data — see `docs/RESULTS.md` §3.)
4. **Evidence-lineage grounding** — every biological claim carries a traceable `source_id` into the exact computed artifacts; absence of evidence is recorded (`#ABSENT`), never padded.
5. **Testable, replayable, auditable** — 27 preserved agent traces, 10 result tables, 24 figures, per-dataset PDF reports, and a complete propensity manifest (`outputs/manifest.json`).

---

## 🏛️ System architecture

```
User Question / Uploaded RNA-seq Matrix
               │
               ▼
    ┌───────────────────────┐
    │     Planner Agent     │ ◄── frozen analysis contract; data-type guards
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │ Computational Analyst │ ◄── deterministic PyDESeq2 / Welch / BH-FDR / GSEApy
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │ Biological Interpreter│ ◄── typed claims (observed/supported/hypothesis), hedged
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │   Evidence Retriever  │ ◄── claim-to-artifact lineage records
    └───────────┬───────────┘
                ▼
    ┌───────────────────────┐
    │   Adversarial Critic  │ ◄── direction/padj/pathway/wording checks;
    └───────────┬───────────┘     FAIL → correction loop (max 2) → re-verify
                ▼
    Certified Output: DEG table + pathways + evidence + audit
    + volcano/pathway figures + PDF lab report + full JSON trace
```

---

## 📊 Measured results (trace-backed — full audit in `docs/RESULTS.md`)

**Architecture comparison** (`outputs/tables/architecture_comparison.csv`, `evaluation/baselines/run_all_baselines.py`, reference set = computed PyDESeq2 truth on GSE202768):

| Metric | LLM-Only | Single Tool-Agent | **BioAgent-Lite (5-agent)** |
| :--- | :---: | :---: | :---: |
| DE Precision | 20.0% | 100.0% | **100.0%** |
| DE Recall | 4.0% | 60.0% | **100.0%** |
| DE F1 | 0.067 | 0.750 | **1.000** |
| Statistical claim accuracy | 12.5% | 100.0% | **100.0%** |
| Evidence Support Rate | 0.0% | 50.0% | **55.6%** (GSE202768) / 100% on 3 of 4 datasets |
| Hallucination rate | **140%** | 0.0% | **0.0%** |

**Generalization across 4 datasets** (`outputs/tables/dataset_generalization.csv`) — all four roles PASS with full statistical-claim accuracy; critic verdicts `PASS` on every dataset (1.0 evidence support on 3/4; 0.579 on the noisy development set).

> **Reading these numbers correctly:** DE F1 / precision / recall / statistical accuracy measure **task performance** ("did it find the right genes?") — 100% on all four datasets. *Evidence Support Rate* is a separate, stricter **integrity meter**: the share of write-up claims carrying a grounded evidence receipt. On the development set, **every gene claim had a receipt** — the only misses (8/19) were pathway names the interpreter mentioned beyond the computed significant list, which the system stamps `#ABSENT` rather than padding. Runs vary 0.55–0.74 there because claim mix varies per LLM run; task accuracy does not vary. Every variant and its source file: [`docs/RESULTS.md` §10](docs/RESULTS.md#10-cross-run-metric-variance-table-the-honest-summary).

**Adversarial robustness** (`outputs/tables/robustness_results.csv`) — R1–R4 stress tests (missing metadata, identical groups, injected decoy gene, statistical trap): **4/4 detected, 4/4 safe completion**.

**Genome-wide ranking** (empirical ROC on 14,009-gene reference table, `roc_auc_curves.png`): **ROC-AUC 0.967 / PR-AUC 0.637** for the system's candidate ranking (LLM-only proxy ≈ chance, 0.518 / 0.039).

**Provenance honesty:** the table above is measured; disease-model style hot links to trace and table files are in [`docs/RESULTS.md`](docs/RESULTS.md), which separates **MEASURED / REPLAYED / GENERATED** artifacts precisely — including known report-figure-vs-CSV discrepancies and the (documented) status of vector-DB/PubMed components as roadmap-not-runtime.

### Real-time validation: drug-resistance fingerprint (PDAC · gemcitabine)

A seeded synthetic test matrix (`scripts/generate_pdac_dataset.py`, 2,000 genes × 6 samples, biomarkers pinned to mathematically known directions) run through the **live** upload engine (real Welch + BH at request time): **56 significant DEGs** recovered in a mechanistically coherent resistance program —

| Gene | log2FC | Role |
|---|---|---|
| `CDA` | **+3.32** | destroys gemcitabine by deamination (direct resistance) |
| `RRM1` | **+2.88** | the drug's ribonucleotide-reductase target — amplified |
| `ABCB1` | **+3.17** | multidrug efflux pump |
| `DCK` | **−2.78** | rate-limiting prodrug-activation kinase — lost |
| `SLC29A1` | **−2.45** | hENT1 nucleoside transporter — entry door shut |

…with the Critic catching the draft's DCK direction inversion (iteration-0 FAIL → force-corrected → PASS). *Note: this is a controlled synthetic validation of the live pipeline, not clinical data.*

### The knockdown use case: "turn the cancer gene off — what happened?"

On **GSE202768** (PRRX1 knockdown in TNBC cells, `KD_DOX` vs `KD_noDOX`): the system first verifies the knockdown itself (`PRRX1 log2FC −2.28, padj 1.3e-29`), then reports the **3,946-gene downstream response** (2,002 up / 1,944 down) and its pathway context — **Extracellular Matrix Organization (Reactome, adjP 2.2e-07)** with `TGFBI +1.95, COL1A1 +2.08, COL5A1 +1.21, TNC +1.89` rising. Read as: release from PRRX1 remodelling shifts the tumor-matrix program. Full walkthrough: [`docs/USAGE.md` §5–6](docs/USAGE.md).

### The critic's self-correction, preserved on disk

`outputs/traces/dev_20260905T165240Z.json` — the draft interpretation claimed `CD82` down-regulated; the Critic flagged `claimed down but log2FC=+1.14 (wrong direction)`; iteration-1 re-interpretation certified `PASS`. The same preservation exists for ablated-critic runs (catches gone) — the honest way to prove the verifier earns its place.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+ · Node.js 18+ (frontend only) · optional NVIDIA GPU with CUDA 12 (falls back gracefully without LLM server)
- Models are local GGUF files (see `configs/models.yaml`); datasets land in `data/raw/` via `tools/download_datasets.py`

### 1. Run the analysis (headless — no UI needed)
```bash
git clone https://github.com/WalidMahmood/bio-agent-lite.git
cd bio-agent-lite
pip install -r requirements.txt

# Optional (recommended): start the local LLM server (one 4B model at a time)
llama.cpp\bin\llama-server.exe -m models\gemma-3-4b-it-UD-Q8_K_XL.gguf -ngl 99 -c 8192 --port 8080

# Full 5-agent run, trace + verdict printed:
python experiments/development/run_dev.py
# LLM-free deterministic run (statistics + critic still fully valid):
python experiments/development/run_dev.py --no-llm
```

### 2. Generate the reference statistics (~25 s)
```bash
python reference/run_deseq2.py       # PyDESeq2 NB GLM → reference/outputs/GSE202768/de_results.csv
python reference/run_enrichment.py   # GSEApy GO / Reactome / KEGG enrichment
```

### 3. Web workbench (optional)
```bash
python backend/main.py               # FastAPI on http://127.0.0.1:8000/docs
cd frontend && npm install && npm run dev   # http://localhost:5173
```
In the browser: pick a dataset chip or **drag-and-drop your own CSV/TSV**, get the live audit, figures and a PDF report.

### 4. Reproduce the entire evaluation
```bash
python evaluation/baselines/run_all_baselines.py     # Table: architecture comparison
python evaluation/ablations/run_ablations.py --dataset GSE202768
python evaluation/robustness/run_robustness.py
python evaluation/run_all_datasets.py                # generalization suite
python evaluation/metrics/generate_all_eval_plots.py
```

---

## 📚 Documentation index

| Document | What it covers |
|---|---|
| **[docs/USAGE.md](docs/USAGE.md)** | **Input/output guide** — formats, upload rules, sign conventions, the 2 worked cancer examples ("resistance program", "gotcha interpretation"), troubleshooting/FAQ |
| **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** | Every REST endpoint, request/response schemas, agent Pydantic contracts, headless entry points, env vars |
| **[docs/EXPLAINABILITY.md](docs/EXPLAINABILITY.md)** | How the system shows its work — claim taxonomy, evidence lineage, the critic's 6 checks, trace anatomy, the live/replayed/generated ledger, how to fact-check numbers yourself |
| **[docs/RESULTS.md](docs/RESULTS.md)** | Complete experiment dossier — every measured table, per-dataset discoveries, model comparison, ROC/PR, 27 traces indexed, known discrepancies |
| **[docs/methodology.md](docs/methodology.md)** | Frozen methodological decisions (Python-vs-R, mouse handling, contrast freeze, thresholds) |
| **[docs/reproducibility.md](docs/reproducibility.md)** | Environment, one-line reproduction commands, verification checkpoints |
| [BioAgent-Lite_MASTER_PLAN.md](BioAgent-Lite_MASTER_PLAN.md) | Research design, hypotheses H1–H5, evaluation protocol |
| [notebooks/BioAgent_Lite_Complete_Demonstration.ipynb](notebooks/BioAgent_Lite_Complete_Demonstration.ipynb) | 44-cell interactive walkthrough (runs LLM-free) |

---

## 📁 Repository structure

```text
bio-agent-lite/
├── agents/           # LangGraph 5-agent implementation (planner, computational, biology,
│                     #   evidence, critic, schemas, graph + correction loop)
├── backend/          # FastAPI service: main.py (routes/telemetry), realtime_engine.py
│                     #   (live Welch+BH analysis of uploaded matrices), report_generator.py
├── frontend/         # Vite+React workbench (upload, agent trace, plots, PDF export)
├── tools/            # dispatcher (per-dataset loaders), expression (§13 guard),
│                     #   validation (R1–R4 hooks), llm_client (llama.cpp OpenAI-compat)
├── reference/        # deterministic statistical pipeline: run_deseq2.py, run_enrichment.py
│                     #   + reference/outputs/ (re-derivable DE & enrichment CSVs)
├── evaluation/       # baselines/, ablations/, robustness/, metrics/ — all suites
├── experiments/      # development/run_dev.py — headless full-system runner
├── data/             # raw/ (4 GEO sets), metadata/, test_datasets/ (seeded PDAC matrix)
├── configs/          # models / datasets / thresholds / experiment YAML (frozen)
├── outputs/          # tables/ (10 CSVs), figures/ (24 PNGs), traces/ (27 JSONs),
│                     #   reports/ (5 PDFs), manifest.json
├── docs/             # USAGE, API_REFERENCE, EXPLAINABILITY, RESULTS, methodology, reproducibility
└── *.pdf/.md/.tex    # academic term-project report deliverables
```

---

## ⚠️ Scope & limitations (honest framing)

* **Research prototype, not a diagnostic tool.** Every output carries a non-clinical disclaimer; thresholds are fixed project parameters.
* Whole project validated on **breast-cancer/perturbation transcriptomics** (Master Plan scope); no claims about other organisms beyond the mouse smoke test.
* Web benchmark runs **replay recorded audited traces** (numbers are genuine live-run artifacts; fresh computation happens via uploads or headless runs) — the precise live/replay/generated ledger is in [docs/EXPLAINABILITY.md §8](docs/EXPLAINABILITY.md#8-the-live--replayed--generated-ledger-read-this-before-citing-numbers).
* ChromaDB / PubMed retrieval are **roadmap components**, not runtime (evidence grounding is deterministic claim-to-artifact lineage — see RESULTS §11); vector-RAG generation is future work.
* Reference pipeline is a reproducible comparison point, not absolute biological truth (Master Plan §25–26).

---

## 📜 License
MIT — for research and educational use. Not approved for clinical diagnostics.
