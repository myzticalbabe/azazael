---
name: azazael-tools
description: TOOLS directory — debug_runner (multi-agent test runner), archive_system (file archiving), COMPREHENSIVE_FIX (LSP repair). Misc system tools not covered by AZAZAEL_TOOLKIT.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: true
---

# Azazael TOOLS — Miscellaneous System Tools

> **Implementation:** `src/TOOLS/`
> **5 .py files** (1 deprecation shim, 3 substantive tools, 1 package init)

---

## Components

| File | Size | Purpose |
|------|:----:|---------|
| `debug_runner.py` | 15.0KB | Multi-agent test runner for integration tests |
| `archive_system.py` | 12.6KB | Archive system for old or unused files |
| `COMPREHENSIVE_FIX.py` | 7.9KB | LSP error diagnosis and desktop shortcut repair |
| `azazael_toolkit.py` | 0.9KB | **Deprecation shim** — re-exports from `AZAZAEL_TOOLKIT/` |
| `__init__.py` | 0.1KB | Package initialization |

## Import Pattern

```python
import sys; sys.path.insert(0, 'src')
from TOOLS.debug_runner import DebugRunner
from TOOLS.archive_system import ArchiveSystem
from TOOLS.COMPREHENSIVE_FIX import comprehensive_fix
```

## Status Note

`TOOLS/azazael_toolkit.py` is a deprecation shim — TOOLS/ functionality is gradually being migrated to `AZAZAEL_TOOLKIT/`. Prefer importing from `AZAZAEL_TOOLKIT` for equivalent tools.

## Related Skills

- `azazael-toolkit` — AZAZAEL_TOOLKIT (destination for migrated TOOLS/ functionality)
- `azazael-testing` — Testing conventions (debug_runner is an integration test tool)
- `azazael-utilities` — UTILITIES sub-systems catalog
