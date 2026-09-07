# LEARNING-LOOP SUBSYSTEM AUDIT — 2026-09-07

Scope: the autonomous learning loop (dreamer -> bridge -> metacognition ->
RL/evolution) and its immediate dependencies. Method: Azazael 3-pass
architecture review (inventory / rate / scorecard) with evidence from the
live Windows DB and the synced repos (WSL `/root/azazael`, Windows
`C:\Users\clint\azazael` — byte-identical for all domain files).

---

## PASS 1 — INVENTORY (What exists)

### Domain files (7,210 LOC)

| File | LOC | Role |
|------|-----|------|
| `src/CORE/WORMS/expansion/dreaming.py` | 1,104 | Dream generator + `run_dreaming_pipeline()`; steers by strategy |
| `src/CORE/WORMS/expansion/meta_cognition.py` | 1,003 | Observe/analyze/adapt; `adapt_strategy`, `recommend_from_evidence` |
| `src/CORE/WORMS/expansion/learning.py` | 2,132 | RLTrainLoop, ModelVersioner, DataPipelineWorm, ABTestRunner, FeatureEngineer, SchemaAwareFeatureExtractor |
| `src/CORE/WORMS/expansion/evolution.py` | 993 | EvolutionEngine (population GA over hyperparameter genomes) |
| `src/CORE/dream_policy_bridge.py` | 117 | `apply_dream_policy` — pipeline <-> metacog adapter, policy_applied audit |
| `src/CORE/local_memory.py` | 1,518 | LocalMemoryStore — SQLite + FTS5 persistence hub for all loops |
| `src/scripts/monitor_learning.py` | 343 | Health monitor (exit 0/1/2, cron-able, --watch mode) |

### Scheduler drivers (Windows only — NOT in either repo)

| File | Schedule | Role |
|------|----------|------|
| `scripts/dream_cycle.py` | every 5 min | `run_dreaming_pipeline(num_episodes=8, scenario_count=40, policy_fn=bridge)` |
| `scripts/metacog_cycle.py` | every 5 min (2026-09-07) | feed cluster outcomes -> analyze -> evidence-driven adaptation |
| `scripts/evolution_cycle.py` | daily | GA over RLTrainLoop hyperparameters -> best genome |
| (TrainingOrchestrator) | — | training runs |

### Data flows (observed live, 2026-09-07 19:53 UTC)

```
dream_cycle (5 min)
  -> dreaming.run_dreaming_pipeline(num_episodes=8, policy_fn=bridge)
     -> steering lookup (dream_tuning_for('global')) -> tuned params
     -> dream rows + strategy_steered events
  -> dream_policy_bridge.apply_dream_policy
     -> meta_cognition.adapt_strategy('global', recommended=..., confidence=...)
        -> ADOPT_CONFIDENCE 0.5 gate -> policy_applied rows + strategy_adaptation
     -> save_state() every run
metacog_cycle (daily)
  -> observe(cluster outcomes) -> analyze_patterns -> recommend_from_evidence
     -> adapt_strategy('global', recommended, confidence)   [NEW 2026-09-07]
evolution_cycle (daily)
  -> EvolutionEngine.fitness = train_from_memory(avg_reward)  [gradient NEW 2026-09-07]
```

---

## PASS 2 — RATE (How healthy)

### Cohesion: 0.85 (High)
The seven domain files serve one purpose (close the learning loop) and share
a single persistence hub. Penalty: `learning.py` is a mixed bag — RL training,
model versioning, ETL, feature extraction, and AB testing in one 2,132-line
file (the classic god-object; `SchemaAwareFeatureExtractor` alone is ~330
lines). Dreaming/meta_cognition/bridge are well-scoped.

### Coupling: 6/10 (Moderate, with one choke point)
- `local_memory.py` is the hub: ~20 inbound call sites across the domain
  (compare `paths.py` at 139 in the wider system — still the single point of
  failure for persistence; all loops die if it breaks).
- Domain -> CORE: `freethreading`, `pattern_memory`, `Agent` (lazy imports).
- Platform coupling: all four cycle drivers hard-code
  `C:/Users/clint/azazael/src` and Windows Task Scheduler names. The loops
  only run on Windows; WSL can query but not drive them.
- All cross-environment copies are byte-identical (verified today).

### Health: 🟡 Mixed (improving)
Six real defects found and fixed today (see Defect Log). The loop now
persists state, steers behavior, gates adoption on evidence, and carries a
reward gradient. Remaining red flags: zero committed tests, god-object
`learning.py`, backup artifacts polluting `src/`, stale WSL DB copy, and the
metacog cycle's original single daily cadence (moved to 5 min on 2026-09-07).

