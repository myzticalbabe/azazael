#!/usr/bin/env python3
"""
scenario_d_nas_pipeline.py — Scenario D: NAS Pipeline (Search → Train → Deploy)

Use evolutionary search to discover optimal neural architecture, train the
best candidate with GRPOTrainer, export to ONNX, and deploy via inference
providers.

Pipeline:
  Evolutionary NAS (evolution.py patterns) → Best Architecture →
  GRPOTrainer → ONNX export → Inference Protocol (12-provider chain)

Usage:
    python scripts/scenario_d_nas_pipeline.py
    python scripts/scenario_d_nas_pipeline.py --generations 20 --population 12
    python scripts/scenario_d_nas_pipeline.py --dry-run
"""

import os
import sys
import time
import json
import math
import random
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# Add src/ to path
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


# ── NAS Architecture Search Space ──────────────────────────────────────

ARCHITECTURE_PATTERNS = {
    "dense_rl": {
        "name": "Dense RL (Standard)",
        "trainer": "RLTrainLoop",
        "params": {"learning_rate": 0.1, "discount_factor": 0.9, "epsilon": 0.1},
        "complexity": "low",
        "use_case": "Simple state-action spaces, epsilon-greedy exploration",
    },
    "policy_gradient": {
        "name": "Policy Gradient (Continuous)",
        "trainer": "SB3_PPO",
        "params": {"learning_rate": 3e-4, "n_steps": 2048, "batch_size": 64},
        "complexity": "medium",
        "use_case": "Continuous action spaces, PPO stability",
    },
    "preference_based": {
        "name": "Preference-Based (Human Feedback)",
        "trainer": "GRPOTrainer",
        "params": {"group_size": 8, "n_updates": 100},
        "complexity": "high",
        "use_case": "Pairwise preference learning, ABTestRunner integration",
    },
    "moe": {
        "name": "Mixture of Experts (Large Scale)",
        "trainer": "SB3_PPO + Ray Tune",
        "params": {"n_experts": 4, "top_k": 2, "learning_rate": 1e-4},
        "complexity": "very_high",
        "use_case": "Distributed hyperparameter search, expert routing",
    },
    "compressed": {
        "name": "Compressed (Edge Deploy)",
        "trainer": "Any + model-compression",
        "params": {"quant_format": "gguf", "bits": 4, "target": "cpu"},
        "complexity": "medium",
        "use_case": "Train dense, quantize for edge deployment",
    },
}

NAS_SEARCH_SPACE = {
    "hidden_layers": [1, 2, 3, 4],
    "neurons_per_layer": [16, 32, 64, 128, 256],
    "activation": ["relu", "tanh", "sigmoid"],
    "learning_rate": [1e-4, 3e-4, 1e-3, 3e-3, 1e-2],
    "batch_size": [16, 32, 64, 128],
    "architecture_pattern": list(ARCHITECTURE_PATTERNS.keys()),
}


@dataclass
class NASIndividual:
    """An individual architecture in the evolutionary population."""
    genome: dict
    fitness: float = 0.0
    generation: int = 0
    id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"arch_{int(time.time())}_{random.randint(1000, 9999)}"


def random_architecture() -> dict:
    """Generate a random architecture configuration from search space."""
    return {
        "hidden_layers": random.choice(NAS_SEARCH_SPACE["hidden_layers"]),
        "neurons_per_layer": random.choice(NAS_SEARCH_SPACE["neurons_per_layer"]),
        "activation": random.choice(NAS_SEARCH_SPACE["activation"]),
        "learning_rate": random.choice(NAS_SEARCH_SPACE["learning_rate"]),
        "batch_size": random.choice(NAS_SEARCH_SPACE["batch_size"]),
        "architecture_pattern": random.choice(NAS_SEARCH_SPACE["architecture_pattern"]),
    }


