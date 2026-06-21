#!/usr/bin/env python3
"""Run execute_all() per category, printing progress as it goes."""
import sys, os, time
sys.path.insert(0, 'src')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from CORE.worm_registry import discover_worms, get_all_categories, reset_registry
print("[1/3] Discovering worms...", flush=True)
reset_registry()
discover_worms()

from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
cats = sorted(get_all_categories())
print(f"[2/3] Found {len(cats)} categories. Running execute_all() sequentially...\n", flush=True)

total_ok = 0
total_fail = 0
failures = []
start_all = time.time()

for i, c in enumerate(cats):
    t0 = time.time()
    try:
        cluster = ClusterWORMZ.build_from_nature(c)
        results = cluster.execute_all()
        n_ok = sum(1 for r in results if r.get('success'))
        n_fail = len(results) - n_ok
        total_ok += n_ok
        total_fail += n_fail
        elapsed = time.time() - t0
        status = 'OK' if n_fail == 0 else f'{n_fail} FAIL'
        print(f'[{i+1}/{len(cats)}] {c:15s}: {n_ok}/{len(results)} OK ({status})  [{elapsed:.1f}s]', flush=True)
        for r in results:
            if not r.get('success'):
                err = str(r.get('error', '?'))[:100]
                print(f'       FAIL {r.get("name", "?"):30s}: {err}', flush=True)
                failures.append((c, r.get('name', '?'), err))
    except Exception as e:
        elapsed = time.time() - t0
        print(f'[{i+1}/{len(cats)}] {c:15s}: BUILD ERROR - {e}  [{elapsed:.1f}s]', flush=True)

total_time = time.time() - start_all
print(f'\n{"="*60}')
print(f'[3/3] COMPLETE in {total_time:.1f}s')
print(f'TOTAL: {total_ok} OK, {total_fail} FAIL across {len(cats)} categories')
if failures:
    failing_cats = set(f[0] for f in failures)
    print(f'Categories with failures: {len(failing_cats)}/17: {sorted(failing_cats)}')
else:
    print('ALL WORMS PASS!')
