---
name: azazael-inference-integration
description: Azazael inference integration — 10-point strategy, P0-P2 implementations (MetaCluster LLM insights, adaptive routing, InferenceSubscriberWorm), audit findings. Load when wiring inference into existing systems or extending integration coverage.
metadata:
  category: architecture
  project: azazael
  parent: azazael-inference
  created: 2026-06-06
---
# Azazael Inference Integration — Strategy & Implementation

## Overview

Strategy for wiring the 11-provider inference system into Azazael's existing 77-worm ecosystem. 10 integration points identified, P0-P2 implemented in the June 2026 buildout session.

## Strategy Document

Full strategy: `azazael/docs/INFERENCE_INTEGRATION_STRATEGY.md`

## Implemented (P0-P2)

### P0: MetaCluster LLM Insights (v1.1.0)
**File:** `CORE/WORMS/METACLUSTER.py`
- `_get_inference()` — lazy-loads InferenceWorm
- `_llm_analyze_results()` — generates 3 insights + 2 recommendations via LLM
- Wired into `orchestrate()` Phase 4: LLM insights prepended to template insights
- Non-breaking, best-effort (falls back to template insights gracefully)

### P1: Intelligent Cross-Nature Routing
**File:** `CORE/WORMS/CROSS_NATURE_ROUTER.py`
- `analyze_routing()` — LLM-adaptive Nature routing
- `_get_inference()` — module-level lazy singleton (double-checked locking)
- Replaces static `feeds_into` chains with LLM-analyzed routing decisions
- Falls back to static routes if inference unavailable

### P2: MemoryBus Inference Subscriber
**File:** `CORE/WORMS/INFERENCE_SUBSCRIBER.py` (v1.0.0)
- Registered worm (category: analysis, p=5, cooldown 30s)
- Subscribes to `cluster.>`, `nature.>`, `inference.>` on MemoryBus
- Dual analysis: quick statistical checks + LLM deep analysis
- Publishes alerts to `inference.alert` topic
- Thread-safe event buffer with configurable capacity

## Not Yet Implemented (P3-P10)

| # | System | Value | Effort |
|---|--------|-------|--------|
| P3 | ClusterWORMZ LLM aggregation | Natural language summaries | Low |
| P4 | PAMS Insight Analyzer | Cross-session pattern detection | Medium |
| P5 | Security Audit LLM | Actionable security reports | Low |
| P6 | Diagnostic LLM Power | Root cause analysis | Medium |
| P7 | Dashboard LLM Content | Narrative dashboards | Low |
| P8 | Healing LLM Decision | Smarter auto-remediation | Medium |
| P9 | ClusterOptimizer LLM | Adaptive concurrency tuning | Low |
| P10 | CLOCKZ Scheduling LLM | Optimized task scheduling | Low |

## Architecture

```
InferenceWorm (p=7) ──→ MetaCluster._llm_analyze_results()
     │                      └── enrich orchestration insights
     ├──→ CrossNatureRoutingEngine.analyze_routing()
     │        └── adaptive Nature routing
     ├──→ InferenceSubscriberWorm (p=5)
     │        └── MemoryBus anomaly detection
     └──→ Future: P3-P10 integrations
```

## Usage

```python
# MetaCluster now auto-enriches insights
mc = MetaCluster()
mc.discover_all()
result = mc.orchestrate(natures=["security", "monitor"])
# result.insights now includes LLM-generated analysis

# Adaptive routing
router = CrossNatureRoutingEngine()
routing = router.analyze_routing(
    execution_results={"security": {"success_count": 4, "failure_count": 1}},
    available_natures=["defense", "monitor", "profiling"]
)
# routing["suggested_next"] → LLM-recommended Natures

# Anomaly detection subscriber
sub = InferenceSubscriberWorm()
sub.start()  # Begins listening to MemoryBus
# ... cluster operations happen ...
alerts = sub.get_alerts()
sub.stop()
```

## Related Skills
- `azazael-inference` — Parent: multi-provider inference system
- `azazael-inference-worms` — InferenceWorm and NimInferenceWorm
- `azazael-inference-providers` — 11-provider registry
- `azazael-clusters` — ClusterWORMZ, NatureClusters, MetaCluster
- `azazael-codex` — PAMS/MemoryBus memory systems
