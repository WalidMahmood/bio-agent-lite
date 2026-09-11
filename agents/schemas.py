"""Pydantic schemas for all agent I/O (Master #38).
Standardized structured contracts with validation, safety guardrails, and audit tracking.
"""
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field

ClaimType = Literal["observed", "supported", "hypothesis"]


class Comparison(BaseModel):
    group_a: str = Field(description="Intervention or perturbation group")
    group_b: str = Field(description="Reference or control group")


class Plan(BaseModel):
    analysis_goal: str
    dataset: str
    organism: str = "Homo sapiens"
    data_type: str = "counts"  # counts, fpkm, cuffdiff
    comparison: Comparison
    design: str
    de_method: str
    required_steps: List[str] = Field(
        default_factory=lambda: [
            "validate_metadata",
            "run_differential_expression",
            "run_enrichment",
            "retrieve_evidence",
            "verify_results",
        ]
    )
    safety_guardrails: List[str] = Field(
        default_factory=lambda: [
            "refuse_fpkm_deseq2",
            "require_bh_fdr",
            "require_hedged_hypothesis",
            "non_clinical_disclaimer",
        ]
    )


class TopGene(BaseModel):
    gene: str
    log2FC: float
    padj: Optional[float] = None
    pvalue: Optional[float] = None
    direction: Literal["up", "down"]


class SigPathway(BaseModel):
    source: str  # GO, Reactome, KEGG
    term: str
    adjP: float
    overlap: str


class ComputationalResult(BaseModel):
    dataset: str
    data_type: str = "counts"
    contrast: str
    n_total_tested: int = 0
    n_sig: int
    n_up: int
    n_down: int
    padj_threshold: float = 0.05
    top_genes: List[TopGene]
    sig_pathways: List[SigPathway]
    execution_log: List[str] = Field(default_factory=list)


class InterpretationClaim(BaseModel):
    statement: str
    type: ClaimType  # observed (direct numbers), supported (literature/pathway corroborated), hypothesis (mechanistic speculation)
    genes: List[str] = Field(default_factory=list)
    pathways: List[str] = Field(default_factory=list)
    hedged: bool = Field(default=True, description="True if statement uses appropriate scientific uncertainty language")


class Interpretation(BaseModel):
    observations: List[str]
    claims: List[InterpretationClaim]
    limitations: List[str]
    uncertainty: List[str]
    disclaimer: str = (
        "RESEARCH PROTOTYPE ONLY: This automated interpretation is generated for computational biology "
        "research and term-project evaluation. It is not approved for clinical diagnostics or medical decisions."
    )


class EvidenceRecord(BaseModel):
    claim: str
    query: str
    source_id: str
    source_db: str  # DE_table, GO, Reactome, KEGG, CuffDiff_study, PubMed_cache
    snippet: str
    relevance: float
    timestamp: str


class CriticVerdict(BaseModel):
    status: Literal["PASS", "FAIL"]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    corrections: List[str] = Field(default_factory=list)
    statistical_checks_passed: bool = True
    biological_grounding_passed: bool = True
    safety_guardrails_passed: bool = True
    audit_scores: Dict[str, Any] = Field(default_factory=dict)
