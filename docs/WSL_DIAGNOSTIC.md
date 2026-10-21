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

## WSL 3.15t Setup (verified 2026-10-21)

Python 3.15t lives at `/opt/python315t/bin/python3.15` (alias
`/usr/local/bin/python3.15t`). Use the existing venv `/root/py315t`
(do NOT create a new one; NOT system python3, which carries no ML stack).

```bash
source /root/py315t/bin/activate

# Packages verified on 3.15t free-threaded (torch 2.16.0 CPU, 2026-10-21):
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install numpy openvino nltk transformers

# GIL-only packages (no cp315t wheel) run on the sanctioned 3.14m sidecar:
# /root/venv-314-gil via /usr/local/bin/python3.14-gil (scrubs PYTHON_GIL).
# Never on a 3.14t build - 3.14t is retired/archived (2026-10-19).

# Verify
python -c "import torch; print('torch', torch.__version__)"
```

---

## Quick Install Steps

### Step 1: Use the 3.15t venv
```bash
wsl -d Ubuntu-26.04 "source /root/py315t/bin/activate && python --version"
```

### Step 2: Install packages
```bash
wsl -d Ubuntu-26.04 "bash -c 'source /root/py315t/bin/activate && pip install numpy openvino nltk torch transformers jupyterlab matplotlib'"
```

---

## After Install - Run Verification

```bash
wsl -d Ubuntu-26.04 "/opt/python315t/bin/python3.15 -c 'import sys; ft = hasattr(sys, \"_is_gil_enabled\") and not sys._is_gil_enabled(); print(f\"3.15t free-threading: {ft}\"); import torch; print(\"torch\", torch.__version__)'"
```
