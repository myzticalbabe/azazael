# Project Alignment Assessment — Azazael Ecosystem

> Generated: June 4, 2026
> Purpose: Determine alignment of all projects across 10 critical dimensions.
> Methodology: Cross-reference PROJECT_MAP.md, PATH_FORWARD.md, AZAZAEL_ARCHITECTURE_ANALYSIS.md,
>             CODEBASE_AUDIT_TODO.md, SKILLS_CATALOG.md, SYSTEM_INSTRUCTIONS.md, azazael.yaml

---

## Executive Summary

**Overall alignment rating: 6.5/10**

The Azazael ecosystem shows strong alignment in core technical dimensions
(Python version, build system, 3.14t readiness) but significant misalignment
in project governance, documentation consistency, and production readiness.

| Dimension | Score | Trend | 
|-----------|-------|-------|
| Python version alignment | 9.5/10 | 🟢 Strong |
| Architecture/pattern alignment | 6.5/10 | 🟡 Improving |
| Dependency flow alignment | 5.5/10 | 🔴 Bottlenecked |
| Path resolution alignment | 7.0/10 | 🟡 12 runtime paths remain |
| Documentation alignment | 5.5/10 | 🔴 Multiple docs inconsistent |
| Build system alignment | 7.5/10 | 🟢 Good (Nuitka pipeline) |
| Testing alignment | 4.5/10 | 🔴 Fragmented |
| Convention alignment | 6.0/10 | 🟡 Improving (mypy rounds) |
| Skills/documentation alignment | 5.0/10 | 🔴 Virtual vs on-disk gap |
| Production readiness alignment | 4.0/10 | 🔴 Wide variance |
| **Overall** | **6.5/10** | 🟡 |

---

## Dimension 1: Python Version Alignment — 9.5/10

### Assessment
All projects in the ecosystem are aligned on **Python 3.14.5t** (free-threading).

| Project | Python Version | Status |
|---------|---------------|--------|
| azazael CORE (src/) | 3.14.5t | ✅ Mandated by SYSTEM_INSTRUCTIONS.md |
| Desktop Standalone Suite (52 EXEs) | 3.14.5t (Nuitka built) | ✅ All *_314t.exe naming |
| packages/azazael-core | 3.14t | ✅ pyproject.toml requires 3.14+ |
| EveUnleashed_Selector | 3.11+ | ⚠️ MISALIGNED — still on 3.11 |
| PerformanceMonitor | 3.14t + Go + Rust | ✅ Python portion aligned |
| Ultimate_Agent_Selector | 3.14t + Go + Rust | ✅ Python portion aligned |
| LlamaServer | Rust (standalone) | ✅ Not Python-dependent |
| PAMS | 3.10+ | ⚠️ MISALIGNED — still on 3.10 |
| CODEX (Desktop) | 3.14t | ✅ |
| agent_system | 3.10+ | ⚠️ MISALIGNED — skeletal, on 3.10 |

**Gaps:**
- EveUnleashed_Selector (3.11+) and PAMS (3.10+) still reference older Python versions
- agent_system is skeletal and explicitly on 3.10+
- 4 of 14 Desktop projects don't explicitly state 3.14t alignment

**Alignment rule:** SYSTEM_INSTRUCTIONS.md Rule 3.14t-1 mandates 3.14t exclusively.
No Python 3.13 is used anywhere. The 3.11/3.10 references in Desktop projects are
from old project scaffolding, not actively enforced.

---

## Dimension 2: Architecture/Pattern Alignment — 6.5/10

### Assessment
The monorepo (src/) has strong internal architectural patterns but external
Desktop projects follow their own conventions.

**Well-aligned layers (within monorepo):**
| Pattern | Used By | Alignment |
|---------|---------|-----------|
| Worm registry (`@register_worm`) | CORE/WORMS/, expansion/ | ✅ All 79 worms |
| Nature clusters (CLUSTERWORMS, METACLUSTER) | CORE/WORMS/ | ✅ Cluster system unified |
| Dynamic path resolution (`CORE/paths.py`) | CORE/, ORCHESTRATION/, root modules | ✅ 139+ consumers |
| Free-threading patterns (FreeThreadPool) | CORE/, tests/ | ✅ All 3.14t-threaded |
| Double-checked locking | CORE/WORMS/ (12 files) | ✅ Unified lazy-init pattern |
| Conditional import fallbacks (`try/except`) | CORE/Agent.py, MemoryBus.py, etc. | ✅ Standardized with type:ignore |

