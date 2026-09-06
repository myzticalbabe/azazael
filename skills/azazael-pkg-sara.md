---
name: azazael-pkg-sara
description: Callable skill for Python package sara 1.3 — RouterOS Security Inspector
metadata:
  category: packages
  project: azazael
  priority: low
---

# sara 1.3

> RouterOS Security Inspector

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sara` |
| Version | `1.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sara`

Invocation pattern:

```bash
sara --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `sara`

Invocation pattern:

```python
import sara
print("sara loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import sara; print('sara OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
