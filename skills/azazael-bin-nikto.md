---
name: azazael-bin-nikto
description: Callable skill for nikto — Web server scanner for misconfigurations and known vulnerabilities
metadata:
  category: web
  project: azazael
  priority: medium
---

# nikto

> Web server scanner for misconfigurations and known vulnerabilities

## Identity

| Field | Value |
|-------|-------|
| Tool | `nikto` |
| Version | `-Version           Print plugin and database versions` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/nikto (Kali)
```

## EXECUTE — canonical invocations

**Basic scan:**

```bash
nikto -h https://target.com
```

**Scan with port:**

```bash
nikto -h target.com -p 8443
```

**Save report:**

```bash
nikto -h target.com -o report.html -Format htm
```

## Verify

```bash
nikto --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
