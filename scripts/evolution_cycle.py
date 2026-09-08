"""Evolution cycle: evolve RLTrainLoop hyperparameters for training reward.

Robustness: seeded RNG (logged, replayable), seeded population from last
best genome (continuity across runs), early stopping on convergence
(max 15 gens, patience 5), per-gen trajectory in the artifact row.
Genome: {learning_rate, epsilon, discount_factor}. Fitness (v3-dual-robust):
min over 2 exploration salts of (info-flood avg + critical-alert avg) over
80-episode runs. Reports the best genome; PROMOTES to production defaults
after 3 consecutive wins over the production baseline (guardrailed, rollback
= delete config/evolved_rl_params.json). All runs recorded by the training
loop itself.

Deterministic fitness (2026-09-07 fix): RLTrainLoop explores via the
module-level `random` module, so an unseeded evaluation is a fresh random
draw every time — the same genome could score +14.7 in one run and -8.1
in the next, making the GA chase noise. fitness() now seeds the RNG from
a stable hash of the genome's genes, so a genome's score is a pure
function of (genome, eval pool). The pool fingerprint (severity
histogram) is recorded in the artifact so landscape drift between runs
is observable instead of silent.
"""
import hashlib
import json
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


N_EPISODES = 80  # eval budget per skill (was 60; runs take ~10-15s, fits the slot)


def genome_seed(genes, salt='a'):
    """Stable per-genome RNG seed (same genes+salt -> same seed, any process)."""
    s = salt + '|' + ','.join('%s=%.6f' % (k, float(genes[k])) for k in sorted(genes))
    return int(hashlib.sha256(s.encode('utf-8')).hexdigest()[:8], 16)


def _eval_salt(genes):
    """One dual-skill evaluation. Assumes RNG already seeded. Returns (total, info, alert)."""
    loop = RLTrainLoop()
    info_stats = loop.train_from_memory(
        n_episodes=N_EPISODES, max_steps=50,
        learning_rate=float(genes['learning_rate']),
        epsilon=float(genes['epsilon']),
        discount_factor=float(genes['discount']))
    alert_stats = RLTrainLoop().train_from_memory(
        n_episodes=N_EPISODES, max_steps=50,
        learning_rate=float(genes['learning_rate']),
        epsilon=float(genes['epsilon']),
        discount_factor=float(genes['discount']),
        event_type='db_health_alert')
    info = float(info_stats.get('avg_reward', 0.0))
    alert = float(alert_stats.get('avg_reward', 0.0))
    return (info + alert, info, alert)


def fitness_genes(genes):
    """v3-dual-robust fitness: min over 2 exploration salts.

    v3 (2026-09-08): single-salt evals let lucky exploration draws win, so
    selection chased noise within the 11-14 band. min-of-2 salts pressures
    robust genes (both draws must score). min <= single-salt mean, so v3
    totals run slightly below v2 for the same genome — same units, and the
    monitor's scale-break note covers the step. Deterministic: pure
    function of (genome, pools).
    """
    best = None
    for salt in ('a', 'b'):
        random.seed(genome_seed(genes, salt))
        total, _, _ = _eval_salt(genes)
        best = total if best is None else min(best, total)
    return best


def fitness_parts(genes):
    """Recompute (total, info, alert) of the argmin salt — reproduces fitness_genes exactly."""
    results = []
    for salt in ('a', 'b'):
        random.seed(genome_seed(genes, salt))
        results.append(_eval_salt(genes))
    results.sort(key=lambda r: r[0])
    total, info, alert = results[0]
    return (round(total, 4), round(info, 4), round(alert, 4))


def fitness(genome):
    return fitness_genes(genome.genes)


