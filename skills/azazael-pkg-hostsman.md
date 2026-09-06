---
name: azazael-pkg-hostsman
description: Callable skill for Python package hostsman 1.1.5 — A tool to manage hosts file
metadata:
  category: packages
  project: azazael
  priority: low
---

# hostsman 1.1.5

> A tool to manage hosts file

## Identity

| Field | Value |
|-------|-------|
| Distribution | `hostsman` |
| Version | `1.1.5` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `hostsman`

Invocation pattern:

```bash
hostsman --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `hostsman`

Invocation pattern:

```python
import hostsman
print("hostsman loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import hostsman; print('hostsman OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
