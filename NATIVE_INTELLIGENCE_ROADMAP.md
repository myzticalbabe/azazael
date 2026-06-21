# Native Intelligence Artifact — Production Roadmap

> **Generated:** 2026-06-01 | **Based on:** CODEBASE_AUDIT_TODO.md, PRODUCTION_TODO.md, PATH_FORWARD.md, and all azazael skills
> **Scope:** Native Intelligence Artifact production wiring across all agent types, ML/RL/AI learning infrastructure

---

## EXECUTIVE SUMMARY

**Current state:** 77 worms across 17 categories, 239 passing tests, 16 projects on system (33.8 GB total), 0 production deployments.

**Target state:** A self-sustaining Native Intelligence Artifact ecosystem where ML/RL/AI learning worms train from real execution data, agent types are unified under a single architecture, and production wiring enables scheduled, observable, resilient operation.

**Key gap:** Only **2 ML worms** (SYSTEMZ_ML, WORMZ_ML) and **5 learning worms** (RLTrainLoop, DataPipelineWorm, ModelVersioner, FeatureEngineer, ABTestRunner) exist. No production pipeline connects them to real worm execution data.

---

## SECTION 1: COMPLETE TODO REVIEW

### 1.1 Critical Blockers (0/8 complete)

| ID | Item | Est. Hours | Depends On |
|----|------|-----------|------------|
| C1 | Unit tests: CLUSTERWORMS dynamic resolution | 4 | — |
| C2 | Unit tests: NATURE_CLUSTERS discovery | 3 | — |
| C3 | Unit tests: METACLUSTER routing engine | 5 | C1 |
| C4 | Integration tests: parallel execution | 4 | C1 |
| C5 | Integration tests: cross-nature orchestration | 6 | C3 |
| C6 | Mock tests: PAMS/MemoryBus | 2 | — |
| C7 | Regression tests: all 77 worms | 8 | — |
| C8 | Test coverage reporting (pytest-cov, target 60%+) | 2 | C1-C7 |
| CR1 | Timeout handling (daemon threads) | 3 | — |
| CR2 | Partial failure handling (continue vs abort) | 2 | CR1 |
| CR3 | Circuit breaker (exists, untested in production) | 4 | — |
| CR4 | Exponential backoff retry (replaces fixed 0.1s) | 2 | — |
| CR5 | Dead letter queue | 3 | CR3 |
| CF1 | Centralized config (YAML/TOML) | 4 | — |
| CF2 | Environment variable validation | 2 | — |
| CF3 | Per-nature config overrides | 3 | CF1 |

### 1.2 High Priority (2/14 complete)

| ID | Item | Est. Hours | Status |
|----|------|-----------|--------|
| H1 | Profile parallel execution bottleneck | 3 | NOT STARTED |
| H2 | ThreadPoolExecutor instead of raw threads | 4 | NOT STARTED |
| H3 | Cache worm registry lookups | 2 | NOT STARTED |
| H4 | **Lazy-load worm modules** | **DONE** | **Phase 5 (this session)** |
| H5 | Cache Mermaid graph output | 1 | NOT STARTED |
| H6 | Batch PAMS events | 3 | NOT STARTED |
| H7 | PAMS server startup automation | 2 | NOT STARTED |
| H8 | Module-level docstrings | 4 | NOT STARTED |
| H9 | Architecture diagram (Mermaid README) | 2 | NOT STARTED |
| H10 | API reference | 3 | NOT STARTED |
| H11 | Structured logging (JSON) | 4 | NOT STARTED |
| H12 | Metrics export | 4 | H11 |
| H13 | Health check endpoint | 3 | — |
| H14 | Worm registration drift alert | 1 | — |

### 1.3 Medium Priority (0/13 complete)

| ID | Item | Est. Hours |
|----|------|-----------|
| M1 | Registry validation at startup | 2 |
| M2 | Registry versioning | 3 |
| M3 | Worm dependency graph | 4 |
| M4 | Worm health scoring | 3 |
| M5 | Workflow templates | 6 |
| M6 | Workflow DSL | 8 |
| M7 | Conditional routing | 4 |
| M8 | Workflow history and replay | 3 |
| M9 | Install ffmpeg | **DONE** |
| M10 | Full HTML to MP4 pipeline | 2 |
| M11 | Progress bar for video gen | 1 |
| M12 | Multiple output formats | 1 |
| M13 | Batch video generation | 2 |

