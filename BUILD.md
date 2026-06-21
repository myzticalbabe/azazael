# AZAZAEL Build Guide — Python 3.14t

## Prerequisites

- Windows 11 (or Windows 10 22H2+)
- Python 3.14.5 free-threading (from python.org)
- Git for Windows

## Quick Start

```bash
# 1. Clone and enter
git clone <repo> azazael
cd azazael

# 2. Create virtual environment
python -m venv .venv314t
.venv314t\Scripts\activate

# 3. Install dependencies (what works on 3.14t)
pip install pyinstaller numpy torch gymnasium langchain pillow

# 4. Build all .exe files
python build_all_314t.py

# 5. Output in G:/AZAZAEL_Standalone/
```

## Building Individual .exe

```bash
python -m PyInstaller --onefile --noconfirm \
  --exclude-module psutil --exclude-module torch \
  --exclude-module matplotlib --exclude-module zmq \
  --exclude-module bcrypt --exclude-module win32com \
  --name=ModuleName_314t \
  --distpath=G:/AZAZAEL_Standalone \
  src/path/to/module.py
```

## Known 3.14t Incompatibilities

| Package | Status | Workaround |
|---------|--------|------------|
| scikit-learn | Broken | Use .bat launcher |
| transformers | Broken (regex C ext) | Use .bat launcher |
| xgboost | Broken | Use .bat launcher |
| ONNX Runtime | Broken | Use .bat launcher |
| Nuitka | Works (patched) | Apply patches via `patch_nuitka_314t.py` |
| psutil | Broken in PyInstaller isolation | --exclude-module psutil |
| zmq | Broken (cython) | --exclude-module zmq |
| matplotlib | Broken (circular import) | --exclude-module matplotlib |
| bcrypt | Broken (C ext) | --exclude-module bcrypt |
| win32com | Broken in isolation | --exclude-module win32com |

## Archive

(Previously archived Python 3.13 .exe files at `G:/archived_files/AZAZAEL_313_EXE_<timestamp>/` — legacy, all builds now on 3.14t)
