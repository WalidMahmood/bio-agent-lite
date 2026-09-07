# BioAgent-Lite
## A Resource-Efficient Multi-Agent Framework for Reliable Gene-Expression Analysis

**Course:** CSE 763 Advanced Bioinformatics / CSE 443 Bioinformatics  
**Project type:** Machine Learning / Agentic Bioinformatics Term Project  
**Primary domain:** Transcriptomics / bulk RNA-seq  
**Benchmark focus:** Cancer and perturbation transcriptomics  
**Hardware target:** Windows machine, 8 GB VRAM, 16 GB RAM  
**Core constraint:** Local/open models and open-source/open-data software wherever practical

---

# 1. Project Overview

The goal of this project is to build and evaluate a small, locally deployable multi-agent system that can perform a controlled gene-expression analysis workflow and produce an evidence-supported biological interpretation.

The project is **not** intended to replace a complete bioinformatics pipeline with an LLM. The statistical and data-processing parts will be performed by established computational tools. The language model will mainly be used for planning, interpretation, evidence synthesis, and verification.

The central question is:

> **Can a specialized multi-agent architecture make a small local language model more reliable for gene-expression analysis than an LLM-only or single-agent approach?**

The project will focus on a reproducible workflow:

```text
RNA-seq expression data + metadata + biological question
                    |
                    v
          Metadata / input validation
                    |
                    v
          Differential expression
                    |
                    v
        Significant genes / statistics
                    |
                    v
        Functional / pathway analysis
                    |
                    v
       Evidence retrieval and grounding
                    |
                    v
        Biological interpretation
                    |
                    v
             Critic / verifier
                    |
                    v
        Evidence-supported final report
```

The main contribution is therefore not simply "using multiple agents." The contribution is the experimental investigation of whether **role specialization, deterministic bioinformatics tools, evidence grounding, and explicit verification** improve reliability under a small-model and low-resource setting.

---

# 2. Why This Problem

LLM-based agents are increasingly being investigated for computational biology. Existing work shows that agents can execute multi-step biological analyses, but also shows that current systems can fail on open-ended biological analysis, tool use, long analytical trajectories, and robustness to problematic inputs.

BixBench introduced more than 50 real-world computational-biology scenarios and nearly 300 open-answer questions. Its evaluation showed substantial limitations even for strong frontier models, demonstrating that biological data analysis is much harder than ordinary biomedical question answering.

More recent agent benchmarks for omics analysis also emphasize the importance of planning, executable analysis, retrieval, self-reflection, and robustness.

This creates a practical research opportunity:

> Instead of asking whether an LLM knows biology, test whether a small local model can participate in a controlled bioinformatics workflow where numerical analysis is delegated to deterministic tools and biological claims are explicitly checked.

The project therefore targets **reliability**, not just generation quality.

---

# 3. Problem Statement

A language model may produce a convincing biological explanation while making an incorrect statistical statement, misreading a comparison, inventing a pathway association, or treating an unsupported biological hypothesis as established fact.

A conventional statistical pipeline avoids many of these problems, but it does not provide natural-language planning, interpretation, evidence synthesis, or interactive reasoning.

We want to combine the strengths of both approaches:

```text
Established bioinformatics software
        +
Small local language model
        +
Specialized agent roles
        +
Evidence retrieval
        +
Explicit verification
```

The system should be able to answer a biological analysis request while keeping a clear separation between:

1. what was statistically calculated,
2. what was retrieved from biological resources,
3. what is an interpretation,
4. what is uncertain,
5. what the system rejected or corrected.

---

# 4. Research Gap and Project Positioning

This project is intentionally narrower than a general autonomous "AI scientist."

Existing work such as BixBench demonstrates that computational biology requires substantially more than biomedical question answering.

Our project instead focuses on one controlled but meaningful workflow:

> **Differential expression → functional/pathway analysis → evidence-grounded biological interpretation**

The research question is not:

> "Can an agent do all of bioinformatics?"

It is:

> "For a defined RNA-seq analysis workflow, does specialization and verification improve the reliability of a small local model?"

The project will also avoid claiming that the reference pipeline represents absolute biological truth. Different valid bioinformatics methods and assumptions can produce different results. We therefore use the term **reference analysis** for the reproducible statistical pipeline against which agent outputs are compared.

---

# 5. Objectives

## Primary objective

Build a resource-efficient multi-agent system that can perform a reproducible gene-expression analysis workflow and produce a biologically interpretable, evidence-supported report.

## Secondary objectives

1. Compare a general-purpose small model with a medical-domain small model.
2. Compare an LLM-only baseline with a tool-using single-agent baseline.
3. Evaluate the full multi-agent system.
4. Perform ablation studies to determine whether individual roles actually contribute.
5. Measure statistical correctness separately from biological interpretation quality.
6. Measure evidence support and hallucination/unsupported-claim rates.
7. Test robustness against deliberately corrupted or misleading inputs.
8. Measure computational cost: runtime, tokens, VRAM, RAM, and tool failures.
9. Keep the complete experiment reproducible on the available hardware.

---

# 6. Research Questions

### RQ1 — Does tool use improve correctness?

Does an LLM connected to deterministic bioinformatics tools perform better than an LLM asked to reason from supplied information alone?

### RQ2 — Does role specialization help?

Does the five-role architecture outperform a single general-purpose agent on the same tasks?

### RQ3 — Does evidence grounding reduce unsupported claims?

Does explicitly retrieving evidence before biological interpretation reduce unsupported or fabricated biological statements?

### RQ4 — Does a critic improve reliability?

