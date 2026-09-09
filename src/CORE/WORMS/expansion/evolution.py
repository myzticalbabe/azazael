# coding: utf-8
"""
ECOSYSTEM EXPANSION — Category: NEURAL ADVANCEMENT (2 worms)
EvolutionEngine — Population-based optimization beyond HYDRAMETA genetic algorithms.
GeneticOptimizer — Per-worm parameter optimization with selection/crossover/mutation.

Extends HYDRAMETA's genetic algorithm with:
- Population-based multi-generational optimization
- Tournament selection with elitism
- Adaptive crossover and mutation rates
- Fitness tracking across generations
- CurativePool-governed evolution gates
- PAMS/LocalMemoryStore integration for evolution history

Part of GOSP DoctoralThesisEngine — Tier 4: HYDRAMETA
"""

import json
import time
import random
import threading
from datetime import datetime
from typing import Any, Callable
from dataclasses import dataclass, field

# -- Module-level imports for 3.14t thread safety (Lesson #29) --
try:
    from CORE.local_memory import get_memory_store as _get_memory_store_global
    _LOCAL_MEMORY_OK = True
except ImportError:
    _LOCAL_MEMORY_OK = False
    _get_memory_store_global = None

try:
    from CORE.worm_registry import register_worm
    _REGISTRY = True
except ImportError:
    _REGISTRY = False
    def register_worm(**kw):
        return lambda cls: cls


import uuid as _uuid


@dataclass
class Genome:
    """An individual in the evolutionary population."""
    genes: dict[str, float]
    fitness: float = 0.0
    generation: int = 0
    parent_ids: list[str] = field(default_factory=list)
    # UUID4 id: unique per genome instance. The old timestamp+random scheme
    # collided within the same millisecond (all genomes in a generation),
    # which poisoned the fitness cache — a fresh child could inherit a
    # cached fitness from a different genome and never be evaluated.
    id: str = field(default_factory=lambda: f"g_{_uuid.uuid4().hex}")
    _crowding_distance: float = field(default=0.0, repr=False)  # NSGA-II crowding distance for diversity preservation


