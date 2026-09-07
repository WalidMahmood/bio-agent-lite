"""Computational Analyst: DETERMINISTIC tool execution layer (Master #11).
No language model is used for numerical calculations.
Delegates to deterministic tools (pydeseq2, CuffDiff parser, FPKM descriptive stats, gseapy).
Returns typed ComputationalResult with execution logging.
"""
import os
import sys
from typing import Tuple, Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.schemas import ComputationalResult
from tools.dispatcher import execute_computation


def run_computation(
    dataset: str = "GSE202768",
    contrast: Optional[str] = None,
    top_n_genes: int = 25,
    top_n_pathways: int = 5,
    padj_thresh: float = 0.05,
) -> Tuple[ComputationalResult, Dict[str, Any]]:
    """Execute deterministic computational analysis for target dataset."""
    result = execute_computation(dataset=dataset, contrast=contrast)

    trace = {
        "agent": "computational_analyst",
        "llm_used": False,
        "dataset": result.dataset,
        "data_type": result.data_type,
        "contrast": result.contrast,
        "genes_tested": result.n_total_tested,
        "significant_genes": result.n_sig,
        "up_regulated": result.n_up,
        "down_regulated": result.n_down,
        "execution_log": result.execution_log,
    }
    return result, trace
