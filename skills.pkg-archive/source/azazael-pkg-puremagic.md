---
name: azazael-pkg-puremagic
description: Callable skill for Python package puremagic 2.2.0 — Pure python implementation of magic file detection
metadata:
  category: packages
  project: azazael
  priority: low
---

# puremagic 2.2.0

> Pure python implementation of magic file detection

## Identity

| Field | Value |
|-------|-------|
| Distribution | `puremagic` |
| Version | `2.2.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `puremagic`

Invocation pattern:

```bash
puremagic --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `puremagic`

Invocation pattern:

```python
import puremagic
print("puremagic loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import puremagic; print('puremagic OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
