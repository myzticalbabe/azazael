---
name: azazael-bin-sherlock
description: Callable skill for sherlock — Hunt down social media accounts by username
metadata:
  category: osint
  project: azazael
  priority: medium
---

# sherlock

> Hunt down social media accounts by username

## Identity

| Field | Value |
|-------|-------|
| Tool | `sherlock` |
| Version | `v0.16.0` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/sherlock (Kali)
```

## EXECUTE — canonical invocations

**Search username:**

```bash
sherlock username
```

**Multiple usernames:**

```bash
sherlock user1 user2 user3
```

**Save to file:**

```bash
sherlock username --output results.txt
```

## Verify

```bash
sherlock --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