### 1.4 Low Priority (0/6 complete)

| ID | Item | Est. Hours |
|----|------|-----------|
| L1 | Remove bare except clauses | 3 |
| L2 | Add __all__ to module exports | 2 |
| L3 | Consolidate hardcoded paths | 2 |
| L4 | Web dashboard | 12 |
| L5 | Real-time Mermaid rendering | 4 |
| L6 | Deployment (CLI, Docker, CI/CD) | 8 |

### 1.5 Total Remaining Work

| Priority | Items | Hours |
|----------|-------|-------|
| Critical | 16 | 57 |
| High | 12 | 32 |
| Medium | 12 | 36 |
| Low | 6 | 29 |
| **TOTAL** | **46** | **~154 hours (4-5 weeks FTE)** |

---

## SECTION 2: NATIVE INTELLIGENCE ARCHITECTURE

### 2.1 Three-Layer Intelligence Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LAYER 3: ORCHESTRATION                           │
│  MetaCluster (routing)  →  NatureClusterManager →  CLUSTERWORMS    │
│  46 routes, 264 paths     17 nature groups         Dynamic resolve │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 2: INTELLIGENCE                            │
│  learning (5 worms)  →   ml (2 worms)  →  analysis (3 worms)       │
│  RLTrainLoop          SYSTEMZ_ML        BinaryAnalysis             │
│  DataPipelineWorm     WORMZ_ML          ReverseTools               │
│  ModelVersioner                         ClusterInspector           │
│  FeatureEngineer                                                        │
│  ABTestRunner                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                    LAYER 1: DATA & MEMORY                           │
│  PamsRecorder  →  LocalMemoryStore  →  MemoryBus                    │
│  (audit trail)    (SQLite/FTS5)       (pub/sub events)             │
│  11633 memories   31 sessions          event streams                │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Current ML/RL/AI Worms

| Worm | Type | Priority | Cooldown | What It Does | Status |
|------|------|---------|----------|-------------|--------|
| RLTrainLoop | RL | 6 | 120s | Reinforcement learning training loop | Defined only |
| DataPipelineWorm | Data | 5 | 90s | ETL with caching/batching/validation | Defined only |
| ModelVersioner | MLOps | 5 | 60s | Model version tracking | Defined only |
| FeatureEngineer | Feat. | 5 | 45s | Extraction, normalization, encoding | Defined only |
| ABTestRunner | Testing | 4 | 120s | A/B experiment orchestration | Defined only |
| SYSTEMZ_ML | Anomaly | 6 | 45s | ML anomaly detection for SystemZ | Defined only |
| WORMZ_ML | Prediction | 5 | 60s | Predictive file prioritization | Defined only |

**Critical gap:** All 7 ML/RL/AI worms are **defined but have no implementation** — they exist as registered stubs in `ECOSYSTEM_EXPANSION.py` with `def execute(self): ...` (pass).

### 2.3 Required Intelligence Pipeline

```
Worm Execution Data
       │
       ▼
PamsRecorder / LocalMemoryStore  ←── 11633 memories ready for training
       │
       ▼
DataPipelineWorm  →  FeatureEngineer  →  RLTrainLoop
  (ETL from DB)       (normalize/encode)  (train policies)
       │                    │                    │
       ▼                    ▼                    ▼
  ModelVersioner       Feature Store        Policy Registry
  (version control)    (SQLite-backed)      (per-worm policies)
       │                                        │
       ▼                                        ▼
  ABTestRunner ←────────────────────────── SYSTEMZ_ML / WORMZ_ML
  (A/B compare models)                      (deploy to production)
```

---

## SECTION 3: PRODUCTION WIRING PLAN

### 3.1 Phase 0: Foundation (Weeks 1-2) — CRITICAL

**Goal:** Make the system safe to run unattended

