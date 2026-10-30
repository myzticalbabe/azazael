---
name: azazael-pkg-opentaxii
description: Callable skill for Python package opentaxii 0.9.3 — TAXII server implementation in Python from EclecticIQ
metadata:
  category: packages
  project: azazael
  priority: low
---

# opentaxii 0.9.3

> TAXII server implementation in Python from EclecticIQ

## Identity

| Field | Value |
|-------|-------|
| Distribution | `opentaxii` |
| Version | `0.9.3` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `opentaxii-add-api-root`
- `opentaxii-add-collection`
- `opentaxii-create-account`
- `opentaxii-delete-blocks`
- `opentaxii-job-cleanup`
- `opentaxii-run-dev`
- `opentaxii-sync-data`
- `opentaxii-update-account`

Invocation pattern:

```bash
opentaxii-add-api-root --help
```

Alternates:

```bash
opentaxii-add-collection --help
opentaxii-create-account --help
opentaxii-delete-blocks --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `opentaxii`

Invocation pattern:

```python
import opentaxii
print("opentaxii loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import opentaxii; print('opentaxii OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
