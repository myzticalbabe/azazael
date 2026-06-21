#!/usr/bin/env python3
"""Quick verification: execute_all on key categories."""
import sys, os, time
sys.path.insert(0, 'src')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from CORE.worm_registry import discover_worms, get_all_categories, reset_registry
reset_registry()
discover_worms()

from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

cats = ['orchestration', 'utility', 'monitor', 'security', 'migration', 'backup']
t0 = time.time()
total_ok = total_fail = 0

for c in cats:
    ct0 = time.time()
    try:
        cluster = ClusterWORMZ.build_from_nature(c)
        results = cluster.execute_all()
        dt = time.time() - ct0
        n_ok = sum(1 for r in results if r.get('success'))
        n_fail = len(results) - n_ok
        total_ok += n_ok
        total_fail += n_fail
        s = 'OK' if n_fail == 0 else f'{n_fail} FAIL'
        print(f'{c:15s}: {n_ok}/{len(results)} ({s}) in {dt:.1f}s')
        for r in results:
            if not r.get('success'):
                err = str(r.get('error','?'))[:120]
                print(f'  FAIL {r.get("name","?")}: {err}')
    except Exception as e:
        print(f'{c:15s}: ERROR: {str(e)[:150]}')

print(f'\nTOTAL: {total_ok}/{total_ok+total_fail} OK in {time.time()-t0:.1f}s')
