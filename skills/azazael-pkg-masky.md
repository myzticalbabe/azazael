---
name: azazael-pkg-masky
description: Callable skill for Python package masky 0.2.1 — Python library with CLI allowing to remotely dump domain user credentials via an ADCS
metadata:
  category: packages
  project: azazael
  priority: low
---

# masky 0.2.1

> Python library with CLI allowing to remotely dump domain user credentials via an ADCS

## Identity

| Field | Value |
|-------|-------|
| Distribution | `masky` |
| Version | `0.2.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `masky`

Invocation pattern:

```bash
masky --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `masky`

Invocation pattern:

```python
import masky
print("masky loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import masky; print('masky OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
