# AZAZAEL — Desktop Projects Operability Audit

> **Generated:** May 29, 2026 — **Updated:** September 7, 2026 (Full re-audit)
> **Purpose:** Complete inventory and operability assessment of all projects on the Desktop
> **Scope:** 40 Desktop directories (was 14 in the original skill, 22 at the 2026-07-30 audit)
> **Method:** 3-pass architecture review — live `du`/`ls` verification, run.py/entry-point discovery, G: drive cross-check
> **Companion report:** `FULL_PROJECT_AUDIT_2026-09-07.md` (scorecard, 6.1/10, 10 improvement items)

---

## Summary — Current Reality (September 7, 2026)

| Metric | Value |
|--------|-------|
| Desktop directories | **40** |
| run.py launchers present | **7** (EveUnleashed_Selector, LlamaServer, PAMS, PerformanceMonitor, Ultimate_Agent_Selector, WSL Models, WSL_CrossExplorer) |
| Operational projects | 12 |
| Output/atlas/render dirs | 12 |
| Deprecated/remnant dirs | 3 (Azazael_UNIFIED, FACEBOOK_UBUNTU_MIRROR, AZAZAEL_ARCHIVE) |
| Housekeeping dirs | 3 (logs, scripts_archive, __pycache__) |
| Total Desktop size | ~25 GB (largest: Graphify atlas 21.3 GB) |
| Deprecated projects archived to G: | 6 ✅ (agent_system, CODEX, CODEX_Studio_Output, METAWORMS, SysTools_JSON_Converter, Azazael_UNIFIED) |

**Key structural changes since the original audit:**
1. **AZAZAEL_Standalone repurposed** — Desktop copy now holds **0 EXEs** (docs hub only). The **52 EXEs live at `G:/AZAZAEL_Standalone`**.
2. **6 deprecated projects archived** to `G:/Desktop_Archive/deprecated_projects/`.
3. **New active projects:** AOA, BCC/BCC_Maps, FACEBOOK (1.5 GB investigation), Libra (legal filing), TikTok_Videos.
4. **New output families:** 7 AZAZAEL_COSMOS_VIEWER variants, Graphify_Codebase_Atlas (21.3 GB), Azazael_Graphs (x3), Filesystem_Graphs/Scans, CODEX_Azazael_Complete, CODEX_Quartet, DisclosureWhitepaper.

---

## Per-Directory Status (40 dirs, verified Sep 7)

### ✅ Operational Projects (12)

| # | Project | Type | Entry | Contents |
|---|---------|------|-------|----------|
| 1 | **AOA** | External | 23 .py, 2 html | Research/investigation arm, evidence builds |
| 2 | **AZAZAEL_Vault** | AZAZAEL | vault_server.py, run_vault.bat | vault_notes.json + index.html |
| 3 | **BCC / BCC_Maps** | External | 5 .py + 3 html (Maps) | BCC investigation + map gallery |
| 4 | **EveUnleashed_Selector** | External | `run.py` ✅ | 31 .py, Tkinter GUI, rani-vl framework |
| 5 | **FACEBOOK** | External | 26 .py, 7 .bat, 126 html | 1.5 GB investigation project |
| 6 | **Libra** | External | 46 .py | Legal filing system (PA/Berks jurisdiction), BIBL/CAIN/CODEX/HORUS subsystems |
| 7 | **LlamaServer** | External | `run.py` ✅ | Rust llama-server + Jan backend |
| 8 | **PAMS** | AZAZAEL | `run.py` ✅ | Memory/event system |
| 9 | **PerformanceMonitor** | External | `run.py` ✅ | Go+Rust+Python telemetry |
| 10 | **Ultimate_Agent_Selector** | External | `run.py` ✅ | 4/7 agents implemented |
| 11 | **WSL Models** | External | `run.py` ✅ | WSL + GGUF launchers |
| 12 | **WSL_CrossExplorer** | External | `run.py` ✅ | WSL file explorer |

### 📦 Output / Atlas / Render Directories (12)

