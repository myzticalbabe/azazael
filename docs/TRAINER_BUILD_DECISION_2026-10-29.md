# Trainers: Build More vs Morph/Mutate Our Own (2026-10-29)

## Where kilo left it
- `b4d37cd1` landed the **trainers_v2 contract end-to-end (F2 closure)**:
  `SB3Agent` with worm_id, factory case-insensitive algo resolution,
  error-dict `train()`, GIL-subprocess fallback, 16 new + 66 existing tests.
- `343cf906` finished SB3 (`tests/test_sb3_trainers_v2.py` 16 passed).
- Standing fleet today: **SB3** (PPO/DQN/A2C/SAC/TD3/DDPG + contrib
  QRDQN/TRPO/TQC/ARS/MaskablePPO), **GRPO** (`learning_grpo.py` GRPOTrainer +
  ABTestRunner, MGPO multi-granularity, token-regulated), **federated**
  (FedAvg over SB3/GRPO policies), **tensor trainer**, all wired through
  `NeuralPipeline._train_sb3` + `TrainingOrchestrator` with worm identity.

So kilo's remaining "build trainers" = widening algo coverage and hardening,
not laying foundations. Foundations are landed.

## Do we need enhanced algos? Some — not many
Gaps worth filling (each is a bounded trainer build):
1. **Offline/constrained** — CQL/BCQ-style or masked-action PPO for safety-
   critical/discrete-masked tasks (MaskablePPO covers masking; offline data
   has no trainer yet).
2. **Multi-objective** — NSGA2 (`src/ML/nsga.py`) exists as stateless
   functions + driver, but no SB3/GRPO trainer consumes its Pareto fronts.
   Wire NSGA2 selection into a trainer and the "more trainers" ask shrinks.
3. **Hierarchical/options** — nothing in the fleet; only build on a real task
   that needs temporal abstraction, not speculatively.

Do NOT import algorithm zoos. Each new trainer must arrive with the F2
contract (worm_id, error-dict train, GIL-subprocess fallback, tests) or it is
a second fleet, not a first-team addition.

## Can we morph/mutate our own? YES — the machinery is already here
- **NSGA2**: `sbx_crossover` + `polynomial_mutation` + non-dominated sort +
  crowding distance (`src/ML/nsga.py`); `nsga_tuner.py` drives tuning.
- **EvolutionEngine** (`evolution.py:144`), **MetaEvolutionWorm**,
  **CPPN mutate**, **wiring_genome** (`mutate_flip_active`,
  `mutate_bump_priority`, `mutate_adjust_cooldown`), **arena Environment.mutate**.
- **Agent.spawn_sub_agent** — the reproduction primitive.

What is missing is the *loop closure*: mutate trainer hyperparameters and
policies under NSGA2 selection pressure, promote winners back into the
trainers_v2 factory. That is cheaper than building trainers by hand and
compounds: every generation improves the whole fleet.

## Decision
1. **Morph first.** Close the loop: NSGA2-driven mutation over existing
   SB3/GRPO hyperparameters → winners registered as first-class factory
   algos. New capability from old parts.
2. **Build selectively.** Only the three gaps above, each with F2 contract +
   tests, each justified by a task no morphed trainer can do.
3. **No zoo imports.** One trainer earned through the factory beats ten
   vendored.

## Next concrete step (proposed)
`trainers_v2` factory gains a `morphed/` namespace: NSGA2 proposes
hyperparam genomes, EvolutionEngine evaluates, Pareto winners land as
`morphed_<algo>_<gen>` with worm_id + tests. Kilo's unfinished trainer tasks
become the evaluation suite for generation 0.
