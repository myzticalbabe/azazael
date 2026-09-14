#!/usr/bin/env python3
"""Live threat vitals log (local reads only; feeds pulled by separate jobs).

Schedule (user-level): hourly.
"""
import json
import logging
import sys
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)
sys.path.insert(0, "C:/Users/clint/azazael/src")

LOG = "G:/source-of-truth/azazael_models/threat_status.jsonl"


def main() -> int:
    from CORE.WORMS.expansion.threatmon import ThreatIntelMonitorWorm
    snap, alerts = ThreatIntelMonitorWorm().check_health()
    line = json.dumps({"at": snap.timestamp, "snapshot": snap.__dict__,
                       "alerts": [a.__dict__ for a in alerts]})
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError as e:
        print(f"log write failed: {e}")
    s = snap.__dict__
    print(f"feed={s['feed_rows']} online={s['online_malicious']} "
          f"decided={s['quorum_decided']} ledger={s['ledger_triage_samples']} "
          f"urlscan={s['urlscan_corroborated_hosts']} ebpf={s['ebpf_comms_baselined']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
