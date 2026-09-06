---
name: azazael-pkg-minikerberos
description: Callable skill for Python package minikerberos 0.4.4 — Kerberos manipulation library in pure Python
metadata:
  category: packages
  project: azazael
  priority: low
---

# minikerberos 0.4.4

> Kerberos manipulation library in pure Python

## Identity

| Field | Value |
|-------|-------|
| Distribution | `minikerberos` |
| Version | `0.4.4` |
| Interpreter | Python 3.13.12 (`/usr/bin/python3.13`) |

## EXECUTE — CLI entry points

The package installs the following console commands (run with `python3.13 -m` or directly):

- `minikerberos-asreproast`
- `minikerberos-ccache2kirbi`
- `minikerberos-ccacheedit`
- `minikerberos-ccacheroast`
- `minikerberos-changepw`
- `minikerberos-cve202233647`
- `minikerberos-cve202233679`
- `minikerberos-getNTPKInit`
- ... plus 7 more

Invocation pattern:

```bash
minikerberos-asreproast --help
```

Alternates:

```bash
minikerberos-ccache2kirbi --help
minikerberos-ccacheedit --help
minikerberos-ccacheroast --help
```

## EXECUTE — Python API

Importable top-level module(s):

- `minikerberos`

Invocation pattern:

```python
import minikerberos
print("minikerberos loaded OK")
```

## Verify

```bash
/usr/bin/python3.13 -c "import minikerberos; print('minikerberos OK')"
```

## Related

- Environment: Kali Python 3.13.12 system packages (969 total)
- See `azazael-skill-catalog` / SKILLS_CATALOG.md for the full skill inventory
