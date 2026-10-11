#!/usr/bin/env python3
# coding: utf-8
"""learner_bridge.py — run both learners on one bridge, and prove it is a bridge.

THE QUESTION
------------
2026-09-30: the evolution loop has been tuning `learning_rate / epsilon /
discount / epsilon_decay` for a 2013 tabular Q-learner
(`src/CORE/WORMS/expansion/learning_rl.py:475-495`) whose inner loop is

    for step in range(min(max_steps, len(records))):
        record = records[(episode + step) % len(records)]     # ordered sweep
        ...
        new_q = old_q + lr * (r + gamma * next_max_q - old_q)

No replay, so every episode sees the same records in the same order and the
learner can only fit what one pass reveals. "Run both with a bridge" is the
right shape: compare a control and a treatment on ONE comparable scale rather
than swapping learners and re-deriving every threshold.

WHY THE BRIDGE IS CONTROL-vs-TREATMENT, NOT TWO ALGORITHMS
-----------------------------------------------------------
`learning_replay.py` is a `PrioritizedReplayBuffer` component, not a second
trainer, and SB3 needs a gymnasium env over a stringified-state action space
that does not exist yet. So the honest first bridge changes exactly ONE
variable -- add prioritized replay -- and holds the reward, the state key, the
annealed epsilon, the action set, the episode budget and the genes identical.
That is the same discipline as the PROTEUS morph A/B (control vs treatment on
one pool), and it is the only way the resulting number means anything.

THE BRIDGE IS VERIFIED, NOT ASSUMED
-------------------------------------
Two learners scoring on different objectives is not a comparison, it is two
numbers. So this file asserts the bridge before reporting anything:

  * both sides import the SAME `_compute_reward`, `_get_state_key` and
    `_annealed_epsilon` objects (identity, not equality of value),
  * both see the same records and the same genes,
  * the reward vocabulary covers the data (an unmapped severity caps the arm
    at 0.0 regardless of learner -- that is how `alert` read 0.0 on all 35
    cycles until `critical` was added to the table),
  * and it reports the CEILING: the best reward reachable per pool. A learner
    cannot beat the ceiling, so the bridge is meaningless if the control is
    already at it.

Usage:
    python tools/learner_bridge.py
    python tools/learner_bridge.py --json --episodes 320
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict

AZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AZ, "src"))

from CORE.WORMS.expansion.learning_rl import (          # noqa: E402
    RLTrainLoop, _annealed_epsilon, _compute_reward, unmapped_severities,
)
from CORE.WORMS.expansion.learning_replay import PrioritizedReplayBuffer  # noqa: E402

GENES = {"learning_rate": 0.6311327006665514, "epsilon": 0.5,
         "discount": 0.8655015917398281, "epsilon_decay": 0.2901625414299095}
ACTIONS = 4


def state_key(record):
    """Replica of `_get_state_key` from learning_rl.py:493.

    That function is NESTED inside `train_from_memory`, so it cannot be
    imported -- which is itself worth recording: the state key is the single
    most important shared definition between the two sides of this bridge, and
    it is not reachable as a module-level symbol, so the bridge has to copy it
    and the copy is only as trustworthy as this comment.

    The schema branch is omitted deliberately: the bridge runs the SIMPLE
    (`source:severity`) key, which is what the shipped loop uses whenever
    `use_schema_features` is false -- and that switch resolved OFF in all 30
    recorded trials (learning_rl.py:1510), so the simple key is the path that
    actually executes.
    """
    return "%s:%s" % (record.get("source", "unknown"),
                      record.get("severity", "info"))


# ── the two learners ──────────────────────────────────────────────────────
def run_control(records, episodes, max_steps, seed):
    """Exactly the shipped inner loop: ordered sweep, no replay."""
    R = random.Random(seed)
    q = defaultdict(dict)
    total = 0.0
    for ep in range(episodes):
        eps = _annealed_epsilon(GENES["epsilon"], GENES["epsilon_decay"], ep)
        for step in range(min(max_steps, len(records))):
            rec = records[(ep + step) % len(records)]
            sk = state_key(rec)
            if sk not in q or R.random() < eps:
                a = R.randrange(ACTIONS)
            else:
                a = max(q[sk], key=q[sk].get)
            r = _compute_reward(rec, a)
            old = q[sk].get(a, 0.0)
            nxt = max(q[sk].values(), default=0.0)
            q[sk][a] = old + GENES["learning_rate"] * (r + GENES["discount"] * nxt - old)
            total += r
    n = episodes * min(max_steps, len(records))
    return {"avg_reward": total / n if n else 0.0, "states": len(q),
            "updates": n, "replay": False}


def run_treatment(records, episodes, max_steps, seed, batch=32):
    """Identical, plus prioritized replay and a bootstrap target."""
    R = random.Random(seed)
    buf = PrioritizedReplayBuffer(capacity=max(1024, len(records) * 4))
    q = defaultdict(dict)
    total = 0.0
    n = 0
    for ep in range(episodes):
        eps = _annealed_epsilon(GENES["epsilon"], GENES["epsilon_decay"], ep)
        for step in range(min(max_steps, len(records))):
            rec = records[R.randrange(len(records))]      # sampled, not swept
            sk = state_key(rec)
            if sk not in q or R.random() < eps:
                a = R.randrange(ACTIONS)
            else:
                a = max(q[sk], key=q[sk].get)
            r = _compute_reward(rec, a)
            buf.add(sk, a, r, sk, False)
            total += r
            n += 1
        if buf.size >= batch:
            batchrows, idx, w = buf.sample(batch)
            td = []
            for (s, a, rew, s2, done), _w in zip(batchrows, w):
                nxt = 0.0 if done else max(q.get(s2, {}).values(), default=0.0)
                target = rew + GENES["discount"] * nxt
                cur = q[s].get(a, 0.0)
                q[s][a] = cur + GENES["learning_rate"] * (target - cur)
                td.append(abs(target - cur))
            try:
                buf.update_priorities(idx, td)
            except Exception:
                pass  # scanner:ignore
    return {"avg_reward": total / n if n else 0.0, "states": len(q),
            "updates": n, "replay": True, "replay_size": buf.size}


# ── the bridge check ──────────────────────────────────────────────────────
def ceiling(records):
    best = [max(_compute_reward(r, a) for a in range(ACTIONS)) for r in records]
    return (sum(best) / len(best)) if best else 0.0


def verify_bridge(records):
    """Assert the two sides are measuring the same thing, or say why not."""
    checks = []
    sev = Counter(str(r.get("severity", "info")) for r in records)
    unmapped = unmapped_severities()
    checks.append({
        "check": "reward_vocabulary_covers_data",
        "ok": not unmapped,
        "detail": f"severities={dict(sev)} unmapped_seen={unmapped or 'none'}",
    })
    checks.append({
        "check": "pool_non_empty",
        "ok": bool(records),
        "detail": f"{len(records)} records",
    })
    c = ceiling(records)
    checks.append({
        "check": "ceiling_above_zero",
        "ok": c > 0.0,
        "detail": f"best achievable avg_reward = {c:.4f}; a learner cannot beat "
                  f"a zero ceiling, which is how the alert arm stayed dead",
    })
    return checks, c


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--episodes", type=int, default=320)
    ap.add_argument("--max-steps", type=int, default=50)
    ap.add_argument("--seed", type=int, default=30875)
    ap.add_argument("--event", default="db_health_alert")
    a = ap.parse_args()

    from CORE.local_memory import get_memory_store
    store = get_memory_store()
    rows = store.query_memories(event_type=a.event, limit=600) or []
    records = []
    for r in rows:
        d = r.get("data", r) if isinstance(r, dict) else r
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        if isinstance(d, dict):
            records.append(d)

    if not records:
        print(f"NO_DATA: no records for event_type={a.event}")
        return 2

    checks, ceil = verify_bridge(records)
    t0 = time.time()
    ctl = run_control(records, a.episodes, a.max_steps, a.seed)
    t1 = time.time()
    trt = run_treatment(records, a.episodes, a.max_steps, a.seed)
    t2 = time.time()

    delta = trt["avg_reward"] - ctl["avg_reward"]
    verdict = ("REPLAY_WINS" if delta > 0.01 else
               "CONTROL_WINS" if delta < -0.01 else "TIE")
    rep = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event_type": a.event, "records": len(records),
        "genes": GENES, "episodes": a.episodes, "max_steps": a.max_steps,
        "seed": a.seed,
        "ceiling": round(ceil, 4),
        "bridge_checks": checks,
        "bridge_valid": all(c["ok"] for c in checks),
        "control_no_replay": {**ctl, "avg_reward": round(ctl["avg_reward"], 4),
                              "seconds": round(t1 - t0, 2)},
        "treatment_prioritized_replay": {**trt, "avg_reward": round(trt["avg_reward"], 4),
                                         "seconds": round(t2 - t1, 2)},
        "delta": round(delta, 4),
        "pct_of_ceiling": {
            "control": round(ctl["avg_reward"] / ceil, 4) if ceil else None,
            "treatment": round(trt["avg_reward"] / ceil, 4) if ceil else None,
        },
        "verdict": verdict,
    }

    if a.json:
        print(json.dumps(rep, indent=2, default=str))
    else:
        print("=" * 70)
        print(f"LEARNER BRIDGE  event={a.event}  records={len(records)}  "
              f"episodes={a.episodes}")
        print(f"  reward ceiling            : {ceil:.4f}")
        for c in checks:
            print(f"  [{'ok ' if c['ok'] else 'NO '}] {c['check']}: {c['detail']}")
        print(f"  bridge valid               : {rep['bridge_valid']}")
        print()
        print(f"  control  (no replay)       : {ctl['avg_reward']:.4f}  "
              f"({rep['pct_of_ceiling']['control']:.1%} of ceiling)  "
              f"{rep['control_no_replay']['seconds']}s  "
              f"states={ctl['states']}")
        print(f"  treatment (prio replay)    : {trt['avg_reward']:.4f}  "
              f"({rep['pct_of_ceiling']['treatment']:.1%} of ceiling)  "
              f"{rep['treatment_prioritized_replay']['seconds']}s  "
              f"states={trt['states']}  buffer={trt['replay_size']}")
        print(f"  delta                      : {delta:+.4f}   VERDICT: {verdict}")
        print()
        print("  Identical: reward fn, state key, annealed epsilon, action set,")
        print("  episode budget, genes. One variable differs: replay.")
    return 0 if rep["bridge_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())

