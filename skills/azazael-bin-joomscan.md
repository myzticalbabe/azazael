---
name: azazael-bin-joomscan
description: Callable skill for joomscan — Joomla CMS vulnerability scanner (OWASP)
metadata:
  category: web
  project: azazael
  priority: medium
---

# joomscan

> Joomla CMS vulnerability scanner (OWASP)

## Identity

| Field | Value |
|-------|-------|
| Tool | `joomscan` |
| Version | `+---++---==[Version : 0.0.7` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/joomscan (Kali)
```

## EXECUTE — canonical invocations

**Basic scan:**

```bash
joomscan -u https://target.com
```

**Scan with proxy:**

```bash
joomscan -u https://target.com -p http://127.0.0.1:8080
```

## Verify

```bash
joomscan --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
