---
name: azazael-orchestration
description: ORCHESTRATION + HYDRA systems — ecosystem crawler, HORUS monitoring, HYDRA adaptive ML cluster, ML platform management, scripts infrastructure. 70+ .py files.
metadata:
  category: system
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Orchestration — ORCHESTRATION + HYDRA Systems

> **Implementation:** `azazael/src/ORCHESTRATION/`, `azazael/src/HYDRA/`
> **Combined footprint:** 70+ .py files across 6 subdirectories

---

## Overview

The ORCHESTRATION system manages ecosystem-level operations including crawling,
optimization, monitoring, ML platform management, and cross-system analysis.
HYDRA is an adaptive sequential ML cluster with dependency-aware processing.

---

## ORCHESTRATION Core Components

| File | Purpose |
|------|---------|
| `ECOSYSTEM_CRAWLER_LAUNCHER.py` | Full crawler execution with resolution management |
| `ECOSYSTEM_OPTIMIZER.py` | Batch operations, replaces redundant `.bat` files with unified Python |
| `HORUS.py` | Human-readable results viewer with visual popup displays |
| `HORUS_LIVE_MONITOR.py` | Real-time monitoring for HORUS |
| `HYDRA.py` | Adaptive sequential ML cluster — dependency-aware, adaptive learning |
| `HYDRA_ANALYZER.py` | Analyzes HYDRA cluster for video production representations |
| `HYDRA_ANALYZER_V2.py` | Enhanced version of HYDRA analyzer |
| `hydra_bridge.py` | Bridge between HYDRA and other systems |
| `INTEROPERABILITY_ANALYSIS.py` | Formal mathematical interoperability analysis |
| `TARBABY.py` | Binary compilation protocols and cross-platform executable generation |

## HYDRA Sub-System

| File | Purpose |
|------|---------|
| `hydra_launcher.py` | Main entry point for HYDRA pipelines |
| `hydra_protocols.py` | Communication and operational protocols |
| `pipeline_specs.py` | HYDRA ML pipeline specifications |
| `ml_test.py` | ML framework verification tests |
| `ml_platforms/harness.py` | Core execution harness *(see `azazael-ml-platforms` for details)* |
| `ml_platforms/health_monitor.py` | Real-time health monitoring *(see `azazael-ml-platforms` for details)* |
| `ml_platforms/PERMANENT_LOAD.py` | Persistent model loading *(see `azazael-ml-platforms` for details)* |

## ML Platforms (`ORCHESTRATION/ml_platforms/` + `improvements/` — ~40 files)

> **Deep-dive:** See `azazael-ml-platforms` for complete file listing, integration patterns (LM Studio, Q-learning pipeline, ONNX/Ray), and common workflows.

| Area | Scope |
|------|-------|
| **Platform Management** | Launcher, harness, install manager, framework activator, config, diagnostics |
| **LM Studio** | Local LLM serving — client, server, integration, autoload |
| **Analysis** | Cross-platform, JAX, Q-analysis (3 variants), MoE verification |
| **Improvements** | Q-learning (3), ML integrations (MLflow, ONNX, Ray), metrics, utilities |
| **HYDRA ML** | Harness, health monitor, permanent load (HYDRA/ml_platforms/) |

## BIBL Sub-System

| File | Purpose |
|------|---------|
| `bibl_crawler.py` | Biblical analysis crawling (BIBL/ directory) |

## Scripts (`ORCHESTRATION/scripts/` — 16 files)

| File | Purpose |
|------|---------|
| `azazael_cli.py` | Command-line interface |
| `azazael_wsa.py` | WSA (Windows Subsystem for Android) tools |
| `run_tests.py` | Test runner |
| `comprehensive_analysis.py` | Full system analysis |
| `complete_module_analysis.py` | Per-module analysis |
| `bat_analysis.py` | Batch file analysis |
| `consistency_checker.py` | Cross-module consistency |
| `check_links.py` | Link validation |
| `fix_syntax_errors.py` | Syntax error fixing |
| `generate_docstrings.py` | Docstring generation |
| `generate_docs_index.py` | Documentation index generation |
| `improve_bat_files.py` | .bat file improvement |
| `test_enhancements.py` | Test improvements |
| `validate_docs.py` | Documentation validation |
| `web_dashboard.py` | Web-based dashboard |

## Working with ORCHESTRATION

### Import Pattern
```python
import sys; sys.path.insert(0, 'azazael/src')
from ORCHESTRATION import ECOSYSTEM_CRAWLER_LAUNCHER
from ORCHESTRATION.HYDRA import HYDRA_ANALYZER
```

### ML Platform Reference
```python
# See azazael-ml-platforms for full ML platform API
from ORCHESTRATION.ml_platforms.harness import Harness
```

## Related Skills

- `azazael-system-startup` — Startup sequence initializes orchestration dependencies
- `azazael-ml-platforms` — **Deep-dive** into ML platform infrastructure (LM Studio, Q-learning, ONNX, Ray, harness)
- `azazael-utilities` — UTILITIES sub-systems (KLINK, PERSEPHONE, POINDEXTER, TARBABY, TERENCE)
- `azazael-sync-patterns` — Sync infrastructure for propagation
