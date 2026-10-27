# BioAgent-Lite API Reference

Base URL: `http://127.0.0.1:8000` · Framework: **FastAPI** (`backend/main.py`, app version 1.2.0) · Interactive OpenAPI docs auto-generated at `http://127.0.0.1:8000/docs` · CORS: `*` (dev configuration).

---

## 1. Endpoints

| # | Method | Path | Purpose |
|---|---|---|---|
| 1 | GET | `/api/health` | Liveness + registered agent roster |
| 2 | GET | `/api/system_info` | Live hardware & LLM telemetry (polled by the UI every 2.5 s) |
| 3 | POST | `/api/upload` | Inspect an expression matrix before running |
| 4 | GET | `/api/datasets` | Built-in benchmark dataset summary |
| 5 | POST | `/api/run` | **Main analysis entry point** |
| 6 | GET | `/api/report/analysis_pdf` | Generate/download per-analysis PDF lab report |
| 7 | GET | `/api/report/pdf` | Download the academic term-project PDF |
| 8 | GET | `/api/tables/{table_name}` | Retrieve any results table (CSV→JSON) |
| 9 | GET | `/api/figures/{figure_name}` | Retrieve any figure PNG |
| 10 | GET | `/api/manifest` | Machine-readable reproducibility manifest |

### 1.1 `GET /api/health`
```json
{"status": "online", "system": "...", "version": "1.2.0",
 "agents": [{"name": "Planner", "role": "..."}, ... 5 agents]}
```

### 1.2 `GET /api/system_info?model=gemma-3-4b`

Query param `model` selects the reported profile. Response:
```json
{
  "gpu":  {"name": "NVIDIA GeForce RTX 5050 Laptop GPU", "vram_total_gb": 8.0,
            "vram_used_gb": 4.9, "vram_pct": 60.1, "cuda_version": "12.4",
            "runtime": "llama.cpp CUDA cuBLAS"},
  "cpu":  {"cores": 12, "threads": 16, "usage_pct": 18.4},
  "ram":  {"used_gb": 7.4, "total_gb": 16.0, "usage_pct": 46.3},
  "model": {"id": "gemma-3-4b", "tokens_per_sec": 38.5, "precision": "Q8_K_XL",
            "benchmark_accuracy": 100.0, "verdict": "..."},
  "context": {"window_size": 8192, "active_tokens": 1420, "pct_used": 17.4,
              "kv_cache_type": "Q8_0 quantized KV cache"},
  "available_models": ["gemma-3-4b", "medgemma-4b", "qwen-3-8b"]
}
```
GPU via live `nvidia-smi` query; CPU/RAM via `psutil`. If any source is unavailable the endpoint degrades gracefully with constants (the UI mirrors this fallback).

### 1.3 `POST /api/upload` — multipart form `file`
Before analysis, the backend inspects the matrix and returns a data-type verdict:
```json
{"status": "success", "filename": "my_counts.csv", "size_bytes": 61051,
 "total_columns": 7, "estimated_genes": 2000,
 "detected_data_type": "Raw Integer Counts",
 "recommended_strategy": "PyDESeq2 Negative Binomial GLM (Wald Test)",
 "guardrail_status": "PASSED (Count schema compliant)"}
```
Normalized (float) values instead return `"detected_data_type": "FPKM / Normalized Values"`,
`"recommended_strategy": "Descriptive log2FC + Welch's t-test (Count-refusal guard triggered)"`,
`"guardrail_status": "ACTIVATED (Refused DESeq2 for normalized values)"`.
Files are stored under `outputs/uploads/` (delimiter auto-detected; first 4 KB sampled).

### 1.4 `GET /api/datasets`
Rows of `outputs/tables/dataset_summary.csv` (accession, role, organism, samples, data type, contrast per dataset).

### 1.5 `POST /api/run` — the main route

Request body:
```json
{"dataset": "GSE202768",              // or "PDAC_Gemcitabine", "custom"
 "model": "gemma-3-4b",               // gemma-3-4b | medgemma-4b | qwen-3-8b
 "query": "Analyze differential expression and enriched pathways.",
 "use_critic": true,                   // accepted (held for schema compatibility)
 "compare_dataset": null,
 "custom_filename": "my_counts.csv"}  // resolves an earlier /api/upload
```

