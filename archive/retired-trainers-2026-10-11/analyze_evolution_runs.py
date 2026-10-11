#!/usr/bin/env python3
"""Analyse a run_evolution_n.py batch (default 50 cycles) and write a report.

Two evidence sources, deliberately cross-checked:

  1. logs/evolution_runs/*.log  — the pipeline's own timestamped stdout. This is
     the ONLY place the wall-clock cost of each phase is visible, because
     evolution_cycle.py logs a line at every stage boundary. Phase time is
     attributed to the stage named on the LATER line of a pair, which is exact
     for this log shape (one line per boundary, no interleaving).
  2. the memory store's `evolution_result` rows — the structured artifact
     (pool_id, trajectory, sprt, pareto_gate, holdout, cma_arm, qd_archive,
     baseline_hash, ...). Matched to runs by `seed`, which the cycle prints and
     embeds in every row.

Outputs state/evolution_50run_analysis.json (machine) and
azazael/EVOLUTION_50RUN_ANALYSIS_<date>.md (human).

Usage:
  python scripts/analyze_evolution_runs.py            # 50 runs, dated today
"""
import argparse
import ast
import glob
import json
import os
import re
import statistics as st
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))

RAWDIR = os.path.join(ROOT, 'logs', 'evolution_runs')
RUNJSON = os.path.join(ROOT, 'logs', 'run_evolution_n.json')
OUTJSON = os.path.join(ROOT, 'state', 'evolution_50run_analysis.json')

TS_RE = re.compile(r'^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\s+(.*)$')
STANDING_RE = re.compile(
    r'promotion standing: beats=(True|False) margin=([-\d.]+) sprt=(\w+)'
    r'\(n=(\d+) llr=([-\d.]+) sigma=([-\d.]+)\) streak=(\d+)/(\d+)')
GEN_RE = re.compile(r'\bgen (\d+): best=([-\d.]+)')
QD_RE = re.compile(r'qd archive: (\d+)/(\d+) cells coverage=([\d.]+) '
                   r'qd_score=([-\d.]+) best=([-\d.]+) \(\+(\d+) this cycle\)')
ARM_RE = re.compile(r'(\w+) arm: (skipped|WON|held)')
META_CAND_RE = re.compile(r'meta: candidate (\d+)/(\d+), mean ([+-][\d.]+) \(ema ([+-][\d.]+)\)')
META_CHAMP_RE = re.compile(r'meta: champ ema ([+-][\d.]+) over (\d+) runs')
BASE_RE = re.compile(r'production baseline: (\{.*\}) -> ([-\d.]+)')


