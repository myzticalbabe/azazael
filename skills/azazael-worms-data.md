---
name: azazael-worms-data
description: Azazael data & insight worms — learning (19), ml (2), analysis (17), visualization (7), sync (2). Load when working with ML training, data pipelines, binary analysis, dashboards, or time sync.
metadata:
  category: architecture
  project: azazael
  parent: azazael-worms
---
# Azazael Worms — Data & Insight

## learning (5 worms) — Priority 4–6, Cooldown 45s–120s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **RLTrainLoop** | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DataPipelineWorm | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ModelVersioner | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FeatureEngineer | 5 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ABTestRunner | 4 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** RLTrainLoop (p=6) is the highest-priority learning worm — reinforcement learning training loop. DataPipelineWorm handles ETL with caching/batching/validation. FeatureEngineer does extraction, normalization, one-hot encoding, imputation.

## ml (2 worms) — Priority 5–6, Cooldown 45s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **SYSTEMZ_ML** | 6 | 45.0s | 1.0.0 | SYSTEMZ_ML.py |
| WORMZ_ML | 5 | 60.0s | 1.0.0 | WORMZ_ML.py |

**Key:** SYSTEMZ_ML augments SystemZ with ML-based anomaly detection. WORMZ_ML adds predictive file prioritization to the WORMZ BIBL crawler. Only 2 ML worms — the smallest category.

## analysis (3 worms) — Priority 5–6, Cooldown 45s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **BinaryAnalysis** | 6 | 60.0s | 1.0.0 | BINARY_ANALYSIS.py |
| **ReverseTools** | 6 | 60.0s | 1.0.0 | REVERSE_TOOLS.py |
| ClusterInspector | 5 | 45.0s | 1.0.0 | CLUSTER_INSPECTOR.py |

**Key:** BinaryAnalysis handles PE/ELF analysis, symbols, entropy, disassembly. ReverseTools wraps Ghidra and radare2/r2pipe. ClusterInspector is a multi-file-type analysis system for txt, md, ps1, html.

## visualization (5 worms) — Priority 4–5, Cooldown 60s–90s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **DashboardGen** | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| GraphRenderer | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| HeatmapBuilder | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ReportCompiler | 4 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| TimelineViz | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** DashboardGen auto-generates HTML dashboards from worm metrics. GraphRenderer uses Graphviz for DOT/SVG. ReportCompiler compiles JSON into PDF/HTML with templates. All at priority 4–5 — nice-to-have, not critical.

## sync (1 worm) — Priority 5, Cooldown 30s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **CLOCKZ** | 5 | 30.0s | 1.0.0 | CLOCKZ.py |

**Key:** CLOCKZ is the only sync worm — time synchronization and scheduling. Smallest sub-category at 1 worm.

## Data Pipeline Architecture

```
learning (training)          analysis (inspection)        visualization (presentation)
    │                              │                            │
    ├─ RLTrainLoop (RL)           ├─ BinaryAnalysis            ├─ DashboardGen (HTML)
    ├─ DataPipelineWorm (ETL)     ├─ ReverseTools (RE)         ├─ GraphRenderer (DOT/SVG)
    ├─ ModelVersioner             ├─ ClusterInspector          ├─ HeatmapBuilder
    ├─ FeatureEngineer             │                           ├─ ReportCompiler (PDF/HTML)
    └─ ABTestRunner                │                           └─ TimelineViz (Gantt)
         │                         │                                │
    ┌────┴────┐                    │                                │
    │ ml (2)  │                    │                                │
    │ SYSTEMZ_ML                   │                                │
    │ WORMZ_ML                     │                                │
    └─────────┘                    │                                │
         │                         │                                │
         └─────────────────────────┴────────────────────────────────┘
                                   │
                            sync: CLOCKZ (time)
```

## Usage Pattern

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# ML training pipeline
cluster = ClusterWORMZ.build_from_nature("learning")
training = cluster.execute_sequential()  # Sequential — ML training is resource-heavy

# Binary analysis
cluster = ClusterWORMZ.build_from_nature("analysis")
analysis = cluster.execute_sequential()

# Generate dashboards from results
cluster = ClusterWORMZ.build_from_nature("visualization")
dashboards = cluster.execute_all()

# Time sync (single worm)
from CORE.worm_registry import WORM_REGISTRY
clockz = WORM_REGISTRY["CLOCKZ"]
clockz.execute()
```

## Related Skills
- `azazael-worms` — Full 77-worm catalog, registry API
- `azazael-worms-core` — Orchestration + utility + diagnostic worms
- `azazael-codex` — CODEX video generation, PAMS/MemoryBus
- `azazael-mermaid` — Mermaid graph generation patterns

Total: **16 data & insight worms** (learning 5 + ml 2 + analysis 3 + visualization 5 + sync 1)
