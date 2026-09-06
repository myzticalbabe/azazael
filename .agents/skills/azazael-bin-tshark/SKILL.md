---
name: azazael-bin-tshark
description: Callable skill for tshark — CLI packet analyzer (Wireshark terminal edition)
metadata:
  category: network
  project: azazael
  priority: medium
---

# tshark

> CLI packet analyzer (Wireshark terminal edition)

## Identity

| Field | Value |
|-------|-------|
| Tool | `tshark` |
| Version | `Licensed under the terms of the GNU General Public License (version 2 or later).` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/tshark (Kali)
```

## EXECUTE — canonical invocations

**Capture on interface:**

```bash
tshark -i eth0
```

**Read pcap file:**

```bash
tshark -r capture.pcap
```

**Filter HTTP traffic:**

```bash
tshark -r capture.pcap -Y 'http.request'
```

**Extract fields:**

```bash
tshark -r capture.pcap -T fields -e ip.src -e ip.dst
```

## Verify

```bash
tshark --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
