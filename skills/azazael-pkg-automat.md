---
name: azazael-pkg-automat
description: Callable skill for Python package Automat 25.4.16 — Self-service finite-state machines for the programmer on the go.
metadata:
  category: packages
  project: azazael
  priority: low
---

# Automat 25.4.16

> Self-service finite-state machines for the programmer on the go.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `Automat` |
| Version | `25.4.16` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `automat-visualize`

Invocation pattern:

```bash
automat-visualize --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `Automat`

Invocation pattern:

```python
import Automat
print("Automat loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import Automat; print('Automat OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
