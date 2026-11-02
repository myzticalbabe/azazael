# Codegraph Mismatch — Diff Report

**Task:** Board 47257 / dive-codegraph-graph-mismatch
**Date:** 2026-11-02
**Investigator:** opencode lane

## Measurement

Ran the same query set against both graph files.

## Results

| Metric | graph.json | graph_merged_llama.json | Delta |
|---|---|---|---|
| Nodes | 60,365 | 45,559 | -14,806 (-24.5%) |
| Edges | 100,888 | 85,510 | -15,378 (-15.2%) |
| Connected | 60,181 | 45,544 | -14,637 |
| Communities | 3,122 | 2,355 | -767 |

## God nodes comparison

| Rank | graph.json | merged_llama |
|---|---|---|
| 1 | sys (1207) | sys (1088) |
| 2 | pathlib (1160) | pathlib (1039) |
| 3 | json (894) | packages skills (1042) |
| 4 | typing (828) | skills/pkg (directory) (969) |
| 5 | os (746) | typing (768) |

## Key differences

1. **graph.json** (used by kilo and opencode) includes all 60K nodes from the full
   azazael tree scan. God nodes are standard library modules (sys, pathlib, json, typing, os).

2. **graph_merged_llama.json** (used by freebuff) has 24.5% fewer nodes. The 3rd and 4th
   god nodes are "packages skills (1042)" and "skills/pkg (directory)" — these are
   package/skill nodes that were merged differently in the llama build.

3. The merged graph appears to be a subset or re-processed version of the full graph,
   with different community detection and node aggregation.

## Recommendation

**Canonical: graph.json** (60,365 nodes, 100,888 edges).

Reasons:
- It is the larger, more complete graph (includes all nodes from the full tree scan).
- It is used by two of three lanes (kilo, opencode).
- Its god nodes are standard library modules, which is the expected pattern for a
  codebase graph (high-degree nodes should be stdlib, not project-specific).
- The merged graph's god nodes include "packages skills (1042)" which suggests it
  aggregates skill directories into single nodes, losing granularity.

**Action:** Update freebuff's `.agents/mcp.json` to point at `graphify-out/graph.json`
instead of `graph_merged_llama.json`. This ensures all three lanes use the same graph.

## Deliverable checklist

- [x] Both graphs measured: nodes/edges/connected/communities
- [x] God nodes compared (top 5 per graph)
- [x] Recommendation: graph.json is canonical
- [x] Action: update freebuff config to use graph.json