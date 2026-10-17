# CUDA Integration Protocol — Azazael Accelerator Chain

## Box Reality (honest, measured 2026-10-16)

| Fact | Value |
|---|---|
| NVIDIA GPU | absent (`nvidia-smi` not found, no `nvml.dll`) |
| CUDA toolkit | absent (no `C:\Program Files\NVIDIA GPU Computing Toolkit`, no `nvcc`) |
| Level Zero | `ze_loader.dll` present, `ze_intel_gpu.dll` absent |
| Intel iGPU | Arc(TM) 140T (8GB) — bound via OpenVINO (system-3.14), torch.xpu (3.12 venv), llama.cpp Vulkan (native binary) |
| NPU | Intel AI Boost — bound via OpenVINO (system-3.14) |

**CUDA cannot run on this box today.** There is no NVIDIA device to bind and no CUDA toolkit to compile with. The protocol below is the complete integration path: when a CUDA-capable machine (or this box with an NVIDIA dGPU added) provides the binary, the sidecar and preflight will pick it up automatically.

## 1. Build the CUDA Binary (recipe in `build-spark/`)

Source tree: `C:\Users\clint\llama-server\build-spark/` (llama.cpp fork with `ggml-cuda`).

**Windows build (from `build-cuda-windows.yml`):**

```powershell
# Prerequisites (install once):
#   - Visual Studio 2022 (MSVC, C++ workload)
#   - Ninja (choco install ninja)
#   - CUDA Toolkit 12.4+ (NVIDIA redist archives, see build-spark/.github/actions/windows-setup-cuda)
#   - CUDA_PATH env var set to toolkit root

# From a developer command prompt (vcvarsall.bat x64):
cmake -S . -B build -G "Ninja Multi-Config" ^
  -DGGML_BACKEND_DL=ON ^
  -DGGML_NATIVE=OFF ^
  -DGGML_CPU=OFF ^
  -DGGML_CUDA=ON ^
  -DLLAMA_BUILD_BORINGSSL=ON
cmake --build build --config Release -j %NUMBER_OF_PROCESSORS% --target ggml-cuda

# Output: build/bin/Release/llama-server.exe
```

**Docker build (from `build-spark/cuda.Dockerfile`):**

```bash
docker build -f build-spark/cuda.Dockerfile -t azazael-llama-cuda .
docker run --gpus all azazael-llama-cuda /app/llama-server
```

**Install location (what the sidecar expects):**

```
C:\Users\clint\llama-server\bin\llama-b10964-cuda\llama-server.exe
```

The sidecar `BACKENDS` tuple already references this path (`tools/accelerator_sidecar.py:73-77`) and skips it if `is_file()` is False — so adding the binary is the only step needed to activate it.

## 2. Integrate into the Accelerator Chain

### `tools/accelerator_sidecar.py` (already done)

`BACKENDS` priority order:
1. `llama_cpp_vulkan` — `llama-b10964-vulkan/llama-server.exe` (Intel Arc via Vulkan — works today)
2. `llama_cpp_cuda` — `llama-b10964-cuda/llama-server.exe` (NVIDIA CUDA — ready, binary absent)
3. `llama_cpp_cpu` — `llama-b10964-cpu/llama-server.exe` (fallback — works today)

The sidecar spawns each backend in order, health-checks it (port open + real chat completion), and binds the first that passes. `/health` reports the actually-bound device, never aspirational.

### `tools/accelerator_preflight.py` (already generic)

Probes every `~/llama-server/bin/*/llama-server.exe` with `--list-devices`. A CUDA binary will auto-discover as `llama.cpp` origin with `Vulkan`/`CUDA` device lines. No code change needed.

### `src/eve_unleashed/core.py` (already correct)

Auto-detect priority: `CUDA > Intel XPU > Apple Metal > CPU`. On this box it resolves to XPU (via the 3.12 venv) or CPU; on a CUDA box it resolves to CUDA.

### `src/eve_unleashed/config.py`

`EveConfig.device` accepts `"cuda"`. `EveConfig.gpu_optimized()` sets `device="cuda"`. Runtime falls through if CUDA is unavailable.

## 3. Protocol Steps (codified)

```
STEP 1 — Provision CUDA hardware + toolkit on the target box.
STEP 2 — Build llama-server with -DGGML_CUDA=ON (see §1).
STEP 3 — Place binary at C:\Users\clint\llama-server\bin\llama-b10964-cuda\llama-server.exe.
STEP 4 — Restart the sidecar (or start it fresh): python tools/accelerator_sidecar.py
STEP 5 — Verify /health reports device=cuda, backend=llama_cpp_cuda.
STEP 6 — Run accelerator_bench.py against the sidecar to record prefill/decode tok/s.
STEP 7 — Compare CUDA numbers vs Vulkan/CPU baseline; the honest prior (iGPU shared
         aperture) does not apply to discrete CUDA — measure, don't assume.
STEP 8 — Update eve_unleashed default device to "cuda" if CUDA wins the benchmark.
```

## 4. Live Inferencing Test

When a CUDA binary and NVIDIA device exist:

```bash
# Start sidecar (will bind CUDA as first healthy backend)
python tools/accelerator_sidecar.py --port 18180

# In another shell, hit the sidecar directly
curl -X POST http://127.0.0.1:18180/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Say hello in one word"}],"max_tokens":8}'

# Benchmark CUDA vs baseline
python tools/accelerator_bench.py --base http://127.0.0.1:18180 --runs 3 --label "CUDA"

# Check sidecar health (device field must be the bound device)
curl http://127.0.0.1:18180/health
```

## 5. What Is NOT True on This Box (do not claim)

- `torch.cuda.is_available()` → False (no CUDA torch build, no NVIDIA device)
- `torch.xpu.is_available()` → True only in the py3.12 ComfyUI venv, not production py315t
- Any CUDA `llama-server.exe` → does not exist yet; must be built per §1
- Live CUDA inferencing → impossible without NVIDIA hardware

## Files Touched

- `tools/accelerator_sidecar.py:67-83` — added `llama_cpp_cuda` backend spec (already applied)
- `tools/accelerator_preflight.py` — generic binary probing (no change needed; CUDA binary auto-discovered)
- `src/eve_unleashed/core.py:372-385` — CUDA-first auto-detect (no change needed)
- `src/eve_unleashed/config.py:28-29,75-83` — `device` field + `gpu_optimized()` (no change needed)
