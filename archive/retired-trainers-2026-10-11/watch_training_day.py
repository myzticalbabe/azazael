#!/usr/bin/env python3
"""watch_training_day.py — long-horizon watcher for the 5-minute training loop.

Samples the live learning-loop health every N minutes for up to H samples and
appends one CSV row per sample to a log. Detached-friendly (setsid/nohup) so it
survives the launching shell. Exits 0.

Usage:
  python scripts/watch_training_day.py [--samples 24] [--interval 15]
                                       [--log /tmp/training_day.csv]
  AZAZAEL_MEMORY_DIR=C:\\Users\\clint\\.azazael python scripts/watch_training_day.py

Each CSV row: utc, active_strategy, state_age_min, steering_24h, switches_24h,
dreams_1h, avg_quality_1h, policy_applied_1h, policy_applied_rate,
mc_evidence_n, mc_success_rate, evolution_flat, evolution_best_fitness
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import sysconfig
import time
from collections import defaultdict
from datetime import datetime, timezone


def _ensure_gil():
    """Free-threaded 3.14t builds have a flaky sqlite3; re-exec with GIL on."""
    if (sysconfig.get_config_var("Py_GIL_DISABLED")
            and os.environ.get("AZAZAEL_GIL_ENFORCED") != "1"):
        os.environ["AZAZAEL_GIL_ENFORCED"] = "1"
        os.execv(sys.executable, [sys.executable, "-X", "gil=1"] + sys.argv)


_ensure_gil()


def db_path():
    env = os.environ.get("AZAZAEL_MEMORY_DIR", "")
    return env if env.endswith(".db") else os.path.join(env, "memory_store.db")


def connect():
    import shutil
    import tempfile
    for attempt in range(3):
        try:
            con = sqlite3.connect(f"file:{db_path()}?mode=ro", uri=True)
            con.execute("SELECT 1 FROM memories LIMIT 1").fetchone()
            return con
        except Exception:
            try:
                con = sqlite3.connect(db_path())
                con.execute("SELECT 1 FROM memories LIMIT 1").fetchone()
                return con
            except Exception:
                time.sleep(1)
    if os.path.exists(db_path()):
        tmp = os.path.join(tempfile.gettempdir(), "ms_watch_copy.db")
        for _ in range(5):
            try:
                shutil.copy2(db_path(), tmp)
                con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
                con.execute("SELECT COUNT(*) FROM memories").fetchone()
                return con
            except Exception:
                time.sleep(2)
    return None


def sample(con):
    cur = con.cursor()

    def latest_event(etype):
        row = cur.execute(
            "SELECT timestamp, data FROM memories WHERE event_type=? ORDER BY id DESC LIMIT 1",
            (etype,)).fetchone()
        if not row:
            return None, None
        d = row[1]
        try:
            d = json.loads(d) if isinstance(d, str) else d
        except Exception:
            d = {}
        return row[0], d

    # active strategy (latest strategy_steered)
    ts, d = latest_event("strategy_steered")
    strategy = (d or {}).get("strategy", "none")

    # state freshness
    state_ts, _ = latest_event("state_saved")
    state_age = None
    if state_ts:
        try:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(state_ts)
            state_age = round(age.total_seconds() / 60.0, 1)
        except Exception:
            state_age = None

    def count_since(etype, minutes):
        return cur.execute(
            "SELECT COUNT(*) FROM memories WHERE event_type=? AND timestamp >= "
            "datetime('now', ?)", (etype, f"-{minutes} minutes")).fetchone()[0]

    dreams = count_since("dream_generated", 60)
    quality = cur.execute(
        "SELECT AVG(CAST(json_extract(data, '$.quality') AS REAL)) FROM memories "
        "WHERE event_type='dream_generated' AND timestamp >= datetime('now','-60 minutes')"
    ).fetchone()[0] or 0.0

    policy = count_since("policy_applied", 60)
    policy_applied = cur.execute(
        "SELECT COUNT(*) FROM memories WHERE event_type='policy_applied' AND "
        "json_extract(data, '$.applied') = 1 AND timestamp >= datetime('now','-60 minutes')"
    ).fetchone()[0]

    steering24 = count_since("strategy_steered", 1440)
    switches24 = cur.execute(
        "SELECT COUNT(*) FROM memories WHERE event_type='strategy_adaptation' AND "
        "json_extract(data, '$.should_adapt') = 1 AND timestamp >= datetime('now','-1440 minutes')"
    ).fetchone()[0]

    # metacog evidence (latest mc_cycle)
    _, mc = latest_event("mc_cycle")
    ev = (mc or {}).get("evidence") or {}
    ev_n = ev.get("n", 0)
    ev_ok = ev.get("success_rate", 0.0)

    # evolution trajectory
    _, evo = latest_event("evolution_result")
    traj = (evo or {}).get("trajectory") or []
    flat = len(set(round(t, 3) for t in traj)) <= 1 if traj else None
    best_fitness = max(traj) if traj else None

    return {
        "utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "active_strategy": strategy, "state_age_min": state_age,
        "steering_24h": steering24, "switches_24h": switches24,
        "dreams_1h": dreams, "avg_quality_1h": round(float(quality), 3),
        "policy_applied_1h": policy, "policy_applied_rate": round(policy / max(policy, 1), 2),
        "mc_evidence_n": ev_n, "mc_success_rate": ev_ok,
        "evolution_flat": flat, "evolution_best_fitness": best_fitness,
    }


def main():
    ap = argparse.ArgumentParser(description="Long-horizon training-day watcher")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--interval", type=int, default=15, help="minutes between samples")
    ap.add_argument("--log", default="training_day_watch.csv")
    args = ap.parse_args()

    con = connect()
    if con is None:
        print("cannot open", db_path(), file=sys.stderr)
        return 2

    new_file = not os.path.exists(args.log)
    f = open(args.log, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=[
        "utc", "active_strategy", "state_age_min", "steering_24h", "switches_24h",
        "dreams_1h", "avg_quality_1h", "policy_applied_1h", "policy_applied_rate",
        "mc_evidence_n", "mc_success_rate", "evolution_flat", "evolution_best_fitness"])
    if new_file:
        w.writeheader()

    for i in range(args.samples):
        try:
            row = sample(con)
            w.writerow(row)
            f.flush()
            print(f"[{i+1}/{args.samples}] {row['utc']} strategy={row['active_strategy']} "
                  f"quality={row['avg_quality_1h']} dreams={row['dreams_1h']} "
                  f"state_age={row['state_age_min']} evo_flat={row['evolution_flat']}",
                  flush=True)
        except Exception as e:
            print(f"sample {i} failed: {e}", file=sys.stderr, flush=True)
        if i + 1 < args.samples:
            time.sleep(args.interval * 60)

    f.close()
    con.close()
    print(f"done: {args.samples} samples -> {args.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())