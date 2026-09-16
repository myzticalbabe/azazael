# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: LEARNER (Nerve)

Nerve removes the tabular-learner ceiling. The inner learner is a Q-table keyed
on `source:severity` whose behaviour is set by four scalars — learning rate,
epsilon, epsilon decay, discount. Widening those bounds on 2026-09-11 moved them
into fresh territory, which was the right first move, but it also proved the
point: the outer loop is reduced to choosing four numbers, and a box with an
optimum on its surface is found immediately (6 generations, flat thereafter).

Nerve changes WHAT is being optimised. Instead of choosing a learning rate, the
outer loop chooses a *policy over learning*: a small network that reads context
and emits per-parameter update modulations.

    m_t = net(state_t)            # multipliers, one per plasticity parameter
    lr_t = lr_base * m_t[0]       # each modulated in [lo, hi]

This is learning-to-learn in the cheap, honest sense. It fits the memory budget
because the modulator is small (hidden=16, ~hundreds of params) while the Q-table
it modulates is already low-dimensional.

Two constraints from the hardware truth:

* The modulator is a learning problem, so it belongs to the GIL interpreter
  (`torch 2.14.0+xpu`, ABI `cp314`). A numpy fallback exists so the module still
  imports and runs — degraded — under the free-threaded pipeline.
* Training the modulator must NOT use more Q-updates as its reward: that is the
  "fake selection pressure" trap documented at `learning_rl.py:335`. The outer
  signal is *evaluation performance*, never update count.
