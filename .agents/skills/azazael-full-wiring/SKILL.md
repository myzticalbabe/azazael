---
name: azazael-full-wiring
description: Complete AZAZAEL production wiring guide — all 17 areas, 70 tasks, priority ordering, and cross-project integration plan
metadata:
  category: planning
  project: azazael
  priority: critical
---

# AZAZAEL — Full Production Wiring Guide

## Overview

This skill documents the complete production wiring roadmap for AZAZAEL — everything needed to go from a development codebase to a production-grade system. It covers 17 areas across 5 priority tiers with 70 specific tasks.

**Canonical reference:** `azazael/CODEBASE_AUDIT_TODO.md` (the living document)
**Companions:** `azazael/DESKTOP_PROJECTS_AUDIT.md`, `azazael/MEMORIES.md`

---

## State Snapshot (May 29, 2026)

| Metric | Value |
|--------|-------|
| Desktop standalone EXEs | 49 (all operational) |
| Python source files | 292 (all syntax-clean) |
| Worms in registry | 77 across 17 categories |
| Deprecation shims | 14 |
| Hardcoded paths eliminated | 67+ |
| Errors logged & resolved | 33 |
| Skills registered | 24 (+ this one) |
| Desktop projects audited | 14 |
| EXEs needing PYTHONPATH at build | 2 (CONCURRENCY, SMARTDISK) |
| EXEs needing tk-inter plugin | 5 (GUI modules) |

---

## 🔴 CRITICAL — Blocking Production (16 tasks, 40-60 hrs)

### 1. Test Coverage
    - Unit tests for cluster modules (CLUSTERWORMS, METACLUSTER v2 flat)
- Integration tests for parallel execution (FreeThreadPool, work-stealing)
- Regression tests for all 226 worms
- Test coverage reporting (pytest-cov, target 60%+)
- **Build command:** `python packages/azazael-core/run_tests.py`

### 2. Error Recovery
- Timeout handling for daemon threads
- Circuit breaker (circuit_breaker.py exists, untested)
- Retry with exponential backoff
- Dead letter queue for failed executions

### 3. Configuration
- Centralized YAML/TOML config (azazael.yaml)
- Environment variable validation
- Per-nature config overrides

---

## 🟡 HIGH PRIORITY — Path Audit, Hygiene, Performance (26 tasks, 25-50 hrs)

