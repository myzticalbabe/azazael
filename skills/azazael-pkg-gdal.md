---
name: azazael-pkg-gdal
description: Callable skill for Python package GDAL 3.13.1 — GDAL: Geospatial Data Abstraction Library
metadata:
  category: packages
  project: azazael
  priority: low
---

# GDAL 3.13.1

> GDAL: Geospatial Data Abstraction Library

## Identity

| Field | Value |
|-------|-------|
| Distribution | `GDAL` |
| Version | `3.13.1` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `gdal2tiles`
- `gdal2xyz`
- `gdal_calc`
- `gdal_edit`
- `gdal_fillnodata`
- `gdal_merge`
- `gdal_pansharpen`
- `gdal_polygonize`
- ... plus 10 more

Invocation pattern:

```bash
gdal2tiles --help
```

Alternates:

```bash
gdal2xyz --help
gdal_calc --help
gdal_edit --help
```

## Verify

```bash
/usr/bin/python3.13 -m pip show GDAL
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
