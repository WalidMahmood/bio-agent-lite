# BioAgent-Lite User Guide — Inputs, Outputs & Workflows

> **One-sentence definition:** BioAgent-Lite takes a **gene-expression matrix** (rows = genes, columns = samples) plus a **biological question**, computes a controlled differential-expression workflow with deterministic statistics, and returns an **evidence-audited report** telling you *which genes changed, in which direction, with what confidence, and through which pathways* — with an adversarial Critic agent that checks every claim before you see it.

This guide is the practical reference: what you can give the system, what you get back, and how to phrase the "cancer gene" questions like *"which genes were switched off, and what happened downstream?"*

---

## 1. What the system can answer

BioAgent-Lite is built around one controlled workflow (**differential expression → pathway enrichment → interpretation → evidence → verification**). Within that workflow, the typical questions it can answer are:

| You ask / provide | The system computes | What you learn |
|---|---|---|
| A count matrix from a drug-response experiment (e.g. resistant vs sensitive cancer cells) | Which genes are significantly up- or down-regulated | *Which mechanisms drive the phenotype* (efflux pumps, drug-inactivation enzymes, transporters…) and **the direction** of each change |
| A knockdown / perturbation dataset (gene G switched **off** vs intact control) | The full expression response to the knockdown | Confirmation that **G is actually down** (direction check), plus **what happened downstream** — the genes and pathways whose expression shifted because G was removed |
| Two cancer subtypes (e.g. TNBC vs non-TNBC cell lines) | Subtype-discriminating markers | A ranked biomarker panel with `log2FC`, FDR-adjusted significance, and pathway context |
| Any CSV/TSV matrix you upload | An automatic data-type inspection (raw counts vs normalized) | Either a rigorous negative-binomial GLM (PyDESeq2), or a **refusal + safe reroute** to descriptive statistics instead of fitting an invalid model |
| "Is this result trustworthy?" | The Critic agent's audit of every claim | `PASS/FAIL` verdict, list of caught errors, and the corrections applied |

**What it is NOT for** (per Master Plan §8 & §39): clinical diagnosis, clinical decision-making, single-cell analysis, variant calling, or any claim of medical-grade performance. Every output carries a non-clinical disclaimer.

---

## 2. Three ways to run it

### 2.1 The Web Workbench (easiest)

```text
Terminal 1 — start the LLM server (optional but recommended):
  llama.cpp\bin\llama-server.exe -m models\gemma-3-4b-it-UD-Q8_K_XL.gguf -ngl 99 -c 8192 --port 8080 --host 127.0.0.1

Terminal 2 — start the FastAPI backend:
  python backend\main.py                      # serves http://127.0.0.1:8000

Terminal 3 — start the React frontend:
  cd frontend
  npm install    (first time only)
  npm run dev                                  # opens http://localhost:5173
```

In the browser you:
1. **Pick a dataset chip** (`GSE202768`, `GSE113650`, `GSE95304`, `GSE336903`, or the `PDAC_Gemcitabine` live test) **or drag-and-drop your own `.csv` / `.tsv`**.
2. The button badge immediately shows the backend's inspection of your file: detected data type, estimated gene count, and whether the **FPKM refusal guard** was triggered.
3. Type a question (default prompt auto-fills), press Enter.
4. You watch the 5-agent progress strip, then receive: a plain-language summary, the stat grid, ranked biomarkers, audited claims, figures (volcano, pathways), limitations, and download buttons for the **PDF lab report** and gene table.

Without the LLM server running, the system still works: the Planner and Biological Interpreter silently fall back to deterministic templates and the statistics remain fully computed (`--no-llm`-equivalent behavior).

### 2.2 The REST API (scriptable)

```bash
#Inspect an uploaded matrix first (optional):
curl -X POST http://127.0.0.1:8000/api/upload -F "file=@your_counts.csv"

#Run the analysis on your own uploaded file:
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"dataset":"custom","custom_filename":"your_counts.csv","model":"gemma-3-4b","query":"Which genes respond to the drug, and how?"}'

#Run a built-in benchmark dataset:
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"dataset":"GSE202768","model":"gemma-3-4b"}'

#Download the generated PDF lab report:
curl -O http://127.0.0.1:8000/api/report/analysis_pdf?dataset=PDAC_Gemcitabine
```

Full endpoint reference including every request/response field: **[docs/API_REFERENCE.md](API_REFERENCE.md)**.

### 2.3 Headless (no server, no UI)

