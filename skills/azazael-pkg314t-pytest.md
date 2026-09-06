---
name: azazael-pkg314t-pytest
description: Callable skill for Python package pytest 9.1.0 — pytest: simple powerful testing with Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# pytest 9.1.0

> pytest: simple powerful testing with Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pytest` |
| Version | `9.1.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `py.test`
- `pytest`

Invocation pattern:

```bash
py.test --help
```

Alternates:

```bash
pytest --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pytest`

Invocation pattern:

```python
import pytest
print("pytest loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import pytest; print('pytest OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
