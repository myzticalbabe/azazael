# SESSION INSIGHTS — May 29, 2026 (Continued)
# azazael-core Packaging, Desktop Audit, Skills & CLI

> Generated: May 29, 2026 — Codebuff Session
> Companion to: MEMORIES.md, ERROR_LOG.md, SESSION_INSIGHTS_2026-05-29.md

> **⚠️ HISTORICAL RECORD**: This session used Python 3.13, which is now **obsolete**. As of Phase 22+, **Python 3.14t (free-threading) is the ONLY Python** used for all builds, development, and workloads. Python 3.13 is not used anywhere. References below to "Python 3.13" reflect the state at the time of this session and should not be replicated.

---

## Session Summary (This Phase)

This phase focused on four major workstreams:
1. **azazael-core .exe packaging** — Bundling worms + clusters, Nuitka build, CI/CD
2. **Desktop Standalone Audit** — Testing all 38 .exe files for operability
3. **New Skills** — Creating azazael-exe-build skill
4. **CLI Enhancement** — Adding `clusters execute` subcommand

---

## Changes Made

### 1. Worm Bundling into azazael-core (50 worms, 10 categories)

| File | Action |
|------|--------|
| `worms/expansion/security.py` | Copied + imports adapted: `CORE.worm_registry` → `azazael_core.worm_registry` |
| `worms/expansion/profiling.py` | Same pattern |
| `worms/expansion/telemetry.py` | Same pattern |
| `worms/expansion/container.py` | Same pattern |
| `worms/expansion/config.py` | Same pattern |
| `worms/expansion/backup.py` | Same pattern |
| `worms/expansion/communication.py` | Same pattern |
| `worms/expansion/learning.py` | Same pattern |
| `worms/expansion/migration.py` | Same pattern |
| `worms/expansion/visualization.py` | Same pattern |
| `worms/expansion/__init__.py` | Re-exports all 50 worms |
| `worms/__init__.py` | Auto-imports expansion on package init |
| `__init__.py` | Added `from .worms import expansion` (try/except guarded) |

**Result:** `discover_worms()` now finds 50 worms across 10 categories in standalone .exe.
Fixed: `discover_worms()` was looking for uppercase `WORMS` directory — changed to lowercase `worms`.

### 2. Cluster Bundling into azazael-core (3 modules, 2,992 lines)

| File | Action |
|------|--------|
| `worms/clusters/CLUSTERWORMS.py` (1165 lines) | Copied + imports adapted |
| `worms/clusters/NATURE_CLUSTERS.py` (935 lines) | Copied + imports adapted |
| `worms/clusters/METACLUSTER.py` (892 lines) | Copied + imports adapted, NATURE_CLUSTERS import path fixed |
| `worms/clusters/__init__.py` | Re-exports with try/except ImportError guards + `_OK` flags |
| `cli.py` | Added `clusters` command with `_safe_str()` for Windows cp1252 terminals |
| `__init__.py` | Added `from .worms import clusters` (try/except guarded) |

**Result:** 8 predefined cluster types + 18 Nature categories available in standalone .exe.
PamsRecorder and MemoryBus imports gracefully fail (already in try/except blocks).

### 3. .exe Build History

| Build | Size | Contents |
|-------|------|----------|
| Initial | 6.8 MB | Core only (paths, registry, config, freethreading) |
| + Worms | 8.0 MB | +50 expansion worms across 10 categories |
| + Clusters | 9.7 MB | +3 cluster modules (CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTER) |

### 4. Desktop Standalone Audit Results

**Inventory:**
- 38 .exe files across 7 tiers
- 91 .bat launcher files
- Built with Python 3.13 + Nuitka via `build_all.py` (historical — all builds now on 3.14t)

**Operability Results:**

| Status | Count | Details |
|--------|-------|---------|
| ✅ Operational | 36 | CLI tools work, GUI apps launch |
| ❌ Broken | 2 | `POPUP_Immersive_314t.exe` (ImportError: tkinter.webview), `Auto_Doc_Gen_314t.exe` (KeyError: 'file') |

**BAT File Issue:**
- 52/91 .bat files have literal `$path` template variable (never substituted)
- All `_314t.bat` variants affected — they attempt to run `python.exe "C:\Users\clint\azazael\src$path"` which is non-functional
- 39 non-`_314t` .bat files are OK (invoke .exe directly)
- **Fix:** Regenerate all `_314t.bat` files to invoke the .exe directly via `%~dp0NAME_314t.exe`

**Largest EXEs:**
| .exe | Size |
|------|------|
| CODEX_Studio_314t.exe | 32.7 MB |
| QL_Optimizer_314t.exe | 22.5 MB |
| Math_Certainty_314t.exe | 22.5 MB |
| BINARY_Analysis_314t.exe | 16.6 MB |
| NETWORK_Diag_314t.exe | 16.6 MB |

### 5. CLI Enhancements

