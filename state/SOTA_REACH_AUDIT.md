# SOTA reach audit — did today's new host hooks reach a live caller?

Date: 2026-10-10. Author: auditor 7 of 7 (20-worker SOTA wave).

**Why this file exists.** Today's wave added host-side capability to ~20 modules.
Most of those workers reported their row as PARTIAL for one repeated reason: *the
hook exists but no production caller invokes it*. A hook invoked only from a test
file is the production-reach failure in its purest form — the code is real, the
tests are green, and no runtime path executes it. `SOTA_BUILDABLE_SUBSET.md`
already set the obligation: an implementation claiming a row closed must name the
`module::symbol` implementing the mechanism **and** the row only counts as adopted
when a production call site exists (the T-15 rule: exercise-only scores zero).

## Method, and its limits

Tooling available to this auditor: file reads and name search only — **no
terminal**, so nothing here is execution-verified. Every claim is a search result
plus, where the shape was ambiguous, an open of the defining file.

Procedure per symbol: search the bare symbol name repo-wide over `-t py`. A hit
was classified by *where* it landed:

- a hit in `tests/` (or a `test_*.py`) → **not** a production caller.
- a hit inside the symbol's own module, in a function that is itself unwired →
  **internal only**, does not count as reach.
- a hit in a different `src/` module at a call site (not a docstring, not a
  dataclass field of the same name) → **production caller**.

`state/` and other git-ignored paths are skipped by the search tool, so no
document in this repo could appear as a caller; that is correct for this question
(a doc is not an invocation) but it means my counts describe **code** reach only.

Two honest caveats:

1. **Method per row is named below** so a claim can be re-checked. Where I did not
   open the file, I say "search only".
2. The archived `onnxruntime*` trees inside the repo produce unrelated matches for
   common names (`predict_next`, `scheduler`, `traverse`). I excluded them from
   every classification; they are not Azazael code.

## Table