Does a dedicated verification stage detect and correct statistical, logical, and evidential errors?

### RQ5 — Can the system work under low-resource constraints?

Can a quantized approximately 4B-parameter model provide useful agentic behavior on an 8 GB VRAM / 16 GB RAM Windows machine?

### RQ6 — Does the system generalize across experiments?

Does a workflow developed on one RNA-seq experiment remain useful on held-out experiments with different biological comparisons?

---

# 7. Hypotheses

### H1 — Tool augmentation

A tool-augmented agent will achieve higher statistical correctness than an LLM-only baseline because numerical analysis is performed by deterministic software.

### H2 — Specialization

The specialized multi-agent system will outperform a single-agent system on at least some reliability metrics.

### H3 — Evidence grounding

The Evidence Agent will reduce the proportion of biological claims that lack supporting evidence.

### H4 — Verification

The Critic Agent will improve error detection and reduce incorrect statistical or biological conclusions.

### H5 — Resource efficiency

A quantized small model will be capable of completing the defined workflow without requiring a cloud API or a large GPU.

These are hypotheses, not guaranteed outcomes. If an ablation does not improve performance, that result will be reported.

---

# 8. Scope

## Included

- Bulk RNA-seq / gene-expression analysis
- Metadata and input validation
- Differential expression
- Multiple-testing-aware significance
- Functional/pathway enrichment
- Biological interpretation
- Evidence retrieval
- Agent orchestration
- Verification / critique
- Robustness testing
- Baseline comparison
- Ablation studies
- Resource measurement
- Reproducible evaluation

## Not included in the core project

- Training a foundation model from scratch
- Large-scale fine-tuning
- Full single-cell RNA-seq analysis
- RNA velocity
- Spatial transcriptomics
- Variant calling
- Protein structure prediction
- Clinical diagnosis
- Clinical decision making
- Autonomous experimental execution
- Claiming medical-grade performance

Optional extensions are only considered after the core experiment is complete.

---

# 9. Final System Architecture

The architecture will contain five specialized roles.

```text
                         USER
                           |
                           v
                    +-------------+
                    |   PLANNER   |
                    +------+------+
                           |
                           v
                +----------------------+
                | COMPUTATIONAL        |
                | ANALYST              |
                | deterministic tools  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | BIOLOGICAL           |
                | INTERPRETER          |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | EVIDENCE             |
                | RETRIEVER            |
                +----------+-----------+
                           |
                           v
                +----------------------+
                | CRITIC / VERIFIER    |
                +----------+-----------+
                           |
                    PASS / CORRECT
                           |
                           v
                   FINAL REPORT
```

The system should be implemented as a stateful workflow rather than five unrelated chatbots.

LangGraph is a suitable orchestration option because it is an open-source, MIT-licensed framework for stateful agent workflows and supports Python. The exact library version used in the experiment will be recorded in the reproducibility manifest.

---

# 10. Agent Roles

## 10.1 Planner Agent

### Purpose

Convert a biological question and dataset description into a constrained analysis plan.

### Input

- Biological question
- Dataset metadata
- Available comparisons
- Available tools
- Data type
- Organism
- Constraints

### Output

A structured plan such as:

```json
{
  "analysis_goal": "...",
  "comparison": {
    "group_a": "...",
    "group_b": "..."
  },
  "required_steps": [
    "validate_metadata",
    "run_differential_expression",
    "run_enrichment",
    "retrieve_evidence",
    "verify_results"
  ]
}
```

### Restrictions

The Planner will not execute arbitrary code.

It selects from predefined tools.

This makes the workflow more reproducible and reduces the chance that the model invents an inappropriate analysis.

---

# 11. Computational Analyst

This is deliberately different from the LLM agents.

The Computational Analyst will be primarily a deterministic software layer.

### Responsibilities

- Load expression matrix
- Load metadata
- Validate sample identifiers
- Validate group labels
- Check missing values
- Check duplicated identifiers
- Check count/measurement type
- Generate basic QC summaries
- Run differential expression
- Apply multiple-testing correction
- Produce structured results
- Run functional/pathway analysis
- Produce machine-readable outputs

The LLM should never manually calculate p-values or fold changes.

The computational layer should calculate them.

---

# 12. Reference Statistical Analysis

## 12.1 Count-based RNA-seq

For datasets containing appropriate count data, the reference differential-expression analysis will use **DESeq2**.

DESeq2 models count data using a negative-binomial framework and estimates variance-mean dependence before testing for differential expression.

Reference workflow:

```text
Count matrix
    |
    v
Metadata validation
    |
    v
Low-count filtering
    |
    v
DESeq2 model
    |
    v
Contrast
    |
    +----> log2 fold change
    |
    +----> p-value
    |
    +----> adjusted p-value
    |
    v
Significant-gene set
```

The exact design formula and contrast will be determined from the dataset metadata and documented for each experiment.

A default significance rule may be:

```text
adjusted p-value < 0.05
```

with an explicitly documented effect-size criterion if used.

The threshold is a project parameter, not something the LLM is allowed to invent.

---

# 13. Important Data-Type Rule

Not every selected GEO dataset provides raw count data in the same format.

This is important.

### GSE202768

GEO provides processed expression data including gene-count and FPKM matrices. This makes it particularly suitable for developing the count-based pipeline.

### GSE95304

GEO provides processed FPKM data and raw data through SRA.

### GSE113650

GEO provides processed expression data and an associated CuffDiff result file.

### GSE58135

GEO provides a larger breast-cancer RNA-seq collection with processed/raw resources.

### GSE336903

