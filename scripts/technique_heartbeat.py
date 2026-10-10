#!/usr/bin/env python3
"""technique_heartbeat.py — unconditional heartbeat caller for the technique runtime.

Closes the L3/L4 gap: run_all/status had no production callers, so nothing
executed the registered adapters outside manual runs. This script is the
heartbeat: invoke every adapter, collect fleet health, leave one join row.

ALLOW_WRITES policy (decided 2026-10-10, see Step 3): the module default in
technique_wiring/_l1_memory.py stays False so ad-hoc run_all() never deposits
rows; the heartbeat ALONE opts in per-run, bounding deposits to one row per
write-loop adapter (EP120 reflection_lesson, EP131 memory_tier_rollup, EP235
recall_feedback) per heartbeat. Revisit only with an explicit order.

Hook discipline: every run leaves source="technique-link" rows
(heartbeat summary + per-hook verify rows), so fleet_link_health and the
live_monitor links block read this heartbeat even when nothing fails.

Fail-open: exit code is always 0; failures go to stderr + failure ledger.
Run from the repo's scripts/ dir or anywhere (paths resolve from __file__).
Scheduled as Azazael-TechniqueHeartbeat (hourly) — see technique_heartbeat.bat.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _fail(where, exc):
    try:
        from CORE.failure_ledger import note_failure
        note_failure(where, exc)
    except Exception as inner:
        print(f"heartbeat recorder down: {where}: {type(inner).__name__}",
              file=sys.stderr)
    print(f"heartbeat note: {where}: {type(exc).__name__}: {exc}", file=sys.stderr)


def main() -> int:
    t0 = time.perf_counter()
    out = {"ok": True, "steps": {}}
    try:
        from CORE.technique_runtime import (
            fleet_link_health,
            load_slices,
            record_link,
            run_all,
        )
        from CORE.technique_wiring import _l1_memory as l1

        out["steps"]["slices"] = load_slices()
        # Step 3 policy: heartbeat-only opt-in, restored immediately after.
        prev = l1.enable_writes(True)
        try:
            run = run_all(record=True)
        finally:
            l1.enable_writes(prev)
        out["steps"]["run_all"] = {
            "n": run.get("n"), "engaged": run.get("engaged"),
            "errored": run.get("errored"),
        }
        out["steps"]["health"] = fleet_link_health(limit=1000)
        try:
            from CORE.WORMS.expansion.queens import rainbow_round
            out["steps"]["rainbow"] = rainbow_round(probe_limit=1)
        except Exception as exc:
            _fail("technique-heartbeat:rainbow", exc)
            out["steps"]["rainbow"] = {"ok": False}
        ok = run.get("errored", 1) == 0
        out["ok"] = bool(ok)
        try:
            out["steps"]["link_kept"] = bool(record_link(
                "technique_heartbeat", "hourly-run-all",
                bool(ok), citation=f"engaged={run.get('engaged')}/n={run.get('n')}"))
        except Exception as exc:  # link row is evidence, never fatal
            _fail("technique-heartbeat:record-link", exc)
            out["steps"]["link_kept"] = False
    except Exception as exc:  # noqa: BLE001 — heartbeat must never raise
        _fail("technique-heartbeat:run", exc)
        out["ok"] = False
        out["error"] = f"{type(exc).__name__}: {exc}"
        out["trace"] = traceback.format_exc(limit=5)
    out["ms"] = round((time.perf_counter() - t0) * 1000, 2)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
