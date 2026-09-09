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

Import-safety (2026-09-08 fix): all execution lives in main(), guarded by
`if __name__ == '__main__'`. Importing this module (for tests or the
benchmark) now loads only the pure helpers; it no longer triggers a GA run
or a promotion write.
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

# NSGA-II multi-objective refinement (2026-09-08 expansion): after the scalar
# loop, info mastery and critical-alert mastery are treated as separate
# objectives, the Pareto front of the evolved population is surfaced, and a
# 'knee' genome (max normalized objective sum) is picked as the balanced
# alternative. Budget-bounded: 2 generations costs ~50-60s extra, fits the
# 5-min slot next to the scalar loop's ~40s.
MULTI_GENS = 2

# Sources that are pure training/bookkeeping noise (the training loops record
# their own training_complete / model_registered events back into the store;
# together RLTrainLoop+ModelVersioner are ~70% of all rows). Excluding them
# keeps the eval pools on real worm/production signals instead of the system
# optimizing against its own feedback loop.
EXCLUDED_TRAINING_SOURCES = [
    'RLTrainLoop',
    'ModelVersioner',
    'GRPOTrainer',
    'EvolutionEngine',
    'sb3_agent',
    'TrainingOrchestrator',
    'ABTestRunner',
    'FleetTrainer',
]


def genome_seed(genes, salt='a'):
    """Stable per-genome RNG seed (same genes+salt -> same seed, any process)."""
    s = salt + '|' + ','.join('%s=%.6f' % (k, float(genes[k])) for k in sorted(genes))
    return int(hashlib.sha256(s.encode('utf-8')).hexdigest()[:8], 16)


# Salts for the conservative min-estimator. Three, not two: one lucky seed
# must not be able to carry a genome into production.
_SALTS = ('a', 'b', 'c')


def _eval_salt(genes, info_pool=None, alert_pool=None, rng=None):
    """One dual-skill evaluation. Returns (total, info, alert).

    persist=False (2026-09-08): GA eval runs score without writing back —
    no training_complete / model_registered / q_table_persisted rows, so a
    full cycle no longer bloats the store or model registry with ~96
    bookkeeping events per run.

    epsilon_decay (2026-09-08 expansion): passed through from the genome so
    the GA can evolve exploration-annealing speed.

    Frozen pools (2026-09-08 fix): when info_pool/alert_pool are given, both
    skills train on those snapshots instead of re-extracting the live
    window — the 300-row eval window drifts ~3 fitness points during a
    single cycle (monitor writes), which used to contaminate trajectories
    and the promotion comparison. None = live extraction (backward compat).

    Isolated RNG (2026-09-09): pass a seeded random.Random and the eval is
    a pure function of (genome, pools, seed) with zero global-state
    traffic — safe for parallel fitness evaluation under free-threading.

    3-salt min (2026-09-09): the min is taken over three salts, so one
    lucky seed can't carry a genome. +50% eval cost, covered by the 4x
    parallel speedup from isolated RNG.
    """
    loop = RLTrainLoop()
    info_stats = loop.train_from_memory(
        n_episodes=N_EPISODES, max_steps=50,
        learning_rate=float(genes['learning_rate']),
        epsilon=float(genes['epsilon']),
        epsilon_decay=float(genes.get('epsilon_decay', 0.0)),
        discount_factor=float(genes['discount']),
        exclude_sources=EXCLUDED_TRAINING_SOURCES,
        records=info_pool,
        persist=False,
        rng=rng)
    alert_stats = RLTrainLoop().train_from_memory(
        n_episodes=N_EPISODES, max_steps=50,
        learning_rate=float(genes['learning_rate']),
        epsilon=float(genes['epsilon']),
        epsilon_decay=float(genes.get('epsilon_decay', 0.0)),
        discount_factor=float(genes['discount']),
        event_type='db_health_alert',
        exclude_sources=EXCLUDED_TRAINING_SOURCES,
        records=alert_pool,
        persist=False,
        rng=rng)
    info = float(info_stats.get('avg_reward', 0.0))
    alert = float(alert_stats.get('avg_reward', 0.0))
    return (info + alert, info, alert)