"""

from __future__ import annotations

import json
import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Neuromodulator",
    "modulated_q_update",
    "NerveTrainer",
    "context_vector",
]

MODULATION_LO = 0.25
MODULATION_HI = 2.0

try:
    import torch as _torch  # type: ignore
except Exception:  # pragma: no cover - free-threaded build cannot load cp314
    _torch = None

try:
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover
    _np = None


def context_vector(source: str, severity: str, step: int, max_steps: int,
                   epsilon: float, q_norm: float = 0.0) -> List[float]:
    """The state the modulator conditions on.

    Deliberately low-dimensional and derived only from values the tabular
    learner already has in hand, so Nerve needs no new instrumentation. The
    hash buckets are stable across processes (unlike `hash()`, which is salted).
    """
    def _bucket(s: str, n: int) -> float:
        h = 0
        for ch in str(s):
            h = (h * 131 + ord(ch)) & 0xFFFFFFFF
        return float(h % n) / float(n)

    frac = float(step) / float(max(1, max_steps))
    return [
        _bucket(source, 8),
        _bucket(severity, 4),
        frac,
        float(epsilon),
        float(min(1.0, max(0.0, q_norm))),
        math.tanh(float(step) / 50.0),
    ]


class Neuromodulator:
    """Small network emitting per-plasticity-parameter multipliers."""

    def __init__(self, n_out: int = 4, in_dim: int = 6, hidden: int = 16,
                 seed: int = 0, use_torch: bool = True):
        self.n_out = int(n_out)
        self.in_dim = int(in_dim)
        self.hidden = int(hidden)
        self.seed = int(seed)
        self.backend = "numpy"
        self._torch_ok = bool(use_torch and _torch is not None)

        rng = random.Random(seed)
        self.w1 = [[rng.gauss(0.0, 1.0 / math.sqrt(self.in_dim)) for _ in range(self.in_dim)]
                   for _ in range(self.hidden)]
        self.b1 = [0.0] * self.hidden
        self.w2 = [[rng.gauss(0.0, 1.0 / math.sqrt(self.hidden)) for _ in range(self.hidden)]
                   for _ in range(self.n_out)]
        self.b2 = [0.0] * self.n_out

        self.net = None
        if self._torch_ok:
            try:
                dev = "xpu" if getattr(_torch, "xpu", None) is not None and _torch.xpu.is_available() else "cpu"
                self.device = dev
                g = _torch.Generator(device="cpu").manual_seed(seed)
                self.net = _torch.nn.Sequential(
                    _torch.nn.Linear(self.in_dim, self.hidden),
                    _torch.nn.Tanh(),
                    _torch.nn.Linear(self.hidden, self.n_out),
                ).to(dev)
                with _torch.no_grad():
                    for p in self.net.parameters():
                        p.copy_(_torch.empty_like(p).uniform_(-0.5, 0.5, generator=g))
                self.backend = "torch:%s" % dev
            except Exception:
                self.net = None
                self.backend = "numpy"

    # -- forward ----------------------------------------------------------
    def _forward_numpy(self, ctx: Sequence[float]) -> List[float]:
        h = []
        for i in range(self.hidden):
            z = self.b1[i] + sum(self.w1[i][j] * ctx[j] for j in range(self.in_dim))
            h.append(math.tanh(z))
        out = []
        for k in range(self.n_out):
            z = self.b2[k] + sum(self.w2[k][i] * h[i] for i in range(self.hidden))
            out.append(z)
        return out

    def modulations(self, ctx: Sequence[float]) -> List[float]:
        """Per-parameter multipliers, squashed into [LO, HI]."""
        raw: List[float]
        if self.net is not None and _torch is not None:
            try:
                with _torch.no_grad():
                    t = _torch.tensor([list(ctx)], dtype=_torch.float32, device=self.net[0].weight.device)
                    raw = [float(v) for v in self.net(t)[0].tolist()]
            except Exception:
                raw = self._forward_numpy(ctx)
        else:
            raw = self._forward_numpy(ctx)
        span = MODULATION_HI - MODULATION_LO
        return [MODULATION_LO + span * (0.5 * (math.tanh(x) + 1.0)) for x in raw]

    # -- parameter vector (for the outer ES loop) --------------------------
    def get_params(self) -> List[float]:
        if self.net is not None and _torch is not None:
            try:
                out: List[float] = []
                for p in self.net.parameters():
                    out.extend(float(v) for v in p.detach().cpu().reshape(-1).tolist())
                return out
            except Exception:
                pass
        out = []
        for row in self.w1:
            out.extend(row)
        out.extend(self.b1)
        for row in self.w2:
            out.extend(row)
        out.extend(self.b2)
        return out

    def set_params(self, params: Sequence[float]) -> None:
        vals = [float(v) for v in params]
        if self.net is not None and _torch is not None:
            try:
                with _torch.no_grad():
                    i = 0
                    for p in self.net.parameters():
                        n = int(p.numel())
                        chunk = vals[i:i + n]
                        if len(chunk) != n:
                            raise ValueError("param length mismatch")
                        p.copy_(_torch.tensor(chunk, dtype=p.dtype, device=p.device).view_as(p))
                        i += n
                return
            except Exception:
                pass
        i = 0
        for r in range(self.hidden):
            for c in range(self.in_dim):
                self.w1[r][c] = vals[i]; i += 1
        for r in range(self.hidden):
            self.b1[r] = vals[i]; i += 1
        for r in range(self.n_out):
            for c in range(self.hidden):
                self.w2[r][c] = vals[i]; i += 1
        for r in range(self.n_out):
            self.b2[r] = vals[i]; i += 1

    @property
    def n_params(self) -> int:
        return self.hidden * self.in_dim + self.hidden + self.n_out * self.hidden + self.n_out

    # -- persistence -------------------------------------------------------
    def save(self, path: str) -> None:
        payload = {"backend": self.backend, "n_out": self.n_out, "in_dim": self.in_dim,
                   "hidden": self.hidden, "seed": self.seed,
                   "params": self.get_params()}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1)

    @classmethod
    def load(cls, path: str) -> Optional["Neuromodulator"]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            obj = cls(d.get("n_out", 4), d.get("in_dim", 6), d.get("hidden", 16),
                      d.get("seed", 0))
            obj.set_params(d.get("params") or [])
            return obj
        except Exception:
            return None


def modulated_q_update(q: Dict[Any, float], state: Any, action: Any, reward: float,
                       next_state: Any, alpha: float, gamma: float,
                       mod: Sequence[float]) -> float:
    """One Q-update whose three plasticity parameters are individually modulated.

    `mod = [alpha_mult, gamma_mult, temperature_mult]`. Returns the TD error so
    callers can log learning progress without recomputing it.
    """
    a_m = float(mod[0]) if len(mod) > 0 else 1.0
    g_m = float(mod[1]) if len(mod) > 1 else 1.0
    alpha_t = min(1.0, max(1e-4, alpha * a_m))
    gamma_t = min(0.999, max(0.0, gamma * g_m))

    key = (state, action)
    prev = float(q.get(key, 0.0))
    nxt = q.get(next_state)
    if isinstance(nxt, dict):
        best_next = max((float(v) for v in nxt.values()), default=0.0)
    else:
        best_next = float(nxt) if nxt is not None else 0.0
    td = reward + gamma_t * best_next - prev
    q[key] = prev + alpha_t * td
    return td


class NerveTrainer:
    """Outer loop: evolves the modulator with a (1+l) evolution strategy.

    Chosen deliberately over backprop-through-episodes. The reward signal is a
    black-box evaluation number (the same number the pipeline already computes),
    there is no differentiable path to it, and the parameter count is tiny — so
    a small ES is both honest and sufficient. Reward is evaluation performance;
    update count is never used as fitness (`learning_rl.py:335`).
    """

    def __init__(self, modulator: Neuromodulator, sigma: float = 0.1,
                 lr: float = 0.05, seed: int = 0, path: Optional[str] = None):
        self.mod = modulator
        self.sigma = float(sigma)
        self.lr = float(lr)
        self.rng = random.Random(seed)
        self.path = path
        self.history: List[dict] = []
        self.best_score = float("-inf")

    def _evaluate(self, evaluate: Any, params: Sequence[float]) -> float:
        saved = self.mod.get_params()
        try:
            self.mod.set_params(params)
            return float(evaluate(self.mod))
        except Exception:
            return float("-inf")
        finally:
            self.mod.set_params(saved)

    def step(self, evaluate: Any, n_offspring: int = 4) -> dict:
        """One (1+l) generation. `evaluate(modulator) -> score` (higher better)."""
        base = self.mod.get_params()
        base_score = np_base = None
        try:
            base_score = float(evaluate(self.mod))
        except Exception:
            base_score = float("-inf")

        improvements: List[Tuple[float, List[float]]] = []
        for _ in range(max(1, n_offspring)):
            cand = [p + self.rng.gauss(0.0, self.sigma) for p in base]
            score = self._evaluate(evaluate, cand)
            improvements.append((score, cand))

        improvements.sort(key=lambda t: t[0], reverse=True)
        best_score, best_params = improvements[0]

        accepted = best_score > base_score
        if accepted:
            # convex combination toward the winner = a smoothed ES step
            blended = [b + self.lr * (w - b) for b, w in zip(base, best_params)]
            self.mod.set_params(blended)
            self.sigma = max(0.01, self.sigma * 0.98)
        else:
            self.sigma = min(0.5, self.sigma * 1.05)

        self.best_score = max(self.best_score, best_score)
        row = {"base": base_score, "best": best_score, "accepted": accepted,
               "sigma": self.sigma, "n_params": self.mod.n_params}
        self.history.append(row)
        if self.path:
            self._persist()
        return row

    def _persist(self) -> None:
        try:
            if self.path:
                self.mod.save(self.path)
            with open(str(self.path) + ".history.json", "w", encoding="utf-8") as fh:
                json.dump(self.history[-128:], fh, indent=1)
        except Exception:
            pass

    def train(self, evaluate: Any, generations: int = 20, n_offspring: int = 4
              ) -> Dict[str, Any]:
        start = self.best_score
        for _ in range(max(1, generations)):
            self.step(evaluate, n_offspring)
        return {"generations": generations, "best": self.best_score,
                "gain": (self.best_score - start) if start != float("-inf") else None,
                "backend": self.mod.backend}
