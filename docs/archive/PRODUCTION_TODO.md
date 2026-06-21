# PRODUCTION_TODO — Azazael Ecosystem Production Roadmap

> *Generated: May 28, 2026 — Last updated: June 3, 2026 — **LangChain 3.14t wheel fix + Codebase Dedup + Lessons #19-23 + Error #54 + No-monkeypatches rule***
> *Current state: 303+ Python files, 79 registered worms across 17 categories, 37/37 CurativePool tests pass (3.14t), 52 Desktop EXEs, DB Grade A healthy. LangChain stack fully native on 3.14t (no fallbacks). Codebase dedup: 4 duplicates eliminated (3 stale copies deleted + 1 consumer updated). Mypy round: 5 CORE files cleaned (CLUSTERWORMS, METACLUSTER, local_memory — 0 own-file errors). Real bug found: learning.py `result` used-before-def. Permanent rule: never patch site-packages.*

---

## 🚨 Lessons Learned — June 3, 2026 Session (Part 2) — LangChain 3.14t Fix + Codebase Dedup + Knowledge Distillation

Lessons from this session: **#19, #20, #21, #22, #23** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

**Key outcomes:**
- ✅ **LangChain 3.14t wheel fix** — pydantic-core and uuid-utils cp314t wheels reinstalled (were segfaulting)
- ✅ **All fallback patches reverted** — uuid_utils/__init__.py, pydantic_core/__init__.py, conftest.py, pytest.ini — all originals restored
- ✅ **37/37 CurativePool tests pass** with native extensions, no plugin suppression
- ✅ **Codebase dedup** — `azazael_toolkit.py` in TOOLS/ → deprecation shim (identical 53-line file removed)
- ✅ **ERROR_LOG.md** updated: Error #54 (pydantic-core/uuid-utils 3.14t wheel segfault)
- ✅ **MEMORIES.md** updated: Session 2026-06-03 (Part 2) — LangChain 3.14t fix
- ✅ **LESSONS_MASTER.md** updated: Lessons #19-23 added (9 categories, 47 total)
- ✅ **Permanent rule**: No monkeypatches — never patch site-packages, fix the actual installation

## 🚨 Lessons Learned — June 3, 2026 Session (Mypy Round) — 5 CORE Files Cleaned + Real Bug Found

Lessons from this session: **#32** (double-checked locking for 3.14t free-threading) — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

**Key outcomes:**
- ✅ **CLUSTERWORMS.py** — 0 own-file mypy errors (~24 fixed): fallback signatures, Optional params, sentinel `# type: ignore[misc, assignment]`, `aggregate_results()` float typing, `clear_messages` signature
- ✅ **METACLUSTER.py** — 0 own-file mypy errors (~9 fixed): `NATURE_DEFINITIONS` assignment type, `CrossNatureRoute` type:ignore moved to correct line, `truthy-function` silenced, `self.ncm` None guard
- ✅ **NATURE_CLUSTERS.py** — Fixed `truthy-function`, `cluster is not None` guard, sentinel assignments. 13 deep-structural errors remain (sentinel `Any` propagation → `object` type inference in `retry_failed_worms`/`get_dead_letter_summary`)
- ✅ **local_memory.py** — All ~30 mypy errors fixed: 15+ `Optional[str/dict/list/int]` param defaults, `Optional[threading.Thread]` annotations, `cursor.lastrowid or 0` pattern, `is not None` guards
- ✅ **learning.py** — ~30+ Optional param defaults fixed. **BUG FIX**: `result` dict moved before persistence block (was used-before-definition — `result["registered_model"]` referenced before `result = {...}`)
- ✅ **CI workflow** — `.github/workflows/test-3.14t.yml` now has mypy step before test suite
- ✅ **Lesson #32** — Double-checked locking pattern documented in LESSONS_MASTER.md

## 🚨 Dedup Round — 3 Stale Copies Deleted + 1 Consumer Updated

