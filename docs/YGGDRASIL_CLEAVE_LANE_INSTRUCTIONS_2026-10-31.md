# Yggdrasil Cleave — Lane Instructions (All 3 Lanes)

**Date:** 2026-10-31
**Prepared by:** opencode lane
**Status:** READY FOR EXECUTION

---

## Overview

The Yggdrasil Cleave is the systematic analysis and visualization of the azazael codebase structure. The goal is to understand all 20 trees, their relationships, and create educational psychological tools that make the codebase visible and comprehensible.

### Current State (measured 2026-10-31)
- **20 trees**, 716 modules, 293,254 lines, 44 connections, 11 hub trees
- **Acceleration stack:** Python + Rust (PyO3 + WASM) + Go + WebGPU
- **Renders:** 11 MP4s in YGGDRASIL_RENDERS_NEW/ (best: WASM 38.7% non-black)
- **Tools:** 9 acceleration tools (Rust, Go, Python)
- **Unified map:** docs/UNIFIED_TREE_MAP.json (all trees visible to each other)

### Nature-Inspired Communication
All trees communicate through 6 channels:
1. **direct_import** — Python import statements (44 connections)
2. **memorybus** — Shared SQLite state (memorybus_queue)
3. **event_bus** — Pub/sub (AOA/core/event_bus.py)
4. **graph_traversal** — Codegraph MCP (BFS/DFS)
5. **shared_state** — Files on disk
6. **mcp_tools** — Engram, PMB, codegraph, barta-scrape

### Environments
- Windows (primary): C:/Azazael/azazael, Python 3.15.0rc3
- Ubuntu (synced): /home/clint/azazael, Python 3.14.x
- Kali (synced): /root/azazael, Python 3.14.6

---

## KILO LANE — Max Inferencing Tasks

These tasks require complex reasoning, architecture decisions, and deep code analysis. Kilo should use max tokens for these.

### Task K1: note_failure Refactoring Strategy
**Priority:** HIGH
**Complexity:** MAX inferencing
**Description:** note_failure has 303 call sites across 18 trees. Any signature change breaks all of them. Design a refactoring strategy that:
- Stabilizes the signature (make it backward-compatible)
- Adds type hints and documentation
- Creates a shim for gradual migration
- Identifies which trees use it most (ORCHESTRATION: 76, CODEX: 74, root: 40)
- Proposes a migration path that doesn't break existing code

