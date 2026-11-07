#!/usr/bin/env python3
"""claim_agreement.py -- Aether A-1: the gate checks whether scored claims are true.

The four HED auditors check artifacts, settings, legs and heads. None of them
asks whether the system's own scored predictions hold up. This leg replays the
live log through the dream agreement metric (a blocked guess meeting a blocked
answer is a hit -- the lineage correctly predicted the wall) and fails when the
live hit-rate drops below the tuned floor.

Floor: `hyper_edge.agreement_floor`, written by agreement_floor.py (A-2).
0.0 (default) is advisory: the rate prints, the leg passes, and the floor
stays visibly untuned rather than silently strict.

Exit: 0 rate >= floor, 1 rate < floor, 2 blind (no log, or no guess/answer
pairs to replay -- HED-2's rule: an absence is never worded as a pass).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def measure(log_path=None) -> dict:
    """Replay the live log; return pairs/hits/hit_rate. Pure read, no writes."""
    from eve_unleashed.intuition import dream  # noqa: PLC0415

    dr = dream(log_path=log_path)
    return {"pairs": dr["pairs"], "hits": dr["hits"],
            "hit_rate": dr["hit_rate"]}


def floor_default() -> float:
    try:
        from defaults_profile import read_default  # noqa: PLC0415
        return float(read_default("hyper_edge.agreement_floor", 0.0))
    except Exception as exc:
        print("claim_agreement: floor unreadable (%s), advisory 0.0" % exc,
              file=sys.stderr)
        return 0.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=None)
    ap.add_argument("--floor", type=float, default=None)
    args = ap.parse_args(argv)
    floor = args.floor if args.floor is not None else floor_default()
    try:
        m = measure(args.log)
    except FileNotFoundError:
        print("claim_agreement: BLIND -- no live log to replay")
        return 2
    if not m["pairs"]:
        print("claim_agreement: BLIND -- 0 guess/answer pairs, nothing to replay")
        return 2
    verdict = "HOLD" if m["hit_rate"] >= floor else "ROTTED"
    print("claim_agreement: pairs=%d hits=%d hit_rate=%.3f floor=%.3f %s"
          % (m["pairs"], m["hits"], m["hit_rate"], floor, verdict))
    return 0 if m["hit_rate"] >= floor else 1


if __name__ == "__main__":
    sys.exit(main())
