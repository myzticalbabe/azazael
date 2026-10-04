"""compliance_ratchet.py — fail-closed ratchet on scanner category counts.

P0: the RULE 0X-7 scanner gates commits; this ratchet fails when any of the
three baselined categories INCREASES above the recorded counts. Baseline is
measured, not aspirational: `config/compliance_baseline.json` holds the
counts at ratchet time (2026-10-03: unicode_emoji 1272,
import_inside_function 954, hardcoded_win_path 14).

Usage:
    python scripts/compliance_ratchet.py            # check, exit 1 on increase
    python scripts/compliance_ratchet.py --record   # re-measure baseline
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "config" / "compliance_baseline.json"
SCANNER = ROOT / "src" / "CORE" / "compliance" / "scanner.py"
KEYS = ("unicode_emoji", "import_inside_function", "hardcoded_win_path")


def measure() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCANNER), "--report", "--dir", str(ROOT / "src")],
        capture_output=True, text=True, timeout=600)
    counts = {}
    for line in (proc.stdout or "").splitlines():
        m = re.match(r"\s*(\w+):\s+(\d+)\s*$", line)
        if m and m.group(1) in KEYS:
            counts[m.group(1)] = int(m.group(2))
    missing = [k for k in KEYS if k not in counts]
    if missing:
        print("ratchet: scanner output missing %s" % missing)
        return {}
    return counts


def main(argv: list[str]) -> int:
    if "--record" in argv:
        counts = measure()
        if not counts:
            return 2
        BASELINE.write_text(json.dumps(counts, indent=2) + "\n",
                            encoding="utf-8")
        print("ratchet: baseline recorded %s" % counts)
        return 0
    if not BASELINE.is_file():
        print("ratchet: no baseline (run --record); skipping")
        return 0
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    now = measure()
    if not now:
        return 2
    bad = ["%s %s -> %s" % (k, base.get(k), now[k])
           for k in KEYS if now[k] > int(base.get(k, 0))]
    if bad:
        print("ratchet: BLOCKED, category increased: %s" % "; ".join(bad))
        print("ratchet: fix the violations or re-record with --record")
        return 1
    print("ratchet: OK %s" % now)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
