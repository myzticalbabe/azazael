# Azazael Cluster API Reference

> Auto-generated from source docstrings — reflects v2.2.0 (July 2026)

## Overview

The Azazael cluster system provides three tiers of worm orchestration:

| Tier | Module | Purpose |
|------|--------|---------|
| **Tier 1** | `CLUSTERWORMS` | Coordinated worm collectives with shared state, PAMS recording, Mermaid visualization |
| **Tier 2** | `NATURE_CLUSTERS` | Nature-based worm grouping — auto-discovers worms by category, cross-Nature routing |
| **Tier 3** | `METACLUSTER` | Cluster-of-clusters orchestrator — coordinates multiple NatureClusters with insights |

---

## Tier 1: ClusterWORMZ (`CORE.WORMS.CLUSTERWORMS`)

**Version:** 2.2.0  
**Registered as:** `@register_worm(category="orchestration", priority=8)`  

### Classes

#### `ClusterWORMZ(cluster_type="system")`

Main cluster orchestrator. Builds a cluster of worms, executes them in parallel or sequentially, aggregates results, and generates Mermaid graphs.

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

cluster = ClusterWORMZ("system")
cluster.set_parallel(True)
results = cluster.execute_all()
```

**Constructor:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `cluster_type` | `str` | `"system"` | One of: `system`, `network`, `bibl`, `security`, `analysis`, `validation`, `health`, `full` |

**Key Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `add_worm(name, module, config=None)` | — | Add a worm to the cluster |
| `remove_worm(name)` | — | Remove a worm by name |
| `set_parallel(parallel)` | — | Enable/disable parallel execution |
| `set_timeout(seconds)` | — | Per-worm timeout (default 60s) |
| `set_partial_failure_threshold(threshold)` | — | Min success fraction (0.0 = all must succeed) |
| `execute_all()` | `list[dict]` | Execute all enabled worms, return per-worm results |
| `execute_worm(name)` | `dict \| None` | Execute single worm by name |
| `aggregate_results()` | `ClusterResult` | Aggregate results from state |
| `get_execution_summary()` | `dict \| None` | Last `execute_all()` summary |
| `was_partial_success()` | `bool` | Whether last run was partial success |
| `get_status()` | `dict` | Full cluster status (breakers, PAMS, bus, etc.) |
| `get_summary()` | `dict` | Fast summary (no heavy imports) |
| `to_mermaid(title="")` | `str` | Mermaid graph of cluster structure |
| `to_mermaid_execution_flow()` | `str` | Mermaid flowchart with execution results |
| `to_mermaid_interactions()` | `str` | Mermaid sequence diagram of inter-worm messaging |

**Class Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `build_from_nature(nature)` | `ClusterWORMZ \| None` | Build cluster from a Nature category in the registry |
| `build_from_registry(worms)` | `ClusterWORMZ` | Build from a list of worm names |
| `build_from_worms(worms)` | `ClusterWORMZ` | Alias for `build_from_registry` |
| `build_full_ecosystem()` | `ClusterWORMZ` | Build cluster containing ALL registered worms |

#### `WormConfig` (dataclass)

| Field | Type | Default |
|-------|------|---------|
| `name` | `str` | — |
| `module` | `str` | — |
| `enabled` | `bool` | `True` |
| `priority` | `int` | `0` |
| `timeout` | `int` | `30` |
| `retry` | `int` | `1` |
| `params` | `dict` | `{}` |

#### `ClusterResult` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `cluster_id` | `str` | Unique cluster ID |
| `worm_results` | `dict[str, Any]` | Per-worm results |
| `aggregated_metrics` | `dict[str, float]` | total_duration_ms, success_rate, avg_duration_ms |
| `duration_ms` | `float` | Total wall time |
| `success_count` | `int` | Number of successful worms |
| `failure_count` | `int` | Number of failed worms |
| `partial_failure_threshold` | `float` | Threshold used for status |
| `overall_status` | `str` | `"success"`, `"partial_success"`, or `"failure"` |

#### `ClusterState`

Thread-safe shared state for cluster execution. Manages results, metrics, and inter-worm messaging.

| Method | Description |
|--------|-------------|
| `add_result(worm_name, result)` | Thread-safe result storage |
| `send_message(from_worm, to_worm, data)` | Send inter-worm message |
| `broadcast(data, exclude=None)` | Broadcast to all worms |
| `get_messages(worm_name)` | Get messages for a worm |
| `clear_messages(worm_name=None)` | Clear processed messages |

#### `WormExecutor(name, config, state, cancellation_token=None)`

Executes a single worm with dynamic registry-based resolution.

---

## Tier 2: NatureCluster / NatureClusterManager (`CORE.WORMS.NATURE_CLUSTERS`)

**Version:** 1.0.0  
**Registered as:** `@register_worm(category="orchestration", priority=9)`  

### Classes

#### `NatureCluster(nature)`

Groups worms by their Nature (category) for coordinated execution.

```python
from CORE.WORMS.NATURE_CLUSTERS import NatureCluster

