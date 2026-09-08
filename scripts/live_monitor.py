#!/usr/bin/env python3
"""live_monitor.py — persistent live dashboard for the Azazael learning loop.

Reads the hot Windows DB (~/.azazael/memory_store.db, see DB default) and
refreshes a dashboard every REFRESH seconds, forever. Built to run inside a
console window that stays open (see open_live_monitor.bat).

Shows, live, with plain-English interpretation:
  - cycle freshness: minutes since last evolution_result / strategy_steered /
    dream_generated / training_complete (red + FLASH when stale >15 min)
  - evolution: latest run + last 5 trajectories + a climb sparkline of per-run
    best fitness; beeps when a new all-time high appears
  - steering: active strategy + what that strategy means
  - activity: dreams & training in the last hour, avg dream quality
  - bottom line: one-sentence verdict on how training is going

Every refresh is also appended to a rolling log file (logs/live_monitor.log,
rotated at 1 MB) so you can review the day's history later.

Stdlib only — runs on Windows Python 3.14 without any deps.

Usage:
  python scripts/live_monitor.py [--refresh 30] [--log logs/live_monitor.log]
"""
import argparse
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone, timedelta

DB = os.environ.get("AZAZAEL_MEMORY_DIR", r"C:\Users\clint\.azazael")
if not DB.endswith(".db"):
    DB = os.path.join(DB, "memory_store.db")

REFRESH = 30
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "live_monitor.log")
LOG_MAX = 1_000_000  # rotate above ~1 MB
_BEST_SEEN = None    # highest best fitness ever observed this session

# ANSI colors (Windows 10+ consoles support these)
C_RED = "\x1b[91m"
C_GRN = "\x1b[92m"
C_YEL = "\x1b[93m"
C_CYN = "\x1b[96m"
C_BLD = "\x1b[1m"
C_RST = "\x1b[0m"

# sparkline glyphs: 0..8 levels, pure ASCII so cmd codepage never mangles
_SPARK = " .:-=+*#%"

# what each steering strategy actually does (plain English)
STRATEGY_MEANING = {
    "aggressive": "high creativity + more episodes; evidence favors it (best policy-apply rate)",
    "conservative": "low creativity (0.15); tepid dreams mostly fail the 0.5 adoption bar (churn fix)",
    "batched": "dreams are queued and integrated in batches for steadier learning",
    "staged": "changes roll out in stages instead of all at once",
    "adaptive": "parameters adjust to recent outcome evidence",
    "aggressive+": "aggressive with extra exploration headroom",
    "steady": "holding current settings while evidence accumulates",
}


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


def count_window(con, event_type, minutes):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return con.execute(
        "SELECT COUNT(*) FROM memories WHERE event_type=? AND timestamp >= ?",
        (event_type, cutoff.isoformat(timespec="seconds"))).fetchone()[0]


def avg_quality(con, minutes):
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    row = con.execute(
        "SELECT AVG(CAST(json_extract(data, '$.quality') AS REAL)) FROM memories "
        "WHERE event_type='dream_generated' AND timestamp >= ?",
        (cutoff.isoformat(timespec="seconds"),)).fetchone()
    return row[0] if row and row[0] is not None else 0.0


def sparkline(vals, width=52):
    """ASCII sparkline of per-run best fitness (oldest -> newest).

    Outlier-robust: scale uses the 10th..90th percentile range and clamps
    so a single legacy off-scale run (e.g. 50.0 pre-reward-fix) does not
    flatten the whole strip.
    """
    if not vals:
        return "(no runs yet)"
    s = sorted(vals)
    n = len(s)
    lo = s[max(0, int(n * 0.1) - 1)]
    hi = s[min(n - 1, int(n * 0.9))]
    rng = (hi - lo) or 1.0
    cells = []
    step = max(1, int(n / width) + (1 if n % width else 0))
    for i in range(0, n, step):
        chunk = vals[i:i + step]
        v = max(chunk)
        level = int((v - lo) / rng * (len(_SPARK) - 1))
        cells.append(_SPARK[min(max(level, 0), len(_SPARK) - 1)])
    return "".join(cells)


