---
name: azazael-pkg-stegcracker
description: Callable skill for Python package stegcracker 2.1.0 — Steganography brute-force utility to uncover hidden data inside files.
metadata:
  category: packages
  project: azazael
  priority: low
---

# stegcracker 2.1.0

> Steganography brute-force utility to uncover hidden data inside files.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `stegcracker` |
| Version | `2.1.0` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `stegcracker`

Invocation pattern:

```bash
stegcracker --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `stegcracker`

Invocation pattern:

```python
import stegcracker
print("stegcracker loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import stegcracker; print('stegcracker OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