@register_worm(
    category="learning", priority=6, cooldown_seconds=120.0,
    description="Evolution engine — population-based optimization with selection, crossover, mutation, and CurativePool governance"
)
class EvolutionEngine:
    """Population-based evolutionary optimization engine.

    Extends HYDRAMETA genetic algorithms with full evolutionary loop:
    INITIALIZE -> EVALUATE -> SELECT -> CROSSOVER -> MUTATE -> REPLACE

    Features:
    - Configurable population size and generations
    - Tournament selection with elitism preservation
    - Adaptive crossover and mutation rates
    - CurativePool-governed evolution gates
    - Full evolution audit trail to LocalMemoryStore

    Usage:
        evo = EvolutionEngine()
        evo.initialize_population({"learning_rate": (0.0001, 0.1),
                                     "batch_size": (8, 256),
                                     "gamma": (0.8, 0.999)})
        for gen in range(10):
            evo.evaluate_population(lambda genome: evaluate_model(genome))
            evo.evolve()
        best = evo.get_best_genome()
    """

    VERSION = "1.0.0"

    def __init__(self, population_size: int = 50, elitism_count: int = 5,
                 crossover_rate: float = 0.7, mutation_rate: float = 0.1,
                 tournament_size: int = 3, early_stop_patience: int = 5,
                 early_stop_tolerance: float = 0.01, memory_store=None):
        self._lock = threading.Lock()
        self._memory_store = memory_store  # Injected store (None = use global, "none" = disabled)
        self.population_size = population_size
        self.elitism_count = elitism_count
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.early_stop_patience = early_stop_patience
        self.early_stop_tolerance = early_stop_tolerance

        # -- Adaptive mutation rate --
        self.base_mutation_rate = mutation_rate
        self.max_mutation_rate = min(mutation_rate * 4.0, 0.5)
        self.min_mutation_rate = mutation_rate * 0.2
        self._diversity_threshold_low = 0.05   # Below this: increase mutation
        self._diversity_threshold_high = 0.15  # Above this: decrease mutation
        self._mutation_adaptation_rate = 0.1   # How fast the rate adjusts per generation

        self._population: list[Genome] = []
        self._generation = 0
        self._gene_bounds: dict[str, tuple[float, float]] = {}
        self._generation_history: list[dict] = []
        self._best_genome: (Genome | None) = None
        self._fitness_cache: dict[str, float] = {}
        self._curative_pool = None  # Lazy CurativePool singleton

    def initialize_population(self, gene_bounds: dict[str, tuple[float, float]],
                              seed_genomes: (list[dict[str, float]] | None) = None) -> list[Genome]:
        """Initialize a random population within gene bounds.

        Args:
            gene_bounds: {gene_name: (min_val, max_val)} for each evolvable parameter
            seed_genomes: Optional pre-existing genomes to seed the population

        Returns:
            list of initialized Genome objects
        """
        with self._lock:
            self._gene_bounds = gene_bounds
            self._population = []
            self._generation = 0
            self._fitness_cache.clear()

            # Seed with provided genomes first, normalized to the current
            # gene bounds. Stale seeds from older genome shapes (e.g. a
            # 3-gene hall-of-famer after a 4th gene is added) get missing
            # genes filled with uniform draws — otherwise _crossover (which
            # iterates parent1's keys) silently drops the new dimension
            # from every child of that seed (2026-09-08 fix).
            if seed_genomes:
                for genes in seed_genomes:
                    full = dict(genes)
                    for name, (min_val, max_val) in gene_bounds.items():
                        if name not in full:
                            if isinstance(min_val, int) and isinstance(max_val, int):
                                full[name] = float(random.randint(min_val, max_val))
                            else:
                                full[name] = random.uniform(min_val, max_val)
                    genome = Genome(genes=full, generation=0)
                    self._population.append(genome)

            # Fill remainder with random genomes
            remaining = self.population_size - len(self._population)
            for _ in range(remaining):
                genes = {}
                for name, (min_val, max_val) in gene_bounds.items():
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        genes[name] = float(random.randint(min_val, max_val))
                    else:
                        genes[name] = random.uniform(min_val, max_val)
                self._population.append(Genome(genes=genes, generation=0))

            return list(self._population)

    def evaluate_population(self, fitness_fn, use_curative: bool = True,
                            workers: int = 1) -> dict[str, Any]:
        """Evaluate fitness for all genomes in the population.

        Args:
            fitness_fn: Callable(genome: Genome) -> float fitness score
            use_curative: Govern evaluation through CurativePool
            workers: Thread-pool width for fitness evals (2026-09-09).
                workers=1 preserves the exact sequential behavior.
                workers>1 requires a thread-safe fitness_fn with isolated
                RNG (no global-random traffic) — true parallelism under
                free-threading. Results are assigned back in population
                order, so stats are identical to the serial path.

        Returns:
            dict with generation stats
        """
        if use_curative:
            self._govern_evolution_gate("evaluate", {
                "generation": self._generation,
                "population_size": len(self._population),
            })

        scores = []
        eval_failures = 0
        todo = [g for g in self._population if g.id not in self._fitness_cache]
        for g in self._population:
            if g.id in self._fitness_cache:
                g.fitness = self._fitness_cache[g.id]

        def _eval_one(genome):
            try:
                return (genome.id, fitness_fn(genome), None)
            except Exception as e:  # noqa: BLE001 — surfaced, not silent
                return (genome.id, 0.0, str(e)[:160])

        if workers > 1 and todo:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=workers,
                                    thread_name_prefix="evo-eval") as pool:
                results = list(pool.map(_eval_one, todo))
        else:
            results = [_eval_one(g) for g in todo]

        by_id = {g.id: g for g in self._population}
        for genome_id, fitness, err in results:
            if err is None:
                by_id[genome_id].fitness = fitness
            else:
                by_id[genome_id].fitness = 0.0
                eval_failures += 1
                if eval_failures <= 3:
                    print('[EvolutionEngine] fitness eval failed for %s: %s' % (
                        genome_id[:12], err))
            with self._lock:
                self._fitness_cache[genome_id] = by_id[genome_id].fitness
        for genome in self._population:
            scores.append(genome.fitness)

        # Sort population by fitness
        with self._lock:
            self._population.sort(key=lambda g: -g.fitness)

        # Track best
        best = self._population[0]
        self._best_genome = best

        stats = {
            "generation": self._generation,
            "best_fitness": best.fitness,
            "avg_fitness": sum(scores) / len(scores) if scores else 0.0,
            "min_fitness": min(scores) if scores else 0.0,
            "population_size": len(self._population),
            "eval_failures": eval_failures,
            "timestamp": datetime.now().isoformat(),
        }

        with self._lock:
            self._generation_history.append(stats)

        return stats

    def evolve(self) -> dict[str, Any]:
        """Perform one generation of evolution: SELECT -> CROSSOVER -> MUTATE -> REPLACE.

        Returns:
            dict with evolution stats for this generation
        """
        with self._lock:
            if len(self._population) < 2:
                return {"error": "Population too small", "generation": self._generation}

            current_pop = list(self._population)
            gene_bounds = dict(self._gene_bounds)

        # -- Elitism: keep best N genomes unchanged --
        new_population = current_pop[:self.elitism_count]

        # -- Adapt mutation rate before selection --
        self._adapt_mutation_rate(current_pop, gene_bounds)

        # -- Selection + Crossover + Mutation --
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_select(current_pop)
            parent2 = self._tournament_select(current_pop)

            # Crossover
            if random.random() < self.crossover_rate:
                child_genes = self._crossover(parent1.genes, parent2.genes)
            else:
                child_genes = dict(parent1.genes)

            # Mutation
            child_genes = self._mutate(child_genes, gene_bounds)

            child = Genome(
                genes=child_genes,
                generation=self._generation + 1,
                parent_ids=[parent1.id, parent2.id],
            )
            new_population.append(child)

        # Replace old population
        with self._lock:
            self._population = new_population[:self.population_size]
            self._generation += 1

        # Persist generation
        self._persist_generation()

        return {
            "generation": self._generation,
            "population_size": len(self._population),
            "elites_preserved": self.elitism_count,
            "timestamp": datetime.now().isoformat(),
        }

    def _tournament_select(self, population: list[Genome]) -> Genome:
        """Tournament selection: pick N random, return fittest."""
        tournament = random.sample(
            population,
            min(self.tournament_size, len(population))
        )
        return max(tournament, key=lambda g: g.fitness)

    def _crossover(self, genes1: dict[str, float], genes2: dict[str, float]) -> dict[str, float]:
        """Uniform crossover: randomly pick each gene from either parent."""
        child = {}
        for key in genes1:
            child[key] = genes1[key] if random.random() < 0.5 else genes2.get(key, genes1[key])
        return child

    def _mutate(self, genes: dict[str, float],
                gene_bounds: dict[str, tuple[float, float]]) -> dict[str, float]:
        """Apply random mutation to genes within bounds."""
        for key, (min_val, max_val) in gene_bounds.items():
            if random.random() < self.mutation_rate:
                perturbation = random.uniform(-0.1, 0.1) * (max_val - min_val)
                genes[key] = max(min_val, min(max_val, genes.get(key, (min_val + max_val) / 2) + perturbation))
        return genes

    def _govern_evolution_gate(self, phase: str, context: dict) -> None:
        """Govern evolution operations through CurativePool — double-checked locking for 3.14t."""
        try:
            if self._curative_pool is None:
                with self._lock:
                    if self._curative_pool is None:
                        from META.MetaWormSpawner import CurativePool
                        self._curative_pool = CurativePool()
            result = self._curative_pool.evaluate_action(
                {"context": f"evolution_{phase}", "params": context},
                {"action_type": "execute", "output_size": 100, "feature": f"evolution_{phase}"},
                [{"role": "user", "content": f"run evolution phase: {phase}"}],
                [{"id": "evo_analyst", "archetype": "The Analyst"}],
            )
            if result["decision"] == "blocked":
                print(f"[EvolutionEngine] CurativePool blocked {phase}: {result['block_reasons']}")
        except ImportError:
            pass

    def _get_store(self):
        """Resolve memory store: injected -> global -> None.

        Thread-safe under 3.14t free-threading — all imports at module level.
        Uses sys.modules lookup pattern from Lesson #29 to avoid import deadlocks.
        """
        if self._memory_store == "none":
            return None
        if self._memory_store is not None:
            return self._memory_store
        if _LOCAL_MEMORY_OK and _get_memory_store_global is not None:
            try:
                return _get_memory_store_global()
            except Exception:
                return None
        return None

    def _persist_generation(self) -> None:
        """Persist generation stats to LocalMemoryStore."""
        store = self._get_store()
        if store is None:
            return
        try:
            store.record_event(
                source="EvolutionEngine",
                event_type="generation_complete",
                data={
                    "generation": self._generation,
                    "best_fitness": self._best_genome.fitness if self._best_genome else 0.0,
                    "population_size": len(self._population),
                    "timestamp": datetime.now().isoformat(),
                },
                severity="info",
                tags=["evolution", f"gen_{self._generation}"],
            )
        except Exception:
            pass

    # -- Adaptive Mutation Rate --------------------------------------

    def _compute_population_diversity(self, population: (list[Genome] | None) = None,
                                      gene_bounds: (dict[str, tuple[float, float]] | None) = None) -> float:
        """Compute normalized gene diversity across the population.

        Returns a float 0.0–1.0 where higher = more diverse.
        Uses coefficient of variation (stddev / mean) averaged across genes.

        Args:
            population: Population to analyze (defaults to self._population)
            gene_bounds: Gene bounds to normalize by (defaults to self._gene_bounds)
        """
        pop = population if population is not None else self._population
        bounds = gene_bounds if gene_bounds is not None else self._gene_bounds

        if len(pop) < 2 or not bounds:
            return 0.0

        diversity_scores = []
        for gene_name, (min_val, max_val) in bounds.items():
            values = [g.genes.get(gene_name, 0.0) for g in pop]
            mean_val = sum(values) / len(values)
            if mean_val == 0:
                diversity_scores.append(0.0)
                continue
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            stddev = variance ** 0.5
            # Normalize by gene range so different-scale genes are comparable
            gene_range = max_val - min_val
            if gene_range > 0:
                diversity_scores.append(min(stddev / gene_range, 1.0))
            else:
                diversity_scores.append(0.0)

        return sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0.0

    def _adapt_mutation_rate(self, population: (list[Genome] | None) = None,
                             gene_bounds: (dict[str, tuple[float, float]] | None) = None) -> float:
        """Dynamically adjust mutation rate based on population diversity.

        - Low diversity -> increase mutation (prevent premature convergence)
        - High diversity -> decrease mutation (exploit good solutions)

        Args:
            population: Population snapshot (from evolve()'s copy)
            gene_bounds: Gene bounds snapshot (from evolve()'s copy)

        Returns the new mutation rate.
        """
        diversity = self._compute_population_diversity(population, gene_bounds)

        if diversity < self._diversity_threshold_low:
            # Premature convergence risk — boost mutation
            target = self.mutation_rate * (1.0 + self._mutation_adaptation_rate * 3.0)
            new_rate = min(target, self.max_mutation_rate)
        elif diversity > self._diversity_threshold_high:
            # Healthy diversity — decay toward base rate
            target = self.mutation_rate * (1.0 - self._mutation_adaptation_rate)
            new_rate = max(target, self.base_mutation_rate)
        else:
            # Moderate diversity — slight decay toward base
            target = self.mutation_rate + (self.base_mutation_rate - self.mutation_rate) * 0.2
            new_rate = max(target, self.min_mutation_rate)

        self.mutation_rate = round(new_rate, 5)
        return self.mutation_rate

    # -- Checkpoint / Restore ----------------------------------------

    def save_checkpoint(self, label: str = "") -> dict[str, Any]:
        """Serialize the full evolutionary state and persist to LocalMemoryStore.

        Saves: population, generation, gene bounds, history, best genome, config.

        Args:
            label: Optional human-readable label for the checkpoint

        Returns:
            dict with checkpoint metadata
        """
        with self._lock:
            checkpoint = {
                "version": self.VERSION,
                "label": label or f"gen_{self._generation}",
                "generation": self._generation,
                "population_size": self.population_size,
                "gene_bounds": {k: list(v) for k, v in self._gene_bounds.items()},
                "crossover_rate": self.crossover_rate,
                "mutation_rate": self.mutation_rate,
                "tournament_size": self.tournament_size,
                "population": [
                    {
                        "id": g.id,
                        "genes": dict(g.genes),
                        "fitness": g.fitness,
                        "generation": g.generation,
                        "parent_ids": list(g.parent_ids),
                    }
                    for g in self._population
                ],
                "generation_history": list(self._generation_history[-50:]),
                "best_genome": (
                    {
                        "id": self._best_genome.id,
                        "genes": dict(self._best_genome.genes),
                        "fitness": self._best_genome.fitness,
                        "generation": self._best_genome.generation,
                    }
                    if self._best_genome else None
                ),
                "saved_at": datetime.now().isoformat(),
                "free_threaded": True,
            }

        # Persist to LocalMemoryStore
        store = self._get_store()
        if store is not None:
            try:
                store.record_event(
                    source="EvolutionEngine",
                    event_type="checkpoint_saved",
                    data=checkpoint,
                    severity="info",
                    tags=["evolution", "checkpoint", f"gen_{self._generation}"],
                )
            except Exception:
                pass

        return {
            "checkpoint_label": checkpoint["label"],
            "generation": checkpoint["generation"],
            "population_count": len(checkpoint["population"]),
            "best_fitness": checkpoint["best_genome"]["fitness"] if checkpoint["best_genome"] else 0.0,
            "saved_at": checkpoint["saved_at"],
        }

    def load_checkpoint(self, label: (str | None) = None) -> bool:
        """Restore evolutionary state from the most recent checkpoint in LocalMemoryStore.

        Args:
            label: Optional label filter to load a specific checkpoint

        Returns:
            True if checkpoint was loaded, False otherwise
        """
        store = self._get_store()
        if store is None:
            return False
        try:
            events = store.search_memories(
                "checkpoint_saved", source="EvolutionEngine", limit=10
            )
            if not events:
                return False

            # Find matching checkpoint
            checkpoint = None
            for ev in reversed(events):
                data = ev.get("data", {})
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except (json.JSONDecodeError, TypeError):
                        continue
                if not isinstance(data, dict) or "population" not in data:
                    continue
                if label and data.get("label") != label:
                    continue
                checkpoint = data
                break

            if checkpoint is None:
                return False

            # Restore state
            with self._lock:
                self._generation = checkpoint.get("generation", 0)
                self.population_size = checkpoint.get("population_size", self.population_size)
                self._gene_bounds = {
                    k: tuple(v) for k, v in checkpoint.get("gene_bounds", {}).items()
                }
                self.crossover_rate = checkpoint.get("crossover_rate", self.crossover_rate)
                self.mutation_rate = checkpoint.get("mutation_rate", self.mutation_rate)
                self.tournament_size = checkpoint.get("tournament_size", self.tournament_size)
                self._generation_history = checkpoint.get("generation_history", [])
                self._fitness_cache.clear()

                # Rebuild population
                self._population = []
                for gdata in checkpoint.get("population", []):
                    genome = Genome(
                        genes=gdata.get("genes", {}),
                        fitness=gdata.get("fitness", 0.0),
                        generation=gdata.get("generation", 0),
                        parent_ids=gdata.get("parent_ids", []),
                        id=gdata.get("id") or f"g_{_uuid.uuid4().hex}",
                    )
                    self._population.append(genome)
                    self._fitness_cache[genome.id] = genome.fitness

                # Restore best genome
                best_data = checkpoint.get("best_genome")
                if best_data:
                    self._best_genome = Genome(
                        genes=best_data.get("genes", {}),
                        fitness=best_data.get("fitness", 0.0),
                        generation=best_data.get("generation", 0),
                        id=best_data.get("id", ""),
                    )
                else:
                    self._best_genome = None

            return True
        except Exception:
            return False

    def has_converged(self) -> bool:
        """Check if the population has converged (no meaningful improvement).

        Returns True if best_fitness hasn't improved by more than
        early_stop_tolerance over the last early_stop_patience generations.
        """
        if self._generation < self.early_stop_patience:
            return False

        recent_bests = [
            h.get("best_fitness", 0.0)
            for h in self._generation_history[-self.early_stop_patience:]
        ]
        if not recent_bests:
            return False

        first_best = recent_bests[0]
        last_best = recent_bests[-1]

        if first_best <= 0:
            return False

        improvement = (last_best - first_best) / abs(first_best)
        return improvement < self.early_stop_tolerance

    # -- Multi-Objective Optimization (Pareto-front) -----------------

    def _non_dominated_sort(self, population: list[Genome],
                            objective_fns: list[Callable]) -> list[list[Genome]]:
        """NSGA-II non-dominated sorting of population into Pareto fronts.

        Each objective_fn should return a float where LOWER is better (minimization).
        Fronts[0] = Pareto-optimal individuals (not dominated by any other).

        Args:
            population: Genomes to sort
            objective_fns: list of fitness functions, each returning float

        Returns:
            list of fronts (each front is a list of genomes)
        """
        n = len(population)
        domination_counts = [0] * n
        dominated_by = [[] for _ in range(n)]
        objectives = []

        for genome in population:
            obj_values = [fn(genome) for fn in objective_fns]
            objectives.append(obj_values)

        # Build domination graph
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # i dominates j if all objectives of i are <= j and at least one is <
                i_dominates_j = all(
                    objectives[i][k] <= objectives[j][k] for k in range(len(objective_fns))
                ) and any(
                    objectives[i][k] < objectives[j][k] for k in range(len(objective_fns))
                )
                if i_dominates_j:
                    dominated_by[i].append(j)
                    domination_counts[j] += 1

        # Build fronts
        fronts = []
        current_front = [i for i, count in enumerate(domination_counts) if count == 0]

        while current_front:
            fronts.append([population[i] for i in current_front])
            next_front = []
            for i in current_front:
                for j in dominated_by[i]:
                    domination_counts[j] -= 1
                    if domination_counts[j] == 0:
                        next_front.append(j)
            current_front = next_front

        return fronts

    def _compute_crowding_distance(self, front: list[Genome],
                                   objective_fns: list[Callable]) -> list[float]:
        """Compute crowding distance for diversity preservation.

        Higher crowding distance = more isolated = higher diversity value.
        Used to select among individuals in the same Pareto front.

        Args:
            front: Non-dominated individuals in a single front
            objective_fns: Objective functions (lower is better)

        Returns:
            list of crowding distances aligned with front
        """
        m = len(front)
        if m <= 2:
            return [float("inf")] * m

        distances = [0.0] * m
        n_objectives = len(objective_fns)

        for obj_idx in range(n_objectives):
            # Sort by this objective
            obj_values = [(i, objective_fns[obj_idx](front[i])) for i in range(m)]
            obj_values.sort(key=lambda x: x[1])

            f_min = obj_values[0][1]
            f_max = obj_values[-1][1]
            f_range = f_max - f_min if f_max != f_min else 1.0

            # Boundary points get infinite distance
            distances[obj_values[0][0]] = float("inf")
            distances[obj_values[-1][0]] = float("inf")

            # Interior points
            for k in range(1, m - 1):
                idx = obj_values[k][0]
                prev_val = obj_values[k - 1][1]
                next_val = obj_values[k + 1][1]
                distances[idx] += (next_val - prev_val) / f_range

        return distances

    def optimize_multi_objective(self, objective_fns: list[Callable],
                                 generations: int = 20,
                                 use_curative: bool = True) -> dict[str, Any]:
        """Run multi-objective evolutionary optimization (NSGA-II style).

        Optimizes for multiple competing objectives simultaneously.
        Returns the Pareto front of non-dominated solutions.

        Each objective_fn should map Genome -> float where LOWER is better.

        Args:
            objective_fns: list of objective functions to minimize
            generations: Number of generations to evolve
            use_curative: Govern through CurativePool

        Returns:
            dict with pareto_front, generation history, and convergence info
        """
        if len(objective_fns) < 2:
            return {"error": "Need at least 2 objective functions for multi-objective optimization"}

        if use_curative:
            self._govern_evolution_gate("multi_objective", {
                "generations": generations,
                "objectives": len(objective_fns),
            })

        history = []
        for gen in range(generations):
            # Non-dominated sort
            fronts = self._non_dominated_sort(self._population, objective_fns)

            # Compute crowding distance for each front
            for front in fronts:
                distances = self._compute_crowding_distance(front, objective_fns)
                for genome, dist in zip(front, distances):
                    genome._crowding_distance = dist

            # Build new population using NSGA-II selection
            with self._lock:
                new_population = []
                for front in fronts:
                    if len(new_population) + len(front) <= self.population_size:
                        new_population.extend(front)
                    else:
                        # Fill remaining slots from best of this front
                        remaining = self.population_size - len(new_population)
                        sorted_front = sorted(
                            front,
                            key=lambda g: getattr(g, "_crowding_distance", 0.0),
                            reverse=True,
                        )
                        new_population.extend(sorted_front[:remaining])
                        break

                # Elitism: ensure best from each objective survives
                elite_slots = set()
                for obj_idx, obj_fn in enumerate(objective_fns):
                    if self._population:
                        best_in_obj = min(self._population, key=obj_fn)
                        if best_in_obj not in new_population:
                            # Place in a unique slot, working backwards from end
                            slot = -(obj_idx + 1)
                            if slot not in elite_slots:
                                new_population[slot] = best_in_obj
                                elite_slots.add(slot)

                # Crossover and mutation on survivors
                offspring = []
                while len(new_population) + len(offspring) < self.population_size * 2:
                    p1 = self._tournament_select(new_population)
                    p2 = self._tournament_select(new_population)
                    if random.random() < self.crossover_rate:
                        child_genes = self._crossover(p1.genes, p2.genes)
                    else:
                        child_genes = dict(p1.genes)
                    child_genes = self._mutate(child_genes, self._gene_bounds)
                    offspring.append(Genome(
                        genes=child_genes,
                        generation=self._generation + 1,
                        parent_ids=[p1.id, p2.id],
                    ))

                # Combine and select next generation via non-dominated sort
                combined = new_population + offspring
                fronts_combined = self._non_dominated_sort(combined, objective_fns)
                next_pop = []
                for front in fronts_combined:
                    if len(next_pop) + len(front) <= self.population_size:
                        next_pop.extend(front)
                    else:
                        remaining = self.population_size - len(next_pop)
                        distances = self._compute_crowding_distance(front, objective_fns)
                        for g, d in zip(front, distances):
                            g._crowding_distance = d
                        sorted_front = sorted(
                            front,
                            key=lambda g: getattr(g, "_crowding_distance", 0.0),
                            reverse=True,
                        )
                        next_pop.extend(sorted_front[:remaining])
                        break

                self._population = next_pop[:self.population_size]
                self._generation += 1

            # Track generation stats
            gen_stats = {
                "generation": self._generation,
                "pareto_front_size": len(fronts[0]) if fronts else 0,
                "total_fronts": len(fronts),
                "population_size": len(self._population),
                "timestamp": datetime.now().isoformat(),
            }
            with self._lock:
                self._generation_history.append(gen_stats)

            # Early stopping: if Pareto front size hasn't changed in patience gens
            if gen >= self.early_stop_patience:
                recent_sizes = [
                    h.get("pareto_front_size", 0)
                    for h in history[-self.early_stop_patience:]
                ]
                if len(set(recent_sizes)) == 1:
                    break

            # Adapt mutation rate using current population snapshot
            with self._lock:
                pop_snapshot = list(self._population)
                bounds_snapshot = dict(self._gene_bounds)
            self._adapt_mutation_rate(pop_snapshot, bounds_snapshot)

        # Extract final Pareto front
        final_fronts = self._non_dominated_sort(self._population, objective_fns)
        pareto_front = final_fronts[0] if final_fronts else []

        return {
            "pareto_front": [
                {
                    "id": g.id,
                    "genes": g.genes,
                    "objectives": [round(fn(g), 6) for fn in objective_fns],
                    "generation": g.generation,
                }
                for g in pareto_front
            ],
            "pareto_front_size": len(pareto_front),
            "generations": self._generation,
            "history": history,
            "timestamp": datetime.now().isoformat(),
        }

    def get_best_genome(self) -> (Genome | None):
        """Get the fittest genome across all generations."""
        return self._best_genome

    def get_generation_history(self, limit: int = 20) -> list[dict]:
        """Get recent generation fitness history."""
        with self._lock:
            return self._generation_history[-limit:]

    def execute(self) -> dict[str, Any]:
        """Standard worm execute — returns current evolution status and auto-saves checkpoint."""
        with self._lock:
            status = {
                "version": self.VERSION,
                "generation": self._generation,
                "population_size": len(self._population),
                "best_fitness": self._best_genome.fitness if self._best_genome else 0.0,
                "best_genes": self._best_genome.genes if self._best_genome else {},
                "gene_bounds": self._gene_bounds,
                "generations_history": len(self._generation_history),
            }
        # Auto-save checkpoint for session-to-session persistence
        if self._population:
            self.save_checkpoint()
        return status


