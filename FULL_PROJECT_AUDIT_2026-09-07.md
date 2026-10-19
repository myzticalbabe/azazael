# AZAZAEL — Full Project Audit Report

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project;
> production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only
> sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Statements
> below describe the state on the date of this record.

> **Date:** September 7, 2026 (session `codebuff_20260907_233715_13888`)
> **Methodology:** 3-Pass Architecture Review (azazael-architecture-review skill)
> **Scope:** Desktop (40 dirs) + azazael core (src/, tests, registry) + G: Drive + recording/tooling health
> **Recorded:** Via DirectMemory (session_start, skills_loaded, audit_begin)

---

## Pass 1: INVENTORY — What Exists

### Tooling / Environment (verified live)

| Item | Status | Evidence |
|------|--------|----------|
| Python (system) | 3.14.7 | `python --version` |
| Python (secondary) | 3.13.14 | `python3 --version` |
| venv-314t | Present | `venv-314t/Scripts/python.exe` |
| FreeBuff | v0.0.171 | `freebuff --version` |
| Bun | 1.3.14 | `bun --version` |
| DirectMemory live DB | 98 MB, 789 sessions | `~/.azazael/memory_store.db` |
| DirectMemory backups | 90,458 + 34,342 sessions | `memory_store.backup_20260906_122325.db`, `_20260907_prearchive.db` |
| Worm registry | **136 worms** (docs say 77) | live `discover_worms()` |
| Skills synced | 1224 (4 updated this session) | `sync_skills.py` |
| azazael src .py | 538 | `find src -name "*.py"` |
| Test files | 117 | `find tests -name "*.py"` |

### 1. Desktop Projects (40 directories — was 14 in skill, 22 at 2026-07-30 audit)

| # | Project | Type | Status | Key Contents |
|---|---------|------|--------|-------------|
| 1 | **AOA** | External | ✅ Active | 23 .py, 2 html — research/investigation arm |
| 2 | **AZAZAEL_ARCHIVE** | AZAZAEL | 📦 Archive | 1 .py remnant |
| 3 | **AZAZAEL_COSMOS_VIEWER** (+6 variants: aoa_g, aoa_source, bcc, kali, progress_governance, vermillion_lightfury) | AZAZAEL | ✅ Output | `cosmos` viewers (1 html each) |
| 4 | **AZAZAEL_Standalone** | AZAZAEL | 🔴 REPURPOSED | **0 EXEs** (was 52). Now docs hub (SYSTEM_INSTRUCTIONS.md, LESSONS_MASTER.md, skills/, eve_unleashed_app.dist). **Real EXEs verified at `G:/AZAZAEL_Standalone` — 52 .exe present** |
| 5 | **AZAZAEL_Vault** | AZAZAEL | ⚠️ Partial | vault_server.py + index.html + run_vault.bat |
| 6 | **Azazael_Audit** | AZAZAEL | ✅ Data | 104 MB audit artifacts |
| 7 | **Azazael_UNIFIED** | AZAZAEL | ❌ Deprecated | ORCHESTRATION_UNIFIED remnant only — archive candidate |
| 8 | **BCC / BCC_Maps** | External | ✅ Active | BCC 2 html; BCC_Maps 5 py + 3 html |
| 9 | **CODEX_Azazael_Complete / CODEX_Quartet** | AZAZAEL | 📦 Output | MP4 renders |
| 10 | **DisclosureWhitepaper** | AZAZAEL | 📦 Output | 443 MB whitepaper MP4 renders |
| 11 | **EveUnleashed_Selector** | External | ✅ Operational | 31 py, run.py, Tkinter GUI |
| 12 | **FACEBOOK** | External | ✅ Active | 26 py, 7 bat, 126 html — 1.5 GB investigation project |
| 13 | **FACEBOOK_UBUNTU_MIRROR** | External | ⚠️ Empty | 0 MB — empty mirror dir |
| 14 | **Graphify_Codebase_Atlas_2026-08-27** | AZAZAEL | ✅ Output | **21 GB** — codebase atlas |
| 15 | **Libra** | External | 🟢 Active | 46 py — legal filing system (PA/Berks jurisdiction) |
| 16 | **LlamaServer** | External | ✅ Operational | run.py, Rust llama-server |
| 17 | **PAMS** | AZAZAEL | ✅ Operational | run.py, benchmark_pams.py |
| 18 | **PerformanceMonitor** | External | ✅ Operational | run.py, Go+Rust+Python |
| 19 | **Project Launchers** | AZAZAEL | ✅ Hub | launcher scripts |
| 20 | **TikTok_Videos** | External | ✅ Data | 1.4 GB video output |
| 21 | **Ultimate_Agent_Selector** | External | ✅ Operational | run.py (4/7 agents implemented) |
| 22 | **WSL Models / WSL_CrossExplorer** | External | ✅ Operational | run.py present both |
| 23 | **azazael_graphs / logs / scripts_archive / __pycache__** | misc | 🧹 Cleanup | housekeeping dirs |

**No longer on Desktop (archived ✅):** agent_system, Azazael_UNIFIED (remnant), CODEX, CODEX_Studio_Output, METAWORMS, SysTools_JSON_Converter → all in `G:/Desktop_Archive/deprecated_projects/`.

### 2. G: Drive (verified)

