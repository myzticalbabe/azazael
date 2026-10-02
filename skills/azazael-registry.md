---
name: azazael-registry
description: Azazael worm registry — @register_worm decorator, WORM_REGISTRY dict, discover_worms(), category management, how to add and register worms.
metadata:
  category: architecture
  project: azazael
---
# Azazael Registry — Worm Registration System

## Core File: `CORE/worm_registry.py`

### Key Global Objects
```python
WORM_REGISTRY: Dict[str, Dict]  # {worm_name: {category, priority, cooldown, ...}}
```

### Key Functions
```python
discover_worms()                           # Scan all .py files, register discovered worms
get_all_categories() -> List[str]           # Returns all 17 category names
get_worms_by_category(cat: str) -> Dict     # Returns worms in a category
```

## @register_worm Decorator

### Signature
```python
@register_worm(
    category: str,          # One of 35 categories (required)
    priority: int,          # 1-10, higher = more important (required)
    cooldown_seconds: float, # Minimum seconds between spawns (required)
    version: str = "0.0.0", # Semver (optional, default "0.0.0")
    description: str = ""   # Human-readable description (optional)
)
```

### Example: Registering a New Worm
```python
from CORE.worm_registry import register_worm

@register_worm(
    category="security",
    priority=6,
    cooldown_seconds=60,
    version="1.0.0",
    description="Scans for vulnerabilities in target directories"
)
class VulnScanner:
    def execute(self) -> Dict:
        """Called by ClusterWORMZ when this worm is executed."""
        try:
            scan_results = self._scan()
            return {"success": True, "data": scan_results}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

    **That's it. No changes needed to CLUSTERWORMS.py or METACLUSTER.py (U3: NATURE_CLUSTERS.py deleted).**

## Discovery Mechanism

`discover_worms()` recursively scans `azazael/src/` for `.py` files:
1. Imports each module
2. Detects classes decorated with `@register_worm`
3. Adds them to `WORM_REGISTRY`
4. Caches results per category

### How CLUSTERWORMS Resolves Worms (3 Strategies)
1. **WORM_REGISTRY lookup** — Fast, metadata-rich (preferred)
2. **Legacy dispatch dict** — Backward compatibility
3. **Import-by-convention** — `_WORM_MODULE_MAP` fallback

## 17 Categories

| Category | Count | Priority Range | Cooldown Range |
|----------|-------|---------------|----------------|
| orchestration | 6 | 3–10 | 5s–30s |
| monitor | 6 | 5–8 | 15s–60s |
| security | 5 | 5–8 | 45s–120s |
| profiling | 5 | 6–7 | 30s–90s |
| telemetry | 5 | 5–7 | 15s–60s |
| container | 5 | 4–6 | 30s–180s |
| communication | 5 | 4–7 | 15s–45s |
| backup | 5 | 4–7 | 30s–300s |
| config | 5 | 4–6 | 30s–120s |
| learning | 5 | 4–6 | 45s–120s |
| migration | 5 | 3–6 | 45s–120s |
| visualization | 5 | 4–5 | 60s–90s |
| utility | 5 | 3–5 | 30s–60s |
| diagnostic | 4 | 4–7 | 30s–60s |
| analysis | 3 | 5–6 | 45s–60s |
| ml | 2 | 5–6 | 45s–60s |
| sync | 1 | 5 | 30s |

## Registry Validation
```python
from CORE.worm_registry import discover_worms, WORM_REGISTRY
discover_worms()
print(f"{len(WORM_REGISTRY)} worms registered")

# Check all worms are importable
for name, info in WORM_REGISTRY.items():
    print(f"  [{info['category']}] {name} v{info['version']} p={info['priority']}")
```

## Key Facts
- **62% of worms (48/77)** from `ECOSYSTEM_EXPANSION.py` — primary worm factory
- **Highest priority**: MetaCluster (p=10, 5s cooldown)
- **4 worms at v0.0.0**: DiagnosticWorm, FastErrorScanner, OSCongruency, WormFleet
- **All worms at 0 spawns** — SpawnDiversityEngine ready but unused

For per-worm details, load skill `azazael-worms-core`, `-monitor`, `-security`, `-devops`, or `-data`.

## Related Skills
- `azazael-worms` — Parent: full 77-worm catalog, category overview
- `azazael-worms-core` — orchestration, utility, diagnostic (15 worms)
- `azazael-worms-monitor` — monitor, profiling, telemetry (16 worms)
- `azazael-worms-security` — security, config, backup (15 worms)
- `azazael-worms-devops` — container, communication, migration (15 worms)
- `azazael-worms-data` — learning, ml, analysis, visualization, sync (16 worms)
    - `azazael-clusters` — CLUSTERWORMS, METACLUSTER consumers
