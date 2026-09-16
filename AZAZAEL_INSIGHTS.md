# AZAZAEL INSIGHTS — Session Memories & Architectural Reflections

> *Generated: May 28, 2026 — Last updated: July 6, 2026 (DirectMemory v1.1.0)*

---

## 1. Architecture Overview (Current State)

### Worm Registry — The Central Nervous System
- **226 worms** registered across **35 categories** via `CORE/worm_registry.py` *(2026-09-14 clean rebuild ×2; was 184/27, 77/17 pre-neural-mesh)*
- Categories: analysis, axon, backup, communication, config, consensus, consolidation, container, defense, dendrite, diagnostic, engram, envmesh, federated, glia, immune, learning, mesh, metabolic, migration, ml, monitor, network, orchestration, plasticity, profiling, security, servemesh, synapse, sync, telemetry, thalamus, utility, visualization, xenomorph
- Dynamic discovery via `discover_worms()` scanning `CORE/WORMS/`, `META/`, and top-level `src/`
- Decorator-based: `@register_worm(category="security", priority=5, ...)`

### Cluster Architecture (New — This Session)
```
NATURE_CLUSTERS.py          METACLUSTER.py
       │                          │
       │  NatureCluster            │  MetaCluster
       │  (per-category)           │  (cluster-of-clusters)
       │       │                  │       │
       │       ▼                  │       ▼
       │  CLUSTERWORMS.py ◄────────┤  CrossNatureRoutingEngine
                       │  (dynamic resolution)     │  (70 routes, 594 paths)
       │       │                  │
       ▼       ▼                  ▼
  WORM_REGISTRY ──────── PamsRecorder ──────── MemoryBus
```

### Key Files Modified This Session

| File | Change | Impact |
|------|--------|--------|
| `CORE/WORMS/CLUSTERWORMS.py` | Complete rewrite — dynamic worm resolution, PAMS/MemoryBus, Mermaid graphs, Nature-based building | Replaced hardcoded if/elif with registry lookup |
| `CORE/WORMS/NATURE_CLUSTERS.py` | NEW — NatureCluster + NatureClusterManager | 35 auto-discovered categories |
| `CORE/WORMS/METACLUSTER.py` | NEW — MetaCluster + CrossNatureRoutingEngine | 70 routes, 594 cross-nature paths |
| `CORE/paths.py` | NEW — Centralized path resolution | Cached, env-var-aware paths |
| `METAWORMS.py` | Deprecation shim → re-exports from `METAWORMS_ENRICHED` | Backward compatible |

---

## 2. Design Decisions & Rationale

### Why Dynamic Resolution over Hardcoded Dispatch
- **Before**: 15+ explicit imports + if/elif chain in `WormExecutor.execute()`
- **After**: 3-strategy resolution:
  1. WORM_REGISTRY lookup (fast, metadata-rich)
  2. Legacy dispatch dict (backward compat)
  3. Import-by-convention via `_WORM_MODULE_MAP`
- **Impact**: Adding a new worm now only requires `@register_worm(...)` — zero changes to CLUSTERWORMS.py

### Why Nature-Based Clustering
- Worms naturally group by function (security, profiling, monitoring, etc.)
- `NATURE_CLUSTERS.py` auto-discovers these groups from the registry
- `METACLUSTER.py` orchestrates cross-nature workflows
- Enables parallel execution of independent nature groups

### PAMS/MemoryBus/DirectMemory Integration
- Every cluster action records to `PamsRecorder` (44 events, 44 pams recorded)
- `MemoryBus` publishes cluster lifecycle events (start, complete, error)
- **DirectMemory v1.1.0** (July 6, 2026) now handles cross-session learning:
  - `record_decision()` / `record_lesson()` / `set_goal()` for agent knowledge
  - `get_context_for_new_session()` feeds past learnings back at session start
  - 37-event `_V` canonical vocabulary with `validate_event_type()`
  - 14 static query/maintenance methods (summary_stats, db_size, integrity_check, purge, merge, replay, session_gc, import_events, filtered_query, session_search, mapping, crossref)
  - Replaces SessionMemory — `workspace/session_memory.db` has 0 sessions, never populated
- Session-level persistence for post-mortem analysis

### Thread Safety Design
- `results_lock` (threading.Lock) for parallel execution path
- `_cancellation` Event for graceful shutdown
- Retry logic in sequential path (respects `config.retry`)

---

## 3. Pre-Existing Issues Catalogued (Not Introduced This Session)