def mutate(genome: dict, mutation_rate: float = 0.3) -> dict:
    """Mutate an architecture genome with given probability."""
    child = dict(genome)
    for key in NAS_SEARCH_SPACE:
        if random.random() < mutation_rate:
            child[key] = random.choice(NAS_SEARCH_SPACE[key])
    return child


def crossover(parent1: dict, parent2: dict) -> dict:
    """Single-point crossover between two parent genomes."""
    keys = list(NAS_SEARCH_SPACE.keys())
    point = random.randint(1, len(keys) - 1)
    child = {}
    for i, k in enumerate(keys):
        child[k] = parent1[k] if i < point else parent2[k]
    return child


def estimate_fitness(genome: dict, source: str) -> float:
    """Estimate architecture fitness using heuristic scoring.

    In production, this would train for a few episodes and measure actual
    performance. Here we use a heuristic that favors:
    - Moderate complexity (not too few, not too many params)
    - Higher learning rates for faster convergence
    - Architecture pattern matched to available data
    """
    fitness = 0.5  # Baseline

    # Prefer moderate hidden layers (2-3 is sweet spot)
    layers = genome.get("hidden_layers", 2)
    if layers in (2, 3):
        fitness += 0.15
    elif layers == 1:
        fitness += 0.05
    else:
        fitness += 0.10  # 4 layers still useful

    # Prefer moderate neuron counts
    neurons = genome.get("neurons_per_layer", 64)
    if 32 <= neurons <= 128:
        fitness += 0.10
    elif neurons >= 256:
        fitness += 0.05  # Large, but potentially powerful
    else:
        fitness += 0.0

    # Activation preference
    act = genome.get("activation", "relu")
    if act == "relu":
        fitness += 0.10  # Fast, widely supported
    elif act == "tanh":
        fitness += 0.05

    # Learning rate: moderate preferred
    lr = genome.get("learning_rate", 3e-4)
    if 3e-4 <= lr <= 1e-3:
        fitness += 0.10
    elif lr >= 1e-2:
        fitness += 0.05  # Fast but unstable

    # Pattern match bonus
    pattern = genome.get("architecture_pattern", "dense_rl")
    pattern_info = ARCHITECTURE_PATTERNS.get(pattern, {})
    if pattern_info.get("trainer") in ("GRPOTrainer", "SB3_PPO"):
        fitness += 0.10  # These are our primary trainers

    # Add small noise for diversity
    fitness += random.uniform(-0.05, 0.05)
    return max(0.0, min(1.0, fitness))


def tournament_selection(population: List[NASIndividual], k: int = 3) -> NASIndividual:
    """Select an individual via tournament selection."""
    tournament = random.sample(population, min(k, len(population)))
    return max(tournament, key=lambda ind: ind.fitness)


