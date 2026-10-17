---
name: azazael-dedup
description: Deduplication procedures — MD5 hash comparison, duplicate file detection, deprecation shim creation, cleanup patterns
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Deduplication Procedures

> **Purpose:** Find and eliminate duplicate files using MD5 hash comparison, establish deprecation shims for moved code.
> **Context:** The Azazael codebase has accumulated duplicate modules across `src/`, `azazael/packages/`, and `Desktop/` directories.

---

## Detection Pattern

### Find Duplicates by MD5 Hash

```python
import hashlib
from pathlib import Path

def find_duplicates(directory: str = ".") -> dict:
    """Find files with identical MD5 hashes across the codebase."""
    hash_map = {}
    for f in Path(directory).rglob("*.py"):
        if f.stat().st_size == 0:
            continue
        md5 = hashlib.md5(f.read_bytes()).hexdigest()
        hash_map.setdefault(md5, []).append(f)
    
    duplicates = {h: files for h, files in hash_map.items() if len(files) > 1}
    return duplicates

# Usage
dups = find_duplicates("src")
for md5, files in sorted(dups.items(), key=lambda x: -len(x[1])):
    sizes = [f.stat().st_size for f in files]
    print(f"[{len(files)} copies] {sizes[0]} bytes")
    for f in files:
        print(f"  {f}")
```

### Find Near-Duplicates by Filename + Size

```python
def find_same_name_same_size(directory: str = ".") -> dict:
    """Find files with same name AND same size (likely identical content)."""
    from collections import defaultdict
    by_name = defaultdict(list)
    for f in Path(directory).rglob("*.py"):
        by_name[f.name].append(f)
    
    near_dups = {}
    for name, files in by_name.items():
        size_groups = defaultdict(list)
        for f in files:
            size_groups[f.stat().st_size].append(f)
        for size, same_size_files in size_groups.items():
            if len(same_size_files) > 1:
                near_dups[f"{name} ({size}b)"] = same_size_files
    return near_dups
```

---

## Deprecation Shim Pattern

When a module is relocated, DO NOT delete the original file. Instead, create a shim:

```python
# deprecation_shim.py — Original location, now in AZAZAEL_TOOLKIT/
# DEPRECATED: Use from AZAZAEL_TOOLKIT.foo import bar instead

import warnings
warnings.warn(
    "src/TOOLS/foo.py is deprecated. "
    "Use 'from AZAZAEL_TOOLKIT.foo import bar' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from AZAZAEL_TOOLKIT.foo import bar  # noqa: E402, F401

__all__ = ["bar"]
```

### Shim Requirements

| Element | Required | Purpose |
|---------|----------|---------|
| `FutureWarning` | ✅ | Ensures warning is always visible (not filtered by default) |
| `stacklevel=2` | ✅ | Points to the caller, not the shim |
| Source file path in message | ✅ | Helps locate the deprecated import |
| Destination path in message | ✅ | Tells the developer where to find the replacement |
| `# noqa: E402, F401` | ✅ | Suppresses linter warnings for late import / unused import |
| `__all__` re-export | ✅ | Maintains API compatibility |
| Docstring | ✅ | Quick reference without reading warning message |

---

## Cleanup Procedure

1. **Scan** — Run MD5 hash scan across all source directories
2. **Verify** — Confirm duplicates are truly identical (not just same name)
3. **Identify canonical source** — Which copy is the authoritative one?
4. **Create shim** — At the duplicate location pointing to the canonical source
5. **Import shim test** — Verify `from old_location import X` still works via shim
6. **Remove duplicate** — Delete the duplicate file (not the shim, not the canonical)
7. **Clean up shims later** — After all references are updated, remove shims

---

## Related Skills

- `azazael-shims` — Deprecation shim pattern details
- `azazael-paths` — Dynamic path resolution for module relocation
- `azazael-separation` — Monolith separation plan (6 layers, 27 programs)
- `azazael-files` — Complete file index and module map
