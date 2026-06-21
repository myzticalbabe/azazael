---
name: azazael-worms-core
description: Azazael core infrastructure worms — orchestration (6), utility (5), diagnostic (4). Load when working with CLUSTERWORMS, MetaCluster, PAMS/MemoryBus, or diagnostic tools.
metadata:
  category: architecture
  project: azazael
---
# Azazael Worms — Core Infrastructure

## orchestration (6 worms) — Priority 3–10, Cooldown 5s–30s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **MetaCluster** | 10 | 5.0s | 1.0.0 | METACLUSTER.py |
| **NatureClusterManager** | 9 | 10.0s | 1.0.0 | NATURE_CLUSTERS.py |
| **ClusterWORMZ** | 8 | 20.0s | 2.0.0 | CLUSTERWORMS.py |
| ConcurrencyManager | 7 | 20.0s | 1.0.0 | CONCURRENCY.py |
| WormFleet | 6 | 30.0s | 0.0.0 | WORM_FLEET.py |
| NatureCluster | 3 | 20.0s | 1.0.0 | NATURE_CLUSTERS.py |

**Key:** MetaCluster (p=10) is the highest-priority worm in the entire ecosystem. ClusterWORMZ at v2.0.0 is the most recently upgraded.

## utility (5 worms) — Priority 3–5, Cooldown 30s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| WORMZ | 5 | 60.0s | 1.0.0 | WORMZ.py |
| OMNIV2 | 4 | 60.0s | 2.0.0 | OMNI_WORM_V2.py |
| MemoryBus | 3 | 30.0s | 1.0.0 | MemoryBus.py |
| PamsRecorder | 3 | 30.0s | 1.0.0 | PamsRecorder.py |
| MorphingWorm | 3 | 30.0s | 1.0.0 | MORPHING_WORM.py |

**Key:** MemoryBus (pub/sub) and PamsRecorder (audit trail) are the dual memory systems used by all cluster operations. OMNIV2 and MorphingWorm are environment analysis tools.

## diagnostic (4 worms) — Priority 4–7, Cooldown 30s–60s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| NetworkDiag | 7 | 30.0s | 1.0.0 | NETWORK_DIAG.py |
| DiagnosticWorm | 5 | 60.0s | 0.0.0 | DIAGNOSTIC_WORM.py |
| FastErrorScanner | 4 | 45.0s | 0.0.0 | ERROR_SCAN_WORM.py |
| MorphingWormV2 | 4 | 45.0s | 2.0.0 | MORPHING_WORM_V2.py |

**Key:** Two worms still at v0.0.0 (DiagnosticWorm, FastErrorScanner) — pre-release. NetworkDiag is the highest-priority diagnostic.

## Usage Pattern
```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Run all orchestration worms
cluster = ClusterWORMZ.build_from_nature("orchestration")
results = cluster.execute_sequential()

# Run diagnostic scans
cluster = ClusterWORMZ.build_from_nature("diagnostic")
results = cluster.execute_sequential()

# Run utility infrastructure
cluster = ClusterWORMZ.build_from_nature("utility")
results = cluster.execute_sequential()
```

Total: **15 core infrastructure worms** (orchestration + utility + diagnostic)
