# coding: utf-8
"""Engram #813 (DEEPSEEK ARXIV-HARVEST) — router-option battery, one mode per slice.

Baseline (measured FIRST in this session, not after the change):

    switch-mode, collinear batch (64 identical rows, seed 7):
        counts [0,0,0,64,0,64,0,0]  used 2/8
        cumulative entropy 0.3333 (= log(2)/log(8), the top-k floor)
        cumulative gini 0.75       min_max_ratio 0.0
    live pool baseline: 500 technique-link rows, 100% severity info,
    ok_rate 1.0 -> ZERO measured negatives exist in the stream today.

Slice layout (each a separate gated commit, ONE variable each):
  A instrumentation (gini / min_max_ratio / cumulative view) -- this file's
    bottom block, plus the byte-identical contract for ``switch``.
  B R1 Loss-Free bias (arXiv:2408.15664)  C R2 BIP quota (2502.15451)
  D R3 LPR prototypes (2506.21328) + SimBal diversity stats
  E F1 NAT negatives  F F2 Likra near-miss   (training_intake.py side)

The structural floor is stated plainly (test E of
``test_cutting_edge_production_fixes.py``): a collinear batch pins the
top-k used set to ``top_k`` experts, so NO logit- or bias-side fix can
raise PER-BATCH entropy on that fixture. Mode acceptance is therefore
stated on the CUMULATIVE view (across batches) and, for the
assignment-side modes (bip/lpr), per-batch as well, because assignment
side-steps the pinning argument. An entropy claim is never asserted where
the fixture cannot support it.
"""

import math
import sys
from pathlib import Path

import pytest

# Repo convention: tests insert src/ themselves (tests/conftest.py does not).
SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from CORE.WORMS.expansion.cutting_edge_model import (  # noqa: E402
    gini_coefficient, load_entropy_normalised, SparseMoE,
)

#: The collinear fixture -- the live 2-of-8 defect, replicated.
D_MODEL, N_EXPERTS, TOP_K, SEED = 16, 8, 2, 7
COLLINEAR_BATCH = [[1.0 * j for j in range(D_MODEL)]] * 64

#: Baseline numbers, asserted once so the fixture's identity is pinned.
COLLINEAR_COUNTS = [0, 0, 0, 64, 0, 64, 0, 0]
COLLINEAR_GINI = 0.75
COLLINEAR_ENTROPY = 1.0 / 3.0


def _entropy_norm(counts, n):
    total = sum(counts)
    if total <= 0 or n < 2:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    return -sum(p * math.log(p) for p in probs) / math.log(n)


def _build(mode=None):
    kwargs = {}
    if mode is not None:
        kwargs["route_mode"] = mode
    return SparseMoE(d_model=D_MODEL, n_experts=N_EXPERTS, top_k=TOP_K,
                     seed=SEED, **kwargs)


# --------------------------------------------------------------------------
# Slice A -- instrumentation
# --------------------------------------------------------------------------

def test_gini_helper_values_with_positive_control():
    """Gini: even load exactly 0.0 (positive control first), full collapse -> 1."""
    assert gini_coefficient([16] * 8) == 0.0
    # One expert takes everything in an 8-expert gate -> (n-1)/n = 7/8.
    assert math.isclose(gini_coefficient([0, 0, 0, 0, 0, 0, 0, 512]), 7 / 8)
    # The measured baseline spread (two of eight live) is 0.75 -- both numbers.
    assert math.isclose(gini_coefficient([0, 0, 0, 64, 0, 64, 0, 0]), 0.75)
    # Degenerate support: nothing measured must read 0.0, never "balanced".
    assert gini_coefficient([]) == 0.0
    assert gini_coefficient([0] * 8) == 0.0


def test_entropy_helper_matches_module_and_baseline():
    """load_entropy_normalised stays the one entropy vocabulary."""
    assert math.isclose(load_entropy_normalised([64, 64] + [0] * 6, 8), 1 / 3)
    assert math.isclose(_entropy_norm([64, 64] + [0] * 6, 8), 1 / 3)
    # even -> 1.0
    assert math.isclose(load_entropy_normalised([16] * 8, 8), 1.0)


def test_forward_stats_carry_instrumentation():
    """forward's stats and the balance snapshot share the same vocabulary."""
    moe = _build()
    _out, _aux, stats = moe.forward(COLLINEAR_BATCH)
    assert stats["counts"] == COLLINEAR_COUNTS  # baseline unchanged
    assert math.isclose(stats["gini"], COLLINEAR_GINI)
    assert stats["min_max_ratio"] == 0.0  # six experts never used per batch
    # clean-up: load_balanced vocabulary untouched
    probe = moe._load_snapshot(COLLINEAR_BATCH)
    assert math.isclose(probe["gini"], COLLINEAR_GINI)
    res = moe.balance_step(COLLINEAR_BATCH)
    assert "load_balanced" in res
    assert "gini" in res  # additive key, not a replacement


def test_cumulative_snapshot_support_and_starved_list():
    """Cumulative view names its support; zero tokens read as 'nothing', not 'even'."""
    moe = _build()
    empty = moe.cumulative_snapshot()
    assert empty["tokens_routed"] == 0
    assert empty["entropy_normalised"] == 0.0
    assert empty["used_experts"] == 0
    assert empty["starved_experts"] == list(range(8))

    moe.forward(COLLINEAR_BATCH)
    moe.forward(COLLINEAR_BATCH)
    cum = moe.cumulative_snapshot()
    # 64 rows x top_k 2 per forward, two forwards -> 256 routed slots.
    assert cum["tokens_routed"] == 256
    assert cum["counts"] == [0, 0, 0, 128, 0, 128, 0, 0]
    assert math.isclose(cum["entropy_normalised"], COLLINEAR_ENTROPY)
    assert cum["starved_experts"] == [0, 1, 2, 4, 6, 7]


def test_switch_mode_is_default_and_byte_identical():
    """No mode set -> shipped router, byte-identical forward-to-forward."""
    a = _build()
    b = _build()
    counts_a = a.forward(COLLINEAR_BATCH)[2]["counts"]
    counts_b = b.forward(COLLINEAR_BATCH)[2]["counts"]
    assert counts_a == COLLINEAR_COUNTS
    assert counts_a == counts_b
    assert a.route_mode == "switch"
    # A new positional-args construction (the pipeline's 3-line call) stays valid.
    c = SparseMoE(D_MODEL, N_EXPERTS, TOP_K, SEED)
    assert c.route_mode == "switch"


def test_unknown_mode_rejected_ctor_and_setter():
    """A mode that cannot describe a router raises; none is silently clamped."""
    for bad in ("loss-free", "BIP", "", "lpr ", None):
        with pytest.raises(ValueError):
            SparseMoE(D_MODEL, N_EXPERTS, TOP_K, SEED, route_mode=bad)
    moe = _build()
    for bad in ("loss-free", "", None):
        with pytest.raises(ValueError):
            moe.set_route_mode(bad)
    # The setter is switchable and revertible.
    moe.set_route_mode("lpr")
    assert moe.route_mode == "lpr"
    moe.set_route_mode("switch")
    assert moe.route_mode == "switch"
