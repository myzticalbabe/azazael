# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: ALLOCATION (Circulation)

Circulation decides how much compute each search operator receives.

Why it exists. `scripts/evolution_cycle.py` gates its second arm with a fixed
rule::

    _cma_wanted = best is not None and _gate_margin < 2 * PROMOTE_MARGIN

On the 2026-09-11 widened-bounds batch every margin was >= 2.91 against a 1.5
threshold, so the arm was skipped **50/50** and CMA-ES / DE / TPE contributed
nothing. A fixed threshold cannot express "this operator earns its keep"; it
only expresses "this operator is not needed right now", and once a regime shifts
the arm never returns.

Circulation replaces the threshold with Thompson sampling over Beta posteriors:
an operator that produces promoted genomes earns more budget, one that never does
fades — but a `floor` guarantees no operator is ever fully starved, so a regime
change can be discovered instead of being structurally unreachable.
"""

from __future__ import annotations

import json
import random
from typing import Dict, Iterable, List, Optional

__all__ = ["ThompsonAllocator", "PROTEUS_ARMS", "reward_for_outcome"]

DEFAULT_FLOOR = 0.02

# In PROTEUS the allocator's arms include the STRUCTURAL operators, so the
# scheduler can fund a move that changes the search space or the world rather
# than only a numeric point (`PROTEUS_DEEP_EXPANSION.md` section 2.7).
PROTEUS_ARMS = ("ga", "cma", "de", "tpe", "morph", "arena", "chorus")

# Outcome -> (success, weight). A holdout pass is worth far more than beating a
# reused snapshot baseline, because E9 showed the latter buying 0/4 holdout
# passes. Weighting them equally is what let the fixed gate look productive.
_OUTCOME_REWARD = {
    "holdout_pass": (True, 1.0),
    "promoted": (True, 0.6),
    "beat_baseline": (True, 0.2),
    "novel": (True, 0.1),
    "flat": (False, 0.3),
    "holdout_fail": (False, 1.0),
    "error": (False, 1.0),
}


def reward_for_outcome(outcome: str) -> "Tuple[bool, float]":
    """Map a cycle outcome onto allocator feedback.

    Unknown outcomes fail closed (counted as failure, unit weight) so a new
    outcome string cannot silently inflate an arm's posterior.
    """
    return _OUTCOME_REWARD.get(str(outcome), (False, 1.0))


class ThompsonAllocator:
    """Beta-Bernoulli Thompson sampling over named operators.

    Usage::

        alloc = ThompsonAllocator(["ga", "cma", "de", "chorus"])
        for _ in range(cycles):
            arms = alloc.choose(2)          # exploit/explore by posterior draw
            ...
            alloc.update("cma", success=promoted)
        alloc.allocation(100)               # integer budget share, floored
    """

    def __init__(self, arms: Iterable[str], alpha: float = 1.0,
                 beta: float = 1.0, floor: float = DEFAULT_FLOOR,
                 rng: Optional[random.Random] = None):
        self.arms: List[str] = list(arms)
        if not self.arms:
            raise ValueError("ThompsonAllocator needs at least one arm")
        self.floor = max(0.0, float(floor))
        self._rng = rng or random.Random()
        self._prior = (float(alpha), float(beta))
        # success/failure pseudo-counts, seeded with the prior
        self._s: Dict[str, float] = {a: float(alpha) for a in self.arms}
        self._f: Dict[str, float] = {a: float(beta) for a in self.arms}
        self._pulls: Dict[str, int] = {a: 0 for a in self.arms}
        self._wins: Dict[str, int] = {a: 0 for a in self.arms}

    # -- allocation --------------------------------------------------------
    def choose(self, k: int = 1) -> List[str]:
        """Top-k arms by posterior draw (Thompson sampling)."""
        if k <= 0:
            return []
        k = min(k, len(self.arms))
        draws = []
        for a in self.arms:
            draws.append((self._rng.betavariate(self._s[a], self._f[a]), a))
        draws.sort(reverse=True)
        return [a for _, a in draws[:k]]

    def weights(self) -> Dict[str, float]:
        """Posterior mean success probability per arm."""
        out = {}
        for a in self.arms:
            s, f = self._s[a], self._f[a]
            out[a] = s / (s + f) if (s + f) > 0 else 0.0
        return out

    def allocation(self, total: int, temperature: float = 1.0) -> Dict[str, int]:
        """Integer budget split proportional to posterior means.

        Normalised weights do not sum with a floor applied, so the remainder is
        handed back to the strongest arms. The floor guarantees every arm keeps
        a minimum share, which is the whole point (see E10 in
        EVOLUTION_50RUN_GAPS_AND_FIXES.md).
        """
        total = int(total)
        if total <= 0:
            return {a: 0 for a in self.arms}
        raw = self.weights()
        t = max(float(temperature), 1e-6)
        powered = {a: max(w, 1e-9) ** (1.0 / t) for a, w in raw.items()}
        denom = sum(powered.values()) or 1.0
        share = {a: powered[a] / denom for a in self.arms}

        # apply the exploration floor, then renormalise
        f = self.floor
        floored = {a: max(share[a], f) for a in self.arms}
        fdenom = sum(floored.values()) or 1.0
        floored = {a: v / fdenom for a, v in floored.items()}

        out = {a: int(v * total) for a, v in floored.items()}
        # hand the rounding remainder to the highest-posterior arms
        remainder = total - sum(out.values())
        for a in sorted(self.arms, key=lambda x: floored[x], reverse=True):
            if remainder <= 0:
                break
            out[a] += 1
            remainder -= 1
        return out

    # -- feedback ----------------------------------------------------------
    def update(self, arm: str, success: bool, weight: float = 1.0,
               decays: Optional[Dict[str, float]] = None) -> None:
        """Record an outcome for `arm`.

        `weight` lets a strong success count for more than a marginal one
        (e.g. holdout-passed counts 1.0, beat-baseline counts 0.2). `decays`
        optionally multiplies every arm's pseudo-counts first, so old evidence
        fades in a non-stationary regime.
        """
        if decays:
            for a in self.arms:
                self._s[a] = max(self._prior[0], self._s[a] * decays.get(a, 1.0))
                self._f[a] = max(self._prior[1], self._f[a] * decays.get(a, 1.0))
        if arm not in self._s:
            self._s[arm] = self._prior[0]
            self._f[arm] = self._prior[1]
            self.arms.append(arm)
            self._pulls[arm] = 0
            self._wins[arm] = 0
        w = max(0.0, float(weight))
        self._pulls[arm] += 1
        if success:
            self._s[arm] += w
            self._wins[arm] += 1
        else:
            self._f[arm] += w

    def report(self) -> Dict[str, dict]:
        """Per-arm standing for the monitor/audit trail."""
        w = self.weights()
        out = {}
        for a in self.arms:
            out[a] = {
                "weight": round(w[a], 4),
                "pulls": self._pulls.get(a, 0),
                "wins": self._wins.get(a, 0),
                "successes": round(self._s[a] - self._prior[0], 3),
                "failures": round(self._f[a] - self._prior[1], 3),
            }
        return out

    def starved(self, threshold: float = 1e-9) -> List[str]:
        """Arms whose posterior mean has collapsed to (near) zero."""
        return [a for a, v in self.weights().items() if v <= threshold]

    # -- persistence -------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "arms": self.arms, "floor": self.floor, "prior": self._prior,
            "s": self._s, "f": self._f, "pulls": self._pulls, "wins": self._wins,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThompsonAllocator":
        obj = cls(data.get("arms") or ["ga"], floor=data.get("floor", DEFAULT_FLOOR))
        obj._prior = tuple(data.get("prior", (1.0, 1.0)))
        obj._s = dict(data.get("s") or obj._s)
        obj._f = dict(data.get("f") or obj._f)
        obj._pulls = dict(data.get("pulls") or obj._pulls)
        obj._wins = dict(data.get("wins") or obj._wins)
        for a in obj._s:
            if a not in obj.arms:
                obj.arms.append(a)
        return obj

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)

    @classmethod
    def load(cls, path: str) -> "ThompsonAllocator":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))
