# PRODUCTION_TODO — Azazael Ecosystem Production Roadmap

> **SUPERSEDED as of Sep 2, 2026 — see `CODEBASE_AUDIT_TODO.md` (primary living production plan, Phase 23+, Session 28 refresh).** Keep in place for reference only; do not add new items here.

> *Generated: May 28, 2026 — Last updated: July 2, 2026 — **AOA Architecture Disclosure Rebuild session***
> *Current state: 300+ syntax-clean files, 129 registered worms, 188+ tests passed (3.14t), 23 categories, 52 Desktop EXEs, 14/14 Desktop projects standalone, PostgreSQL adapter available, DB monitoring live, AOA whitepaper published (14 diagrams, 2 MP4s)*

---

## 🚨 Lessons Learned — July 2, 2026 Session (AOA Architecture Disclosure Rebuild)

Lessons: #38, #39, #40, #41, #42, #43 — see LESSONS_MASTER.md for details.

| # | Lesson | Category |
|---|--------|----------|
| #38 | Mermaid classDef must appear AFTER graph TB/LR — before causes Syntax error | Mermaid |
| #39 | Professional disclosure docs = single scrollable whitepaper, not tabbed UI | Design |
| #40 | Red strikethrough corrections tables are unprofessional — use Verified Specs | Design |
| #41 | Semantic color palettes need global classDef per diagram mapped to function | Design |
| #42 | Heredoc with single-quoted delimiter prevents shell expansion on Windows bash | Tooling |
| #43 | Puppeteer needs 5-8s wait for 14 Mermaid diagrams before scroll capture | Tooling |

---

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

> **3.14t test status (2026-06-01, UPDATED):**
> - `psutil` segfault **FIXED** via `pip install --force-reinstall --no-deps psutil` (selected cp314t wheel) — Error #49 resolved
> - **8 test files pass standalone on 3.14t** (188+ tests): test_agent.py (16), test_memorybus.py (32), test_pool.py (19), test_worm_imports.py (14), test_cluster_worms.py (5), test_clusterworms_unit.py (39), test_config_and_breaker.py (36), test_nature_clusters_unit.py (27)
> - **1 file slow** (test_metacluster_unit.py ~5 min): full MetaCluster orchestration runs 85+ worms across 17 natures — use `--timeout 420`
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

