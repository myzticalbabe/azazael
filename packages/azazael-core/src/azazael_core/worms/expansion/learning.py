# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: LEARNING (5 worms)
RLTrainLoop, ModelVersioner, DataPipelineWorm, ABTestRunner, FeatureEngineer
"""

import os
import sys
import json
import time
import hashlib
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ── Worm Registry Import ─────────────────────────────────────────────
try:
    from azazael_core.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls

# ── Python 3.14t Free-Threading Awareness ────────────────────────────
try:
    from azazael_core.freethreading import is_free_threaded, FreeThreadPool, ThreadSafeDict, ThreadSafeList
    _FREETHREAD = True
except ImportError:
    _FREETHREAD = False
    FreeThreadPool = None
    ThreadSafeDict = dict
    ThreadSafeList = list
    def is_free_threaded() -> bool:
        import sysconfig
        try:
            return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
        except Exception:
            return False


@register_worm(category="learning", priority=6, cooldown_seconds=120.0,
    description="RL train loop — reinforcement learning training loop with environment stepping")
class RLTrainLoop:
    """Reinforcement learning training loop with environment stepping."""

    VERSION = "1.0.0"

    def __init__(self):
        self._episodes: List[Dict] = []
        self._q_table: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        self._lock = threading.Lock()

    def train_episode(self, env, agent, max_steps: int = 1000) -> Dict[str, Any]:
        """Run a single training episode."""
        state = getattr(env, "reset", lambda: 0)()
        total_reward = 0.0
        steps = 0
        for _ in range(max_steps):
            action = getattr(agent, "act", lambda s: 0)(state)
            try:
                next_state, reward, done, *_ = getattr(env, "step", lambda a: (0, 0, True, {}))(action)
            except Exception:
                break
            total_reward += reward
            state = next_state
            steps += 1
            if done:
                break
        episode = {"steps": steps, "total_reward": total_reward, "timestamp": time.time()}
        with self._lock:
            self._episodes.append(episode)
        return episode

    def get_training_stats(self) -> Dict[str, Any]:
        with self._lock:
            if not self._episodes:
                return {"episodes": 0}
            rewards = [e["total_reward"] for e in self._episodes]
            return {"episodes": len(rewards), "avg_reward": round(sum(rewards) / len(rewards), 2),
                    "max_reward": max(rewards), "min_reward": min(rewards)}


@register_worm(category="learning", priority=5, cooldown_seconds=60.0,
    description="Model versioner — track ML model versions with metadata and performance comparison")
class ModelVersioner:
    """Tracks ML model versions with metadata."""

    VERSION = "1.0.0"

    def __init__(self):
        self._models: Dict[str, List[Dict]] = {}
        self._lock = threading.Lock()

    def register_model(self, name: str, version: str, metrics: Dict[str, float], metadata: Dict = None) -> Dict:
        entry = {"name": name, "version": version, "metrics": metrics, "metadata": metadata or {},
                 "registered_at": datetime.now().isoformat()}
        with self._lock:
            if name not in self._models:
                self._models[name] = []
            self._models[name].append(entry)
        return entry

    def compare_versions(self, name: str, v1: str, v2: str) -> Dict[str, Any]:
        """Compare metrics between two model versions."""
        versions = self._models.get(name, [])
        m1 = next((m for m in versions if m["version"] == v1), None)
        m2 = next((m for m in versions if m["version"] == v2), None)
        if not m1 or not m2:
            return {"error": "Version not found"}
        comparison = {}
        for k in set(list(m1["metrics"]) + list(m2["metrics"])):
            comparison[k] = {"v1": m1["metrics"].get(k), "v2": m2["metrics"].get(k),
                            "delta": round(m2["metrics"].get(k, 0) - m1["metrics"].get(k, 0), 4)}
        return {"model": name, "v1": v1, "v2": v2, "comparison": comparison}


@register_worm(category="learning", priority=5, cooldown_seconds=90.0,
    description="Data pipeline worm — ETL preprocessing with caching, batching, and validation")
class DataPipelineWorm:
    """ETL data preprocessing pipeline with caching and batching."""

    VERSION = "1.0.0"

    def __init__(self):
        self._cache: Dict[str, Any] = ThreadSafeDict() if ThreadSafeDict != dict else {}
        self._lock = threading.Lock()

    def extract(self, source: str, fmt: str = "json") -> Any:
        """Extract data from a source."""
        cache_key = f"extract:{source}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        path = Path(source)
        if not path.exists():
            return None
        if fmt == "json":
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = path.read_text(encoding="utf-8")
        self._cache[cache_key] = data
        return data

    def transform(self, data: Any, transformations: List[Callable]) -> Any:
        """Apply a chain of transformations."""
        result = data
        for tf in transformations:
            result = tf(result)
        return result

    def load(self, data: Any, target: str, fmt: str = "json"):
        """Load transformed data to target."""
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        else:
            path.write_text(str(data), encoding="utf-8")


@register_worm(category="learning", priority=4, cooldown_seconds=120.0,
    description="A/B test runner — split-test framework with statistical significance")
class ABTestRunner:
    """A/B test framework with basic statistical analysis."""

    VERSION = "1.0.0"

    def __init__(self):
        self._experiments: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def create_experiment(self, name: str, variants: List[str]):
        with self._lock:
            self._experiments[name] = {v: {"impressions": 0, "conversions": 0} for v in variants}

    def track(self, experiment: str, variant: str, converted: bool):
        with self._lock:
            exp = self._experiments.get(experiment, {})
            if variant in exp:
                exp[variant]["impressions"] += 1
                if converted:
                    exp[variant]["conversions"] += 1

    def get_results(self, experiment: str) -> Dict[str, Any]:
        with self._lock:
            exp = self._experiments.get(experiment, {})
        results = {}
        for var, metrics in exp.items():
            rate = metrics["conversions"] / max(metrics["impressions"], 1)
            results[var] = {"conversion_rate": round(rate, 4), **metrics}
        return {"experiment": experiment, "variants": results}


@register_worm(category="learning", priority=5, cooldown_seconds=45.0,
    description="Feature engineer — feature extraction, normalization, one-hot encoding, missing-value imputation")
class FeatureEngineer:
    """Feature engineering pipeline for ML preprocessing."""

    VERSION = "1.0.0"

    def __init__(self):
        self._feature_cache: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def normalize(self, values: List[float]) -> List[float]:
        """Min-max normalization to [0, 1]."""
        if not values:
            return []
        mn, mx = min(values), max(values)
        if mn == mx:
            return [0.5] * len(values)
        return [(v - mn) / (mx - mn) for v in values]

    def one_hot_encode(self, categories: List[str], known_categories: Optional[List[str]] = None) -> Dict[str, List[int]]:
        """One-hot encode categorical variables."""
        cats = known_categories or sorted(set(categories))
        cat_to_idx = {c: i for i, c in enumerate(cats)}
        encoded = [[0] * len(cats) for _ in categories]
        for i, cat in enumerate(categories):
            if cat in cat_to_idx:
                encoded[i][cat_to_idx[cat]] = 1
        return {"categories": cats, "encoded": encoded}

    def impute_missing(self, values: List[Optional[float]], strategy: str = "mean") -> List[float]:
        """Impute missing (None) values."""
        valid = [v for v in values if v is not None]
        if not valid:
            return [0.0] * len(values)
        fill = sum(valid) / len(valid) if strategy == "mean" else sorted(valid)[len(valid) // 2]
        return [v if v is not None else fill for v in values]
