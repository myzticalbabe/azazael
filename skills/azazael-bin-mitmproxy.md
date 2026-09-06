---
name: azazael-bin-mitmproxy
description: Callable skill for mitmproxy — Interactive HTTPS man-in-the-middle proxy
metadata:
  category: intercept
  project: azazael
  priority: medium
---

# mitmproxy

> Interactive HTTPS man-in-the-middle proxy

## Identity

| Field | Value |
|-------|-------|
| Tool | `mitmproxy` |
| Version | `11.x (Kali 3.13 backend)` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/mitmproxy (Kali)
```

## EXECUTE — canonical invocations

**Start interactive proxy:**

```bash
mitmproxy --listen-port 8080
```

**Non-interactive dump:**

```bash
mitmdump -w flows.mitm
```

**Transparent mode:**

```bash
mitmproxy --mode transparent
```

## Verify

```bash
mitmproxy --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
