---
name: azazael-bin-hydra
description: Callable skill for hydra — Online password cracking (network services brute-force)
metadata:
  category: cracking
  project: azazael
  priority: medium
---

# hydra

> Online password cracking (network services brute-force)

## Identity

| Field | Value |
|-------|-------|
| Tool | `hydra` |
| Version | `Hydra v9.7 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or ` |
| Status | INSTALLED |

## Install

```bash
Present at /usr/bin/hydra (Kali)
```

## EXECUTE — canonical invocations

**Brute-force SSH:**

```bash
hydra -l root -P pass.txt ssh://192.168.1.1
```

**Brute-force web login:**

```bash
hydra -l admin -P pass.txt 192.168.1.1 http-post-form '/login:user=^USER^&pass=^PASS^:F=incorrect'
```

**SMB brute-force:**

```bash
hydra -L users.txt -P pass.txt smb://target
```

## Verify

```bash
hydra --help | head -20
```

## Related

- Part of the Azazael binary-tool skill set (`azazael-bin-*`)
- See SKILLS_CATALOG.md for the full skill inventory
