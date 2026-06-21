# Torch cp314t Build Troubleshooting Guide

> Build target: torch 2.10.0 for Python 3.14t cp314t ABI
> Environment: WSL2 Ubuntu 26.04, g++ 15.2.0

## Build Attempts & Errors (2026-05-28)

### Attempt 1: Missing submodules
```
ERROR: Could not find CMakeLists.txt in third_party/googletest
FIX: git submodule update --init --recursive
```

### Attempt 2: Kineto/XPUPTI dependency
```
ERROR: Could not find PtiConfig.cmake
FIX: USE_KINETO=0 added to build flags
```

### Attempt 3: SYCL toolkit detection
```
ERROR: Can not run SYCL_CMPLR_TEST
FIX: USE_XPU=0 added to build flags
```

### Attempt 4: Missing peachpy
```
ERROR: ModuleNotFoundError: No module named 'peachpy'
FIX: pip3 install peachpy (but peachpy itself may fail on 3.14t)
```

### Attempt 5: PATH pollution from Windows
```
ERROR: PATH contains Windows paths (C:/Program Files/Git/...)
FIX: Use clean WSL session: wsl -e bash -c '...'
```

## Known Working Flags
```bash
USE_CUDA=0 USE_CUDNN=0 USE_KINETO=0 USE_XPU=0 \
USE_MKLDNN=1 USE_NNPACK=1 USE_QNNPACK=1 USE_XNNPACK=1 \
BLAS=OpenBLAS MAX_JOBS=8
```

## Clean Build Command (for next attempt)
```bash
# In a CLEAN WSL session (no Windows PATH):
wsl -e bash -c '
export PATH=/usr/local/python314t/bin:/usr/bin:/bin
export PYTHONPATH=
cd /tmp/pytorch
rm -rf build dist *.egg-info
pip3 install --break-system-packages peachpy pyyaml typing_extensions numpy
python3 setup.py bdist_wheel
'
```

## Alternative: Disable NNPACK
If peachpy cannot be installed on 3.14t:
```bash
USE_NNPACK=0  # Disables NNPACK (uses default BLAS fallback)
```

## Alternative: Use conda/pip nightly
Check if PyTorch has nightly cp314t builds:
```bash
pip3 install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu
```
