# LESSONS — Task B: RaceConditionDetector & ErrorRecoveryOrchestrator

**Task:** Build P0 worms for 3.14t thread safety and error recovery
**Date:** June 4, 2026
**Reference:** WORM_PROPOSALS.md Proposals 1-2

---

## RaceConditionDetector (race_detector.py)

### Design Decisions
- **Module-level imports only** — no function-body imports (Lesson #29 compliance)
- **Non-invasive instrumentation** — wraps Lock.acquire() and __setattr__() rather than modifying worm logic
- **Concurrent write window**: 100ms — two writes from different threads within this window = potential data race
- **Memory store integration**: `_LOCAL_MEMORY_OK` flag for graceful degradation

### Key Methods
- `instrument_worm(worm_instance, label)` — Wraps lock acquisition + attribute writes with tracing
- `detect_data_races()` — Analyzes access logs for concurrent write conflicts
- `detect_thread_imports(code_paths)` — Scans source files for function-body imports (3.14t deadlock risk)
- `generate_safety_report()` — Comprehensive report with recommendations

### Worm Registration
- Category: `security`, Priority: 9, Cooldown: 60s
- Registered in `expansion/__init__.py` and `__all__`

---

## ErrorRecoveryOrchestrator (error_recovery.py)

### Design Decisions
- **Exponential backoff with jitter**: 1s → 2s → 4s + random(0-50%) jitter
- **Circuit breaker**: 5 failures in window opens circuit for 300s
- **Fallback strategy**: `get_status()` if `execute()` fails, otherwise safe degraded response
- **Recovery recording**: All attempts tracked in `RecoveryEntry` dataclasses
- **Thread-safe**: All state guarded by `threading.Lock`

### Key Methods
- `execute_with_recovery(worm_type, worm_instance)` — Full retry/fallback/circuit-break pipeline
- `get_circuit_breaker_status()` — Which worms are currently open
- `reset_circuit(worm_type)` — Manual recovery after fix
- `get_stats()` — Success rate, failure counts, recent recoveries

### Worm Registration
- Category: `orchestration`, Priority: 9, Cooldown: 30s
- Registered in `expansion/__init__.py` and `__all__`

---

## Validation
- Both files pass `py_compile` syntax check
- No function-body imports (3.14t safe)
- All instrumentation is non-destructive (read-only wrapping)
