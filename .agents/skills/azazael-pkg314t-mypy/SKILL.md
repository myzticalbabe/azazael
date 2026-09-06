---
name: azazael-pkg314t-mypy
description: Callable skill for Python package mypy 2.1.0 — Optional static typing for Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# mypy 2.1.0

> Optional static typing for Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `mypy` |
| Version | `2.1.0` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `dmypy`
- `mypy`
- `mypyc`
- `stubgen`
- `stubtest`

Invocation pattern:

```bash
dmypy --help
```

Alternates:

```bash
mypy --help
mypyc --help
stubgen --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `mypy`

Invocation pattern:

```python
import mypy
print("mypy loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import mypy; print('mypy OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
