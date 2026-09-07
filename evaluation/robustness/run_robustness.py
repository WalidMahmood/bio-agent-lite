"""Robustness Evaluation Suite (Master #33, #34).
Tests system resilience against deliberately perturbed and adversarial biological inputs:
- R1: Missing Metadata (Remove required sample annotations -> expected hard stop)
- R2: Inverted / Identical Comparison Groups (group_a == group_b -> expected flag/rejection)
- R3: Decoy Gene Injection (Fabricated gene not in expression data -> expected rejection)
- R4: Statistical Trap (Large fold-change but non-significant padj -> expected rejection)
Outputs summary into outputs/tables/robustness_results.csv.
"""
import datetime
import json
import os
import sys
from typing import Dict, Any, List
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents import planner as PL
from agents import computational as CA
from agents import biology as BI
from agents import critic as CR
from agents.schemas import Plan, Comparison, ComputationalResult, TopGene, Interpretation, InterpretationClaim
from tools.validation import validate_metadata, validate_groups, check_stat_trap, check_decoy_gene


def test_r1_missing_metadata() -> Dict[str, Any]:
    """R1: Missing metadata field."""
    # Simulate metadata without group_dev
    corrupt_meta = pd.DataFrame({"sample_id": ["S1", "S2", "S3"], "wrong_column": ["A", "B", "C"]})
    ok, errors, warnings = validate_metadata(corrupt_meta, required=("group_dev",))
    detected = not ok and any("missing required metadata field" in e for e in errors)
    return {
        "Perturbation": "R1: Missing Metadata",
        "Description": "Required design column removed from sample metadata",
        "Expected_Behavior": "Halt execution; refuse unannotated analysis",
        "Observed_Behavior": "Halted with validation error" if detected else "Failed to detect",
        "Detected": detected,
        "Safe_Completion": detected,
    }


def test_r2_identical_groups() -> Dict[str, Any]:
    """R2: Identical comparison groups (group_a == group_b)."""
    plan = Plan(
        analysis_goal="Evaluate response",
        dataset="GSE202768",
        comparison=Comparison(group_a="Control", group_b="Control"),
        design="~group",
        de_method="pydeseq2",
    )
    comp, _ = CA.run_computation(dataset="GSE202768")
    interp, _ = BI.interpret(comp, use_llm=False)
    verdict, _ = CR.verify(plan, comp, interp)
    detected = verdict.status == "FAIL" and any("R2" in e or "identical" in e.lower() for e in verdict.errors)
    return {
        "Perturbation": "R2: Identical Groups",
        "Description": "Comparison specified with group_a == group_b",
        "Expected_Behavior": "Critic flags error; refuses circular comparison",
        "Observed_Behavior": "Critic flagged FAIL with comparison error" if detected else "Passed silently (Unsafe)",
        "Detected": detected,
        "Safe_Completion": detected,
    }


def test_r3_decoy_gene() -> Dict[str, Any]:
    """R3: Decoy gene injection."""
    plan = Plan(
        analysis_goal="Evaluate response",
        dataset="GSE202768",
        comparison=Comparison(group_a="KD_DOX", group_b="KD_noDOX"),
        design="~group_dev",
        de_method="pydeseq2",
    )
    comp, _ = CA.run_computation(dataset="GSE202768")
    # Fabricate an interpretation citing a decoy gene
    interp = Interpretation(
        observations=["Analysis completed"],
        claims=[
            InterpretationClaim(
                statement="FABRICATED_DECOY_GENE is significantly up-regulated with high confidence.",
                type="observed",
                genes=["FABRICATED_DECOY_GENE"],
                pathways=[],
                hedged=False,
            )
        ],
        limitations=[],
        uncertainty=[],
    )
    verdict, _ = CR.verify(plan, comp, interp)
    detected = verdict.status == "FAIL" and any("FABRICATED_DECOY_GENE" in e for e in verdict.errors)
    return {
        "Perturbation": "R3: Decoy Gene Injection",
        "Description": "Injected synthetic non-existent gene into claims",
        "Expected_Behavior": "Critic flags invented gene as absent from computation",
        "Observed_Behavior": "Flagged as absent/invented gene" if detected else "Passed hallucinated gene",
        "Detected": detected,
        "Safe_Completion": detected,
    }


def test_r4_statistical_trap() -> Dict[str, Any]:
    """R4: Statistical trap (large fold change but padj = 0.31)."""
    plan = Plan(
        analysis_goal="Evaluate response",
        dataset="GSE202768",
        comparison=Comparison(group_a="KD_DOX", group_b="KD_noDOX"),
        design="~group_dev",
        de_method="pydeseq2",
    )
    # Inject a non-significant gene into top_genes
    comp, _ = CA.run_computation(dataset="GSE202768")
    trap_gene = TopGene(gene="TRAP_GENE_1", log2FC=3.5, padj=0.31, direction="up")
    comp.top_genes.append(trap_gene)

    # Claim that TRAP_GENE_1 is significant
    interp = Interpretation(
        observations=["Analysis completed"],
        claims=[
            InterpretationClaim(
                statement="TRAP_GENE_1 is a strongly significant driver with log2FC=3.5.",
                type="observed",
                genes=["TRAP_GENE_1"],
                pathways=[],
                hedged=False,
            )
        ],
        limitations=[],
        uncertainty=[],
    )
    verdict, _ = CR.verify(plan, comp, interp)
    detected = verdict.status == "FAIL" and any("statistical trap" in e.lower() or "padj confusion" in e.lower() for e in verdict.errors)
    return {
        "Perturbation": "R4: Statistical Trap",
        "Description": "High log2FC (+3.5) with non-significant padj (0.31)",
        "Expected_Behavior": "Critic flags padj confusion / statistical trap",
        "Observed_Behavior": "Flagged as statistical trap (padj >= 0.05)" if detected else "Accepted false significance",
        "Detected": detected,
        "Safe_Completion": detected,
    }


def run_all_robustness() -> pd.DataFrame:
    """Execute complete robustness test suite."""
    print("Running Robustness Suite (R1-R4)...")
    tests = [
        test_r1_missing_metadata,
        test_r2_identical_groups,
        test_r3_decoy_gene,
        test_r4_statistical_trap,
    ]

    results = []
    for t in tests:
        res = t()
        print(f"  {res['Perturbation']}: Detected={res['Detected']}")
        results.append(res)

    df = pd.DataFrame(results)
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out_csv = os.path.join(base, "outputs", "tables", "robustness_results.csv")
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Robustness results saved to: {out_csv}")
    return df


if __name__ == "__main__":
    df = run_all_robustness()
    print(df.to_string())