def parse_log(path):
    """Return (fields, phases) for one raw cycle log."""
    f = {'path': os.path.basename(path)}
    gens, phases, stamps = [], [], []
    blocked = []
    with open(path, encoding='utf-8', errors='replace') as fh:
        for ln in fh:
            m = TS_RE.match(ln.rstrip('\n'))
            if not m:
                continue
            ts, msg = m.group(1), m.group(2)
            stamps.append((ts, msg))
            if msg.startswith('seed='):
                f['seed'] = int(msg.split('=')[1])
            elif msg.startswith('strategy='):
                parts = msg.split()
                f['strategy'] = parts[0].split('=')[1]
                f['explore_prob'] = float(parts[1].split('=')[1])
            elif msg.startswith('meta: candidate'):
                mm = META_CAND_RE.search(msg)
                if mm:
                    f['meta_candidate'] = True
                    f['meta_n'] = (int(mm.group(1)), int(mm.group(2)))
                    f['meta_mean'] = float(mm.group(3))
                    f['meta_ema'] = float(mm.group(4))
            elif msg.startswith('meta: champ ema'):
                mm = META_CHAMP_RE.search(msg)
                if mm:
                    f['meta_candidate'] = False
                    f['meta_ema'] = float(mm.group(1))
                    f['meta_runs'] = int(mm.group(2))
            elif msg.startswith('meta:') and 'params=' in msg:
                try:
                    f['meta_params'] = ast.literal_eval(msg.split('params=', 1)[1])
                except Exception:
                    pass  # scanner:ignore
            elif GEN_RE.search(msg):
                gm = GEN_RE.search(msg)
                gens.append((int(gm.group(1)), float(gm.group(2))))
            elif msg.startswith('converged at gen'):
                f['converged_at'] = int(msg.split('gen ')[1].split(',')[0])
            elif msg.startswith('BEST parts:'):
                mm = re.search(r'total=([-\d.]+) info=([-\d.]+) alert=([-\d.]+)', msg)
                if mm:
                    f['best_total'], f['best_info'], f['best_alert'] = map(float, mm.groups())
            elif msg.startswith('production baseline:'):
                mm = BASE_RE.search(msg)
                if mm:
                    try:
                        f['baseline_genes'] = ast.literal_eval(mm.group(1))
                    except Exception:
                        pass  # scanner:ignore
                    f['baseline_fit'] = float(mm.group(2))
            elif msg.startswith('champion re-eval on current pool:'):
                f['champion_reeval'] = float(msg.split(':')[-1])
            elif STANDING_RE.search(msg):
                mm = STANDING_RE.search(msg)
                f['beats'] = mm.group(1) == 'True'
                f['margin'] = float(mm.group(2))
                f['sprt_decision'] = mm.group(3)
                f['sprt_n'] = int(mm.group(4))
                f['sprt_llr'] = float(mm.group(5))
                f['sprt_sigma'] = float(mm.group(6))
                f['streak'] = (int(mm.group(7)), int(mm.group(8)))
            elif msg.startswith('pareto gate:'):
                try:
                    f['pareto_gate'] = ast.literal_eval(msg.split('pareto gate:', 1)[1])
                except Exception:
                    pass  # scanner:ignore
            elif msg.startswith('holdout:') and 'cooldown' not in msg:
                try:
                    f['holdout'] = ast.literal_eval(msg.split('holdout:', 1)[1])
                except Exception:
                    pass  # scanner:ignore
            elif msg.startswith('holdout cooldown:'):
                f['holdout_cooldown'] = True
            elif msg.startswith('promotion BLOCKED by'):
                blocked.append(msg.split('BLOCKED by', 1)[1].strip())
            elif msg.startswith('PROMOTED to'):
                f['promoted'] = True
            elif msg.startswith('SPRT rejected'):
                f['sprt_rejected'] = True
            elif QD_RE.search(msg):
                mm = QD_RE.search(msg)
                f['qd'] = {'filled': int(mm.group(1)), 'total': int(mm.group(2)),
                           'coverage': float(mm.group(3)), 'score': float(mm.group(4)),
                           'best': float(mm.group(5)), 'added': int(mm.group(6))}
            elif ARM_RE.search(msg):
                mm = ARM_RE.search(msg)
                f.setdefault('arm', {})['name'] = mm.group(1)
                f['arm']['outcome'] = mm.group(2)
            elif msg.startswith('checkpoint saved:'):
                mm = re.search(r'gen (\d+) best=([-\d.]+)', msg)
                if mm:
                    f['ckpt'] = (int(mm.group(1)), float(mm.group(2)))
            elif msg.startswith('canary:'):
                f['canary'] = msg.split('canary:', 1)[1].strip()[:60]
            elif msg.startswith('FATAL'):
                f['fatal'] = True
    if gens:
        f['generations'] = len(gens)
        f['trajectory'] = [g[1] for g in gens]
        f['first_gen_fit'] = gens[0][1]
        f['last_gen_fit'] = gens[-1][1]
    f['blocked'] = blocked

    # Phase cost: attribute each inter-line gap to the stage on the later line.
    for (t0, m0), (t1, m1) in zip(stamps, stamps[1:]):
        d = (time.mktime(time.strptime(t1, '%Y-%m-%dT%H:%M:%S'))
             - time.mktime(time.strptime(t0, '%Y-%m-%dT%H:%M:%S')))
        if d <= 0:
            continue
        phases.append((stage_of(m1), d))
    f['phases'] = phases
    f['wall_s'] = (time.mktime(time.strptime(stamps[-1][0], '%Y-%m-%dT%H:%M:%S'))
                   - time.mktime(time.strptime(stamps[0][0], '%Y-%m-%dT%H:%M:%S'))) \
        if stamps else 0.0
    return f


def stage_of(msg):
    if msg.startswith('gen ') or msg.startswith('converged'):
        return 'ga_search'
    if 'arm:' in msg:
        return 'second_arm'
    if msg.startswith('h of') or msg.startswith('tpe seeds') or msg.startswith('qd seed:'):
        return 'seeding'
    if msg.startswith('pareto gate') or msg.startswith('multi-objective'):
        return 'pareto_refine'
    if msg.startswith('holdout'):
        return 'holdout_gate'
    if msg.startswith('promotion standing') or msg.startswith('SPRT'):
        return 'sprt_gate'
    if msg.startswith('production baseline') or msg.startswith('BEST'):
        return 'baseline_eval'
    if msg.startswith('qd archive'):
        return 'qd_update'
    if msg.startswith('checkpoint'):
        return 'checkpoint'
    if msg.startswith('canary'):
        return 'canary_check'
    if msg.startswith('meta:'):
        return 'meta'
    if msg.startswith('seed=') or msg.startswith('strategy='):
        return 'startup'
    return 'other'