### 9. CODEX Video Pipeline
> Lessons: [#6](LESSONS_MASTER.md) (winget timeout), [#5](LESSONS_MASTER.md) (network drives)
- [x] Install ffmpeg (`winget install ffmpeg` or manual) — **DONE** (ffmpeg 8.1.1 via WinGet)
- [x] Test full `.html` → `.mp4` scrolling video generation — **DONE**
- [ ] Add progress bar to video generation
- [x] Support multiple output formats (mp4, webm, gif) — **DONE**
- [x] Batch video generation for all CODEX HTML files — **DONE**

### 10. AOA Architecture Disclosure *(NEW — July 2, 2026)*
> Lessons: #38, #39, #40, #41, #42, #43
- [x] Color audit: find/fix duplicate classDef (ph, ev) — DONE
- [x] 12-classDef WCAG AA semantic palette — DONE
- [x] 14 Mermaid diagrams, 7-section whitepaper — DONE
- [x] Arm Capability Matrix (8 arms, source-verified) — DONE
- [x] Verified Architecture Specifications (14 specs) — DONE
- [x] 7-anchor Table of Contents — DONE
- [x] Render 1080p HEVC MP4 via Puppeteer (85s, 2,125 frames) — DONE
- [x] 2.5x speed version (34s, 850 frames) — DONE
- [x] Distribute HTML + MP4s to WSL, Kali, G: — DONE
- [x] Create aoa-disclosure-build skill (4.4 KB) — DONE
- [ ] Automated rebuild pipeline (benchmark_data.json -> HTML -> MP4 -> distribute)
- [ ] CI/CD trigger on worm registry changes

---

## 🔵 LOW PRIORITY (Nice to Have)

### 10. Code Hygiene
> Lessons: [#19](LESSONS_MASTER.md) (import hygiene), [#7](LESSONS_MASTER.md) (nohup/cleanup), [#17](LESSONS_MASTER.md) (HAS_* flags)
- [x] Remove `PurePosixPath` import from `WORMZ.py` (unused) — **DONE**
- [ ] Standardize error handling across all worms (some use bare except)
- [ ] Remove `sys` import from `paths.py` (unused) — **DONE**
- [ ] Consolidate duplicate `_LOCAL_TARGETS` / `_DESKTOP_TARGETS` config in TRIMZ.py and ERRORZ.py into `paths.py`
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

## 🚨 3.14t-ONLY RULES (Mandatory)

### Python Version Policy
- **Python 3.13 is NEVER used.** Python 3.14t is the ONLY Python for ALL workloads.
- Default `python` command IS 3.14t — never use `python313` or `Python313/python.exe` paths
- ~~Before Nuitka build: `python azazael/docs/scripts/patch_nuitka_314t.py --apply`~~ — **SUSPENDED**: Nuitka 4.1.2 broken on 3.14.5t (CompiledFrameType.c _PyStackRef)
- All package installs use 3.14t with automatic `cp314t` wheel selection

### Build Policy
- ~~All .exe builds: `python -m nuitka ...` (no Python313 path prefix)~~ — **SUSPENDED**
- All build_all.py commands: use default `python` (not hardcoded Python313 paths)
- Never recommend installing Python 3.13 as a workaround

### Documentation Policy
- All docs: write "Python 3.14t" or "3.14t free-threading" — never "Python 3.13"
- Skills must say 3.14t only
- TODO items must say 3.14t only
- Error logs must be updated if they recommend 3.13

### Verification
- Run `check_tooling.py` at session start to verify 3.14t tooling
- ~~Run `patch_nuitka_314t.py --verify` to check Nuitka patches are active~~ — **SUSPENDED**

---

| Priority | Items | Est. Effort | Status |
|----------|-------|-------------|--------|
| 🔴 Critical | 1-3 (+2 new) | 2-3 weeks | 67 Phase 2 tests done; circuit breaker, retry, dead letter queue DONE (Item 2); pytest segfault on 3.14t (Item 1) |
| 🟡 High | 4-6 (+4 new: GPU re-eval, SYCL docs, disk monitoring, tracker health) | 1-2 weeks | 4 new items from Phase 5; tracker session_id fix DONE (Item 6) |
| 🟢 Medium | 7-9 | 2-4 weeks | 4/5 CODEX items done (ffmpeg installed, HTML-to-video tested, formats supported, batch scripts exist) |
| 🔵 Low | 10-12 (+3 new: schedule cleanup, eval refactor, model policy) | 1-3 weeks | 3 items done (tracker verified, cleanup script created+scheduled) |

---

## 📝 Notes

- **300+ files, 129 worms, 23 categories** — manageable scope. Worm count: 77→129 after live @register_worm scan found 6 unreported categories. for a solo developer
- **Test baseline updated**: 188+ standalone tests pass on 3.14t (8 files). MetaCluster orchestration takes ~5 min (1 file). pytest still unavailable on 3.14t (Error #48).
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
- **AOA Architecture Disclosure**: 7-section whitepaper built July 2, 2026. 14 Mermaid diagrams with 12-color WCAG AA semantic palette. 2 videos (85s + 34s HEVC 1080p). Distributed to WSL Ubuntu, Kali Linux, G:, Windows Desktop. New skill: aoa-disclosure-build.md. Key numbers: 226 worms, 35 cats, 8 arms, 13 compliance components, 49 EXEs, 25 skills, 4 Quartet pillars, 8 canonical docs, 70 routes, 594 paths.

---

## Staleness Note — 2026-09-16

This file is **superseded** (see the banner at the top) and is retained for reference
only. Its remaining figures are historical: it reports 129 registered worms and 23
categories where the 2026-09-14 rebuild measured **226 worms / 35 categories**, and
"pytest still unavailable on 3.14t (Error #48)" no longer holds — pytest runs, though
`tests/test_spine_mesh.py` currently **hangs** (attributed away from the 2026-09-16
tombstone guard; see `AZAZAEL_INSIGHTS.md` section 14).

Living plans, in priority order: `CODEBASE_AUDIT_TODO.md` (primary),
`NEURAL_MESH_FUNCTION_TODO.md`, `NEURAL_MESH_BRAINSTEM_TODO.md`,
`LIVE_MONITOR_RESTRUCTURE_TODO.md`.
