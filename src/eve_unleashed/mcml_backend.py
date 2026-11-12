"""mcml_backend -- opt-in OpenCL backend selection for Eve training.

NEW module only; mcml.py semantics untouched. Backend is chosen by the
MCML_BACKEND environment flag (cpu|opencl, default cpu) so every existing
caller keeps CPU unless it opts in:

    MCML_BACKEND=opencl PYTHONPATH=src python -m eve_unleashed.mcml_backend

make_dense() returns mcml.Dense on cpu or mcml_gpu.GpuDense on opencl
(lazy import; a clear RuntimeError when pyopencl is missing, so a box
without the wheel fails loudly instead of silently training on CPU).

The cpu default is a portability choice, not a speed one: measured
2026-11-12 on Intel Arc 140T with kernels cached, opencl is 1.44x FASTER
than cpu at 64->32 batch 16 (51.24 ms vs 73.73 ms). The earlier 0.45x
reading was taken before GpuDense cached its kernel objects, and it is
superseded, not a second opinion.
train_batch() is backend-blind: it only uses forward/backward/step/
zero_grad/params/grads, the surface both layers share.
report() prints exactness (GpuDense vs Dense from the SAME seed:
max|d| on forward outputs, grads, and post-step params) plus ms
before/after on the same batch.
"""
from __future__ import annotations

import os
import time
from typing import List

from eve_unleashed.mcml import Dense, Vec

BACKEND_ENV = "MCML_BACKEND"
DEFAULT_BACKEND = "cpu"

FWD_TOL = 2e-5
GRAD_TOL = 2e-5
REPLICA_TOL = 1e-6


def backend_name() -> str:
    return os.getenv(BACKEND_ENV, DEFAULT_BACKEND).strip().lower()


def make_dense(in_dim: int, out_dim: int, seed: int = 7):
    """Dense on cpu, GpuDense on opencl. Same seed => same init."""
    name = backend_name()
    if name == "cpu":
        return Dense(in_dim, out_dim, seed=seed)
    if name == "opencl":
        try:
            from eve_unleashed.mcml_gpu import GpuDense
        except ImportError as e:
            raise RuntimeError(
                "MCML_BACKEND=opencl needs pyopencl, which is not installed; "
                "unset the flag for CPU or install the wheel"
            ) from e
        return GpuDense(in_dim, out_dim, seed=seed)
    raise ValueError(f"{BACKEND_ENV} must be cpu|opencl, got {name!r}")


def _zero_grad(layer) -> None:
    # mcml.Dense owns no zero_grad (only Sequential resets block grads);
    # GpuDense does. Same reset either way.
    if hasattr(layer, "zero_grad"):
        layer.zero_grad()
        return
    layer.gW = [[0.0] * layer.in_dim for _ in range(layer.out_dim)]
    layer.gb = [0.0] * layer.out_dim


def _step(layer, lr: float) -> None:
    # Mirrors Sequential.step exactly for a lone Dense.
    if hasattr(layer, "step"):
        layer.step(lr)
        return
    layer.W = [[w - lr * gw for w, gw in zip(row, grow)]
               for row, grow in zip(layer.W, layer.gW)]
    layer.b = [x - lr * gb for x, gb in zip(layer.b, layer.gb)]


def train_batch(layer, xs: List[Vec], ts: List[Vec], lr: float,
                steps: int = 1) -> float:
    """One backend-blind training loop; returns mean squared error."""
    loss = 0.0
    for _ in range(steps):
        total = 0.0
        for x, t in zip(xs, ts):
            y = layer.forward(x)
            diff = [a - b for a, b in zip(y, t)]
            total += sum(d * d for d in diff) / len(diff)
            layer.backward(x, [2.0 * d / len(diff) for d in diff])
        _step(layer, lr)
        _zero_grad(layer)
        loss = total / len(xs)
    return loss


def _maxd(a: Vec, b: Vec) -> float:
    return max(abs(x - y) for x, y in zip(a, b))


def report(in_dim: int = 64, out_dim: int = 32, batch: int = 16,
           steps: int = 20, lr: float = 0.01) -> int:
    """Exactness + timing of opencl vs cpu on the same batch. Exit-code int."""
    import random
    rng = random.Random(20261112)
    xs = [[rng.uniform(-1, 1) for _ in range(in_dim)] for _ in range(batch)]
    ts = [[rng.uniform(-1, 1) for _ in range(out_dim)] for _ in range(batch)]

    # Phase 1 -- exactness on a FRESH pair (same seed => same init).
    # Any training must happen after the comparison, never before it.
    os.environ[BACKEND_ENV] = "cpu"
    cpu = make_dense(in_dim, out_dim, seed=7)
    os.environ[BACKEND_ENV] = "opencl"
    try:
        gpu = make_dense(in_dim, out_dim, seed=7)
    except RuntimeError as e:
        print(f"NO-BACKEND: {e}")
        return 2
    x0 = xs[0]
    fwd_d = _maxd(gpu.forward(x0), cpu.forward(x0))
    from eve_unleashed.mcml_gpu import mse_batch
    _, grad_y = mse_batch([cpu.forward(v) for v in xs], ts)
    _zero_grad(gpu)
    _zero_grad(cpu)
    for x, g in zip(xs, grad_y):
        gpu.backward(x, g)
        cpu.backward(x, g)
    grad_d = _maxd(gpu.grads(), cpu.grads())
    _step(gpu, lr)
    _step(cpu, lr)
    post_d = _maxd(gpu.params(), cpu.params())

    # Phase 2 -- timing on a SECOND fresh pair, same batch, both backends.
    os.environ[BACKEND_ENV] = "cpu"
    cpu2 = make_dense(in_dim, out_dim, seed=7)
    t0 = time.perf_counter()
    cpu_loss = train_batch(cpu2, xs, ts, lr, steps)
    cpu_ms = (time.perf_counter() - t0) * 1000
    os.environ[BACKEND_ENV] = "opencl"
    gpu2 = make_dense(in_dim, out_dim, seed=7)
    t0 = time.perf_counter()
    gpu_loss = train_batch(gpu2, xs, ts, lr, steps)
    gpu_ms = (time.perf_counter() - t0) * 1000
    print(f"backend: cpu loss={cpu_loss:.6f} ms={cpu_ms:.2f}")
    print(f"backend: opencl loss={gpu_loss:.6f} ms={gpu_ms:.2f}")
    print(f"exactness: fwd max|d|={fwd_d:.3e} (tol {FWD_TOL:.0e})")
    print(f"exactness: grads max|d|={grad_d:.3e} (tol {GRAD_TOL:.0e})")
    print(f"exactness: post-step max|d|={post_d:.3e} (tol {REPLICA_TOL:.0e})")
    print(f"timing: cpu {cpu_ms:.2f} ms vs opencl {gpu_ms:.2f} ms = "
          f"{cpu_ms / gpu_ms:.2f}x")
    ok = (fwd_d <= FWD_TOL and grad_d <= GRAD_TOL and post_d <= REPLICA_TOL)
    print(f"VERDICT: {'OK' if ok else 'MISMATCH'} opt-in backend "
          f"matches CPU within tolerance")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(report())
