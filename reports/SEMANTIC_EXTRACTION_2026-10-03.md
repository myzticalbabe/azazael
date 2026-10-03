# Full semantic extraction — doc graph, 2026-10-03

Method, measurements, and the traps, for the next assistant. The runnable pipeline
and its runbook live at **`tools/graph_semantic/`** (`README.md` is the handoff).

## What was asked

> use graphify and be the LLM for full semantic extraction
> we need all docs graphed
> provide memories for other assistant to do full semantic extraction

There is no `GEMINI_API_KEY` / `GOOGLE_API_KEY` on this host, so graphify's semantic
subagent cannot run. **The agent is the LLM.** This pass built that layer by hand
plus the mechanical scaffolding to keep it reproducible.

## Result

| | before | after |
|---|---|---|
| nodes | 32,303 | **35,888** |
| links | 56,443 | **67,041** |
| connected components | 126 | **10** |
| project docs with a node | 151 (of 1,527) | **1,527 (100%)** |
| nodes carrying `rationale` | 271 | **2,239** |
| document / rationale / concept nodes | ~11,572 | **15,159** |

- Extraction mix: **92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS**; INFERRED mean
  confidence **0.88**.
- 2,018 communities, 12 hyperedges, **1 isolated node**, **0 self-loop edges**
  (removed in `build_graph.py`), and **3,426 document→entity `mentions` edges**
  (see the enhanced-semantic layer). The non-giant components are now tiny
  (7 / 6 / 4 / 3 / 2 … nodes).
- `graphify diagnose multigraph`: 0 exact-duplicate edges, 0 collapsed endpoint
  pairs, 0 external-reference edges. 101 self-loop edges remain (harmless,
  uninvestigated).

Net: one pass took the graph from **126 → 10 connected components** while adding
3,585 nodes. It is now far *more* connected than the git-native graph it started
from, and doc coverage is total. (The figures above are from the reproduced run;
the report doc itself is counted too, which is why the doc total is 1,527 rather
than the 1,526 measured before it was added.)

## What the layers are

1. **Authored semantic layer** — 269 nodes, 367 edges, 12 hyperedges, hand-written
   by the agent from reading a digest of the corpus. Covers the ~120 docs that carry
   design intent: governance (RULEs, gates, sentinels), architecture (cluster tiers,
   two-ledger, six-tier paradigm, TD-series), the neural mesh and its audit findings,
   free-threading hazards, packaging, and the PMB loop repair.
2. **Doc-file layer** — one `document` node per project doc (1,425 nodes), 114
   directory buckets, 2,529 edges (316 doc→doc from markdown links, 935 doc→code
   from backticked paths).
3. **Concept layer** — 580 deduped concept hubs extracted from headings that appear
   in 2–60 docs, with 1,516 edges.
4. **Coverage layer** — 1,297 nodes / 2,902 edges. Closes the gaps the first three
   layers leave: the 1,234 `skills/*.md` files (frontmatter `name`/`description`/
   `metadata.category` → concept node + 43 category hubs), the 36 BIBL lexicon
   volumes, the 13 `src/CODEX/DOCUMENTATION/*` duplicates linked to their canonical
   `docs/*` twin, the three degree-0 polyglot islands, and the dimensionless
   `.ps1`/`.sh`/`.java`/`__init__.py` files (no supported AST language, so degree-0
   by construction) grouped under suite/marker concept nodes. Adds 14 authored
   rationale rows and 16 `ATTACH` edges binding authored group nodes to spine nodes.
5. **Rationale tranche 2** — 20 authored nodes / 26 edges for the large load-bearing
   docs the first pass had not read (task registry, research record, both
   full-project audits, session-insight and lesson records, worm audit, project map,
   cross-environment manifest, Rust tracker, sync strategy, worm proposals,
   algorithm log).
6. **Enhanced semantic layer** — 3,426 `mentions` edges across 492 docs. Every
   document's *body* is matched against known entity labels; an edge is emitted only
   when the label literally appears in the text. Identifier-shape and
   document-frequency (≤40) guards stop corpus vocabulary like `Environment` and
   `Category` from becoming hubs.
7. **Bridge layer** — 17 grounded edges that pull the last stranded components onto
   the main graph (noxfile→type gate, cascade→inference endpoints, cluster_route→
   Tier-2, graph_learn→ML harness, animation/vega→CODEX video, forensic audits→
   error-lesson audit, mesh resilience→mesh architecture audit, PowerShell suite→
   launcher/deploy).

## The design decision that made it work

**Docs must be edges, not just nodes.** A node with no edge is its own connected
component, so naively adding 1,425 doc nodes would have added ~1,425 components and
made fragmentation dramatically worse. Every layer therefore attaches:

- doc → directory bucket (guarantees ≥1 edge per doc)
- directory bucket → a semantic **spine** node (which is anchored into the code
  graph) — this is what pulls the doc tree onto the main component
- doc → doc, doc → code node, concept → AST node id

Measured: adding the doc layer moved components **133 → 119** while adding 2,059
nodes. The full pass ends at 118, i.e. **more connected than the git-native 126**.

## Corrections to earlier findings

- **The "1,584 components" figure was the older B-tree graph**, not this one. This
  tree (A) had **126** components at 32,303 nodes. Any fragmentation claim must name
  which graph it was measured on.
- The earlier conclusion "fragmentation is a documentation artefact, not a clustering
  problem" was **right about the cause and wrong about the fix**. It is an
  *edge* problem: docs lacked identity and edges. Giving them both fixed it. Clustering
  knobs (`--resolution`, `--exclude-hubs`) remain useless for this — unchanged.
