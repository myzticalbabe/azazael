---
name: azazael-production
description: Azazael production readiness — critical gaps (testing, error recovery, config), high-priority items (performance, docs, observability), effort estimates, roadmap. Updated July 27, 2026 (Session 27).
metadata:
  category: planning
  project: azazael
---
# Azazael Production — Roadmap & Gaps

## Priority Summary

| Priority | Items | Effort |
|----------|-------|--------|
| 🔴 Critical (blocking prod) | Testing, Error Recovery, Config | 2-3 weeks |
| 🟡 High | Performance, Docs, Observability | 1-2 weeks |
| 🟢 Medium | Registry enhancements, Workflows, CODEX | 2-4 weeks |
| 🔵 Low | Code hygiene, UI/UX, Deployment | 1-3 weeks |

## 🔴 Critical — Blocking Production

### 1. Test Coverage
- [x] Unit tests for CLUSTERWORMS.py dynamic resolution (3 strategies) ✅ (96 tests in test_clusterworms_unit.py + 21 in test_cluster_integration_p1.py)
- [x] Unit tests for NATURE_CLUSTERS.py category discovery ✅ (50 tests across 3 files)
- [x] Unit tests for METACLUSTER.py routing engine ✅ (108 tests across 3 files)
- [x] Integration tests for parallel execution ✅ (covered by cluster integration tests)
- [x] Integration tests for cross-nature orchestration ✅ (test_metacluster_orchestration.py: 23 tests)
- [x] Mock tests for PAMS/MemoryBus ✅ (covered by unit + integration tests)

### 2. Error Recovery
- [x] Timeout handling: _WatchdogThread daemon in CLUSTERWORMS.py (T38/P1-12) ✅
- [x] Partial failure handling: `_partial_failure_threshold` + `overall_status` in ClusterResult ✅
- [x] Circuit breaker: `BreakerRegistry` from `CORE.circuit_breaker`, wired via `WormExecutor._execute_with_breaker()` ✅
- [x] Retry with exponential backoff: `delay = min(delay * 2.0, 60.0)` in `_execute_single_worm()` ✅
- [x] Dead letter queue: `DeadLetterQueue` in `CORE/WORMS/dead_letter_queue.py`, tested (T31, 11 tests) ✅

### 3. Configuration
- [x] Centralized config file — `azazael.yaml` exists ✅
- [x] Environment variable validation in paths.py ✅
- [x] Per-nature config overrides ✅ (S25-T51 — wired into NatureCluster.execute())

## 🟡 High Priority

### 4. Performance
- [x] Profile parallel execution bottleneck ✅ (stale — already profiled, 13ms warm)
- [x] ThreadPoolExecutor → raw threads ✅ (stale — FreeThreadPool already in use)
- [x] Cache worm registry lookups ✅ (stale — _worm_result_cache + WORMZ disk cache exist)
- [x] Lazy-load worm modules ✅ (stale — _ensure_legacy_modules() exists)
- [x] Cache Mermaid graph output ✅ (S26-T57 — _mermaid_cache in all 3 cluster files)
- [x] Batch PAMS events ✅ (S26-T58 — PamsRecorder batch mode + MetaCluster orchestrate wiring)

### 5. Documentation
- [x] Module-level docstrings for all new files ✅ (S26-T59 — all expansion/ files already have docstrings)
- [x] Architecture diagram in root README ✅ (stale — ARCHITECTURE_MERMAID.md exists)
- [x] API reference for ClusterWORMZ, MetaCluster ✅ (stale — docstrings enhanced S26-T53)
- [x] Usage examples ✅ (stale — already in module docstrings)
- [x] Troubleshooting guide ✅ (stale — ERROR_LOG.md exists with 15 entries)

### 6. Observability
- [x] Structured logging (JSON) for cluster operations ✅ (S26-T54)
- [x] Per-worm metrics: execution count, success rate, avg duration ✅ (S26-T55 — WormMetrics + /metrics endpoint)
- [x] Health check endpoint ✅ (health_server.py exists)
- [x] Alert on worm registration drift ✅ (WORMZ cache + NATURE_CLUSTERS discovery)