| Step | Task | Hours | Dependencies |
|------|------|-------|-------------|
| 0.1 | Centralized YAML config | 4 | — |
| 0.2 | Environment variable validation | 2 | 0.1 |
| 0.3 | Circuit breaker production wiring | 4 | — |
| 0.4 | Exponential backoff retry | 2 | 0.3 |
| 0.5 | Dead letter queue | 3 | 0.3 |
| 0.6 | Timeout handling for daemon threads | 3 | — |
| 0.7 | Unit tests for cluster modules | 12 | — |
| 0.8 | Integration tests for parallel exec | 4 | 0.7 |
| **Total** | | **34 hours** | |

**Success criteria:** `python run_tests.py` passes 100%, system can run `MetaCluster.orchestrate()` without hanging on thread leaks.

### 3.2 Phase 1: Observability (Weeks 2-3) — HIGH

**Goal:** Know what the system is doing

| Step | Task | Hours | Dependencies |
|------|------|-------|-------------|
| 1.1 | Structured JSON logging | 4 | — |
| 1.2 | Metrics: execution count, duration, success rate | 4 | 1.1 |
| 1.3 | Health check endpoint | 3 | — |
| 1.4 | Worm registration drift alert | 1 | — |
| 1.5 | Batch PAMS events | 3 | — |
| **Total** | | **15 hours** | |

**Success criteria:** Real-time dashboard showing cluster health, execution metrics, and worm registration status.

### 3.3 Phase 2: Intelligence Pipeline (Weeks 3-4) — MEDIUM

**Goal:** ML/RL/AI worms learn from real execution data

| Step | Task | Hours | Dependencies |
|------|------|-------|-------------|
| 2.1 | Implement DataPipelineWorm (ETL from LocalMemoryStore) | 6 | 0.1 |
| 2.2 | Implement FeatureEngineer (normalize worm execution data) | 4 | 2.1 |
| 2.3 | Implement RLTrainLoop (train from real execution history) | 8 | 2.2 |
| 2.4 | Implement ModelVersioner (version control for trained models) | 3 | 2.3 |
| 2.5 | Implement SYSTEMZ_ML (anomaly detection from SystemZ data) | 6 | 2.1 |
| 2.6 | Implement WORMZ_ML (predictive prioritization) | 4 | 2.1 |
| 2.7 | Implement ABTestRunner (A/B compare model versions) | 4 | 2.4 |
| 2.8 | Create feature store (SQLite-backed, per-worm features) | 3 | 2.2 |
| **Total** | | **38 hours** | |

**Success criteria:** 7 ML/RL/AI worms can train from real execution data and produce actionable insights.

### 3.4 Phase 3: Agent Type Wiring (Weeks 4-5) — MEDIUM

**Goal:** Unify all 7 ML/RL/AI worms into production pipeline

