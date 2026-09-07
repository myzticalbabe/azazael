"""Evolution cycle: evolve RLTrainLoop hyperparameters for training reward.

Robustness: seeded RNG (logged, replayable), seeded population from last
best genome (continuity across runs), early stopping on convergence
(max 12 gens, patience 3), per-gen trajectory in the artifact row.
Genome: {learning_rate, epsilon, discount_factor}. Fitness: avg_reward of a
short training run. Reports the best genome; does NOT rewrite production
defaults (human decision). All runs recorded by the training loop itself.
"""
import random
import sys
sys.path.insert(0, 'C:/Users/clint/azazael/src')

import os
import time

os.makedirs(r'C:\Users\clint\azazael\logs', exist_ok=True)
_LOG = open(r'C:\Users\clint\azazael\logs\evolution_cycle.log', 'a', encoding='utf-8')


def log(msg):
    line = '%s %s' % (time.strftime('%Y-%m-%dT%H:%M:%S'), msg)
    print(line, flush=True)
    _LOG.write(line + '\n')
    _LOG.flush()


from CORE.WORMS.expansion.evolution import EvolutionEngine
from CORE.WORMS.expansion.learning import RLTrainLoop


def fitness(genome):
    loop = RLTrainLoop()
    stats = loop.train_from_memory(
        n_episodes=30, max_steps=50,
        learning_rate=float(genome.genes['learning_rate']),
        epsilon=float(genome.genes['epsilon']),
        discount_factor=float(genome.genes['discount']))
    return float(stats.get('avg_reward', 0.0))


def last_best_genes():
    """Best genome from the most recent evolution_result row (or None)."""
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        rows = store.query_memories(event_type='evolution_result', limit=1)
        if rows:
            data = rows[0].get('data', {}) or {}
            genes = data.get('best_genes')
            if isinstance(genes, dict) and genes:
                return genes
    except Exception as e:
        log('seed lookup failed (fresh start): %s' % str(e)[:120])
    return None


seed = int(time.time()) % 100000
random.seed(seed)
log('seed=%d' % seed)

evo = EvolutionEngine(population_size=8, elitism_count=2,
                      crossover_rate=0.7, mutation_rate=0.15,
                      early_stop_patience=3, early_stop_tolerance=0.01)
seed_genes = last_best_genes()
evo.initialize_population({
    'learning_rate': (0.01, 0.5),
    'epsilon': (0.0, 0.5),
    'discount': (0.8, 0.999),
}, seed_genomes=[seed_genes] if seed_genes else None)

trajectory = []
for gen in range(12):
    stats = evo.evaluate_population(fitness)
    best = evo.get_best_genome()
    trajectory.append(round(stats.get('best_fitness', 0.0), 4))
    log(f'gen {gen}: best={stats.get("best_fitness")} '
        f'genes={best.genes if best else None}')
    if evo.has_converged():
        log(f'converged at gen {gen}, stopping early')
        break
    evo.evolve()

best = evo.get_best_genome()
log('BEST: %s' % (best.genes if best else None))
try:
    from CORE.direct_memory import DirectMemory
    DirectMemory().record('evolution_result', {
        'action': 'evolution run complete',
        'best_genes': best.genes if best else {},
        'generations': len(trajectory),
        'population': 8,
        'seed': seed,
        'trajectory': trajectory,
        'seeded_from_prior': bool(seed_genes),
    }, tags=['evolution', 'artifact'])
except Exception as e:
    log('artifact record failed: %s' % e)