def evo_history(con, n=20):
    """Recent evolution_result rows, newest first, as dicts (JSON-safe)."""
    out = []
    for ts, d in latest(con, "evolution_result", n):
        traj = [float(x) for x in (d.get("trajectory") or [])]
        out.append({
            "ts": ts,
            "traj": traj,
            "best": max(traj) if traj else 0.0,
            "flat": len(set(round(x, 3) for x in traj)) <= 1 if traj else None,
            "genes": d.get("best_genes") or {},
            # v2-dual (2026-09-08): combined best splits into info/alert
            # parts; older rows lack these keys (v1 scale, info-only).
            "info": d.get("best_info"),
            "alert": d.get("best_alert"),
            "fit": d.get("fitness", "v1"),
        })
    return out


def collect(con):
    """Gather all dashboard data into a dict (also used by the web server)."""
    data = {}

    data["freshness"] = []
    for et, label in [("evolution_result", "evolution"), ("strategy_steered", "metacog/steer"),
                      ("dream_generated", "dreaming"), ("training_complete", "training")]:
        rows = latest(con, et, 1)
        if not rows:
            data["freshness"].append({"label": label, "ts": None, "age": None, "ok": False})
            continue
        ts, _ = rows[0]
        a = age_min(ts)
        data["freshness"].append({"label": label, "ts": ts, "age": a, "ok": a is not None and a < 15})

    data["evo"] = evo_history(con, 20)

    rows = latest(con, "strategy_steered", 1)
    if rows:
        ts, d = rows[0]
        data["strategy"] = {"value": d.get("strategy", "?"), "ts": ts}
    else:
        data["strategy"] = {"value": "?", "ts": None}
    data["steer_24h"] = count_window(con, "strategy_steered", 1440)

    data["activity"] = {
        "dreams": count_window(con, "dream_generated", 60),
        "quality": round(avg_quality(con, 60), 3),
        "training": count_window(con, "training_complete", 60),
        "adaptations": count_window(con, "strategy_adaptation", 60),
        "policy_applied": count_window(con, "policy_applied", 60),
    }
    return data


# ---------------------------------------------------------------------------
# Interpretation layer — turn the numbers into plain English
# ---------------------------------------------------------------------------

def explain(data):
    """Return list of (verdict, detail) explanation lines about the data."""
    out = []

    # --- freshness verdict ---
    stale = [f for f in data["freshness"] if not f["ok"]]
    if not stale:
        out.append(("OK", "All 4 loops are firing on their 5-min cadence — training is live."))
    else:
        names = ", ".join(f["label"] for f in stale)
        out.append(("WARN", f"{names} stale (>15 min) — check Windows Task Scheduler; "
                            f"the loops can silently stop when trigger windows expire."))

    # --- evolution verdict ---
    # Trend is only meaningful within one fitness scale (v1 vs v2-dual).
    evo = data["evo"]
    if len(evo) >= 3 and len({e["fit"] for e in evo[:4]}) == 1:
        recent = evo[0]["best"]
        prev3 = [e["best"] for e in evo[1:4]]
        mid = sum(prev3) / len(prev3)
        if recent > mid * 1.03:
            trend = f"climbing (recent {recent:.2f} vs avg {mid:.2f} of prior 3)"
        elif recent < mid * 0.97:
            trend = f"dip (recent {recent:.2f} vs avg {mid:.2f} of prior 3 — normal noise, re-seeds each run)"
        else:
            trend = f"steady around {mid:.2f}"
        out.append(("EVO", f"best fitness {trend}."))

    if evo and evo[0]["flat"] is False:
        out.append(("EVO", "trajectory is non-flat — reward is action-dependent, so evolution has a "
                           "real gradient to climb (the reward fix is working)."))
    if evo:
        eps = evo[0]["genes"].get("epsilon", -1)
        if eps is not None and eps < 0.02:
            out.append(("EVO", f"epsilon={eps:.3f} — near-pure exploitation: the policy has converged to "
                               "deterministic actions; random exploration now mostly hurts reward."))
        elif eps is not None and eps < 0.12:
            out.append(("EVO", f"epsilon={eps:.3f} — mostly exploiting, light exploration remaining."))
        elif eps is not None:
            out.append(("EVO", f"epsilon={eps:.3f} — still exploring widely; search is sampling new genes."))

    # --- steering verdict ---
    s = data["strategy"]
    if s["value"] != "?":
        meaning = STRATEGY_MEANING.get(s["value"].lower(),
                                       "no canned description — check metacog output")
        out.append(("STEER", f"strategy '{s['value']}' -> {meaning}."))

    # --- activity verdict ---
    a = data["activity"]
    if a["quality"] >= 0.6:
        out.append(("ACT", f"dream quality {a['quality']:.2f} — healthy; dreams are being adopted."))
    elif a["quality"] >= 0.45:
        out.append(("ACT", f"dream quality {a['quality']:.2f} — mediocre; many dreams may miss the 0.5 bar."))
    else:
        out.append(("ACT", f"dream quality {a['quality']:.2f} — weak; check creativity factors."))

    return out


