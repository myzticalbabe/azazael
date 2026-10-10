# Wire decisions — `test_is_the_wire` rows — 2026-10-10 (Worker E)

Source: `NEURAL_MESH_WIRE_OR_CUT_WORKLIST.md`, decider `test_is_the_wire`.
Worklist `test_is_the_wire` pending count: **44**. Rows decided below: **44**. Match: YES (44/44).
Scope: `test_reached_only` rows whose bracket tag is `test_is_the_wire` (the 6 `dynamic_call` rows in that section are out of scope).
Method: (1) opened each cited `tests/<file>` at each cited line, confirmed the line names the function;
(2) targeted content search for the function name across `src/` (excluding `tests/`, excluding the worklist itself).
`*.pre_gate_backup` duplicates inside `src/` are reported but NOT counted as live production callers.
Docstring Usage examples, code comments, `register()` host-string mentions, and f-string runbook text are NOT counted as callers.
Decisions only — no code cut, no production callers implemented. Escalations are proposals for the coordinator.

Summary counts: ACCEPT-TEST-AS-WIRE **28** / ESCALATE **16** / STALE-VERIFY **0**.
All 44 cited test-reference sets verified Y on the exact cited line (one weak ref noted: `test_mesh_clock_poison.py:286` names the function inside a message-content string assertion, not a call — still Y per "names the function", flagged in table).

