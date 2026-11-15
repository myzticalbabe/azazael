# coding: utf-8
"""Tests for src/CORE/reward_scales.py — canonical reward co-tabulation."""
import os
import sys
import tempfile

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from CORE.reward_scales import (  # noqa: E402
    SCALES,
    canonical_reward,
    describe_scale,
    emit_canonical,
    emitting_scales,
    producerless_scales,
    scale_distributions,
    to_common_scale,
)
from CORE.local_memory import LocalMemoryStore  # noqa: E402


def _tmp_store():
    tmp = tempfile.mkdtemp(prefix="rewardscales_")
    return LocalMemoryStore(db_path=os.path.join(tmp, "t.db"))


def test_module_under_test_is_this_tree():
    """The assertions below must describe THIS worktree, not the hub tree.

    The ELIZA editable install registers a meta-path finder that resolves
    `CORE` to C:\\Azazael\\azazael\\src, and it answers before `sys.path`
    unless this tree's `src` is already on the path. A green run against the
    wrong tree is the shadow-split the session warning exists to name; this
    turns it into a failure that prints the tree it actually loaded.
    """
    import CORE.reward_scales as _module
    loaded = os.path.normcase(os.path.dirname(os.path.dirname(
        os.path.abspath(_module.__file__))))
    expected = os.path.normcase(os.path.join(ROOT, "src"))
    assert loaded == expected, (
        "CORE resolved to %s, not this tree's src; run with PYTHONPATH=<repo>/src "
        "(the editable install points at the hub tree)" % loaded)


def test_scales_registered():
    for sid in ("rate_01", "boolean", "count", "millis", "fitness_points",
                "zscore", "loss", "margin", "probability"):
        assert sid in SCALES
        assert "higher_better" in SCALES[sid]
        assert "producer" in SCALES[sid]
    assert describe_scale("nope") == {}
    # `severity_payoff` named an RL per-step table this tree does not have and
    # no module read or wrote it: a scale invented rather than observed. The
    # registry is a claim of coverage, so it is gone (measured 2026-11-15).
    assert "severity_payoff" not in SCALES
    assert canonical_reward(0.1, "severity_payoff", "p")["reason"] == "unknown-scale"


def test_producer_split_is_measured_not_assumed():
    """Every declared producer must exist, and the split must be declared.

    A registry that lists a scale nobody writes advertises coverage it does not
    have; a `producer` path that no longer exists is the same lie wearing a
    filename. Both are asserted here instead of being trusted.
    """
    for sid, entry in SCALES.items():
        producer = entry.get("producer")
        if producer is None:
            continue
        assert producer, "%s declares an empty producer" % sid
        for relative in producer:
            assert os.path.isfile(os.path.join(ROOT, relative)), \
                "%s names %r, which is not in the tree" % (sid, relative)
    asserted = tuple(sorted(sid for sid, e in SCALES.items()
                            if e.get("producer")))
    assert emitting_scales() == asserted
    assert set(emitting_scales()) | set(producerless_scales()) == set(SCALES)
    assert not set(emitting_scales()) & set(producerless_scales())
    # Nothing writes these yet: no baseline can exist, so to_common_scale must
    # keep refusing them rather than inventing a zero-variance distribution.
    assert producerless_scales() == ("fitness_points", "loss", "margin",
                                     "probability", "zscore")


def test_canonical_valid_and_shaped():
    rec = canonical_reward(0.75, "rate_01", "probe")
    assert rec == {"value": 0.75, "scale_id": "rate_01",
                   "provenance": "probe", "ok": True, "reason": ""}


def test_canonical_rejects_honestly():
    assert canonical_reward(0.5, "nope", "p")["reason"] == "unknown-scale"
    bad = canonical_reward("x", "rate_01", "p")
    assert bad["ok"] is False and bad["reason"] == "non-numeric"
    nan = canonical_reward(float("nan"), "rate_01", "p")
    assert nan["ok"] is False and nan["value"] is None
    over = canonical_reward(2.0, "rate_01", "p")
    assert over["ok"] is True and "out-of-range" in over["reason"]
    b = canonical_reward(True, "boolean", "p")
    assert b["ok"] is True and b["value"] == 1
    assert canonical_reward(True, "rate_01", "p")["ok"] is False


def test_to_common_scale_math_and_refusals():
    base = {"mean": 10.0, "std": 2.0}
    assert to_common_scale({"value": 14.0}, base) == pytest.approx(2.0)
    assert to_common_scale({"value": 14.0}, None) is None
    assert to_common_scale({"value": 14.0}, {}) is None
    assert to_common_scale({"value": 14.0}, {"mean": 10.0, "std": 0.0}) is None
    assert to_common_scale({"value": "x"}, base) is None
    assert to_common_scale({}, base) is None


def test_emit_roundtrip_and_distributions():
    store = _tmp_store()
    assert emit_canonical(store, 0.8, "rate_01", "probe", worm="w1") is True
    assert emit_canonical(store, 120.0, "millis", "probe", worm="w1") is True
    rows = store.query_memories(source="reward-ledger", limit=10)
    assert len(rows) == 2
    dist = scale_distributions(store)
    assert dist["rate_01"]["n"] == 1
    assert dist["millis"]["mean"] == pytest.approx(120.0)
    assert dist["millis"]["std"] == pytest.approx(0.0)
    # end-to-end: measured baseline feeds the mapping
    z = to_common_scale({"value": 0.8}, {"mean": 0.8, "std": 0.0} | {})
    assert z is None  # zero variance refuses, even on real data
