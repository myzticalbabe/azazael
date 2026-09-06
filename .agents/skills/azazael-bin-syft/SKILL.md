---
name: azazael-bin-syft
description: Callable skill for syft — Generate SBOM (Software Bill of Materials) from container images/filesystems (Anchore)
metadata:
  category: security
  project: azazael
  priority: medium
---

# syft

> Generate SBOM (Software Bill of Materials) from container images/filesystems (Anchore)

## Identity

| Field | Value |
|-------|-------|
| Tool | `syft` |
| Version | `syft [not provided]` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/syft (Kali)
```

## EXECUTE — canonical invocations

**SBOM for image:**

```bash
syft nginx:latest
```

**SPDX output:**

```bash
syft nginx:latest -o spdx-json
```

**SBOM for dir:**

```bash
syft dir:./project
```

## Verify

```bash
syft --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
