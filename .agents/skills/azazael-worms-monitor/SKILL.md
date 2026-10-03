---
name: azazael-worms-monitor
description: Azazael observability worms — monitor (12), profiling (5), telemetry (6). Load when working with SystemZ, NETWORXZ, PROCESSZ, profiling tools, or telemetry/alerting.
metadata:
  category: architecture
  project: azazael
  parent: azazael-worms
---
# Azazael Worms — Observability (Monitor, Profiling, Telemetry)

## monitor (6 worms) — Priority 5–8, Cooldown 15s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **SystemZ** | 8 | 15.0s | 1.0.0 | SYSTEMZ.py |
| **PROCESSZ** | 7 | 15.0s | 1.0.0 | PROCESSZ.py |
| **NETWORXZ** | 7 | 15.0s | 1.0.0 | NETWORXZ.py |
| OSCongruency | 6 | 30.0s | 0.0.0 | OS_CONGRUENCY.py |
| DISKZ | 5 | 30.0s | 1.0.0 | DISKZ.py |
| SMARTDISK | 5 | 60.0s | 1.0.0 | SMARTDISK.py |

**Key:** SystemZ (p=8) is the anchor — CPU, memory, disk, processes. OSCongruency at v0.0.0 is pre-release. All three Z-suffixed worms (SystemZ, PROCESSZ, NETWORXZ) share the 15s cooldown for real-time monitoring.

### Typical Monitor Pipeline
```python
cluster = ClusterWORMZ.build_from_nature("monitor")
results = cluster.execute_all()  # Parallel — all 15s cooldown
# SystemZ + PROCESSZ + NETWORXZ run simultaneously
```

## profiling (5 worms) — Priority 6–7, Cooldown 30s–90s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **CodeProfiler** | 7 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| **GILContentionProbe** | 7 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| CPUFlameProfiler | 6 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| IOBottleneckFinder | 6 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| MemoryLeakDetector | 6 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** GILContentionProbe is specifically designed for Python 3.14t free-threading diagnostics — lock contention analysis. MemoryLeakDetector uses tracemalloc. All profiling worms are from the single factory file ECOSYSTEM_EXPANSION.py.

## telemetry (5 worms) — Priority 5–7, Cooldown 15s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **SpanTracer** | 7 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| EventRouter | 6 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| MetricAggregator | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| AlertEscalator | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| LogStreamer | 5 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** SpanTracer uses OpenTelemetry-compatible spans. MetricAggregator is Prometheus-style (counter/gauge/histogram). EventRouter is pub/sub with topic routing.

## Observability Stack Architecture

```
monitor (real-time)          profiling (deep-dive)        telemetry (aggregation)
    │                              │                            │
    ├─ SystemZ (CPU/mem)          ├─ CodeProfiler              ├─ SpanTracer (OTel)
    ├─ PROCESSZ (procs)           ├─ GILContentionProbe        ├─ MetricAggregator (Prometheus)
    ├─ NETWORXZ (network)         ├─ CPUFlameProfiler          ├─ EventRouter (pub/sub)
    ├─ DISKZ (disk I/O)           ├─ IOBottleneckFinder        ├─ AlertEscalator
    ├─ SMARTDISK (SMART)          └─ MemoryLeakDetector        └─ LogStreamer
    └─ OSCongruency (Windows)
         │                              │                            │
         └──────────────────────────────┴────────────────────────────┘
                                    │
                            MemoryBus (pub/sub)
                            PamsRecorder (audit)
```

## Usage Pattern

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Real-time health check (monitor only)
cluster = ClusterWORMZ.build_from_nature("monitor")
health = cluster.execute_all()

# Deep profiling run
cluster = ClusterWORMZ.build_from_nature("profiling")
profile = cluster.execute_sequential()  # Sequential — profiling is resource-intensive

# Telemetry aggregation
cluster = ClusterWORMZ.build_from_nature("telemetry")
metrics = cluster.execute_all()
```

## Related Skills
- `azazael-worms` — Full 77-worm catalog, registry API
- `azazael-worms-core` — Orchestration + utility + diagnostic worms
- `azazael-threading` — 3.14t parallel execution patterns
- `azazael-parallel` — Optimized parallel execution for profiling under 3.14t

Total: **16 observability worms** (monitor 6 + profiling 5 + telemetry 5)
