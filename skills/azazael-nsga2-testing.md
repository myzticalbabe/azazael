# Azazael NSGA-II Testing — EvolutionEngine Unit Tests

## Overview
Comprehensive unit tests for the NSGA-II evolutionary optimization engine.

## Test Classes (9 classes, 16 tests)

### TestNSGA2NonDominatedSort (4 tests)
- **test_trivial_front_all_non_dominated**: All individuals Pareto-optimal when objectives trade off
- **test_clear_domination**: One genome clearly dominates another
- **test_partial_domination_no_dominance**: Neither dominates (different objective strengths)
- **test_three_tiers**: Three tiers of domination (Pareto, middle, worst)

### TestCrowdingDistance (3 tests)
- **test_two_individuals_both_infinite**: Boundary points get infinite distance
- **test_three_individuals_boundary_vs_interior**: Min/max = inf, interior = finite
- **test_crowding_distance_normalized**: Distance normalized by objective range

### TestMultiObjectiveOptimization (2 tests)
- **test_optimize_returns_pareto_front**: Valid Pareto front with objectives computed
- **test_no_two_objectives_errors**: Single objective rejected with clear error

### TestTournamentSelection (2 tests)
- **test_selection_returns_fittest**: Average fitness above population mean
- **test_highest_fitness_always_wins**: Best individual wins its tournaments

### TestAdaptiveMutation (3 tests)
- **test_low_diversity_increases_mutation**: Identical population -> mutation boost
- **test_high_diversity_decreases_mutation**: Diverse population -> mutation decays
- **test_mutation_stays_in_bounds**: Rate never exceeds max or falls below min

### TestCheckpointRoundTrip (2 tests)
- **test_save_and_load_restores_state**: Generation, population, best fitness preserved
- **test_has_converged_detects_stagnation**: Plateaus detected
- **test_has_converged_returns_false_when_improving**: Progress not flagged

### TestElitism (1 test)
- **test_elites_survive_generation**: Top individuals persist after evolve()

### TestPopulationDiversity (2 tests)
- **test_identical_population_zero_diversity**: Same genes -> 0 diversity
- **test_maximally_diverse_population**: Full range spread -> high diversity

### TestGeneticOptimizer (2 tests)
- **test_initialize_creates_engine**: Creates EvolutionEngine with correct population size
- **test_optimize_returns_best_params**: Finds parameters maximizing a+b

## Running
```bash
cd azazael && python tests/test_nsga2.py
```
