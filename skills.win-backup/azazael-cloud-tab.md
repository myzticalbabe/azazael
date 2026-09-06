---
name: azazael-cloud-tab
description: Extracted Cloud inference tab module for Inference Studio — reduces God Object anti-pattern
metadata:
  category: architecture
  project: azazael
  version: 1.0.0
  created: 2026-06-07
---

# Azazael Cloud Tab Module

## Overview
`CORE/inference/cloud_tab.py` — Self-contained Cloud Inference tab extracted from `AZAZAEL_Inference_Studio.py`. Reduces the God Object anti-pattern by isolating all cloud provider UI and API logic into its own module.

## Quick Start
```python
from CORE.inference.cloud_tab import CloudTab

cloud_tab = CloudTab(
    parent=tab_frame,
    theme=THEME,
    status_callback=self._set_status,
    dot_callback=self._draw_dot,
    emotion_engine=emotion,
)

# Use from Inference Studio
prompt = cloud_tab.get_prompt()
cloud_tab.launch(max_tokens=1024, temperature=0.7)
cloud_tab.set_prompt("Explain quantum computing.")
```

## Features
- Provider selector dropdown with auto-discovery
- Background provider refresh (avoids 38s startup freeze)
- Prompt input with default text
- Response output with error display
- Thread-safe API calls via background threads
- ASCII-safe output (strips non-ASCII for Windows console)
- Emotional emoji reactions integrated
- Safe token/temperature clamping

## Architecture
```
AZAZAEL_Inference_Studio.py
    └── CloudTab (delegation, not inheritance)
         ├── Provider selector (Combobox)
         ├── Prompt input (Text widget)
         ├── Response output (Text widget)
         ├── Launch button -> background thread -> providers API
         └── _finish() -> main thread UI update
```

## Why Extraction Matters
Before: 1,949-line God Object with Cloud tab logic inline (~130 lines)
After: Inference Studio delegates to CloudTab (~15 lines), Cloud tab is 200 lines in its own module

## Related Skills
- `azazael-inference-providers` — 11 cloud inference providers
- `azazael-inference-integration` — Wiring providers into Studio
- `azazael-secrets-manager` — Unified API key management
