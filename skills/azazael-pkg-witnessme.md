---
name: azazael-pkg-witnessme
description: Callable skill for Python package witnessme 1.5.0 — Web Inventory tool that uses Pyppeteer (headless Chrome/Chromium) and provides some extra bells & whistles to make life easier.
metadata:
  category: packages
  project: azazael
  priority: low
---

# witnessme 1.5.0

> Web Inventory tool that uses Pyppeteer (headless Chrome/Chromium) and provides some extra bells & whistles to make life easier.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `witnessme` |
| Version | `1.5.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `witnessme`
- `wmapi`
- `wmdb`

Invocation pattern:

```bash
witnessme --help
```

Alternates:

```bash
wmapi --help
wmdb --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `witnessme`

Invocation pattern:

```python
import witnessme
print("witnessme loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import witnessme; print('witnessme OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