GEO provides a processed FPKM matrix with six samples.

Therefore, we will **not feed FPKM values into DESeq2 as if they were raw counts**.

For datasets without suitable raw/count data, the analysis method will be explicitly documented and chosen according to the available data type. Where an original study's processed differential-expression result is used for comparison, it will be labeled as a study/reference result rather than treated as universal ground truth.

This distinction is essential for methodological correctness.

---

# 14. Functional and Pathway Analysis

After differential expression, the system will analyze the biological functions associated with significant genes.

Candidate open resources/tools include:

- Gene Ontology
- Reactome
- Bioconductor annotation packages
- clusterProfiler
- Reactome Analysis Service

Reactome provides open data and an Analysis Service/API. Its analysis tools support identifier-list over-representation/pathway analysis and expression-associated analyses.

For the main implementation, the preferred local approach is:

```text
DE gene list
    |
    v
Identifier mapping
    |
    v
GO / pathway enrichment
    |
    v
FDR-adjusted pathway results
```

A local Bioconductor-based implementation is preferred where practical because it improves reproducibility and avoids making the experiment dependent on an external service being available at evaluation time.

Reactome can be used as an additional evidence/pathway resource.

---

# 15. Biological Interpreter Agent

The Biological Interpreter receives only summarized, structured results.

It should not receive the full 20,000-gene expression matrix unless there is a specific reason.

Example input:

```text
Dataset:
GSE202768

Comparison:
Group A vs Group B

Top differential genes:
GENE1 ...
GENE2 ...
GENE3 ...

Significant pathways:
Pathway A ...
Pathway B ...

Statistics:
log2FC
adjusted p-value
gene counts
```

The agent produces:

1. Main observations
2. Biological interpretation
3. Relevant pathways
4. Possible mechanisms
5. Evidence-supported statements
6. Limitations
7. Uncertainty

The language should distinguish:

- observed result
- evidence-supported interpretation
- hypothesis/speculation

For example:

> "The observed expression pattern is consistent with activation of..."

rather than:

> "The experiment proves that..."

---

# 16. Evidence Retriever Agent

The Evidence Agent exists because the language model's internal knowledge should not be treated as the evidence for a scientific claim.

The workflow is:

```text
Biological claim candidate
        |
        v
Evidence query
        |
        v
Open biological resource
        |
        v
Relevant records
        |
        v
Evidence snippets / metadata
        |
        v
Claim-to-evidence mapping
```

Possible resources include:

- NCBI / PubMed
- Gene Ontology
- Reactome
- UniProt
- other openly accessible biological resources where licensing and access permit use

The evidence layer should preserve:

- source identifier
- gene/pathway
- retrieved text/metadata
- query
- retrieval timestamp
- relevance score if used

The final report should be able to show why a biological claim was made.

---

# 17. Critic / Verification Agent

The Critic is a core part of the research contribution.

It receives:

- original question
- planned analysis
- computational results
- biological interpretation
- evidence records

It checks four categories.

## Statistical checks

- Was the correct group comparison used?
- Are the reported genes actually in the computed result?
- Is the adjusted p-value significant?
- Is the direction of change correct?
- Were p-values confused with adjusted p-values?
- Was an inappropriate method applied to the data type?

## Biological checks

- Is the gene/pathway actually present?
- Does retrieved evidence support the claim?
- Is the interpretation stronger than the evidence allows?

## Logical checks

- Does the conclusion follow from the analysis?
- Are correlation and causation being confused?
- Are unsupported mechanisms being stated as facts?

## Output

```json
{
  "status": "PASS",
  "errors": [],
  "warnings": [],
  "corrections": []
}
```

or:

```json
{
  "status": "FAIL",
  "errors": [
    "GENE_X was reported as significant but adjusted p-value is 0.31"
  ],
  "corrections": [
    "Remove GENE_X from significant-gene claims"
  ]
}
```

The Critic can trigger a bounded correction loop.

The loop should have a maximum number of iterations to prevent infinite agent execution.

---

# 18. Models

## 18.1 Primary model — Gemma 3 4B IT

Gemma 3 4B IT is the primary local reasoning model.

Google's model card describes Gemma 3 as a family of lightweight open models, with a 128K context window for the 4B size. The model is intended for text generation/reasoning and can be deployed in resource-constrained environments.

A Q4/QAT GGUF release is available from Google, specifically intended to reduce memory requirements while preserving quality relative to the corresponding higher-precision model.

Model source:

https://huggingface.co/google/gemma-3-4b-it

Q4/QAT source:

https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf

The exact quantization, runtime, and hardware utilization will be recorded.

---

# 19. Biomedical Comparison — MedGemma 4B IT

MedGemma 4B IT is the secondary model.

MedGemma is a collection of Gemma 3 variants trained for medical text and image comprehension.

Important:

> MedGemma is a medical-domain model, not a dedicated transcriptomics foundation model.

That distinction is part of the experiment.

We are testing whether medical-domain specialization helps on our biological reasoning tasks, not assuming that it will.

Model source:

https://huggingface.co/google/medgemma-4b-it

A 4-bit community quantization is available, but the exact model artifact used must be recorded because model license and redistribution conditions still apply.

---

# 20. Optional Small Biomedical Baseline — BioMedLM

BioMedLM may be included as an optional lightweight biomedical language-model baseline if the available time permits.

It is not required for the core experiment.

If it proves difficult to integrate reliably with structured tool use, it will be dropped rather than allowed to delay the core project.

This prevents the model-comparison section from becoming larger than the actual research question.

---

# 21. Why We Are Not Using DNA/RNA Foundation Models as the Main Agent

