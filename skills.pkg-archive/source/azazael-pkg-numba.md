---
name: azazael-pkg-numba
description: Callable skill for Python package numba 0.65.1 — compiling Python code using LLVM
metadata:
  category: packages
  project: azazael
  priority: low
---

# numba 0.65.1

> compiling Python code using LLVM

## Identity

| Field | Value |
|-------|-------|
| Distribution | `numba` |
| Version | `0.65.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `numba`

Invocation pattern:

```python
import numba
print("numba loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import numba; print('numba OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