**Files to analyze:** src/CORE/*.py (where note_failure is defined), all 303 call sites
**Deliverable:** Architecture document in docs/NOTE_FAILURE_REFACTORING_STRATEGY.md

### Task K2: GNN-Based Tree Boundary Detection
**Priority:** MEDIUM
**Complexity:** MAX inferencing (research + implementation)
**Description:** Replace the hardcoded LIMBS literal in yggdrasil_census.py with automatic tree boundary detection using graph neural networks. Research:
- Heterogeneous GNN for monolith decomposition (arxiv 2508.07486, Mo2oM)
- Soft clustering for overlapping microservices
- How to train on our 750-module codebase
- Integration with existing census tool

**Deliverable:** Research document + prototype in tools/gnn_tree_boundary.py

### Task K3: GraphRAG Integration Design
**Priority:** MEDIUM
**Complexity:** MAX inferencing
**Description:** Design GraphRAG integration for code search. Replace chunk-based embedding with symbol-level graph retrieval. Research:
- Bidirectional graph expansion (arxiv 2601.08773)
- Symbol-level indexing (functions, classes, modules)
- Graph-aware retrieval vs chunk-based embedding
- Integration with semantic.py

**Deliverable:** Design document in docs/GRAPHRAG_INTEGRATION_DESIGN.md

### Task K4: CPG Layer via Joern
**Priority:** MEDIUM
**Complexity:** MAX inferencing
**Description:** Add Code Property Graph layer using Joern for control-flow + data-flow analysis. Research:
- Joern Python support (JavaCC parser)
- CPGQL for pattern mining
- Integration with existing import-graph
- How to mine patterns like "functions that catch exceptions without logging"

**Deliverable:** Research document + integration plan in docs/CPG_JOERN_INTEGRATION.md

### Task K5: Semantic Zoom UX Design
**Priority:** HIGH
**Complexity:** MAX inferencing (UX design)
**Description:** Design semantic zoom for educational psychological tools. Research:
- C4 model (Context→Container→Component→Code)
- Semantic zoom (arxiv 2510.00003)
- Cognitive load theory (intrinsic/germane/extraneous)
- Details on demand (Shneiderman's mantra)
- Design 4 zoom levels with specific content for each

**Deliverable:** UX design document in docs/SEMANTIC_ZOOM_UX_DESIGN.md

### Task K6: Guided Tour Narrative Design
**Priority:** HIGH
**Complexity:** MAX inferencing (educational design)
**Description:** Design guided tour mode for educational psychological tools. Create:
- Narrated walkthrough of the codebase (20 trees)
- Progressive disclosure based on user expertise level
- Quiz questions at each step
- Feedback and reinforcement
- Story arc: "trunk → branches → leaves → roots"

**Deliverable:** Tour script in docs/GUIDED_TOUR_SCRIPT.md

---

## FREEBUFF LANE — Mechanical Tasks

These tasks are well-defined and can be done mechanically. Freebuff should use standard tokens.

### Task F1: Vulture Dead Code Removal
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Remove 58 dead code findings from Vulture report (docs/VULTURE_DEAD_CODE_REPORT_2026-10-31.txt). 18 unreachable code, 19 unused imports, 21 unused variables. Use `vulture --fix` for safe removals, manual review for 60% confidence items.

**Files:** src/CORE/*.py, src/CODEX/*.py, src/TOOLS/*.py, etc.
**Deliverable:** Commit with dead code removed, tests still passing

### Task F2: TODO/FIXME/HACK Triage
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Triage 106 TODO/FIXME/HACK markers in src/. Categorize as: (a) fix now, (b) defer, (c) won't fix. Create tracking document.

**Files:** All src/**/*.py
**Deliverable:** docs/TODO_TRIAGE_2026-10-31.md

### Task F3: Unresolved Import Investigation
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Investigate 73 target-not-found + 54 variable-unresolved imports. Determine if they're stale references, dynamic imports, or conditional imports. Fix or document each.

**Files:** All src/**/*.py
**Deliverable:** docs/UNRESOLVED_IMPORTS_REPORT.md

### Task F4: Temporal Replay Render
**Priority:** LOW
**Complexity:** Standard
**Description:** Create temporal replay render showing codebase evolution over git history. Use git log data to animate node appearance over time. Extend YGGDRASIL_3D_TEMPORAL.html.

**Files:** tools/precompute_force_layout.py, YGGDRASIL_3D_TEMPORAL.html
**Deliverable:** YGGDRASIL_TEMPORAL_REPLAY.mp4 (full git history)

### Task F5: Quiz Mode Implementation
**Priority:** LOW
**Complexity:** Standard
**Description:** Implement quiz mode in the 3D render. "Which tree handles X?" with feedback. Add to semantic render.

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html
**Deliverable:** Updated render with quiz overlay

### Task F6: Annotation System
**Priority:** LOW
**Complexity:** Standard
**Description:** Add annotation system to 3D render. Users can add notes to trees/modules. Persist to localStorage.

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html
**Deliverable:** Updated render with annotation support

### Task F7: WebGPU TSL Migration
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Migrate from WebGL to WebGPU TSL renderer. Requires Three.js r171+ with proper module paths. Fix CORS issues with CDN.

**Files:** YGGDRASIL_3D_WEBGPU_TSL.html
**Deliverable:** Working WebGPU TSL render

### Task F8: WASM SIMD Fix
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Fix wasm-bindgen to export cosine_similarity_simd. Currently compiled but not in JS wrapper. Try alternative attribute or manual WASM binding.

**Files:** src/RUST_WASM/src/lib.rs
**Deliverable:** Working SIMD export in wasm_pkg/

---

## OPENCODE LANE — Integration & Orchestration Tasks

These tasks require integration across multiple systems. OpenCode handles orchestration.