| function | test ref (verified Y/stale) | production callers found in src/ | decision | rationale |
|---|---|---|---|---|
| `NeuralPipeline.replay_failed` | tests/test_replay_failed.py:42 (Y), :53 (Y), :47 (Y) | none — 4 hits: live def `src/CORE/NeuralPipeline.py:725`, 1 backup def, 1 contract comment (:732), 1 f-string (:753) | ESCALATE | Needs production caller: DLQ replay path is unwired, dead letters accumulate with no prod replay — suggested call site: `CORE/neural_loop.py` recovery stage or an operator DLQ command supplying `execute_fn`. |
| `chorus.FailureDigest.from_analysis` | tests/test_proteus_organs.py:718 (Y) | none — 1 hit: def `src/CORE/WORMS/expansion/chorus.py:85` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_proteus_organs.py:718 pins peak/allocator→digest mapping); value-object factory, no standalone prod path needed yet. |
| `db_monitor.DatabaseMonitorWorm._policy_advice` | tests/test_policy_advice.py:56 (Y) | none — 1 hit: def `src/CORE/WORMS/expansion/db_monitor.py:436` (not even an internal self-call) | ESCALATE | Needs production caller: private advisory nothing reads (zero internal callers) — suggested call site: `DatabaseMonitorWorm` alert/monitoring loop attaching `loop.recommend` advice to alerts. |
| `db_monitor.DatabaseMonitorWorm.create_backup` | tests/test_db_monitor_worm.py:445 (Y), :458 (Y), :479 (Y) | none exact — 20 hits, 19 are different symbols (`_create_backup`, `create_backup_snapshot`); sole exact hit is live def `src/CORE/WORMS/expansion/db_monitor.py:215` | ESCALATE | Needs production caller: backup capability with no scheduler/operator caller — suggested call site: `ScheduledDbMonitorWorm` cycle or scheduled maintenance loop. |
| `engram.RecallRouterWorm.route_recall` | tests/test_spine_mesh.py:953 (Y), :959 (Y), :962 (Y) | FOUND (2 live callers): `src/CORE/technique_wiring/_l1_memory.py:256` (`router.route_recall(...)` in `ep235`) and `:368` (`RecallRouterWorm().route_recall(...)` in `ep389`); plus def `engram.py:400`, docstring/register strings (not callers) | ACCEPT-TEST-AS-WIRE | Already wired in production (`_l1_memory.py:256,368`); test is supplementary contract (tests/test_spine_mesh.py:953) — worklist "only caller" claim is stale. |
| `error_recovery.ErrorRecoveryOrchestrator.execute_with_recovery` | tests/test_error_recovery.py:76 (Y), :95 (Y), :115 (Y) | none — 2 hits: def `:100`, docstring Usage example `:78` (not executable) | ESCALATE | Needs production caller: central retry/circuit-breaker wrapper nothing uses, worms execute unprotected — suggested call site: MetaCluster/ClusterWORMZ dispatch or `neural_loop` stage execution wrap. |
| `error_recovery.ErrorRecoveryOrchestrator.reset_circuit` | tests/test_error_recovery.py:193 (Y), tests/test_p0_worms.py:261 (Y), :286 (Y) | none — 1 hit: def `:328` | ESCALATE | Needs production caller: pairs with `execute_with_recovery`; no ops reset path — suggested call site: health-monitor/alert-remediation loop or operator ops path resetting after recovery. |
| `evolution.GeneticOptimizer.optimize_cma` | tests/test_v2_engines.py:187 (Y) | none — 2 hits: def `evolution.py:1428`, comment `:1585` | ESCALATE | Needs production caller: deferred optimizer backend, `optimize()` never dispatches to it — suggested call site: `GeneticOptimizer.optimize` backend selection or evolution scheduling path. |
| `evolution.GeneticOptimizer.optimize_de` | tests/test_v2_engines.py:194 (Y) | none — 1 hit: def `evolution.py:1441` | ESCALATE | Needs production caller: same as `optimize_cma` (DE backend undispatched) — suggested call site: `GeneticOptimizer.optimize` dispatch or evolution scheduling path. |
| `learning_features.SchemaAwareFeatureExtractor.fallback_accuracy_report` | tests/test_learning_worms.py:593 (Y), :611 (Y) | none — 2 hits: live def `learning_features.py:357` + backup def | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_learning_worms.py:593 pins fallback telemetry report); no prod caller needed. |
| `learning_pipeline.DataPipelineWorm.extract_field` | tests/test_learning_worms.py:68 (Y) | none — 4 hits: live+backup defs, 2 docstring Usage examples (not executable) | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:68); ETL transform factory in public pipeline toolkit, deferred-production consumer. |
| `learning_pipeline.DataPipelineWorm.extract_recent` | tests/test_learning_worms.py:42 (Y) | none — 2 hits: live def `:161` + backup def | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:42); thin `recall_recent` read delegate, public read API. |
| `learning_pipeline.DataPipelineWorm.filter_by_severity` | tests/test_learning_worms.py:79 (Y) | none — 3 hits: live+backup defs + 1 comment mention | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:79); ETL filter factory, deferred-production consumer. |
| `learning_pipeline.DataPipelineWorm.filter_by_source` | tests/test_learning_worms.py:90 (Y) | none — 3 hits: live+backup defs + 1 comment mention | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:90); ETL filter factory, deferred-production consumer. |
| `learning_pipeline.DataPipelineWorm.get_memory_stats` | tests/test_learning_worms.py:48 (Y) | none — 2 hits: live+backup defs | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_learning_worms.py:48); stats delegate, no prod caller needed. |
| `learning_pipeline.DataPipelineWorm.load_to_memory` | tests/test_learning_worms.py:151 (Y) | none — 2 hits: live def `:260` + backup def | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:151); public ingest API (`record_event` entry), deferred-production producers. |
| `learning_pipeline.DataPipelineWorm.process_batches` | tests/test_learning_worms.py:128 (Y) | none — 2 hits: live def `:276` + backup def | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:128); generic batch utility, no prod caller needed. |
| `learning_pipeline.DataPipelineWorm.schedule_dynamic_refresh` | tests/test_learning_worms.py:544 (Y), :553 (Y), :564 (Y) | none — 2 hits: live def `:559` + backup def | ESCALATE | Needs production caller: docstring says "In a production daemon, call this periodically", nothing does — suggested call site: scheduler daemon / `ScheduledTrainingWorm` cycle / `neural_loop` periodic stage. |
| `learning_pipeline.DataPipelineWorm.search_memory` | tests/test_learning_worms.py:37 (Y) | none — 2 hits: live def `:154` + backup def | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_learning_worms.py:37); thin FTS5 `search_memories` delegate, public read API. |
| `learning_replay.PrioritizedReplayBuffer.add_from_memories` | tests/test_learning_evolution.py:97 (Y), :108 (Y) | none — 1 hit: def `:172` | ESCALATE | Needs production caller: Memory→Replay bridge never fed in prod — suggested call site: `RLTrainLoop` training prep or pipeline→replay ingestion step. |
| `learning_rl.RLTrainLoop.tune_and_train` | tests/test_learning_worms.py:354 (Y), :367 (Y) | none — 2 hits: live def `:858` + backup def | ESCALATE | Needs production caller: combined tune+train entry with no scheduled caller — suggested call site: `ScheduledTrainingWorm` / `TrainingOrchestrator` scheduled training path. |
| `learning_rl.RLTrainLoop.tune_history` | tests/test_learning_worms.py:382 (Y), :395 (Y) | none — 2 hits: live def `:988` + backup def | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_learning_worms.py:382); history query readout, no prod caller needed. |
| `loom.NoveltyDrive.novelty_weight` | tests/test_proteus_organs.py:530 (Y), :531 (Y) | none — 1 hit: def `:272` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_proteus_organs.py:530 pins capped weight); pure helper, deferred-production outer-loop consumer. |
| `loom.descriptors_from_archive` | tests/test_proteus_organs.py:551 (Y) | none — 1 hit: def `:320` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_proteus_organs.py:551); pure archive→point-cloud adapter, deferred-production QD consumer. |
| `meta_cognition.MetaCognitionWorm.compute_cross_worm_correlation` | tests/test_neural_advancement.py:213 (Y), :220 (Y), :226 (Y) | none — 1 hit: def `:941` | ESCALATE | Needs production caller: cross-worm analytics never runs in prod loop — suggested call site: `MetaCognitionWorm` periodic analysis / `neural_loop` meta stage. |
| `morph.Genome.to_trainer_kwargs` | tests/test_proteus_organs.py:115 (Y), :127 (Y), :138 (Y) | none — 1 hit: def `:260` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_proteus_organs.py:115 pins gene→kwarg mapping); downstream trainer opt-in, deferred-production. |
| `morph.load_genome` | tests/test_proteus_organs.py:314 (Y), :320 (Y) | none — 1 hit: def `:503` | ESCALATE | Needs production caller: persistence round-trip half with no checkpoint-restore caller — suggested call site: `EvolutionEngine` generation checkpoint restore / operator resume path (pairs with `save_genome`). |
| `morph.save_genome` | tests/test_proteus_organs.py:313 (Y) | none — 1 hit: def `:495` | ESCALATE | Needs production caller: no checkpoint-persist caller — suggested call site: `EvolutionEngine` generation checkpointing (pairs with `load_genome`). |
| `scheduling.ScheduledTrainingWorm._get_ab` | tests/test_scheduling.py:205 (Y) | none — 1 live def `:216` (+1 different symbol `_get_ab_runner` elsewhere, not a caller) | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_scheduling.py:205 verifies lazy constructor suite); getter needs no prod caller, AB path deferred-production. |
| `scheduling.TrainingOrchestrator.get_run_history` | tests/test_training_orchestrator.py:95 (Y) | none — 1 hit: def `:1140` | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_training_orchestrator.py:95); history introspection for operators, prod status covered by `get_status`. |
| `spine_registry.audit_state` | tests/test_brainstem_playing_field.py:230 (Y) | none — 4 hits: def `:2272` + 3 comments | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_brainstem_playing_field.py:230); provenance classifier introspection, no prod loop needed. |
| `spine_registry.counter_floor_report` | tests/test_spine_brainstem_persistence.py:563 (Y) | none — 1 hit: def `:2236` | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_spine_brainstem_persistence.py:563); resets-in-force ledger readout. |
| `spine_registry.get_gossip_trust_state` | tests/test_gossip_trust_allowlist.py:243 (Y), tests/test_spine_mesh.py:1105 (Y), :1147 (Y) | none — 1 hit: def `:3563` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_gossip_trust_allowlist.py:243); trust policy/crypto readout, diagnostic. |
| `spine_registry.get_module_health` | tests/test_spine_mesh.py:299 (Y) | none — 1 hit: def `:3222` | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_spine_mesh.py:299); module health endpoint contract. |
| `spine_registry.get_q_evidence` | tests/test_brainstem_playing_field.py:123 (Y), :131 (Y), :157 (Y) | none — 1 hit: def `:2078` | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_brainstem_playing_field.py:123 pins ledger-fallback evidence); introspection API. |
| `spine_registry.homeostat_reset` | tests/test_spine_mesh.py:114 (Y), :125 (Y), :140 (Y) | none — 1 hit: def `:3021` | ACCEPT-TEST-AS-WIRE | Fixture hygiene / explicit operator reset (tests/test_spine_mesh.py:114 test setup); no routine prod caller desired. |
| `spine_registry.purge_fixtures` | tests/test_brainstem_playing_field.py:241 (Y), tests/test_spine_tombstone_enforcement.py:84 (Y), :91 (Y) | none — 5 hits: def `:2328` + 4 comments | ACCEPT-TEST-AS-WIRE | Fixture hygiene (tests/test_brainstem_playing_field.py:241); on-demand tombstoning purge, no routine prod caller desired. |
| `spine_registry.purge_implausible_stamps` | tests/test_mesh_clock_poison.py:232 (Y-call), :237 (Y-call), :286 (Y-string: asserts `"purge_implausible_stamps" in msg`, not a call) | none programmatic — 3 hits: def `:3141`, `notifier.py:335` f-string remedy text (not a call), docstring operator runbook `:3160` | ESCALATE | Needs production caller: clock-poison remedy is manual-only, poisoned stamps persist in store/gossip otherwise — suggested call site: clock-skew alert handler (`notifier.py`) auto-remedy when refused exceeds threshold, or periodic fabric maintenance. |
| `spine_registry.purged_blocked_writes` | tests/test_spine_tombstone_enforcement.py:107 (Y), :126 (Y), :128 (Y) | none — 1 hit: def `:426` | ACCEPT-TEST-AS-WIRE | Test-only diagnostic (tests/test_spine_tombstone_enforcement.py:107); tombstone-refusal counter readout about callers. |
| `spine_registry.reset_counters` | tests/test_spine_brainstem_persistence.py:509 (Y), :526 (Y), :544 (Y) | none — 3 hits: def `:2184` + 2 comments | ACCEPT-TEST-AS-WIRE | Operator on-demand repair (tests/test_spine_brainstem_persistence.py:509 pins journal/floor record); no routine prod caller desired. |
| `spine_registry.revert_policy` | tests/test_spine_mesh.py:708 (Y) | none — 5 hits: def `:3053` + 4 comments | ESCALATE | Needs production caller: policy-journal undo never invoked — suggested call site: `worm_governance` emergency-rollback or operator remediation after faulty adaptation. |
| `spine_registry.route_weight_range` | tests/test_brainstem_playing_field.py:318 (Y), :331 (Y), :342 (Y) | none — 2 hits: def `:2623` + 1 comment | ACCEPT-TEST-AS-WIRE | Exercised contract (tests/test_brainstem_playing_field.py:318 pins declared-vs-reachable ceiling defect); diagnostic readout. |
| `spine_registry.spine_reset` | tests/test_colour_queens.py:49 (Y), :51 (Y), tests/test_federated_robustness.py:37 (Y) | none — 2 hits: def `:3096` + 1 comment; def docstring "for tests / explicit operator action" | ACCEPT-TEST-AS-WIRE | Fixture hygiene / explicit operator action (tests/test_colour_queens.py:49 fixture); no routine prod caller desired. |
| `tensorgene.boruta_relevance` | tests/test_boruta_relevance.py:27 (Y), :34 (Y), :40 (Y) | none — 1 hit: def `:99` | ESCALATE | Needs production caller: all-relevant gene gate nothing consumes, passenger genes survive — suggested call site: `DataPipelineWorm` feature selection / `learning_features` extraction or `RLTrainLoop` tuning prep. |

