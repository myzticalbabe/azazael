---
name: azazael-pkg-pytest
description: Callable skill for Python package pytest 9.0.3 — pytest: simple powerful testing with Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# pytest 9.0.3

> pytest: simple powerful testing with Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pytest` |
| Version | `9.0.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

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
/usr/bin/python3.13 -c "import pytest; print('pytest OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
