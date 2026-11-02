#!/usr/bin/env python
# coding: utf-8
"""floor_measure.py - re-measure the recall floor thresholds against the corpus.

WHY. PMB_RECALL_MIN_BEST (0.89) and PMB_RECALL_FLOOR (0.70) are a property of
the STORE, not of the software: they sit in the gap between what a noise query
and a real query score. The canon says re-measure after a large purge, because
the numbers move with the corpus. Recorded 2026-10-30: noise best 0.836 max /
0.645 mean, real best 0.949 min, a 0.113 gap.

WHAT IT MEASURES. Only the daemon (:8765) - the unfloored store. Measuring
through the proxy would measure the thresholds themselves. Each query's BEST
row score is the statistic the query floor compares, so that is what is
reported: max/mean of noise bests, min/mean of real bests, and the gap between
them, with a verdict on whether both thresholds still sit inside it.

READ-ONLY: recall calls only, no writes.

Usage:
    python tools/floor_measure.py            # 12 noise + 12 real probes
    python tools/floor_measure.py --noise 20 --real 20
    python tools/floor_measure.py --json
Exit codes: 0 = both thresholds inside the gap, 1 = a threshold is outside it
(the floor no longer separates noise from real on this corpus), 2 = the daemon
could not be measured.
"""
import argparse
import json
import random
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mcp_startup_gate as gate  # noqa: E402

#: The query floor and the row floor as shipped (azazael/tools/pmb_floor_proxy.py
#: and supervisor_mcp.py). Read from the environment when set, so a changed
#: deployment is measured rather than described.
import os  # noqa: E402
QUERY_FLOOR = float(os.environ.get("PMB_RECALL_MIN_BEST", "0.89"))
ROW_FLOOR = float(os.environ.get("PMB_RECALL_FLOOR", "0.70"))

#: REAL probes: questions this corpus must answer, in the vocabulary of the
#: project. Deliberately NOT copied from stored memory verbatim - a verbatim
#: copy measures the copy, not retrieval.
REAL = [
    "how does the pmb floor proxy filter recall rows",
    "what does the lane queue claim protocol guarantee about two lanes polling",
    "why did the kilo lane see an empty task board",
    "what is the session order gate and when must it exit non-zero",
    "how are agent order blocks generated into lane instruction files",
    "what happens when the opencode mcp client cannot reach the endpoint",
    "which interpreter is the production python for this project",
    "how do I record a lesson that must survive the session",
    "what does the anti-pattern ratchet compare against",
    "how is the memory store backed up without stopping the daemon",
    "what is the difference between a claim lease and a retired row",
    "how do domain trees avoid forking the renderer",
]

#: NOISE probes: off-topic, plus random nonces. Both classes matter - a nonce
#: can score high by accident (measured 2026-10-30: 1 nonce in 15 reached
#: 0.836), and an ordinary off-topic question is the realistic failure.
NOISE = [
    "how to bake sourdough bread at altitude",
    "who won the 1998 world cup final",
    "best chess opening against the sicilian defence",
    "what is the boiling point of nitrogen at sea level",
    "how do migratory birds navigate using magnetic fields",
    "recommend a hiking trail near reading pennsylvania",
    "what causes the northern lights",
    "how to change a bicycle chain",
    "history of the ottoman empire in the 16th century",
    "what is the airspeed velocity of an unladen swallow",
]


def _best(client, query):
    payload = client.call("recall", {"query": query, "top_k": 10})
    if payload.get("_error"):
        return None, str(payload["_error"])[:160]
    rows = [r for r in (payload.get("results") or []) if isinstance(r, dict)]
    if not rows:
        return 0.0, ""
    return max([r.get("score") or 0.0 for r in rows]), ""


def _probe(client, queries, label):
    scores = []
    for q in queries:
        best, err = _best(client, q)
        if best is None:
            print("  !! %s probe failed: %s" % (label, err))
            return None
        scores.append((q, best))
    return scores


def _stats(scores):
    vals = [s for _q, s in scores]
    return {"n": len(vals), "max": max(vals), "mean": sum(vals) / len(vals),
            "min": min(vals)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--noise", type=int, default=len(NOISE))
    ap.add_argument("--real", type=int, default=len(REAL))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    noise = list(NOISE)
    extra = max(0, args.noise - len(noise))
    noise += ["zzq" + secrets.token_hex(6) for _ in range(extra)]
    noise = noise[:args.noise]
    real = (REAL * 2)[:args.real]

    client = gate.Mcp("http://127.0.0.1:%d/mcp" % gate.DAEMON_PORT)
    ok, info = client.initialize()
    if not ok:
        print("daemon at :%d did not initialize: %s" % (gate.DAEMON_PORT, info))
        return 2

    nscores = _probe(client, noise, "noise")
    rscores = _probe(client, real, "real")
    if nscores is None or rscores is None:
        return 2

    n, r = _stats(nscores), _stats(rscores)
    gap = r["min"] - n["max"]
    query_ok = n["max"] < QUERY_FLOOR <= r["min"]
    row_ok = n["max"] < ROW_FLOOR <= r["min"]

    if args.json:
        print(json.dumps({"noise": n, "real": r, "gap": gap,
                          "query_floor": QUERY_FLOOR, "row_floor": ROW_FLOOR,
                          "query_floor_inside_gap": query_ok,
                          "row_floor_inside_gap": row_ok,
                          "noise_scores": sorted(nscores, key=lambda x: -x[1]),
                          "real_scores": sorted(rscores, key=lambda x: x[1])},
                         indent=2, ensure_ascii=False))
    else:
        print("noise  n=%d  max %.3f  mean %.3f  min %.3f"
              % (n["n"], n["max"], n["mean"], n["min"]))
        print("real   n=%d  max %.3f  mean %.3f  min %.3f"
              % (r["n"], r["max"], r["mean"], r["min"]))
        print("gap (real min - noise max): %+.3f" % gap)
        print()
        print("highest-scoring noise probes:")
        for q, s in sorted(nscores, key=lambda x: -x[1])[:3]:
            print("  %.3f  %s" % (s, q[:64]))
        print("lowest-scoring real probes:")
        for q, s in sorted(rscores, key=lambda x: x[1])[:3]:
            print("  %.3f  %s" % (s, q[:64]))
        print()
        print("query floor %.2f inside the gap: %s"
              % (QUERY_FLOOR, "YES" if query_ok else "NO"))
        print("row   floor %.2f inside the gap: %s"
              % (ROW_FLOOR, "YES" if row_ok else "NO"))
    return 0 if (query_ok and row_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
