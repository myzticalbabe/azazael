---
name: azazael-bin-trufflehog
description: Callable skill for trufflehog — Find leaked credentials across repos/files/APIs
metadata:
  category: security
  project: azazael
  priority: medium
---

# trufflehog

> Find leaked credentials across repos/files/APIs

## Identity

| Field | Value |
|-------|-------|
| Tool | `trufflehog` |
| Version | `trufflehog: error: expected command but got "version", try --help` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/trufflehog (Kali)
```

## EXECUTE — canonical invocations

**Scan git repo:**

```bash
trufflehog git https://github.com/org/repo
```

**Scan filesystem:**

```bash
trufflehog filesystem /path/to/dir
```

**Scan GitHub org:**

```bash
trufflehog github --org=orgname
```

## Verify

```bash
trufflehog --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
