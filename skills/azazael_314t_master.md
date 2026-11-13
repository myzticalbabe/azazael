---
name: azazael-314t-master
description: Master reference for Python 3.14t free-threading setup — paths, package status, compiler strategy, video generation, WSL2 integration
metadata:
  category: environment
  project: azazael
---
# AZAZAEL 3.14t — Master Skill & Memory File
> **Generated:** 2026-05-28 | **Updated:** 2026-05-28 (v2)
> **Python:** 3.14.5 free-threading (cp314t ABI) | **Hardware:** Intel 16-core CPU (no GPU)
> **OS:** Windows 11 + WSL2 Ubuntu 26.04 | **Compiler:** g++ 15.2.0
> **This file is AI agent memory — /skill azazael-314t-master**
---
## QUICK REFERENCE
| Resource | Value |
|----------|-------|
| Windows Python 3.14t | `C:/Users/clint/.local/bin/python3.14t.exe` |
| WSL Python 3.14t | `/usr/local/python314t/bin/python3` |
| AZAZAEL venv | `C:/Users/clint/azazael/.venv-3.14t/Scripts/python.exe` |
| Critique videos | `Desktop/AZAZAEL_Standalone/Critique/videos/` |
| G: Wheels (450) | `G:\AZAZAEL\*.whl` |
| G: cp314t Wheels | `G:\AZAZAEL\cp314t_wheels\` |
| Source-of-Truth | `G:\AZAZAEL\SOURCE_OF_TRUTH_2026-05-28.md` |
| Build Scripts | `azazael/scripts/build/` |
| Documentation | `azazael/docs/` |
## DELIVERABLE STATUS (Complete ✅)
| Deliverable | Count | Format |
|-------------|-------|--------|
| Architecture Videos | 11 | .mp4 + .wmv |
| Mermaid Diagram Videos | 10 | .mp4 + .wmv |
| Mermaid HTML Diagrams | 10 | .html |
| Original HTML Templates | 26 | .html |
| Dissertation HTML | 1 | .html (auto-scroll) |
| **Total Videos** | **42** | 21 .mp4 + 21 .wmv |
## PACKAGE STATUS (Python 3.14t cp314t)
### ✅ Working (Windows native)
`numpy` 2.4.6 | `Pillow` | `PyYAML` 6.0.3 | `PyZMQ` 27.1.0 | `regex` 2026.4.4 | `openvino` 2026.1.0 | `onnx` 1.21.0 | `ml_dtypes` 0.5.4 | `protobuf` 7.35.0 | `typing_extensions` 4.15.0
### ❌ Broken (needs cp314t rebuild via g++)
`torch` | `torchvision` | `torchaudio` | `scipy` | `opencv-python` | `scikit-learn` | `pandas` | `matplotlib` | `lxml`
### 🔧 WSL Working
`torch` 2.12.0+cu130 (WSL Python 3.14t)
## KEY ARCHITECTURAL DECISIONS
### 1. g++ > MSVC for C Extensions
- 3x faster builds, 20% better numerical throughput
- Better auto-vectorization (AVX2, FMA)
- Lower atomics contention latency in free-threaded mode
- **Strategy:** WSL2 g++ for heavy compute; Rust/PyO3 for Windows-native .pyd
### 2. Pure-Python Bitmap Font for Video
- ffmpeg `drawtext` segfaults (fontconfig broken on Windows)
- Custom 5×7 pixel font in `bitmap_font.py` (70+ chars, zero deps)
- PPM frames → ffmpeg pipe for encoding
### 3. cp314t ≠ cp314 ABI
- Python 3.14t has different PyObject layout, critical section markers
- All 450 G: wheels tagged `cp314` are incompatible with 3.14t
- Must rebuild from source for `cp314t` ABI tag
### 4. Go & Node.js Integration
- **Go 1.26.3**: c-shared libraries via Python `ctypes`; ZMQ IPC for goroutine safety
- **Node.js v24**: ZMQ IPC bridge; do NOT bridge C++ extensions directly
- **node-gyp 12.3.0**: Available for native addons but use IPC for Python interop
## FILE MAP (Key Files)
```
azazael/
├── scripts/
│   ├── bitmap_font.py              # 5×7 pixel font (265 lines)
│   ├── video_frame_generator.py    # Frame → ffmpeg (421 lines)
│   ├── master_generate.py          # Video orchestration (156 lines)
│   └── build/
│       └── build_cp314t_wheel.sh   # WSL wheel builder
├── skills/
│   └── azazael_314t_master.md      # THIS FILE
├── docs/
│   ├── CPP_VS_GPP_EXTENSION_ANALYSIS.md  # 9.3KB deep analysis
│   └── VIDEO_GENERATION_PROTOCOL.md
└── templates/video/                # JSON video templates
Desktop/AZAZAEL_Standalone/
├── Critique/
│   ├── videos/                     # 42 files (21 .mp4 + 21 .wmv)
│   ├── mermaid/                    # 10 .html diagrams
│   └── html/                       # 26 templates + dissertation
├── TODO_314t.md                    # General tasks
└── TODO_GPP_NATIVE.md              # g++ package upgrade plan (4.6KB)
## COMMON COMMANDS
```bash
# Windows Python 3.14t
/c/Users/clint/.local/bin/python3.14t.exe -c "import numpy; print('OK')"
# WSL Python 3.14t
wsl /usr/local/python314t/bin/python3 -c "import torch; print(torch.__version__)"
# Generate videos
cd /c/Users/clint && python azazael/scripts/master_generate.py
# Build cp314t wheel in WSL
wsl bash /mnt/c/Users/clint/azazael/scripts/build/build_cp314t_wheel.sh
# Check Go
/c/Program\ Files/Go/bin/go.exe version
# Check node-gyp
node-gyp --version
## LESSONS LEARNED
1. **ffmpeg drawtext on Windows is unreliable** — fontconfig segfaults. Use subtitle filter or bitmap fonts.
2. **Python 3.14t ABI `cp314t` is NOT `cp314`** — all C extensions need rebuild.
3. **WSL2 g++ builds 3x faster than MSVC** for large C++ codebases like torch.
4. **Pure Python can replace C extensions** for simple tasks (bitmap fonts, video framing).
5. **ZMQ is the safest IPC bridge** between Windows and WSL Python processes.
6. **Go goroutines + free-threaded CPython = deadlock risk** — use ctypes or IPC, not shared memory.
7. **Always `git submodule update --init --recursive`** before building torch from source.
8. **winget is available** on this system for package installation.
9. **Node.js v24 on Windows, v22 on WSL** — version skew is acceptable via IPC.
10. **450 wheels on G: are cp314, not cp314t** — all need auditing.
## NEXT PRIORITY ACTIONS
1. Complete torch cp314t build in WSL (submodule init + setup.py bdist_wheel)
2. Build scipy, opencv, sklearn in WSL for cp314t
3. Set up ZMQ IPC bridge between Windows AZAZAEL and WSL compute
4. Audit all 450 G: wheels for cp314t compatibility
5. Prototype Rust/PyO3 Windows-native .pyd
> RETIRED 2026-10-19 — describes `C:/Users/clint/.local/bin/python3.14t.exe` and `.venv-3.14t`, both gone.
> Production is 3.16t (`C:/Azazael/.venvs/py316t`); `C:/Azazael/.venvs/py314m` is the only 3.14 fallback.
> Kept as provenance, not callable.
> Production is 3.15t (`C:/Azazael/.venvs/py315t`); `C:/Azazael/.venvs/py314m` is the only 3.14 fallback.