**Routing logic (important to know):**
* The run is routed to the **live realtime engine** (`backend/realtime_engine.py`) when: `custom_filename`
is set, `dataset == "PDAC_Gemcitabine"`, `dataset` contains "custom", or the query mentions
gemcitabine/pdac/pancreatic/real-time. This path computes **real statistics at request time**
( Welch's t-test + Benjamini-Hochberg on your matrix, live figures).
* Otherwise (`GSE202768`, `GSE113650`, `GSE95304`, `GSE336903`) the endpoint serves the **recorded and
audited evaluation trace** for that dataset (replaying a genuine full LangGraph run previously stored
in `outputs/traces/`), overlaid with the stored agent artifacts. The distinction and its rationale
are documented in [docs/EXPLAINABILITY.md §8](EXPLAINABILITY.md) and [docs/RESULTS.md](RESULTS.md).

Response (both branches share this shape; live branch adds `data_type` etc. in `stats`):
```json
{
  "status": "success",
  "dataset": "GSE202768",
  "model": {"id": "gemma-3-4b", "name": "Gemma 3 4B IT", "tokens_per_sec": 38.5, "...": "..."},
  "total_latency_s": 24.8,
  "plain_summary": "Plain-language narrative of the findings...",
  "steps": [                       // 5-agent trajectory
    {"id": "planner", "agent": "...", "status": "completed", "icon": "...",
     "tools_selected": [...], "tool_calls": [{"tool": "...", "input": "...", "output": "..."}],
     "thought": "...", "decision": "...", "latency_s": 1.2, "tokens": 480},
    {"id": "computational_analyst", "..." : "..."}, {"id": "biological_interpreter", "...": "..."},
    {"id": "evidence_retriever", "...": "..."}, {"id": "critic", "...": "..."}
  ],
  "stats": {"genes_tested": 14009, "significant_genes": 3946,
             "up_regulated": 2002, "down_regulated": 1944,
             "padj_threshold": 0.05, "contrast": "KD_DOX vs KD_noDOX"},
  "top_genes": [{"gene": "TGFBI", "log2FC": 1.95, "padj": 4.7e-37, "direction": "up"}, ...],
  "sig_pathways": [{"source": "Reactome", "term": "Extracellular Matrix Organization ...",
                     "adjP": 2.2e-07, "overlap": "25/291"}],
  "interp": {"observations": [...], "claims": [{"statement": "...", "type": "observed|supported|hypothesis",
             "genes": [...], "pathways": [...] }], "limitations": [...],
             "disclaimer": "RESEARCH PROTOTYPE ONLY ... not approved for clinical diagnostics ..."},
  "figures": {"volcano": "...", "pathways": "...", "confusion_matrix": "...",
               "breakdown": "...", "benchmark_radar": "..."},
  "downloads": {"analysis_pdf": "...", "pdf_report": "...",
                 "gene_table_csv": "...", "trace_json": "/api/manifest"}
}
```
All floating-point infinities/NaNs are sanitized (`inf → ±999.0`, `NaN → null`) by `sanitize_floats()` before serialization.

### 1.6 `GET /api/report/analysis_pdf?dataset=<name>&model=<model>`
Builds (if needed) and returns `outputs/reports/BioAgent_Analysis_Report_<dataset>.pdf`.
ReportLab letter format containing: executive summary, run metadata, computational metrics table,
top-10 biomarkers with direction flags, embedded volcano + pathway figures, the sequential
multi-agent execution narrative, audited observations, limitations + disclaimer.
Valid `dataset` values include all four benchmark accessions, `PDAC_Gemcitabine`
and any `custom` upload key.

### 1.7 `GET /api/report/pdf`
Returns the academic `Term_Project_Report.pdf` (404 if absent).

### 1.8 `GET /api/tables/{table_name}` and `GET /api/figures/{figure_name}`
Serve anything under `outputs/tables/` (CSV → JSON `{table, rows}`) and `outputs/figures/` (PNG binary). Valid table names include:

```
architecture_comparison  ablation_results  robustness_results
dataset_generalization  dataset_summary  model_comparison
model_systems_tradeoffs  all_models_4datasets_comparison
all_datasets_confusion_matrix_metrics  resource_usage
```
Unknown names return 404.

### 1.9 `GET /api/manifest`
Full `outputs/manifest.json` — datasets, hardware, model, thresholds, artifact index, headline metrics — JSON-sanitized recursively.

---

## 2. Agent data contracts (`agents/schemas.py`)

All inter-agent payloads are Pydantic models; the LangGraph state is a `TypedDict` with
`question, dataset, plan, comp, interp, evidence, verdict, traces, iterations`.

| Model | Fields | Producer → consumer |
|---|---|---|
| `Comparison` | `group_a` (intervention), `group_b` (reference) | Planner consumes; used for contrast string |
| `Plan` | `analysis_goal, dataset, organism="Homo sapiens", data_type="counts" (counts\|fpkm\|cuffdiff), comparison: Comparison, design, de_method, required_steps[5], safety_guardrails[4]` | Planner → Computational Analyst |
| `TopGene` | `gene, log2FC, padj?, pvalue?, direction: "up"\|"down"` | Computational Analyst (evidence & critic too) |
| `SigPathway` | `source (GO\|Reactome\|KEGG), term, adjP, overlap` | Computational Analyst → Interpreter |
| `ComputationalResult` | `dataset, data_type, contrast, n_total_tested, n_sig, n_up, n_down, padj_threshold=0.05, top_genes: List[TopGene], sig_pathways, execution_log` | Analyst → Interpreter/Evidence/Critic (no LLM) |
| `InterpretationClaim` | `statement, type: observed\|supported\|hypothesis, genes[], pathways[], hedged=True` | Interpreter → Critic |
| `Interpretation` | `observations[], claims[], limitations[], uncertainty[], disclaimer` | Interpreter → Critic / final report |
| `EvidenceRecord` | `claim, query, source_id, source_db, snippet, relevance, timestamp` | Evidence Retriever → report (lineage) |
| `CriticVerdict` | `status: PASS\|FAIL, errors[], warnings[], corrections[], statistical_checks_passed, biological_grounding_passed, safety_guardrails_passed, audit_scores` | Critic → routing |

Full field-level semantics and usage examples: [docs/USAGE.md §4](USAGE.md).

---

## 3. LangGraph execution flow (`agents/graph.py`)

```
START → planner → compute → biology → evidence → critic ─┬─ PASS → END
                                                          ├─ iterations ≥ 2("giveup") → END (FAIL stands)
                                                          └─ "correct" → n_correct → evidence → critic …
```
* `MAX_CORRECTIONS = 2` (bounded loop ⇒ at most 3 critic evaluations per run).
* `_apply_correction()`: removes flagged genes from claims and rewrites absolute language
(`proves|proven|definitively demonstrates|certainly causes` → `is consistent with the observation that`).
* The deterministic agents (Analyst, Evidence, Critic) never invoke the LLM. Planner and Interpreter
fall back to deterministic templates when `use_llm=False` or the llama-server (port 8080) is down.

---

## 4. Headless entry points

| Command | Runs | Writes |
|---|---|---|
| `python experiments\development\run_dev.py [--no-llm]` | one full 5-agent run on GSE202768 | `outputs/traces/dev_<UTC>.json` |
| `python reference\run_deseq2.py` | PyDESeq2 NB GLM (GSE202768, `~group_dev`) | `reference/outputs/GSE202768/de_results.csv`, `qc_summary.json` |
| `python reference\run_enrichment.py` | GSEApy enrichr (GO / Reactome / KEGG) | `reference/outputs/GSE202768/enrichment_*.csv` |
| `python tools\download_datasets.py [--only ACC]` | GEO FTP fetch into `data/raw/` | raw dataset files |
| `python scripts\generate_pdac_dataset.py` | regenerate the seeded synthetic test matrix | `data/test_datasets/PDAC_gemcitabine_counts.csv` |
| `python evaluation\baselines\run_all_baselines.py` | 3 architectures (LLM-only / single-tool / 5-agent) | `outputs/tables/architecture_comparison.csv` + traces |
| `python evaluation\ablations\run_ablations.py --dataset GSE202768` | 5 ablation configurations | `outputs/tables/ablation_results.csv` + traces |
| `python evaluation\robustness\run_robustness.py` | adversarial stress tests R1–R4 | `outputs/tables/robustness_results.csv` |
| `python evaluation\run_all_datasets.py` | full system on 4 datasets (generalization) | `outputs/tables/dataset_generalization.csv` + traces |
| `python evaluation\metrics\generate_all_eval_plots.py` | ROC/pr/confusion/ablation plots | `outputs/figures/*.png` |

---

## 5. Environment variables (`.env.example`)

| Var | Default | Purpose |
|---|---|---|
| `BACKEND_HOST` / `BACKEND_PORT` | `127.0.0.1` / `8000` | FastAPI bind |
| `FRONTEND_PORT` | `5173` | Vite dev server |
| `LLM_SERVER_ENDPOINT` | `http://127.0.0.1:8080` | llama.cpp OpenAI-compatible endpoint |
| `DEFAULT_MODEL` | `gemma-3-4b` | model id fallback |
| `LLM_TEMPERATURE` / `LLM_MAX_TOKENS` / `LLM_TIMEOUT_SECONDS` | `0.1` / `1500` / `300` | inference hyper-parameters |
| `VRAM_BUDGET_GB` / `CONTEXT_WINDOW_TOKENS` | `8.0` / `8192` | resource guards |
| `DATA_DIR` / `OUTPUTS_DIR` / `TABLES_DIR` / `FIGURES_DIR` / `REPORTS_DIR` / `TRACES_DIR` | `./data`, `./outputs`, … | artifact locations |
| `UPLOAD_DIR` | `./data/uploads` | legacy upload path name (the server actually writes to `outputs/uploads/` — kept for compatibility) |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | reserved for the roadmap vector store (not used by the deployed engine) |

---

## 6. Known interface quirks (honesty ledger)

* `use_critic` is accepted into request validation but not read anywhere in the current dispatch
logic — the critic is always on in the recorded traces, and the live engine carries narrative audit
text. (Roadmap: wire it to a real toggle in the live path.)
* Requests with `custom_filename` now resolve correctly from `outputs/uploads/` (was a known
`NameError` on `UPLOAD_DIR`, fixed 2026-10).
* `agents/computational.py::run_computation` accepts but ignores its `top_n_genes/top_n_pathways/padj_thresh`
kwargs — downstream defaults (25 genes / 5 pathways per source / padj 0.05) always apply.
* The four benchmark `/api/run` responses are recorded-trace **replays** (not fresh LangGraph
invocations). For fresh computation use the live upload path or the headless entry points.
See [docs/RESULTS.md §10](RESULTS.md) and [docs/EXPLAINABILITY.md §8](EXPLAINABILITY.md).