## Anomalies / notes

- Test refs: 0 stale. Every cited test line exists and names the function on that exact line (76/77 cited lines are direct calls; `test_mesh_clock_poison.py:286` is a string-content assertion `"purge_implausible_stamps" in msg`, still Y per "names the function" but weaker — its 2 sibling refs :232/:237 are direct calls).
- Worklist def-line drift: cited `Module:line` definition numbers are stale across the board (e.g. `spine_registry` cites drifted ~50–90 lines: `audit_state` cited 2218 vs live def 2272; `scheduling.get_run_history` cited 1105 vs live 1140 which is `get_status`; `meta_cognition` cited 857 vs live def 941; `learning_pipeline` cites off by ~14). Functions all still exist; only the probe's line numbers moved. Test refs themselves are fresh.
- `src/` holds `*.pre_gate_backup` duplicates (`NeuralPipeline.py.pre_gate_backup`, `learning.py.pre_gate_backup`) that duplicate defs for `replay_failed`, `fallback_accuracy_report`, `extract_field`, `filter_by_*`, `get_memory_stats`, `load_to_memory`, `process_batches`, `schedule_dynamic_refresh`, `search_memory`, `tune_and_train`, `tune_history` — excluded from live-caller counts.
- `route_recall` is the single worklist-stale claim: the worklist says test-only, but 2 live production callers exist (`_l1_memory.py:256` in `ep235`, `:368` in `ep389`). Accepted (already wired), not escalated.
- Unresolved: none — all 44 rows resolved to a decision with cited evidence. No source/test/worklist file edited.

