# SOTA row rescore — reassigning the 48 rows that pointed at the new layer

Date: 2026-10-09. Companion to `SOTA_OUTLIER_DIAGNOSIS.md`.

Measured triage of all 141 map rows (`state/sota_batches/batch06/technique_codebase_map.json`):

| where the row's `target` points | rows |
|---|---|
| a NEW module added by the programme (misplaced — must be reassigned) | **48** |
| a pre-existing host module | 93 |
| no target named (mostly theory-only / accept-gap) | 13 |

The 48 misplaced rows were re-scored against the code by four workers, each opening
the files it cited. Their outputs are reproduced verbatim below; each row carries the
real host (or ACCEPT-GAP), a size estimate for the HOST edit, and the evidence read.
Nothing here is implemented yet — this is the specification the host edits need.


---

## state/rescore_partA.md

# Rescore part A — the 17 rows that point at `skill_library.py`

Scope: every row in `state/sota_batches/batch06/technique_codebase_map.json` whose
`target` names `skill_library.py`. I found **17** such rows (EP34, EP135, EP150,
EP155, EP162, EP180, EP250, EP255, EP265, EP270, EP275, EP302, EP347, EP354,
EP363, EP364, EP387) — matching the coordinator's count.

**Counts: 17 reassigned to an existing host, 0 fully ACCEPT-GAP. Sizes: S=2,
M=5, L=10.**

The decisive finding behind most rows: `src/CORE/skill_library.py` is a **Python**
module, but the project's actual L2 skill layer is a **flat markdown corpus** —
`skills/*.md` (the SOURCE corpus, RULE 0R; 1,243 files) mirrored to
`.agents/skills/<n>/SKILL.md` (the LOAD PATH, what `skill()` reads) — governed by
two existing tools (`tools/canon_drift_check.py`, `src/SCRIPTS/sync_skills.py`)
and indexed by `SKILLS_CATALOG.md`. The blueprint's own L2 line is "replaces flat
files". So an L2 delta belongs on that corpus and its tooling, not in a new
module — which is why 12 of these 17 rows point at a place the techniques were
never going to be adopted from.

Citation strength is marked: **(read)** = I opened it; **(g/s)** = confirmed by
glob or search; **(map)** = the map names the symbol, I did not open it.

