---
name: azazael-pkg-volatility3
description: Callable skill for Python package volatility3 2.28.0 — Memory forensics framework
metadata:
  category: packages
  project: azazael
  priority: low
---

# volatility3 2.28.0

> Memory forensics framework

## Identity

| Field | Value |
|-------|-------|
| Distribution | `volatility3` |
| Version | `2.28.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `vol`
- `volshell`

Invocation pattern:

```bash
vol --help
```

Alternates:

```bash
volshell --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `volatility3`

Invocation pattern:

```python
import volatility3
print("volatility3 loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import volatility3; print('volatility3 OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
