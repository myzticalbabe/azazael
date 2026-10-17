---
name: azazael-conventions
description: Azazael Python coding conventions — patterns, style rules, import style, error handling patterns, threading patterns, anti-patterns to avoid.
metadata:
  category: conventions
  project: azazael
  auto_load: true
---
# Azazael Coding Conventions

## Import Style
```python
# Standard library first
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
from PIL import Image
import psutil

# Project imports (absolute from src/)
from CORE.worm_registry import register_worm, discover_worms
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
```

**Rules:**
- All imports at top of file (no function-body imports)
- Remove unused imports when refactoring
- Use absolute imports from `src/`

## Path Handling
```python
from CORE.paths import get_project_root, get_src_dir, get_g_drive

# Always use pathlib.Path
root = get_project_root()
config_path = root / "config" / "settings.yaml"

# Handle Optional[Path] returns
g_drive = get_g_drive()
if g_drive:
    archive = g_drive / "AZAZAEL"
```

## Worm Pattern
```python
from CORE.worm_registry import register_worm

@register_worm(
    category="security",
    priority=6,
    cooldown_seconds=60,
    version="1.0.0",
    description="Scans for vulnerabilities"
)
class MyWorm:
    def execute(self) -> Dict:
        """Execute worm logic. Called by ClusterWORMZ."""
        try:
            result = self._do_work()
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _do_work(self):
        ...
```

## Thread Safety
```python
import threading

class ThreadSafeComponent:
    def __init__(self):
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._results = []
    
    def execute_parallel(self, items):
        def worker(item):
            if self._cancel.is_set():
                return
            result = process(item)
            with self._lock:
                self._results.append(result)
        
        threads = []
        for item in items:
            t = threading.Thread(target=worker, args=(item,), daemon=True)
            t.start()
            threads.append(t)
        # ...
```

## Factory Methods
```python
# CORRECT:
@classmethod
def build_from_registry(cls):
    instance = cls("registry")  # Use cls(), not cls.__new__()
    return instance

# WRONG:
@classmethod
def build_from_registry(cls):
    instance = cls.__new__(cls)  # Bypasses __init__!
    return instance
```

## Mermaid Graph Generation
```python
def to_mermaid(self) -> str:
    lines = ["graph TD"]
    # Use ASCII only (no Unicode emoji!)
    lines.append(f'    status["Status: {ok} OK / {fail} FAIL"]')
    return "\n".join(lines)
```

## Anti-Patterns (From ERROR_LOG.md)

| ❌ Never | ✅ Always |
|----------|----------|
| Nested quotes in basher commands | Write to temp file, run `python _tmp.py` |
| Unicode emoji (✓✗🔷⚡) | ASCII: `OK`, `FAIL`, `*`, `>>` |
| `f"...{d[\"key\"]}..."` | `k = "key"; f"...{d[k]}..."` |
| `cls.__new__(cls)` | `cls()` |
| `import x` inside function | `import x` at top of file |
| Leave temp files | Clean up `_test_*.py`, `_trace_*.py` |

## Pre-Commit Checklist
See `azazael-testing` skill for the canonical pre-commit checklist (syntax check, integration test, emoji check, temp file cleanup, etc.).

## Related Skills
- `azazael-git` — Commit conventions, branching strategy
- `azazael-mermaid` — Mermaid graph generation patterns
- `azazael-threading` — 3.14t threading patterns
- `azazael-environment` — Python version, dependencies, path setup
- `azazael-testing` — Pre-commit validation checklist (canonical)
