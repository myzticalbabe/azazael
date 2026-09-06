---
name: azazael-pkg-plotext
description: Callable skill for Python package plotext 5.2.8 — plotext plots directly on terminal
metadata:
  category: packages
  project: azazael
  priority: low
---

# plotext 5.2.8

> plotext plots directly on terminal

## Identity

| Field | Value |
|-------|-------|
| Distribution | `plotext` |
| Version | `5.2.8` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `plotext`

Invocation pattern:

```bash
plotext --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `plotext`

Invocation pattern:

```python
import plotext
print("plotext loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import plotext; print('plotext OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
