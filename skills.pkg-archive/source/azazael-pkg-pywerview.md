---
name: azazael-pkg-pywerview
description: Callable skill for Python package pywerview 0.3.3 — A Python port of PowerSploit's PowerView
metadata:
  category: packages
  project: azazael
  priority: low
---

# pywerview 0.3.3

> A Python port of PowerSploit's PowerView

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pywerview` |
| Version | `0.3.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pywerview`

Invocation pattern:

```bash
pywerview --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pywerview`

Invocation pattern:

```python
import pywerview
print("pywerview loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pywerview; print('pywerview OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
