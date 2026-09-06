---
name: azazael-pkg-watchdog
description: Callable skill for Python package watchdog 6.0.0 — Filesystem events monitoring
metadata:
  category: packages
  project: azazael
  priority: low
---

# watchdog 6.0.0

> Filesystem events monitoring

## Identity

| Field | Value |
|-------|-------|
| Distribution | `watchdog` |
| Version | `6.0.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `watchmedo`

Invocation pattern:

```bash
watchmedo --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `watchdog`

Invocation pattern:

```python
import watchdog
print("watchdog loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import watchdog; print('watchdog OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
