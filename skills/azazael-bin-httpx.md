---
name: azazael-bin-httpx
description: "Callable skill for httpx — Fast HTTP probe tool (ProjectDiscovery Go) — discover working HTTP hosts. NOTE: system 'httpx' is the Python CLI, not this tool."
metadata:
  category: recon
  project: azazael
  priority: medium
---

# httpx

> Fast HTTP probe tool (ProjectDiscovery Go) — discover working HTTP hosts. NOTE: system `httpx` is the Python CLI, not this tool.

## Identity

| Field | Value |
|-------|-------|
| Tool | `httpx` |
| Version | `not installed` |
| Status | NOT INSTALLED — install first |

## Install

```bash
go install github.com/projectdiscovery/httpx/cmd/httpx@latest  (system /usr/bin/httpx is the Python CLI — do not confuse)
```

## EXECUTE — canonical invocations

**Probe hosts for live HTTP:**

```bash
httpx -l hosts.txt -title -status-code
```

**Single target:**

```bash
httpx -u https://target.com -tech-detect
```

**Follow redirects + screenshot:**

```bash
httpx -l hosts.txt -follow-redirects -screenshot
```

## Verify

```bash
command -v httpx && echo 'httpx installed OK'
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