There are many biological foundation models designed specifically for DNA or RNA sequences.

Those are valuable for sequence-level tasks such as:

- motif prediction
- regulatory prediction
- RNA sequence representation
- structure-related tasks

However, the primary input to this project is a **gene-expression matrix plus experimental metadata**.

The task is not:

```text
DNA sequence -> prediction
```

It is:

```text
RNA-seq expression
    +
experimental design
    ->
differential expression
    ->
pathway interpretation
```

Therefore, forcing a sequence foundation model into the reasoning layer would not be methodologically justified.

Sequence models may be discussed as related work/future extensions.

---

# 22. Local / Open-Source Software Stack

The target implementation should use locally runnable/open-source software wherever practical.

## Agent orchestration

- LangGraph

LangGraph is MIT-licensed and provides stateful agent orchestration.

https://github.com/langchain-ai/langgraph

## Statistical analysis

- R
- Bioconductor
- DESeq2

https://bioconductor.org/packages/DESeq2/

## Annotation

- org.Hs.eg.db
- AnnotationDbi

## Enrichment

- clusterProfiler
- Gene Ontology resources
- Reactome

## Python

- Python
- pandas
- numpy
- scipy
- scikit-learn
- matplotlib
- pydantic

## Local model inference

Potential runtimes:

- llama.cpp / GGUF-compatible runtime
- Transformers
- another local inference runtime if it provides stable support for the selected checkpoint

The exact runtime will be frozen after the first successful local benchmark.

---

# 23. Dataset Suite

The dataset list is fixed for the project.

We will not replace the selected datasets simply to make the benchmark more convenient.

---

## 23.1 GSE336903 — Smoke Test

NCBI GEO accession:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE336903

Description:

- Human breast cancer cell-line RNA-seq
- 6 samples
- 3 control biological replicates
- 3 treatment biological replicates
- processed FPKM matrix available

Role:

> Fast pipeline and agent smoke test.

This dataset is not intended to carry the main scientific evaluation because of its very small sample size.

---

## 23.2 GSE202768 — Development Dataset

NCBI GEO accession:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202768

Title:

> Epigenetic heterogeneity and transcriptional drivers of triple-negative breast cancer (PRRX1 KD RNA-Seq)

Organism:

> Homo sapiens

GEO identifies this as a high-throughput expression-profiling experiment.

The dataset is useful for development because it contains controlled perturbation structure and processed expression/count resources.

Role:

> Main development and workflow-debugging dataset.

We will use it to stabilize:

- metadata parsing
- comparison selection
- reference analysis
- agent prompts
- tool interfaces
- evidence workflow

---

## 23.3 GSE95304 — Held-Out Evaluation Dataset

NCBI GEO accession:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE95304

Title:

> Systematic Functional Perturbations Uncover a Prognostic Genetic Network Driving Human Breast Cancer [RNA-Seq]

GEO lists 20 samples, including:

- scrambled controls
- shFra-1
- shMyc
- shE2F1
- shp53
- shEZH2

The processed resource includes FPKM data, while raw data are available through SRA.

Role:

> Held-out evaluation.

This dataset should not be used to tune the agent's prompts or thresholds after the evaluation protocol has been fixed.

---

## 23.4 GSE113650 — External Validation Dataset

NCBI GEO accession:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113650

Title:

> RNA-seq analysis of breast cancer

GEO lists six human breast-cancer cell lines:

- MCF7
- BT474
- T47D
- MDA-MB-468
- HCC70
- HCC1143

The original study compares three TNBC cell lines with three non-TNBC cell lines.

Role:

> External validation with a different biological comparison from the main perturbation datasets.

This helps test whether the workflow generalizes beyond the exact development setup.

---

## 23.5 GSE58135 — Optional Generalization Evaluation

NCBI GEO accession:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE58135

This is a larger breast-cancer RNA-seq collection containing:

- breast cancer cell lines
- TNBC primary tumors
- ER+/HER2-negative primary tumors
- uninvolved breast tissue
- normal breast tissue

GEO lists 168 samples.

Role:

> Optional larger-scale/generalization evaluation.

This dataset will only be activated after the core three-dataset experiment is stable.

It is explicitly a secondary evaluation so that its size does not jeopardize the core 5-day project.

---

# 24. Dataset Split Strategy

The project does not train the language model.

Therefore, the main concern is not model training leakage but **evaluation leakage and experimenter tuning**.

The roles are:

```text
GSE336903
    -> smoke test

GSE202768
    -> development

GSE95304
    -> held-out evaluation

GSE113650
    -> external validation

GSE58135
    -> optional generalization
```

Once evaluation thresholds/prompts/configurations are frozen, no further tuning should be performed on the held-out evaluation dataset.

---

# 25. Reference Analysis vs Agent Analysis

The experiment will have two separate paths.

```text
                    SAME DATASET
                         |
             +-----------+-----------+
             |                       |
             v                       v
      REFERENCE PIPELINE         BIOAGENT-LITE
             |                       |
             v                       v
       reference results        agent results
             |                       |
             +-----------+-----------+
                         |
                         v
                   EVALUATION
```

The reference pipeline provides a reproducible computational reference.

The agent must not be given the reference result during its normal inference.

---

# 26. What Counts as Correct?

There will not be a claim of absolute biological ground truth.

Instead, correctness will be defined at multiple levels.

## Level 1 — Computational correctness

Does the agent report results that agree with the reference computation?

## Level 2 — Statistical correctness

Does the agent correctly interpret:

