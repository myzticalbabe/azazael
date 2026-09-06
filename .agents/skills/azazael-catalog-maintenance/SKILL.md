---
name: azazael-catalog-maintenance
description: SKILLS_CATALOG.md format, numbering convention, Sections pattern, and maintenance procedures for adding new entries
metadata:
  category: process
  project: azazael
  priority: low
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# SKILLS_CATALOG.md Maintenance

## Format

Each entry follows this pattern:


## Numbering Convention

Entries are numbered sequentially. The quick reference table (## Skill Quick Reference)
contains ALL skills in one table. New skills are added at the END of this table.

The ## New Skills — Created sections group skills by creation session and are not
numbered within the section.

## Sections

1. **Quick Reference table** — Master list of all skills with #, name, category, description
2. **New Tools** — Non-skill tools created during sessions
3. **Skills Updated** — Updates to existing skills with dates
4. **New Skills — Created [Date]** — Grouped by session (Session 1, 2, 3, etc.)

## Adding a New Entry

1. Find the last entry in the Quick Reference table (e.g., | 67 |)
2. Add the new entry after it with the next sequential number
3. Optionally add to the relevant ## New Skills section
4. Run sync_skills.py to propagate to .agents/

## Common Issues

- **Bash backtick escaping**: Python inline scripts run from bash interpret backticks
  as command substitution. Use str_replace for catalog edits, not bash piping.
- **Duplicate entries**: Always check if the entry already exists before adding.
- **Number gaps**: Don't leave gaps in the numbering sequence.