| File | Issue | Severity | Status |
|------|-------|----------|--------|
| `TRIMZ.py:90` | `_LOCAL_TARGETS = [_PROJECT_ROOT]` — narrow desktop target list | Low | Config, not bug |
| `ERRORZ.py:93` | Same `_LOCAL_TARGETS` pattern | Low | Config, not bug |
| `MORPHING_WORM.py:131` | Bare except clause tracked | Info | By design |
| `OMNI_WORM_V2.py:27` | `syntax_traps` includes `except:` as detectable pattern | Info | By design |
| Multiple files | `except Exception` (broad) in non-critical paths | Low | Acceptable for worms |
| System | `pathlib.PurePosixPath` imported in TRIMZ.py but unused | Trivial | Cleanup opportunity |

---

## 4. Mermaid Graph Architecture

### Cluster Hierarchy
```mermaid
graph TD
    MC[MetaCluster] --> NC1[NatureCluster: security]
    MC --> NC2[NatureCluster: profiling]
    MC --> NC3[NatureCluster: monitor]
    MC --> NC4[NatureCluster: container]
    MC --> NC5[NatureCluster: communication]
    MC --> NC6[NatureCluster: backup]
    MC --> NC7[NatureCluster: config]
    MC --> NC8[NatureCluster: system]
    MC --> NC9[NatureCluster: diagnostic]
    MC --> NC10[NatureCluster: optimization]
    MC --> NC_N[NatureCluster: ...17 total]
    
    NC1 --> W1[SECURZ]
    NC1 --> W2[CRYPTOZ]
    NC3 --> W3[SYSTEMZ]
    NC3 --> W4[PROCESSZ]
    
    MC --> RE[CrossNatureRoutingEngine]
    RE --> R1[security→monitor]
    RE --> R2[profiling→optimization]
    RE --> R3[container→backup]
```

### Execution Flow
```mermaid
sequenceDiagram
    participant User
    participant ClusterWORMZ
    participant WormRegistry
    participant WormExecutor
    participant PamsRecorder
    participant MemoryBus
    
    User->>ClusterWORMZ: build_from_nature("security")
    ClusterWORMZ->>WormRegistry: get_worms_by_category("security")
    WormRegistry-->>ClusterWORMZ: [SECURZ, CRYPTOZ, ...]
    ClusterWORMZ->>PamsRecorder: record_event("cluster.build", ...)
    ClusterWORMZ->>MemoryBus: publish("cluster.execute.start", ...)
    
    loop Each worm
        ClusterWORMZ->>WormExecutor: execute(worm_config)
        WormExecutor->>WormRegistry: _resolve_worm_dynamic(name)
        WormRegistry-->>WormExecutor: worm class/function
        WormExecutor-->>ClusterWORMZ: result
    end
    
    ClusterWORMZ->>PamsRecorder: record_event("cluster.complete", ...)
    ClusterWORMZ->>MemoryBus: publish("cluster.execute.complete", ...)
    ClusterWORMZ-->>User: [results]
```

---

## 5. CODEX Video Status

