"""Evidence Retriever Agent (Master #16).
Grounds biological claims against deterministic computational results and pathway databases.
Maintains rigorous source lineage, query tracking, timestamps, and relevance scores.
"""
import datetime
import os
import sys
from typing import List, Tuple, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.schemas import EvidenceRecord, Interpretation, ComputationalResult


def retrieve(interp: Interpretation, comp: ComputationalResult) -> Tuple[List[EvidenceRecord], Dict[str, Any]]:
    """Retrieve grounded evidence records for all claims made by the Biological Interpreter."""
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    records: List[EvidenceRecord] = []

    # Map available genes from the computational result
    gene_map = {g.gene.upper(): g for g in comp.top_genes}

    # Map available pathways
    pathway_terms = [(p.source, p.term.lower(), p) for p in comp.sig_pathways]

    for claim in interp.claims:
        # 1. Gene evidence grounding
        for g in claim.genes:
            g_clean = g.strip().upper()
            if g_clean in gene_map:
                hit = gene_map[g_clean]
                records.append(
                    EvidenceRecord(
                        claim=claim.statement[:120],
                        query=f"gene:{g_clean}",
                        source_id=f"{comp.dataset}:top_differential_genes#{g_clean}",
                        source_db="DE_computation",
                        snippet=f"{hit.gene}: log2FC={hit.log2FC:.2f}, padj={hit.padj:.2e}, direction={hit.direction}",
                        relevance=1.0,
                        timestamp=now,
                    )
                )
            else:
                records.append(
                    EvidenceRecord(
                        claim=claim.statement[:120],
                        query=f"gene:{g_clean}",
                        source_id=f"{comp.dataset}:top_differential_genes#ABSENT",
                        source_db="DE_computation",
                        snippet=f"Gene '{g_clean}' NOT FOUND in computed top significant results",
                        relevance=0.0,
                        timestamp=now,
                    )
                )

        # 2. Pathway evidence grounding
        for p in claim.pathways:
            p_clean = p.strip().lower()
            hit_p = None
            for src, term_lower, p_obj in pathway_terms:
                if p_clean in term_lower or term_lower in p_clean:
                    hit_p = (src, p_obj)
                    break

            if hit_p:
                src, p_obj = hit_p
                records.append(
                    EvidenceRecord(
                        claim=claim.statement[:120],
                        query=f"pathway:{p[:40]}",
                        source_id=f"{comp.dataset}:enrichment_{src}#{p_obj.term[:30]}",
                        source_db=src,
                        snippet=f"{p_obj.term}: FDR={p_obj.adjP:.2e}, overlap={p_obj.overlap}",
                        relevance=0.95,
                        timestamp=now,
                    )
                )
            else:
                records.append(
                    EvidenceRecord(
                        claim=claim.statement[:120],
                        query=f"pathway:{p[:40]}",
                        source_id=f"{comp.dataset}:enrichment#ABSENT",
                        source_db="Pathway_Enrichment",
                        snippet=f"Pathway '{p}' not detected in significant computed enrichments",
                        relevance=0.0,
                        timestamp=now,
                    )
                )

    trace = {
        "agent": "evidence_retriever",
        "dataset": comp.dataset,
        "n_records": len(records),
        "grounded_records": sum(1 for r in records if r.relevance > 0),
        "missing_records": sum(1 for r in records if r.relevance == 0),
        "corpus": "computed_differential_expression_and_enrichment",
    }
    return records, trace
