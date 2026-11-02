# Yggdrasil Trees — Complete Registry & Semantic Rendering Guide

**Date:** 2026-10-31
**Purpose:** Educational psychological tools for codebase understanding

---

## 1. All 20 Trees (complete registry)

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

### Tree Categories

| Category | Trees | Total Lines | Description |
|----------|-------|-------------|-------------|
| **Core Infrastructure** | CORE, META, UTILITIES | 181,889 | Foundational: paths, logging, inference, memory |
| **Code Generation** | CODEX, RENDERING | 36,271 | Video generation, HTML capture, templates |
| **Orchestration** | ORCHESTRATION, HYDRA, DAEMONS | 41,078 | Task scheduling, swarm, health monitoring |
| **Intelligence** | ML, PSYCHE, META | 12,963 | Machine learning, psychology, agent config |
| **Tools & CLI** | TOOLS, CLI, SCRIPTS, AZAZAEL_TOOLKIT | 12,913 | Debugging, CLI, scripts, toolkit |
| **Execution** | INTERPRETERS, SHARDS | 3,130 | Language runners, shard management |
| **Agent Systems** | AOA, eve_unleashed | 13,170 | Agent orchestration, desktop app |
| **Testing** | tests | 2,052 | Test suites |
| **Stubs** | RENDERING, SHORTCUTS | 99 | Minimal/placeholder |

---

## 2. How to Improve Rendering Detail (Educational Psychological Tools)

### 2.1 Cognitive Load Theory (from web research)

Three types of cognitive load must be balanced:

| Type | Description | How to Manage |
|------|-------------|---------------|
| **Intrinsic** | Inherent complexity of the codebase | Show only relevant trees initially |
| **Germane** | Mental effort to understand relationships | Use semantic zoom to reveal connections progressively |
| **Extraneous** | Unnecessary visual complexity | Remove decorative elements, use clean design |

**Principle:** Match visualization complexity to audience expertise. Novices see 3-5 trees. Experts see all 20.

### 2.2 Semantic Zoom (from arxiv 2510.00003)

Different representations at different zoom levels:

| Zoom Level | What's Shown | Detail |
|------------|-------------|--------|
| **Far (overview)** | Tree nodes as colored spheres | Name + line count |
| **Medium** | Tree nodes + connection edges | Imports, exports, channels |
| **Close** | Individual modules within a tree | Classes, functions, imports |
| **Very close** | Source code snippets | Docstrings, key functions |

**Implementation:** Scale-dependent LOD (Level of Detail) — nodes change shape/size/content based on camera distance.

### 2.3 Details on Demand (Shneiderman's mantra)

"Overview first, zoom and filter, then details on demand."

1. **Overview:** Show all 20 trees as a mycelium network
2. **Zoom:** Click a tree to expand it, showing its modules
3. **Filter:** Toggle trees on/off, filter by category
4. **Details:** Hover for tooltip, click for full source

### 2.4 Educational Psychological Design Principles

For renders to be **educational psychological tools**, they must:

1. **Reduce anxiety** — Use calming colors (blues, greens), smooth animations, no jarring transitions
2. **Build mental models** — Show structure before detail (tree → modules → functions → code)
3. **Provide feedback** — Interactive elements respond to user input (hover, click, drag)
4. **Support different learning styles** — Visual (3D graph), verbal (captions), kinesthetic (interaction)
5. **Progressive disclosure** — Don't overwhelm; reveal complexity gradually
6. **Highlight relationships** — Connections between trees are more important than individual trees
7. **Use real data** — All metrics come from actual codebase analysis (not mock data)
8. **Tell a story** — Captions narrate the journey through the codebase

### 2.5 Specific Rendering Improvements

| Current | Improved | How |
|---------|----------|-----|
| 2D labels | 3D text sprites | Use THREE.Sprite with canvas texture |
| Static colors | Animated color transitions | Lerp between states on interaction |
| Fixed node size | Size by complexity metric | log2(lines) or sqrt(classes) |
| No hover info | Rich tooltips with semantic data | Raycaster + HTML overlay |
| No zoom levels | Semantic zoom (LOD) | Scale-dependent rendering |
| No filtering | Category toggles | Show/hide trees by category |
| No search | Text search with highlight | Filter nodes by name/keyword |
| No path finding | Shortest path highlighting | Dijkstra on tree graph |
| No temporal | Git history animation | Nodes appear over time |
| No audio | Sonification | Pitch by complexity, rhythm by connections |

### 2.6 Web Search Findings (Creative Adaptations)

