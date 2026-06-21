# SESSION INSIGHTS — May 29, 2026 — Phase 16
## Eve Unleashed Standalone Desktop App

### Summary
Rebuilt Eve Unleashed as a standalone desktop application for local AI inferencing with an embedded Python REPL, system monitor, and multi-backend benchmarks. Packaged as `Eve_Unleashed_314t.exe` (10.2 MB).

### What Was Done

#### 1. New File: `eve_unleashed_app.py` (564 lines)
Created a unified Tkinter desktop application at `Desktop/EveUnleashed_Selector/eve_unleashed_app.py` with four tabs:

**Inference Tab:**
- `BackendDiscoverer` class — auto-discovers Ollama, llama-cpp-python, llama-server SYCL, transformers, Go PerfMon gateway
- `run_inference()` — real inference with measured latency and tokens/sec; graceful fallback to simulated when no backend is reachable
- Backend listbox with selection, test button, prompt input with scrolled response display

**Python REPL Tab:**
- `PythonREPL` class — sandboxed interpreter with `exec()`/`eval()`, stdout/stderr capture, variable tracking
- Pre-loaded namespace: `sys`, `os`, `Path`, `json`, `time`, `datetime`
- "Show Vars" button displays user-defined variables
- `Ctrl+Enter` keyboard shortcut for instant execution

**System Monitor Tab:**
- `SystemMonitor` class — psutil-based metrics collection (CPU %, RAM used/total, disk I/O rates, network throughput)
- 2x2 metric card grid with color-coded thresholds (green < 50%, yellow < 85%, red > 85%)
- System info bar: hostname, OS, uptime, process/thread count, Python 3.14t status
- Background thread polling every 2 seconds

**Benchmarks Tab:**
- 5 predefined test prompts (reasoning, safety, architecture, training, learning)
- Runs across all available backends
- TreeView with columns: backend, test, latency (ms), tokens/sec, status
- Color-coded rows: green (real), yellow (simulated), red (error)
- Summary bar with real/simulated/error counts

**Theme System:**
- 3 themes: Obsidian (dark GitHub-style), Aurora (deep navy/cyan), Midnight (near-black/purple)
- Per-theme color palette: bg, fg, accent, success, warning, error, card_bg, border, input_bg, tab colors, fonts
- Dynamic switching via theme buttons in title bar

#### 2. Bug Fixed: UnicodeEncodeError on Windows Console
- **Error:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u26a1'` (lightning emoji)
- **Root Cause:** The entry-point `if __name__ == "__main__"` block printed `⚡ Eve Unleashed` to stdout, which uses cp1252 on Windows
- **Fix:** Added `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` and `sys.stderr.reconfigure(...)` at module top when `sys.platform == 'win32'`. Also replaced all emoji/special chars in console output with ASCII equivalents.

#### 3. EXE Build
- Built with Nuitka 4.1.2 on Python 3.13 (historical — all builds now on 3.14t with patched Nuitka)
- Command: `--standalone --onefile --enable-plugin=tk-inter`
- Result: `Eve_Unleashed_314t.exe` (10,664,960 bytes / 10.2 MB)
- Verified operational — launches GUI without crashes (timeout kills GUI process at exit 124 = expected)

#### 4. build_all.py Updated
- Added `"Eve_Unleashed": "../EveUnleashed_Selector/eve_unleashed_app.py"` to MODULES dict (Tier 3)
- Added `"Eve_Unleashed"` to NEEDS_TKINTER set for tk-inter plugin
- Note: Source path uses `../` prefix since it's outside `azazael/src/` (external project)

#### 5. New Skill Created
- `azazael/skills/azazael-eve-unleashed.md` — Complete documentation: architecture diagram, build command, feature breakdown, dependency table, known issues, integration notes
- Skills count: 10 → 11

### Design Decisions
1. **Tkinter over PyQt/Electron** — Zero additional dependencies, works with Nuitka, consistent with existing AZAZAEL POPUP apps
2. **Threaded inference** — All backend calls run on daemon threads to keep UI responsive; results delivered via `queue.Queue` processed in main thread
3. **Graceful degradation** — Every optional dependency (psutil, ollama, llama_cpp, transformers) has a `HAS_*` flag; missing deps → simulated/placeholder output instead of crashes
4. **Single-file app** — Entire application in one `.py` file for easy Nuitka packaging and distribution
5. **Path resolution** — Uses `Path(__file__).resolve().parent` for dev; Nuitka EXE works because no relative imports needed

### File Manifest
| File | Action | Size |
|------|--------|------|
| `eve_unleashed_app.py` | Created | 564 lines, ~22 KB |
| `Eve_Unleashed_314t.exe` | Built | 10,664,960 bytes |
| `build_all.py` | Updated | +2 lines |
| `azazael/skills/azazael-eve-unleashed.md` | Created | ~3 KB |
| `azazael/MEMORIES.md` | Updated | Phase 16 section |
| `azazael/SESSION_INSIGHTS_2026-05-29_PHASE16.md` | Created | This file |

### Next Steps (Suggested)
1. Regenerate BAT launcher for Eve_Unleashed via `regenerate_bats.py`
2. Add GPU monitoring (nvidia-smi, Intel GPU tools) to System Monitor tab
3. Wire Eve Unleashed to PAMS/MemoryBus for session recording
4. Add model download/management tab within the app
5. Create `eve_unleashed.bat` launcher in AZAZAEL_Standalone
