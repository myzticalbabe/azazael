---
name: azazael-hats
description: Tool hat codification — White Hat / Red Hat (reserved) / Cerulean Hat (Blue). Hat follows authorization and intent. Canonical content lives at azazael/HAT_TAXONOMY.md.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael Hats — Tool Codification

> **This skill is a mirror of `azazael/HAT_TAXONOMY.md` — the single source of truth.**
> The canonical content lives at the project root and is maintained there.
> `sync_skills.py` propagates skill files to `.agents/skills/azazael-hats/SKILL.md`.

## Rule

Every tool is deemed White Hat or Red Hat in `HAT_TAXONOMY.md`, or it is
Cerulean Hat (Blue) by default. No other designations are used.

## Principle

The hat follows authorization and intent, not the binary. The Kali audit
arsenal (nmap, nuclei, ffuf, theHarvester, sherlock, sqlmap, BloodHound and
the rest — 34 tools, present in the kali-linux WSL2 distro) is White Hat
under authorization. Red Hat is a reserved designation for unauthorized
use only; nothing is currently deemed Red Hat.

## Usage

- **Read directly:** `read_files(["azazael/HAT_TAXONOMY.md"])` — 57+ tools
  explicitly listed with designation and status
- **Load as skill:** `skill("azazael-hats")` — loads from
  `.agents/skills/azazael-hats/SKILL.md`
- **Sync after edit:** `python azazael/src/scripts/sync_skills.py`

## Related

- `azazael/HAT_TAXONOMY.md` — Canonical single source of truth
- `azazael/SYSTEM_INSTRUCTIONS.md` — Hat Codification section