def bottom_line(data):
    """One-sentence overall verdict."""
    evo = data["evo"]
    s = data["strategy"]
    a = data["activity"]
    stale = [f for f in data["freshness"] if not f["ok"]]
    parts = []
    if stale:
        parts.append(f"{len(stale)} loop(s) stale")
    if evo:
        parts.append(f"evolution best {evo[0]['best']:.2f}"
                     f"{' (climbing)' if len(evo) >= 2 and evo[0]['best'] > sum(e['best'] for e in evo[1:4]) / max(1, len(evo[1:4])) else ''}")
    if s["value"] != "?":
        parts.append(f"strategy {s['value']}")
    if a["dreams"]:
        parts.append(f"{a['dreams']} dreams/hr @ {a['quality']:.2f} quality")
    if not parts:
        return "No data yet — waiting for the first cycle to fire."
    return "Training is live: " + "; ".join(parts) + "."


def render(data, now):
    """Console text for one refresh."""
    lines = []
    L = lines.append
    L("=" * 78)
    L(f"  AZAZAEL LIVE MONITOR   {now.strftime('%Y-%m-%d %H:%M:%S')}   (refresh {REFRESH}s, Ctrl+C to stop)")
    L("=" * 78)

    # --- cycle freshness ---
    L("\n[1] CYCLE FRESHNESS  (minutes since last event; <5 = on cadence)")
    for f in data["freshness"]:
        if f["ts"] is None:
            L(f"    {f['label']:<18} no events found")
            continue
        a = f["age"]
        if f["ok"]:
            L(f"    {C_GRN}{f['label']:<18} last {f['ts'][11:19]}Z  age {a:>6} min   [OK]{C_RST}")
        else:
            L(f"{C_RED}    {f['label']:<18} last {f['ts'][11:19]}Z  age {a:>6} min   [STALE!]{C_RST}")

    # --- evolution ---
    L("\n[2] EVOLUTION")
    evo = data["evo"]
    if evo:
        e = evo[0]
        L(f"    latest at {e['ts'][11:19]}Z  best {C_GRN}{e['best']:.3f}{C_RST}  "
          f"non-flat={not e['flat']}  lr={e['genes'].get('learning_rate', 0):.4f}  "
          f"eps={e['genes'].get('epsilon', 0):.4f}  disc={e['genes'].get('discount', 0):.4f}"
          f"  [{e['fit']}]")
        if e["info"] is not None or e["alert"] is not None:
            L(f"    parts: info={e['info'] if e['info'] is not None else '?'}  "
              f"alert={e['alert'] if e['alert'] is not None else '?'}")

        L("    last 5 runs (best / gens / eps):")
        for e2 in evo[:5]:
            L(f"      {e2['ts'][11:16]}Z  {C_GRN}{e2['best']:6.2f}{C_RST}  gens={len(e2['traj']):2d}  "
              f"eps={e2['genes'].get('epsilon', 0):.3f}  flat={e2['flat']}  [{e2['fit']}]")

        fits = {e2["fit"] for e2 in evo[:5]}
        if len(fits) > 1:
            L(f"      {C_YEL}(note: mixed fitness scales {sorted(fits)} — "
              f"v2-dual bests run ~1pt higher by construction, not a spike){C_RST}")

        bests = [e2["best"] for e2 in evo][::-1]  # oldest -> newest
        L(f"    climb (per-run best, {len(bests)} runs, newest right):")
        L(f"      {C_CYN}{sparkline(bests)}{C_RST}")
        if len(bests) >= 2:
            L(f"      min {min(bests):.2f}   max {max(bests):.2f}   "
              f"recent: {bests[-3] if len(bests) >= 3 else bests[0]:.2f} -> {bests[-1]:.2f}")
        if max(bests) > 25:
            L(f"      (note: {max(bests):.2f} is a legacy pre-reward-fix run; excluded from scale)")
    else:
        L("    no evolution_result rows yet")

    # --- steering ---
    L("\n[3] STEERING")
    s = data["strategy"]
    L(f"    active strategy: {C_YEL}{s['value']}{C_RST}" + (f"   (at {s['ts'][11:19]}Z)" if s["ts"] else ""))
    L(f"    steering events (24h): {data['steer_24h']}")

    # --- activity ---
    a = data["activity"]
    L("\n[4] ACTIVITY (last 60 min)")
    L(f"    dreams:      {a['dreams']}   avg quality {a['quality']:.3f}")
    L(f"    training:    {a['training']}")
    L(f"    adaptations: {a['adaptations']}")
    L(f"    policy apps: {a['policy_applied']}")

    # --- what it means ---
    L("\n[5] WHAT IT MEANS")
    for tag, msg in explain(data):
        col = {"OK": C_GRN, "WARN": C_RED, "EVO": C_CYN, "STEER": C_YEL, "ACT": C_CYN}.get(tag, "")
        L(f"    {col}{tag:<6}{C_RST} {msg}")
    L(f"    {C_BLD}BOTTOM LINE:{C_RST} {bottom_line(data)}")

    L("\n" + "-" * 78)
    L("  Log: " + os.path.abspath(LOG_PATH))
    L("  Web: http://<this-pc>:8765  (live_monitor_web.py)")
    L("  Tip: press Ctrl+C to exit (the window itself stays open).")
    return "\n".join(lines)


