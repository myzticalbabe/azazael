---
name: azazael-pkg-scapy
description: Callable skill for Python package scapy 2.7.1 — Scapy: interactive packet manipulation tool
metadata:
  category: packages
  project: azazael
  priority: low
---

# scapy 2.7.1

> Scapy: interactive packet manipulation tool

## Identity

| Field | Value |
|-------|-------|
| Distribution | `scapy` |
| Version | `2.7.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `scapy`

Invocation pattern:

```bash
scapy --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `scapy`

Invocation pattern:

```python
import scapy
print("scapy loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import scapy; print('scapy OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