### 4. Path Audit & Portability
- Remaining hardcoded paths: data dictionaries in COMPLETE_SYSTEMS_ANALYSIS (9), FULL_ECOSYSTEM_ANALYSIS (6), TWITLER_ANALYSIS (1) — informational, not functional
- Fix AZAZAEL_TOOLKIT/update_docs_paths.py hardcoded mappings
- Fix CODEX/VIDEOS/*.py hardcoded output paths
- Fix CORE/PYTHON_MANAGER.py hardcoded venv paths

### 5. Deprecation Shim Cleanup
- 14 shims active — verify zero consumers before removing
- Create automated shim auditor script
- Target: remove all shims in Phase 16

### 6. Import Hygiene
- Run autoflake across all 292 files (completed for canonical + comprehensive files)
- Install ruff for broader linting
- Remove all bare `except:` clauses

### 7. Performance Optimization
- Profile parallel execution bottleneck
- Cache worm registry lookups
- Lazy-load worm modules
- Batch PAMS events

### 8. Documentation
- Module-level docstrings for cluster files
- Architecture diagram (can auto-generate from Mermaid)
- Troubleshooting guide from ERROR_LOG.md

### 9. Observability
- Structured JSON logging
- Metrics: execution count, duration, success rate
- Health check endpoint

---

## 🟢 MEDIUM PRIORITY (13 tasks, 15-30 hrs)

### 10. Registry Enhancements
- Validate registry at startup
- Registry versioning
- Worm dependency graph visualization

### 11. Cross-Nature Workflows
- Standard workflow templates
- Workflow DSL
- Conditional routing

### 12. CODEX Video Pipeline
- Install ffmpeg
- Test HTML -> MP4 generation
- Multiple output formats

---

## 🏗️ Technical Debt (5 tasks, 5-10 hrs)

### 13. build_all.py Robustness
- `env` scoping: ✅ Fixed (Phase 12)
- `--output-dir`: ✅ Present (Phase 12)
- Pre-build validation script needed
- Post-build verification (--help test) needed

### 14. Nuitka Build Patterns
- Document 3 patterns: normal, PYTHONPATH-dependent, tkinter-dependent
- NOFOLLOW_EXTRAS filtering for size control
- Build output verification

---

## 🎯 Recommended Execution Order

1. **Fix build pipeline robustness** (1 hr) — pre/post-build validation
2. **Remove remaining hardcoded paths** (2-3 hrs) — data dicts, video paths
3. **Write test suite** (15-20 hrs) — critical for production
4. **Implement error recovery** (10-15 hrs) — circuit breaker, retry
5. **Centralize configuration** (5-8 hrs) — YAML, env vars
6. **Import hygiene sweep** (3-5 hrs) — autoflake, ruff, bare excepts
7. **Performance optimization** (8-12 hrs) — profiling, caching
8. **Remove deprecation shims** (2-3 hrs) — after verifying zero consumers
9. **Documentation + Observability** (10-15 hrs)
10. **Registry + Workflow enhancements** (10-15 hrs)
11. **Deployment pipeline** (5-8 hrs) — Docker, CI/CD

---

## Desktop Cross-Project Integration

### Projects to Wire Together

| AZAZAEL System | Desktop Project | Integration |
|---------------|-----------------|-------------|
| Worm registry (226 worms) | EveUnleashed_Selector | Agent types -> worm categories |
| Observability worms | PerformanceMonitor | Telemetry -> SystemZ/NETWORXZ |
| PAMS/MemoryBus | Ultimate_Agent_Selector | Memory bridge -> event recording |
| AZAZAEL_LAUNCHER.bat | WSL Models | Add WSL model launch to menu |
| CODEX Studio | CODEX_Studio.bat | Already wired (launcher -> src/CODEX/) |
| AZAZAEL_Standalone | build_all.py | Add external project EXEs to build list |

### Projects to Archive
- `Azazael_UNIFIED` -> `G:/AZAZAEL/` (re-attempt, partial content remains)
- `CODEX` -> `G:/AZAZAEL/` (re-attempt)
- `CODEX_Studio_Output` -> `G:/AZAZAEL/` (re-attempt)
- `METAWORMS` -> `G:/AZAZAEL/` (output data only)

### Projects to Decide
- `agent_system` — Develop or delete? (skeletal, 3 empty __init__.py files)
- `SysTools_JSON_Converter` — Archive or keep? (data only, no code)

---

## Key Build Commands

### Desktop EXE Build
```bash
cd Desktop/AZAZAEL_Standalone
python build_all.py              # Build all 49 EXEs
python build_all.py CONCURRENCY  # Build single module
python regenerate_bats.py        # Regenerate BAT launchers
```

### Nuitka Build with PYTHONPATH (for CORE-dependent modules)
```bash
# Python 3.14t is the ONLY build Python. Run patch before building.
python azazael/docs/scripts/patch_nuitka_314t.py --apply

PYTHONPATH="C:/Users/clint/src" python -m nuitka \
  --standalone --onefile --assume-yes-for-downloads \
  --output-filename=MODULE_314t.exe \
  --nofollow-import-to=torch --nofollow-import-to=optree \
  C:/Users/clint/src/CORE/WORMS/MODULE.py
```

### Test Suite
```bash
cd azazael/packages/azazael-core
python run_tests.py
```

### Source-of-Truth Sync
```bash
cd src
python -c "import shutil; from pathlib import Path; ..."
# See SESSION_INSIGHTS_2026-05-29_PHASE14.md for full script
```