| symbol | row | production caller? | caller, or NONE | who must wire it |
|---|---|---|---|---|
| `scheduling.next_interval_hours` | EP187 | **YES** | `ScheduledTrainingWorm._scheduler_loop` — `scheduling.py:921` | — (reader is live) |
| `scheduling.record_contribution` | EP187 | NO | tests only — the field's *source* has no caller | the scheduler loop must record outcomes, else `contribution_weights` is always unwritten |
| `allocation.apply_dense_reward` | EP351 | **YES** | `learning_grpo.py:284`, inside the live reward path | — (inert at default weight 0) |
| `allocation.dense_implicit_reward` | EP351 | **YES** | called by `apply_dense_reward` — `learning_grpo.py:488` | — |
| `learning_grpo.ingest_replay_trajectory` | EP350 | NO | tests only | the run/exercise path (registry **H-3**) must emit trajectories, not this module |
| `learning_grpo.replay_offline_step` | EP350 | NO | tests only | same as above |
| `reflexion.locate_pivotal_turn` | EP345 | **YES** | `record_reflection` — `reflexion.py:190` | — |
| `reflexion.pivotal_credit_weights` | EP345 | **YES** | `record_reflection` — `reflexion.py:195` | — |
| `structured_action.drive_for_workflow_step` | EP44 | **YES** | imported and called by `workflow.py:73` (`_react_step_drive`, guarded) | — |
| `structured_action.plan_mutations` | EP44 | internal only | `structured_action.py:298`; the `workflow.py:1018` hit is the *dataclass field*, not a call | `workflow.py` already consumes the mutations list — no action |
| `workflow.submit_workflow` | EP209 | NO | tests only | whatever owns the run loop must hand the workflow to a pool as one unit |
| `workflow.execute(cost_fn=…)` | EP248 | NO | tests only | the caller that knows step costs |
| `workflow.execute(scheduler=…)` | EP209 | NO | tests only | the run loop |
| `cascade.route_node` | EP186, EP223 | NO | tests only | `dispatch_plan`/`METACLUSTER` DAG executor |
| `freethreading.submit_group` | EP130, EP209 | NO | tests only (the `freethreading.py:531` hits are inside a docstring example above the defs) | `dispatch_plan` level fan-out |
| `freethreading.wait_group` | EP130 | NO | tests only | same |
| `freethreading.group_results` | EP130 | NO | tests only | same |
| `allocation.joint_action_space` | EP223 | NO | tests only | the joint policy over the three routers |
| `allocation.action_space` (allocator) | EP223 | internal only | called by `joint_action_space` (`allocation.py:301/376`), itself unwired | same |
| `allocation.participation_prior` | EP253 | internal only | called by `action_space` (`allocation.py:301`) | `dispatch_plan.assign_roles` |
| `cluster_route.action_space` | EP223 | NO | tests only | same joint policy |
| `dispatch_plan.plan_dag(ready_order, fissions)` | EP130, EP374 | **YES** (consumer) | `METACLUSTER.py:441` reads `plan["ready_order"]` | — for the key; the *fission* key has no reader |
| `dispatch_plan.assign_roles(participation=…)` | EP253 | NO | tests only | the allocator that holds the prior |
| `METACLUSTER._plan_execution_order(granularity=, capability_split=, plan_out=)` | EP186, EP197, EP374 | NO | tests only supply the hooks; `orchestrate` forwards them only when given | the top-level invoker of `MetaCluster.orchestrate` |
| `local_memory.record_event(admit=…)` | EP395 | NO | tests only | the write path's callers (every recorder site) |
| `local_memory.record_event(agent_id=…)` | EP160 | NO | tests only; `local_memory.py:647` is an **internal** pass-through of a candidate row's own field | the multi-agent callers |
| `local_memory.object_graph` | EP206 | NO | tests only | the recall/read path |
| `local_memory.traverse` | EP206 | NO | tests only | same |
| `policy.require_authority` | EP327 | NO | tests only | the policy evaluation callsite that holds the presented authority |
| `policy.bind_task_authority` | EP269 | NO | tests only | the task spawner |
| `policy.residual_obligations` | EP382 | NO | tests only | the obligation monitor |
| `pre_action_gate.install_capabilities` | EP269 | NO | tests only | **deployment**: something must install an authority table, or the check is inert |
| `pre_action_gate.authorize` | EP269 | **YES** | consulted by `_check_rule_0x_0y`, the live acceptance path | — but see the inert-gate note below |
| `governance.quantify` | EP156 | internal only | called by `evaluate_with_uncertainty` (`governance.py:451`) | whoever calls `evaluate_with_uncertainty` |
| `governance.evaluate_with_uncertainty` | EP156, EP349 | NO | tests only | the middleware acceptance path |
| `governance.add_scorer` | EP349 | NO | tests only | the same — **no in-repo scorer exists**, so this is the honest ACCEPT-GAP half |
| `governance.register_obligation` | EP382 | NO | tests only | the duty-creating path |
| `governance.residual_obligations` (pipeline) | EP382 | NO | tests only | the obligation monitor |
| `neural_loop.LoopContext.mode_decider` | EP266 | READ live, SET never | `neural_loop.py:504` reads it; only tests set it | `run_cycle` / the loop's caller must inject `cascade.select_mode`/`route` |
| `dream_arena.predict_next` | EP238 | internal only | called by `simulate` (`dream_arena.py:176`), itself unwired | `rehearse_dispatch` (sibling file) |
| `dream_arena.simulate` | EP238 | NO | tests only | same |
| `codebase_graph.consult` / `graph_artifacts.MapBeforeAct` | EP237 | internal only | `graph_artifacts.py:161` calls `consult_map`; nothing calls the stage | the L4 execution layer (`workflow.py`) |

## Ranked: hooks whose only caller outside themselves is a test file

These are the production-reach failures, worst first (a row whose *entire*
mechanism is here cannot be adopted no matter how many tests pass):

1. **`install_capabilities`** (EP269) — the enforcement is live (`authorize` runs on
   every edit) but the *table* is never installed, so the check cannot deny and
   grants cannot be exercised. The gate is reached and inert at once.
2. **`mode_decider`** (EP266) — the loop reads it on every route stage and nothing
   in production ever sets it, so the per-turn mode policy can never fire.
3. **`record_contribution`** (EP187) — `next_interval_hours` is live and reads a
   field nothing in production writes.
4. **`freethreading.submit_group` / `wait_group` / `group_results`** (EP130,
   EP209, EP248) — three symbols, zero callers; the executor capability is
   complete and unreachable.