### Task O1: Semantic Zoom Implementation
**Priority:** HIGH
**Complexity:** Standard (integration)
**Description:** Implement semantic zoom in 3D render. Camera distance-based LOD: far (tree name + lines), medium (+imports), close (+modules), very close (source). Use C4 model (Context→Container→Component→Code).

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html, tools/unified_tree_map.py
**Deliverable:** Updated render with semantic zoom

### Task O2: Mini-Map Implementation
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Add mini-map to 3D render showing global context. Corner overlay with simplified tree network.

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html
**Deliverable:** Updated render with mini-map

### Task O3: Category Filters
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Add category filter toggles to 3D render. Show/hide trees by category (Core, Tools, ML, etc.).

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html
**Deliverable:** Updated render with filter panel

### Task O4: Path Finding Highlight
**Priority:** MEDIUM
**Complexity:** Standard
**Description:** Implement shortest path highlighting between two trees. Use Dijkstra on tree graph. Highlight path in 3D render.

**Files:** YGGDRASIL_3D_SEMANTIC_V2.html, tools/unified_tree_map.py
**Deliverable:** Updated render with path finding

### Task O5: Render All Trees to .mp4
**Priority:** HIGH
**Complexity:** Standard
**Description:** Render all improved visualizations as .mp4 for upload. Use CDP screencast capture. Ensure all info visible in video.

**Files:** All HTML renders
**Deliverable:** .mp4 files for all renders

### Task O6: Update MANIFEST.md
**Priority:** LOW
**Complexity:** Standard
**Description:** Update MANIFEST.md with all new renders, tools, and status. Keep index current.

**Files:** YGGDRASIL_RENDERS_NEW/MANIFEST.md
**Deliverable:** Updated manifest

---

## Task Assignment Summary

| Lane | Tasks | Count | Complexity |
|------|-------|-------|------------|
| **Kilo** | K1-K6 | 6 | MAX inferencing |
| **Freebuff** | F1-F8 | 8 | Standard |
| **OpenCode** | O1-O6 | 6 | Standard (integration) |

### Priority Order
1. **K1** (note_failure) — blocks everything else
2. **K5** (semantic zoom UX) — needed for render improvements
3. **O1** (semantic zoom impl) — depends on K5
4. **F1** (dead code removal) — cleanup before cleave
5. **F2** (TODO triage) — cleanup before cleave
6. **K2** (GNN boundary) — research for cleave
7. **K3** (GraphRAG) — research for cleave
8. **K4** (CPG Joern) — research for cleave
9. **K6** (guided tour) — educational content
10. **O5** (render all) — final deliverable

### Files Referenced
- src/CORE/*.py (note_failure, 303 call sites)
- tools/yggdrasil_census.py (LIMBS literal)
- tools/unified_tree_map.py (tree map)
- docs/UNIFIED_TREE_MAP.json (unified map)
- docs/VULTURE_DEAD_CODE_REPORT_2026-10-31.txt (dead code)
- YGGDRASIL_RENDERS_NEW/ (all renders)
- YGGDRASIL_RENDERS_NEW/MANIFEST.md (index)

---

## Communication Protocol

### Hybrid Communication (Nature-Inspired)
Trees communicate through 6 channels:
1. **direct_import** — Python imports (44 connections)
2. **memorybus** — Shared SQLite state
3. **event_bus** — Pub/sub
4. **graph_traversal** — Codegraph MCP
5. **shared_state** — Files on disk
6. **mcp_tools** — Engram, PMB, codegraph

### Lane Communication
- **Board:** `python C:/Users/clint/_board.py` (tasks, status, announces)
- **PMB:** `pmb_record_batch` (activities, discoveries)
- **Engram:** `mem_save` (observations, decisions)
- **Shared files:** `docs/`, `tools/`, `YGGDRASIL_RENDERS_NEW/`

### Status Updates
Each lane posts status to `lane.<lane>.status` after completing each task.
Each lane claims tasks via `python C:/Users/clint/_board.py claim <lane>`.
Each lane retires tasks via `python C:/Users/clint/_board.py done <board_id> "<evidence>"`.

---

## Recording

This document is the master instruction set for the Yggdrasil Cleave.
All lanes should read this before starting work.
All progress should be recorded via PMB and Engram.
All deliverables should be placed in their designated locations.
All .mp4 renders should be placed in YGGDRASIL_RENDERS_NEW/.
