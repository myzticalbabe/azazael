---
name: azazael-pkg-shodan
description: Callable skill for Python package shodan 1.31.0 — Python library and command-line utility for Shodan (https://developer.shodan.io)
metadata:
  category: packages
  project: azazael
  priority: low
---

# shodan 1.31.0

> Python library and command-line utility for Shodan (https://developer.shodan.io)

## Identity

| Field | Value |
|-------|-------|
| Distribution | `shodan` |
| Version | `1.31.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `shodan`

Invocation pattern:

```bash
shodan --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `shodan`

Invocation pattern:

```python
import shodan
print("shodan loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import shodan; print('shodan OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
