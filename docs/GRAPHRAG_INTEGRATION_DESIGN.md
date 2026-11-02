# GraphRAG Integration Design

**Task:** Board 46998 / YGGDRASIL-CLEAVE-K3
**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)

## Problem

The codebase has 60,365 nodes and 100,888 edges in graph.json, but search is limited to
keyword matching. GraphRAG would enable symbol-level indexing, bidirectional expansion,
and community-aware retrieval.

## Design

### 1. Symbol-level indexing

Index every code symbol (function, class, method, variable) as a node with:
- `symbol_name`: fully qualified name (e.g., `CORE.failure_ledger.note_failure`)
- `symbol_type`: function | class | method | variable | constant
- `source_file`: file path
- `source_location`: line number
- `community`: detected community name
- `degree`: number of connections

### 2. Bidirectional expansion

When a query matches a node, expand in both directions:
- **Outgoing**: what this node calls/uses/imports
- **Incoming**: what calls/uses/imports this node
- **Community**: other nodes in the same community
- **Hyperedges**: multi-node groupings

Expansion depth: 2 hops (configurable). Each hop adds nodes with decreasing weight.

### 3. Retrieval algorithm

```
query -> embed(query) -> vector search (top 50) -> graph expansion (2 hops) -> rerank -> top 10
```

1. Embed the query using mxbai-embed-large-v1
2. Vector search against the semantic index (top 50 chunks)
3. For each matched chunk, find the corresponding graph node
4. Expand 2 hops in all directions
5. Combine original + expanded nodes
6. Re-rank by: relevance (vector score) * graph_centrality (degree) * community_boost
7. Return top 10 with provenance (which hop, which relation)

### 4. Community-aware retrieval

Nodes in the same community as a high-relevance node get a boost. This enables
"find all code related to X" queries that span multiple files.

### 5. Implementation plan

- Phase 1: Add symbol-level index to graph.json (extend graphify output)
- Phase 2: Implement bidirectional expansion in codegraph_mcp.py
- Phase 3: Add GraphRAG retrieval endpoint to semantic.py
- Phase 4: Test with known queries

### Deliverable checklist

- [x] Design documented
- [x] Symbol-level indexing specified
- [x] Bidirectional expansion specified
- [x] Retrieval algorithm specified
- [x] Implementation plan defined