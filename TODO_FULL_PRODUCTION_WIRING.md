# AZAZAEL — Full Production Wiring TODO

> **SUPERSEDED as of Sep 2, 2026 — see `CODEBASE_AUDIT_TODO.md` (primary living production plan).** Legacy 15-area roadmap, kept for reference only.

> **Created:** May 29, 2026 — Codebuff Session Phase 12
> **Status:** Comprehensive roadmap for production readiness
> **Companion:** azazael/skills/azazael-production.md, azazael/MEMORIES.md

---

## State Snapshot (May 29, 2026)

| Metric | Value |
|--------|-------|
| Syntax-clean Python files | 256 |
| Worms in registry | 77 |
| Worm categories | 17 |
| Desktop standalone EXEs | 37 (all operational) |
| BAT launchers | 37 (all fixed) |
| Integration tests | 28 |
| Pytest tests | 20 |
| CI workflows | 1 |
| Skills created | 2 (exe-build, standalone-audit) |
| Broken EXEs fixed | 3 (POPUP_Immersive, Auto_Doc_Gen, QL_Optimizer) |
| Unbuilt Desktop modules | 9 (source available, no EXE) |
| Missing-source modules | 2 (Complete_Systems, Twitler_Analysis) |

---

## 🔴 CRITICAL — Blocking Production (0/8 complete)

