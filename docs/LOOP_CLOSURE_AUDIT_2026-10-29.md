# Loop Closure Audit + Transformation Taxonomy (2026-10-29)

## 1. Loop audit: what closes, what dangles

| Loop | Stages present | Closes? | Gap |
|---|---|---|---|
| Evolution (`evolution.py`) | SELECT→CROSSOVER→MUTATE→REPLACE, elitism, fencing, early-stop, levy-on-stagnation | YES (internally) | Output is a better genome population — but no consumer promotes winners into `trainers_v2`. Evolution improves genomes nobody adopts. |
| SB3 train (`sb3_agent.py:train`) | data→gym env→learn→register_model→ModelVersioner→PAMS payload | YES (model registered) | Hyperparams are fixed per call — nothing varies them. Train is a point, not a search. |
| GRPO (`learning_grpo.py`) | group→reward→normalize→update→snapshot→buffer | YES (policy updates) | Zero-variance guard can no-op; snapshots persist but no outer loop selects among them. |
| Memory/PAMS (promote→recall→train) | promote stores, recall reads, train consumes | HALF | Train consumes memories, but no lesson flows back as a *constraint* on the next train. Lessons are recorded, not enforced. |
| Sync (`sync_all.py`) | sync legs → `--verify` PASS | YES | Verified tonight (2085/2085, md5). Closes. |
| Shard sweep (`SHARDS`) | sweep→sweep.json→route_lang | YES (as of 72333c07) | Smallest closed loop in the repo. Template for the others. |
| Morph (proposed) | mutate→evaluate→promote→factory | NO — NOT BUILT | This is the missing closure from TRAINER_BUILD_DECISION. |

**One-sentence verdict:** every *inner* loop closes; the *outer* loop —
evolution output → trainer factory input — does not exist yet. That single
missing edge is the whole build.

## 2. Four transformations, precisely distinguished

Borrowed terms, fixed meanings for this repo. Ranked by depth of change:

### MUTATE — vary parameters, keep identity
Same algorithm, same code path, different numbers. Learning rate 3e-4 →
1e-4, SBX crossover on a hyperparam vector, polynomial mutation on
`wiring_genome` priorities. `NSGA2`, `EvolutionEngine`, `wiring_genome.mutate_*`
live here. Identity preserved: `morphed_ppo_gen3` is still PPO. Cheapest,
safest, compounds fastest. **Do first, continuously.**

### MORPH — vary structure, keep lineage
Same ancestry, new shape. PPO + GRPO advantage graft (the arena synthesis
pattern), SB3 policy head swapped, replay buffer replaced with a
token-regulated one, two trainers fused behind one `train()` contract.
Lineage recorded (`parent_ids`), behavior may differ discontinuously.
`EvolutionEngine` crossover + grafting live here. **Do second, per gap.**

### TRANSMOGRIFICATION — change kind, keep function
Same contract, unrecognizable implementation. The gateway pair IS this:
identical OpenAI-front-end behavior, one in Go stdlib, one in Rust
axum/tokio. A Python trainer reimplemented as a compiled Rust shard behind
`RustResult` is transmogrification. Function preserved bit-for-bit
(golden agreement), kind wholly different. **Do third, for hot paths only**
(build cost is a full rewrite + golden proof).

### TRANSSUBSTANTIATION — change essence, keep accidents
The deepest cut, used sparingly and literally: the *observable form stays
identical* while the *underlying reality changes*. A `train()` call that
returns the same dict shape but is now served by a morphed Pareto-winner
instead of the original algorithm — the caller cannot tell, the substance
is different. Factory promotion (`morphed_<algo>_<gen>` shadowing the
canonical name after golden proof) is transsubstantiation as a deployment
act. **Do last, as the promotion mechanism itself** — it is how a winner
takes the throne without breaking a single caller.

Memory aid: **mutate** tunes the instrument, **morph** rebuilds it,
**transmogrify** re-casts it in another medium, **transsubstantiate**
replaces what it *is* while it still *looks* the same.

## 3. Algo styles we can create (from these four moves)

With SB3 (11 algos) × GRPO × NSGA2 × EvolutionEngine × 6-language shards:

1. **Morphed-hyperparam family** (mutate): `morphed_ppo_g3`, `morphed_sac_g7`
   — Pareto winners on sample-efficiency × stability. Infinite supply.
2. **Grafted hybrids** (morph): PPO+GRPO advantages, GRPO+NSGA2 selection,
   MaskablePPO+offline constraints. Bounded by real gaps (3 identified).
3. **Transmogrified hot paths** (transmogrify): Rust/Go reimplementations of
   the 3–5 measured bottlenecks behind identical result dicts. Gateway done;
   runners and parsers next.
4. **Shadow-promoted champions** (transsubstantiation): factory names that
   resolve to morphed winners after golden proof — callers unchanged,
   substance upgraded. The endgame of the morph loop.
5. **Federated composites** (morph at population level): FedAvg over
   heterogeneous morphed policies — already scaffolded in `federated.py`.
6. **Wiring-genome specialists** (mutate at infra level): per-worm priority/
   cooldown/activity genomes evolved for routing, not learning — pure
   `wiring_genome` NSGA2 search, zero training cost.

## 4. Build order (cheapest closure first)
1. `morphed/` factory namespace + NSGA2 hyperparam search (closes THE loop).
2. Three gap trainers (offline, multi-objective, hierarchical-on-demand).
3. Transmogrified runners/parsers by sweep measurement.
4. Shadow promotion once golden behavioral fixtures exist.

## Sources
- `src/CORE/WORMS/expansion/evolution.py:442` (generation cycle)
- `src/CORE/sb3_agent.py:641` (train), `learning_grpo.py:394` (update_policy)
- `src/ML/nsga.py` (sbx + polynomial), `wiring_genome.py:239+` (mutators)
- `SHARDS/polyglot.py:77` (sweep), `registry.py` route_lang
- Prior: TRAINER_BUILD_DECISION_2026-10-29.md, MULTILINGUAL_SHARD_REVIEW
