# Azazael Codebase — COMPREHENSIVE REWRITE PLAN (REWRITE_TODO.md)

**Generated:** 2026-05-28
**Status:** ACTION REQUIRED — 265 files, 73 registered worms, 17 categories

---

## ⚠️ CRITICAL ISSUES — MUST FIX BEFORE REWRITE

### 1. Hardcoded Paths (MASSIVE ISSUE)
Over **40+ files** contain hardcoded absolute Windows paths like:
- `C:/Users/clint/Desktop/Azazael_UNIFIED`
- `C:/Users/clint/Desktop/CODEX/`
- `C:/Azazael/Azazael_UNIFIED`

These MUST be replaced with dynamic path resolution using `Path(__file__).parent` chains.

| File | Hardcoded Path | Priority |
|------|---------------|----------|
| `OMNI_WORM_V2.py` | `C:/Users/clint/Desktop/Azazael_UNIFIED` | CRITICAL |
| `CHANGELOG_GENERATOR.py` | `C:/Users/clint/Desktop/Azazael/version.py` | HIGH |
| `CLI/azazael_cli.py` | `C:/Azazael/Azazael_UNIFIED` | CRITICAL |
| `CORE/NODE.py` | `C:/Users` path detection | HIGH |
| `CORE/PamsRecorder.py` | hardcoded db path | HIGH |
| `CORE/STRESS_TEST.py` | `C:/Users/clint/Desktop/Azazael` | HIGH |
| `CORE/PYTHON_MANAGER.py` | `C:/Azazael/Azazael_UNIFIED` | HIGH |
| `HYDRAMETA_UV.py` | multiple `C:/Users/clint` paths | HIGH |
| `META/DebugZ.py` | `C:/Users/clint/Desktop` | HIGH |
| `META/FleetZ.py` | hardcoded root paths | HIGH |
| `UTILITIES/TERENCE/TERENCE.py` | `C:/Azazael/Azazael_UNIFIED` | HIGH |

### 2. Duplicate/Redundant Classes (CONGRUENCY PROBLEM)
These classes exist in MULTIPLE files with divergent implementations:

| Class | File 1 | File 2 | Action |
|-------|--------|--------|--------|
| `METAZ` | `METAWORMS.py:111` | `METAWORMS_ENRICHED.py:233` | Choose one canonical source |
| `DEPENDZ` | `METAWORMS.py:167` | `METAWORMS_ENRICHED.py:314` | Choose one canonical source |
| `VALIDZ` | `METAWORMS.py:216` | `METAWORMS_ENRICHED.py:371` | Choose one canonical source |
| `DEADZ` | `METAWORMS.py:259` | `METAWORMS_ENRICHED.py:433` | Choose one canonical source |
| `METRICZ` | `METAWORMS.py:310` | `METAWORMS_ENRICHED.py:502` | Choose one canonical source |
| `LOGZ` | `METAWORMS.py:377` | `METAWORMS_ENRICHED.py:604` | Choose one canonical source |
| `CHANGEZ` | `METAWORMS.py:421` | `METAWORMS_ENRICHED.py:656` | Choose one canonical source |
| `METAWORMS` | `METAWORMS.py:466` | `METAWORMS_ENRICHED.py:737` | Choose one canonical source |
| `TRIMZ` | `TRIMZ.py:225` | `META/TRIMZ.py:239` | Choose one canonical source |
| `DOCKERZ` | `DOCKERZ.py:78` | `META/DOCKERZ.py:80` | Choose one canonical source |
| `HEALTHZ` | `HEALTHZ.py:50` | `META/HEALTHZ.py:46` | Choose one canonical source |
| `OPTIMIZ` | `OPTIMIZ.py:45` | `META/OPTIMIZ.py:45` | Choose one canonical source |
| `METRICZ` | `METRICZ.py:111` | `METAWORMS.py:310` | Choose one canonical source |
| `WormExecutor` | `CONCURRENCY.py:157` | `CLUSTERWORMS.py:162` | Unify into FREETHREAD_UPGRADE.py |

