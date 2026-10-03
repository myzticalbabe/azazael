---
name: azazael-tool-environ-updater
description: environ_updater — environment/PATH reconciliation for toolbelt scripts. Use when a tool runs standalone but fails under the fleet because env vars or PATH entries differ.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: false
---
# environ_updater

Location: `azazael/src/SCRIPTS/environ_updater.py`

## When to use
- Reconcile PATH/env between interactive shells and fleet runs.
- Fix "works standalone, fails in worm" environment drift.

## How to run
```
python azazael/src/SCRIPTS/environ_updater.py
```

## Notes
- Capability worm: `EnvironUpdaterWorm` (TOOLBELTZ).
