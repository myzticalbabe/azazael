---
name: azazael-separation
description: Azazael project separation — extraction playbooks, dependency analysis, sub-project inventory, standalone packaging procedures.
metadata:
  category: architecture
  project: azazael
---

# Azazael Project Separation Skill

## Overview

Azazael has 292 Python source files spanning 16+ sub-projects. This skill documents the separation strategy, dependency maps, and extraction playbooks for breaking the monolith into standalone, independently operable projects.

For the complete separation plan, see `PATH_FORWARD.md`.

---

## Sub-Project Inventory

### Core Framework
| Project | Location | Files | Dependencies | Extractable? |
|---------|----------|-------|-------------|-------------|
| **CORE/** | `azazael/src/CORE/` | 20+ | stdlib only | ✅ Low effort |
| **CORE/WORMS/** | `azazael/src/CORE/WORMS/` | 50 worms | CORE | ✅ Medium (after CORE extracted) |
| **ORCHESTRATION/** | `azazael/src/ORCHESTRATION/` | 15+ | CORE, HYDRA, META | ⚠️ Medium (cross-deps) |
| **HYDRA/** | `azazael/src/HYDRA/` | 10+ | CORE, ORCHESTRATION/ml_platforms | ⚠️ Medium (duplicates resolved) |
| **META/** | `azazael/src/META/` | 8 | CORE, root modules | ✅ Low (all shimmed) |
| **CODEX/** | `azazael/src/CODEX/` | 30+ | CORE, ORCHESTRATION | ⚠️ Medium |
| **UTILITIES/** | `azazael/src/UTILITIES/` | 20+ | CORE (partial), or standalone | Varies |
| **CLI/** | `azazael/src/CLI/` | 5+ | CORE | ✅ Low |
| **TOOLS/** | `azazael/src/TOOLS/` | 3+ | CORE | ✅ Low |

### Root-Level Modules (17 canonical .py files)
All in `azazael/src/`:
UVZ, OPTIMIZ, DOCKERZ, METAWORMS, METRICZ, TELEMETRYZ, HEALTHZ, ERRORZ, TRIMZ,
MISSING_TOOLS, HYDRA_CONTAINER, HYDRAMETA_UV, CHANGELOG_GENERATOR,
HORUS_INTEGRATION, ECOSYSTEM_HEALTH_CHECK, FILE_MANIFEST_GENERATOR,
AUTO_DOC_GENERATOR, METAWORMS_POPUP, ANIMATION_PROTOCOLS, enrichment_display,
matrix_animation, QL_FILE_OPTIMIZER

### External Desktop Projects (Already Standalone)
| Project | Stack | Standalone? |
|---------|-------|------------|
| EveUnleashed_Selector | Python 3.11+ (rani-vl) | ✅ setup.py |
| PerformanceMonitor | Go + Rust + Python 3.14t + HTML | ✅ start.bat |
| Ultimate_Agent_Selector | Python + Go/Rust scaffolding | ⚠️ Partial |
| agent_system | Python (skeletal) | ❌ Stub |

---

## Dependency Chain

```
CORE/ (paths.py, worm_registry.py, freethreading.py)
  ↑  ← Everything depends on CORE
  ├── CORE/WORMS/ (226 worms)
  │     ↑
  ├── ORCHESTRATION/ ← CORE, HYDRA, META
  │     ↑
  ├── HYDRA/ ← CORE, ORCHESTRATION/ml_platforms
  │     ↑
  ├── META/ ← CORE, root modules (via shims)
  │     ↑
  ├── CODEX/ ← CORE, ORCHESTRATION
  │     ↑
  └── Root modules ← CORE

UTILITIES/KLINK: STANDALONE (env-var-driven, no CORE dependency)
```

---

## Extraction Playbooks

### Phase I: Extract `azazael-core` Package
```bash
# Target: azazael/src/CORE/ → pip-installable azazael-core
# Files: paths.py, worm_registry.py, freethreading.py, MemoryBus.py,
#         PamsRecorder.py, Agent.py, AgentPool.py, NODE.py, STRUCTURE.py,
#         __init__.py, PYTHON_MANAGER.py, FREETHREAD_UPGRADE.py
#
# Steps:
# 1. Create azazael-core/pyproject.toml
# 2. Copy CORE/*.py to azazael-core/azazael_core/
# 3. Update internal imports to use package-relative paths
# 4. pip install -e azazael-core
# 5. Update all consumers: from CORE.X import → from azazael_core import
#
# Dependencies: stdlib only (no external deps)
# Effort: 2-4 hours
# Blockers: None
```

### Phase II: Extract `azazael-worms` Package
```bash
# Target: Root modules + CORE/WORMS/ → azazael-worms
# Files: 17 root-level .py files + CORE/WORMS/*.py
#
# Steps:
# 1. Move root modules to azazael-worms/azazael_worms/
# 2. Move CORE/WORMS/ to azazael-worms/azazael_worms/worms/
# 3. Add azazael-core dependency
# 4. Update all from CORE.X imports → from azazael_core.X
# 5. Create deprecation shims for old import paths
#
# Dependencies: azazael-core
# Effort: 4-8 hours
# Blockers: CORE.paths imports in worm files (already dynamic — should work)
```

### Phase III: Extract `azazael-orchestration` Package
```bash
# Target: ORCHESTRATION/ + HYDRA/ → azazael-orchestration
#
# Steps:
# 1. Move ORCHESTRATION/* to azazael-orchestration/azazael_orchestration/
# 2. Move HYDRA/* to azazael-orchestration/azazael_orchestration/hydra/
#    (Remove HYDRA/ml_platforms/ shims — ORCHESTRATION canonical)
# 3. Fix cross-imports between ex-ORCHESTRATION and ex-HYDRA
# 4. Add azazael-core + azazael-worms dependencies
#
# Dependencies: azazael-core, azazael-worms
# Effort: 8-16 hours
# Blockers: Cross-imports between ORCHESTRATION and HYDRA
```

### Phase IV: Extract `azazael-codex` Package
```bash
# Target: CODEX/ → azazael-codex
#
# Steps:
# 1. Move CODEX/* to azazael-codex/azazael_codex/
# 2. Remove CODEX/CORE/ shims (already pointing to root)
# 3. Fix remaining hardcoded paths in comprehensive/ and TESTING/
# 4. Add azazael-core dependency
#
# Dependencies: azazael-core
# Effort: 4-8 hours
# Blockers: 5 hardcoded paths in TESTING/conftest.py + test files
```

### Phase V: KLINK (Already Standalone)
```bash
# KLINK uses env-var-driven defaults:
# - PAMS_DATA_DIR → memory database
# - LLAMA_SERVER_EXE → llama executable
# - LLAMA_MODELS_DIR → model files
# - LLAMA_LAUNCH_SCRIPT → launch script
# No CORE dependency. Ready for separate repo.
```

### Phase VI: Desktop Project Integration
```bash
# Each Desktop project could optionally integrate azazael-core:
# - EveUnleashed_Selector: worm registry for vision agent management
# - PerformanceMonitor: metric telemetry via worm system
# - Ultimate_Agent_Selector: AgentPool for NPU orchestration
# None require it — all are currently standalone.
```

---

## Remaining Hardcoded Paths (12 runtime, ~15 documentation)

Runtime paths needing fixes before extraction:
- `CODEX/VIDEOS/create_dual_pane_video.py` — 1 output path
- `CODEX/TESTING/conftest.py` — 1 ECOSYSTEM_ROOT
- `CODEX/TESTING/UNIT/test_*.py` — 3 sys.path.inserts
- `CODEX/TESTING/PERFORMANCE/test_performance.py` — 1 sys.path.insert
- `CODEX/TESTING/INTEGRATION/test_ecosystem_integration.py` — 1 sys.path.insert
- `ORCHESTRATION/scripts/azazael_cli.py` — 1 ROOT Path
- `ORCHESTRATION/scripts/bat_analysis.py` — 1 base_path
- `ORCHESTRATION/scripts/web_dashboard.py` — 1 Root dict
- `ORCHESTRATION/ml_platforms/improvements/metrics_tracker.py` — 1 init default
- `CORE/WORMS/WORMZ_POPUP.py` — 1 cmd list

---

## Separation Readiness Scorecard

| Sub-Project | Dependencies Resolved | Hardcoded Paths | Shimmed | Readiness |
|------------|----------------------|-----------------|---------|-----------|
| CORE/ | ✅ | ✅ (0) | N/A | 🟢 Ready |
| Root Modules | ✅ | ✅ (0 remaining runtime) | 13 shims | 🟢 Ready |
| KLINK | ✅ | ✅ (env vars) | N/A | 🟢 Ready |
| ORCHESTRATION/ | ⚠️ | ⚠️ (3 scripts) | 3 shims | 🟡 Near |
| HYDRA/ | ⚠️ | ✅ (0) | 3 shims | 🟡 Near |
| CODEX/ | ⚠️ | ⚠️ (5 test files) | 8 shims | 🟡 Near |
| META/ | ✅ | ✅ (0) | All shimmed | 🟢 Ready to remove |

---

## Related Skills
- `azazael-dedup` — Finding and eliminating duplicates
- `azazael-shims` — Deprecation shim patterns
- `azazael-architecture` — Project structure
- `azazael-paths` — Dynamic path resolution
- `azazael-deploy` — Docker, CLI packaging, G:/ archive
