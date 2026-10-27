# Explainability â€” How BioAgent-Lite Shows Its Work

This document answers one question in full: **when the system says something about biology, how do you know why it said it, and how do you check it yourself?**

That is not a slogan here â€” it is the core research contribution (Master Plan Â§52â€“53). Everything below is inspectable in the repository today.

---

## 1. Design principle: five separated layers of a statement

Every final report keeps an explicit epistemic ledger. A reader can always tell which of these five categories a given sentence belongs to:

| Category | Meaning | How it surfaces |
|---|---|---|
| **Computed** | A number produced by deterministic code (PyDESeq2 / Welch / BH / enrichment), never by the LLM | `stats`, `top_genes`, `sig_pathways`; re-derivable byte-for-byte from `reference/outputs/*.csv` |
| **Retrieved** | A value copied verbatim from a named source artifact with lineage | `EvidenceRecord.source_id` like `GSE202768:top_differential_genes#TGFBI` |
| **Interpreted** | The Biological Interpreter's reading of the computed numbers | `interp.claims` with `type âˆˆ {observed, supported, hypothesis}` |
| **Hypothesized** | Speculation, explicitly hedged | `type: "hypothesis"` + `hedged: true`; absolute verbs are rewritten by the correction loop |
| **Rejected/Corrected** | What the Critic refused and how the text changed | `verdict.errors`, `verdict.corrections`, iteration snapshots inside the trace |

The Biological Interpreter can only write `"is consistent with"`-grade verbs; the cleanup rule literally replaces `proves|proven|definitively demonstrates|certainly causes` with `is consistent with the observation that` during correction (`agents/graph.py::_apply_correction`).

---

## 2. The claim taxonomy (`InterpretationClaim.type`)

| Type | Contract | Example |
|---|---|---|
| `observed` | Must restate only numbers present in `ComputationalResult` | "PRRX1 is down-regulated at log2FC âˆ’2.28 (padj 1.3e-29)" |
| `supported` | Generalization tied to named computed pathways/evidence | "Knockdown is associated with extracellular-matrix remodeling (Reactome R-HSA-1474244, adjP 2.2e-07)" |
| `hypothesis` | Mechanistic speculation, must stay hedged | "Loss of PRRX1 may relieve repression of collagen program genes" |

Any claim that fails its contract is what the Critic exists to catch.

---

## 3. Evidence records: lineage, not vibes (`agents/evidence.py`)

The Evidence Retriever runs **after** interpretation and **before** the Critic. For each claim it emits records with complete lineage:

```json
{
  "claim": "TGFBI is significantly up-regulated in the knockdown...",
  "query": "gene:TGFBI",
  "source_id": "GSE202768:top_differential_genes#TGFBI",
  "source_db": "DE_computation",
  "snippet": "log2FC=1.95, padj=4.7e-37, direction=up",
  "relevance": 1.0,
  "timestamp": "2026-09-05T16:52:40Z"
}
```

* **`relevance 1.0`** â€” gene found verbatim in the computed table; `0.95` â€” pathway matched a significant enrichment term; **`0.0`** â€” nothing supported the claim, and the record becomes `source_id: "...#ABSENT"` so *absence of evidence is itself recorded evidence*.
* The grounding corpus is the **computed differential-expression and enrichment artifacts themselves** (`"corpus": "computed_differential_expression_and_enrichment"`) â€” i.e., claims are traceable to the exact CSVs a reviewer can recompute with `python reference/run_deseq2.py`.

**Scope honesty:** the deployed runtime does **not** call ChromaDB or PubMed Entrez. Those appear in `requirements.txt`, `.env.example` and some narrative strings as a **documented roadmap item**. What exists today is the deterministic claim-to-artifact grounding above â€” weaker scope, but every bit of it is real and verifiable. See Â§8 for the full live/replayed/generated ledger.

---

## 4. The Adversarial Critic: every check, ranked (`agents/critic.py`)

