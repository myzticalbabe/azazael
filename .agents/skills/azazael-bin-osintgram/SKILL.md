---
name: azazael-bin-osintgram
description: Callable skill for osintgram — Instagram OSINT via public API
metadata:
  category: osint
  project: azazael
  priority: medium
---

# osintgram

> Instagram OSINT via public API

## Identity

| Field | Value |
|-------|-------|
| Tool | `osintgram` |
| Version | `master (clone, /root/osint-tools/Osintgram)` |
| Status | INSTALLED |

## Install

```bash
Cloned at /root/osint-tools/Osintgram (git clone https://github.com/Datalux/Osintgram && pip3 install -r requirements.txt)
```

## EXECUTE — canonical invocations

**Configure username:**

```bash
echo 'target' > config/settings.json
```

**Run commands:**

```bash
python3 main.py info
```

**Get followers:**

```bash
python3 main.py followers
```

## Verify

```bash
cd /root/osint-tools/Osintgram && python3 main.py --help | head -10
```

## Invoke

Not a PATH binary — run via the project clone:

```bash
cd /root/osint-tools/Osintgram && python3 main.py
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
