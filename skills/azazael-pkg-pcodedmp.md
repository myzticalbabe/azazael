---
name: azazael-pkg-pcodedmp
description: Callable skill for Python package pcodedmp 1.2.6 — A VBA p-code disassembler
metadata:
  category: packages
  project: azazael
  priority: low
---

# pcodedmp 1.2.6

> A VBA p-code disassembler

## Identity

| Field | Value |
|-------|-------|
| Distribution | `pcodedmp` |
| Version | `1.2.6` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `pcodedmp`

Invocation pattern:

```bash
pcodedmp --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `pcodedmp`

Invocation pattern:

```python
import pcodedmp
print("pcodedmp loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import pcodedmp; print('pcodedmp OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
