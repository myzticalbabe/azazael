# LESSONS — Task H: Function-Body Import Elimination (Completion)

**Task:** Eliminate ALL remaining function-body imports across the worm codebase
**Date:** June 4, 2026
**Reference:** LESSONS_MASTER.md #28, #29, #31, #32; LESSONS_TASK_E_LOCKING_AUDIT.md

---

## Background

Lesson #28 established that `importlib.import_module()` is NOT thread-safe under Python 3.14t free-threading. Lesson #29 established the module-level pre-import pattern as the fix. But the audit was incomplete — 3 files with function-body imports remained.

---

## The Final 3 Files Fixed

### File 1: `METACLUSTER.py` (line 73)

```python
# BEFORE — import inside except block (function body):
except ImportError:
    _ROUTER_OK = False
    CrossNatureRoutingEngine = None
    from dataclasses import dataclass as _dc  # <-- DEADLOCK RISK
    @_dc
    class _CrossNatureRoute:
        from_nature: str = ""

# AFTER — module-level import already existed:
from dataclasses import dataclass, field  # Already at top of file
...
except ImportError:
    _ROUTER_OK = False
    CrossNatureRoutingEngine = None
    @dataclass  # Use existing module-level import
    class _CrossNatureRoute:
        from_nature: str = ""
```

**Fix type:** Remove function-body import, use existing module-level import.

### File 2: `CROSS_NATURE_ROUTER.py` (line 37)

```python
# BEFORE — same pattern, but dataclass NOT imported at module level:
except ImportError:
    _NATURE_OK = False
    NATURE_DEFINITIONS = {}
    from dataclasses import dataclass as _dc  # <-- DEADLOCK RISK
    @_dc
    class _CrossNatureRoute: ...

# AFTER — module-level import + simplified usage:
from dataclasses import dataclass  # Added to module-level imports
...
except ImportError:
    _NATURE_OK = False
    NATURE_DEFINITIONS = {}
    @dataclass  # Use module-level import
    class _CrossNatureRoute: ...
```

**Additionally fixed:** `_get_mem_bus()` and `_get_pams()` had double-checked locking gaps — `if _mem_bus is None and not _BUS_OK:` without a lock. Both now use proper double-checked locking with `threading.Lock()`.

### File 3: `CODEX_TOOLS.py` (4 function-body imports)

```python
# BEFORE — 4 lazy imports inside __init__ methods:
class CainAnalyzerWorm:
    def __init__(self):
        try:
            from CAIN_ANALYZER import run_complete_analysis as _analyze  # DEADLOCK RISK
            self._analyze = _analyze
        except ImportError: ...

class AutoDownloaderWorm:
    def __init__(self):
        try:
            from AUTO_DOWNLOADER import AutoDownloader  # DEADLOCK RISK
            self._downloader = AutoDownloader()
        except ImportError: ...

# Same pattern for EmojiMakerWorm and EnhancedAnimationsWorm

# AFTER — all 4 imports at module level:
try:
    from CAIN_ANALYZER import run_complete_analysis as _cain_analyze
except ImportError:
    _cain_analyze = None

try:
    from AUTO_DOWNLOADER import AutoDownloader as _AutoDownloaderCls
except ImportError:
    _AutoDownloaderCls = None

try:
    from emoji_maker import EmojiMaker as _EmojiMakerCls
except ImportError:
    _EmojiMakerCls = None

try:
    from enhanced_animations import ANIMATIONS as _ANIMATIONS_MOD, generate_css as _gen_css
except ImportError:
    _ANIMATIONS_MOD = None
    _gen_css = None

# __init__ methods now just check module-level flags:
class CainAnalyzerWorm:
    def __init__(self):
        self._analyzer_ok = _cain_analyze is not None
        self._analyze = _cain_analyze
```

**Impact:** 4 `__init__` methods simplified from ~10 lines each to ~2 lines. All imports happen at module load on the main thread.

---

## The Complete Import Elimination Scorecard

