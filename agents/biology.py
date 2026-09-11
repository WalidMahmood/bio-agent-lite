"""Biological Interpreter Agent (Master #15).
Translates structured computational summaries into evidence-supported biological findings.
Enforces strict claim taxonomy (observed / supported / hypothesis), scientific hedging,
and explicit non-clinical safety disclaimers.
"""
import json
import os
import sys
from typing import Tuple, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.schemas import Interpretation, InterpretationClaim, ComputationalResult
from tools.llm_client import chat, extract_json_safe

SYSTEM_PROMPT = """You are a rigorous, specialized biological interpreter for transcriptomics research.
Given structured statistical outputs (top differentially expressed genes and pathway enrichments), your job is to produce a careful biological interpretation.

CRITICAL SCIENTIFIC & SAFETY RULES:
1. Distinguish strictly between:
   - "observed": Factual numerical results calculated directly in the table (e.g. "Gene X is up-regulated with log2FC=2.1, padj=1e-10").
   - "supported": Biological interpretation corroborated by computed pathway enrichments (e.g. "Up-regulated genes are enriched for extracellular matrix organization").
   - "hypothesis": Proposed biological mechanisms or downstream implications. MUST use hedged, probabilistic scientific language ("is consistent with", "suggests potential involvement", "may reflect").
2. FORBIDDEN WORDS in hypotheses: Never write "proves", "proven", "definitively demonstrates", or "certainly causes".
3. Distinguish correlation from causation. Knockdown effects reflect transcriptional responses, not necessarily direct binding.
4. Output MUST be valid JSON matching this schema:
{
  "observations": ["summary of key numbers and strongest hits"],
  "claims": [
    {
      "statement": "Clear biological statement",
      "type": "observed | supported | hypothesis",
      "genes": ["GENE1", "GENE2"],
      "pathways": ["Pathway Name"],
      "hedged": true
    }
  ],
  "limitations": ["experimental limitations, sample size, bulk RNA-seq resolution"],
  "uncertainty": ["unresolved questions requiring experimental validation"]
}
"""


def interpret(comp: ComputationalResult, use_llm: bool = True) -> Tuple[Interpretation, Dict[str, Any]]:
    """Generate biological interpretation from structured computational summary."""
    genes_txt = "\n".join(
        [
            f"- {g.gene}: log2FC={g.log2FC:.2f}, padj={f'{g.padj:.2e}' if g.padj is not None else 'N/A (descriptive FPKM)'}, direction={g.direction}"
            for g in comp.top_genes[:15]
        ]
    )
    pw_txt = "\n".join(
        [f"- {p.source} {p.term}: FDR={p.adjP:.2e}, overlap={p.overlap}" for p in comp.sig_pathways[:8]]
    )

    user_prompt = f"""Dataset: {comp.dataset} ({comp.data_type})
Biological Contrast: {comp.contrast}
Statistical Summary: {comp.n_sig} significant genes at FDR < {comp.padj_threshold} ({comp.n_up} up, {comp.n_down} down).

Top Statistically Significant Genes:
{genes_txt}

Top Statistically Enriched Pathways:
{pw_txt}

Task: Produce a rigorous, evidence-supported biological interpretation adhering to all scientific constraints and claim classifications in JSON.
"""

    trace: Dict[str, Any] = {
        "agent": "biological_interpreter",
        "dataset": comp.dataset,
        "contrast": comp.contrast,
        "llm_used": use_llm,
    }

    if use_llm:
        try:
            out = chat(user_prompt, system=SYSTEM_PROMPT, max_tokens=1500, temperature=0.15)
            parsed = extract_json_safe(out["text"])
            claims = [InterpretationClaim(**c) for c in parsed.get("claims", [])]
            interp = Interpretation(
                observations=parsed.get("observations", []),
                claims=claims,
                limitations=parsed.get("limitations", []),
                uncertainty=parsed.get("uncertainty", []),
            )
            trace.update(
                {
                    "latency_s": out["latency_s"],
                    "usage": out["usage"],
                    "claims_count": len(interp.claims),
                    "status": "success",
                }
            )
            return interp, trace
        except Exception as e:
            trace["llm_error"] = str(e)

    # Deterministic dataset-aware fallback
    top_gene = comp.top_genes[0].gene if comp.top_genes else "N/A"
    top_pathway = comp.sig_pathways[0].term if comp.sig_pathways else "None detected"

    fallback_claims = [
        InterpretationClaim(
            statement=f"{comp.n_sig} genes reached significance threshold (padj<{comp.padj_threshold}) with {comp.n_up} up-regulated and {comp.n_down} down-regulated in {comp.contrast}.",
            type="observed",
            genes=[g.gene for g in comp.top_genes[:3]],
            pathways=[],
            hedged=True,
        ),
        InterpretationClaim(
            statement=f"Top enriched biological process is {top_pathway}, supported by multiple differential transcripts.",
            type="supported",
            genes=[g.gene for g in comp.top_genes[:3]],
            pathways=[top_pathway],
            hedged=True,
        ),
        InterpretationClaim(
            statement=f"Observed expression shifts are consistent with perturbation-induced pathway modulation in {comp.dataset}.",
            type="hypothesis",
            genes=[top_gene],
            pathways=[top_pathway],
            hedged=True,
        ),
    ]

    interp = Interpretation(
        observations=[
            f"{comp.n_sig} genes significant at padj < {comp.padj_threshold} in {comp.contrast}.",
            f"Strongest differential hit by adjusted significance: {top_gene}.",
        ],
        claims=fallback_claims,
        limitations=[
            "Small sample size per group; results warrant orthogonal biological replication.",
            "Bulk transcriptomics measures average cell population expression.",
        ],
        uncertainty=[
            "Direct transcriptional targets versus secondary downstream regulatory cascades remain unverified without kinetic ChIP/degron assays."
        ],
    )
    trace.update({"llm_used": False, "fallback": True, "status": "fallback_applied"})
    return interp, trace
