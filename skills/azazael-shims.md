---
name: azazael-shims
description: Deprecation shim pattern — when to create shims, how to use FutureWarning, re-export patterns, testing procedures, and cleanup
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Deprecation Shims

> **Purpose:** Safe module relocation without breaking imports. Shims maintain backward compatibility while directing developers to the new location.
> **Context:** As Azazael refactors its monolith into sub-projects, many modules move. Shims prevent runtime breakage.

---

## When to Create a Shim

Create a deprecation shim when:
- A module is **relocated** to a different package/directory
- A module is **renamed** but callers still use the old name
- A module is **split** into multiple files and the old import path should still work
- A class/function is **moved** to a different module but the old import should redirect

## When NOT to Create a Shim

- **Internal implementation details** — Only public API modules need shims
- **Temporary files** — If nothing imports it, just delete it
- **Generated files** — Auto-generated code should be regenerated, not shimmed
- **During active development** — Wait until the new location is stable

---

## Shim Template

```python
# coding: utf-8
"""
DEPRECATED — Use new location instead.

This file is a backward-compatibility shim.
All functionality has been moved to:
    from NEW_LOCATION import NEW_NAME
"""

import warnings
warnings.warn(
    "azazael/src/OLD_LOCATION.py is deprecated. "
    "Use 'from NEW_LOCATION import NEW_NAME' instead.",
    FutureWarning,
    stacklevel=2,
)

from NEW_LOCATION import NEW_NAME  # noqa: E402, F401

__all__ = ["NEW_NAME"]
```

### Critical Elements

| Element | Why |
|---------|-----|
| `FutureWarning` | Always visible (not filtered by default in Python 3.14) |
| `stacklevel=2` | Error message points to the REAL caller, not the shim |
| Old path in message | `grep`-able, lets devs find all deprecated imports |
| New path in message | Tells devs exactly where to update their import |
| `# noqa: E402` | Suppresses "import not at top of file" linter warning |
| `# noqa: F401` | Suppresses "imported but unused" linter warning |
| `__all__` | Explicit re-export maintains API contract |
| Docstring | Tells devs what's happening without running code |

---

## Shim Testing Procedure

```python
# Test that the shim works (syntax + import)
python -c "from OLD_MODULE import NAME; print('Shim OK')"

# Test that the warning fires
python -W all -c "import OLD_MODULE"

# Test that the new location also works
python -c "from NEW_MODULE import NAME; print('New location OK')"

# Test that both return the same type
python -c "
from OLD_MODULE import NAME as OldName
from NEW_MODULE import NAME as NewName
assert type(OldName) is type(NewName), 'Type mismatch!'
print('Type compatibility OK')
"
```

---

## Shim Lifecycle

1. **Create** — Write shim at old location pointing to new location
2. **Verify** — Run the testing procedure above
3. **Propagate** — Update all internal references to use new import
4. **Wait** — Let downstream consumers update their imports
5. **Remove** — After verification period (recommended: 2 weeks or 2 sessions), delete the shim
6. **Clean up** — Run `sync_skills.py` if any skill references changed

---

## Known Shim Examples in Azazael

| Shim Path | Destination | Status |
|-----------|-------------|--------|
| `TOOLS/azazael_toolkit.py` | `AZAZAEL_TOOLKIT/` | Active |
| `CORE/codebuff_tracker.py` | `CORE/direct_memory.py` | Deprecated (raises ImportError) |
| `CORE/record_session.py` | `CORE/direct_memory.py` | Deprecated (raises ImportError) |

---

## Related Skills

- `azazael-dedup` — Deduplication procedures (MD5 hash comparison)
- `azazael-files` — Complete file index, import resolution
- `azazael-architecture` — Project layout, module organization
- `azazael-separation` — Monolith separation plan