| File | Function-body imports BEFORE | Function-body imports AFTER | Fix |
|------|---------------------------|--------------------------|-----|
| `CLUSTERWORMS.py` | 5 (PAMS, MemoryBus, breaker, config, futures) | 0 | Lesson #29 |
| `LEGACY_DISPATCH` (CLUSTERWORMS.py) | 19 `__import__()` lambdas | 0 | Lesson #29 |
| `NETWORK_DIAG.py` | 5 `import psutil` | 0 | Module-level `try/except ImportError` |
| `evolution.py` | 1 (`from CORE.local_memory import get_memory_store`) | 0 | Module-level `_get_memory_store_global` |
| `METACLUSTER.py` | 1 (`from dataclasses import dataclass as _dc`) | 0 | Existing module import |
| `CROSS_NATURE_ROUTER.py` | 1 (`from dataclasses import dataclass as _dc`) | 0 | New module-level import |
| `CODEX_TOOLS.py` | 4 (CAIN_ANALYZER, AUTO_DOWNLOADER, emoji_maker, enhanced_animations) | 0 | Module-level `try/except` |
| `TELEMETRYZ.py` | 1 (`import os` missing, latent bug) | 0 | Added module-level import |
| **TOTAL** | **37 function-body imports eliminated** | **0** | |

---

## Lesson H1: The `except ImportError` + Fallback Class Pattern

When a module import can fail, declare the fallback class at module level:

```python
# CORRECT — no function-body imports, graceful degradation:
try:
    from OPTIONAL_MODULE import OptionalClass as _OptCls
    _OPT_OK = True
except ImportError:
    _OptCls = None
    _OPT_OK = False

class MyWorm:
    def __init__(self):
        if _OPT_OK and _OptCls is not None:
            self._helper = _OptCls()
        else:
            self._helper = None
```

**Key insight:** The class reference (`_OptCls`) is resolved at module load time on the main thread. The instantiation happens at runtime in any thread — instantiation is safe, importing is not.

---

## Lesson H2: The `dataclass` Import Trap

**Pattern:** `from dataclasses import dataclass as _dc` inside an `except ImportError` block. This appears in 2 files.

**Why it's a trap:** The `except ImportError` block already handles a different module failing — adding another import inside it creates a potential chain failure if `dataclasses` also fails (extremely unlikely for stdlib, but the pattern is wrong).

**Fix:** Move `from dataclasses import dataclass` to module-level imports (top of file). `dataclasses` is stdlib and always available.

---

## Lesson H3: The Code Review Fidelity Problem

**Discovery:** The code-searcher found only 1 function-body import in CODEX_TOOLS.py (the CAIN_ANALYZER one), but the file had 3 MORE (AUTO_DOWNLOADER, emoji_maker, enhanced_animations). The code-reviewer-deepseek caught this.

**Lesson:** Code searchers find what you ask for. Code reviewers find what you didn't ask for. Both are needed. **Never trust a single search query to find ALL instances of a pattern — always follow up with a code reviewer.**

---

## Session Actions Recorded

| File | Change | Lines |
|------|--------|-------|
| `METACLUSTER.py` | Removed `from dataclasses import dataclass as _dc` | -3 |
| `CROSS_NATURE_ROUTER.py` | Module-level `from dataclasses import dataclass`; locked `_get_mem_bus()` and `_get_pams()` | +10 |
| `CODEX_TOOLS.py` | 4 module-level imports replacing 4 function-body imports | +16, -24 |
| `NETWORK_DIAG.py` | 5 `import psutil` → module-level; `except Exception` → `except ImportError` | +6, -10 |
| `evolution.py` | `GeneticOptimizer.optimize()` function-body import → module-level | +2, -4 |
| `learning.py` | 4 double-checked locked lazy inits (RLTrainLoop x2, ModelVersioner, DataPipelineWorm) | +24 |
| `dreaming.py` | `_govern_dreaming_gate` CurativePool double-checked locked | +8 |
| `evolution.py` | `_govern_evolution_gate` CurativePool double-checked locked | +8 |

**Final metric:** 0 function-body imports across all worm source files. 30/30 tests pass.

**Cross-reference:** LESSONS_MASTER.md #28 (import deadlock), #29 (module-level pre-import), #31 (PamsRecorder circular init), #32 (double-checked locking). This task completes the 3.14t import safety trilogy.
