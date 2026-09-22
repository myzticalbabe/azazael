#!/usr/bin/env python3
# coding: utf-8
"""Refresh graphify-out/ WITHOUT an LLM, then clear the in-flight marker.

Why this entry point exists. The spine cycle's proprioception gate refuses to
write while any derived artifact is stale, and `graphify-out/graph.json` plus
`GRAPH_REPORT.md` are two of the seven it checks. `tools/refresh_all.py`
deliberately does not rebuild them, so the gate could only ever be satisfied by
hand -- which is exactly what happened: the loop refused hourly from
2026-09-18T20:45 to 2026-09-20T02:00 and reported nothing wrong.

Two things made the graph look un-refreshable, and neither is true:

1. `tools/graph_rebuild.py` runs the SEMANTIC pass, which on the free tier is
   limited to 5 requests/minute and loses chunks to 429s. That is the quota
   problem, and it is real -- for that pass.
   `graphify update` re-extracts CODE and needs no model at all.

2. `graphify` is installed in the SYSTEM Python 3.14, while the repo's refresh
   path runs under the 3.14t venv. `sys.executable -m graphify` therefore can
   never reach it. This script takes the interpreter explicitly instead.

Order matters: `update` rewrites graph.json, then `cluster-only` regenerates
GRAPH_REPORT.md from it. `graph_rebuild.py` records that running extract alone
left the report 49 sources stale -- the rebuild reproducing the very
report/artifact mismatch the freshness guard exists to catch.

Takes ~31 minutes on this tree (101k files), so it is meant to be launched
detached, not awaited.

Usage:
    python scripts/graph_refresh_no_llm.py            # run it here, in front
    python scripts/graph_refresh_no_llm.py --status   # report staleness only
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: graphify lives in the system interpreter, not the venv. Hard-coded rather
#: than inherited from sys.executable because inheriting it is the bug.
GRAPHIFY_PY = Path(r"C:\Users\clint\AppData\Local\Programs\Python\Python314\python.exe")

#: The cycle drops this while a pass is in flight so the next fire does not
#: start a second one. Cleared here on every exit path.
MARKER = Path(os.path.expanduser("~")) / ".azazael" / "graph_refresh.running"

#: Full per-step output is kept here. On 2026-09-21 the `update .` step died
#: with a single reported line ("EOF marker not found") after 1522s and the
#: very next question -- *what* failed? -- could not be answered, because every
#: earlier line had been discarded. That is the one-line diagnostic cap the
#: audits keep re-finding, applied to this script's own reporting.
LOGS = ROOT / "logs"

STEPS: tuple[tuple[str, ...], ...] = (
    ("-m", "graphify", "update", "."),
    ("-m", "graphify", "cluster-only", "--out", "graphify-out"),
)


def log(msg: str) -> None:
    print(f"{datetime.now().isoformat(timespec='seconds')} {msg}", flush=True)


def graph_stale(root: Path | None = None) -> bool | None:
    """Is graphify-out/ behind its sources? None if the probe cannot answer.

    None is deliberately not False: an unreadable probe is not evidence of
    freshness, and the caller decides what to do about that.
    """
    root = root or ROOT
    try:
        sys.path.insert(0, str(root / "tools"))
        import artifact_freshness as af  # noqa: PLC0415

        rows = af.audit(root)
    except Exception:
        return None
    graph = [r for r in rows
             if str(r.get("artifact", "")).startswith("graphify-out/")]
    return any(r.get("stale") for r in graph) if graph else None


def write_marker() -> None:
    """Claim the in-flight slot so the hourly cycle does not start a second pass.

    `spine_cycle_apply._launch_graph_refresh()` writes this marker before it
    spawns us, but a standalone run (`python scripts/graph_refresh_no_llm.py`)
    never did. So the scheduled cycle, which only consults the marker, could see
    "nothing in flight" and launch a competing ~31 minute re-extract over the
    same tree. The reader parses "<start-time> <pid>", so the body must be
    written in exactly that shape -- a live pid is what lets the guard tell a
    real pass from a corpse left by a killed one.
    """
    try:
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.write_text("%.6f %d" % (time.time(), os.getpid()), encoding="utf-8")
    except OSError:
        pass


def clear_marker() -> None:
    try:
        MARKER.unlink()
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--status", action="store_true",
                    help="report graphify-out/ staleness and exit")
    args = ap.parse_args(argv)

    if args.status:
        st = graph_stale()
        print("graphify-out:", {True: "STALE", False: "current",
                                None: "unknown (probe failed)"}[st])
        return 0 if st is False else 1

    if not GRAPHIFY_PY.exists():
        log(f"FAIL: graphify interpreter missing at {GRAPHIFY_PY}")
        log("      (graphify is in the SYSTEM Python 3.14, not the 3.14t venv)")
        clear_marker()
        return 2

    write_marker()
    started = time.time()
    log(f"start (interpreter={GRAPHIFY_PY.name} pid={os.getpid()})")
    rc_all = 0
    try:
        for i, step in enumerate(STEPS, start=1):
            t0 = time.perf_counter()
            try:
                proc = subprocess.run([str(GRAPHIFY_PY), *step], cwd=str(ROOT),
                                      capture_output=True, text=True, timeout=5400)
                rc = proc.returncode
                text = (proc.stdout or "") + (proc.stderr or "")
            except subprocess.TimeoutExpired as exc:
                rc = None
                text = "timed out after 5400s\n%s" % (
                    (exc.stdout if isinstance(exc.stdout, str) else "") or "")
            tail = [ln for ln in text.splitlines() if ln.strip()]
            dump = LOGS / ("graph_refresh_step%d.log" % i)
            try:
                LOGS.mkdir(parents=True, exist_ok=True)
                dump.write_text(text or "(no output)\n", encoding="utf-8",
                                errors="replace")
            except OSError:
                dump = None
            log(f"{' '.join(step[2:])!r:34} rc={rc} in {time.perf_counter() - t0:.0f}s"
                f" | {tail[-1][:140] if tail else 'no output'}"
                + (" | full: %s" % dump.relative_to(ROOT) if dump else ""))
            if rc != 0:
                rc_all = rc or 1
    finally:
        # Always clear, so a failed pass does not block the next attempt; the
        # caller's mtime-based backstop covers a process that dies here.
        clear_marker()

    st = graph_stale()
    log("graphify-out: %s" % {True: "STILL STALE", False: "current",
                              None: "unknown (probe failed)"}[st])
    log(f"done in {time.time() - started:.0f}s rc={rc_all}")
    return 0 if (rc_all == 0 and st is False) else 1


if __name__ == "__main__":
    sys.exit(main())