- log2 fold change
- p-value
- adjusted p-value
- significance threshold
- direction of effect
- comparison labels

## Level 3 — Pathway correctness

Does the reported pathway appear in the computed enrichment results and satisfy the defined statistical criteria?

## Level 4 — Evidence support

Does an external/open biological source support the claim?

## Level 5 — Logical correctness

Does the conclusion follow from the available evidence?

This layered definition is more defensible than a single "accuracy" score.

---

# 27. Baselines

The project must compare the proposed architecture against simpler alternatives.

## Baseline 1 — LLM-only

The model receives the task and relevant summarized information but has no computational tool execution and no multi-agent verification.

Purpose:

> Measure how much can be achieved through ordinary language-model reasoning alone.

---

## Baseline 2 — Single Tool-Using Agent

One model can:

- inspect data summaries
- call predefined tools
- receive results
- produce a final answer

No explicit specialized roles.

Purpose:

> Separate the effect of tool use from the effect of multi-agent specialization.

---

## Baseline 3 — Planner + Computational Analyst

Planning is separated from computation.

Purpose:

> Determine whether basic planning/tool separation is already sufficient.

---

## Baseline 4 — Planner + Computation + Biology

Adds biological interpretation.

Purpose:

> Measure the contribution of explicit biological interpretation.

---

## Baseline 5 — Planner + Computation + Biology + Evidence

Adds evidence grounding.

Purpose:

> Measure whether retrieval reduces unsupported biological claims.

---

## Proposed System — Full Five-Role Architecture

```text
Planner
   +
Computational Analyst
   +
Biological Interpreter
   +
Evidence Retriever
   +
Critic
```

Purpose:

> Evaluate whether the complete architecture provides the best reliability/cost trade-off.

---

# 28. Ablation Studies

The following ablations will be performed if runtime permits.

### A1 — Remove Planner

```text
No Planner
```

The workflow starts directly from the analysis request.

### A2 — Remove Biological Interpreter

The system reports computational results without a dedicated biological interpretation stage.

### A3 — Remove Evidence Retriever

The Biological Interpreter must work without external evidence.

### A4 — Remove Critic

The system produces the first final answer without verification.

### A5 — Single-agent

All responsibilities are assigned to one agent.

The most important ablation is:

> **Full system vs Full system without Critic**

because this directly tests whether explicit verification improves reliability.

---

# 29. Evaluation Metrics

## 29.1 Differential-expression metrics

For a defined significant-gene set:

### Precision

```text
TP / (TP + FP)
```

### Recall

```text
TP / (TP + FN)
```

### F1

```text
2 * precision * recall / (precision + recall)
```

These will be calculated against the reference analysis under the predefined criteria.

---

## 29.2 Top-K overlap

Measure overlap between:

- reference top-K genes
- agent top-K genes

Possible values:

```text
K = 10
K = 25
K = 50
```

The exact K values will be fixed before final evaluation.

---

## 29.3 Statistical correctness

Count whether the final report correctly states:

- significance
- direction
- fold change
- adjusted p-value
- group comparison

This can be automatically checked for many claims.

---

# 30. Pathway Evaluation

For pathway results:

- pathway overlap
- top-K pathway overlap
- precision
- recall
- F1
- adjusted-p-value correctness

The system must not receive credit for naming a biologically plausible pathway that is absent from the computed analysis unless the claim is explicitly framed as a hypothesis and supported by evidence.

---

# 31. Evidence Support Rate

Every biological claim in the final report should be categorized:

```text
Supported
Partially supported
Unsupported
Contradicted
```

Primary metric:

```text
Evidence Support Rate
=
supported claims / total factual biological claims
```

A stricter version may count only fully supported claims in the numerator.

The exact annotation rule will be defined before final evaluation.

---

# 32. Hallucination / Unsupported-Claim Rate

We will count:

- invented genes
- invented pathways
- fabricated statistics
- fabricated citations
- unsupported biological mechanisms
- claims contradicted by the computed results

A claim such as:

> "Gene X is significant"

is considered a factual computational claim and must be traceable to the result table.

---

# 33. Robustness Evaluation

The system should not only perform well on clean inputs.

We will deliberately create controlled perturbations.

## R1 — Missing metadata

Remove or corrupt a required metadata field.

Expected behavior:

> Stop or request clarification rather than silently continuing.

## R2 — Incorrect group labels

Introduce an intentionally incorrect comparison.

Expected behavior:

> Detect inconsistency or flag the analysis.

## R3 — Decoy gene

Add an irrelevant or fabricated gene identifier.

Expected behavior:

> Do not treat the decoy as evidence.

## R4 — Statistical trap

Provide a gene with:

```text
large log2FC
but non-significant adjusted p-value
```

Expected behavior:

> Do not call it statistically significant.

## R5 — Conflicting evidence

Provide sources that do not all support the same interpretation.

Expected behavior:

> Report uncertainty rather than forcing a conclusion.

## R6 — Prompt/context bloat

Add irrelevant text to the input.

Expected behavior:

> Preserve the correct workflow.

---

# 34. Robustness Metrics

For each perturbation:

- error detection rate
- unsafe completion rate
- correction rate
- unsupported-claim rate
- final-task correctness

The main question is:

> Does the system recognize that something is wrong?

rather than simply:

> Does it generate an answer?

---

# 35. Agent Trace Evaluation

Because this is an agentic project, the final answer alone is not enough.

We will store:

- Planner output
- selected tools
- tool inputs
- tool outputs
- Biological Interpreter output
- Evidence queries
- retrieved evidence
- Critic output
- correction loop
- final answer