---

## Reach audit 2026-10-10 (post-SOTA-wave)

Re-checked the decisions above against the code as it stands AFTER the 2026-10-10 SOTA
absorption wave. Method: content search for each symbol named above, then reading the
hits. No code file was edited. Anything not re-measured in this pass is marked
`UNVERIFIED-BY-EXECUTION` — this pass had no terminal.

**Counts: 44 decisions / 16 STILL UNWIRED (needs a production caller) / 28 SETTLED,
of which 2 proven actually reachable / 0 new CUTs proposed / 2 doc claims INVALIDATED.**

### 1. Decision = needs a production caller, still unwired (16)

Every ESCALATE row. Each row's own evidence cell measured "none" for `src/` callers and
nothing in the SOTA wave added one, so each is capability no live invocation reaches.
Suggested call sites are the row's own; status is `UNVERIFIED-BY-EXECUTION` unless noted.

| # | symbol | suggested caller (row's own) | caller now |
|---|---|---|---|
| 1 | `NeuralPipeline.replay_failed` | `neural_loop` recovery stage / operator DLQ replay | none |
| 2 | `db_monitor.DatabaseMonitorWorm._policy_advice` | the monitor's own alert loop | none (not even an internal self-call) |
| 3 | `db_monitor.DatabaseMonitorWorm.create_backup` | `ScheduledDbMonitorWorm` cycle | none |
| 4 | `error_recovery.ErrorRecoveryOrchestrator.execute_with_recovery` | MetaCluster/ClusterWORMZ dispatch or a `neural_loop` stage wrap | none |
| 5 | `error_recovery.ErrorRecoveryOrchestrator.reset_circuit` | health-monitor / operator reset path | none |
| 6 | `evolution.GeneticOptimizer.optimize_cma` | `optimize()` backend dispatch | none |
| 7 | `evolution.GeneticOptimizer.optimize_de` | same backend dispatch | none |
| 8 | `learning_pipeline.DataPipelineWorm.schedule_dynamic_refresh` | scheduler daemon / `ScheduledTrainingWorm` cycle | none |
| 9 | `learning_replay.PrioritizedReplayBuffer.add_from_memories` | `RLTrainLoop` training prep | none |
| 10 | `learning_rl.RLTrainLoop.tune_and_train` | scheduled training path | none |
| 11 | `meta_cognition.MetaCognitionWorm.compute_cross_worm_correlation` | the worm's periodic analysis / meta stage | none |
| 12 | `morph.load_genome` | `EvolutionEngine` checkpoint restore | none |
| 13 | `morph.save_genome` | `EvolutionEngine` checkpointing | none |
| 14 | `spine_registry.purge_implausible_stamps` | clock-skew alert auto-remedy in `notifier.py` | none (remedy text only) |
| 15 | `spine_registry.revert_policy` | `worm_governance` emergency rollback | none |
| 16 | `tensorgene.boruta_relevance` | `DataPipelineWorm` feature selection / `RLTrainLoop` prep | none |

