"""Critic-free policy optimization contracts used by the algorithm laboratory.

This module implements the mathematical update contracts needed to compare
REINFORCE, RLOO, REINFORCE++, Dr GRPO, DAPO, GSPO, and GDPO without claiming
that a name alone makes an algorithm production-ready. Callers must still
provide real rollouts, deterministic seeds, and qualification evidence.

Measurement-space note (forensic, 2026-10-06): each estimator's advantage
lives in its own space — raw returns (REINFORCE), leave-one-out deltas
(RLOO), batch z-scores (REINFORCE++), group z-scores (GRPO), centered
deltas (Dr GRPO), decoupled multi-stream z-scores (GDPO). The per-algorithm
``loss`` in run_policy_lab is therefore NOT comparable across estimators;
PolicyEvidence.normalization names the space so no consumer can silently
rank across it. Cross-space decisions (promotion, gating) must go through
an explicit common scale (see bounded_margin in expansion/exmachina.py).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp, isfinite, log, sqrt
from statistics import fmean, pstdev
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class PolicyEvidence:
    """One reproducible comparison result for a critic-free algorithm."""

    algorithm: str
    seed: int
    samples: int
    advantage_mean: float
    advantage_std: float
    loss: float
    accepted_groups: int
    skipped_groups: int
    normalization: str = "unknown"

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def _validate_rewards(rewards: Sequence[float]) -> list[float]:
    values = [float(value) for value in rewards]
    if not values or any(not isfinite(value) for value in values):
        raise ValueError("rewards must be a non-empty finite sequence")
    return values


def reinforce_advantages(rewards: Sequence[float]) -> list[float]:
    """REINFORCE returns-to-go with a zero baseline."""

    return _validate_rewards(rewards)


def rloo_advantages(rewards: Sequence[float]) -> list[float]:
    """RLOO subtracts every other sample's mean from each sample."""

    values = _validate_rewards(rewards)
    count = len(values)
    if count < 2:
        return [0.0]
    total = sum(values)
    return [value - (total - value) / (count - 1) for value in values]


def reinforce_plus_plus_advantages(
    rewards: Sequence[float],
    *,
    global_rewards: Sequence[float] | None = None,
    baseline: float | None = None,
) -> list[float]:
    """REINFORCE++ with global-batch normalization and optional baseline.

    Global normalization uses the complete supplied batch. When a learned
    baseline is supplied, rewards are centered by it before global scaling.
    """

    values = _validate_rewards(rewards)
    population = _validate_rewards(global_rewards or values)
    if baseline is None:
        centered_population = population
        centered = values
    else:
        center = float(baseline)
        if not isfinite(center):
            raise ValueError("baseline must be finite")
        centered_population = [value - center for value in population]
        centered = [value - center for value in values]
    scale = pstdev(centered_population)
    if scale <= 1e-12:
        return [0.0 for _ in centered]
    return [value / scale for value in centered]


def grpo_advantages(rewards: Sequence[float]) -> list[float]:
    """Standard GRPO local mean/std normalization."""

    values = _validate_rewards(rewards)
    scale = pstdev(values)
    if scale <= 1e-12:
        return [0.0 for _ in values]
    mean = fmean(values)
    return [(value - mean) / scale for value in values]


def dr_grpo_advantages(rewards: Sequence[float]) -> list[float]:
    """Dr GRPO local centering without std or response-length rescaling."""

    values = _validate_rewards(rewards)
    mean = fmean(values)
    return [value - mean for value in values]


def gdpo_advantages(streams: Mapping[str, Sequence[float]]) -> list[float]:
    """GDPO decoupled multi-reward normalization (ICML 2026, NVIDIA).

    Joint GRPO-style normalization over combined multi-reward rollouts
    collapses distinct reward combinations into identical advantages,
    destroying resolution. GDPO normalizes each reward stream
    INDEPENDENTLY (z-score within stream, zero-variance streams contribute
    0.0 rather than NaN) and combines per-sample by mean. Relative
    differences WITHIN each stream are preserved; no stream's scale can
    swamp another's.

    Args:
        streams: mapping of stream name -> per-sample rewards. All streams
            must cover the same samples in the same order with equal length.

    Returns:
        Per-sample combined advantages (mean of per-stream z-scores).
    """

    if not streams:
        raise ValueError("streams must be a non-empty mapping")
    names = list(streams)
    columns = [_validate_rewards(streams[name]) for name in names]
    width = len(columns[0])
    if any(len(column) != width for column in columns):
        raise ValueError("all streams must have equal length")
    norms: list[list[float]] = []
    for column in columns:
        scale = pstdev(column)
        if scale <= 1e-12:
            norms.append([0.0 for _ in column])
            continue
        mean = fmean(column)
        norms.append([(value - mean) / scale for value in column])
    return [fmean([norms[stream][index] for stream in range(len(names))])
            for index in range(width)]


