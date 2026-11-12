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

Per-rung floors (U-2): the global rate averages the weakest rung away, so the
leg also holds the weakest rung with >= MIN_RUNG_PAIRS pairs against
`hyper_edge.agreement_rung_floor`. Scoring is the native replay kernel
(native_replay: Cython when built, pure Python otherwise -- same math).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))


def measure(log_path=None) -> dict:
    """Replay the live log; return pairs/hits/rate/by_rung. Pure read."""
    from eve_unleashed.live_log import read_events  # noqa: PLC0415
    from eve_unleashed.native_replay import rung_rates  # noqa: PLC0415

    return rung_rates(read_events(log_path)["records"])


MIN_RUNG_PAIRS = 5


def floor_default(which="floor") -> float:
    # Literal keys, never a computed "hyper_edge." + name: settings_shadow
    # resolves a read only when the reader is called with a literal string,
    # and a parameterized key reads as orphan_knob (measured 2026-11-07).
    try:
        from defaults_profile import read_default  # noqa: PLC0415
        if which == "rung":
            return float(read_default("hyper_edge.agreement_rung_floor", 0.0))
        return float(read_default("hyper_edge.agreement_floor", 0.0))
    except Exception as exc:
        print("claim_agreement: floor unreadable (%s), advisory 0.0" % exc,
              file=sys.stderr)
        return 0.0


def weakest_rung(by_rung: dict):
    """(rung, rate) of the weakest qualifying cell, else (None, None)."""
    cand = [(r, c["rate"]) for r, c in by_rung.items()
            if c.get("pairs", 0) >= MIN_RUNG_PAIRS]
    if not cand:
        return None, None
    return min(cand, key=lambda kv: kv[1])


LEDGER_KEYS = {"frame", "cursor_id", "tree", "node", "verdict", "claim",
               "prev_hash", "hash"}
# In the wild (LIVEVIEW_CURSOR_SWARM_V0.jsonl, 22 rows): landed, held,
# quarantine, rolledback. Measured 2026-11-12, not quoted from prose.
LEDGER_VERDICTS = {"landed", "held", "quarantine", "rolledback"}


def validate_ledger(path):
    """Check every ledger row: JSON, exact keys, verdict, chain, hash.

    Hash scheme measured against the live ledger: sha256 over
    json.dumps(body_without_hash, sort_keys=True) with DEFAULT separators,
    prev links the previous row's hash, 'GENESIS' opens row 1.
    Returns {"rows", "bad": [(lineno, frame, reason)], "verdicts"}.
    """
    import hashlib
    import json
    bad, verdicts, prev, n = [], {}, "GENESIS", 0
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            n += 1
            try:
                row = json.loads(line)
            except ValueError as exc:
                bad.append((lineno, None, "not JSON: %s" % exc))
                continue
            frame = row.get("frame")
            keys = set(row)
            if keys != LEDGER_KEYS:
                bad.append((lineno, frame,
                            "keys %s (want exactly %s)"
                            % (sorted(keys), sorted(LEDGER_KEYS))))
                continue
            if row.get("verdict") not in LEDGER_VERDICTS:
                bad.append((lineno, frame,
                            "verdict %r not in %s"
                            % (row.get("verdict"), sorted(LEDGER_VERDICTS))))
            verdicts[row.get("verdict")] = verdicts.get(row.get("verdict"), 0) + 1
            if row.get("prev_hash") != prev:
                bad.append((lineno, frame, "prev_hash breaks the chain"))
            body = {k: v for k, v in row.items() if k != "hash"}
            expect = hashlib.sha256(
                json.dumps(body, sort_keys=True).encode()).hexdigest()
            if row.get("hash") != expect:
                bad.append((lineno, frame, "hash mismatch"))
            prev = row.get("hash", prev)
    return {"rows": n, "bad": bad, "verdicts": verdicts}


def ledger_main(path) -> int:
    try:
        rep = validate_ledger(path)
    except OSError:
        print("claim_agreement: BLIND -- no ledger at %s" % path)
        return 2
    if not rep["rows"]:
        print("claim_agreement: BLIND -- 0 ledger rows, nothing to replay")
        return 2
    if rep["bad"]:
        lineno, frame, reason = rep["bad"][0]
        print("claim_agreement: BROKEN -- ledger line %d (frame %s): %s "
              "(%d rows checked)" % (lineno, frame, reason, rep["rows"]))
        return 1
    print("claim_agreement: ledger CHAIN OK N=%d verdicts=%s"
          % (rep["rows"], rep["verdicts"]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=None)
    ap.add_argument("--ledger", default=None,
                    help="cursor JSONL ledger to validate as the claim source")
    ap.add_argument("--floor", type=float, default=None)
    ap.add_argument("--rung-floor", type=float, default=None)
    args = ap.parse_args(argv)
    if args.ledger is not None:
        return ledger_main(args.ledger)
    floor = args.floor if args.floor is not None else floor_default()
    rung_floor = args.rung_floor if args.rung_floor is not None \
        else floor_default("rung")
    try:
        m = measure(args.log)
    except FileNotFoundError:
        print("claim_agreement: BLIND -- no live log to replay")
        return 2
    if not m["pairs"]:
        print("claim_agreement: BLIND -- 0 guess/answer pairs, nothing to replay")
        return 2
    wrung, wrate = weakest_rung(m["by_rung"])
    rotted = m["hit_rate"] < floor or \
        (wrate is not None and wrate < rung_floor)
    print("claim_agreement: pairs=%d hits=%d hit_rate=%.3f floor=%.3f "
          "weakest=%s rate=%s rung_floor=%.3f backend=%s %s"
          % (m["pairs"], m["hits"], m["hit_rate"], floor,
             wrung, wrate, rung_floor, m["backend"],
             "ROTTED" if rotted else "HOLD"))
    return 1 if rotted else 0

def verdict(argv=None):
    """Cursor-speed verdict: timed in-process main(), same classes as the CLI.

    Direct (single-threaded) calls only: stdout is captured with a global
    redirect, so the threaded fan-out in deep_dive keeps calling main().
    Additive by construction: main() and every print path are untouched.
    Returns {"exit", "line", "ms"}.
    """
    import contextlib  # local: the module top (and the CLI) stays byte-identical
    import io
    import time
    args = list(argv) if argv else []
    buf = io.StringIO()
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(buf):
        try:
            rc = main(args)
        except SystemExit as exc:
            rc = exc.code
    ms = (time.perf_counter() - t0) * 1000.0
    line = next((ln for ln in buf.getvalue().splitlines() if ln.strip()), "")
    return {"exit": rc if isinstance(rc, int) else 0,
            "line": line, "ms": ms}


if __name__ == "__main__":
    sys.exit(main())