```powershell
#Full 5-agent run on the development dataset (needs llama-server on :8080):
python experiments\development\run_dev.py

#LLM-free run (pure deterministic analysis + critic, works on any machine):
python experiments\development\run_dev.py --no-llm

#Reference statistics only (PyDESeq2 NB GLM + GSEApy enrichment):
python reference\run_deseq2.py
python reference\run_enrichment.py

#Re-run the full evaluation suite (baselines / ablations / robustness / all datasets):
python evaluation\baselines\run_all_baselines.py
python evaluation\ablations\run_ablations.py --dataset GSE202768
python evaluation\robustness\run_robustness.py
python evaluation\run_all_datasets.py
```

Every headless run writes a complete trace JSON to `outputs/traces/` and the printed verdict is `status=PASS/FAIL, errors, warnings, iterations`.

---

## 3. Input specification

### 3.1 Expression matrix (the main input)

A **CSV or TSV** where rows are genes and columns are samples:

```csv
Gene,Sensitive_Rep1,Sensitive_Rep2,Sensitive_Rep3,Resistant_Rep1,Resistant_Rep2,Resistant_Rep3
CDA,122,119,123,1282,1187,1187
RRM1,267,258,244,1895,1811,1811
DCK,1450,1390,1520,210,225,205
```

Requirements and auto-detection:

| Aspect | Accepted | Detection behavior |
|---|---|---|
| File format | `.csv` (comma) or `.tsv/.txt` (tab) — auto-detected | Tab accepted if the header line contains no comma |
| Gene column | First column, OR a column named `gene`, `Gene`, `symbol`, `GeneSymbol`, `gene_name`, `id` (case-insensitive) | Renamed to `Gene` internally |
| Gene IDs | **HGNC symbols** (recommended — enables pathway annotation), **Ensembl IDs** supported (mouse `ENSMUSG*` recognized and handled descriptively) | Mouse IDs are detected and never given human pathway credit |
| Sample → group | Column **names** encode groups. Treatment side matches: `res*`, `treat*`, `kd*`, `dox*`, `sh*`, `mut*`, `pert*`. Control side matches: `sens*`, `ctrl*`, `con*`, `nodox*`, `scr*`, `wt`, `parental` | If either side gets < 2 columns, columns are split evenly (2nd half = treatment) |
| Group size | ≥ 2 samples per group | Smaller runs are rejected rather than silently reported |
| Values: raw integer counts | → **PyDESeq2 negative-binomial GLM (Wald test) + BH-FDR** — the rigorous path | Checked by `tools/expression.py::assert_is_counts`: > 1% non-integer values or any negative value ⇒ refusal |
| Values: FPKM/TPM/normalized | → **§13 Data-Type Refusal Guard fires**: DESeq2 is *refused*, system reroutes to descriptive log2FC ranking + Welch's t-test + Benjamini-Hochberg, marked `padj = N/A (Descriptive FPKM)` | Float detection both on upload preview and at computation time. No fake p-values are ever generated for normalized data |

Sign convention: **`direction: "up"` always means higher expression in the treatment / intervention group (group A) than in the control (group B)**. Group A keywords are the treatment-side keywords above; group B is the control side.

Uploads are stored under `outputs/uploads/`. There is no enforced file-size cap; a realistic bulk RNA-seq matrix (20k–60k genes) is the intended scale.

### 3.2 Metadata tables (built-in datasets)

The four bundled GEO datasets come with curated metadata in `data/metadata/` (`sample, gsm, group_dev, include_dev`, etc.). For your own GEO matrices you do **not** need a separate metadata file — group assignment comes from column names (§3.1). The metadata tables matter only when you run the headless reference pipeline on the built-in datasets, where column samples are mapped to design groups (e.g. GSE202768: `KD_DOX` = shPRRX1 knockdown induced with doxycycline, vs `KD_noDOX` = not induced).

### 3.3 Built-in benchmark datasets

| Accession | Role | Organism / data | Samples | Contrast analyzed | Statistical path |
|---|---|---|---|---|---|
| **GSE202768** | Development & tuning | Human breast cancer (TNBC), raw counts | 16 (6 used) | Hs578 shPRRX1 knockdown **induced (KD_DOX)** vs **not induced (KD_noDOX)** — "cancer gene switched off" | PyDESeq2 counts GLM |
| **GSE113650** | External validation | Human breast cancer cell lines, CuffDiff study result | 6 | TNBC (MDA-MB-468, HCC70, HCC1143) vs non-TNBC (MCF7, BT474, T47D) | Study reference result + evaluation vs known truth |
| **GSE95304** | Held-out evaluation | Human breast cancer, per-sample FPKM tracking | 20 | shMyc / shFra-1 vs scrambled controls | FPKM descriptive ranking (no fake p-values) — refusal guard demo |
| **GSE336903** | Smoke test | **Mouse** colorectal organoid, processed FPKM | 6 | treatment vs control | FPKM descriptive, mouse-aware |
| **PDAC_Gemcitabine** | Live upload validation | Synthetic *seeded* test matrix (2,000 genes × 6 samples) generated by `scripts/generate_pdac_dataset.py` with known chemoresistance markers | 3 vs 3 | drug-resistant vs drug-sensitive | Live Welch t-test + BH computed at request time |