def append_log(data, now):
    """Append one refresh to the rolling log file (rotate at 1 MB)."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        if os.path.exists(LOG_PATH) and os.path.getsize(LOG_PATH) > LOG_MAX:
            bak = LOG_PATH + ".1"
            if os.path.exists(bak):
                os.remove(bak)
            os.rename(LOG_PATH, bak)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"=== {now.isoformat()} ===\n")
            for fr in data["freshness"]:
                a = fr["age"] if fr["age"] is not None else -1
                f.write(f"  {fr['label']:<18} age {a:>6} min  {'OK' if fr['ok'] else 'STALE'}\n")
            evo = data["evo"]
            if evo:
                e = evo[0]
                f.write(f"  evolution best {e['best']:.3f} eps {e['genes'].get('epsilon', 0):.4f} "
                        f"traj {[round(x, 2) for x in e['traj']]} [{e['fit']}]"
                        + (f" info={e['info']} alert={e['alert']}"
                           if e["info"] is not None or e["alert"] is not None else "")
                        + "\n")
            s = data["strategy"]
            f.write(f"  strategy {s['value']}  steer24h {data['steer_24h']}  "
                    f"activity {data['activity']}\n")
            f.write(f"  >> {bottom_line(data)}\n")
    except Exception as e:
        print(f"log write failed: {e}", file=sys.stderr)


def beep_if_high(data):
    """Beep when a new all-time-best fitness appears this session."""
    global _BEST_SEEN
    if not data["evo"]:
        return False
    best = data["evo"][0]["best"]
    if _BEST_SEEN is None or best > _BEST_SEEN:
        is_new = _BEST_SEEN is not None
        _BEST_SEEN = best
        if is_new:
            sys.stdout.write("\a")  # console bell
            sys.stdout.flush()
            return True
    return False


def main():
    global REFRESH, LOG_PATH
    ap = argparse.ArgumentParser(description="Persistent Azazael live dashboard")
    ap.add_argument("--refresh", type=int, default=30)
    ap.add_argument("--log", default=LOG_PATH)
    args = ap.parse_args()
    REFRESH = max(5, args.refresh)
    LOG_PATH = os.path.abspath(args.log)

    con = db_connect()
    if con is None:
        print(f"FATAL: cannot open {DB}", file=sys.stderr)
        return 2

    while True:
        now = datetime.now()
        try:
            data = collect(con)
            text = render(data, now)
            new_high = beep_if_high(data)
            if new_high:
                text = text.replace(
                    f"  AZAZAEL LIVE MONITOR   {now.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"  AZAZAEL LIVE MONITOR   {now.strftime('%Y-%m-%d %H:%M:%S')}"
                    f"{C_YEL}   *** NEW BEST {_BEST_SEEN:.3f} ***{C_RST}")
            append_log(data, now)
        except Exception as e:
            text = f"render error: {e}"
            con = db_connect()  # reconnect on next loop
        print("\033[2J\033[H", end="")
        print(text)
        time.sleep(REFRESH)


if __name__ == "__main__":
    sys.exit(main())