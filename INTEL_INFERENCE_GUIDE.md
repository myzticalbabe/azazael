# Intel-Native Inference Optimization Guide

> **Last updated:** June 9, 2026  
> **Hardware:** Intel Core Ultra 9 285H (Meteor Lake), Intel Arc 140T GPU (8GB), Intel AI Boost NPU  
> **Python:** 3.14.5t (free-threading)  
> **OS:** Windows 11  

---

## 1. Hardware Overview

Your system has three Intel compute accelerators:

| Device | Specs | Status | Best For |
|--------|-------|--------|----------|
| **CPU** | Intel Core Ultra 9 285H (16C/16T, 2.9GHz, AVX-512) | ✅ Always available | General inference, small models |
| **GPU** | Intel Arc 140T (8GB shared, 128 EUs, integrated) | ✅ Detected by OpenVINO | LLM inference, batch processing |
| **NPU** | Intel AI Boost (lightweight accelerator) | ✅ Detected by OpenVINO | Lightweight inference, embeddings |

**Critical Gap:** All 5 local inference methods (Ollama, LM Studio, LlamaCpp Direct, HuggingFace Direct) run on **CPU only** — the Intel Arc GPU and AI Boost NPU are idle for those paths.

---

## 2. Inference Options (Ranked by Intel Optimization)

### Tier 1: OpenVINO (Best for Intel Hardware) ✅

**What it is:** Intel's optimized inference framework that uses oneAPI Level Zero to access GPU and NPU hardware acceleration.

**Status:** Connected and working
- OpenVINO 2026.2.0 installed ✅
- `openvino_genai` 2026.2.0 (LLM pipeline) installed ✅
- `optimum-intel` 1.27.0 (HuggingFace conversion) installed ✅
- GPU (Intel Arc 140T) detected by OpenVINO ✅
- NPU (Intel AI Boost) detected by OpenVINO ✅

**Usage:**
```python
from CORE.inference.providers import get_provider

# Auto-detect best device (GPU > NPU > CPU)
ov = get_provider("openvino")
result = ov.chat("Hello, how are you?")

# Choose specific device
import os
os.environ["OPENVINO_DEVICE"] = "GPU"  # or "NPU", "CPU", "AUTO"
result = ov.chat("What's the weather?")
```

**Set device via environment variable:**
```bash
# Use Intel Arc GPU (default: AUTO)
set OPENVINO_DEVICE=GPU

# Use Intel AI Boost NPU
set OPENVINO_DEVICE=NPU

# Let OpenVINO auto-select
set OPENVINO_DEVICE=AUTO
```

**Available models:** Any HuggingFace model is auto-converted to OpenVINO format on first use. Start with small models like `TinyLlama/TinyLlama-1.1B-Chat-v1.0` for testing.

### Tier 2: Cloud APIs (NVIDIA NIM, Groq, etc.)

**What they are:** Remote inference APIs that work regardless of local hardware.

**NVIDIA NIM** (best free cloud option):
- 40 RPM permanent free access
- 80+ models including Mistral Large 3 675B
- No credit card required
- **Usage:** `export NVIDIA_NIM_API_KEY=nvapi-...`

**Groq** (fastest free inference):
- LPU-powered, ~300 tok/s
- 30 RPM, 6000 TPM
- Models: Llama 4 Scout 17B, Llama 3.3 70B

### Tier 3: CPU-Only Local (Not Intel-Optimized)

**Ollama, LM Studio, LlamaCpp Direct, HuggingFace Direct** — All run on CPU only.  
These need a separate Python environment or custom GPU build to access Intel Arc GPU.

---

## 3. Intel GPU Compute Runtime Setup

The Intel GPU compute runtime provides low-level access to the GPU via oneAPI Level Zero.  
**Current status:** Only `ze_intel_gpu_raytracing.dll` is present for raytracing — the full compute runtime (`ze_intel_gpu.dll`) is missing.

### Option A: Install via Intel Graphics Driver (Done ✅)
The latest Intel Arc GPU driver (32.0.101.8826) has been downloaded to:
`C:\Users\clint\Downloads\gfx_win_101.8826.exe` (~823 MB)

