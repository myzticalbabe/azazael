# WSL Ubuntu Module Diagnostic & Install

> **3.14 RETIRED 2026-10-19 (Windows production).** Windows production is
> `C:\Azazael\.venvs\py315t`; the only sanctioned 3.14 runtime is
> `C:\Azazael\.venvs\py314m`. The WSL paths below are a record of the
> 2026-09 state and are not the Windows runtime.
>
> **Python 3.14t path in WSL:** `/usr/local/python314t/bin/python3.14t`
> **Python 3.13 is NOT used in WSL.** All WSL workloads use 3.14t free-threading.

## Current Status

### WSL Ubuntu-26.04 3.14t (packages)
- nltk
- numpy
- openvino
- torch (CPU)
- transformers
- scikit-learn, scipy, pandas, matplotlib (via cp314t wheels)

### ONNX Status on 3.14t
ONNX/ONNX Runtime does NOT have cp314t wheels and segfaults on Windows 3.14t.
In WSL, ONNX may work if built from source with g++.

### Windows 3.14t (cp314t verified)
| Package | Status |
|---------|--------|
| numpy | ✅ cp314t wheel works |
| torch (CPU) | ✅ cp314t wheel works |
| openvino | ✅ cp314t wheel works |
| nltk | ✅ pure Python, no wheel issue |
| onnx | ❌ segfaults on 3.14t |
| onnxruntime | ❌ segfaults on 3.14t |
| scikit-learn | ❌ no cp314t wheel |
| scipy | ❌ no cp314t wheel |
| pandas | ❌ no cp314t wheel |

---

## WSL 3.14t Setup

Python 3.14t is already installed at `/usr/local/python314t/bin/python3.14t`.
Create a 3.14t venv:

```bash
# Create 3.14t venv (NOT system python3 which is 3.13)
/usr/local/python314t/bin/python3.14t -m venv ~/azazael_314t
source ~/azazael_314t/bin/activate

# Install packages that work on 3.14t
pip install numpy openvino nltk
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers

# For ONNX — build from source in WSL with g++:
pip install onnx --no-binary :all:

# Verify
python -c "import torch, transformers, nltk, openvino, numpy; print('OK')"
```

---

## Quick Install Steps

### Step 1: Create 3.14t venv
```bash
wsl -d Ubuntu-26.04 "/usr/local/python314t/bin/python3.14t -m venv ~/azazael_314t"
```

### Step 2: Install packages
```bash
wsl -d Ubuntu-26.04 "bash -c 'source ~/azazael_314t/bin/activate && pip install numpy openvino nltk torch transformers jupyterlab matplotlib'"
```

---

## After Install - Run Verification

```bash
wsl -d Ubuntu-26.04 "/usr/local/python314t/bin/python3.14t -c 'import sys; ft = hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled(); print(f"3.14t free-threading: {ft}"); import torch, transformers, nltk, openvino, numpy; print(\"3.14t modules OK\")'"
```
