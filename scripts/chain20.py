"""Run the entire chain 20x: dream + metacog + training rotation, sequentially.

Each step is the same entrypoint the scheduler uses; per-script
single-instance locks serialize with scheduled fires (which SKIP while
a chain step holds its lock). Progress to chain20.log. Rerun-safe:
each round is independent; failures logged, chain continues.
"""
import subprocess
import time

PY = r'C:\Users\clint\AppData\Local\Programs\Python\Python315\python.exe'
PY_FT = r'C:\Users\clint\AppData\Local\Programs\Python\Python315\python3.15t.exe'
SCRIPTS = r'C:\Users\clint\azazael\scripts'
LOG = r'C:\Users\clint\azazael\logs\chain20.log'
ROUNDS = 20
STEP_TIMEOUT = 900


def log(msg):
    line = '%s %s' % (time.strftime('%Y-%m-%dT%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def step(name, args, binary=None):
    t0 = time.time()
    try:
        p = subprocess.run([binary or PY] + args, capture_output=True,
                           text=True, timeout=STEP_TIMEOUT,
                           cwd=r'C:\Users\clint\azazael', encoding="utf-8", errors="replace")
        ok = p.returncode == 0
        tail = ((p.stdout or '') + (p.stderr or '')).strip().splitlines()
        tail = tail[-1][-160:] if tail else ''
    except Exception as e:
        ok, tail = False, 'EXC %s' % str(e)[:120]
    log('%s rc=%s %.0fs :: %s' % (name, 'ok' if ok else 'FAIL',
                                  time.time() - t0, tail))
    return ok


def main():
    ok = fail = 0
    for i in range(1, ROUNDS + 1):
        r0 = time.time()
        log('--- round %d/%d ---' % (i, ROUNDS))
        for name, script, extra, binary in (
                ('dream', 'dream_cycle.py', [], None),
                ('metacog', 'metacog_cycle.py', [], None),
                ('train', 'run_training_orchestrator.py', [], None),
                ('evolution', 'evolution_cycle.py', [], PY_FT)):
            if step('%s[%d]' % (name, i), [SCRIPTS + '\\' + script] + extra,
                    binary=binary):
                ok += 1
            else:
                fail += 1
        log('round %d done in %.0fs (ok=%d fail=%d)' % (i, time.time() - r0, ok, fail))
    log('CHAIN20 DONE ok=%d fail=%d' % (ok, fail))


if __name__ == '__main__':
    main()