def fitness_skill(genes, idx, info_pool=None, alert_pool=None):
    """Deterministic single-objective fitness (min over 2 salts), like fitness_genes.

    idx: 1 = info-skill score, 2 = alert-skill score. Used by the NSGA-II
    multi-objective phase so the Pareto front trades info mastery vs
    critical-alert mastery as separate objectives.
    """
    best = None
    for salt in _SALTS:
        parts = _eval_salt(genes, info_pool, alert_pool,
                           rng=random.Random(genome_seed(genes, salt)))
        v = parts[idx]
        best = v if best is None else min(best, v)
    return best


def fitness_genes(genes, info_pool=None, alert_pool=None):
    """v3-dual-robust fitness: min over 2 exploration salts.

    v3 (2026-09-08): single-salt evals let lucky exploration draws win, so
    selection chased noise within the 11-14 band. min-of-2 salts pressures
    robust genes (both draws must score). min <= single-salt mean, so v3
    totals run slightly below v2 for the same genome — same units, and the
    monitor's scale-break note covers the step. Deterministic: pure
    function of (genome, pools).
    """
    best = None
    for salt in _SALTS:
        total, _, _ = _eval_salt(genes, info_pool, alert_pool,
                                 rng=random.Random(genome_seed(genes, salt)))
        best = total if best is None else min(best, total)
    return best


def fitness_parts(genes, info_pool=None, alert_pool=None):
    """Recompute (total, info, alert) of the argmin salt — reproduces fitness_genes exactly."""
    results = []
    for salt in _SALTS:
        results.append(_eval_salt(genes, info_pool, alert_pool,
                                  rng=random.Random(genome_seed(genes, salt))))
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
        recs = DataPipelineWorm().extract_from_memory(
            limit=300, exclude_sources=EXCLUDED_TRAINING_SOURCES)
        fp = dict(Counter(r.get('severity', 'unknown') for r in recs))
        hard = DataPipelineWorm().extract_from_memory(
            event_type='db_health_alert', limit=2000,
            exclude_sources=EXCLUDED_TRAINING_SOURCES)
        if hard:
            fp['hard_count'] = len(hard)
            fp['hard_newest'] = max(
                (r.get('timestamp', '') for r in hard), default='')
        return fp
    except Exception:
        return {}


def last_best_genes():
    """Champion genome from the most recent evolution_result row (or None).

    Prefers champion_genes (the genome that actually earned champion_reeval)
    so the seed chain tracks the true champion; falls back to best_genes for
    artifacts recorded before the champion_genes fix (2026-09-08).
    """
    try:
        from CORE.local_memory import get_memory_store
        store = get_memory_store()
        rows = store.query_memories(event_type='evolution_result', limit=1)
        if rows:
            data = rows[0].get('data', {}) or {}
            genes = data.get('champion_genes') or data.get('best_genes')
            if isinstance(genes, dict) and genes:
                return genes
    except Exception as e:
        log('seed lookup failed (fresh start): %s' % str(e)[:120])
    return None


# Champion promotion (2026-09-08): 3 consecutive wins over the production
# baseline promotes genes to config/evolved_rl_params.json, which
# ScheduledTrainingWorm loads as hyperparameter overrides.
# Guardrails: deterministic 3-salt re-eval (no luck), margin 0.75,
# scale-consistent streak (v3 rows only), range-validated genes, fresh-pool
# holdout gate, .prev backup + one-shot auto-canary with landscape probe.
PROMOTE_MARGIN = 0.75
PROMOTE_WINS = 3
PROMOTE_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config', 'evolved_rl_params.json')


PROMOTE_KEYS = ('learning_rate', 'epsilon', 'discount', 'epsilon_decay')


