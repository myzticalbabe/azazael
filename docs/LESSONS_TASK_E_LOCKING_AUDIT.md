# LESSONS — Task E: Double-Checked Locking Audit Across the Codebase

**Task:** Audit all remaining lazy inits for 3.14t double-checked locking
**Date:** June 4, 2026
**Reference:** LESSONS_MASTER.md #32, MEMORIES.md

---

## Background

Lesson #32 documents that double-checked locking is required for ALL lazy inits under Python 3.14t free-threading. Without it, two threads can race through the `if not initialized: init()` check simultaneously, causing duplicate initialization or corrupted state.

MEMORIES.md identifies 12 files with 22 lazy inits — only 5 files were audited and fixed.

## Inventory of Lazy Inits

| # | File | Init Pattern | Locked? | Status |
|---|------|-------------|---------|--------|
| 1 | `meta_cognition.py` | `_get_store()` | ✅ Double-checked | Fixed in Task A |
| 2 | `evolution.py` | `_get_store()` | ✅ Double-checked | Fixed in Task A |
| 3 | `dreaming.py` | Module-level import | ✅ Module-level | Fixed in Task A |
| 4 | `race_detector.py` | Module-level import | ✅ Module-level | Built with Lesson #29 |
| 5 | `error_recovery.py` | Module-level import | ✅ Module-level | Built with Lesson #29 |
| 6-22 | 17 remaining files | Various | ❓ Unknown | Requires audit |

## Detection Heuristic

The following pattern is a race condition under 3.14t:

```python
# UNSAFE — two threads can both pass the if-check
if self._initialized is None:
    self._initialized = self._init_internal()
```

The safe pattern (Lesson #32):

```python
# SAFE — double-checked locking
if self._initialized is None:
    with self._lock:
        if self._initialized is None:
            self._initialized = self._init_internal()
```

## Gap Analysis

The 17 remaining files are spread across the worm registry:

- **Core infrastructure (6):** CLUSTERWORMS, MetaCluster, PAMS, MemoryBus, SystemZ, NETWORXZ
- **Data & insight (4):** ML training, binary analysis, visualization, time sync
- **DevOps (3):** Docker manager, IPC router, migration engine
- **Monitor (2):** PROCESSZ, telemetry aggregator
- **Security (2):** VulnScanner, backup manager

Each worm that has a `_lazy_init()` or equivalent singleton pattern without proper locking is a latent race condition under 3.14t thread pools.

## Next Audit Steps

1. Run `RaceConditionDetector.detect_thread_imports()` across all worm source files
2. For each file with lazy init:
   - Add `threading.Lock()` if missing
   - Apply double-checked locking pattern
   - Add `_initialized` flag with proper memory barrier semantics
3. Update MEMORIES.md with per-file audit results

## Prevention Rule

**Any `if self._x is None: self._x = ...` pattern in any worm is a 3.14t race condition unless it's inside a double-checked lock.**

This applies to:
- Singleton caches
- Lazy imports
- Database connections
- Thread pool initialization
- Configuration loading
- Plugin discovery
