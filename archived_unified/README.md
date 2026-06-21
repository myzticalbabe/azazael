# Azazael Unified — Archived Module Reference

> **Status:** Archived (moved out of `src/` to prevent import conflicts)
> **Restored from:** `G:\azazael-archive` (2026-02-12 backup)
> **File count:** ~210 `.py` files across 12 modules
> **Original location:** `azazael/src/Azazael_UNIFIED/`

## Why Archived?

The `Azazael_UNIFIED` directory contained a refactored/canonicalized copy of the entire Azazael codebase. However, its sub-modules (`CODEX`, `CORE`, `HYDRA`, `ORCHESTRATION`, etc.) directly **duplicated** the module names in `azazael/src/`, causing Python import conflicts. Moving them here ensures:

- ✅ `src/` modules resolve correctly (no import ambiguity)
- ✅ The preserved code is still accessible for reference
- ✅ The archive can be re-integrated piece by piece

## Module Reference

| Module | Files | Description |
|--------|-------|-------------|
| `CLI/` | 1 | Azazael command-line interface entry point (`azazael_cli.py`) |
| `CODEX/` | 57 | Code analysis, generation, syntax fixing, documentation generation |
| `CORE/` | 29 | Core system management — environment, Python, local dev, node management |
| `HYDRA/` | 11 | ML Hydra protocol — harness, launcher, health monitoring, Q-learning analysis |
| `META/` | 15 | Meta-programming — code manipulation, template generation, reflection tools |
| `ORCHESTRATION/` | 69 | System orchestration — ADLP module, FusionCore, system manager, healing |
| `OUTPUT/` | 0 | Output directory (empty — runtime generated) |
| `SCRIPTS/` | 4 | Utility scripts — bootstrap, integration helpers |
| `SHORTCUTS/` | 0 | Shortcut links (empty — Windows-only) |
| `TOOLS/` | 2 | Comprehensive fix tools, system utilities |
| `UTILITIES/` | 22 | General-purpose helpers — caching, formatting, encoding, async utilities |
| `config/` | 0 | Configuration templates (empty — runtime populated) |

### Additional Files

| File | Description |
|------|-------------|
| `CLI_ENUMERATION.txt` | Complete catalog of all 50+ CLI tools across sections |
| `requirements_311.txt` | Python 3.11 dependency list |
| `requirements_314.txt` | Python 3.14 dependency list |
| `requirements_314_final.txt` | Python 3.14 final dependency list |
| `requirements_314_full.txt` | Python 3.14 full dependency list |

## Key Modules & Their Role

### ORCHESTRATION (69 files) — System Integration Layer

The most feature-rich module, containing the full ADLP (Assistant Dynamic Logging Protocol) ecosystem:

- **`ADLP_FusionCore.py`** — Unified intelligence layer v4.0. Centralized logging to `fusion.json`, `modules.json`, `knowledge.json`. Module registration with tier tracking (System, Assistant, ML, Knowledge, Orchestration).
- **`ADLP_MLOrchestrator.py`** — ML task lifecycle: prediction, classification, regression, clustering, anomaly detection, QA, summarization, generation.
- **`AssistantLogProtocol.py`** — Standardized logging protocol with checksums, confidence scoring, source tracking.
- **`AssistantLogProtocol_Enhanced.py`** — Async logging with log rotation, compression, TTL expiration.
- **`ADLP_SystemTools.py`** — Path fixing, dependency checking, environment validation.
- **`FusionHealer.py`** — Self-healing system: auto-fixes import errors, path issues, environment corruption.
- **`SystemManager.py`** — `HealthStatus` + `SystemCrawler` for comprehensive system introspection.
- **`SystemManagerGUI.py`** — Tkinter management GUI for system monitoring and control.
- **`TotalFusion.py`** — Integrates FusionCore + MLOrch + Healer into a unified system.
- **`SelfImprovingGUI.py`** — ML-powered adaptive GUI layout with `WidgetMetrics` tracking.
- **`MathCertainty.py`** — MCPS (Mathematical Certainty Proof System): HashChain, ProofType, CertaintyLevel using SHA-256.

### CODEX (57 files) — Code Analysis & Generation

Complete code analysis pipeline covering syntax validation, docstring generation, link checking, documentation indexes, batch analysis, and HTML reporting.

### CORE (29 files) — System Foundation

Environment management (`environ_updater.py`), Python version management (`PYTHON_MANAGER.py`), local dev setup (`LOCAL_DEV.py`), node management (`NODE.py`), and system health monitoring.

### HYDRA (11 files) — ML Infrastructure

Training harness, job launcher, health monitoring, permanent model loading, Q-learning analysis (single, full, multi-model variants), MoE verification, cross-platform analysis, diagnostics.

### UTILITIES (22 files) — General-Purpose Helpers

Caching strategies, data formatting, path utilities, encoding helpers, async primitives, stream processing, timing utilities.

## How to Restore Individual Modules

To move a module back to active use:

```bash
# Restore a specific module to src/
cp -r azazael/archived_unified/ORCHESTRATION azazael/src/ORCHESTRATION

# Verify there are no naming conflicts
diff -rq azazael/src/ORCHESTRATION azazael/archived_unified/ORCHESTRATION

# Run import verification
python3 -c "from ORCHESTRATION.ADLP_FusionCore import *"
python3 -c "from ORCHESTRATION.SystemManager import *"
```

**Warning:** Many modules depend on each other (e.g., ORCHESTRATION imports from CORE, CODEX imports from UTILITIES). You may need to restore multiple modules together.

## Cross-Platform Notes

- **`CORE/WORMS/OS_CONGRUENCY.py`** — Windows-only. Uses `winreg` + PowerShell. On Linux, it calls `sys.exit(0)` with a warning.
- **Windows paths**: Some files still reference `C:\Users\clint\Desktop` — these have been updated to relative paths where identified.
- **`winreg` imports**: Wrapped in try/except for Linux compatibility.
