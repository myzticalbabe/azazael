# Tree Drift & SNA Diff — Windows vs WSL ecosystem graphs — 2026-09-07

Pipeline rerun on both runtimes with the same code:
- WSL: `python3` (free-threaded 3.14t, GIL-guarded scripts) — 603 .py files
- Windows: `Python314` 3.14.7 GIL-enabled via `scripts/win_run_pipeline.bat` — 632 .py files

## Tree drift (`.py` inventory)

| direction | count | contents |
|-----------|-------|----------|
| Windows-only | 55 | `src/AOA/` (24), `src/CORE/` additions (16: `codebase_graph.py`, `graph_drift.py`, `graph_artifacts.py`, `project_atlas.py`, `WORM_FLEET.py`, `pattern_memory.py`, `archive_store.py`, `ERROR_SCAN_WORM.py`, `full_scan.py`, `_logging_shim.py`, `worm_health.py`, `BENCHMARK_WORM.py`, `CLAWBOT.py`, ...), cycle drivers (`scripts/dream_cycle.py`, `evolution_cycle.py`, `metacog_cycle.py`, `monitor_learning.py`, `rollover_archive.py`), `scripts/gephi_headless/` (headless Gephi engine), `src/SCRIPTS/` (4), `src/CODEX/` (2), misc |
| WSL-only | 1 real | `src/CORE/paths.py` (legacy module — see below) |

The apparent 25 WSL-only `src/scripts/*` files are a **case-sensitivity false positive**: WSL has separate `src/scripts/` and `src/SCRIPTS/` dirs; Windows is case-insensitive, so both names are one dir and all 25 files exist there.

### `src/CORE/paths.py` — legacy, deliberately removed on Windows
- Windows git history shows `paths.py` was tracked then **removed** when `src/CORE/paths/` (the domain package: `internal.py`, `external.py`, `state.py`, `targets.py` + shim `__init__.py`) replaced it (package dated Aug 29 vs WSL's June 17).
- WSL still carries BOTH the legacy module and an older copy of the package.
- **Fix applied:** synced the newer Windows package (all 5 files) into WSL → byte-identical now. Did NOT re-add `paths.py` to Windows (would shadow/conflict; Python prefers the package anyway). 109 Windows files import `CORE.paths` and resolve via the package.
- Note: this changes WSL's ecosystem graph — `paths.py` node (betweenness #2 on WSL) becomes `paths/__init__.py` (as on Windows).

## SNA diff (603-node WSL vs 632-node Windows)

### Network metrics
| metric | WSL | WIN |
|--------|-----|-----|
| density | 0.0029 | 0.0028 |
| avg_degree | 1.755 | 1.772 |
| diameter | 10 | 10 |
| avg_shortest_path | 4.028 | 3.715 |
| communities | 327 | 341 |
| largest community | 52 | 49 |

### Rankings are stable across the drift
**Top influence (eigenvector)** — identical order in both: `worm_registry.py`, `freethreading.py`, `learning.py`, `local_memory.py`, `METACLUSTER.py`, `NATURE_CLUSTERS.py`. Only #5/#6 swap (`scheduling.py` vs `PamsRecorder.py`).

**Top bridges (betweenness)** — `worm_registry.py` #1 in both. Differences are the expected file-level shifts:
- WSL #2 `src/CORE/paths.py` → WIN #2 `src/CORE/paths/__init__.py` (the legacy→package swap above)
- Windows adds `src/CORE/__init__.py` (#3) and `azazael_ctl.py` (#7) as bridges — files absent from WSL
- `compliance/orchestrator.py` + `pre_action_gate.py` rank higher on WSL (those files' importers live there)

### K-core shells
- 5-core backbone: n=19 in both (the cluster-worm spine)
- 4-core: 31 (WSL) vs 24 (WIN); 3-core: 40 vs 45; 2-core: 75 vs 89 — Windows pulls more modules into mid-cores via the AOA subsystem and cycle drivers (`dream_cycle.py`, `evolution_cycle.py` enter the 3/2-cores)

## Bottom line
The learning-loop core (learning.py, local_memory, meta_cognition, dreaming) ranks identically in influence on both runtimes. The SNA deltas are all attributable to the 55 Windows-only files (AOA, CORE tooling) and the paths.py→package migration. Recommend a one-way sync of the 55 Windows-only files into WSL for full parity (not done here — those are Windows-native subsystems and WSL may not have their deps).