# coding: utf-8
"""
NEURAL MESH — Category: FEDERATED (3 worms)
Distributed learning: Bare primary, Win/WSL2 workers, Kali reward.

FederatedAggregatorWorm, NASMeshSearcherWorm, RewardShaperMeshWorm
"""

import threading
from datetime import datetime
from typing import Any
from collections import defaultdict

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls


@register_worm(category="federated", priority=7, cooldown_seconds=180.0,
    description="FedAvg over SB3Agent/GRPOTrainer policies; Ray backend")
class FederatedAggregatorWorm:
    """Federated averaging aggregator."""

    VERSION = "1.0.0"

    def __init__(self):
        self._clients: dict[str, dict] = {}
        self._rounds = 0
        self._lock = threading.Lock()

    def submit(self, env: str, weights: list[float], samples: int) -> dict[str, Any]:
        with self._lock:
            self._clients[env] = {"weights": list(weights), "samples": samples,
                                  "at": datetime.now().isoformat()}
            return {"success": True, "env": env, "clients": len(self._clients)}

    def aggregate(self) -> dict[str, Any]:
        with self._lock:
            if not self._clients:
                return {"success": True, "aggregated": False, "reason": "no_clients"}
            total = sum(c["samples"] for c in self._clients.values()) or 1
            dim = len(next(iter(self._clients.values()))["weights"])
            avg = [0.0] * dim
            for c in self._clients.values():
                w = c["samples"] / total
                for i, v in enumerate(c["weights"]):
                    avg[i] += v * w
            self._rounds += 1
            self._clients.clear()
            return {"success": True, "aggregated": True, "rounds": self._rounds,
                    "dim": dim, "avg_head": [round(v, 4) for v in avg[:4]]}

    def execute(self) -> dict[str, Any]:
        r = self.aggregate()
        if not r.get("aggregated"):
            with self._lock:
                return {"success": True, "method": "execute",
                        "result": {"rounds": self._rounds,
                                   "waiting_clients": len(self._clients)}}
        return {"success": True, "method": "execute", "result": r}


@register_worm(category="federated", priority=6, cooldown_seconds=300.0,
    description="Evolutionary NAS (EvolutionEngine/MAPElites/SepCMAES) distributed across envs")
class NASMeshSearcherWorm:
    """Distributed neural architecture search coordinator."""

    VERSION = "1.0.0"

    def __init__(self):
        self._proposals: list = []
        self._evaluated = 0
        self._best: dict | None = None
        self._lock = threading.Lock()

    def propose(self, env: str, arch: dict, reward: float = 0.0) -> dict[str, Any]:
        with self._lock:
            self._proposals.append({"env": env, "arch": arch, "reward": reward})
            if self._best is None or reward > self._best.get("reward", -1):
                self._best = {"env": env, "arch": arch, "reward": reward}
            return {"success": True, "proposals": len(self._proposals),
                    "best_reward": self._best["reward"]}

    def evaluate_batch(self) -> dict[str, Any]:
        with self._lock:
            n = len(self._proposals)
            self._evaluated += n
            self._proposals.clear()
            return {"success": True, "evaluated": n,
                    "total_evaluated": self._evaluated, "best": self._best}

    def execute(self) -> dict[str, Any]:
        with self._lock:
            return {"success": True, "method": "execute",
                    "result": {"pending": len(self._proposals),
                               "evaluated": self._evaluated, "best": self._best}}


@register_worm(category="federated", priority=6, cooldown_seconds=60.0,
    description="6-provider inference reward during training; DLQ on fail")
class RewardShaperMeshWorm:
    """Multi-provider reward shaper."""

    VERSION = "1.0.0"
    PROVIDERS = ("groq", "openrouter", "nim", "lmstudio", "llamaserver", "ollama")

    def __init__(self):
        self._scores: dict[str, list] = defaultdict(list)
        self._dlq: list = []
        self._lock = threading.Lock()

    def score(self, provider: str, reward: float, ok: bool = True) -> dict[str, Any]:
        with self._lock:
            if not ok:
                self._dlq.append({"provider": provider, "at": datetime.now().isoformat()})
                return {"success": True, "provider": provider, "dlq": True,
                        "dlq_depth": len(self._dlq)}
            self._scores[provider].append(reward)
            hist = self._scores[provider][-100:]
            avg = round(sum(hist) / len(hist), 4)
            return {"success": True, "provider": provider, "avg": avg,
                    "samples": len(hist)}

    def weights(self) -> dict:
        with self._lock:
            avgs = {p: (sum(v[-50:]) / len(v[-50:]) if v else 0.0)
                    for p, v in self._scores.items()}
            total = sum(max(0.0, a) for a in avgs.values()) or 1.0
            return {"weights": {p: round(max(0.0, a) / total, 3) for p, a in avgs.items()},
                    "dlq_depth": len(self._dlq)}

    _REWARD_MODEL = None  # lazy-loaded task5 logistic

    @classmethod
    def _load_reward_model(cls) -> dict | None:
        if cls._REWARD_MODEL is not None:
            return cls._REWARD_MODEL
        try:
            import json as _json
            cls._REWARD_MODEL = _json.load(
                open("G:/source-of-truth/azazael_models/reward_model.json", encoding="utf-8"))
        except Exception:
            cls._REWARD_MODEL = {}
        return cls._REWARD_MODEL

    def local_score(self, rtt_ms: float = 50.0, fail_rate: float = 0.0,
                    size_kb: float = 100.0) -> dict[str, Any]:
        """Offline reward P(prefer | rtt, fail_rate, size) from task5 model.
        Falls back to the rtt/fail heuristic when the model file is missing."""
        import math as _math
        m = self._load_reward_model() or {}
        x = [min(2.0, rtt_ms / 2000.0), max(0.0, min(1.0, fail_rate)),
             min(1.0, size_kb / 5000.0)]
        if m.get("coef"):
            z = sum(c * v for c, v in zip(m["coef"], x)) + (m.get("intercept") or [0.0])[0]
            p = 1.0 / (1.0 + _math.exp(-z))
            src = "reward_model.json"
        else:
            p = 1.0 if (rtt_ms < 300 and fail_rate < 0.3) else 0.0
            src = "heuristic"
        return {"success": True, "reward": round(p, 4), "src": src,
                "features": {"rtt_ms": rtt_ms, "fail_rate": fail_rate, "size_kb": size_kb}}

    def execute(self) -> dict[str, Any]:
        return {"success": True, "method": "execute", "result": self.weights()}
