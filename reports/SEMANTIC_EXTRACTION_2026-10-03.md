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
| nodes | 32,303 | **34,624** |
| links | 56,443 | **60,813** |
| connected components | 126 | **118** |
| project docs with a node | 151 (of 1,525) | **1,525 (100%)** |
| nodes carrying `rationale` | 271 | **926** |
| document / rationale / concept nodes | ~11,572 | **13,895** |

- Extraction mix: **92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS**; INFERRED mean
  confidence **0.88**.
- 1,632 communities, 12 hyperedges.
- `graphify diagnose multigraph`: 0 exact-duplicate edges, 0 collapsed endpoint
  pairs, 0 external-reference edges. 101 self-loop edges remain (harmless,
  uninvestigated).

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
- Three polyglot sub-projects remain degree-0 islands (`packages/azazael-core`,
  `gateway-go`, `native/worm_manifest`). Unresolved.

## New trap this pass created (honest)

With docs as first-class nodes, **doc-reference hubs now top the god-node list**:

1. `Catch-All Refactoring Backlog (graphify-prioritized)` — **583 edges**
2. `f()` — 260 (known false hub)
3. `DirectMemory` — 197
4. `LocalMemoryStore` — 109
5. `SKILLS_CATALOG — the skills inventory` — 100
7. `Azazael Ecosystem: Comprehensive Task Registry [TASK_REGISTRY.md]` — 92

A backlog document that lists per-line file detail now outranks every real code
abstraction. That is the **same defect class as the stdlib god nodes and the
`indirect_call` false hub**: a high-degree node that encodes "this file mentions
many things" rather than "this is a core abstraction". Any centrality ranking must
now filter `file_type in {document, concept}` reference hubs, or weight by relation
type, in addition to the existing stdlib filter.

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
python tools/graph_semantic/run_extraction.py          # 1..7
graphify cluster-only . --no-viz --no-label            # 8 regenerate report
```

Last verified: 2026-10-03, `tools/graph_semantic/` clean under the AST scanner,
anti-pattern ratchet unchanged (3,687), type gate unchanged (1,410).
