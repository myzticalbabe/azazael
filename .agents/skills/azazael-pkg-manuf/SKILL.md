---
name: azazael-pkg-manuf
description: Callable skill for Python package manuf 1.1.5 — Parser library for Wireshark's OUI database
metadata:
  category: packages
  project: azazael
  priority: low
---

# manuf 1.1.5

> Parser library for Wireshark's OUI database

## Identity

| Field | Value |
|-------|-------|
| Distribution | `manuf` |
| Version | `1.1.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `manuf`

Invocation pattern:

```bash
manuf --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `manuf`

Invocation pattern:

```python
import manuf
print("manuf loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import manuf; print('manuf OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
