---
name: azazael-eve-unleashed
description: Eve Unleashed standalone desktop app — local AI inferencing with Python REPL, system monitor, multi-backend benchmarks. Build, deploy, and feature guide.
---

# Eve Unleashed — Standalone Desktop App

**Version:** 1.0.0 | **Built:** May 29, 2026 | **EXE:** `Eve_Unleashed_314t.exe` (10.2 MB)

## Overview

Eve Unleashed is a standalone Tkinter desktop application that provides:
- **Multi-backend AI inferencing** — Ollama, llama.cpp, transformers backends with auto-discovery
- **Python REPL** — Embedded Python interpreter for local environment interaction with variable tracking
- **System Monitor** — Real-time CPU, RAM, disk I/O, network throughput
- **Benchmark Runner** — Unified multi-backend benchmark with latency and tokens/sec reporting

## Architecture

```
eve_unleashed_app.py          # Main entry point (Tkinter GUI)
├── BackendDiscoverer         # Discovers Ollama, llama.cpp, transformers, etc.
│   └── run_inference()       # Real inference with auto-fallback to simulated
├── PythonREPL                # Sandboxed Python interpreter
│   └── execute(code)         # eval/exec with stdout capture + variable tracking
├── SystemMonitor             # psutil-based system metrics collector
│   └── get_metrics()         # CPU, RAM, disk, network, uptime
└── EveUnleashedApp           # Tkinter GUI with 4 tabs
    ├── Inference tab         # Backend selector, prompt input, response display
    ├── Python REPL tab       # Code editor + output, Ctrl+Enter to run
    ├── System Monitor tab    # 4 metric cards + system info bar, auto-poll 2s
    └── Benchmarks tab        # TreeView results, run across all backends
```

## Build Command

```bash
# Requirements: Python 3.14t venv (~/venv-314t), Nuitka 4.1.2+
# --nofollow-import-to=transformers is REQUIRED: Nuitka's transformers plugin
# crashes on this machine's broken transformers install (FATAL plugin issue, 2026-08-27).
cd ~/Desktop/AZAZAEL_Standalone
~/venv-314t/Scripts/python.exe -m nuitka --standalone --onefile \
  --assume-yes-for-downloads \
  --enable-plugin=tk-inter \
  --nofollow-import-to=transformers \
  --nofollow-import-to=torch \
  --output-filename=Eve_Unleashed_314t.exe \
  C:/Users/clint/Desktop/EveUnleashed_Selector/eve_unleashed_app.py
```

## Features

### 1. Inference Tab
- Auto-discovers backends: Ollama (via `ollama` package), llama-cpp-python (GGUF models), llama-server SYCL, transformers
- Real inference with measured latency and tokens/sec
- Graceful fallback to simulated responses when no backend is reachable
- Backend test button for quick connectivity check

### 2. Python REPL Tab
- Full Python interpreter with `exec()` and `eval()` support
- Stdout/stderr captured and displayed in output pane
- Variable tracking — "Show Vars" displays user-defined namespace variables
- Pre-loaded imports: `sys`, `os`, `Path`, `json`, `time`, `datetime`
- Keyboard shortcut: `Ctrl+Enter` to execute

### 3. System Monitor Tab
- 2x2 metric grid: CPU %, Memory (used/total GB), Disk I/O (R/W MB/s), Network (↓↑ KB/s)
- Color-coded thresholds: green < 50%, yellow < 85%, red > 85%
- System info bar: hostname, OS, uptime, process/thread count, Python 3.14t status
- Auto-refresh every 2 seconds via background thread

### 4. Benchmarks Tab
- 5 predefined test prompts (reasoning, safety, architecture, training, learning)
- Runs across all available backends
- TreeView results: backend, test name, latency (ms), tokens/sec, status
- Color-coded: green = real inference, yellow = simulated, red = error
- Summary bar with real/simulated/error counts
- **🌐 Benchmark All Models mode (added 2026-08-27):** auto-discovers every model on every backend (Ollama via package/REST, GGUF files on disk), runs the canonical 5-prompt suite per model (reasoning/coding/summary/creative/math, 512 tokens), swaps a dedicated llama.cpp server per GGUF, streams rows into the TreeView live. Double-run guarded.

## Verified Model Benchmarks (2026-08-27)

> Hardware: Intel Core Ultra 9 285H (16 cores) + Intel Arc 140T iGPU (8 GB shared) + 15.4 GB RAM.
> Suite: 5 prompts (reasoning, coding, summary, creative, math), max_tokens 512, temp 0.7.
> GGUF backend: llama.cpp Vulkan (Jan backend b9967), `-ngl 99 -c 4096 -t 8`. Ollama backend: REST /api/generate.

