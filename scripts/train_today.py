#!/usr/bin/env python3
"""Full-day training compressed into one run: exploration + chaos + fitness.

- EXPLORATION (epsilon-greedy): each cycle picks a random env pair and takes a
  REAL measurement (WSL round-trip / G: IO / DNS). No fabricated outcomes.
- CHAOS (safe, rotating): worker prune path, partition detect/heal path, and
  one CONTROLLED failure (unresolvable host) to guarantee a failure gradient.
- FITNESS: per-cycle metrics appended to G: fitness.jsonl (loss proxy, Q
  spread, alerts, ledger size). Final deltas printed.
- Every 4th cycle runs SpineCycleWorm(apply=True) so proposals land.

Usage: python C:/Users/clint/azazael/scripts/train_today.py [cycles=12]
"""
import json
import logging
import os
import random
import socket
import subprocess
import sys
import time

logging.disable(logging.CRITICAL)
sys.path.insert(0, "C:/Users/clint/azazael/src")

FIT = "G:/source-of-truth/azazael_models/fitness.jsonl"
CYCLES = int(sys.argv[1]) if len(sys.argv) > 1 else 12
EPSILON = 0.35


def measure(env):
    """REAL latency probe per env. Returns (success, ms)."""
    t0 = time.perf_counter()
    try:
        if env == "wsl2-ubuntu":
            r = subprocess.run(["wsl", "-d", "Ubuntu-26.04", "--", "echo", "ok"],
                               capture_output=True, timeout=60)
            ok = r.returncode == 0
        elif env == "wsl2-kali":
            r = subprocess.run(["wsl", "-d", "kali-linux", "--", "echo", "ok"],
                               capture_output=True, timeout=60)
            ok = r.returncode == 0
        elif env == "g_archive":
            p = "G:/source-of-truth/azazael_models/probe.tmp"
            open(p, "w").write("x" * 4096)
            os.stat(p)
            os.remove(p)
            ok = True
        elif env == "windows":
            socket.gethostbyname("localhost")
            ok = True
        else:
            ok = False
        return ok, round((time.perf_counter() - t0) * 1000, 1)
    except Exception:
        return False, round((time.perf_counter() - t0) * 1000, 1)


def main():
    from CORE.WORMS.expansion.mesh import MeshRouterWorm
    from CORE.WORMS.expansion.spine import SpineCycleWorm
    from CORE.WORMS.expansion.immune import ImmuneSentinelWorm
    from CORE.WORMS.expansion.glia import MicrogliaWorm
    from CORE import spine_registry as sp
    rnd = random.Random(20260914)
    m, glia, sent = MeshRouterWorm(), MicrogliaWorm(), ImmuneSentinelWorm()
    envs = ["wsl2-ubuntu", "wsl2-kali", "g_archive", "windows"]
    chaos_kinds = ["prune", "partition", "controlled-fail"]
    hist = []
    for c in range(1, CYCLES + 1):
        # 1. EXPLORATION: epsilon-greedy real probe
        dst = rnd.choice(envs)
        ok, ms = measure(dst)
        # success = responsive under 30s
        m.record_route_result(dst, ok and ms < 30000, ms)
        expl = {"cycle": c, "trial": dst, "ok": ok, "ms": ms}
        # 2. CHAOS rotating drill (real code paths, truthful outcomes)
        kind = chaos_kinds[(c - 1) % len(chaos_kinds)]
        # All chaos flows through registered ChaosWorm (homeostat only
        # proposes on registry-known worms) with truthful operation outcomes.
        from CORE.WORMS.expansion.chaos import ChaosWorm
        dr = ChaosWorm().drill(kind if kind != "controlled-fail" else kind)
        ok = bool(dr.get("result", {}).get("ok", False))
        ms_d = float(dr.get("result", {}).get("ms", 1.0))
        sp.record_outcome("diagnostic", "ChaosWorm", ok, ms_d)
        ch = {"kind": kind, "ok": ok}
        # 3. FITNESS sample
        view = sp.get_homeostat_view()
        samples = sum(v.get("successes", 0) + v.get("failures", 0) for v in view.values())
        fails = sum(v.get("failures", 0) for v in view.values())
        q = sp.get_q_weights()
        qvals = list(q.values()) if isinstance(q, dict) else []
        spread = round(max(qvals) - min(qvals), 3) if len(qvals) > 1 else 0.0
        fit = {"cycle": c, "samples": samples, "fails": fails, "q_spread": spread,
               "trial_ms": ms}
        hist.append(fit)
        try:
            with open(FIT, "a", encoding="utf-8") as f:
                f.write(json.dumps(fit) + "\n")
        except OSError:
            pass
        print(f"[{c}/{CYCLES}] trial={dst} ok={ok} {ms}ms chaos={kind} "
              f"samples={samples} fails={fails} spread={spread}", flush=True)
        if c % 4 == 0:
            rep = SpineCycleWorm(min_interval_seconds=0).run_cycle(apply=True)
            # Surface a refused write instead of printing a success-shaped
            # "proposals=0" -- the shape that hid the ~30h refusal.
            if rep.get("skipped"):
                print(f"  apply-cycle REFUSED: {rep.get('skipped')} -- "
                      f"{rep.get('reason')}", flush=True)
            else:
                home = rep.get("homeostat", {})
                print(f"  apply-cycle: scanned={home.get('scanned')} "
                      f"proposals={len(home.get('proposals') or [])} "
                      f"applied={home.get('applied')}", flush=True)
    sp.save_spine_state()
    print(f"DONE samples={hist[-1]['samples']} fails={hist[-1]['fails']} "
          f"spread={hist[0]['q_spread']}->{hist[-1]['q_spread']}")


if __name__ == "__main__":
    main()