### 2. CUT decisions

This document proposes none (it is decisions-only, no code cut). The deletion half of
the same class was executed separately — see the reach audit appended to
`THEATER_REMOVAL_TASKS_2026-10-10.md`, where **3 of its 6 tracked deletions are back in
the tree**. Read that section before trusting either document's "removed" claim.

### 3. SETTLED — do not re-check these (28 + 1)

- The 27 remaining ACCEPT-TEST-AS-WIRE rows are test-exercised contracts and diagnostics
  that need no production caller by design. The decision stands and no work is
  outstanding; re-opening them as a backlog is the measurement-artifact error this
  project has already made twice.
- `engram.RecallRouterWorm.route_recall` — the one ACCEPT row whose "only caller" claim
  was stale. PROVEN reachable, not merely accepted: `technique_wiring/_l1_memory.py:256`
  (`ep235`) and `:368` (`ep389`).
- Bonus, same class, from the sibling registry: ACTION_REGISTRY D-2's write-only finding
  for `engram_read_pressure` is now CLOSED, and by a reader, not a deletion —
  `src/CORE/technique_runtime.py:483 _read_pressure_summary` consumes the payload and
  `src/CORE/WORMS/expansion/engram.py:517` calls `_record_read_stats(pressure)`. The
  premise-and-fix is recorded at `technique_runtime.py:486-491`.

### 4. Invalidated evidence (2)

1. **The worklist's def-line drift note is confirmed again, and it is not cosmetic.**
   Every cited definition line in this document should be treated as stale before reuse.
2. **`eliminate_common_subgraphs` is still published as a CONFIRMED DEFECT by an adapter,
   and the symbol is in fact called in production.** `src/CORE/dispatch_plan.py:210`
   defines it, `src/CORE/WORMS/METACLUSTER.py:447` calls it during live plan construction,
   and `technique_wiring/_l5_dispatch.py:123` exercises it — yet
   `technique_wiring/_l5_dispatch.py:14` and its `:538-541` defect-data block still assert
   the confirmed defect. Any reader acting on that data is acting on a stale signal;
   whoever owns `_l5_dispatch.py` should re-verify its defect claim against the reducer's
   body before it gates anything.
