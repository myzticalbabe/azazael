---
name: azazael-optimization-session
description: Lazy import optimization patterns — module splitting, PAMS HTTP cache, fast-path registry discovery. Pattern reference for future speed improvements.
metadata:
  category: performance
  project: azazael
  priority: high
---

# AZAZAEL — Import Optimization Patterns

> **Session:** 2026-06-01 | **Focus:** Reducing discover_worms() from 8.3s to 0.51s (16x)
> **Key Techniques:** Lazy imports, module splitting, HTTP timeout caching, fast-path registry

---

## EXECUTIVE SUMMARY

The worm discovery pipeline (`discover_worms()`) and NatureClusterManager discovery (`discover_all_natures()`) were the two biggest startup bottlenecks in Azazael. After optimization:

| Metric | Before | After | Speedup |
|--------|--------|-------|---------|
| discover_worms() first call | 8.3s | **0.51s** | **16x** |
| BINARY_ANALYSIS import | 4.18s | **~0.002s** | **~2000x** |
| METACLUSTER import | 2.01s | **~0.05s** | **~40x** |
| CLUSTERWORMS import | 2.00s | **~0.05s** | **~40x** |
| NCM.discover_all_natures() | 36.2s | **2.37s** | **15x** |
| PAMS record_event (cached) | 2.015s | **0.003s** | **775x** |
| NCM.discover_all_natures() (hot) | 36.2s | **0.065s** | **557x** |

---

## PATTERN 1: Lazy Import via `_get_xxx()` Functions

### Problem
Heavy modules (PamsRecorder, MemoryBus, circuit breaker, tkinter) were instantiated at module level. Simply importing the module triggered all these heavy init chains.

### Solution
Replace module-level instantiation with lazy getter functions:

```python
# BEFORE: Eager import at module level
from CORE.PamsRecorder import PamsRecorder
_pams = PamsRecorder()

# AFTER: Lazy getter, instantiated on first use
_pams = None
def _get_pams():
    global _pams
    if _pams is None:
        try:
            from CORE.PamsRecorder import PamsRecorder
            _pams = PamsRecorder()
        except ImportError:
            _pams = False  # Sentinel: don't retry
    return _pams if _pams else None
```

### Where Applied
- `NATURE_CLUSTERS.py` — `_get_pams()`, `_get_mem_bus()`, `_get_breaker_registry()`
- `METACLUSTER.py` — `_get_pams()`, `_get_mem_bus()`
- `CLUSTERWORMS.py` — `_get_pams()`, `_get_mem_bus()`, `_get_breaker_registry()` (+ tkinter moved into `run_popup()`)
- `BINARY_ANALYSIS.py` — All heavy sub-modules lazy-loaded inside methods