| Capability | Status | Notes |
|-----------|--------|-------|
| PIL frame generation | ✅ Working | 13.7 fps, 96KB/frame @ 1920×1080 |
| ffmpeg for .mp4 | ❌ Not installed | Needs `winget install ffmpeg` or manual install |
| Scrolling video generator | ⚠️ Import-ready | `create_scrolling_video.py` retained; requires ffmpeg |
| Archived superseded scripts | ✅ Done | 14 duplicated/older scripts → `G:\AZAZAEL\CODEX_VIDEOS\` |

---

## 6. G:\ Drive Archive

```
G:\AZAZAEL\
├── CODEX_VIDEOS\          # 14 superseded video scripts
│   ├── make_video_v2.py
│   ├── make_video_v3.py
│   ├── make_video_quad.py
│   ├── make_video_zip.py
│   ├── make_video_zipper.py
│   ├── make_video_vibrant.py
│   ├── make_video_docs.py
│   ├── create_reference_video.py
│   ├── create_dual_pane_popup.py
│   ├── create_azazael_educational_video.py
│   ├── generate_video.py
│   ├── generate_video_v2.py
│   ├── generate_matrix_video.py
│   └── video_popup.py
└── frames\                # Test frame output directory
```

---

## 7. Key Metrics

| Metric | Value |
|--------|-------|
| Total Python files (syntax-clean) | 256 |
| Worms in registry | 104 (runtime verified July 6, 2026) |
| Categories | 18 (runtime verified) |
| DirectMemory version | **v1.1.0** (37 _V types, learning loop, 14 static methods) |
| DirectMemory DB | 1,116 MB, 79,189 sessions, 646,755 events |
| Cross-nature routes | 46 |
| Cross-nature paths | 264 |
| PAMS events recorded | 44 |
| PAMS records | 44 |
| MemoryBus publications | 1 (test) |
| Cluster build_full_ecosystem | 226 worms |
| Mermaid graph (NATURE_CLUSTERS) | 8,535 chars |
| PIL frame generation speed | 13.7 fps |

---

## 8. Lessons Learned

1. **JSON escaping in spawn_agents**: Windows `cmd.exe` has severe escaping issues with nested quotes. Solution: write Python scripts to file, then run them. Far more reliable.

2. **Python f-string backslash restrictions**: Python < 3.12 doesn't allow backslash escapes inside f-string expressions. Pre-extract variables. Fixed in `METACLUSTER.py:694`.

3. **Emoji on Windows**: Unicode emoji characters can cause `UnicodeEncodeError` in terminals without `PYTHONIOENCODING=utf-8`. Replaced with ASCII alternatives in Mermaid output.

4. **Don't use `cls.__new__()` for factory methods**: Use `cls()` + manual init, or a proper classmethod factory. Fixed in `CLUSTERWORMS.build_from_nature()`.

5. **Thread safety matters even with GIL**: In free-threading Python (3.14t), `list.append()` from multiple threads without a lock is a race condition. Use `threading.Lock()`.

6. **Deprecation shims > deletion**: Converting `METAWORMS.py` to a deprecation shim preserves backward compatibility for the 3 test files that import it.

---

## 9. Reflection

The Azazael ecosystem has evolved from a collection of standalone worm scripts into a cohesive, registry-driven architecture. The three-tier cluster system (CLUSTERWORMS → NATURE_CLUSTERS → METACLUSTER) enables both targeted single-nature operations and cross-nature orchestration. **DirectMemory v1.1.0 (July 6, 2026) is now fully self-sufficient** — the canonical session recorder handles all cross-session learning (decisions, lessons, goals) via event-based recording in its existing `memories` table, eliminating the need for a separate SessionMemory database.

Key architectural strengths:
- **Registry as single source of truth** for worm discovery
- **Nature-based grouping** maps naturally to operational domains
- **Mermaid graph generation** enables visual documentation at all levels
- **Backward compatibility** maintained via deprecation shims and fallback dispatch
- **DirectMemory self-sufficiency** — stdlib-only, <0.1s, 37-event vocabulary, agent learning loop, no external DB dependencies

Areas for continued investment:
- Test coverage (currently minimal)
- Error recovery (timeout handling, partial failures)
- Performance profiling (parallel execution bottlenecks)
- Documentation (module-level docstrings, architecture diagrams)

---

## 10. Session Error Patterns (New — Error Recording SOP)

### Mandatory Error Recording
As of this session, a mandatory **ERROR LOG** system has been established:
- `ERROR_LOG.md` — 140 errors catalogued, max #189 (2026-09-14; was 15 at writing) with timestamps, causes, fixes, preventions
- `SYSTEM_INSTRUCTIONS.md` — SOP requiring error recording BEFORE proceeding to next task

### Top Error Patterns
| Pattern | Frequency | Root Cause |
|---------|-----------|------------|
| JSON escaping in spawn_agents | 3 | Nested quotes in Windows shell |
| Unicode emoji on Windows | 3 | Terminal encoding mismatch |
| Python f-string backslash | 2 | Python < 3.12 limitation |
| Code hygiene (unused imports, temp files) | 4 | No pre-commit linting |

### Prevention Rules Established
1. Write Python scripts to temp files — never nest quotes in basher
2. Use ASCII alternatives (OK/FAIL/*) instead of Unicode symbols
3. Pre-extract computed expressions before f-strings
4. Run import linter before committing
5. Maintain post-session cleanup checklist

---

## 11. Worm Config Trace Summary (New)

Full per-worm configuration audit completed: `WORM_CONFIG_TRACE.md` + `worm_config_trace.json`

### Key Findings
- **62% of worms** (48/77) originate from a single file: `ECOSYSTEM_EXPANSION.py`
- **Highest priority**: MetaCluster (p=10, cooldown=5s)
- **Longest cooldown**: ColdArchivist (300s = 5min)
- **Version anomalies**: ClusterWORMZ v2.0.0 (upgraded this session), 4 worms at v0.0.0 (pre-release)
- **All 226 worms have 0 spawns** — SpawnDiversityEngine ready but unused in production

### Category Distribution
| Priority | Count |
|----------|-------|
| 10 | 1 (MetaCluster) |
| 9 | 1 (NatureClusterManager) |
| 8 | 3 (ClusterWORMZ, SystemZ, VulnScanner) |
| 7 | 8 |
| 6 | 15 |
| 5 | 23 |
| 4 | 16 |
| 3 | 7 (utility/infrastructure) |

---

## 12. Per-Function Mesh Audit (2026-09-16)

Full per-function pre-flight audit of the mesh: **1411 functions across 63
modules**, 21 automated probes (PF01-PF21) plus 6 manual checks (M1-M6).
Generator: `tools/mesh_function_preflight.py` (deterministic, re-runnable).
Checklist: `NEURAL_MESH_FUNCTION_TODO.md`. Analysis: `NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`.
Census: P0 130 / P1 319 / P2 890; 72 functions pass every probe.

### The census, re-ranked by risk not count

| probe | failing | reads as |
|-------|---------|----------|
| PF04 | 1106 | annotation debt (review cost, no risk) |
| PF02 | 693 | docstring debt (review cost, no risk) |
| PF17 | 532 | **38% of the mesh is reached by no test** |
| PF14 | 300 | catches `Exception` alone |
| PF15 | 118 | **swallows the evidence** |
| PF16 | 114 | **nothing in the repo references it** |
| PF18 | 15 | writes module-level state (concurrency) |

PF02+PF04 (1799) dominate the counts and carry no risk. The probes describing
functions the mesh cannot test, cannot reach, or cannot see failing total 764 -
and every real bug found this session came from that set.

### Bugs found and fixed (all P0, all silent)

| Function | Defect | Why monitoring missed it |
|----------|--------|--------------------------|
| `EvolutionEngine.evolve` | snapshot taken outside the lock, blind write-back -> a whole generation of offspring discarded while `_generation` advanced twice | produced plausible output, only faster |
| `EvolutionEngine.optimize_multi_objective` | elite slot `-(obj_idx+1)` walks off the list when objectives > survivors -> `IndexError` escapes the whole optimisation | only reachable when a caller adds an objective |
| `moead_weights` | fallback drew twice for `n_obj == 2`, so Tchebycheff weights did not sum to 1 -> every comparison mis-scaled | wrong output is still output |
| `save_checkpoint` / `_get_store` / `restore_checkpoint` | success-shaped return while persisting nothing; relevance-ranked search could return a STALE checkpoint | stale state looks like state |

Common signature: **the code reported success without establishing the
precondition for it.** None produced a traceback, a log line, or a red monitor.

### New primitives (built because the shapes recurred)

- **`CORE/WORMS/expansion/fencing.py`** - Kleppmann fencing tokens reapplied from distributed locks to in-process shared state. A writer mints a monotonic token before starting, works unlocked, and only the commit path writes; a stale token cannot commit. Process-wide on purpose (an instance lock cannot see a sibling instance). Never blocks, never raises; `fence_report()` makes contention trendable. Justified by PF18 = 15 module-level writers.
- **`CORE/WORMS/expansion/silence.py`** - silent-failure ledger. `pass` destroys a measurement: "the fabric healed" and "the fabric failed to load its learning every start for a week" are byte-identical. Two moves beyond a counter: **signature clustering** is the alarm (a rising count is a flaky peer; a NEW exception type is an unpredicted failure mode), and **budgets** make "graceful" checkable (`budget=0` = this failure is a fault). Bounded at 24 signatures and 512 tags. Justified by PF15 = 118.

Tests: `tests/test_mesh_audit_insights.py` (21).

### Inferred, recorded, not yet built

1. **Non-occurrence monitoring.** All 4 defects above are events that did *not* happen, and every existing monitor is occurrence-driven. More occurrence telemetry is structurally incapable of catching them. The missing primitive is a **liveness obligation**: a named expectation with a deadline, minted by the code that should cause it and discharged when it fires. `fence_report()` rejections and `silence_report()` tripped() are the only two places in the mesh that record a negative today.
2. **Coverage obligation as data.** PF16 = 114 should be resolved by generalising the `SERVED_ENGINES` / `UNSERVED_ENGINES` wire-or-cut pattern from `evolution.py` - a decision recorded as data with a test asserting the data matches reality - rather than by writing tests for code nothing calls.
3. **Auditor precision as a trended quantity.** 4 of 21 probes were miscalibrated on first run (PF13, PF15, PF20, PF21); every cleared finding was a human judgement that the process currently discards. Persisting the census per session and recording rejected findings turns a one-off audit into a time series and makes auditor drift observable.

### Method lessons

1. Calibrate the instrument before acting on its reading - acting first would have manufactured 13 fake "unbounded loop" fixes.
2. Sort the backlog by consequence-if-live, not by count.
3. Promote a recurring fix shape to a primitive; a fix applied N times is a fix that will be forgotten N times.
4. If a function cannot fail, its caller cannot know - report the side effect's fate in the return value.
5. Verify the verifier - tests written to demonstrate a fix encode the author's model of the bug, not an independent check of it.

Reasoning traces (13) recorded for training: `data/training/neural_mesh_function_audit_2026-09-16.jsonl`.