#### From "Semantic Zoom and Mini-Maps for Software Cities" (arxiv 2510.00003)
- **Semantic zoom** changes object structure (not just size) at different scales
- **Mini-maps** provide global context while zoomed in
- **Level of Detail (LoD)**: display visual objects with different polygon counts
- **Smart zoom**: adapt content density based on zoom level

#### From "Cognitive Load as a Guide" (nightingaledvs.com)
- **Intrinsic load** = inherent complexity (can't reduce, only manage)
- **Extraneous load** = presentation complexity (minimize this)
- **Germane load** = learning effort (maximize this)
- **12 spectrums** for calibrating cognitive load in visualizations

#### From "Software Architecture Diagrams 2026" (8starlabs, icepanel)
- **C4 model**: Context → Container → Component → Code (4 levels of zoom)
- **Zoomable diagrams** across all C4 levels
- **Semantic model** with reusable elements across views

#### From "Information Visualization" (infovis-wiki)
- **Details on demand**: Shneiderman's mantra
- **Semantic zooming**: objects change appearance/shape as they change size
- **Meta data**: incorporate knowledge about meaning, not just visual detail

---

## 3. Build Suggestions (Implementation Plan)

### Phase 1: Semantic Zoom (immediate)
1. Add camera distance-based LOD to tree network render
2. Far: tree name only. Medium: + line count. Close: + modules/classes/functions. Very close: + imports/exports
3. Implement mini-map in corner showing global context

### Phase 2: Interactive Exploration (short-term)
1. Click tree → expand to show modules as child nodes
2. Hover → rich tooltip with semantic data (already started)
3. Search box → highlight matching trees/modules
4. Category filters → toggle trees by category
5. Path finding → highlight shortest path between two trees

### Phase 3: Educational Features (medium-term)
1. Guided tour mode — narrated walkthrough of the codebase
2. Quiz mode — "which tree handles X?" with feedback
3. Progressive disclosure — reveal complexity based on user level
4. Annotation system — add notes to trees/modules
5. Export to PDF/SVG for documentation

### Phase 4: Advanced (long-term)
1. XR/VR support — immersive 3D exploration
2. Sonification — audio feedback for structure
3. Multi-user collaboration — shared exploration
4. AI assistant — "explain this tree" with LLM
5. Temporal replay — watch codebase evolve over git history

---

## 4. All Trees List (for reference)

1. **CORE** — 337 modules, 165,991 lines, hub to 17 trees. The trunk. Everything connects here.
2. **CODEX** — 90 modules, 36,174 lines. Video generation, HTML capture, templates.
3. **ORCHESTRATION** — 84 modules, 37,505 lines. Task scheduling, swarm, health monitoring.
4. **META** — 20 modules, 10,214 lines. Agent config, meta-reflection, state machine.
5. **UTILITIES** — 22 modules, 5,684 lines. KLINK, PERSEPHONE, POINDEXTER, TARBABY, TERENCE.
6. **SCRIPTS** — 30 modules, 7,897 lines. Fix scripts, build scripts, analysis tools.
7. **eve_unleashed** — 21 modules, 5,866 lines. Desktop AI app, model management.
8. **ML** — 9 modules, 1,188 lines. Neural networks, RL, GRPO training.
9. **PSYCHE** — 7 modules, 1,561 lines. CAIN psychoanalysis, curative pools.
10. **INTERPRETERS** — 6 modules, 2,001 lines. Go/Rust language runners.
11. **SHARDS** — 4 modules, 1,129 lines. Skill shard repository.
12. **AOA** — 30 modules, 7,304 lines. Agent orchestration arms.
13. **AZAZAEL_TOOLKIT** — 9 modules, 2,250 lines. Core framework, QL analysis.
14. **CLI** — 2 modules, 255 lines. Command-line interface.
15. **DAEMONS** — 4 modules, 881 lines. Background daemons.
16. **HYDRA** — 11 modules, 2,692 lines. Adaptive ML cluster.
17. **TOOLS** — 10 modules, 2,511 lines. Debug, archive, fix tools.
18. **RENDERING** — 6 modules, 97 lines. (Stub) Character rendering.
19. **SHORTCUTS** — 1 module, 2 lines. (Stub) Keyboard shortcuts.
20. **tests** — 13 modules, 2,052 lines. Test suites.

---

## 5. Recording

- Engram: observation saved (topic_key: yggdrasil/trees-semantic-rendering)
- PMB: activity recorded
- Document: YGGDRASIL_TREES_SEMANTIC_RENDERING_GUIDE.md
- Location: C:/Azazael/azazael/docs/
