# coding: utf-8
"""redteam.py — reward red-team critic: predicts which high-reward
trajectories are hacks BEFORE they pay out.

Features are hack signatures, not outcomes: verbosity ratio, template
regurgitation (repetition), confidence/outcome mismatch history, and
score velocity spikes. A trajectory the task reward loves but the critic
flags gets its reward taxed: r' = r * (1 - hack_p). Stdlib-only.
"""
import math
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).
_SWALLOWED: List[str] = []

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        _SWALLOWED.append("%s:no-recorder" % where)


def featurize(traj: dict) -> list[float]:
    """traj: {tokens, distinct_tokens, template_match(0..1), conf,
    outcome_ok(0/1 or None), score_vel}. Returns fixed feature vector."""
    toks = max(1, int(traj.get("tokens", 1)))
    distinct = max(1, int(traj.get("distinct_tokens", toks)))
    return [
        min(2.0, toks / 500.0),                      # verbosity
        1.0 - distinct / toks,                        # repetition
        float(traj.get("template_match", 0.0)),       # regurgitation
        float(traj.get("conf", 0.5)),                 # claimed confidence
        min(3.0, abs(float(traj.get("score_vel", 0.0)))),  # spike
    ]


class HackCritic:
    """Online logistic critic over hack signatures. Labels come from
    adjudication: 1 = confirmed hack (fluent-but-wrong, verbose filler),
    0 = legit. Starts as a prior; every adjudication sharpens it."""

    VERSION = "1.0.0"

    def __init__(self, dim: int = 5, lr: float = 0.5):
        self.w = [0.0] * dim
        self.b = -1.0  # prior: innocent until proven guilty
        self.lr = lr
        self.n = 0

    def hack_p(self, traj: dict) -> float:
        x = featurize(traj)
        z = self.b + sum(wi * xi for wi, xi in zip(self.w, x))
        return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))

    def adjudicate(self, traj: dict, is_hack: bool):
        """Online SGD step on a confirmed label."""
        x = featurize(traj)
        p = self.hack_p(traj)
        y = 1.0 if is_hack else 0.0
        err = p - y
        self.w = [wi - self.lr * err * xi for wi, xi in zip(self.w, x)]
        self.b -= self.lr * err
        self.n += 1

    def taxed_reward(self, reward: float, traj: dict) -> dict:
        """r' = r * (1 - hack_p). Never flips sign, only taxes."""
        p = self.hack_p(traj)
        return {"reward": reward, "hack_p": round(p, 3),
                "taxed": round(reward * (1.0 - p), 4)}


def progras_center(scores: list[float], outcomes: list[int]) -> list[float]:
    """PROGRS-style outcome-conditioned centering (independently derived).

    Shifts process scores of INCORRECT trajectories to zero mean per group:
    removes fluent-but-wrong positive bias while preserving rankings.
    outcomes: 1 = correct, 0 = incorrect.
    """
    if not scores or not outcomes or len(scores) != len(outcomes):
        return list(scores)
    bad = [s for s, o in zip(scores, outcomes) if not o]
    mu = sum(bad) / len(bad) if bad else 0.0
    return [s - (mu if not o else 0.0) for s, o in zip(scores, outcomes)]