**Honesty note:** the PDAC matrix is a *synthetic controlled test* whose biomarkers (CDA, RRM1, ABCB1, DCK, SLC29A1…) were seeded with mathematically known directions and magnitudes. It validates that the live computational path produces the correct known answer — it is **not** real clinical RNA-seq data.

### 3.4 The LLM (optional ingredient)

Models are local GGUF files placed in `models/` — no cloud API, no download-on-demand:

| Model | File | Size | Role |
|---|---|---|---|
| Gemma 3 4B IT (primary) | `models/gemma-3-4b-it-UD-Q8_K_XL.gguf` | 4.81 GB | Reasoning for Planner + Biological Interpreter |
| MedGemma 4B IT | `models/medgemma-4b-it-UD-Q8_K_XL.gguf` | 4.81 GB | Biomedical-domain comparison |
| Qwen3 8B | `models/Qwen3-8B-Q4_K_M.gguf` | 4.68 GB | Third-model comparison (disable thinking with `/no_think`) |

Serve **one at a time** on an 8 GB VRAM GPU (peak usage ≈ 4,919 MB for the 4B models). The three deterministic agents (Analyst, Evidence, Critic) never call the LLM — put the server down and the analysis over the data still runs.

---

## 4. Output specification

Every run (web, API, or headless) returns the same seven layers:

### 4.1 `stats` — the numerical core (deterministic)

```json
{
  "genes_tested": 14009,
  "significant_genes": 3946,
  "up_regulated": 2002,
  "down_regulated": 1944,
  "padj_threshold": 0.05,
  "contrast": "KD_DOX vs KD_noDOX"
}
```

### 4.2 `top_genes` — the biomarker table (the "which genes changed" answer)

```json
{"gene": "TGFBI", "log2FC": 1.95, "padj": 4.7e-37,  "direction": "up"},
{"gene": "PRRX1", "log2FC": -2.28, "padj": 1.3e-29, "direction": "down"}
```

* `log2FC` — log₂ fold change. `+2` = quadrupled expression in the treatment vs control; `-1` = halved. The size of the effect.
* `padj` — Benjamini-Hochberg FDR-adjusted p-value ("probability this looks differential purely by chance"). Significant if `< 0.05`. On FPKM datasets this is deliberately `N/A` instead of fabricated.
* `direction` — the sign of log2FC (see §3.1 sign convention).

### 4.3 `sig_pathways` — the "what biological programs moved" answer

```json
{"source": "Reactome", "term": "Extracellular Matrix Organization R-HSA-1474244", "adjP": 2.2e-07, "overlap": "25/291"}
```

`overlap 25/291` = 25 of your changed genes are members of that pathway (which has 291 annotated genes). Sources: Gene Ontology, Reactome, KEGG (GSEApy enrichment).

### 4.4 `interp` — the interpretation with an honesty stamp

Three typed schemas per claim: `"type": "observed"` (restating a number), `"supported"` (backed by enrichment/evidence), `"hypothesis"` (explicitly hedged speculation). Absolute language (`proves`, `definitively`) is forbidden by the critic. Closing `limitations` and a fixed non-clinical `disclaimer` are always attached.

### 4.5 `critic` verdict — the audit stamp

```json
{"status": "PASS", "errors": [], "warnings": [], "corrections": [],
 "audit_scores": {"total_claims_audited": 15, "errors_found": 0, ...}}
```

A `FAIL` means you did **not** receive the uncorrected wrong answer — see [docs/EXPLAINABILITY.md](EXPLAINABILITY.md) for every check it performs.

### 4.6 Figures

`volcano_plot_<dataset>.png` — every gene, x = log2FC, y = −log10(padj); significant points colored, top genes labeled.
`pathways_<dataset>.png` — top enriched pathways as −log10(adjP) bars.

### 4.7 Downloads

* **PDF laboratory report** — executive summary, metrics table, top-10 biomarkers with FDR and direction, embedded figures, the full 5-agent trajectory, and the critic audit log.
* **Gene table CSV** and **full trace JSON** (every agent step, every tool call, every evidence record).

---

## 5. Worked example A — "Which genes make cancer cells drug-resistant?"

Upload `data/test_datasets/PDAC_gemcitabine_counts.csv` (or hit the PDAC preset). Ask: *"Which genes respond to gemcitabine, and which pushes drive resistance?"*

Result (56 significant DEGs at `padj < 0.05, |log2FC| ≥ 0.5`):

