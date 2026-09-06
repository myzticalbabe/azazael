---
name: azazael-curative
description: CurativePool 3.14t — CAIN psychological framework, free-threaded agent governance, 3-pool concurrent evaluation architecture
---

# CurativePool 3.14t — CAIN Governance Architecture

**Version:** 1.0.0  
**Pipeline:** MONITOR → LEARN 3.14t → INFER → ARTIFACT  
**Framework:** CAIN Accountability System (Cognitive Accountability & Introspective Navigation)

## Overview

The CurativePool implements a three-layer concurrent evaluation framework for governing autonomous agent actions in Python 3.14t free-threaded environments. Derived from the CAIN 75-panel psychological analysis, it enforces scope validation, necessity judgment, and emotional attunement before any worm execution.

| Component | Purpose | Concurrency |
|-----------|---------|-------------|
| Validation Layer | Scope, necessity, emotion checks | Pool 1 (must complete first) |
| Audit & Memory | PAMS recording, MemoryBus events, metrics | Pool 2 (concurrent with Pool 3) |
| Feedback Loop | Archetype routing, calibration, cost metering | Pool 3 (concurrent with Pool 2) |

## Architecture

### Pool 1: Validation Layer
Runs first. Provides results that Pool 2 and Pool 3 depend on.

- **`ScopeValidator`** — Compares proposed action vs request parameters. Rejects deviations >10%. Returns dict with `valid`, `deviations`, `max_deviation_pct`.
- **`NecessityJudge`** — Scores output necessity (p>0.8 threshold). Uses action type + request context + output size. Returns dict with `necessary`, `confidence`, `action` ("proceed"/"hold_for_review").
- **`EmotionDetector`** — Analyzes conversation for frustration signals (repeated corrections, short responses, negative feedback). Returns dict with `frustration_detected`, `frustration_score`, `signals`.

### Pool 2: Audit & Memory
Concurrent with Pool 3. Depends on Pool 1 results.

- **`AuditWriter`** — Records full action context to PAMS: request → action → outcome → deviation. Includes timestamp, event_type, audit_hash.
- **`MemoryBusPublisher`** — Publishes lifecycle events (`curative.action.evaluated`) with scope_valid, necessary, frustration status.
- **`MetricsCollector`** — Thread-safe aggregation (`threading.Lock`). Tracks total_actions, scope_violations, unnecessary_actions, frustration_triggers, avg_deviation_pct.

### Pool 3: Feedback Loop
Concurrent with Pool 2. Uses Pool 1 results.

- **`ArchetypeRouter`** — Routes tasks to optimal agent by archetype (6 types: The Hero, The Analyst, The Builder, The Muse, The Guardian, The Accountant).
- **`CalibrationUpdater`** — Adjusts quality-weighting based on violation_rate over last 50 evaluations. Returns "tighten" (rate > 0.15) or "maintain".
- **`CostMeter`** — Calculates economic impact: wasted_output_kb, compute_cost, user_time_wasted_s, trust_erosion_score.

## Thread Safety Pattern

```python
# Minimal locked region — acquire lock only for critical section
class MetricsCollector:
    def __init__(self):
        self._metrics = {...}
        self._lock = threading.Lock()

    def record_action(self, ...):
        with self._lock:
            self._metrics["total_actions"] += 1
        return dict(self._metrics)  # snapshot under lock

    def report(self):
        with self._lock:
            return dict(self._metrics)
```

## Thread Ordering

```
CORRECT:                           WRONG (data race):
t1.start()  # Pool 1               t1.start()
t1.join()   # Pool 1 completes     t2.start()  # Pool 2 reads stale Pool 1
t2.start()  # Pool 2               t3.start()
t3.start()  # Pool 3               t1.join()
t2.join()                          t2.join()
t3.join()                          t3.join()
```

## CLI Commands

| Flag | Description |
|------|-------------|
| `--curative` | Run CurativePool 3.14t evaluation using CAIN framework |
| `--query-session` | Query last 20 session actions from `data/pams_events.db` |

## Integration

- **File:** `src/META/MetaWormSpawner.py` (CurativePool class, ~220 lines)
- **Wiring:** Lazy-init in `run_fleet()` — evaluates each worm before execution, blocks scope/necessity/frustration violations
- **Fleet governance gate:** `evaluate_action()` returns `"allowed"` or `"blocked"` for each proposed action

## CLI Usage Examples

```bash
# Run CurativePool evaluation
python src/META/MetaWormSpawner.py --curative

# Query session actions from DB
python src/META/MetaWormSpawner.py --query-session

# Run fleet with CurativePool governance
python src/META/MetaWormSpawner.py --run
```

## Known Issues

- **Stdlib logging shadowing:** If `import logging` fails after adding CORE to sys.path, the fix is to import stdlib `logging` BEFORE adding CORE, or check that `CORE/logging.py` has been renamed to `azazael_logging.py`.
- **Unicode in CLI:** Avoid emoji/unicode characters in print statements when running on Windows with cp1252 encoding.

## Dependencies

| Dependency | Purpose |
|------------|---------|
| Python 3.14t | Free-threaded (no-GIL) concurrent execution |
| `threading` | Daemon threads for pool execution, Lock for metrics |
| `sqlite3` | Session action database (`data/pams_events.db`) |

## Lessons

- LESSONS_MASTER.md #13 — CAIN 75-panel psychological analysis
- LESSONS_MASTER.md #14 — CurativePool for 3.14t architecture
- LESSONS_MASTER.md #15 — Thread ordering in concurrent pools
- LESSONS_MASTER.md #17 — CurativePool fleet governance pattern
- LESSONS_MASTER.md #18 — Thread-safe audit recording pattern

## Related Skills

- `azazael-codex` — CODEX systems, PAMS, MemoryBus, video generation
- `azazael-conventions` — Project coding conventions, anti-patterns
- `azazael-314t-master` — 3.14t free-threading mastery
