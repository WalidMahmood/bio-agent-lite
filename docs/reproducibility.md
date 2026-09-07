# BioAgent-Lite: Reproducibility Guide

This document provides step-by-step instructions to reproduce all tables, figures, agent runs, and evaluation metrics reported in the **BioAgent-Lite** term paper for CSE 763 / CSE 443.

---

## 1. Environment & Hardware Specifications

- **Operating System:** Windows 11 / 10 (x64)
- **GPU:** NVIDIA GeForce RTX 5050 (8 GB VRAM, Compute Capability 8.9+, CUDA 12.4)
- **RAM:** 16 GB System Memory
- **Python Version:** 3.11.9
- **Inference Runtime:** `llama.cpp` CUDA 12.4 server (`llama-server.exe`)
- **Primary Model:** Google Gemma 3 4B IT (`models/gemma-3-4b-it-UD-Q8_K_XL.gguf`, 4.81 GB)

---

## 2. Directory Structure Verification (Master Plan §41)

All files strictly conform to the layout defined in Section 41 of `BioAgent-Lite_MASTER_PLAN.md`:

```text
BioAgent-Lite/
├── README.md                                  # Repository overview and quickstart
├── BioAgent-Lite_MASTER_PLAN.md               # Master Plan and experimental design
├── TASKS.md                                   # Phase tracking and progress log
├── requirements.txt                           # Python dependencies
│
├── configs/                                   # System configurations
│   ├── models.yaml                            # Model IDs, quantizations, VRAM budgets
│   ├── datasets.yaml                          # Accessions, paths, contrasts, data types
│   ├── thresholds.yaml                        # Significance thresholds (padj < 0.05, |log2FC| >= 1.0)
│   └── experiment.yaml                        # Reproducibility seeds and prompt versions
│
├── data/                                      # Benchmark transcriptomic data
│   ├── raw/                                   # GSE202768, GSE113650, GSE95304, GSE336903
│   ├── processed/                             # Formatted count and expression matrices
│   └── metadata/                              # Sample annotations and design factors
│
├── reference/                                 # Deterministic statistical references
│   ├── run_deseq2.py                          # Reference pydeseq2 execution script
│   ├── run_enrichment.py                      # Reference gseapy pathway script
│   └── outputs/                               # Saved reference CSV tables
│
├── agents/                                    # Multi-Agent LangGraph system
│   ├── schemas.py                             # Pydantic data contracts and claim taxonomy
│   ├── planner.py                             # Constrained Planner agent
│   ├── computational.py                       # Deterministic computational dispatcher
│   ├── biology.py                             # Evidence-hedged Biological Interpreter
│   ├── evidence.py                            # Lineage-tracking Evidence Retriever
│   ├── critic.py                              # 4-layer adversarial verification Critic
│   └── graph.py                               # Stateful LangGraph cyclic workflow
│
├── tools/                                     # Deterministic bioinformatics tool suite
│   ├── dispatcher.py                          # Tool execution & FPKM count-refusal guard (§13)
│   ├── expression.py                          # Expression matrix QC and inspection
│   ├── validation.py                          # Metadata and column validation
│   └── llm_client.py                          # Local llama.cpp OpenAI-compatible client
│
├── evaluation/                                # Benchmark and ablation suites
│   ├── baselines/                             # LLM-only and Single Tool-Agent baselines
│   ├── ablations/                             # -Critic, -Evidence, -Planner ablations
│   ├── robustness/                            # Adversarial stress tests (R1–R4)
│   └── metrics/                               # Metric calculation and ML plotting
│
├── notebooks/                                 # Interactive Jupyter walkthroughs
│   └── BioAgent_Lite_Complete_Demonstration.ipynb
│
├── backend/                                   # FastAPI backend service
│   └── main.py                                # API endpoints for tables, figures, health
│
├── frontend/                                  # React + Vite scientific workbench
│   └── src/App.tsx                            # High-density interactive UI
│
├── outputs/                                   # Final scientific deliverables
│   ├── tables/                                # Tables 1 to 7 (CSV)
│   ├── figures/                               # Volcano, pathways, confusion matrix, ROC
│   ├── traces/                                # Audited agent trajectory JSONs
│   ├── reports/                               # final_report.md
│   └── manifest.json                          # Machine-readable experiment manifest
│
└── docs/                                      # Methodology and documentation
    ├── methodology.md                         # Statistical and agent methodology
    └── reproducibility.md                     # This document
```

---

## 3. One-Line Reproduction Commands

### Step 1: Start Local Model Server (Optional for LLM Inference)
```powershell
llama.cpp\bin\llama-server.exe -m models\gemma-3-4b-it-UD-Q8_K_XL.gguf -ngl 99 -c 8192 --port 8080 --host 127.0.0.1
```

### Step 2: Reproduce Reference DESeq2 & Enrichment (Master Plan §12)
```powershell
python reference\run_deseq2.py
python reference\run_enrichment.py
```

### Step 3: Reproduce Architectural Baselines (Table 3)
```powershell
python evaluation\baselines\run_all_baselines.py
```

### Step 4: Reproduce Role Ablation Studies (Table 4)
```powershell
python evaluation\ablations\run_ablations.py
```

### Step 5: Reproduce Adversarial Robustness Suite (Table 7)
```powershell
python evaluation\robustness\run_robustness.py
```

### Step 6: Reproduce Multi-Dataset Generalization (Table 6)
```powershell
python evaluation\run_all_datasets.py
```

### Step 7: Generate All ML Evaluation Plots (Confusion Matrices, ROC, PR Curves)
```powershell
python evaluation\metrics\generate_all_eval_plots.py
```

### Step 8: Start Backend & Frontend Services
```powershell
# In terminal 1 (FastAPI backend):
python backend\main.py

# In terminal 2 (Vite frontend):
cd frontend
npm run dev
```

---

## 4. Verification Checkpoints

- **Table 3 Check:** Verify `outputs/tables/architecture_comparison.csv` shows BioAgent-Lite with Precision = 1.0, Recall = 1.0, F1 = 1.0, and Hallucination = 0.0%.
- **Figure Check:** Verify `outputs/figures/confusion_matrices.png` and `outputs/figures/roc_auc_curves.png` exist with publication-grade resolution.
- **Trace Check:** Verify `outputs/traces/dev_20260905T165240Z.json` documents the $CD82$ direction-inversion detection and surgical correction by the Critic.
- **Notebook Check:** Open `notebooks/BioAgent_Lite_Complete_Demonstration.ipynb` in VS Code or JupyterLab; run all cells sequentially to reproduce all outputs inline.
