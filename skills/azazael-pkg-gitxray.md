---
name: azazael-pkg-gitxray
description: Callable skill for Python package gitxray 1.0.20 — A multifaceted security tool which leverages Public GitHub REST APIs for OSINT, Forensics, Pentesting and more.
metadata:
  category: packages
  project: azazael
  priority: low
---

# gitxray 1.0.20

> A multifaceted security tool which leverages Public GitHub REST APIs for OSINT, Forensics, Pentesting and more.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `gitxray` |
| Version | `1.0.20` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `gitxray`

Invocation pattern:

```bash
gitxray --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `gitxray`

Invocation pattern:

```python
import gitxray
print("gitxray loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import gitxray; print('gitxray OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
