#!/usr/bin/env python3
"""Berks Counseling Center live monitor (first-party public sites only).

Runs BerksMonitorWorm.check_all(), appends JSONL to G:, feeds per-site
up/down into the spine ledger (downtime becomes training signal).
Schedule (user-level): every 30 min.
"""
import json
import logging
import sys
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)
sys.path.insert(0, "C:/Users/clint/azazael/src")

LOG = "G:/source-of-truth/azazael_models/bcc_status.jsonl"


def main() -> int:
    from CORE.WORMS.expansion.berks import BerksMonitorWorm
    from CORE import spine_registry as sp
    rep = BerksMonitorWorm().check_all()
    line = json.dumps({"at": datetime.now(timezone.utc).isoformat(),
                       "up": rep["up"], "of": rep["of"], "results": rep["results"]})
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"log write failed: {e}")
    for r in rep["results"]:
        try:
            sp.record_outcome("monitor", f"berks:{r['host']}", bool(r["up"]), 0.0)
        except Exception:
            pass
    try:
        sp.save_spine_state()
    except Exception:
        pass
    for r in rep["results"]:
        state = "UP" if r["up"] else "DOWN"
        print(f"{state} {r['host']} http={r.get('http_status')} "
              f"{r.get('http_ms', '?')}ms tls_days={r.get('tls_days_left')}")
    return 0 if rep["up"] == rep["of"] else 1


if __name__ == "__main__":
    sys.exit(main())
