---
name: azazael-pkg-artifacts
description: Callable skill for Python package artifacts 20230928 — ForensicArtifacts.com Artifact Repository.
metadata:
  category: packages
  project: azazael
  priority: low
---

# artifacts 20230928

> ForensicArtifacts.com Artifact Repository.

## Identity

| Field | Value |
|-------|-------|
| Distribution | `artifacts` |
| Version | `20230928` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — Python API

Importable top-level module(s):

- `artifacts`

Invocation pattern:

```python
import artifacts
print("artifacts loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import artifacts; print('artifacts OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