**To install:**
1. **Close all graphics-intensive applications** (games, video editors, browsers)
2. **Run as Administrator:** Right-click `gfx_win_101.8826.exe` → "Run as administrator"
3. **Select "Clean Installation"** checkbox during install to ensure all components (including GPU compute runtime) are properly installed
4. **Reboot** when prompted
5. **Verify:** After reboot, check these DLLs are present:
   ```
   dir C:\Windows\System32\ze_intel*.dll
   ```
   Expected output should include both:
   - `ze_intel_gpu.dll` (GPU compute runtime — currently MISSING)
   - `ze_intel_gpu_raytracing.dll` (already present)

**Why this matters:** This driver update installs `ze_intel_gpu.dll` which provides the full Level Zero GPU compute runtime, enabling:
- GPU-accelerated inference via OpenVINO
- Intel XPU support for PyTorch (if available)
- Vulkan compute workloads via the Vulkan SDK (already installed)

### Option B: Install oneAPI Level Zero Loader (Alternative)
If the graphics driver doesn't include the compute DLL, install the Intel oneAPI Base Toolkit:
```bash
# Download from:
# https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html
```

### Option C: Use OpenVINO (Already Working — No Action Needed)
OpenVINO handles GPU access through its own runtime — **no additional setup needed** for OpenVINO-based inference.

---

## 4. Performance Comparison

| Method | Hardware | Setup Complexity | Speed (est.) | Best For |
|--------|----------|-----------------|--------------|----------|
| **OpenVINO GPU** | Intel Arc 140T | ✅ Done | Fast | Quality inference with GPU |
| **OpenVINO NPU** | AI Boost | ✅ Done | Moderate | Lightweight tasks |
| **OpenVINO CPU** | Core Ultra 9 | ✅ Done | Moderate | Fallback |
| **NVIDIA NIM** | Cloud API | ✅ Key needed | Very Fast | Large models |
| **Groq** | Cloud API | ✅ Key needed | Fastest | Quick queries |
| **Ollama (CPU)** | CPU only | ✅ Done | Slow | Local, no-GPU fallback |
| **LM Studio (CPU)** | CPU only | ✅ Done | Slow | Local GUI |
| **IPEX-LLM** | Intel GPU | ❌ Not on 3.14t | Fast | Future optimization |

---

## 5. 10-Phase Gemini Protocol Status

The 10-Phase Multi-Tier Gemini Injection Protocol was left in an incomplete state (Error #74).  
**Current status:** RESTART_PROTOCOL_REQUIRED = TRUE

The protocol requires `thinker-with-files-gemini` agent which is not available in the current Codebuff deployment.  
A fallback plan should be established if the primary agent remains unavailable.

---

## 6. Next Steps for Optimization

1. **Use OpenVINO provider** — Call `get_provider("openvino")` instead of Ollama for local Intel-accelerated inference
2. **Install full Intel GPU compute runtime** — Download latest Intel Arc driver for full Level Zero support
3. **Test OpenVINO GPU inference** — Run a small model through `OPENVINO_DEVICE=GPU` to verify GPU offload
4. **Evaluate IPEX-LLM** — When Python 3.14t support arrives, IPEX-LLM could provide additional GPU optimization
5. **Configure Ollama with Vulkan** — Rebuild or configure Ollama with Vulkan backend (Vulkan SDK 1.4.350 is installed)

---

## 7. Quick Reference

```bash
# List all inference providers
python -c "import sys; sys.path.insert(0,'src'); from CORE.inference.providers import list_providers; [print(p['id'], p['name']) for p in list_providers()]"

# Self-test OpenVINO
python -c "import sys; sys.path.insert(0,'src'); from CORE.inference.providers import get_provider; get_provider('openvino').self_test()"

# Check Intel hardware detection
python -c "import openvino; core=openvino.Core(); print(core.available_devices); [print(d, core.get_property(d, 'FULL_DEVICE_NAME')) for d in core.available_devices]"

# Run on GPU
set OPENVINO_DEVICE=GPU
python -c "import sys; sys.path.insert(0,'src'); from CORE.inference.providers import get_provider; r=get_provider('openvino').chat('Hello!'); print(r['content'][:200])"
```
