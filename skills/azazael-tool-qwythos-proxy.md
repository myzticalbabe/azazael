---
name: azazael-tool-qwythos-proxy
description: qwythos_proxy — local HTTP proxy tool in azazael/src/TOOLS. Use when traffic inspection, request interception, or proxy-mediated downloads are needed.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: false
---
# qwythos_proxy

Location: `azazael/src/TOOLS/qwythos_proxy.py`

## When to use
- Intercept/inspect HTTP traffic from local tooling.
- Mediate downloads or API calls through a local proxy hop.

## How to run
```
python azazael/src/TOOLS/qwythos_proxy.py --help
```

## Notes
- Capability-probe worm: `QwythosProxyWorm` in `src/CORE/WORMS/TOOLBELTZ.py`.
- Verify availability with the worm's `scan()` before directing runs.
