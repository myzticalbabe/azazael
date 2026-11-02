# Yggdrasil Cleave — Forensic AST Audit & Creative Adaptations Report

**Date:** 2026-10-31
**Auditor:** OpenCode agent (opencode lane)
**Scope:** Full azazael codebase (src/ tree, 750 modules, 20 trees, 311,605 lines)

---

## 1. Codebase Scale (measured)

| Metric | Value |
|--------|-------|
| Trees | 20 |
| Modules (src) | 750 |
| Modules (archive) | 210 |
| Loose modules (no tree) | 43 |
| Lines (src) | 311,605 |
| Classes | 1,396 (1,365 public) |
| Functions | 1,981 |
| Methods | 6,625 |
| Public API | 3,346 |
| Silence guards | 1,224 |
| Entry points (__main__) | 397 |
| Parse failures | 0 |
| Worms | 224 (37 categories, 208 under CORE) |
| Skills (shards) | 1,248 (1,246 dirs + 2 loose) |

---

## 2. Tier Analysis (census-derived)

### Tier A — Cleave Today (clean, no shims needed)
| Tree | Modules | Lines | Status |
|------|---------|-------|--------|
| DAEMONS | 3 | 876 | Clean |
| SHARDS | 4 | 1,125 | Clean |
| tests | 13 | 2,039 | Clean |

### Tier B — Needs Shim (inbound dependencies)
| Tree | Inbound (any) | Inbound (module) | Importers |
|------|---------------|-------------------|-----------|
| CORE | 17 | 6 | 17 trees |
| META | 3 | 0 | 3 |
| ORCHESTRATION | 3 | 1 | 3 |
| UTILITIES | 3 | 1 | 3 |
| ML | 2 | 2 | 2 |
| eve_unleashed | 2 | 0 | 2 |
| AZAZAEL_TOOLKIT | 1 | 1 | 1 |
| INTERPRETERS | 1 | 1 | 1 |
| PSYCHE | 1 | 0 | 1 |
| SCRIPTS | 1 | 0 | 1 |

### Tier D — Stub (minimal implementation)
| Tree | Modules | Lines |
|------|---------|-------|
| RENDERING | 3 | 88 |
| SHORTCUTS | 1 | 1 |

### Mixed-Language (unaudited for non-Python)
| Tree | Python | Other |
|------|--------|-------|
| AOA | 30 | html: 2 |
| CLI | 2 | powershell: 1, shell: 1 |
| CODEX | 87 | html: 130, javascript: 61, batch: 7 |
| HYDRA | 11 | batch: 2 |
| TOOLS | 10 | batch: 2 |

### Self-Contained Units (cleavable_now = true, self_contained = true)
- CORE/parallel (1 module, 501 lines, 6 classes)
- CODEX/DOCUMENTATION (1 module, 1 line)
- CORE/WORMS/expansion/generated (1 module, 18 lines)
- RENDERING/characters/oxman (1 module, 17 lines)
- RENDERING/characters/wraith (1 module, 18 lines)
- RENDERING/pipeline (1 module, 53 lines)
- SHORTCUTS (1 module, 1 line)
- UTILITIES (1 module, 1 line)

---

## 3. Gaps Identified (forensic)

### 3.1 Missing __init__.py (9 directories)
These directories contain .py files but lack __init__.py, relying on namespace packages:
1. `src/CODEX/comprehensive` (6 modules)
2. `src/CODEX/POPUPS` (9 modules)
3. `src/CODEX/SESSION_TEMPLATE/generators` (5 modules)
4. `src/CORE/parallel` (1 module)
5. `src/CORE/WORMS/expansion/generated/_staging` (1 module)
6. `src/DAEMONS` (3 modules)
7. `src/RENDERING/characters/oxman` (1 module)
8. `src/RENDERING/characters/wraith` (1 module)
9. `src/RENDERING/pipeline` (1 module)

**Impact:** Namespace packages work but break certain tooling (pytest discovery, mypy, packaging). Should be fixed for any tree that will be cleaved independently.

### 3.2 TODO/FIXME/HACK Markers (106 total)
- 12 FIXME markers (known defects)
- 20 HACK markers (workarounds)
- 74 TODO markers (planned work)

**Impact:** These represent known technical debt. Should be triaged before cleaving.

### 3.3 Unresolved Imports
| Category | Count | Meaning |
|----------|-------|---------|
| external-package | 127 | Third-party packages not installed or not scanned |
| target-not-found | 73 | Import targets that don't exist in the tree |
| variable-unresolved | 54 | Dynamic/conditional imports (import *) |
| outside-src | 4 | Imports from outside src/ |

**Impact:** 73 target-not-found suggests stale references or dynamic imports. These should be investigated before cleaving — a cleaved tree with broken imports is not independently runnable.