The Critic audits each claim against the **raw numerical matrix** â€” the same numbers you could recompute yourself. Six checks:

| # | Check | Severity | Trigger example | Typical error string |
|---|---|---|---|---|
| 1 | **Comparison sanity** (R2) | ERROR | `group_a == group_b` | `Invalid experimental comparison: intervention and control groups are identical (R2)` |
| 2 | **Invented gene** (R3) | ERROR | gene in a claim never appears in computed results | `<G> reported in claim #i but absent from computed top results (invented gene)` |
| 3 | **Statistical trap / padj confusion** (R4) | ERROR | claim says "significant" but `padj â‰¥ 0.05` | padj-confusion / statistical-trap error + removal correction |
| 4 | **Direction concordance** | ERROR | text says up/down but sign of computed log2FC disagrees | `CD82 claimed down but log2FC=1.14 (wrong direction)` |
| 5 | **Pathway existence** | WARNING | named pathway absent from significant enrichment | `uncredited / absent from significant enrichment results` |
| 6 | **Hedging / wording** | ERROR (hypothesis claims) / WARNING (observed) | `proves`, `definitively`, `certainly causes` | `Hypothesis stated with unscientific certainty...` |

Verdict derivation (`FAIL` iff any ERROR), audit scores (`total_claims_audited / errors_found / warnings_found / corrections_required`), and three roll-up booleans: `statistical_checks_passed`, `biological_grounding_passed`, `safety_guardrails_passed`.

### The bounded correction loop

```
critic â†’ FAIL â†’ n_correct (remove bad-gene claims, un-certain the language)
              â†’ evidence â†’ critic  (at most MAX_CORRECTIONS = 2 times)
```
After 2 failed corrections the run terminates with the FAIL verdict standing â€” **a wrong answer is never laundered into a PASS**; you receive the correction history instead.

### Proof it works, not just a description â€” three preserved catches

1. **`outputs/traces/dev_20260905T165240Z.json`** â€” the canonical case: iteration-0 draft claimed `CD82` down-regulated; the Critic flagged `claimed down but log2FC=1.14 (wrong direction)`; iteration-1 certified `PASS` after correction. Cited in `docs/reproducibility.md` ("Trace Check").
2. **`data/test_datasets/PDAC_gemcitabine_counts.csv` live validation** â€” draft called `DCK` up-regulated; flag â†’ forced rewrite to down-regulation (loss of prodrug activation). Recorded in the PDAC report and README.
3. **Ablation traces** â€” with the Critic removed (`ablation_w_o_*` traces), direction errors on `TGFBI/COL1A1/COL5A1` go unflagged.  See [docs/RESULTS.md Â§6](RESULTS.md).

---

## 5. Anatomy of a trace (the flight recorder)

Every headless run writes `outputs/traces/<run_id>.json` (27 traces currently preserved):

```
run_id, question, use_llm
plan        â†’ the Planner's frozen contract (groups, design, method, guardrails)
comp        â†’ numerical core (n_tested, n_sig, up/down, top_genes[25], sig_pathways)
interp      â†’ observations, typed claims, limitations
evidence    â†’ full lineage records (Â§3)
verdict     â†’ PASS/FAIL + errors + warnings + corrections
traces[]    â†’ per-agent steps: llm_used, latency_s, token usage,
              and on each critic pass: "verdict_snapshot" + "iteration"
iterations  â†’ how many corrective cycles ran
```

Because every intermediate state is frozen, any figure in the paper can be traced back: e.g., the ESR numbers in the generalization table come from `evidence[].relevance â‰¥ 0.7` inside these exact files.

---

## 6. Fact-checking a result yourself (3 minutes, no agent needed)

All three come from `reference/outputs/GSE202768/` produced by `python reference/run_deseq2.py` + `run_enrichment.py` (pydeseq2 0.5.4, ~25 s):

