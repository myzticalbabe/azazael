---
name: azazael-pkg-aiosmb
description: Callable skill for Python package aiosmb 0.4.4 — Asynchronous SMB protocol implementation
metadata:
  category: packages
  project: azazael
  priority: low
---

# aiosmb 0.4.4

> Asynchronous SMB protocol implementation

## Identity

| Field | Value |
|-------|-------|
| Distribution | `aiosmb` |
| Version | `0.4.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `asmbcertreq`
- `asmbclient`
- `asmbgetfile`
- `asmbscanner`
- `asmbshareenum`

Invocation pattern:

```bash
asmbcertreq --help
```

Alternates:

```bash
asmbclient --help
asmbgetfile --help
asmbscanner --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `aiosmb`

Invocation pattern:

```python
import aiosmb
print("aiosmb loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import aiosmb; print('aiosmb OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
