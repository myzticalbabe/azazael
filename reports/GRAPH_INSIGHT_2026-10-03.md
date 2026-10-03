# Graph Insight — Azazael code graph, 2026-10-03

**Source:** `C:\Users\clint\azazael\graphify-out\graph.json`
**Built at commit:** `9902fed6` · **49,666 nodes / 75,974 links / 3,368 communities**
**Method:** degree centrality, in/out-degree, distinct-neighbour-community brokerage,
cross-community bridge edges, orphan and island detection. Stdlib concept nodes
filtered out of the architecture rankings (see Finding 1).

---

## Finding 1 — The graph's "god nodes" are mostly stdlib artifacts

The raw top-7 by degree are `sys` (824), `pathlib` (740), `json` (604), `os` (598),
`time` (406), `typing` (380), `datetime` (366). These are **not architecture** — they are
import targets that every module points at, so they form four of the five largest
"communities":

| Community | Nodes | What it really is |
|---|---:|---|
| `json` | 772 | every module that imports `json` |
| `sys` | 734 | every module that imports `sys` |
| `re` | 328 | every module that imports `re` |
| `argparse` | 274 | every CLI module |
| `sqlite3` | 247 | every storage module |

Only 42 of 366 concept nodes are stdlib, but they absorb the majority of cross-community
edges (e.g. `sys <-> json` = 690, `sqlite3 <-> json` = 255). **Any centrality ranking that
does not filter these is dominated by noise.** Fix: drop `file_type == "concept"` nodes
whose label is in the stdlib set before ranking, or assign them a single shared
"stdlib" community.

## Finding 2 — `f()` is the #1 brokerage node and it is a false hub

`f()` at `tests/test_exmachina_operators.py:L142` has **262 edges across 154 distinct
files**, all but a handful of them `indirect_call`. It is a local helper named `f` inside a
pytest test, and the resolver collapses every bare-name `f` reference in the tree onto it.
The same class of collision exists for `_fixture()` (84 edges, 41 communities) and, at
scale, `main()` — **458 nodes, one per file** — and `run()` (15).

**Implication:** `indirect_call` (1,161 edges) and bare-name resolution cannot be trusted
for cross-file reasoning. The graph should either (a) namespace callable labels by their
`source_file`, or (b) drop `indirect_call` from centrality metrics. Until then, treat any
generic-named function at the top of a ranking as suspect.

## Finding 3 — The real architecture hubs (stdlib + false hubs removed)

| Node | Degree | Distinct neighbour communities | Reading |
|---|---:|---:|---|
| `DirectMemory` (`direct_memory.py`) | 204 | **49** | the true memory backbone — touches the most subsystems |
| `CORE/worm_registry.py` | 173 | 36 | every worm registers here |
| `LocalMemoryStore` (`local_memory.py`) | 122 | 37 | second memory pillar |
| `MemoryBus` (`MemoryBus.py`) | 89 | — | pub/sub hub |
| `ClusterWORMZ` (`CLUSTERWORMS.py`) | 76 | 38 | parallel execution hub |
| `SpineCycleWorm` (`spine.py`) | 92 | — | the mesh cycle driver |
| `EvolutionEngine` (`evolution.py`) | 103 | — | fitness/selection |

`DirectMemory` is the single most connective real symbol in the codebase (49 distinct
communities). That matches the architecture docs: it is the canonical session recorder
everything writes through.

## Finding 4 — Genuine cross-community bridges (the spine mesh is real)

Filtering stdlib, the strongest architecture bridges are the **spine state pair** and the
**evolution pair**:

```
 53  load_spine_state(97)      <-> spine_registry.py(1291)
 28  save_spine_state(628)     <-> spine_registry.py(1291)
 22  _q_observe_unlocked(299)  <-> spine_registry.py(1291)
 38  GeneticOptimizer(208)     <-> EvolutionEngine(1558)
 32  `spine.py` - 109 functions(23) <-> RedQueenWorm(60)
 22  proteus_hooks.py(12)      <-> morph_record(39)
 30  cli_crossref.py(110)      <-> DirectMemory(3166)
 25  ProviderResult(4)         <-> ParallelInferenceEngine(747)
```

These are the load/save/observe spine contract, the optimizer→engine handoff, and the
inference result path — i.e. the graph independently rediscovers the mesh the docs claim.
No action needed; this is confirmation the wiring exists.

## Finding 5 — Documentation creates a shadow graph

Node composition: **code 21,371 · document 16,517 · rationale 11,409 · concept 366**.
Docs and rationale are **56%** of all nodes. A handful of documents are super-connectors:

- `Azazael_DUAL_PANE.md` — **780-degree node, 779 out-edges** (references nearly everything)
- `NEURAL_MESH_FUNCTION_TODO.md` — emits ~6 "N functions" inventory nodes, each with 64–118 out-edges
- `ERROR_LOG.md` (165 out), `LESSONS_MASTER.md` (111 out), `SYSTEM_INSTRUCTIONS.md` (55 out)

**Implication:** a single hand-written index doc can outrank every real module in centrality.
When mining, separate the "code graph" from the "doc graph", or the report tells you about
prose rather than software.

## Finding 6 — Three sub-projects are invisible islands

These roots have **degree 0** — no edge in or out:

| Node | Manifest | Language |
|---|---|---|
| `azazael-core` | `packages/azazael-core/pyproject.toml` | Python (packaged) |
| `gateway-go` | `gateway-go/go.mod` | Go |
| `worm-manifest` | `native/worm_manifest/Cargo.toml` | Rust |

The extractor is single-language: it parses Python imports/calls and markdown, so the Go
and Rust trees contribute only their manifest file and nothing links them to the Python
core. **The polyglot split is real but structurally disconnected in the graph.**

## Finding 7 — 162 isolated nodes, including stale artifacts

- 4 `cosmos/graph.labels.0.js` / `graph.links.js` dumps (`ecosystem/`, `ecosystem_win/`,
  `learning_loop/`, `learning_loop_win/`) — generated JS copies of *this same graph*,
  now orphans inside it.
- ~10 PowerShell shortcut scripts (`pin_to_taskbar.ps1`, `make_project_shortcuts.ps1`, …).
- `COMPLIANCE_CHECKLIST.md` — an isolated doc.
- Only 5 docs/`archive` files leaked in (`docs/archive/*.md`); `archive_store.py` and
  `archive_system.py` are legitimate code that merely contain "archive" in the name.

Minor hygiene: add the cosmos `.js` dumps and the shortcut scripts to `.graphifyignore`,
or accept them as harmless.

## Finding 8 — Community granularity is too fine

3,368 communities for 49,666 nodes ≈ **14.7 nodes/community**. At that size the partition
is near leaf-level and cross-community bridges are mostly stdlib noise. Raising the
resolution threshold (fewer, larger communities) would make the bridge table meaningful.

---

## Finding 9 — The fragmentation is a DOCUMENTATION artifact, not a clustering problem

Follow-up investigation ("how do we fix structural fragmentation?"). The graph
has **1,584 connected components** for 49,666 nodes / 75,974 edges (mean degree
3.06 — it is sparse). Two candidate fixes were tested and **both failed**:

- **`--exclude-hubs N` made it worse.** The parameter is a degree PERCENTILE
  below which nodes are *kept* for partitioning, so `5` keeps only the bottom 5%
  (29,021 communities) and `99` still excludes the top 1% (6,433). The sparse
  graph cannot tolerate hub removal.
- **`--resolution` barely moves it.** `0.2` (coarser) gave 3,378 communities vs
  3,368 at the default `1.0`; the number of components is unchanged either way.

Re-projecting the graph with different exclusion sets shows the real cause:

| Scenario | Components | Largest |
|---|---:|---:|
| Full graph | 1,584 | 36,941 |
| Drop `skills/` | **390** | 36,405 |
| Drop `skills/` + `docs/` | 370 | 35,620 |
| Drop all docs (any `.md`) | **258** | 32,114 |
| CODE dirs only | 607 | 26,136 |

**`skills/` alone accounts for ~75% of the components: 8,011 of its 8,547 nodes
(93.7%) sit in components of their own.** Root-level `.md` files are 28.2%
stranded and `docs/` 43.0%, while the code trees are almost fully connected
(`tests/` 0.0%, `packages/` 1.1%, `tools/` 3.8%, `scripts/` 8.2%, `src/` 11.9%).

**What the components are:** the largest is 36,941 nodes — the real code graph.
Everything after it is a document cluster: `src/CODEX/Azazael_DUAL_PANE.md` (781),
`src/CODEX/DOCUMENTATION/CHANGELOG.md` (284), `MEMORIES.md` (100),
`RECONCILIATION_AND_INTERMESH_2026-09-28.md` (79), one cluster per skill, one per
doc.

**The fix (three options, in order of effort):**

1. **Separate the two layers.** The graph is the union of a well-connected CODE
graph and a fragmented DOC graph. For "what calls this?" questions, exclude the
doc trees — `drop all docs` gives **258 components** (an 84% reduction) with the
code core intact at 32,114. `skills/` is the same tooling content the project
already excludes as `.agents/skills` ("a map of its own tooling"), so excluding
`/skills/` is consistent with the existing scope decision — but it is a scope
change, so it belongs to the maintainer, not to an unattended edit.
2. **Keep both, as two graphs.** `graphify update` reads `.graphifyignore` and
`.gitignore`; maintain a code graph and a doc graph and query them separately.
3. **Wire the doc layer in.** Give each skill/doc a `references` edge to the code
it documents, so it joins the main component. This is semantic extraction (the
part that needs an LLM) and is the only option that both keeps and connects the
docs.

Until then: **read the graph's centrality/bridge output as two graphs, not one.**
A `skills/` node's isolation is not a defect in the code — it is the code graph
being asked to answer a documentation question.

## Recommended actions (in priority order)

1. **Filter stdlib concept nodes** out of every centrality/bridge metric, or collapse them
   into one "stdlib" community. *(highest value — most of the current noise)*
2. **Namespace or exclude `indirect_call`** so generic names (`f`, `main`, `_fixture`)
   stop impersonating hubs.
3. **Split code graph from doc graph** when mining; report on `file_type == "code"` only
   for architecture questions.
4. **Add the 4 cosmos `.js` dumps + shortcut `.ps1`s to `.graphifyignore`.**
5. **Cross-link the polyglot sub-projects** (`azazael-core`, `gateway-go`, `worm-manifest`)
   at least to the Python core by a manifest edge, or exclude them explicitly.
6. **Coarsen community detection** so bridges are architectural, not stdlib.

None of these block the P0/P1/P3 compliance work; they are graph-quality improvements.
