# MASTER_TASKS.md — Azazael Task Registry

> **Canonical registry of all active and completed tasks.** Updated July 8, 2026 (Session 8 — CLOSED).
> Cross-reference: LESSONS_MASTER.md, CODEBASE_AUDIT_TODO.md, SESSION_STARTUP.md
> **Mypy:** 261 errors / 84 files (down from 416, −155, 10 files graduated)
> **sync_all.py:** 6-environment bidirectional sync (Windows 11 + WSL2 Ubuntu + Desktop + G: source + G: AZAZAEL + Kali WSL2)

---

## Active Tasks (Incomplete)

| # | Task | Priority | Status | Owner |
|---|------|----------|--------|-------|
| T1 | Build all 39 standalone .exe targets via Nuitka 4.1.2 | P0 | Blocked (LNK2001 for 3.14t) | build_all_concurrent.py |
| T2 | Resolve Nuitka 3.14t free-threading linker errors (GEN_THRESHOLD, GEN_COUNT, GEN_INC_COUNT) | P0 | Needs investigation | Nuitka upstream |
| T3 | Run full concurrent build test (neural tier, both platforms) | P0 | Failed (0/12), needs Nuitka fix | build_all_concurrent.py |
| T4 | Expand build_all_concurrent.py to include all remaining targets from STANDALONE_BUILDS.md | P1 | Registry complete, build blocked | build_all_concurrent.py |
| T5 | Full project syntax audit (256 files) | P1 | Not yet run this session | py_compile |
| T6 | Worm registry integration test (77 worms, 17 categories) | P1 | Not yet run this session | worm_registry |
| T7 | Record all session actions via DirectMemory (canonical) | P0 | Pending | SOP Rule 5 |
| T8 | Delete temporary files from repo (_test_*.py, _trace_*.py, _tmp.py) | P2 | Check needed | Post-session cleanup |
| T9 | Update LESSONS_MASTER.md with Lessons #54-#61 (Tasks F, G, H) | P2 | 3 task-specific docs created, not yet merged to master | LESSONS_MASTER.md |
| T10 | Verify 0 function-body imports across ALL 256 .py files (not just WORMS/) | P2 | WORMS/ verified, full audit pending | Code audit |

---

## Completed Tasks (This Session)

| # | Task | Result | Date |
|---|------|--------|------|
| C1 | Investigate G: drive for rebuilt Nuitka 3.14t | 70+ builds confirmed, patch_nuitka_314t.py created | June 4 |
| C2 | Fix WSL2 Nuitka 4.1.2 installation | Reinstalled (was broken editable install) | June 4 |
| C3 | Create patch_nuitka_314t.py | docs/scripts/patch_nuitka_314t.py with --apply, --verify, --rollback | June 4 |
| C4 | Complete locking audit across all worm files | 10 fixes: learning.py (4), dreaming.py (2), evolution.py (2), NETWORK_DIAG.py (1), CODEX_TOOLS.py (1) | June 4 |
| C5 | Eliminate all function-body imports from WORMS/ | 37 imports eliminated across 7 files. Final: 0 remaining | June 4 |
| C6 | Create sync_all.py | 5-environment bidirectional sync with --status, --verify, --sync-all | June 4 |
| C7 | Create build_all_concurrent.py | 39-target concurrent Nuitka build orchestrator | June 4 |
| C8 | Create pre-commit hook | .git/hooks/pre-commit runs sync_all.py --verify | June 4 |
| C9 | Create ENVIRONMENT_ALIGNMENT.md | Permanent documentation of 5 environments | June 4 |
| C10 | Sync 76 files to WSL2 | expansion/, tests/, scripts/, docs/ synced | June 4 |
| C11 | Fix WSL2 sync destination bug | Source=/mnt/c, dest=/root/azazael (was both /mnt/c) | June 4 |
| C12 | Fix succeed→success typo | build_all_concurrent.py line 323 | June 4 |
| C13 | Create lessons for Tasks F, G, H | 3 enriched lesson documents created | June 4 |
| C14 | Create MASTER_TASKS.md | This file | June 4 |
| C15 | Fix METACLUSTER, CODEX_TOOLS, CROSS_NATURE_ROUTER function-body imports | 6 imports eliminated | June 4 |
| C16 | Fix NETWORK_DIAG.py except Exception→ImportError | Quality improvement | June 4 |

