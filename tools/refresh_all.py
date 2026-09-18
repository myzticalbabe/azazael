#!/usr/bin/env python3
# coding: utf-8
"""One command to refresh every derived artifact, then audit the result.

The refresh order is the measured dependency chain, not a guess:

    mesh_function_preflight.py             -> NEURAL_MESH_FUNCTION_TODO.md
    mesh_function_preflight.py --verdict   -> NEURAL_MESH_WIRE_OR_CUT.json
    nature_integration_map.py              -> MAP.json + INTEROP.mmd + dataset

The census must run first because `--verdict` reads the probe results, and the
map last because it consumes the verdict table. Running them out of order
produces a map built on a previous census -- which is exactly how the table
went stale in the first place (section 12 of the audit analysis).

The graph is *not* rebuilt here on purpose: a graphify pass is minutes long,
needs its own interpreter, and is the one artifact whose rebuild has a
side-effect budget. `--audit-only` reports its staleness instead.

Exit 0 only when the trailing freshness audit passes, so this is safe to put in
a session-startup sequence or a pre-commit hook: a stale map becomes a non-zero
exit rather than a silent input.

Usage:
    python tools/refresh_all.py               # refresh + audit
    python tools/refresh_all.py --audit-only  # audit only, no writes
    python tools/refresh_all.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]

# (argv tail, human label). Order is the dependency chain.
STEPS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("tools/mesh_function_preflight.py",), "census -> NEURAL_MESH_FUNCTION_TODO.md"),
    (("tools/mesh_function_preflight.py", "--verdict"), "verdict -> NEURAL_MESH_WIRE_OR_CUT.json"),
    (("tools/nature_integration_map.py",), "map -> MAP.json + INTEROP.mmd + dataset"),
)


def run_step(args: Sequence[str], timeout: int = 900) -> dict:
    """Run one refresh step; never let one failure abort the audit."""
    cmd = [sys.executable, *args]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(args), "rc": None, "error": "timeout"}
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    return {"cmd": " ".join(args), "rc": proc.returncode,
            "last": tail[0][:160], "error": (proc.stderr or "").strip()[-160:]}


def audit() -> tuple[int, dict]:
    """Run the freshness guard in-process and return (rc, parsed)."""
    sys.path.insert(0, str(ROOT / "tools"))
    import artifact_freshness as af  # noqa: PLC0415 -- local import keeps this runnable as a script

    rows = af.audit(ROOT)
    graph = af.graph_report_mismatch(ROOT)
    stale = [r for r in rows if r["stale"]]
    return (1 if stale or graph["mismatch"] else 0), {
        "artifacts": rows, "graph": graph,
        "stale_count": len(stale),
        "stale": [r["artifact"] for r in stale],
    }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit-only", action="store_true",
                    help="report staleness without rewriting anything")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    results: list[dict] = []
    if not args.audit_only:
        for step, label in STEPS:
            res = run_step(step)
            res["label"] = label
            results.append(res)
            if not args.json:
                state = "ok" if res["rc"] == 0 else "FAILED(rc=%s)" % res["rc"]
                print("[refresh] %-14s %s  %s" % (state, label, res.get("last", "")))

    rc, report = audit()
    if args.json:
        print(json.dumps({"refresh": results, "audit": report}, indent=2))
        return rc

    print()
    print("%-44s %-8s %s" % ("ARTIFACT", "STATUS", "NEWER SOURCES"))
    for row in report["artifacts"]:
        if not row["exists"]:
            status, detail = "MISSING", "-"
        elif row["stale"]:
            status, detail = "STALE", str(row["newer_count"])
        else:
            status, detail = "current", "0"
        print("%-44s %-8s %s" % (row["artifact"], status, detail))
    g = report["graph"]
    if g.get("mismatch"):
        print("\ngraph/report: MISMATCH -- %s" % g["reason"])
    elif g.get("checked"):
        print("\ngraph/report: consistent (nodes=%s clustered=%s)"
              % (g.get("nodes"), g.get("clustered")))

    failed = [r for r in results if r["rc"] != 0]
    print()
    if rc == 0 and not failed:
        print("OK: refreshed and audited -- every derived artifact is current")
        return 0
    if failed:
        print("FAIL: %d refresh step(s) failed: %s"
              % (len(failed), ", ".join(r["cmd"] for r in failed)))
        return 1
    print("FAIL: %d stale artifact(s)%s"
          % (report["stale_count"],
             ", plus a graph/report mismatch" if g.get("mismatch") else ""))
    return 1


if __name__ == "__main__":
    sys.exit(main())