| EP | technique | current target (new layer) | real host | size | evidence |
|---|---|---|---|---|---|
| EP34 | Chain-of-Thought Prompting | `CORE/skill_library.py :: protocol_artifact` | `azazael/skills/*.md` (SKILL.md body = the prompt-level scaffold) + `tools/canon_drift_check.py :: classify` (keeps both live copies identical) | M | **(read)** canon_drift_check documents the three copies and that only `skills/`+`.agents/skills/` are live; **(g/s)** 1,243 `skills/*.md`. The runtime "render a plan into a prompt" half has no host — the client reads SKILL.md directly. |
| EP135 | SoK agentic skills | `CORE/skill_library.py :: protocol_artifact, commit_gate, family_index` | corpus frontmatter in `azazael/skills/*.md` + `azazael/SKILLS_CATALOG.md` + `.agents/skills/azazael-catalog-maintenance/SKILL.md` (the documented 7-stage lifecycle) | M | **(g/s)** catalog-maintenance and catalog-reconciliation skills exist and describe format/numbering/maintenance; dozens of SKILL.md cite `SKILLS_CATALOG.md` as the inventory. |
| EP150 | Agentic Reasoning Survey | `azazael/src/CORE/skill_library.py :: family_index` | `tools/run_technique_exercises.py` (the layer-by-layer suite; it is the scaffold the row says is missing) | S | Review row, no mechanism to implement. The coordinator's suite runs one exercise per layer slice and prints a per-layer verdict — registering the L2 row there closes it. |
| EP155 | Agentic Proposing skill synthesis | `skill_library.py :: protocol_artifact`; `PSYCHE/distill.py :: person_utilities` | `azazael/skills/*.md` as the acquisition target + `src/SCRIPTS/sync_skills.py :: sync_all` (corpus writer) + `src/PSYCHE/distill.py` (distillation) | L | **(g/s)** `sync_skills.py :: sync_all` exists at lines 138/229 and canon_drift_check names it as the propagator; **(g/s)** `src/PSYCHE/distill.py` exists. MGPO is a training objective — large. |
| EP162 | Agent Skills Survey + Governance | `CORE/skill_library.py :: commit_gate` | `tools/canon_drift_check.py` — the only existing gate over the corpus — extended with the four security gates over the same object | L | **(read)** canon_drift_check gates drift only (no static analysis, no sandboxing, no permission check) over 1,243 skills. The corpus is the real object; the gate belongs beside its sibling gate. |
| EP180 | Autogenesis AGP/AGS | `CORE/skill_library.py :: commit_gate` + `meta_evolution.py :: Lifecycle` | `src/CORE/meta_evolution.py :: Lifecycle` (generalise propose/assess/commit from one resource type to tools/prompts/envs/memory) | L | **(g/s)** file exists; **(map)** Lifecycle/LEGAL_TRANSITIONS/improvement_proved cited by the map for that file. |
| EP250 | Compiled subterranean agents | `CORE/skill_library.py :: protocol_artifact` | `src/CORE/escalation_sft.py` (the LoRA-based SFT path that folds procedures into weights) fed from the corpus | L | **(g/s)** `src/CORE/escalation_sft.py` exists; the map names it as the LoRA SFT path for exactly this compile step (EP308's gap). |
| EP255 | MUSE-Autoskill lifecycle | `CORE/skill_library.py :: commit_gate` | `src/CORE/local_memory.py :: LocalMemoryStore` (per-skill accumulated experience) + the corpus artifact | M | **(map)** local_memory carries the event store the experience would accumulate in; **(read)** skill_library has no per-skill store at all. |
| EP265 | SkillSmith skill/tool co-evolution | `CORE/skill_library.py :: family_index` | `azazael/SKILLS_CATALOG.md` (the existing loading-order/priority surface) + the corpus gate for version-scoped nogoods | M | **(g/s)** catalog hits show load ORDER is maintained there ("Added 3 skills to loading order"). Budget allocation between competing skills is a catalog concern, not a Python one. |
| EP270 | Reasoning Primitive Induction | `CORE/skill_library.py :: protocol_artifact` | trace source `src/CORE/local_memory.py` → mined artifacts into `azazael/skills/*.md` | L | **(read)** skill_library only validates artifacts; nothing mines traces. A miner is a new function over the existing trace store. |
| EP275 | Socratic-SWE trace-derived skills | `CORE/skill_library.py :: commit_gate` | same as EP270, plus `tools/run_technique_exercises.py` as the execution-validated task filter | L | **(read)** the admission gate exists in skill_library; the ingest/induce/repair-generate half has no host anywhere — real work. |
| EP302 | Transferable interaction patterns | `CORE/skill_library.py :: family_index` | corpus frontmatter field in `azazael/skills/*.md` (layout sketch) + `SKILLS_CATALOG.md` index | M | **(read)** skill_library's family_index groups by a caller-supplied family string only; there is no structural key, and the corpus is where the field would persist. |
| EP347 | Auto AGI Compiler | `CORE/skill_library.py :: commit_gate` | `src/CORE/meta_evolution.py :: Lifecycle / improvement_proved` for the compile→verify→commit half | L | **(g/s)** file exists; **(map)** cites those symbols. The "secretly deterministic live span + calibrated deopt" half needs an execution engine the repo does not own — that half is a genuine unhostable core inside an otherwise hosted row. |
| EP354 | EvoSOP Procedure Synthesis | `CORE/skill_library.py :: protocol_artifact` | **the operators already exist** — `tools/canon_drift_check.py :: _reconcile` is the corpus merge; `skill_library.py :: merge_sops` / `prune_sops` are the implemented-but-uncalled pair | S | **(read)** canon_drift_check `_reconcile` performs a content-preserving, reversible merge of the two live corpus layers and PRINTS the choice per file; **(read)** skill_library docstring states merge_sops/prune_sops were added precisely because "the set was missing its two maintenance operators". The only work left is a caller. |
| EP363 | LOGOS living logic | `CORE/skill_library.py :: commit_gate` | `src/CORE/meta_evolution.py :: Lifecycle` (extend untrusted-until-evidenced promotion beyond skills) + catalog versioning | L | **(g/s)** file exists; **(read)** skill_library's commit gate is fail-closed for skills only; nothing versions prompts/memory/roles/workflows. |
| EP364 | Capability trees | `skill_library.py :: family_index`; `worm_registry.py` (flat) | `.agents/skills/` (the FLAT load path this row is about) + `src/CORE/worm_registry.py` (the flat registry) | L | The row's own words are "the flat-SKILL.md scaling limit"; **(g/s)** 1,243 flat skills + a flat worm registry are the objects. Hierarchy means changing the loader/catalog, not adding a Python tree beside them. |
| EP387 | Knowledge-centric self-improvement | `skill_library.py :: commit_gate`; `data_retention.py :: distill_aged_memories` | `src/CORE/data_retention.py :: distill_aged_memories` (the existing knowledge distillation) + `src/CORE/local_memory.py` as the persistent object | L | **(map)** both symbols cited for that file; **(read)** skill_library's gate is per-artifact admission, not cross-task distillation. |

## Boundary notes (rows that look like mine but are not)

- **EP308** (SoftSkill / mathematical muscle memory) references
  `skill_library.py :: protocol_artifact` inside its *gap text*, but its `target`
  is `PSYCHE/distill.py :: test_theta_frozen, theta` + `CORE/escalation_sft.py`.
  It belongs to the distillation row set, not to this slice — flagging so it is
  not double-counted. Its gap confirms `escalation_sft.py` is the LoRA SFT path
  I reassigned EP250 onto.
- **EP364**'s target also names `worm_registry.py`, which is outside the L2 slice;
  I recorded the corpus half as the primary host.
- Several of these rows (EP250, EP347, EP270, EP275, EP363) need a trained model
  or an execution engine the repo deliberately does not own; I marked the whole
  row L rather than splitting it, because the hostable half cannot be delivered
  without deciding whether the unhostable half is accepted.

## What this changes

Twelve of the 17 rows are L2 corpus/tooling work (`.agents/skills`, `skills/`,
`SKILLS_CATALOG.md`, the two corpus tools), not new Python. One row (**EP354**)
is already implemented on both sides — the merge operator exists in the drift
tool and the SOP merge/prune pair exists in the uncalled module — and needs only
a caller. That is the concrete shape of "remediate by adoption, not by adjacency".

---

## state/rescore_partB.md

# Re-score part B — rows whose `target` names `dispatch_plan.py`

Date: 2026-10-09. Scope: every row in `state/sota_batches/batch06/technique_codebase_map.json`
whose `target` string names `dispatch_plan.py`.

**Count correction: there are 13 such rows, not 12.** Reason for the discrepancy: the
brief's filter was applied to the *six* new-layer modules, and two of these rows name
`dispatch_plan.py` only as one of several targets (`EP209`, `EP187`) or inside a longer
cell (`EP345` cites a line range, `EP253` cites "role-pool dispatch" rather than a
symbol). One further row — **EP300** ("Tensors prevent multi-agent LLM collisions") —
*mentions* `CORE/dispatch_plan.py` in its `gap` prose ("Conflict handling in
`CORE/dispatch_plan.py` is topological only") but its `target` is `(none — searched)`,
so it is **not** in this slice; it is a L5 no-host row for whoever takes the ABSENT set.

## Preamble

Of the 13 rows, **11 are reassigned to an existing host** and **2 are marked
ACCEPT-GAP** (`EP214`, `EP227`) because the mechanism they name has no counterpart in
this tree — I searched for it and found nothing to point at. `EP187` is a split row: its
allocation half has a host and its logits-cache half is an ACCEPT-GAP, so it is counted
with the 11 and the gap is stated in its evidence cell.

By size of the **host edit** required (not the paper's ambition): **S = 0, M = 6, L = 7**.
No row is an S: every one of them asks the host to do something it currently cannot do
(learn a policy, model cost, or restructure what the schedulable unit is), and none is a
one-line change. Nothing here was implemented — this slice is reassignment only.

Ground rule I held to: a `path::symbol` appears below only if I opened the file in this
slice or confirmed the symbol with a search whose output I read. Where that provenance is
weaker I say so in the evidence cell rather than quietly citing it.

| EP | technique | current target (new layer) | real host (path::symbol, or ACCEPT-GAP) | size | evidence (what I read) |
|---|---|---|---|---|---|
| EP130 | GAP graph-based planning | `CORE/dispatch_plan.py :: plan_dag, eliminate_common_subgraphs` | `CORE/WORMS/expansion/learning_grpo.py :: GRPOTrainer` (the learner that emits DAGs) + `CORE/freethreading.py :: WorkStealingPool` (fan-out executor for independent branches) | M | `dispatch_plan.plan_dag` returns `levels` (per-node depth) which is exactly the branch grouping a fan-out executor consumes; `GRPOTrainer` read at head (`generate_group`, group-normalized advantages, DeepSeek-R1 lineage) — it trains a policy but knows nothing about DAG structure; `WorkStealingPool` is in the canonical import list at the head of `freethreading.py`. No component currently emits plans, so the learner half is new work rather than a rewrite. |
| EP186 | SGDe Harness Compilation | `CORE/dispatch_plan.py :: plan_dag, eliminate_common_subgraphs` | `CORE/cascade.py :: CascadeRouter.route` (per-node Python-vs-LLM offloading) + `CORE/WORMS/expansion/consensus.py :: QuorumVoterWorm` (structural-consensus voting) + `CORE/WORMS/METACLUSTER.py :: _plan_execution_order` (plan construction) | L | `cascade.py` read in full: `route(task, triage_fn, big_fn)` already makes a cheap-vs-expensive call per task with a 0.65 threshold and an escalation ledger — the offload decision is a real existing primitive, just never attached to DAG nodes. `QuorumVoterWorm` (`consensus.py:44`) and `SplitBrainResolverWorm` (`:256`) confirmed by search. `METACLUSTER._plan_execution_order` confirmed at line 304. |
| EP187 | Hive logits cache + agent-aware scheduling | `CORE/dispatch_plan.py :: eliminate_common_subgraphs + CORE/WORMS/expansion/scheduling.py :: ScheduledTrainingWorm` | `CORE/WORMS/expansion/scheduling.py :: ScheduleConfig.interval_hours` / `ScheduledTrainingWorm` (contribution-weighted allocation) + `CORE/WORMS/expansion/allocation.py :: ThompsonAllocator` for the weighting — **logits-cache half = ACCEPT-GAP** | M | `scheduling.py` head read: the scheduler is interval-based (`interval_hours: float = 24.0`, `max_duration_minutes`, `n_episodes`) with no value or contribution term — the row's diagnosis is confirmed in the source. `allocation.py` head read: `ThompsonAllocator`, `PROTEUS_ARMS`, `reward_for_outcome` give exactly the contribution-weighted machinery the schedule lacks. Logits-level reuse has no host: Azazael does not own an inference engine (`inference_pool.py` calls Ollama over HTTP, read at head: `_ollama_infer` posts to `/api/generate`), so the API never exposes logits. |
| EP197 | Teaching AI Agents to Plan Like Humans | `CORE/dispatch_plan.py :: plan_dag` | `CORE/WORMS/METACLUSTER.py :: _plan_execution_order` (granularity policy at plan-build time) + `CORE/WORMS/expansion/learning_grpo.py :: GRPOTrainer` (imitation learner) | M | `plan_dag` read in full: depth comes from declared `deps` only (`levels[child] = max(levels[child], levels[node] + 1)`) and nothing consults task complexity — the row's claim is confirmed in code. `_plan_execution_order` (L304) is where the per-nature task lists are actually built, so a complexity policy belongs there, not in the new module. |
| EP209 | SAGA workflow-atomic scheduling | `CORE/freethreading.py :: WorkStealingPool ; CORE/dispatch_plan.py :: Agora pool/affinity (L153-165)` | `CORE/freethreading.py :: WorkStealingPool` (the scheduler itself) + `CORE/workflow.py :: DependencyGraph` / `WorkflowEngine` (the workflow graph as the schedulable unit) | L | `freethreading.py` head read (canonical import list: `WorkStealingQueue`, `WorkStealingPool`, `FreeThreadPool`, `CancellationToken`); `workflow.py` head read (`__all__` includes `DependencyGraph`, `WorkflowEngine`, `WorkflowStep`, `ConditionalRouter`, and the module imports `ThreadPoolExecutor, as_completed`) — so a workflow is already a first-class object with a dependency resolver, which is precisely the unit SAGA says the scheduler should schedule instead of a bare task. Note the row's own target already points at `freethreading` first; the new-module half is the misfiled part. |
| EP214 | ARISE Data-Flow Repair Graphs | `CORE/dispatch_plan.py :: plan_dag / eliminate_common_subgraphs` | **ACCEPT-GAP** | L | Searched `src/` for `def_use`, `defuse`, `statement_graph` → **0 matches**. The technique's deliverable is a program graph whose nodes are statements with def-use edges; this tree has a *dispatch* DAG (`plan_dag`) and, per the map, a Z3 module over compliance constraints — neither is a data-flow slice over source. Nothing to host it, and the row was mis-filed onto the plan DAG because both are "graphs". |
| EP223 | Uno-Orchestra Parsimonious Agent Routing | `CORE/dispatch_plan.py :: plan_dag ; CORE/cluster_route.py :: tpe_lite_suggest ; CORE/cascade.py :: CascadeRouter.route` | `CORE/cluster_route.py :: tpe_lite_suggest` + `CORE/cascade.py :: CascadeRouter.route` + `CORE/WORMS/expansion/allocation.py :: ThompsonAllocator` (one policy over the arm set) | L | `tpe_lite_suggest(trials, bounds, n_candidates=24)` confirmed at `cluster_route.py:64` and `proto_route(query, protos)` at `:55`; `CascadeRouter.route` read in full (cheap→big escalation, per-task); `ThompsonAllocator` read at `allocation.py` head (Beta posteriors with a `floor`, i.e. funded arms). The row's gap is that these three decide *separately*; the host edit is a single policy over their joint action space, which is why it is L. |
| EP227 | FlowAgent Continuous Tool Flow | `CORE/dispatch_plan.py :: plan_dag` | **ACCEPT-GAP** | L | Searched `src/` for `flow_matching` and `continuous_trajectory` → **0 matches**. The mechanism is conditional flow matching over a continuous semantic space; every plan artefact here is discrete (`plan_dag` takes `[{"id", "deps"}]` and returns a string `order`). There is no continuous model to host a flow, and the paper's global-plan/utility-convergence guarantee cannot be approximated by the existing DAG. |
| EP238 | SepsisAgent Clinical World Model | `CORE/dispatch_plan.py :: rehearse_dispatch` | `CORE/dream_arena.py :: compile_world, admit_worlds` (action-consequence world substrate) | L | `dream_arena.py` read in full: `compile_world(dream)` builds an arena `Environment` config (severity mix, `hard_ratio`, `era_pressure`) and `admit_worlds(arena, dreams, genome=None)` admits novel ones — a world-generation path exists, but it is dream-conditioned, not action-conditioned, and nothing predicts next state given an action. `rehearse_dispatch` read in full: it folds plan/assignment *gaps* into `predicted_failures` and never simulates consequences, so the row is right that a predictor is missing and right that `rehearse_dispatch` is where it would be consumed — but the model itself belongs with the world substrate, and L reflects that a next-state predictor has to be built, not wired. |
| EP248 | Agent JIT compilation | `CORE/dispatch_plan.py :: plan_dag` | `CORE/workflow.py :: WorkflowEngine` (NL→executable parallel steps) + `CORE/freethreading.py :: WorkStealingPool` | L | `workflow.py` head read: steps carry control flow and the engine executes via `ThreadPoolExecutor, as_completed`, so "compiled" parallel execution has a real home. Searched `src/` for `cost_model`, `latency_distribution`, `jit_compile` → **0 matches**: the Monte-Carlo latency estimator the scheduler needs does not exist anywhere, which is the L. |
| EP253 | MACA Structure-Guided Coordination | `CORE/dispatch_plan.py :: role-pool dispatch` | `CORE/WORMS/expansion/allocation.py :: ThompsonAllocator` (learned participation) feeding `CORE/dispatch_plan.py :: assign_roles` (the static map) | M | `assign_roles` read in full: `role_pools: {role: pool}` is a caller-supplied static dict and the function only reports `locality_hits` — no learning, exactly as the row says. `allocation.py` head read gives the learned-allocation primitive (`ThompsonAllocator` over `PROTEUS_ARMS` with `reward_for_outcome`) that can supply the prior; the row's "replace the static pool map with a learned participation prior" is a M-sized edit across those two. |
| EP345 | AI agents retry from pivotal mistakes | `CORE/dispatch_plan.py :: (LoongReflect prune-branch-keep-lesson, ~L221)` | `CORE/WORMS/expansion/reflexion.py :: record_reflection, reflections_for` (trajectory lessons) with `CORE/dispatch_plan.py :: record_backtrack` as the existing prune-half | M | `record_backtrack(branch, corrective_lesson)` read in full — it already prunes a branch and keeps the lesson, and always accepts. **Weaker provenance, stated plainly:** for `reflexion.py` I am relying on this session's earlier read (outline: `record_reflection` L20, `reflections_for` L52), not a re-open in this slice — the coordinator should re-confirm those two line numbers before filing. The genuinely missing half is pivotal-turn *location* (prefix reuse + suffix isolation) plus pivotal-aware credit assignment; the lesson store and the prune exist, so this is M, not L. |
| EP374 | TopoAgent topological reasoning | `azazael/src/CORE/dispatch_plan.py :: plan_dag` | `CORE/WORMS/METACLUSTER.py :: orchestrate / _execute_nature` (the "atom" is a nature) | M | `_plan_execution_order` confirmed at `METACLUSTER.py:304` by search, and the head/plan region of that module establishes that a *nature* is the unit both planned and executed. `plan_dag` read in full: it has no node-splitting path (gaps are limited to missing id / duplicate / unknown dep / cycle), so "adaptive atomic fission at a tool-capability boundary" is a new branch in the host, not a flag. The per-atom context isolation half would sit on the ASIL observation boundary, which I did not open in this slice, so I am not citing it as a host. |

## Notes for the coordinator

- **Two rows in this slice are not dispatch-layer at all.** `EP214` (data-flow graph over
  statements) and `EP227` (continuous flow matching) were filed onto `plan_dag` only
  because the words "graph" and "trajectory" appear in both. They belong in the
  no-host/ACCEPT-GAP bucket and should not be re-pointed at another module just to make
  the table look complete.
- **`assign_roles`, `rehearse_dispatch` and `record_backtrack` are all in the new
  `dispatch_plan.py`** — so for `EP253`, `EP238` and `EP345` the honest fix is not only
  "re-point the row" but "move the function": those three live in the misplaced module
  and their real host is named above. That is a code move, outside this slice's
  no-code-edit rule.
- **`EP209`'s existing target already names `freethreading.py` first** (the
  `dispatch_plan` mention is the second half), so the map's own cell is evidence that the
  misfiling was partial rather than total.
- I did not open `consensus.py`, `reflexion.py`, `structured_action.py` or
  `local_memory.py` bodies in this slice; the one citation that depends on a prior read
  (`reflexion.py`) is flagged as such rather than presented as verified here.

---

## state/rescore_partC.md

# Rescore slice C — rows targeting `verification_gate.py` / `structured_action.py`

Worker C of 4. Scope: every row of
`state/sota_batches/batch06/technique_codebase_map.json` whose `target` **contains**
`verification_gate.py` or `structured_action.py`.

## Preamble — counts, and one correction to the brief

The brief said 15 rows (8 + 7). That count was taken from rows where one of these
modules is the **first** `.py` named in `target`. The true set is **19** rows: four
more name one of them as a *secondary* target (EP160, EP266, EP269, EP383), and
EP395 names `verification_gate.py` first with `local_memory.py` second. I covered all
19; a row whose target is `audit_trail.py :: audit_verification_gate` also matched the
regex and was **excluded** as a false positive (it targets a pre-existing host).

| outcome | rows |
|---|---|
| reassigned to a pre-existing host | **16** |
| ACCEPT-GAP (no host in this tree) | **3** (EP122, EP132, EP352) |
| size S (host edit < ~30 lines) | 2 (EP44, EP152) |
| size M (a function or two) | 9 |
| size L (a real feature) | 8 |

**The most useful result for the coordinator:** three of these rows' deltas **already
exist** in the new layer and are only *misplaced*, so they are relocation tasks and
not new work — EP44 (`structured_action.py :: drive` implements the ReAct driver
loop and says so in its docstring), EP152 (`verification_gate.py :: decompose_rubric`
+ `_split_criterion`), EP370 (`verification_gate.py :: epistemic_state` +
`record_epistemic`). Two rows (EP122, EP132) are surveys/reviews whose "gap" is a
research recommendation, and one (EP352) needs model internals this tree does not own.

Evidence convention below: **opened** = I read the file; **symbol-scan** = I read the
file's top-level `def`/`class` listing (line numbers from that scan). Every path,
symbol and line number in the table came from one of those two; nothing is inferred
from the map's own wording.

| EP | technique | current target (new layer) | real host (path::symbol, or ACCEPT-GAP) | size | evidence (what I read) |
|---|---|---|---|---|---|
| EP44 | ReAct reasoning+acting | `CORE/structured_action.py :: semantic_action, observe` | `src/CORE/workflow.py :: WorkflowEngine` (the step loop/dependency graph — the driver of steps) | **S** | **opened** `structured_action.py` in full: `drive()` already implements thought→action→observation with plan repair on gap, and its docstring states it closes this exact map gap. **symbol-scan** `workflow.py`: `WorkflowStep` 78, `Workflow` 95, `WorkflowResult` 107, `WorkflowTemplate` 128, `ConditionalRouter` 254, `DependencyGraph` 387, `WorkflowEngine` 501, `get_workflow_engine` 953 |
| EP122 | The Four Pillars of LLM Autonomous Agents | `azazael/src/CORE/structured_action.py :: observe, semantic_action` | **ACCEPT-GAP** | L | **opened** `structured_action.py`: no profiling pillar and no subjective/objective evaluation split exists; the map's gap text is a survey recommendation, not a mechanism. Nothing to edit in any host I opened |
| EP125 | SWE-agent Agent-Computer Interface | `CORE/structured_action.py :: observe, semantic_action, record_asil` | `src/CORE/sentinel_enforcer.py :: enforce_write` / `:: enforce_replace` (the edit action vocabulary **is** the choke point's API; the post-edit guardrail belongs on the same path) | **M** | **symbol-scan** `sentinel_enforcer.py`: `enforce` 236, `enforce_write` 373, `enforce_replace` 385, `get_status` 550 |
| EP132 | How Autonomous LLM Agents Work | `azazael/src/CORE/structured_action.py :: observe, semantic_action, record_asil` | **ACCEPT-GAP** | L | **opened** `structured_action.py`. The map's own gap says "Review — no mechanism to implement"; the named open problems (hallucination, human parity, perception cost) are research questions |
| EP152 | DeepVerifier rubric verification | `azazael/src/CORE/verification_gate.py :: verify_before_accept, margin_check, divergence_gate` | `src/CORE/compliance/pre_action_gate.py :: PreActionGate` (acceptance policy at the gate) — and the delta is **already written**: `verification_gate.py :: decompose_rubric` 538 / `_split_criterion` 517 | **S** | **symbol-scan** `verification_gate.py` (18 symbols incl. `decompose_rubric` 538, `traceback`-free pure helpers) and `compliance/pre_action_gate.py` (`PreActionGate` 140, `get_pre_action_gate` 1502, `self_test` 1516) |
| EP156 | Agent uncertainty quantification | `azazael/src/CORE/verification_gate.py :: margin_check` | `src/CORE/compliance/governance.py :: ConfidenceGate` (existing confidence host) | **M** | **symbol-scan** `governance.py`: `JudgeVerdict` 35, `MultiAgentJudge` 62, `ConfidenceGate` 245, `BehavioralGraphAnalyzer` 325, `DualLedgerValidator` 481, `RealtimeAuditPipeline` 655 |
| EP160 | AgentSys Hierarchical Memory Isolation | `CORE/local_memory.py :: LocalMemoryStore + CORE/structured_action.py :: observe` | `src/CORE/local_memory.py :: LocalMemoryStore` (per-agent partition belongs at the store; `observe` is a validator and cannot isolate) | **L** | **symbol-scan** `local_memory.py`: `class LocalMemoryStore` 191, `record_event` 557. Gap text names a missing isolation boundary, not a validator change |
| EP168 | Agentics 2.0 transduction algebra | `CORE/structured_action.py :: semantic_action` | `src/CORE/workflow.py :: Workflow` (composition of typed steps) | **L** | **symbol-scan** `workflow.py` (above). The operator surface (`<<`, type merge, map-reduce composition) exists in **neither** file I opened nor in `rollback.py` (`record_merge` 31, `rollback_merge` 50) — this needs a design decision before it is a task |
| EP169 | Agentic AI Attack/Defense Survey | `CORE/verification_gate.py :: verify_before_accept + tools/engram_supervise.py` | `src/CORE/redteam.py :: HackCritic` (the existing adversarial-critic host) + `compliance/policy.py :: PolicyRule` (design-dimension checklist as data) | **M** | **symbol-scan** `redteam.py`: `featurize` 13, `HackCritic` 27, `progras_center` 62; `compliance/policy.py`: `PolicyEffect` 35 (ALLOW/DENY only), `PolicyRule` 40, `PolicyEngine` 115, `enforce_gate` 251 |
| EP191 | ReTAS Dialectical Alignment | `CORE/WORMS/expansion/meta_cognition.py :: MetaCognitionWorm + CORE/verification_gate.py :: verify_before_accept` | `src/CORE/WORMS/expansion/meta_cognition.py :: MetaCognitionWorm` — **already a pre-existing host, so this row is not misplaced** | **M** | **symbol-scan** `WORMS/expansion/meta_cognition.py`: `class MetaCognitionWorm` 118 |
| EP266 | ALAR adaptive latent agentic reasoning | ``CORE/latent_refine.py :: refine`` + ``latent_align.py :: prefix_inject`` + `CORE/structured_action.py :: semantic_action` | `src/CORE/neural_loop.py :: Loop` / `:: _stage_route` (per-turn mode policy is a routing decision in the existing loop) | **M** | **symbol-scan** `neural_loop.py`: `LoopContext` 162, `_stage_route` 447, `_stage_act` 475, `_stage_grade` 512, `default_stages` 979, `class Loop` 1008, `run_cycle` 1080 |
| EP269 | Agent libOS | ``CORE/compliance/`` (policy, state_machine, pre_action_gate, governance) + `CORE/structured_action.py :: semantic_action` | `src/CORE/compliance/policy.py :: PolicyEngine` + `compliance/pre_action_gate.py :: PreActionGate` | **L** | **symbol-scan** `policy.py` (`PolicyEngine` 115, `enforce_gate` 251, `default_policy_rules` 220, `BrokerInterceptor` 317) and `pre_action_gate.py` (`PreActionGate` 140). No `task_authority`/`capability` symbol in either scan |
| EP327 | Agent safety is action alignment | `CORE/structured_action.py :: semantic_action` | `src/CORE/compliance/policy.py :: PolicyEngine.enforce_gate` (authority-exercised vs authority-granted is a policy relation) | **M** | **symbol-scan** `policy.py` (above). `semantic_action` (opened) validates verb/target only — it has no authority input to compare against |
| EP349 | LLM-as-a-Verifier continuous verification | `CORE/verification_gate.py :: verify_before_accept *(unread)*` | `src/CORE/compliance/governance.py :: ConfidenceGate` | **L** | **symbol-scan** `governance.py` (`ConfidenceGate` 245). A continuous graded statistic needs a scoring source this tree does not have (models are providers) |
| EP352 | Hidden states predict AI agent failure | `CORE/verification_gate.py :: (S-RCT rollout vetting, ~L322)` | **ACCEPT-GAP** | L | **symbol-scan** `src/CORE/layerwise.py` — the nearest-named module is layer-wise **training** math (`lisa_sample` 10, `badam_blocks` 19, `mezo_perturb` 36, `galore_project` 49), not inference-time activation probing. No activation-probe host exists |
| EP370 | SLEUTH epistemic working memory | `azazael/src/CORE/verification_gate.py :: confirmed_revise ; :: margin_check` | `src/CORE/local_memory.py :: LocalMemoryStore` (recall should surface structured state, not raw rows) — delta **already written** as `verification_gate.py :: epistemic_state` 435 / `record_epistemic` 598 | **M** | **symbol-scan** `verification_gate.py` (`epistemic_state` 435, `record_epistemic` 598) and `local_memory.py` (`LocalMemoryStore` 191) |
| EP382 | ETAS effect-typed agent language | `azazael/src/CORE/structured_action.py :: semantic_action` | `src/CORE/compliance/policy.py :: PolicyRule` / `:: PolicyEffect` (effect rows + temporal calculus) + `compliance/governance.py :: RealtimeAuditPipeline` (residual-obligation monitor) | **L** | **symbol-scan** both files: `PolicyEffect` 35 is literally `ALLOW`/`DENY` only — the map's own cross-cutting finding says this class cannot express obligations; `RealtimeAuditPipeline` 655 |
| EP383 | Safety drift + action supervision | `azazael/src/CORE/verification_gate.py :: confidence_divergence_check ; azazael/src/CORE/circuit_breaker.py :: CircuitBreaker.force_trip / DeadLetter` | `src/CORE/circuit_breaker.py :: CircuitBreaker.force_trip` + `:: DeadLetter` — **already a pre-existing host** (second target), which is where termination belongs | **M** | **symbol-scan** `circuit_breaker.py`: `DeadLetter` 78, `force_trip` 144, `CircuitBreaker` 91, `BreakerRegistry` 343; `verification_gate.py`: `confidence_divergence_check` 166 |
| EP395 | ConsistencyGate write-time admission | `azazael/src/CORE/verification_gate.py :: verify_before_accept ; azazael/src/CORE/local_memory.py :: filter_quarantined (L950) / audit_retrieval` | `src/CORE/local_memory.py :: LocalMemoryStore.record_event` (the write path — admission must run before commit, not at retrieval) | **M** | **symbol-scan** `local_memory.py`: `LocalMemoryStore` 191, `record_event` 557; `audit_trail.py`: `audit_retrieval` 634, `audit_verification_gate` 654, `verify_completeness` 727 |

## Two things the coordinator should not miss

1. **The relocation set is cheap and should be done first.** EP44, EP152 and EP370
   are S/M because the code already exists in the new layer; only the *call path*
   is missing. That is the same repair shape as the 2026-10-09 boundary hooks.
2. **Two rows keep a pre-existing host and must not be reassigned further** (EP191 →
   `meta_cognition.py`, EP383 → `circuit_breaker.py`): their second target is already
   a real host, which means the map was only half-wrong for them — the *added*
   mechanism also exists, but in the new layer (`confidence_divergence_check`).

## Limitations

- I did not open `compliance/state_machine.py`, `compliance/governance.py`,
  `policy.py`, `pre_action_gate.py`, `redteam.py`, `neural_loop.py`, `workflow.py`,
  `layerwise.py` or `rollback.py` in full — only their symbol listings. So I can say
  a class/function **exists at line N**, not what it does internally. Sizes are
  therefore estimates from the gap text plus the host's surface.
- `compliance/pre_action_gate.py` is 1502 lines and I read none of its body; if the
  acceptance path is implemented differently than its name suggests, EP152/EP269's
  host choice should be re-checked by whoever implements it.
- EP168 and EP349 are the two rows where I would accept a reviewer moving my host
  choice to ACCEPT-GAP: both need a capability this tree does not visibly own.

---

## state/rescore_partD.md

# Row reassignment — latent_refine.py and rubric_evolution.py (worker D)

Source rows: `state/sota_batches/batch06/technique_codebase_map.json` (141 rows, one per
episode code), filtered to rows whose `target` names `latent_refine.py` (2 rows) or
`rubric_evolution.py` (2 rows). Both are **new modules of the 'SOTA blueprint' programme**,
so by the 2026-10-09 outlier diagnosis each row's delta belongs in the pre-existing
subsystem that owns the mechanism — not beside it.

Every `path :: symbol` cited below was **opened and read** during this pass (no citation is
taken from the map's own text). This is a reassignment only: no code was implemented here.

| EP | technique | current target (new layer) | real host (pre-existing) | size | evidence |
|---|---|---|---|---|---|
| EP266 | ALAR adaptive latent agentic reasoning | `CORE/latent_refine.py :: refine` + `latent_align.py :: prefix_inject` + `structured_action.py :: semantic_action` | `CORE/cascade.py :: CascadeRouter.route` | M | Opened `cascade.py`: `route(task, triage_fn, big_fn)` returns `{"answer", "via": "triage"\|"big", "confidence", "escalated"}` after comparing a caller-supplied confidence against `self.threshold` (0.65, `__init__`), with `n_escalated` accounting. That is a per-call cheap-vs-expensive **mode decision** — the same shape as choosing latent reasoning vs explicit CoT per turn. The latent carriers themselves stay correctly hosted by the new modules; only the per-turn *selector* is misplaced. |
| EP388 | LatentMT latent reasoning | `CORE/latent_refine.py :: refine, bounded_correct` (+ `latent_align.py`) | **ACCEPT-GAP** (no host in this tree) | L | Opened `latent_refine.py`: its module docstring states "NOT covered: the frozen-LLM + learned-reasoner pairing (needs a live model) — explicitly out of scope", and the module owns only the bounding, the iteration and the verdict over **caller-supplied** corrections. The residual delta is recurrent compute *inside a live model's hidden states*; models are consumed as opaque providers here (inference pool / provider registry), so no pre-existing host can own it. Keep as an accepted gap until an in-repo model path exists. |
| EP350 | Training AI agents without live environments | `CORE/rubric_evolution.py :: gate_distillation` | `CORE/WORMS/expansion/learning_grpo.py :: GRPOTrainer` | M | Opened `learning_grpo.py`: `GRPOTrainer` — "Group Relative Policy Optimization for worm selection … generates a group of candidate worms, scores them relative to each other, and updates the policy using group-normalized advantages" — is the only local policy-optimisation implementation, so the offline replayed-prefix protocol and the step-decaying sampling schedule belong on the trainer's data/sampling path. Note the distillation-loop alternative: `PSYCHE/distill.py` (opened) implements BC → DAgger → dDPO rounds with `test_theta_frozen` pinning theta, but for the P1 person artifact only, so it would need generalising before it could host a generic offline-replay recipe. |
| EP351 | Direct-OPD weak-to-strong distillation | `CORE/rubric_evolution.py :: gate_distillation` | `CORE/WORMS/expansion/learning_grpo.py :: GRPOTrainer` | S–M | Opened both candidates: `learning_grpo.py` (GRPOTrainer, group-normalised advantages) and `PSYCHE/distill.py` ("preference step — dDPO-style: shift student toward teacher where they disagree most, KL-regularized to reference"). The checkpoint-pair trick (post-RL vs pre-RL log-ratio as a dense implicit reward on the student's own states) is a **trainer-side reward construction**, so it lands on the trainer rather than on a new rubric module. |

## Notes for the coordinator

- `gate_distillation` in `rubric_evolution.py` is the *gate*, and the rows that point at it
  (EP350, EP351) are distillation-*protocol* techniques: the gate can keep gating, but the
  protocol half belongs to the training/distillation tier. That is why both rows move to the
  same host.
- EP266 is the only case here where an existing module already exposes the exact decision
  point (`CascadeRouter.route`); it is the cheapest of the four to adopt for real.
- EP388 should be *kept as a gap and marked accepted* rather than re-targeted again on the
  next pass — the blocker is architectural (no in-repo model internals), not editorial.
