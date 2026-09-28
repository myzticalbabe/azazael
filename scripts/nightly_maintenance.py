"""Nightly maintenance entrypoint for Task Scheduler.

Runs CORE.data_retention.run_maintenance(): event TTL, session rotation,
DB quota check, .audit archival, conditional VACUUM, WAL checkpoint.
Appends results to logs/maintenance.log (scheduler captures no output).

CWD-independent: uses absolute paths throughout.
"""
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))

LOG = _ROOT / "logs" / "maintenance.log"


def main() -> int:
    from CORE.data_retention import run_maintenance
    LOG.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    # Chain-quiet guard (2026-09-27): bulk writes (cap trims, quota
    # batches, VACUUM) race the chain's 8 writers for the DB lock. If a
    # chain job fired within the last 15 minutes, run the light subset
    # (TTL + caps are small indexed deletes); the heavy passes wait for a
    # quiet window. Never fail the task on this decision.
    heavy_ok = True
    try:
        import json as _json
        _lf = _ROOT / "state" / "chain_controller_last_fire.json"
        _at = (_json.loads(_lf.read_text(encoding="utf-8")).get("at", "")
               if _lf.is_file() else "")
        if _at:
            from datetime import datetime as _dt
            _parsed = _dt.fromisoformat(_at)
            if _parsed.tzinfo is None:
                # 2026-09-28: chain writes naive local isoformat; comparing
                # against aware now() raised (naive-vs-aware) and the check
                # failed open every night. Assume local wall time.
                _parsed = _parsed.astimezone()
            _age = (_dt.now().astimezone() - _parsed).total_seconds()
            if _age < 900:
                heavy_ok = False
                print("chain active %.0fs ago: light pass (no vacuum/quota)" % _age)
    except Exception as _e:
        print("chain-quiet check failed open: %s" % str(_e)[:120])
    try:
        results = run_maintenance(light=not heavy_ok)
    except Exception as e:  # never fail the scheduled task loudly
        results = {"fatal": str(e)[:200]}
    elapsed = time.perf_counter() - t0
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"=== {time.strftime('%Y-%m-%dT%H:%M:%S')} ({elapsed:.0f}s) ===\n")
        for task, result in results.items():
            status = "OK" if "error" not in result else "FAIL"
            f.write(f"  [{status}] {task}: {result}\n")
    # Drain the PAMS fallback queue on the live path (2026-09-27): the
    # dashboard-thread drain never runs (no --watch process), so 5k rows
    # sat unflushed since 09-24. Flush marks only PAMS-confirmed rows and
    # no-ops when PAMS is down — safe to run every night.
    try:
        from CORE.MemoryBus import MemoryBus
        drained = MemoryBus().flush_local_queue()
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"  bus_drain: {drained} rows flushed\n")
    except Exception as _e:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"  bus_drain: SKIPPED ({str(_e)[:120]})\n")
    # The pass itself is worth remembering: which caps/TTLs fired and what
    # the quota backstop did. Fail-soft — a dead store must not fail upkeep.
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        if store is not None:
            summary = {k: (v if isinstance(v, (int, float, str, bool))
                           else str(v)[:300])
                       for k, v in (results or {}).items()}
            store.record_event(source="retention", event_type="retention_pass",
                               data={"tasks": summary,
                                     "elapsed_s": round(elapsed, 1)},
                               severity="info",
                               tags=["retention", "maintenance"])
    except Exception:
        pass
    print(f"maintenance done in {elapsed:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
