---
name: azazael-pkg-distro
description: Callable skill for Python package distro 1.9.0 — Distro - an OS platform information API
metadata:
  category: packages
  project: azazael
  priority: low
---

# distro 1.9.0

> Distro - an OS platform information API

## Identity

| Field | Value |
|-------|-------|
| Distribution | `distro` |
| Version | `1.9.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `distro`

Invocation pattern:

```bash
distro --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `distro`

Invocation pattern:

```python
import distro
print("distro loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import distro; print('distro OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
