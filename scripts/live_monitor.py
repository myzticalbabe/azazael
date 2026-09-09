#!/usr/bin/env python3
"""live_monitor.py — persistent live dashboard for the Azazael learning loop.

Reads the hot Windows DB (~/.azazael/memory_store.db, see DB default) and
refreshes a dashboard every REFRESH seconds, forever. Built to run inside a
console window that stays open (see open_live_monitor.bat).

Shows, live, with plain-English interpretation (detail in the log file):
  - LOOPS: cycle freshness in one line (red when stale >15 min)
  - EVO: latest best + promotion standing; GENES + climb sparkline
  - META: meta-evolution champion search-params, margin EMA, live candidate
  - STEER: active strategy + dream/adapt activity, width-adaptive
  - TRAIN: fixed compact grid of all 15 tracks (reward + trend arrow)
  - Verdict: one line; STALE/HARDPOOL alerts only when firing

Fixed frame, truncate-never-wrap: the layout is bounded by construction
at any window size (small windows show the same sections narrower).
Detail (trajectories, fingerprints, explanations) lives in the rolling
log file, not on screen.

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
C_ORG = "\x1b[38;5;202m"   # red-orange GOSP title
C_RST = "\x1b[0m"

# rainbow wheel (256-color hue rotation) for the twinkling GOSP info line
_RAINBOW = [196, 202, 208, 214, 220, 190, 154, 118, 82, 46,
            49, 51, 45, 39, 33, 27, 93, 129, 165, 201]
_FRAME_NO = [0]   # increments per render -> colors drift = twinkle


def _rainbow(text, width, step=3):
    """Per-character rainbow gradient that shifts every frame (twinkle).

    Truncates to width FIRST (visible chars), then colorizes, so the
    frame math stays exact and lines never wrap.
    """
    import re
    plain = re.sub("\x1b\\[[0-9;]*m", "", text)[:max(0, width)]
    frame = _FRAME_NO[0]
    out = []
    for i, ch in enumerate(plain):
        out.append(f"\x1b[38;5;{_RAINBOW[(i + frame * step) % len(_RAINBOW)]}m{ch}")
    out.append(C_RST)
    return "".join(out)

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
        if t.tzinfo is None:
            # naive timestamps are local wall-clock (some writers omit the
            # offset); assuming UTC would silently shift ages by hours.
            t = t.replace(tzinfo=datetime.now().astimezone().tzinfo)
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
    """Count events in the last N minutes, robust to mixed timestamp formats.

    The store holds both offset (+00:00) and naive-local timestamps, so a
    SQL string comparison against one cutoff silently drops rows. Filter
    by parsed age in Python instead (rows come newest-first; small scan).
    """
    try:
        rows = con.execute(
            "SELECT timestamp FROM memories WHERE event_type=? ORDER BY id DESC LIMIT 500",
            (event_type,)).fetchall()
    except Exception:
        return 0
    n = 0
    for (ts,) in rows:
        a = age_min(ts)
        if a is None:
            continue
        if a <= minutes:
            n += 1
    return n


def age_of_latest(con, event_type):
    """Minutes since the newest event of this type, or None if never seen."""
    rows = con.execute(
        "SELECT timestamp FROM memories WHERE event_type=? ORDER BY id DESC LIMIT 1",
        (event_type,)).fetchone()
    return age_min(rows[0]) if rows else None


def avg_quality(con, minutes):
    try:
        rows = con.execute(
            "SELECT timestamp, data FROM memories WHERE event_type='dream_generated' "
            "ORDER BY id DESC LIMIT 200").fetchall()
    except Exception:
        return 0.0
    vals = []
    for ts, d in rows:
        a = age_min(ts)
        if a is None or a > minutes:
            continue
        try:
            vals.append(float((parse_data(d) or {}).get("quality", 0) or 0))
        except (ValueError, TypeError):
            continue
    return round(sum(vals) / len(vals), 3) if vals else 0.0


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
        # promotion standing + pool drift (2026-09-08): surfaced from the
        # artifact so the wallboard shows whether the GA beats production
        # and whether the eval pool is moving (fresh hard alerts).
        pool = d.get("pool_fingerprint") or {}
        if isinstance(pool, str):
            try:
                pool = json.loads(pool)
            except Exception:
                pool = {}
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
            "baseline": d.get("baseline"),
            "beats": bool(d.get("beats_baseline")),
            "promoted": bool(d.get("promoted")),
            "champ": d.get("champion_reeval"),
            "pool": pool,
        })
    return out


# Training rotation — must match run_training_orchestrator.py's ROTATION
# (order matters: next_rotation uses the same slot arithmetic).
TRAIN_ALGOS = ("PPO", "DQN", "A2C", "SAC", "TD3", "DDPG", "QRDQN",
               "TRPO", "TQC", "ARS", "MaskablePPO", "GRPO", "DPO", "OFFLINE", "RL",
               "DREAMTUNE", "WORMGA")
TRAIN_EVENT_TYPES = ("sb3_training_orchestrated",
                     "grpo_training_orchestrated",
                     "dpo_training_orchestrated",
                     "offline_training_orchestrated",
                     "training_run_complete",
                     "dreamtune_training_orchestrated",
                     "wormga_training_orchestrated")
# training_run_complete rows from before the RL track was wired (2026-09-09)
# used a degenerate reward scale (25.0/50.0) — excluded from the wallboard.
RL_LIVE_SINCE = "2026-09-09"


def sb3_training(con, n=3):
    """Latest training runs per algo + reward series (dashboard + web).

    Covers all rotation tracks (SB3 PPO/DQN/A2C/SAC/TD3/DDPG/QRDQN/TRPO/TQC/
    ARS/MaskablePPO, GRPO worm-selection, DPO preference learning, OFFLINE
    holdout, RL scheduled pipeline). Same shape
    for both viewers: {algo: latest runs,
    series: reward history per algo, counts, next_rotation}. Rewards are None
    for runs recorded before the reward-tracking fix (2026-09-08). GRPO/DPO
    rewards are on a different scale than SB3 episode totals — the renderer
    notes this.
    """
    ph = ",".join("?" for _ in TRAIN_EVENT_TYPES)
    rows = con.execute(
        "SELECT timestamp, event_type, source, data FROM memories WHERE event_type IN (%s) "
        "ORDER BY id DESC LIMIT 500" % ph,
        TRAIN_EVENT_TYPES).fetchall()
    by_algo = {}
    counts = {}
    for ts, et, src, data in rows:
        d = parse_data(data)
        algo = d.get("algo")
        if algo is None and et == "training_run_complete" and src == "ScheduledTrainingWorm":
            if ts < RL_LIVE_SINCE:
                continue
            algo = "RL"
            d = {"algo": "RL",
                 "run_id": d.get("run_id"),
                 "model_version": d.get("model_version"),
                 "eval_mean_reward": d.get("avg_reward"),
                 "eval_std_reward": None,
                 "records_used": d.get("records"),
                 "total_timesteps": None,
                 "dpo_loss": None}
        if not algo:
            continue
        counts[algo] = counts.get(algo, 0) + 1
        by_algo.setdefault(algo, []).append({
            "time_utc": ts,
            "run_id": d.get("run_id"),
            "model_version": d.get("model_version"),
            "eval_mean_reward": d.get("eval_mean_reward"),
            "eval_std_reward": d.get("eval_std_reward"),
            "records_used": d.get("records_used"),
            "total_timesteps": d.get("total_timesteps"),
            "dpo_loss": d.get("dpo_loss"),
        })
    out = {a: by_algo.get(a, [])[:n] for a in TRAIN_ALGOS}
    out["series"] = {
        a: [{"time_utc": r["time_utc"], "reward": r["eval_mean_reward"]}
            for r in by_algo.get(a, []) if r["eval_mean_reward"] is not None][:40]
        for a in TRAIN_ALGOS
    }
    out["counts"] = counts
    out["next_rotation"] = TRAIN_ALGOS[int(time.time()) // 300 % len(TRAIN_ALGOS)]
    return out


def collect(con):
    """Gather all dashboard data into a dict (also used by the web server)."""
    data = {}

    data["freshness"] = []
    # training freshness: watch the newest of EVERY training event type.
    # (2026-09-09 fix: the original 3-type list missed GRPO/DPO/OFFLINE/
    # DREAMTUNE/WORMGA rows, so training read stale for hours while those
    # tracks ran constantly.)
    train_evts = ("training_complete", "sb3_training_orchestrated",
                  "training_run_complete", "grpo_training_orchestrated",
                  "dpo_training_orchestrated", "offline_training_orchestrated",
                  "dreamtune_training_orchestrated",
                  "wormga_training_orchestrated")
    for et, label in [("evolution_result", "evolution"), ("strategy_steered", "metacog/steer"),
                      ("dream_generated", "dreaming"), ("training_complete", "training")]:
        rows = latest(con, et, 1)
        if et == "training_complete":
            newest_ts, newest_age = None, None
            for tet in train_evts:
                r = latest(con, tet, 1)
                if r:
                    a = age_min(r[0][0])
                    if newest_age is None or (a is not None and a < newest_age):
                        newest_age, newest_ts = a, r[0][0]
            data["freshness"].append({"label": label, "ts": newest_ts, "age": newest_age,
                                      "ok": newest_age is not None and newest_age < 15})
            continue
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
        # Rolling 60-min counts of an every-5-min event sit pinned at ~12 and
        # look frozen. Surface the age of the newest event instead so liveness
        # is visible; counts stay in the log.
        "adapt_age": age_of_latest(con, "strategy_adaptation"),
        "apply_age": age_of_latest(con, "policy_applied"),
    }

    # Last time the active strategy actually CHANGED (should_adapt rows), not
    # merely when an adaptation was evaluated. This is what answers "has it
    # adapted recently?"
    data["last_flip"] = None
    flip_rows = latest(con, "strategy_adaptation", 30)
    for ts, d in flip_rows:
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        if d.get("should_adapt"):
            data["last_flip"] = {
                "ts": ts, "age": age_min(ts),
                "to": d.get("recommended_strategy") or d.get("current_strategy"),
                "reason": (d.get("rationale") or "")[:60],
            }
            break

    data["training"] = sb3_training(con)

    # meta-evolution state (file-based, cheap; None until the first
    # meta-scoring cycle writes config/evolved_meta_params.json).
    data["meta"] = None
    try:
        meta_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "config", "evolved_meta_params.json")
        if os.path.exists(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                data["meta"] = json.load(f)
    except Exception:
        data["meta"] = None

    # GOSP learner evidence (written by the WSL gosp_* scripts on each
    # run; absent until the first run — all fields optional).
    data["gosp"] = {"learner": None, "parity": None, "rani": None}
    try:
        _home = os.path.expanduser("~")
        _lp = os.path.join(_home, "GOSP_LEARNER_TRAIN_evidence.json")
        if os.path.exists(_lp):
            with open(_lp, encoding="utf-8") as f:
                _ld = json.load(f)
            _wb, _wa = _ld.get("native_intel_weights_before") or {}, _ld.get("native_intel_weights_after") or {}
            _mover, _mdelta = "?", 0.0
            for _k, _v0 in _wb.items():
                try:
                    _dd = abs(float(_wa.get(_k, _v0)) - float(_v0))
                except (ValueError, TypeError):
                    continue
                if _dd > abs(_mdelta):
                    _mdelta, _mover = (_wa.get(_k, _v0) - _v0), _k
            _aft = _ld.get("learner_state_after") or {}
            data["gosp"]["learner"] = {
                "docs": _ld.get("docs_fed"), "date": (_ld.get("date") or "")[:16],
                "iter": _aft.get("iterations"), "conv": _aft.get("converged"),
                "acc": _aft.get("current_accuracy"),
                "mover": _mover, "mfrom": round(float(_wb.get(_mover, 0)), 3) if _mover in _wb else None,
                "mto": round(float(_wa.get(_mover, 0)), 3) if _mover in _wa else None,
            }
        _pp = os.path.join(_home, "GOSP_PARITY_evidence.json")
        if os.path.exists(_pp):
            with open(_pp, encoding="utf-8") as f:
                _pd = json.load(f)
            _agree, _total = 0, 0
            _ag = _pd.get("agreement") or {}
            if isinstance(_ag, dict):
                for _q, _r in _ag.items():
                    if not isinstance(_r, dict):
                        continue
                    _total += 1
                    if not _r.get("rust_only") and not _r.get("python_only"):
                        _agree += 1
            data["gosp"]["parity"] = {"agree": _agree, "total": _total,
                                      "date": (_pd.get("date") or "")[:16]}
        _rp = os.path.join(_home, "GOSP_RANI_INTEGRATION_evidence.json")
        if os.path.exists(_rp):
            with open(_rp, encoding="utf-8") as f:
                _rd = json.load(f)
            data["gosp"]["rani"] = {"mode": _rd.get("mode"),
                                    "date": (_rd.get("date") or "")[:16]}
        # RANI batteries (Eve Unleashed AdversarialEngine): newest of the
        # GOSP-integration and live-LLM evidence files. Backend identity
        # is the point — every round is stamped with what answered it.
        _best, _best_ts = None, ""
        for _rf in ("GOSP_RANI_INTEGRATION_evidence.json",
                    "RANI_LLM_evidence.json"):
            _fp = os.path.join(_home, _rf)
            try:
                if not os.path.exists(_fp):
                    continue
                with open(_fp, encoding="utf-8") as f:
                    _ed = json.load(f)
            except Exception:
                continue
            _dt = str(_ed.get("date") or "")
            if _dt >= _best_ts:
                _best_ts, _best = _dt, _ed
        if _best:
            _sm = _best.get("engine_summary") or {}
            _probes = _best.get("probes") or []
            _nr = sum(len(_p.get("rounds") or []) for _p in _probes) or len(_best.get("rounds") or [])
            _adv = _sm.get("adversarial_detected")
            if _adv is None:
                _adv = sum(1 for _p in _probes for _r in (_p.get("rounds") or [])
                           if _r.get("adversarial_flag"))
                _adv += sum(1 for _r in (_best.get("rounds") or []) if _r.get("adversarial_flag"))
            data["gosp"]["rani_batt"] = {
                "backend": _best.get("backend") or _best.get("model") or "?",
                "rounds": _nr or _sm.get("total_rounds"),
                "adv": _adv,
                "score": _sm.get("avg_score"),
                "lat": _sm.get("avg_latency_ms"),
                "date": _best_ts[:16],
            }
    except Exception:
        pass

    # recent training runs across all tracks (newest first, for TRAIN2)
    data["recent_runs"] = []
    try:
        _ph = ",".join("?" for _ in TRAIN_EVENT_TYPES)
        _seen = set()
        for _ts, _et, _src, _d in con.execute(
                "SELECT timestamp, event_type, source, data FROM memories "
                f"WHERE event_type IN ({_ph}) ORDER BY id DESC LIMIT 12",
                TRAIN_EVENT_TYPES).fetchall():
            _d = parse_data(_d)
            _rid = _d.get("run_id")
            if _rid is not None:
                if _rid in _seen:
                    continue
                _seen.add(_rid)
            _algo = _d.get("algo")
            if _algo is None and _et == "training_run_complete" and _src == "ScheduledTrainingWorm":
                _algo = "RL"
            if not _algo:
                continue
            _rw = _d.get("eval_mean_reward", _d.get("avg_reward"))
            data["recent_runs"].append({"algo": _algo, "reward": _rw,
                                        "age": age_min(_ts),
                                        "ver": _d.get("model_version")})
            if len(data["recent_runs"]) >= 4:
                break
    except Exception:
        pass

    # promotion file standing (evolved hyperparams actually in production)
    data["promo"] = None
    try:
        _pj = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "config", "evolved_rl_params.json")
        if os.path.exists(_pj):
            with open(_pj, encoding="utf-8") as f:
                _pd = json.load(f)
            _gg = _pd.get("genes") or {}
            _mt = os.path.getmtime(_pj)
            data["promo"] = {
                "lr": round(float(_gg.get("learning_rate", 0)), 4),
                "eps": round(float(_gg.get("epsilon", 0)), 4),
                "disc": round(float(_gg.get("discount", 0)), 4),
                "fit": _pd.get("fitness"),
                "wins": _pd.get("wins"),
                "age": round((time.time() - _mt) / 60.0, 1),
            }
    except Exception:
        pass

    # store size / rows / hourly growth (python-side age filter: the
    # store mixes offset and naive-local timestamps, so SQL string
    # comparison against one cutoff silently drops rows)
    data["store"] = None
    try:
        _dbrow = con.execute("SELECT COUNT(*) FROM memories").fetchone()
        _n = _dbrow[0] if _dbrow else 0
        _h = 0
        try:
            for (_ts,) in con.execute(
                    "SELECT timestamp FROM memories ORDER BY id DESC LIMIT 3000").fetchall():
                _a = age_min(_ts)
                if _a is None:
                    continue
                if _a <= 60:
                    _h += 1
        except Exception:
            pass
        try:
            _mb = round(os.path.getsize(DB) / 1e6, 1)
        except OSError:
            _mb = None
        data["store"] = {"mb": _mb, "rows": _n, "per_hr": _h}
    except Exception:
        pass

    # inference servers (best-effort, short timeout so refresh never hangs)
    data["servers"] = []
    try:
        import urllib.request as _url
        for _port in (18090, 18091, 18080):
            _ok, _ms = False, None
            try:
                _t0 = time.time()
                _r = _url.urlopen(f"http://127.0.0.1:{_port}/health", timeout=1)
                _ok = _r.status == 200
                _ms = int((time.time() - _t0) * 1000)
            except Exception:
                pass
            data["servers"].append({"port": _port, "ok": _ok, "ms": _ms})
    except Exception:
        pass

    # dream tuning file (what creativity the last dream cycle actually used)
    data["tuned"] = None
    try:
        _tp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "config", "tuned_creativity.json")
        if os.path.exists(_tp):
            with open(_tp, encoding="utf-8") as f:
                _td = json.load(f)
            _mt = os.path.getmtime(_tp)
            data["tuned"] = {
                "cf": _td.get("creativity_factor"),
                "sc": _td.get("scenario_count"),
                "age": round((time.time() - _mt) / 3600.0, 1),
            }
    except Exception:
        pass

    # last policy bridge verdict (what dreams actually did)
    data["policy"] = None
    try:
        _prows = con.execute(
            "SELECT timestamp, data FROM memories WHERE event_type='policy_applied' "
            "ORDER BY id DESC LIMIT 1").fetchall()
        if _prows:
            _pts, _pdd = _prows[0]
            _pdd = parse_data(_pdd)
            _det = _pdd.get("details") or {}
            _ap = _det.get("applied") or []
            _sk = _det.get("skipped") or []
            _last = _ap[-1] if _ap else {}
            data["policy"] = {
                "age": age_min(_pts),
                "napplied": len(_ap), "nskipped": len(_sk),
                "worm": _last.get("worm"), "rec": _last.get("recommended"),
                "conf": _last.get("confidence"),
                "adapted": _last.get("should_adapt"),
            }
    except Exception:
        pass

    # llm benchmark scoreboard (latest row per model)
    data["llm"] = []
    try:
        _seen_models = set()
        for _ts, _dd in con.execute(
                "SELECT timestamp, data FROM memories WHERE event_type='llm_benchmark' "
                "ORDER BY id DESC LIMIT 20").fetchall():
            _dd = parse_data(_dd)
            _m = _dd.get("model") or "?"
            if _m in _seen_models:
                continue
            _seen_models.add(_m)
            data["llm"].append({
                "model": _m, "age": age_min(_ts),
                "prompt": _dd.get("prompt_tps"), "gen": _dd.get("gen_tps"),
                "think": _dd.get("think_chars"),
            })
            if len(data["llm"]) >= 5:
                break
    except Exception:
        pass

    # alert rate last hour (crit split for the human)
    data["alerts"] = {"per_hr": 0, "crit": 0}
    try:
        for _ts, _sv in con.execute(
                "SELECT timestamp, severity FROM memories WHERE event_type='db_health_alert' "
                "ORDER BY id DESC LIMIT 500").fetchall():
            _a = age_min(_ts)
            if _a is None:
                continue
            if _a > 60:
                break
            data["alerts"]["per_hr"] += 1
            if _sv == "critical":
                data["alerts"]["crit"] += 1
    except Exception:
        pass

    # latest tuner outputs (best params each specialist found)
    data["tuners"] = {}
    try:
        for _et, _tk in (("dreamtune_training_orchestrated", "dreamtune"),
                         ("wormga_training_orchestrated", "wormga")):
            _rows = con.execute(
                "SELECT timestamp, data FROM memories WHERE event_type=? "
                "ORDER BY id DESC LIMIT 1", (_et,)).fetchall()
            if not _rows:
                continue
            _ts, _dd = _rows[0]
            _dd = parse_data(_dd)
            data["tuners"][_tk] = {
                "age": age_min(_ts),
                "fit": _dd.get("eval_mean_reward"),
                "ver": _dd.get("model_version"),
                "params": _dd.get("best_params") or {},
                "board": _dd.get("leaderboard") or {},
            }
    except Exception:
        pass

    # cycle process liveness from their own log files (complements event
    # freshness: proves the scheduler tasks themselves are firing).
    # dbmon is special: the daemon only logs at startup/errors, so its
    # liveness comes from its snapshot events, not its log file.
    data["cycles"] = []
    try:
        _logdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "logs")
        for _fn, _lb in (("evolution_cycle.log", "evo"),
                         ("training_orchestrator.log", "train"),
                         ("dream_cycle.log", "dream"),
                         ("metacog_cycle.log", "meta"),
                         ("db_monitor.log", "dbmon")):
            _fp = os.path.join(_logdir, _fn)
            try:
                _age = round((time.time() - os.path.getmtime(_fp)) / 60.0, 1)
            except OSError:
                _age = None
            data["cycles"].append({"label": _lb, "age": _age})
        try:
            _snap = con.execute(
                "SELECT timestamp FROM memories WHERE event_type='db_health_snapshot' "
                "ORDER BY id DESC LIMIT 1").fetchone()
            if _snap:
                for _c in data["cycles"]:
                    if _c.get("label") == "dbmon":
                        _c["age"] = age_min(_snap[0])
        except Exception:
            pass
    except Exception:
        pass
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
        out.append(("OK", "All 4 loops are firing on their 5-min cadence - training is live."))
    else:
        names = ", ".join(f["label"] for f in stale)
        out.append(("WARN", f"{names} stale (>15 min) - check Windows Task Scheduler; "
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
            trend = f"dip (recent {recent:.2f} vs avg {mid:.2f} of prior 3 - normal noise, re-seeds each run)"
        else:
            trend = f"steady around {mid:.2f}"
        out.append(("EVO", f"best fitness {trend}."))

    if evo and evo[0]["flat"] is False:
        out.append(("EVO", "trajectory is non-flat - reward is action-dependent, so evolution has a "
                           "real gradient to climb (the reward fix is working)."))
    if evo:
        eps = evo[0]["genes"].get("epsilon", -1)
        if eps is not None and eps < 0.02:
            out.append(("EVO", f"epsilon={eps:.3f} - near-pure exploitation: the policy has converged to "
                               "deterministic actions; random exploration now mostly hurts reward."))
        elif eps is not None and eps < 0.12:
            out.append(("EVO", f"epsilon={eps:.3f} - mostly exploiting, light exploration remaining."))
        elif eps is not None:
            out.append(("EVO", f"epsilon={eps:.3f} - still exploring widely; search is sampling new genes."))

    # --- steering verdict ---
    s = data["strategy"]
    if s["value"] != "?":
        meaning = STRATEGY_MEANING.get(s["value"].lower(),
                                       "no canned description - check metacog output")
        out.append(("STEER", f"strategy '{s['value']}' -> {meaning}."))

    # --- activity verdict ---
    a = data["activity"]
    if a["quality"] >= 0.6:
        out.append(("ACT", f"dream quality {a['quality']:.2f} - healthy; dreams are being adopted."))
    elif a["quality"] >= 0.45:
        out.append(("ACT", f"dream quality {a['quality']:.2f} - mediocre; many dreams may miss the 0.5 bar."))
    else:
        out.append(("ACT", f"dream quality {a['quality']:.2f} - weak; check creativity factors."))

    # --- training verdict ---
    tr = data.get("training", {})
    # RL excluded from the lead comparison (2026-09-09): its reward is a
    # Q-value average on a different scale than SB3 episode totals, but it
    # stays visible in the grid.
    scored = {a: r["eval_mean_reward"] for a in TRAIN_ALGOS if a != "RL"
              for r in (tr.get(a) or [])[:1] if r.get("eval_mean_reward") is not None}
    if len(scored) >= 2:
        best = max(scored, key=scored.get)
        others = [(a, v) for a, v in sorted(scored.items()) if a != best]
        out.append(("EVO", f"Training lead: {best} (reward {scored[best]:.1f}) vs "
                            + ", ".join(f"{a} {v:.1f}" for a, v in others)))

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
    tr = data.get("training", {})
    # RL excluded from the lead comparison (2026-09-09): its reward is a
    # Q-value average on a different scale than SB3 episode totals, but it
    # stays visible in the grid.
    scored = {a: r["eval_mean_reward"] for a in TRAIN_ALGOS if a != "RL"
              for r in (tr.get(a) or [])[:1] if r.get("eval_mean_reward") is not None}
    if scored:
        best = max(scored, key=scored.get)
        parts.append(f"training lead {best} ({scored[best]:.1f})")
    if not parts:
        return "No data yet - waiting for the first cycle to fire."
    return "Training is live: " + "; ".join(parts) + "."


# Display names that are shorter than the registry algo keys.
_ALGO_DISP = {"MaskablePPO": "MaskPPO"}
# last-seen latest-run id per algo, for the "new run" flash
_LAST_RUN_ID = {}


def _algo_name(a):
    return _ALGO_DISP.get(a, a)


def _algo_trend(series):
    """Up/down arrow of the two most recent rewards (series newest-first).

    Returns '^' if the newest run beat the previous, 'v' if it fell, '=' if
    equal, or '' when there aren't two usable points yet.
    """
    vals = [p["reward"] for p in series[:2] if p.get("reward") is not None]
    if len(vals) < 2:
        return ""
    return "^" if vals[0] > vals[1] else ("v" if vals[0] < vals[1] else "=")


def _last_run_meta(a, tr):
    """Return (run, color) for an algo's newest run, updating the flash map."""
    runs = tr.get(a) or []
    if not runs:
        return None, ""
    r = runs[0]
    rid = r.get("run_id")
    m = r.get("eval_mean_reward")
    fresh = _LAST_RUN_ID.get(a) not in (None, rid)
    _LAST_RUN_ID[a] = rid
    arrow = _algo_trend(tr.get("series", {}).get(a) or [])
    if fresh:
        col = C_YEL  # new run since the previous refresh
    elif arrow == "^":
        col = C_GRN
    elif arrow == "v":
        col = C_RED
    else:
        col = ""
    return r, col


