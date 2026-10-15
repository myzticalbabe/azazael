# BLIND-22 wire-or-retire PROPOSALS — corrected predicate (2026-10-15, #721 item 4)

Task: #657 BLIND-22 / #712 Phase 2. **Proposals ONLY** — this file never edits
`state/adoption_census.json`; opencode applies census fields.

**Predicate**: the #682-corrected module-qualified audit (Phase 1, this session).
A symbol here has NO reference outside `technique_wiring/` that is module-qualified
— i.e. its only caller is its own exercise adapter. That is EXERCISE-ONLY, which is
a strict SUBSET of blind: every one of these has at least one call site inside
`technique_wiring/`.

Audit header:
```
PRODUCTION-CALLED      : 115
```
Exercise-only rows: **29** (18 LocalMemoryStore methods + 11 others).

## Proposed dispositions

| EP | binding | sym | refs outside technique_wiring (module-qualified) | proposal |
|---|---|---|---|---|
| EP97 | `{_POLICY}:grpo_advantages` | `grpo_advantages` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP105 | `CORE.prm:sp_prm_scores` | `sp_prm_scores` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP110 | `CORE.WORMS.expansion.allocation:MCTSPlanner` | `MCTSPlanner` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP120 | `CORE.local_memory:LocalMemoryStore.reflect_replay` | `reflect_replay` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP146 | `CORE.local_memory:LocalMemoryStore.bounded_context` | `bounded_context` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP151 | `{_POLICY}:gdpo_advantages` | `gdpo_advantages` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP154 | `CORE.local_memory:LocalMemoryStore.workspace_protocol_st` | `workspace_protocol_status` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP160 | `CORE.local_memory:LocalMemoryStore.agent_scope_probe` | `agent_scope_probe` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP192 | `CORE.local_memory:LocalMemoryStore.ontology_triple_view` | `ontology_triple_view` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP206 | `CORE.local_memory:LocalMemoryStore.document_graph_stats` | `document_graph_stats` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP216 | `CORE.local_memory:LocalMemoryStore.score_pending_actions` | `score_pending_actions` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP221 | `CORE.local_memory:LocalMemoryStore.decay_memory_in_place` | `decay_memory_in_place` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP233 | `CORE.local_memory:LocalMemoryStore.backward_chain_recall` | `backward_chain_recall` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP242 | `CORE.local_memory:LocalMemoryStore.experience_edges` | `experience_edges` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP247 | `CORE.local_memory:LocalMemoryStore.orientation_index` | `orientation_index` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP259 | `CORE.WORMS.expansion.policy_optimization:depo_filter` | `depo_filter` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP280 | `PSYCHE.distill:onpolicy_refine` | `onpolicy_refine` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP294 | `CORE.WORMS.expansion.reflexion:reflections_for` | `reflections_for` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP319 | `CORE.local_memory:LocalMemoryStore.transition_check` | `transition_check` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP336 | `CORE.local_memory:LocalMemoryStore.retype_ladder` | `retype_ladder` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP350 | `CORE.rubric_evolution:gate_distillation` | `gate_distillation` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP391 | `CORE.local_memory:LocalMemoryStore.programmatic_memory_s` | `programmatic_memory_surface` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP394 | `CORE.local_memory:LocalMemoryStore.lifecycle_fidelity` | `lifecycle_fidelity` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP395 | `CORE.local_memory:LocalMemoryStore.capsule_probe` | `capsule_probe` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP412 | `CORE.WORMS.expansion.policy_optimization:depo_filter` | `depo_filter` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP414 | `CORE.local_memory:LocalMemoryStore.generative_compaction` | `generative_compaction_status` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP440 | `CORE.latent_align:norm_calibrate` | `norm_calibrate` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP471 | `CORE.rubric_evolution:gate_distillation` | `gate_distillation` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |
| EP478 | `CORE.local_memory:LocalMemoryStore.composite_eviction_pr` | `composite_eviction_preview` | 0 | RETIRE -> documented EXERCISE-ONLY (census: opencode) |

## Rationale and the exception

- **RETIRE here means "documented exercise-only", not deletion.** The technique is
  reachable only through its own adapter; that is its support today. Deleting would
  remove a working exercise path; wiring a fresh caller would manufacture the very
  "pure function nothing calls" defect this campaign removes (the #682/§0f rule).
- **`LocalMemoryStore.*` group (18)**: these are methods on a live class. Their
  exercise adapter reaches them; no production path does. Proposal is RETIRE
  (documented) per item, NOT a bulk delete — each needs its own owner sign-off
  because the class is live and a future caller is plausible. Marked as a group
  only to make the review tractable.
- **Dynamic-dispatch caveat is CLOSED** (#682 §0g(b)): 0 of these symbols appear as
  a string literal outside the probe file; `LocalMemoryStore` defines no
  `__getattr__`/`__getattribute__`/`__dir__`.
- **Never a silent skip**: each row is enumerated with its binding and the reason a
  reference is absent (module-qualified predicate), so opencode can apply census
  fields per item.

## Handoff

Proposals are consumed by the census owner (opencode). This lane does not write
`state/adoption_census.json`.