**New: `clusters execute <type>` subcommand**

```bash
azazael-core clusters execute system     # Execute the system cluster
azazael-core clusters execute security   # Execute the security cluster
azazael-core clusters execute            # List available types
```

Shows: cluster description, resolved worms, loaded worm count, execution status.

**New: `tests/conftest.py`**
- Session-scoped fixtures: `run_cli`, `worm_registry`, `cluster_registry`, `nature_definitions`
- Proper `sys.path` setup for test imports

### 6. GitHub Actions CI

**Created: `.github/workflows/build.yml`**
- Triggers on tag push + manual dispatch
- Python 3.13, Nuitka standalone build (historical — now using 3.14t)
- `run_tests.py` integration suite (primary — no pytest dependency)
- Optional pytest with `continue-on-error: true`
- Auto-release with artifact upload

### 7. Test Infrastructure

**`run_tests.py`** — 25+ integration tests using plain Python assertions + subprocess:
- Import chain (3 cluster modules, worm registry)
- All 5 CLI commands (version, paths, registry, clusters, config)
- ClusterWORMZ, NatureClusterManager, MetaCluster class tests
- Mermaid graph generation
- Cluster registry + Nature definitions counts

**`tests/test_cli.py`** — 20 pytest tests:
- Version, Paths, Registry, Clusters, Config, Help CLI commands
- Cluster module import tests
- Class instantiation + Mermaid generation

**Known issue:** pytest 9.0.3 segfaults on Python 3.13 + cygwin bash (historical — 3.13 is not used).
Workaround: `run_tests.py` uses plain Python, no pytest dependency.

### 8. New Skills Created

**`azazael-exe-build.md`** — Comprehensive Nuitka .exe building guide:
- Python 3.13 requirement (3.14 incompatible — historical, now using 3.14t with patched Nuitka)
- Standard build command with all flags documented
- azazael-core specific build procedure
- Desktop Standalone Suite build via `build_all.py`
- Module inventory (39 modules, 7 tiers)
- Typical .exe sizes by dependency level
- 5 common gotchas with fixes
- .bat launcher pattern (correct and broken)
- CI/CD build pattern

---

## Architecture Findings

### 1. Nuitka + Python 3.14 Incompatibility Is Fundamental
The Python 3.14 free-threading C API changes affect `PyObject` layout and critical section markers.
Nuitka's C code generation cannot handle these changes without patching. All builds now use Python 3.14t with patches applied via `patch_nuitka_314t.py`.

### 2. Standalone .exe Bundle Size Correlates With Deps
Pure Python → 4-8 MB. +pyyaml → 8-12 MB. +PIL/tkinter → 12-18 MB. +numpy → 18-25 MB. +multimedia → 30-35 MB.

### 3. Emoji in Terminal Output Is a Real Windows Problem
NATURE_DEFINITIONS contains emoji icons. On Windows cp1252 terminals, these cause `UnicodeEncodeError`.
Fix: `.encode('cp1252', 'replace').decode('cp1252')` — preserves all printable chars, strips non-encodable ones.

### 4. BAT Template Bug Is Widespread
52/91 .bat files contain `$path` as a literal string. This was clearly a template variable meant for
substitution during build, but the substitution step was never implemented or failed silently.

### 5. pytest 9.0.3 Segfault on Python 3.13 + Cygwin (historical — 3.13 is not used)
This is an environmental issue, not a code bug. The workaround (`run_tests.py` using plain assertions)
is robust and CI-friendly.

---

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| azazael-core CLI commands | 4 | 5 (+clusters execute) |
| Worms in standalone .exe | 0 | 50 |
| Cluster modules bundled | 0 | 3 |
| Standalone .exe size | 6.8 MB | 9.7 MB |
| Desktop .exe files audited | 0 | 38 |
| Operational Desktop .exe | — | 36/38 (94.7%) |
| Broken Desktop .exe | — | 2/38 |
| Broken .bat launchers | — | 52/91 |
| New skills created | — | 1 (azazael-exe-build) |
| CI workflow | — | 1 (.github/workflows/build.yml) |
| Integration tests | 0 | 25+ |
| Pytest tests | 0 | 20 |

---

## Remaining Work

### High Priority
1. Fix 52 broken `_314t.bat` files — regenerate to invoke .exe directly
2. Fix `POPUP_Immersive_314t.exe` — missing tkinter.webview dependency
3. Fix `Auto_Doc_Gen_314t.exe` — KeyError: 'file' in doc generation
4. Rebuild Desktop standalone .exe files with latest canonical sources

### Medium Priority
5. Add `clusters execute` to run_tests.py
6. Add `conftest.py` fixtures to existing test_cli.py tests
7. Create azazael-standalone-audit skill for periodic operability checks

### Low Priority
8. Docker containerization for reproducible .exe builds
9. CI/CD pipeline for all 39 Desktop .exe files
10. Pytest upgrade when segfault is fixed upstream
