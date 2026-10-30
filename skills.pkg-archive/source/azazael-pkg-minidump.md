---
name: azazael-pkg-minidump
description: Callable skill for Python package minidump 0.0.21 — Python library to parse Windows minidump file format
metadata:
  category: packages
  project: azazael
  priority: low
---

# minidump 0.0.21

> Python library to parse Windows minidump file format

## Identity

| Field | Value |
|-------|-------|
| Distribution | `minidump` |
| Version | `0.0.21` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `minidump`

Invocation pattern:

```bash
minidump --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `minidump`

Invocation pattern:

```python
import minidump
print("minidump loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import minidump; print('minidump OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
