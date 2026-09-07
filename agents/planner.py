"""Planner agent (Master #10).
Converts biological questions into a constrained, machine-checkable execution plan.
Selects exclusively from predefined deterministic tools; forbids arbitrary code execution.
Includes few-shot prompting, dynamic dataset detection, and robust fallback.
"""
import os
import re
import sys
from typing import Tuple, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.schemas import Plan, Comparison
from tools.llm_client import chat, extract_json_safe

SYSTEM_PROMPT = """You are a senior bioinformatics planning agent.
Your objective is to translate a biological research question and dataset request into a constrained, structured analysis plan.

CONSTRAINTS:
1. Return ONLY a valid JSON object matching the requested schema. No conversational filler or markdown formatting outside JSON.
2. Select tools ONLY from predefined available tools:
   - "validate_metadata"
   - "run_differential_expression"
   - "run_enrichment"
   - "retrieve_evidence"
   - "verify_results"
3. Identify the organism, data type (counts, fpkm, cuffdiff), and proper comparison groups.
4. Enforce scientific guardrails (e.g. refuse FPKM in count-based models).

FEW-SHOT EXAMPLE:
User Question: "Perform differential expression on GSE202768 TNBC cells comparing DOX-induced PRRX1 knockdown against uninduced controls."
Output JSON:
{
  "analysis_goal": "Identify differentially expressed genes and pathways resulting from DOX-induced PRRX1 knockdown in Hs578 TNBC cells",
  "dataset": "GSE202768",
  "organism": "Homo sapiens",
  "data_type": "counts",
  "comparison": {
    "group_a": "KD_DOX",
    "group_b": "KD_noDOX"
  },
  "design": "~group_dev",
  "de_method": "pydeseq2 (Wald negative binomial test)",
  "required_steps": [
    "validate_metadata",
    "run_differential_expression",
    "run_enrichment",
    "retrieve_evidence",
    "verify_results"
  ],
  "safety_guardrails": [
    "refuse_fpkm_deseq2",
    "require_bh_fdr",
    "require_hedged_hypothesis",
    "non_clinical_disclaimer"
  ]
}
"""

DATASET_PROFILES = {
    "GSE202768": {
        "organism": "Homo sapiens",
        "data_type": "counts",
        "comparison": {"group_a": "KD_DOX", "group_b": "KD_noDOX"},
        "design": "~group_dev",
        "de_method": "pydeseq2 (Wald negative-binomial test, padj<0.05)",
        "goal": "Identify genes and pathways associated with DOX-induced PRRX1 knockdown in Hs578 TNBC cells",
    },
    "GSE113650": {
        "organism": "Homo sapiens",
        "data_type": "cuffdiff",
        "comparison": {"group_a": "TNBC", "group_b": "nonTNBC"},
        "design": "CellLine_type (3 TNBC vs 3 non-TNBC)",
        "de_method": "CuffDiff study statistical output (q_value<0.05)",
        "goal": "Evaluate transcriptional divergence between TNBC and receptor-positive breast cancer cell lines",
    },
    "GSE95304": {
        "organism": "Homo sapiens",
        "data_type": "fpkm",
        "comparison": {"group_a": "shMyc", "group_b": "shSCR"},
        "design": "Perturbation vs Scrambled Control",
        "de_method": "Descriptive FPKM fold-change (log2FC>=1.0, count guard active)",
        "goal": "Identify perturbation targets and cell-cycle pathways altered upon oncogene knockdown",
    },
    "GSE336903": {
        "organism": "Mus musculus",
        "data_type": "fpkm",
        "comparison": {"group_a": "treatment", "group_b": "control"},
        "design": "Treatment vs Control (3v3)",
        "de_method": "Descriptive FPKM fold-change (mouse gene annotation)",
        "goal": "Smoke test differential expression on mouse cell line FPKM matrix",
    },
}


def _detect_dataset(text: str) -> str:
    """Detect dataset accession from query text."""
    for acc in ["GSE202768", "GSE113650", "GSE95304", "GSE336903"]:
        if acc.lower() in text.lower():
            return acc
    return "GSE202768"


def make_plan(question: str, dataset: str = "auto", use_llm: bool = True) -> Tuple[Plan, Dict[str, Any]]:
    """Generate a structured, constrained analysis plan."""
    if dataset == "auto":
        dataset = _detect_dataset(question)
    dataset = dataset.upper()
    profile = DATASET_PROFILES.get(dataset, DATASET_PROFILES["GSE202768"])

    trace: Dict[str, Any] = {"agent": "planner", "question": question, "target_dataset": dataset}

    if use_llm:
        user_prompt = f"""Biological Question: {question}
Target Dataset Accession: {dataset}
Dataset Characteristics: Organism={profile['organism']}, Available format={profile['data_type']}, Expected comparison={profile['comparison']['group_a']} vs {profile['comparison']['group_b']}.

Generate the constrained analysis plan in exact JSON format.
"""
        try:
            out = chat(user_prompt, system=SYSTEM_PROMPT, max_tokens=600)
            parsed = extract_json_safe(out["text"])
            # Ensure proper schema mapping
            if "comparison" in parsed and isinstance(parsed["comparison"], dict):
                parsed["comparison"] = Comparison(**parsed["comparison"])
            plan = Plan(**parsed)
            trace.update(
                {
                    "llm_used": True,
                    "latency_s": out["latency_s"],
                    "usage": out["usage"],
                    "status": "success",
                }
            )
            return plan, trace
        except Exception as e:
            trace["llm_error"] = str(e)

    # Deterministic dataset-aware fallback
    plan = Plan(
        analysis_goal=profile["goal"],
        dataset=dataset,
        organism=profile["organism"],
        data_type=profile["data_type"],
        comparison=Comparison(**profile["comparison"]),
        design=profile["design"],
        de_method=profile["de_method"],
        required_steps=[
            "validate_metadata",
            "run_differential_expression",
            "run_enrichment",
            "retrieve_evidence",
            "verify_results",
        ],
        safety_guardrails=[
            "refuse_fpkm_deseq2",
            "require_bh_fdr",
            "require_hedged_hypothesis",
            "non_clinical_disclaimer",
        ],
    )
    trace.update({"llm_used": False, "fallback": True, "status": "fallback_applied"})
    return plan, trace
