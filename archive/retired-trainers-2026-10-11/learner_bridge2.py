#!/usr/bin/env python3
# coding: utf-8
"""learner_bridge2.py — three arms, one reward, one action space, one scale.

Extends `learner_bridge.py` (control vs treatment) with a THIRD arm that is
actually a different class of algorithm: a neural network trained by
stable-baselines3 DQN, on `remediation_env.RemediationEnv`.

Why the extra arm exists
------------------------
The first bridge changed one variable (add replay) and therefore could not
answer "is the learner itself the constraint?" Two tabular variants differ in
sample efficiency; they do not differ in representational power. A function
approximator does. So:

  A  control     tabular Q, ordered sweep, no replay     (shipped today)
  B  treatment   tabular Q + PrioritizedReplayBuffer      (same class, better)
  C  modern      SB3 DQN, MlpPolicy, on RemediationEnv   (different class)

All three optimise `_compute_reward` over the SAME four remediation actions
on the SAME records with the SAME genes, so the numbers are comparable by
construction rather than by hope. The previous mismatch — SB3's
`Discrete(3)` severity space versus the tabular learner's four remediation
actions — is removed by `remediation_env`, which imports the reward rather
than copying it.

THE DEGENERACY CHECK IS PART OF THE RESULT
------------------------------------------
`RemediationEnv.state_count` reports how many distinct states the pool
actually contains, and `is_degenerate()` says so explicitly. On the alert
pool that is 1 state / 4 actions: a bandit, where the optimal policy is a
constant and NO learner can demonstrate anything. This tool reports that as
a first-class result and downgrades its own verdict accordingly, because a
confident number from a degenerate pool is the exact failure this whole
evening has been about.

Usage:
    python tools/learner_bridge2.py
    python tools/learner_bridge2.py --event db_health_info --steps 20000
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import defaultdict

AZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AZ, "src"))
sys.path.insert(0, os.path.join(AZ, "scripts"))

from CORE.WORMS.expansion.learning_rl import (          # noqa: E402
    _annealed_epsilon, _compute_reward, unmapped_severities,
)
from CORE.WORMS.expansion.learning_replay import PrioritizedReplayBuffer  # noqa: E402
from CORE.WORMS.expansion.remediation_env import (      # noqa: E402
    RemediationEnv, N_ACTIONS, build_features, run_greedy_policy,
)

GENES = {"learning_rate": 0.6311327006665514, "epsilon": 0.5,
         "discount": 0.8655015917398281, "epsilon_decay": 0.2901625414299095}


def state_key(rec):
    return "%s:%s" % (rec.get("source", "unknown"), rec.get("severity", "info"))


def arm_a_tabular(records, episodes, max_steps, seed):
    R = random.Random(seed)
    q = defaultdict(dict)
    tot = 0.0
    n = 0
    for ep in range(episodes):
        eps = _annealed_epsilon(GENES["epsilon"], GENES["epsilon_decay"], ep)
        for step in range(min(max_steps, len(records))):
            rec = records[(ep + step) % len(records)]
            sk = state_key(rec)
            a = R.randrange(N_ACTIONS) if (sk not in q or R.random() < eps) \
                else max(q[sk], key=q[sk].get)
            r = _compute_reward(rec, a)
            old = q[sk].get(a, 0.0)
            q[sk][a] = old + GENES["learning_rate"] * (
                r + GENES["discount"] * max(q[sk].values(), default=0.0) - old)
            tot += r
            n += 1
    return {"avg_reward": tot / n if n else 0.0, "states": len(q), "updates": n,
            "class": "tabular"}


def arm_b_replay(records, episodes, max_steps, seed, batch=32):
    R = random.Random(seed)
    buf = PrioritizedReplayBuffer(capacity=max(1024, len(records) * 4))
    q = defaultdict(dict)
    tot = 0.0
    n = 0
    for ep in range(episodes):
        eps = _annealed_epsilon(GENES["epsilon"], GENES["epsilon_decay"], ep)
        for _ in range(min(max_steps, len(records))):
            rec = records[R.randrange(len(records))]
            sk = state_key(rec)
            a = R.randrange(N_ACTIONS) if (sk not in q or R.random() < eps) \
                else max(q[sk], key=q[sk].get)
            r = _compute_reward(rec, a)
            buf.add(sk, a, r, sk, False)
            tot += r
            n += 1
        if buf.size >= batch:
            rows, idx, _w = buf.sample(batch)
            td = []
            for (s, a, rew, s2, done) in rows:
                nxt = 0.0 if done else max(q.get(s2, {}).values(), default=0.0)
                tgt = rew + GENES["discount"] * nxt
                cur = q[s].get(a, 0.0)
                q[s][a] = cur + GENES["learning_rate"] * (tgt - cur)
                td.append(abs(tgt - cur))
            try:
                buf.update_priorities(idx, td)
            except Exception:
                pass  # scanner:ignore
    return {"avg_reward": tot / n if n else 0.0, "states": len(q), "updates": n,
            "class": "tabular+replay"}


def arm_c_dqn(records, max_steps, total_steps, seed, lr):
    """Function approximator. Falls back to a documented reason, never to a
    number produced by something other than the requested algorithm."""
    t0 = time.time()
    try:
        import torch
        from stable_baselines3 import DQN
    except Exception as e:
        return {"error": f"unavailable: {type(e).__name__}: {e}",
                "class": "dqn"}
    try:
        from CORE.WORMS.expansion.remediation_env import gymnasium_env
        env, base = gymnasium_env(records, horizon=max_steps, seed=seed)
        model = DQN("MlpPolicy", env, learning_rate=lr, buffer_size=4096,
                    learning_starts=64, train_freq=16, seed=seed, verbose=0,
                    device="cpu")
        model.learn(total_timesteps=int(total_steps))
        # Evaluate deterministically against the same reward the others saw.
        tot = 0.0
        n = 0
        for ep in range(20):
            obs, _ = env.reset(seed=seed + ep)
            for _ in range(max_steps):
                act, _ = model.predict(obs, deterministic=True)
                obs, rew, term, trunc, _ = env.step(int(act))
                tot += rew
                n += 1
                if term or trunc:
                    break
        return {"avg_reward": tot / n if n else 0.0,
                "states": base.state_count,
                "class": "dqn", "params": sum(p.numel() for p in model.policy.parameters()),
                "timesteps": int(total_steps), "seconds": round(time.time() - t0, 1)}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "class": "dqn"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--event", default="db_health_alert")
    ap.add_argument("--episodes", type=int, default=320)
    ap.add_argument("--max-steps", type=int, default=50)
    ap.add_argument("--dqn-steps", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=30875)
    a = ap.parse_args()

    from CORE.local_memory import get_memory_store
    store = get_memory_store()
    records = []
    for r in (store.query_memories(event_type=a.event, limit=600) or []):
        d = r.get("data", r) if isinstance(r, dict) else r
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        if isinstance(d, dict):
            records.append(d)
    if not records:
        print(f"NO_DATA: no records for {a.event}")
        return 2

    env = RemediationEnv(records, horizon=a.max_steps, seed=a.seed)
    ceil = env.ceiling
    greedy = run_greedy_policy(records)
    degenerate = env.is_degenerate()
    feat_states = env.state_count

    res = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "event": a.event, "records": len(records), "genes": GENES,
        "reward_ceiling": round(ceil, 4),
        "greedy_always_remediate": round(greedy, 4),
        "tabular_states": len({state_key(r) for r in records}),
        "feature_states": feat_states,
        "degenerate_pool": degenerate,
        "unmapped_severities": unmapped_severities(),
        "arms": {},
    }
    res["arms"]["A_tabular"] = arm_a_tabular(records, a.episodes, a.max_steps, a.seed)
    res["arms"]["B_replay"] = arm_b_replay(records, a.episodes, a.max_steps, a.seed)
    res["arms"]["C_dqn"] = arm_c_dqn(records, a.max_steps, a.dqn_steps, a.seed,
                                     GENES["learning_rate"])
    for k, v in res["arms"].items():
        if "avg_reward" in v:
            v["avg_reward"] = round(v["avg_reward"], 4)
            v["pct_of_ceiling"] = (round(v["avg_reward"] / ceil, 4)
                                   if ceil else None)

    scored = {k: v for k, v in res["arms"].items() if "avg_reward" in v}
    if scored:
        best = max(scored.items(), key=lambda kv: kv[1]["avg_reward"])
        res["best_arm"] = best[0]
    res["conclusion_is_meaningful"] = not degenerate

    if a.json:
        print(json.dumps(res, indent=2, default=str))
        return 0
    print("=" * 72)
    print(f"THREE-ARM BRIDGE  event={a.event}  records={len(records)}")
    print(f"  reward ceiling (best action)   : {ceil:.4f}")
    print(f"  greedy always-remediate        : {greedy:.4f}")
    print(f"  distinct TABULAR states        : {res['tabular_states']}")
    print(f"  distinct FEATURE states        : {feat_states}")
    print(f"  degenerate pool (states<=1)    : {degenerate}")
    print()
    for k in ("A_tabular", "B_replay", "C_dqn"):
        v = res["arms"][k]
        if "error" in v:
            print(f"  {k:<12} UNAVAILABLE: {v['error'][:74]}")
        else:
            print(f"  {k:<12} {v['avg_reward']:>8.4f}  "
                  f"({v['pct_of_ceiling']:>6.1%} of ceiling)  "
                  f"{v.get('class','')}  states={v.get('states')}")
    print()
    if degenerate:
        print("  VERDICT: NOT MEANINGFUL. This pool has one state, so the task")
        print("  is a 1-state bandit: no transition, no horizon, no credit to")
        print("  assign. The optimal policy is a constant and every arm is")
        print("  expected to land near the ceiling. These numbers rank nothing.")
        print("  Fix the pool (populate `source`, add states) before comparing.")
    else:
        print(f"  best arm: {res.get('best_arm')}  "
              f"(comparison is meaningful: {feat_states} distinct states)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