### 3. sys.path.insert Proliferation
Over **157 instances** of `sys.path.insert(0, ...)` across the codebase. Each manual path injection is a code smell that signals import architecture failure. Solution: proper `__init__.py` package structure + `pyproject.toml`.

### 4. Inconsistent VERSION Attributes
79 files declare `VERSION = "1.0.0"` but no centralized version tracking. Many are likely out of sync.

---

## 📋 PHASE 1: File Reorganization (Days 1-2)

### 1.1 Eliminate Duplicate Classes
> Lessons: [#24](LESSONS_MASTER.md) (deprecation shims), [#27](LESSONS_MASTER.md) (verify tech stack before auditing)
- [ ] Audit all duplicate implementations (see table above)
- [ ] Select canonical implementation for each
- [ ] Add deprecation shim in old location pointing to canonical
- [ ] Update all imports across the codebase

### 1.2 Fix Hardcoded Paths
> Lessons: [#1](LESSONS_MASTER.md) (TOML forward slashes), [#5](LESSONS_MASTER.md) (network drive timeouts)
- [ ] Create `azazael/src/CORE/paths.py` with `get_project_root()` and `get_azazael_root()`
- [ ] Replace ALL hardcoded paths with dynamic resolution
- [ ] Add CI check that rejects new hardcoded paths

> **Note:** See [`LESSONS_MASTER.md`](LESSONS_MASTER.md) for all 37 lessons (canonical cross-reference).

### 1.3 Standardize Module Imports
> Lessons: [#19](LESSONS_MASTER.md) (import hygiene — module-level only)
- [ ] Remove ALL `sys.path.insert(0, ...)` hacks
- [ ] Create proper `__init__.py` re-exports for all packages
- [ ] Add `pyproject.toml` with correct package layout

---

## 📋 PHASE 2: Code Quality (Days 3-5)

### 2.1 Fix Bare Excepts
> Lessons: [#17](LESSONS_MASTER.md) (HAS_* flags: initialize before try/except)
Current: 24 bare excepts found in non-CODEX/test files
- [ ] Fix all to use `except Exception:` or specific exception types
- [ ] Add logging to every except block

### 2.2 Standardize Class Patterns
- [ ] All classes: add `VERSION = "X.Y.Z"` class attribute
- [ ] All classes: add `__repr__` method
- [ ] All public methods: add docstrings
- [ ] Add type annotations to all function signatures

### 2.3 Python 3.14t Readiness
> Lessons: [#8](LESSONS_MASTER.md) (cp314t wheel tag), [#9](LESSONS_MASTER.md) (psycopg2), [#10](LESSONS_MASTER.md) (thread safety), [#11](LESSONS_MASTER.md) (test timeout), [#12](LESSONS_MASTER.md) (psutil fix), [#13](LESSONS_MASTER.md) (pytest segfault)

**3.14t-ONLY RULE: Python 3.13 is NOT used. Python 3.14t is the ONLY Python.**
- [ ] Replace all manual ThreadPoolExecutor with FreeThreadPool
- [ ] Migrate WormExecutor → WormPool (FREETHREAD_UPGRADE.py)
- [ ] Migrate ClusterExecutor → ClusterRunner (FREETHREAD_UPGRADE.py)
- [ ] Add `is_free_threaded()` checks to performance-critical paths
- [ ] Before Nuitka builds: `python azazael/docs/scripts/patch_nuitka_314t.py --apply`
- [ ] Verify all build commands use `python` (not `python313` or Python313 paths)
- [ ] Never recommend Python 3.13 as a workaround or fallback

### 2.4 Testing Coverage
> Lessons: [#14](LESSONS_MASTER.md) (store injection for hermetic tests), [#15](LESSONS_MASTER.md) (test infra pays), [#16](LESSONS_MASTER.md) (verify queries first)
- [ ] Current: 24 unit tests for worm_registry only
- [ ] Add: tests for all 73 registered worms
- [ ] Add: integration tests for cross-worm communication
- [ ] Add: free-threading stress tests

---

## 📋 PHASE 3: Architecture (Days 6-10)

### 3.1 Centralized Configuration
- [ ] Create `azazael/src/CORE/config.py` — single source of truth
- [ ] Migrate all scattered config classes (ERRORZConfig, TRIMZConfig, etc.)
- [ ] Support env vars, .env files, CLI flags

### 3.2 Unified Logging
- [ ] Replace scattered `print()` calls with proper logging
- [ ] Integrate `AzazaelDynamicLogger` project-wide
- [ ] Add structured logging (JSON format)

### 3.3 Telemetry Pipeline
- [ ] Wire SpanTracer, MetricAggregator, EventRouter into all worms
- [ ] Add OpenTelemetry exporter
- [ ] Create monitoring dashboard

### 3.4 Plugin Architecture
- [ ] Make worm discovery fully dynamic (no manual import lists)
- [ ] Support external worm packages
- [ ] Hot-reload worms without restart

---

## 📋 PHASE 4: Specific File Rewrites (Days 11-14)

### 4.1 CORE/WORMS/ — Full Rewrite
Status: 25 files, 76 classes, heavy duplication

- [ ] **SYSTEMZ.py** (64 lines) → rewrite with FreeThreadPool integration
- [ ] **PROCESSZ.py** (295 lines) → refactor, remove hardcoded paths
- [ ] **NETWORXZ.py** (242 lines) → add proper error handling
- [ ] **DISKZ.py** (305 lines) → add SMART monitoring integration
- [ ] **CLOCKZ.py** (241 lines) → add cron-like scheduling
- [ ] **WORMZ.py** (769 lines) → split into smaller modules
- [ ] **CONCURRENCY.py** (675 lines) → replace with FREETHREAD_UPGRADE
- [ ] **CLUSTERWORMS.py** (672 lines) → replace with ClusterRunner
- [ ] **BINARY_ANALYSIS.py** (1498 lines!) → split into 3-4 focused modules
- [ ] **NETWORK_DIAG.py** (1311 lines!) → split into traceroute, ping, netstat modules
- [ ] **OS_CONGRUENCY.py** (989 lines) → platform-specific splits
- [ ] **SMARTDISK.py** (716 lines) → integrate with DISKZ
- [ ] **REVERSE_TOOLS.py** (932 lines) → split by tool
- [ ] **ECOSYSTEM_EXPANSION.py** (50 worms) → split by category into separate files

### 4.2 META/ vs root METAWORMS.py
- [ ] Decide: keep META/ directory or merge into root
- [ ] Remove METAWORMS_ENRICHED.py duplication
- [ ] Standardize single canonical source

### 4.3 ORCHESTRATION/ Cleanup
> Lessons: [#1](LESSONS_MASTER.md) (TOML forward slashes), [#17](LESSONS_MASTER.md) (HAS_* flags), [#5](LESSONS_MASTER.md) (network drive timeouts)
- [ ] Remove hardcoded paths from all scripts
- [ ] Fix 10 bare excepts in ml_platforms scripts
- [ ] Add proper CLI interface

---

## 📋 PHASE 5: Documentation & Finalization (Days 15-16)

- [ ] Generate API docs for all 73 worms
- [ ] Create architecture diagrams (GraphRenderer + DOT)
- [ ] Write migration guide from old to new APIs
- [ ] Add CONTRIBUTING.md
- [ ] Create `pyproject.toml` with proper metadata

---

## 🔍 INCONSISTENCIES MAP

| Issue | Count | Severity |
|-------|-------|----------|
| Hardcoded absolute paths | 40+ | CRITICAL |
| Duplicate class implementations | 14 pairs | CRITICAL |
| `sys.path.insert(0, ...)` hacks | 157 | HIGH |
| Bare excepts (non-CODEX) | 24 | HIGH |
| Missing VERSION attribute | ~100 classes | MEDIUM |
| Missing docstrings | ~150 classes | MEDIUM |
| Missing type annotations | ~80% of code | MEDIUM |
| `except Exception:` too broad | 183+ | LOW |
| `# coding: utf-8` in Python 3 files | 28 | LOW (harmless noise) |

---

## ✅ COMPLETED IN THIS SESSION

1. **Registered 7 existing worms:** ERRORZ, TRIMZ, METRICZ, DOCKERZ, HEALTHZ, OPTIMIZ, TELEMETRYZ
2. **Created 50 new worms** in ECOSYSTEM_EXPANSION.py across 10 categories
3. **Total: 73 worms in 17 categories** (up from 23 in 7)
4. **Created FREETHREAD_UPGRADE.py** with WormPool, ClusterRunner, 3.14t integration
5. **Fixed 4 bare excepts** in core files (ERROR_SCAN_WORM, OMNI_WORM_V2, CHANGELOG_GENERATOR, azazael_cli)
6. **Created INSIGHTS.md** with ecosystem analysis

---

## 🚨 IMMEDIATE NEXT ACTIONS

1. **FIX hardcoded paths** — This is the #1 source of runtime failures
2. **ELIMINATE duplicate classes** — 14 pairs causing import confusion
3. **REMOVE sys.path.insert hacks** — Build proper package structure
4. **SPLIT mega-files** — BINARY_ANALYSIS (1498 lines), NETWORK_DIAG (1311 lines)
5. **ADD tests** — Only 24 tests for 73 worms is unacceptable

---

## 📋 PHASE 6: Production Reproducibility (NEW — May 28, 2026)

### 6.1 Deterministic Builds
- [ ] Pin ALL dependency versions in requirements_314.txt with exact == versions
- [ ] Add requirements_314_freeze.txt (pip freeze output for reproducibility)
- [ ] Create Dockerfile for containerized reproducible builds
- [ ] Add hash verification for downloaded models and artifacts
- [ ] Create CI/CD pipeline (.github/workflows/build.yml) for automated .exe builds

### 6.2 Build System
- [ ] Standardize PyInstaller .spec files for all 37+ .exe modules
- [ ] Create build_all_314t.py orchestrator script with parallel build support
- [ ] Add --reproucible-build flag to PyInstaller for bytecode determinism
- [ ] Generate build manifest (build_manifest.json) with SHA256 hashes per .exe
- [ ] Create automated smoke test suite for all built .exe files

### 6.3 Environment Reproducibility
- [ ] Capture full system environment: Python version, OS, CPU, GPU, drivers
- [ ] Create environment snapshot (environment_snapshot.json) for each build
- [ ] Add virtual environment bootstrap script (bootstrap_314t.py)
- [ ] Support Windows, Linux, macOS in build matrix
- [ ] Document exact winget/choco/brew package versions needed

### 6.4 Model & Artifact Reproducibility
- [ ] Add model checksum verification before inference
- [ ] Create model registry (model_registry.json) with SHA256, source URL, license
- [ ] Support offline model cache (~/.azazael/models/)
- [ ] Add model version pinning per framework
- [ ] Create model download/resume utility with progress bar

### 6.5 Testing Reproducibility
- [ ] Expand test suite to 100+ unit tests covering all 73 worms
- [ ] Add integration test harness with mock PAMS/MemoryBus
- [ ] Create deterministic random seed for all ML tests
- [ ] Add performance regression benchmarks
- [ ] Generate test coverage reports (coverage.py)

### 6.6 Documentation
- [ ] Create BUILD.md with exact build instructions
- [ ] Create REPRODUCIBILITY.md with environment setup guide
- [ ] Document all known 3.14t C extension incompatibilities
- [ ] Add troubleshooting guide for common build failures
- [ ] Create architecture decision records (ADR/) for key design choices

### 6.7 Release Pipeline
- [ ] Create release.sh script: build -> test -> sign -> package -> publish
- [ ] Add code signing for Windows .exe files
- [ ] Create installer (NSIS or MSI) for end-user deployment
- [ ] Auto-generate CHANGELOG.md from git history
- [ ] Tag releases with semver: v4.0.0-314t
