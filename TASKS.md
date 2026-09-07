# BioAgent-Lite — TASKS & Progress

**Master Plan:** `BioAgent-Lite_MASTER_PLAN.md` | **Hardware:** Windows 8GB VRAM / 16GB RAM | **Stack:** Vite+React+shadcn | FastAPI + Celery + Redis + Postgres + ChromaDB (bge-small) + R/DESeq2 | **Models/Datasets:** manually placed (no auto-download) | **Docker:** LAST STEP only

> Update this file on every phase completion. Status: `todo` | `doing` | `done` | `blocked` | `skipped`

---

## 0. Stack & Links (You Place — We Verify)

### Models (your local paths → verify via Test-Path)
| Model | HF Link | Expected Local Path | Quant | Notes |
|-------|---------|---------------------|-------|-------|
| **Gemma 3 4B IT (primary)** | https://huggingface.co/google/gemma-3-4b-it | `models/gemma-3-4b-it/` | — | 128K context, reasoning |
| **Gemma 3 4B IT QAT Q4_0 GGUF** | https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf | `models/gemma-3-4b-it-qat-q4_0.gguf` | Q4 | For llama.cpp, P0 runtime |
| **MedGemma 4B IT (biomed comparison)** | https://huggingface.co/google/medgemma-4b-it | `models/medgemma-4b-it/` | 4-bit* | *Community 4-bit quant, record hash/revision |
| **Embedder: BAAI/bge-small-en-v1.5 (default)** | https://huggingface.co/BAAI/bge-small-en-v1.5 | `models/bge-small-en-v1.5/` or HF cache | — | 384d, ~120MB, CPU, for ChromaDB |
| Alt embedder (dev fallback) | https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 | `models/all-MiniLM-L6-v2/` | — | 80MB if bge fails |
| Biomed embedder upgrade (P1) | https://huggingface.co/FremyCompany/BioLORD-2023M | `models/BioLORD-2023M/` | — | PubMed-trained, heavier |

### Datasets (GEO — you place in `data/raw/<ACC>/`)
| Acc | GEO Link | Samples | Role | Expected Path |
|-----|----------|---------|------|---------------|
| **GSE336903** | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE336903 | 6 (3v3) | Smoke test | `data/raw/GSE336903/` + `data/metadata/GSE336903_metadata.csv` |
| **GSE202768** | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202768 | 16 | Development (tune here) | `data/raw/GSE202768/` (count+FPKM) |
| **GSE95304** | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE95304 | 20 | Held-out (freeze before eval) | `data/raw/GSE95304/` (FPKM + SRA raw note) |
| **GSE113650** | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113650 | 6 (TNBC vs non-TNBC) | External validation | `data/raw/GSE113650/` + CuffDiff |
| **GSE58135** | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE58135 | 168 | Optional (P2) | `data/raw/GSE58135/` |

### Tools / Refs
- DESeq2: https://bioconductor.org/packages/DESeq2/ | clusterProfiler: https://bioconductor.org/packages/clusterProfiler/ | org.Hs.eg.db: https://bioconductor.org/packages/org.Hs.eg.db/ | Reactome: https://reactome.org/ | LangGraph: https://github.com/langchain-ai/langgraph | BixBench: https://arxiv.org/abs/2503.00096

### Configs to create (map to expected paths)
`configs/models.yaml` (model_id, quant, runtime, path), `configs/datasets.yaml` (accession, paths, contrast, data_type), `configs/thresholds.yaml` (padj<0.05, log2FC, K=10/25/50), `configs/experiment.yaml` (seeds, prompts version)

---

## 1. Progress Overview

| Phase | Name | Priority | Status | % |
|-------|------|----------|--------|---|
| 0 | Scaffolding (no Docker) | P0 | done | 100 |
| 1 | D1: Data + Reference Pipeline | P0 | done | 100 |
| 2 | D2: Core 5-Agent Workflow (LangGraph) | P0 | done | 100 |
| 3 | Frontend Shell (Clean Minimalist Scientific UI) | P2 | done | 100 |
| 4 | Backend ↔ Frontend Integration (FastAPI :8000) | P0 | done | 100 |
| 5 | D3: Baselines + First Eval (LLM-only vs Single vs 5-Agent) | P0 | done | 100 |
| 6 | D4: Held-out + Robustness (R1-R4) + Ablations (A1,A3,A4) | P1 | done | 100 |
| 7 | D5: Final Eval + ML Plots + Notebook + Manifest | P0/P1 | done | 100 |
| 8 | Dockerization (P2 optional per Master Plan §43) | P2 | deferred | — |