# Canary + rollback + holdout (2026-09-09): the 3-win streak proves the
# candidate beats production on frozen pools, but pools are shared across
# runs — a candidate can overfit one snapshot. Two extra gates:
#
# 1. Holdout gate (pre-promotion): re-extract FRESH pools (data pulled
#    after the GA ran, never seen during search) and require the
#    candidate to beat the baseline there too, by the same margin.
# 2. Canary watch (post-promotion): the run after a promotion, with
#    fresh pools, re-evaluates production (= the new genes) plus the
#    built-in defaults as a landscape probe. If the landscape is stable
#    (defaults reproduce within LANDSCAPE_TOL) but production regressed
#    more than CANARY_TOL below its promotion fitness, the previous
#    production file (kept as .prev.json on every promotion) is restored
#    automatically. If the landscape moved instead, the canary is
#    inconclusive and just clears. Either way the canary fires once.
PREV_JSON = PROMOTE_JSON + '.prev.json'
CANARY_JSON = PROMOTE_JSON + '.canary.json'
CANARY_TOL = 1.5
LANDSCAPE_TOL = 1.0


def production_genes():
    """Currently-promoted genes, else ScheduleConfig built-in defaults."""
    try:
        with open(PROMOTE_JSON, encoding='utf-8') as f:
            data = json.load(f)
        g = {k: float(data['genes'][k])
             for k in ('learning_rate', 'epsilon', 'discount')}
        if (0.01 <= g['learning_rate'] <= 0.5 and 0.0 <= g['epsilon'] <= 0.5
                and 0.8 <= g['discount'] <= 0.999):
            g['epsilon_decay'] = float(data['genes'].get('epsilon_decay', 0.0))
            g['epsilon_decay'] = max(0.0, min(g['epsilon_decay'], 0.2))
            return g
        log('promoted file out of range, using built-in defaults')
    except Exception:
        pass
    from CORE.WORMS.expansion.scheduling import ScheduleConfig
    c = ScheduleConfig()
    return {'learning_rate': float(c.learning_rate),
            'epsilon': float(c.epsilon),
            'discount': float(c.discount_factor),
            'epsilon_decay': float(getattr(c, 'epsilon_decay', 0.0))}


def _builtin_default_genes():
    """ScheduleConfig built-ins — the landscape probe for canary checks."""
    from CORE.WORMS.expansion.scheduling import ScheduleConfig
    c = ScheduleConfig()
    return {'learning_rate': float(c.learning_rate),
            'epsilon': float(c.epsilon),
            'discount': float(c.discount_factor),
            'epsilon_decay': float(getattr(c, 'epsilon_decay', 0.0))}


def _holdout_gate(cand_genes, base_genes):
    """Evaluate candidate vs baseline on freshly-extracted pools.

    Returns dict with cand/base/margin/passed, or {'passed': False,
    'reason': ...} on extraction failure (fail closed — no promotion on
    an unverified holdout). Runs serially: 2 genomes x 3 salts.
    """
    try:
        from CORE.WORMS.expansion.learning import DataPipelineWorm
        fresh_info = DataPipelineWorm().extract_from_memory(
            limit=N_EPISODES * 10, exclude_sources=EXCLUDED_TRAINING_SOURCES)
        fresh_alert = DataPipelineWorm().extract_from_memory(
            event_type='db_health_alert', limit=N_EPISODES * 10,
            exclude_sources=EXCLUDED_TRAINING_SOURCES)
        if not fresh_info or not fresh_alert:
            return {'passed': False, 'reason': 'degenerate fresh pools'}
        fc = round(fitness_genes(cand_genes, fresh_info, fresh_alert), 4)
        fb = round(fitness_genes(base_genes, fresh_info, fresh_alert), 4)
        margin = round(fc - fb, 4)
        return {'passed': bool(fc > fb + PROMOTE_MARGIN), 'cand': fc,
                'base': fb, 'margin': margin,
                'fresh_info': len(fresh_info), 'fresh_alert': len(fresh_alert)}
    except Exception as e:
        return {'passed': False, 'reason': str(e)[:120]}


