---
name: azazael-pkg-chirp
description: Callable skill for Python package chirp 20251108 — A cross-platform cross-radio programming tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# chirp 20251108

> A cross-platform cross-radio programming tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `chirp` |
| Version | `20251108` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `chirpc`
- `chirpw`
- `experttune`

Invocation pattern:

```bash
chirpc --help
```

Alternates:

```bash
chirpw --help
experttune --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `chirp`

Invocation pattern:

```python
import chirp
print("chirp loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import chirp; print('chirp OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
