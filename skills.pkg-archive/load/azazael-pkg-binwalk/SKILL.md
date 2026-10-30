---
name: azazael-pkg-binwalk
description: Callable skill for Python package binwalk 2.4.3 — Firmware analysis tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# binwalk 2.4.3

> Firmware analysis tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `binwalk` |
| Version | `2.4.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `binwalk`

Invocation pattern:

```bash
binwalk --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `binwalk`

Invocation pattern:

```python
import binwalk
print("binwalk loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import binwalk; print('binwalk OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
