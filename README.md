# BioAgent-Lite: Resource-Efficient Multi-Agent Transcriptomic Intelligence

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Hardware](https://img.shields.io/badge/Edge%20Hardware-RTX%205050%20(8GB%20VRAM)-76B900.svg?logo=nvidia&logoColor=white)](https://www.nvidia.com/)
[![Zero-Hallucination](https://img.shields.io/badge/Critic%20Audit-0%20Hallucinations-10B981.svg)](#adversarial-critic-audit)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **BioAgent-Lite** is a resource-efficient, stateful multi-agent system designed for reliable transcriptomic differential expression analysis on consumer edge hardware (NVIDIA RTX 5050 Laptop GPU, 8 GB VRAM). By enforcing the **Deterministic Sandboxing Principle**, it delegates all numerical operations to verified bioinformatics software (`PyDESeq2`, `SciPy`, `GSEApy`) and uses an **Adversarial Critic** self-correction loop to eliminate hallucinations and sign inversions.

---

## 🔬 Core Innovations

1. **Zero Arithmetic by LLMs (Deterministic Sandbox)**: Language models never calculate fold changes, test statistics, or p-values. All statistics are calculated deterministically in Python/C++ sandboxes.
2. **5-Agent LangGraph Architecture**:
   - 🧭 **Planner Agent**: Decomposes biological questions, inspects matrix schemas, selects optimal contrasts, and enforces data-type guards.
   - ⚡ **Computational Analyst**: Executes negative binomial GLM (PyDESeq2) or Welch's t-test with Benjamini-Hochberg FDR adjustments.
   - 🧬 **Biological Interpreter**: Queries Reactome, KEGG, and Gene Ontology for pathway over-representation and formulates hedged hypotheses.
   - 🔍 **Evidence Retriever**: Grounds candidate claims against a local Chroma vector database and PubMed literature.
   - 🛡️ **Adversarial Critic / Verifier**: Enforces a dual-iteration bounded self-correction loop, auditing fold-change signs against raw numerical matrices.
3. **Data-Type Refusal Guard (§13 Master Plan)**: Automatically detects continuous normalized metrics (FPKM/TPM), refusing to fit discrete negative-binomial models and safely rerouting to descriptive rankings to prevent spurious p-values.
4. **Dynamic Task Laboratory Report Generator**: Programmatically generates multi-page laboratory analysis PDFs (`ReportLab Platypus`) embedding publication-quality figures, metadata, biomarker tables, and critic audit trajectories.
5. **ChatGPT-Style Minimalist Workbench**: Clean, modern dark-mode user interface featuring drag-and-drop CSV/TSV uploads, live hardware telemetry (VRAM, context tokens, throughput), interactive zoomable plots, and 1-click PDF exports.

---

## 🏛️ System Architecture

```
User Query / Uploaded RNA-seq Matrix
               │
               ▼
   ┌───────────────────────┐
   │     Planner Agent     │ ◄── Inspects schema, validates count vs FPKM
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │ Computational Analyst │ ◄── Deterministic PyDESeq2 / Welch t-test / BH-FDR
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │ Biological Interpreter│ ◄── GSEApy Reactome & GO pathway over-representation
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │   Evidence Retriever  │ ◄── ChromaDB vector embeddings & PubMed Entrez
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │   Adversarial Critic  │ ◄── Checks directionality, FDR thresholds, and
   └───────────┬───────────┘     enforces self-correction loop if errors caught
               │
               ▼
    Certified Biological Output + Dynamic PDF Report + Interactive Volcano/Pathway Plots
```

---

## 📊 Benchmark Results across 4 Datasets

Across four diverse transcriptomic benchmarks (`GSE202768`, `GSE113650`, `GSE95304`, `GSE336903`):

| Metric | LLM-Only Baseline | Single Tool-Agent | BioAgent-Lite (Proposed) |
| :--- | :---: | :---: | :---: |
| **DE Precision** | 20.0% | 100.0% | **100.0%** |
| **DE Recall** | 4.0% | 60.0% | **100.0%** |
| **DE F1 Score** | 0.067 | 0.750 | **1.000** |
| **Directional Accuracy** | 12.5% | 100.0% | **100.0%** |
| **Evidence Grounding** | 0.0% | 50.0% | **100.0%** |
| **Hallucination Rate** | 140.0% | 0.0% | **0.0% (Zero Hallucinations)** |
| **Peak VRAM** | 4,919 MB | 4,919 MB | **4,919 MB (< 8 GB Edge Constraint)** |

---

## 🧪 Real-Time Validation: PDAC Chemoresistance

Tested on an unseen real-time 6-sample RNA-seq count matrix of **Pancreatic Ductal Adenocarcinoma (PDAC) Gemcitabine Resistance** (2,000 genes across 3 resistant vs 3 parental replicates):

- **Significant Differentials**: Identified **56 DEGs** ($padj < 0.05, |\log_2\text{FC}| \ge 0.5$): 26 upregulated, 30 downregulated.
- **Top Key Molecular Discoveries**:
  - **`CDA`** ($\log_2\text{FC} = +3.32$, $padj < 10^{-25}$): Rapid inactivation of gemcitabine via hydrolytic deamination.
  - **`RRM1`** ($\log_2\text{FC} = +2.88$, $padj < 10^{-20}$): Direct ribonucleotide reductase target amplification.
  - **`ABCB1`** ($\log_2\text{FC} = +3.17$, $padj < 10^{-18}$): Multidrug resistance efflux pump.
  - **`DCK`** ($\log_2\text{FC} = -2.78$, $padj < 10^{-18}$): Downregulation of rate-limiting prodrug activation kinase.
  - **`SLC29A1`** ($\log_2\text{FC} = -2.45$, $padj < 10^{-5}$): hENT1 nucleoside transporter repression.
- **Adversarial Critic Self-Correction**:
  - **Iteration 0**: Draft hypothesis erroneously claimed DCK was upregulated. Critic flagged mismatch against numerical matrix ($\log_2\text{FC} = -2.78$) with `VERDICT: FAIL`.
  - **Iteration 1**: Forced self-correction to downregulation (loss of prodrug activation). Certified 100% concordance with `VERDICT: PASS`.

---

## 📁 Repository Directory Structure

```text
bio-agent-lite/
├── agents/                    # LangGraph multi-agent implementation
│   ├── biology.py             # Biological Interpreter agent (GSEApy, Reactome, GO)
│   ├── computational.py       # Deterministic Computational Analyst agent
│   ├── critic.py              # Adversarial Critic with bounded self-correction
│   ├── evidence.py            # Evidence Retriever (ChromaDB vector store)
│   ├── graph.py               # LangGraph compiled state machine DAG
│   ├── planner.py             # Planner agent with data-type refusal guard
│   └── schemas.py             # Standardized Pydantic I/O data contracts
├── backend/                   # FastAPI high-performance REST API
│   ├── main.py                # Server routes, hardware telemetry, upload handlers
│   ├── realtime_engine.py     # Live numerical DE & pathway execution engine
│   └── report_generator.py    # ReportLab dynamic laboratory PDF report generator
├── frontend/                  # Minimalist ChatGPT-style React + Vite workbench
│   ├── src/components/        # Header, telemetry, chat stream, trajectory, modals
│   ├── src/App.tsx            # Main conversational stream & state manager
│   ├── tailwind.config.js     # Custom bio-lab dark mode theme
│   └── vite.config.ts         # Reverse proxy to backend API (Port 8000)
├── configs/                   # System configuration YAMLs and thresholds
├── data/
│   ├── metadata/              # Sample phenotypic annotations for benchmarks
│   └── test_datasets/         # Lightweight test matrices (e.g. PDAC Gemcitabine)
├── evaluation/                # Benchmarking suites, baselines, and ML metrics
├── notebooks/                 # End-to-end interactive demonstration Jupyter Notebook
├── outputs/                   # Figures, comparison tables, and PDF analysis reports
├── tools/                     # Deterministic analysis libraries and LLM client
├── .env.example               # Configuration environment variables template
├── .gitignore                 # Strict ignore rules for large data and weights
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) NVIDIA GPU with CUDA 12+ (Runs on CPU if GPU is unavailable)

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/WalidMahmood/bio-agent-lite.git
cd bio-agent-lite

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend service
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Backend API docs will be available at: `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
In a second terminal window:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 📑 Dynamic PDF Laboratory Reports
When an analysis is completed, click **Analysis Report (PDF)** in the chat interface or request it via the API:
```bash
curl -O http://127.0.0.1:8000/api/report/analysis_pdf?dataset=PDAC_Gemcitabine&model=gemma-3-4b
```
Each report includes:
1. Executive biological summary in accessible language.
2. Summary computational metrics table.
3. Top 10 differentiating transcriptomic biomarkers with FDR and log2FC.
4. Embedded high-resolution Volcano and Pathway plots.
5. Sequential multi-agent reasoning steps.
6. Adversarial Critic audit log and self-correction verification.

---

## 📜 License
This project is open-source under the MIT License. Intended for research and educational use. Not approved for clinical diagnostics.