def _write_canary(promoted_genes, promote_fit, default_fit):
    try:
        with open(CANARY_JSON, 'w', encoding='utf-8') as f:
            json.dump({'genes': promoted_genes, 'promote_fit': promote_fit,
                       'default_fit': default_fit,
                       'written_at': time.strftime('%Y-%m-%dT%H:%M:%S')},
                      f, indent=2)
    except Exception as e:
        log('canary write failed: %s' % str(e)[:120])


def _check_canary(info_pool, alert_pool, pool_reused):
    """One-shot post-promotion watch. Returns a report dict for the artifact.

    Deferred while pools are shared (same data the promotion was scored
    on — re-eval would be circular). Fires once on the first run with
    fresh pools, then deletes the canary file.
    """
    try:
        with open(CANARY_JSON, encoding='utf-8') as f:
            can = json.load(f)
    except Exception:
        return {}
    if not info_pool or not alert_pool:
        return {'status': 'deferred-degenerate-pools'}
    if pool_reused:
        return {'status': 'deferred-shared-pools'}
    report = {'status': 'unknown'}
    try:
        if not os.path.exists(PROMOTE_JSON):
            report = {'status': 'cleared-manual-rollback'}
            log('canary cleared: production file removed manually')
        else:
            prod = production_genes()
            dflt = _builtin_default_genes()
            prod_now = round(fitness_genes(prod, info_pool, alert_pool), 4)
            dflt_now = round(fitness_genes(dflt, info_pool, alert_pool), 4)
            landscape_shift = abs(dflt_now - float(can.get('default_fit', dflt_now)))
            regress = float(can.get('promote_fit', prod_now)) - prod_now
            report = {'status': 'pass', 'prod_now': prod_now,
                      'default_now': dflt_now,
                      'landscape_shift': round(landscape_shift, 4),
                      'regress': round(regress, 4)}
            if landscape_shift > LANDSCAPE_TOL:
                report['status'] = 'inconclusive-landscape-moved'
                log('canary inconclusive: landscape moved (default shift %.3f)' % landscape_shift)
            elif regress > CANARY_TOL:
                if os.path.exists(PREV_JSON):
                    with open(PREV_JSON, encoding='utf-8') as f:
                        prev = json.load(f)
                    with open(PROMOTE_JSON + '.canary-failed.json', 'w', encoding='utf-8') as f:
                        json.dump({'genes': prod,
                                   'failed_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                                   'regress': round(regress, 4)}, f, indent=2)
                    with open(PROMOTE_JSON, 'w', encoding='utf-8') as f:
                        json.dump(prev, f, indent=2)
                    report['status'] = 'ROLLED-BACK'
                    log('canary FAILED: production regressed %.3f — restored %s' % (
                        regress, PREV_JSON))
                else:
                    report['status'] = 'regressed-no-prev'
                    log('canary FAILED: regressed %.3f but no .prev to restore' % regress)
            else:
                log('canary PASS: production holding (regress %.3f)' % regress)
    except Exception as e:
        report = {'status': 'error', 'reason': str(e)[:120]}
        log('canary check failed: %s' % str(e)[:120])
    try:
        os.remove(CANARY_JSON)
    except Exception:
        pass
    return report


POOL_SNAPSHOT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'state', 'evolution_pool_snapshot.json'))
POOL_MAX_AGE_S = 1800  # 30 min: consecutive 5-min cycles share one pool


