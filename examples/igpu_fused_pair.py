"""example: fused Dense-Tanh-Dense pair + tiled SGEMM on the iGPU.

Builds FusedPair (device-resident batch path) beside a CPU reference of
two mcml.Dense blocks from the SAME seeds, then compares forward
outputs, input grads, param grads, post-step params, and times both on
the same batch.

Exit 0 + VERDICT when every tolerance holds, exit 2 without a GPU.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

FWD_TOL = 2e-5
GRAD_TOL = 2e-5
PARAM_TOL = 2e-6


def maxd(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def tanh(v):
    return (math_exp(v) - 1.0 / math_exp(v)) / (math_exp(v) + 1.0 / math_exp(v))


def math_exp(v):
    import math
    return math.exp(v)


def cpu_pass(d1, d2, x, target, learn=False, lr=0.01):
    """Forward + backward through Dense-tanh-Dense. Returns (y2, gx)."""
    from eve_unleashed.mcml import mse
    y1 = [tanh(v) for v in d1.forward(x)]
    y2 = d2.forward(y1)
    loss, gy2 = mse(y2, target)
    gy1_pre = d2.backward(y1, gy2)
    gy1 = [g * (1.0 - t * t) for g, t in zip(gy1_pre, y1)]
    gx = d1.backward(x, gy1)
    if learn:
        for d in (d1, d2):
            d.W = [[w - lr * gw for w, gw in zip(row, grow)]
                   for row, grow in zip(d.W, d.gW)]
            d.b = [v - lr * gv for v, gv in zip(d.b, d.gb)]
    return y2, gx, loss


def zero_ref(d):
    d.gW = [[0.0] * d.in_dim for _ in range(d.out_dim)]
    d.gb = [0.0] * d.out_dim


def main() -> int:
    try:
        from eve_unleashed.mcml_gpu import FusedPair, mse_batch
    except Exception as e:  # noqa: BLE001 - reported, never swallowed
        print(f"NO-GPU-BACKEND: {e}")
        return 2

    from eve_unleashed.mcml import Dense

    rng = random.Random(20261112)
    in_dim, hid_dim, out_dim, batch = 64, 128, 32, 32
    X = [[rng.uniform(-1, 1) for _ in range(in_dim)] for _ in range(batch)]
    T = [[rng.uniform(-1, 1) for _ in range(out_dim)] for _ in range(batch)]

    d1 = Dense(in_dim, hid_dim, seed=3)
    d2 = Dense(hid_dim, out_dim, seed=4)
    zero_ref(d1)
    zero_ref(d2)
    try:
        pair = FusedPair(in_dim, hid_dim, out_dim, seed1=3, seed2=4)
    except Exception as e:  # noqa: BLE001
        print(f"NO-GPU-BACKEND: {e}")
        return 2

    # -- forward --
    ref_y, gx_ref = [], []
    for x, t in zip(X, T):
        y2, gx, _ = cpu_pass(d1, d2, x, t)
        ref_y.append(y2)
        gx_ref.append(gx)
    got_y = pair.forward_batch(X)
    fwd = max(maxd(a, b) for a, b in zip(got_y, ref_y))
    print(f"forward: max|d|={fwd:.3e} (tol {FWD_TOL:.0e})")

    # -- backward: same grad_y into both paths --
    _, grad_y = mse_batch(ref_y, T)
    gx_gpu = pair.backward_batch(grad_y)
    gin = max(maxd(a, b) for a, b in zip(gx_gpu, gx_ref))
    cpu_g1 = [w for row in d1.gW for w in row] + list(d1.gb)
    cpu_g2 = [w for row in d2.gW for w in row] + list(d2.gb)
    gpu_grads = pair.grads()
    n1 = in_dim * hid_dim + hid_dim
    g1 = maxd(gpu_grads[:n1], cpu_g1)
    g2 = maxd(gpu_grads[n1:], cpu_g2)
    print(f"grad_x: max|d|={gin:.3e} (tol {GRAD_TOL:.0e})")
    print(f"grad_W1/b1: max|d|={g1:.3e} (tol {GRAD_TOL:.0e})")
    print(f"grad_W2/b2: max|d|={g2:.3e} (tol {GRAD_TOL:.0e})")

    # -- one step, compare params --
    lr = 0.01
    for d in (d1, d2):
        d.W = [[w - lr * gw for w, gw in zip(row, grow)]
               for row, grow in zip(d.W, d.gW)]
        d.b = [v - lr * gv for v, gv in zip(d.b, d.gb)]
    pair.step(lr)
    ref_params = ([w for row in d1.W for w in row] + list(d1.b) +
                  [w for row in d2.W for w in row] + list(d2.b))
    p = maxd(pair.params(), ref_params)
    print(f"post-step params: max|d|={p:.3e} (tol {PARAM_TOL:.0e})")

    # -- timing: same batch, 20 forward+backward passes each --
    t0 = time.perf_counter()
    for _ in range(20):
        for x, t in zip(X, T):
            cpu_pass(d1, d2, x, t)
    cpu_ms = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    for _ in range(20):
        pair.forward_batch(X)
        pair.backward_batch(grad_y)
    gpu_ms = (time.perf_counter() - t0) * 1000
    print(f"timing: cpu {cpu_ms:.1f} ms vs fused {gpu_ms:.1f} ms = "
          f"{cpu_ms / gpu_ms:.2f}x")

    ok = (fwd <= FWD_TOL and gin <= GRAD_TOL and g1 <= GRAD_TOL and
          g2 <= GRAD_TOL and p <= PARAM_TOL)
    print(f"VERDICT: {'OK' if ok else 'MISMATCH'} fused pair vs CPU reference")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
