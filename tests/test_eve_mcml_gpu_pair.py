"""Fused Dense-Tanh-Dense pair + tiled SGEMM: exactness against mcml."""
import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed.mcml import Dense, mse

gpu = pytest.importorskip("eve_unleashed.mcml_gpu")


def _maxd(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def _zero(d):
    d.gW = [[0.0] * d.in_dim for _ in range(d.out_dim)]
    d.gb = [0.0] * d.out_dim


def _requires_gpu():
    try:
        gpu.OpenCLContext()
    except Exception as e:  # noqa: BLE001 - absence is a skip, not a pass
        pytest.skip(f"no OpenCL device: {e}")


def _fixture(in_dim=16, hid=24, out_dim=8, batch=6, seed=5):
    rng = random.Random(seed)
    X = [[rng.uniform(-1, 1) for _ in range(in_dim)] for _ in range(batch)]
    T = [[rng.uniform(-1, 1) for _ in range(out_dim)] for _ in range(batch)]
    return X, T


def test_fused_pair_forward_matches_dense_tanh_dense():
    _requires_gpu()
    X, _ = _fixture()
    d1, d2 = Dense(16, 24, seed=3), Dense(24, 8, seed=4)
    pair = gpu.FusedPair(16, 24, 8, seed1=3, seed2=4)
    got = pair.forward_batch(X)
    for x, y in zip(X, got):
        y1 = [math.tanh(v) for v in d1.forward(x)]
        assert _maxd(y, d2.forward(y1)) <= 2e-5


def test_fused_pair_backward_matches_dense_grads():
    _requires_gpu()
    X, T = _fixture()
    d1, d2 = Dense(16, 24, seed=3), Dense(24, 8, seed=4)
    _zero(d1)
    _zero(d2)
    gx_ref = []
    ref_y = []
    for x, t in zip(X, T):
        y1 = [math.tanh(v) for v in d1.forward(x)]
        y2 = d2.forward(y1)
        ref_y.append(y2)
        _, gy2 = mse(y2, t)
        gy1 = [g * (1.0 - v * v)
               for g, v in zip(d2.backward(y1, gy2), y1)]
        gx_ref.append(d1.backward(x, gy1))
    pair = gpu.FusedPair(16, 24, 8, seed1=3, seed2=4)
    pair.forward_batch(X)
    _, grad_y = gpu.mse_batch(ref_y, T)
    gx = pair.backward_batch(grad_y)
    for a, b in zip(gx, gx_ref):
        assert _maxd(a, b) <= 2e-5
    grads = pair.grads()
    n1 = 16 * 24 + 24
    assert _maxd(grads[:n1],
                 [w for row in d1.gW for w in row] + d1.gb) <= 2e-5
    assert _maxd(grads[n1:],
                 [w for row in d2.gW for w in row] + d2.gb) <= 2e-5


def test_fused_pair_step_matches_dense_update():
    _requires_gpu()
    X, T = _fixture()
    d1, d2 = Dense(16, 24, seed=3), Dense(24, 8, seed=4)
    _zero(d1)
    _zero(d2)
    ref_y = []
    for x, t in zip(X, T):
        y1 = [math.tanh(v) for v in d1.forward(x)]
        y2 = d2.forward(y1)
        ref_y.append(y2)
        _, gy2 = mse(y2, t)
        gy1 = [g * (1.0 - v * v)
               for g, v in zip(d2.backward(y1, gy2), y1)]
        d1.backward(x, gy1)
    pair = gpu.FusedPair(16, 24, 8, seed1=3, seed2=4)
    pair.forward_batch(X)
    _, grad_y = gpu.mse_batch(ref_y, T)
    pair.backward_batch(grad_y)
    lr = 0.01
    for d in (d1, d2):
        d.W = [[w - lr * gw for w, gw in zip(row, grow)]
               for row, grow in zip(d.W, d.gW)]
        d.b = [v - lr * gv for v, gv in zip(d.b, d.gb)]
    pair.step(lr)
    want = ([w for row in d1.W for w in row] + d1.b +
            [w for row in d2.W for w in row] + d2.b)
    assert _maxd(pair.params(), want) <= 2e-6


@pytest.mark.parametrize("pct", [0.0, 0.5, 1.0])
def test_hybrid_dense_can_step_and_learn(pct):
    """HybridDense delegated step/zero_grad to Dense, which has neither."""
    _requires_gpu()
    X, T = _fixture(batch=8)
    h = gpu.HybridDense(16, 8, seed=7, gpu_pct=pct)
    before = gpu.mse_batch(h.forward(X), T)[0]
    for _ in range(40):
        y = h.forward(X)
        _, gy = gpu.mse_batch(y, T)
        h.backward(X, gy)
        h.step(0.05)
        h.zero_grad()
    after = gpu.mse_batch(h.forward(X), T)[0]
    assert after < before, f"gpu_pct={pct}: loss {before} -> {after}"


def test_hybrid_dense_tune_pins_a_split():
    _requires_gpu()
    X, T = _fixture(batch=8)
    h = gpu.HybridDense(16, 8, seed=7, gpu_pct=0.5)
    pinned = h.tune(X, T, steps=2)
    assert 0.0 <= pinned <= 1.0
    assert h._pinned_pct == pinned


def test_tiled_sgemm_rounds_partial_tiles():
    """Batch size not divisible by TILE must still be exact."""
    _requires_gpu()
    X, T = _fixture(batch=5)  # 5 < TILE(16): ragged tile path
    d1, d2 = Dense(16, 24, seed=3), Dense(24, 8, seed=4)
    pair = gpu.FusedPair(16, 24, 8, seed1=3, seed2=4)
    got = pair.forward_batch(X)
    for x, y in zip(X, got):
        y1 = [math.tanh(v) for v in d1.forward(x)]
        assert _maxd(y, d2.forward(y1)) <= 2e-5
