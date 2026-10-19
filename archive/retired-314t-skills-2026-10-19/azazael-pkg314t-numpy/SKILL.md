---
name: azazael-pkg314t-numpy
description: Callable skill for Python package numpy 2.4.6 — Fundamental package for array computing in Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# numpy 2.4.6

> Fundamental package for array computing in Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `numpy` |
| Version | `2.4.6` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `f2py`
- `numpy-config`

Invocation pattern:

```bash
f2py --help
```

Alternates:

```bash
numpy-config --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `numpy`

Invocation pattern:

```python
import numpy
print("numpy loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import numpy; print('numpy OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
