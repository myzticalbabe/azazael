---
name: azazael-pkg-osrframework
description: Callable skill for Python package osrframework 0.20.5 — OSRFramework - A set of AGPLv3+ OSINT tools developed by i3visio analysts for online research.
metadata:
  category: packages
  project: azazael
  priority: low
---

# osrframework 0.20.5

> OSRFramework - A set of AGPLv3+ OSINT tools developed by i3visio analysts for online research.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `osrframework` |
| Version | `0.20.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `alias_generator`
- `alias_generator.py`
- `checkfy`
- `checkfy.py`
- `domainfy`
- `domainfy.py`
- `mailfy`
- `mailfy.py`
- ... plus 8 more

Invocation pattern:

```bash
alias_generator --help
```

Alternates:

```bash
alias_generator.py --help
checkfy --help
checkfy.py --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `osrframework`

Invocation pattern:

```python
import osrframework
print("osrframework loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import osrframework; print('osrframework OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
