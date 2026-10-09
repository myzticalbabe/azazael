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

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)

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
    # Generic aliases (2026-09-14): callers passing plain success/fail used
    # to fall through to the (False, 1.0) default — success recorded as
    # failure with full weight. Never again.
    "success": (True, 1.0),
    "fail": (False, 1.0),
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
                 rng: Optional[random.Random] = None,
                 explore: float = 0.0):
        self.arms: List[str] = list(arms)
        if not self.arms:
            raise ValueError("ThompsonAllocator needs at least one arm")
        self.floor = max(0.0, float(floor))
        self._rng = rng or random.Random()
        self._prior = (float(alpha), float(beta))
        # Epsilon exploration (2026-09-28): with probability `explore`, pick
        # uniformly instead of drawing posteriors, so a collapsed arm keeps
        # recovering pulls. Counted in _explore_hits; survives round-trips.
        self.explore = min(1.0, max(0.0, float(explore)))
        self._explore_hits = 0
        # success/failure pseudo-counts, seeded with the prior
        self._s: Dict[str, float] = {a: float(alpha) for a in self.arms}
        self._f: Dict[str, float] = {a: float(beta) for a in self.arms}
        self._pulls: Dict[str, int] = {a: 0 for a in self.arms}
        self._wins: Dict[str, int] = {a: 0 for a in self.arms}

    # -- allocation --------------------------------------------------------
    def select(self, k: int = 1):
        """Alias for choose() — backward-compat for thompson_env.py."""
        return self.choose(k)[0] if k == 1 else self.choose(k)

    def choose(self, k: int = 1) -> List[str]:
        """Top-k arms by posterior draw (Thompson sampling).

        With probability `explore`, one slot is filled by a uniform pick
        instead (epsilon exploration against posterior collapse).
        """
        if k <= 0:
            return []
        k = min(k, len(self.arms))
        out: List[str] = []
        if self.explore > 0.0 and self._rng.random() < self.explore:
            out.append(self._rng.choice(self.arms))
            self._explore_hits += 1
        draws = []
        for a in self.arms:
            draws.append((self._rng.betavariate(self._s[a], self._f[a]), a))
        draws.sort(reverse=True)
        for _, a in draws:
            if len(out) >= k:
                break
            if a not in out:
                out.append(a)
        return out[:k]

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
    def update(self, arm: str, success=True, weight: float = 1.0,
               decays: Optional[Dict[str, float]] = None) -> None:
        """Record an outcome for `arm`.

        `weight` lets a strong success count for more than a marginal one
        (e.g. holdout-passed counts 1.0, beat-baseline counts 0.2). `decays`
        optionally multiplies every arm's pseudo-counts first, so old evidence
        fades in a non-stationary regime.

        Backward-compat: thompson_env.py calls update(arm, reward_float).
        If `success` is a float, treat as weight w/ success=(w>0.5).
        If reward_for_outcome tuple (ok, w) passed as success, unwrap.
        """
        # unwrap (ok, w) tuple
        if isinstance(success, tuple) and len(success) == 2:
            success, weight = bool(success[0]), float(success[1])
        elif isinstance(success, (int, float)) and not isinstance(success, bool):
            w = float(success)
            # FG-lite optimism: never-promoted arms get +0.1 exploration bonus
            # via weight floor handled in choose_with_bonus; here map float->bool
            weight, success = (w if w > 0 else 1.0), (w > 0.5)
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
        out["_meta"] = {"explore": self.explore,
                        "explore_hits": self._explore_hits}
        return out

    def starved(self, threshold: float = 1e-9) -> List[str]:
        """Arms whose posterior mean has collapsed to (near) zero."""
        return [a for a, v in self.weights().items() if v <= threshold]

    # -- persistence -------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "arms": self.arms, "floor": self.floor, "prior": self._prior,
            "s": self._s, "f": self._f, "pulls": self._pulls, "wins": self._wins,
            "explore": self.explore, "explore_hits": self._explore_hits,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThompsonAllocator":
        obj = cls(data.get("arms") or ["ga"], floor=data.get("floor", DEFAULT_FLOOR),
                  explore=data.get("explore", 0.0))
        obj._prior = tuple(data.get("prior", (1.0, 1.0)))
        obj._s = dict(data.get("s") or obj._s)
        obj._f = dict(data.get("f") or obj._f)
        obj._pulls = dict(data.get("pulls") or obj._pulls)
        obj._wins = dict(data.get("wins") or obj._wins)
        try:
            obj._explore_hits = int(data.get("explore_hits", 0) or 0)
        except (TypeError, ValueError):
            note_failure("allocation:L250", None)
            obj._explore_hits = 0
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

    # -- FG-lite + propensity (2026-09-15 P0) --------------------------------
    def choose_with_bonus(self, k: int = 1, fg_lambda: float = 0.1) -> List[str]:
        """Thompson draw + Feel-Good optimism for never-promoted arms."""
        base = self.choose(k)
        # if top arm has <2 pulls, mix in least-pulled arm for exploration
        if self._pulls and min(self._pulls.values()) < 2 and k == 1:
            least = min(self._pulls, key=lambda a: self._pulls[a])
            if least not in base and self._rng.random() < fg_lambda * 5:
                return [least]
        return base


