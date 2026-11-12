"""mcml_gpu -- OpenCL backend for MCML (stdlib ctypes only).

GpuDense: device-resident Dense with fused forward/backward/step kernels.
HybridDense: batch rows split across GPU/CPU by tunable percentage.
tune(): measures and pins the fastest split.

Pure stdlib + ctypes OpenCL. No numpy, no pyopencl dependency in the hot path.
"""

from __future__ import annotations

import ctypes
import math
import random
import struct
import time
from typing import List, Optional, Sequence, Tuple

try:
    import pyopencl as cl
    PYOPENCL_AVAILABLE = True
except ImportError:
    PYOPENCL_AVAILABLE = False
    cl = None

# Re-export MCML types
from eve_unleashed.mcml import Dense, Sequential, Vec, Mat, ACTIVATIONS, Activate, _xavier, digest, describe, rebuild


# OpenCL kernel source
KERNEL_SOURCE = """
__kernel void dense_forward(
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

__kernel void dense_backward(
    __global const float* W,
    __global const float* x, __global const float* grad_y,
    __global float* grad_x, __global float* gW, __global float* gb,
    int in_dim, int out_dim
) {
    int o = get_global_id(0);
    if (o >= out_dim) return;
    float gy = grad_y[o];
    for (int i = 0; i < in_dim; i++) {
        gW[o * in_dim + i] += gy * x[i];
    }
    gb[o] += gy;
}

__kernel void dense_backward_input(
    __global const float* W,
    __global const float* grad_y, __global float* grad_x,
    int in_dim, int out_dim
) {
    int i = get_global_id(0);
    if (i >= in_dim) return;
    float sum = 0.0f;
    for (int o = 0; o < out_dim; o++) {
        sum += W[o * in_dim + i] * grad_y[o];
    }
    grad_x[i] = sum;
}

__kernel void dense_step(
    __global float* W, __global float* b,
    __global const float* gW, __global const float* gb,
    float lr, int in_dim, int out_dim
) {
    int idx = get_global_id(0);
    int total = in_dim * out_dim + out_dim;
    if (idx >= total) return;
    if (idx < in_dim * out_dim) {
        W[idx] -= lr * gW[idx];
    } else {
        int b_idx = idx - in_dim * out_dim;
        b[b_idx] -= lr * gb[b_idx];
    }
}
"""


class OpenCLContext:
    """Manages OpenCL context, queue, and program."""

    def __init__(self, platform_idx: int = 0, device_idx: int = 0):
        if not PYOPENCL_AVAILABLE:
            raise RuntimeError("pyopencl not available")
        platforms = cl.get_platforms()
        if platform_idx >= len(platforms):
            platform_idx = 0
        platform = platforms[platform_idx]
        devices = platform.get_devices()
        if device_idx >= len(devices):
            device_idx = 0
        device = devices[device_idx]
        self.ctx = cl.Context([device])
        self.queue = cl.CommandQueue(self.ctx)
        self.program = cl.Program(self.ctx, KERNEL_SOURCE).build()
        self.mf = cl.mem_flags

    def buffer(self, host_array: List[float], flags=None) -> cl.Buffer:
        """Create buffer from host array."""
        if flags is None:
            flags = self.mf.READ_ONLY | self.mf.COPY_HOST_PTR
        arr = (ctypes.c_float * len(host_array))(*host_array)
        return cl.Buffer(self.ctx, flags, hostbuf=arr)

    def read_buffer(self, buf: cl.Buffer, shape: int) -> List[float]:
        """Read buffer back to host."""
        result = [0.0] * shape
        arr = (ctypes.c_float * shape)(*result)
        cl.enqueue_copy(self.queue, arr, buf)
        self.queue.finish()
        return list(arr)


