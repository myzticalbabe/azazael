---
name: azazael-shims
description: Azazael deprecation shim pattern — when to use, how to create, how to test, examples from all 13 shims created.
metadata:
  category: maintenance
  project: azazael
---

# Azazael Deprecation Shim Skill

## Overview

A **deprecation shim** is a thin replacement file that re-exports symbols from a canonical source while emitting a `UserWarning` directing developers to update their imports. As of May 29, 2026, **13 shims** have been created across 3 directories.

---

## When to Create a Shim

| Situation | Action |
|-----------|--------|
| Byte-for-byte duplicate in two locations | Shim the non-canonical copy |
| Stale copy with hardcoded paths (canonical has dynamic paths) | Shim the stale copy |
| Near-duplicate with minor bugs (CSS typos, missing decorators) | Shim the buggy copy |
| File with broken imports that never worked | Fix the canonical, shim the broken copy |
| Directory restructuring (canonical moved) | Shim old location → new location |

---

## Shim Template

### Pattern A: Explicit Imports (preferred for small modules)

```python
# coding: utf-8
"""
DIR/SUBDIR/MODULE.py — DEPRECATION SHIM

This file was [a duplicate | stale copy | etc].
It now re-exports from the canonical source: MODULE.py

Update your imports from:
    from DIR.SUBDIR.MODULE import Something
to:
    from MODULE import Something

This shim will be removed in a future release.
"""

import sys
import warnings
from pathlib import Path

warnings.warn(
    "DIR.SUBDIR.MODULE is deprecated. "
    "Use 'from MODULE import ...' instead. "
    "This shim will be removed in a future release.",
    UserWarning,
    stacklevel=2,
)

_src_dir = Path(__file__).resolve().parent.parent.parent  # Adjust depth as needed
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from MODULE import ExportedClass1, ExportedClass2, public_function  # noqa: E402, F401

__all__ = ["ExportedClass1", "ExportedClass2", "public_function"]
```

### Pattern B: `from X import *` (for large modules with many exports)

```python
# Use same boilerplate as Pattern A, but replace the import line with:

from MODULE import *  # noqa: E402, F401
# No __all__ needed — defers to canonical module's __all__

# WHEN TO USE:
# - Module has 15+ public exports (tedious to list)
# - Module is large (300+ lines)
# - Shim will be removed soon (< 3 months)
# - No namespace pollution concerns (deprecation warning tells users to update anyway)
```

### Path Resolution by Directory

| Shim Location | `parent.parent...` Chain | Resolves To |
|--------------|--------------------------|-------------|
| `META/X.py` | `.parent.parent` (META → src) | `azazael/src/` |
| `HYDRA/ml_platforms/X.py` | `.parent.parent.parent` (ml_platforms → HYDRA → src) | `azazael/src/` |
| `CODEX/CORE/X.py` | `.parent.parent.parent` (CORE → CODEX → src) | `azazael/src/` |
| `META/METAWORMS_POPUP.py` | `.parent.parent` (META → src) | `azazael/src/` |

---

## Testing a Shim

### Test 1: Import Verification
```python
import sys; sys.path.insert(0, 'azazael/src')
import warnings

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    from DIR.SUBDIR.MODULE import ExportedName
    assert len(w) == 1, f"Expected 1 warning, got {len(w)}"
    assert "deprecated" in str(w[0].message).lower()

print("OK: Warning fires correctly")
```

### Test 2: Symbol Identity (shim and canonical match)
```python
from DIR.SUBDIR.MODULE import ExportedName as Shimmed
from MODULE import ExportedName as Canonical
assert Shimmed is Canonical, "Shim and canonical should reference same object"
print("OK: Symbols match")
```

### Test 3: No Import Reference Check
```bash
rg "from DIR\.SUBDIR\.MODULE|import DIR\.SUBDIR\.MODULE" azazael/src/
# Should return 0 results
```

---

## Warning Category Decision

| Category | Visible by Default? | When to Use |
|----------|---------------------|-------------|
| `UserWarning` | ✅ Yes | **Shims** — developers should see this immediately |
| `DeprecationWarning` | ❌ No (filtered) | Library deprecations for end-users |
| `FutureWarning` | ✅ Yes | Upcoming behavior changes |
| `PendingDeprecationWarning` | ❌ No (filtered) | Very early heads-up |

**All 13 Azazael shims use `UserWarning`** — this is the correct choice for in-project deprecation notices.

---

## Real Examples

### Small Module (3 exports) — META/UVZ.py
```python
from UVZ import UVResult, UVZ, main
__all__ = ["UVResult", "UVZ", "main"]
```

### Medium Module (3 exports) — META/OPTIMIZ.py
```python
from OPTIMIZ import OptimizationResult, OPTIMIZ, main
__all__ = ["OptimizationResult", "OPTIMIZ", "main"]
```

### Large Module (many exports) — CODEX/CORE/ANIMATION_PROTOCOLS.py
```python
from ANIMATION_PROTOCOLS import *  # 313 lines, ~15+ animation classes
```

### Package Shim — HYDRA/ml_platforms/__init__.py
```python
from ORCHESTRATION.ml_platforms.config import (
    LexiconUpdater, MLPlatformConfig, load_config, discover_modules
)
from ORCHESTRATION.ml_platforms.diagnostics import (
    print_platform_status, list_workflows
)
__all__ = [...]  # 10+ names
```

---

## Shim Lifecycle

1. **Create shim** — Duplicate identified, canonical determined
2. **Add deprecation warning** — `UserWarning` fires on import
3. **Document in MEMORIES.md** — Add to shims table
4. **Wait (1-3 months)** — Allow importers to update
5. **Remove shim** — Delete the shim file, clean up MEMORIES.md

---

## Related Skills
- `azazael-dedup` — Finding and comparing duplicates
- `azazael-separation` — Project extraction and deprecation timelines
- `azazael-architecture` — Project structure and canonical locations
