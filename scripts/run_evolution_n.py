#!/usr/bin/env python3
"""Run the FULL evolution pipeline N times back-to-back and record outcomes.

Purpose (2026-09-11): the audit trail only ever sees the pipeline at its
scheduled 5-minute cadence, interleaved with host sleep and other cycles. This
runner fires `evolution_cycle.py` in a tight loop so a single sitting produces
a statistically usable sample of cycles (denominators, gate block rates, arm
win rates, era churn) that can then be analysed from one directory.

It is the SAME entrypoint the scheduler uses (`scripts/evolution_cycle.py`, via
the free-threaded interpreter like `run_evolution_cycle_314t.bat`), so what it
measures is production behaviour, not a harness. Consequences are therefore
real: cycles may promote genomes into `state/evolved_rl_params.json` and arm
the auto-canary, exactly as the scheduled loop does. The pipeline's own gates
(SPRT -> pareto -> holdout -> canary) are the guardrails, unchanged.

Handling the scheduler: `_acquire_cycle_lock()` is non-blocking, so if the
scheduled task (or another chain step) holds the lock our run is SKIPPED with a
log line and no seed. A skipped attempt is retried (bounded) so N means N real
cycles, not N attempts.

Outputs:
  logs/run_evolution_n.log          one line per attempt (append-only)
  logs/run_evolution_n.json         structured per-run records (atomic rewrite)
  logs/evolution_runs/<n>-<seed>.log  full stdout of each real cycle

Usage:
  python scripts/run_evolution_n.py --runs 50
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

PY_FT = r'C:\Users\clint\AppData\Local\Programs\Python\Python314\python3.14t.exe'
CYCLE = os.path.join(HERE, 'evolution_cycle.py')
LOG = os.path.join(ROOT, 'logs', 'run_evolution_n.log')
OUT = os.path.join(ROOT, 'logs', 'run_evolution_n.json')
RAWDIR = os.path.join(ROOT, 'logs', 'evolution_runs')

SEED_RE = re.compile(r'seed=(\d+)')
GEN_RE = re.compile(r'\bgen (\d+): best=([-0-9.]+)')

# Lines worth lifting out of a run's stdout for the analysis pass. Keyed by the
# stable prefix the pipeline logs; the first match wins.
INTEREST_PREFIXES = (
    'strategy=', 'meta:', 'production baseline:', 'BEST:', 'BEST parts:',
    'promotion standing:', 'pareto gate:', 'holdout:', 'PROMOTED to',
    'promotion BLOCKED', 'SPRT rejected', 'champion re-eval on current pool:',
    'qd archive:', 'checkpoint saved:', 'converged at gen', 'canary:',
    'holdout cooldown:', 'arm:', 'CMA arm:', 'FATAL',
    # PROTEUS Phase C: the oracle gate decision and any model retrain it triggered.
    'oracle gate:', 'oracle model',
    # PROTEUS Phase D/E (2026-09-12): Cranium / Circulation / Morph. A veto or
    # a rescue is only attributable after the fact if the line was captured.
    'cranium:', 'CRANIUM rescue', 'CRANIUM veto',
    'circulation:', 'circulation feedback:', 'morph:',
)


def log(msg):
    line = '%s %s' % (time.strftime('%Y-%m-%dT%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def write_json(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def run_once(timeout):
    """One pipeline invocation. Returns (record, full_stdout)."""
    t0 = time.time()
    try:
        p = subprocess.run(
            [PY_FT, CYCLE], capture_output=True, text=True,
            timeout=timeout, cwd=ROOT)
        rc, out = p.returncode, (p.stdout or '') + (p.stderr or '')
    except subprocess.TimeoutExpired as e:
        rc = 'timeout'
        out = (e.stdout or '') if isinstance(e.stdout, str) else ''
    except Exception as e:  # noqa: BLE001
        rc, out = 'exc', 'EXCEPTION %s' % str(e)[:200]

    seeds = SEED_RE.findall(out)
    seed = int(seeds[-1]) if seeds else None
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    interesting = []
    for ln in lines:
        for pref in INTEREST_PREFIXES:
            if ln.split(' ', 1)[-1].startswith(pref) or pref in ln:
                interesting.append(ln)
                break
    closed = [ln for ln in lines if ln.startswith('closed')]
    lock_stamp = [ln for ln in lines if 'holds the lock' in ln]
    # 'closed' is the pipeline's own lock-close banner; either shape means the
    # lock was held elsewhere and this attempt produced no cycle.
    skipped = seed is None and (bool(lock_stamp) or not lines)
    return {
        'rc': rc,
        'seed': seed,
        'skipped': skipped,
        'seconds': round(time.time() - t0, 1),
        'generations': len(re.findall(r'\bgen \d+: best=', out)),
        'promoted': 'PROMOTED to' in out,
        'blocked': sorted({ln.split('BLOCKED by')[1].strip()
                           for ln in lines if 'BLOCKED by' in ln}),
        'sprt': next((ln.split('sprt=', 1)[1].split(')')[0]
                      for ln in lines if 'sprt=' in ln), ''),
        'interesting': interesting,
        'last': lines[-1][:200] if lines else '',
    }, out


def main():
    ap = argparse.ArgumentParser(description='Run the evolution pipeline N times')
    ap.add_argument('--runs', type=int, default=50)
    ap.add_argument('--timeout', type=int, default=900, help='seconds per cycle')
    ap.add_argument('--max-retries', type=int, default=5,
                    help='attempts allowed when a run is lock-skipped')
    args = ap.parse_args()

    os.makedirs(RAWDIR, exist_ok=True)
    records = []
    write_json(OUT, {'started': time.strftime('%Y-%m-%dT%H:%M:%S'),
                     'runs': args.runs, 'records': records})
    log('RUN%s START (interpreter=%s)' % (args.runs, os.path.basename(PY_FT)))

    done = 0
    attempt = 0
    t_start = time.time()
    while done < args.runs:
        attempt += 1
        rec, out = run_once(args.timeout)
        rec['attempt'] = attempt
        rec['run'] = done + 1
        if rec['skipped'] and rec['rc'] == 0:
            # Lock held by a scheduled fire: not a cycle, do not count it.
            log('attempt %d SKIPPED (lock held) %.0fs' % (attempt, rec['seconds']))
            if attempt - done > args.max_retries + done:
                # give up on this slot rather than spin forever
                log('giving up on run %d after %d skipped attempts'
                    % (done + 1, args.max_retries))
                done += 1
            time.sleep(2.0)
            continue
        done += 1
        rec['run'] = done
        if rec['seed'] is not None:
            with open(os.path.join(RAWDIR, '%03d-%d.log' % (done, rec['seed'])),
                      'w', encoding='utf-8') as f:
                f.write(out)
        records.append(rec)
        write_json(OUT, {'started': time.strftime('%Y-%m-%dT%H:%M:%S'),
                         'runs': args.runs, 'records': records})
        log('run %d/%d seed=%s rc=%s %.0fs gens=%s promoted=%s %s' % (
            done, args.runs, rec['seed'], rec['rc'], rec['seconds'],
            rec['generations'], rec['promoted'], rec['last'][-90:]))

    elapsed = time.time() - t_start
    summary = {
        'finished': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'runs': args.runs,
        'cycles': len(records),
        'promoted': sum(1 for r in records if r['promoted']),
        'blocked_shapes': sorted({b for r in records for b in r['blocked']}),
        'avg_seconds': round(sum(r['seconds'] for r in records) / max(1, len(records)), 1),
        'elapsed_minutes': round(elapsed / 60.0, 1),
        'records': records,
    }
    write_json(OUT, summary)
    log('RUN%s DONE cycles=%d promoted=%d avg=%.1fs total=%.1fmin' % (
        args.runs, summary['cycles'], summary['promoted'],
        summary['avg_seconds'], summary['elapsed_minutes']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