This will allow us to inspect failure cases and produce an agent trajectory diagram for the report.

---

# 36. Resource Evaluation

Because the project is specifically resource-constrained, computational cost is part of the evaluation.

Measure:

- model loading time
- inference latency
- total workflow time
- tokens generated
- number of LLM calls
- number of tool calls
- peak VRAM
- peak RAM
- CPU time where practical
- number of correction iterations

The final comparison should therefore consider:

```text
quality
+
reliability
+
cost
```

rather than accuracy alone.

---

# 37. Context Management

Although Gemma 3 4B supports a large context window, the project will deliberately avoid passing the complete expression matrix to the model.

Instead:

```text
20,000+ genes
       |
       v
deterministic computation
       |
       v
structured summary
       |
       +--> top DE genes
       +--> statistics
       +--> significant pathways
       +--> QC summary
       +--> metadata
       |
       v
small LLM context
```

This reduces memory requirements and makes the workflow easier to reproduce.

---

# 38. Structured Outputs

Every agent should return structured data wherever possible.

Examples:

```json
{
  "decision": "...",
  "reason": "...",
  "confidence": 0.0,
  "evidence_ids": [],
  "warnings": []
}
```

The system should avoid relying on free-form text when a machine-checkable representation is possible.

Pydantic or equivalent schema validation can be used.

---

# 39. Safety and Scientific Guardrails

The system is a research prototype.

It must not:

- provide medical diagnosis
- claim clinical validity
- claim causal biological mechanisms without evidence
- invent statistical results
- treat model confidence as statistical confidence
- present hypotheses as established facts

The final report should explicitly distinguish:

```text
Computed result
Evidence-supported interpretation
Hypothesis
Limitation
```

---

# 40. Reproducibility

The following will be recorded:

- dataset accession
- dataset download date
- model identifier
- model revision if available
- quantization
- inference runtime
- Python version
- R version
- Bioconductor version
- package versions
- operating system
- GPU model
- VRAM
- RAM
- random seeds where applicable
- prompts/system instructions
- analysis thresholds
- reference-pipeline configuration

A machine-readable experiment manifest should be generated.

---

# 41. Project Directory Structure

Proposed structure:

```text
BioAgent-Lite/
│
├── README.md
├── MASTER_PLAN.md
├── requirements.txt
├── environment.yml
├── renv.lock
│
├── configs/
│   ├── models.yaml
│   ├── datasets.yaml
│   ├── thresholds.yaml
│   └── experiment.yaml
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── metadata/
│
├── reference/
│   ├── deseq2/
│   ├── enrichment/
│   └── outputs/
│
├── agents/
│   ├── planner.py
│   ├── computational.py
│   ├── biology.py
│   ├── evidence.py
│   └── critic.py
│
├── tools/
│   ├── expression.py
│   ├── differential_expression.py
│   ├── enrichment.py
│   ├── evidence.py
│   └── validation.py
│
├── evaluation/
│   ├── baselines/
│   ├── ablations/
│   ├── robustness/
│   └── metrics/
│
├── experiments/
│   ├── smoke/
│   ├── development/
│   ├── heldout/
│   └── external/
│
├── outputs/
│   ├── tables/
│   ├── figures/
│   ├── traces/
│   └── reports/
│
└── docs/
    ├── methodology.md
    └── reproducibility.md
```

---

# 42. Five-Day Execution Plan

The five-day plan is deliberately prioritized.

## Day 1 — Data + Reference Pipeline

### Must finish

- Download/access datasets
- Inspect metadata
- Implement dataset loader
- Validate GSE202768
- Establish reference analysis
- Produce first DE results
- Produce first enrichment results

### Model checkpoint

Run the selected quantized Gemma model locally.

If local inference is unusably slow, adjust the runtime/model configuration before building the full system.

---

## Day 2 — Core Agent Workflow

Implement:

```text
Planner
    ↓
Computational tools
    ↓
Biological Interpreter
    ↓
Evidence
    ↓
Critic
```

Start with GSE202768.

Store complete traces.

---

## Day 3 — Baselines + First Evaluation

Run:

1. LLM-only
2. Single tool-using agent
3. Full five-role system

Generate:

- DE metrics
- pathway metrics
- evidence support
- hallucination checks
- runtime

If the full system is not stable, fix the core workflow before adding extra datasets.

---

## Day 4 — Held-Out + Robustness

Run:

- GSE95304
- GSE113650

Then run robustness tests:

- missing metadata
- wrong labels
- statistical trap
- decoy information
- conflicting evidence
- prompt bloat

Run the most important ablations.

---

## Day 5 — Analysis + Final Deliverables

Generate:

- final metric tables
- ablation table
- robustness table
- resource table
- agent trace diagrams
- failure cases
- final report
- presentation
- reproducibility package

GSE58135 is only activated if the core evaluation is already complete.

---

# 43. Priority Levels

To prevent scope creep, tasks are divided into three levels.

## P0 — Must Have

- GSE202768
- reference analysis
- Gemma 3 4B
- five-role architecture
- LLM-only baseline
- single-agent baseline
- full-system evaluation
- statistical correctness
- evidence support
- Critic
- at least one robustness test
- reproducibility information

## P1 — Should Have

- GSE95304
- GSE113650
- ablations
- complete robustness suite
- MedGemma comparison
- resource benchmarking

## P2 — Only if time remains

- GSE58135
- BioMedLM
- additional pathway resources
- more robustness scenarios
- UI/demo polish
- additional model comparisons

The project is considered successful if all P0 items are completed.

---

# 44. Failure / Kill Criteria