@register_worm(
    category="learning", priority=5, cooldown_seconds=180.0,
    description="Genetic optimizer — per-worm parameter optimization using genetic algorithms with fitness tracking"
)
class GeneticOptimizer:
    """Per-worm genetic parameter optimizer.

    Optimizes execution parameters for individual worm types using
    genetic algorithms. Tracks fitness across generations and
    automatically selects optimal parameter configurations.

    Usage:
        opt = GeneticOptimizer()
        opt.initialize("SystemZ", {"scan_depth": (1, 10), "timeout_ms": (100, 5000)})
        best_params = opt.optimize(generations=10)
    """

    VERSION = "1.0.0"

    def __init__(self):
        self._lock = threading.Lock()
        self._engines: dict[str, EvolutionEngine] = {}
        self._optimization_history: dict[str, list[dict]] = {}

    def initialize(self, worm_type: str, param_bounds: dict[str, tuple[float, float]],
                   population_size: int = 30) -> EvolutionEngine:
        """Initialize an evolution engine for a specific worm type."""
        engine = EvolutionEngine(population_size=population_size)
        engine.initialize_population(param_bounds)
        with self._lock:
            self._engines[worm_type] = engine
            self._optimization_history[worm_type] = []
        return engine

    def optimize(self, worm_type: str, generations: int = 10,
                 fitness_fn=None) -> dict[str, Any]:
        """Run evolutionary optimization for a worm type.

        Args:
            worm_type: Worm type to optimize
            generations: Number of generations to evolve
            fitness_fn: Optional custom fitness function

        Returns:
            dict with best parameters and optimization stats
        """
        engine = self._engines.get(worm_type)
        if not engine:
            return {"error": f"No engine initialized for {worm_type}"}

        # Fail loud without an explicit fitness (2026-09-09 fix): the old
        # placeholder (mean of gene values) silently "optimized" worms
        # toward MAXIMUM parameter values — the opposite of tuning.
        if fitness_fn is None:
            return {"error": "fitness_fn is required (no safe default: higher "
                             "is not better for timeouts/scales/depths)"}

        history = []
        for gen in range(generations):
            stats = engine.evaluate_population(fitness_fn)
            engine.evolve()
            history.append(stats)

            # Early stopping check
            if engine.has_converged():
                break

        best = engine.get_best_genome()

        result = {
            "worm_type": worm_type,
            "generations": generations,
            "best_parameters": best.genes if best else {},
            "best_fitness": best.fitness if best else 0.0,
            "history": history,
            "timestamp": datetime.now().isoformat(),
        }

        with self._lock:
            self._optimization_history[worm_type].append(result)

        # Persist using module-level import (3.14t safe per Lesson #29)
        store = None
        if _LOCAL_MEMORY_OK and _get_memory_store_global:
            try:
                store = _get_memory_store_global()
            except Exception:
                pass
        if store is not None:
            store.record_event(
                source="GeneticOptimizer",
                event_type="optimization_complete",
                data=result,
                severity="info",
                tags=["genetic", "optimization", worm_type],
            )

        return result

    def optimize_multi(self, worm_type: str, objective_fns: list[Callable],
                       generations: int = 20) -> dict[str, Any]:
        """Run multi-objective evolutionary optimization for a worm type.

        Args:
            worm_type: Worm type to optimize
            objective_fns: list of objective functions (each Genome -> float, lower=better)
            generations: Number of generations

        Returns:
            dict with Pareto front and optimization stats
        """
        engine = self._engines.get(worm_type)
        if not engine:
            return {"error": f"No engine initialized for {worm_type}"}

        if len(objective_fns) < 2:
            return {"error": "Need at least 2 objectives for multi-objective optimization"}

        result = engine.optimize_multi_objective(
            objective_fns, generations=generations
        )

        with self._lock:
            self._optimization_history[worm_type].append({
                "type": "multi_objective",
                "pareto_front_size": result.get("pareto_front_size", 0),
                "generations": result.get("generations", 0),
                "timestamp": datetime.now().isoformat(),
            })

        return result

    def execute(self) -> dict[str, Any]:
        """Standard worm execute — returns optimization status."""
        with self._lock:
            return {
                "version": self.VERSION,
                "optimized_worms": list(self._engines.keys()),
                "total_optimizations": sum(len(h) for h in self._optimization_history.values()),
            }
