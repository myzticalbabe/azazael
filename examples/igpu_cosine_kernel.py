"""Cosine kernel over the memory store's vector shape (stdlib ctypes).

N vectors of D floats, one dot product per row against a query vector,
cosine written out: out[r] = (X[r] . q) / (|X[r]| |q|). Row norms are
precomputed on the host (they are stored beside the vectors); the query
norm is a scalar argument.

Verifies GPU rows against pure-Python cosine on probe rows, prints
pure-Python ms vs OpenCL ms and the ratio.

Exit 0 + VERDICT on success, exit 2 with the reason when no GPU device.
"""
from __future__ import annotations

import math
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from _ocl_ctypes import (CL_DEVICE_TYPE_GPU, Context, OclError, device_name)

COSINE_SRC = """
__kernel void cosine_batch(
    __global const float* X, __global const float* q,
    __global const float* norms, __global float* out,
    float qnorm, int dim, int nrows
) {
    int r = get_global_id(0);
    if (r >= nrows) return;
    float dot = 0.0f;
    for (int i = 0; i < dim; i++) {
        dot += X[r * dim + i] * q[i];
    }
    float denom = norms[r] * qnorm;
    out[r] = (denom > 0.0f) ? dot / denom : 0.0f;
}
"""


def py_cosine_row(row, q, qnorm):
    dot = sum(a * b for a, b in zip(row, q))
    n = math.sqrt(sum(a * a for a in row))
    return dot / (n * qnorm) if n * qnorm > 0 else 0.0


def main() -> int:
    rng = random.Random(20261112)
    try:
        ctx = Context(COSINE_SRC, CL_DEVICE_TYPE_GPU)
    except OclError as e:
        print(f"NO-GPU-DEVICE: {e}")
        return 2
    try:
        print(f"device={device_name(ctx.device)}")
        nrows, dim = 4096, 256
        X = [[rng.uniform(-1, 1) for _ in range(dim)] for _ in range(nrows)]
        q = [rng.uniform(-1, 1) for _ in range(dim)]
        norms = [math.sqrt(sum(a * a for a in row)) for row in X]
        qnorm = math.sqrt(sum(a * a for a in q))
        flat = [v for row in X for v in row]
        d_X = ctx.buffer(len(flat), flat)
        d_q = ctx.buffer(len(q), list(q))
        d_n = ctx.buffer(len(norms), norms)
        d_o = ctx.buffer(nrows)
        k = ctx.kernel("cosine_batch")
        ctx.set_arg(k, 0, d_X)
        ctx.set_arg(k, 1, d_q)
        ctx.set_arg(k, 2, d_n)
        ctx.set_arg(k, 3, d_o)
        ctx.set_arg(k, 4, float(qnorm))
        ctx.set_arg(k, 5, dim)
        ctx.set_arg(k, 6, nrows)
        t0 = time.perf_counter()
        ctx.launch(k, (nrows,))
        ocl_ms = (time.perf_counter() - t0) * 1000
        got = ctx.read_floats(d_o, nrows)
        # Verify on probe rows: first 4 + 4 deterministic pseudo-random.
        probes = [0, 1, 2, 3] + [rng.randrange(nrows) for _ in range(4)]
        maxd = 0.0
        for r in probes:
            want = py_cosine_row(X[r], q, qnorm)
            maxd = max(maxd, abs(got[r] - want))
        print(f"shape: N={nrows} D={dim}")
        print(f"probe rows {probes}: max|d|={maxd:.3e} (bound 1e-5)")
        if maxd > 1e-5:
            print("MISMATCH: device cosine disagrees with pure Python")
            return 1
        t0 = time.perf_counter()
        for r in range(nrows):
            py_cosine_row(X[r], q, qnorm)
        py_ms = (time.perf_counter() - t0) * 1000
        print(f"pure-Python ms: {py_ms:.2f}")
        print(f"OpenCL ms:      {ocl_ms:.2f}")
        print(f"ratio: {py_ms / ocl_ms:.2f}x")
        print("VERDICT: OK cosine_batch matches pure Python, numbers above")
        return 0
    finally:
        ctx.close()


if __name__ == "__main__":
    sys.exit(main())
