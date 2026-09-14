# Azazael Rust Conversion Plan

**Version:** 1.1.0 | **Created:** June 4, 2026 | **Updated:** June 4, 2026 | **Source of Truth:** G:/source-of-truth/

---

## Prerequisites

Before starting any crate conversion:

| Requirement | Status | Setup Command |
|------------|--------|---------------|
| Rust toolchain (MSVC ABI) | ✅ Required | `rustup default stable-x86_64-pc-windows-msvc` |
| cargo workspace support | ✅ Required | Included with rustup |
| `cargo-insta` (snapshot testing) | 🔧 Recommended | `cargo install cargo-insta` |
| `maturin` (PyO3 builds) | 🔧 Phase 1+ | `pip install maturin` |
| G: drive mounted | ✅ Required | Already mounted (477G, 364G free) |
| Windows SDK / MSVC Build Tools | ✅ Required | Visual Studio 2022 Build Tools |

**Note on timelines:** Effort estimates assume a solo developer working on Rust conversion full-time. Multiply by 2-3x if splitting time with Python development. All estimates are **optimistic**; realistic timelines add 50% buffer for testing, CI setup, and edge cases.

---

## Executive Summary

The Azazael ecosystem comprises **311 Python files (124,553 lines)** across 10+ module categories, currently bundled via Nuitka for standalone .exe deployment. This plan outlines a phased Rust conversion strategy targeting performance-critical infrastructure, CLI tools, and long-running services while preserving Python for templating, GUI popups, and one-off scripting.

### Current State

| Metric | Value |
|--------|-------|
| Total Python files | 311 |
| Total lines of code | 124,553 |
| Largest module | unified_generator.py (5,536 lines) |
| Registered worms | 88+ |
| Worm categories | 17 |
| Standalone .exe files planned | 39 (via Nuitka) |
| Existing Rust project | GOSP (338 lines, ratatui TUI) |

### Target State

| Component | Current | Target |
|-----------|---------|--------|
| Worm Registry | Python `@register_worm` | Rust proc macro `#[register_worm]` |
| LocalMemoryStore | Python SQLite + FTS5 | Rust rusqlite + tantivy |
| Cluster Execution | Python threading | Rust rayon + tokio |
| HYDRA Pipeline | Python sequential | Rust async pipeline |
| GOSP | Rust skeleton (338 lines) | Full DoctoralThesisEngine |
| CODEX Video | Python PIL + ffmpeg | Rust image + ffmpeg crates |
| Web Dashboard | Python Flask-ish | Rust axum + HTMX |

---

## Phase 1: Core Infrastructure (Weeks 1-3)

### Crate: `azazael-registry`
**Status:** 🔴 Not started | **Priority:** P0 | **Dependencies:** `azazael-paths`

Convert the worm registry to a Rust crate with:

| Python Component | Rust Equivalent |
|-----------------|-----------------|
| `WORM_REGISTRY: Dict[str, Dict]` | `HashMap<String, RegistryEntry>` behind `RwLock` |
| `@register_worm` decorator | `#[register_worm(category="learning", priority=7)]` proc macro |
| `discover_worms()` directory scan | `walkdir` + `inventory` crate for compile-time registration |
| `SpawnDiversityEngine` | `SpawnDiversityEngine` with priority queue + cooldown tracking |
| `get_worms_by_category()` | `fn by_category(&self, cat: &str) -> Vec<&RegistryEntry>` |

**Cargo.toml dependencies:**
```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
walkdir = "2"
chrono = "0.4"
parking_lot = "0.12"         # RwLock
inventory = "0.3"             # Compile-time registration
once_cell = "1"               # Lazy statics
```

**Estimated effort:** 3-4 days
**Python compatibility:** PyO3 bindings for calling from Python during transition

---

### Crate: `azazael-memory`
**Status:** 🔴 Not started | **Priority:** P0 | **Dependencies:** `azazael-paths`

Convert LocalMemoryStore (1,380 lines) to Rust with enhanced full-text search:

| Python Component | Rust Equivalent |
|-----------------|-----------------|
| `LocalMemoryStore` class | `MemoryStore` struct with connection pool |
| `query_memories()` | `fn query(&self, filters: QueryFilters) -> Vec<MemoryRecord>` |
| `search_memories()` FTS5 | `tantivy` full-text search index |
| `record_event()` | `fn record(&self, event: MemoryEvent) -> Result<()>` |
| `get_stats()` | `fn stats(&self) -> MemoryStats` |
| `recall_recent()` | `fn recent(&self, limit: usize) -> Vec<MemoryRecord>` |

