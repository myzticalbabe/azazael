# LESSONS — Task C: Fixing __setattr__ Instrumentation for 3.14t

**Task:** Fix RaceConditionDetector's __setattr__ tracing to actually intercept writes
**Date:** June 4, 2026
**Reference:** code-reviewer-deepseek feedback, Python data model

---

## Problem Discovered

The initial `RaceConditionDetector.instrument_worm()` stored a traced `__setattr__` on the worm **instance** dict:

```python
worm_instance.__setattr__ = traced_setattr.__get__(worm_instance, type(worm_instance))
```

This **does not work**. Per the Python data model (PEP 252, `object.__setattr__`):
- `obj.attr = value` calls `type(obj).__setattr__(obj, "attr", value)` — always looked up on the **type**, not the instance
- Instance-dict `__setattr__` entries are **never consulted** for normal attribute writes
- The tracing was silently broken — zero write events would be captured

This was a fundamental misunderstanding of CPython's special method lookup.

## Root Cause

CPython special methods (`__setattr__`, `__getattribute__`, `__init__`, etc.) are looked up on the **type**, bypassing the instance `__dict__`. This is by design — it prevents instance-level overrides from breaking fundamental object behavior.

## Fix: Class-Level Patch + Per-Instance Registry

```python
# 1. Install class-level __setattr__ ONCE per type
def _install_class_tracer(self, worm_type):
    original_setattr = worm_type.__setattr__
    worm_type._rcd_original_setattr = original_setattr

    def traced_class_setattr(obj, name, value):
        # 2. Check per-instance registry — only trace registered instances
        registry = self._setattr_registry.get(worm_type, {})
        entry = registry.get(id(obj))
        if entry is not None and name in entry["shared_attrs"]:
            self._record_access(trace)
        return original_setattr(obj, name, value)

    worm_type.__setattr__ = traced_class_setattr

# 3. Per-instance registry: {type: {id(instance): {"shared_attrs": set, "worm_id": str}}}
# 4. On uninstrument: remove from registry; restore class __setattr__ if all instances removed
```

### Key Design Decisions
- **Class-level patch installed once** per type — correct for CPython's type lookup
- **`id(obj)` as registry key** — fast O(1) lookup without weakref overhead
- **Restores original on uninstrument** — no permanent class mutation
- **Graceful degradation for C extensions** — `_install_class_tracer()` catches `TypeError` for immutable types

## Alternative Considered: WeakKeyDictionary

A `weakref.WeakKeyDictionary` would auto-cleanup on GC, but:
- Adds `weakref` dependency and complexity
- GC timing is non-deterministic — cleaned entries might not align with `uninstrument()` calls
- `id()` + explicit cleanup is simpler and equally correct for this use case

## Files Modified
- `src/CORE/WORMS/expansion/race_detector.py` — Complete rewrite of `instrument_worm()`, `uninstrument_worm()`, added `_install_class_tracer()`, `_setattr_registry`

## Validation
- Syntax check passes
- 30/30 tests pass
- Multi-instance scenario: two instances of same class instrumented independently, both traced correctly, uninstrument restores original

## Prevention
- Always verify Python data model assumptions with `python -c` smoke tests before implementing special method overrides
- Special methods (`__*__`) are type-looked-up; instance dict entries don't override them
- Use class-level patching with per-instance filters for multi-instance-safe instrumentation