def pool_fingerprint():
    """Severity histogram of the eval pool — landscape drift indicator.

    Also reports the hard (critical-alert) pool size and newest timestamp,
    so hard-example inflow starvation is visible: if hard_count stalls for
    days, evolution is re-mastering frozen rows and needs fresh production
    errors (chaos drills, re-armed watchdogs, real incidents).
    """
    try:
        from collections import Counter
        from CORE.WORMS.expansion.learning import DataPipelineWorm
        recs = DataPipelineWorm().extract_from_memory(limit=300)
        fp = dict(Counter(r.get('severity', 'unknown') for r in recs))
        hard = DataPipelineWorm().extract_from_memory(
            event_type='db_health_alert', limit=2000)
        if hard:
            fp['hard_count'] = len(hard)
            fp['hard_newest'] = max(
                (r.get('timestamp', '') for r in hard), default='')
        return fp
    except Exception:
        return {}


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

evo = EvolutionEngine(population_size=24, elitism_count=3,
                      crossover_rate=0.7, mutation_rate=0.15,
                      early_stop_patience=5, early_stop_tolerance=0.01)
seed_genes = last_best_genes()

# Hall of fame: best champion ever recorded, by champion_reeval score.
# Keeps the global best in the population even if recent runs regressed,
# so a bad run can never erase the best-known genome.
hof_genes = None
try:
    from CORE.local_memory import get_memory_store
    _store = get_memory_store()
    _rows = _store.query_memories(event_type='evolution_result', limit=40)
    _best = None   # best v3-scale champion (comparable units)
    _best_any = None  # fallback: best of any scale (transition periods)
    for _r in _rows:
        _d = _r.get('data', {}) or {}
        if isinstance(_d, str):
            import json as _json
            try:
                _d = _json.loads(_d)
            except Exception:
                continue
        _c = _d.get('champion_reeval')
        if _c is None:
            continue
        if _best_any is None or _c > _best_any[0]:
            _best_any = (_c, _d.get('best_genes'))
        if str(_d.get('fitness', '')).startswith('v3'):
            if _best is None or _c > _best[0]:
                _best = (_c, _d.get('best_genes'))
    _pick = _best or _best_any
    if _pick and isinstance(_pick[1], dict) and _pick[1]:
        hof_genes = _pick[1]
        log('hall-of-fame seed: champ=%s genes=%s' % (_pick[0], {k: round(v, 4) for k, v in _pick[1].items()}))
except Exception as e:
    log('hall-of-fame lookup failed: %s' % str(e)[:120])

_seeds = [g for g in (seed_genes, hof_genes) if isinstance(g, dict) and g]
# Dedupe identical gene dicts
_seen = set()
_unique_seeds = []
for _g in _seeds:
    _key = tuple(sorted(_g.items()))
    if _key not in _seen:
        _seen.add(_key)
        _unique_seeds.append(_g)

evo.initialize_population({
    'learning_rate': (0.01, 0.5),
    'epsilon': (0.0, 0.5),
    'discount': (0.8, 0.999),
}, seed_genomes=_unique_seeds)

trajectory = []
for gen in range(15):
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
best_total, best_info, best_alert = fitness_parts(best.genes) if best else (0.0, 0.0, 0.0)
log('BEST parts: total=%s info=%s alert=%s' % (best_total, best_info, best_alert))

# Champion re-evaluation on the current pool: with deterministic fitness
# this score is comparable across runs, separating 'genome got worse'
# from 'the data landscape moved' (drift shows in pool_fingerprint).
champ_score = None
if seed_genes:
    try:
        champ_score = round(fitness_genes(seed_genes), 4)
        log('champion re-eval on current pool: %s' % champ_score)
    except Exception as e:
        log('champion re-eval failed: %s' % str(e)[:120])

# Champion promotion (2026-09-08): 3 consecutive wins over the production
# baseline promotes genes to config/evolved_rl_params.json, which
# ScheduledTrainingWorm loads as hyperparameter overrides.
# Guardrails: deterministic re-eval (no luck), margin 0.5, scale-consistent
# streak (v3 rows only), range-validated genes. Rollback = delete the file.
PROMOTE_MARGIN = 0.75
PROMOTE_WINS = 3
PROMOTE_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'evolved_rl_params.json')


