---
name: azazael-evolutionary-optimization
description: NSGA-II and genetic algorithms — EvolutionEngine Pareto-front optimization and per-worm parameter tuning.
metadata:
  category: algorithm
  project: azazael
  priority: high
  auto_load: false
---

# Azazael Evolutionary Optimization — NSGA-II + Genetic Algorithms

## Overview
Azazael provides two evolutionary optimization engines:
- **EvolutionEngine** — Population-based NSGA-II optimization with Pareto front
- **GeneticOptimizer** — Per-worm parameter optimization using genetic algorithms

## EvolutionEngine (v1.0.0)

### Core Loop
```
INITIALIZE -> EVALUATE -> SELECT -> CROSSOVER -> MUTATE -> REPLACE
```

### Features
- **Tournament selection** with elitism preservation
- **Uniform crossover** (random gene from each parent)
- **Adaptive mutation rate**: adjusts based on population diversity
  - Low diversity → boost mutation (prevent premature convergence)
  - High diversity → decay toward base rate
- **Early stopping**: converges when best fitness plateaus
- **CurativePool governance**: evolution gates for safety
- **Checkpoint save/load**: full state serialization to LocalMemoryStore

### Multi-Objective (NSGA-II)
- `optimize_multi_objective()` supports 2+ competing objectives
- Non-dominated sorting into Pareto fronts
- Crowding distance for diversity preservation within fronts
- Elitism: best of each objective survives
- Adaptive mutation rate per generation

### Crowding Distance
Computed per front: boundary points get infinite distance, interior points get
normalized difference of neighboring objective values.
```
distance[i] = sum over objectives of (f[i+1] - f[i-1]) / (f_max - f_min)
```

## GeneticOptimizer (v1.0.0)
- Wraps EvolutionEngine per worm type
- `initialize(worm_type, param_bounds)` -> Engine
- `optimize(worm_type, generations)` -> Best params
- `optimize_multi(worm_type, objective_fns)` -> Pareto front

## Key Files
| File | Purpose |
|------|---------|
| `CORE/WORMS/expansion/evolution.py` | EvolutionEngine, GeneticOptimizer, Genome dataclass |