The project should not fail because an optional component becomes difficult.

## If MedGemma integration fails

Continue with Gemma 3.

## If BioMedLM integration fails

Drop it.

## If GSE58135 takes too long

Keep it optional.

## If external evidence retrieval becomes unreliable

Use a smaller controlled evidence corpus and clearly document it.

## If the five-agent workflow becomes too slow

Keep the five roles but reuse the same local model instance and reduce unnecessary LLM calls.

## If the full five-role system does not outperform a simpler baseline

Report the result.

This is an experiment, not a requirement that the proposed architecture must win.

---

# 45. Expected Results

We expect the following qualitative pattern, but this is not assumed as a result:

```text
LLM-only
    ↓
good language / weak numerical reliability

Single tool-agent
    ↓
better computational correctness

Multi-agent
    ↓
better separation of responsibilities

Multi-agent + Evidence
    ↓
better support for biological claims

Multi-agent + Critic
    ↓
better error detection and robustness
```

The actual measurements will determine whether these expectations are supported.

---

# 46. Main Tables for the Final Report

## Table 1 — Dataset summary

| Dataset | Samples | Data type | Biological comparison | Role |
|---|---:|---|---|---|
| GSE336903 | 6 | processed FPKM | control vs treatment | smoke |
| GSE202768 | 16 | count/FPKM resources | PRRX1-related perturbation | development |
| GSE95304 | 20 | FPKM/processed resources | multiple perturbations | held-out |
| GSE113650 | 6 | processed expression | TNBC vs non-TNBC | external |
| GSE58135 | 168 | large RNA-seq collection | multiple breast-cancer/tissue groups | optional |

Exact analysis subsets and contrasts will be documented before evaluation.

---

## Table 2 — Model comparison

| Model | Size | Domain | Quantization | Runtime | Statistical correctness | Evidence support | Hallucination |
|---|---:|---|---|---:|---:|---:|---:|
| Gemma 3 4B | 4B | General | Q4 | | | | |
| MedGemma 4B | 4B | Medical | 4-bit | | | | |
| BioMedLM | 2.7B | Biomedical | if used | | | | |

---

## Table 3 — Agent architecture comparison

| System | Planner | Tools | Biology | Evidence | Critic | DE F1 | Evidence support |
|---|---|---|---|---|---|---:|---:|
| LLM-only | No | No | implicit | No | No | | |
| Single-agent | No | Yes | implicit | optional | No | | |
| Planner + Computation | Yes | Yes | No | No | No | | |
| + Biology | Yes | Yes | Yes | No | No | | |
| + Evidence | Yes | Yes | Yes | Yes | No | | |
| Full | Yes | Yes | Yes | Yes | Yes | | |

---

## Table 4 — Ablation

| Configuration | DE | Pathway | Evidence | Hallucination | Robustness |
|---|---:|---:|---:|---:|---:|
| Full | | | | | |
| - Planner | | | | | |
| - Biology | | | | | |
| - Evidence | | | | | |
| - Critic | | | | | |

---

## Table 5 — Resource usage

| Configuration | LLM calls | Tokens | Runtime | Peak VRAM | Peak RAM |
|---|---:|---:|---:|---:|---:|
| LLM-only | | | | | |
| Single-agent | | | | | |
| Full | | | | | |

---

# 47. Figures for the Final Report

At minimum:

1. Overall system architecture
2. End-to-end workflow
3. Reference vs agent evaluation pipeline
4. Differential-expression comparison
5. Pathway comparison
6. Baseline comparison
7. Ablation results
8. Robustness results
9. Resource/latency comparison
10. Example successful agent trace
11. Example failure-and-correction trace

---

# 48. Example End-to-End Run

Example user question:

> "Compare the specified perturbation group against the control group and identify genes and biological pathways associated with the response."

### Step 1 — Planner

Identifies:

- dataset
- groups
- required comparison
- analysis sequence

### Step 2 — Computational Analyst

Runs:

- metadata validation
- expression validation
- differential expression
- enrichment

### Step 3 — Biological Interpreter

Receives only structured results and produces candidate interpretations.

### Step 4 — Evidence Agent

Retrieves evidence for the major claims.

### Step 5 — Critic

Checks:

```text
Does the gene exist?
Is it significant?
Is the direction correct?
Does the pathway exist in the computed output?
Does evidence support the interpretation?
```

### Step 6 — Correction

If an error is found:

```text
Critic
   ↓
correction request
   ↓
Interpreter / report
   ↓
Critic
```

Maximum correction iterations will be fixed.

### Step 7 — Final report

Contains:

- analysis summary
- significant genes
- pathway results
- biological interpretation
- evidence
- limitations
- confidence/verification status

---

# 49. What Makes This Different From a Normal LLM Demo

A normal biomedical LLM demo might look like:

```text
Question
   ↓
LLM
   ↓
Answer
```

This project instead looks like:

```text
Question
   ↓
Plan
   ↓
Executable statistical analysis
   ↓
Machine-checkable results
   ↓
Biological interpretation
   ↓
External evidence
   ↓
Verification
   ↓
Correction
   ↓
Final answer
```

The second system can be evaluated at every stage.

That is the main reason the project is suitable as a bioinformatics/ML term project rather than simply a chatbot demonstration.

---

# 50. Limitations

The project will have several limitations.

### Dataset limitation

The selected benchmark is concentrated in human breast-cancer/perturbation transcriptomics. Therefore, broad claims about all transcriptomics or all organisms should not be made.

### Sample-size limitation

Some selected datasets are small. They are useful for controlled benchmarking but do not establish clinical or population-level conclusions.

