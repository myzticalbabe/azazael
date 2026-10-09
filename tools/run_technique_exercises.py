#!/usr/bin/env python3
# coding: utf-8
"""Run the six SOTA technique exercises, and fail if any of them stops working.

Why this exists (2026-10-09): the six incorporation modules
(`CORE/structured_action.py`, `latent_align.py`, `latent_refine.py`,
`dispatch_plan.py`, `rubric_evolution.py`, `skill_library.py`) shipped with six
exercise scripts that each pass by hand -- and nothing in the tree invoked them.
`tools/terence_invariants.py`'s `orphan_mechanisms` oracle flagged every one:
"has no importer, no scheduler entry, and no shell reference. Written and never
invoked." A mechanism that only works when a human types its name is not wired;
it is a claim.

This is the missing caller. It is deliberately one entry point rather than six
scheduler jobs: the chain controller's plan is the scheduler, and its jobs are
meant to be cycles, not a pile of one-shot probes. Registering `techniques` as a
single job gives all six a real caller and gives the oracle something true to
see.

A failing exercise is reported as a FAILURE, never as a skip: an exercise that
cannot run is the exact condition this tool exists to surface.

Usage:
    python tools/run_technique_exercises.py            # run all six
    python tools/run_technique_exercises.py --json     # machine-readable
    python tools/run_technique_exercises.py --list     # names only

Exit 0 = every exercise ran and reported chain/complete success.
Exit 1 = at least one exercise failed, timed out, or did not report a chain.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "technique_exercises.json"

#: (script, technique it exercises). The script names are load-bearing: the
#: orphan oracle resolves a caller by finding the filename in another file's
#: text, so dropping a name here re-orphans that exercise.
EXERCISES: tuple[tuple[str, str], ...] = (
    ("tools/exercise_l7_asil.py",
     "EP465 ASIL -- JSON observations + semantic actions"),
    ("tools/exercise_l7_latent.py",
     "EP440 StateBridge -- orthogonal latent alignment"),
    ("tools/exercise_lrt_refine.py",
     "EP472 LRT -- tiny recurrent latent refiner"),
    ("tools/exercise_p2b_dispatch.py",
     "EP186/EP187 -- DAG dispatch + common-subgraph elimination"),
    ("tools/exercise_p2b_slice2.py",
     "EP209 SAGA -- workflow-atomic affinity + work stealing"),
    ("tools/exercise_p2c_rubric.py",
     "EP471 ARISE-RL -- rubric Generator/Solver co-evolution"),
    ("tools/exercise_technique_runtime.py",
     "all 181 -- every harvested technique has a production call site"),
    ("tools/exercise_wired_boundaries.py",
     "production boundaries reach the runtime (not just import it)"),
)


def run_exercise(script: str, timeout: int = 300) -> dict:
    """Run one exercise and parse its verdict from the last output line.

    The exercises print a human narrative and then a single JSON object as the
    last line; that line is the machine-readable verdict and the only part
    parsed here.
    """
    path = ROOT / script
    rec: dict = {"script": script, "exists": path.is_file()}
    if not rec["exists"]:
        rec.update(rc=None, ok=False, error="script missing")
        return rec
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(ROOT), capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        rec.update(rc=None, ok=False, error="timeout")
        return rec
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    rec["rc"] = proc.returncode
    rec["last"] = lines[-1][:200] if lines else ""
    verdict = None
    for ln in reversed(lines[-3:]):
        ln = ln.strip()
        if ln.startswith("{") and ln.endswith("}"):
            try:
                verdict = json.loads(ln)
            except ValueError:
                continue
            break
    if verdict is None:
        rec.update(ok=False, error="no JSON verdict on the last lines")
        if proc.stderr:
            rec["stderr"] = proc.stderr.strip()[-200:]
        return rec
    rec["verdict"] = verdict
    # Every exercise reports `chain`; a false chain means the mechanism ran but
    # did not close its loop, which is the failure this tool cares about most.
    rec["ok"] = proc.returncode == 0 and verdict.get("chain") is True
    return rec


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--list", action="store_true", help="print the exercises only")
    args = ap.parse_args(argv)

    if args.list:
        for script, what in EXERCISES:
            print("%-34s %s" % (script, what))
        return 0

    results = [run_exercise(script) for script, _ in EXERCISES]
    passed = [r for r in results if r.get("ok")]
    failed = [r for r in results if not r.get("ok")]

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(
        {"total": len(results), "passed": len(passed),
         "failed": [r["script"] for r in failed], "results": results},
        indent=1), encoding="utf-8")

    if args.json:
        print(json.dumps({"total": len(results), "passed": len(passed),
                          "failed": [r["script"] for r in failed],
                          "results": results}, indent=2))
        return 1 if failed else 0

    print("TECHNIQUE EXERCISES (%d)" % len(results))
    for r in results:
        state = "ok  " if r.get("ok") else "FAIL"
        print("  %s %-34s %s" % (state, r["script"],
                                 r.get("error") or r.get("last", "")))
    print()
    if failed:
        print("FAIL: %d/%d exercise(s) not passing: %s"
              % (len(failed), len(results),
                 ", ".join(r["script"] for r in failed)))
        return 1
    print("OK: %d/%d technique exercises ran and closed their loop" % (
        len(passed), len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