---

## Task Dependencies

```
C4 (locking audit) ──> C5 (import elimination) ──> C15 (final 3 files)
                                                        │
C6 (sync_all.py) ──> C11 (WSL2 fix) ──> C10 (sync 76 files)
        │
        └──> C8 (pre-commit hook)

C7 (build_all_concurrent.py) ──> C12 (typo fix) ──> T3 (neural tier test)
                                    │
                                    └──> T2 (LNK2001 — BLOCKED)
```

---

## Environment Status (as of July 8, 2026 — Session 8 Closed)

| Environment | Status | .py files | Skills | Docs |
|-------------|--------|-----------|--------|------|
| Windows 11 (primary) | OK | 486 | 132 | 47 |
| WSL2 Ubuntu-26.04 | OK (synced) | 481 | 132 | 47 |
| Desktop AZAZAEL_Standalone | OK | 0 | — | 47 |
| G: source-of-truth | OK (synced) | 479 | 132 | 47 |
| G: AZAZAEL_ROOT | OK (synced) | 635 | 132 | 47 |
| Kali WSL2 | ⚠️ Not initialized | 0 | — | 0 |

---

## Nuitka Status

| Platform | Python | Nuitka | Build Status |
|----------|--------|--------|-------------|
| Windows 11 | 3.14.6t | 4.1.2 | Builds progress to linking, fails with LNK2001 |
| WSL2 | 3.14.6t | 4.1.2 | Verified, not yet tested for build |

**Root cause of build failure:** Python 3.14 free-threading is only "experimentally supported" by Nuitka 4.1.2. C code generation cannot resolve certain module-level variables for free-threaded builds.

---

## Lesson Documents Created This Session

| Document | Domain | Lessons |
|----------|--------|---------|
| LESSONS_TASK_C_INSTRUMENTATION_FIX.md | `__setattr__` on instances doesn't work (CPython looks up on type) | 3 |
| LESSONS_TASK_D_NUITKA_BUILD.md | Nuitka build attempt, root cause, path forward | 5 |
| LESSONS_TASK_E_LOCKING_AUDIT.md | 17-file locking gap inventory, detection heuristic | 1 |
| LESSONS_TASK_F_ENVIRONMENT_ALIGNMENT.md | 5-environment topology, WSL2 path duality, sync patterns | 5 |
| LESSONS_TASK_G_CONCURRENT_BUILD.md | 39-target registry, LNK2001 diagnosis, build command construction | 6 |
| LESSONS_TASK_H_IMPORT_ELIMINATION.md | Complete 37-import elimination, final 3 files, code review fidelity | 3 |

**Total new lessons: 23** across 6 documents.

---

## Path Forward

1. **Mypy burndown:** Continue fixing CORE/ errors (261 remaining, 84 files). Next: pick top file from leaderboard.
2. **Immediate:** Resolve Nuitka 3.14t LNK2001 (contact Nuitka upstream or apply C-level patches)
3. **Short-term:** Run full syntax audit (256 files), worm registry test (77 worms)
4. **Short-term:** Record all session actions via DirectMemory (canonical)
5. **Medium-term:** Build all 39 targets concurrently once Nuitka is fixed
6. **Medium-term:** Merge 23 new lessons into LESSONS_MASTER.md
7. **Ongoing:** Run sync_all.py --sync-all after every session

---

## Session 5 (July 8, 2026) — Full Audit + Mypy Burndown

### Completed
- **C17**: Audit DISCLOSURE_WHITEPAPER_TODO.md — whitepaper corruption recovered (37MB→146K), 8 stale facts fixed
- **C18**: Mypy: learning_pipeline.py 51→0
- **C19**: Mypy: providers.py 43→0 (instance vars + dict typing)
- **C20**: Mypy: threading_utils.py 33→0 (type: ignore override/type-var)
- **C21**: sync_all.py bidirectional — added sync_wsl_to_windows(), sync_wsl_to_g(), --sync-to windows/g
- **C22**: Monitor worms re-audited — 4/6 pass WSL, 2 Windows-only confirmed
- **C23**: All docs synced to Windows + G: archives

