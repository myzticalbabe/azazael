# LESSONS — Task A: Fixing _get_store() Deadlock Risk Under 3.14t

**Task:** Fix function-body imports in neural advancement modules
**Date:** June 4, 2026
**Reference:** LESSONS_MASTER.md #28, #29

---

## Problem

`MetaCognitionWorm._get_store()`, `EvolutionEngine._get_store()`, and `DreamingModule` persistence methods called `from CORE.local_memory import get_memory_store` inside function bodies. Under Python 3.14t free-threading, `importlib.import_module()` is NOT thread-safe — concurrent calls from background threads deadlock the import system.

This was the exact same bug documented in Lesson #28 (ClusterWORMZ parallel hang) and #29 (module-level import pattern).

## Fix

Moved imports to module level:

```python
# Module level — safe under 3.14t
try:
    from CORE.local_memory import get_memory_store as _get_memory_store_global
    _LOCAL_MEMORY_OK = True
except ImportError:
    _LOCAL_MEMORY_OK = False
    _get_memory_store_global = None

# In _get_store() — no imports, just lookup
def _get_store(self):
    if not self._persistence_enabled:
        return None
    if self._memory_store is not None:
        return self._memory_store
    if _LOCAL_MEMORY_OK and _get_memory_store_global is not None:
        try:
            return _get_memory_store_global()
        except Exception:
            return None
    return None
```

## Files Modified
- `src/CORE/WORMS/expansion/meta_cognition.py` — Module-level import + updated `_get_store()`
- `src/CORE/WORMS/expansion/evolution.py` — Module-level import + updated `_get_store()`
- `src/CORE/WORMS/expansion/dreaming.py` — Module-level import added (existing methods already safe)

## Validation
- All 5 files pass `py_compile` syntax check
- 30/30 tests pass
- No function-body imports remain in any persistence path

## Prevention
- ANY `import` in a function body that could be called from a `ThreadPoolExecutor` worker is a deadlock risk under 3.14t
- Pattern: module-level `try/except` import → `if _FLAG: call()` — never `from X import Y` inside a method
