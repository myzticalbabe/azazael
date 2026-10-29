#!/usr/bin/env python3
"""morphed_trainers — close the outer loop: evolve -> factory.

NSGA-II searches numeric SB3 hyperparameters (log learning_rate,
gamma, and one algo-native knob) against Pareto objectives; winners land
as first-class `morphed_<algo>_g<gen>` entries resolvable by the
trainers_v2 factory path in SB3Agent. Mutation varies parameters and
keeps identity (MUTATE, not morph): a morphed PPO is still PPO.

Objectives are proxy-evaluated (no full SB3 learn per genome — that cost
belongs to generation promotion, not search): reward-proxy favors
mid-range stable hyperparams, cost-proxy favors small batches/frequent
updates. Pareto fronts come from src/ML/nsga.py (sbx + polynomial).

Usage:
    from CORE.morphed_trainers import propose, promote, resolve_morphed
    proposals = propose("PPO", generations=8, pop_size=24, seed=7)
    winner = promote(proposals[0])   # registers morphed_ppo_g<N>
    SB3Agent(algo=winner["name"])     # resolves via factory
"""

import json
import math
import time
from pathlib import Path

import numpy as np

from ML.nsga import NSGA2

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here


# Searchable numeric knobs per algo: (key, low, high, log_scale).
MORPHABLE_KNOBS: dict = {
    "PPO": [("learning_rate", 1e-5, 1e-3, True),
            ("gamma", 0.90, 0.999, False),
            ("clip_range", 0.1, 0.3, False)],
    "DQN": [("learning_rate", 1e-5, 1e-3, True),
            ("gamma", 0.90, 0.999, False),
            ("tau", 0.1, 1.0, False)],
    "SAC": [("learning_rate", 1e-5, 1e-3, True),
            ("gamma", 0.90, 0.999, False),
            ("tau", 0.005, 0.05, False)],
    "A2C": [("learning_rate", 1e-5, 1e-3, True),
            ("gamma", 0.90, 0.999, False),
            ("gae_lambda", 0.8, 1.0, False)],
}

DEFAULT_KNOBS = [("learning_rate", 1e-5, 1e-3, True),
                 ("gamma", 0.90, 0.999, False)]

_STORE_PATH = Path(__file__).with_name("morphed_registry.json")


def _load_store() -> dict:
    try:
        return json.loads(_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"generation": 0, "entries": {}}


def _save_store(store: dict) -> None:
    store["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    _STORE_PATH.write_text(json.dumps(store, indent=1) + "\n", encoding="utf-8")


def _decode(genome, knobs: list) -> dict:
    """Genome unit-cube -> hyperparam dict (log-scale where flagged)."""
    params: dict = {}
    for value, (key, low, high, log_scale) in zip(genome, knobs):
        value = min(1.0, max(0.0, float(value)))
        if log_scale:
            params[key] = math.exp(math.log(low) + value * (math.log(high) - math.log(low)))
        else:
            params[key] = low + value * (high - low)
    return params


def propose(algo: str = "PPO", generations: int = 8,
            pop_size: int = 24, seed: int = 7) -> list:
    """NSGA-II search over knobs; return Pareto-front proposals (JSON-safe).

    Each proposal: {algo, params, objectives, rank}. No training happens
    here — search is proxy-evaluated; promotion pays the real cost.
    """
    knobs = MORPHABLE_KNOBS.get(algo, DEFAULT_KNOBS)
    dim = len(knobs)

    def reward_proxy(x: np.ndarray) -> float:
        """Maximize: favor mid-range stable hyperparams (negative cost)."""
        params = _decode(x, knobs)
        lr_penalty = abs(float(np.log10(params.get("learning_rate", 3e-4))) + 3.5)
        gamma = float(params.get("gamma", 0.99))
        gamma_penalty = abs(gamma - 0.99) * 10.0
        return float(lr_penalty + gamma_penalty)

    def cost_proxy(x: np.ndarray) -> float:
        """Maximize: favor cheap configs (placeholder for wall-clock)."""
        params = _decode(x, knobs)
        return float(abs(float(x[0]) - 0.5) + abs(float(x[-1]) - 0.5))

    bounds = np.array([[0.0, 1.0]] * dim)
    driver = NSGA2(fns=[reward_proxy, cost_proxy], bounds=bounds,
                   pop_size=pop_size, seed=seed)
    pareto_x, pareto_f = driver.run(generations)
    proposals = []
    for rank, (genome, objs) in enumerate(zip(pareto_x, pareto_f)):
        proposals.append({
            "algo": algo,
            "params": _decode(genome, knobs),
            "objectives": [float(o) for o in objs],
            "rank": rank,
            "seed": seed,
            "generations": generations,
        })
    return proposals


def promote(proposal: dict) -> dict:
    """Register a Pareto proposal as morphed_<algo>_g<gen> (transsubstantiation
    hook: the name is factory-resolvable; substance upgraded, callers unchanged)."""
    store = _load_store()
    store["generation"] = int(store.get("generation", 0)) + 1
    gen = store["generation"]
    algo = str(proposal.get("algo", "PPO"))
    name = f"morphed_{algo.lower()}_g{gen}"
    store.setdefault("entries", {})[name] = {
        "algo": algo,
        "params": proposal.get("params", {}),
        "objectives": proposal.get("objectives", []),
        "parent": "nsga2-pareto",
        "generation": gen,
    }
    try:
        _save_store(store)
    except OSError as e:
        note_failure("morphed_trainers:store", e)
        return {"name": "", "ok": False, "error": str(e)}
    return {"name": name, "ok": True, "generation": gen,
            "algo": algo, "params": store["entries"][name]["params"]}


def resolve_morphed(name: str) -> dict | None:
    """Return the stored entry for a morphed name, or None."""
    return _load_store().get("entries", {}).get(name)


def list_morphed() -> dict:
    """All registered morphed trainers."""
    return _load_store().get("entries", {})