| Gene | log2FC | What it means |
|---|---|---|
| `CDA` | **+3.32** | Cytidine deaminase — metabolically **destroys** gemcitabine; its overexpression is direct resistance |
| `RRM1` | **+2.88** | The actual drug **target** — amplifying target = needing more drug |
| `ABCB1` | **+3.17** | P-glycoprotein **efflux pump** ejecting the drug from cells |
| `DCK` | **−2.78** | The kinase that **activates** the prodrug — its loss means less target hit |
| `SLC29A1` | **−2.45** | hENT1 nucleoside **transporter** — the drug's door into the cell gets shut |

Reading pattern: **up-regulated ∈ {inactivate the drug, remove the target, eject the drug} + down-regulated ∈ {activate the drug, transport the drug} ⇒ a complete, mechanistically coherent resistance program.** Both halves of the story are visible in the same table.

If you then ask *"what happens to DCK"* — the system reports `direction: down`, `log2FC: −2.78`, the evidence record `DE_computation#DCK`, and the interpreter's hedged claim that loss of the rate-limiting activation kinase is *consistent with* reduced drug sensitivity. If a draft interpretation had called DCK "up-regulated", the Critic flags it (`claimed down but log2FC is negative`) and forces a correction before you see it.

## 6. Worked example B — "This cancer gene was switched off — what happened?"

Load `GSE202768` and ask about the knockdown. This dataset is a literature-standard design: **PRRX1** (an EMT/mesenchymal transcription factor implicated in triple-negative breast cancer) is knocked down with doxycycline-inducible shRNA, and high-throughput sequencing captures what changes.

1. **The knockdown itself is verified**: `PRRX1 log2FC = −2.28, padj = 1.3e-29` — the target gene is genuinely, massively down.
2. **3,946 genes shift significantly** (2,002 up / 1,944 down) — the downstream response.
3. **The response is coherent**: the top movers are extracellular-matrix and collagen genes (`TGFBI +1.95, padj 4.7e-37`; `COL1A1 +2.08`; `COL5A1 +1.21`; `TNC +1.89`, while metabolic genes like `IGFBP1 −2.50, PDP1 −1.07` drop), and pathway enrichment crowns **Extracellular Matrix Organization (Reactome, adjP 2.2e-07)** — i.e. release from PRRX1 control remodels the tumor-matrix program.
4. The report states plainly: *knockdown confirmed, direction correct* — and the interpreter's claim that PRRX1 suppression is associated with matrix reprogramming is typed `"supported"` with lineage records showing exactly which computed numbers and enrichment terms back it.

This is the canonical use of the phrase "if we turn this gene off, it did/didn't help": the same workflow applies to **any** shRNA/siRNA/CRISRI-style perturbation counts matrix, e.g. the held-out GSE95304 set (shMyc −2.15 → glycolysis/ribosome program shift).

---

## 7. Troubleshooting & FAQ

| Symptom | Cause | Fix |
|---|---|---|
| Analysis still completes when llama.cpp is down | Intentional fallback: deterministic agents + template interpreter | None needed; stats and critic remain fully valid |
| `padj: "N/A (FPKM Guard)"` on some datasets | Data is normalized/FPKM → §13 exact refusal guard rerouted to descriptive stats | Provide raw integer counts to unlock the NB GLM |
| Upload badge says `ACTIVATED (Refused DESeq2 …)` | Same guard, at upload inspection time | Expected behavior for FPKM files |
| Frontend shows `offline` telemetry | Backend not on :8000, or vite proxy untouched | Start `python backend\main.py`; check `http://127.0.0.1:8000/docs` |
| `LLM request failed` in log | llama-server not started, wrong port, or model loaded elsewhere | Run §2.1 terminal 1; one model at a time on 8 GB VRAM |
| Ensembl mouse gene names in output | Dataset genuinely mouse (`ENSMUSG*`) Descriptive path | Expected; pathway credit uses mouse-aware handling, never human libs |
| `custom_filename` upload runs stats but story text sounds canned | Live engine computes real statistics and figures; narrative & pathway context for uploads are template/treasury-based | See [docs/EXPLAINABILITY.md §8](EXPLAINABILITY.md) for exact live vs pre-baked breakdown |

**Can I add a fifth GEO dataset?** Yes — `tools/download_datasets.py --only <ACC>` fetches from NCBI FTP into `data/raw/<ACC>/`, then add a metadata CSV and a `DATASET_PROFILES` entry in `agents/planner.py` + a loader in `tools/dispatcher.py`.

**Where is the vector database / PubMed?** Not in the deployed runtime. Evidence grounding is deterministic and verifiable against the computed tables (see EXPLAINABILITY §8); the Chroma/PubMed components remain listed in `requirements.txt` as a documented roadmap item, and are absent from every code path today.

**Not for clinical use.** Every output ships with the disclaimer; thresholds are project parameters, not diagnostics.
