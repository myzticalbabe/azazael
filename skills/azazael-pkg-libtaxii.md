---
name: azazael-pkg-libtaxii
description: Callable skill for Python package libtaxii 1.1.119 — TAXII 1.X Library.
metadata:
  category: packages
  project: azazael
  priority: low
---

# libtaxii 1.1.119

> TAXII 1.X Library.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `libtaxii` |
| Version | `1.1.119` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `collection_information_client`
- `discovery_client`
- `discovery_client_10`
- `feed_information_client_10`
- `fulfillment_client`
- `inbox_client`
- `inbox_client_10`
- `poll_client`
- ... plus 2 more

Invocation pattern:

```bash
collection_information_client --help
```

Alternates:

```bash
discovery_client --help
discovery_client_10 --help
feed_information_client_10 --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `libtaxii`

Invocation pattern:

```python
import libtaxii
print("libtaxii loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import libtaxii; print('libtaxii OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
