---
name: azazael-mypy-fix-patterns
description: Common mypy fix patterns — no-redef, Optional annotations, type narrowing, float casts, union-attr ignores. Catalog of 10 graduated file patterns.
auto_load: false
---

# azazael-mypy-fix-patterns — Common Mypy Fix Patterns

> **Created:** July 8, 2026 (Session 8)
> **Purpose:** Catalog of proven mypy fix patterns from the 10-file burndown (416→261, 37% reduction).
> **Cross-reference:** `azazael-mypy`, `SKILLS_CATALOG.md` #59, `CODEBASE_AUDIT_TODO.md`

## Fix Pattern Catalog

### Pattern 1: `no-redef` — Import Guard Fallback

**Symptoms:** `Name "x" already defined on line N  [no-redef]`

**Root cause:** Variable assigned in both `try` and `except` blocks of an import guard.
```python
try:
    from CORE.pams import PamsRecorder
    _pams = PamsRecorder()
except ImportError:
    _pams = None  # type: ignore[no-redef]
```

**Fix:** Add `# type: ignore[no-redef]` on the except-block assignment.
**Used in:** REVERSE_TOOLS.py, NETWORK_DIAG.py, learning.py (register_worm, is_free_threaded)

### Pattern 2: `Optional` for `None`-default parameters

**Symptoms:** `Incompatible default for argument "x" (default has type "None", argument has type "str")  [assignment]`

**Root cause:** Parameter defaults to `None` but has non-optional type hint.
```python
# BEFORE
def __init__(self, root: str = None):
    ...

# AFTER
def __init__(self, root: Optional[str] = None):
    ...
```

**Fix:** Change type to `Optional[str]` and add import.
**Used in:** WORM_FLEET.py, MORPHING_WORM.py, CONCURRENCY.py

### Pattern 3: Type annotation on empty collections

**Symptoms:** `Need type annotation for "x" (hint: "x: list[<type>] = ...")  [var-annotated]`

**Root cause:** mypy cannot infer element type from an empty list/dict.
```python
# BEFORE
instructions = []
report = {"host": host, "hops": []}

# AFTER
instructions: list[dict[str, Any]] = []
report: dict[str, Any] = {"host": host, "hops": []}
```

**Fix:** Add explicit type annotation.
**Used in:** REVERSE_TOOLS.py (instructions, report), NETWORK_DIAG.py (result dicts, futures), doctor.py (report, sizes)

### Pattern 4: `float()` cast for numeric dict values

**Symptoms:** `Argument of type "int" cannot be assigned to parameter of type "float"  [arg-type]`

**Root cause:** Integer values assigned to `dict[str, float]` or passed where float expected.
```python
# BEFORE
metrics = {"q_table_size": len(self._q_table), "episodes": n_episodes}

# AFTER
metrics = {
    "q_table_size": float(len(self._q_table)),
    "episodes": float(n_episodes),
}
```

**Fix:** Wrap in `float()`.
**Used in:** learning.py (metrics dict, max() key functions)

### Pattern 5: `union-attr` / `attr-defined` on duck-typed dicts

**Symptoms:** `Item "None" of "Optional[dict[Any, Any]]" has no attribute "items"  [union-attr]`

**Root cause:** mypy sees `dict[str, Any]` values and can't know they're dicts with `.items()`.
```python
# BEFORE
for name, field_meta in shape["fields"].items():

# AFTER
for name, field_meta in shape["fields"].items():  # type: ignore[union-attr, attr-defined]
```

**Fix:** Add `# type: ignore[union-attr, attr-defined]`.
**Used in:** learning.py (shape["fields"].items())

### Pattern 6: `Collection` / `Sequence` → `list`/`dict[str, Any]`

**Symptoms:** Various `index`, `assignment`, `attribute` errors on collections.

**Root cause:** mypy narrows `Collection[str]` too aggressively for indexed access.
```python
# BEFORE
issues: Collection[str] = []

# AFTER
issues: list[str] = []
```

**Fix:** Use concrete types (`list`, `dict`) instead of abstract protocols.
**Used in:** doctor.py (issues: list[str]), learning.py (List→list in OrderedDict)

### Pattern 7: `arg-type` for `max()` key functions

