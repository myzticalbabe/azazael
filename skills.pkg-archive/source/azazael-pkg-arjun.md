---
name: azazael-pkg-arjun
description: Callable skill for Python package arjun 2.2.7 — HTTP parameter discovery suite
metadata:
  category: packages
  project: azazael
  priority: low
---

# arjun 2.2.7

> HTTP parameter discovery suite

## Identity

| Field | Value |
|-------|-------|
| Distribution | `arjun` |
| Version | `2.2.7` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `arjun`

Invocation pattern:

```bash
arjun --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `arjun`

Invocation pattern:

```python
import arjun
print("arjun loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import arjun; print('arjun OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
