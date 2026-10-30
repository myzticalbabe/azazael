---
name: azazael-pkg-plaso
description: Callable skill for Python package plaso 20260119 — Plaso (log2timeline) - Super timeline all the things
metadata:
  category: packages
  project: azazael
  priority: low
---

# plaso 20260119

> Plaso (log2timeline) - Super timeline all the things

## Identity

| Field | Value |
|-------|-------|
| Distribution | `plaso` |
| Version | `20260119` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `plaso-image_export`
- `plaso-log2timeline`
- `plaso-pinfo`
- `plaso-psort`
- `plaso-psteal`

Invocation pattern:

```bash
plaso-image_export --help
```

Alternates:

```bash
plaso-log2timeline --help
plaso-pinfo --help
plaso-psort --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `plaso`

Invocation pattern:

```python
import plaso
print("plaso loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import plaso; print('plaso OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