### 3.4 Single-Point-of-Failure: note_failure
- **303 call sites** across 18 trees all import `note_failure` from CORE
- Dominates symbol interop: 76 (ORCHESTRATION) + 74 (CODEX) + 40 (root) + 29 (AOA) + 29 (SCRIPTS) + 22 (eve_unleashed) + 19 (META) + 14 (UTILITIES) + 12 (tests) + 10 (HYDRA) + 9 (ML) + 9 (TOOLS) + 8 (AZAZAEL_TOOLKIT) + ...

**Impact:** Any change to note_failure's signature breaks 303 call sites. This is the #1 coupling point in the codebase. Should be stabilized or refactored before cleaving.

### 3.5 Silent Trees (no mycelium presence)
- RENDERING and SHORTCUTS have 0 mycelium hub sites
- These trees are completely isolated from the ecosystem's cross-cutting concerns

**Impact:** Either these are truly standalone (good for cleaving) or they're dead code (should be removed).

### 3.6 Mycelium Hub Concentration
| Hub | Trees | Sites |
|-----|-------|-------|
| audit | 12 | 1,726 |
| inference | 11 | 1,024 |
| paths | 16 | 588 |
| pams | 8 | 766 |
| worm_registry | 5 | 446 |
| memorybus | 3 | 244 |

**Impact:** audit and inference are the most cross-cutting concerns. Cleaving any tree that depends on these requires either including them as dependencies or creating shims.

### 3.7 Sapling Inventory
- 31 saplings from src, 40 with archive
- 24 per-limb (shard slots)
- 6 shard slots remain in src

**Impact:** 6 remaining shard slots suggest the shard system is nearly full. New capabilities may need a new shard allocation strategy.

### 3.8 Cross-Language Coverage
- Only 1 cross-language edge (CODEX batch->python)
- 127 external-package + 4 outside-src unresolved imports
- CODEX tree has 130 HTML + 61 JS files that are NOT analyzed by the Python-only AST census

**Impact:** The entire CODEX tree's web assets are invisible to the cleave analysis. Tree-sitter would fix this.