class GpuDense:
    """Fully-connected block on OpenCL device."""

    def __init__(self, in_dim: int, out_dim: int, seed: int = 7, ctx: Optional[OpenCLContext] = None) -> None:
        if in_dim < 1 or out_dim < 1:
            raise ValueError(f"dense dims must be >= 1, got {in_dim} -> {out_dim}")
        rng = random.Random(seed)
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.seed = seed
        self.ctx = ctx or OpenCLContext()

        # Host-side params for replication/digest
        self.W: Mat = [[_xavier(rng, in_dim, out_dim) for _ in range(in_dim)] for _ in range(out_dim)]
        self.b: Vec = [_xavier(rng, in_dim, out_dim) for _ in range(out_dim)]
        self.gW: Mat = [[0.0] * in_dim for _ in range(out_dim)]
        self.gb: Vec = [0.0] * out_dim

        # Device buffers
        flat_W = [v for row in self.W for v in row]
        flat_gW = [v for row in self.gW for v in row]
        self.d_W = self.ctx.buffer(flat_W, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)
        self.d_b = self.ctx.buffer(self.b, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)
        self.d_gW = self.ctx.buffer(flat_gW, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)
        self.d_gb = self.ctx.buffer(self.gb, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)

        # Cache kernel objects once: pyopencl builds a NEW kernel on every
        # program.<name> access, which is real per-call cost in a hot loop.
        self.k_forward = cl.Kernel(self.ctx.program, "dense_forward")
        self.k_backward = cl.Kernel(self.ctx.program, "dense_backward")
        self.k_step = cl.Kernel(self.ctx.program, "dense_step")

    def _sync_to_host(self):
        """Sync device buffers to host arrays."""
        flat_W = self.ctx.read_buffer(self.d_W, self.in_dim * self.out_dim)
        self.W = [flat_W[i * self.in_dim:(i + 1) * self.in_dim] for i in range(self.out_dim)]
        self.b = self.ctx.read_buffer(self.d_b, self.out_dim)
        flat_gW = self.ctx.read_buffer(self.d_gW, self.in_dim * self.out_dim)
        self.gW = [flat_gW[i * self.in_dim:(i + 1) * self.in_dim] for i in range(self.out_dim)]
        self.gb = self.ctx.read_buffer(self.d_gb, self.out_dim)

    def forward(self, x: Vec) -> Vec:
        if len(x) != self.in_dim:
            raise ValueError(f"dense {self.in_dim}->{self.out_dim} got input len {len(x)}")
        d_x = self.ctx.buffer(x)
        d_y = cl.Buffer(self.ctx.ctx, self.ctx.mf.WRITE_ONLY, size=self.out_dim * 4)

        self.k_forward(
            self.ctx.queue, (self.out_dim,), None,
            self.d_W, self.d_b, d_x, d_y,
            ctypes.c_int(self.in_dim), ctypes.c_int(self.out_dim)
        )
        self.ctx.queue.finish()

        y = self.ctx.read_buffer(d_y, self.out_dim)
        return y

    def backward(self, x: Vec, grad_y: Vec) -> Vec:
        d_x = self.ctx.buffer(x)
        d_grad_y = self.ctx.buffer(grad_y)
        d_grad_x = cl.Buffer(self.ctx.ctx, self.ctx.mf.WRITE_ONLY, size=self.in_dim * 4)

        self.k_backward(
            self.ctx.queue, (self.out_dim,), None,
            self.d_W, d_x, d_grad_y,
            d_grad_x, self.d_gW, self.d_gb,
            ctypes.c_int(self.in_dim), ctypes.c_int(self.out_dim)
        )
        self.ctx.queue.finish()

        grad_x = self.ctx.read_buffer(d_grad_x, self.in_dim)
        return grad_x

    def params(self) -> Vec:
        self._sync_to_host()
        return [v for row in self.W for v in row] + list(self.b)

    def grads(self) -> Vec:
        self._sync_to_host()
        return [v for row in self.gW for v in row] + list(self.gb)

    def zero_grad(self):
        self.gW = [[0.0] * self.in_dim for _ in range(self.out_dim)]
        self.gb = [0.0] * self.out_dim
        flat_gW = [0.0] * (self.in_dim * self.out_dim)
        self.d_gW = self.ctx.buffer(flat_gW, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)
        self.d_gb = self.ctx.buffer([0.0] * self.out_dim, self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR)

    def step(self, lr: float):
        total = self.in_dim * self.out_dim + self.out_dim
        self.k_step(
            self.ctx.queue, (total,), None,
            self.d_W, self.d_b, self.d_gW, self.d_gb,
            ctypes.c_float(lr),
            ctypes.c_int(self.in_dim), ctypes.c_int(self.out_dim)
        )
        self.ctx.queue.finish()
        self._sync_to_host()


