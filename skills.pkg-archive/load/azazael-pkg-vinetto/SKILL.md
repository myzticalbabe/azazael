---
name: azazael-pkg-vinetto
description: Callable skill for Python package vinetto 0.9.15 — Vinetto: The Thumbnail File Parser
metadata:
  category: packages
  project: azazael
  priority: low
---

# vinetto 0.9.15

> Vinetto: The Thumbnail File Parser

## Identity

| Field | Value |
|-------|-------|
| Distribution | `vinetto` |
| Version | `0.9.15` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `vinetto`

Invocation pattern:

```bash
vinetto --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `vinetto`

Invocation pattern:

```python
import vinetto
print("vinetto loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import vinetto; print('vinetto OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