**Cargo.toml dependencies:**
```toml
[dependencies]
rusqlite = { version = "0.31", features = ["bundled", "vtab"] }
tantivy = "0.22"              # Full-text search (replaces SQLite FTS5)
serde = { version = "1", features = ["derive"] }
serde_json = "1"
chrono = "0.4"
parking_lot = "0.12"
r2d2 = "0.8"                  # Connection pool
r2d2_sqlite = "0.24"
```

**Estimated effort:** 4-5 days
**Note:** tantivy provides significantly better search performance than SQLite FTS5 and supports fuzzy matching, faceted search, and BM25 scoring.

---

### Crate: `azazael-paths`
**Status:** 🔴 Not started | **Priority:** P0 | **Dependencies:** None

Centralized path resolution crate (shared by all other crates):

```rust
pub fn get_project_root() -> PathBuf { /* AZAZAEL_ROOT or cwd discovery */ }
pub fn get_g_drive() -> PathBuf { /* G:/ discovery */ }
pub fn get_worms_dir() -> PathBuf { /* src/CORE/WORMS */ }
pub fn get_output_dir() -> PathBuf { /* output/ */ }
pub fn get_config_path() -> PathBuf { /* azazael.yaml */ }
```

**Estimated effort:** 1 day

---

## Phase 2: Cluster Execution Engine (Weeks 3-5)

### Crate: `azazael-cluster`
**Status:** 🔴 Not started | **Priority:** P1 | **Dependencies:** `azazael-registry`, `azazael-memory`

Convert the cluster system (CLUSTERWORMS 1,439 lines + NATURE_CLUSTERS 1,276 lines + METACLUSTER) to Rust:

| Python Component | Rust Equivalent |
|-----------------|-----------------|
| `ClusterWORMZ` (v2.0.0) | `ClusterWormz` struct with dynamic resolution |
| `NatureClusterManager` | `NatureClusterManager` with auto-discovery |
| `MetaCluster` (70 routes, 594 paths) | `MetaCluster` with routing graph (petgraph) |
| Python threading | `rayon` parallel iterators + `tokio` tasks |
| Cross-nature routing | `petgraph::Graph` with Dijkstra/A* pathfinding |
| Mermaid graph generation | `mermaid` crate or template-based output |

**Cargo.toml dependencies:**
```toml
[dependencies]
azazael-registry = { path = "../azazael-registry" }
azazael-memory = { path = "../azazael-memory" }
rayon = "1.10"
tokio = { version = "1", features = ["full"] }
petgraph = "0.6"
crossbeam = "0.8"
```

**Benchmark target:** 10x throughput improvement over Python threading (GIL-free + work-stealing)

**Estimated effort:** 5-7 days

---

### Crate: `azazael-hydra`
**Status:** 🔴 Not started | **Priority:** P1 | **Dependencies:** `azazael-cluster`

Convert HYDRA pipeline (HYDRA_ANALYZER_V2 1,273 lines + ml_platforms/) to async Rust:

| Python Component | Rust Equivalent |
|-----------------|-----------------|
| 6-stage pipeline | `tokio` async pipeline with stages as futures |
| HYDRA_ANALYZER_V2 | `HydraAnalyzer` with ML inference |
| ml_platforms/harness.py | Platform harness with burn/candle ML |
| ml_platforms/qlearning_table.py | Q-learning with burn-ndarray |
| ml_platforms/weakness_testing.py | Weakness testing framework |

