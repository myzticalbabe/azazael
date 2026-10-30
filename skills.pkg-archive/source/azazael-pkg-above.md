---
name: azazael-pkg-above
description: Callable skill for Python package above 2.8.1 — Network Security Sniffer
metadata:
  category: packages
  project: azazael
  priority: low
---

# above 2.8.1

> Network Security Sniffer

## Identity

| Field | Value |
|-------|-------|
| Distribution | `above` |
| Version | `2.8.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `above`

Invocation pattern:

```bash
above --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `above`

Invocation pattern:

```python
import above
print("above loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import above; print('above OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