```
Agent Type Map:

┌──────────────────────────────────────────────────────────────────────┐
│ REINFORCEMENT LEARNING AGENTS                                       │
│  RLTrainLoop    → trains worm dispatch policies from execution data │
│  ABTestRunner   → A/B tests policy versions in production           │
├──────────────────────────────────────────────────────────────────────┤
│ DATA PIPELINE AGENTS                                                │
│  DataPipelineWorm  → ETL from LocalMemoryStore to ML-ready formats  │
│  FeatureEngineer   → extract, normalize, encode features per worm   │
│  ModelVersioner    → version control for trained models + features  │
├──────────────────────────────────────────────────────────────────────┤
│ PREDICTIVE AGENTS                                                   │
│  SYSTEMZ_ML  → anomaly detection on SystemZ monitoring data         │
│  WORMZ_ML    → predict which files need attention (priority scores) │
├──────────────────────────────────────────────────────────────────────┤
│ EXECUTION LOOP:                                                     │
│  DataPipeline → FeatureEngineer → RLTrainLoop → ModelVersioner     │
│       ↓                                          ↓                  │
│  SYSTEMZ_ML/WORMZ_ML ← ABTestRunner ← Policy Registry              │
│       ↓                                                             │
│  NatureClusterManager → dispatch optimized worms                    │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.5 Phase 4: Deployment (Weeks 5-6) — LOW

| Step | Task | Hours | Dependencies |
|------|------|-------|-------------|
| 4.1 | Single-entry `azazael` CLI | 4 | 3.x |
| 4.2 | Registry validation at startup | 2 | 0.1 |
| 4.3 | Docker container | 4 | 4.1 |
| 4.4 | Scheduled runs (Task Scheduler) | 2 | 4.3 |
| 4.5 | Web dashboard | 12 | 3.x |
| **Total** | | **24 hours** | |

---

## SECTION 4: ML/RL/AI LEARNING ROADMAP

### 4.1 Data Sources Already Available

| Source | Volume | Type | Used For |
|--------|--------|------|----------|
| LocalMemoryStore | 11,633 memories | Execution history | Training data |
| PAMS fallback records | JSON buffer | Session audit | Validation |
| WORM_REGISTRY | 77 entries | Worm metadata | Feature encoding |
| NatureCluster status | 17 clusters | Per-category stats | State representation |

### 4.2 Training Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         TRAINING PIPELINE                            │
│                                                                      │
│  LocalMemoryStore                                                    │
│  │  (query_memories: source, event_type, severity, timestamp)        │
│  ▼                                                                   │
│  DataPipelineWorm.execute()                                          │
│  │  - Filters: last N days, relevant sources                         │
│  │  - Transforms: JSON → flat records                                │
│  │  - Outputs: Pandas DataFrame (or dict list)                       │
│  ▼                                                                   │
│  FeatureEngineer.execute()                                           │
│  │  - Extracts: worm_name, duration_ms, success_rate, error_type     │
│  │  - Normalizes: min-max scaling per feature                        │
│  │  - Encodes: one-hot for categorical (category, severity)          │
│  ▼                                                                   │
│  RLTrainLoop.execute()                                               │
│  │  - State: current cluster state, recent history window            │
│  │  - Action: which worm to dispatch, in which order                  │
│  │  - Reward: execution success, duration reduction, error avoidance │
│  │  - Policy: Q-learning or PPO (starts with random)                │
│  ▼                                                                   │
│  ModelVersioner.execute()                                            │
│     - Saves policy to model_registry/{worm_name}/v{N}                │
│     - Records: training date, data window, reward curve              │
│                                                                      │
│  DEPLOYMENT LOOP:                                                    │
│  ModelVersioner → ABTestRunner → SYSTEMZ_ML / WORMZ_ML               │
│       │              │                  │                            │
│       │              ▼                  ▼                            │
│       │       Production A/B    Anomaly scores / priority scores     │
│       │       (50/50 split)     fed back to NatureClusterManager     │
│       └──────────────────────────────────────────────────────────►   │
│                    Rollback if new policy performs worse              │
└──────────────────────────────────────────────────────────────────────┘
```

### 4.3 ML Library Selection for Python 3.14t

Based on `azazael_314t_optimum.md` findings:

| Component | Choice | Status |
|-----------|--------|--------|
| **NumPy** | 2.4.6 | Works on 3.14t |
| **PyTorch** | 2.12.0 CPU | Works with `PYTHON_GIL=0` |
| **scikit-learn** | Not tested | May need rebuild |
| **Pandas** | Not tested | May have C extension issues |
| **Ollama** | Subprocess bridge | Only working LLM backend |

**Recommended strategy:** Start with pure-Python / NumPy implementations for ML worms, migrate to PyTorch for GPU if it becomes available. Keep Ollama for text-based inference (SMARTDISK reports, dashboard generation).

---

## SECTION 5: AGENT TYPE CATALOG

### 5.1 All Agent Types in Native Intelligence Architecture

