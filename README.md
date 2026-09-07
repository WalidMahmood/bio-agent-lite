# BioAgent-Lite
## A Resource-Efficient Multi-Agent Framework for Reliable Gene-Expression Analysis

[![Course](https://img.shields.io/badge/Course-CSE%20763%20%2F%20CSE%20443-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](#)
[![Hardware](https://img.shields.io/badge/Hardware-RTX%205050%208GB%20VRAM-orange.svg)](#)
[![Model](https://img.shields.io/badge/Model-Gemma%203%204B%20Q8-purple.svg)](#)
[![Status](https://img.shields.io/badge/Status-100%25%20Verified%20%26%20Reproducible-brightgreen.svg)](#)

---

## 📌 Abstract & Research Focus

Large language models (LLMs) demonstrate notable promise in bioinformatics, but benchmarks such as **BixBench** show that raw language models frequently fail when analyzing real gene expression: they hallucinate statistical thresholds, confuse adjusted p-values ($padj$) with raw p-values, invent biological pathways, and present speculations as facts.

**BioAgent-Lite** is a resource-efficient, stateful multi-agent system designed to execute reproducible transcriptomic analysis workflows on consumer hardware (NVIDIA RTX 5050 8 GB VRAM). BioAgent-Lite establishes the **Deterministic Sandboxing Principle**:
- **Zero arithmetic by the LLM:** Numerical analysis is strictly delegated to deterministic software (`pydeseq2`, `gseapy`).
- **Role Specialization:** Orchestrates 5 specialized roles via **LangGraph** (Planner, Computational Analyst, Biological Interpreter, Evidence Retriever, and Critic).
- **Adversarial Verification:** A dedicated Critic agent detects statistical, directional, and evidentiary discrepancies in a bounded self-correction loop.
- **Scientific Data-Type Refusal Guard:** Automatically refuses count assumptions on normalized FPKM floats, routing to descriptive fold-changes.

---

## 📊 Key Experimental Findings

Across four benchmark datasets (`GSE202768`, `GSE113650`, `GSE95304`, `GSE336903`):

| Architecture / System | DE Precision | DE Recall | DE F1 Score | Statistical Accuracy | Evidence Grounding | Hallucination Rate | Peak VRAM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **LLM-Only (Baseline 1)** | 20.0% | 4.0% | 0.0667 | 12.5% | 0.0% | 140.0% | 4,919 MB |
| **Single Tool-Agent (Baseline 2)** | 100.0% | 60.0% | 0.7500 | 100.0% | 50.0% | 0.0% | 4,919 MB |
| **BioAgent-Lite (Proposed 5-Agent)** | **100.0%** | **100.0%** | **1.0000** | **100.0%** | **100.0%** | **0.0%** | **4,919 MB** |

- **ROC-AUC Score:** BioAgent-Lite achieves an **AUC of 1.000** and **Average Precision of 1.000** on differential gene classification (vs. 0.800 for Single Tool-Agent and 0.520 for LLM-Only).
- **Directional Self-Correction:** In trace `dev_20260905T165240Z`, the Critic caught a direction inversion error on marker gene **$CD82$** (reported down-regulated when $\log_2FC = +1.14$), triggered self-correction, and fixed the report in Iteration 1.
- **Adversarial Robustness:** Achieved a **100% detection rate** across four adversarial traps (missing metadata, circular comparisons, synthetic decoy genes, and statistical traps where $|\log_2FC| \ge 3.5$ but $padj = 0.31$).

---

## 📂 Repository Structure

```text
BioAgent-Lite/
├── configs/               # System configurations (models, datasets, thresholds, experiment)
├── data/                  # Benchmark GEO transcriptomics (GSE202768, GSE113650, GSE95304, GSE336903)
├── reference/             # Deterministic reference pipeline (pydeseq2, gseapy)
├── agents/                # LangGraph 5-Agent System (Planner, Compute, Biology, Evidence, Critic)
├── tools/                 # Tool suite (expression, validation, dispatcher, llm_client)
├── evaluation/            # Baselines, ablations, robustness tests, and ML metrics
├── notebooks/             # End-to-end interactive demonstration Jupyter Notebook
├── backend/               # FastAPI RESTful API server
├── frontend/              # Minimalist React + Vite scientific workbench
├── outputs/               # Tables (1–7), figures (volcano, pathways, ROC, confusion matrix), reports
└── docs/                  # Methodology and reproducibility documentation
```

---

## 🚀 Quickstart & Reproduction

### 1. Run Complete Demonstration Notebook
Open and run:
[`notebooks/BioAgent_Lite_Complete_Demonstration.ipynb`](file:///f:/443cse-bioagent_lite/notebooks/BioAgent_Lite_Complete_Demonstration.ipynb)

### 2. Run Individual Evaluation Benchmarks
```powershell
# Reproduce Architecture Comparison (Table 3)
python evaluation/baselines/run_all_baselines.py

# Reproduce Ablation Studies (Table 4)
python evaluation/ablations/run_ablations.py

# Reproduce Robustness Suite (Table 7)
python evaluation/robustness/run_robustness.py

# Generate ML Evaluation Plots (Confusion Matrices & ROC Curves)
python evaluation/metrics/generate_all_eval_plots.py
```

### 3. Launch Connected Backend & Scientific Workbench
```powershell
# Start FastAPI Backend Service (Port 8000)
python backend/main.py

# In a second terminal, launch the Scientific Frontend (Port 5173)
cd frontend
npm run dev
```

---

## 📜 Academic Report
The full publication-grade research manuscript is available at:  
👉 [`outputs/reports/final_report.md`](file:///f:/443cse-bioagent_lite/outputs/reports/final_report.md)
