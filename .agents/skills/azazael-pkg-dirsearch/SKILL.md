---
name: azazael-pkg-dirsearch
description: Callable skill for Python package dirsearch 0.4.3 — Advanced web path scanner
metadata:
  category: packages
  project: azazael
  priority: low
---

# dirsearch 0.4.3

> Advanced web path scanner

## Identity

| Field | Value |
|-------|-------|
| Distribution | `dirsearch` |
| Version | `0.4.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `dirsearch`

Invocation pattern:

```bash
dirsearch --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `dirsearch`

Invocation pattern:

```python
import dirsearch
print("dirsearch loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import dirsearch; print('dirsearch OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
