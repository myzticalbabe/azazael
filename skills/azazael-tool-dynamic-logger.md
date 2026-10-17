---
name: azazael-tool-dynamic-logger
description: AzazaelDynamicLogger — leveled logging helper used by toolbelt modules. Use when adding logging to azazael tools or debugging tool output capture.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: false
---
# AzazaelDynamicLogger

Locations: `src/AZAZAEL_TOOLKIT/AzazaelDynamicLogger.py`, `src/TOOLS/AzazaelDynamicLogger.py`, `src/UTILITIES/AzazaelDynamicLogger.py` (shared implementation).

## When to use
- Add leveled, file-backed logging to a toolbelt script.
- Capture tool runs for later audit review.

## Notes
- Tested by `src/SCRIPTS/test_dynamic_logging.py`.
- Writes go through the sentinel permit when imported under CORE.