**Key outcomes:**
- ✅ **Deleted** `src/AZAZAEL_TOOLKIT/AzazaelDynamicLogger.py` (198 lines) — 0 Python consumers, stale copy of root canonical
- ✅ **Deleted** `src/UTILITIES/AzazaelDynamicLogger.py` (70 lines) — compressed copy, 1 consumer updated
- ✅ **Deleted** `src/UTILITIES/PamsRecorder.py` (194 lines) — stale v1.0 copy, canonical is CORE/PamsRecorder.py v2.0
- ✅ **Updated** `src/UTILITIES/Loggers/__init__.py` — changed relative import `from ..AzazaelDynamicLogger` → absolute import from root
- ✅ **Confirmed not duplicates**: AZAZAEL_TOOLKIT root-name files (root files are thin wrappers, not stale copies); METAWORMS_ENRICHED.py classes (independent implementations); CONCURRENCY.py WormExecutor (different context)

## 🚨 Lessons Learned — June 2, 2026 Session (D: Drive Cleanup, CODEX Downloads & DB Integration)

Lessons from this session: **#14, #18, #32, #8-9, #6, #7, #11** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

## 🚨 Lessons Learned — June 2, 2026 Session (D: Drive Cleanup & CODEX Downloads)

Lessons from this session: **#33, #36, #37, #5** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

---

## 🚨 Lessons Learned — Phase 5 Session (2026-06-01)

Lessons from this session: **#29, #34, #35, #16** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

## 🚨 Lessons Learned — Desktop Standalone Session (2026-06-01 afternoon)

Lessons from this session: **#1, #17, #25, #28, #27, #26** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

---

## 🔴 CRITICAL (Blocking Production)

