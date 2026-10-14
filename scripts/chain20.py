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
#: rc recorded when a step does not return. The log line's `rc=` field is read
#: as a code, so it has to BE one -- it used to print `rc=FAIL`, a verdict word
#: in a field named rc, and discarded the exception text, so a timed-out round
#: and a crashed round looked identical and neither left a code to grep for.
RC_TIMEOUT = 124
RC_EXC = 127


def log(msg):
    line = '%s %s' % (time.strftime('%Y-%m-%dT%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def step(name, args, binary=None):
    t0 = time.time()
    rc = None
    try:
        p = subprocess.run([binary or PY] + args, capture_output=True,
                           text=True, timeout=STEP_TIMEOUT,
                           cwd=r'C:\Users\clint\azazael', encoding="utf-8", errors="replace")
        rc = p.returncode
        tail = ((p.stdout or '') + (p.stderr or '')).strip().splitlines()
        tail = tail[-1][-160:] if tail else ''
    except subprocess.TimeoutExpired as e:
        # The partial output survives the timeout; keep it as the evidence of
        # WHERE the step hung instead of replacing it with the word TIMEOUT.
        part = (e.stdout or '') + (e.stderr or '')
        if isinstance(part, bytes):
            part = part.decode('utf-8', 'replace')
        rc = RC_TIMEOUT
        tail = 'TIMEOUT after %ss :: %s' % (
            STEP_TIMEOUT, part.strip().replace('\n', ' ')[-160:])
    except Exception as e:
        rc = RC_EXC
        tail = 'EXC %s: %s' % (type(e).__name__, str(e)[:120])
    log('%s rc=%s %.0fs :: %s' % (name, rc, time.time() - t0, tail))
    return rc == 0


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