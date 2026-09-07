"""Metacognition cycle: feed -> observe -> analyze per worm -> adapt worst.

Reads recent cluster execution rows, observes outcomes into MetaCognitionWorm,
runs per-worm analysis (which persists confidence models), adapts the worst
offender, records a cycle summary row. Actuation beyond scoring is
human-approved (no config writes here).
"""
import sys
sys.path.insert(0, 'C:/Users/clint/azazael/src')

from CORE.WORMS.expansion.meta_cognition import MetaCognitionWorm
from CORE.local_memory import get_memory_store

mc = MetaCognitionWorm()
store = get_memory_store()

recent = store.query_memories(event_type='clusterwormz_execute_complete',
                              limit=30) if store else []
fed = 0
seen = {}
for r in recent:
    data = r.get('data', {}) or {}
    if isinstance(data, str):
        continue
    wt = str(data.get('cluster_type', 'unknown'))
    ok = not data.get('fail')
    mc.observe(worm_type=wt,
               action='cluster_execute',
               outcome='success' if ok else 'error',
               context={'cluster_id': data.get('cluster_id', '')})
    st = seen.setdefault(wt, {'ok': 0, 'err': 0})
    st['ok' if ok else 'err'] += 1
    fed += 1

adapted = None
adapted_worm = None
if fed:
    for wt in seen:
        mc.analyze_patterns(worm_type=wt)
    worst = max(seen, key=lambda w: seen[w]['err'] / max(1, seen[w]['err'] + seen[w]['ok']))
    if seen[worst]['err']:
        adapted_worm = worst
        adapted = mc.adapt_strategy(worst, 'default')

if store is not None:
    try:
        store.record_event(source='MetaCognitionWorm', event_type='mc_cycle',
                           data={'fed': fed, 'worm': adapted_worm,
                                 'adapted': bool(adapted and adapted.get('should_adapt')),
                                 'recommendation': (adapted or {}).get('recommended_strategy', 'none')},
                           severity='info', tags=['metacognition', 'cycle'])
    except Exception as e:
        print('cycle record failed:', e)

print(f'fed={fed} worm={adapted_worm} adapted={bool(adapted and adapted.get("should_adapt"))} '
      f'rec={adapted.get("recommended_strategy") if adapted else "none"}', flush=True)

import os
import time
os.makedirs(r'C:\Users\clint\azazael\logs', exist_ok=True)
with open(r'C:\Users\clint\azazael\logs\metacog_cycle.log', 'a', encoding='utf-8') as f:
    f.write('%s fed=%d worm=%s adapted=%s rec=%s\n' % (
        time.strftime('%Y-%m-%dT%H:%M:%S'), fed, adapted_worm,
        bool(adapted and adapted.get('should_adapt')),
        (adapted or {}).get('recommended_strategy', 'none')))