### 1. Test Coverage *(67 unit tests exist — see Phase 2)*
> Lessons: [#14](LESSONS_MASTER.md) (store injection), [#15](LESSONS_MASTER.md) (test infra pays), [#16](LESSONS_MASTER.md) (verify queries first)
- [x] (Phase 2): Unit tests for FreeThreadedAgent, AgentPool, MemoryBus — 67 passing
- [x] Refactor all test files from module-level `sys.exit()` to `def test_*()` functions — **DONE**
- [ ] Unit tests for `CLUSTERWORMS.py` dynamic resolution (strategy 1/2/3)
- [ ] Unit tests for `NATURE_CLUSTERS.py` category discovery
- [ ] Unit tests for `METACLUSTER.py` routing engine
- [ ] Integration tests for parallel execution path
- [ ] Integration tests for cross-nature orchestration
- [ ] Mock tests for PAMS/MemoryBus recording

> **3.14t test status (2026-06-03, FINAL):**
> - ✅ **LangChain stack fully native** — pydantic-core 2.46.4 + uuid-utils 0.16.0 with working cp314t wheels (no fallbacks)
> - ✅ **37/37 CurativePool tests pass** on 3.14t with native extensions, no plugin suppression
> - ✅ **pydantic-core** segfault fixed via `pip install --force-reinstall --no-deps pydantic-core` + `pip install --upgrade pydantic`
> - ✅ **uuid-utils** 0.16.0 has proper `cp314-cp314t-win_amd64.whl` — upgraded from broken version
> - ✅ **All fallback patches removed** — uuid_utils/__init__.py, pydantic_core/__init__.py, conftest.py, pytest.ini all reverted to originals
> - `psutil` segfault **FIXED** via `pip install --force-reinstall --no-deps psutil` (selected cp314t wheel) — Error #49 resolved
> - **8 test files pass standalone on 3.14t** (188+ tests): test_agent.py (16), test_memorybus.py (32), test_pool.py (19), test_worm_imports.py (14), test_cluster_worms.py (5), test_clusterworms_unit.py (39), test_config_and_breaker.py (36), test_nature_clusters_unit.py (27)
> - **1 file slow** (test_metacluster_unit.py ~5 min): full MetaCluster orchestration runs 85+ worms across 17 natures — use `--timeout 420`
> - **17 DLQ tests added** (8 test_dlq.py + 9 test_dlq_watch.py) — all passing
> - **RL production pipeline verified** — PyTorch 2.12.0 + SB3 2.8.0 + gymnasium 1.2.3 end-to-end (test_rl_314t.py)
> - pytest 9.0.3 still segfaults on 3.14t (Error #48) — use standalone `python tests/test_*.py` or `python run_tests.py`
> - Runner: `python run_tests.py` (or `--skip-slow` for quick runs)

### 2. Error Recovery & Resilience
> Lessons: [#10](LESSONS_MASTER.md) (thread safety), [#20](LESSONS_MASTER.md) (lazy init discipline)
- [ ] Timeout handling: daemon threads still run after timeout — add Thread.stop() or cancellation token
- [ ] Partial failure: if 3/5 worms fail, should cluster continue or abort?
- [x] Circuit breaker: stop executing worms in a cluster if error rate exceeds threshold — **DONE**
- [x] Retry with exponential backoff — **DONE**
- [x] Dead letter queue for failed worm executions — **DONE**


### 3. Configuration Management
> Lessons: [#1](LESSONS_MASTER.md) (TOML forward slashes on Windows)
- [ ] Centralized config file (YAML/TOML) for cluster timeouts, retry counts, parallelism
- [ ] Environment variable validation in `paths.py`
- [ ] Per-nature config overrides (e.g., security worms need longer timeout)

---

## 🟡 HIGH PRIORITY

### 4. Performance Optimization
> Lessons: [#20](LESSONS_MASTER.md) (lazy imports), [#21](LESSONS_MASTER.md) (fast-path), [#22](LESSONS_MASTER.md) (module splitting), [#30](LESSONS_MASTER.md) (HTTP timeouts), [#31](LESSONS_MASTER.md) (profile first)
- [ ] Profile parallel execution bottleneck (thread creation overhead)
- [ ] Consider `concurrent.futures.ThreadPoolExecutor` instead of raw threads
- [ ] Cache worm registry lookups (currently re-importing on each resolution)
- [ ] Lazy-load worm modules (import only when needed)
- [ ] Mermaid graph generation: cache output, only regenerate on change
- [ ] Batch PAMS events (currently one event per action)
- [ ] **NEW** GPU inference: blocked by Intel oneAPI compiler bug (see [#34](LESSONS_MASTER.md)) — re-evaluate after 2026.1+ release

### 5. Documentation
- [ ] Module-level docstrings for all new files
- [ ] Architecture diagram (Mermaid) in root README
- [ ] API reference for `ClusterWORMZ.build_from_nature()`, `MetaCluster.discover_all()`
- [ ] Usage examples for common workflows
- [ ] Troubleshooting guide for common errors
- [ ] **NEW** GPU Acceleration section: document SYCL limitations and Intel Arc compatibility

### 6. Observability
> Lessons: [#14](LESSONS_MASTER.md) (store injection), [#18](LESSONS_MASTER.md) (API parity), [#32](LESSONS_MASTER.md) (browser-use needs server)
- [ ] Structured logging (JSON format) for all cluster operations
- [ ] Metrics export: execution count, duration, success rate per nature
- [ ] Health check endpoint for cluster/meta-cluster status
- [ ] Alert on worm registration drift (worms added/removed)
- [x] CodebuffTracker DB verification: 20,941 memories, 31 sessions, 10.46 MB — healthy
- [ ] **NEW** Disk usage monitoring: alert at 80%
- [x] **NEW** CodebuffTracker session_id alignment: fix `get_session_summary()` to match current session ID — **DONE**
- [x] **NEW** PostgreSQL adapter: CORE/postgres_memory.py (see [#18](LESSONS_MASTER.md))
- [x] **NEW** DatabaseMonitorWorm: live DB health monitoring (see [#14](LESSONS_MASTER.md))
- [x] **NEW** ScheduledDbMonitorWorm: hourly scheduled DB health checks
- [x] **NEW** CLI --db-monitor dashboard flag: live DB health snapshot
- [x] **NEW** Web dashboard DB Monitor card: live HTML card (see [#32](LESSONS_MASTER.md))

---

## 🟢 MEDIUM PRIORITY

### 7. Worm Registry Enhancements
- [ ] Validate registry at startup (check all registered worms are importable)
- [ ] Registry versioning: detect when worms are added/removed between sessions
- [ ] Worm dependency graph (e.g., PROCESSZ depends on SYSTEMZ)
- [ ] Worm health scoring based on execution history

### 8. Cross-Nature Workflows
- [ ] Define standard workflow templates (e.g., "audit" = security + diagnostic + reporting)
- [ ] Workflow DSL for composing nature pipelines
- [ ] Conditional routing: if security scan fails → escalate to diagnostic
- [ ] Workflow history and replay

### 9. CODEX Video Pipeline & Template Viewer
> Lessons: [#6](LESSONS_MASTER.md) (winget timeout), [#5](LESSONS_MASTER.md) (network drives), [#59-62](LESSONS_MASTER.md) (CODEX restoration)
- [x] Install ffmpeg (`winget install ffmpeg` or manual) — **DONE** (ffmpeg 8.1.1 via WinGet)
- [x] Test full `.html` → `.mp4` scrolling video generation — **DONE**
- [ ] Add progress bar to video generation
- [x] Support multiple output formats (mp4, webm, gif) — **DONE**
- [x] Batch video generation for all CODEX HTML files — **DONE**
- [x] Restore 8 CODEX CORE + 3 META scripts from G: drive — **DONE**
- [x] Fix circular import in all 11 deprecation shim files — **DONE**
- [x] CAIN template functional — verified generator + output — **DONE**
- [x] Unified template_viewer.html — switch between all 11 styles — **DONE**
- [x] generate_all.bat — batch regenerate all 11 styles — **DONE**

---

## 🔵 LOW PRIORITY (Nice to Have)

### 10. Code Hygiene
> Lessons: [#19](LESSONS_MASTER.md) (import hygiene), [#7](LESSONS_MASTER.md) (nohup/cleanup), [#17](LESSONS_MASTER.md) (HAS_* flags)
- [x] Remove `PurePosixPath` import from `WORMZ.py` (unused) — **DONE**
- [x] Remove unused imports (`hashlib`, `traceback`) from CLUSTERWORMS.py — **DONE** (June 3)
- [x] Unify sequential/parallel retry logic via `_execute_single_worm()` — **DONE** (June 3)
- [ ] Standardize error handling across all worms (some use bare except)
- [ ] Remove `sys` import from `paths.py` (unused) — **DONE**
- [x] Consolidate duplicate `_LOCAL_TARGETS` / `_DESKTOP_TARGETS` config from TRIMZ.py, ERRORZ.py, METAWORMS_ENRICHED.py, HYDRAMETA_UV.py into `CORE/paths.py` — **DONE** (June 3)
- [x] **Mypy cleanup — 5 CORE files cleared** (CLUSTERWORMS.py: 0 own-file errors, METACLUSTER.py: 0 own-file errors, local_memory.py: all fixed, learning.py: ~30 fixed + real bug, NATURE_CLUSTERS.py: partial) — **DONE** (June 3)
- [x] **CI mypy step added** to test-3.14t.yml (`mypy src/CORE/ --ignore-missing-imports --check-untyped-defs`) — **DONE** (June 3)
- [ ] Add `__all__` to all module exports
- [ ] **NEW** `eval` usage in `wsl2_cleanup.sh` — refactor to array-based dispatch

### 11. UI/UX
- [ ] Web dashboard for cluster status (replacing/tkinter supplementing)
- [ ] Real-time Mermaid graph rendering in browser
- [ ] CLI `azazael cluster status` command
- [ ] CLI `azazael cluster run --nature security` command

### 12. Deployment
> Lessons: [#7](LESSONS_MASTER.md) (nohup not a daemon — use Task Scheduler), [#6](LESSONS_MASTER.md) (winget timeout)
- [ ] Single-entry `azazael` CLI command (consolidate all worm CLIs)
- [ ] Docker container with all dependencies
- [ ] Scheduled cluster runs (cron/task scheduler integration) — see [#7](LESSONS_MASTER.md)
- [ ] Git hook integration (run diagnostics on commit)
- [x] **NEW** Schedule `azazael/scripts/wsl2_cleanup.sh` via Windows Task Scheduler — weekly Mon 6 AM
- [x] Weekly cleanup script: `azazael/scripts/wsl2_cleanup.sh` — created
- [x] **June 2:** D:\ fully cleaned (52,820 files → 30 music videos). G:\ serves as primary archive.
- [x] **June 2:** archive_system.py hardened with PROTECTED_PATTERNS, confirmation prompts, and --yes flag.
- [x] **June 2:** YouTube music video download pipeline verified (Firefox history → yt-dlp → D:\).

---

## 📊 Effort Estimates

## 🚨 Lessons Learned — June 3, 2026 Session (RL Compat + Production Prep + Dedup + Knowledge Distillation)

Lessons from this session: **#14, #15, #46, #47, #48, #49, #50** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

## 🚨 Lessons Learned — June 3, 2026 Session (Thread Migration + Registry Warm-Up SOP)

Lessons from this session: **#51, #52, #53** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

### Thread Migration Progress
- ✅ **workflow.py ThreadPoolExecutor migration** — Replaced raw `threading.Thread()` per-layer step execution with `ThreadPoolExecutor` + `as_completed()`. Fixed `concurrent.futures.TimeoutError` import (removed in Python 3.14 — using builtin). 7 other files assessed per lesson #50 and kept as-is (daemon threads appropriate for servers, lifecycle loops, measurement tools).
- ✅ **24/24 workflow tests pass** | **34/34 freethreading tests pass** | **6 DLQ + 3 retry + 7 routing + 3 NCM tests pass**

### Extended NATURE_CLUSTERS Tests
- ✅ **test_nature_clusters_extended.py** — NEW: 19 tests covering DLQ management, retry logic, cross-nature routing, NCM DLQ aggregation, definitions validation, discovery dedup, mermaid graph structure
- Uses `MockWorm` class (avoids registry discovery overhead for fast tests)
- 2 discovery-dependent tests (`test_discovery_dedup`, `test_mermaid_functions_structure`) require warm registry + 120s timeout

### Profiling Script
- ✅ **scripts/profile_clusterworms_parallel.py** — NEW: profiles CLUSTERWORMS parallel vs sequential execution across 4 cluster types (system, network, bibl, full). Reports min/max/avg/median/p95. Saves JSON results.

### Registry SOP Formalized
- ✅ **SYSTEM_INSTRUCTIONS.md** — Added Rules REG-1 through REG-4 mandating registry warm-up, adequate timeouts, caching awareness, and discovery-before-cluster-operations
- ✅ **LESSONS_MASTER.md** — Lesson #53: registry warm-up procedure with measured timings (~38s cold, <2s warm)

### RL Pipeline Verification Results
- ✅ PyTorch 2.12.0+cpu — `_C.cp314t-win_amd64.pyd` confirmed (proper cp314t build)
- ✅ gymnasium 1.2.3 — built from source (`--no-binary`), env creation + reset works
- ✅ stable-baselines3 2.8.0 — PPO model training (512 steps), save, load, predict all verified
- ✅ Full production pipeline: tensor ops → nn → env → train → persist → inference
- ✅ All 17 DLQ tests pass (8 DLQ + 9 watch)
- ✅ DB healthy: Grade A (100/100), 3.54 MB, 3,275 memories, 47 sessions

### Remaining RL Blockers
- ❌ opencv-python-headless 4.12.0.88 — segfault on 3.14t (awaiting 4.14.0 cp314t support)
- ❌ gym (old API) 0.26.2 — uninstalled, archived, incompatible

### Production Prep Progress (June 3, 2026)
- ✅ **Full 3.14t compat check**: 20/20 packages pass (--verbose confirms all categories)
- ✅ **CLUSTERWORMS.execute_all() FreeThreadPool migration** (v2.0.0 → v2.1.0)
  - Replaced raw threads + results_lock + cancel_event with FreeThreadPool + as_completed
  - Lock-free result collection (main thread sole writer)
  - Two-level TimeoutError handling (per-future + as_completed collective)
  - 34/34 freethreading integration tests pass
  - 17/17 DLQ + watch tests pass
- ✅ **check_314t_compat.py created** — categorized package checker with --quick/--verbose/--json
- ✅ **test_freethreading.py created** — 34 integration tests for FreeThreadPool, worker stealing, thread safety

## 🚨 Lessons Learned — June 3, 2026 Session (Agent Infrastructure — AgentRegistry, SB3Agent, MemoryBus)

Lessons from this session: **#54, #55, #56, #57** — see [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for details.

### Agent Registry
- ✅ **CORE/agent_registry.py** — NEW: @register_agent decorator, AGENT_REGISTRY global dict, auto-discovery (opt-in via AZAZAEL_AUTO_DISCOVER_AGENTS), AgentHealthReporter with instance tracking and aggregated health summaries, convenience functions (create_agent, get_agents_by_category, get_all_agent_categories)
- Uses `from __future__ import annotations` + `TYPE_CHECKING` for circular-import-safe FreeThreadedAgent reference

### SB3Agent
- ✅ **CORE/sb3_agent.py** — NEW: SB3Agent(FreeThreadedAgent) wrapping PPO/DQN/A2C with @register_agent
- `train(source, total_timesteps)` — extracts training data via DataPipelineWorm, creates gym environment from memory records, trains SB3 model
- `predict()`, `predict_batch()`, `save()`, `load()` — full inference lifecycle
- Auto ModelVersioner registration after training
- Correct env reward (action matched to severity level)
- `SB3AgentPool` — multi-agent pool with `train_parallel()` using `execute_many()` for true parallel

### MemoryBus Integration
- ✅ **Lazy init** — MemoryBus created on first use via `_ensure_bus()`, 0.5s PAMS timeout
- `send_message(target, action)`, `broadcast_message(action)`, `poll_messages()` — inter-agent messaging
- `_handle_bus_command()` — execute/get_stats/get_state/set_state/shutdown/ping
- PAMS deferred: agent_init event recorded on first `execute()` call

### RLTrainLoop Persistence
- ✅ **register_to_versioner()** — Q-table policy versioning via ModelVersioner
- ✅ **_save_q_table_to_store()** / **load_q_table_from_store()** — durable Q-table persistence
- ✅ Auto-registration after `train_from_memory()`

### TrainingOrchestrator (NEW)
- ✅ **TrainingOrchestrator worm** in `expansion/scheduling.py` — orchestrates SB3 deep RL pipeline on schedule
- Pipeline: DataPipelineWorm (extract) → SB3Agent (train PPO/DQN/A2C) → ModelVersioner (register)
- Daemon scheduler with configurable interval, responsive shutdown via stop_event
- Records all runs to LocalMemoryStore for observability
- Unlike ScheduledTrainingWorm (Q-learning), uses real SB3 deep RL

### Verified
- ✅ SB3Agent: PPO/DQN/A2C creation, prediction, environment, pool — all working
- ✅ AgentHealthReporter: instance registration, health checks, summary — all working
- ✅ MemoryBus: lazy init (0.5s), send/broadcast/poll — all working
- ✅ RLTrainLoop: ModelVersioner persistence — verified
- ✅ TrainingOrchestrator: creation, execute(), scheduler start/stop — verified

### P0 Production Items Status
- 🔴 Unit tests for CLUSTERWORMS dynamic resolution — existing (39 tests)
- 🔴 Unit tests for METACLUSTER.py routing engine — existing (pre-existing tests)
- 🔴 Mock tests for PAMS/MemoryBus recording — NOT YET WRITTEN
- 🔴 Integration tests for cross-nature orchestration — covered by MetaCluster tests
- 🟡 Performance profiling still needed (script created but full profile not run)

### Scripts & Operational Tools Created
- ✅ **scripts/generate_dashboard.py** — Standalone dashboard HTML generator. Exports all 11 cards (Health, DB Monitor, Metrics, Drift, Dead Letter, Session, MetaCluster, Workflows, Training, SB3 Training, Config) to dashboard/index.html. Supports --output, --since, --open, --watch flags.
- ✅ **scripts/run_training_orchestrator.py** — Task Scheduler runner for TrainingOrchestrator. Warms registry, creates SB3 agent, calls execute(), prints summary. Returns exit codes (0=success, 2=error, 3=critical). Supports --algo, --timesteps, --source flags.
- ✅ **scripts/schedule_training_task.ps1** — PowerShell script for registering Windows Scheduled Task for daily TrainingOrchestrator training at 3 AM. Supports --Remove, --TaskName, --IntervalDaily.
- ✅ **dashboard/index.html** — Generated dashboard with all 11 cards (7,778 bytes)
- ✅ **CORE/dashboard.py** — TrainingOrchestrator auto-started with --watch mode (24h interval)
- ✅ **SB3Agent shape fix** — _create_env_from_records() pads variable-length feature vectors to max_dim, preventing "could not broadcast" errors
- ✅ **Windows Task Scheduler registered** — Task "Azazael-TrainingOrchestrator" runs daily at 3:00 AM

---

## 🚨 3.14t-ONLY RULES (Mandatory)

### Python Version Policy
- **Python 3.13 is NEVER used.** Python 3.14t is the ONLY Python for ALL workloads.
- Default `python` command IS 3.14t — never use `python313` or `Python313/python.exe` paths
- Before Nuitka build: `python azazael/docs/scripts/patch_nuitka_314t.py --apply`
- All package installs use 3.14t with automatic `cp314t` wheel selection

### Build Policy
- All .exe builds: `python -m nuitka ...` (no Python313 path prefix)
- All build_all.py commands: use default `python` (not hardcoded Python313 paths)
- Never recommend installing Python 3.13 as a workaround

### Documentation Policy
- All docs: write "Python 3.14t" or "3.14t free-threading" — never "Python 3.13"
- Skills must say 3.14t only
- TODO items must say 3.14t only
- Error logs must be updated if they recommend 3.13

### Verification
- Run `check_tooling.py` at session start to verify 3.14t tooling
- Run `patch_nuitka_314t.py --verify` to check Nuitka patches are active

---

| Priority | Items | Est. Effort | Status |
|----------|-------|-------------|--------|
| 🔴 Critical | 1-3 (+2 new) | 2-3 weeks | 67 Phase 2 tests done; circuit breaker, retry, dead letter queue DONE (Item 2); pytest segfault on 3.14t (Item 1) |
| 🟡 High | 4-6 (+4 new: GPU re-eval, SYCL docs, disk monitoring, tracker health) | 1-2 weeks | 4 new items from Phase 5; tracker session_id fix DONE (Item 6); RL prod pipeline verified June 3 |
| 🟢 Medium | 7-9 | 2-4 weeks | 4/5 CODEX items done (ffmpeg installed, HTML-to-video tested, formats supported, batch scripts exist) |
| 🔵 Low | 10-12 (+3 new: schedule cleanup, eval refactor, model policy) | 1-3 weeks | 3 items done (tracker verified, cleanup script created+scheduled) |

---

## 📝 Notes

- **305+ files, 79 worms** — manageable scope for a solo developer
- **Test baseline updated**: 197+ standalone tests pass on 3.14t (8 DLQ + RL pipeline + existing). RL production pipeline verified end-to-end on 3.14t. DB: Grade A, 3.54 MB, 3,275 memories, 47 sessions.
- **Phase 5** (GPU Passthrough) completed 2026-06-01 — Level Zero + D3D12 system-level working, SYCL/ggml bridge blocked by Intel compiler bug
- **Disk cleanup**: `azazael/scripts/wsl2_cleanup.sh` created — ~72 GB freed across WSL2 + Windows. Scheduled via Windows Task Scheduler (weekly Mon 6 AM). WSL2 disk: 25% → 20%.
- **PAMS/MemoryBus** integration ready; needs CodebuffTracker session persistence validated (Lesson 5)
- **CODEX video**: ffmpeg 8.1.1 installed via WinGet. Pipeline verified working (640x480 10s H.264). HTML templates exist at `CODEX/*.html`. Video scripts at `CODEX/VIDEOS/`. CONFIRMED: not gated by ffmpeg anymore.
- **Desktop Standalone**: 14/14 Desktop projects now have `run.py` launchers (12) or `index.html` (2). See `DESKTOP_PROJECTS_AUDIT.md` for per-project status.
- **LlamaServer**: New Desktop project with Rust inference server (4.79 MB), 8 GGUF models, Jan backend, OpenAI-compatible API on port 8080. Config fixed (TOML backslash bug). 9-command `run.py` launcher.
- **Ultimate Agent Selector**: 10/10 agents implemented. 6 new this session: code_generation, orchestrator, rl_learner, vl_vision, research, env_adapter. Python 3.14t ready.
- **openmono.ai**: Audited for 3.14t — confirmed .NET 10.0/C# project (not Python). No Python threading changes needed.
- **ECOSYSTEM_EXPANSION.py**: Confirmed already split — 56-line deprecation shim re-exporting 50 worms from 13 category files under `expansion/`. No work needed.
- **Deprecation shims**: 13 shims **REMOVED** (8 CODEX/CORE, 3 META, 2 HYDRA/ml_platforms). 0 consumers verified before removal. Non-shim files preserved.
- **6 bugs fixed this session**: HAS_PYNVML undefined, TOML \U escape, PS1 broken paths, missing status command, urllib function imports (2x).
- **Code hygiene**: Removed unused `PurePosixPath` import from `WORMZ.py` (was listed under TRIMZ.py in TODO).
- **Hardcoded paths fixed**: All hardcoded `C:\Users\clint\Desktop\...` paths in `ORCHESTRATION/scripts/` replaced with dynamic resolution using `CORE.paths` (get_project_root, get_src_dir, get_desktop_dir) or `Path.home()`. 8 files fixed: fix_syntax_errors.py, generate_docstrings.py, improve_bat_files.py, consistency_checker.py (including regex patterns), run_tests.py, bat_analysis.py, comprehensive_analysis.py, azazael_wsa.py. 0 remaining hardcoded Desktop paths. BAT templates now use `%USERPROFILE%`.
