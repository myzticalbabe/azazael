# coding: utf-8
"""Tests for src/CORE/WORMS/expansion/hybrid_rewards.py — unit contract.

The blender promises a [0, 1] aggregate. update() must refuse anything
outside that contract (returning False) instead of blending-then-clamping
it, which previously recorded every negative reward as a silent 0.0.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from CORE.WORMS.expansion.hybrid_rewards import (  # noqa: E402
    HybridRewardComputer,
    RewardConfig,
    RewardSource,
)


def _computer(weights=None):
    cfg = RewardConfig(source_weights=weights or {RewardSource.ENVIRONMENT: 1.0})
    return HybridRewardComputer(cfg)


def test_update_accepts_unit_range():
    hr = _computer()
    assert hr.update(RewardSource.ENVIRONMENT, 0.0) is True
    assert hr.update(RewardSource.ENVIRONMENT, 1.0) is True
    assert hr.update(RewardSource.ENVIRONMENT, 0.42) is True


def test_update_refuses_out_of_range():
    hr = _computer()
    assert hr.update(RewardSource.ENVIRONMENT, -0.5) is False
    assert hr.update(RewardSource.ENVIRONMENT, 1.5) is False
    assert hr.update(RewardSource.ENVIRONMENT, 250.0) is False
    # Refused observations leave no trace: aggregate of nothing is 0.0.
    assert hr.compute_hybrid() == 0.0


def test_update_refuses_non_numeric():
    hr = _computer()
    assert hr.update(RewardSource.ENVIRONMENT, float("nan")) is False
    assert hr.update(RewardSource.ENVIRONMENT, float("inf")) is False
    assert hr.update(RewardSource.ENVIRONMENT, float("-inf")) is False
    assert hr.update(RewardSource.ENVIRONMENT, True) is False
    assert hr.update(RewardSource.ENVIRONMENT, "0.5") is False
    assert hr.update(RewardSource.ENVIRONMENT, None) is False
    assert hr.compute_hybrid() == 0.0


def test_single_source_passthrough():
    # One source at weight 1.0: confidence cancels, value comes back whole.
    hr = _computer()
    assert hr.update(RewardSource.ENVIRONMENT, 0.7) is True
    assert hr.compute_hybrid() == 0.7


def test_two_source_weighting():
    hr = _computer({RewardSource.ENVIRONMENT: 0.5,
                    RewardSource.USER_FEEDBACK: 0.5})
    assert hr.update(RewardSource.ENVIRONMENT, 1.0) is True
    assert hr.update(RewardSource.USER_FEEDBACK, 0.0) is True
    assert hr.compute_hybrid() == 0.5


def test_refused_source_does_not_dilute():
    # A refused USER_FEEDBACK must not drag the ENVIRONMENT value down.
    hr = _computer({RewardSource.ENVIRONMENT: 0.5,
                    RewardSource.USER_FEEDBACK: 0.5})
    assert hr.update(RewardSource.ENVIRONMENT, 0.8) is True
    assert hr.update(RewardSource.USER_FEEDBACK, -3.0) is False
    assert hr.compute_hybrid() == 0.8