def production_genes():
    """Currently-promoted genes, else ScheduleConfig built-in defaults."""
    try:
        with open(PROMOTE_JSON, encoding='utf-8') as f:
            data = json.load(f)
        g = {k: float(data['genes'][k])
             for k in ('learning_rate', 'epsilon', 'discount')}
        if (0.01 <= g['learning_rate'] <= 0.5 and 0.0 <= g['epsilon'] <= 0.5
                and 0.8 <= g['discount'] <= 0.999):
            return g
        log('promoted file out of range, using built-in defaults')
    except Exception:
        pass
    from CORE.WORMS.expansion.scheduling import ScheduleConfig
    c = ScheduleConfig()
    return {'learning_rate': float(c.learning_rate),
            'epsilon': float(c.epsilon),
            'discount': float(c.discount_factor)}


try:
    baseline_genes = production_genes()
    baseline_fit = round(fitness_genes(baseline_genes), 4)
    log('production baseline: %s -> %s' % (
        {k: round(v, 4) for k, v in baseline_genes.items()}, baseline_fit))
except Exception as e:
    baseline_genes, baseline_fit = {}, 0.0
    log('baseline eval failed: %s' % str(e)[:120])

beats = bool(best) and (best_total > baseline_fit + PROMOTE_MARGIN)
streak = 0
if beats:
    streak = 1
    try:
        from CORE.local_memory import get_memory_store
        _hrows = get_memory_store().query_memories(
            event_type='evolution_result', limit=PROMOTE_WINS - 1)
        for _hr in _hrows:
            _hd = _hr.get('data', {}) or {}
            if isinstance(_hd, str):
                try:
                    _hd = json.loads(_hd)
                except Exception:
                    break
            if (str(_hd.get('fitness', '')).startswith('v3')
                    and _hd.get('beats_baseline')):
                streak += 1
            else:
                break
    except Exception as e:
        log('streak lookup failed: %s' % str(e)[:120])
log('promotion standing: beats=%s streak=%s/%s' % (beats, streak, PROMOTE_WINS))

promoted = False
if beats and streak >= PROMOTE_WINS and best:
    try:
        with open(PROMOTE_JSON, 'w', encoding='utf-8') as f:
            json.dump({
                'genes': best.genes,
                'fitness': best_total,
                'fitness_detail': {'info': best_info, 'alert': best_alert},
                'baseline': baseline_fit,
                'wins': streak,
                'promoted_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'run_seed': seed,
            }, f, indent=2)
        promoted = True
        log('PROMOTED to %s (rollback: delete the file)' % PROMOTE_JSON)
    except Exception as e:
        log('promotion write failed: %s' % str(e)[:120])

try:
    from CORE.direct_memory import DirectMemory
    dm = DirectMemory()
    dm.record('evolution_result', {
        'action': 'evolution run complete',
        'fitness': 'v3-dual-robust',
        'best_genes': best.genes if best else {},
        'best_total': best_total,
        'best_info': best_info,
        'best_alert': best_alert,
        'baseline': baseline_fit,
        'beats_baseline': beats,
        'promoted': promoted,
        'generations': len(trajectory),
        'population': 24,
        'episodes': N_EPISODES,
        'seed': seed,
        'trajectory': trajectory,
        'seeded_from_prior': bool(seed_genes),
        'champion_reeval': champ_score,
        'pool_fingerprint': pool_fingerprint(),
    }, tags=['evolution', 'artifact'])
    if promoted and best:
        dm.record('evolution_promotion', {
            'action': 'champion promoted to production defaults',
            'genes': best.genes,
            'fitness': best_total,
            'baseline': baseline_fit,
            'wins': streak,
            'rollback': 'delete config/evolved_rl_params.json',
        }, tags=['evolution', 'promotion'])
except Exception as e:
    log('artifact record failed: %s' % e)