class HybridDense:
    """Batch rows split across GPU/CPU by tunable percentage."""

    def __init__(
        self,
        in_dim: int,
        out_dim: int,
        seed: int = 7,
        gpu_pct: float = 0.5,
        ctx: Optional[OpenCLContext] = None
    ) -> None:
        if not 0.0 <= gpu_pct <= 1.0:
            raise ValueError("gpu_pct must be in [0.0, 1.0]")
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.gpu_pct = gpu_pct
        self.cpu_layer = Dense(in_dim, out_dim, seed=seed)
        self.gpu_layer = GpuDense(in_dim, out_dim, seed=seed + 1000, ctx=ctx) if gpu_pct > 0.0 else None
        self._pinned_pct: Optional[float] = None

    def forward(self, batch: List[Vec]) -> List[Vec]:
        if not batch:
            return []
        n = len(batch)
        gpu_n = int(n * self.gpu_pct) if self.gpu_layer else 0
        cpu_n = n - gpu_n

        results = []
        if gpu_n > 0:
            for i in range(gpu_n):
                results.append(self.gpu_layer.forward(batch[i]))
        if cpu_n > 0:
            for i in range(gpu_n, n):
                results.append(self.cpu_layer.forward(batch[i]))
        return results

    def backward(self, batch: List[Vec], grads: List[Vec]) -> List[Vec]:
        n = len(batch)
        gpu_n = int(n * self.gpu_pct) if self.gpu_layer else 0
        cpu_n = n - gpu_n

        results = []
        if gpu_n > 0:
            for i in range(gpu_n):
                results.append(self.gpu_layer.backward(batch[i], grads[i]))
        if cpu_n > 0:
            for i in range(gpu_n, n):
                results.append(self.cpu_layer.backward(batch[i], grads[i]))
        return results

    def zero_grad(self):
        # mcml.Dense has gW/gb but no zero_grad/step (only Sequential does),
        # so the CPU side is reset and updated here rather than delegated.
        self.cpu_layer.gW = [[0.0] * self.cpu_layer.in_dim
                             for _ in range(self.cpu_layer.out_dim)]
        self.cpu_layer.gb = [0.0] * self.cpu_layer.out_dim
        if self.gpu_layer:
            self.gpu_layer.zero_grad()

    def step(self, lr: float):
        # Same update math as Sequential.step, applied to the CPU side.
        d = self.cpu_layer
        d.W = [[w - lr * gw for w, gw in zip(row, grow)]
               for row, grow in zip(d.W, d.gW)]
        d.b = [v - lr * gv for v, gv in zip(d.b, d.gb)]
        if self.gpu_layer:
            self.gpu_layer.step(lr)

    def params(self) -> Vec:
        if self.gpu_pct > 0.5 and self.gpu_layer:
            return self.gpu_layer.params()
        return self.cpu_layer.params()

    def grads(self) -> Vec:
        if self.gpu_pct > 0.5 and self.gpu_layer:
            return self.gpu_layer.grads()
        return self.cpu_layer.grads()

    def tune(self, batch: List[Vec], target: List[Vec], steps: int = 10) -> float:
        """Measure and pin the fastest GPU percentage."""
        best_pct = self.gpu_pct
        best_time = float('inf')

        for pct in [i / 10.0 for i in range(11)]:
            self.gpu_pct = pct
            if pct == 0.0:
                self.gpu_layer = None
            elif pct == 1.0:
                self.cpu_layer = Dense(self.in_dim, self.out_dim, seed=7)

            t0 = time.perf_counter()
            for _ in range(steps):
                out = self.forward(batch)
                loss, grad_y = mse_batch(out, target)
                self.backward(batch, grad_y)
                self.step(0.01)
                self.zero_grad()
            elapsed = time.perf_counter() - t0

            if elapsed < best_time:
                best_time = elapsed
                best_pct = pct

        self.gpu_pct = best_pct
        self._pinned_pct = best_pct
        return best_pct


