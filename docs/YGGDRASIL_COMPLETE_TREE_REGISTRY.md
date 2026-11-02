# Yggdrasil Complete Tree & Domain Registry

**Date:** 2026-10-31
**Purpose:** One mind of all trees — visible to each other across all environments

---

## 1. The 20 Source Trees (src/)

| # | Tree | Modules | Lines | Classes | Functions | Imports From | Imported By | Hub? | Status |
|---|------|---------|-------|---------|-----------|-------------|-------------|------|--------|
| 1 | **CORE** | 337 | 165,991 | 173 | 1,981 | CORE, META, ML, SCRIPTS, UTILITIES, ORCHESTRATION, PSYCHE | 17 trees | ✅ | Active |
| 2 | **CODEX** | 90 | 36,174 | 3 | 0 | CORE, CODEX, ORCHESTRATION, META, UTILITIES | none | ✅ | Active |
| 3 | **ORCHESTRATION** | 84 | 37,505 | 85 | 0 | CORE, ORCHESTRATION | CODEX, HYDRA, CORE | ✅ | Active |
| 4 | **META** | 20 | 10,214 | 79 | 0 | CORE, META | CODEX, CORE, eve_unleashed | ✅ | Active |
| 5 | **UTILITIES** | 22 | 5,684 | 0 | 0 | CORE, eve_unleashed | CODEX, CORE, eve_unleashed | ✅ | Active |
| 6 | **SCRIPTS** | 30 | 7,897 | 13 | 0 | CORE, SCRIPTS | CORE | ✅ | Active |
| 7 | **eve_unleashed** | 21 | 5,866 | 46 | 0 | CORE, META, eve_unleashed, UTILITIES | AOA, UTILITIES | ✅ | Active |
| 8 | **ML** | 9 | 1,188 | 9 | 0 | CORE, ML | CORE, tests | ✅ | Active |
| 9 | **PSYCHE** | 7 | 1,561 | 2 | 0 | CORE, PSYCHE | CORE | ✅ | Active |
| 10 | **INTERPRETERS** | 6 | 2,001 | 12 | 0 | CORE, INTERPRETERS | SHARDS | ✅ | Active |
| 11 | **SHARDS** | 4 | 1,129 | 0 | 0 | CORE, SHARDS, INTERPRETERS | none | ✅ | Active |
| 12 | **AOA** | 30 | 7,304 | 2 | 0 | CORE, eve_unleashed | none | — | Active |
| 13 | **AZAZAEL_TOOLKIT** | 9 | 2,250 | 7 | 0 | CORE | TOOLS | — | Active |
| 14 | **CLI** | 2 | 255 | 1 | 0 | CORE | none | — | Active |
| 15 | **DAEMONS** | 4 | 881 | 1 | 0 | CORE | none | — | Active |
| 16 | **HYDRA** | 11 | 2,692 | 10 | 0 | CORE, ORCHESTRATION | none | — | Active |
| 17 | **TOOLS** | 10 | 2,511 | 10 | 0 | CORE, AZAZAEL_TOOLKIT | none | — | Active |
| 18 | **RENDERING** | 6 | 97 | 0 | 0 | none | none | — | Stub |
| 19 | **SHORTCUTS** | 1 | 2 | 0 | 0 | none | none | — | Stub |
| 20 | **tests** | 13 | 2,052 | 42 | 0 | CORE, ML | none | — | Active |

**Totals:** 20 trees, 716 modules, 293,254 lines, 44 connections, 11 hub trees

---

## 2. The 11 Domain Trees (domain_trees.py)