### Mypy: 416→322 (−94, 6 files graduated, 94→89 files)

## Session 6 (July 8, 2026) — Mypy Burndown + sync_all.py WSL Fixes

### Completed
- **C24**: Mypy: audit_trail.py 22→0 (Optional annotations, dict typing, _uuid7 fix)
- **C25**: sync_all.py WSL fixes — get_env_status() + verify_integrity() work from WSL (IS_WSL detection, _resolve_path(), wsl_files())
- **C26**: sync_all.py --sync-all from WSL — 347 files to Windows + G: archives
- **C27**: All TODO docs updated: stale mypy counts, session numbers, sync features
- **C28**: Session milestone recorded in DirectMemory + session end

### Mypy: 354→344 (−10, 4th file graduated, −72 total from 416)

## Session 8 (July 8, 2026) — Mypy Burndown + Kali Integration + TODO Audit

### Completed
- **C29**: Mypy: REVERSE_TOOLS.py 19→0 (_pams no-redef, instructions + report annotations)
- **C30**: Mypy: doctor.py 17→0 (issues/report/sizes type annotations)
- **C31**: Mypy: WORM_FLEET.py 15→0 (typing imports, Optional[str] for root)
- **C32**: Mypy: learning.py 17→0 (no-redef, float() casts, .items() ignores) + NETWORK_DIAG.py 15→0 (_pams no-redef, dict annotations, rtts typing)
- **C33**: Kali added to sync_all.py — run_wsl_kali(), sync_wsl_to_kali(), get_env_status() probe, --sync-to kali, 5→6 environments
- **C34**: TODO audit — 22 stale references fixed across 6 docs
- **C35**: All changes synced to Windows + G: archives

### Mypy: 322→261 (−61, 5 files graduated, 10 total from 416)

---

*Last updated: June 4, 2026 — Environment realignment session*

## June 14, 2026 — Autodiff Suite Milestone

### Created
- **4 skills**: `azazael-autodiff-forward`, `azazael-autodiff-backprop`, `azazael-autodiff-gradient`, `azazael-autodiff-higher-order`
- **3 test files**: `test_autodiff_skills.py` (34/35 pass), `test_optimizers_convergence.py` (46/46 pass), `benchmark_autodiff_modes.py` (4 benchmarks)
- **SKILLS_CATALOG.md**: entries #55-58 with `auto_load: true`

### Mygrad 2.3.0 on 3.14.6t Free-Threading
- 4 limitations diagnosed: `.backward(seed)` on vectors, `.grad` property (no setter), `null_grad()` → None, `mg.tensor()` no kwarg
- Workarounds: auto-fallback to finite differences in `jacobian()`, slice assignment `p.grad[:] *= x` in `clip_gradients()`, None.grad guard in `jvp()`

### Test Coverage
- 115+ new tests added (34 autodiff skills + 46 optimizer convergence + 35 autodiff suite = 115+)
- Total standalone tests: ~415+ (was ~295)
- Architecture quality: 6.2 → 6.3 (+0.1)

---

## June 14, 2026 (Session 2) — Session Start

- DirectMemory session `codebuff_20260614_124931` initialized
- 38 stale sessions auto-closed
- SESSION_STARTUP.md updated with congruency marker
- CODEBASE_AUDIT_TODO.md v9 reflects autodiff suite status

### Mypy + Pyright Skills & Type Audit
- **2 skills created**: `azazael-mypy` (#59), `azazael-pyright` (#60) — `auto_load: true`
- **pyrightconfig.json** created — balanced strictness, excludes build artifacts
- **7 `__init__.py`** files added: `src/`, `AZAZAEL_TOOLKIT/`, `CODEX/CORE/`, `META/`, `ORCHESTRATION/BIBL/`, `SCRIPTS/`, `UTILITIES/PERSEPHONE/bin/`
- **3 indentation-critical files fixed**: `install_manager.py` (UnifiedInstaller), `rust_runner.py` (RustRunner), `go_runner.py` (GoRunner) — all method bodies were at class level
- **mypy**: 1,466 → 1,248 errors (-218, -14.9%)
- **pyright**: 1,976 → 1,224 errors (-752, -38.1% with pyrightconfig.json)