@dataclass(frozen=True)
class TokenTrace:
    """Token log-probability deltas and validity mask for one rollout."""

    log_ratios: tuple[float, ...]
    mask: tuple[bool, ...] | None = None
    reward: float = 0.0
    group_rewards: tuple[float, ...] | None = None
    overlong: bool = False

    def valid_indices(self) -> tuple[int, ...]:
        if self.mask is None:
            return tuple(range(len(self.log_ratios)))
        if len(self.mask) != len(self.log_ratios):
            raise ValueError("mask and log_ratios must have equal length")
        return tuple(index for index, active in enumerate(self.mask) if active)


def _valid_log_ratios(trace: TokenTrace) -> list[float]:
    return [float(trace.log_ratios[index]) for index in trace.valid_indices()]


def token_policy_loss(
    trace: TokenTrace,
    advantage: float,
    *,
    clip_low: float = 0.2,
    clip_high: float = 0.28,
) -> float:
    """DAPO token-level clipped surrogate with an asymmetric clip range."""

    ratios = _valid_log_ratios(trace)
    if not ratios:
        return 0.0
    unclipped = [exp(value) for value in ratios]
    clipped = [min(clip_high, max(clip_low, value)) for value in unclipped]
    losses = [-min(value * advantage, clipped_value * advantage)
              for value, clipped_value in zip(unclipped, clipped)]
    return fmean(losses)


def sequence_policy_loss(
    trace: TokenTrace,
    advantage: float,
    *,
    clip_low: float = 0.2,
    clip_high: float = 0.28,
) -> float:
    """GSPO sequence-level geometric-mean ratio with asymmetric clipping."""

    ratios = _valid_log_ratios(trace)
    if not ratios:
        return 0.0
    sequence_ratio = exp(fmean(ratios))
    clipped_ratio = min(clip_high, max(clip_low, sequence_ratio))
    return -min(sequence_ratio * advantage, clipped_ratio * advantage)


def select_dapo_groups(
    groups: Iterable[TokenTrace],
    *,
    max_tokens: int,
    target_groups: int,
) -> tuple[list[TokenTrace], int]:
    """Dynamically retain informative, non-overlong groups within a token budget."""

    if max_tokens <= 0 or target_groups <= 0:
        return [], 0
    selected: list[TokenTrace] = []
    used = 0
    skipped = 0
    for trace in groups:
        valid = trace.valid_indices()
        if trace.overlong or not valid:
            skipped += 1
            continue
        group_rewards = _validate_rewards(
            trace.group_rewards if trace.group_rewards is not None
            else (trace.reward,))
        if len(group_rewards) < 2 or pstdev(group_rewards) <= 1e-12:
            skipped += 1
            continue
        cost = len(valid)
        if used + cost > max_tokens or len(selected) >= target_groups:
            skipped += 1
            continue
        selected.append(trace)
        used += cost
    return selected, skipped


def run_policy_lab(
    rewards_by_algorithm: dict[str, Sequence[float]],
    *,
    seed: int,
) -> list[PolicyEvidence]:
    """Run deterministic advantage contracts and return comparable evidence."""

    estimators = {
        "REINFORCE": (reinforce_advantages, "raw returns"),
        "RLOO": (rloo_advantages, "leave-one-out deltas"),
        "REINFORCE++": (reinforce_plus_plus_advantages, "batch z-scores"),
        "GRPO": (grpo_advantages, "group z-scores"),
        "DR_GRPO": (dr_grpo_advantages, "centered deltas"),
    }
    evidence: list[PolicyEvidence] = []
    for algorithm, rewards in rewards_by_algorithm.items():
        if algorithm not in estimators:
            raise ValueError(f"unsupported laboratory algorithm: {algorithm}")
        fn, space = estimators[algorithm]
        values = _validate_rewards(rewards)
        advantages = fn(values)
        loss = -fmean(advantage * value for advantage, value in zip(advantages, values))
        evidence.append(PolicyEvidence(
            algorithm=algorithm,
            seed=int(seed),
            samples=len(values),
            advantage_mean=fmean(advantages),
            advantage_std=pstdev(advantages),
            loss=float(loss),
            accepted_groups=1 if advantages else 0,
            skipped_groups=0 if advantages else 1,
            normalization=space,
        ))
    return evidence
