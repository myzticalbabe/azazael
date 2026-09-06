---
name: azazael-bin-responder
description: Callable skill for responder — LLMNR/NBT-NS/mDNS responder for credential capture
metadata:
  category: intercept
  project: azazael
  priority: medium
---

# responder

> LLMNR/NBT-NS/mDNS responder for credential capture

## Identity

| Field | Value |
|-------|-------|
| Tool | `responder` |
| Version | `You need to install python3-netifaces or run Responder with python3...` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/responder (Kali)
```

## EXECUTE — canonical invocations

**Run all poisoners:**

```bash
responder -I eth0 -A
```

**Analyze only mode:**

```bash
responder -I eth0 -A -w
```

**Disable WPAD proxy:**

```bash
responder -I eth0 -wF
```

## Verify

```bash
responder --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
