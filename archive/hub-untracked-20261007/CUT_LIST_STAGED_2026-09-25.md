# Staged wire-or-cut list (2026-09-25 census — NOT YET EXECUTED)

Forensic census of every algorithm in the pipeline: 14 FIRES / 20 WIRED-IDLE /
27 DEAD (full evidence in session record 2026-09-25). Already executed:
`src/CORE/qd_bridge.py` deleted (zero importers, verified), Chestburster +
NASMeshSearcher labels corrected, `structural_mutate` + `run_diversity_evidence`
verified WIRED (no action).

## Proposed CUTS (needs operator approval — destructive)

| # | Item | Evidence of death | Risk of cutting |
|---|------|-------------------|-----------------|
| 1 | `deepseek`, `vllm`, `sglang`, `openwebui`, `jan`, `kilo`, `opencode` names in servemesh CHAIN / hyper_optimizer / query_loop | Not in provider registry — `get_provider()` raises `ValueError`; silently skipped | Low (dead references), but servemesh CHAIN order changes — review |
| 2 | `zhipu`, `ovhcloud` registry entries | No chain/aug/API-score membership; zero cache files | Low, registry-only |
| 3 | `*_native` classes (ollama_native, gemini_native, huggingface_native, mistral_fim_native, cohere_native) | No production `get_provider()` calls with these names | Low, dead classes |
| 4 | `llama_cpp_direct`, `huggingface_direct`, `openvino` providers | Actively avoided per providers.py:3001-3035 | Low |
| 5 | `llama_mythos_v2`, `llama_qwopus`, `llama_ornith` registry entries | Local servers never started; zero cache files | Low |
| 6 | `CPPNGenome`, `Chorus` (as called modules) | Only verify_proteus references; zero prod calls | Medium — verify_proteus asserts on them; update script + tests together |
| 7 | `Arena`/`ArenaWorld`, `Loom` | Only verify_proteus; unfunded arms | Medium — PROTEUS_ARMS lists `arena`; reconciling changes allocation surface |
| 8 | HYDRAMETA, `FusionCore`/`FusionHealer`/`TotalFusion` | `__main__` demos + legacy imports only | Medium — legacy ORCHESTRATION imports reference them; cut in dependency order |
| 9 | `NerveTrainer`, `QLearningFileOptimizer`, `AzazaelOptimizer`, `DistributedTrainer`, `MultiAgentQLearning`, `SpawnDiversityEngine`, `SB3AgentPool`, `AgentPool`, `AgentHealth*`, `Qwen35SSM` | `__main__`/test-only, zero prod callers | Low-Medium each; batch after 1-8 |

## Proposed KEEP-IDLE (do not cut — reachable, may fire)
`SchemaAwareFeatureExtractor` (ALLPAR/flag paths), `GeneticOptimizer` (fires via DREAMTUNE/WORMGA — actually FIRES, keep), NASMeshSearcherWorm (spine-guarded), Kademlia gossip, `RLTrainLoop` (indirect), inference engines, eve/Emotion/Policy/MultiAgentJudge/Workflow/CrossNature routers, `FeatureEngineer` (dead only via dead parent — re-evaluate if NeuralPipeline production use ever lands), all 12 WIRED-IDLE cloud providers (credential/key-gated, not code-dead).

## Executed 2026-09-25 (monitoring shift)
- Group 1 executed as **filter-not-delete**: `next_provider()` skips registry-absent
  names, reports them (`skipped_unresolvable`). CHAIN tuple untouched (audit
  trail + tests pin it). Rationale: deletion would change failover order
  semantics; filtering fixes the downstream-ValueError degradation.
- Groups 2–5 **downgraded to KEEP-IDLE** on re-verification (census overstated):
  zhipu/ovhcloud are documented, user-configurable providers (never-fired ≠
  dead); `*_native`/`*_direct` classes are package-exported and referenced by
  PARALLEL_INFERENCE_WORM + the avoidance block (the avoidance IS the
  resolution); local-model entries are inert registry data confined to
  providers.py. Cutting any of these fixes no error and risks breaking
  user configuration. Revisit only with a firing-path redesign, not a sweep.
- Groups 6-9 **downgraded to KEEP (test-pinned design)**: `arena`/`morph`/
  `chorus`/`tpe` in PROTEUS_ARMS are intentionally wider than the fundable
  SEARCH_ARMS set — `test_default_decision_set_is_only_fundable_arms` pins the
  strict-subset relation as the 9/12 mislabelling fix. HYDRAMETA/ADLP are
  live-imported legacy (242 refs); cutting fixes no error and risks import
  breakage. Group 9's `__main__`/test-only trainers stay dead-declared but
  present: deleting them saves nothing at runtime and orphans their tests.

## Rule applied
Tested-but-never-called = DEAD. Monitored-label-only = WIRED-IDLE. Anything with a
last-7d execution artifact = FIRES. Re-run the census before executing cuts —
an idle item may have fired since.

## E-P2 rulings (2026-09-25 monitoring shift)
- GRPOTUNE: already delisted (run_full_pass.py derives lists from registry; test asserts exclusion). No action.
- ALLPAR (4/1885 picks, 0 wins): working as designed. Thompson avoids a 0/4 track; epsilon floor + 48-slot stalest backstop guarantee retry. No code change; forcing picks would fund known-losing compute.