def _load_or_freeze_pools():
    """Shared frozen pools across consecutive runs (2026-09-09 hardening).

    Within-run freezing (2026-09-08) made trajectories pool-consistent,
    but the production baseline still swung 31.6 -> 26.4 on identical
    genes between runs minutes apart. Reusing one snapshot while fresh
    makes streak comparisons apples-to-apples too.

    Returns (info_pool, alert_pool, reused, age_s). Degenerate (empty)
    extractions are never persisted and fall back to live per-eval
    extraction. The cycle lock serializes readers/writers.
    """
    from CORE.WORMS.expansion.learning import DataPipelineWorm
    now = time.time()
    try:
        with open(POOL_SNAPSHOT_PATH, encoding='utf-8') as f:
            snap = json.load(f)
        age = now - float(snap.get('saved_at', 0))
        info_pool, alert_pool = snap.get('info'), snap.get('alert')
        if (isinstance(info_pool, list) and isinstance(alert_pool, list)
                and info_pool and alert_pool and age < POOL_MAX_AGE_S):
            log('reusing pool snapshot (age %ds): info=%d alert=%d' % (
                age, len(info_pool), len(alert_pool)))
            return info_pool, alert_pool, True, int(age)
        log('pool snapshot unusable (age %s), re-freezing' % (
            ('%ds' % age) if age >= 0 else 'missing'))
    except Exception as e:
        log('pool snapshot load failed, extracting fresh: %s' % str(e)[:100])
    try:
        info_pool = DataPipelineWorm().extract_from_memory(
            limit=N_EPISODES * 10, exclude_sources=EXCLUDED_TRAINING_SOURCES)
        alert_pool = DataPipelineWorm().extract_from_memory(
            event_type='db_health_alert', limit=N_EPISODES * 10,
            exclude_sources=EXCLUDED_TRAINING_SOURCES)
        if not info_pool or not alert_pool:
            log('pool extraction degenerate (info=%d alert=%d), '
                'using live evals without persisting' % (
                    len(info_pool or []), len(alert_pool or [])))
            return None, None, False, 0
        log('frozen pools: info=%d alert=%d' % (len(info_pool), len(alert_pool)))
        tmp = POOL_SNAPSHOT_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump({'saved_at': now, 'info': info_pool,
                       'alert': alert_pool}, f, ensure_ascii=False, default=str)
        os.replace(tmp, POOL_SNAPSHOT_PATH)
        return info_pool, alert_pool, False, 0
    except Exception as e:
        log('pool freeze failed, falling back to live evals: %s' % str(e)[:120])
        return None, None, False, 0


# --- Meta-evolution (2026-09-09): evolve the search itself ---------------
# A 1+1 evolution strategy over the GA's own hyperparameters. One cycle =
# one meta-sample (slow by nature: ~12/hour), so the design is a cautious
# hill-climb, not a full GA: exploit the best-known meta-params 75% of
# cycles, explore a single-param perturbation otherwise; promote the
# candidate after 3 runs if its mean beats the champion's EMA.
#
# Meta-fitness = same-pool MARGIN (best_total - baseline_fit), the honest
# signal per the 2026-09-08 audit: absolute fitness is pool-polluted,
# margin isolates search quality on identical data.
#
# Deliberately NOT evolved: population_size (wall-clock cost),
# elitism_count (stability), PROMOTE_MARGIN/WINS (safety-critical —
# letting the search relax its own promotion guardrail is textbook
# reward hacking; those stay hand-set).
META_STATE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'config', 'evolved_meta_params.json'))
META_BOUNDS = {
    'mutation_rate': (0.02, 0.4),
    'crossover_rate': (0.3, 1.0),
    'tournament_size': (2, 5),
    'early_stop_patience': (3, 8),
    'early_stop_tolerance': (0.001, 0.05),
}
META_DEFAULTS = {
    'mutation_rate': 0.15,
    'crossover_rate': 0.7,
    'tournament_size': 3,
    'early_stop_patience': 5,
    'early_stop_tolerance': 0.01,
}
META_INT_KEYS = ('tournament_size', 'early_stop_patience')
META_EXPLORE_PROB = 0.25
META_CANDIDATE_RUNS = 3


def _meta_load():
    try:
        with open(META_STATE_PATH, encoding='utf-8') as f:
            st = json.load(f)
        params = {k: float(st.get('params', {}).get(k, META_DEFAULTS[k]))
                  for k in META_BOUNDS}
        for k in META_INT_KEYS:
            params[k] = int(round(params[k]))
        return {'params': params,
                'score_ema': float(st.get('score_ema', 0.0)),
                'runs': int(st.get('runs', 0)),
                'candidate': st.get('candidate'),
                'candidate_runs': int(st.get('candidate_runs', 0)),
                'candidate_sum': float(st.get('candidate_sum', 0.0))}
    except Exception:
        return {'params': dict(META_DEFAULTS), 'score_ema': 0.0, 'runs': 0,
                'candidate': None, 'candidate_runs': 0, 'candidate_sum': 0.0}


