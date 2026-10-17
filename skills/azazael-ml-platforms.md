---
name: azazael-ml-platforms
description: ML platform infrastructure — LM Studio integration, Q-learning, ONNX, Ray, harness, diagnostics, health monitoring, model analysis. Covers 44+ files across ORCHESTRATION/ml_platforms, improvements/, and HYDRA.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: true
---

# Azazael ML Platforms — Model Execution & Learning Infrastructure

> **Implementation:** `src/ORCHESTRATION/ml_platforms/`, `src/HYDRA/ml_platforms/`
> **Total files:** ~44 across 3 locations
> **Related skill:** `azazael-orchestration` (parent domain)

---

## File Map

### ORCHESTRATION/ml_platforms/ (26 files)

| Category | Files | Purpose |
|----------|-------|---------|
| **Core** | `__init__.py`, `autoload.py`, `config.py` | Package init, auto-loading, live-lexicon config management |
| **Installation** | `auto_install.py`, `install_manager.py`, `install_improvements.py`, `install_light.py`, `installation_debug.py` | ML platform install, management, debugging |
| **LM Studio** | `lm_studio_client.py`, `lm_studio_server.py`, `lm_studio_integration.py`, `lm_studio_autoload.py` | Local LLM serving via LM Studio (client, server, integration, autoload) |
| **Analysis** | `unified_analysis.py`, `cross_platform_analysis.py`, `jax_analysis.py`, `run_qanalysis.py`, `run_qanalysis_full.py`, `run_qanalysis_multi.py` | Multi-platform analysis, JAX analysis, Q-analysis variants |
| **Framework** | `framework_activator.py`, `harness.py`, `launcher.py` | ML framework activation, test/execution harness, launcher |
| **Utilities** | `changelog.py`, `diagnostics.py`, `universal_converter.py`, `verify_moe.py`, `openinterpreter_startup.py` | Change tracking, diagnostics, format conversion, MoE verification, OpenInterpreter startup |

### ORCHESTRATION/ml_platforms/improvements/ (14 files)

| Category | Files | Purpose |
|----------|-------|---------|
| **Q-Learning** | `deep_learning_qlearning.py`, `enhanced_qlearning.py`, `qlearning_table.py` | Deep learning Q-table, enhanced Q-learning, Q-table module |
| **Integration** | `mlflow_integration.py`, `ml_integration.py`, `onnx_integration.py`, `ray_integration.py` | MLflow tracking, generic ML integration, ONNX model support, Ray distributed compute |
| **Metrics** | `metrics_tracker.py`, `qualitative_improvements.py`, `strategic_intelligence.py` | Quantitative metrics, qualitative improvements, strategic intelligence system |
| **Utilities** | `tensor_utils.py`, `vectorize_utils.py`, `weakness_testing.py`, `__init__.py` | Tensor operations, vectorization, adversarial testing, package init |

### HYDRA/ml_platforms/ (4 files)

| File | Purpose |
|------|---------|
| `__init__.py` | ML Platform Configuration Module (deprecated shim layer) |
| `harness.py` | Test/execution harness for HYDRA ML clusters |
| `health_monitor.py` | ML platform health monitoring |
| `PERMANENT_LOAD.py` | Persistent load operations management |

---

## Key Integration Patterns

### LM Studio Local LLM Serving

```
lm_studio_server.py  ←  lm_studio_client.py  ←  lm_studio_integration.py
                                          ↕
                                 lm_studio_autoload.py (auto-load on startup)
```

**Usage:** LM Studio provides local LLM inference. `lm_studio_client.py` wraps the API, `lm_studio_integration.py` provides higher-level integration, and `lm_studio_autoload.py` ensures the server starts automatically.

### Q-Learning Pipeline

```
qlearning_table.py → enhanced_qlearning.py → deep_learning_qlearning.py
                                 ↓
                        ml_integration.py
                                 ↓
                   mlflow_integration.py (tracking)
```

**Usage:** Start with `qlearning_table.py` for basic Q-tables, use `enhanced_qlearning.py` for improved convergence, and `deep_learning_qlearning.py` for neural-network-backed Q-learning.

### Model Serving & Analysis

```
launcher.py → harness.py → run_qanalysis*.py
                                ↓
            unified_analysis.py + cross_platform_analysis.py
                                ↓
                   universal_converter.py (format conversion)
```

---

## Common Workflows

### Run ML Analysis (Q-analysis)

```python
from ORCHESTRATION.ml_platforms.run_qanalysis import run_analysis
from ORCHESTRATION.ml_platforms.ml_integration import get_model

model = get_model("qlearning")
results = run_analysis(model, iterations=1000)
```

### Start LM Studio Server

```python
from ORCHESTRATION.ml_platforms.lm_studio_server import start_lm_studio
from ORCHESTRATION.ml_platforms.lm_studio_client import query_lm_studio

port = start_lm_studio()  # Auto-start LM Studio server
response = query_lm_studio("prompt", port=port)
```

### Health Check HYDRA ML Platform

```python
from HYDRA.ml_platforms.health_monitor import check_health
from HYDRA.ml_platforms.harness import run_harness_test

status = check_health()  # Returns ML platform health status
run_harness_test()       # Runs full harness test suite
```

---

## Related Skills

- `azazael-orchestration` — **High-level parent** with ORCHESTRATION + HYDRA overview (70+ files). Use this skill for ML platform deep-dive.
- `azazael-inference-protocol` — 12-provider failover for LLM inference
- `azazael-system-startup` — Auto-loads this skill at session start
- `azazael-utilities` — Utility modules (KLINK, PERSEPHONE) used by ML platforms