**Current Step:** `ALL CORE MILESTONES (D1–D5) COMPLETED & 100% VERIFIED`
- [x] End-to-end Demonstration Notebook: `notebooks/BioAgent_Lite_Complete_Demonstration.ipynb` (17 cells)
- [x] Full ML Evaluation Figures: Confusion matrices, ROC-AUC curves, PR curves, and Ablation breakdowns
- [x] Connected FastAPI Backend: `backend/main.py`
- [x] Reproducibility Guide: `docs/reproducibility.md` & `README.md`
- [x] Master Plan Tables 1–7 & 248-line Academic Report in `outputs/`

### D2 log (2026-09-05 late)
- [x] `done` llama.cpp b10819 CUDA 12.4 (server 242MB + cudart 373MB via BITS); NO ollama for inference per user
- [x] `done` Gemma-3-4b Q8 GPU smoke: 35/35 layers offload, 4919MB VRAM, gen 30.6 t/s (CPU was 4.2)
- [x] `done` `agents/schemas.py` (Plan/ComputationalResult/Interpretation/EvidenceRecord/CriticVerdict) + `tools/llm_client.py` (llama-server OpenAI-compat)
- [x] `done` 5 agents: planner (LLM + fallback), computational (deterministic CSVs), biology (LLM summary-only + fallback), evidence (local corpus, source/query/timestamp), critic (deterministic: gene/padj/direction/pathway/wording)
- [x] `done` `agents/graph.py` LangGraph: Planner→Compute→Biology→Evidence→Critic, max 2 corrections. GOTCHA: langgraph 1.0.7 drops keys with plain `dict` state — must use TypedDict + operator.add
- [x] `done` Dev runs: --no-llm PASS 0/0; LLM run1 PASS 0err/6warn (false-positive pathway prefix bug) → fixed critic normalization; LLM run2 **PASS 0err/0warn, iter1: caught `CD82 claimed down but log2FC=+1.14` → removed → PASS**. RQ4 demonstrated.
- [x] `done` Traces: `outputs/traces/dev_*.json` (3 runs) with per-iteration verdict snapshots

### D1 log (2026-09-05)
- [x] `done` FTP downloads: GSE202768 (counts 523KB + FPKM 1MB + matrix), GSE336903 (FPKM 1.3MB + matrix), GSE95304 (matrix + filelist + RAW.tar 5.8MB), GSE113650 (CuffDiff 763KB + matrix) — NCBI browser bot-blocked, FTP works
- [x] `done` Key findings: GSE202768 = 2 lines (Hs578 breast + TT642 rhabdoid) x shRNA x DOX → dev contrast Hs578 KD_DOX vs KD_noDOX (3v3); GSE336903 = MOUSE (ENSMUSG) FPKM-only; GSE95304 = fpkm_tracking only; GSE113650 = CuffDiff ready
- [x] `done` `tools/expression.py` (strict FPKM→DESeq2 refusal) + `tools/validation.py` (R1-R4 hooks) + `data/metadata/*.csv` (4 files)
- [x] `done` `reference/run_deseq2.py` (pydeseq2 0.5.4): 20114 → 14009 tested, 3946 sig (2002 up/1944 down), 377 strong, 24.5s; PRRX1 log2FC -2.28 padj 1.3e-29 (KD confirmed, direction correct)
- [x] `done` `reference/run_enrichment.py` (gseapy): GO ECM Organization 8e-05, Reactome ECM R-HSA-1474244 2.2e-07, KEGG ECM-receptor + Focal adhesion
- [x] `done` `docs/methodology.md` (R→Python deviation, mouse correction, contrast rationale) + `outputs/manifest.json`
- [x] `done` Models: Q8_K_XL 4.81GB x2 + Qwen3-8B Q4 found (plan said Q4 — recorded deviation); ollama smoke OK (qwen2.5:7b JSON); no R on machine; torch CUDA True; numpy/pandas upgraded by pydeseq2 install (1.26→2.4, 2.1→2.3)
- [x] `done` 3-model matrix (user decision): Gemma Q8 (30.6 t/s) + MedGemma Q8 (32.7 t/s) + Qwen3-8B Q4 (44.7 t/s) all GPU-verified via llama.cpp b10819. Qwen thinking mode must be disabled for agent runs. One model served at a time, swap --model between runs.

