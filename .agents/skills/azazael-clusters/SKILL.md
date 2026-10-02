---
name: azazael-clusters
description: Azazael cluster system — ClusterWORMZ v2.0.0 API, MetaCluster v2 flat dispatch, parallel execution, thread safety, Mermaid graphs.
metadata:
  category: architecture
  project: azazael
---
# Azazael Clusters — Flat Dispatch (U3)

## Architecture (U3: flat — the nature middle layer is deleted, D1)
```
METACLUSTER.py                CLUSTERWORMS.py
     │                              │
     │ MetaCluster v2               │ ClusterWORMZ v2.0.0
     │ flat per-category dispatch   │ Dynamic worm resolution
     │                              │ PAMS/MemoryBus
     │                              │
     └──────────────┬───────────────┘
                    │
               WORM_REGISTRY (247 worms, 35 categories)
```

## CLUSTERWORMS.py — `CORE/WORMS/CLUSTERWORMS.py` (v2.0.0)

### Key APIs
```python
# Build cluster from a category
cluster = ClusterWORMZ.build_from_nature("security")
# Returns ClusterWORMZ with configs for all security worms
# (method name kept for compatibility; takes a registry category)

# Build from entire registry
cluster = ClusterWORMZ.build_full_ecosystem()
# Returns ClusterWORMZ with the whole fleet

# Build from specific worm names
cluster = ClusterWORMZ.build_from_registry(["SYSTEMZ", "PROCESSZ"])

# Build from configs directly
cluster = ClusterWORMZ("custom")
cluster.configs = [WormConfig(...), ...]
```

### Dynamic Worm Resolution (3 strategies)
1. **WORM_REGISTRY lookup** — Fast, metadata-rich (preferred)
2. **Legacy dispatch dict** — Backward compatibility
3. **Import-by-convention** — `_WORM_MODULE_MAP` fallback

### Execution Modes
- **execute_all()** — Parallel execution with FreeThreadPool (set_parallel)
- **execute_all(worm_names=[...])** — Subset execution; retired/quarantined skip
- **to_mermaid_execution_flow()** — Generates Mermaid graph of execution

### Thread Safety
- `results_lock` (threading.Lock) — protects results list in parallel path
- `_cancellation` (threading.Event) — graceful shutdown
- Retry with configurable max attempts

### PAMS/MemoryBus Integration
- `_record()` → PamsRecorder (audit trail)
- `_mem_bus.publish()` → MemoryBus (pub/sub lifecycle events)
- Events: cluster.build, cluster.execute.start, cluster.execute.complete, cluster.execute.error

## NATURE_CLUSTERS.py — DELETED (U3/D1)

The 1701-line taxonomy module is gone. Its live behaviors were absorbed:
execution → `ClusterWORMZ.build_from_registry` per category; dead letters →
`DeadLetterQueue.get_dead_letter_summary` / `retry_all_failed_worms`;
ask-owner normalization → `_execute_worm_class`; sweep guard →
`run_mesh_cycle._NO_EXECUTE`; retirement/quarantine enforcement →
`ClusterWORMZ.execute_all` skips.

## METACLUSTER.py — `CORE/WORMS/METACLUSTER.py` (v2.0.0 flat)

### Key APIs
```python
mc = MetaCluster()
mc.discover_all()  # Discovers all registry categories (35) with worm counts

result = mc.orchestrate()  # Runs all categories via ClusterWORMZ each
result = mc.orchestrate_nature("security")  # One category end-to-end
result = mc.orchestrate_adaptive(max_natures=5)  # Top-5 by priority weight
```

### Execution Modes
- `orchestrate()` — Run all categories (requested order, no routing graph)
- `orchestrate_adaptive()` — Top-N by priority weight, circular-infra filtered
- `orchestrate_nature(name)` / `orchestrate_full_pipeline(name)` — One category
- Hooks kept: `pre_nature`, `post_nature`, `on_insight`, `on_error`

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
print(f"Orchestrated {result.natures_executed} categories: "
      f"{result.total_worms_ok} OK/{result.total_worms_fail} FAIL")
```
