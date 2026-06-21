# AZAZAEL PHASE 6+ TODO
## Generated: May 29, 2026 — Buffy/Codebuff Session

---

## Phase 6: Completed ✅

- [x] Create 8 CODEX/CORE deprecation shims (ANIMATION_PROTOCOLS, CHANGELOG_GENERATOR, ECOSYSTEM_HEALTH_CHECK, enrichment_display, FILE_MANIFEST_GENERATOR, HORUS_INTEGRATION, matrix_animation, QL_FILE_OPTIMIZER)
- [x] Compare all 8 pairs (3 identical, 5 stale) and verify 0 import references
- [x] Analyze 4 external Desktop projects (EveUnleashed_Selector, PerformanceMonitor, Ultimate_Agent_Selector, agent_system)
- [x] Create PATH_FORWARD.md comprehensive separation plan
- [x] Create 3 new skills (azazael-dedup, azazael-shims, azazael-separation)
- [x] Update PAMS records (MEMORIES.md, ERROR_LOG.md, SESSION_INSIGHTS)
- [x] Validate (292 files syntax-clean, all 8 shims import verified)
- [x] Code review

---

## Phase 7: Remaining Runtime Hardcoded Paths (12 files) ✅ COMPLETED May 29

- [x] CODEX/VIDEOS/create_dual_pane_video.py — 2 output paths + missing Path import → Path(__file__).parent
- [x] CODEX/TESTING/conftest.py — 1 ECOSYSTEM_ROOT → Path.home() / "Desktop"
- [x] CODEX/TESTING/UNIT/test_wormz.py — 1 sys.path.insert → __file__ resolution to src/
- [x] CODEX/TESTING/UNIT/test_metaworms.py — 2 (sys.path.insert + assertion) → __file__ resolution + str(folder)
- [x] CODEX/TESTING/UNIT/test_hydra.py — 1 sys.path.insert → __file__ resolution to src/
- [x] CODEX/TESTING/PERFORMANCE/test_performance.py — 2 (sys.path.insert + default arg) → __file__ resolution + None sentinel
- [x] CODEX/TESTING/INTEGRATION/test_ecosystem_integration.py — 1 sys.path.insert → __file__ resolution to src/
- [x] ORCHESTRATION/scripts/azazael_cli.py — 6 (ROOT, SHORTY, 4 sub-cmds) → Path(__file__).parent.parent, Path.home()/Desktop, internal project paths
- [x] ORCHESTRATION/scripts/bat_analysis.py — 1 base_path → Path.home() / "Desktop" / "SHORTY"
- [x] ORCHESTRATION/scripts/web_dashboard.py — 4 paths dict entries → computed from __file__ and Path.home()
- [x] ORCHESTRATION/ml_platforms/improvements/metrics_tracker.py — 1 base_path default → None sentinel with Path(__file__) fallback
- [x] CORE/WORMS/WORMZ_POPUP.py — 1 cmd path → Path(__file__).resolve().parent / "WORMZ.py"

**Session total: 63 hardcoded paths fixed across 43 files. 292 files syntax-clean.**

---

## Phase 8: Split ECOSYSTEM_EXPANSION.py

- [ ] Count worms per category (already done: 50 worms, 10 categories)
- [ ] Create CORE/WORMS/expansion/ directory
- [ ] Split into category files: expansion_orchestration.py, expansion_utility.py, expansion_diagnostic.py, etc.
- [ ] Create ECOSYSTEM_EXPANSION.py as re-export shim
- [ ] Test worm registry discovers all 50 worms from new files

---

## Phase 9: Extract CORE/ as Standalone Package

