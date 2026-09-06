---
name: corpus-reference-integrity
description: Sweep documentation corpora for references to skills/files that do not
  exist (phantom refs), classify false positives, and resolve confirmed phantoms —
  either create the referenced skill (make them real) or fix the doc with a dated
  correction. Harness sweep_corpus_refs.py; applied to the BCC investigation corpus
  2026-09-02 (6 phantom skills found + made real).
metadata:
  category: process
  projects: azazael, bcc-investigation
  priority: high
  audit_date: 2026-09-02
  auto_load: false
---

# Corpus Reference Integrity — Phantom-Reference Sweep

## Why

Docs accumulate backticked references (`bcc-ddap-portal-enumeration`,
`foo/bar.py`) that no longer — or never — correspond to real files. Each phantom
cite is a broken promise: a future reader will look for the skill/file and find
nothing.2026-09-02 the BCC investigation corpus (63 docs at sweep time; corpus since reconciled to 64 — FINAL_STATUS_REPORT inventory verified 2026-09-03) was swept and found **6 phantom skill names, all in README.md's "Reusable Skills" section** — each
described as loadable but existing nowhere (0 files, 0 catalog mentions).

## The harness

`sweep_corpus_refs.py` at project root:

- Scans all corpus docs for backticked tokens in known reference shapes —
  skill-like names (`bcc-*`, `azazael-*`, `investigation-*`, hyphenated
  identifiers) and file paths (`*.py`, `*.sh`, `*.json` basenames).
- Checks each against the real trees: user-root, `azazael/.agents/skills/`,
  project files, G: canonical skill dirs.
- Reports hits by doc so each is classified individually.

## Classification discipline

Not every hit is a phantom:

| Class | Example | Verdict |
|---|---|---|
| True phantom | skill name cited as loadable, 0 files + 0 catalog | FIX (create or correct) |
| CLI flag / inline example | `--file X.html` | False positive — regex tokenization |
| Real file, mis-bucketed | `bcc_pp2.html`, `kali_bcc_osint.sh` at root | False positive — add to real-file set |
| Doc typo of a real file | `build_html.py` vs real `rebuild_html.py` | Fix the doc (dated correction) |
| Different namespace by design | G: `bcc-*` family vs registered `investigation-*` | Note in INDEX.md / catalog, no change |

Verify phantoms with an existence PROOF (0 files + 0 catalog mentions) BEFORE
writing any correction — never assume from a search miss.

## Resolving: "make the skills real" (user directive 2026-09-02)

When the referenced skill SHOULD exist and the techniques are real (they were,
scattered through the corpus), create it — in the session's two-location pattern:

1. **Case-scoped original** in the doc's owning namespace (G:
   `BCC_Investigation/skills/<name>/SKILL.md`, dir-form, no frontmatter) —
   encodes the REAL verified technique sourced from the corpus docs.
2. **Generalized version** in `azazael/.agents/skills/<generalized-name>.md`
   (flat, YAML frontmatter, registered in SKILLS_CATALOG) — the reusable
   methodology, not the case.
3. Update the owning INDEX (4 → 10 skills) + catalog (register + inventory bump
   + EXCLUDED-BY-DESIGN note for the case-scoped family) + rewrite the phantom
   table in the source doc to reference the now-real skills.
4. Propagate (catalog 6/6, skills 5/5 hash-identical) + RE-SWEEP to 0 true
   phantoms.

When the referenced skill has no real content behind it, instead: dated
correction in the citing doc (same fix-in-place pattern as skill-claim fixes) —
state what's actually available and point to the real replacement.

## Re-check after any edit

Re-run the sweep expected-zero for true phantoms, and run the structural HTML
audit on any edited .html docs (edit-side effects must be regression-free).