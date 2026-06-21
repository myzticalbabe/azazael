# TensorFlow Build Guide for Python 3.14 / 3.14t

## Current Status (May 30, 2026)

### ✅ Working
- **tf-nightly (2.22.0.dev20260530) on Python 3.14 (non-free-threaded)**
  - cp314-cp314-manylinux_2_27_x86_64 wheel
  - Verified: `import tensorflow as tf; tf.reduce_sum(tf.random.uniform([10]))` works
  - GPU: CUDA not available on this system, CPU mode works
  - No GIL benefits (non-free-threaded)
  - Installed at: `/usr/local/lib/python3.14/site-packages/tensorflow/`

### ❌ Not Working
- **TensorFlow on Python 3.14t (free-threaded)**
  - No cp314t wheels exist for any TF variant (tensorflow, tf-nightly, tensorflow-cpu)
  - No patches available from TensorFlow team
  - Tracked in: [TF Issue #115828](https://github.com/tensorflow/tensorflow/issues/115828)
  - Root cause: PyObject struct layout changed in 3.14t (ob_tid added, ob_type at different offset)
  - Workaround attempts (all failed):
    1. LD_PRELOAD Py_GetVersion hook → bypasses pybind11 version check but segfaults on PyObject access
    2. LD_PRELOAD compat shim for _Py* symbols → provides renamed functions but struct layout still wrong
    3. Binary patching of .so files → corrupts C++ mangled symbols, no way to fix struct layout via patching
    4. Bazel source build → needs 16+ GiB RAM, tf-master source lacks free-threaded config

### ✅ Working on 3.14t
- PyTorch 2.12.0+cpu (cp314t wheel, GIL disabled verified)
- ONNX Runtime 1.26.0 (cp314t wheel)
- OpenVINO (cp314t .so found)

## Prerequisites

### System Requirements
- RAM: 8+ GiB (16+ GiB recommended for Bazel builds)
- Disk: 100+ GiB free (Bazel cache can grow large)
- OS: Linux x86_64
- Python: 3.14.5 (non-t) or 3.14.5 (t)

### Installed Tools
- Bazel 7.7.0
- GCC 15.2.0
- mold linker 2.40.4
- 32 GiB swap file created at /swapfile

## Option 1: Quick Install (Recommended)

### For Python 3.14 (non-free-threaded)
```bash
pip install tf-nightly
# Or from local wheel:
pip install /tmp/tf_nightly-2.22.0.dev20260530-cp314-cp314-manylinux_2_27_x86_64.whl
```

### For Python 3.14t (free-threaded)
Not possible yet. Use PyTorch instead:
```bash
pip install torch torchvision torchaudio
```

## Option 2: Source Build with Bazel

### Setup
```bash
cd /tmp/tf-master  # TF master source, May 2026

# Set up environment
export LD_LIBRARY_PATH=/usr/local/python314t-native/lib:$LD_LIBRARY_PATH
export BAZEL_LINKER=mold

# Configure for 3.14t
PYTHON_BIN_PATH=/usr/local/python314t-native/bin/python3.14 \
PYTHON_LIB_PATH=/usr/local/python314t-native/lib/python3.14t/site-packages \
USE_DEFAULT_PYTHON_LIB_PATH=1 \
python3 configure.py
```

### Build

> **Important**: You must run `python3 configure.py` (or `./configure`) in the source directory before any `bazel build` command. This generates `.tf_configure.bazelrc` which tells Bazel which Python version to use, what compiler flags to pass, and which optional features to enable.

```bash
# Build pip package (may take 1-2 hours)
bazel build \
  --local_ram_resources=4096 \
  --jobs=2 \
  --discard_analysis_cache \
  --nokeep_state_after_build \
  //tensorflow/tools/pip_package:build_pip_package

# Build specific targets for faster iteration
bazel build //tensorflow/python:pywrap_tensorflow
```

### Build for specific backends
```bash
# CPU only
bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package

# With MKL
bazel build --config=opt --config=mkl //tensorflow/tools/pip_package:build_pip_package

# Monolithic build (faster linking)
bazel build --config=opt --config=monolithic //tensorflow/tools/pip_package:build_pip_package

# Dynamic kernels (smaller binaries)
bazel build --config=opt --config=dynamic_kernels //tensorflow/tools/pip_package:build_pip_package
```

## Option 3: Bazel Alternatives

### No true alternative exists
TensorFlow's core build system is exclusively Bazel. There is no CMake, setuptools, or Makefile alternative for the main library. TensorFlow Lite has CMake support, but the full TF library does not.

### Remote Build Execution (RBE)
Offload compilation to cloud servers:
- [BuildBarn](https://buildbarn.io/) - Open source RBE
- [BuildBuddy](https://buildbuddy.io/) - Commercial RBE
- [EngFlow](https://www.engflow.com/) - Commercial RBE

### Docker-based builds
Use official TensorFlow build Docker images:
```bash
docker pull tensorflow/build:latest-python3.14
docker run -it tensorflow/build:latest-python3.14
```

### Use TensorFlow C API instead
For minimal deployments, use libtensorflow.so via ctypes/cffi:
```bash
pip install tensorflow-c-python  # Minimal C API bindings
```

### Remote Build Execution (RBE) Options
If you have access to cloud resources, these services offload compilation:
- **[BuildBarn](https://buildbarn.io/)** — Open-source RBE compatible with Bazel
- **[BuildBuddy](https://buildbuddy.io/)** — Commercial RBE with free tier, includes caching
- **[EngFlow](https://www.engflow.com/)** — Enterprise RBE with remote caching

### Memory-Constrained Build Tips
For machines with limited RAM (like this 7.4 GiB system):
```bash
bazel build \
  --local_ram_resources=4096 \          # Limit Bazel RAM usage to 4 GiB
  --jobs=2 \                             # Only 2 parallel compile jobs
  --discard_analysis_cache \             # Free analysis cache after loading
  --nokeep_state_after_build \           # Don't keep build state
  --experimental_ui_max_stdouterr_bytes=1 \  # Reduce UI memory
  //tensorflow/tools/pip_package:build_pip_package
```

### Docker-Based Builds
Use official TensorFlow build Docker images (pre-configured environments):
```bash
# Pull the latest Python 3.14 build image
docker pull tensorflow/build:latest-python3.14

# Run build inside container
docker run -it --rm \
  -v /tmp/tf-master:/tf/src \
  tensorflow/build:latest-python3.14 \
  bash -c "cd /tf/src && python3 configure.py && bazel build //tensorflow/tools/pip_package:build_pip_package"
```

## Binary Patching Workarounds (for reference)

All artifacts saved in /tmp/:
- `/tmp/py_version_hook.c` / `.so` - Py_GetVersion override for pybind11
- `/tmp/tf_compat.c` / `.so` - _Py* symbol compat shim
- `/tmp/tf_nightly-2.22.0.dev20260530-cp314-cp314-manylinux_2_27_x86_64.whl` - cp314 wheel

These can bypass the pybind11 version check and provide renamed symbols, but CANNOT fix the fundamental PyObject struct layout incompatibility in 3.14t.

## Environment Verification

```bash
# Check Python version and ABI
python3 -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))"

# Check supported wheel tags
python3 -c "from packaging import tags; [print(t) for t in tags.sys_tags()]"

# Check TF installation
python3 -c "import tensorflow as tf; print(tf.__version__)"

# Check PyTorch installation
python3 -c "import torch; print(torch.__version__)"
```

## Related Files
- `/tmp/tf-master/` - TF master source (WORKSPACE, requirements_lock_3_14.txt)
- `/tmp/tf_compat.c` / `.so` - LD_PRELOAD compat shim
- `/tmp/py_version_hook.c` / `.so` - LD_PRELOAD version hook
- `/usr/local/python314t-native/` - Python 3.14.5t installation
- `/usr/local/lib/python3.14/` - Python 3.14.5 (non-t) installation
