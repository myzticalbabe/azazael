---
name: azazael-bin-wpscan
description: Callable skill for wpscan — WordPress vulnerability scanner
metadata:
  category: web
  project: azazael
  priority: medium
---

# wpscan

> WordPress vulnerability scanner

## Identity

| Field | Value |
|-------|-------|
| Tool | `wpscan` |
| Version | `Version 3.8.28` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/wpscan (Kali)
```

## EXECUTE — canonical invocations

**Basic scan:**

```bash
wpscan --url https://target.com
```

**Enumerate users/plugins:**

```bash
wpscan --url https://target.com --enumerate u,vp
```

**API token scan:**

```bash
wpscan --url https://target.com --api-token TOKEN
```

## Verify

```bash
wpscan --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