### Reference-analysis limitation

The reference pipeline is a reproducible comparison point, not absolute biological truth.

### Model limitation

Small local models may have weaker reasoning and instruction-following ability than large frontier models.

### Evidence limitation

Retrieval quality depends on the selected biological resources and identifier mapping.

### Agent limitation

More agents do not automatically mean better results. Additional roles may increase latency or introduce new failure modes.

### Hardware limitation

The project is optimized for a single consumer machine rather than a large GPU cluster.

---

# 51. Reproducibility Principles

Every reported experiment should be reproducible from:

```text
dataset accession
+
configuration
+
model identifier
+
model quantization
+
prompt version
+
software versions
+
random seed
+
analysis script
```

No final metric should be produced manually.

All evaluation tables should be generated from saved experiment outputs.

---

# 52. Scientific Integrity

The system should never be evaluated only by whether its final answer "sounds correct."

Every important claim should have a trace:

```text
Claim
  ↓
Source:
  - computational output
  - pathway output
  - evidence record
  - model interpretation
```

This allows a reviewer to inspect exactly where a conclusion came from.

---

# 53. Final Research Contribution

The intended contribution is a small but experimentally grounded framework for evaluating **reliability-oriented agent design in computational biology**.

The project investigates three ideas together:

### 1. Specialization

Different responsibilities are assigned to different roles.

### 2. Grounding

Numerical and biological claims are connected to computational results and external evidence.

### 3. Verification

An explicit critic checks the final reasoning before the result is presented.

The key result is not whether the system looks intelligent.

The key result is:

> **whether these design choices measurably improve correctness, evidence support, robustness, and/or efficiency compared with simpler baselines.**

---

# 54. References and Verified Resources

## Core models

- Gemma 3 4B IT:
  https://huggingface.co/google/gemma-3-4b-it

- Gemma 3 4B Q4/QAT:
  https://huggingface.co/google/gemma-3-4b-it-qat-q4_0-gguf

- MedGemma 4B IT:
  https://huggingface.co/google/medgemma-4b-it

## Datasets

- GSE336903:
  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE336903

- GSE202768:
  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE202768

- GSE95304:
  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE95304

- GSE113650:
  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE113650

- GSE58135:
  https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE58135

## Statistical / bioinformatics tools

- DESeq2:
  https://bioconductor.org/packages/DESeq2/

- Bioconductor:
  https://bioconductor.org/

- clusterProfiler:
  https://bioconductor.org/packages/clusterProfiler/

- Human annotation package:
  https://bioconductor.org/packages/org.Hs.eg.db/

- Reactome:
  https://reactome.org/

## Agent framework

- LangGraph:
  https://github.com/langchain-ai/langgraph

## Related benchmarks

- BixBench:
  https://arxiv.org/abs/2503.00096

- Benchmarking LLM-based Agents for Single-cell Omics Analysis:
  https://arxiv.org/abs/2508.13201

---

# 55. Final Project Definition

## Name

**BioAgent-Lite**

## Full title

**A Resource-Efficient Multi-Agent Framework for Reliable Gene-Expression Analysis**

## Problem

Reliable automation of a defined RNA-seq gene-expression analysis workflow using small local language models.

## Main idea

Combine:

```text
Small local LLM
      +
Specialized agent roles
      +
Deterministic bioinformatics tools
      +
Biological evidence retrieval
      +
Explicit verification
```

## Agents

```text
1. Planner
2. Computational Analyst
3. Biological Interpreter
4. Evidence Retriever
5. Critic / Verifier
```

## Main model

**Gemma 3 4B IT, quantized**

## Biomedical comparison

**MedGemma 4B IT, quantized**

## Optional model

**BioMedLM 2.7B**

## Datasets

```text
GSE336903 -> smoke test
GSE202768 -> development
GSE95304  -> held-out evaluation
GSE113650 -> external validation
GSE58135  -> optional generalization
```

## Main baselines

```text
LLM-only
Single tool-using agent
Planner + Computation
Planner + Computation + Biology
Planner + Computation + Biology + Evidence
Full five-role system
```

## Main evaluation

```text
Differential-expression correctness
Pathway agreement
Statistical correctness
Evidence support
Hallucination / unsupported claims
Robustness
Latency
Token usage
VRAM
RAM
```

## Main scientific question

> **Does a lightweight, specialized, evidence-grounded and verified multi-agent architecture improve the reliability of gene-expression analysis compared with simpler LLM and agent baselines under consumer hardware constraints?**

---

# 56. Status

### Locked

- Project direction
- Core problem
- Five-role architecture
- Primary task
- Dataset list
- Primary model
- Biomedical comparison model
- Baseline philosophy
- Reference-analysis philosophy
- Evaluation philosophy
- Hardware constraint
- 5-day execution priority

### To be fixed during implementation

- Exact local inference runtime
- Exact quantized model artifact
- Exact contrasts for each dataset
- Exact enrichment configuration
- Exact number of evaluation cases
- Final prompt versions
- Exact robustness perturbation count
- Final optional components

These implementation details should be frozen **before the final held-out evaluation**, not tuned against the held-out results.

---

# 57. Final Principle

The project should be judged by the quality of its experiment, not by how complicated the architecture looks.

If the Critic helps, the results should show it.

If evidence retrieval helps, the results should show it.

If five roles are unnecessary, the ablation should reveal that.

If the small model is insufficient, that should be documented.

The objective is to build a system that can be **measured, inspected, reproduced, and defended**, rather than simply producing impressive-looking biological answers.