- Three polyglot sub-projects were degree-0 islands (`packages/azazael-core`,
  `gateway-go`, `native/worm_manifest`). **Resolved** by the coverage layer: each now
  has a concept node whose rationale is quoted from its own manifest, with grounded
  edges into the subsystem it belongs to. `gateway-go` alone links 11 nodes.## New trap this pass created — and its fix

With docs as first-class nodes, **doc-reference hubs took over the god-node list**:
`Catch-All Refactoring Backlog` hit **583 edges**, outranking `DirectMemory` (197).
That is the **same defect class as the stdlib god nodes and the `indirect_call` false
hub**: a high-degree node encoding "this file mentions many things", not "this is a
core abstraction".

`tools/graph_semantic/god_nodes.py` fixes the *measurement* (it does not delete
nodes). It adds the filters graphify's own ranking lacks: `file_type in
{document, concept, rationale}` (md and non-md), graphify's file/concept/json-key
nodes, stdlib module names, ≤2-character names, and test-local helpers. The corrected
ranking is all real code:

1. `DirectMemory` 197 · 2. `LocalMemoryStore` 109 · 3. `EvolutionEngine` 93 ·
4. `MemoryBus` 84 · 5. `SpineCycleWorm` 83 · 6. `ClusterWORMZ` 80 ·
7. `SessionMemory` 63 · 8. `ComplianceOrchestrator` 58 · 9. `ParallelInferenceEngine` 56 ·
10. `FreeThreadedAgent` 53

`--patch-report` rewrites the `## God Nodes` section of `GRAPH_REPORT.md` in place.
This is applied *after* `cluster-only`, which otherwise regenerates the raw ranking.
The same correction is available at the source via
`tools/graph_semantic/graphify_patch.py` (`god_nodes_fixed` + `install()` monkeypatch
+ an upstream unified diff), so an embedder does not have to post-process at all.

**Anchor audit.** `audit_anchors.py` checks the claim that every authored node is
anchored to a real AST symbol. Two real defects were found and fixed: a
`canon_drift_check` anchor pointing at a label that does not exist
(`check_drift` → `cmd_check`/`classify`) and a `worm_config_trace` anchor whose node
was never defined (removed; `WORM_REGISTRY` folded into `azazael_registry_doc`).
It also reports the honest caveat that graphify **rewrites 6 authored ids to their
source-file stem** on merge (`type_check_gate` → `tools_type_check_gate`, etc.) —
edges survive, but the on-disk id is not the authored one.

## Traps that cost time (all encoded in the pipeline)

1. **Label collisions silently delete nodes.** `graphify` dedups by label, so a doc
   node titled after a code file (`docs/*/X_API.md` is titled `X.py`) is merged into
   the code node and lost. 4 docs vanished this way before the guard.
2. **Non-ASCII filenames collide on id.** `BIBL/Α.md`, `Γ.md`, `Î.md` normalize to
   one stem. Disambiguated with a short SHA-1 of the path.
3. **`build_merge` replaces per `source_file` AND per tier.** Patch the generator,
   never `graph.json` — a direct edit is silently reverted by the next rebuild.
4. **`build_from_json` and `build_merge` disagree on component count** for identical
   data. Always compare before/after with the *same* function.
5. **`--exclude-hubs N` is a degree percentile below which nodes are KEPT**, not
   "exclude the top N%". It makes this graph far worse.
6. **Boilerplate headings are not concepts.** The generated skill docs emit
   `Related` / `Verify` / `Identity` in ~1,090 files each; without a doc-frequency
   cap they become the three largest hubs.
7. `graphify-out/` is gitignored, so `graph.json` and `GRAPH_REPORT.md` are
   generated and not committed. The authored content was therefore moved to
   `tools/graph_semantic/` so it is tracked and reviewable.

## Scope and exclusions

1,525 project docs included. 532 `.md` files excluded as archive/backup/vendor/
generated, by directory: `archived`, `archive`, `archived_unified`, `backup`,
`skills.win-backup`, `target`, plus build/cache dirs (`graphify-out`, `node_modules`,
`.agents`, `graphs`, `output`, …). `skills/` (1,235 docs) **is** included — it is
generated content but it is the project's own skill corpus.

## Reproduce

```bash
python tools/graph_semantic/run_extraction.py --report   # every layer, then report + God Nodes patch
python tools/graph_semantic/audit_anchors.py             # anchors resolve to real AST nodes
graphify diagnose multigraph --graph graphify-out/graph.json   # want 0 collapsed/dup
```

`run_extraction.py` runs all layers (ast_index → doc_scope → doc_digest →
semantic_layer → doc_layer → concept_layer → coverage_layer → rationale_tranche2 →
enhanced_semantic → bridge_layer → build_graph), and `--report` then runs
`graphify cluster-only` and re-applies `god_nodes.py --patch-report`, because
`cluster-only` **overwrites both hub-derived community labels and the patched God
Nodes section**. `run_extraction.py` forces `PYTHONIOENCODING=utf-8` on every child.

`tools/graph_semantic/graphify_patch.py --emit-patch` writes the upstream diff that
fixes `graphify.analyze.god_nodes` at its source
(`tools/graph_semantic/patches/graphify_analyze_god_nodes.patch`).

Last verified: 2026-10-03, `tools/graph_semantic/` clean under the AST scanner,
anti-pattern ratchet unchanged (3,687), type gate unchanged (1,410).
