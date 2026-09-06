---
name: azazael-bin-trivy
description: Callable skill for trivy — Comprehensive vulnerability scanner for containers, filesystems, git repos (Aqua Security)
metadata:
  category: security
  project: azazael
  priority: medium
---

# trivy

> Comprehensive vulnerability scanner for containers, filesystems, git repos (Aqua Security)

## Identity

| Field | Value |
|-------|-------|
| Tool | `trivy` |
| Version | `Version: dev` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/trivy (Kali)
```

## EXECUTE — canonical invocations

**Scan container image:**

```bash
trivy image nginx:latest
```

**Scan filesystem:**

```bash
trivy fs /path/to/project
```

**Scan git repo:**

```bash
trivy repo https://github.com/org/repo
```

**Scan IaC:**

```bash
trivy config ./terraform
```

## Verify

```bash
trivy --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
