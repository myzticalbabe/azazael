"""Metacognition cycle: feed recent worm executions -> observe -> adapt.

Reads recent cluster execution rows, observes outcomes into MetaCognitionWorm,
adapts strategy for the worst offender, records a cycle summary row.
Actuation beyond scoring is human-approved (no config writes here).
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
for r in recent:
    data = r.get('data', {}) or {}
    if isinstance(data, str):
        continue
    mc.observe(worm_type=str(data.get('cluster_type', 'unknown')),
               action='cluster_execute',
               outcome='error' if data.get('fail') else 'success',
               context={'cluster_id': data.get('cluster_id', '')})
    fed += 1

adapted = None
if fed:
    adapted = mc.adapt_strategy('system', 'default')

if store is not None:
    try:
        store.record_event(source='MetaCognitionWorm', event_type='mc_cycle',
                           data={'fed': fed, 'adapted': bool(adapted and adapted.get('should_adapt')),
                                 'recommendation': (adapted or {}).get('recommended_strategy', 'none')},
                           severity='info', tags=['metacognition', 'cycle'])
    except Exception as e:
        print('cycle record failed:', e)

print(f'fed={fed} adapted={bool(adapted and adapted.get("should_adapt"))} '
      f'rec={adapted.get("recommended_strategy") if adapted else "none"}')