### 3.9 Loose Modules
- 43 src/*.py modules belong to no tree
- These are orphaned at the root level

**Impact:** Should be assigned to trees or extracted as standalone modules.

---

## 4. Creative Adaptations (web-searched, genuinely usable)

### 4.1 Code Property Graphs (CPG)
**Source:** Joern (joern.io), arxiv 2603.24837 (codebadger)
**What:** Unified graph combining AST + CFG (control flow) + PDG (program dependence). Enables taint analysis, vulnerability detection, pattern mining.
**Applicability:** Our census only does import-graph analysis. CPG would add control-flow and data-flow analysis, enabling deeper gap detection. The audit hub (1,726 sites) is a natural CPG consumer.
**Effort:** Medium — Joern supports Python via JavaCC parser. Could integrate as a new tier in the census.

### 4.2 Tree-sitter (multi-language parsing)
**Source:** tree-sitter.github.io, arxiv 2603.27277 (codebase-memory)
**What:** Incremental parsing for 27+ languages. Cross-file dependency graphs. 90% token reduction for LLM context.
**Applicability:** Our AST census is Python-only. Tree-sitter would analyze CODEX's 130 HTML + 61 JS files, CLI's PowerShell scripts, HYDRA's batch files. The codebase-memory paper shows 92% accuracy on code exploration tasks.
**Effort:** Low — tree-sitter Python bindings available. Could replace ast.parse in yggdrasil_census.py.

### 4.3 GraphRAG (AST-derived knowledge graphs)
**Source:** arxiv 2601.08773, Memgraph, LanceDB
**What:** Knowledge graphs built from AST structure, with bidirectional graph expansion at query time. Outperforms chunk-based embedding retrieval.
**Applicability:** Our semantic.py uses chunk-based embedding (512-char chunks). GraphRAG would provide more precise retrieval by traversing the dependency graph. The codegraph_mcp already has a graph but uses unidirectional BFS.
**Effort:** Medium — requires graph schema design and bidirectional traversal.

### 4.4 3D Force-Directed Graph Visualization
**Source:** vasturiano/3d-force-graph, CodeLandscapeViewer
**What:** Interactive 3D visualization of dependency graphs. Nodes sized by LOC, colored by type, animated particles on edges.
**Applicability:** Our Yggdrasil renders are 2D SVG/HTML. 3D would better represent the 20-tree structure and make cleave boundaries visible. 3d-force-graph supports up to 100K nodes.
**Effort:** Low — drop-in replacement for the D3 force layout in our capture scripts.

### 4.5 GNN Microservice Extraction
**Source:** arxiv 2508.07486 (Mo2oM), MDPI 17/7/303, IJCAI 2022
**What:** Heterogeneous graph neural networks for automatic monolith decomposition. Soft clustering for overlapping microservices. Mo2oM achieves 85%+ accuracy on microservice boundary detection.
**Applicability:** Our Tier B trees (needs shim) could be automatically clustered using GNNs. The note_failure coupling (303 sites) would be naturally handled by soft clustering. Could replace the hardcoded LIMBS literal.
**Effort:** High — requires training data and GNN framework (PyTorch Geometric).

### 4.6 Vulture/Deadcode (Python dead code detection)
**Source:** jendrikseipp/vulture, deadcode (GitHub)
**What:** AST-based dead code detection with confidence tiers (60-100%). Finds unused functions, classes, imports, variables, attributes. Auto-fix available.
**Applicability:** We have NO dead code detection at all. Vulture would identify which of the 750 modules are unreachable. Confidence tiers allow triage: 100% = safe to remove, 60% = needs review.
**Effort:** Low — `pip install vulture`, run against src/.

### 4.7 Universal AST (CodePrism)
**Source:** rustic-ai.github.io/codeprism
**What:** Language-agnostic graph-based code analysis. 47x faster than traditional AST (2.8s vs 42.3s for full scan). Handles dynamic imports, metaclasses, inheritance.
**Applicability:** Our census takes ~10s for 750 modules. Universal AST would reduce this to <1s and add cross-language support. The dynamic import handling (confidence 0.7) would resolve some of our 54 variable-unresolved imports.
**Effort:** High — requires Rust implementation or porting.

### 4.8 Bidirectional Graph Expansion (Reliable Graph-RAG)
**Source:** arxiv 2601.08773
**What:** Bidirectional graph traversal at query time, combining AST-derived structure with semantic search. Outperforms unidirectional BFS.
**Applicability:** Our codegraph_mcp.py does unidirectional BFS from seeds. Bidirectional expansion would find paths between any two nodes more efficiently and avoid the "shared soup" problem (where paths walk through documents).
**Effort:** Low — modify _neighbours to support bidirectional traversal.

### 4.9 Code-Graph-RAG (Tree-sitter + embeddings)
**Source:** vitali87/code-graph-rag, code-graph-rag.com
**What:** Combines Tree-sitter structural parsing with vector embeddings for code intelligence. Reduces AI tool calls by 90%.
**Applicability:** Our semantic.py uses chunk-based embedding. Code-graph-rag would index by symbol (function, class) rather than by chunk, providing more precise retrieval. Could replace or augment the Chunker.
**Effort:** Medium — requires symbol-level chunking and graph-aware retrieval.

### 4.10 Joern CPGQL (pattern mining)
**Source:** joern.io, docs.joern.io
**What:** Graph query language for code property graphs. Enables pattern mining: "find all functions that call X without checking Y".
**Applicability:** Our codebase has 1,224 silence guards (except ImportError). CPGQL could find patterns like "functions that catch exceptions without logging" or "modules that import X but don't use it". This would be a powerful audit tool.
**Effort:** Medium — Joern supports Python. Could run as a separate audit pass.

---

## 5. Bleeding-Edge Engineering Opportunities

### Priority 1 (low effort, high impact)
1. **Add Vulture dead code detection** — `pip install vulture && vulture src/` — identifies unreachable modules among 750
2. **Add missing __init__.py** — 9 directories, trivial fix, enables proper packaging
3. **Implement bidirectional BFS in codegraph_mcp** — modify _neighbours for reverse traversal
4. **Add 3D force-graph to Yggdrasil renders** — drop-in replacement for 2D D3 layout

### Priority 2 (medium effort, high impact)
5. **Integrate Tree-sitter** — replace ast.parse in yggdrasil_census.py for multi-language support
6. **Implement GraphRAG** — replace chunk-based embedding with symbol-level graph retrieval
7. **Add CPG layer** — Joern integration for control-flow + data-flow analysis
8. **Implement code-graph-rag** — symbol-level indexing with graph-aware retrieval

### Priority 3 (high effort, transformative)
9. **GNN-based tree boundary detection** — automatic clustering to replace hardcoded LIMBS
10. **Universal AST (CodePrism)** — Rust-based, 47x faster, cross-language
11. **Joern CPGQL pattern mining** — systematic audit of all 750 modules

### Priority 4 (research/experimental)
12. **Mo2oM soft clustering** — overlapping microservice extraction for Tier B trees
13. **Heterogeneous GNN** — graph neural network for dependency analysis
14. **3D VR codebase exploration** — vasturiano/3d-force-graph-vr for immersive navigation

---

## 6. Recommended Next Steps

1. **Immediate:** Run Vulture on src/ to identify dead code. Fix 9 missing __init__.py. Triage 106 TODO/FIXME/HACK markers.
2. **Short-term:** Integrate Tree-sitter into yggdrasil_census.py. Add bidirectional BFS to codegraph_mcp. Add 3D visualization to Yggdrasil renders.
3. **Medium-term:** Implement GraphRAG for code search. Add CPG layer via Joern. Implement code-graph-rag for symbol-level indexing.
4. **Long-term:** GNN-based automatic tree boundary detection. Universal AST migration. Mo2oM for overlapping service extraction.

---

## 7. Recording

- Engram: observation #saved (architecture, topic_key: yggdrasil/cleave-forensic-audit)
- PMB: activity recorded (outbox_id: 1475)
- This document: azazael/docs/YGGDRASIL_CLEAVE_FORENSIC_AUDIT_2026-10-31.md
