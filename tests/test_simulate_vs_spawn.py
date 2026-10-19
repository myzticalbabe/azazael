#!/usr/bin/env python3
"""EP110 simulate-vs-spawn: rehearsal is measured, decision flips on scale."""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from CORE.WORMS.expansion.allocation import rehearse_then_decide

_ARMS = ["discover", "execute", "report"]
_PROXY = {("discover",): 0.5, ("discover", "execute"): 0.7,
          ("execute",): 0.4, ("report",): 0.2}
_VERIFY = {("discover", "execute"): 0.9, ("discover", "report"): 0.6,
           ("discover",): 0.3}


def _run(**kw):
    args = {"arms": _ARMS,
            "pre_score": lambda seq: _PROXY.get(tuple(seq), 0.35),
            "post_eval": lambda seq: _VERIFY.get(tuple(seq), 0.1),
            "iters": 12}
    args.update(kw)
    return rehearse_then_decide(**args)


def test_rehearsal_runs_live_planner():
    out = _run(spawn_cost=1e9)
    assert out["visits"] > 0
    assert out["best_seq"]
    assert set(out["best_seq"]) <= set(_ARMS)
    assert out["rehearsal_seconds"] >= 0.0


def test_simulate_branch_when_spawn_dwarfs_rehearsal():
    with mock.patch("time.perf_counter", side_effect=[100.0, 100.05]):
        out = _run(spawn_cost=5.0)
    assert out["decision"] == "simulate"
    assert abs(out["margin"] - 4.95) < 1e-9


def test_spawn_branch_when_rehearsal_exceeds_spawn():
    with mock.patch("time.perf_counter", side_effect=[100.0, 100.05]):
        out = _run(spawn_cost=0.01)
    assert out["decision"] == "spawn"
    assert out["margin"] < 0.0


def test_ep110_wiring_invokes_live_rehearsal():
    from CORE.technique_wiring import _l5_dispatch as l5
    out = l5._ep110()
    assert out["engaged"] is True
    assert out["accepted"] is True
    assert out["decision"] in ("simulate", "spawn")
    assert out["where"].endswith("rehearse_then_decide")