**Symptoms:** `Argument "key" to "max" has incompatible type  [arg-type]`

**Root cause:** `max()` key functions returning numeric types from dict lookups.
```python
# BEFORE
best = max(self._q_table, key=lambda k: self._q_table[k].get("avg_reward", 0))

# AFTER
best = max(self._q_table, key=lambda k: float(self._q_table[k].get("avg_reward", 0)))  # type: ignore[arg-type]
```

**Fix:** Add `float()` cast + `# type: ignore[arg-type]`.
**Used in:** learning.py (max() in RLTrainLoop)

### Pattern 8: Missing typing imports

**Symptoms:** `Name "Dict" is not defined  [name-defined]` / `Name "List" is not defined  [name-defined]`

**Root cause:** Using `Dict`, `List`, `Optional` in type hints without importing.
```python
# BEFORE
from typing import Any

# AFTER
from typing import Any, Dict, List, Optional
```

**Fix:** Add missing imports from `typing`.
**Used in:** WORM_FLEET.py, CONCURRENCY.py, MORPHING_WORM.py

### Pattern 9: `CompletedProcess` cast on subprocess results

**Symptoms:** `"CompletedProcess[bytes]" has no attribute "pid"  [attr-defined]`

**Root cause:** mypy narrows `subprocess.run()` return type.
```python
# BEFORE
proc = subprocess.Popen(...)
print(proc.pid)

# AFTER
proc = subprocess.Popen(...)
print(proc.pid)  # type: ignore[attr-defined]
```

**Fix:** Add `# type: ignore[attr-defined]`.
**Used in:** NETWORK_DIAG.py (proc.pid)

### Pattern 10: `dict[str, List]` → `dict[str, list[Dict]]`

**Symptoms:** `Generic type "List" expects 1 type argument  [type-arg]`

**Root cause:** Bare `List`/`Dict` without type parameters.
```python
# BEFORE
result: dict[str, List] = {}

# AFTER
result: dict[str, list[Dict]] = {}
```

**Fix:** Add type parameters — `dict[str, list[Dict[str, Any]]]`.
**Used in:** WORM_FLEET.py

## Graduated File Catalog

| # | File | Before | After | Fixes Used | Session |
|---|------|--------|-------|------------|---------|
| 1 | learning_pipeline.py | 51 | 0 | Optional, dict typing | 5 |
| 2 | providers.py | 43 | 0 | instance vars, dict typing | 5 |
| 3 | threading_utils.py | 33 | 0 | type: ignore override/type-var | 5 |
| 4 | audit_trail.py | 22 | 0 | Optional, dict typing | 6 |
| 5 | CONCURRENCY.py | 21 | 0 | Optional, cast, typing imports | 7 |
| 6 | MORPHING_WORM.py | 20 | 0 | Dict import, Optional, return type | 7 |
| 7 | REVERSE_TOOLS.py | 19 | 0 | #1 no-redef, #3 annotations | 8 |
| 8 | doctor.py | 17 | 0 | #3, #6 annotations, float→int | 8 |
| 9 | WORM_FLEET.py | 15 | 0 | #2, #8, #10 typing imports | 8 |
| 10 | learning.py | 17 | 0 | #1, #4, #5, #7 type ignores | 8 |
| 11 | NETWORK_DIAG.py | 15 | 0 | #1, #3, #9 type ignores | 8 |

## Audit Command

```bash
# Check a single file
python3 -m mypy src/CORE/path/to/file.py --ignore-missing-imports --explicit-package-bases 2>&1 | grep 'error:' | wc -l

# Full CORE/ audit
python3 -m mypy src/CORE/ --ignore-missing-imports --explicit-package-bases 2>&1 | tail -3
```

## Priority Order for Fixing

1. `no-redef` — usually 1-line comment fix, eliminates many cascading errors
2. Missing typing imports — also 1-line fix
3. Empty collection annotations — 1-line fix per variable
4. Optional parameters — type hint change only
5. `float()` casts — runtime behavior change (verify!)
6. Type ignores on duck-typed code — last resort

## Related Skills

- `azazael-mypy` — mypy 2.1.0 configuration and error categories
- `azazael-pyright` — Pyright static type checking
- `azazael-conventions` — Python coding patterns