### Defect log (2026-09-07, all verified live)

| # | Defect | Root cause | Fix | Live proof |
|---|--------|-----------|-----|-----------|
| 1 | Strategy "evolution" was a random walk | `load_state()` used FTS5 (relevance-ranked) -> restored stale July rows -> every cycle restarted at `default` | `query_memories` newest-first | state now loads `conservative` across cycles |
| 2 | Steering never fired | live driver calls pipeline directly, no strategy passed | steering lookup inside `run_dreaming_pipeline` | `strategy_steered` every 5-min cycle |
| 3 | Metacog state died at exit | `metacog_cycle.py` never called `save_state()` | added | — |
| 4 | Conservative trap | exploration gated `creativity > 0.2`; conservative sets 0.15 -> suggestion channel silenced | reduce, don't eliminate | suggestions 0.00 -> 1.00/dream |
| 5 | Adoption churn | no confidence gate -> flips on 0.06-0.12 noise | `ADOPT_CONFIDENCE = 0.5` | bridge records `low-confidence` holds |
| 6 | Flat evolution (open) | `_compute_reward` ignored the chosen action -> every genome scored ~50.0 | action-dependent reward (error->remediate, warning->alert, info->log) | eps 0.0/0.1/0.5 -> -5.43/+8.07/+4.24 |

---

## PASS 3 — SCORECARD (12 dimensions, subsystem)

| Dimension | Score | Assessment | Key improvement |
|-----------|-------|-----------|-----------------|
| Modular cohesion | 7.5 | Domain is one purpose; `learning.py` is a god-object | Split learning.py by worm |
| Inter-module coupling | 6.0 | Clean domain graph; local_memory is the choke point | Defensive copy / WAL check |
| Dependency hygiene | 7.0 | No shims in domain; 5 `.fixbak`/`.pre_gate` artifacts pollute src | Move backups to `backups/` |
| Type safety | 6.0 | Annotated; mypy not run in-session on the domain | Add mypy to monitor |
| Test coverage | 2.0 | **Zero committed tests** for the loop (scratch-DB suites only) | Commit test suite in `src/tests/` |
| Documentation | 7.5 | Docstrings + this audit + monitor; no TODO/roadmap docs exist | Add LEARNING_LOOP_TODO.md |
| Build system | 5.0 | No build; Task Scheduler + sys.path hacks | Package as installed module |
| 3.14t readiness | 7.0 | Free-threading guards present; verified Python 3.14 import | — |
| Shell injection safety | 10.0 | 0 `shell=True` in domain | — |
| Package management | 4.0 | sys.path.insert(0, 'src') in every driver | editable install |
| Desktop integration | n/a | No desktop surface (loops are headless) | — |
| **Overall** | **6.4/10** | Working end-to-end, evidence-gated, evolving; unshipped quality gates | 8 improvement items |

---

## IMPROVEMENT ITEMS (cross-referenced — no TODO docs exist, so all are ADDITIVE)

| ID | Item | Effort | Impact | Priority |
|----|------|--------|--------|----------|
| AR-1 | Commit the learning-loop test suite (reward, steering, evidence, persistence) into `src/tests/` | 3h | 🔴 | P0 |
| AR-2 | Split `learning.py` (2,132 LOC) into per-worm modules | 4h | 🔴 | P1 |
| AR-3 | Move `.fixbak_*`/`.pre_gate_backup` artifacts to a `backups/` dir + .gitignore | 0.2h | 🟡 | P1 |
| AR-4 | Make the WSL monitor default to the live DB (stale-copy trap cost a false FAIL today) | 0.5h | 🟡 | P1 |
| AR-5 | Run the monitor against the live DB for 24h to confirm the evolution WARN clears after the reward fix | 0h (watch) | 🟡 | P1 |
| AR-6 | Convert cycle drivers to a package (`src/scripts/` as a module) — kill sys.path hacks | 2h | 🟢 | P2 |
| AR-7 | Add mypy run over the domain to the monitor's FAIL checks | 1h | 🟢 | P2 |
| AR-8 | Write LEARNING_LOOP_TODO.md to track AR-1..7 (cross-reference target) | 0.5h | 🟢 | P2 |

### Baseline metrics (recorded so improvement is measurable)

- Loop cadence: 5 min; state_saved age 0.7 min (was 20 h stale this morning)
- steering events: 13 in 60-min window (was 0 all day)
- switches(24h): 8 (was 0)
- avg dream quality(1h): 0.732
- evolution trajectory: flat (pre-fix); next daily run must show spread
- training avg_reward: 50.0 constant (pre-fix); next run must vary by genome