# Azazael Ubuntu 25.10 Bare Metal Install Guide

## Overview
- **Target OS**: Ubuntu 25.10 (arm64/x86_64)
- **Python**: 3.13.x
- **Purpose**: AI/ML Development with Intel iGPU + NPU support

---

## Pre-Installation

### Required Files
| Location | Contents |
|----------|----------|
| `AZAZAEL_BOOT/linux-wheels/` | Python packages (.whl) |
| `AZAZAEL_BOOT/docs/` | Documentation |
| `AZAZAEL_BOOT/scripts/` | Post-install scripts |

---

## Step 1: Install Ubuntu 25.10

1. Download Ubuntu 25.10 ISO from https://cdimages.ubuntu.com/daily-live/current/
2. Create bootable USB with Rufus or Ventoy
3. Boot from USB and install Ubuntu
4. Partition scheme:
   - `/boot/efi` - 1GB (EFI System)
   - `/` - 50GB+ (Root)
   - `swap` - 16GB (if < 32GB RAM)
   - `/home` - Remaining

---

## Step 2: Copy Azazael Files

```bash
# After first boot, copy Azazael files from USB/storage
sudo mkdir /mnt/azazael
sudo mount /dev/sdb1 /mnt/azazael  # Adjust device as needed
cp -r /mnt/azazael/AZAZAEL_BOOT ~/
```

---

## Step 3: Install Python Packages

### Option A: From Local Wheels (Offline)

```bash
cd ~/AZAZAEL_BOOT/linux-wheels

# Install all compatible wheels
pip3 install --break-system-packages --no-deps *.whl

# Install additional required packages from PyPI
pip3 install --break-system-packages regex safetensors tokenizers

# Install torch and openvino
pip3 install --no-deps torch-2.10.0+cpu-cp313-cp313-manylinux_2_28_x86_64.whl
pip3 install --no-deps openvino-2025.4.1-20426-cp313-cp313-manylinux2014_x86_64.whl
```

### Option B: From PyPI (Online)

```bash
# Install core ML packages
pip3 install --break-system-packages torch numpy openvino

# Install remaining packages from local wheels
cd ~/AZAZAEL_BOOT/linux-wheels
pip3 install --break-system-packages --no-deps annotated_doc-0.0.4-py3-none-any.whl \
    anyio-4.12.1-py3-none-any.whl certifi-2026.1.4-py3-none-any.whl \
    click-8.3.1-py3-none-any.whl colorama-0.4.6-py2.py3-none-any.whl \
    filelock-3.24.0-py3-none-any.whl fsspec-2026.2.0-py3-none-any.whl \
    h11-0.16.0-py3-none-any.whl httpcore-1.0.9-py3-none-any.whl \
    httpx-0.28.1-py3-none-any.whl huggingface_hub-1.4.1-py3-none-any.whl \
    idna-3.11-py3-none-any.whl jinja2-3.1.6-py3-none-any.whl \
    joblib-1.5.3-py3-none-any.whl markdown_it_py-4.0.0-py3-none-any.whl \
    mdurl-0.1.2-py3-none-any.whl mpmath-1.3.0-py3-none-any.whl \
    networkx-3.6.1-py3-none-any.whl nltk-3.9.2-py3-none-any.whl \
    openvino_telemetry-2025.2.0-py3-none-any.whl packaging-26.0-py3-none-any.whl \
    pygments-2.19.2-py3-none-any.whl rich-14.3.2-py3-none-any.whl \
    setuptools-82.0.0-py3-none-any.whl shellingham-1.5.4-py2.py3-none-any.whl \
    sympy-1.14.0-py3-none-any.whl tqdm-4.67.3-py3-none-any.whl \
    transformers-5.1.0-py3-none-any.whl typer-0.23.1-py3-none-any.whl \
    typer_slim-0.23.1-py3-none-any.whl typing_extensions-4.15.0-py3-none-any.whl
```

---

## Step 4: Verify Installation

```bash
python3 -c "
import torch; print('torch:', torch.__version__)
import numpy; print('numpy:', numpy.__version__)
import transformers; print('transformers:', transformers.__version__)
import openvino; print('openvino:', openvino.__version__)
import sympy; print('sympy:', sympy.__version__)
import networkx; print('networkx:', networkx.__version__)
print('All packages working!')
"
```

