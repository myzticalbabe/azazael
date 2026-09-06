---
name: azazael-catalog-reconciliation
description: SKILLS_CATALOG.md numbering reconciliation pattern — master table
  is the source of truth, bucket-sum verification, and the cascading-undercount
  trap. Covers INVENTORY-vs-rows drift, section-range accounting, appended
  session-skill rows (#1221+), and the off-by-one root cause where a new table
  row is added without bumping the inventory total.
metadata:
  category: process
  project: azazael
  auto_load: false
  version: 1.0.0
  created: 2026-09-02
---

# SKILLS_CATALOG Numbering Reconciliation

## Core Rule: The Master Table Is the Truth

Per `azazael-catalog-maintenance`, the `## Skill Quick Reference` table contains
**ALL skills, sequentially numbered, no gaps**. Whenever the Inventory Summary
disagrees with the table, **the table wins** — reconcile the summary to the
table, never the reverse.

## The Cascading-Undercount Trap (root cause, discovered 2026-09-02)

**Symptom:** the Inventory Total is exactly 1 lower than the row count, and the
"Core skills" count is a few short of reality.

**Root cause:** a new row (`#1221 kali-graph-protocol`, added Aug 31, 2026) was
appended to the table but its author **never bumped the Inventory Total**.
Every later addition inherited the off-by-one — each session that added N rows
also set the total only N−1 higher than its predecessor. Additionally, the two
pre-trapped rows (`#1221`–`#1222`) were never counted in "Core skills
(non-package)" at all, so later "core" increments under-counted by 2.

**The cascade math:**
```
table rows after #1221+#1222  = 1,222   claimed total = 1,221  (off by 1)
+AOA ×4   → rows 1,226        claimed 1,225                    (off by 1)
+sweep ×13→ rows 1,239        claimed 1,238                    (off by 1)
```
Core: 132 base claimed → 149, but true core = 132 + **19** appended non-package
rows = **151**.

## Reconciliation Procedure

1. **Count the table.** Parse every `| N | \`name\` |` row. Verify:
   - rows are fully contiguous `1..max` (zero gaps),
   - zero duplicate numbers.
2. **Bucket by section ranges** (the `## Skill Quick Reference` headers):
   - Core 1–132 · Kali package 133–1100 · 3.14t package 1101–1174 ·
     Binary tool 1175–1220
   - **Appended session skills = rows > 1220** (kali-graph #1221 onward).
     These are non-package by definition → all count as **Core**.
3. **Bucket-sum check:** `core + kali + 3.14t + binary` MUST equal the total
   row count. Any mismatch = a summary error.

   ```
   example (2026-09-02 corrected state):
   151 core + 968 kali + 74 3.14t + 46 binary = 1239 rows  ✓
   ```
4. **Fix the Inventory Summary** (`## Inventory Summary`):
   - Total canonical skills = exact row count.
   - Core skills (non-package) = section-core (132) + appended (rows >1220).
   - Leave Kali / 3.14t / Binary counts alone (they match their section
     ranges; verify, don't assume).
5. **Annotate the header** — append a "Current: N total" line under the
   "Last Updated" note so the growth is visible at a glance.
6. **Re-verify** with bucket-sum, and re-sync the catalog to **all** mirrors
   (3 G: catalog copies: AZAZAEL_ROOT / source-of-truth / AZAZAEL_SOURCE_OF_TRUTH
   + azazael-dev + Kali WSL `/root/azazael/`, `MSYS_NO_PATHCONV=1` for the
   wsl bridge).

## Verification Snippet (Python, exact-token safe)

Use exact backticked-token matching when checking a skill is *registered* —
substring checks false-positive hard: `azazael-inference` matches insider
`azazael-inference-protocol`, and regex token patterns miss `bin-theHarvester`
(capital-H) and `python3.14-ml` (dot). A bare `if name in catalog` either way
is not sufficient; test with `` catalog.count("`"+name+"`") ``.

## Anti-Patterns

- **Editing the summary to match a mistaken count** instead of the master
  table. The table is generated from the real skill set; the summary is
  derived state.
- **Adding a row without bumping the total** — create the off-by-one the
  cascade starts from. Always do the table-add and the count-bump as one edit.
- **Trusting a previous session's count** — the cascade is silent; only a
  fresh count against the current table is trustworthy.
- **Fixing only the total** — a legacy under-count of early rows (like
  #1221–#1222 missing from Core) persists until Core is recomputed as
  `section-core + appended`, not just incremented.
- **Forgetting the mirrors** — the catalog exists in 5+ places; a corrected
  count that stays local is still a stale artifact everywhere else.

## Session Records

- 2026-09-02: reconciled 1,238→**1,239** total (core 149→**151**) after
  `#1221 kali-graph-protocol` (Aug 31) started a cascading off-by-one that
  propagated through +19 appended session rows. Bucket-sum 151+968+74+46=1,239
  verified; header annotated; all mirrors updated.