- [ ] Create azazael-core/ directory with pyproject.toml
- [ ] Copy CORE/*.py to azazael-core/azazael_core/
- [ ] Remove 157 sys.path.insert hacks → proper package imports
- [ ] pip install -e azazael-core
- [ ] Update all consumers: from CORE.X → from azazael_core.X
- [ ] Test worm registry still works

---

## Phase 10: Remove Deprecation Shims

- [ ] Verify 0 remaining imports to META/* shims
- [ ] Verify 0 remaining imports to CODEX/CORE/* shims
- [ ] Verify 0 remaining imports to HYDRA/ml_platforms/* shims
- [ ] Delete all 13 shim files
- [ ] Clean up MEMORIES.md shim table

---

## Phase 11: Extract Root Modules as azazael-worms

- [ ] Move 17 root .py files to azazael-worms package
- [ ] Move CORE/WORMS/ to azazael-worms/worms/
- [ ] Create deprecation shims for old locations
- [ ] Test all 77 worms register and execute

---

## Phase 12: Extract ORCHESTRATION + HYDRA

- [ ] Merge ORCHESTRATION/ and HYDRA/ into azazael-orchestration
- [ ] Remove HYDRA/ml_platforms/ (already shimmed)
- [ ] Fix cross-imports
- [ ] Test HYDRA cluster + TARBABY + HORUS

---

## Phase 13: Extract CODEX as azazael-codex

- [ ] Move CODEX/ to azazael-codex
- [ ] Remove CODEX/CORE/ shims (already pointing to root)
- [ ] Fix remaining test hardcoded paths
- [ ] Test video generation, documentation, comprehensive analysis

---

## Phase 14: Desktop Project Integration (Optional)

- [ ] Evaluate EveUnleashed_Selector + azazael-core integration
- [ ] Evaluate PerformanceMonitor + azazael-core metric telemetry
- [ ] Evaluate Ultimate_Agent_Selector + AgentPool integration
- [ ] Evaluate agent_system as new agent implementation framework

---

## Remaining Dedup Opportunities

- [ ] Audit AZAZAEL_TOOLKIT/ duplicates (4 pairs — likely intentional packaging)
- [ ] Audit CODEX/SESSION_TEMPLATE/ duplicates (4 pairs — nested directory)
- [ ] Audit ORCHESTRATION/HYDRA/ remaining duplicates (1 pair — harness.py)
- [ ] Audit any new duplicates introduced during refactoring

---

## DB Integration Session (June 2, 2026)

### Accomplished
- [x] PostgreSQL adapter: CORE/postgres_memory.py — full API parity with LocalMemoryStore
- [x] DatabaseMonitorWorm: health checks, alerts, thresholds, continuous monitoring
- [x] ScheduledDbMonitorWorm: hourly scheduled DB health pipeline
- [x] CLI dashboard `--db-monitor` flag with live health snapshot
- [x] Web dashboard DB Monitor card with live HTML rendering
- [x] Store injection pattern for test isolation
- [x] 15 PostgreSQL integration tests (test_postgres_memory.py)
- [x] 30+ worm unit tests with isolated temp stores (test_db_monitor_worm.py)
- [x] Chrome confirmed available for browser-use agent

### New worms registered
- DatabaseMonitorWorm (monitor, p=6, cd=60s)
- ScheduledDbMonitorWorm (monitor, p=6, cd=120s)

---

## 🚨 3.14t-ONLY PREREQUISITES (Every Session)

### Build Readiness
- [ ] **Python 3.14t is default**: `python -c "import sys; print(sys.version)"` → `3.14.5`
- [ ] **Nuitka patches applied**: `python azazael/docs/scripts/patch_nuitka_314t.py --apply`
- [ ] **Patch verification**: `python azazael/docs/scripts/patch_nuitka_314t.py --verify`
- [ ] **psutil working**: `python -c "import psutil; print('OK:', psutil.cpu_count())"`
- [ ] **No Python 3.13 references**: Do not use `python313`, `Python313`, or `Python 3.13`
- [ ] **Build commands use `python`** (not `Python313/python.exe`)

### Documentation
- [ ] All docs/skills say "Python 3.14t" — never "Python 3.13"
- [ ] TODO items reference 3.14t only
- [ ] Error logs don't recommend 3.13 as a fallback

---

## Validation Checklist (Every Session)

- [ ] Full syntax check: 300+ files, 0 failures
- [ ] Import test: all 13 shims resolve
- [ ] No new hardcoded paths introduced
- [ ] No new duplicate files created
- [ ] PAMS updated (MEMORIES.md, ERROR_LOG.md, SESSION_INSIGHTS)
- [ ] Lessons added to `LESSONS_MASTER.md` (see [LESSONS_MASTER.md](LESSONS_MASTER.md))
- [ ] Temp files cleaned up
- [ ] Code review completed
- [ ] 3.14t-only rules verified (no 3.13 refs)
- [ ] `patch_nuitka_314t.py` applied if building .exe

---

*Total estimated effort: Phase 7 (2-4h), Phase 8 (3-6h), Phase 9-13 (20-40h), Phase 14 (8-16h)*
