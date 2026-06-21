# LESSONS — Session June 4, 2026

## Lesson 1: Test Monkey-Patching Is a Code Smell — Inject Dependencies Instead

**Failure**: `test_neural_advancement.py` used `self.mc._persist_observation = lambda obs: None` monkey-patching to avoid slow SQLite writes to the production database. Tests timed out (300s) without this hack.

**Root Cause**: `MetaCognitionWorm.observe()`, `EvolutionEngine._persist_generation()`, and `DreamingModule._persist_dreaming_session()` all called `get_memory_store()` — a global singleton that connects to `~/.azazael/memory.db`. Each `observe()` call triggered a SQLite write, making tests impossibly slow.

**Fix**: Added `memory_store` injection parameter to `MetaCognitionWorm.__init__()`, `EvolutionEngine.__init__()`, and `DreamingModule.__init__()`. Three modes:
- `None` (default): Use global `get_memory_store()` — production behavior
- A `LocalMemoryStore` instance: Use injected store — integration testing
- `"none"` (string): Skip all persistence — fast unit testing

All `_persist_*()` methods, `save_state()`, `load_state()`, `save_checkpoint()`, and `load_checkpoint()` now check `self._memory_store` before calling `get_memory_store()`.

**Tests now pass in 0.06s** with `MetaCognitionWorm(memory_store="none")`.

---

## Lesson 2: Floating-Point Equality in Tests Requires `assertAlmostEqual`

**Failure**: `test_min_mutation_rate_is_fraction` failed with `assert 0.020000000000000004 != 0.02` because `0.1 * 0.2` in Python produces `0.020000000000000004`.

**Fix**: Use `assertAlmostEqual(value, expected, delta=0.001)` instead of `assertEqual()` for any computed float comparison.

---

## Lesson 3: NSGA-II Elitism Must Use Unique Slots Per Objective

**Failure**: In `optimize_multi_objective()`, the elitism loop overwrote `new_population[-1]` for every objective, so only the last objective's best survived. The first N-1 objectives' elites were lost.

**Fix**: Use `new_population[-(obj_idx + 1)]` with a `elite_slots` tracking set to ensure each objective's best occupies a unique slot from the end of the population.

---

## Lesson 4: Duplicate Code from Bad `str_replace` Requires Manual Cleanup

**Failure**: A `str_replace` that appended multi-objective code before `has_converged()` left a dangling duplicate `has_converged()` method body after `optimize_multi_objective()`'s return statement. The syntax checker didn't catch it because it was unreachable code (after a `return`).

**Fix**: Always read the full file after a large `str_replace` to verify no dangling content. The duplicate was removed manually.

---

## Lesson 5: `Callable` Must Be Explicitly Imported for Type Hints

**Failure**: `_non_dominated_sort()` and `_compute_crowding_distance()` used `List[Callable]` in type hints, but `Callable` was not in `evolution.py`'s imports. While Python 3.14 defers annotation evaluation (PEP 649), explicit imports are required for `typing.get_type_hints()` and code clarity.

**Fix**: Added `Callable` to `from typing import Dict, List, Optional, Any, Tuple, Callable`.

---

## Lesson 6: Thread-Safe Diversity Computation Must Use Snapshot Copies

**Failure**: `_compute_population_diversity()` and `_adapt_mutation_rate()` read `self._population` outside the lock in `evolve()` — racing with concurrent mutations.

**Fix**: Methods now accept optional `population` and `gene_bounds` parameters. `evolve()` and `optimize_multi_objective()` pass snapshot copies taken under the lock.

---

## Lesson 7: Session-to-Session State Must Auto-Save on `execute()`

**Failure**: `MetaCognitionWorm.save_state()`, `EvolutionEngine.save_checkpoint()`, and `DreamingModule` state were never called automatically. On process restart, all neural knowledge was lost.

**Fix**: 
- `MetaCognitionWorm.execute()` now calls `self.save_state()` after generating the introspection report
- `MetaCognitionWorm.__init__()` now calls `self.load_state()` to auto-restore from previous sessions
- `EvolutionEngine.execute()` now calls `self.save_checkpoint()` when population is non-empty
- `DreamingModule` now auto-loads scenarios on init

---

## Lesson 8: WSL2 Expansion Directory Was Never Synced

**Failure**: Windows `azazael/src/CORE/WORMS/expansion/` (16 files, including all neural advancement modules) was never synced to WSL2 `/root/azazael/src/CORE/WORMS/expansion/`. The WSL2 installation was running a stale version without meta_cognition, evolution, or dreaming modules.

**Fix**: Copied all 16 `.py` files + `hydra_bridge.py` from Windows to WSL2. Verified with `ls -la`.

---

## Lesson 9: Data-Driven Dreams Beat Random Suggestions

**Failure**: `DreamingModule._generate_policy_suggestions()` used `random.random()` for confidence scores and hardcoded `"retry_with_backoff"` as the only recovery action. Dreams were synthetic, not evidence-based.

**Fix**: Replaced with:
- `_mine_error_recovery_patterns()` — detects error→success sequences from current scenario data
- `_mine_historical_recovery_patterns()` — queries LocalMemoryStore for cross-session error-recovery patterns
- Confidence scores now reflect actual evidence counts and historical success rates

---

## Lesson 10: Cross-Worm Correlation Reveals Hidden Dependencies

**Finding**: Wired `MetaCognitionWorm.compute_cross_worm_correlation()` into HydraBridge. Error patterns from one worm type can predict failures in another — e.g., SystemZ errors correlate with NETWORXZ failures. The correlation matrix enables joint CurativePool governance recommendations.