**Cargo.toml dependencies:**
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
burn = "0.14"                  # Rust ML framework (or candle)
ndarray = "0.15"
rand = "0.8"
```

**Estimated effort:** 7-10 days

---

## Phase 3: Neural Advancements (Weeks 5-7)

### Crate: `azazael-neural`
**Status:** 🔴 Not started | **Priority:** P2 | **Dependencies:** `azazael-registry`, `azazael-memory`

Convert the three neural advancement modules to Rust:

| Python Component | Lines | Rust Equivalent |
|-----------------|-------|-----------------|
| MetaCognitionWorm | 493 | `MetaCognitionEngine` with observation buffer |
| EvolutionEngine | 412 | `EvolutionEngine` with rayon parallel fitness |
| DreamingModule | 511 | `DreamingModule` with async simulation |
| CurativePool | ~800 | `CurativePool` governance gates |

**Key improvements in Rust:**
- Parallel fitness evaluation via `rayon::par_iter()`
- Lock-free observation buffer via `crossbeam::queue::ArrayQueue`
- Async dreaming simulation via `tokio::spawn`
- Proper type safety for Genome/Dream/Observation structs

**Estimated effort:** 5-7 days

---

## Phase 4: GOSP — DoctoralThesisEngine (Weeks 2-8, ongoing)

### Crate: `gosp`
**Status:** 🟡 Started (338 lines) | **Priority:** P0 | **Dependencies:** `azazael-registry`, `azazael-memory`

Expand the existing GOSP Rust project into the full 7-tier DoctoralThesisEngine:

| Tier | Component | Status |
|------|-----------|--------|
| Tier 1: INGESTION | File scanner, format parser | 🔴 Not started |
| Tier 2: EXTRACTION | Semantic meaning extractor (local LLM) | 🔴 Not started |
| Tier 3: STRUCTURING | Knowledge graph builder | 🔴 Not started |
| Tier 4: HYDRAMETA | Cross-domain analysis engine | 🔴 Not started |
| Tier 5: DISTILLATION | Pattern synthesis (MetaCognitionWorm) | 🔴 Not started |
| Tier 6: DREAMING | Offline simulation (DreamingModule) | 🔴 Not started |
| Tier 7: PUBLICATION | Academic formatting, dissertation output | 🔴 Not started |

**CLI commands:**
```bash
gosp scan <path>            # Tier 1: Scan files and index
gosp harvest <query>        # Tier 2-3: Extract semantic meaning
gosp search <query>         # Tier 3: Search knowledge base
gosp serve                  # Tier 4-7: HTTP API server
gosp api <endpoint>         # REST API client
gosp tui                    # Interactive terminal UI
gosp train --epochs <N>     # Train with CurativePool governance
gosp dream --episodes <N>   # Run dreaming cycle
gosp thesis --output <dir>  # Generate dissertation
```

**Estimated effort:** 10-15 days for full 7-tier implementation

---

## Phase 5: CODEX & Tooling (Weeks 6-10)

### Crate: `azazael-codex`
**Status:** 🔴 Not started | **Priority:** P3 | **Dependencies:** None

Video generation pipeline in Rust:

| Python Component | Lines | Rust Equivalent |
|-----------------|-------|-----------------|
| make_video_vibrant.py | 1,415 | `codex-render` crate with `image` + `ffmpeg` |
| CODEX_Studio.py | 1,381 | `codex-studio` CLI + TUI |
| generate_dashboard_video.py | 1,215 | Dashboard video generator |
| SESSION_TEMPLATE | 5,536 | Template engine with `tera` or `handlebars` |

### Crate: `azazael-dashboard`
**Status:** 🔴 Not started | **Priority:** P3 | **Dependencies:** `azazael-memory`

Web dashboard (1,334 lines) in Rust:

```toml
[dependencies]
axum = "0.7"
maud = "0.26"          # Compile-time HTML templates
htmx = "0.6"           # HTMX frontend interactions
tower-http = "0.5"     # CORS, compression, tracing
```

---

## Migration Strategy

### Dual-Runtime Architecture (Transition Period)

```
┌─────────────────────────────────────────────┐
│              Azazael Runtime                 │
│                                              │
│  ┌──────────┐    PyO3 FFI    ┌───────────┐  │
│  │  Python   │◄─────────────►│   Rust    │  │
│  │  Runtime  │   (maturin)   │  Runtime  │  │
│  │           │               │           │  │
│  │ • CODEX   │               │ • Registry│  │
│  │ • POPUPs  │               │ • Memory  │  │
│  │ • Scripts │               │ • Cluster │  │
│  │ • Skills  │               │ • HYDRA   │  │
│  │ • Tests   │               │ • Neural  │  │
│  └──────────┘               └───────────┘  │
│                                              │
│  Python calls Rust via PyO3 bindings         │
│  Rust exposes Python modules via maturin     │
└─────────────────────────────────────────────┘
```

### Migration Order
1. Build `azazael-paths` (no deps, used by everything)
2. Build `azazael-registry` (no deps, used by cluster/neural/GOSP)
3. Build `azazael-memory` (depends on paths, used by everything)
4. Build `azazael-cluster` (depends on registry + memory)
5. Build `azazael-neural` (depends on registry + memory)
6. Build `gosp` (depends on all of the above)
7. Build `azazael-hydra` (depends on cluster + neural)
8. Build `azazael-codex` + `azazael-dashboard` (independent leaf crates)

### Cargo Workspace Structure

```
G:/source-of-truth/
├── Cargo.toml              # Workspace root
├── MANIFEST.json           # Source of truth manifest
├── crates/
│   ├── azazael-paths/      # Phase 1
│   ├── azazael-registry/   # Phase 1
│   ├── azazael-memory/     # Phase 1
│   ├── azazael-cluster/    # Phase 2
│   ├── azazael-hydra/      # Phase 2
│   ├── azazael-neural/     # Phase 3
│   └── azazael-codex/      # Phase 5
│   ├── gosp/              # GOSP (Phase 4)
│   │   ├── Cargo.toml
│   │   └── src/
│   └── azazael-dashboard/ # Phase 5
│       ├── Cargo.toml
│       └── src/
```

---

## What Stays Python

| Component | Reason |
|-----------|--------|
| CODEX SESSION_TEMPLATE (5,536 lines) | Template-heavy, Python string manipulation is sufficient |
| CODEX POPUPS (tkinter GUIs) | tkinter has no good Rust equivalent; keep as Python |
| Worm scripts (one-off utilities) | Rapid iteration; Python is faster for scripting |
| Skill documents (.md files) | Documentation, not code |
| Test suites | Test against both Python and Rust implementations |
| Nuitka standalone .exe builds | Continue for Python-only components; Rust crates get `cargo build --release` |
| Academic formatting (LaTeX, Markdown) | Python's text processing libraries are mature |
| Expansion modules (security, profiling, telemetry, container, config, backup, migration, communication, scheduling, db_monitor, visualization) | ~8,000 lines across 12 modules; low performance sensitivity, high configurability — stays Python unless profiling shows bottlenecks |

---

## Benchmark Targets

| Component | Python Baseline | Rust Target | Improvement |
|-----------|----------------|-------------|-------------|
| Worm discovery (88 worms) | ~10s cold start | <1s | 10x |
| Memory query (10K records) | ~500ms | <50ms | 10x |
| Cluster execution (parallel) | Thread-limited (GIL) | Full CPU utilization | 5-20x |
| Evolution fitness eval (50 genomes) | Sequential | Parallel (rayon) | 8-16x |
| GOSP file scan (1K files) | N/A (not built) | <2s | New capability |
| Binary size (standalone) | ~5-15 MB (Nuitka) | ~3-8 MB (Rust) | 40-50% smaller |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| PyO3 FFI overhead negates Rust perf gains | Benchmark before/after; use zero-copy where possible |
| Rust learning curve for contributors | Python stays for scripts; Rust for infrastructure only |
| Dual maintenance burden | Phase out Python implementations after Rust reaches parity |
| G: drive CI not reliable | Daily health check workflow already in place |
| Nuitka patch fragility | Rust eliminates Nuitka dependency for converted components |

---

## Per-Crate Acceptance Criteria

### `azazael-paths`
- [ ] `get_project_root()` matches Python `get_project_root()` output
- [ ] `get_g_drive()` resolves G:/ correctly
- [ ] All path functions return canonicalized paths

### `azazael-registry`
- [ ] `#[register_worm]` proc macro registers into global HashMap
- [ ] `discover_worms()` finds all 88+ worms in <1s (vs ~10s Python)
- [ ] `SpawnDiversityEngine::pick_next_spawn()` returns valid spawn with correct cooldown enforcement
- [ ] Category rotation never spawns same category consecutively
- [ ] Staleness bonus increases priority for never-spawned worms

