---
name: azazael-pkg314t-pip
description: Callable skill for Python package pip 26.1.2 — The PyPA recommended tool for installing Python packages.
metadata:
  category: packages
  project: azazael
  priority: low
---

# pip 26.1.2

> The PyPA recommended tool for installing Python packages.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pip` |
| Version | `26.1.2` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `pip`
- `pip3`

Invocation pattern:

```bash
pip --help
```

Alternates:

```bash
pip3 --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pip`

Invocation pattern:

```python
import pip
print("pip loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import pip; print('pip OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