**Misaligned layers:**
| Pattern | Monorepo | Desktop Projects | Gap |
|---------|----------|-----------------|-----|
| Module structure | Package-based (`from CORE.X import`) | Script-based (`run.py`) | ⚠️ Different philosophies |
| Error handling | Structured (ERROR_LOG.md, circuit breaker) | Ad-hoc print() statements | 🔴 Major gap |
| Configuration | Centralized (azazael.yaml) | Per-project config files | 🔴 No unified config |
| Testing | ~295+ standalone tests | Minimal/no tests | 🔴 Desktop projects untested |
| Logging | Structured (azazael_logging.py, MemoryBus) | print() statements | 🔴 No logging standard |

**Architecture anti-patterns found:**
1. **Root *.py files** (30+ standalone entry points) — no consistent pattern, varying quality
2. **META/** directory (13 deprecation shims) — should be deleted, still accumulating
3. **CODEX/CORE/** — 8 shims remain, plus 4 unique files with no root counterpart
4. **Root-level `sys.path.insert(0, ...)`** — 157+ instances preventing clean package extraction

---

## Dimension 3: Dependency Flow Alignment — 5.5/10

### Assessment
Dependencies flow through CORE/paths.py and CORE/worm_registry.py as a hub, creating
a star topology that is both the system's strength and its bottleneck.

```
Expected dependency flow (from PATH_FORWARD.md):
    CORE/ (stdlib only)
      ↑
    CORE/WORMS/ ← CORE
      ↑
    ORCHESTRATION/ ← CORE, HYDRA, META
      ↑
    CODEX/ ← CORE, ORCHESTRATION
      ↑
    Root modules ← CORE
      ↑
    Desktop projects → Standalone (no CORE dependency)
```

**Alignment issues:**
| Issue | Detail | Impact |
|-------|--------|--------|
| CORE/paths.py bottleneck | 139+ inbound deps | 🔴 Single failure point |
| CORE/worm_registry.py coupling | 77+ inbound deps (all worms) | 🟡 Any API change breaks all worms |
| META/ shims | 13 files re-exporting from root | 🔴 Dead code, confuses dependency analysis |
| CODEX/CORE/ shims | 8 files re-exporting from root | 🔴 Same issue |
| Desktop projects | 0 depend on CORE (by design) | 🟢 Good — true independence |
| 4 circular import chains | Between CORE modules | 🔴 Refactoring risk |
| 157+ sys.path.insert | In root modules and scripts | 🔴 Prevents clean package extraction |

---

## Dimension 4: Path Resolution Alignment — 7.0/10

### Assessment
The `CORE/paths.py` system provides centralized dynamic path resolution,
but ~12 runtime hardcoded paths remain in source files.

**Aligned modules (using CORE/paths.py):**
- CORE/ — all modules use `from CORE.paths import get_*`
- ORCHESTRATION/ — fixed in Phase 22 (8 scripts updated)
- Root modules — fixed in Phase 5 (37+ absolute paths eliminated)
- META/ — all shimmed, no hardcoded paths

**Misaligned files (still have hardcoded paths — from PATH_FORWARD.md):**
| File | Paths | Type |
|------|-------|------|
| CODEX/VIDEOS/create_dual_pane_video.py | 1 output path | Runtime |
| CODEX/TESTING/conftest.py | 1 ECOSYSTEM_ROOT | Test fixture |
| CODEX/TESTING/UNIT/test_*.py | 3 sys.path.insert | Tests |
| CODEX/TESTING/PERFORMANCE/test_performance.py | 1 sys.path.insert | Test |
| CODEX/TESTING/INTEGRATION/test_ecosystem_integration.py | 1 sys.path.insert | Test |
| ORCHESTRATION/scripts/azazael_cli.py | 1 ROOT Path | Runtime |
| ORCHESTRATION/scripts/bat_analysis.py | 1 base_path | Runtime |
| ORCHESTRATION/scripts/web_dashboard.py | 1 Root dict | Runtime |
| ORCHESTRATION/ml_platforms/improvements/metrics_tracker.py | 1 init default | Runtime |
| CORE/WORMS/WORMZ_POPUP.py | 1 cmd list | Runtime |
| **Total runtime** | **12 paths** | **Needs fixes** |

Additionally, ~15 documentation/metadata paths exist in CODEX/comprehensive/
that are safe (documentation only, not executed).

---

## Dimension 5: Documentation Alignment — 5.5/10

### Assessment
Documentation is fragmented across 5+ documents with inconsistent coverage.

| Document | Scope | Last Updated | Alignment Issue |
|----------|-------|-------------|-----------------|
| PROJECT_MAP.md | Complete ecosystem inventory | May 29, 2026 | 🟡 Stale — EXE count 52 (doc says 51) |
| PATH_FORWARD.md | Separation plan | June 1, 2026 | 🟡 Separation plan not yet actioned |
| AZAZAEL_ARCHITECTURE_ANALYSIS.md | Architecture efficiency | June 4, 2026 | 🟢 Current |
| CODEBASE_AUDIT_TODO.md | Production plan (primary) | June 4, 2026 | 🟢 Current |
| PRODUCTION_TODO.md | Original gaps (superseded) | June 3, 2026 | 🔴 Stale — should be archived |
| REWRITE_TODO.md | Rewrite plan (legacy) | May 28, 2026 | 🔴 Stale — should be archived |
| PHASE_6_TODO.md | Phase tasks (legacy) | May 29, 2026 | 🔴 Stale — should be archived |
| MEMORIES.md | Anti-patterns, architecture | June 4, 2026 | 🟢 Current |
| ERROR_LOG.md | Error ledger (55 entries) | June 4, 2026 | 🟢 Current |
| SYSTEM_INSTRUCTIONS.md | SOP, 3.14t rules | June 3, 2026 | 🟢 Current |
| LESSONS_MASTER.md | Lessons (44 + template) | June 4, 2026 | 🟢 Current (just improved) |
| SKILLS_CATALOG.md | Skills index (36 entries) | Updated June 4 | 🟢 Current |

**Key misalignments:**
1. **3 of 4 TODO documents are stale** — PRODUCTION_TODO.md still actively referenced
   despite being superseded by CODEBASE_AUDIT_TODO.md
2. **PROJECT_MAP.md EXE count wrong** — says 51 EXEs, actual is 52
3. **SKILLS_CATALOG.md** — lists 36 skills, only 19 exist on disk (17 virtual)
4. **Desktop projects** — no consistent documentation format (8 loose .md files on Desktop)
5. **Lessons reference "47 lessons"** in SYSTEM_INSTRUCTIONS.md but actual count is 44

---

## Dimension 6: Build System Alignment — 7.5/10

### Assessment
The Nuitka pipeline for the Desktop Standalone Suite is well-aligned.
The package system and CI pipeline are not.

| Build Target | System | Alignment Status |
|-------------|--------|-----------------|
| Desktop EXEs (52) | build_all.py (Nuitka, Tiers 1-10) | 🟢 Strong — all 52 modules tracked |
| Desktop BATs (51) | regenerate_bats.py | 🟡 52:51 gap — 1 missing BAT |
| packages/azazael-core | pyproject.toml | 🟢 Scaffolded, not published |
| Desktop projects (14) | Per-project run.py | 🟡 Inconsistent (Python/Go/Rust) |
| CI pipeline | .github/workflows/test-3.14t.yml | 🔴 Not running on GitHub |
| Pre-build validation | Manual (patch_nuitka_314t.py) | 🟡 Not automated |

**Known issues (from PROJECT_MAP.md):**
- CLUSTERWORMS EXE: "Worm registry not available" — Nuitka onefile CORE.* import path limitation
- CONCURRENCY/SMARTDISK: need PYTHONPATH during build (2 modules)
- CODEX_Studio: `--help` times out in onefile mode (Tkinter startup delay)
- No pre-build validation script (3.14t check, Nuitka patch, dep check)
- No build output smoke tests (EXE --help after build)

---

## Dimension 7: Testing Alignment — 4.5/10

### Assessment
Testing is fragmented and inconsistent across the ecosystem.

| Project | Test Count | Method | Coverage Estimate |
|---------|-----------|--------|------------------|
| azazael CORE (src/) | ~295+ standalone tests | `python tests/test_*.py` | ~15% of codebase |
| Desktop Standalone EXEs | 7 deep-tested (Phase 22) | Manual `./EXE --help` | ~13% of 52 EXEs |
| Desktop projects | Minimal | None systematic | ~0-5% |
| packages/azazael-core | run_tests.py passes | Integration tests | ~30% of package |
| CODEX/ | CODEX/TESTING/ files exist | Partial | ~10% |
| EveUnleashed_Selector | Training tests | Existing | Unknown |

**Alignment issues:**
1. **No unified test runner** — pytest segfaults on 3.14t (Error #48), tests run standalone
2. **No coverage reporting** — pytest-cov doesn't work without pytest
3. **Desktop projects have near-zero tests** — all 14 projects untested
4. **No CI pipeline** — test-3.14t.yml exists but not integrated with GitHub
5. **CODEX test files have hardcoded paths** — 5 files with sys.path.insert that would break on other machines

---

## Dimension 8: Convention Alignment — 6.0/10

### Assessment
Coding conventions are well-established for CORE/ files but inconsistently
applied across root modules, Desktop projects, and legacy directories.

| Convention | CORE/ | Root *.py | Desktop Projects | CODEX/ |
|-----------|-------|-----------|-----------------|--------|
| Type annotations | ✅ Strong | 🟡 Partial | ❌ Minimal | 🟡 Partial |
| Module-level imports | ✅ Fixed (3.14t-safe) | 🟡 Mixed | ❌ Function-body imports | 🟡 Mixed |
| import threading | ✅ Added to all files | 🟡 Inconsistent | ❌ Not checked | 🟡 Inconsistent |
| Error handling (try/except) | ✅ Structured | 🟡 Bare excepts | ❌ print() only | 🟡 Mixed |
| Dynamic paths | ✅ CORE/paths.py | ✅ Fixed | ❌ Hardcoded | 🟡 Partial |
| HAS_* flags | ✅ Standard pattern | 🟡 Inconsistent | ❌ Missing | 🟡 Inconsistent |
| `__all__` exports | 🟡 Partial | ❌ Missing | ❌ Missing | ❌ Missing |
| Docstrings | 🟡 Inconsistent | 🟡 Inconsistent | ❌ Minimal | 🟡 Partial |
| shell=True safety | ⚠️ 6 HIGH RISK | ❌ Not audited | ❌ Not audited | ❌ Not audited |
| mypy-clean | 🟡 Improving (3 rounds) | ❌ Not checked | ❌ Not checked | ❌ Not checked |

**Key convention gaps:**
1. **6 HIGH RISK shell=True usages** — all in source files with dynamic variables
2. **~1,490 remaining mypy errors** across 142 files
3. **No `__all__` in most modules** — unclear public API boundaries
4. **Bare `except:` clauses** — still present in legacy root modules
5. **3 legacy skill files lack YAML frontmatter** — invisible to automated tooling

---

## Dimension 9: Skills/Documentation Alignment — 5.0/10

### Assessment
The SKILLS_CATALOG.md lists 36 skills but only 19 exist as files on disk.
The remaining 17 are "virtual" — loaded dynamically from conversation memory.

| Skill Source | Count | Status |
|-------------|-------|--------|
| On-disk skills (`skills/*.md`) | 19 | ✅ Actual files (incl. 3 legacy) |
| Virtual skills (conversation memory only) | 17 | ⚠️ No file on disk |
| Skills with YAML frontmatter | 16 | ✅ Parseable by tooling |
| Legacy skills without frontmatter | 3 (azazael_314t_master, _optimum, _insights) | ⚠️ Flagged |
| **Total listed in catalog** | **36** | **19 on disk, 17 virtual** |

**Alignment issues:**
1. **17 virtual skills have no file** — relying on conversation memory (fragile)
2. **3 legacy files lack frontmatter** — not parseable by automated tools
3. **Catalog references skills that don't exist** — mismatch between catalog and disk
4. **Documentation references wrong lesson count** — SYSTEM_INSTRUCTIONS.md says "47 lessons"
   but actual is 44 (after duplicate fix)

---

## Dimension 10: Production Readiness Alignment — 4.0/10

### Assessment
Production readiness varies dramatically across the ecosystem.

| Project | Readiness | Key Gap | 
|---------|-----------|---------|
| CORE/ infrastructure | 🟡 6.5/10 | Test coverage (15%), mypy errors (1,490) |
| CORE/WORMS/ (79 worms) | 🟡 6.0/10 | Import-time bottlenecks (38s cold start) |
| Desktop EXEs (52) | 🟢 7.5/10 | 52:51 BAT gap, Nuitka import limits |
| Desktop projects (14) | 🔴 3.0/10 | Near-zero tests, inconsistent stacks |
| Package system | 🔴 2.5/10 | Scaffolded but not published |
| G: Drive archive | 🟡 5.0/10 | Slow SD card (Error #53) |
| Test infrastructure | 🔴 3.5/10 | No CI, pytest segfaults, no coverage |
| Documentation | 🟡 6.0/10 | 3 stale TODO docs, 17 virtual skills |

**Top 5 alignment priorities:**
1. **CI pipeline** — test-3.14t.yml exists but not running (AR-8)
2. **Test coverage** — ~15% overall, 0% for Desktop projects (AR-7)
3. **Hardcoded paths** — 12 runtime paths still unfixed
4. **META/ shim cleanup** — 13 files should be deleted (AR-9)
5. **Package migration** — 157 sys.path.insert hacks prevent clean packaging (AR-5)

---

## Misalignment Heatmap

| Project \ Dimension | Python | Arch | Deps | Paths | Docs | Build | Tests | Conv | Skills | Prod | Avg |
|--------------------|--------|------|------|-------|------|-------|-------|------|-------|------|-----|
| **CORE/** | 10 | 8 | 5 | 8 | 7 | 7 | 5 | 7 | N/A | 6 | **7.0** |
| **CORE/WORMS/** | 10 | 9 | 7 | 9 | 6 | 7 | 5 | 6 | N/A | 6 | **7.2** |
| **CODEX/** | 10 | 8 | 6 | 6 | 5 | 5 | 3 | 5 | N/A | 5 | **5.9** |
| **ORCHESTRATION/** | 10 | 6 | 5 | 7 | 5 | 6 | 3 | 5 | N/A | 4 | **5.6** |
| **Root *.py** | 10 | 4 | 5 | 7 | 4 | N/A | 2 | 4 | N/A | 4 | **5.0** |
| **META/** | 10 | 3 | 3 | N/A | 3 | N/A | N/A | 3 | N/A | 3 | **4.2** |
| **Desktop EXEs** | 10 | 7 | 8 | N/A | 6 | 8 | 3 | 6 | N/A | 7 | **6.9** |
| **Desktop Projects** | 7 | 4 | 8 | 2 | 4 | 5 | 1 | 3 | N/A | 3 | **4.1** |
| **G: Drive** | N/A | N/A | N/A | N/A | 5 | N/A | N/A | N/A | N/A | 5 | **5.0** |
| **Package System** | 9 | 5 | 3 | N/A | 5 | 5 | 4 | 3 | N/A | 3 | **4.6** |
| **Skills/Docs** | N/A | N/A | N/A | N/A | 5 | N/A | N/A | N/A | 5 | N/A | **5.0** |

**Legend:** 🔴 0-4 = Critical misalignment | 🟡 5-7 = Needs improvement | 🟢 8-10 = Well-aligned

---

## Alignment Roadmap (Priority-Ordered)

| Priority | Action | Dimensions Improved | Effort |
|----------|--------|-------------------|--------|
| P0 | Fix 6 shell=True HIGH RISK usages | Conventions (8), Safety | 2h |
| P0 | Set up CI pipeline (test-3.14t.yml) | Testing (4.5), Build (7.5) | 4h |
| P1 | Fix 12 runtime hardcoded paths | Paths (7.0), Desktop Projects (4.1) | 3h |
| P1 | Delete META/ shims (verify 0 consumers) | Architecture (6.5), Deps (5.5) | 1h |
| P1 | Add pytest-cov + coverage reporting | Testing (4.5) | 2h |
| P1 | Fix ~1,490 mypy errors (next 5 files) | Conventions (6.0), Type safety | 8h |
| P2 | Archive 3 stale TODO docs | Docs (5.5) | 1h |
| P2 | Switch from sys.path.insert to editable pip install | Deps (5.5), Package (4.6) | 3h |
| P2 | Add YAML frontmatter to 3 legacy skill files | Skills/Docs (5.0) | 0.5h |
| P2 | Fix 52:51 EXE/BAT gap in Standalone Suite | Build (7.5) | 1h |
| P3 | Create skill files for 17 virtual skills | Skills/Docs (5.0) | 4h |
| P3 | Evaluate LlamaServer + EveUnleashed integration | Desktop Projects (4.1) | 3h |

---

## Key Findings

### Strengths (High Alignment)
1. **Python 3.14t** — Unified across all actively maintained projects (9.5/10)
2. **Build pipeline** — 52 EXEs tracked in build_all.py, Nuitka pipeline mature (7.5/10)
3. **CORE/ infra patterns** — Worm registry, nature clusters, dynamic paths well-established
4. **Free-threading safety** — 12 files fixed with double-checked locking (8.0/10 readiness)

### Critical Weaknesses (Low Alignment)
1. **Desktop project testing** — 14 projects, near-zero tests (0-5% coverage)
2. **Documentation fragmentation** — 5 docs, 3 stale, 17 virtual skills without files
3. **Package system** — Scaffolded but not used; 157 sys.path.insert hacks remain
4. **META/ shim accumulation** — 13 dead files that should have been deleted
5. **No CI pipeline** — test-3.14t.yml exists but never runs

### Recommended Next Session
1. Fix 6 shell=True HIGH RISK usages (AR-1)
2. Set up CI pipeline (AR-8)
3. Delete META/ deprecation shims (AR-9)
