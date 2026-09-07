"""Evolution cycle: evolve RLTrainLoop hyperparameters for training reward.

Genome: {learning_rate, epsilon, discount_factor}. Fitness: avg_reward of a
short training run. Reports the best genome; does NOT rewrite production
defaults (human decision). All runs recorded by the training loop itself.
"""
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


evo = EvolutionEngine(population_size=8, elitism_count=2,
                      crossover_rate=0.7, mutation_rate=0.15)
evo.initialize_population({
    'learning_rate': (0.01, 0.5),
    'epsilon': (0.0, 0.5),
    'discount': (0.8, 0.999),
})
for gen in range(4):
    stats = evo.evaluate_population(fitness)
    best = evo.get_best_genome()
    log(f'gen {gen}: best={stats.get("best_fitness")} '
        f'genes={best.genes if best else None}')
    evo.evolve()

best = evo.get_best_genome()
log('BEST: %s' % (best.genes if best else None))
try:
    from CORE.direct_memory import DirectMemory
    DirectMemory().record('evolution_result', {
        'action': 'evolution run complete',
        'best_genes': best.genes if best else {},
        'generations': 4,
        'population': 8,
    }, tags=['evolution', 'artifact'])
except Exception as e:
    log('artifact record failed: %s' % e)
