# AZAZAEL — Codebase Audit & Production Wiring TODO

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project;
> production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only
> sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Audit rows
> below describe the state on their date.

> **Created:** May 29, 2026 — Consolidated from Phase 12-14 sessions
> **Updated:** Sep 13, 2026 (Neural Mesh Gap Audit + G1-G12 Fixes) — BCC corpus qualifiers (37 bannered docs + 3 .md/skill files), FINAL_STATUS_REPORT inventory reconciled (TOTAL 64), G: archive gap filled (40 html), filing-source dating probe, mirror check closed. Prior: June 19, 2026 (v11) — Audit fix marathon.
> **Replaces:** TODO_FULL_PRODUCTION_WIRING.md, PHASE_6_TODO.md (incorporated)
> **Status:** Living document — update with each phase
> **Companions:** azazael/memories.md, azazael/ERROR_LOG.md, SESSION_INSIGHTS_*.md

---

## Session Completion — Sep 13, 2026 (Neural Mesh Architecture Gap Audit + All-Fix Pass)

| ID | Item | Status |
|----|------|--------|
| NM-1 | Neural mesh architecture audit — 12 gaps identified (G1-G12) across spine/synapse/immune/dreaming | ✅ **DONE** |
| NM-2 | G1: Unified Q-table — SynapseWeightWorm delegates to spine_registry._Q_WEIGHTS | ✅ **DONE** |
| NM-3 | G2: Adaptive alpha — Welford variance tracking in _reinforce_q | ✅ **DONE** |
| NM-4 | G3: Kademlia XOR-distance routing in SpineGossipWorm | ✅ **DONE** |
| NM-5 | G4: SSMSequenceWorm — input-dependent gating, learned B/C params | ✅ **DONE** |
| NM-6 | G5: AttentionRouterWorm — softmax over natures, Q-weight driven | ✅ **DONE** |
| NM-7 | G6: PlasticityWorm wired into SpineCycleWorm (Hebbian/STDP) | ✅ **DONE** |
| NM-8 | G7: Graduated scar healing (3 consecutive successes threshold) | ✅ **DONE** |
| NM-9 | G8: MorphogenesisWorm auto-registration gate | ✅ **DONE** |
| NM-10 | G9: DreamingModule curriculum sampling (severity-weighted) | ✅ **DONE** |
| NM-11 | G10: Typed data contracts in NATURE_DEFINITIONS | ✅ **DONE** |
| NM-12 | G11: AutoencoderAnomalyWorm (linear autoencoder, online learning) | ✅ **DONE** |
| NM-13 | G12: Temporal discounting in DreamingModule | ✅ **DONE** |
| NM-14 | Gephi export pipeline built (tools/gephi_mesh_pipeline.py) | ✅ **DONE** |
| NM-15 | 220 worms / 35 categories verified (was 108/19 in Sep 3 docs) | ✅ **DONE** |
| NM-16 | 47/47 tests pass, 9/9 files compile clean | ✅ **DONE** |

**Metrics:** 220 worms, 35 categories, 12 G-fixes, 47 tests passing.

---

## Session Completion — Sep 2, 2026 (Session 28 — Graphify Refresh + CODEX Sweep + BCC Re-verify)