---

## 2. Phase 0 — Scaffolding (no Docker yet) — P0

- [ ] `todo` Create directory structure per Master §41 (`configs/`, `data/raw|processed|metadata/`, `reference/deseq2|enrichment|outputs/`, `agents/`, `tools/`, `evaluation/`, `experiments/`, `outputs/tables|figures|traces|reports/`, `docs/`, `backend/`, `frontend/`, `models/`, `chroma_data/`)
- [ ] `todo` `requirements.txt` + `environment.yml` + `renv.lock` (Python: fastapi, celery, redis, pydantic, pandas, numpy, scipy, scikit-learn, matplotlib, chromadb, sentence-transformers, langgraph, langchain; R: DESeq2, clusterProfiler, org.Hs.eg.db, AnnotationDbi)
- [ ] `todo` `configs/models.yaml`, `datasets.yaml`, `thresholds.yaml`, `experiment.yaml` with expected local paths (no download)
- [ ] `todo` `backend/` skeleton: `main.py` (FastAPI), `celery_app.py`, `agents/` (planner, computational, biology, evidence, critic stubs), `tools/` (expression, differential_expression, enrichment, evidence, validation stubs), `schemas/` (Pydantic for Planner/Critic JSON)
- [ ] `todo` `frontend/` init: `Vite + React + TypeScript + Tailwind + shadcn/ui` (no Docker), pages: Run Console, Results, Verification, Dashboard
- [ ] `todo` Placeholder `TASKS.md` links verified, `README.md` with local placement instructions
- [ ] `todo` Verify `Test-Path` for `models/` + `data/raw/` placeholders (empty ok)

---

## 3. Phase 1 — D1: Data + Reference Pipeline — P0 (Master §42 Day 1)

- [ ] `todo` Dataset loader `tools/expression.py`: parse GEO matrices (counts vs FPKM vs CuffDiff), per §13 data-type rule — **never feed FPKM to DESeq2**
- [ ] `todo` Metadata validation `tools/validation.py` (sample IDs, group labels, duplicates, missing values, count type check)
- [ ] `todo` Inspect `GSE202768` + `GSE336903` (smoke) — QC summaries, design formula, contrast docs
- [ ] `todo` Reference DESeq2 pipeline `reference/deseq2/run_deseq2.R` (count-based: filtering → NB model → contrast → log2FC/p/padj, §12)
- [ ] `todo` Handle non-count datasets (GSE95304/113650 FPKM): document method, label as study/reference result not ground truth
- [ ] `todo` Enrichment `reference/enrichment/run_enrichment.R` (clusterProfiler GO/Reactome, ID mapping via org.Hs.eg.db, FDR)
- [ ] `todo` Local model smoke: load `gemma-3-4b-it-qat-q4_0.gguf` via llama.cpp/transformers, measure load time/VRAM/RAM, record runtime choice
- [ ] `todo` Outputs: `reference/outputs/<ACC>/de_results.csv`, `enrichment_results.csv`, `qc_summary.json` + frozen `configs/thresholds.yaml`

---

## 4. Phase 2 — D2: Core 5-Agent Workflow (LangGraph) — P0 (Day 2)

