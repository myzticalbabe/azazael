---
name: azazael-worm-registry-fixes
description: Worm registry module path fixes — how discover_worms() stores module names incorrectly, the 28 affected worms, and the fix pattern
metadata:
  category: architecture
  project: azazael
  priority: high
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Worm Registry Module Path Fixes

> **Context:** The `discover_worms()` function in `worm_registry.py` auto-discovers worm modules from the `CORE/WORMS/` directory. However, modules imported via `sys.path` manipulation (as opposed to dotted-path imports) store `cls.__module__` as the short filename without the package prefix. This causes `importlib.import_module()` calls using the registry's `module` field to fail for 28 worms.

---

## The Bug

When `discover_worms()` imports a module like `CAIN_WORM.py` from `CORE/WORMS/`, it adds the WORMS directory to `sys.path` and calls:

```python
module_name = "CAIN_WORM"  # filename[:-3]
module = importlib.import_module(module_name)
```

Because the module was imported via a flat `sys.path` entry (not a dotted path), the module's `__name__` attribute is just `"CAIN_WORM"` instead of `"CORE.WORDS.CAIN_WORM"`.

When `register_worm()` stores `cls.__module__` in the registry, it stores the short name:
```python
"module": cls.__module__  # "CAIN_WORM" instead of "CORE.WORMS.CAIN_WORM"
```

This causes `worm_health_check.py` and other tools that use `importlib.import_module(module)` with the registry's module field to fail with `ModuleNotFoundError`.

## The 28 Affected Worms

| Worm | Old Module | Fixed Module |
|------|-----------|-------------|
| CainWorm | CAIN_WORM | CORE.WORMS.CAIN_WORM |
| CLOCKZ | CLOCKZ | CORE.WORMS.CLOCKZ |
| ClusterInspector | CLUSTER_INSPECTOR | CORE.WORMS.CLUSTER_INSPECTOR |
| ConcurrencyManager | CONCURRENCY | CORE.WORMS.CONCURRENCY |
| DEPENDZ | DEPENDZ | CORE.WORMS.DEPENDZ |
| DiagnosticWorm | DIAGNOSTIC_WORM | CORE.WORMS.DIAGNOSTIC_WORM |
| DISKZ | DISKZ | CORE.WORMS.DISKZ |
| FastErrorScanner | ERROR_SCAN_WORM | CORE.WORMS.ERROR_SCAN_WORM |
| InferenceSubscriberWorm | INFERENCE_SUBSCRIBER | CORE.WORMS.INFERENCE_SUBSCRIBER |
| InferenceWorm | INFERENCE_WORM | CORE.WORMS.INFERENCE_WORM |
| METAZ | METAZ | CORE.WORMS.METAZ |
| MorphingWorm | MORPHING_WORM | CORE.WORMS.MORPHING_WORM |
| MorphingWormV2 | MORPHING_WORM_V2 | CORE.WORMS.MORPHING_WORM_V2 |
| NETWORXZ | NETWORXZ | CORE.WORMS.NETWORXZ |
| NetworkDiag | NETWORK_DIAG | CORE.WORMS.NETWORK_DIAG |
| NimInferenceWorm | NIM_INFERENCE | CORE.WORMS.NIM_INFERENCE |
| OMNIV2 | OMNI_WORM_V2 | CORE.WORMS.OMNI_WORM_V2 |
| PROCESSZ | PROCESSZ | CORE.WORMS.PROCESSZ |
| ParallelInferenceWorm | PARALLEL_INFERENCE_WORM | CORE.WORMS.PARALLEL_INFERENCE_WORM |
| ReverseTools | REVERSE_TOOLS | CORE.WORMS.REVERSE_TOOLS |
| SMARTDISK | SMARTDISK | CORE.WORMS.SMARTDISK |
| SYSTEMZ_ML | SYSTEMZ_ML | CORE.WORMS.SYSTEMZ_ML |
| SystemZ | SYSTEMZ | CORE.WORMS.SYSTEMZ |
| VideoAnalyzerWorm | VIDEO_ANALYZER_WORM | CORE.WORMS.VIDEO_ANALYZER_WORM |
| WORMZ | WORMZ | CORE.WORMS.WORMZ |
| WORMZ_ML | WORMZ_ML | CORE.WORMS.WORMZ_ML |
| WormFleet | WORM_FLEET | CORE.WORMS.WORM_FLEET |
| DeadLetterQueue | dead_letter_queue | CORE.WORMS.dead_letter_queue |

## Root Cause: `already_has_classes` Skip (v2.0 fix)

The first fix attempt placed the module-name correction **inside** the `for attr_name in dir(module)` inner loop. This failed for ~26 worms that use `@register_worm` directly on their class definitions.

