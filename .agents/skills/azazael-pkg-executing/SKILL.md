---
name: azazael-pkg-executing
description: Callable skill for Python package executing 2.2.1 — Get the currently executing AST node of a frame, and other information
metadata:
  category: packages
  project: azazael
  priority: low
---

# executing 2.2.1

> Get the currently executing AST node of a frame, and other information

## Identity

| Field | Value |
|-------|-------|
| Distribution | `executing` |
| Version | `2.2.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `executing`

Invocation pattern:

```python
import executing
print("executing loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import executing; print('executing OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