| # | Domain | Kind | Roots | Description |
|---|--------|------|-------|-------------|
| 1 | **sentinel** | mixed | src/SCRIPTS, src/CORE/compliance | Rules development, compliance, sentinel enforcer |
| 2 | **cain** | code | src/CODEX, src/PSYCHE | CAIN psychoanalysis, video generation |
| 3 | **eve_rani** | code | src/eve_unleashed | Eve Unleashed desktop app |
| 4 | **hives** | code | src/CORE/WORMS | Swarm worms, cluster system |
| 5 | **gosp** | mixed | (files: src/ML/gosp.py, scripts/gosp_parity_check.py, scripts/gosp_rani_integration.py) | GOSP CLI + parity. Evidence dirs: C:/Users/clint/gosp_cli_run, C:/Users/clint/gosp_parity |
| 6 | **ml** | code | src/ML, src/ORCHESTRATION/ml_platforms | Machine learning, neural networks |
| 7 | **shards** | mixed | src/SHARDS | Skill shard repository (1248 shards) |
| 8 | **dev** | stacks | (files: tools/dev_stack_census.py, tools/domain_trees.py) | Deep-learning stacks, all environments. Canon: Ubuntu INTEL_NPU_IGPU_SETUP_GUIDE.md, WORKSPACE_HARDWARE_PROTOCOL.md, TENSORFLOW_BUILD_REPORT.md, UBUNTU_ARCHITECTURE_RECOVERY.md |
| 9 | **edge0** | code | C:/Users/clint/edge0-intel | Edge0 intelligence project (separate repo) |
| 10 | **wraith** | code | src/RENDERING/characters/wraith, src/RENDERING/pipeline | Wraith character rendering |
| 11 | **oxman** | code | src/RENDERING/characters/oxman, src/RENDERING/pipeline | Oxman character rendering |

---

## 3. Environment Locations

| Environment | Path | Python | Status |
|-------------|------|--------|--------|
| **Windows** | C:/Azazael/azazael | 3.15.0rc3 | Primary (this machine) |
| **Ubuntu** | /home/clint/azazael (WSL) | 3.14.x | Synced |
| **Kali** | /root/azazael (WSL) | 3.14.6 | Synced |

### External Projects (not in azazael tree)

| Project | Location | Description |
|---------|----------|-------------|
| edge0-intel | C:/Users/clint/edge0-intel | Edge0 intelligence (separate repo, 100+ Python files) |
| gosp_cli_run | C:/Users/clint/gosp_cli_run | GOSP CLI evidence |
| gosp_parity | C:/Users/clint/gosp_parity | GOSP parity evidence |
| yggdrasil_forest | C:/Users/clint/yggdrasil_forest | Forest clips + atlas JSONs |

---

## 4. Nature-Inspired Communication (All Trees Visible to Each Other)

### Communication Channels (6)

| Channel | Mechanism | Nature Pattern | Trees Using |
|---------|-----------|---------------|-------------|
| **direct_import** | Python `import` | Neural network (synaptic) | All except RENDERING, SHORTCUTS |
| **memorybus** | Shared SQLite (memorybus_queue) | Mycelium (decentralized) | CORE, SCRIPTS, TOOLS |
| **event_bus** | Pub/sub (AOA/core/event_bus.py) | Ant colony (pheromone) | AOA, CORE |
| **graph_traversal** | Codegraph MCP (BFS/DFS) | Slime mold (shortest path) | All (via MCP) |
| **shared_state** | Files on disk | Stigmergy (environment) | All |
| **mcp_tools** | Engram, PMB, codegraph | Symbiosis (mutual benefit) | All |

### Hub Trees (connected to 3+ others)

| Hub | Connections | Role |
|-----|------------|------|
| **CORE** | 17 | The trunk — everything connects here |
| **CODEX** | 5 | Video generation, templates |
| **ORCHESTRATION** | 3 | Task scheduling, swarm |
| **META** | 3 | Agent config, state machine |
| **UTILITIES** | 3 | Helper tools |
| **eve_unleashed** | 4 | Desktop AI app |
| **ML** | 2 | Machine learning |
| **SCRIPTS** | 2 | Fix/build scripts |
| **PSYCHE** | 1 | Psychology |
| **INTERPRETERS** | 1 | Language runners |
| **SHARDS** | 1 | Skill shards |

### Isolated Trees (0 connections)