def _training_grid(tr, width):
    """Fixed-height compact grid: one cell per algo, N columns by width.

    Cell: `PPO v3 289.4^` (model version, latest mean reward, trend vs
    previous run). Green improving / red falling / yellow = new since
    last refresh. Row count depends ONLY on width (never on data), so
    the frame height is predictable — this is what keeps the wallboard
    on one screen.
    """
    ncols = max(1, (width - 4) // 20)          # 18-char cell + 2-space separator
    rows_out = []
    if not tr.get("counts"):
        return ["    no training artifacts yet"]
    cells = []
    for a in TRAIN_ALGOS:
        r, col = _last_run_meta(a, tr)
        if r is None:
            cells.append((f"{_algo_name(a):<7}{"--":>11}", ""))
            continue
        m = r.get("eval_mean_reward")
        if m is None:
            cells.append((f"{_algo_name(a):<7}{"n/a":>11}", ""))
            continue
        arrow = _algo_trend(tr.get("series", {}).get(a) or [])
        ver = (r.get("model_version") or "?").lstrip("v") or "?"
        if len(ver) > 4 and "." in ver:
            ver = ".".join(ver.split(".")[:2])
        val = f"v{ver} {m:.1f}{arrow}"
        cells.append((f"{_algo_name(a):<7}{val:>11}", col))
    for i in range(0, len(cells), ncols):
        chunk = cells[i:i + ncols]
        parts = []
        for body, col in chunk:
            parts.append(f"{col}{body}{C_RST}" if col else body)
        rows_out.append("    " + "  ".join(parts))
    return rows_out


def _vis_len(s):
    """Visible length ignoring ANSI color codes."""
    import re
    return len(re.sub("\x1b\\[[0-9;]*m", "", s))


def _fit(s, width):
    """Truncate to window width (visible chars); never wrap, never scroll.

    Colors are stripped on truncation (simpler than re-closing codes, and
    truncated lines are rare edge cases on narrow windows).
    """
    import re
    if _vis_len(s) <= width:
        return s
    return re.sub("\x1b\\[[0-9;]*m", "", s)[:max(0, width)]


def render(data, now):
    """Fixed-frame one-screen wallboard (2026-09-09 redesign).

    Every section has a data-independent line budget and every line is
    truncated (never wrapped) to the window width, so the frame height is
    bounded by construction: header 3 + LOOPS 1 + EVO 2 + STEER 1 +
    TRAIN head 1 + grid ceil(15/ncols) + VERDICT 1 + alerts 0..2.
    Small windows show the same sections narrower — never scrolled.
    The plain-English interpretation moved to the log file (append_log).
    """
    width, height = shutil.get_terminal_size((100, 30))
    width = max(64, min(width, 200))
    _FRAME_NO[0] += 1   # twinkle step for the rainbow GOSP line
    # Priority drop for short windows (2026-09-09): the bottom sections
    # (TRAIN grid, verdict) must never be cut — drop detail lines first.
    show_climb = height >= 22
    show_genes = height >= 19
    lines = []
    L = lines.append

    L("=" * width)
    L(_fit(f"  AZAZAEL LIVE MONITOR   {now.strftime('%Y-%m-%d %H:%M:%S')}   (refresh {REFRESH}s, Ctrl+C to stop)", width))
    L("=" * width)

    # --- cycle freshness, one line ---
    bits = []
    any_stale = False
    for f in data["freshness"]:
        if f["ts"] is None:
            bits.append((f"{f['label']}: --", C_RED))
            any_stale = True
            continue
        a = f["age"]
        ok = f["ok"]
        if not ok:
            any_stale = True
        label = f"{f['label']} {a:.1f}m"
        bits.append((label, C_GRN if ok else C_RED))
    L(_fit("LOOPS  " + "   ".join(f"{c}{t}{C_RST}" if c else t for t, c in bits), width))

    # --- evolution ---
    evo = data["evo"]
    hard_stale = None  # hours since newest hard example (None = unknown/absent)
    if evo:
        e = evo[0]
        g = e.get("genes") or {}
        # promotion standing folded into the EVO line (0 extra rows)
        prom_txt = ""
        if e.get("baseline") is not None:
            if e["beats"]:
                prom_txt = (f"  {C_GRN}beats base +{e['best'] - e['baseline']:.2f}{C_RST}"
                            + (f"  {C_YEL}PROMOTED{C_RST}" if e["promoted"] else ""))
            else:
                prom_txt = f"  vs base {e['baseline']:.1f}"
        L(_fit(f"EVO    best {C_GRN}{e['best']:.3f}{C_RST}"
                 + (f"  info={e['info'] if e['info'] is not None else '?'} "
                    f"alert={e['alert'] if e['alert'] is not None else '?'}"
                    if e.get("info") is not None or e.get("alert") is not None else "")
                 + prom_txt, width))
        # --- the three learners together: META + GOSP beside EVO ---
        _m = data.get("meta") or {}
        _mp = _m.get("params") or {}
        if _mp:
            _meta_txt = (f"META   mut={_mp.get('mutation_rate', 0):.2f} "
                         f"xov={_mp.get('crossover_rate', 0):.2f} "
                         f"tour={_mp.get('tournament_size', 0)} "
                         f"pat={_mp.get('early_stop_patience', 0)} "
                         f"tol={_mp.get('early_stop_tolerance', 0):.3f}  "
                         f"ema {_m.get('score_ema', 0):+.2f}/{_m.get('runs', 0)}r")
            _cand = _m.get("candidate")
            if _cand:
                _diff = [k for k in ("mutation_rate", "crossover_rate",
                                     "tournament_size", "early_stop_patience",
                                     "early_stop_tolerance")
                         if _cand.get(k) != _mp.get(k)]
                _cr, _cs = _m.get("candidate_runs", 0), _m.get("candidate_sum", 0.0)
                _cmean = f" mean{_cs / _cr:+.2f}" if _cr else ""
                if _diff:
                    _cv = _cand[_diff[0]]
                    _cv = round(_cv, 4) if isinstance(_cv, float) else _cv
                    _meta_txt += (f"  {C_YEL}testing {_diff[0]}={_cv} "
                                  f"({_cr}/3{_cmean}){C_RST}")
                else:
                    _meta_txt += f"  {C_YEL}testing candidate ({_cr}/3{_cmean}){C_RST}"
        else:
            _meta_txt = "META   no meta state yet (first scored cycle still running)"
        L(_fit(_meta_txt, width))
        _g = data.get("gosp") or {}
        _gl = _g.get("learner") or {}
        L(_fit(f"{C_ORG}{C_BLD}Gossamer Oxford Semantical Parser{C_RST}", width))
        _gtxt = "GOSP  "
        if _gl:
            _gsegs = []
            if _gl.get("iter") is not None:
                _gsegs.append(f"iter={_gl['iter']}")
            if _gl.get("conv") is not None:
                _gsegs.append(f"conv={_gl['conv']}")
            if _gl.get("acc") is not None:
                _gsegs.append(f"acc={_gl['acc']}")
            if _gl.get("docs") is not None:
                _gsegs.append(f"docs={_gl['docs']}")
            _gtxt += "  " + " ".join(_gsegs)
            if _gl.get("mover") and _gl["mover"] != "?":
                _gtxt += f"  top mover {_gl['mover']} {_gl.get('mfrom')}->{_gl.get('mto')}"
            _gp = _g.get("parity") or {}
            if _gp.get("total"):
                _gtxt += f"  parity {_gp['agree']}/{_gp['total']}"
            _gr = _g.get("rani") or {}
            if _gr.get("mode"):
                _gtxt += f"  rani {_gr['mode'].split(' ')[0]}"
        else:
            _gtxt += " no learner evidence yet (run gosp_learner_train.py in WSL)"
        L(_rainbow(_gtxt, width))
        # --- Eve Unleashed RANI: which backend answered last + battery stats ---
        _rb = (data.get("gosp") or {}).get("rani_batt")
        if _rb:
            _rparts = [f"backend={_rb.get('backend', '?')}"]
            if _rb.get("rounds") is not None:
                _rparts.append(f"{_rb['rounds']} rounds")
            if _rb.get("adv") is not None:
                _rparts.append(f"adv={_rb['adv']}")
            if isinstance(_rb.get("score"), (int, float)):
                _rparts.append(f"score={_rb['score']:.2f}")
            if isinstance(_rb.get("lat"), (int, float)):
                _lat = _rb['lat']
                _rparts.append(f"lat={_lat / 1000:.1f}s" if _lat >= 1000 else f"lat={_lat:.0f}ms")
            if _rb.get("date"):
                _rparts.append(f"({_rb['date']})")
            L(_fit("EVE    " + "  ".join(_rparts), width))
        else:
            L(_fit("EVE    no RANI battery yet (run gosp_rani_integration.py or rani_llm_test.py)", width))
        # evo genetics detail: champion re-eval, beat rate, pool mix
        _champs = [e2.get("champ") for e2 in evo[:2]]
        _champ_txt = "champ " + "->".join("%.2f" % c for c in _champs if c is not None) or "champ n/a"
        _beat_n = sum(1 for e2 in evo[:10] if e2.get("beats"))
        _pool0 = evo[0].get("pool") or {}
        _pmix = "/".join(f"{k}={_pool0[k]}" for k in ("info", "critical", "warning")
                         if isinstance(_pool0.get(k), (int, float)))
        L(_fit(f"EVO2   {_champ_txt}  beats {_beat_n}/{min(10, len(evo))}  pool {_pmix}"
               + (f"  run gens={len(evo[0].get('traj') or [])}" if evo[0].get("traj") else ""), width))
        # pool drift: hard-alert inflow (starvation would freeze this)
        pool = e.get("pool") or {}
        hard = pool.get("hard_count")
        hard_ts = (pool.get("hard_newest") or "")[11:16] if pool.get("hard_newest") else ""
        # staleness: age of the newest hard example in hours (None if unknown)
        hard_stale = None
        if pool.get("hard_newest"):
            try:
                hdt = datetime.fromisoformat(str(pool["hard_newest"]).replace("Z", "+00:00"))
                hard_stale = (now - hdt.astimezone()).total_seconds() / 3600.0
            except Exception:
                hard_stale = None
        pool_txt = ""
        if hard:
            pool_txt = f"  hard {hard}" + (f"@{hard_ts}Z" if hard_ts else "")
            if hard_stale is not None and hard_stale > 24:
                pool_txt += f"  {C_RED}(stale {hard_stale:.0f}h){C_RST}"
        L(_fit(f"GENES lr={g.get('learning_rate', 0):.4f} eps={g.get('epsilon', 0):.4f} "
                 f"disc={g.get('discount', 0):.4f} dec={g.get('epsilon_decay', 0):.4f}  [{e['fit']}]{pool_txt}", width)) if show_genes else None
        bests = [e2["best"] for e2 in evo][::-1]
        if show_climb:
            L(f"CLIMB ({len(bests)} runs, newest right) {C_CYN}{sparkline(bests, width=max(10, width - 30))}{C_RST}")
        # per-generation trajectory of the latest run (how it got there)
        _tj = evo[0].get("traj") or []
        if _tj:
            _tvals = [f"{x:.2f}" for x in _tj]
            _tflag = "flat" if len(set(round(x, 3) for x in _tj)) <= 1 else f"+{_tj[-1] - _tj[0]:+.2f}"
            L(_fit(f"TRAJ   {' '.join(_tvals)}  [{_tflag} over {len(_tvals)} gens]", width))
    else:
        L("EVO    no evolution_result rows yet")

    # --- steering + activity on one line ---
    s = data["strategy"]
    act = data["activity"]
    flip = data.get("last_flip")
    flip_txt = ""
    if flip and flip.get("to") != s["value"]:
        # strategy currently differs from last committed flip -> show pending
        flip_txt = f"  [last change -> {C_GRN}{flip['to']}{C_RST} {flip['age']}m ago]"
    elif flip:
        fa = flip.get("age")
        if fa is not None and fa < 60:
            flip_txt = f"  [{C_YEL}flipped to {flip['to']} {flip['age']}m ago{C_RST}]"
        else:
            flip_txt = f"  [last flip -> {flip['to']} {flip['age']}m ago]"
    # STEER line is width-adaptive (2026-09-08): segments are dropped
    # right-to-left when the window is tight so the line never wraps.
    steer_segs = [f"STEER  {C_YEL}{s['value']}{C_RST} ({data['steer_24h']}/24h)"]
    if flip_txt:
        steer_segs.append(flip_txt)
    steer_segs.append(f"DREAMS {act['dreams']}/hr q={act['quality']:.3f}")
    _tn = data.get("tuned")
    if _tn and isinstance(_tn.get("cf"), (int, float)):
        steer_segs.append(f"tuned cf={_tn['cf']:.2f} sc={_tn.get('sc', '?')}")
    steer_segs.append(f"adapt {act.get('adapt_age')}m ago  apply {act.get('apply_age')}m ago")
    _steer = steer_segs[0]
    for _seg in steer_segs[1:]:
        if len(_steer) + len(_seg) + 3 <= width - 4:
            _steer += "   " + _seg
        else:
            break
    L(_fit(_steer, width))

    # --- policy verdict: what the last dream round actually did ---
    _py = data.get("policy")
    if _py:
        _ptxt = f"POLICY applied {_py.get('napplied', 0)} skipped {_py.get('nskipped', 0)}"
        if _py.get("worm") and _py.get("rec"):
            _cf = _py.get("conf")
            _cfs = f"{_cf:.3f}" if isinstance(_cf, (int, float)) else "?"
            _ad = "ADAPTED" if _py.get("adapted") else "held"
            _ptxt += f"  {_py['worm']}->{_py['rec']} conf={_cfs} {_ad}"
        _pa = _py.get("age")
        if isinstance(_pa, (int, float)):
            _ptxt += f"  {_pa:.0f}m ago"
        L(_fit(_ptxt, width))

    # --- meta-director: who trains next + top tracks by win rate ---
    try:
        import meta_director as _md
    except Exception:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import meta_director as _md
        except Exception:
            _md = None
    if _md is not None:
        try:
            _ledger = _md.load_ledger(TRAIN_ALGOS)
            _slot = int(time.time()) // 300
            _pick = _md.pick(_slot, _ledger, TRAIN_ALGOS)
            _top = _md.top_tracks(_ledger, TRAIN_ALGOS, 3)
            L(_fit(f"DIR    next {C_CYN}{_pick}{C_RST}  "
                   + "  ".join(f"{a}({m:.2f})" for a, m in _top), width))
        except Exception:
            L(_fit("DIR    director unavailable", width))
    else:
        L(_fit("DIR    director unavailable", width))

    # --- training: fixed compact grid (row count depends only on width) ---
    tr = data.get("training", {})
    nxt = tr.get("next_rotation", "?")
    L(_fit(f"TRAIN  next slot {C_CYN}{nxt}{C_RST}   (reward ^/v vs previous run, yellow = new)", width))
    for r_ in _training_grid(tr, width):
        L(r_)

    # --- run counts per track (cycles each algo has completed) ---
    _counts = tr.get("counts") or {}
    if _counts:
        _ordered = sorted(_counts.items(), key=lambda kv: -kv[1])
        _total = sum(_counts.values())
        L(_fit(f"RUNS   {_total} total  " + "  ".join(f"{_algo_name(a)}x{n}" for a, n in _ordered), width))

    # --- recent runs: last few training cycles across all tracks ---
    _rr = data.get("recent_runs") or []
    if _rr:
        _cells = []
        for _r in _rr[:4]:
            _rw = f"{_r['reward']:.1f}" if isinstance(_r.get("reward"), (int, float)) else "?"
            _age = f"{_r['age']:.0f}m" if isinstance(_r.get("age"), (int, float)) else "?"
            _cells.append(f"{_r.get('algo', '?')} {_rw} ({_age} ago)")
        L(_fit("LAST   " + "   ".join(_cells), width))

    # --- promotion file: hyperparams actually live in production ---
    _pr = data.get("promo")
    if _pr:
        _streak, _streak_n = "", 0
        for _e2 in data.get("evo") or []:
            if str(_e2.get("fit", "")).startswith("v3") and _e2.get("beats"):
                _streak_n += 1
            else:
                break
        if _streak_n:
            _streak = f"  streak {_streak_n}/3"
        L(_fit(f"PROMO  lr={_pr['lr']} eps={_pr['eps']} disc={_pr['disc']} "
               f"fit={_pr.get('fit')} wins={_pr.get('wins')} {_pr.get('age')}m ago{_streak}", width))
    else:
        L(_fit("PROMO  no promoted params file (defaults in effect)", width))

    # --- tuner bests: what the specialist tracks found ---
    _tn = data.get("tuners") or {}
    _dt = _tn.get("dreamtune") or {}
    if _dt:
        _dp = _dt.get("params") or {}
        _cf = _dp.get("creativity_factor")
        _sc = _dp.get("scenario_count")
        _dtxt = (f"TUNE   dreamtune cf={_cf:.2f} sc={_sc:.0f}" if isinstance(_cf, (int, float)) else "TUNE   dreamtune ?")
        if isinstance(_dt.get("fit"), (int, float)):
            _dtxt += f" fit={_dt['fit']:.3f}"
        L(_fit(_dtxt, width))
    _wb = _tn.get("wormga") or {}
    _board = _wb.get("board") or {}
    if _board:
        _ab = {"SYSTEMZ": "SYS", "PROCESSZ": "PRC", "DISKZ": "DSK",
               "NETWORXZ": "NET", "CLOCKZ": "CLK", "HEALTHZ": "HLT"}
        _cells = []
        for _w in ("SYSTEMZ", "PROCESSZ", "DISKZ", "NETWORXZ", "CLOCKZ", "HEALTHZ"):
            _e = _board.get(_w) or {}
            _sr = _e.get("success_rate")
            _cells.append(f"{_ab.get(_w, _w[:3])} {int(round(_sr * 100))}%" if isinstance(_sr, (int, float)) else f"{_ab.get(_w, _w[:3])} ?")
        _wfit = f" fit={_wb['fit']:.3f}" if isinstance(_wb.get("fit"), (int, float)) else ""
        L(_fit("WORMS  " + "  ".join(_cells) + _wfit, width))

    # --- cycle processes: scheduler tasks proven alive by their own logs ---
    _cy = data.get("cycles") or []
    if _cy:
        _bits = []
        for _c in _cy:
            _a = _c.get("age")
            _txt = f"{_c.get('label')} {_a:.0f}m" if isinstance(_a, (int, float)) else f"{_c.get('label')} --"
            _bits.append((_txt, _a is not None and _a < 15))
        L(_fit("CYCLES " + "   ".join(f"{C_GRN}{t}{C_RST}" if _ok else f"{C_RED}{t}{C_RST}" for t, _ok in _bits), width))

    # --- store size + write rate + alert load ---
    _st = data.get("store")
    if _st:
        _mb = f"{_st['mb']}MB" if _st.get("mb") is not None else "?"
        _al = data.get("alerts") or {}
        _atxt = f"  alerts {_al.get('per_hr', 0)}/hr ({_al.get('crit', 0)} crit)" if _al.get("per_hr") else ""
        L(_fit(f"STORE  {_mb} {(_st.get('rows') or 0):,} rows  +{(_st.get('per_hr') or 0):,}/hr{_atxt}", width))

    # --- inference servers ---
    _sv = data.get("servers") or []
    if _sv:
        _bits = []
        for _s in _sv:
            if _s.get("ok"):
                _bits.append(f":{_s['port']} ok {_s.get('ms')}ms")
            else:
                _bits.append(f"{C_RED}:{_s['port']} DOWN{C_RST}")
        L(_fit("SRV    " + "   ".join(_bits), width))

    # --- llm scoreboard: measured tok/s per local model ---
    _lm = data.get("llm") or []
    if _lm:
        _cells = []
        for _m in _lm:
            _nm = str(_m.get("model", "?"))
            for _cut in ("-it-", "-instruct", "-uncensored", ".gguf", "_GGUF"):
                _nm = _nm.split(_cut)[0]
            _nm = _nm.split("/")[-1].split("\\")[-1][:14]
            _gp = f"{_m['gen']:.0f}/s" if isinstance(_m.get("gen"), (int, float)) else "?"
            _pp = f"{_m['prompt']:.0f}" if isinstance(_m.get("prompt"), (int, float)) else "?"
            _th = "T" if (_m.get("think") or 0) > 200 else ""
            _cells.append(f"{_nm} {_pp}/{_gp}{_th}")
        L(_fit("MODELS " + "   ".join(_cells), width))

    # --- alerts + verdict: fixed lines, only what fires ---
    if any_stale:
        L(_fit(f"{C_RED}STALE  {', '.join(f['label'] for f in data['freshness'] if not f['ok'])} "
                 f">15 min - check Task Scheduler.{C_RST}", width))
    if evo and hard_stale is not None and hard_stale > 24:
        L(_fit(f"{C_RED}HARDPOOL  no fresh critical-alert examples for {hard_stale:.0f}h - "
               f"evolution is re-mastering frozen rows.{C_RST}", width))
    bl = bottom_line(data)
    L(_fit(f"    {C_BLD}Verdict:{C_RST} {bl}", width))

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
            tr = data.get("training", {})
            if tr.get("counts"):
                scored = {a: r["eval_mean_reward"] for a in TRAIN_ALGOS
                          for r in (tr.get(a) or [])[:1] if r.get("eval_mean_reward") is not None}
            f.write("  train " + ", ".join(f"{a}={v:.1f}" for a, v in sorted(scored.items()))
                    + f"  next={tr.get('next_rotation')}\n")
            for tag, msg in explain(data):
                f.write(f"  {tag:<6} {msg}\n")
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


def _paint_in_place(frame_lines):
    """Redraw the dashboard in place: no full-screen clear, no scrolling.

    Moves the cursor home, overwrites each row (erasing to end-of-line so a
    shorter row never leaves stale text), then erases only the rows below the
    frame. Never emits a trailing newline past the bottom row, so the console
    never scrolls -- everything stays on one screen and updates in place.
    """
    import shutil as _sh
    size = _sh.get_terminal_size((100, 30))
    max_rows = max(4, size.lines - 1)
    rows = frame_lines[:max_rows]          # never exceed the visible window
    if len(rows) < max_rows:
        rows = rows + [""] * (max_rows - len(rows))  # wipe any longer old frame

    out = ["\033[H"]                       # cursor home (keep the old buffer)
    for i, line in enumerate(rows):
        if i:
            out.append("\r\n")
        out.append(line)
        out.append("\033[K")               # erase to end of this line
    out.append("\033[J")                   # erase everything below the frame
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def _pid_alive(pid):
    """Windows liveness check (2026-09-09 fix): os.kill(pid, 0) is not
    supported on Windows (WinError 87) — it always raised, so every guard
    using it never blocked. OpenProcess is the correct probe."""
    try:
        import ctypes
        _SYNCHRONIZE = 0x00100000
        h = ctypes.windll.kernel32.OpenProcess(_SYNCHRONIZE, False, int(pid))
        if not h:
            return False
        ctypes.windll.kernel32.CloseHandle(h)
        return True
    except Exception:
        return False


def _single_instance():
    """Exit if another live monitor is already running (2026-09-09).

    Two painters would fight over consoles and double every log line.
    Stale PID files are stolen (crash-safe), like dream_cycle's guard.
    """
    lock = os.path.join(tempfile.gettempdir(), "azazael_live_monitor.lock")
    try:
        with open(lock) as f:
            old = int((f.read() or "0").strip() or 0)
        if old and _pid_alive(old):
            print(f"Another live monitor is already running (PID {old}) - not starting a second one.",
                  file=sys.stderr)
            return False
    except (OSError, ValueError):
        pass
    try:
        with open(lock, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass
    return True


def main():
    global REFRESH, LOG_PATH
    ap = argparse.ArgumentParser(description="Persistent Azazael live dashboard")
    ap.add_argument("--refresh", type=int, default=30)
    ap.add_argument("--log", default=LOG_PATH)
    args = ap.parse_args()
    REFRESH = max(5, args.refresh)
    LOG_PATH = os.path.abspath(args.log)

    if not _single_instance():
        return 2

    con = db_connect()
    if con is None:
        print(f"FATAL: cannot open {DB}", file=sys.stderr)
        return 2

    first = True
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

        if first:
            # clear once on startup so the first frame starts from a clean screen
            sys.stdout.write("\033[2J\033[H")
            first = False
        _paint_in_place(text.split("\n"))
        time.sleep(REFRESH)


if __name__ == "__main__":
    sys.exit(main())