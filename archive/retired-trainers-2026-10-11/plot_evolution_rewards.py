#!/usr/bin/env python3
"""plot_evolution_rewards.py — quantify the fitness-landscape noise.

Groups generation_complete rows (emitted per generation by the evolution cycle)
into per-run bursts (gap > 90s = new run) and plots, per run:

  - the fitness spread (min .. max per-generation best) as a vertical bar
  - the best-fitness trajectory from evolution_result rows (dashed line)

Shows how noisy each evolution run's fitness landscape is — the reason
run-to-run best fitness oscillates even as the ceiling climbs.

Usage:
  AZAZAEL_MEMORY_DIR=C:\\Users\\clint\\.azazael python scripts/plot_evolution_rewards.py
  python3 scripts/plot_evolution_rewards.py --out graphs/reports/evolution_rewards.png
"""
import argparse
import json
import os
import sys
import sysconfig
import tempfile
import shutil
import time
from datetime import datetime, timedelta, timezone


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
    import sqlite3
    con = None
    for _ in range(3):
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
        tmp = os.path.join(tempfile.gettempdir(), "ms_plot_copy.db")
        for _ in range(5):
            try:
                shutil.copy2(db_path(), tmp)
                con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
                con.execute("SELECT COUNT(*) FROM memories").fetchone()
                return con
            except Exception:
                time.sleep(2)
    return None


def load():
    import sqlite3
    con = connect()
    if con is None:
        return [], []
    cur = con.cursor()
    rows = cur.execute(
        "SELECT timestamp, data FROM memories WHERE event_type='generation_complete' "
        "ORDER BY id").fetchall()
    runs = []
    cur_run = []
    last = None
    for ts, data in rows:
        d = data
        try:
            d = json.loads(d) if isinstance(d, str) else d
        except Exception:
            continue
        fit = d.get("best_fitness")
        if fit is None:
            continue
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if last is not None and (t - last).total_seconds() > 90:
            if cur_run:
                runs.append(cur_run)
            cur_run = []
        cur_run.append((t, float(fit)))
        last = t
    if cur_run:
        runs.append(cur_run)

    evo_rows = cur.execute(
        "SELECT timestamp, data FROM memories WHERE event_type='evolution_result' "
        "ORDER BY id").fetchall()
    evo = []
    for ts, data in evo_rows:
        d = data
        try:
            d = json.loads(d) if isinstance(d, str) else d
        except Exception:
            continue
        traj = d.get("trajectory") or []
        if traj:
            t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            evo.append((t, max(float(x) for x in traj)))
    con.close()
    return runs, evo


def plot(runs, evo, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(14, 6), dpi=110)
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")
    ax.tick_params(colors="#c9d1d9")
    for spine in ax.spines.values():
        spine.set_color("#30363d")

    big = [r for r in runs if len(r) >= 3]
    if not big:
        print("no training runs with >=3 genomes yet")
        return
    xs = list(range(len(big)))
    ax.set_title("Evolution reward spread per run (worst..best genome) + best trajectory",
                 color="#e6edf3", fontsize=13)
    ax.set_xlabel("evolution run (oldest -> newest)", color="#c9d1d9")
    ax.set_ylabel("avg_reward (fitness)", color="#c9d1d9")

    for x, r in zip(xs, big):
        vals = [v for _, v in r]
        lo, hi = min(vals), max(vals)
        med = sorted(vals)[len(vals) // 2]
        ax.vlines(x, lo, hi, color="#3fb950", linewidth=3, alpha=0.85)
        ax.plot(x, med, "o", color="#ffd700", markersize=4)
        ax.plot(x, hi, "o", color="#f47067", markersize=5)

    if evo:
        evo.sort()
        ex = [datetime.now(timezone.utc)]  # placeholder replaced below
        # map evolution best-fitness rows to same x-scale (by time order)
        big_t0 = big[0][0][0]
        ex = [(t - big_t0).total_seconds() for t, _ in evo if t >= big_t0]
        ey = [v for t, v in evo if t >= big_t0]
        if ex:
            ax.plot(ex, ey, "--", color="#58a6ff", linewidth=1.6, alpha=0.9,
                    label="evolution_result best (time-aligned)")
            ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")

    ax.grid(axis="y", color="#21262d", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(out, facecolor=fig.get_facecolor())
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser(description="Plot evolution reward spread")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "graphs", "reports",
        "evolution_rewards.png"))
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    runs, evo = load()
    print(f"{len(runs)} training runs, {len(evo)} evolution results")
    plot(runs, evo, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())