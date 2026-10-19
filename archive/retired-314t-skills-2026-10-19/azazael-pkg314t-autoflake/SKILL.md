---
name: azazael-pkg314t-autoflake
description: Callable skill for Python package autoflake 2.3.3 — Removes unused imports and unused variables
metadata:
  category: packages
  project: azazael
  priority: low
---

# autoflake 2.3.3

> Removes unused imports and unused variables

## Identity

| Field | Value |
|-------|-------|
| Distribution | `autoflake` |
| Version | `2.3.3` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `autoflake`

Invocation pattern:

```bash
autoflake --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `autoflake`

Invocation pattern:

```python
import autoflake
print("autoflake loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import autoflake; print('autoflake OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
