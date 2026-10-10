# ABSENT-row triage (generated — do not hand-edit)

Source: `technique_codebase_map.json` (19 ABSENT rows) + `batch06/recheck_*.md` verdicts (36 parsed). Regenerate: `python tools/absent_triage.py`

| route | rows |
|---|---|
| ACCEPT-GAP-INFRA | 9 |
| BUILD-IN-HOST | 3 |
| NEEDS-HOST | 7 |

**Route rule** (written down so it can be argued with): a row is `ACCEPT-GAP-INFRA` when its subject is a model/training-stack internal this repo does not own (it consumes models as opaque providers); `BUILD-IN-HOST` when a real host was named by the re-check; otherwise `NEEDS-HOST`.

> **Binding constraint inherited from S1/S3.** A row built as a new standalone module with no production consumer is EXERCISE-ONLY by construction — it inflates the adoption count while changing no behaviour. `BUILD-IN-HOST` rows must be implemented where a caller already runs, or not at all.

## ACCEPT-GAP-INFRA (9)

| row | technique | host / reason |
|---|---|---|
| EP11 | ZeRO Memory Optimization | ZeRO optimizer/gradient/parameter partitioning -- no training stack that large |
| EP14 | ELECTRA + Reformer Efficiency | LSH attention + reversible residuals -- repo trains no transformer |
| EP38 | PaLM 540B Scaling | 540B dense-scale result -- consumes such models as providers |
| EP39 | Flamingo Few-Shot VLM | frozen vision-language bridge -- VLM reachable as a provider only |
| EP52 | GPT-4 Technical Report | multimodal pretraining + RLHF reward models -- no training-time alignment stack |
| EP68 | PagedAttention / vLLM | PagedAttention/KV block paging -- no owned inference engine |
| EP176 | Trigonometry fixes the AI memory bottleneck | token-level KV scoring -- nearest module disclaims the mechanism in its docstring |
| EP226 | MELT Looped Transformer | per-layer shared KV / looped-LM inference path -- model-internal |
| EP245 | Measure-theoretic reasoning bounds | measure-theoretic OOD bounds -- theory-only input, no runtime counterpart |

## BUILD-IN-HOST (3)

| row | technique | host / reason |
|---|---|---|
| EP183 | LogicLoc neurosymbolic localization | nearest: azazael/src/CORE/cd2_verifier.py :: SMTVerifier; azazael/src/CORE/compliance/state_machine.py :: FormalVerifier |
| EP206 | ObjectGraph Agent File Format | nearest: azazael/src/CORE/local_memory.py :: get_knowledge_graph_stats |
| EP252 | Drop-Stable-Rampup data scheduling | CORE/WORMS/expansion/scheduling.py :: `ScheduledTrainingWorm` exists but schedules *when* to train (DataPipelineWorm -> RLTrainLoop -> ModelVersioner) |

## NEEDS-HOST (7)

| row | technique | host / reason |
|---|---|---|
| EP110 | OneFlow Single-Agent Baseline | — |
| EP141 | AIRS-Bench research agents | none in the corrected inventory |
| EP153 | SERA soft-verified repo agents | none in the corrected inventory |
| EP237 | Why AI agents must map before acting | searched `azazael/src` for `cognitive_map` / `map_before` / `exploration_prior` / `world_map` — 0 matches |
| EP278 | VATS error-path injection | searched `azazael/src` for `injection` / `untrusted` / `sanitize` / `prompt_injection` — 0 matches; CORE/WORMS/expansion/security.py is `VulnScanner`/ |
| EP300 | Tensors prevent multi-agent LLM collisions | (none — searched) |
| EP343 | Agentic Test-Time Training aTTT | `CORE/WORMS/expansion/reflexion.py` (nearest artefact — and it states "verbal reinforcement **without weight updates**") |
