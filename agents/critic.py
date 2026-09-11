"""Critic / Verifier Agent (Master #17).
Performs multi-layered scientific, statistical, biological, and safety verification:
1. Statistical Verification: Gene presence, adjusted p-value significance (padj < 0.05),
   fold-change direction concordance, detection of statistical traps (large LFC with high padj).
2. Biological Verification: Pathway enrichment confirmation, identification of uncredited pathways.
3. Logical & Scientific Hedging: Hypotheses must use probabilistic language; forbids "proves".
4. Safety Verification: Non-clinical disclaimer presence and group comparison sanity (R2).
Triggers bounded correction loop if errors are detected.
"""
import os
import re
import sys
from typing import Tuple, List, Dict, Any, Set
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.schemas import CriticVerdict, Plan, ComputationalResult, Interpretation

STRONG_WORDS = re.compile(r"\b(proves|proven|definitively|certainly causes|undeniably)\b", re.I)
UP_PAT = re.compile(r"\b(up[\s-]?regulat|increas|elevat)", re.I)
DOWN_PAT = re.compile(r"\b(down[\s-]?regulat|decreas|reduc|suppress)", re.I)


def _norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"^(go|reactome|kegg)\s+", "", s)
    s = re.sub(r"\s*\(.*?\)", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def verify(
    plan: Plan,
    comp: ComputationalResult,
    interp: Interpretation,
    padj_thresh: float = 0.05,
) -> Tuple[CriticVerdict, Dict[str, Any]]:
    """Execute complete verification audit on agent reasoning and claims."""
    errors: List[str] = []
    warnings: List[str] = []
    corrections: List[str] = []

    # Map genes from computational result
    gene_map = {g.gene.upper(): g for g in comp.top_genes}

    # Map normalized pathway terms
    pw_terms: Set[str] = {_norm(p.term) for p in comp.sig_pathways}

    # 1. Comparison Sanity Guard (Robustness R2)
    if plan.comparison.group_a.lower() == plan.comparison.group_b.lower():
        errors.append("Invalid experimental comparison: intervention and control groups are identical (R2)")
        corrections.append("Specify distinct comparison groups in the plan")

    # 2. Disclaimer & Safety Guard
    if not interp.disclaimer or "clinical" not in interp.disclaimer.lower():
        warnings.append("Missing standard non-clinical research prototype disclaimer")

    # 3. Claims Verification Audit
    for idx, claim in enumerate(interp.claims):
        statement = claim.statement

        # Gene checks
        for g in claim.genes:
            g_clean = g.strip().upper()
            if g_clean not in gene_map:
                errors.append(f"{g_clean} reported in claim #{idx+1} but absent from computed top results (invented gene)")
                corrections.append(f"Remove or correct uncomputed gene {g_clean}")
            else:
                hit = gene_map[g_clean]
                # Stat Trap Check (padj confusion)
                if hit.padj is not None and (claim.type == "observed" or "significan" in statement.lower()):
                    if hit.padj >= padj_thresh:
                        errors.append(
                            f"{g_clean} claimed significant but padj={hit.padj:.2g} >= {padj_thresh} (statistical trap / padj confusion)"
                        )
                        corrections.append(f"Remove {g_clean} from significant claims")

                # Direction Check
                if UP_PAT.search(statement) and not DOWN_PAT.search(statement):
                    if hit.log2FC < 0:
                        errors.append(
                            f"{g_clean} claimed up-regulated but computed log2FC={hit.log2FC:.2f} is negative (wrong direction)"
                        )
                        corrections.append(f"Fix direction for {g_clean} to down-regulated")

                elif DOWN_PAT.search(statement) and not UP_PAT.search(statement):
                    if hit.log2FC > 0:
                        errors.append(
                            f"{g_clean} claimed down-regulated but computed log2FC={hit.log2FC:.2f} is positive (wrong direction)"
                        )
                        corrections.append(f"Fix direction for {g_clean} to up-regulated")

        # Pathway checks
        for p in claim.pathways:
            np = _norm(p)
            if not any(np in t or t in np for t in pw_terms):
                warnings.append(f"Pathway '{p}' in claim #{idx+1} is uncredited / absent from significant enrichment results")

        # Scientific Hedging Check
        if claim.type == "hypothesis" and STRONG_WORDS.search(statement):
            errors.append(f"Hypothesis stated with unscientific certainty ('{statement[:80]}...')")
            corrections.append(f"Rephrase claim #{idx+1} using probabilistic scientific hedging ('suggests', 'is consistent with')")

        if claim.type in ("observed", "supported") and STRONG_WORDS.search(statement):
            warnings.append(f"Overly strong causal phrasing in empirical claim: '{statement[:80]}...'")

    status = "FAIL" if errors else "PASS"
    stat_ok = not any("padj" in e or "direction" in e or "trap" in e for e in errors)
    bio_ok = not any("invented" in e for e in errors)
    safety_ok = not any("Invalid experimental comparison" in e or "Hypothesis stated" in e for e in errors)

    verdict = CriticVerdict(
        status=status,
        errors=errors,
        warnings=warnings,
        corrections=corrections,
        statistical_checks_passed=stat_ok,
        biological_grounding_passed=bio_ok,
        safety_guardrails_passed=safety_ok,
        audit_scores={
            "total_claims_audited": len(interp.claims),
            "errors_found": len(errors),
            "warnings_found": len(warnings),
            "corrections_required": len(corrections),
        },
    )

    trace = {
        "agent": "critic",
        "dataset": comp.dataset,
        "verdict_status": status,
        "errors_count": len(errors),
        "warnings_count": len(warnings),
        "statistical_checks_passed": stat_ok,
        "biological_grounding_passed": bio_ok,
        "safety_guardrails_passed": safety_ok,
    }
    return verdict, trace
