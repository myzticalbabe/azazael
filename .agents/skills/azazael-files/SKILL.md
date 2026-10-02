---
name: azazael-files
description: Azazael file index — complete module map, what lives where, import resolution, key files by function, file sizes and purposes.
metadata:
  category: architecture
  project: azazael
---
# Azazael Files — Complete Module Index

## Project Structure
```
azazael/
├── src/
│   ├── CORE/
│   │   ├── worm_registry.py          # @register_worm, discover_worms(), WORM_REGISTRY
│   │   ├── paths.py                  # Centralized path resolution
│   │   ├── WORMS/
│   │   │   ├── CLUSTERWORMS.py       # ClusterWORMZ v2.0.0 — dynamic resolution
    │   │   │   ├── CLUSTERWORMS.py       # ClusterWORMZ + ClusterWORMZ flat dispatch
│   │   │   ├── METACLUSTER.py        # MetaCluster orchestrator (70 routes, 594 paths)
│   │   │   ├── ECOSYSTEM_EXPANSION.py # 48 worms (62% of all worms)
│   │   │   ├── WORM_FLEET.py         # WormFleet (v0.0.0, p=6)
│   │   │   └── ...other worm files
│   ├── METAWORMS.py                  # Deprecation shim → METAWORMS_ENRICHED.py
│   ├── METAWORMS_ENRICHED.py         # Canonical enriched worm implementations
│   ├── ERRORZ.py                     # Error tracking worm
│   ├── TRIMZ.py                      # File trimming utility
│   ├── PamsRecorder.py               # Session audit trail (p=3)
│   ├── MemoryBus.py                  # Pub/sub event bus (p=3)
│   ├── CODEX/
│   │   ├── VIDEOS/                   # 6 active video generation scripts
│   │   ├── TESTING/                  # Test files
│   │   └── CORE/                     # CODEX core utilities
│   ├── ORCHESTRATION/                # Orchestration scripts and tests
│   └── META/                         # Meta-level utilities (DebugZ, InferenceBridge)
├── worm_config_trace.json            # Machine-readable worm config dump
├── MEMORIES.md                       # Canonical anti-pattern catalog
├── ERROR_LOG.md                      # 15+ errors with cause/fix/prevention
├── SYSTEM_INSTRUCTIONS.md            # Mandatory error recording SOP
├── PRODUCTION_TODO.md                # Production readiness roadmap
├── WORM_CONFIG_TRACE.md              # Per-worm config audit (226 worms)
└── AZAZAEL_INSIGHTS.md               # Architecture deep-dive
```

## Key Files by Function

### Registry & Discovery
| File | Purpose |
|------|---------|
| `CORE/worm_registry.py` | Decorator, registry dict, discovery scan |
| `ECOSYSTEM_EXPANSION.py` | 48 worm definitions (primary factory) |

### Cluster System
| File | Purpose |
|------|---------|
| `CORE/WORMS/CLUSTERWORMS.py` | Dynamic worm resolution, parallel execution |
| `CORE/WORMS/CLUSTERWORMS.py` | Category execution, Mermaid graphs |
| `CORE/WORMS/METACLUSTER.py` | Cross-nature routing, pipeline execution |

### Memory Systems
| File | Purpose |
|------|---------|
| `PamsRecorder.py` | Session audit trail (p=3) |
| `MemoryBus.py` | Pub/sub event bus (p=3) |

### Paths & Config
| File | Purpose |
|------|---------|
| `CORE/paths.py` | `get_project_root()`, `get_g_drive()`, etc. |
| `ERRORZ.py` | Error tracking, `_LOCAL_TARGETS` config |
| `TRIMZ.py` | File trimming, `_LOCAL_TARGETS` config |

### Deprecation
| File | Purpose |
|------|---------|
| `METAWORMS.py` | Deprecation shim → re-exports from enriched |
| `METAWORMS_ENRICHED.py` | Canonical enriched worm implementations |

## Related Skills
- `azazael-paths` — Path resolution (get_project_root, get_g_drive, all paths)
- `azazael-registry` — Worm registry API, @register_worm, discovery
- `azazael-architecture` — High-level project layout and key numbers

## Import Resolution
- All imports use `sys.path.insert(0, 'azazael/src')` to add src to path
- Project imports: `from CORE.worm_registry import register_worm`
- Cluster imports: `from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ`

## Documentation Files (Must Read at Startup)
| File | Size | Purpose |
|------|------|---------|
| `MEMORIES.md` | 4.4 KB | Canonical memory, anti-patterns |
| `ERROR_LOG.md` | 10.7 KB | Error ledger (15 entries) |
| `SYSTEM_INSTRUCTIONS.md` | 4.6 KB | Error recording SOP |
| `PRODUCTION_TODO.md` | 4.8 KB | Production gaps, effort estimates |
| `WORM_CONFIG_TRACE.md` | 8.7 KB | Per-worm config audit |
| `AZAZAEL_INSIGHTS.md` | 11.2 KB | Architecture deep-dive |