cluster = NatureCluster("security")
cluster.discover_worms()
result = cluster.execute()
```

| Method | Returns | Description |
|--------|---------|-------------|
| `discover_worms()` | `int` | Auto-discover worms from registry, return count |
| `add_worm_manual(name, cls)` | — | Manually add a worm class |
| `set_parallel(enabled)` | — | Enable parallel execution |
| `set_timeout(seconds)` | — | Per-worm timeout |
| `execute(worm_names=None)` | `NatureResult` | Execute all (or subset) of worms |
| `get_status()` | `dict` | Cluster status with breaker stats |
| `get_worm_info()` | `list[dict]` | Detailed info per worm |
| `get_failed_executions(since=0)` | `list[dict]` | Dead letter queue entries |
| `retry_failed_worms(max_retries=2)` | `dict` | Retry all failed worms |
| `clear_failed_executions()` | — | Clear dead letter queue |
| `to_mermaid()` | `str` | Mermaid subgraph for this Nature |

#### `NatureClusterManager`

Manages all NatureClusters across the ecosystem. Scores which Natures need attention based on system state.

```python
from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

ncm = NatureClusterManager()
ncm.discover_all_natures()
results = ncm.execute_priority_natures(max_natures=3)
```

| Method | Returns | Description |
|--------|---------|-------------|
| `discover_all_natures()` | `dict[str, int]` | Discover all, return `{nature: worm_count}` |
| `get_cluster(nature)` | `NatureCluster \| None` | Get or create a cluster |
| `execute_nature(nature, parallel=False)` | `NatureResult \| None` | Execute a single Nature |
| `execute_all_natures(parallel_natures=False, parallel_worms=False)` | `dict[str, NatureResult]` | Execute all Natures |
| `execute_priority_natures(max_natures=3)` | `dict[str, NatureResult]` | Execute top-N by priority score |
| `get_status()` | `dict` | Full manager status |
| `list_all_worms()` | `dict[str, list[str]]` | Worms grouped by Nature |
| `get_cross_nature_routes()` | `list[CrossNatureRoute]` | All routing paths |
| `get_dead_letter_summary(lookback_seconds=3600)` | `dict` | Aggregated DLQ across all natures |
| `retry_all_failed_worms(max_retries=2)` | `dict` | Retry failures across all natures |
| `to_mermaid(include_routes=True)` | `str` | Full Mermaid graph |
| `to_mermaid_functions()` | `str` | Mermaid class diagram |

#### `NatureResult` (dataclass)

| Field | Type |
|-------|------|
| `nature` | `str` |
| `worm_results` | `dict[str, Any]` |
| `success_count` | `int` |
| `failure_count` | `int` |
| `duration_ms` | `float` |
| `started_at` / `completed_at` | `str` (ISO) |
| `cluster_id` | `str` |
| `errors` | `list[str]` |
| `insights` | `list[str]` |

#### `CrossNatureRoute` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `from_nature` | `str` | Source Nature |
| `to_nature` | `str` | Destination Nature |
| `data_mapping` | `dict[str, str]` | Worm result key → input key mappings |
| `description` | `str` | Human-readable description |

### Nature Definitions (`NATURE_DEFINITIONS`)

18 Natures defined with purpose, triggers, `feeds_into` routing, and icons:

| Nature | Icon | Purpose |
|--------|------|---------|
| `analysis` | 🧠 | Code and data pattern analysis |
| `backup` | 💾 | State snapshots, incremental backups |
| `communication` | 📨 | Message brokering, RPC, webhooks |
| `config` | ⚙️ | Config linting, env validation |
| `container` | 📦 | Container lifecycle, image auditing |
| `defense` | 🛡️ | Error detection, security auditing |
| `diagnostic` | 🔍 | Deep system analysis |
| `learning` | 🤖 | RL training, model versioning |
| `migration` | 🚚 | Code migration, dependency upgrades |
| `monitor` | 📊 | Resource monitoring |
| `optimization` | ⚡ | Performance tuning |
| `orchestration` | 🎯 | Worm coordination, spawn management |
| `profiling` | 📈 | Code profiling, bottleneck analysis |
| `repair` | 🔧 | Automated code repair |
| `security` | 🔒 | Vulnerability scanning, port auditing |
| `sync` | 🕐 | Time synchronization |
| `telemetry` | 📡 | Span tracing, metric aggregation |
| `visualization` | 🎨 | Dashboard generation, graph rendering |

---

## Tier 3: MetaCluster (`CORE.WORMS.METACLUSTER`)

**Version:** 1.0.0  
**Registered as:** `@register_worm(category="orchestration", priority=10)`  

### Classes

#### `MetaCluster`

The top-level orchestrator — coordinates multiple NatureClusters with cross-Nature routing and insight generation.

```python
from CORE.WORMS.METACLUSTER import MetaCluster