| ID | Item | Status |
|----|------|--------|
| S28-1 | Regenerated ALL graphify graphs — azazael (591.7 MB), vermillion_lightfury, aoa_g, aoa_source (14:34), Kali (41,530 nodes, 14:37) via `graphify_refresh_all.sh` | ✅ **DONE** |
| S28-2 | CODEX generator sweep — 46 HTML/JS producers scanned (AST `\n` scan + join byte-scan + py_compile + emit-and-CDP-verify); **1 real defect fixed**: `generate_dashboard_video.py:966` unterminated `\"` → `\""`; all other producers emit clean (incl. unified_generator 11 styles, 3,622x-`\n` cain template); fixed generator propagated 3/3 hash-identical | ✅ **DONE** |
| S28-3 | BCC 53-gap sweep — 62 gaps/53 open baseline extracted; live Sep-2026 re-verification annex added to INVESTIGATION_GAPS.html (FY2025 990 public May 8, 2026: revenue $12,494,569 / deficit −$796,924 / contributions $204,333; OIG SRS-A-26-025 still active est. FY2028; federal awards $1,965,700 UEI VC1XNFDJTV33; board now disclosed on /about-us; G-56 archive.org obtainable) | ✅ **DONE** |
| S28-4 | AOA Kali toolchain arm — 9 arms/71 caps; real `kali_arm.py` (40 caps), WSL bridge, dry-run-safe; both test suites PASS; real-payload nmap verification | ✅ **DONE** |
| S28-5 | Skills catalog reconciled — **1,253 rows / 165 core** (33 session skills #1221–#1253), header=summary=rows bucket-verified; 7 new skills registered; cross-ref web 6/6 mirrors | ✅ **DONE** |
| S28-6 | G: archive recovery + cleanups — MBR repaired, 850,507 files inventoried, 4.86→18.04→35.30 GB; node_modules cluster-slack cleanup; historical archive catalog + README; Phase 9 generation diffs; AOA wired in-repo | ✅ **DONE** |
| S28-7 | FINAL_STATUS_REPORT.html — 4 missing Session 28 rows added, stale 1,240/152 audit row corrected → 1,253/165 | ✅ **DONE** |
| S28-8 | All artifacts synced to G: mirrors (hash-verified) + session milestone + NEXT_SESSION_PLAN.md handoff written | ✅ **DONE** |

**Nothing sent. BCC excluded from all recipient lists.**

---

## Session Completion — Sep 3, 2026 (Session 28 cont. — BCC corpus qualifiers + archive fill + dating probe)

| ID | Item | Status |
|----|------|--------|
| S28-9 | FINAL_STATUS_REPORT.html Document Inventory reconciled against live corpus — **TOTAL 63 → 64** (62 html + README + COMPLAINT_AGENCY_LETTER.txt); G_ARCHIVE_CATALOG reclassified Session Artifacts → Audit & Reference (5→6); category sum = live corpus bucket-verified; NEXT_SESSION_PLAN.md stale-63 line annotated | ✅ **DONE** |
| S28-10 | As-of board-role qualifiers extended — 37 bannered docs (real `id="board-role-asof-sep2026"` added, CDP banner-visibility sweep **37/37 visible**), 3 .md/bcc-* skill files qualified, INVESTIGATION_GAPS.html Sep-3 annex | ✅ **DONE** |
| S28-11 | G: BCC_Investigation archive gap filled — **25 local-only docs copied hash-identical (40 html in archive)**; 22 non-bannered docs remain local-only (flagged) | ✅ **DONE** |
| S28-12 | Filing-source dating probe — DDAP/BCO/IRS-e-file all checked; **reorg bracket stands ~May 8 → Sep 2, 2026**; PA BCO cert #3306 public (FY2025 renewal filed ~May 15, 2026); DOS corporate record Cloudflare-walled (gap #26/#27 action stands) | ✅ **DONE** |
| S28-13 | Mirror check closed-no-action — FINAL_STATUS_REPORT/SESSION_MILESTONE are root-level corpus docs (not azazael-repo files); canonical mirror G:/source-of-truth/azazael hash-current; azazael-dev/Kali never carried them | ✅ **DONE** |

**Nothing sent. BCC excluded from all recipient lists.**

---

## Session Completion — June 19, 2026 (Audit Fix Marathon)

| ID | Item | Status |
|----|------|--------|
| AR-1 | Fix shell=True HIGH RISK — 3 remaining found & fixed (environ_updater, lsp_diagnosis, gate_bash) | ✅ **DONE** |
| AR-5 | Fix azazael-core pyproject.toml Python >=3.13→3.14 | ✅ **DONE** |
| — | Create unified requirements-3.14t.txt lockfile (ADDITIVE) | ✅ **DONE** |
| AR-22 | Create sync-ubuntu.exclude to trim Ubuntu bloat | ✅ **DONE** |
| — | Catalog tools/36 .py files with README.md (ADDITIVE) | ✅ **DONE** |
| — | All changes synced to Kali (canonical) | ✅ **DONE** |

---

## State Snapshot (Sep 2, 2026 — Session 28 Refresh)

| Metric | Value | Change |
|--------|-------|--------|
| Python version | **3.14.7t** | ✅ Unchanged (3.14t family) |
| Skills catalog | **1,253 rows / 165 core** | ⬆️ Reconciled (was 1,220 base; 33 session skills #1221–#1253) |
| AOA arms / caps | **9 arms / 71 caps** | ⬆️ Kali toolchain arm added (40 caps, real payloads verified) |
| HTML generator defects | **0 remaining** | 🟢 CODEX sweep: 1 found+fixed (dashboard capture script), all 46 producers emit-verified |
| Graphify graphs | **5/5 regenerated Sep 2** (azazael 591.7 MB, kali 41,530 nodes) | ✅ All current |
| BCC investigation | **62 gaps / 53 open / 9 resolved** | 🟢 Live re-verify annex added; FY2025 990 public (net loss −$796,924) |
| G: drive | **35.30 GB free post-cleanup** | ⬆️ From 4.86 GB (MBR repair + node_modules cluster-slack recovery) |
| Session handoff | NEXT_SESSION_PLAN.md (8 sections, thread scoring) | ✅ Written + mirrored |

## State Snapshot — Live Reconcile (Sep 13, 2026 — neural mesh audit verified)

| Metric | Live value (2026-09-13) | vs prior snapshot |
|--------|-------|--------|
| Worms in registry | **220 across 35 categories** (live `discover_worms`; expansion packs discovered since Sep 3; all G1-G12 new worms registered) | ⬆️ Sep 3 said 108/19 — **doubled via expansion packs**; Jun 5 said 91/17 |
| Python source files (src/) | **526 .py files** (excl. `__pycache__`; 25 Python-bearing top dirs: CORE 185, ORCHESTRATION 83, CODEX 74, SCRIPTS 26, AOA 24, UTILITIES 23, META 16…) | ⬆️ June 5 said 322 .py / 18 subdirs |
| Standalone EXEs | **52 EXEs + 52 BATs @ `G:\AZAZAEL_Standalone`** (51 `_314t.exe` + `AZAZAEL_314t_Launcher.exe`; 1.97 GB, 9,024 files) | ✅ Count matches June 5 (52/52) but **location moved Desktop→G:** — Desktop/AZAZAEL_Standalone is docs-only now |
| Skills catalog rows | **1,253 numbered rows** | ✅ Matches Sep 2 snapshot |
| FINAL_STATUS_REPORT inventory | **TOTAL 64 docs** = 62 root html (5 documented exclusions) + README.md + COMPLAINT_AGENCY_LETTER.txt; 8 categories bucket-verified | ⬆️ Corrected from 63 (G_ARCHIVE_CATALOG.html was miscounted as Session Artifact → reclassified Audit & Reference) |
| BCC corpus as-of qualifiers | **37/37 bannered docs** carry `id="board-role-asof-sep2026"`, CDP-verified visible; 3 .md/skill files qualified (bcc-investigation, bcc-owl-framework, README.md) | 🟢 Sweep complete — banner real-id added (was comment-only marker) |
| G: BCC_Investigation archive | **42 files / 40 html** (25 docs added hash-identical) | ⬆️ Was 15 html — all 37 bannered docs now mirrored; **22 non-bannered html remain local-only** (open item) |
| BCC reorg dating bracket | **~May 8 → Sep 2, 2026** (990 signing floor; new slate live) | 🟢 Filing probe: PA BCO cert #3306 APPROVED, FYE 06/30/2025, expires 05/15/2027 → FY2025 renewal filed ~May 15, 2026 (inside window, roster not public); DOS record Cloudflare-walled |

---

## State Snapshot (June 5, 2026 — Comprehensive Project Audit)

| Metric | Value | Change |
|--------|-------|--------|
| Python version | **3.14.6/3.14.7 + 3.14t** (Win default 3.14.7, WSL Ubuntu 3.14.7 FT, Kali 3.14.6 FT) | ⚠️ Was pinned 3.14.5t-only; prescriptive 3.14.5 pins elsewhere unverified |
| Python source files (src/) | **322 .py files** across **18 subdirectories** | ⬆️ Was 305 (17 new) — ⚠️ **SUPERSEDED Sep 3: live = 526 .py** (see Live Reconcile snapshot) |
| Worms in registry | **226** across **35 categories** | ⬆️ Was 91/17 — ⚠️ **SUPERSEDED Sep 14: live = 226 / 35, 70 routes / 594 paths** (clean rebuild ×2) |
| Desktop standalone EXEs | **52** (operational) | ✅ 52 EXEs + 52 BATs — ⚠️ **SUPERSEDED Sep 3: count holds (52/52) but suite now lives at `G:\AZAZAEL_Standalone`** (Desktop folder docs-only; see Live Reconcile snapshot) |
| Desktop projects inventoried | **17** (was 14) | ⚠️ 3 undocumented: AZAZAEL_Vault, AZAZAEL_ARCHIVE, scripts_archive |
| G: AZAZAEL_ROOT | **6,567 files, 14.7 GB** | Most complete G: copy |
| G: source-of-truth | **5,296+ files** | ✅ Synced June 7 (was 5,075 file gap) |
| G: standalone/ backup | **NOT FOUND** | 🔴 Missing from disk |
| CAIN_ARCHIVE (7.5 GB) | **LOST** (Error #58) | 🔴 No recovery |
| Error log | **60 errors** (#56-60 added) | 🟢 Updated June 5 |
| DirectMemory sessions | **130 sessions, 1,774 memories, 0 open** | ✅ Clean (was 98 orphaned) |
| azazael project total | **9,459 files, 46.7 GB** | ⚠️ May include build artifacts |
| Destructive behavior doc | **CREATED** `LESSONS_DESTRUCTIVE_BEHAVIOR.md` (4 incidents, 6 rules) | 🔴 CRITICAL — must be read at startup |
| MEMORIES.md anti-patterns | **11 total** (added #11: never delete/move/re-create user work) | ✅ Updated June 5 |
| CAIN scroll speed standard | **5.0 WPS** (from MetaWormSpawner.py), 98s for session report | ✅ Determined June 5 |
| Stale path references | **90 fixed** in CODEX/DOCUMENTATION/API/*.md | ✅ Desktop/azazael → ~/azazael |
| Desktop scripts archive | **59 files** in scripts_archive/ (was 52) | ⚠️ 7 files added since documented |
| Skills on disk (azazael/skills/) | **41 .md files** (was 39) | ⬆️ 2 new type-checking skills (June 14 Session 2) |
| Skills pre-loaded in .agents/skills/ | **74 skills** (2 new type-checking registered June 14 Session 2) | ✅ All loadable via skill() |
| CAIN deliverables (Desktop) | **5 items, 417.9 MB total** | ✅ Comprehensive analysis completed |
| CAIN_ARCHIVE (7.5 GB) | **LOST** (Error #58) | 🔴 No recovery path available |
| G: source-of-truth/azazael | **5,296+ files** | ✅ Synced June 7 (robocopy, automated) |
| G: AZAZAEL/AZAZAEL_ROOT | **6,567 files, 14.7 GB** | ⚠️ Most complete G: copy |
| G: standalone/ backup | **NOT FOUND** | 🔴 PROJECT_MAP.md says it exists but not on disk |
| azazael project total | **9,459 files, 46.7 GB** | ⚠️ Verify: may include build artifacts |
| Desktop projects inventoried | **17** (was 14) | ⚠️ 3 new finds: AZAZAEL_Vault, AZAZAEL_ARCHIVE, scripts_archive |
| `shell=True` HIGH RISK usages | **5 fixed** (1 intentional — bash runner) | ✅ 5/6 refactored to safe list form |
| Legacy skill files (no frontmatter) | **3 fixed** (azazael_314t_master, _optimum, _insights) | ✅ YAML frontmatter added |
| META/ deprecation shims | **13 .py files + __pycache__ deleted** | ✅ output/ and reports/ preserved |
| Stale TODO docs | **3 archived** (PRODUCTION_TODO, REWRITE_TODO, PHASE_6_TODO) | ✅ Moved to docs/archive/ |
| CI pipeline | **Fixed** (removed stale `cd azazael` paths) | ✅ test-3.14t.yml updated |
| pytest-cov config | **Added** to pyproject.toml | ✅ Coverage config with src/ source path |
| Architecture review lessons | **4 new (##41-44)** | Methodology, versioning, skills audit, consolidation |
| Architecture review skills | **2 new** | `azazael-architecture-review`, `azazael-todo-management` |
| Lesson planning improvements | **TOC + template** | By-domain TOC, tag index, creation template |

---

## PHASE 23+ — SEQUENTIAL PRODUCTION PLAN

### Execution Order — DO NOT SKIP STEPS

Each step depends on the previous one completing. Implement in sequence.

---

### Step 1: ✅ Post-Session Cleanup — DONE (June 2)
- [x] pip cache purge — 749 MB freed
- [x] Windows Temp cleanup — ~2.5 GB freed
- [x] G: archive filled — docs, scripts, .agent skills, core package, config
- [x] G: redundant standalone backup deleted — ~500 MB freed
- [x] G: obsolete 3.13 .exe files deleted — ~400 MB freed
- [x] post_install.sh fixed for Ubuntu 26.04
- [x] WSL Python 3.14.5t + ML packages installed and verified
- [x] Error resolution skill created (azazael-error-resolution.md)
- [x] LESSONS_MASTER.md updated: 37→42 lessons, sections 7-8 added
- [x] ERROR_LOG.md updated: errors #51-#53 added
- [x] SYSTEM_INSTRUCTIONS.md updated: Phase 22+, error count 53+
- [x] SESSION_STARTUP.md rewritten: Phase 22+ state snapshot

### Step 2: ✅ G:\source-of-truth\azazael Vault Update — DONE
- [x] Vault verified — contains CODEBASE_AUDIT_TODO.md, src/ with CORE, etc.
- [x] File count: vault has azazael/src/ contents (slow G: drive — verify full sync)
- [x] vault is synced with latest source from C:

### Step 3: Test Suite — Cluster Modules (In Progress)
> **Lessons:** #14 (store injection), #15 (test infra pays), #16 (verify queries first)
> **Completed so far:** 85 new CLUSTERWORMS unit tests | Existing NATURE_CLUSTERS + METACLUSTER tests cover most gaps
> **Remaining:** ~6-8 hours
- [x] Unit tests for CLUSTERWORMS.py dynamic resolution — **85 tests added** (all passing)
  - ✓ WormConfig/ClusterResult dataclasses
  - ✓ CLUSTER_REGISTRY validation (8 types, descriptions, worms)
  - ✓ _WORM_MODULE_MAP + _LEGACY_DISPATCH structure
  - ✓ _STANDARD_METHODS priority order
  - ✓ _resolve_worm_dynamic (3 strategies: registry, legacy dispatch, module map)
  - ✓ _execute_worm_class method resolution
  - ✓ WormExecutor (known/unknown worms, state updates)
  - ✓ ClusterState (results, messaging, broadcast, clear)
  - ✓ ClusterWORMZ construction (all 8 types, config methods)
  - ✓ build_from_nature, build_from_registry, build_full_ecosystem
  - ✓ Sequential and parallel execution
  - ✓ Retry logic
  - ✓ Aggregation and metrics
  - ✓ Mermaid generation (3 graph types)
  - ✓ Full lifecycle integration tests
- [x] Unit tests for NATURE_CLUSTERS.py category discovery — **already comprehensive** (30+ tests in test_nature_clusters_unit.py)
- [x] Unit tests for METACLUSTER.py routing engine — **already comprehensive** (30+ tests in test_metacluster_unit.py + test_metacluster_orchestration.py)
- [ ] Integration tests for parallel execution (FreeThreadPool, work-stealing)
- [ ] Integration tests for cross-nature orchestration
- [ ] Mock tests for PAMS/MemoryBus event recording
- [ ] Regression tests for all 226 worms (import + register + basic smoke)
- [ ] Test coverage reporting (pytest-cov, target: 60%+)

### Step 4: Error Recovery & Resilience
> **Dependency:** Step 3 (test infrastructure in place)
> **Lessons:** #10 (thread safety), #20 (lazy init discipline)
> **Est. Hours:** 10-15
- [ ] Timeout handling: daemon threads must be joined or killed
- [ ] Partial failure handling: should cluster continue or abort?
- [ ] Circuit breaker: stop if error rate exceeds threshold (90%+ in 10s)
- [ ] Retry with exponential backoff (replacing fixed 0.1s sleep)
- [ ] Dead letter queue for failed executions (circuit_breaker.py exists but untested)

### Step 5: Centralized Configuration
> **Dependency:** Step 4 (error handling patterns established)
> **Lessons:** #1 (TOML forward slashes on Windows)
> **Est. Hours:** 5-8
- [ ] Centralized config file (YAML/TOML) — azazael.yaml at project root
- [ ] Environment variable validation in paths.py (G_DRIVE, DESKTOP, etc.)
- [ ] Per-nature config overrides (security vs network timeout policies)

### Step 6: Import Hygiene + Deprecation Shim Removal
> **Dependency:** Step 5 (config patterns established)
> **Lessons:** #19 (import hygiene), #24 (deprecation shims > deletion)
> **Est. Hours:** 5-8
- [ ] Run autoflake on all 1,622 .py files to remove unused imports
- [ ] Verify 0 remaining imports to META/, CODEX/CORE/, HYDRA/ml_platforms shims
- [ ] Delete all 14 deprecation shim files
- [ ] Clean up MEMORIES.md shim table
- [ ] Standardize error handling — remove bare `except:` clauses
- [ ] Add `__all__` to all module exports (77 worm files + 20 cluster files)

### Step 7: Performance Optimization
> **Dependency:** Step 6 (clean codebase to profile)
> **Lessons:** #20 (lazy imports), #21 (fast-path), #22 (module splitting), #30 (HTTP timeouts), #31 (profile first)
> **Est. Hours:** 8-12
- [ ] Profile parallel execution bottleneck (cProfile on 100-worm cluster run)
- [ ] Consider ThreadPoolExecutor instead of raw threading.Thread
- [ ] Cache worm registry lookups (currently O(n) scan per query)
- [ ] Lazy-load worm modules (all 77 import at startup)
- [ ] Cache Mermaid graph output (regenerated every call)
- [ ] Batch PAMS events (individual writes currently)

### Step 8: Documentation + Observability
> **Dependency:** Step 7 (optimized code documented)
> **Lessons:** #14 (store injection), #18 (API parity), #32 (browser-use needs server)
> **Est. Hours:** 10-15
- [ ] Module-level docstrings for all new cluster files
- [ ] Architecture diagram in root README (can auto-generate from Mermaid)
- [ ] API reference for ClusterWORMZ, MetaCluster
- [ ] Usage examples with CLI output
- [ ] Troubleshooting guide (common errors + fixes from ERROR_LOG.md)
- [ ] Structured logging (JSON) for cluster operations
- [ ] Metrics: execution count, duration, success rate per cluster type
- [ ] Health check endpoint / CLI command
- [ ] Alert on worm registration drift (count changes)

### Step 9: Registry + Workflow Enhancements
> **Dependency:** Step 8 (observability in place to monitor)
> **Est. Hours:** 10-15
- [ ] Validate registry at startup (detect missing deps, circular imports)
- [ ] Registry versioning (detect when worms change)
- [ ] Worm dependency graph visualization
- [ ] Worm health scoring (import success, config validity, test coverage)
- [ ] Standard workflow templates (security scan → vulnerability report → auto-fix)
- [ ] Workflow DSL for defining multi-step orchestration
- [ ] Conditional routing (if error_rate > X, escalate to MetaCluster)
- [ ] Workflow history and replay (PAMS audit trail)

### Step 10: CODEX Video Pipeline, Template Viewer & CAIN Framework
> **Dependency:** Standalone — can run parallel with Step 7-9
> **Lessons:** #6 (winget timeout), #5 (network drives), #59-62 (CODEX restoration), #63 (CAIN shared data pattern)
> **Est. Hours:** 6-10
- [x] Restore 8 CODEX CORE scripts from G: drive archive
- [x] Restore 3 META scripts (METAWORMS_POPUP, OPTIMIZ, UVZ) from G: drive
- [x] Fix circular import in all 11 deprecation shim files
- [x] Sync fixed files back to G: drive as source of truth
- [x] CAIN template generator verified — generates output_cain.html successfully
- [x] Created unified template_viewer.html — switch between all 11 styles
- [x] Created generate_all.bat — batch regenerate all styles
- [x] Install ffmpeg on build machine
- [ ] Progress bar for video generation (tqdm)
- [x] Multiple output formats (MP4, WebM, GIF)
- [x] Batch generation from template directory
- [x] CAIN_DATA.py — shared data module (single source of truth for framework constants)
- [x] CAIN_WORM.py — registered @register_worm class (CainWorm, category=analysis, priority=6)
- [x] CAIN_ANALYZER.py — standalone CLI module in CODEX/CORE/ (text/HTML/JSON output)
- [x] build_all.py — CAIN_Analyzer added to Tier 10
- [x] CAIN_Analyzer_314t.bat — batch launcher on Desktop
- [x] template_viewer.html — CAIN panel with framework overview
- [x] CAIN footer added to key CODEX HTML reports (ANALYSIS_REPORT, ANALYSIS_REPORT_V2, ANALYSIS_REPORT_DIVERSE)
- [x] G: drive sync — CAIN files + updated docs synced to archive
- [x] LESSONS_MASTER.md — lesson #63 (shared data module pattern)

### Step 11: Deployment Pipeline
> **Dependency:** Steps 3-9 complete (production-ready code)
> **Lessons:** #7 (nohup not a daemon — use Task Scheduler), #6 (winget timeout)
> **Est. Hours:** 8-12
- [ ] Single-entry `azazael` CLI (merge azazael-core into main CLI)
- [ ] Docker container for reproducible builds
- [ ] Scheduled cluster runs (cron / Windows Task Scheduler)
- [ ] Git hook integration (pre-commit worm check)
- [ ] Pre-build validation script: check Python 3.14t, run patch script, verify source, check tkinter/CORE.* imports
- [ ] Build output verification in build_all.py: run `./EXE --help` after build

### Step 12: UI/UX + Code Hygiene
> **Dependency:** Step 11 (deployment infrastructure in place)
> **Est. hours:** 5-10
- [ ] Real-time Mermaid rendering in browser
- [ ] CLI `azazael cluster status --live`
- [ ] Web dashboard for remote inferencing
- [ ] Multi-model comparison mode (Eve Unleashed)
- [ ] PAMS server startup and health check automation

---

## 📊 Effort Estimates

| Step | Phase | Description | Est. Hours | Dependencies |
|------|-------|-------------|------------|-------------|
| 1 | Phase 22+ | Post-session cleanup | ✅ DONE | — |
| 2 | Phase 23 | G: vault update | ✅ DONE | Step 1 |
| 3 | Phase 23 | Test suite — cluster modules | 15-20 (progress: 85 CLUSTERWORMS unit tests done) | Step 2 (optional) |
| 4 | Phase 23 | Error recovery & resilience | 10-15 | Step 3 |
| 5 | Phase 24 | Centralized configuration | 5-8 | Step 4 |
| 6 | Phase 24 | Import hygiene + shim removal | 5-8 | Step 5 |
| 7 | Phase 24 | Performance optimization | 8-12 | Step 6 |
| 8 | Phase 25 | Documentation + observability | 10-15 | Step 7 |
| 9 | Phase 25 | Registry + workflow enhancements | 10-15 | Step 8 |
| 10 | Phase 25 | CODEX video pipeline | 5-8 | Standalone |
| 11 | Phase 26 | Deployment pipeline | 8-12 | Steps 3-9 |
| 12 | Phase 26 | UI/UX + code hygiene | 5-10 | Step 11 |
| | **TOTAL** | | **82-124** | |

---

## 🚨 3.14t-ONLY PRE-BUILD CHECKLIST

### Prerequisites Before Any Build
- [ ] ~~**Run**: `python azazael/docs/scripts/patch_nuitka_314t.py --apply` (patches Nuitka 4.1.2 for 3.14t)~~ — **SUSPENDED**: Nuitka broken on 3.14.5t (CompiledFrameType.c _PyStackRef error)
- [ ] **Test psutil**: `python -c "import psutil; print(psutil.cpu_count())"` (may need `--force-reinstall`)
- [ ] **Confirm Python**: `python -c "import sys; print(sys.version); print('Free-threaded:', not sys._is_gil_enabled())"`
- [ ] **Python 3.13 is NOT used.** Never reference `Python313`, `python313`, or `Python 3.13`.
- [ ] **All build commands use `python`** (no full path to Python313/python.exe)

### Nuitka Build Status
> **❌ BROKEN on Python 3.14.5t as of June 12, 2026.** Nuitka 4.1.2 C backend fails with `CompiledFrameType.c(866): error C2440: cannot convert from 'int' to '_PyStackRef'`. The existing patch_nuitka_314t.py does not cover this file. Nuitka .exe builds are suspended until upstream Nuitka adds proper 3.14t support or a CompiledFrameType.c patch is developed.

### Package Installation on 3.14t
- `pip install` picks `cp314t` wheels automatically
- For broken packages: `pip install --force-reinstall --no-deps <package>` — **this fixes most issues**
- **pydantic-core**: If segfaults on import, run `pip install --force-reinstall --no-deps pydantic-core` then `pip install --upgrade pydantic` (pip will resolve compatible version pair)
- **uuid-utils**: If no cp314t wheel found, `pip install --upgrade uuid-utils` (0.16.0+ has proper cp314t wheel)
- **psutil 7.2.2** has working cp314t wheel — if segfaults, reinstall
- **psycopg2-binary** cp314t wheel is broken (missing DLLs) — use pg8000 instead
- **Never patch site-packages** — fallback monkey-patches in __init__.py are forbidden. Fix the actual wheel installation.

---

## 📁 Related Files

- [`azazael/LESSONS_MASTER.md`](LESSONS_MASTER.md) — All 88 lessons learned (2026-09-14 count; was cited as 57) (canonical reference)
- `azazael/LESSONS_DESTRUCTIVE_BEHAVIOR.md` — ⚠️ CRITICAL: 4 incidents of destroying user work, 6 prevention rules
- `azazael/LESSONS_DEV_TOOLS.md` — Effective dev commands reference (13 sections)
- `azazael/skills/azazael-error-resolution.md` — **NEW** Sequential error resolution decision tree
- `azazael/skills/azazael-production.md` — Detailed gap analysis
- `azazael/skills/azazael-exe-build.md` — Nuitka build procedures (**SUSPENDED** — broken on 3.14.5t)
- `azazael/skills/azazael-standalone-audit.md` — Periodic EXE audit procedures
- `azazael/MEMORIES.md` — Persistent cross-session knowledge
- `azazael/ERROR_LOG.md` — All 140 recorded errors, max #189 (2026-09-14; was cited as 54+)
- `azazael/TODO_FULL_PRODUCTION_WIRING.md` — (Legacy) Original 15-area roadmap (now superseded)
- `azazael/PHASE_6_TODO.md` — (Legacy) Phase-specific tasks (now incorporated)
- `azazael/PRODUCTION_TODO.md` — (Legacy) Original production gaps (now superseded)
- `azazael/REWRITE_TODO.md` — (Legacy) Original rewrite plan (now superseded)
- `Desktop/AZAZAEL_Standalone/build_all.py` — EXE build orchestrator
- `packages/azazael-core/run_tests.py` — Integration test suite
- `.github/workflows/build.yml` — CI workflow

---

## 🏗️ Architecture Review — All Projects (June 4, 2026)

### 1. AZAZAEL CORE — `C:\Users\clint\azazael\`

**Type:** Primary monorepo | **Files:** 305+ .py in src/ + 50+ support files
**Architecture Quality Rating:** **6.8/10** (from AZAZAEL_ARCHITECTURE_ANALYSIS.md)

> **Note on scorecard:** Section 7 below rates the overall ecosystem at **6.2/10** — this is because it **adds 4 new dimensions** (shell injection safety, package management, desktop integration, test coverage) that were not included in the original 8-dimension AZAZAEL_ARCHITECTURE_ANALYSIS.md rating. The underlying CORE quality is consistent at ~6.8.

| Layer | Files | Cohesion | Coupling | Health |
|-------|-------|----------|----------|--------|
| **CORE/** infra | 20+ | 0.65 | 🔴 9.8 (paths.py: 139+ deps) | 🟡 Mixed: paths, memory, agents, logging |
| **CORE/WORMS/** | 57+ (29 + 28 expansion) | 0.85 | 🟢 3.2 | 🟢 Well-grouped by nature |
| **CODEX/** | 70+ | 0.90 | 🟢 2.1 | 🟢 Highly cohesive video pipeline |
| **ORCHESTRATION/** | 70+ | 0.60 | 🟢 2.8 | 🟡 Mixed: deployment, ML, analysis |
| **HYDRA/** | 11 | 0.70 | 🟢 2.5 | 🟡 ML pipeline, partly integrated |
| **META/** | 13 | 0.30 | 🟢 1.5 | 🔴 Deprecation shims (phasing out) |
| **UTILITIES/** | 23 | 0.55 | 🟡 3.5 | 🟡 Mixed tools (KLINK, PERSEPHONE, TARBABY) |
| **Root *.py files** | 30+ | 0.40 | 🔴 5.0 | 🔴 Standalone entry points, hard to maintain |
| **AZAZAEL_TOOLKIT/** | 8 | 0.70 | 🟢 2.0 | 🟢 Thin wrappers, consistent pattern |
| **TOOLS/** | 5 | 0.50 | 🟢 1.8 | 🟡 Miscellaneous tools |
| **SCRIPTS/** | ~20 | 0.60 | 🟢 1.5 | 🟢 Utility scripts |
| **CLI/** | 2 | 0.80 | 🟢 1.2 | 🟢 Thin CLI layer |

**Key issues identified:**
1. **CORE/paths.py bottleneck** — 139+ inbound deps, single point of failure for refactoring
2. **Root *.py files** — 30+ standalone entry points with high variability in quality
3. **META/** — 13 deprecation shim files ✅ DELETED (June 4, 2026)
4. **~1,490 remaining mypy errors** across 142 files
5. **~15% test coverage** — critical gap
6. **5 HIGH-RISK shell=True** usages ✅ FIXED (1 remaining is intentional bash runner)

**Improvement opportunities:**
- Split paths.py into domain-specific modules (P0)
- Run autoflake full pass on all src/ (P1)
- Fix remaining ~1,490 mypy errors (P1)

---

### 2. DESKTOP STANDALONE SUITE — `Desktop\AZAZAEL_Standalone\`

**Type:** Compiled executables | **Files:** 52 EXEs + 52 BATs
**Architecture Quality Rating:** **7.5/10**

> **Note:** Verified June 4, 2026 — 52 EXEs and 52 BATs. The previously reported 52:51 gap has been resolved. Minor name mismatch: `AZAZAEL_314t_Launcher.exe` has no matching BAT, `CAIN_Analyzer_314t.bat` has no matching EXE — but total counts are now equal.

| Metric | Value |
|--------|-------|
| EXE count | 52 (`*_314t.exe`) |
| BAT count | 52 (`*_314t.bat`) |
| Build system | `build_all.py` — 52 modules tracked in Tiers 1-10 |
| Build Python | 3.14t (Nuitka **SUSPENDED** — broken on 3.14.5t) |
| NEEDS_TKINTER | 14 modules |
| NEEDS_PYTHONPATH | 2 modules (CONCURRENCY, SMARTDISK) |
| Deep-tested EXEs | 7 (Phase 22) — all functional |

**Key issues:**
- **SUSPENDED**: Nuitka .exe builds blocked by CompiledFrameType.c _PyStackRef error on 3.14.5t
- CLUSTERWORMS EXE: "Worm registry not available" — Nuitka can't resolve CORE.* imports in onefile mode
- CONCURRENCY/SMARTDISK need PYTHONPATH during build
- CODEX_Studio --help times out in onefile mode (Tkinter startup delay)

**Improvement opportunities (when Nuitka is fixed upstream):**
- Add build output smoke tests (run `./EXE --help` after build)
- Investigate CORE.* import resolution for CLUSTERWORMS EXE

---

### 3. DESKTOP PROJECTS (17 Desktop Items — Fresh Audit June 5, 2026)

**Type:** Standalone applications | **Status:** 14/14 original projects have run.py launchers

| # | Project | Files | Size | run.py | Status | Notes |
|---|---------|-------|------|--------|--------|-------|
| 1 | **AZAZAEL_Standalone** | 10,062 | 1,962 MB | ✅ (EXEs) | 🟢 Active | 52 EXEs + 73 BATs at G:/AZAZAEL_Standalone (2026-09-14); Desktop copy is docs/build-dirs only; Nuitka builds suspended (3.14t incompatibility) |
| 2 | **AZAZAEL_Vault** | 93 | 95 MB | ❌ | 🟡 Unknown | ⚠️ NOT in any prior audit doc — new find |
| 3 | **AZAZAEL_ARCHIVE** | 11 | 19 KB | ❌ | 🟡 Archive | ⚠️ NOT in any prior audit doc — new find |
| 4 | **Azazael_UNIFIED** | 2 | 7 KB | ✅ | 🟢 Active | MUST remain on Desktop (Anti-Pattern #10) |
| 5 | **CODEX** | 145 | 485 KB | ✅ | 🟢 Active | Video generation suite |
| 6 | **CODEX_Studio_Output** | 4 | 4.5 MB | ❌ (index.html) | 🟡 Archive | Output artifacts |
| 7 | **EveUnleashed_Selector** | 167 | 21.3 MB | ✅ | 🟢 Active | VL inference GUI; has README |
| 8 | **LlamaServer** | 8 | 4.6 MB | ✅ | 🟢 Active | Rust LLM server |
| 9 | **METAWORMS** | 2 | 10 KB | ✅ | 🟢 Active | MUST remain on Desktop (Anti-Pattern #10) |
| 10 | **PAMS** | 13 | 283 KB | ✅ | 🟢 Active | Memory system |
| 11 | **PerformanceMonitor** | 1,298 | 587 MB | ✅ | 🟡 Active | Multi-lang; large due to Go/Rust build artifacts |
| 12 | **SysTools_JSON_Converter** | 5 | 41 KB | ✅ | 🟢 Active | JSON utility |
| 13 | **Ultimate_Agent_Selector** | 28 | 196 KB | ✅ | 🟢 Active | Agent framework |
| 14 | **WSL Models** | 11 | 11 KB | ✅ | 🟢 Active | WSL model storage; has README |
| 15 | **WSL_CrossExplorer** | 7 | 64 KB | ✅ | 🟢 Active | WSL file explorer |
| 16 | **agent_system** | 14 | 33 KB | ✅ | 🟢 Active | Agent system |
| 17 | **scripts_archive** | 59 | 359 KB | ❌ | 🟡 Archive | Was 52 files — 7 more added |

**Key issues:**
- All 14 originally documented projects have run.py launchers ✅
- 3 undocumented items found: AZAZAEL_Vault, AZAZAEL_ARCHIVE, scripts_archive (⚠️ need documentation)
- EveUnleashed_Selector and PerformanceMonitor have multi-language stacks (Go, Rust, Python) — adds complexity
- ❌ Do NOT archive or delete any Desktop projects (see Anti-Pattern #10, #11)

**Improvement opportunities:**
- Document AZAZAEL_Vault and AZAZAEL_ARCHIVE in PROJECT_MAP.md
- Evaluate integration of EveUnleashed_Selector with azazael-core AgentPool
- Evaluate LlamaServer as inference backend for CORE agents

---

### 4. G: DRIVE ARCHIVE — Fresh Audit (June 5, 2026)

**Type:** Backup/archive | **Volume:** 476.7 GB exFAT (363 GB free)

| Directory | Files | Size | Health | Notes |
|-----------|-------|------|--------|-------|
| `G:\source-of-truth\azazael\` | 4,934 | 11.8 GB | 🟡 **LAG** | 1,633 files behind AZAZAEL_ROOT |
| `G:\AZAZAEL\AZAZAEL_ROOT` | 6,567 | 14.7 GB | 🟢 Most complete | Includes skills/, standalone/ contents |
| `G:\AZAZAEL\standalone\` | — | — | 🔴 **NOT FOUND** | PROJECT_MAP.md documented this but it's gone |
| `G:\AZAZAEL\CODEX_VIDEOS` | 45 | 3 MB | 🟢 Present | Generated video files |
| `G:\AZAZAEL\local_memory` | 1 | 1 MB | 🟢 Present | memory_store.db (SQLite) |
| `G:\AZAZAEL\archive\` | 114 | 21 MB | 🟡 Legacy | old BATs, EXEs, scripts |
| `G:\source-of-truth\archives\` | 23,125 | — | 🟡 Unknown | Large — needs investigation |
| `G:\CAIN_archive_20260605` | — | — | 🔴 **NOT FOUND** | Confirmed lost (Error #58) |

**Key issues:**
- G: drive is slow SD card (robocopy times out on large transfers — Error #53)
- **Cross-copy drift: 1,633 files** — AZAZAEL_ROOT (6,567 files) vs source-of-truth (4,934 files)
- standalone/ backup is MISSING despite PROJECT_MAP.md documentation
- CAIN_archive completely lost (7.5 GB — Error #58)
- G: volume reported "dirty" in prior sessions — may need chkdsk after reboot

---

### 5. PACKAGE SYSTEM

**Scaffolded but not published:** `packages/azazael-core/`

> Only `packages/azazael-core/` exists — no other package scaffolds.

| Package | Status | Location |
|---------|--------|----------|
| `azazael-core` | ✅ Scaffolded, `pyproject.toml` exists | `packages/azazael-core/` |
| `azazael-worms` | ❌ Not created | Planned for Phase II separation |
| `azazael-orchestration` | ❌ Not created | Planned for Phase III |
| `azazael-codex` | ❌ Not created | Planned for Phase IV |

**Key issues:**
- Package system is scaffolded but not actively used — all imports still use `sys.path.insert(0, 'src')`
- 157+ `sys.path.insert(0, ...)` hacks across the codebase (from REWRITE_TODO.md)
- No published packages to PyPI or private registry

**Improvement opportunities:**
- Switch from `sys.path.insert` hacks to editable pip install (`pip install -e packages/azazael-core`)
- Incremental migration: one subproject at a time

---

### 6. TEST INFRASTRUCTURE

| Test file | Tests | Status | Notes |
|-----------|-------|--------|-------|
| test_agent.py | 16 | ✅ Passing | FreeThreadedAgent |
| test_memorybus.py | 32 | ✅ Passing | MemoryBus |
| test_pool.py | 19 | ✅ Passing | AgentPool |
| test_worm_imports.py | 14 | ✅ Passing | Worm imports |
| test_cluster_worms.py | 5 | ✅ Passing | Basic cluster |
| test_clusterworms_unit.py | 39 | ✅ Passing | Dynamic resolution |
| test_config_and_breaker.py | 36 | ✅ Passing | Config, circuit breaker |
| test_nature_clusters_unit.py | 27 | ✅ Passing | Nature clusters |
| test_metacluster_unit.py | ~10 | ✅ Slow (~5 min) | MetaCluster orchestration |
| test_dlq.py | 8 | ✅ Passing | Dead letter queue |
| test_dlq_watch.py | 9 | ✅ Passing | DLQ monitoring |
| test_freethreading.py | 34 | ✅ Passing | FreeThreadPool |
| test_autodiff_skills.py | 35 | ✅ 34/35 pass | 4-section autodiff verification (1 expected mygrad limitation) |
| test_optimizers_convergence.py | 46 | ✅ 46/46 pass | 7 optimizers on quadratic bowl + Rosenbrock |
| benchmark_autodiff_modes.py | 4 benchmarks | ✅ All run | Forward vs reverse mode, free-threading scaling |
| test_workflow.py | 24 | ✅ Passing | Workflow engine |
| test_ncm_integration.py | 3 | ✅ Passing | NCM integration |
| test_nature_clusters_extended.py | 19 | ✅ Passing | Extended nature tests |
| **Total (standalone)** | **~415+** | ✅ All passing | +115 autodiff tests (34+46+35) |

**Key issues:**
- pytest 9.0.3 segfaults on 3.14t (Error #48) — must run tests standalone via `python tests/test_*.py`
- test_metacluster_unit.py takes ~5 minutes (CLUSTER INSPECTOR worm is bottleneck)
- Test coverage reporting not set up (pytest-cov doesn't work with standalone execution)
- No CI pipeline (test-3.14t.yml exists but not running on GitHub)

---

### 7. ARCHITECTURE QUALITY SCORECARD

| Dimension | Score (1-10) | Assessment | Key Improvement |
|-----------|-------------|------------|-----------------|
| **Modular cohesion** | 7.2 | Good — nature clusters have clear boundaries | N/A |
| **Inter-module coupling** | 5.5 | Poor — CORE/ is over-coupled | Split paths.py into domain modules |
| **Dependency hygiene** | 6.0 | Fair — 18 shims, 4 circular import chains | Delete META/ shims after verification |
| **Type safety** | 8.2 | Improving — mypy: 1,466→1,048 (-418, -28.5%); 6 indentation-critical files fixed; pyright with config: 1,224 | Fix remaining 1,048 mypy errors across 171 files |
| **Test coverage** | 4.0 | Improving — 115+ new tests (autodiff suite) | Add pytest-cov reporting |
| **Documentation** | 6.0 | Fair — 24 skills, good architecture docs, weak module docs | Add module-level docstrings |
| **Build system** | 4.5 | ⚠️ Suspended — 51 EXEs exist but Nuitka broken on 3.14.5t | Await upstream Nuitka 3.14t fix |
| **3.14t readiness** | 8.0 | Strong — free-threading patterns throughout | Monitor for new cp314t wheel issues |
| **Shell injection safety** | 5.5 | Poor — 6 HIGH RISK shell=True usages | Refactor to subprocess.call([...]) |
| **Package management** | 4.0 | Weak — scaffolded but not used | Switch to editable pip install |
| **Desktop project integration** | 6.5 | Fair — all have run.py, no core integration | Evaluate 3 key projects for integration |
| **Overall** | **6.5/10** | ⬆️ +0.1 (type safety: -28.5% mypy errors, 6 files fixed, 2 TARBABY files at zero) | 12 improvement items identified |

---

### 8. NEW IMPROVEMENT ITEMS — From Architecture Review

| ID | Item | Effort | Impact | Status |
|----|------|--------|--------|--------|
| AR-1 | Fix 6 shell=True HIGH RISK usages | 2h | 🔴 High | ✅ **DONE** — 5 fixed (6th is intentional bash runner) |
| AR-2 | Fix 3 legacy skill files: add YAML frontmatter | 0.5h | 🟢 Low | ✅ **DONE** — azazael_314t_master, _optimum, _insights updated June 4 |
| AR-3 | ❌ **CANCELLED** — Archive deprecated Desktop projects (Azazael_UNIFIED, METAWORMS) | — | — | ❌ **DO NOT DO**. User has restored these projects multiple times. They must remain on Desktop. See MEMORIES.md Anti-Pattern #10. |
| AR-4 | ~~Add EXE smoke tests to build_all.py~~ | — | — | ❌ **SUSPENDED** — Nuitka broken on 3.14.5t |
| AR-5 | Switch from sys.path.insert to editable pip install | 3h | 🟡 Medium | ⏳ Pending |
| AR-6 | ~~Investigate CLUSTERWORMS EXE CORE.* import resolution~~ | — | — | ❌ **SUSPENDED** — Nuitka broken on 3.14.5t |
| AR-7 | Add pytest-cov configuration | 2h | 🔴 High | ✅ **DONE** — pyproject.toml [tool.coverage.*] added June 4 |
| AR-8 | Set up CI pipeline (test-3.14t.yml on GitHub) | 4h | 🔴 High | ✅ **DONE** — Fixed stale `cd azazael` paths, ready for GitHub activation June 4 |
| AR-9 | Delete META/ deprecation shims | 1h | 🟡 Medium | ✅ **DONE** — 13 .py files + __pycache__ deleted, output/ reports/ preserved June 4 |
| AR-10 | Archive 3 stale TODO docs | 0.5h | 🟢 Low | ✅ **DONE** — PRODUCTION_TODO, REWRITE_TODO, PHASE_6_TODO moved to docs/archive/ June 4 |
| AR-11 | Fix remaining ~1,490 mypy errors | 8h | 🔴 High | ⏳ Pending |
| AR-12 | Evaluate LlamaServer integration with CORE agents | 3h | 🟢 Low | ⏳ Pending |
| AR-13 | Fix stale path in ENVIRONMENT_WIRING_PLAN.md (Desktop/Azazael_UNIFIED) | 0.1h | 🟢 Low | ✅ **DONE** — Updated to RESTORED status |
| AR-14 | Add auto-duration (words/5.0 WPS) to CODEX_Studio.py --duration auto | 2h | 🟡 Medium | ✅ **DONE** — CAIN_WPS=5.0, is_auto boolean, single HTML read |
| AR-15 | Audit existing CAIN .mp4 videos against 5.0 WPS standard | 1h | 🟡 Medium | ✅ **DONE** — CAIN_session_20260605.mp4 was 8.2 WPS (too fast), re-rendered at 98s |
| AR-16 | Offer user restoration of 52 files from Desktop/scripts_archive/ | 0.1h | 🟡 Medium | ⏳ ASK FIRST |
| AR-17 | Sync G: source-of-truth with AZAZAEL_ROOT (1,633 file gap) | 1h | 🟡 Medium | ✅ **DONE** — Automated via scripts/sync_g_drive.py, robocopy with /R:1 /W:1, June 7 |
| AR-18 | Document AZAZAEL_Vault in PROJECT_MAP.md (vault_server.py, Python 3.13 EXE) | 0.5h | 🟢 Low | ✅ DONE — documented below |
| AR-19 | Document AZAZAEL_ARCHIVE in PROJECT_MAP.md (METAWORMS enriched data) | 0.5h | 🟢 Low | ✅ DONE — documented below |
| AR-20 | Register 3 guardrail skills as globally loadable (powershell-escape, session-recording, crossplat-fileops) | 1h | 🟡 Medium | ✅ **DONE** — 68 skills registered in .agents/skills/ via mass registration, June 7 |
| AR-21 | Investigate missing G: standalone/ backup (was documented in PROJECT_MAP but not on disk) | 0.5h | 🟡 Medium | ⏳ Pending |
| AR-22 | Investigate azazael/ 46.7 GB size (verify node_modules, build artifacts) | 0.5h | 🟢 Low | ⏳ Pending |

**22 items (16 original + 6 new from audit: AR-17 through AR-22).**

---

### 9. RECOMMENDED IMMEDIATE ACTIONS (Priority Order)

| # | AR-ID | Action | Priority | Status |
|---|-------|--------|----------|--------|
| 1 | AR-1 | Fix 6 shell=True HIGH RISK usages | P0 | ✅ **DONE** — 5 fixed (6th is intentional) June 4 |
| 2 | AR-10 | Archive 3 stale TODO docs | P0 | ✅ **DONE** — Moved to docs/archive/ June 4 |
| 3 | AR-9 | Delete META/ deprecation shims | P0 | ✅ **DONE** — 13 files + __pycache__ deleted June 4 |
| 4 | AR-2 | Fix 3 legacy skill files (YAML frontmatter) | P0 | ✅ **DONE** — azazael_314t_*.md + _insights.md June 4 |
| 5 | AR-7 | Add pytest-cov configuration | P0 | ✅ **DONE** — pyproject.toml [tool.coverage.*] June 4 |
| 6 | AR-8 | Set up CI pipeline (GitHub Actions) | P0 | ✅ **DONE** — test-3.14t.yml paths fixed June 4 |
| 7 | AR-4 | ~~Add EXE smoke tests to build_all.py~~ | — | ❌ **SUSPENDED** — Nuitka broken on 3.14.5t |
| 8 | AR-11 | Fix remaining mypy errors — next 5 files | P1 | ⏳ Next priority |
| 9 | AR-3 | ❌ **CANCELLED** — Archive deprecated Desktop projects | — | ❌ DO NOT DO. User restored these multiple times. MEMORIES.md #10. |
| 10 | AR-5 | Switch to editable pip install for azazael-core | P2 | ⏳ Pending |
| 11 | AR-6 | ~~Investigate CLUSTERWORMS EXE import resolution~~ | — | ❌ **SUSPENDED** — Nuitka broken |
| 12 | AR-12 | Evaluate LlamaServer integration | P3 | ⏳ Pending |
| 13 | AR-17 | Sync G: source-of-truth with AZAZAEL_ROOT | P1 | ✅ **DONE** — sync_g_drive.py automation, June 7 |
| 14 | AR-20 | Register 3 guardrail skills as globally loadable | P1 | ✅ **DONE** — 68 skills pre-loaded, June 7 |
| 15 | AR-18 | Document AZAZAEL_Vault in PROJECT_MAP | P0 | ✅ DONE — vault_server.py, 95 MB, Python 3.13 |
| 16 | AR-19 | Document AZAZAEL_ARCHIVE in PROJECT_MAP | P0 | ✅ DONE — METAWORMS enriched data |
| 17 | AR-21 | Investigate missing G: standalone/ backup | P2 | ⏳ Not on disk despite documentation |
| 18 | AR-22 | Investigate azazael/ 46.7 GB size | P2 | ⏳ Verify build artifacts |

**13 of 22 items completed.** AR-16 pending (ASK FIRST — requires user input).

```
✅ Completed June 7 Session:
  1. DirectMemory canonical system (replaces CodebuffTracker/SessionRecorder)
  2. Deadlock fix: local_memory.py _QueryTimer.__exit__ lock re-acquisition
  3. 98 orphaned sessions closed → 0 open
  4. Merged sessions: multi-message grouping via merged_session_id
  5. Deprecation warnings: record_session.py, codebuff_tracker.py → FutureWarning
  6. 68 skills pre-loaded in .agents/skills/ (34 new)
  7. G: sync automated (scripts/sync_g_drive.py, robocopy)
  8. G: source-of-truth synced (5,296+ files, DB backed up)
  9. AR-17 + AR-20 marked DONE
 10. Cluster execution verified (no hangs after deadlock fix)

✅ Completed June 14 Session — AUTODIFF SUITE:
  1. 4 autodiff skills created: forward, backprop, gradient (7 optimizers), higher-order
     - Registered in SKILLS_CATALOG.md as #55-58 with auto_load: true
  2. tests/test_autodiff_skills.py — 35 tests across 4 sections (34/35 pass)
  3. tests/test_optimizers_convergence.py — 46/46 pass (all 7 optimizers on quadratic bowl + Rosenbrock)
  4. tests/benchmark_autodiff_modes.py — 4 benchmarks (reverse-vs-forward, JVP, free-threading, throughput)
  5. MYGRAD 2.3.0 LIMITATIONS DIAGNOSED on Python 3.14.5t free-threading:
     - .backward(seed) on vector outputs → .grad stays None (auto-fallback to finite differences)
     - .grad has no setter → workaround: slice assignment p.grad[:] *= x
     - null_grad() sets .grad to None (not zero)
     - mg.tensor() doesn't accept requires_grad kwarg
  6. Skill docs fixed: jacobian() with finite-diff fallback, clip_gradients() with slice assignment,
     jvp() with None.grad guard in forward-mode skill
  7. 3 skill docs updated: forward, backprop, higher-order
```

```
✅ Completed June 4 Session:
  1. Fix 6 shell=True HIGH RISK usages (AR-1)
  2. Archive 3 stale TODO docs (AR-10)
  3. Delete META/ deprecation shims (AR-9)
  4. Fix 3 legacy skill files (AR-2)
  5. Add pytest-cov configuration (AR-7)
  6. Set up CI pipeline (AR-8)

✅ Completed June 7 Session (above):
  - DirectMemory canonical, deadlock fixed, sessions cleaned, skills pre-loaded, G: sync automated

✅ Completed June 5 Session (not AR-tracked):
  - LESSONS_DESTRUCTIVE_BEHAVIOR.md (4 incidents, 6 rules)
  - MEMORIES.md Anti-Pattern #11 (never delete/move/re-create user work)
  - SESSION_STARTUP.md updated (destructive behavior warning)
  - 90 stale path references fixed (CODEX/DOCUMENTATION/API/*.md)
  - Desktop projects verified: all 12 run.py working
  - Azazael_UNIFIED restored from archive
  - METAWORMS run.py created
  - 7 active launchers restored from scripts_archive
  - CAIN session analysis rendered (HTML + MP4 + WMV)
  - CAIN re-rendered at 98s (5.0 WPS standard)
  - CAIN scroll speed standard determined (5.0 WPS)
  - LESSONS_DEV_TOOLS.md created (13 sections, effective dev commands)
  - AR-13: ENVIRONMENT_WIRING_PLAN.md stale path fixed (Azazael_UNIFIED marked RESTORED)
  - AR-14: CODEX_Studio.py --duration auto (CAIN_WPS=5.0, auto-duration from word count)
  - AR-15: CAIN videos audited against 5.0 WPS (session report was 63% too fast, now correct)

⏳ Next Session (P1):
  7. Add EXE smoke tests to build_all.py (AR-4)
  7. Fix remaining mypy errors — next 5 files (AR-11) (AR-4 suspended: Nuitka broken)
  16. ASK USER about restoring scripts_archive files (AR-16)

⏳ Future (P2-P3):
  9. Switch to editable pip install (AR-5)
  10. Investigate CLUSTERWORMS EXE import (AR-6)
  12. Evaluate LlamaServer integration (AR-12)

❌ CANCELLED (Do NOT suggest):
  - AR-3: Archive deprecated Desktop projects
```

## Audit Finding Cross-Reference (June 19, 2026)

Classification of all 10 audit findings against existing TODO steps:

| # | Finding | AR-ID | Classification | Existing Step | Notes |
|---|---------|-------|---------------|---------------|-------|
| 1 | 3 remaining shell=True (environ_updater, lsp_diagnosis, gate_bash) | AR-1 | ⚠️ REINFORCES | AR-1 (shell=True) | AR-1 claimed DONE but 3 remained; now truly DONE |
| 2 | os.system() — 0 actual calls | AR-1 | ✅ ADDITIVE | None | All 7 matches in compliance docs/scanner test strings only |
| 3 | No mypy.ini (actually present in pyproject.toml) | — | 🔴 DUPLICATE | pyproject.toml [tool.mypy] | Already configured |
| 4 | No .coveragerc (actually present in pyproject.toml) | AR-7 | 🔴 DUPLICATE | pyproject.toml [tool.coverage.*] | Already DONE |
| 5 | 4 deprecated Desktop projects | AR-3 | 🔴 DUPLICATE | AR-3 CANCELLED | User restored; must remain |
| 6 | Ubuntu-26.04 1.3GB bloat | AR-22 | ⚠️ REINFORCES | AR-22 (azazael size) | Now TRIMMED: 270MB with G: archive backup |
| 7 | No unified lockfile | — | ✅ ADDITIVE | Step 1 (post-session cleanup) | requirements-3.14t.txt created |
| 8 | tools/ 36 .py scripts (cohesion 0.4) | — | ✅ ADDITIVE | PATH_FORWARD separation | README catalog created; subdirectories created |
| 9 | azazael-core pyproject.toml Python >=3.13 | AR-5 | ⚠️ REINFORCES | AR-5 (editable pip install) | Fixed to >=3.14; pip install -e verified |
| 10 | gate_bash.py no Windows cmd.exe fallback | — | ✅ ADDITIVE | None | bash/cmd fallback added with OSError handling |

**Ratio:** 40% ADDITIVE (4/10) — audit uncovered genuine new gaps. 30% REINFORCES (3/10) — extended existing items. 30% DUPLICATE (3/10) — already covered.

---
## Correction addendum — 2026-09-29 (stale counts)
- Dated rows above cite 220/35 (NM-15), 226/35, 91/17 worm counts: live
  `discover_worms()` now reports **250 worms / 35 categories**
  (`src/CORE/worm_registry.py`). Inline rows are point-in-time history — do not
  edit; re-run discovery for fresh numbers.
- Skill counts: `SKILLS_CATALOG.md` regenerated this date — **1,234** table rows =
  1,234 mirror dirs = 1,234 canonical files (prior 1,224 / 1,259 claims superseded).

