---
name: azazael-pkg314t-patchelf
description: Callable skill for Python package patchelf 0.17.2.4 — A small utility to modify the dynamic linker and RPATH of ELF executables.
metadata:
  category: packages
  project: azazael
  priority: low
---

# patchelf 0.17.2.4

> A small utility to modify the dynamic linker and RPATH of ELF executables.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `patchelf` |
| Version | `0.17.2.4` |
| Interpreter | Python 3.14.6 free-threading (`/usr/local/bin/python3.14t`) |

## Notes

No console entry points or detectable top-level modules; treat as a library dependency.

## Verify

```bash
/usr/local/bin/python3.14t -m pip show patchelf
```

## Related

- Environment: Azazael Python 3.14.6 (3.14t) environment packages
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
