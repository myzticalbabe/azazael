# PROJECT MAP — Complete Azazael Ecosystem Inventory

> *Generated: May 29, 2026 — Phase 22*
> *Purpose: Single source of truth for all projects, their locations, status, and relationships*

---

## 1. AZAZAEL CORE — `C:\Users\clint\azazael\`

**Status:** 🟢 Active | **Type:** Primary codebase

### Structure
| Directory | Files | Description |
|-----------|-------|-------------|
| `src/` | 305 .py | Main source tree (18 subdirectories) |
| `src/CORE/` | 58 .py | Core infrastructure (worm_registry, paths, config, freethreading, local_memory, etc.) |
| `src/CORE/WORMS/` | 29 .py + 28 expansion | Worm implementations (91 discovered worms across 17 categories) |
| `src/ORCHESTRATION/` | 70 .py | Orchestration layer (HYDRA pipeline, HYDRA_Bridge, scripts, ml_platforms) |
| `src/CODEX/` | 70 .py | CODEX Studio, video generation, testing, POPUPS |
| `src/HYDRA/` | 11 .py | HYDRA ML cluster (ml_platforms shims) |
| `src/UTILITIES/` | 23 .py | Utility tools (TARBABY, etc.) |
| `src/META/` | 13 .py | Deprecation shims |
| `src/AZAZAEL_TOOLKIT/` | 8 .py | Toolkit scripts |
| `src/TOOLS/` | 5 .py | Tool scripts |
| `src/SCRIPTS/` | 4 .py | Script collection |
| `src/INTERPRETERS/` | 3 .py | Language interpreters |
| `src/CLI/` | 2 .py | CLI interface |
| `tests/` | 7 .py | Pytest test suite (87 pass, 15 execution-skipped) |
| `skills/` | 36 .md | Skill definitions for Codebuff (was 13, grew to 36) |
| `MEMORIES.md` | — | Cross-session memory (anti-patterns, architecture, metrics) |
| `ERROR_LOG.md` | — | 46 logged errors with root causes and fixes |
| `SESSION_STARTUP.md` | — | Next session congruency marker |
| `SYSTEM_INSTRUCTIONS.md` | — | Error recording SOP |
| `SKILLS_CATALOG.md` | — | Complete skills inventory |

### Worm Registry
- **91 worms** across **17 categories**: analysis(3), backup(5), communication(5), config(5), container(5), diagnostic(4), learning(5), migration(5), ml(2), monitor(6), orchestration(5), profiling(5), security(5), sync(1), telemetry(5), utility(5), visualization(5)
- Discovered via `CORE/worm_registry.py` → `discover_worms()` — scans `CORE/WORMS/` at runtime
- Auto-categorization heuristics based on class name
- **Known limitation**: filesystem-based discovery doesn't work in Nuitka onefile EXEs

---

## 2. DESKTOP STANDALONE SUITE — `C:\Users\clint\Desktop\AZAZAEL_Standalone\`

**Status:** 🟢 Active | **Type:** Compiled executables

| Metric | Value |
|--------|-------|
| EXE count | 51 (`*_314t.exe`) |
| BAT count | 51 (`*_314t.bat`) — 1:1 pairing |
| Build system | `build_all.py` — 51 modules tracked |
| NEEDS_TKINTER | 14 modules (all rebuilt with tk-inter plugin, Phase 21) |
| NEEDS_PYTHONPATH | 2 modules (CONCURRENCY, SMARTDISK) |
| Build Python | 3.14t (patched Nuitka) |
| G: backup | `/g/AZAZAEL/standalone/` (51 EXEs + 51 BATs) |

### 7 EXEs Deep-Tested (Phase 22)
| EXE | Test | Result |
|-----|------|--------|
| CODEX_Studio | `--cli` | ✅ Works (requires --input/-o args) |
| CONCURRENCY | `--scan` | ✅ Produces JSON scan report (4 modules) |
| CLUSTERWORMS | `--discover` | ⚠️ "Worm registry not available" — Nuitka CORE.* import path limitation |
| HYDRA | `--help` | ✅ Works |
| HYDRA_Container | `--help` | ✅ Works |
| OS_Congruency | `--help` | ✅ Works |
| SMARTDISK | `--help` | ✅ Works |