1. **Check a gene** in `de_results.csv` (`gene, baseMean, log2FoldChange, lfcSE, stat, pvalue, padj`):
   ```powershell
   # Windows (PowerShell):
   Import-Csv reference\outputs\GSE202768\de_results.csv | Where-Object gene -eq PRRX1
   # â†’ expect log2FoldChange âˆ’2.28, padj 1.3e-29, direction down (knockdown confirmed)
   ```
2. **Check a pathway** in `enrichment_Reactome.csv` (`overlap Gene_set P-value Adjusted...`):
   `Extracellular Matrix Organization R-HSA-1474244 â†’ overlap 25/291, adjP 2.2e-07`.
   Notation: `25/291` = 25 of your changed genes are among that pathway's 291 annotated members.
3. **Ad-hoc claim checks** with the provided utility:
   ```powershell
   python tools\check_claims.py      # greps DE / interferon / migration terms vs reference tables
   ```

If any number in a report disagrees with these tables, the system itself is designed to have failed loudly first (Critic) â€” and you now have the tooling to prove it either way.

---

## 7. Reading the directional semantics correctly

* Group order is fixed by the Planner: **A = intervention** (treatment/knockdown/resistant), **B = reference** (control/sensitive/parental).
* `direction: "up"` â‡’ higher in A. For a **knockdown** question, the knocked-down gene itself must appear **down** (as PRRX1, âˆ’2.28, does); genes that *rise* when a repressor is removed (TGFBI, COL1A1) appear **up** â€” that combination is itself a mechanistic signal (relief of repression).
* `|log2FC| â‰¥ 1.0` marks "strong" regulators (a config parameter, `configs/thresholds.yaml` â€” the LLM cannot invent thresholds); `padj < 0.05` is the significance gate; FPKM datasets show `padj = N/A` *by design*.

---

## 8. The live / replayed / generated ledger (read this before citing numbers)

For scientific honesty â€” and because every claim above survives review â€” here is the exact provenance of everything the system shows you:

| The thing | Status | What that means |
|---|---|---|
| PyDESeq2 / Welch / BH statistics | **LIVE computation** | Recomputed per run from matrices; matches `reference/outputs` |
| Upload inspection + refusal guard | **LIVE** | Real parsing + real float-fraction heuristic |
| Volcano/pathway/benchmark figures | **LIVE for uploads & GSE202768** | Plotted from the computed tables at request time |
| LangGraph 5-agent runs (headless) | **LIVE** | Fresh graph per invocation (e.g. `run_dev.py`) |
| Critic verification + correction loop | **LIVE in headless runs** | Dev/eval/ablation traces are genuine per-run logs |
| Web UI runs on `GSE202768 / GSE113650 / GSE95304 / GSE336903` | **REPLAYED** | Serves the recorded, audited traces from those real runs â€” numbers/audit are genuine; latency shown is recorded, not fresh |
| Web UI run on `PDAC_Gemcitabine` / uploaded files | **LIVE statistics + template narrative** | Welch + BH + real figures at request time; the surrounding agent story/citations/pathway treasury is pre-written for the demo |
| `model_comparison.csv`, `model_systems_tradeoffs.csv`, `resource_usage.csv`, `dataset_summary.csv`, naive-baseline panels | **GENERATED** | Written by their generator scripts from constant copies â€” reproduce raw runs from `outputs/traces/` instead |
| ChromaDB / PubMed / ollama embedder | **ROADMAP ONLY** | In config/requirements/narrative text; zero runtime calls |

The practical implication for a user:
* For **fresh numbers on any matrix**, use the live path (upload) or headless runners.
* For **benchmark datasets**, trust the numbers (they came from real, trace-backed runs) and cite `outputs/tables/architecture_comparison.csv` / `dataset_generalization.csv` rather than the hand-built convenience tables.
* The full experiment-by-experiment audit is in [docs/RESULTS.md](RESULTS.md).
