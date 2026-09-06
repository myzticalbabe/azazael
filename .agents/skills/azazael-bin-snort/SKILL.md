---
name: azazael-bin-snort
description: Callable skill for snort — Open-source network intrusion detection/prevention system (Cisco)
metadata:
  category: ids
  project: azazael
  priority: medium
---

# snort

> Open-source network intrusion detection/prevention system (Cisco)

## Identity

| Field | Value |
|-------|-------|
| Tool | `snort` |
| Version | `o"  )~   Version 3.12.2.0` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/snort (Kali)
```

## EXECUTE — canonical invocations

**Run in IDS mode:**

```bash
snort -i eth0 -c /etc/snort/snort.conf -A console
```

**Analyze pcap:**

```bash
snort -r capture.pcap -c /etc/snort/snort.conf -A console
```

**Test config:**

```bash
snort -c /etc/snort/snort.conf -T
```

## Verify

```bash
snort --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
