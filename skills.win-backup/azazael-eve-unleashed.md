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
# Requirements: Python 3.14t, Nuitka 4.1.2+ (patched)
cd ~/Desktop/AZAZAEL_Standalone
python -m nuitka --standalone --onefile \
  --assume-yes-for-downloads \
  --enable-plugin=tk-inter \
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
2. **Nuitka 3.14t patches required** — Run `patch_nuitka_314t.py --apply` before building
3. **GGUF model discovery** — Scans `~/Desktop/eve_rebuild_test/`, `~/Desktop/eve_rebuild/`, `~/.cache/lm-studio/models/`
4. **Simulated fallback** — When no backend is reachable, returns `[SIMULATED:...]` placeholder responses

## Integration

- **build_all.py** — Listed in Tier 3 (CODEX Analysis) with `NEEDS_TKINTER` flag
- **Desktop path** — `~/Desktop/AZAZAEL_Standalone/Eve_Unleashed_314t.exe`
- **Source** — `~/Desktop/EveUnleashed_Selector/eve_unleashed_app.py` (external project, not in azazael/src)
- **Skills directory** — This file at `azazael/skills/azazael-eve-unleashed.md`
