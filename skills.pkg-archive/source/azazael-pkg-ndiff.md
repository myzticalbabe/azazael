---
name: azazael-pkg-ndiff
description: Callable skill for Python package ndiff 7.99 — Nmap scan diff tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# ndiff 7.99

> Nmap scan diff tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `ndiff` |
| Version | `7.99` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ndiff`

Invocation pattern:

```bash
ndiff --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `ndiff`

Invocation pattern:

```python
import ndiff
print("ndiff loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import ndiff; print('ndiff OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