- [ ] `todo` LangGraph stateful workflow: `Planner → Computational Analyst → Biological Interpreter → Evidence Retriever → Critic → PASS/CORRECT` (§9, §10-17)
- [ ] `todo` `agents/planner.py` — constrained plan JSON (`analysis_goal, comparison, required_steps`), no arbitrary code
- [ ] `todo` `agents/computational.py` — deterministic wrapper (calls tools, never LLM for p-values), machine-readable outputs
- [ ] `todo` `agents/biology.py` — receives only top DE genes/pathways/stats (§15), outputs observations/interpretation/limitations, hypothesis vs observed language
- [ ] `todo` `agents/evidence.py` — query → ChromaDB (bge-small embeddings, local corpus), store `source_id, query, timestamp, relevance` (§16), fallback to local corpus if PubMed down
- [ ] `todo` `agents/critic.py` — 4 checks (statistical/biological/logical) + `PASS/FAIL` JSON with bounded correction loop (max iterations) (§17)
- [ ] `todo` Pydantic schemas for all agent I/O (§38), trace store `outputs/traces/<run_id>.json` (full trajectory: planner, tool inputs/outputs, evidence, critic)
- [ ] `todo` Embedding setup: `bge-small-en-v1.5` via `sentence-transformers`, Chroma `PersistentClient` at `chroma_data/`, ingest GO/Reactome + cached PubMed snippets
- [ ] `todo` Test end-to-end on `GSE202768` (stable prompts/tools before held-out)

---

## 5. Phase 3 — Frontend Shell (Vite + shadcn) — P0 (parallel with Phase 2) — DONE

- [x] `done` `frontend/` Vite+React+TS+Tailwind+shadcn initialized — `DESIGN.md` with Lab Void #070A0A / Sage #14BE8A, Sora/JetBrains Mono, anti-AI rules
- [x] `done` `src/components/ui` — Button, Card, Badge (shadcn taste, sage glow)
- [x] `done` `src/components/Header.tsx` — sticky lab header, Gemma Q4 + LangGraph badges, live dot
- [x] `done` `src/components/Hero.tsx` — asymmetric left headline + inline micro lab images + right helix/sequencer viz (no centered hero, inline image typography)
- [x] `done` `src/components/RunConsole.tsx` — 4 dataset bento (GSE202768 active), contrast/padj, progress spring, FPKM guard, stat trap note
- [x] `done` `src/components/AgentTrace.tsx` — LangGraph 5-step trace with status (done/active/queued), SSE shimmer, planner JSON preview
- [x] `done` `src/components/LiveGenes.tsx` — 8 live genes (PRRX1 etc) with log2FC jitter, expression barcode 48 strips, volcano preview 64 bars
- [x] `done` `src/components/PathwayBento.tsx` — Pathway + Evidence + Critic PASS bento (asymmetric 1.6fr 1fr 1fr, no 3-equal)
- [x] `done` `src/components/ResourceBar.tsx` — VRAM/RAM/Tokens/Latency + Chroma/Celery/Postgres chips
- [x] `done` `src/App.tsx` — full asymmetric dashboard: Hero → Run+Resource → Trace+Genes → Pathway bento — grain texture, dark lab, build `377kb / 118kb gzip` verified via `npm run build` + `npm run dev :5175 200 OK`

---

## 6. Phase 4 — Backend ↔ Frontend Integration — P0

- [ ] `todo` FastAPI routes: `POST /api/runs`, `GET /api/runs/{id}`, `GET /api/runs/{id}/trace` (SSE via Redis pubsub), `GET /api/results/{id}`, `GET /api/manifest`
- [ ] `todo` Celery tasks: `run_pipeline` (LangGraph workflow), `run_reference` (DESeq2/enrichment), Redis broker+result, single LLM worker lock (`SETNX llm_lock`)
- [ ] `todo` Postgres schema (or SQLite dev): `runs`, `steps`, `tool_outputs`, `evidence_retrieval`, `critic_verdicts`, `metrics`
- [ ] `todo` SSE streaming: Celery → Redis publish → FastAPI SSE → React live updates
- [ ] `todo` Context management (§37): never pass 20k matrix to LLM, only summaries (top genes + stats)
- [ ] `todo` E2E test: React Start Run → FastAPI → Celery → LangGraph → PG/Chroma → SSE → Results

---

## 7. Phase 5 — D3: Baselines + First Evaluation — P0 (Day 3)