### Ollama models (20/20 real, 0 errors)

| Model | Avg latency | Avg t/s | Peak t/s |
|---|---|---|---|
| **llama3.2:1b** ⭐ best | 4,922 ms | **44.2** | 46.0 |
| gemma2:2b | 7,978 ms | 27.2 | 28.0 |
| gemma3:4b | 10,324 ms | 21.5 | 23.0 |
| eve-unleashed:latest | 31,114 ms | 18.5 | 18.6 (always emits full 512 tokens) |

### LM Studio GGUF models (6/6, swap-benchmarked one at a time)

| Model | Avg t/s | Load | Notes |
|---|---|---|---|
| **gemma-4-E2B-it (Q4_K_M)** 🥇 fastest | **28.2** | 4.6 s | |
| Qwen3-4b-Z-Image-Engineer-V4 (Q4_K_S) | 23.2 | 6.6 s | |
| **gemma-4-E4B-it (Q4_K_M)** ⭐ balance | 17.9 | 10.6 s | best capability/speed |
| Llama3.3-8B-Thinking-Heretic-Uncensored (i1-Q4_K_S) | 14.7 | 12.6 s | uncensored; terse outputs |
| gemma-4-E4B-it (IQ4_XS) | 11.8 | 8.6 s | slower than its Q4_K_M twin (anomaly, re-test) |
| Qwen3.5-9B (Q4_K_M) | 10.9 | 14.6 s | thinking model, burns all 512 tokens |

**Guidance:** E2B when latency matters, E4B Q4_K_M as daily driver, Qwen3.5-9B for quality, Llama3.3-8B-Heretic for uncensored at 8B (a 27B uncensored, e.g. Qwen3.8-27B, does NOT fit in 15.4 GB shared RAM — see known issues).

**Artifacts:** `Desktop/EveUnleashed_Selector/logs/inference_test_results_2026-08-27.json`, `logs/gguf_benchmark_results_2026-08-27.json`, `logs/gguf_benchmark_2026-08-27.log`.

## Themes
- **Obsidian** (default) — Dark GitHub-style with blue accent
- **Aurora** — Deep navy with cyan accent
- **Midnight** — Near-black with purple accent
- Dynamic switching via theme buttons in title bar

## Dependencies

| Package | Required | Purpose |
|---------|----------|---------|
| `tkinter` | **Yes** | GUI framework |
| `psutil` | Recommended | System metrics |
| `ollama` | Optional | Ollama backend inference |
| `llama-cpp-python` | Optional | Local GGUF inference |
| `transformers` | Optional | HuggingFace backend |
| `torch` | Optional | ML framework |
| `Pillow` | Optional | Image processing |
| `requests` | Optional | HTTP backend calls |

## Known Issues

1. **Unicode on Windows console** — Fixed with `sys.stdout.reconfigure(encoding='utf-8')` at startup
2. **Nuitka transformers plugin crash** — Use `--nofollow-import-to=transformers --nofollow-import-to=torch` (see build command); `patch_nuitka_314t.py` no longer required with Nuitka 4.1.2
3. **GGUF model discovery** — FIXED 2026-08-27: now scans `~/.lmstudio/models` first; Ollama discovery falls back to REST `/api/tags` when the `ollama` package is missing (0 → 14 models found)
4. **Simulated fallback** — When no backend is reachable, returns `[SIMULATED:...]` placeholder responses
5. **IPEX-SYCL llama.cpp build broken on this machine** — `llama-server/bin/ipex-sycl/.../llama-server.exe` fails to load `api-ms-win-crt-filesystem-l1-1-0.dll`; use the Jan Vulkan backend b9967 instead (`AppData/Roaming/Jan/data/llamacpp/backends/b9967/win-vulkan-common_cpus-x64/build/bin/llama-server.exe`)
6. **Memory ceiling** — 15.4 GB shared RAM (iGPU has no private VRAM): dense models above ~14B Q4 will not fit; 27B quant thrashes swap at <1–2 t/s

## Integration

- **build_all.py** — Listed in Tier 3 (CODEX Analysis) with `NEEDS_TKINTER` flag
- **Desktop path** — `~/Desktop/AZAZAEL_Standalone/Eve_Unleashed_314t.exe`
- **Source** — `~/Desktop/EveUnleashed_Selector/eve_unleashed_app.py` (external project, not in src)
- **Skills directory** — This file at `azazael/skills/azazael-eve-unleashed.md`
