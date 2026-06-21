# SESSION INSIGHTS — May 29, 2026 — Phase 17

> **Phase:** Eve Unleashed GPU Monitoring + PAMS Wiring
> **Based on:** Phase 16 followup suggestions
> **Built on:** Eve Unleashed v1.0 (Phase 16)

---

## Changes Made

### 1. BAT Launcher Regenerated
- Ran `regenerate_bats.py` — Eve_Unleashed_314t.bat created (95 bytes)
- 50 BAT launchers total, all current

### 2. GPU Monitoring Added to System Monitor Tab
- **pynvml** installed and used for NVIDIA GPU metrics (temperature, utilization%, memory used/total, power draw)
- **Intel Arc WMI fallback** — uses `wmic path Win32_VideoController` to detect Intel GPUs (Arc 140T detected)
- GPU metric card added as 3rd row in monitor tab with 5 sub-metrics:
  - GPU utilization (color-coded: green <50%, yellow 50-80%, red >80%)
  - GPU temperature
  - VRAM used/total
  - Power draw
  - GPU name
- **Fixed (code review):** WMI GPU name cached on first call instead of spawning `subprocess.run` every 2 seconds
- **Fixed (code review):** pynvml `nvmlShutdown()` called on app close via `_on_close`

### 3. PAMS/MemoryBus Wiring
- **PamsRecorder** import with graceful fallback (`HAS_PAMS` flag)
- `_record_pams()` helper method wraps all recording calls with try/except
- Session start recorded just before `mainloop()`
- Session end recorded in `_on_close()` callback
- Per-inference events: backend name, latency_ms, tokens_per_sec, model, response length
- Per-REPL events: code snippet, output, has_error flag, severity
- Benchmark completion: total tests, passed, failed, backends tested
- All recording calls use `source="EveUnleashed"` tag

### 4. Code Review Fixes Applied
- **Dead code fix:** Restructured llama.cpp inference so local GGUF falls through to HTTP endpoint on failure (previously unreachable)
- **Theme switching fix:** Replaced broken 2-widget `_set_theme` with recursive widget-tree walker that re-themes all Frame/Label/Text/Listbox/Button/Canvas widgets
- **REPL-inference integration:** Injected `eve_infer()` and `eve_backends()` into REPL namespace
- **ASCII-safety:** Removed Unicode arrows from `_display_monitor_data` (D/U instead of down/up arrows, OK/-- instead of checkmarks)

### 5. Records Updated
- `MEMORIES.md` — Phase 17 section added
- `CODEBASE_AUDIT_TODO.md` — Marked 5 completed tasks: build_all.py bugs (2), Nuitka patterns skill (1), import hygiene (1/4), hardcoded paths (1)
- `SESSION_INSIGHTS_2026-05-29_PHASE17.md` — This file

---

## Build Results

| Metric | Value |
|--------|-------|
| Eve_Unleashed_314t.exe size | 11.3 MB (was 10.2, +1.1 MB for pynvml) |
| Total standalone EXEs | 50 |
| BAT launchers | 50 |
| Skills | 11 |
| Syntax check | Pass |
| EXE test (timeout 8s) | Exit 124 = OK (GUI killed by timeout) |

---

## Patterns & Lessons

### Pattern: Python Patch Scripts for Complex Edits
When str_replace fails due to Unicode characters, write a temporary Python patch script that reads the file, applies all fixes, and writes back. Run it via basher with a simple command. Clean up the temp file after.

### Anti-Pattern: subprocess.run() in Hot Loop
Never call `subprocess.run()` every 2 seconds in a monitor poll loop. Cache the result if it won't change (e.g., GPU name). The fix: store `_gpu_name_cached` on first WMI call.

### Anti-Pattern: pynvml Init Without Shutdown
Always pair `nvmlInit()` with `nvmlShutdown()`. The fix: call shutdown in `_on_close()` callback.

### Pattern: Graceful Fallback Imports
```python
try:
    from CORE.PamsRecorder import PamsRecorder
    _pams_recorder = PamsRecorder()
    HAS_PAMS = True
except Exception:
    _pams_recorder = None
    HAS_PAMS = False
```
This pattern allows the app to work even when PAMS is unavailable — all recording calls go through a helper that checks `HAS_PAMS` first.

---

## Errors Encountered

### Error 1: str_replace Unicode Matching Failure
**Symptom:** `str_replace` could not find old string containing Unicode arrows (down/up arrows, checkmarks) in `_display_monitor_data`
**Root Cause:** Unicode characters in the file didn't match the escaped versions in the tool call
**Fix:** Wrote `_eve_patch.py` temp script to apply edits via Python, which handles Unicode natively
**Prevention:** When editing files with Unicode, use Python patch scripts instead of str_replace

### Error 2: Indentation Nesting Bug from Patch Script
**Symptom:** SyntaxError on line 1188 — `_display_monitor_data` nested inside `_display_benchmark_results`
**Root Cause:** Patch script regex replaced back one line too few, causing method to be indented inside previous method
**Fix:** str_replace to fix indentation block
**Prevention:** Add more defensive regex patterns in patch scripts, verify indentation after patching

---

## CODEBASE_AUDIT_TODO.md Updates

### Tasks Completed This Phase:
- build_all.py `env` scoping bug — ✅ Fixed Phase 12, verified Phase 15
- build_all.py `--output-dir` — ✅ Fixed Phase 12, verified Phase 15
- Nuitka patterns skill (`azazael-exe-build.md`) — ✅ Created Phase 14
- Import hygiene (autoflake on 12 files) — ✅ Phase 15
- Hardcoded paths (data dicts documented) — ✅ Phase 15

### Remaining Critical Tasks:
- Test coverage (0/8 tasks)
- Error recovery (0/5 tasks)
- Configuration (0/3 tasks)

---

## Next Session Recommendations
1. **Start on test coverage** — Unit tests for CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTER
2. **Error recovery** — Circuit breaker, retry with exponential backoff
3. **Configuration** — Centralized azazael.yaml config file
