---
name: azazael-bin-nuclei
description: Callable skill for nuclei — Fast vulnerability scanner based on YAML templates (ProjectDiscovery)
metadata:
  category: recon
  project: azazael
  priority: medium
---

# nuclei

> Fast vulnerability scanner based on YAML templates (ProjectDiscovery)

## Identity

| Field | Value |
|-------|-------|
| Tool | `nuclei` |
| Version | `/_/ /_/\__,_/\___/_/\___/_/   v3.8.0` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/nuclei (Kali)
```

## EXECUTE — canonical invocations

**Scan target with default templates:**

```bash
nuclei -u https://target.com
```

**Scan list of hosts:**

```bash
nuclei -l hosts.txt
```

**Specific template:**

```bash
nuclei -u https://target.com -t http/exposures/
```

**Update templates:**

```bash
nuclei -update-templates
```

## Verify

```bash
nuclei --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
