"""Run the graph semantic-extraction pipeline in order.

Mechanical steps only. Step 4 (authoring nodes/edges) is the LLM's job — this
runner emits the digest for reading and then consumes whatever the authored
`semantic_layer.py` currently contains.

Usage (from the repo root):
    python tools/graph_semantic/run_extraction.py            # full pipeline
    python tools/graph_semantic/run_extraction.py --digest   # stop after the digest
    python tools/graph_semantic/run_extraction.py --no-build # skip merge/export
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

# Order matters: ast_index and doc_scope are prerequisites for everything after.
STEPS = [
    ("ast_index.py", "label -> AST node id index (edge anchors)"),
    ("doc_scope.py", "enumerate project docs + exclusions"),
    ("doc_digest.py", "compact digest for the LLM to read"),
    ("semantic_layer.py", "emit the authored semantic fragment"),
    ("doc_layer.py", "one document node per doc + buckets + xrefs"),
    ("concept_layer.py", "deduped concept hubs from headings"),
]

BUILD = ("build_graph.py", "merge + cluster + label + export")


def run(script: str, label: str) -> int:
    print(f"\n=== {script} — {label} ===", flush=True)
    proc = subprocess.run(
        [sys.executable, str(HERE / script)],
        cwd=str(ROOT),
        check=False,
        timeout=1800,  # a full merge+cluster can take many minutes
    )
    if proc.returncode != 0:
        print(f"FAILED: {script} (exit {proc.returncode})", file=sys.stderr)
    return proc.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--digest", action="store_true",
                    help="stop after the digest so the agent can author")
    ap.add_argument("--no-build", action="store_true",
                    help="emit fragments but do not merge/export the graph")
    args = ap.parse_args()

    for script, label in STEPS:
        rc = run(script, label)
        if rc != 0:
            return rc
        if args.digest and script == "doc_digest.py":
            print("\nDigest ready: read graphify-out/_digest_p1..p4.txt, then edit "
                  "tools/graph_semantic/semantic_layer.py and re-run without --digest.",
                  flush=True)
            return 0

    if not args.no_build:
        rc = run(*BUILD)
        if rc != 0:
            return rc
        print("\nNext: graphify cluster-only . --no-viz --no-label  (regenerate report)",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
