---
name: azazael-pkg314t-idna
description: Callable skill for Python package idna 3.18 — Internationalized Domain Names in Applications (IDNA)
metadata:
  category: packages
  project: azazael
  priority: low
---

# idna 3.18

> Internationalized Domain Names in Applications (IDNA)

## Identity

| Field | Value |
|-------|-------|
| Distribution | `idna` |
| Version | `3.18` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.14t -m` or directly):

- `idna`

Invocation pattern:

```bash
idna --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `idna`

Invocation pattern:

```python
import idna
print("idna loaded OK")
```

## Verify

```bash
/usr/local/bin/python3.14t -c "import idna; print('idna OK')"
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