### `azazael-memory`
- [ ] `record_event()` + `query_memories()` round-trip correctly
- [ ] `search_memories()` tantivy index returns BM25-scored results
- [ ] `get_stats()` matches LocalMemoryStore stats within 1% tolerance
- [ ] Connection pool handles 100 concurrent readers without deadlock

### `azazael-cluster`
- [ ] `MetaCluster` routes correctly across all 70 routes / 594 paths
- [ ] Parallel execution achieves >=5x throughput vs Python sequential
- [ ] Mermaid graph output matches Python output node-for-node

### `azazael-hydra`
- [ ] All 6 pipeline stages execute in correct order
- [ ] CurativePool governance gates at each stage
- [ ] MetaCognitionWorm observation fires after each stage
- [ ] Evolution optimization runs post-pipeline
- [ ] Dreaming cycle runs post-pipeline

### `azazael-neural`
- [ ] MetaCognitionEngine OBSERVE→ANALYZE→ADAPT→VALIDATE loop matches Python behavior
- [ ] EvolutionEngine tournament selection + crossover + mutation matches Python genetics
- [ ] DreamingModule RECALL→SIMULATE→EVALUATE→INTEGRATE pipeline matches Python output
- [ ] Parallel fitness evaluation achieves >=8x throughput vs Python sequential

### `gosp`
- [ ] All 9 CLI commands functional (`scan`, `harvest`, `search`, `serve`, `api`, `tui`, `train`, `dream`, `thesis`)
- [ ] TUI renders ratatui interface with all 5 original commands
- [ ] HTTP server mode responds to queries on configurable port

### Global
- [ ] All crates have `#[cfg(test)]` unit tests with >80% line coverage
- [ ] CI pipeline builds all crates and runs tests on G: drive
- [ ] `cargo build --release` produces binaries under 8 MB each