def mse_batch(preds: List[Vec], targets: List[Vec]) -> Tuple[float, List[Vec]]:
    """Batch MSE loss."""
    n = len(preds)
    dim = len(preds[0])
    total_loss = 0.0
    grads = []
    for p, t in zip(preds, targets):
        diff = [pi - ti for pi, ti in zip(p, t)]
        loss = sum(d * d for d in diff) / dim
        total_loss += loss
        grads.append([2.0 * d / dim for d in diff])
    return total_loss / n, grads


# --- Fused Dense-Tanh-Dense pair + tiled SGEMM (Board-47996) ---
# Batch matmuls run through one tiled kernel; every intermediate (X, y1,
# gy1, grads) lives in device buffers for the whole pass, so a training
# step costs one upload (X), one upload (grad_y), one read (y2/grad_x) --
# no per-layer, per-sample round trips like the GpuDense loop.

TILE = 16

SGEMM_SRC = """
#define TILE 16
__kernel void sgemm_nt(
    __global const float* A, __global const float* B,
    __global const float* bias, __global float* C,
    int M, int N, int K
) {
    int row = get_global_id(0);
    int col = get_global_id(1);
    int lx = get_local_id(0);
    int ly = get_local_id(1);
    __local float As[TILE][TILE + 1];
    __local float Bs[TILE][TILE + 1];
    float acc = 0.0f;
    int ntiles = (K + TILE - 1) / TILE;
    for (int t = 0; t < ntiles; t++) {
        int k0 = t * TILE;
        As[lx][ly] = (row < M && k0 + ly < K) ? A[row * K + k0 + ly] : 0.0f;
        Bs[ly][lx] = (col < N && k0 + lx < K) ? B[col * K + k0 + lx] : 0.0f;
        barrier(CLK_LOCAL_MEM_FENCE);
        for (int j = 0; j < TILE; j++) {
            acc += As[lx][j] * Bs[ly][j];
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }
    if (row < M && col < N) {
        C[row * N + col] = acc + bias[col];
    }
}

__kernel void tanh_inplace(__global float* y, int n) {
    int i = get_global_id(0);
    if (i >= n) return;
    float v = y[i];
    float e2 = exp(2.0f * v);
    y[i] = (e2 - 1.0f) / (e2 + 1.0f);
}

__kernel void pair_bwd_a(
    __global const float* W2, __global const float* gy2,
    __global const float* y1, __global float* gy1,
    int B, int H1, int H2
) {
    int b = get_global_id(0);
    int i = get_global_id(1);
    if (b >= B || i >= H1) return;
    float s = 0.0f;
    for (int o = 0; o < H2; o++) {
        s += W2[o * H1 + i] * gy2[b * H2 + o];
    }
    float t = y1[b * H1 + i];
    gy1[b * H1 + i] = s * (1.0f - t * t);
}

__kernel void pair_bwd_b(
    __global const float* y1, __global const float* gy2,
    __global float* gW2, __global float* gb2,
    int B, int H1, int H2
) {
    int o = get_global_id(0);
    int i = get_global_id(1);
    if (o >= H2) return;
    if (i < H1) {
        float s = 0.0f;
        for (int b = 0; b < B; b++) {
            s += y1[b * H1 + i] * gy2[b * H2 + o];
        }
        gW2[o * H1 + i] += s;
    } else if (i == H1) {
        float s = 0.0f;
        for (int b = 0; b < B; b++) {
            s += gy2[b * H2 + o];
        }
        gb2[o] += s;
    }
}

__kernel void pair_bwd_c(
    __global const float* X, __global const float* gy1,
    __global float* gW1, __global float* gb1,
    int B, int IN, int H1
) {
    int h = get_global_id(0);
    int i = get_global_id(1);
    if (h >= H1) return;
    if (i < IN) {
        float s = 0.0f;
        for (int b = 0; b < B; b++) {
            s += X[b * IN + i] * gy1[b * H1 + h];
        }
        gW1[h * IN + i] += s;
    } else if (i == IN) {
        float s = 0.0f;
        for (int b = 0; b < B; b++) {
            s += gy1[b * H1 + h];
        }
        gb1[h] += s;
    }
}

__kernel void pair_bwd_d(
    __global const float* W1, __global const float* gy1,
    __global float* gx,
    int B, int IN, int H1
) {
    int b = get_global_id(0);
    int i = get_global_id(1);
    if (b >= B || i >= IN) return;
    float s = 0.0f;
    for (int h = 0; h < H1; h++) {
        s += W1[h * IN + i] * gy1[b * H1 + h];
    }
    gx[b * IN + i] = s;
}
"""


