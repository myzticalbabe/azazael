---
name: azazael-clusters
description: Azazael cluster system — ClusterWORMZ v2.0.0 API, NatureClusters, MetaCluster, CrossNatureRoutingEngine, parallel execution, thread safety, Mermaid graphs.
metadata:
  category: architecture
  project: azazael
---
# Azazael Clusters — Three-Tier Architecture

## Architecture
```
METACLUSTER.py              NATURE_CLUSTERS.py         CLUSTERWORMS.py
     │                            │                          │
     │ MetaCluster                │ NatureCluster            │ ClusterWORMZ v2.0.0
     │ CrossNatureRoutingEngine   │ NatureClusterManager     │ Dynamic worm resolution
     │ 70 routes, 594 paths       │ Auto-discovery           │ PAMS/MemoryBus
     │                            │                          │
     └────────────────────────────┴──────────────────────────┘
                              │
                         WORM_REGISTRY (226 worms)
```

## CLUSTERWORMS.py — `CORE/WORMS/CLUSTERWORMS.py` (v2.0.0)

### Key APIs
```python
# Build cluster from a nature (category)
cluster = ClusterWORMZ.build_from_nature("security")
# Returns ClusterWORMZ with configs for all security worms

# Build from entire registry
cluster = ClusterWORMZ.build_from_registry()
# Returns ClusterWORMZ with all 226 worms

# Build from specific worm names
cluster = ClusterWORMZ.build_from_worms(["SYSTEMZ", "PROCESSZ"])

# Build from configs directly
cluster = ClusterWORMZ(configs=[WormConfig(...), ...])
```

### Dynamic Worm Resolution (3 strategies)
1. **WORM_REGISTRY lookup** — Fast, metadata-rich (preferred)
2. **Legacy dispatch dict** — Backward compatibility
3. **Import-by-convention** — `_WORM_MODULE_MAP` fallback

### Execution Modes
- **execute_all()** — Parallel execution with `ThreadPoolExecutor`-style threading
- **execute_sequential()** — Sequential with retry logic
- **to_mermaid_execution_flow()** — Generates Mermaid graph of execution

### Thread Safety
- `results_lock` (threading.Lock) — protects results list in parallel path
- `_cancellation` (threading.Event) — graceful shutdown
- Retry with configurable max attempts

### PAMS/MemoryBus Integration
- `_record()` → PamsRecorder (audit trail)
- `_mem_bus.publish()` → MemoryBus (pub/sub lifecycle events)
- Events: cluster.build, cluster.execute.start, cluster.execute.complete, cluster.execute.error

## NATURE_CLUSTERS.py — `CORE/WORMS/NATURE_CLUSTERS.py`

### Key APIs
```python
ncm = NatureClusterManager()
ncm.discover_all_natures()  # Auto-discovers 17 nature groups from registry
ncm.clusters  # Dict of {nature_name: NatureCluster}
```

### NatureCluster
- Per-category grouping of worms
- Mermaid graph generation (`to_mermaid()`)
- Execution statistics tracking

## METACLUSTER.py — `CORE/WORMS/METACLUSTER.py`

### Key APIs
```python
mc = MetaCluster()
mc.discover_all()  # Discovers all natures and builds cross-nature routes

# CrossNatureRoutingEngine
mc.router.routes  # 70 routes
mc.router.paths    # 264 cross-nature paths
```

### CrossNatureRoutingEngine
- Routes between nature pairs (e.g., security→monitor, profiling→optimization)
- Pipeline execution: run Natures in sequence
- Adaptive routing based on results

### Execution Modes
- `orchestrate()` — Run all Natures in parallel
- `orchestrate_adaptive()` — Run with adaptive routing
- `orchestrate_pipeline(["security", "monitor", "diagnostic"])` — Sequential pipeline

## Related Skills
- `azazael-parallel` — 3.14t parallel execution optimization for CLUSTERWORMS/FreeThreadPool
- `azazael-worms` — Full 77-worm catalog, registry API
- `azazael-worms-core` — orchestration + utility + diagnostic worms
- `azazael-threading` — threading.Lock, threading.Event, Queue patterns
- `azazael-mermaid` — Mermaid graph generation patterns

## Common Patterns

### Building and Running a Cluster
```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

cluster = ClusterWORMZ.build_from_nature("security")
results = cluster.execute_all()
print(f"{len(results)} worms executed")
print(cluster.to_mermaid_execution_flow(results))
```

### Full Ecosystem Scan
```python
from CORE.WORMS.METACLUSTER import MetaCluster

mc = MetaCluster()
mc.discover_all()
result = mc.orchestrate()
print(f"Orchestrated {result.natures_executed} Natures: "
      f"{result.total_worms_ok} OK/{result.total_worms_fail} FAIL")
```