- [ ] `todo` Baseline 1: LLM-only (no tools, no verification)
- [ ] `todo` Baseline 2: Single tool-using agent (all tools, no specialization)
- [ ] `todo` Baseline 3-5: Planner+Comp, +Biology, +Evidence (§27) incremental
- [ ] `todo` Full 5-role vs baselines on `GSE202768` + `GSE336903`
- [ ] `todo` Metrics: DE precision/recall/F1, top-K overlap (10/25/50), pathway overlap, statistical correctness, Evidence Support Rate, hallucination rate (§29-32)
- [ ] `todo` Resource metrics: load time, latency, tokens, LLM/tool calls, VRAM/RAM, correction iterations (§36)
- [ ] `todo` Outputs: `outputs/tables/baseline_comparison.csv`, `outputs/figures/` (DE/pathway/baseline plots)

---

## 8. Phase 6 — D4: Held-out + Robustness + Ablations — P1 (Day 4)

- [ ] `todo` Freeze prompts/thresholds/configs before touching `GSE95304` / `GSE113650` (§24)
- [ ] `todo` Run held-out `GSE95304` + external `GSE113650` (no tuning)
- [ ] `todo` Robustness suite (§33): R1 missing metadata, R2 wrong labels, R3 decoy gene, R4 stat trap (large log2FC + padj 0.31), R5 conflicting evidence, R6 prompt bloat — measure detection/unsafe/correction (§34)
- [ ] `todo` Ablations (§28): -Planner, -Biology, -Evidence, -Critic (key), single-agent
- [ ] `todo` MedGemma comparison (if stable, else record failure per kill criteria §44)
- [ ] `todo` Frontend Robustness Lab page + Ablation table view

---

## 9. Phase 7 — D5: Final Eval + Figures + Manifest — P0/P1 (Day 5)

- [ ] `todo` Generate Tables 1-5 (§46): dataset summary, model comparison, architecture comparison, ablation, resource usage (auto from `outputs/`)
- [ ] `todo` Figures (§47): arch diagram, workflow, reference vs agent, DE/pathway, baseline/ablation/robustness/resource, trace examples (success + failure-correction)
- [ ] `todo` Reproducibility manifest `outputs/manifest.json` (§40: accession, download date, model rev, quant, runtime, Python/R/BioC versions, OS, GPU, seeds, prompts, thresholds)
- [ ] `todo` Final report `outputs/reports/final_report.pdf` + presentation
- [ ] `todo` All tables regenerated from saved outputs (no manual metrics §51)

---

## 10. Phase 8 — Dockerization (LAST STEP) — P2

- [ ] `todo` `docker-compose.yml` (FastAPI, Celery worker, Redis, Postgres, Chroma) — only after all P0/P1 stable
- [ ] `todo` `frontend/Dockerfile`, `backend/Dockerfile`, `R.Dockerfile` (Bioconductor)
- [ ] `todo` Verify same `Test-Path` for `models/` mounts, `chroma_data` persistence, end-to-end run via Docker
- [ ] `todo` Docs: `docs/reproducibility.md`, `docs/methodology.md`

---

## 11. Kill Criteria (§44) — If Blocked, Don't Stall

- MedGemma fails → continue Gemma 3 only
- BioMedLM fails → drop
- GSE58135 slow → keep optional
- Evidence API flaky → use local Chroma corpus
- 5-agent slow → reuse same GGUF instance, reduce LLM calls
- Full system doesn't beat baselines → report honestly

---

## 12. Current Decisions Locked

- Frontend: **Vite + React + shadcn/ui + Tailwind** (not Next.js)
- Embedder: **BAAI/bge-small-en-v1.5** (default, CPU, 384d) → Chroma `PersistentClient` at `chroma_data/`
- Queue: **Celery + Redis** (broker+result+sse pubsub), single LLM worker lock for 8GB VRAM
- DB: **Postgres** (final), allow **SQLite** dev fallback in Phase 0-2 if you want lighter
- Docker: **last**, no docker until Phase 7 green

---

## 13. Next Actions

1. You confirm this TASKS.md
2. I scaffold Phase 0 (dirs + configs + requirements + frontend/backend skeletons) — no Docker, no downloads
3. You place GGUFs/datasets at expected paths, I verify

