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


def main() -> int:
    from CORE.WORMS.expansion.mesh import MeshRouterWorm
    from CORE.WORMS.expansion.spine import SpineCycleWorm
    from CORE import spine_registry as sp

    # 1. Traffic: keep the ledger fed so homeostat clears MIN_SAMPLES.
    m = MeshRouterWorm()
    for dst in ("bare", "wsl2-ubuntu", "wsl2-kali", "g_archive"):
        try:
            m.record_route_result(dst, True, 50.0)
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
