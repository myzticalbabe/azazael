"""Nightly maintenance entrypoint for Task Scheduler.

Runs CORE.data_retention.run_maintenance(): event TTL, session rotation,
DB quota check, .audit archival, conditional VACUUM, WAL checkpoint.
Appends results to logs/maintenance.log (scheduler captures no output).

CWD-independent: uses absolute paths throughout.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, "C:/Users/clint/azazael/src")

LOG = Path(r"C:\Users\clint\azazael\logs\maintenance.log")


def main() -> int:
    from CORE.data_retention import run_maintenance
    LOG.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        results = run_maintenance()
    except Exception as e:  # never fail the scheduled task loudly
        results = {"fatal": str(e)[:200]}
    elapsed = time.perf_counter() - t0
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"=== {time.strftime('%Y-%m-%dT%H:%M:%S')} ({elapsed:.0f}s) ===\n")
        for task, result in results.items():
            status = "OK" if "error" not in result else "FAIL"
            f.write(f"  [{status}] {task}: {result}\n")
    print(f"maintenance done in {elapsed:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
