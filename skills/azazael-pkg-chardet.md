---
name: azazael-pkg-chardet
description: Callable skill for Python package chardet 5.2.0 — Universal encoding detector for Python 3
metadata:
  category: packages
  project: azazael
  priority: low
---

# chardet 5.2.0

> Universal encoding detector for Python 3

## Identity

| Field | Value |
|-------|-------|
| Distribution | `chardet` |
| Version | `5.2.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `chardetect`

Invocation pattern:

```bash
chardetect --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `chardet`

Invocation pattern:

```python
import chardet
print("chardet loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import chardet; print('chardet OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