mc = MetaCluster()
mc.discover_all()
result = mc.orchestrate(natures=["security", "defense", "monitor"])
print(f"Orchestrated {result.natures_executed} Natures: {result.total_worms_ok}OK/{result.total_worms_fail}FAIL")
for insight in result.insights:
    print(f"  {insight}")
```

| Method | Returns | Description |
|--------|---------|-------------|
| `discover_all()` | `dict[str, int]` | Discover all Nature clusters |
| `orchestrate(natures=None, parallel=False, max_natures=0)` | `MetaClusterResult` | Orchestrate Natures end-to-end |
| `orchestrate_nature(nature, parallel=False)` | `MetaClusterResult \| None` | Single-Nature convenience |
| `orchestrate_adaptive(max_natures=5, parallel=False)` | `MetaClusterResult` | Auto-prioritize by system state |
| `orchestrate_full_pipeline(start_nature, parallel=False)` | `MetaClusterResult` | Follow routing graph from Nature |
| `on(hook_name, callback)` | — | Register hook: `pre_nature`, `post_nature`, `on_insight`, `on_error` |
| `get_status()` | `dict` | Full MetaCluster status |
| `get_last_result()` | `MetaClusterResult \| None` | Most recent orchestration result |
| `export_state(filepath="")` | `str` | Export state to JSON |
| `to_mermaid()` | `str` | Full Mermaid graph (delegates to NCM) |
| `to_mermaid_execution_flow(result=None)` | `str` | Execution flow flowchart |
| `to_mermaid_routing_topology()` | `str` | Cross-Nature routing topology |
| `to_mermaid_all_functions()` | `str` | Class diagram of all worms |

#### `MetaClusterResult` (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `orchestration_id` | `str` | Unique run identifier |
| `started_at` / `completed_at` | `str` (ISO) | Timestamps |
| `duration_ms` | `float` | Total wall time |
| `natures_executed` | `int` | How many Natures ran |
| `total_worms_ok` / `total_worms_fail` | `int` | Aggregate worm counts |
| `nature_results` | `dict[str, Any]` | Per-Nature results |
| `routed_data` | `dict[str, Any]` | Cross-Nature routed data |
| `insights` | `list[str]` | Human-readable insights |
| `recommendations` | `list[str]` | Actionable recommendations |
| `cross_nature_paths_used` | `list[str]` | Routing paths activated |
| `errors` | `list[str]` | All errors encountered |

#### `MetaClusterState` (dataclass)

Shared state across a MetaCluster run:

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `str` | Orchestration run ID |
| `phase` | `str` | `idle` → `discovering` → `executing_*` → `analyzing` → `complete` |
| `active_natures` | `set[str]` | Natures being executed |
| `completed_natures` | `set[str]` | Successfully completed |
| `failed_natures` | `set[str]` | Failed during execution |
| `worm_results` | `dict[str, dict]` | `{nature: {worm: result}}` |
| `routed_messages` | `list[dict]` | Cross-Nature messages |
| `events` | `list[dict]` | Event log |
| `metrics` | `dict[str, float]` | Aggregated metrics |

---

## CLI Commands

### `azazael-ctl cluster`

```bash
# Show cluster ecosystem health
azazael-ctl cluster status
azazael-ctl cluster status --json

