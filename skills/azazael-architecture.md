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
    │       ├── CLUSTERWORMS.py     # ClusterWORMZ + flat category dispatch
    │       └── METACLUSTER.py    # MetaCluster orchestrator v2, flat (U3: router deleted)
├── METAWORMS.py              # Deprecation shim → re-exports from METAWORMS_ENRICHED.py
└── METAWORMS_ENRICHED.py     # Canonical enriched worm implementations
```

## Key Numbers
- **226 worms** across **35 categories** (2026-09-14)
- **62%** of worms defined in `ECOSYSTEM_EXPANSION.py`
- **70 routes**, **594 paths** in MetaCluster routing engine
- **300+** syntax-clean Python files (2026-09-16; this read 256)
- **0** spawns on all worms (fresh registry)

## Worm Registry
- `@register_worm` decorator registers worms at import time
- `discover_worms()` scans all `.py` files in `azazael/src/`
- 35 categories, 226 registered worms
- See `azazael-registry` skill for full API details

## Path System
- `get_project_root()` — always returns the azazael project root
- `get_g_drive()` — returns `Optional[Path]`, callers must handle None
- All paths use `pathlib.Path`, dynamic resolution with caching

## Neural Mesh (2026-09-16)

The mesh outgrew this skill's original three-file sketch. Modules added under
`CORE/WORMS/expansion/` during the 2026-09-15/16 audits, each one removing a
specific ceiling the batch model had already hit:

| Module | Removes |
|---|---|
| `fencing.py` | lost-update races between two *instances* of the same engine (process-wide fencing tokens) |
| `silence.py` | the unmeasurability of a bare `pass` in an exception handler (118 existed) |
| `liveness.py` | occurrence-only monitoring -- obligations with deadlines, so an event that *did NOT happen* is observable |
| `cppn.py`, `morph.py`, `nerve.py` | fixed-topology limits |
| `chorus.py`, `loom.py`, `arena.py` | single-strategy execution |
| `fabric_state.py` | operator state that did not survive a restart |

Two new natures (`engram`, `synapse`) are wired into the mesh, and
`CORE/spine_registry.py` (the Q brainstem) gained store tombstones, evidence
classes, evidence-shrunk ranking, and a delta-vs-target split for `record_outcome`.

**Load `azazael-mesh-resilience-primitives` for the four primitives and the method
that produced them**; `NEURAL_MESH_BRAINSTEM_TODO.md` and
`NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md` carry the measurements.

## Related Skills
- `azazael-paths` — Full path resolution API, get_project_root, get_g_drive, all paths
- `azazael-registry` — Worm registry API, @register_worm, discovery
- `azazael-files` — Complete file index and import resolution
- `azazael-threading` — 3.14t threading patterns
- `azazael-worms` — Full worm catalog (**226** worms / 35 categories as of the 2026-09-14 rebuild; this line read "77" and was stale)
- `azazael-mesh-resilience-primitives` — fencing tokens, the silent-failure ledger,
  liveness obligations, store tombstones (2026-09-16)