class LinUCBAllocator:
    """Contextual LinUCB (2026-09-15 P0) — auditable alternative to Thompson.

    E[r|x] = x^T theta_a + alpha * sqrt(x^T A_a^-1 x). Stdlib-only.
    Use for routing with features [ms_ema, fail_rate, load, arm_onehot].
    """

    def __init__(self, arms, dim: int = 4, alpha: float = 1.0):
        self.arms = list(arms)
        self.dim = dim
        self.alpha = alpha
        import copy
        self._A = {a: [[1.0 if i == j else 0.0 for j in range(dim)]
                       for i in range(dim)] for a in self.arms}
        self._b = {a: [0.0] * dim for a in self.arms}

    def _solve(self, A, b):
        # Gauss-Jordan for tiny dim (<=8); no numpy needed
        n = len(A)
        M = [row[:] + [bb] for row, bb in zip(A, b)]
        for c in range(n):
            piv = max(range(c, n), key=lambda r: abs(M[r][c])) if n else c
            M[c], M[piv] = M[piv], M[c]
            d = M[c][c] or 1e-9
            M[c] = [v / d for v in M[c]]
            for r in range(n):
                if r != c:
                    f = M[r][c]
                    M[r] = [rv - f * cv for rv, cv in zip(M[r], M[c])]
        return [row[-1] for row in M]

    def choose(self, x, k: int = 1):
        scored = []
        for a in self.arms:
            theta = self._solve(self._A[a], self._b[a])
            mean = sum(t * xi for t, xi in zip(theta, x))
            # var = x^T A^-1 x via solve A y = x
            y = self._solve(self._A[a], list(x))
            var = max(0.0, sum(xi * yi for xi, yi in zip(x, y)))
            scored.append((mean + self.alpha * (var ** 0.5), a))
        scored.sort(reverse=True)
        return [a for _, a in scored[:k]]

    def update(self, arm: str, x, reward: float):
        A, b = self._A[arm], self._b[arm]
        for i in range(self.dim):
            for j in range(self.dim):
                A[i][j] += x[i] * x[j]
            b[i] += x[i] * reward


class SuccessiveHalvingPruner:
    """BOHB-lite fidelity pruner (2026-09-15 P0): 10->20->80 eps, keep 1/3."""

    def __init__(self, rungs=(10, 20, 80), eta: int = 3):
        self.rungs = list(rungs)
        self.eta = eta

    def promote(self, scored):
        """scored: [(id, score)] -> ids promoted to next rung (top 1/eta)."""
        scored = sorted(scored, key=lambda t: t[1], reverse=True)
        n = max(1, len(scored) // self.eta)
        return [i for i, _ in scored[:n]]


class MCTSPlanner:
    """P1-3 ToolTree-lite MCTS over PROTEUS arms (pre-eval=TPE proxy, post=holdout).

    Node = arm sequence; UCT select, expand 1 child, rollout=allocator draw,
    backprop mean value. Stdlib-only, depth<=2 for CPU box.
    """

    def __init__(self, arms, alloc=None, c: float = 1.4, depth: int = 2):
        self.arms = list(arms)
        self.alloc = alloc
        self.c = c
        self.depth = depth
        self._N = {}
        self._Q = {}

    def _uct(self, seq):
        import math
        n_p = sum(self._N.get(seq + (a,), 0) for a in self.arms) or 1
        best, best_v = None, -1e18
        for a in self.arms:
            k = seq + (a,)
            q = self._Q.get(k, 0.0)
            n = self._N.get(k, 0)
            v = q + self.c * math.sqrt(math.log(n_p + 1) / (n + 1))
            if v > best_v:
                best, best_v = a, v
        return best

    def plan(self, pre_score, post_eval, iters: int = 20):
        """pre_score(seq)->float proxy, post_eval(seq)->float verify."""
        best, best_v = (), -1e18
        for _ in range(iters):
            seq, d = (), 0
            while d < self.depth:
                a = self._uct(seq)
                # pre-prune: skip arms scoring < 0.3 proxy
                if pre_score(seq + (a,)) < 0.3 and d == 0:
                    break
                seq = seq + (a,)
                d += 1
            v = post_eval(seq) if seq else 0.0
            k = seq
            self._N[k] = self._N.get(k, 0) + 1
            self._Q[k] = self._Q.get(k, 0.0) + (v - self._Q.get(k, 0.0)) / self._N[k]
            if v > best_v:
                best, best_v = seq, v
        return {"best_seq": list(best), "value": best_v,
                "visits": dict(self._N)}
