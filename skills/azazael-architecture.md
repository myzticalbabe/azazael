---
name: azazael-architecture
description: Azazael project architecture — worm registry, cluster system, paths, module organization. Load when navigating or modifying the Azazael codebase structure.
metadata:
  category: architecture
  project: azazael
---
# Azazael Architecture

## Project Layout
```
azazael/src/
├── CORE/
│   ├── worm_registry.py      # @register_worm decorator, discover_worms()
│   ├── paths.py              # Centralized path resolution (get_project_root, get_g_drive, etc.)
│   └── WORMS/
│       ├── CLUSTERWORMS.py   # ClusterWORMZ v2.0.0 — dynamic worm resolution, Nature-based
│       ├── NATURE_CLUSTERS.py # NatureCluster + NatureClusterManager with auto-discovery
│       └── METACLUSTER.py    # MetaCluster orchestrator, CrossNatureRoutingEngine
├── METAWORMS.py              # Deprecation shim → re-exports from METAWORMS_ENRICHED.py
└── METAWORMS_ENRICHED.py     # Canonical enriched worm implementations
```

## Key Numbers
- **77 worms** across **17 categories**
- **62%** of worms defined in `ECOSYSTEM_EXPANSION.py`
- **46 routes**, **264 paths** in MetaCluster routing engine
- **256** syntax-clean Python files
- **0** spawns on all worms (fresh registry)

## Worm Registry
- `@register_worm` decorator registers worms at import time
- `discover_worms()` scans all `.py` files in `azazael/src/`
- 17 categories, 77 registered worms
- See `azazael-registry` skill for full API details

## Path System
- `get_project_root()` — always returns the azazael project root
- `get_g_drive()` — returns `Optional[Path]`, callers must handle None
- All paths use `pathlib.Path`, dynamic resolution with caching

## Related Skills
- `azazael-paths` — Full path resolution API, get_project_root, get_g_drive, all paths
- `azazael-registry` — Worm registry API, @register_worm, discovery
- `azazael-files` — Complete file index and import resolution
- `azazael-threading` — 3.14t threading patterns
- `azazael-worms` — Full 77-worm catalog
