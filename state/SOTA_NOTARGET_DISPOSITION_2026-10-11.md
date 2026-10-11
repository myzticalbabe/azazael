# SOTA NO-TARGET DISPOSITION — 2026-10-11

Follows the census precision repair (commit `23f5fa5f`, self-test 7/7 green).
Question: what to do with the 23 NO-TARGET rows + EP350 + the commit_gate ×6.
Method: falsify-first — every verdict below was checked against the tree, not
the map. No theater callers invented.

## Instrument state after this session

`python tools/adoption_census.py` (map at
`C:/Azazael/state/sota_batches/batch06/technique_codebase_map.json`,
backup `C:/Temp/technique_codebase_map.bak-20261011b.json`):
141 rows — ADOPTED 106, in_production 112, HOST-COMPOSED 8,
EXERCISE-ONLY 10, NO-TARGET 17, built 124.

## Retargets (map defect class, cf. EP351): 6

Adapter named a real host:symbol; map held prose/empty. Verdict follows evidence.

| EP | old target | new target | evidence | verdict |
|---|---|---|---|---|
| EP253 | `''` | `CORE/dispatch_plan.py :: assign_roles` | adapter `_ep253` exercises `assign_roles` as participation prior; production caller `src/CORE/WORMS/METACLUSTER.py:420` read on disk | ADOPTED |
| EP259 | `''` | `CORE/WORMS/expansion/policy_optimization.py :: depo_filter` | adapter `_ep259` names `depo_filter` (ESPO tripwire, `policy_optimization.py:224` exists); no production caller — only `_b01_05.py:148,150` exercise | EXERCISE-ONLY |
| EP280 | `` `PSYCHE/distill.py` `` (bare path) | `PSYCHE/distill.py :: onpolicy_refine` | adapter registration `PSYCHE.distill:onpolicy_refine` (`_l6_evolve.py:502`); only importer is `_l6_evolve.py:462` exercise | EXERCISE-ONLY |
| EP336 | `''` | `CORE/local_memory.py :: LocalMemoryStore.retype_ladder` | adapter `ep336` calls `store.retype_ladder()` (`_l1_memory.py:343`); method exists (`local_memory.py:2282`); no production caller | EXERCISE-ONLY |
| EP343 | prose (`reflexion.py` nearest-artefact note) | `CORE/WORMS/expansion/reflexion.py :: record_reflection` | def exists (`reflexion.py:130`); production caller `src/CORE/technique_runtime.py:319` — same caller as EP113 (already ADOPTED, consistent) | ADOPTED |
| EP345 | prose (`dispatch_plan.py :: (LoongReflect …, ~L221)`) | `CORE/dispatch_plan.py :: record_backtrack, reuse_prefix` | both exist (`dispatch_plan.py:417,450`); adapter calls both (`_b01_05.py:103,106`); zero production callers; module itself notes caller-side enforcement deferred (no live plan object) | EXERCISE-ONLY |

## No-host normalizations (verdict stays NO-TARGET, provenance now explicit): 14

Target set to the adapter's `where` verbatim. Missing precondition in parentheses.

- EP11 `no-host: training partitioner` (datacenter-scale ZeRO; no trainer here)
- EP14 `no-host: pretraining loop` (no pretraining loop in tree)
- EP38 `no-host: 540B dense model` (no 540B model on this box)
- EP39 `no-host: vision<->language bridge` (no VLM bridge)
- EP52 `no-host: multimodal pretraining` (a report, not a hostable technique)
- EP68 `no-host: owned inference engine` (vLLM named only in AOA comments, servemesh string list, CODEX venv manifest — no PagedAttention host)
- EP226 `no-host: re-entrant model blocks` (adapter `_l0_model.py:322` + rule text)
- EP245 `no-host: theory bound` (zero `wasserstein|lipschitz|optimal_transport` hits in `src/`)
- EP141 `no-host: research-lifecycle eval harness`
- EP153 `no-host: soft-verified rollout labelling`
- EP237 `no-host: act-time map stage missing`
- EP278 `no-host: error-path injection harness` (`CORE/redteam.py` exists but is a reward-hack critic, not an injection harness)
- EP300 `no-host: no joint-plan tensor`
- EP352 `no-host: hidden-state failure predictor` (adapter: needs model internals)

## Withheld retargets — adapter name does not match map name (human ruling): 3

- EP110 map "OneFlow Single-Agent Baseline" vs adapter "Simulate-vs-spawn costing"→`allocation:MCTSPlanner`. Left `''`.
- EP262 map "SCALE Self-Improving Web Agent" vs adapter "Selector/Predictor/Judger self-probing"→`neural_loop:STAGES` (`STAGES` exists at `neural_loop.py:87`). Left `''`.
- EP308 map "Giving AI Agents Mathematical Muscle Memory" vs adapter "SoftSkill virtual tokens"→no-host. Left `''`. (The `probe` reference from H-5 was resolved by removal; no math-memory host found.)

## Map/adapter conflicts — same shape as EP183, do not rule silently: 2

- EP214 "ARISE Data-Flow Repair Graphs": map PARTIAL→`dispatch_plan :: plan_dag / eliminate_common_subgraphs`, census ADOPTED via `METACLUSTER.py:411,455` (real calls, read on disk). Adapter `_ep214` is `_no_host` ("no def-use/data-flow analysis exists"). Both true at different resolutions; full technique absent, DAG/CSE present.
- EP227 "FlowAgent Continuous Tool Flow": map PARTIAL→`plan_dag`, ADOPTED via `:411`. Adapter `_no_host` ("needs trained flow model"). Same split.

## EP350 (reward-gated distillation) — ACCEPT-GAP with complete evidence

`gate_distillation` (`rubric_evolution.py:89`) has zero production callers.
Candidate consumers checked and excluded: `PSYCHE/distill.py` is a toy
person-simulator lab (BC/DAgger/dDPO over synthetic traits), imported only by
`_l6_evolve.py:462` exercise; GRPO trains real policies but nothing gates a
distillation decision on gain; `record_rubric_cycle` cites the ledger without
gating. The replay protocol (`ingest_replay_trajectory`,
`replay_offline_step`) is unfed. Revisit when a real policy-distillation loop
exists (feeds H-3 trajectory→training edge work).

## commit_gate ×6 — shared host by harvest design, not a defect

EP162/255/275/347/363/387 all target `skill_library.py :: commit_gate`
(a real skill-admission validator, `:95`). Five score EXERCISE-ONLY because
the only in-host mention is the module-docstring Usage example (`:29`,
correctly excluded as prose — the NEGATIVE-A case) and all other callers are
`_l2_skills.py` exercise. EP387 is HOST-COMPOSED via its second segment
(`data_retention :: distill_aged_memories`). Six harvest episodes, one
mechanism: no action unless the symbol is ever split.

## Remaining worklist (untouched this session)

- NO-TARGET 17: EP11,14,38,39,52,68,110,141,153,226,237,245,262,278,300,308,352
  (14 normalized no-host + 3 withheld above).
- EXERCISE-ONLY 10: EP162,255,275,347,363 (commit_gate), EP259,280,336,345
  (retargeted, caller-less), EP350 (gap above).
- HOST-COMPOSED 8: EP144,156,215,221,247,298,337,387 — promotion candidates
  iff a cross-module caller appears; not pursued (no theater).