def _meta_save(st):
    try:
        tmp = META_STATE_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(st, f, indent=2)
        os.replace(tmp, META_STATE_PATH)
    except Exception as e:
        log('meta state save failed: %s' % str(e)[:100])


def _meta_propose(st):
    """Pick this cycle's meta-params: exploit champion or explore one
    perturbed dimension. Returns (params, is_candidate)."""
    if st['candidate'] is None and random.random() < META_EXPLORE_PROB:
        cand = dict(st['params'])
        key = random.choice(sorted(META_BOUNDS))
        lo, hi = META_BOUNDS[key]
        if key in META_INT_KEYS:
            cand[key] = int(min(hi, max(lo, cand[key] + random.choice((-1, 1)))))
        else:
            cand[key] = min(hi, max(lo, cand[key] * random.uniform(0.8, 1.25)))
        st['candidate'] = cand
        st['candidate_runs'] = 0
        st['candidate_sum'] = 0.0
        log('meta: exploring %s=%s (champ %s)' % (key, cand[key], st['params'][key]))
        return cand, True
    if st['candidate'] is not None:
        return dict(st['candidate']), True
    return dict(st['params']), False


def _meta_score(st, params, is_candidate, margin):
    """Fold one cycle's margin into the meta-state; promote qualifying
    candidates. Returns a short status string for the log/artifact."""
    if is_candidate:
        st['candidate_runs'] += 1
        st['candidate_sum'] += margin
        mean = st['candidate_sum'] / st['candidate_runs']
        if st['candidate_runs'] >= META_CANDIDATE_RUNS:
            old_ema = st['score_ema']
            if mean > old_ema:
                st['params'] = dict(st['candidate'])
                st['score_ema'] = mean
                msg = ('meta: candidate PROMOTED (mean %+.2f > ema %+.2f): %s'
                       % (mean, old_ema, st['params']))
            else:
                msg = ('meta: candidate rejected (mean %+.2f <= ema %+.2f)'
                       % (mean, old_ema))
            st['candidate'] = None
            st['candidate_runs'] = 0
            st['candidate_sum'] = 0.0
        else:
            msg = ('meta: candidate %d/%d, mean %+.2f (ema %+.2f)'
                   % (st['candidate_runs'], META_CANDIDATE_RUNS, mean,
                      st['score_ema']))
    else:
        st['runs'] += 1
        alpha = 0.2
        st['score_ema'] += alpha * (margin - st['score_ema'])
        msg = 'meta: champ ema %+.2f over %d runs' % (st['score_ema'], st['runs'])
    _meta_save(st)
    return msg


def _acquire_cycle_lock():
    """Single-instance guard (2026-09-08): a manual run colliding with the
    scheduled one was observed twice (12:14 and 12:49 — two processes
    interleaved in the log and raced on the promotion file). Non-blocking;
    returns the open handle to hold for the run, or None when another
    cycle owns the lock. The OS releases msvcrt locks on process death,
    so no stale-lock cleanup is needed."""
    import msvcrt
    lock_path = os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'logs', 'evolution_cycle.lock'))
    fh = open(lock_path, 'w')
    try:
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        return fh
    except OSError:
        fh.close()
        return None