---

## Installed Packages

| Package | Version | Source |
|---------|---------|--------|
| torch | 2.10.0+cpu | local/pypi |
| numpy | 2.3.5 | local/pypi |
| scipy | 1.17.0 | pypi |
| pandas | 2.3.3 | pypi |
| scikit-learn | 1.8.0 | pypi |
| matplotlib | 3.10.8 | pypi |
| transformers | 5.1.0 | local |
| openvino | 2025.4.1 | local/pypi |
| xgboost | 3.2.0 | pypi |
| lightgbm | 4.6.0 | pypi |
| catboost | 1.2.8 | pypi |
| sympy | 1.14.0 | local |
| networkx | 3.6.1 | local |
| nltk | 3.9.2 | local |
| flask | 3.1.2 | pypi |
| fastapi | 0.129.0 | pypi |
| streamlit | 1.54.0 | pypi |
| gradio | 6.6.0 | pypi |
| opencv-python-headless | 4.13.0 | pypi |
| albumentations | 2.0.8 | pypi |
| scikit-image | 0.26.0 | pypi |
| seaborn | 0.13.2 | pypi |
| plotly | 6.5.2 | pypi |
| bokeh | 3.8.2 | pypi |
| mlflow | 3.9.0 | pypi |
| optuna | 4.7.0 | pypi |
| ray | 2.53.0 | pypi |
| spacy | 3.8.11 | pypi |
| textblob | 0.19.0 | pypi |
| gensim | 4.4.0 | pypi |

---

## Hardware Acceleration (Optional)

### Intel GPU/NPU Support
```bash
# Install Intel drivers
sudo apt install intel-opencl-icd intel-npu-driver

# Verify
clinfo | grep -i intel
```

---

## Quick Commands

```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list | grep -E "torch|numpy|transformers|openvino"

# Test import
python3 -c "import torch; print(torch.__version__)"
```

---

**Generated**: 2026-02-17

---

## Update Log

### 2026-02-17 - Initial Migration
- Migrated from Windows Azazael to Ubuntu 25.10
- Python 3.14 → 3.13.7
- All core ML packages verified working
- Backup synced to external storage (7.1GB)

### 2026-02-17 - Documentation Expansion
- Added azazael_paper.tex (LaTeX for scientific papers)
- Added azazael_environment.xml (GNOME-compatible config)
- Updated chain-of-actions for .tex, .xml auto-append

### 2026-02-17 - Visual Representations & Auto-Populate
- Added VISUAL_REPRESENTATIONS.txt (12 diagram types)
- Added FULL_COMMAND_REFERENCE.txt (shell commands)
- Added CHAIN_OF_INFORMATION.txt (flow diagrams)
- Added INFORMATION_GENERATION.txt (instructions)
- Added COMPLIANCE_CHECK.txt (verification)
- Auto-populated all chain files with new entries

### 2026-02-17 - ML Frameworks Installed
- scipy: 1.17.0
- pandas: 3.0.1
- matplotlib: 3.10.8
- scikit-learn: 1.8.0
- pillow: 12.1.1
- xgboost: 3.2.0
- lightgbm: 4.6.0
- catboost: 1.2.8
- Wheels downloaded to linux-wheels/

### 2026-02-17 - Full Stack Installation
- Web Serving: flask, fastapi, streamlit, gradio
- CV: opencv-python-headless, albumentations, scikit-image
- Viz: seaborn, plotly, bokeh
- MLOps: mlflow, optuna, ray
- NLP: spacy, textblob, gensim

### 2026-02-17 - Hardware Acceleration Challenge Map
- Created HARDWARE_ACCELERATION.txt
- Mapped GPU options: Intel OpenCL ✅, OneDNN ✅, CUDA ❌

### 2026-02-17 - Dependency Tree Analysis Added
- Added pipdeptree: 2.30.0
- Generated DEPENDENCY_TREE.txt
- Added step 7: Dependency Tree Analysis to chain-of-actions