def load_artifacts():
    """evolution_result rows indexed by run_seed."""
    try:
        from CORE.local_memory import get_memory_store
        rows = get_memory_store().query_memories(event_type='evolution_result', limit=400)
    except Exception as e:  # noqa: BLE001
        print('store unavailable: %s' % str(e)[:160])
        return {}
    out = {}
    for r in rows:
        d = r.get('data', {})
        if isinstance(d, str):
            try:
                d = json.loads(d)
            except Exception:
                continue
        seed = d.get('seed')
        if seed is not None:
            out[int(seed)] = d
    return out


def median(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 4) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rawdir', default=RAWDIR)
    ap.add_argument('--out', default=OUTJSON)
    ap.add_argument('--report', default='')
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.rawdir, '*.log')))
    runs = [parse_log(p) for p in files]
    runs = [r for r in runs if 'seed' in r]
    arts = load_artifacts()

    # ---- aggregates -------------------------------------------------------
    n = len(runs)
    beats = [r for r in runs if r.get('beats')]
    blocked = Counter(b for r in runs for b in r['blocked'])
    sprt = Counter(r.get('sprt_decision') for r in runs if r.get('sprt_decision'))
    gens = Counter(r.get('generations') for r in runs if r.get('generations'))
    margins = [r['margin'] for r in runs if 'margin' in r]
    llrs = [r['sprt_llr'] for r in runs if 'sprt_llr' in r]
    sigmas = [r['sprt_sigma'] for r in runs if 'sprt_sigma' in r]
    bases = [r['baseline_fit'] for r in runs if 'baseline_fit' in r]
    arms = Counter((r.get('arm') or {}).get('outcome', 'none') for r in runs)
    pool_ids = Counter(a.get('pool_id') for a in arts.values())
    era_sizes = Counter(pool_ids.values())

    phase_tot = defaultdict(float)
    phase_n = Counter()
    for r in runs:
        for stg, d in r['phases']:
            phase_tot[stg] += d
            phase_n[stg] += 1

    # alert objective vs its own floor (is the pareto floor binding?)
    alert_gaps = []
    for r in runs:
        pg = r.get('pareto_gate') or {}
        if pg.get('cand_alert') is not None and pg.get('alert_floor') is not None:
            alert_gaps.append(round(float(pg['cand_alert']) - float(pg['alert_floor']), 4))

    # trajectory shape: best flat while mean moves == plateau (EV-8)
    plateaus = 0
    for r in runs:
        t = r.get('trajectory')
        if t and len(t) > 2 and max(t) == min(t):
            plateaus += 1

    summary = {
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'cycles': n,
        'matched_artifacts': sum(1 for r in runs if r['seed'] in arts),
        'promoted_in_batch': sum(1 for r in runs if r.get('promoted')),
        'promoted_in_store': sum(1 for a in arts.values() if a.get('promoted')),
        'fatal': sum(1 for r in runs if r.get('fatal')),
        'wall_s_median': median([r['wall_s'] for r in runs]),
        'wall_s_total': round(sum(r['wall_s'] for r in runs), 1),
        'beats_rate': round(len(beats) / n, 4) if n else None,
        'sprt_decisions': dict(sprt),
        'blocked_by': dict(blocked),
        'generations_used': dict(sorted(gens.items(), key=lambda kv: (kv[0] is None, kv[0]))),
        'converged_early': sum(1 for r in runs if 'converged_at' in r),
        'flat_best_trajectory': plateaus,
        'margin_median': median(margins),
        'margin_min': round(min(margins), 4) if margins else None,
        'margin_max': round(max(margins), 4) if margins else None,
        'margin_stdev': round(st.pstdev(margins), 4) if len(margins) > 1 else None,
        'sprt_llr_median': median(llrs),
        'sprt_llr_max': round(max(llrs), 2) if llrs else None,
        'sprt_sigma_median': median(sigmas),
        'sprt_sigma_min': round(min(sigmas), 6) if sigmas else None,
        'baseline_drift': round(max(bases) - min(bases), 4) if bases else None,
        'baseline_first_last': (bases[0], bases[-1]) if bases else None,
        'arm_outcomes': dict(arms),
        'eras_in_batch': len(pool_ids),
        'era_reuse_sizes': dict(sorted(era_sizes.items(), key=lambda kv: (kv[0] is None, kv[0]))),
        'qd_coverage_last': runs[-1].get('qd', {}).get('coverage') if runs else None,
        'phase_seconds_total': {k: round(v, 1) for k, v in
                                sorted(phase_tot.items(), key=lambda kv: -kv[1])},
        'phase_share_pct': {k: round(100.0 * v / max(1e-9, sum(phase_tot.values())), 1)
                            for k, v in sorted(phase_tot.items(), key=lambda kv: -kv[1])},
        'alert_floor_gap_median': median(alert_gaps),
        'alert_floor_violations': sum(1 for g in alert_gaps if g < 0),
        'runs': runs,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp = args.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    os.replace(tmp, args.out)
    print('wrote %s' % args.out)

    rp = args.report or os.path.join(
        ROOT, 'EVOLUTION_50RUN_ANALYSIS_%s.md' % time.strftime('%Y%m%d'))
    with open(rp, 'w', encoding='utf-8') as f:
        f.write(render(summary))
    print('wrote %s' % rp)
    return 0


def render(s):
    L = []
    A = L.append
    A('# EVOLUTION 50-RUN ANALYSIS — %s' % s['generated'][:10])
    A('')
    A('Evidence: %d back-to-back invocations of the production entrypoint '
      '(`scripts/evolution_cycle.py`, free-threaded interpreter) via '
      '`scripts/run_evolution_n.py`, analysed from the pipeline\'s own '
      'timestamped stdout (`logs/evolution_runs/`) and the `evolution_result` '
      'rows it writes to the live store. Regenerate with '
      '`python scripts/analyze_evolution_runs.py`.' % s['cycles'])
    A('')
    # This file is regenerated wholesale on every run, so hand-written analysis
    # must not live in it - point at the companion doc instead.
    A('> Hand-written analysis (gaps, fixes, regressions) is NOT kept here: this')
    A('> file is regenerated on every analysis run. See')
    A('> `EVOLUTION_50RUN_GAPS_AND_FIXES.md` for the findings that accompany it.')
    A('')
    A('## 1. Headline numbers')
    A('')
    A('| Signal | Value |')
    A('|---|---|')
    A('| Cycles analysed | %d |' % s['cycles'])
    A('| Matched `evolution_result` rows | %d |' % s['matched_artifacts'])
    A('| Fatal cycles | %d |' % s['fatal'])
    A('| Median cycle wall time | %ss |' % s['wall_s_median'])
    A('| Promotions (this batch) | %d |' % s['promoted_in_batch'])
    A('| `beats_baseline` rate | %s |' % s['beats_rate'])
    A('| SPRT decisions | %s |' % s['sprt_decisions'])
    A('| Blocked by gate | %s |' % (s['blocked_by'] or '{}'))
    A('| Generations used | %s |' % s['generations_used'])
    A('| Converged early (<15 gens) | %d |' % s['converged_early'])
    A('| Flat best-trajectory cycles | %d |' % s['flat_best_trajectory'])
    A('| Margin (median / min / max) | %s / %s / %s |' % (
        s['margin_median'], s['margin_min'], s['margin_max']))
    A('| SPRT LLR (median / max) | %s / %s |' % (s['sprt_llr_median'], s['sprt_llr_max']))
    A('| SPRT sigma (median / min) | %s / %s |' % (s['sprt_sigma_median'], s['sprt_sigma_min']))
    A('| Baseline drift inside batch | %s (%s) |' % (
        s['baseline_drift'], s['baseline_first_last']))
    A('| Pool eras in batch | %d %s |' % (s['eras_in_batch'], s['era_reuse_sizes']))
    A('| Second-arm outcomes | %s |' % s['arm_outcomes'])
    A('| QD coverage (final) | %s |' % s['qd_coverage_last'])
    A('')
    A('## 2. Where the wall-clock goes')
    A('')
    A('| Stage | Total s | Share |')
    A('|---|---:|---:|')
    for k, v in s['phase_seconds_total'].items():
        A('| %s | %.1f | %s%% |' % (k, v, s['phase_share_pct'][k]))
    A('')
    A('## 3. Alert-objective margin over its own floor')
    A('')
    A('Median `cand_alert - alert_floor` = %s; violations = %d.'
      % (s['alert_floor_gap_median'], s['alert_floor_violations']))
    A('')
    A('## 4. Per-cycle records')
    A('')
    A('| # | seed | gens | margin | SPRT | streak | holdout | pareto | arm | promoted | blocked |')
    A('|---|---:|---:|---:|---|---:|---|---|---|---|---|')
    for r in s['runs']:
        ho = r.get('holdout') or {}
        ho_s = 'cooldown' if r.get('holdout_cooldown') else (
            ('pass' if ho.get('passed') else 'fail') if ho else '-')
        A('| %s | %s | %s | %s | %s(n=%s) | %s | %s | %s | %s | %s | %s |' % (
            r.get('run', ''), r.get('seed'), r.get('generations'), r.get('margin'),
            r.get('sprt_decision'), r.get('sprt_n'), r.get('streak'),
            ho_s, (r.get('pareto_gate') or {}).get('source', '-'),
            (r.get('arm') or {}).get('outcome', '-'),
            'YES' if r.get('promoted') else '', ', '.join(r.get('blocked', []))))
    A('')
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    sys.exit(main())