def main():
    _lock = _acquire_cycle_lock()
    if _lock is None:
        log('another evolution cycle holds the lock, skipping this run')
        return
    seed = int(time.time()) % 100000
    random.seed(seed)
    log('seed=%d' % seed)

    meta_st = _meta_load()
    meta_params, meta_is_cand = _meta_propose(meta_st)
    log('meta: %s params=%s' % (
        'candidate' if meta_is_cand else 'champion',
        {k: round(v, 4) for k, v in meta_params.items()}))

    evo = EvolutionEngine(population_size=24, elitism_count=3,
                          crossover_rate=meta_params['crossover_rate'],
                          mutation_rate=meta_params['mutation_rate'],
                          tournament_size=meta_params['tournament_size'],
                          early_stop_patience=meta_params['early_stop_patience'],
                          early_stop_tolerance=meta_params['early_stop_tolerance'])
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
            # Pair the champion score with the genome that earned it. Pre-fix
            # artifacts (before 2026-09-08) only have best_genes — fall back.
            # v3-only (2026-09-08 fix): older-scale champions (e.g. the 40s
            # band) re-eval far below current genomes and only waste
            # population slots while diluting new genes via crossover.
            _genes = _d.get('champion_genes') or _d.get('best_genes')
            if str(_d.get('fitness', '')).startswith('v3'):
                if _best is None or _c > _best[0]:
                    _best = (_c, _genes)
        _pick = _best
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
        'epsilon_decay': (0.0, 0.1),  # exploration-annealing speed (2026-09-08)
    }, seed_genomes=_unique_seeds)

    # Frozen eval pools (2026-09-08 fix, 2026-09-09 shared-snapshot
    # hardening): one snapshot per cycle, reused by consecutive cycles
    # while fresh, so genomes, champion re-eval AND the baseline — this
    # run and the next — are all scored on identical data. Same
    # extraction params the live path used (limit = N_EPISODES * 10),
    # so historical fitness stays comparable.
    info_pool, alert_pool, pool_reused, pool_age_s = _load_or_freeze_pools()

    def fitness_frozen(genome):
        return fitness_genes(genome.genes, info_pool, alert_pool)

    # One-shot canary watch for the previous promotion (2026-09-09).
    # Deferred automatically while pools are shared.
    canary_report = _check_canary(info_pool, alert_pool, pool_reused)
    if canary_report:
        log('canary: %s' % canary_report.get('status'))

    # Parallel eval workers (2026-09-09): fitness is now RNG-isolated per
    # genome (no global-random traffic), so the population evaluates with
    # true parallelism under free-threading. 8 workers ≈ one per 3 genomes
    # at population 24; results assign back in order, stats bit-identical.
    _workers = 8

    trajectory = []
    for gen in range(15):
        stats = evo.evaluate_population(fitness_frozen, workers=_workers)
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
    best_total, best_info, best_alert = (
        fitness_parts(best.genes, info_pool, alert_pool) if best else (0.0, 0.0, 0.0))
    log('BEST parts: total=%s info=%s alert=%s' % (best_total, best_info, best_alert))

    # Champion re-evaluation on the current pool: with deterministic fitness
    # this score is comparable across runs, separating 'genome got worse'
    # from 'the data landscape moved' (drift shows in pool_fingerprint).
    champ_score = None
    if seed_genes:
        try:
            champ_score = round(fitness_genes(seed_genes, info_pool, alert_pool), 4)
            log('champion re-eval on current pool: %s' % champ_score)
        except Exception as e:
            log('champion re-eval failed: %s' % str(e)[:120])

    try:
        baseline_genes = production_genes()
        baseline_fit = round(fitness_genes(baseline_genes, info_pool, alert_pool), 4)
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
    meta_msg = _meta_score(meta_st, meta_params, meta_is_cand,
                           (best_total - baseline_fit) if best else 0.0)
    log(meta_msg)

    promoted = False
    holdout = {}
    if beats and streak >= PROMOTE_WINS and best:
        # Holdout gate (2026-09-09): the streak was scored on frozen pools
        # the GA searched on. Re-extract fresh pools and require the
        # candidate to beat the baseline there too — fail closed.
        holdout = _holdout_gate(best.genes, baseline_genes)
        log('holdout: %s' % holdout)
        if not holdout.get('passed'):
            log('promotion BLOCKED by holdout gate')
    if beats and streak >= PROMOTE_WINS and best and holdout.get('passed'):
        try:
            if os.path.exists(PROMOTE_JSON):
                with open(PROMOTE_JSON, encoding='utf-8') as f:
                    prev_data = f.read()
                with open(PREV_JSON, 'w', encoding='utf-8') as f:
                    f.write(prev_data)
            with open(PROMOTE_JSON, 'w', encoding='utf-8') as f:
                json.dump({
                    'genes': best.genes,
                    'fitness': best_total,
                    'fitness_detail': {'info': best_info, 'alert': best_alert},
                    'baseline': baseline_fit,
                    'holdout': holdout,
                    'wins': streak,
                    'promoted_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'run_seed': seed,
                }, f, indent=2)
            promoted = True
            log('PROMOTED to %s (prev kept at %s, auto-canary armed)' % (
                PROMOTE_JSON, PREV_JSON))
            try:
                _write_canary(best.genes, best_total, round(fitness_genes(
                    _builtin_default_genes(), info_pool, alert_pool), 4))
            except Exception as e:
                log('canary arm failed: %s' % str(e)[:120])
        except Exception as e:
            log('promotion write failed: %s' % str(e)[:120])

    # --- NSGA-II multi-objective refinement (2026-09-08 expansion) ---
    # Info mastery and critical-alert mastery as separate objectives. The
    # engine's Pareto machinery (non-dominated sort + crowding distance) is
    # used as-is; objectives are negated (engine minimizes). The 'knee' is the
    # front member with the max normalized objective sum — the balanced pick.
    pareto = None
    try:
        res = evo.optimize_multi_objective(
            [lambda g: -fitness_skill(g.genes, 1, info_pool, alert_pool),
             lambda g: -fitness_skill(g.genes, 2, info_pool, alert_pool)],
            generations=MULTI_GENS)
        front = res.get('pareto_front', []) or []
        if front:
            obj = [f['objectives'] for f in front]
            lo = [min(o[i] for o in obj) for i in range(2)]
            hi = [max(o[i] for o in obj) for i in range(2)]
            rng = [max(1e-9, hi[i] - lo[i]) for i in range(2)]

            def _norm(o):
                return sum((o[i] - lo[i]) / rng[i] for i in range(2))

            knee = max(front, key=lambda f: _norm(f['objectives']))
            pareto = {
                'front': [{'genes': f['genes'],
                           'info': round(-f['objectives'][0], 4),
                           'alert': round(-f['objectives'][1], 4)}
                          for f in front],
                'knee': {'genes': knee['genes'],
                         'info': round(-knee['objectives'][0], 4),
                         'alert': round(-knee['objectives'][1], 4)},
                'generations': res.get('generations', MULTI_GENS),
            }
            log('multi-objective: front=%d knee=%s info=%.3f alert=%.3f' % (
                len(front),
                {k: round(v, 4) for k, v in knee['genes'].items()},
                pareto['knee']['info'], pareto['knee']['alert']))
    except Exception as e:
        log('multi-objective phase failed: %s' % str(e)[:160])

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
            'meta_params': meta_params,
            'meta_candidate': meta_is_cand,
            'meta_msg': meta_msg,
            'champion_reeval': champ_score,
            'champion_genes': seed_genes,
            'pool_fingerprint': pool_fingerprint(),
            'pool_snapshot_reused': pool_reused,
            'pool_snapshot_age_s': pool_age_s,
            'pareto': pareto,
            'holdout': holdout,
            'canary': canary_report,
        }, tags=['evolution', 'artifact'])
        if promoted and best:
            dm.record('evolution_promotion', {
                'action': 'champion promoted to production defaults',
                'genes': best.genes,
                'fitness': best_total,
                'baseline': baseline_fit,
                'holdout': holdout,
                'wins': streak,
                'rollback': 'auto-canary armed; manual: restore %s' % PREV_JSON,
            }, tags=['evolution', 'promotion'])
    except Exception as e:
        log('artifact record failed: %s' % e)


if __name__ == '__main__':
    main()