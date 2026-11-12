"""Door 2: the same matvec through the CPU OpenCL device (stdlib ctypes).

Second door into the same kernels: proves the OpenCL path is not tied
to one device, and gives the CPU-device baseline the HybridDense split
tunes against. Prints the GPU-device ms beside the CPU-device ms for the
same shapes.

Exit 0 + VERDICT line on success, exit 2 when no CPU OpenCL device exists.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from _ocl_ctypes import (CL_DEVICE_TYPE_CPU, CL_DEVICE_TYPE_GPU, Context,
                         OclError, device_name)
from igpu_opencl_compute import MATVEC_SRC, py_matvec


def main() -> int:
    rng = random.Random(20261109)
    try:
        gpu = Context(MATVEC_SRC, CL_DEVICE_TYPE_GPU)
    except OclError as e:
        print(f"NO-GPU-DEVICE: {e}")
        return 2
    try:
        cpu = Context(MATVEC_SRC, CL_DEVICE_TYPE_CPU)
    except OclError as e:
        print(f"NO-CPU-DEVICE: {e}")
        return 2
    try:
        print(f"door=2 gpu={device_name(gpu.device)}")
        print(f"door=2 cpu={device_name(cpu.device)}")
        # Correctness on the CPU device.
        in_dim, out_dim = 64, 32
        W = [[rng.uniform(-1, 1) for _ in range(in_dim)]
             for _ in range(out_dim)]
        b = [rng.uniform(-1, 1) for _ in range(out_dim)]
        x = [rng.uniform(-1, 1) for _ in range(in_dim)]
        flat = [v for row in W for v in row]
        d_W = cpu.buffer(len(flat), flat)
        d_b = cpu.buffer(len(b), list(b))
        d_x = cpu.buffer(len(x), list(x))
        d_y = cpu.buffer(out_dim)
        k = cpu.kernel("matvec")
        for i, a in enumerate([d_W, d_b, d_x, d_y, in_dim, out_dim]):
            cpu.set_arg(k, i, a)
        cpu.launch(k, (out_dim,))
        got = cpu.read_floats(d_y, out_dim)
        want = py_matvec(W, b, x)
        maxd = max(abs(g - w) for g, w in zip(got, want))
        print(f"correctness(cpu-device): max|d|={maxd:.3e} (bound 1e-5)")
        if maxd > 1e-5:
            print("MISMATCH on CPU device")
            return 1
        print("shape | gpu-device ms | cpu-device ms | gpu/cpu")
        print("------|----------------|----------------|--------")
        for in_d, out_d in [(64, 128), (128, 256), (256, 512)]:
            W2 = [[rng.uniform(-1, 1) for _ in range(in_d)]
                  for _ in range(out_d)]
            b2 = [rng.uniform(-1, 1) for _ in range(out_d)]
            x2 = [rng.uniform(-1, 1) for _ in range(in_d)]
            iters = max(1, 2_000_000 // (in_d * out_d))
            times = {}
            for name, c in (("gpu", gpu), ("cpu", cpu)):
                dW = c.buffer(in_d * out_d,
                              [v for row in W2 for v in row])
                dB = c.buffer(out_d, b2)
                dX = c.buffer(in_d, x2)
                dY = c.buffer(out_d)
                kk = c.kernel("matvec")
                for i, a in enumerate([dW, dB, dX, dY, in_d, out_d]):
                    c.set_arg(kk, i, a)
                t0 = time.perf_counter()
                for _ in range(iters):
                    c.launch(kk, (out_d,))
                times[name] = ((time.perf_counter() - t0) * 1000 / iters)
            r = times["cpu"] / times["gpu"] if times["gpu"] else float("inf")
            print(f"{in_d}->{out_d:4d} | {times['gpu']:13.3f} | "
                  f"{times['cpu']:13.3f} | {r:.2f}x")
        print("VERDICT: OK door=2 cpu-device matches pure Python, table above")
        return 0
    finally:
        gpu.close()
        cpu.close()


if __name__ == "__main__":
    sys.exit(main())
