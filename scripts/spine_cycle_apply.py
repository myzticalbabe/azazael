#!/usr/bin/env python3
"""Hourly self-improvement cycle: SpineCycleWorm with apply=True.

Closes the loop the audit found open: default run_cycle(apply=False) is a
dry-run, and nothing invoked it on a schedule, so the homeostat ledger
starved (0 samples) and the Red Queen had no pressure. This entry point:
  1. feeds recent mesh route outcomes (keeps ledger above MIN_SAMPLES),
  2. runs run_cycle(apply=True) so proposals land,
  3. persists spine state (restart-safe).

Schedule (user-level, no admin):
  schtasks /create /tn AzazaelSpineCycle /tr "python %AZAZAEL_ROOT%\\scripts\\spine_cycle_apply.py" /sc hourly /f
Logs to ~/.azazael/spine_cycle.log. Checkpoint models stay on G:.
"""
import json
import logging
import os
import sys
import time
from datetime import datetime

logging.disable(logging.CRITICAL)
sys.path.insert(0, "C:/Users/clint/azazael/src")

LOG = os.path.expanduser("~/.azazael/spine_cycle.log")


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat()} {msg}"
    print(line, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def _measure(env: str) -> tuple:
    """REAL latency probe per env (no fabricated outcomes)."""
    import socket as _s
    import subprocess as _sp
    import time as _t
    t0 = _t.perf_counter()
    try:
        if env == "wsl2-ubuntu":
            ok = _sp.run(["wsl", "-d", "Ubuntu-26.04", "--", "echo", "ok"],
                         capture_output=True, timeout=60).returncode == 0
        elif env == "wsl2-kali":
            ok = _sp.run(["wsl", "-d", "kali-linux", "--", "echo", "ok"],
                         capture_output=True, timeout=60).returncode == 0
        elif env == "g_archive":
            p = "G:/source-of-truth/azazael_models/probe.tmp"
            open(p, "w").write("x" * 4096)
            os.stat(p)
            os.remove(p)
            ok = True
        else:
            _s.gethostbyname("localhost")
            ok = True
    except Exception:
        ok = False
    return ok, round((_t.perf_counter() - t0) * 1000, 1)


def main() -> int:
    from CORE.WORMS.expansion.mesh import MeshRouterWorm
    from CORE.WORMS.expansion.spine import SpineCycleWorm
    from CORE import spine_registry as sp

    # 0. Gossip round: merge ubuntu/kali ledgers via C: drop dir first, so
    # the cycle below sees the whole fleet's experience, not just local.
    try:
        import subprocess as _sp0
        _gr = _sp0.run([sys.executable, "C:/Users/clint/azazael/scripts/gossip_round.py"],
                       capture_output=True, text=True, timeout=300)
        _gl = (_gr.stdout or "").strip().splitlines()
        log(f"gossip: {_gl[-1][:160] if _gl else 'no-output'}")
    except Exception as exc:
        log(f"gossip: skipped ({str(exc)[:80]})")
    # 1. CURIOSITY probe: gemma ranks candidate envs (~20s, guarded); fallback
    # is thinnest-ledger-key. The pick is MEASURED for real, never fabricated.
    m = MeshRouterWorm()
    cands = ["wsl2-ubuntu", "wsl2-kali", "g_archive", "windows"]
    order = list(cands)
    try:
        from CORE.WORMS.expansion.driver import GemmaDriverWorm
        stats = {}
        try:
            gt = json.load(open("G:/source-of-truth/azazael_models/groundtruth.json"))
            vw = sp.get_homeostat_view()
            for e in cands:
                rk = [k for k in vw if k.endswith(">" + e)]
                n = sum(vw[k].get("successes", 0) + vw[k].get("failures", 0) for k in rk)
                stats[e] = {"ok_rate": gt.get(e, {}).get("ok_rate", 1.0),
                            "median_ms": gt.get(e, {}).get("median_ms", 50.0),
                            "samples": n}
        except Exception:
            stats = {}
        r = GemmaDriverWorm(timeout=90.0).rank_trials(
            cands, context="hourly mesh health probe", stats=stats or None)
        if r.get("order"):
            order = r["order"]
            log(f"curiosity: model-ranked {order} (src={r.get('src')})")
    except Exception as exc:
        log(f"curiosity: heuristic order ({str(exc)[:60]})")
    for dst in order[:2]:
        try:
            ok, ms = _measure(dst)
            m.record_route_result(dst, ok and ms < 30000, ms)
        except Exception:
            pass
    # 1b. eBPF sample (WSL Ubuntu, best-effort ~15s): score live syscall
    # rates vs bcc_baseline.json; any baseline alert becomes a ledger
    # failure sample so the homeostat trains on kernel telemetry hourly.
    try:
        import json as _json
        import shutil
        import subprocess as _sp
        # refresh the C: mirror WSL can read (WSL cannot see G:)
        for src, dst in (("G:/source-of-truth/azazael_models/bcc_baseline.json",
                          "C:/Users/clint/azazael/output/bcc_baseline.json"),):
            try:
                shutil.copyfile(src, dst)
            except OSError:
                pass
        r = _sp.run(["wsl", "-d", "Ubuntu-26.04", "--", "python3",
                     "/mnt/c/Users/clint/azazael/scripts/bcc_oneshot.py"],
                    capture_output=True, text=True, timeout=120)
        ebpf = _json.loads((r.stdout or "").strip().splitlines()[-1])
        n_alerts = len(ebpf.get("alerts", [])) if ebpf.get("success") else -1
        if n_alerts >= 0:
            # success = quiet window; the 8s collection is the duration.
            m.record_route_result("wsl2-ubuntu", n_alerts == 0, 8000.0)
            log(f"ebpf: comms={(ebpf.get('comms'))} alerts={n_alerts}")
        else:
            log(f"ebpf: skipped ({str(ebpf.get('error'))[:80]})")
    except Exception as exc:
        log(f"ebpf: skipped ({str(exc)[:80]})")
    # 2. Cycle with apply=True (proposals land, not just reported).
    c = SpineCycleWorm(min_interval_seconds=0)
    rep = c.run_cycle(apply=True)
    # 3. Persist is done inside run_cycle; belt-and-braces save.
    try:
        sp.save_spine_state()
    except Exception:
        pass
    home = (rep.get("homeostat") or {})
    log(f"cycle={rep.get('cycles')} scanned={home.get('scanned')} "
        f"proposals={len(home.get('proposals') or [])} "
        f"applied={home.get('applied')} queen={ (rep.get('red_queen') or {}).get('queen_role')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
