#!/usr/bin/env python3
"""live_monitor.py — persistent live dashboard for the Azazael learning loop.

Reads the hot Windows DB (C:\\Users\\clint\\.azazael\\memory_store.db) and
refreshes a dashboard every REFRESH seconds, forever. Built to run inside a
console window that stays open (see open_live_monitor.bat).

Shows, live:
  - cycle freshness: minutes since last evolution_result / strategy_steered /
    dream_generated / training_complete
  - evolution: latest best fitness, trajectory (non-flat?), eps/lr/discount
  - steering: active strategy + steering counts (24h)
  - activity: dreams & training in the last hour, avg dream quality

Stdlib only — runs on Windows Python 3.14 without any deps.

Usage:
  python scripts/live_monitor.py [--refresh 30]
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone

DB = os.environ.get("AZAZAEL_MEMORY_DIR", r"C:\Users\clint\.azazael")
if not DB.endswith(".db"):
    DB = os.path.join(DB, "memory_store.db")

REFRESH = 30


def db_connect():
    """Open the DB read-only, falling back to a local copy on lock errors."""
    for _ in range(3):
        try:
            con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
            con.execute("SELECT 1 FROM memories LIMIT 1").fetchone()
            return con
        except Exception:
            time.sleep(1)
    tmp = os.path.join(tempfile.gettempdir(), "ms_livemon.db")
    for _ in range(3):
        try:
            shutil.copy2(DB, tmp)
            con = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
            con.execute("SELECT 1 FROM memories LIMIT 1").fetchone()
            return con
        except Exception:
            time.sleep(2)
    return None


def parse_data(d):
    try:
        return json.loads(d) if isinstance(d, str) else d
    except Exception:
        return {}


def age_min(ts):
    try:
        t = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return round((datetime.now(timezone.utc) - t).total_seconds() / 60.0, 1)
    except Exception:
        return None


def latest(con, event_type, n=1):
    rows = con.execute(
        "SELECT timestamp, data FROM memories WHERE event_type=? ORDER BY id DESC LIMIT ?",
        (event_type, n)).fetchall()
    out = []
    for ts, data in rows:
        out.append((ts, parse_data(data)))
    return out


def count_since(con, event_type, minutes):
    return con.execute(
        "SELECT COUNT(*) FROM memories WHERE event_type=? AND timestamp >= ?",
        (event_type, datetime.now(timezone.utc).isoformat(timespec="seconds"))).fetchone()[0]


def count_window(con, event_type, minutes):
    cutoff = (datetime.now(timezone.utc) - __import__("datetime").timedelta(minutes=minutes))
    return con.execute(
        "SELECT COUNT(*) FROM memories WHERE event_type=? AND timestamp >= ?",
        (event_type, cutoff.isoformat(timespec="seconds"))).fetchone()[0]


def avg_quality(con, minutes):
    cutoff = (datetime.now(timezone.utc) - __import__("datetime").timedelta(minutes=minutes))
    row = con.execute(
        "SELECT AVG(CAST(json_extract(data, '$.quality') AS REAL)) FROM memories "
        "WHERE event_type='dream_generated' AND timestamp >= ?", (cutoff.isoformat(timespec="seconds"),)).fetchone()
    return row[0] if row and row[0] is not None else 0.0


def render(con, now):
    lines = []
    L = lines.append
    L("=" * 78)
    L(f"  AZAZAEL LIVE MONITOR   {now.strftime('%Y-%m-%d %H:%M:%S')}   (refresh {REFRESH}s, Ctrl+C to stop)")
    L("=" * 78)
    L("  cycles: evolution / metacog / dreaming / training   |   DB: " + DB)

    # --- cycle freshness ---
    L("\n[1] CYCLE FRESHNESS  (minutes since last event; <5 = on cadence)")
    for et, label in [("evolution_result", "evolution"), ("strategy_steered", "metacog/steer"),
                      ("dream_generated", "dreaming"), ("training_complete", "training")]:
        rows = latest(con, et, 1)
        if not rows:
            L(f"    {label:<18} no events found")
            continue
        ts, _ = rows[0]
        a = age_min(ts)
        ok = "OK" if (a is not None and a < 15) else "STALE"
        L(f"    {label:<18} last {ts[11:19]}Z  age {a:>6} min   [{ok}]")

    # --- evolution ---
    L("\n[2] EVOLUTION  (latest run)")
    rows = latest(con, "evolution_result", 1)
    if rows:
        ts, d = rows[0]
        traj = [float(x) for x in (d.get("trajectory") or [])]
        genes = d.get("best_genes") or {}
        flat = len(set(round(x, 3) for x in traj)) <= 1 if traj else None
        L(f"    at {ts[11:19]}Z  gens={d.get('generations')}  seed={d.get('seed')}")
        L(f"    trajectory  {' -> '.join(f'{x:.2f}' for x in traj)}")
        L(f"    best fitness {max(traj):.3f}   non-flat={not flat}   seeded_from_prior={d.get('seeded_from_prior')}")
        L(f"    lr={genes.get('learning_rate', 0):.4f}  eps={genes.get('epsilon', 0):.4f}  "
          f"discount={genes.get('discount', 0):.4f}")
    else:
        L("    no evolution_result rows yet")

    # --- steering ---
    L("\n[3] STEERING")
    rows = latest(con, "strategy_steered", 1)
    if rows:
        ts, d = rows[0]
        L(f"    active strategy: {d.get('strategy', '?')}   (at {ts[11:19]}Z)")
    n_steer = count_window(con, "strategy_steered", 1440)
    L(f"    steering events (24h): {n_steer}")

    # --- activity ---
    L("\n[4] ACTIVITY (last 60 min)")
    L(f"    dreams:      {count_window(con, 'dream_generated', 60)}   avg quality {avg_quality(con, 60):.3f}")
    L(f"    training:    {count_window(con, 'training_complete', 60)}")
    L(f"    adaptations: {count_window(con, 'strategy_adaptation', 60)}")
    L(f"    policy apps: {count_window(con, 'policy_applied', 60)}")

    L("\n" + "-" * 78)
    L("  Tip: press Ctrl+C to exit (the window itself stays open).")
    return "\n".join(lines)


def main():
    global REFRESH
    ap = argparse.ArgumentParser(description="Persistent Azazael live dashboard")
    ap.add_argument("--refresh", type=int, default=30)
    args = ap.parse_args()
    REFRESH = max(5, args.refresh)

    con = db_connect()
    if con is None:
        print(f"FATAL: cannot open {DB}", file=sys.stderr)
        return 2

    while True:
        now = datetime.now()
        try:
            text = render(con, now)
        except Exception as e:
            text = f"render error: {e}"
            con = db_connect()  # reconnect on next loop
        os.system("cls" if os.name == "nt" else "clear")
        print(text)
        time.sleep(REFRESH)


if __name__ == "__main__":
    sys.exit(main())