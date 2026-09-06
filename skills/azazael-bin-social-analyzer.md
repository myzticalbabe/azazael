---
name: azazael-bin-social-analyzer
description: Callable skill for social-analyzer — Social media analysis and API-free lookup
metadata:
  category: osint
  project: azazael
  priority: medium
---

# social-analyzer

> Social media analysis and API-free lookup

## Identity

| Field | Value |
|-------|-------|
| Tool | `social-analyzer` |
| Version | `master (clone, /root/osint-tools/social-analyzer)` |
| Status | INSTALLED |

## Install

```bash
Cloned at /root/osint-tools/social-analyzer (git clone https://github.com/qeeqbox/social-analyzer)
```

## EXECUTE — canonical invocations

**CLI search:**

```bash
node app.js --username username --metadata
```

**Start web UI:**

```bash
node app.js --webserver
```

## Verify

```bash
cd /root/osint-tools/social-analyzer && node app.js --help | head -10
```

## Invoke

Not a PATH binary — run via the project clone:

```bash
cd /root/osint-tools/social-analyzer && node app.js
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
