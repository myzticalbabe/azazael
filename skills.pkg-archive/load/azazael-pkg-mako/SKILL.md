---
name: azazael-pkg-mako
description: Callable skill for Python package Mako 1.3.10.dev0 — A super-fast templating language that borrows the best ideas from the existing templating languages.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Mako 1.3.10.dev0

> A super-fast templating language that borrows the best ideas from the existing templating languages.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Mako` |
| Version | `1.3.10.dev0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `mako-render`

Invocation pattern:

```bash
mako-render --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Mako`

Invocation pattern:

```python
import Mako
print("Mako loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import Mako; print('Mako OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
