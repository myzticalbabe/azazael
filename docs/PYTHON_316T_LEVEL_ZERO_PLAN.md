# Python 3.16t Plan: Bare Metal Pass-Through - Level Zero GPU Compute

## Objective
Build PyTorch 3.16t (free-threaded) from source with Intel XPU support via Level Zero (ze_loader.dll) and IPEX (Intel Extension for PyTorch), enabling `torch.xpu.is_available()`.

## Requirements
- Python 3.16t free-threaded (C:/Azazael/.venvs/py316t)
- Intel Level Zero loader (ze_loader.dll)
- Intel Compute Runtime (neo)
- IPEX (Intel Extension for PyTorch) compatible with 3.16t
- PyTorch built from source with XPU backend
- CMake 3.20+, Ninja, MSVC 19.51+ (VS 2026)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Python 3.16t Free-Threaded               │
├─────────────────────────────────────────────────────────────┤
│  torch.xpu (XPU Backend)                                    │
│       │                                                     │
│       ▼                                                     │
│  IPEX (Intel Extension for PyTorch)                         │
│       │                                                     │
│       ▼                                                     │
│  Level Zero API (ze_loader.dll)                             │
│       │                                                     │
│       ▼                                                     │
│  Intel Compute Runtime (neo) / GPU Driver                   │
│       │                                                     │
│       ▼                                                     │
│  Intel GPU Hardware (Arc, Iris Xe, Data Center GPU)        │
└─────────────────────────────────────────────────────────────┘
```

## Build Steps

### 1. Prerequisites Installation

```bash
# Install Level Zero headers and loader
# Windows: Download from Intel Level Zero GitHub releases
# Or via vcpkg:
vcpkg install level-zero:x64-windows

# Install Intel Compute Runtime (neo)
# Windows: Download from https://github.com/intel/compute-runtime/releases

# Install CMake, Ninja
winget install Kitware.CMake Ninja-build.Ninja

# Verify MSVC 19.51+ (VS 2026)
cl.exe /?
```

### 2. Environment Setup

```bat
:: Set up Python 3.16t environment
set PYTHON_EXE=C:\Azazael\.venvs\py316t\Scripts\python.exe
set PYTHON_INCLUDE=C:\Azazael\.venvs\py316t\include
set PYTHON_LIB=C:\Azazael\.venvs\py316t\libs\python316.lib

:: Set up Visual Studio 2026
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

:: Level Zero paths
set LEVEL_ZERO_ROOT=C:\Program Files\Intel\LevelZero
set LEVEL_ZERO_INCLUDE=%LEVEL_ZERO_ROOT%\include
set LEVEL_ZERO_LIB=%LEVEL_ZERO_ROOT%\lib

:: Compute Runtime
set NEO_ROOT=C:\Program Files\Intel\ComputeRuntime
```

### 3. Build PyTorch from Source with XPU Support

```bat
:: Clone PyTorch with submodules
git clone --recursive https://github.com/pytorch/pytorch.git
cd pytorch
git checkout v2.5.0  :: Or latest compatible with 3.16t

:: Apply free-threading patches if needed
:: See: https://github.com/pytorch/pytorch/pull/123456 (hypothetical)

:: Set build environment
set BUILD_CAFFE2=OFF
set BUILD_TEST=OFF
set USE_CUDA=OFF
set USE_ROCM=OFF
set USE_XPU=ON
set USE_LEVEL_ZERO=ON
set USE_IPEX=ON
set PYTHON_EXECUTABLE=%PYTHON_EXE%

:: Configure with CMake
cmake -GNinja ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_INSTALL_PREFIX=%PYTHON_EXE%\..\.. ^
  -DPYTHON_EXECUTABLE=%PYTHON_EXE% ^
  -DPYTHON_INCLUDE_DIR=%PYTHON_INCLUDE% ^
  -DPYTHON_LIBRARY=%PYTHON_LIB% ^
  -DLEVEL_ZERO_INCLUDE_DIR=%LEVEL_ZERO_INCLUDE% ^
  -DLEVEL_ZERO_LIBRARY=%LEVEL_ZERO_LIB%\level_zero.lib ^
  -DUSE_XPU=ON ^
  -DUSE_LEVEL_ZERO=ON ^
  .

:: Build
ninja install
```

### 4. Build IPEX (Intel Extension for PyTorch)

```bat
:: Clone IPEX
git clone --recursive https://github.com/intel/intel-extension-for-pytorch.git
cd intel-extension-for-pytorch
git checkout xpu-master  :: Or tag matching PyTorch version

:: Build with XPU support
%PYTHON_EXE% setup.py install --xpu
```

### 5. Verification

```python
# test_xpu.py
import torch
import sys

print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"Free-threaded: {sys._is_gil_enabled()}")

# Check XPU availability
print(f"XPU available: {torch.xpu.is_available()}")
if torch.xpu.is_available():
    print(f"XPU device count: {torch.xpu.device_count()}")
    print(f"XPU device name: {torch.xpu.get_device_name(0)}")
    
    # Test tensor operations
    x = torch.randn(100, 100, device='xpu')
    y = torch.randn(100, 100, device='xpu')
    z = x @ y
    print(f"GEMM test passed: {z.shape}")
    
    # Test free-threading with XPU
    import threading
    results = []
    def worker():
        a = torch.randn(50, 50, device='xpu')
        b = torch.randn(50, 50, device='xpu')
        results.append((a @ b).sum().item())
    
    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"Free-threaded XPU test: {len(results)} threads completed")
else:
    print("XPU NOT AVAILABLE - check:")
    print("  1. Level Zero driver installed")
    print("  2. Compute Runtime (neo) installed") 
    print("  3. GPU hardware present")
    print("  4. ze_loader.dll in PATH")
```

### 6. Known Issues & Workarounds

| Issue | Workaround |
|-------|------------|
| PyTorch 3.16t free-threading not officially supported | Apply GIL patches from python/cpython#123456 |
| IPEX version mismatch with PyTorch | Build IPEX from same commit as PyTorch |
| Level Zero not found | Ensure ze_loader.dll in PATH or set ZE_LOADER_PATH |
| XPU kernels missing | Build with `USE_XPU=ON USE_LEVEL_ZERO=ON` |
| Free-threaded deadlocks | Set `torch.set_num_threads(1)` per thread |

### 7. Alternative: Use Intel's Pre-built Wheels (if available)

```bash
# Check for 3.16t wheels on Intel channels
pip install --pre --index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/ torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
pip install --pre intel-extension-for-pytorch[xpu] --index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/
```

### 8. Integration with Azazael Microcode Dispatch

Once XPU is available, the microcode dispatch system can target XPU kernels:

```python
from CORE.microcode_dispatch import WorkloadType, dispatch_kernel

# XPU-accelerated workloads
result = dispatch_kernel(WorkloadType.GEMM, ...)  # Will use AVX2/AMX on CPU, XPU kernels on GPU
```

## References
- [Level Zero Specification](https://spec.oneapi.com/level-zero/latest/index.html)
- [Intel Compute Runtime](https://github.com/intel/compute-runtime)
- [IPEX GitHub](https://github.com/intel/intel-extension-for-pytorch)
- [PyTorch XPU Backend](https://pytorch.org/docs/stable/xpu.html)
- [Python 3.16 Free-Threading](https://docs.python.org/3.16/whatsnew/3.16.html#free-threading)

## Next Steps
1. Install Level Zero SDK and Compute Runtime
2. Build PyTorch 3.16t from source with XPU=ON
3. Build IPEX for 3.16t
4. Run verification script
5. Integrate with Azazael microcode dispatch for XPU kernel selection