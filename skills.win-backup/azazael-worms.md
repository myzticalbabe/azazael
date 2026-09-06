---
name: azazael-worms
description: Azazael worm registry — all 95 worms across 18 categories, @register_worm decorator, how to add/register worms, category breakdown, priority/cooldown patterns. Updated July 25, 2026 (Session 20 — stale skill doc refresh).
metadata:
  category: architecture
  project: azazael
---
# Azazael Worms — Registry & Categories

## Worm Registry System

### File: `CORE/worm_registry.py`
- `WORM_REGISTRY` — dict of all 95 registered worms
- `@register_worm(category, priority, cooldown_seconds, version, description)` — decorator
- `discover_worms()` — scans all `.py` files in `azazael/src/` for registered worms
- `get_all_categories()` — returns list of 18 category names
- `get_worms_by_category(cat)` — returns dict of worms in a category

### How to Add a New Worm
```python
from CORE.worm_registry import register_worm

@register_worm(
    category="security",
    priority=6,
    cooldown_seconds=60,
    version="1.0.0",
    description="Scans for vulnerabilities in target directories"
)
class MyNewWorm:
    def execute(self):
        ...
```

That's it. No changes needed to CLUSTERWORMS.py, NATURE_CLUSTERS.py, or METACLUSTER.py — the registry handles discovery.

## Category Breakdown (18 Categories)

| Category | Count | Priority Range | Cooldown Range |
|----------|-------|---------------|----------------|
| orchestration | 6 | 3–10 | 5s–30s |
| monitor | 6 | 5–8 | 15s–60s |
| security | 6 | 5–8 | 45s–120s |
| profiling | 5 | 6–7 | 30s–90s |
| telemetry | 6 | 5–7 | 15s–60s |
| defense | 1 | 5 | 30s |
| container | 5 | 4–6 | 30s–180s |
| communication | 5 | 4–7 | 15s–45s |
| backup | 5 | 4–7 | 30s–300s |
| config | 5 | 4–6 | 30s–120s |
| learning | 9 | 4–6 | 45s–120s |
| migration | 5 | 3–6 | 45s–120s |
| visualization | 7 | 4–5 | 60s–90s |
| utility | 8 | 3–5 | 30s–60s |
| diagnostic | 5 | 4–7 | 30s–60s |
| analysis | 8 | 5–6 | 45s–60s |
| ml | 2 | 5–6 | 45s–60s |
| sync | 1 | 5 | 30s |

## Key Observations

1. **ECOSYSTEM_EXPANSION.py** — primary worm factory (48 worms, now supplemented by expansion modules to 95 total)
2. **Highest priority**: MetaCluster (p=10, 5s cooldown)
3. **Lowest priority**: MemoryBus, MorphingWorm, NatureCluster, PamsRecorder, LegacyShimGen (p=3)
4. **Longest cooldown**: ColdArchivist (300s = 5min) — backup ops
5. **4 worms at v0.0.0**: DiagnosticWorm, FastErrorScanner, OSCongruency, WormFleet (pre-release)
6. **All 95 worms verified spawned** — 95/95 in MetaCluster orchestration (July 2026)

## Important Worms (by category)

### orchestration
- **MetaCluster** (p=10, 5s) — Top priority, cluster-of-clusters orchestrator
- **NatureClusterManager** (p=9, 10s) — Auto-discovers nature groups
- **ClusterWORMZ** (p=8, 20s) — Dynamic worm resolution, Nature-based building

### monitor
- **SystemZ** (p=8, 15s) — Core system monitoring
- **PROCESSZ** (p=7, 15s) — Process manager
- **NETWORXZ** (p=7, 15s) — Network monitoring

### utility
- **MemoryBus** (p=3, 30s) — Pub/sub event bus
- **PamsRecorder** (p=3, 30s) — Session audit trail recorder

Full per-worm config trace: `azazael/WORM_CONFIG_TRACE.md` and `azazael/worm_config_trace.json`

## Related Sub-Skills (Detailed Per-Category Breakdowns)
- `azazael-worms-core` — orchestration + utility + diagnostic worms (19)
- `azazael-worms-monitor` — monitor + profiling + telemetry worms (17)
- `azazael-worms-security` — security + config + backup + defense worms (17)
- `azazael-worms-devops` — container + communication + migration worms (15)
- `azazael-worms-data` — learning + ml + analysis + visualization + sync worms (27)

Also: `azazael-registry` for registry API details, `azazael-clusters` for execution APIs.