| Path | Contents |
|------|----------|
| `G:/AZAZAEL` | AZAZAEL_ROOT, BCC evidence, AOA, docs |
| `G:/AZAZAEL_SOURCE_OF_TRUTH` | sync mirror |
| `G:/AZAZAEL_Standalone` | **52 EXEs** + .bat launchers (the real standalone suite) |
| `G:/AZAZAEL_UBUNTU` | Ubuntu/WSL mirror |
| `G:/Desktop_Archive/deprecated_projects` | 6 archived projects ✅ |

### 3. azazael Core Repo

- **Uncommitted work:** **151 changed files** — all from the 2026-09-07 learning-loop session: `scripts/evolution_cycle.py`, `scripts/live_monitor.py`, `src/CORE/WORMS/expansion/evolution.py`, `learning.py`, `learning_features.py`, `learning_pipeline.py`, `scheduling.py`, `codebuff_tracker.py`, `config.py`, etc.
- **Recent commits:** live-monitor dashboard, evolution reward plot fix, headless Gephi renders, environment sync diff report.
- **Subsystem audit already present:** `LEARNING_LOOP_AUDIT_20260907.md` — 6.4/10 overall, 8 improvement items (cohesion 0.85, coupling 6/10, health 🟡).

---

## Pass 2: RATE — How Healthy

| Layer | Cohesion | Coupling | Health | Notes |
|-------|----------|----------|--------|-------|
| Desktop output/atlas dirs | 0.9 | 2 | 🟢 | self-contained renders |
| Desktop active projects (run.py) | 0.7 | 4 | 🟢 | all 8 documented run.py launchers present |
| AOA / BCC / FACEBOOK / Libra | 0.6 | 5 | 🟡 | active but no run.py launchers — inconsistent entry points |
| AZAZAEL_Standalone (Desktop) | 0.8 | 1 | 🟡 | docs hub; EXEs relocated to G: — Desktop copy is stale/misleading |
| azazael src/CORE | 0.7 | 7 | 🟡 | 136-worm registry, growing |
| Deprecated remnants (Azazael_UNIFIED, FACEBOOK_UBUNTU_MIRROR) | 0.2 | 1 | 🔴 | cleanup candidates |

---

## Pass 3: SCORECARD (12 dimensions)

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Modular cohesion | 7.5 | clear module boundaries in src/ |
| Inter-module coupling | 5.5 | CORE remains a choke point |
| Dependency hygiene | 7.0 | deprecated recorders hard-blocked; shims in archive |
| Type safety | 5.0 | mypy/pyright baselines still thousands of errors (per earlier audits) |
| Test coverage | 4.5 | 117 test files; pytest segfaults on 3.14t (Error #48) — must run standalone |
| Documentation | 7.0 | 1224 skills, audit trail docs |
| Build system | 6.0 | 52 EXEs on G:, Nuitka 3.14t build issues known |
| 3.14t readiness | 7.0 | venv-314t works; test_clusterworms_unit segfaults (known) |
| Shell injection safety | 7.0 | os_system backlog reduced to 10 (Aug 8 audit) |
| Package management | 4.0 | sys.path hacks remain |
| Desktop integration | 6.5 | run.py launchers; 3 stubs in Ultimate_Agent_Selector |
| **Overall** | **6.1/10** | 10 improvement items (below) |

---

## Improvement Items (cross-referenced)

| ID | Item | Priority |
|----|------|----------|
| A-1 | **Commit the 151 uncommitted files** from the Sep 7 learning-loop session (evolution.py, learning.py, live_monitor, config) — uncommitted work = data-loss risk | P0 |
| A-2 | **Reconcile Desktop/AZAZAEL_Standalone** — it holds 0 EXEs but the name implies the suite; add README pointing to `G:/AZAZAEL_Standalone` or replace contents | P1 |
| A-3 | Update `DESKTOP_PROJECTS_AUDIT.md` — 14 documented projects ≠ 40 actual dirs; add AOA/BCC/FACEBOOK/Libra/atlas dirs + archived list | P1 |
| A-4 | Fix `test_clusterworms_unit.py` segfault (exit 139) on 3.14t or mark known-skip — currently looks like a broken test | P1 |
| A-5 | Clean empty/stale dirs: `FACEBOOK_UBUNTU_MIRROR` (0 MB), `Desktop/Azazael_UNIFIED` remnant, `Desktop/logs`, `Desktop/__pycache__` | P2 |
| A-6 | Add run.py launchers to AOA, BCC, FACEBOOK, Libra for entry-point consistency (matches the 14-project convention) | P2 |
| A-7 | Archive `Desktop/Graphify_Codebase_Atlas_2026-08-27` (21 GB) to G: — desktop space pressure | P2 |
| A-8 | Update worm-count docs (77 → 136) in SKILLS_CATALOG.md / startup docs | P2 |
| A-9 | Complete Ultimate_Agent_Selector 3 stubs (code_generation, orchestrator, rl_learner) | P3 |
| A-10 | Execute LEARNING_LOOP_AUDIT_20260907.md's 8 improvement items (esp. AR-4: WSL monitor default to live DB) | P1 |

---

## Recording Status

- DirectMemory session `codebuff_20260907_233715_13888` — session_start, skills_loaded, audit_begin recorded (verified in `~/.azazael/memory_store.db`).
- Backups healthy: Sep 6 (90,458 sessions) and Sep 7 pre-archive (34,342).
- RULE 0R sync run: 1224 skills, 4 updated.

*Report generated from live filesystem + DB queries — no inference agents were available in this session's tool roster.*