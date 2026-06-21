---
name: azazael-314t-insights
description: Discoveries from 3.14t migration — ABI incompatibility, g++ vs MSVC, ffmpeg workarounds, Go/Node safety, WSL2 compute strategy
metadata:
  category: environment
  project: azazael
---
# AZAZAEL 3.14t — Insights & Discoveries

> **Session:** 2026-05-28 | **Focus:** C++ vs g++ analysis, package rebuild, toolchain setup
> **Key Outcome:** g++ 15.2.0 (WSL2) confirmed as superior compiler for cp314t ABI extensions

---

## INSIGHT 1: cp314t ABI Is Fundamentally Incompatible with cp314

Python 3.14t free-threading uses different PyObject layouts and critical-section markers than standard Python 3.14. All 450 pre-built wheels on G:\AZAZAEL tagged `cp314` will NOT load on 3.14t. This means every C extension package must be rebuilt from source specifically for `cp314t`.

**Impact:** ~15 packages need rebuild for full AZAZAEL functionality.

---

## INSIGHT 2: g++ Builds 3x Faster Than MSVC for Large C++ Packages

Benchmark estimates for torch 2.10.0 (2000+ translation units):
- MSVC: ~61 minutes (52 min compile + 8 min link)
- g++ 15.2.0 + ninja: ~20 minutes (18 min compile + 2 min link)

This is due to ninja's superior parallel scheduling, GCC's faster template instantiation, and GNU ld's incremental LTO.

---

## INSIGHT 3: Windows Python Cannot Load Linux .so Files

Even though WSL2 can build cp314t extensions with superior performance, those `.so` files are ELF format and cannot be loaded by Windows CPython (which expects PE/COFF `.pyd`). The only paths for Windows-native extensions are:
1. MSVC (traditional, slower)
2. MinGW-w64 cross-compile (risky — UCRT segfaults)
3. Rust/PyO3 + maturin (safe, modern, memory-safe)

**Recommendation:** Heavy compute in WSL2 with ZMQ IPC; Rust/PyO3 for Windows-native where needed.

---

## INSIGHT 4: ffmpeg drawtext Is Broken on This Windows Build

Fontconfig segfaults when `drawtext` filter is used. Workaround: pure-Python 5×7 bitmap font rendered to PPM frames, piped to ffmpeg for encoding. This approach:
- Adds zero C extension dependencies
- Works identically on Windows and WSL
- Produces visually clean text at multiple scales
- ~265 lines of Python for 70+ ASCII characters

---

## INSIGHT 5: Go + Free-Threaded Python = Deadlock Risk

Goroutines and the Python 3.14t free-threaded runtime both manage their own thread pools. Direct CGo bridging between them risks:
- GOMAXPROCS vs Python thread count contention
- GC pause interference
- Lock ordering inversions

**Safe path:** Go builds c-shared libraries (`-buildmode=c-shared`), Python loads via `ctypes` with explicit GIL management. Even safer: ZMQ IPC between processes.

---

## INSIGHT 6: Node.js Native Addons Cannot Directly Serve Python

node-gyp builds V8 C++ addons (`.node` files). These are fundamentally incompatible with CPython's C API. Bridging via C++ leads to:
- Two garbage collectors (V8 + CPython) with no coordination
- Conflicting thread-local storage
- Undefined behavior in signal handling

**Safe path:** ZMQ IPC bridge. Node.js ↔ Python communication over sockets, not shared memory.

---

## INSIGHT 7: Torch Build from Source Requires Painstaking Dependency Management

The torch 2.10.0 CMake build has hard dependencies on many GPU-related submodules (Kineto, XPUPTI, SYCL) even for CPU-only builds. Each must be explicitly disabled:
```bash
USE_CUDA=0 USE_CUDNN=0 USE_KINETO=0 USE_XPU=0
```
Additionally, NNPACK requires the `peachpy` Python package for assembly code generation. The build must use the CORRECT Python (WSL `/usr/local/python314t/bin/python3`, NOT Windows Python).

---

## INSIGHT 8: 450 Wheels on G: Need cp314t Audit

The G:\AZAZAEL wheel repository is structured for cp314, not cp314t. Each wheel's compatibility tag must be checked:
- `cp314` wheels → incompatible, needs rebuild
- `cp314t` wheels → compatible (rare — only numpy, zmq, regex, openvino found)
- `none-any` wheels → compatible (pure Python, no ABI dependency)

---

## INSIGHT 9: Mermaid Diagram Videos Provide Architecture Visibility

Converting 10 Mermaid HTML diagrams to bitmap-font .mp4/.wmv videos makes architecture documentation accessible without a browser. The diagram videos (25-36KB each) complement the 11 full architecture videos for a total of 42 deliverables.

---

## INSIGHT 10: WSL2 Is the Strategic Compute Layer

The optimal AZAZAEL architecture splits compute:
- **Windows 11 Host:** Lightweight orchestration (numpy, zmq, yaml, regex)
- **WSL2 Ubuntu:** Heavy compute (torch, scipy, opencv, sklearn)
- **IPC:** ZMQ sockets for low-latency (<100μs) cross-boundary communication

This avoids the cp314t/.pyd problem entirely for heavy packages while leveraging g++'s superior build and runtime performance.

