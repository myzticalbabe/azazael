"""Scheduled dream cycle: recall -> dream (3 episodes) -> evaluate -> persist.

Never auto-integrates (no policy application without review).
Run every 5 minutes via Task Scheduler (Azazael-DreamCycle).
"""
import json
import sys

sys.path.insert(0, 'C:/Users/clint/azazael/src')
from CORE.WORMS.expansion.dreaming import DreamingModule

dm = DreamingModule()
out = dm.run_dreaming_pipeline(num_episodes=3, auto_integrate=False)
print(json.dumps({
    'dream_count': out.get('dream_count'),
    'duration_ms': out.get('duration_ms'),
    'timestamp': out.get('timestamp'),
}, default=str))
