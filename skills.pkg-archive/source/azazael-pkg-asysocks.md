---
name: azazael-pkg-asysocks
description: Callable skill for Python package asysocks 0.2.12 — No summary available.
metadata:
  category: packages
  project: azazael
  priority: low
---

# asysocks 0.2.12

> No summary available.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `asysocks` |
| Version | `0.2.12` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `asysocks-brute`
- `asysocks-portscan`
- `asysocks-proxy`
- `asysocks-sec`
- `asysocks-tunnel`

Invocation pattern:

```bash
asysocks-brute --help
```

Alternates:

```bash
asysocks-portscan --help
asysocks-proxy --help
asysocks-sec --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `asysocks`

Invocation pattern:

```python
import asysocks
print("asysocks loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import asysocks; print('asysocks OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