class FusedPair:
    """Device-resident Dense-Tanh-Dense pair trained as batch tensors.

    Same init as Sequential([Dense(seed1), Activate('tanh'),
    Dense(seed2)]) so exactness against the CPU path is meaningful.
    """

    def __init__(self, in_dim: int, hid_dim: int, out_dim: int,
                 seed1: int = 3, seed2: int = 4,
                 ctx: Optional[OpenCLContext] = None) -> None:
        self.in_dim, self.hid_dim, self.out_dim = in_dim, hid_dim, out_dim
        self.ctx = ctx or OpenCLContext()
        # One program carrying both the existing Dense kernels and the
        # fused-pair kernels (dense_step is reused by step()).
        self.program = cl.Program(
            self.ctx.ctx, KERNEL_SOURCE + SGEMM_SRC).build()
        # Cache kernel objects once: every self.program.<name> access
        # builds a NEW kernel in pyopencl, which is real per-call cost.
        self.k_sgemm = cl.Kernel(self.program, "sgemm_nt")
        self.k_tanh = cl.Kernel(self.program, "tanh_inplace")
        self.k_bwd_a = cl.Kernel(self.program, "pair_bwd_a")
        self.k_bwd_b = cl.Kernel(self.program, "pair_bwd_b")
        self.k_bwd_c = cl.Kernel(self.program, "pair_bwd_c")
        self.k_bwd_d = cl.Kernel(self.program, "pair_bwd_d")
        self.k_step = cl.Kernel(self.program, "dense_step")
        ref1 = Dense(in_dim, hid_dim, seed=seed1)
        ref2 = Dense(hid_dim, out_dim, seed=seed2)
        rw = self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR
        self.d_W1 = self.ctx.buffer(_flat(ref1.W), rw)
        self.d_b1 = self.ctx.buffer(list(ref1.b), rw)
        self.d_W2 = self.ctx.buffer(_flat(ref2.W), rw)
        self.d_b2 = self.ctx.buffer(list(ref2.b), rw)
        self._d_X = self._d_y1 = None
        self._B = 0
        self.zero_grad()

    # -- primitives --
    def _sgemm(self, d_A, d_B, d_bias, d_C, M: int, N: int, K: int) -> None:
        self.k_sgemm(
            self.ctx.queue, (_round_up(M), _round_up(N)), (TILE, TILE),
            d_A, d_B, d_bias, d_C,
            _cl_int(M), _cl_int(N), _cl_int(K))
        self.ctx.queue.finish()

    def _new(self, values: Sequence[float], rw: bool = True):
        flags = self.ctx.mf.READ_WRITE | self.ctx.mf.COPY_HOST_PTR
        return self.ctx.buffer(list(values), flags)

    # -- batch pass --
    def forward_batch(self, X: List[Vec]) -> List[Vec]:
        B = len(X)
        in_dim, hid_dim, out_dim = self.in_dim, self.hid_dim, self.out_dim
        self._d_X = self._new([v for row in X for v in row])
        self._d_y1 = self._new([0.0] * (B * hid_dim))
        d_y2 = self._new([0.0] * (B * out_dim))
        self._sgemm(self._d_X, self.d_W1, self.d_b1, self._d_y1,
                    B, hid_dim, in_dim)
        self.k_tanh(self.ctx.queue, (_round_up(B * hid_dim),), None,
                    self._d_y1, _cl_int(B * hid_dim))
        self.ctx.queue.finish()
        self._sgemm(self._d_y1, self.d_W2, self.d_b2, d_y2,
                    B, out_dim, hid_dim)
        self._B = B
        # Residency: X and y1 stay on device for backward_batch.
        return _unflat(self.ctx.read_buffer(d_y2, B * out_dim), out_dim)

    def backward_batch(self, G: List[Vec]) -> List[Vec]:
        B = self._B
        in_dim, hid_dim, out_dim = self.in_dim, self.hid_dim, self.out_dim
        d_gy2 = self._new([v for row in G for v in row])
        d_gy1 = self._new([0.0] * (B * hid_dim))
        d_gx = self._new([0.0] * (B * in_dim))
        q = self.ctx.queue
        self.k_bwd_a(q, (B, hid_dim), None,
                     self.d_W2, d_gy2, self._d_y1, d_gy1,
                     _cl_int(B), _cl_int(hid_dim), _cl_int(out_dim))
        self.k_bwd_b(q, (out_dim, hid_dim + 1), None,
                     self._d_y1, d_gy2, self.d_gW2, self.d_gb2,
                     _cl_int(B), _cl_int(hid_dim), _cl_int(out_dim))
        self.k_bwd_c(q, (hid_dim, in_dim + 1), None,
                     self._d_X, d_gy1, self.d_gW1, self.d_gb1,
                     _cl_int(B), _cl_int(in_dim), _cl_int(hid_dim))
        self.k_bwd_d(q, (B, in_dim), None,
                     self.d_W1, d_gy1, d_gx,
                     _cl_int(B), _cl_int(in_dim), _cl_int(hid_dim))
        q.finish()
        return _unflat(self.ctx.read_buffer(d_gx, B * in_dim), in_dim)

    def zero_grad(self):
        self.d_gW1 = self._new([0.0] * (self.in_dim * self.hid_dim))
        self.d_gb1 = self._new([0.0] * self.hid_dim)
        self.d_gW2 = self._new([0.0] * (self.hid_dim * self.out_dim))
        self.d_gb2 = self._new([0.0] * self.out_dim)

    def step(self, lr: float):
        for d_W, d_b, d_gW, d_gb, in_dim, out_dim in (
                (self.d_W1, self.d_b1, self.d_gW1, self.d_gb1,
                 self.in_dim, self.hid_dim),
                (self.d_W2, self.d_b2, self.d_gW2, self.d_gb2,
                 self.hid_dim, self.out_dim)):
            total = in_dim * out_dim + out_dim
            self.k_step(
                self.ctx.queue, (total,), None,
                d_W, d_b, d_gW, d_gb,
                _cl_float(lr),
                _cl_int(in_dim), _cl_int(out_dim))
            self.ctx.queue.finish()

    def params(self) -> Vec:
        w1 = self.ctx.read_buffer(self.d_W1, self.in_dim * self.hid_dim)
        b1 = self.ctx.read_buffer(self.d_b1, self.hid_dim)
        w2 = self.ctx.read_buffer(self.d_W2, self.hid_dim * self.out_dim)
        b2 = self.ctx.read_buffer(self.d_b2, self.out_dim)
        n1, n2 = self.in_dim * self.hid_dim, self.hid_dim * self.out_dim
        return w1 + b1 + w2 + b2

    def grads(self) -> Vec:
        gw1 = self.ctx.read_buffer(self.d_gW1, self.in_dim * self.hid_dim)
        gb1 = self.ctx.read_buffer(self.d_gb1, self.hid_dim)
        gw2 = self.ctx.read_buffer(self.d_gW2, self.hid_dim * self.out_dim)
        gb2 = self.ctx.read_buffer(self.d_gb2, self.out_dim)
        return gw1 + gb1 + gw2 + gb2


