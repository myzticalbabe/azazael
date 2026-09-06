---
name: azazael-pkg-playwright
description: Callable skill for Python package playwright 1.55.0+ds — A high-level API to automate web browsers
metadata:
  category: packages
  project: azazael
  priority: low
---

# playwright 1.55.0+ds

> A high-level API to automate web browsers

## Identity

| Field | Value |
|-------|-------|
| Distribution | `playwright` |
| Version | `1.55.0+ds` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `playwright`

Invocation pattern:

```bash
playwright --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `playwright`

Invocation pattern:

```python
import playwright
print("playwright loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import playwright; print('playwright OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