| Type | Worms | Purpose | Production Status |
|------|-------|---------|-------------------|
| **Orchestrators** | MetaCluster, NatureClusterManager, ClusterWORMZ | Coordinate execution | Stable, needs tests |
| **Monitors** | SystemZ, PROCESSZ, NETWORXZ, SMARTDISK, DISKZ, METRICZ | System health | Stable |
| **Security** | VulnScanner, PortAuditor, CertMonitor, FirewallAudit, PermissionScanner | Vulnerability detection | Stable |
| **Diagnostics** | ClusterInspector, FastErrorScanner, CodeProfiler, GILContentionProbe | Problem analysis | Stable |
| **ML/RL/AI** | RLTrainLoop, SYSTEMZ_ML, WORMZ_ML, DataPipelineWorm, FeatureEngineer, ModelVersioner, ABTestRunner | Learning, prediction, optimization | **Stubs only** |
| **Analysis** | BinaryAnalysis, ReverseTools, CodeAnalyzer | Data analysis | Stable |
| **Telemetry** | OpenTelemetryTracer, MetricAggregator, EventRouter, SpanTracer, AlertManager | Observability | Stable |
| **Backup** | StateSnapshooter, IncrementalBackup, RecoveryTester, ColdArchivist, DataReplicator | Data protection | Stable |
| **Config** | ConfigLinter, EnvValidator, SecretRotator, FeatureFlagManager, ComplianceChecker | Configuration | Stable |
| **Container** | DockerLifecycle, ComposeValidator, ImageAuditor, RegistryCleaner, K8sHealthChecker | Container management | Stable |
| **Communication** | MessageBroker, RPCClient, WebhookDispatcher, ProtocolNegotiator, IPCManager | Inter-agent messaging | Stable |
| **Migration** | CodeMigrator, DepUpgrader, SchemaVersioner, DataTransformer, ConfigConverter | Code/data migration | Stable |
| **Learning** | RLTrainLoop, DataPipelineWorm, ModelVersioner, FeatureEngineer, ABTestRunner | Training, ETL, MLOps | **Stubs only** |
| **Visualization** | DashboardGen, GraphRenderer, HeatmapBuilder, ReportCompiler, TimelineViz | Data presentation | Stable |
| **Sync** | CLOCKZ | Time sync | Stable |

---

## SECTION 6: RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Python 3.14t breaks scikit-learn/Pandas | High | High | Pure NumPy fallback; Ollama bridge for LLM |
| No GPU available for ML training | Certain | Medium | CPU-only training with PyTorch; smaller models |
| LocalMemoryStore grows unbounded | Medium | Medium | Add purge_old() to scheduled runs |
| Worm execution data format changes | Medium | Low | ModelVersioner tracks schema version |
| Circuit breaker false positives under load | Low | Medium | Tune thresholds per nature |
| No CI/CD = manual deployment errors | High | Medium | Dockerize before production cutover |

---

## APPENDIX A: Quick Reference — Key Files

| File | Purpose |
|------|---------|
| `PRODUCTION_TODO.md` | Full production gap analysis (legacy) |
| `CODEBASE_AUDIT_TODO.md` | Consolidated TODO tracker (canonical) |
| `PATH_FORWARD.md` | Project separation plan |
| `LESSONS_2026-06-01.md` | Lessons from this optimization session |
| `skills/azazael-optimization-session.md` | Lazy import / PAMS cache patterns |
| `skills/azazael-production.md` | Detailed production gap analysis |
| `skills/azazael-worms-data.md` | ML/RL/AI worm catalog |
| `skills/azazael-deploy.md` | Deployment plan (Docker, CLI, scheduling) |
| `skills/azazael-clusters.md` | Three-tier cluster architecture |

## APPENDIX B: Files Modified This Session

| File | Change |
|------|--------|
| `src/CORE/PamsRecorder.py` | `_pams_unreachable` cache + periodic retry |
| `src/CORE/worm_registry.py` | Fast-path dir() loop skip |
| `src/CORE/WORMS/BINARY_ANALYSIS.py` | Split into wrapper + sub-modules |
| `src/CORE/WORMS/BINARY_ANALYSIS_TYPES.py` | NEW |
| `src/CORE/WORMS/BINARY_ANALYSIS_PARSE.py` | NEW |
| `src/CORE/WORMS/BINARY_ANALYSIS_TOOLS.py` | NEW |
| `src/CORE/WORMS/METACLUSTER.py` | Lazy PAMS/MemoryBus |
| `src/CORE/WORMS/CLUSTERWORMS.py` | Lazy PAMS/MemoryBus/breaker/tkinter |
| `src/CORE/WORMS/NATURE_CLUSTERS.py` | Lazy PAMS + breaker |
| `tests/conftest.py` | PAMS cache warm-up fixture |
| `tests/test_binary_analysis_parse.py` | NEW (17 tests) |
| `tests/test_binary_analysis_tools.py` | NEW (28 tests) |
| `tests/test_ncm_integration.py` | NEW (8 tests) |
| `run_tests.py` | Registered new tests |
| `NATIVE_INTELLIGENCE_ROADMAP.md` | THIS DOCUMENT |
| `LESSONS_2026-06-01.md` | NEW |
| `skills/azazael-optimization-session.md` | NEW |