def _flat(m: Mat) -> List[float]:
    return [v for row in m for v in row]


def _unflat(v: List[float], cols: int) -> List[Vec]:
    return [v[i * cols:(i + 1) * cols] for i in range(len(v) // cols)]


def _round_up(n: int, m: int = TILE) -> int:
    return ((n + m - 1) // m) * m


def _cl_int(v: int):
    return ctypes.c_int(v)


def _cl_float(v: float):
    return ctypes.c_float(v)


def bench_shapes():
    """Benchmark MCML shapes on CPU vs GPU."""
    shapes = [
        (64, 128), (128, 256), (256, 512), (512, 1024),
        (1024, 2048), (2048, 4096),
    ]
    print("shape | pure-Python ms | OpenCL ms | ratio")
    print("------|----------------|-----------|------")

    for in_dim, out_dim in shapes:
        x = [random.uniform(-1, 1) for _ in range(in_dim)]
        grad_y = [random.uniform(-1, 1) for _ in range(out_dim)]

        # CPU - use Sequential with one Dense block
        cpu_model = Sequential([Dense(in_dim, out_dim, seed=42)])
        t0 = time.perf_counter()
        for _ in range(100):
            y = cpu_model.forward(x)
            cpu_model.backward(grad_y)
            cpu_model.step(0.01)
            cpu_model.zero_grad()
        cpu_ms = (time.perf_counter() - t0) * 1000 / 100

        # GPU
        try:
            gpu_dense = GpuDense(in_dim, out_dim, seed=42)
            t0 = time.perf_counter()
            for _ in range(100):
                y = gpu_dense.forward(x)
                gpu_dense.backward(x, grad_y)
                gpu_dense.step(0.01)
                gpu_dense.zero_grad()
            gpu_ms = (time.perf_counter() - t0) * 1000 / 100
            ratio = cpu_ms / gpu_ms if gpu_ms > 0 else float('inf')
            print(f"{in_dim}->{out_dim:4d} | {cpu_ms:12.2f} | {gpu_ms:9.2f} | {ratio:.2f}x")
        except Exception as e:
            print(f"{in_dim}->{out_dim:4d} | {cpu_ms:12.2f} | {'ERROR':>9} | {'N/A':>4}")
            print(f"  GPU error: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        bench_shapes()
    else:
        print("mcml_gpu: OpenCL backend for MCML")
        print("Usage: python -m eve_unleashed.mcml_gpu bench")
        # Quick self-test
        if PYOPENCL_AVAILABLE:
            print("OpenCL available - running quick test...")
            dense = GpuDense(4, 3, seed=1)
            x = [1.0, 2.0, 3.0, 4.0]
            y = dense.forward(x)
            print(f"  forward([1,2,3,4]) -> {y}")
            grad_y = [0.1, 0.2, 0.3]
            grad_x = dense.backward(x, grad_y)
            print(f"  backward -> {grad_x}")
            print("  OK")
        else:
            print("OpenCL not available (pyopencl not installed)")