---
name: azazael-tool-learning-monitor
description: monitor_learning — learning-loop dashboard monitor (live window, LAN web page, rolling log). Use to watch evolution reward/fitness cycles while they run.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: false
---
# monitor_learning

Location: `src/SCRIPTS/monitor_learning.py`

## When to use
- Watch the learning loop live (reward plot, cycle cadence).
- Serve the LAN status page for the learning dashboard.

## How to run
```
python src/SCRIPTS/monitor_learning.py
```

## Notes
- Companion: `src/SCRIPTS/generate_telemetry.py` for RULE 0Z-F counters.
- Capability worm: `MonitorLearningWorm` (TOOLBELTZ).