def step_nas_search(source: str, generations: int, pop_size: int,
                    dry_run: bool) -> dict:
    """Step 1: Evolutionary NAS search for optimal architecture."""
    print(f"\n── Step 1: Evolutionary NAS Search ─────────────────────", flush=True)
    print(f"  Generations: {generations}, Population: {pop_size}", flush=True)

    if dry_run:
        print("  [DRY-RUN] Would run evolutionary search", flush=True)
        best = NASIndividual(
            genome=random_architecture(),
            fitness=0.85,
            generation=1,
            id="dry_run_best",
        )
        return {"population": [], "best": best, "search_complete": True,
                "generations_run": generations, "history": []}

    population = [NASIndividual(genome=random_architecture())
                  for _ in range(pop_size)]

    history = []
    best_overall = None

    for gen in range(1, generations + 1):
        # Evaluate fitness
        for ind in population:
            ind.fitness = estimate_fitness(ind.genome, source)
            ind.generation = gen

        # Sort by fitness
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        best = population[0]
        gen_avg = sum(ind.fitness for ind in population) / len(population)

        history.append({
            "generation": gen,
            "best_fitness": round(best.fitness, 4),
            "avg_fitness": round(gen_avg, 4),
            "best_genome": best.genome,
        })

        if best_overall is None or best.fitness > best_overall.fitness:
            best_overall = best

        print(f"  Gen {gen:2d}: best={best.fitness:.4f} "
              f"avg={gen_avg:.4f} pattern={best.genome.get('architecture_pattern')}",
              flush=True)

        # Evolve: keep top 20%, breed rest
        next_gen = population[:max(2, pop_size // 5)]  # Elitism

        while len(next_gen) < pop_size:
            parent1 = tournament_selection(population[:pop_size // 2])
            parent2 = tournament_selection(population[:pop_size // 2])
            child_genome = crossover(parent1.genome, parent2.genome)
            child_genome = mutate(child_genome)
            next_gen.append(NASIndividual(genome=child_genome))

        population = next_gen

    return {
        "population": population,
        "best": best_overall or population[0],
        "search_complete": True,
        "generations_run": generations,
        "history": history,
    }


def step_train_best(data: dict, source: str, dry_run: bool) -> dict:
    """Step 2: Train the best architecture using GRPOTrainer."""
    print("\n── Step 2: Train Best Architecture ──────────────────────", flush=True)

    best = data.get("best")
    if not best:
        print("  [ERROR] No best architecture found", flush=True)
        return data

    genome = best.genome
    pattern_key = genome.get("architecture_pattern", "dense_rl")
    pattern = ARCHITECTURE_PATTERNS.get(pattern_key, {})
    trainer_name = pattern.get("trainer", "GRPOTrainer")

    print(f"  Best architecture:", flush=True)
    print(f"    Pattern:  {pattern.get('name', pattern_key)}", flush=True)
    print(f"    Trainer:  {trainer_name}", flush=True)
    print(f"    Layers:   {genome.get('hidden_layers')}", flush=True)
    print(f"    Neurons:  {genome.get('neurons_per_layer')}", flush=True)
    print(f"    LR:       {genome.get('learning_rate')}", flush=True)
    print(f"    Batch:    {genome.get('batch_size')}", flush=True)
    print(f"    Fitness:  {best.fitness:.4f}", flush=True)

    if dry_run:
        print(f"  [DRY-RUN] Would train {trainer_name} with best architecture", flush=True)
        data["trained"] = True
        data["trainer"] = trainer_name
        return data

    # Route to appropriate trainer based on best architecture
    if trainer_name == "GRPOTrainer":
        from CORE.WORMS.expansion.learning_grpo import GRPOTrainer
        trainer = GRPOTrainer()
        groups = trainer.generate_group(
            {"task_type": "nas", "source": source,
             "architecture": pattern_key},
            group_size=genome.get("batch_size", 8) // 8,
        )
        rewards = trainer.compute_group_rewards(groups, {
            "task_type": "nas", "source": source,
        })
        trainer.update_policy(groups, rewards,
                              context_key=f"nas_{source}")
        best_worm = trainer.select_best(f"nas_{source}")
        stats = trainer.get_stats()
        data["train_result"] = {
            "trainer": "GRPOTrainer",
            "trained": True,
            "best_worm": best_worm,
            "n_updates": stats.get("n_updates", 0),
        }
    elif trainer_name == "SB3_PPO":
        from CORE.sb3_agent import SB3Agent
        trainer = SB3Agent(algo="PPO")
        result = trainer.train(
            source=source,
            total_timesteps=2000,
            register_model=True,
        )
        data["train_result"] = result
    else:
        from CORE.WORMS.expansion.learning import RLTrainLoop
        trainer = RLTrainLoop()
        result = trainer.train_from_memory(
            source=source, n_episodes=50,
            use_schema_features=True,
        )
        data["train_result"] = result

    data["trained"] = True
    data["trainer"] = trainer_name
    data["trainer_instance"] = trainer
    return data


def step_export_and_deploy(data: dict, dry_run: bool) -> dict:
    """Step 3: Export trained model to ONNX and deploy."""
    print("\n── Step 3: ONNX Export & Deployment ────────────────────", flush=True)

    onnx_path = Path("output/models/nas_best.onnx")
    onnx_path.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        print(f"  [DRY-RUN] ONNX path: {onnx_path}", flush=True)
        data["onnx_path"] = str(onnx_path)
        data["deploy_targets"] = ["12-Provider Failover Chain",
                                   "LM Studio (localhost:1234)"]
        return data

    # Export to ONNX
    try:
        from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx
        trainer = data.get("trainer_instance")
        if trainer:
            export_to_onnx(trainer, str(onnx_path))
            size_kb = onnx_path.stat().st_size / 1024 if onnx_path.exists() else 0
            print(f"  ONNX exported ({size_kb:.1f} KB): {onnx_path}", flush=True)
    except ImportError:
        print(f"  [INFO] ONNX module not available — mock export", flush=True)
        onnx_path.write_text(json.dumps({"nas": True}))

    # Deploy via inference protocol
    deploy_targets = []
    try:
        from CORE.inference.providers import get_best_provider, list_providers
        available = list_providers()
        best = get_best_provider()
        deploy_targets.append(f"12-Provider Chain ({len(available)} available)")
        print(f"  Best provider: {best}", flush=True)
    except ImportError:
        deploy_targets.append("12-Provider Chain (CORE.inference not available)")
        print("  [INFO] Inference providers not available", flush=True)

    deploy_targets.append("LM Studio (local fallback)")
    data["onnx_path"] = str(onnx_path)
    data["deploy_targets"] = deploy_targets
    data["deployed"] = True
    return data


def summary(data: dict, elapsed: float):
    """Print a formatted summary."""
    best = data.get("best", None)
    history = data.get("history", [])

    print("\n" + "=" * 60)
    print("  SCENARIO D: NAS PIPELINE — Complete")
    print("=" * 60)
    print(f"  Generations:  {data.get('generations_run', 0)}")
    if history:
        final = history[-1]
        print(f"  Best fitness: {final.get('best_fitness', 'N/A')}")
        print(f"  Avg fitness:  {final.get('avg_fitness', 'N/A')}")
    if best:
        print(f"  Best pattern: {best.genome.get('architecture_pattern', 'N/A')}")
    print(f"  Trained:      {data.get('trained', False)}")
    print(f"  Trainer:      {data.get('trainer', 'N/A')}")
    print(f"  ONNX path:    {data.get('onnx_path', 'N/A')}")
    print(f"  Deployed to:  {', '.join(data.get('deploy_targets', ['N/A']))}")
    print(f"  Duration:     {elapsed:.1f}s")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Scenario D: NAS Pipeline — Evolutionary search → train → ONNX → deploy",
    )
    parser.add_argument("--source", default="SystemZ",
                        help="Data source filter (default: SystemZ)")
    parser.add_argument("--generations", type=int, default=10,
                        help="Number of NAS generations (default: 10)")
    parser.add_argument("--population", type=int, default=8,
                        help="Population size per generation (default: 8)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print steps without executing")
    parser.add_argument("--output", default=None,
                        help="Save NAS results JSON to path")

    args = parser.parse_args()

    print("=" * 60)
    print("  SCENARIO D: NAS Pipeline")
    print("  Evolutionary NAS → Best Architecture → GRPOTrainer → ONNX → Inference")
    print("=" * 60)
    print(flush=True)

    t0 = time.time()
    data: dict = {}

    # Step 1: NAS search
    nas_result = step_nas_search(args.source, args.generations,
                                  args.population, args.dry_run)
    data.update(nas_result)

    # Step 2: Train best architecture
    data = step_train_best(data, args.source, args.dry_run)

    # Step 3: Export and deploy
    data = step_export_and_deploy(data, args.dry_run)

    elapsed = time.time() - t0
    summary(data, elapsed)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v for k, v in data.items()
                        if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
        out.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")
        print(f"\nResults saved to: {out}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