**Why:** When `importlib.import_module("CLOCKZ")` is called, the `@register_worm` decorator fires **during module import**, registering the class with a short module name (e.g., `"CLOCKZ"`). Immediately after import, the `already_has_classes` check detects that this module's classes are already in `WORM_REGISTRY` and **skips the entire `dir(module)` loop** — along with the fix code inside it.

```
import_module("CLOCKZ") → @register_worm fires → WORM_REGISTRY["CLOCKZ"]["module"] = "CLOCKZ"
                          → already_has_classes = True → continue (skip dir() loop!)
                                                             → fix never runs
```

## The Fix — Two-Path Correction (v2.1)

**Path 1 (Post-import fix, runs for ALL modules):** Right after `importlib.import_module()`, before the `already_has_classes` check, scan `WORM_REGISTRY` for entries whose `source_file` matches this module. If any are found with short module names, correct them immediately.

**Path 2 (Inner-loop fix, runs for non-@register_worm modules):** The original per-class fix inside the `for attr_name in dir(module)` loop. Handles classes without `@register_worm` that are discovered via the `hasattr(obj, "VERSION")` check.

```python
module = importlib.import_module(module_name)
full_module_name = f"CORE.WORMS.{module_name}"

# ── Path 1: Fix modules registered during import (via @register_worm) ──
# Must run BEFORE already_has_classes check to catch worms that
# would be skipped by the dir(module) loop.
src_file = getattr(module, "__file__", "")
if src_file:
    src_name = os.path.basename(src_file)
    with _registry_lock:
        for cinfo in WORM_REGISTRY.values():
            if cinfo.get("source_file", "").endswith(src_name):
                cmod = cinfo.get("module", "")
                if cmod and not cmod.startswith("CORE.WORMS."):
                    cinfo["module"] = full_module_name

# ── Path 2: Fix modules discovered via VERSION attribute ──
# (runs inside for attr_name in dir(module) loop)
for attr_name in dir(module):
    ...
    register_fn(obj)
    if attr_name in WORM_REGISTRY:
        current_module = WORM_REGISTRY[attr_name].get("module", "")
        if current_module and not current_module.startswith("CORE.WORMS."):
            WORM_REGISTRY[attr_name]["module"] = full_module_name
```

## Cache Loading Fix (v2.2)

The pickle cache (`.azazael/worm_registry_cache.pkl`) stores class objects directly. When unpickling, Python resolves `sys.path` relative imports — if `CORE/WORMS/` is not on `sys.path`, unpickling fails with `ModuleNotFoundError`. A fix is also applied in the cache-loading path:

```python
if registry:
    with _registry_lock:
        WORM_REGISTRY.update(registry)
        # Fix module names for cache-loaded entries
        for cname, cinfo in WORM_REGISTRY.items():
            cmodule = cinfo.get("module", "")
            csrc = cinfo.get("source_file", "")
            if not cmodule.startswith("CORE.WORMS.") and "CORE" in csrc and "WORMS" in csrc:
                csrc_fixed = csrc.replace("\\", "/")
                if "CORE/WORMS/" in csrc_fixed:
                    idx = csrc_fixed.index("CORE/WORMS/")
                    full_mod = csrc_fixed[idx:].replace(".py", "").replace("/", ".")
                    cinfo["module"] = full_mod
```

This fix runs every time the cache is loaded, ensuring backward compatibility with any cache created before the v2.1 fix.

## Verification

### Fresh discovery (no cache)
```bash
rm -f ~/.azazael/worm_registry_cache.pkl
python -c "
import sys; sys.path.insert(0, 'azazael/src')
from CORE.worm_registry import WORM_REGISTRY, discover_worms
discover_worms()
short = sum(1 for n,i in WORM_REGISTRY.items() 
    if 'CORE' in i.get('source_file','') and 'WORMS' in i.get('source_file','') 
    and not i.get('module','').startswith('CORE.WORMS.'))
print(f'Short names: {short}')
"
```

### Cache path (second call)
```bash
python -c "
import sys; sys.path.insert(0, 'azazael/src')
from CORE.worm_registry import WORM_REGISTRY, discover_worms
n = discover_worms()  # Should return 0 (cache hit)
...
"
```

## Pre-existing Import Issues

Two worm files have import errors unrelated to the module path fix:

| File | Error | Cause |
|------|-------|-------|
| `OS_CONGRUENCY.py` | `register_worm() got an unexpected keyword argument 'version'` | Uses `@register_worm(version="1.0.0")` with invalid parameter. Fixed by removing `version=` kwarg. |
| `CODEX_TOOLS.py` | `No module named 'CAIN_ANALYZER'` | Line 35: `from CAIN_ANALYZER import run_complete_analysis` — module not available on sys.path. Requires creating CAIN_ANALYZER or fixing the import. |

## Related Skills

- `azazael-registry` — Worm registry API (@register_worm, discover_worms)
- `azazael-worms` — All 95 worms catalog
- `azazael-worms-core` — Core infrastructure worms
