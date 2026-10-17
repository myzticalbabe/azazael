"""Concept 2: Process-weighted hybrid rewards.

Implements hybrid reward computation that combines multiple signal sources
with process-aware weighting, enabling graceful degradation under load
and selective tool engagement based on confidence thresholds.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class RewardSource(Enum):
    """Sources of reward signal for hybrid computation."""

    ENVIRONMENT = "environment"
    USER_FEEDBACK = "user_feedback"
    TOOL_OUTPUT = "tool_output"
    PREDICTIVE = "predictive"


@dataclass
class RewardConfig:
    """Configuration for hybrid reward weighting."""

    source_weights: Dict[RewardSource, float]
    min_confidence: float = 0.3
    max_confidence: float = 0.95
    decay_rate: float = 0.97


class HybridRewardComputer:
    """Computes hybrid rewards from multiple sources with process weighting."""

    def __init__(self, config: RewardConfig):
        self.config = config
        self._source_total: Dict[RewardSource, float] = {
            src: 0.0 for src in RewardSource
        }
        self._source_count: Dict[RewardSource, int] = {
            src: 0 for src in RewardSource
        }
        self._step = 0

    def update(self, source: RewardSource, reward: float, step: Optional[int] = None) -> None:
        """Update accumulated reward for a source.

        Args:
            source: The reward source enum value.
            reward: The reward value from that source.
            step: Optional step number for decay adjustment.
        """
        if step is not None:
            self._step = step
        decay = self.config.decay_rate ** max(0, self._step - 1)
        adj = reward * decay
        self._source_total[source] += adj
        self._source_count[source] += 1

    def compute_hybrid(self, step: Optional[int] = None) -> float:
        """Compute the aggregated hybrid reward across all sources.

        Returns a weighted, confidence-adjusted aggregate in [0, 1].
        """
        if step is not None:
            self._step = step

        total_weight = 0.0
        weighted_sum = 0.0

        for src in RewardSource:
            if self._source_count[src] == 0:
                continue
            w = self.config.source_weights.get(src, 0.0)
            if w <= 0:
                continue
            avg = self._source_total[src] / max(1, self._source_count[src])
            # Confidence scaling: newer observations get higher weight
            conf_factor = min(
                self.config.max_confidence,
                self.config.min_confidence + (1.0 - self.config.min_confidence)
                * (self._source_count[src] / max(1, (self._step or 1))),
            )
            weighted_sum += w * avg * conf_factor
            total_weight += w * conf_factor

        if total_weight == 0:
            return 0.0
        return min(1.0, max(0.0, weighted_sum / total_weight))

    def reset(self) -> None:
        """Reset all accumulated rewards."""
        for src in RewardSource:
            self._source_total[src] = 0.0
            self._source_count[src] = 0
        self._step = 0
