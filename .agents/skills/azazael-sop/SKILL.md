---
name: azazael-sop
description: Standard Operating Procedure — ALL canonical mandates (RULEs 0A-0Z, Rule 0, COMPLIANCE SENTINEL), error recording, cleanup enforcement. Canonical content lives at azazael/SOP.md.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael SOP — Standard Operating Procedure

> **This skill is a mirror of `azazael/SOP.md` — the single source of truth.**
> The canonical content lives at the project root and is maintained there.
> `sync_skills.py` propagates SOP.md content to `.agents/skills/azazael-sop/SKILL.md`.

## Purpose

The SOP contains all canonical mandates (RULEs 0A-0Z, Rule 0, COMPLIANCE SENTINEL),
error recording procedures, cleanup enforcement, and operational templates.

## Usage

- **Read directly:** `read_files(["azazael/SOP.md"])`
- **Load as skill:** `skill("azazael-sop")` — loads from `.agents/skills/azazael-sop/SKILL.md`
- **Sync after edit:** `python azazael/src/scripts/sync_skills.py`

## Related

- `azazael/SOP.md` — Canonical single source of truth
- `azazael/SYSTEM_INSTRUCTIONS.md` — RULEs canonical source
- `azazael/ERROR_LOG.md` — Error recording ledger