| # | Project | Contents |
|---|---------|----------|
| 13 | **AOA_Complete_Atlas_2026-08-27** | AOA atlas |
| 14 | **AZAZAEL_COSMOS_VIEWER** (+6 variants: aoa_g, aoa_source, bcc, kali, progress_governance, vermillion_lightfury) | 7 `cosmos` HTML viewers |
| 15 | **Azazael_Audit** | 104 MB audit artifacts |
| 16 | **Azazael_Filesystem_Graphs_2026-08-27** | filesystem graph renders |
| 17 | **Azazael_Full_Filesystem_Scans_2026-08-27** | 206 MB full scans |
| 18 | **Azazael_Graphs_2026-08-27 / 2026-08-28** | graph renders + html |
| 19 | **CODEX_Azazael_Complete / CODEX_Quartet** | MP4 renders |
| 20 | **DisclosureWhitepaper** | 443 MB whitepaper MP4s |
| 21 | **Graphify_Codebase_Atlas_2026-08-27** | **21.3 GB** codebase atlas |
| 22 | **TikTok_Videos** | 1.4 GB video output |
| 23 | **azazael_graphs** | live graph output |

### ⚠️ Partial / Repurposed / Deprecated (6)

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 24 | **AZAZAEL_Standalone** | 🔴 REPURPOSED | **0 EXEs on Desktop** — docs hub (SYSTEM_INSTRUCTIONS.md, LESSONS_MASTER.md, skills/). Real 52 EXEs at `G:/AZAZAEL_Standalone` |
| 25 | **Azazael_UNIFIED** | ❌ Deprecated | ORCHESTRATION_UNIFIED remnant only — archive candidate |
| 26 | **AZAZAEL_ARCHIVE** | 📦 Archive | 1 .py remnant |
| 27 | **FACEBOOK_UBUNTU_MIRROR** | ⚠️ Empty | 0 MB empty mirror dir |
| 28 | **Project Launchers** | ✅ Hub | launcher scripts |
| 29 | **scripts_archive / logs / __pycache__** | 🧹 Housekeeping | cleanup candidates |

### ✅ Archived to G: (no longer on Desktop)

| Project | Destination |
|---------|-------------|
| agent_system | `G:/Desktop_Archive/deprecated_projects/` |
| Azazael_UNIFIED | `G:/Desktop_Archive/deprecated_projects/` |
| CODEX | `G:/Desktop_Archive/deprecated_projects/` |
| CODEX_Studio_Output | `G:/Desktop_Archive/deprecated_projects/` |
| METAWORMS | `G:/Desktop_Archive/deprecated_projects/` |
| SysTools_JSON_Converter | `G:/Desktop_Archive/deprecated_projects/` |

---

## Statistics

| Metric | 2026-05-29 | 2026-07-30 | **2026-09-07** |
|--------|-----------|------------|----------------|
| Desktop dirs | 14 | 22 | **40** |
| run.py launchers | 8 | — | **7** |
| ✅ Operational | 3 | — | **12** |
| ⚠️ Partial/Repurposed | 5 | — | **3** |
| ❌ Deprecated on Desktop | 6 | — | **2** |
| EXEs on Desktop | 52 | 0 | **0** (52 on G:) |

---

## Priority Actions (Sep 7 re-audit)

### Done Since Original Audit
1. ✅ 6 deprecated projects archived to `G:/Desktop_Archive/deprecated_projects/`
2. ✅ AZAZAEL_Standalone EXEs relocated to `G:/AZAZAEL_Standalone` (52 verified)
3. ✅ EveUnleashed, PAMS, WSL_CrossExplorer, PerformanceMonitor all have working run.py
4. ✅ Learning-loop session work committed (a289ad6d, 74 files)

### Short-Term
5. Reconcile `Desktop/AZAZAEL_Standalone` — 0 EXEs but name implies the suite; add README pointing to `G:/AZAZAEL_Standalone`
6. Add run.py launchers to AOA, BCC, FACEBOOK, Libra for entry-point consistency
7. Update worm-count docs (77 → 136) and skill-count docs (1224)
8. Execute `LEARNING_LOOP_AUDIT_20260907.md`'s 8 improvement items (esp. AR-4 WSL monitor → live DB)

### Medium-Term
9. Archive `Graphify_Codebase_Atlas_2026-08-27` (21.3 GB) to G: — desktop space pressure
10. Clean empty/stale dirs: FACEBOOK_UBUNTU_MIRROR, Azazael_UNIFIED remnant, logs/, __pycache__
11. Complete Ultimate_Agent_Selector 3 stubs (code_generation, orchestrator, rl_learner)
12. Fix `evolution_cycle.py` champion_reeval/best_genes artifact mis-pairing (store champion_genes)

---

*Report updated from live filesystem verification + `FULL_PROJECT_AUDIT_2026-09-07.md`. Session `codebuff_20260907_233715_13888` recorded via DirectMemory.*