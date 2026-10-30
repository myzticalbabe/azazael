---
name: azazael-pkg-textfsm
description: Callable skill for Python package textfsm 2.1.0 — Python module for parsing semi-structured text into python tables.
metadata:
  category: packages
  project: azazael
  priority: low
---

# textfsm 2.1.0

> Python module for parsing semi-structured text into python tables.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `textfsm` |
| Version | `2.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `textfsm`

Invocation pattern:

```bash
textfsm --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `textfsm`

Invocation pattern:

```python
import textfsm
print("textfsm loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import textfsm; print('textfsm OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
