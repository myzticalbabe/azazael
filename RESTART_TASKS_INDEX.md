# RESTART_TASKS index — EV id → board row

Generated from `RESTART_TASKS_2026-10-31.md` (16 EV entries, 29 distinct board row numbers) against `telemetry_store.db`. Regenerate with `python tools/restart_tasks_index.py`; do not hand-edit, the statuses move.

**The board owns the task text.** Each row below points at `memorybus_queue.content.detail`, which is the authoritative body. The EV sections in the source file keep only what a queue row cannot carry: the measurement, the refutation, and the correction.

> **Duplicate task_ids across rows:** `DUP-GUARD-CONTROL` → [46849, 46850]. Same text filed twice; retire one, do not work both.

| EV | subject | rows | lane(s) | status(es) |
|---|---|---|---|---|
| **EV-001** | PF16 reachability must be module-linked, then 134 rows re-disposed | [46818](EV-001-PF16-MODULE-LINK) | kilo | done |
| **EV-002** | 135 `wired` rows have no module-linked caller | [46819](EV-002-WIRED-ROWS-REAL) | kilo | done |
| **EV-003** | 37 dead controls | [46820](EV-003-DEAD-CONTROLS-37) | kilo | done |
| **EV-004** | `memory_store.db` at 1835 MB against a 500 MB configured quota | [46821](EV-004-STORE-1835MB) | kilo | done |
| **EV-005** | rotation UNVERIFIED (0 rotations recorded) | [46822](EV-005-ROTATION-UNVERIFIED) | kilo | done |
| **EV-006** | two gates are BLIND | [46823](EV-006-TWO-BLIND-GATES) | kilo | done |
| **EV-007** | semantic index under cap on the next full re-index | [46824](EV-007-SEMANTIC-INDEX-442MB) | kilo | done |
| **EV-008** | AP-5 finds one historical request in archived prose | [46825](EV-008-AP5-HISTORICAL) | kilo | done |
| **EV-009** | batch-loop queue protocol (built and verified this session) | no board row (narrative only) | — | no rows |
| **EV-010** | 33 control-named functions have no caller (tasked, not bulk-wired) | no board row (narrative only) | — | no rows |
| **EV-011** | domain trees (built; 8 of them measured, renders tasked) | [46829](DT-FK1), [46830](DT-FK2), [46831](DT-FK3), [46832](DT-TREE-SENTINEL), [46833](DT-TREE-CAIN), [46834](DT-TREE-EVE-RANI), [46835](DT-TREE-HIVES), [46836](DT-TREE-GOSP), [46837](DT-TREE-ML), [46838](DT-TREE-SHARDS), [46839](DT-TREE-EDGE0), [46840](DT-EDGE-RESOLVE), [46841](DT-MANDATE-0D), [46842](DT-MANDATE-0G), [46843](DT-MANDATE-0ZA), [46844](DT-MANDATE-PROVENANCE) | freebuff, kilo, opencode | blocked, claimed, done |
| **EV-012** | two inference mandates do not match the code (measured 2026-10-31, tasked) | no board row (narrative only) | — | no rows |
| **EV-012a** | these are DEFENCES, not generic policy (user, 2026-10-31) | no board row (narrative only) | — | no rows |
| **EV-014** | the WSL lanes were starting with NO standing orders (found and fixed 2026-10-31) | [46846](DT-MANDATE-PROVENANCE-2), [46847](DT-BOARD-BLOCKED-TRIAGE), [46851](DT-QUEUE-DUPLICATE-ROWS) | kilo | blocked, claimed |
| **EV-015** | the task queue was 2x duplicated, and nothing refused a re-post (fixed 2026-10-31) | [46849](DUP-GUARD-CONTROL), [46850](DUP-GUARD-CONTROL), [46851](DT-QUEUE-DUPLICATE-ROWS) | kilo | blocked, claimed, done |
| **EV-016** | the duplicate check was keyed on task_id alone (fixed 2026-10-31) | [46847](DT-BOARD-BLOCKED-TRIAGE), [46849](DUP-GUARD-CONTROL), [46850](DUP-GUARD-CONTROL) | kilo | blocked, done |

## Live rows (8 of 29)

Rows whose status is not `done`/`blocked`/`archived`. These are the ones the source list is still describing as outstanding, and they are the reason its prose still reads as a to-do list.

| row | lane | task_id | body starts |
|---|---|---|---|
| 46834 | kilo | `DT-TREE-EVE-RANI` | DT-3 EVE/RANI tree: domain_atlas_eve_rani currently reads src/eve_unleashed + src/ML/gosp.py (22 modules, 55 c |
| 46837 | kilo | `DT-TREE-ML` | DT-6 ML SHARDS tree: domain_atlas_ml.json (src/ML + src/ORCHESTRATION/ml_platforms, 50 modules, 104 classes).  |
| 46839 | kilo | `DT-TREE-EDGE0` | DT-8 EDGE0 tree: domain_atlas_edge0.json (C:/Users/clint/edge0-intel, 161 py of 1561 files, 142 classes). The  |
| 46840 | kilo | `DT-EDGE-RESOLVE` | DT-9 Domain edge counts are per-root sums (cross_root_edges_resolved=false). Build the honest version: scan a  |
| 46842 | kilo | `DT-MANDATE-0G` | DT-MANDATE-0G (Gemini mandate): RULE 0G requires spawning `thinker-with-files-gemini` at EVERY major phase. ME |
| 46843 | kilo | `DT-MANDATE-0ZA` | DT-MANDATE-0Z-A (6-API deep analysis): the azazael-6api-analysis skill and RULE 0Z-A require querying all infe |
| 46846 | kilo | `DT-MANDATE-PROVENANCE-2` | SCOPE REDUCED 2026-10-31: the per-clause DeepSeek-V4-Pro attribution is UNOBTAINABLE (no per-clause provenance |
| 46851 | kilo | `DT-QUEUE-DUPLICATE-ROWS` | DELETE THE 394 SURPLUS TASK ROWS (measured 2026-10-31). memorybus_queue holds 764 lane-task rows for 370 disti |

## What is deliberately NOT in this index

- The EV narrative (what was measured, what was refuted, what the numbers were). It stays in the source file, because a queue row is a work order, not a record of a measurement.
- Retired rows: 21 of the 29 cited ids are retired. A row retired later changes its status column on the next regeneration; nothing else needs editing.