---

## 3. DESKTOP PROJECTS

### Active Projects

| Project | .py | .exe | .bat | Subdirs | Status |
|---------|-----|------|------|---------|--------|
| **AZAZAEL_Standalone** | 26 | 52 | 51 | 39 | 🟢 Fully operational |
| **azazael** | 11 | 0 | 0 | src, tests, skills | 🟢 Active development |
| **EveUnleashed_Selector** | 32 | 0 | 3 | agents, build, config, data, docs, inference, models, output, ql, tests, training, wheels | 🟡 Partially operational |
| **PerformanceMonitor** | 4 | 0 | 1 | frontend, go, python, rust | 🟡 Partially operational |
| **Ultimate_Agent_Selector** | 6 | 0 | 0 | agents, config, golang_backend, insights, launcher, models, rust_backend, src, tests, training | 🟡 Partially operational |
| **WSL_CrossExplorer** | 1 | 0 | 0 | config, frontend, src | 🟡 Partially operational |
| **CODEX** | 60+ | 0 | 5 | 20+ subdirs | 🟡 Video generation suite |
| **PAMS** | 2 | 0 | 0 | config, data, logs, src | 🟡 Memory system |

### Additional Desktop Items (Audit June 5, 2026)
| Project | Files | Size | Launcher | Description |
|---------|-------|------|----------|-------------|
| **AZAZAEL_Vault** | 93 | 95 MB | `vault_server.exe` (6.5 MB) | Nuitka-built vault server (Python 3.13, not 3.14t). Contains vault_server.py (29 KB), index.html (79 KB), run_vault.bat. Build artifacts include _nuitka_test.build/ and dist/. |
| **AZAZAEL_ARCHIVE** | 11 | 19 KB | None | Archived METAWORMS enriched data (changez, deadz, dependz, logz, metaz, metricz, validz JSON files). Includes run.py + metaworms_report.html. |
| **scripts_archive** | 59 | 359 KB | None | Archived Desktop scripts (was 52 files, grew to 59). See AR-16 for restoration consideration. |

### Deprecated / Archived
| Project | Notes |
|---------|-------|
| **Azazael_UNIFIED** | Old unified codebase — superseded by azazael/ |
| **METAWORMS** | Legacy — superseded by CORE/WORMS/ |
| **agent_system** | Skeletal (3 .py stubs) |
| **SysTools_JSON_Converter** | Utility tool |
| **CODEX_Studio_Output** | Output artifacts from CODEX Studio |
| **WSL Models** | WSL-related model storage |

### Loose Desktop Scripts
| Type | Files |
|------|-------|
| .py (11) | `_pick_draft.py`, `create_memories.py`, `full_inference_test.py`, `gen_everything.py`, `llama_client.py`, `max_ctx.py`, `module_G.py`, `probe_all.py`, `probe_model.py`, `test_write.py`, `write_test.py` |
| .bat (7) | `AZAZAEL_LAUNCHER.bat`, `CODEX_Studio.bat`, `CODEX_Studio_Launcher.bat`, `build_llama_all_backends.bat`, `build_tensorflow_intel.bat`, `install_nvidia_ncg_python314.bat`, `test_oneapi.bat` |
| .ps1 (2) | `azazael.ps1`, `launch_llama_stack.ps1` |
| .md (8) | Plan/guide/reflection docs |
| .lnk | `CODEX_Studio.lnk`, `Eve_Unleashed.lnk` |

---

## 4. G: DRIVE ARCHIVE — `/g/AZAZAEL/`

**Status:** 🟡 Drift detected | **Source-of-truth:** 11.8 GB (4,934 files) | **AZAZAEL_ROOT:** 14.7 GB (6,567 files)