# List predefined clusters
azazael-ctl cluster list

# List all Nature categories
azazael-ctl cluster natures

# Show dead letter queue (last N hours)
azazael-ctl cluster dead-letter
azazael-ctl cluster dead-letter --lookback 24
```

### Module-level CLIs

```bash
# CLUSTERWORMS
python -m CORE.WORMS.CLUSTERWORMS --type system --execute --parallel
python -m CORE.WORMS.CLUSTERWORMS --list
python -m CORE.WORMS.CLUSTERWORMS --build-nature security --execute
python -m CORE.WORMS.CLUSTERWORMS --discover

# NATURE_CLUSTERS
python -m CORE.WORMS.NATURE_CLUSTERS --execute security --parallel
python -m CORE.WORMS.NATURE_CLUSTERS --execute-all
python -m CORE.WORMS.NATURE_CLUSTERS --execute-priority 3
python -m CORE.WORMS.NATURE_CLUSTERS --mermaid

# METACLUSTER
python -m CORE.WORMS.METACLUSTER --orchestrate security defense monitor
python -m CORE.WORMS.METACLUSTER --adaptive 5
python -m CORE.WORMS.METACLUSTER --pipeline security
python -m CORE.WORMS.METACLUSTER --mermaid-routing
```

---

## Observability

### Structured Logging

All three modules use `CORE.azazael_logging` for JSON-structured logging:

- `CLUSTERWORMS`: `log.info("cluster_execution_started", {...})`, `log.warning("cluster_thread_timeout", {...})`
- `NATURE_CLUSTERS`: `log.info("worm_executing", {...})`, `log.warning("worm_failed", {...})`
- `METACLUSTER`: `log.info("nature_executed", {...})`, `log.error("nature_failed", {...})`

### Metrics (via `CORE.metrics.MetricsRegistry`)

| Metric | Type | Description |
|--------|------|-------------|
| `cluster.executions_total` | Counter | Total cluster executions |
| `cluster.execution_count` | Gauge | Per-cluster run count |
| `cluster.success_rate` | Gauge | Last run success fraction |
| `cluster.duration_ms` | Histogram | Avg per-worm execution time |
| `metacluster.orchestrate.duration_ms` | Gauge | MetaCluster run duration |
| `metacluster.orchestrate.worms_ok` | Gauge | Successful worms |
| `metacluster.orchestrate.worms_fail` | Gauge | Failed worms |
| `metacluster.orchestrate.natures` | Gauge | Natures orchestrated |

### Health Endpoints

- **TCP:** `localhost:18420` — JSON health report
- **Prometheus:** `localhost:18421` — OpenMetrics text format
- **HTTP:** `localhost:9090/health`, `localhost:9090/metrics`

### PAMS Recording

All cluster operations record to PAMS memory for persistent audit trails:
- `cluster_created`, `cluster_built_from_nature`, `nature_config_applied`
- `cluster_execution_started`, `cluster_execution_completed`
- `cluster_thread_timeout`
- `nature_cluster_discovery`, `nature_cluster_executed`
- `nature_manager_discovery`, `nature_manager_executed_all`
- `metacluster_discovery`, `metacluster_orchestrated`, `metacluster_exported`