| Tree | Status | Notes |
|------|--------|-------|
| **RENDERING** | Stub | 6 modules, 97 lines. No imports, no exports. |
| **SHORTCUTS** | Stub | 1 module, 2 lines. No imports, no exports. |
| **CLI** | Active | 2 modules, 255 lines. Only imports CORE. |
| **DAEMONS** | Active | 4 modules, 881 lines. Only imports CORE. |
| **HYDRA** | Active | 11 modules, 2,692 lines. Imports CORE + ORCHESTRATION. |
| **TOOLS** | Active | 10 modules, 2,511 lines. Imports CORE + AZAZAEL_TOOLKIT. |
| **AOA** | Active | 30 modules, 7,304 lines. Imports CORE + eve_unleashed. |
| **SHARDS** | Active | 4 modules, 1,129 lines. Imports CORE, SHARDS, INTERPRETERS. |
| **tests** | Active | 13 modules, 2,052 lines. Imports CORE, ML. |

---

## 5. Nature-Inspired Patterns Applied

| Pattern | Nature Example | Codebase Application |
|---------|---------------|---------------------|
| **Mycelium** | Decentralized fungal network | memorybus (shared SQLite) — all trees read/write shared state |
| **Neural network** | Weighted synaptic connections | Import frequency as edge weights — hot paths emerge |
| **Ant colony** | Pheromone trails | Frequently-used imports get higher weight |
| **Slime mold** | Shortest path optimization | BFS/Dijkstra on dependency graph (codegraph_mcp) |
| **Bee colony** | Scout/worker/forager roles | Scout discovers, worker analyzes, forager aggregates |
| **Stigmergy** | Indirect coordination via environment | File-based markers (.done, .claimed) |
| **Neural plasticity** | Connections strengthen with use | Import weights update based on usage frequency |
| **Symbiosis** | Mutual benefit between species | CORE provides paths/logging/inference to all trees |

---

## 6. Unified Tree Map Files

| File | Location | Description |
|------|----------|-------------|
| UNIFIED_TREE_MAP.json | docs/ | Full tree map (20 trees, 44 connections, environments) |
| UNIFIED_TREE_MAP (v2) | docs/ | Updated with environments + swarm + nature patterns |
| tree_network_3d.json | YGGDRASIL_RENDERS_NEW/ | 3D visualization data (20 nodes, 44 links) |
| domain_trees.py | tools/ | Domain tree declarations (11 domains) |
| unified_tree_map.py | tools/ | Tree map builder |
| nature_swarm.py | tools/ | Swarm coordinator |
| build_tree_network_3d.py | tools/ | 3D network data builder |

---

## 7. All Trees Are Now Visible to Each Other

The unified tree map ensures every tree can see:
- **What other trees exist** (20 trees in the registry)
- **What each tree imports** (imports_from per tree)
- **What imports each tree** (imported_by per tree)
- **How many modules/lines/classes/functions** each tree has
- **What communication channels** each tree uses
- **Which trees are hubs** (connected to 3+ others)
- **Which trees are isolated** (0 connections)
- **Which environment** each tree runs on (Windows/Ubuntu/Kali)

### Communication Protocol

All trees and lanes communicate through 6 channels:
1. **direct_import** — Python imports (44 connections)
2. **memorybus** — Shared SQLite state (memorybus_queue)
3. **event_bus** — Pub/sub (AOA/core/event_bus.py)
4. **graph_traversal** — Codegraph MCP (BFS/Dijkstra)
5. **shared_state** — Files on disk
6. **mcp_tools** — Engram, PMB, codegraph, barta-scrape

### Lane Communication

- **Board:** `python C:/Users/clint/_board.py` (tasks, status, announces)
- **PMB:** `pmb_record_batch` (activities, discoveries)
- **Engram:** `mem_save` (observations, decisions)
- **Shared files:** `docs/`, `tools/`, `YGGDRASIL_RENDERS_NEW/`

---

## 8. Recording

- Engram: observation saved (topic_key: yggdrasil/complete-tree-registry)
- PMB: activity recorded
- Document: YGGDRASIL_COMPLETE_TREE_REGISTRY.md
- Location: C:/Azazael/azazael/docs/