> **⚠️ Cross-copy drift:** source-of-truth lags behind AZAZAEL_ROOT by **1,633 files**. Needs reconciliation.

| Directory | Contents | Health |
|-----------|----------|--------|
| `AZAZAEL_ROOT/src/` | 610 .py files (source mirror) | 🟢 Present |
| `AZAZAEL_ROOT/skills/` | Skill markdown files | 🟢 Present |
| `AZAZAEL_ROOT/` | Records: MEMORIES.md, ERROR_LOG.md, SESSION_STARTUP.md, etc. | 🟢 Present |
| `source-of-truth/azazael/` | 4,934 files, 11.8 GB — azazael project copy | 🟡 **Lags by 1,633 files** |
| `source-of-truth/archives/` | 23,125 files — large archive | 🟡 Needs investigation |
| `standalone/` | ~~51 EXEs + 51 BATs~~ | 🔴 **NOT FOUND** — documented but not on disk |
| `archive/` | 3 dirs, 40 files — old BATs, old EXEs, Desktop scripts | 🟡 Legacy |
| `archive/old_bats_20260529/` | 39 archived old-style BATs | 🟡 Present |
| `archive/old_exes_20260529/` | Archived EXEs (incl. old 17.4 MB HYDRA_Bridge) | 🟡 Present |
| `CODEX_VIDEOS/` | 45 files, 3 MB — generated videos | 🟢 Present |
| `local_memory/` | memory_store.db (SQLite memory database) | 🟢 Present |
| `CAIN_archive_20260605` | — | 🔴 **LOST** — Error #58 (7.5 GB) |

---

## 5. TEST SUITE SUMMARY

| Test File | Passed | Failed | Skipped | Notes |
|-----------|--------|--------|---------|-------|
| `test_config_and_breaker.py` | 32 | 0 | 4 | Config validation, circuit breaker, discovery |
| `test_clusterworms_unit.py` | 32 | 0 | 7 | ClusterWORMZ construction + execution (7 exec skipped) |
| `test_nature_clusters_unit.py` | 23 | 0 | 4 | NatureCluster construction + discovery (4 exec skipped) |
| **Total** | **87** | **0** | **15** | Execution tests hang (Error #37) — skipped |

---

## 6. KNOWN ISSUES & LIMITATIONS

| # | Issue | Severity | Phase Identified |
|---|-------|----------|-----------------|
| 1 | CLUSTERWORMS EXE: "Worm registry not available" — Nuitka can't resolve CORE.* imports in onefile mode without PYTHONPATH, and `discover_worms()` filesystem scanning doesn't work in bundled EXE | 🟡 Medium | Phase 22 |
| 2 | Execution tests hang (test_execute_single_worm, test_execute_all, test_execute_discovered_worms) — Error #37 | 🟡 Warning | Phase 19 |
| 3 | CODEX_Studio is GUI-first — `--help` times out in onefile mode due to Tkinter startup delay | 🟢 Minor | Phase 22 |
| 4 | Nuitka 3.14t compatibility — requires patches via patch_nuitka_314t.py | 🟡 Fixed | Phase 9 |
| 5 | CONCURRENCY/SMARTDISK need PYTHONPATH during build | 🟡 Warning | Phase 12 |

---

## 7. BUILD SYSTEM

**File:** `Desktop/AZAZAEL_Standalone/build_all.py`

- **51 modules** in MODULES dict (14 NEEDS_TKINTER, 2 NEEDS_PYTHONPATH)
- Tiers 1-9: WormZ Registry → Orchestration → Standalone GUI
- Build Python: 3.14t (free-threading, patched Nuitka)
- NOFOLLOW_EXTRAS: torch, optree, openvino, numpy, PIL, cv2, matplotlib, pandas, scipy, sklearn
- BAT regenerator: `regenerate_bats.py` — maintains 1:1 EXE↔BAT pairing
