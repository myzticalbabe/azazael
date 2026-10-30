---
name: azazael-pkg-sslyze
description: Callable skill for Python package sslyze 6.3.1 — Fast and powerful SSL/TLS scanning library.
metadata:
  category: packages
  project: azazael
  priority: low
---

# sslyze 6.3.1

> Fast and powerful SSL/TLS scanning library.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `sslyze` |
| Version | `6.3.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `sslyze`

Invocation pattern:

```bash
sslyze --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `sslyze`

Invocation pattern:

```python
import sslyze
print("sslyze loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import sslyze; print('sslyze OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