### 1. Test Coverage (0 tests → 50+)
> Lessons: [#14](LESSONS_MASTER.md) (store injection), [#15](LESSONS_MASTER.md) (test infra pays), [#16](LESSONS_MASTER.md) (verify queries first)
- [ ] Unit tests for CLUSTERWORMS.py dynamic resolution (3 strategies)
- [ ] Unit tests for NATURE_CLUSTERS.py category discovery
- [ ] Unit tests for METACLUSTER.py routing engine (70 routes, 594 paths)
- [ ] Integration tests for parallel execution (FreeThreadPool, work-stealing)
- [ ] Integration tests for cross-nature orchestration
- [ ] Mock tests for PAMS/MemoryBus event recording
- [ ] Regression tests for all 226 worms (import + register + basic smoke)
- [ ] Test coverage reporting (pytest-cov, target: 60%+)

### 2. Error Recovery (0/5)
> Lessons: [#10](LESSONS_MASTER.md) (thread safety), [#20](LESSONS_MASTER.md) (lazy init discipline)
- [ ] Timeout handling: daemon threads must be joined or killed
- [ ] Partial failure handling: should cluster continue or abort?
- [ ] Circuit breaker: stop if error rate exceeds threshold (90%+ in 10s)
- [ ] Retry with exponential backoff (replacing fixed 0.1s sleep)
- [ ] Dead letter queue for failed executions (circuit_breaker.py exists but untested)

### 3. Configuration (0/3)
> Lessons: [#1](LESSONS_MASTER.md) (TOML forward slashes on Windows)
- [ ] Centralized config file (YAML/TOML) — azazael.yaml at project root
- [ ] Environment variable validation in paths.py (G_DRIVE, DESKTOP, etc.)
- [ ] Per-nature config overrides (security vs network timeout policies)

---

## 🟡 HIGH PRIORITY (0/8 complete)

### 4. Desktop Standalone — Complete All EXE Builds (0/9)
- [ ] Build CLUSTERWORMS_314t.exe (source: CORE/WORMS/CLUSTERWORMS.py)
- [ ] Build CONCURRENCY_314t.exe (source: CORE/WORMS/CONCURRENCY.py)
- [ ] Build METACLUSTER_314t.exe (source: CORE/WORMS/METACLUSTER.py)
- [ ] Build NATURE_Clusters_314t.exe (source: CORE/WORMS/NATURE_CLUSTERS.py)
- [ ] Build SMARTDISK_314t.exe (source: CORE/WORMS/SMARTDISK.py)
- [ ] Build Create_Video_314t.exe (source: CODEX/VIDEOS/create_video.py)
- [ ] Build Matrix_Video_314t.exe (source: CODEX/VIDEOS/generate_matrix_video.py)
- [ ] Build Compress_Video_314t.exe (source: CODEX/VIDEOS/compress_video.py)
- [ ] Build Video_Popup_314t.exe (source: CODEX/VIDEOS/video_popup.py)

### 5. Performance Optimization (0/6)
> Lessons: [#20](LESSONS_MASTER.md) (lazy imports), [#21](LESSONS_MASTER.md) (fast-path), [#22](LESSONS_MASTER.md) (module splitting), [#30](LESSONS_MASTER.md) (HTTP timeouts), [#31](LESSONS_MASTER.md) (profile first)
- [ ] Profile parallel execution bottleneck (cProfile on 100-worm cluster run)
- [ ] Consider ThreadPoolExecutor instead of raw threading.Thread
- [ ] Cache worm registry lookups (currently O(n) scan per query)
- [ ] Lazy-load worm modules (all 77 import at startup)
- [ ] Cache Mermaid graph output (regenerated every call)
- [ ] Batch PAMS events (individual writes currently)

### 6. Documentation (0/5)
- [ ] Module-level docstrings for all new cluster files
- [ ] Architecture diagram in root README (can auto-generate from Mermaid)
- [ ] API reference for ClusterWORMZ, MetaCluster
- [ ] Usage examples with CLI output
- [ ] Troubleshooting guide (common errors + fixes from ERROR_LOG.md)

### 7. Observability (0/4)
> Lessons: [#14](LESSONS_MASTER.md) (store injection), [#18](LESSONS_MASTER.md) (API parity), [#32](LESSONS_MASTER.md) (browser-use needs server)
- [ ] Structured logging (JSON) for cluster operations
- [ ] Metrics: execution count, duration, success rate per cluster type
- [ ] Health check endpoint / CLI command
- [ ] Alert on worm registration drift (count changes)

---

## 🟢 MEDIUM PRIORITY (0/8 complete)

### 8. Registry Enhancements (0/4)
- [ ] Validate registry at startup (detect missing deps, circular imports)
- [ ] Registry versioning (detect when worms change)
- [ ] Worm dependency graph visualization
- [ ] Worm health scoring (import success, config validity, test coverage)

### 9. Cross-Nature Workflows (0/4)
- [ ] Standard workflow templates (security scan → vulnerability report → auto-fix)
- [ ] Workflow DSL for defining multi-step orchestration
- [ ] Conditional routing (if error_rate > X, escalate to MetaCluster)
- [ ] Workflow history and replay (PAMS audit trail)

### 10. CODEX Video Pipeline (0/5)
- [ ] Install ffmpeg on build machine
- [ ] Test full HTML → MP4 generation
- [ ] Progress bar for video generation (tqdm)
- [ ] Multiple output formats (MP4, WebM, GIF)
- [ ] Batch generation from template directory

---

## 🔵 LOW PRIORITY (0/6 complete)

### 11. Code Hygiene (0/3)
> Lessons: [#19](LESSONS_MASTER.md) (import hygiene), [#7](LESSONS_MASTER.md) (nohup/cleanup), [#17](LESSONS_MASTER.md) (HAS_* flags)
- [ ] Standardize error handling — remove bare `except:` clauses
- [ ] Add `__all__` to all module exports (77 worm files + 20 cluster files)
- [ ] Consolidate hardcoded paths (still ~10 in QL_FILE_OPTIMIZER, CODEX files)

### 12. UI/UX (0/3)
- [ ] Web dashboard for cluster status (Flask/React)
- [ ] Real-time Mermaid rendering in browser
- [ ] CLI `azazael cluster status --live`

### 13. Deployment (0/4)
> Lessons: [#7](LESSONS_MASTER.md) (nohup not a daemon — use Task Scheduler), [#6](LESSONS_MASTER.md) (winget timeout)
- [ ] Single-entry `azazael` CLI (merge azazael-core into main CLI)
- [ ] Docker container for reproducible builds
- [ ] Scheduled cluster runs (cron / Windows Task Scheduler) — see [#7](LESSONS_MASTER.md)
- [ ] Git hook integration (pre-commit worm check)

---

## 🏗️ Technical Debt (0/4)

### 14. Path Resolution (0/2)
- [ ] Eliminate remaining 10+ hardcoded `C:/Users/clint/Desktop` paths
- [ ] Fix `QL_FILE_OPTIMIZER.py` hardcoded DESKTOP_PATH constant

### 15. Deprecation Shim Cleanup (0/2)
- [ ] Verify all 14 deprecation shims have valid canonical sources
- [ ] Rebuild 4 shim-sourced EXEs from canonical files directly (File_Manifest, Changelog_Gen, Matrix_Animation, QL_Optimizer)

---

## 📊 Effort Estimates

| Priority | Items | Tasks | Est. Hours |
|----------|-------|-------|------------|
| 🔴 Critical | 3 | 16 | 40-60 |
| 🟡 High | 4 | 24 | 20-40 |
| 🟢 Medium | 3 | 13 | 15-30 |
| 🔵 Low | 3 | 10 | 15-25 |
| 🏗️ Tech Debt | 2 | 4 | 5-10 |
| **TOTAL** | **15** | **67** | **95-165** |

---

## 🎯 Recommended Execution Order

1. **Build remaining 9 Desktop EXEs** (2-3 hours) — immediate, unblocks standalone suite
2. **Write test suite for cluster modules** (15-20 hours) — critical for production confidence
3. **Implement error recovery** (10-15 hours) — circuit breaker, retry, dead letter queue
4. **Centralize configuration** (5-8 hours) — YAML config file, env var validation
5. **Performance optimization** (8-12 hours) — profiling, caching, lazy loading
6. **Documentation + Observability** (10-15 hours) — docstrings, logging, metrics
7. **Registry + Workflow enhancements** (10-15 hours) — validation, DSL, history
8. **Deployment pipeline** (5-8 hours) — Docker, CI/CD, single CLI

---

## 📁 Related Files

- [`azazael/LESSONS_MASTER.md`](LESSONS_MASTER.md) — All 35+ lessons learned categorized (canonical reference)
- `azazael/skills/azazael-production.md` — Detailed gap analysis
- `azazael/skills/azazael-exe-build.md` — Nuitka build procedures
- `azazael/skills/azazael-standalone-audit.md` — Periodic EXE audit procedures
- `azazael/MEMORIES.md` — Persistent cross-session knowledge
- `azazael/ERROR_LOG.md` — All 28 recorded errors with root causes
- `azazael/PRODUCTION_TODO.md` — (Legacy) Original production gaps list
- `Desktop/AZAZAEL_Standalone/build_all.py` — EXE build orchestrator
- `Desktop/AZAZAEL_Standalone/regenerate_bats.py` — BAT launcher fixer
- `packages/azazael-core/run_tests.py` — Integration test suite
- `.github/workflows/build.yml` — CI workflow