### Rules
- Use `_var = None` at module level, `_get_var()` function for lazy access
- Use `False` as sentinel for failed imports (don't retry on every call)
- Move `import tkinter` inside the function that uses it (not at module level)
- Update all callers to use `_get_xxx()` instead of the old module-level variable

---

## PATTERN 2: Module Splitting (Breaking Up Monoliths)

### Problem
`BINARY_ANALYSIS.py` was a ~800-line monolith importing heavy C extension modules (pefile, elftools, capstone). Importing it triggered all these even for simple operations like `get_summary()`.

### Solution
Split into focused sub-modules, keep original as thin wrapper:

```
BINARY_ANALYSIS_TYPES.py  (~80 lines)  — Data classes, constants, _get_pams()
BINARY_ANALYSIS_PARSE.py  (~350 lines) — PE/ELF parsing functions
BINARY_ANALYSIS_TOOLS.py  (~300 lines) — Text tools (sed, awk, strings, entropy)
BINARY_ANALYSIS.py        (~150 lines) — Thin wrapper class with lazy imports
```

### Key Detail
The original class API (`BinaryAnalysis.get_summary()`, `BinaryAnalysis.analyze_binary()`) is preserved. The heavy imports happen inside methods, not at module level:

```python
class BinaryAnalysis:
    def get_summary(self):
        from CORE.WORMS.BINARY_ANALYSIS_TYPES import _get_pams
        # ... lightweight logic

    def analyze_binary(self, path):
        from CORE.WORMS.BINARY_ANALYSIS_PARSE import parse_pe_headers, extract_symbols
        # ... heavy parsing only triggered on actual use
```

---

## PATTERN 3: PAMS HTTP Timeout Caching

### Problem
`PamsRecorder.record_event()` tried `requests.post(url, timeout=2)` on EVERY call. When PAMS isn't running, each call blocks for the full 2s timeout. 18 calls = 36s.

### Solution
Add class-level unreachable flag with periodic retry:

```python
class PamsRecorder:
    _pams_unreachable = False     # Skip HTTP after first failure
    _pams_retry_interval = 60.0   # Seconds before retrying
    _pams_last_attempt = 0.0      # Timestamp of last attempt

    def record_event(self, ...):
        now = time.monotonic()
        if HTTP_OK:
            should_retry = not type(self)._pams_unreachable
            if not should_retry and (now - type(self)._pams_last_attempt) >= type(self)._pams_retry_interval:
                should_retry = True
            if should_retry:
                type(self)._pams_last_attempt = now
                try:
                    resp = requests.post(url, json=event, timeout=2)
                    if resp.status_code == 200:
                        type(self)._pams_unreachable = False  # Clear on success
                        return True
                except Exception:
                    type(self)._pams_unreachable = True       # Cache failure
```

### Warm-Up Fixture (for tests)
```python
# In conftest.py — runs at import time before any test collection
def _warm_pams_cache():
    try:
        from CORE.PamsRecorder import PamsRecorder, get_recorder, HTTP_OK
        if HTTP_OK:
            rec = get_recorder()
            rec.record_event("conftest_warmup", {}, source="conftest", severity="debug")
    except Exception:
        pass
```

---

## PATTERN 4: Registry Fast-Path (Skipping dir() Loop)

### Problem
`discover_worms()` iterated every module's `dir()` to find `@register_worm` classes, even though the decorator already registered them during import.

### Solution
After importing a module, check if its classes are already in `WORM_REGISTRY`. If so, skip the expensive dir() loop:

```python
# After importing a module:
already_has_classes = False
for name, info in WORM_REGISTRY.items():
    source = info.get("source_file", "")
    if source.endswith(filename):
        already_has_classes = True
        break

if not already_has_classes:
    # Fall back to expensive dir() loop only if no decorator registered this module
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and hasattr(obj, "VERSION"):
            ...
```

Also replaced `inspect.isclass(obj)` with `isinstance(obj, type)` for speed.

---

## TEST INFRASTRUCTURE ADDED

| File | Tests | Purpose |
|------|-------|---------|
| `tests/test_binary_analysis_parse.py` | 17 | PE/ELF parsing, symbol extraction |
| `tests/test_binary_analysis_tools.py` | 28 | sed, awk, strings, hexdump, entropy |
| `tests/test_ncm_integration.py` | 8 | Full NCM discovery workflow |
| `tests/conftest.py` | — | PAMS cache warm-up fixture |
| `run_tests.py` | — | Registers new test files |

**All 239 fast tests pass.** Test files use standalone `__main__` blocks (no pytest dependency).

---

## RELATED FILES MODIFIED

| File | Change |
|------|--------|
| `src/CORE/WORMS/BINARY_ANALYSIS.py` | Split into thin wrapper with lazy imports |
| `src/CORE/WORMS/BINARY_ANALYSIS_TYPES.py` | NEW — shared types module |
| `src/CORE/WORMS/BINARY_ANALYSIS_PARSE.py` | NEW — PE/ELF parsing |
| `src/CORE/WORMS/BINARY_ANALYSIS_TOOLS.py` | NEW — text processing tools |
| `src/CORE/WORMS/METACLUSTER.py` | Lazy PAMS/MemoryBus |
| `src/CORE/WORMS/CLUSTERWORMS.py` | Lazy PAMS/MemoryBus/breaker/tkinter |
| `src/CORE/WORMS/NATURE_CLUSTERS.py` | Lazy PAMS + circuit breaker |
| `src/CORE/PamsRecorder.py` | `_pams_unreachable` cache + periodic retry |
| `src/CORE/worm_registry.py` | Fast-path dir() loop skip |
| `tests/conftest.py` | PAMS cache warm-up fixture |
| `run_tests.py` | Register new test files |

---

## FUTURE OPTIMIZATION TARGETS

1. **NCM loop in NatureClusterManager** — The remaining ~2s for `discover_all_natures()` is from PamsRecorder.record_event() fallback path. Could be further reduced by batching events.
2. **Other heavy modules** — Check for module-level `import psutil`, `import requests`, `from PIL import Image`, etc. across all 95 worms.
3. **Thread safety** — The `_pams_unreachable` cache uses class-level attributes without a lock. For true 3.14t parallelism, add a `threading.Lock()` around cache checks.
4. **Slow test (test_metacluster_unit.py)** — 31/33 pass, 2 pre-existing failures. The ~38s discovery phase is now eliminated; the remaining time is from actual worm execution.
