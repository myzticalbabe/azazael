# Semantic Zoom UX Design

**Task:** Board 47000 / YGGDRASIL-CLEAVE-K5
**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)

## Problem

The 3D graph visualization (graph3d) has no zoom levels. All 60,365 nodes are rendered at
once, making it impossible to navigate. Cognitive load theory suggests limiting visible
information to 7±2 items per view.

## Design: 4 Zoom Levels (C4 Model)

### Level 0: System Context (1-5 nodes)
- Shows only the top-level trees (CORE, CODEX, ORCHESTRATION, etc.)
- Each tree is a single node with size proportional to LOC
- Edges show inter-tree dependencies
- Label: tree name + LOC + file count

### Level 1: Container View (5-20 nodes)
- Shows communities within a selected tree
- Each community is a node with size proportional to member count
- Edges show inter-community connections
- Label: community name + member count

### Level 2: Component View (20-50 nodes)
- Shows files within a selected community
- Each file is a node with size proportional to lines
- Edges show file-level imports/calls
- Label: filename + lines + classes

### Level 3: Code View (50-200 nodes)
- Shows functions/classes within a selected file
- Each symbol is a node
- Edges show call/import relationships
- Label: symbol name + type + line number

## Navigation

- **Scroll wheel**: zoom in/out (changes level)
- **Click**: select a node (drill down one level)
- **Right-click**: go back one level
- **Hover**: show tooltip with node details
- **Search bar**: jump to any node at any level

## Cognitive Load Theory

- Miller's Law: 7±2 items in working memory
- Each zoom level shows 5-20 items (within cognitive capacity)
- Zoom transitions are animated (300ms fade) to maintain spatial context
- Breadcrumb trail shows the zoom path (System > CORE > failure_ledger > note_failure)

## Implementation

- Phase 1: Add zoom level state to graph3d renderer
- Phase 2: Implement level 0 (system context) with tree aggregation
- Phase 3: Implement level 1-3 with community/file/symbol drill-down
- Phase 4: Add search and navigation

## Deliverable checklist

- [x] 4 zoom levels defined (C4 model)
- [x] Navigation controls specified
- [x] Cognitive load theory applied
- [x] Implementation plan defined