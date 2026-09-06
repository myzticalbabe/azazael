---
name: azazael-bin-phoneinfoga
description: Callable skill for phoneinfoga — Phone number OSINT and footprinting
metadata:
  category: osint
  project: azazael
  priority: medium
---

# phoneinfoga

> Phone number OSINT and footprinting

## Identity

| Field | Value |
|-------|-------|
| Tool | `phoneinfoga` |
| Version | `2.11.0` |
| Status | INSTALLED |

## Install

```bash
Installed at /usr/local/bin/phoneinfoga (2.11.0 prebuilt release)
```

## EXECUTE — canonical invocations

**Lookup number:**

```bash
phoneinfoga scan -n +33612345678
```

**Start web UI:**

```bash
phoneinfoga serve
```

## Verify

```bash
phoneinfoga --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
