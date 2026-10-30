---
name: azazael-pkg-shellfire
description: Callable skill for Python package shellfire 0.14 — shellfire is an exploitation shell focusing on exploiting command injection vulnerabilities, eg., LFI, RFI, SSTI, etc.
metadata:
  category: packages
  project: azazael
  priority: low
---

# shellfire 0.14

> shellfire is an exploitation shell focusing on exploiting command injection vulnerabilities, eg., LFI, RFI, SSTI, etc.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `shellfire` |
| Version | `0.14` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `shellfire`

Invocation pattern:

```bash
shellfire --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `shellfire`

Invocation pattern:

```python
import shellfire
print("shellfire loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import shellfire; print('shellfire OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
