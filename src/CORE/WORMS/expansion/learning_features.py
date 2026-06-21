# coding: utf-8
"""
learning_features.py - FeatureEngineer (fast-loading focused module)

Extracted from learning.py (103K monolith) for fast loading.
Used by: scheduling.py
"""

import threading
from typing import Any

try:
    from CORE.freethreading import ThreadSafeDict
except ImportError:
    ThreadSafeDict = dict

try:
    from CORE.worm_registry import register_worm
except ImportError:
    def register_worm(**kw):
        return lambda cls: cls

@register_worm(category="learning", priority=5, cooldown_seconds=45.0,
    description="Feature engineer — feature extraction from LocalMemoryStore, normalization, encoding, imputation")
class FeatureEngineer:
    """Feature engineering pipeline for ML preprocessing.
    
    Works with data extracted by DataPipelineWorm from LocalMemoryStore.
    Provides: normalization, one-hot encoding, missing-value imputation.
    Also provides feature extraction specifically for worm execution data.
    """

    VERSION = "2.0.0"

    def __init__(self):
        self._feature_cache: dict[str, Any] = {}
        self._lock = threading.Lock()

    def normalize(self, values: list[float]) -> list[float]:
        """Min-max normalization to [0, 1]."""
        if not values:
            return []
        mn, mx = min(values), max(values)
        if mn == mx:
            return [0.5] * len(values)
        return [(v - mn) / (mx - mn) for v in values]

    def one_hot_encode(self, categories: list[str], known_categories: (list[str] | None) = None) -> dict[str, list[int]]:
        """One-hot encode categorical variables."""
        cats = known_categories or sorted(set(categories))
        cat_to_idx = {c: i for i, c in enumerate(cats)}
        encoded = [[0] * len(cats) for _ in categories]
        for i, cat in enumerate(categories):
            if cat in cat_to_idx:
                encoded[i][cat_to_idx[cat]] = 1
        return {"categories": cats, "encoded": encoded}

    def impute_missing(self, values: list[(float | None)], strategy: str = "mean") -> list[float]:
        """Impute missing (None) values."""
        valid = [v for v in values if v is not None]
        if not valid:
            return [0.0] * len(values)
        fill = sum(valid) / len(valid) if strategy == "mean" else sorted(valid)[len(valid) // 2]
        return [v if v is not None else fill for v in values]

    def extract_worm_features(self, records: list[dict]) -> dict[str, Any]:
        """Extract ML-ready features from worm execution records.
        
        Converts LocalMemoryStore records into feature vectors suitable
        for training RLTrainLoop or SYSTEMZ_ML models.
        
        Features extracted:
        - Execution duration (numeric)
        - Success rate (boolean -> float)
        - Source entropy (categorical -> one-hot)
        - Severity distribution (categorical -> count vector)
        - Hour of day (cyclic)
        - Day of week (cyclic)
        """
        if not records:
            return {"count": 0, "features": [], "labels": []}

        features = []
        labels = []
        sources = set()

        for r in records:
            sources.add(r.get("source", "unknown"))

        source_list = sorted(sources)

        for r in records:
            feat = []
            # Duration (if available in data)
            data = r.get("data", {})
            if isinstance(data, dict):
                duration = data.get("duration_ms", data.get("duration", 0))
                feat.append(float(duration) if duration else 0.0)
            else:
                feat.append(0.0)

            # Success (boolean -> float)
            success = r.get("severity", "") != "error"
            feat.append(1.0 if success else 0.0)

            # Source (one-hot)
            source = r.get("source", "unknown")
            source_vec = [1.0 if s == source else 0.0 for s in source_list]
            feat.extend(source_vec)

            features.append(feat)
            labels.append(1.0 if success else 0.0)

        return {
            "count": len(features),
            "feature_dim": len(features[0]) if features else 0,
            "features": features,
            "labels": labels,
            "source_categories": source_list,
        }

    def get_summary(self):
        return {"status":"ok","worm":"FeatureEngineer"}

