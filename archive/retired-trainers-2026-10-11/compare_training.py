#!/usr/bin/env python3
"""compare_training.py — side-by-side view of SB3 training runs (PPO/DQN/A2C).

Pulls the latest sb3_training_orchestrated artifacts from LocalMemoryStore,
groups them by algorithm, and prints the most recent runs per algo with
reward, model version, data slice, and duration so you can compare the
three trainers. Also shows which algo the rotation will run next.

Runs recorded before the reward-tracking fix (2026-09-08) have no
eval_mean_reward and are flagged as pre-fix rather than shown as 0.

Usage:
    python scripts/compare_training.py            # last 3 runs per algo
    python scripts/compare_training.py --runs 5   # last 5 runs per algo
    python scripts/compare_training.py --json     # machine-readable output
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

ALGOS = ["PPO", "DQN", "A2C"]


def rotated_algo() -> str:
    """Next algo for the current 5-minute slot (mirrors run_training_orchestrator)."""
    return ALGOS[int(time.time()) // 300 % len(ALGOS)]


def fetch_runs(limit: int = 500):
    from CORE.local_memory import get_memory_store
    store = get_memory_store()
    rows = store.query_memories(event_type="sb3_training_orchestrated", limit=limit)
    runs = []
    for r in rows:
        d = r.get("data", {})
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        if not isinstance(d, dict):
            continue
        d["_timestamp"] = r.get("timestamp", "")
        runs.append(d)
    return runs


def _reward_str(run: dict) -> str:
    mean = run.get("eval_mean_reward")
    if mean is None:
        return "n/a (pre-fix)"
    std = run.get("eval_std_reward")
    if std is None:
        return f"{mean}"
    return f"{mean} ± {std}"


def print_table(runs_by_algo: dict, per_algo: int) -> None:
    print("=" * 78)
    print("  SB3 training comparison (latest %d runs per algo)" % per_algo)
    print("=" * 78)
    for algo in ALGOS:
        runs = runs_by_algo.get(algo, [])
        if not runs:
            print(f"\n{algo}: no runs recorded yet")
            continue
        print(f"\n{algo}  ({len(runs)} total in window)")
        print("  %-20s %-10s %-8s %-14s %-8s %-8s %-8s" % (
            "time (UTC)", "version", "reward", "timesteps", "records", "dur(s)", "run_id"))
        for run in runs[:per_algo]:
            ts = (run.get("_timestamp") or "")[:19]
            print("  %-20s %-10s %-8s %-14s %-8s %-8s %s" % (
                ts,
                run.get("model_version", "?"),
                _reward_str(run),
                run.get("total_timesteps", "?"),
                run.get("records_used", "?"),
                round((run.get("duration_ms") or 0) / 1000.0, 1),
                run.get("run_id", "?"),
            ))
        if runs:
            latest = runs[0]
            print("  latest reward: %s  (model %s)" % (
                _reward_str(latest), latest.get("model_version", "?")))
    print("\nRotation: next slot trains %s (PPO -> DQN -> A2C, 5-min slots)" % rotated_algo())
    print("=" * 78)


def print_json(runs_by_algo: dict, per_algo: int) -> None:
    out = {"algorithms": {}}
    for algo in ALGOS:
        out["algorithms"][algo] = [
            {
                "time_utc": r.get("_timestamp"),
                "run_id": r.get("run_id"),
                "model_version": r.get("model_version"),
                "eval_mean_reward": r.get("eval_mean_reward"),
                "eval_std_reward": r.get("eval_std_reward"),
                "total_timesteps": r.get("total_timesteps"),
                "records_used": r.get("records_used"),
                "duration_ms": r.get("duration_ms"),
            }
            for r in runs_by_algo.get(algo, [])[:per_algo]
        ]
    out["next_rotation"] = rotated_algo()
    print(json.dumps(out, indent=2, default=str))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3,
                        help="Runs to show per algo (default: 3)")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of the table")
    parser.add_argument("--limit", type=int, default=500,
                        help="Max artifacts to scan (default: 500)")
    args = parser.parse_args()

    runs = fetch_runs(limit=args.limit)
    runs_by_algo = defaultdict(list)
    for r in runs:
        runs_by_algo[r.get("algo", "?")].append(r)

    if args.json:
        print_json(runs_by_algo, args.runs)
    else:
        print_table(runs_by_algo, args.runs)
    return 0


if __name__ == "__main__":
    sys.exit(main())