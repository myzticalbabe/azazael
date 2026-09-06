---
name: azazael-bin-ghunt
description: Callable skill for ghunt — Google account OSINT (requires cookies)
metadata:
  category: osint
  project: azazael
  priority: medium
---

# ghunt

> Google account OSINT (requires cookies)

## Identity

| Field | Value |
|-------|-------|
| Tool | `ghunt` |
| Version | `v2.15.0 (clone, /root/osint-tools/GHunt)` |
| Status | INSTALLED |

## Install

```bash
Cloned at /root/osint-tools/GHunt (git clone https://github.com/mxrch/GHunt)
```

## EXECUTE — canonical invocations

**Login with cookies:**

```bash
python3 ghunt.py login
```

**Lookup account:**

```bash
python3 ghunt.py email target@gmail.com
```

## Verify

```bash
cd /root/osint-tools/GHunt && python3 ghunt.py --help | head -10
```

## Invoke

Not a PATH binary — run via the project clone:

```bash
cd /root/osint-tools/GHunt && python3 ghunt.py
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
