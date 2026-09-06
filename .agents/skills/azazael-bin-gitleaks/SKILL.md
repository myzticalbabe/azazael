---
name: azazael-bin-gitleaks
description: Callable skill for gitleaks — Scan git repos for secrets and credentials
metadata:
  category: security
  project: azazael
  priority: medium
---

# gitleaks

> Scan git repos for secrets and credentials

## Identity

| Field | Value |
|-------|-------|
| Tool | `gitleaks` |
| Version | `version` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/gitleaks (Kali)
```

## EXECUTE — canonical invocations

**Scan local repo:**

```bash
gitleaks detect --source .
```

**Scan staged changes:**

```bash
gitleaks protect --staged
```

**Full repo history:**

```bash
gitleaks detect --source . --log-opts='--all'
```

## Verify

```bash
gitleaks --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