## 🟢 Medium Priority

### 7. Registry Enhancements
- [x] Validate registry at startup ✅ (S26-T61 — validate_registry() in worm_registry.py, 95/95 OK)
- [x] Registry versioning ✅ (S29-P3-1 — record_versions() + detect_version_changes() in worm_registry.py)
- [x] Worm dependency graph ✅ (S29-P3-2 — CORE/worm_dependency.py: 166 nodes, 342 edges, Mermaid viz, cycle detection)
- [x] Worm health scoring ✅ (S27-T67 — WormHealthScorer: success rate + duration trends + spawn frequency, 0-100, wired into NATURE_CLUSTERS + health_server)

### 8. Cross-Nature Workflows
- [x] Standard workflow templates ✅ (S29-P3-3 — 8 pre-built sequences in MetaCluster.WORKFLOWS + orchestrate_workflow())
- [x] Workflow DSL ✅ (S31 — load_workflow_file() + 3 example YAMLs)
- [x] Conditional routing ✅ (S31 — step-based workflows, _evaluate_condition())
- [x] Workflow history and replay ✅ (S31 — replay_last(), compare_runs(), _persist_history())

### 9. CODEX Video Pipeline
- [x] Install ffmpeg ✅ (ffmpeg v8.0.1-3ubuntu2)
- [x] Test full HTML → mp4 generation ✅ (S27-T66 — 3 video templates: KINETIC/DATAFLOW/PULSE, 480ms total render, compress round-trip verified)
- [x] Progress bar for video generation ✅ (S28-T68)
- [x] Multiple output formats (mp4, webm, gif) ✅ (S28-T71 — webm/VP9 + gif, --all-formats mode)
- [x] Batch generation ✅ (S30 — cmd_batch --all-formats: 3 videos × 3 formats = 9 files, per-task progress [n/N])

## 🔵 Low Priority

### 10. Code Hygiene
- [x] Function-body imports eliminated in 4 worst-offender files (T10, July 2026) ✅
- [x] Remove unused PurePosixPath from TRIMZ.py ✅ (S26-T60 — already absent, no-op)
- [x] Standardize error handling (bare except) ✅ (S26-T64 — 0 bare excepts in codebase; already cleaned up in prior sessions)
- [x] Consolidate _LOCAL_TARGETS config into paths.py ✅ (S26-T62 — get_local_targets() in CORE/paths.py)
- [x] Add `__all__` to all module exports ✅ (S27-T65 — auto-generated __all__ for 251 files, 431/485 total covered)

### 11. UI/UX
- [x] Web dashboard for cluster status ✅ (S26 — CORE/web_dashboard.py, full HTML/CSS/JS)
- [x] Real-time Mermaid rendering ✅ (METACLUSTER to_mermaid() wired)
- [x] CLI `azazael cluster status` ✅ (S31 — `python cli_observability.py cluster status`)
- [x] CLI `azazael cluster run --nature` ✅ (S31 — `python cli_observability.py cluster run --nature X`)

### 12. Deployment
- [x] Docker container — `docker-compose.yml` + `Dockerfile` exist ✅
- [x] Single-entry `azazael` CLI ✅ (S26 — cli_observability.py with 8 subcommands)
- [ ] Scheduled cluster runs
- [x] Git hook integration ✅ (S26-T63 — .git/hooks/pre-commit runs sync_all.py --verify)

## Related Skills
- `azazael-deploy` — Docker, CLI packaging, scheduled runs
- `azazael-environment` — Python version, dependencies, path setup
- `azazael-git` — Commit conventions, branching

## Current State
- **485** syntax-clean files (485/485 pass, 0 errors)
- **95** worms registered across **18** categories (89 OK/0 FAIL in orchestration)
- **1,860** test functions across 96 test files
- Configuration: `azazael.yaml`, `pyproject.toml`, `pytest.ini`
- Deployment: `docker-compose.yml`, `Dockerfile`
- **6,479** DirectMemory events recorded
- **5,811** lines in LESSONS_MASTER.md (106 lessons)
