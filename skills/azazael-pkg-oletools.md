---
name: azazael-pkg-oletools
description: Callable skill for Python package oletools 0.60.2 — Python tools to analyze security characteristics of MS Office and OLE files (also called Structured Storage, Compound File Binary Format or Compound Document Fi
metadata:
  category: packages
  project: azazael
  priority: low
---

# oletools 0.60.2

> Python tools to analyze security characteristics of MS Office and OLE files (also called Structured Storage, Compound File Binary Format or Compound Document Fi

## Identity

| Field | Value |
|-------|-------|
| Distribution | `oletools` |
| Version | `0.60.2` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `ezhexviewer`
- `ftguess`
- `mraptor`
- `msodde`
- `olebrowse`
- `oledir`
- `olefile`
- `oleid`
- ... plus 7 more

Invocation pattern:

```bash
ezhexviewer --help
```

Alternates:

```bash
ftguess --help
mraptor --help
msodde --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `oletools`

Invocation pattern:

```python
import oletools
print("oletools loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import oletools; print('oletools OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
