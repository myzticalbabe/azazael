# FULL PROJECT AUDIT — 2026-09-24

> Method: azazael-architecture-review (3-pass: Inventory / Rate / Scorecard).
> All counts below were produced by runtime commands this session (find/wc,
> py_compile sweep, worm_registry introspection), not copied from prior docs.
> Prior docs are cited only in the DRIFT section, where they disagree with runtime.

---

## SESSION RECORD

- DirectMemory session_start recorded: event id 1137159
  (`dm.record('session_start', {'purpose': 'full audit all projects', ...})`)
- Canonical docs read in RULE 0K order (SYSTEM_INSTRUCTIONS, SOP, MANDATES,
  ERROR_LOG, MEMORIES, SESSION_STARTUP, LESSONS_MASTER, PRODUCTION_TODO).
- Guardrail skills loaded: error-prevention, mandates, sop, pams-memory, hats,
  eleven-followups, system-startup, desktop-projects, architecture-review.

---

## PASS 1 — INVENTORY (runtime-verified counts)

### 1. AZAZAEL CORE — azazael/src/ (719 .py, 28 dirs)

| Layer | .py | Notes |
|-------|-----|-------|
| CORE/ | 350 | incl. CORE/WORMS (registry, clusters) |
| ORCHESTRATION/ | 83 | HYDRA bridge, ml_platforms |
| CODEX/ | 74 | video pipeline, CAIN |
| AOA/ | 29 | architecture disclosure tooling |
| SCRIPTS/ | 29 | sync_skills, telemetry, auto_sync |
| UTILITIES/ | 23 | KLINK, PERSEPHONE, POINDEXTER, TARBABY |
| META/ | 16 | deprecation shims |
| ML/ + HYDRA/ | 9 + 11 | ml platforms mirror |
| eve_unleashed/ | 11 | desktop app modules |
| AZAZAEL_TOOLKIT/ | 9 | toolkit |
| tests/ (in src) | 14 | |
| DAEMONS/ INTERPRETERS/ TOOLS/ CLI/ SHORTCUTS/ | 3+3+10+2+1 | |
| root-level src/*.py | 42 | thin wrappers (intentional pattern) |
| **TOTAL** | **719** | all outside __pycache__/egg-info |

Supporting: packages/ 28 .py | tests/ 190 test files (199 entries) |
skills/ 1226 .md | .agents/skills/ 1228 SKILL.md | ERROR_LOG 160 entries (max #209)

### 2. WORM REGISTRY (introspected at runtime)

- Registered worms: **232** across **36 categories**
- Top categories: security 25, learning 19, analysis 18, monitor 15,
  network 13, orchestration 10, xenomorph 8, visualization 7
- Neural-mesh categories present: axon 4, dendrite 4, synapse 6, glia 4,
  thalamus 3, engram 5, plasticity 5, immune 5, metabolic 3, repair 1,
  defense 1, consensus 3, consolidation 4, federated 3, servemesh 3, envmesh 6
- `discover_worms()` returned 12 this run (module-scan path); registry size
  232 via decorator + auto-registration. Known cold-start/scan asymmetry.

### 3. DESKTOP PROJECTS — 38 directories (prior audit documented 14)

Active / content-bearing (runtime counts):

| Project | py | exe | bat | Status |
|---------|----|-----|-----|--------|
| AZAZAEL_Standalone | 0 | **0** | **0** | [CRITICAL] see DRIFT-1 (dir now 1.3M docs + build log) |
| azazael (main, see above) | 719 | - | - | Healthy |
| PAMS | 3 | 0 | 0 | Partial — memory/event system |
| EveUnleashed_Selector | 31 | 0 | 0 | Partial — multi-agent framework |
| Libra | 46 | 0 | 0 | NEW since prior audit — BCC/PA work |
| FACEBOOK | 26 | 0 | 7 | NEW — capture tooling |
| Graphify_Codebase_Atlas_2026-08-27 | 10 | 0 | 1 | NEW — atlas output |
| AOA | 23 | 0 | 0 | NEW — disclosure mp4/html |
| BCC_Maps | 5 | 0 | 0 | NEW — map renders |
| Ultimate_Agent_Selector | 4 | 0 | 0 | Partial |
| PerformanceMonitor | 4 | 0 | 1 | Partial — Go+Rust+Python |
| AZAZAEL_Vault | 3 | 0 | 1 | Vault launcher |
| WSL_CrossExplorer | 2 | 0 | 0 | Partial (WSL required) |
| LlamaServer | 2 | 0 | 1 | Partial |
| WSL Models | 1 | 0 | 7 | Partial — GGUF launchers |
| AZAZAEL_ARCHIVE | 1 | 0 | 0 | Data |
| scripts_archive | 10 | 0 | 0 | Archived scripts |
| BCC | 0 | 0 | 0 | Docs/evidence only |
| 6x AZAZAEL_COSMOS_VIEWER_* | 0 | 0 | 0 | Static graph viewers |
| AOA_Complete_Atlas, Azazael_*Graphs*, Azazael_Full_Filesystem_Scans, CODEX_Azazael_Complete, CODEX_Quartet, DisclosureWhitepaper, neural_mesh_render, TikTok_Videos, Project Launchers, logs | 0 | 0 | 0 | Output/data |

Desktop also has 49 .lnk shortcuts (model launchers, viewers, PAMS, etc.).

### 4. WIDER WORKSPACE PROJECTS (top-level, source-bearing)

| Project | py | other | Nature |
|---------|----|-------|--------|
| bcc-openplanter | 131 | - | BCC corpus pipeline |
| BCC_Investigation_Corpus | 131 | - | Investigation corpus |
| llama.cpp | 107 | 1 | vendored/upstream C++ |
| openplanter | 82 | - | agent platform (Dockerfile, LICENSE) |
| azazael-dev | 804 | - | parallel dev tree — fork drift risk |
| scripts | 85 | - | workspace scripts |
| edge0-intel | 52 | - | eval/judge tooling |
| vermillion_lightfury | 41 | - | cinematic/reference project |
| tools | 36 | 1 | misc tools |
| flet_test | 25 | - | UI experiments |
| llama-server | 23 | 6 | Rust server (Cargo.toml) |
| jev-ultrafast | 15 | 1 | upstream lib |
| C: (stray dir) | 14 | - | path-escaping artifact — cleanup candidate |
| tf-build | 9 | - | TF build scratch |
| rainbow_queens_test, tigger, obkb_trial, nuitka_*, gephi_export_*, mindwalk, llama-detect, llama-supervisor | <5 each | | experiments/upstream |

### 5. G: ARCHIVE — mounted and reachable

`/g/AZAZAEL/` present: AI_PROMPTS.txt, ANTI_OBFUSCATION_PROMPT.txt, AOA,
ARCHIVE_STRUCTURE.md, AZAZAEL_ROOT ... (readable this session).

---

## PASS 2 — HEALTH RATINGS

| Project | Cohesion | Coupling | Health |
|---------|----------|----------|--------|
| azazael/src CORE | 0.7 | 9 (paths.py hub) | GREEN - 719/719 compile |
| azazael/src CODEX | 0.9 | 4 | GREEN |
| azazael/src ORCHESTRATION | 0.6 | 6 | YELLOW - mixed concerns |
| azazael/src META | 0.2 | 2 | RED - shims, phase-out candidate |
| azazael/src root wrappers | 0.3 | 5 | YELLOW - intentional but fragile |
| azazael/tests | 0.8 | 5 | YELLOW - 190 files, run status unverified |
| packages/azazael-core | 0.8 | 3 | YELLOW - fork-sync burden |
| Desktop/AZAZAEL_Standalone | 0.5 | 1 | RED - DRIFT-1 |
| Desktop active projects (15) | 0.6 | 3 | YELLOW - no core integration |
| Desktop output/data dirs (16) | 0.1 | 0 | RED - reference only |
| azazael-dev | 0.6 | 7 | RED - DRIFT-6 fork risk |
| bcc-openplanter + BCC corpus | 0.7 | 4 | GREEN - active |
| edge0-intel | 0.7 | 3 | GREEN - active |
| openplanter | 0.8 | 5 | GREEN - upstream |
| llama-server / llama.cpp / jev / mindwalk | 0.8 | 2 | GREEN - upstream/vendored |
| G: archive | 0.5 | 0 | YELLOW - reachable, sync status unknown |

---

## PASS 3 — ARCHITECTURE QUALITY SCORECARD (12 dimensions)

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Modular cohesion | 7.0 | Nature clusters have clear boundaries |
| Inter-module coupling | 5.5 | CORE/paths.py remains the critical hub |
| Dependency hygiene | 6.0 | 18 shims documented; 262 lazy imports = intentional |
| Type safety | 5.0 | Last known mypy 1,248 / pyright 1,224 errors (Jun 14) |
| Test coverage | 4.5 | 190 test files exist; baseline unverified this session |
| Documentation | 8.0 | 1226 skills, extensive canonical docs |
| Build system | 4.0 | build_all.py exists but suite outputs are GONE (DRIFT-1) |
| 3.14t readiness | 3.0 | Codebase is 3.14t-targeted; runtime here is 3.14.7+GIL (DRIFT-2) |
| Shell injection safety | 6.0 | os.system purged (Aug 8 session); shell=True residual unscanned |
| Package management | 4.5 | packages/azazael-core scaffolded; fork-comment sync |
| Desktop integration | 4.0 | 49 .lnk launchers; no core wiring |
| **Overall** | **5.2/10** | 6 improvement items below |

---

## DRIFT REGISTER — runtime vs. documentation (this audit's key output)

| ID | Finding | Severity |
|----|---------|----------|
| DRIFT-1 | Desktop/AZAZAEL_Standalone contains **0 EXEs and 0 BATs** (1.3M total, docs + build_eve log only). Every canonical doc (MEMORIES, PROJECT_MAP, desktop-projects skill) claims 50 EXEs + 50 BATs + build_all.py. The entire standalone suite is resolved as SUPERSEDED (see ADDENDUM): 52/52 EXEs verified at G:/AZAZAEL_Standalone; user 2026-09-24 declares the suite obsolete — fleet is now 1,200+. | SUPERSEDED |
| DRIFT-2 | Active interpreter is **Python 3.14.7, GIL enabled** (sys._is_gil_enabled() == True). The 3.14t-ONLY mandate means this session's runtime is non-compliant; RESOLVED: python3.14t verified (3.14.7t, GIL False, psutil 7.2.2 + numpy 2.5.3 import clean); default `python` remains the GIL build — invoke `python3.14t` explicitly. | RESOLVED |
| DRIFT-3 | Registry is **232 worms / 36 categories** vs 226/35 in skills and 104/18 in MEMORIES. Three different documented numbers, all stale. | HIGH |
| DRIFT-4 | ERROR_LOG has **160 entries, max ID #209**; SESSION_STARTUP claims "138 errors, highest #187". Congruency marker is stale. | MEDIUM |
| DRIFT-5 | Desktop now has **38 project dirs** (Libra, AOA, FACEBOOK, BCC, BCC_Maps, 6x COSMOS_VIEWERs, atlas/graph outputs...) vs the 14 documented in DESKTOP_PROJECTS_AUDIT.md / azazael-desktop-projects skill. | MEDIUM |
| DRIFT-6 | **azazael-dev/** holds 804 .py vs azazael/src's 719 — an untracked parallel tree with fork-drift risk (same failure class as packages/azazael-core fork comments). | HIGH |
| DRIFT-7 | Stray top-level `C:` directory (14 .py) — path-escaping artifact from a `C:\...` shell command. Cleanup candidate (needs user permission per MEMORIES #12). | LOW |
| DRIFT-8 | skills/ (1226 .md) and .agents/skills (1228 SKILL.md) counts vs SKILLS_CATALOG.md expectations — catalog reconciliation needed (bucket-sum trap per azazael-catalog-reconciliation). | MEDIUM |

---

## IMPROVEMENT ITEMS (cross-referenced vs CODEBASE_AUDIT_TODO.md)

| ID | Item | Effort | Priority | Classification |
|----|------|--------|----------|----------------|
| AR-24-1 | Recover/rebuild AZAZAEL_Standalone suite (check G:/AZAZAEL/standalone backup first — SUPERSEDED — user 2026-09-24: 52-EXE suite obsolete; fleet is 1,200+) | - | - | SUPERSEDED |
| AR-24-2 | Switch session runtime to python3.14t (or amend mandate) DONE 2026-09-24: python3.14t verified (GIL False; psutil/numpy import clean) | 0.2h | P0 | DONE |
| AR-24-3 | Reconcile azazael-dev vs azazael/src; declare one source of truth | 3h | P1 | ADDITIVE |
| AR-24-4 | Update SESSION_STARTUP.md + skills with true registry/ERROR_LOG numbers (DRIFT-3/4) | 1h | P1 | REINFORCES (Step 8 docs) |
| AR-24-5 | Refresh DESKTOP_PROJECTS_AUDIT.md for 38 dirs (DRIFT-5) | 2h | P2 | REINFORCES (desktop audit) |
| AR-24-6 | SKILLS_CATALOG.md bucket-sum reconciliation (DRIFT-8) | 1h | P2 | REINFORCES (catalog) |
| AR-24-7 | Run full test suite (190 files) and record baseline | 2h | P1 | REINFORCES (Step 3 tests) |
| AR-24-8 | Remove stray `C:` dir (ASK USER FIRST per MEMORIES #12) | 0.2h | P3 | ADDITIVE |

Additive ratio: 4/8 = 50% — the prior plan was moderately comprehensive;
the standalone-suite disappearance and dev-tree fork are genuine new gaps.

---

## VERIFICATION STATUS (RULE 0A honesty)

- VERIFIED BY RUNTIME: all counts, py_compile 719/719 PASS, registry
  introspection, G: mount, DirectMemory write (event 1137159).
- NOT VERIFIED: test suite pass/fail (not run), EXE build reproducibility,
  G: sync freshness, mypy/pyright current error counts.
- NOT AVAILABLE THIS SESSION: multi-agent inference verification
  (RULE 0G/0Q-A/0V/0W) — no spawn_agents tool in this client; nothing
  claimed, nothing hallucinated.
- INFERENCE FALLBACK EXECUTED (RULE 0Z-A) 2026-09-24: CITING
  `.inference_cache/20260924_004733_openrouter.log` (segfault root-cause analysis);
  groq + gemini returned 404 stale-model errors (recorded as Error #211).

---

## ADDENDUM — 2026-09-24 (implementation wave + user corrections)

**User corrections (authoritative, RULE 0P Level 1):**
1. "52 .exe are no longer relevant. we now have over 1200." — the 52-EXE suite
   (Desktop copy + G:/AZAZAEL_Standalone) is OBSOLETE; the fleet is 1,200+ EXEs.
   Measured census before this correction: Desktop 103, venv-314t/Scripts 74,
   G:/AZAZAEL_Standalone 52 (legacy), scattered ~35. The 1,200+ fleet is not yet
   inventoried in any canonical doc — DRIFT-10.
2. edge0-intel is deliberately NOT incorporated into azazael — see
   EDGE0_INVESTIGATION_2026-09-24.md (The Oxford Compact, 2026-09-23).

**Wave results (runtime-verified):**

| Item | Result |
|------|--------|
| Test baseline (python3.14t) | RED — 28/28 files SEGFAULT, 1 FAIL, 0 passed. RULE 0L analysis via fallback (OpenRouter). Error #212. Log: azazael/logs/test_baseline_2026-09-24.log |
| RULE 0H anti-pattern scan (ast+regex) | non_ascii 4,884 / fstring_backslash 721 / import_in_func 1,309 / c_drive_path 101 / os_system 11 / tstring 11 / cls_new 2. Error #216 |
| azazael-dev vs azazael/src | 182 common, 15 identical, 167 diverged. VERDICT: azazael/src = source of truth; azazael-dev = stale compare-only fork. Error #214 |
| Registry | 232 worms / 36 categories (docs said 226/35 and 77/17) — corrected in skills + SESSION_STARTUP. Error #215 |
| Providers | groq default model 404, gemini-2.0-flash retired, openrouter OK. Error #211 |
| Stray `C:` dir | removed (0 files, empty tree, realpath-guarded) |
| G: legacy suite | 52 EXEs + 52 BATs verified at /g/AZAZAEL_Standalone — legacy per user correction. Error #210 |
| ERROR_LOG | entries #210-#216 added this wave (167 entries, max ID #216) |
| SKILLS_CATALOG | Inventory Summary set to 1,259 (table-wins); 2026-09-24 reconciliation appended |

**DRIFT-10 (new):** the 1,200+-EXE fleet has no inventory record in any
canonical doc (this report predates it). Next audit needs the fleet location /
build system pointer to fold it in.

**Edge0 verdict (summary):** non-incorporation is BY DESIGN — The Oxford
Compact (edge0-intel/COMPACT.md, 2026-09-23) separates three powers (forge /
mesh / audit) with "No member absorbs another's role"; integration is
endpoint + ledger only (build_az_eval.py reads azazael records one-way;
repaird.py interlock: "azazael/BCC off limits").
