---
name: azazael-pkg314t-nuitka
description: Callable skill for Python package Nuitka 4.1.2 — Python compiler with full language support and CPython compatibility
metadata:
  category: packages
  project: azazael
  priority: low
---

# Nuitka 4.1.2

> Python compiler with full language support and CPython compatibility

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Nuitka` |
| Version | `4.1.2` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `nuitka`
- `nuitka-run`

Invocation pattern:

```bash
nuitka --help
```

Alternates:

```bash
nuitka-run --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Nuitka`

Invocation pattern:

```python
import Nuitka
print("Nuitka loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import Nuitka; print('Nuitka OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
