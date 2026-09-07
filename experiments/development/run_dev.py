"""End-to-end dev run on GSE202768. Requires llama-server up on :8080 for LLM steps.
Usage: python experiments/development/run_dev.py [--no-llm]
Saves: outputs/traces/<run_id>.json + outputs/reports/dev_report_<run_id>.md
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.graph import build_graph

QUESTION = ("Compare DOX-induced PRRX1 knockdown (KD_DOX) against uninduced control "
            "(KD_noDOX) in Hs578 TNBC cells and identify genes and pathways "
            "associated with the response.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()
    run_id = "dev_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    graph = build_graph(use_llm=not args.no_llm)
    final = graph.invoke({"question": QUESTION})
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    tpath = os.path.join(base, "outputs", "traces", run_id + ".json")
    os.makedirs(os.path.dirname(tpath), exist_ok=True)
    with open(tpath, "w") as fh:
        json.dump({"run_id": run_id, "question": QUESTION,
                   "use_llm": not args.no_llm, **final}, fh, indent=2, default=str)
    v = final["verdict"]
    print(f"run {run_id}: verdict={v['status']} errors={len(v['errors'])} "
          f"warnings={len(v['warnings'])} iterations={final.get('iterations', 0)}")
    for e in v["errors"]:
        print("  ERR:", e)
    for w in v["warnings"]:
        print("  WARN:", w)
    print("trace:", tpath)


if __name__ == "__main__":
    main()