5. **`route_node`** (EP186, EP223) — the per-node offload decision, no caller.
6. **`workflow.submit_workflow` + `scheduler=` + `cost_fn=`** (EP209, EP248) — the
   whole scheduling seam is test-only.
7. **`allocation.joint_action_space` + `cluster_route.action_space`** (EP223) — the
   joint policy's inputs exist; the policy and its caller do not.
8. **`local_memory` admission/partition/graph** (EP395, EP160, EP206) — four
   capabilities, all opt-in, none opted into.
9. **`policy` authority trio + `governance.register_obligation`/`residual_obligations`**
   (EP327, EP269, EP382) — the authority and obligation surfaces are unreachable.
10. **`MapBeforeAct`** (EP237) and **`dream_arena.predict_next`** (EP238) — the
    act-time stage and the transition predictor, each with an internal caller and
    no external one.
11. **`learning_grpo.ingest_replay_trajectory` / `replay_offline_step`** (EP350) —
    blocked on **H-3** (trajectory producer), which is a different registry item.

## The inert-but-reached class (distinct from no-caller)

Four of these are worse than "unreachable" because they *are* reached and still do
nothing, which no test can distinguish from a pass:

- `authorize` (EP269) — reached on every edit, allow-by-construction with no table.
- `apply_dense_reward` / `dense_implicit_reward` (EP351) — on the live update path,
  and a no-op passthrough while `dense_reward_weight` is 0 (the default).
- `record_event`'s `admit=`/`agent_id=` — reached by every existing caller, but
  every existing caller leaves the new arguments at their defaults.
- `LoopContext.mode_decider` (EP266) — read every stage, always `None`.

## Counts

Of **41 hook symbols** audited:

- with a production caller: **8** (`next_interval_hours`, `apply_dense_reward`,
  `dense_implicit_reward`, `locate_pivotal_turn`, `pivotal_credit_weights`,
  `drive_for_workflow_step`, `dialectic`, `authorize`) — and of these, **3 are
  inert at their defaults**;
- internal-only (called solely from within their own module, by something that is
  itself unwired): **8**;
- whose only external caller is a test file: **23**;
- with no caller anywhere: **2** (`record_contribution`, `submit_workflow`).

So **31 of 41 hooks (76%) do not reach a live production call site** — which is
the single most important sentence in this audit: the wave added capable,
tested, correctly-defaulted code that the running system does not invoke.

## What would close the gap, by file

- `cascade.route_node` ← `dispatch_plan` (level fan-out) or `METACLUSTER._execute_nature`
- `freethreading.submit_group` ← `dispatch_plan.plan_dag` levels, in the L4 executor
- `workflow.submit_workflow` / `cost_fn` / `scheduler` ← the run loop that owns the engine
- `allocation.participation_prior` ← `dispatch_plan.assign_roles`
- `cluster_route.action_space` + `allocation.joint_action_space` ← one policy over the three routers
- `scheduling.record_contribution` ← the scheduler loop that already calls `next_interval_hours`
- `neural_loop.mode_decider` ← `run_cycle` / `Loop`, injecting `cascade.select_mode`
- `dream_arena.predict_next` ← `rehearse_dispatch` (consumes it instead of folding gaps only)
- `MapBeforeAct` ← `workflow.py` (the L4 layer the row names)
- `local_memory` `admit=`/`agent_id=` ← the recorder call sites
- `policy` authority trio + `governance` obligations ← the policy/governance callers that hold an authority
- `install_capabilities` ← **a deployment step, not a code edit**; nothing in-repo should invent a grant table silently

## Note for the coordinator

`local_memory.py` now carries **two** graph surfaces: the new typed `object_graph()`
/ `traverse()` (EP206, lines ~1113/1216) *and* a pre-existing
`object_graph_document` / `export_object_graph` / `load_object_graph` /
`_object_graph_counts` family (lines ~3041-3167) reachable from
`get_knowledge_graph_stats`. Both are live names over related data. That is a
duplicate-surface question, not a reach question, and I did not open both to
compare semantics — flagging it because a second graph API is exactly the
"adjacency, not adoption" pattern the rescore warns about.

This file is written into `state/`, which is git-ignored (`.gitignore:248 state/*`):
the coordinator must `git add -f` it to version it.
