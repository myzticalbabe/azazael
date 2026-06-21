---
name: azazael-python3.14-ml
description: Python 3.14 free-threading ML compatibility — which packages work, which don't, and how to work within 3.14t only.
---

# Python 3.14 Free-Threading ML Compatibility

## Critical Finding (May 28, 2026)

Python 3.14.5 free-threading breaks some ML/AI C extensions.
The free-threading ABI changes are incompatible with some compiled packages.

## Working ML Packages (4/24 tested)
| Package | Status |
|---------|--------|
| numpy | ✅ OK |
| torch (CPU) | ✅ OK |
| gymnasium | ✅ OK |
| langchain | ✅ OK |

## Broken ML Packages (20/24 tested)

### Segfault / Fatal Error
- onnx, onnxruntime, accelerate, tokenizers, gym

### Broken C Extensions
- scikit-learn, pandas, scipy, xgboost, lightgbm, numba

### Dependency Chain Failures
- transformers (regex C ext), ollama (pydantic_core), mlflow, peft, datasets

## Workaround Strategy

### For Development
All development uses Python 3.14.5t only. For ML code, use packages that are compatible:
- **numpy**, **torch (CPU)**, **gymnasium**, **langchain** — all work
- For incompatible packages, seek pure-Python alternatives or use containerized environments

### For .exe Builds
Build directly with Python 3.14.5t + Nuitka 4.1.2 (patched):
```bash
python -m nuitka --standalone --onefile --assume-yes-for-downloads module.py
```

### For Production
- Pure-Python or numpy/torch-only code works fine on 3.14t
- For heavy ML pipelines requiring scikit-learn/pandas/scipy, build cp314t wheels in WSL2 Ubuntu-26.04 using g++ (see `azazael/scripts/build/build_cp314t_wheel.sh`), or use Conda
- **WSL2 uses Python 3.14t exclusively.** Python 3.13 (system default on Ubuntu 26.04) is NOT used. Python 3.14t is at `/usr/local/python314t/bin/python3.14t`
- Track python.org for 3.14.x patches that fix C extension loading
- **Python 3.13 is not used anywhere.** All workloads run on 3.14t.
