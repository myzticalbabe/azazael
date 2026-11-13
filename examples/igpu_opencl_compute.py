"""Door 1: iGPU OpenCL compute via stdlib ctypes (no pyopencl, no numpy).

Probes the ICD loader, runs a matvec kernel (y = W x + b, the exact math
of mcml.Dense.forward) on the GPU device, checks it against pure-Python
list math, then times mcml's hot loop against the OpenCL path for the
SAME shapes and prints shape | pure-Python ms | OpenCL ms | ratio.

Exit 0 + VERDICT line on success. Exit 2 with the reason when no OpenCL
platform/GPU device exists -- a missing device is reported, never faked.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from _ocl_ctypes import (CL_DEVICE_TYPE_GPU, Context, OclError, devices,
                         platforms, platform_name, device_name)

MATVEC_SRC = """
__kernel void matvec(
    __global const float* W, __global const float* b,
    __global const float* x, __global float* y,
    int in_dim, int out_dim
) {
    int o = get_global_id(0);
    if (o >= out_dim) return;
    float sum = b[o];
    for (int i = 0; i < in_dim; i++) {
        sum += W[o * in_dim + i] * x[i];
    }
    y[o] = sum;
}
"""


def py_matvec(W, b, x):
    return [sum(w * v for w, v in zip(row, x)) + bb
            for row, bb in zip(W, b)]


def run_matvec(ctx: Context, W, b, x):
    in_dim, out_dim = len(x), len(b)
    flat_W = [v for row in W for v in row]
    d_W = ctx.buffer(len(flat_W), flat_W)
    d_b = ctx.buffer(len(b), list(b))
    d_x = ctx.buffer(len(x), list(x))
    d_y = ctx.buffer(out_dim)
    k = ctx.kernel("matvec")
    ctx.set_arg(k, 0, d_W)
    ctx.set_arg(k, 1, d_b)
    ctx.set_arg(k, 2, d_x)
    ctx.set_arg(k, 3, d_y)
    ctx.set_arg(k, 4, in_dim)
    ctx.set_arg(k, 5, out_dim)
    ctx.launch(k, (out_dim,))
    return ctx.read_floats(d_y, out_dim)


def main() -> int:
    try:
        plats = platforms()
    except OclError as e:
        print(f"NO-PLATFORM: {e}")
        return 2
    print("platforms:")
    for p in plats:
        ds = [device_name(d) for d in devices(p)]
        print(f"  {platform_name(p)}: {ds if ds else '(no devices)'}")
    try:
        ctx = Context(MATVEC_SRC, CL_DEVICE_TYPE_GPU)
    except OclError as e:
        print(f"NO-GPU-DEVICE: {e}")
        return 2
    print(f"door=1 device={device_name(ctx.device)}")
    try:
        rng = random.Random(20261109)
        in_dim, out_dim = 64, 32
        W = [[rng.uniform(-1, 1) for _ in range(in_dim)]
             for _ in range(out_dim)]
        b = [rng.uniform(-1, 1) for _ in range(out_dim)]
        x = [rng.uniform(-1, 1) for _ in range(in_dim)]
        got = run_matvec(ctx, W, b, x)
        want = py_matvec(W, b, x)
        maxd = max(abs(g - w) for g, w in zip(got, want))
        print(f"correctness: max|d|={maxd:.3e} (bound 1e-5)")
        if maxd > 1e-5:
            print("MISMATCH: device math disagrees with pure Python")
            return 1

        from eve_unleashed.mcml import Dense
        print("shape | pure-Python ms | OpenCL ms | ratio")
        print("------|----------------|-----------|------")
        for in_d, out_d in [(64, 128), (128, 256), (256, 512),
                            (512, 1024)]:
            W2 = [[rng.uniform(-1, 1) for _ in range(in_d)]
                  for _ in range(out_d)]
            b2 = [rng.uniform(-1, 1) for _ in range(out_d)]
            x2 = [rng.uniform(-1, 1) for _ in range(in_d)]
            iters = max(1, 2_000_000 // (in_d * out_d))
            cpu = Dense(in_d, out_d, seed=42)
            cpu.W = [row[:] for row in W2]
            cpu.b = list(b2)
            t0 = time.perf_counter()
            for _ in range(iters):
                cpu.forward(x2)
            cpu_ms = (time.perf_counter() - t0) * 1000 / iters
            d_W = ctx.buffer(in_d * out_d,
                             [v for row in W2 for v in row])
            d_b = ctx.buffer(out_d, b2)
            d_x = ctx.buffer(in_d, x2)
            d_y = ctx.buffer(out_d)
            k = ctx.kernel("matvec")
            ctx.set_arg(k, 0, d_W)
            ctx.set_arg(k, 1, d_b)
            ctx.set_arg(k, 2, d_x)
            ctx.set_arg(k, 3, d_y)
            ctx.set_arg(k, 4, in_d)
            ctx.set_arg(k, 5, out_d)
            t0 = time.perf_counter()
            for _ in range(max(1, iters)):
                ctx.launch(k, (out_d,))
            ocl_ms = (time.perf_counter() - t0) * 1000 / max(1, iters)
            ratio = cpu_ms / ocl_ms if ocl_ms > 0 else float("inf")
            print(f"{in_d}->{out_d:4d} | {cpu_ms:12.3f} | {ocl_ms:9.3f} | "
                  f"{ratio:.2f}x")
        print("VERDICT: OK door=1 matvec matches pure Python, table above")
        return 0
    finally:
        ctx.close()


if __name__ == "__main__":
    sys.exit(main())
