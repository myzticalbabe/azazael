---
name: azazael-todo-management
description: TODO document management methodology — versioning strategy, cross-referencing, ADDITIVE/REINFORCES/DUPLICATE classification, multiple-document consistency. Load before updating any TODO document.
metadata:
  category: process
  project: azazael
  version: 1.0.0
---

# Azazael TODO Management Methodology

## Overview

The Azazael project has multiple TODO documents at different levels of specificity.
This skill documents the methodology for keeping them consistent, versioned, and
non-contradictory when adding new findings or improvement items.

**Why:** 4+ TODO documents with overlapping scope means that every update to one
must be checked against all others. Without a disciplined methodology, items can
be duplicated, contradicted, or lost entirely.

---

## Document Inventory

| Document | Scope | Status | When to Update |
|----------|-------|--------|----------------|
| `CODEBASE_AUDIT_TODO.md` | Living production plan (12 Steps) | ✅ Primary | Every session with findings |
| `PRODUCTION_TODO.md` | Original production gaps | 🔴 Deprecated (active updates paused) | Do not update — archive when prioritized |
| `REWRITE_TODO.md` | Original rewrite plan | 🔴 Legacy | Do not update |
| `PHASE_6_TODO.md` | Phase-specific tasks | 🔴 Legacy | Do not update |

**Best practice:** Maintain ONE primary TODO document and explicitly mark all others
as "superseded by" with a redirect. Even if a secondary document was actively updated
in the past, marking it as Deprecated/Legacy eliminates ambiguity about whether new
findings should be added there.

**Transition note:** `PRODUCTION_TODO.md` was actively updated alongside
`CODEBASE_AUDIT_TODO.md` through June 3, 2026, creating potential confusion. All future
updates should go to `CODEBASE_AUDIT_TODO.md` only.

---

## State Snapshot Management

Every major update should include an updated State Snapshot at the top of the document.

### Snapshot Format
```markdown
## State Snapshot (Date — Description)

| Metric | Value | Change |
|--------|-------|--------|
| Python version | **3.14.6t ONLY** | ✅ Unchanged |
| Source files | **305+ .py** | ✅ Stable |
| Worms in registry | **~79** | ✅ Stable |
| Lessons catalog | **45 lessons** | 🟢 Updated |
| Error log | **55+ errors** | 🟢 Updated |
| ...
```

### Version Convention
```
v1 — Created
v2 — {Description of major update}
v3 — {Description of major update}
v4 — Architecture review completed (Date)
```

### What to Track in Snapshots
- Python version
- File counts (syntax-clean, source files)
- Worms in registry
- Desktop EXE count
- Lessons and error log counts
- Skills catalog count
- Recently fixed metrics (mypy errors, dedup count)
- Known issues (shell=True risks, legacy files)

---

## Adding New Items: Cross-Reference Classification

When adding new improvement items from a review or discovery session:

### Step 1: List existing Steps
Read the current Steps in the primary TODO document. These are typically numbered
sequentially (Step 1, Step 2, ... Step 12).

### Step 2: Classify each new item

```python
classification_choices = {
    "ADDITIVE": "Not covered by any existing Step — fully new scope",
    "REINFORCES": "Overlaps an existing Step but adds new detail or urgency",
    "DUPLICATE": "Already fully covered by an existing Step — skip",
}
```

### Step 3: Build cross-reference table

```
| # | AR-ID | Action | Priority | Existing Step | Additive? |
|---|-------|--------|----------|---------------|-----------|
| 1 | AR-1  | Fix shell=True usages | P0 | New (not in existing Steps) | ✅ Additive |
| 2 | AR-11 | Fix mypy errors | P1 | Overlaps Step 7 (perf opt) | ⚠️ Reinforces |
| 3 | AR-7  | Add pytest-cov | P1 | Step 3 (test suite) | ⚠️ Reinforces |
```

### Step 4: Track the ratio

```
**7 of 12 items are additive** (58% — not covered by existing Steps).
**5 of 12 items reinforce** existing Steps 3, 6, 7, 11.
```

**Interpretation guide:**
| Ratio | Meaning | Action |
|-------|---------|--------|
| >50% additive | TODO was missing significant scope | Good sign — review uncovered real gaps |
| 20-50% additive | TODO was moderately comprehensive | Review validated + extended planning |
| <20% additive | TODO was already comprehensive | Review validated existing planning |

---

## Priority Classification

Each new item needs a priority level:

| Priority | Timeline | Criteria | Label |
|----------|----------|----------|-------|
| P0 | This session | Security risk or blocking | 🔴 P0 |
| P1 | Next 3 sessions | Significant quality improvement | 🟡 P1 |
| P2 | Within 5 sessions | Important but not urgent | 🟢 P2 |
| P3 | Future | Nice-to-have or low impact | 🔵 P3 |

**Effort estimation guide:**
| Effort | Hours | Example |
|--------|-------|---------|
| Small | 0.5-2h | Fix shell=True, fix skill metadata |
| Medium | 2-4h | Add pytest-cov, run autoflake pass |
| Large | 4-8h | Fix remaining mypy errors, set up CI |
| X-Large | 8-16h | Extract CORE package, full dedup pass |

---

## Multiple-Document Consistency Rules

**Rule 1: ONE primary, ALL others marked as superseded**
- `CODEBASE_AUDIT_TODO.md` = primary
- `PRODUCTION_TODO.md` = ✅ ARCHIVED July 6, 2026 — file deleted, references migrated
- `REWRITE_TODO.md` = add header: "LEGACY — do not update"
- `PHASE_6_TODO.md` = add header: "LEGACY — incorporated into CODEBASE_AUDIT_TODO.md"

**Rule 2: When updating the primary, check ALL secondaries for stale info**
- Before adding new items: grep the secondaries for overlapping content
- After adding: update the State Snapshot header to mention which docs were checked

**Rule 3: Archive strategy**
```
When a TODO document is definitively superseded:
1. Add header: "SUPERSEDED as of {Date} — see {Primary Doc}"
2. Keep in place for 2-3 sessions (backwards reference)
3. Move to archive/ directory with summary of what it contained
```

**Rule 4: Phase labels must stay consistent**
```
If CODEBASE_AUDIT_TODO.md says "Phase 23+", all secondary docs should use
the same phase numbering. Mismatched phase labels cause confusion about
which items are current vs completed.
```

---

## Recommended Archive Layout

```
docs/archive/
├── PRODUCTION_TODO.md          # Superseded June 4, 2026
├── REWRITE_TODO.md             # Superseded June 4, 2026
├── PHASE_6_TODO.md             # Superseded June 4, 2026
├── TODO_FULL_PRODUCTION_WIRING.md  # Superseded earlier
└── ARCHIVE_MANIFEST.md         # Summary: what each contained + where current lives
```

---

## Companion Skills

- `azazael-architecture-review` — Run this FIRST to generate findings, then use `azazael-todo-management` to integrate them
- `azazael-production` — Production readiness roadmap and gap analysis
- `azazael-sop` — Pre-session checklist, post-session cleanup
- `azazael-testing` — Validation commands and pre-commit checks

## Related Lessons

- Lesson #42 — TODO Document Versioning: Cross-Reference New Items Against Existing Plan Steps
- Lesson #44 — Comprehensive TODO Update: 4 TODO Documents Must Stay Consistent
- Lesson #24 — Always read existing docs before writing new ones (foundational discipline)
