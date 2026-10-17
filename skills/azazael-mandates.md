---
name: azazael-mandates
description: Complete Codification of ALL active mandates — 37 total (31 RULEs 0A-0Z-C + 1 mandatory enforcement mechanism + 5 promoted RULEs 0B-0F). Canonical content lives at MANDATES.md.
metadata:
  category: system
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael MANDATES — Complete Codification

> **This skill is a mirror of `MANDATES.md` — the single source of truth.**
> The canonical content lives at the project root and is maintained there.
> `sync_skills.py` propagates MANDATES.md content to `.agents/skills/azazael-mandates/SKILL.md`.

## Purpose

MANDATES.md contains all 37 active mandates: 31 RULEs (0A through 0Z-C including sub-rules 0H-A, 0Q-A, 0T-A, 0T-B, 0Z-A, plus promoted RULEs 0B-0F), 1 mandatory enforcement mechanism (PRE-ACTION GATE BANNER / RULE 0S), agent classification reference, and priority tiers.

## Usage

- **Read directly:** `read_files(["MANDATES.md"])`
- **Load as skill:** `skill("azazael-mandates")` — loads from `.agents/skills/azazael-mandates/SKILL.md`
- **Sync after edit:** `python src/SCRIPTS/sync_skills.py`

## Related

- `MANDATES.md` — Canonical single source of truth
- `SYSTEM_INSTRUCTIONS.md` — RULEs canonical source (primary)
- `SOP.md` — Procedural mirror (secondary)
- `skill("azazael-mandates")` — Pre-loaded at every session start (auto_load: true); loads from `.agents/skills/azazael-mandates/SKILL.md`
- `azazael-system-startup` — Includes MANDATES.md in Step 1 `read_files()` call for automatic session loading
