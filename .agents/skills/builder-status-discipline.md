---
name: builder-status-discipline
description: Track which generator script owns which artifact in repos with
  multiple builders — document a builder-status map (canonical / legacy-clean /
  non-writing-stub), edit only canonical producers, and never fix a generated
  artifact without fixing its generator. Proven on AOA + CODEX 2026-09-02.
metadata:
  category: process
  projects: azazael, aoa, codex
  priority: medium
  audit_date: 2026-09-02
  auto_load: false
---

# Builder Status Discipline — Know Which Script Owns the Output

## Problem

Repos accumulate multiple generator scripts for the same artifact (a canonical
`build.py`, older variants, half-finished stubs). Editors guess, edit the wrong
one, or fix a GENERATED file while its generator reproduces the bug on the next
run. Both happened on 2026-09-02.

## The builder-status map

For any artifact with more than one plausible producer, maintain a table:

| Artifact | Canonical producer | Status | Notes |
|---|---|---|---|
| `AOA_STRUCTURE.html` | `build.py` | ✅ CANONICAL | registry-driven; regenerate, don't hand-edit |
| `AOA_DISCLOSURE.html` | `build_disclosure.py` | ✅ CANONICAL | registry-driven |
| `AOA_STRUCTURE.html` (legacy) | `gen_html.py` | ✅ CLEAN, legacy | older flat variant; correct writer, pre-registry content |
| — | `build_final.py` | ⚠️ NON-WRITING STUB | builds content, never writes back; dead |

Statuses: **CANONICAL** (the producer that ships), **CLEAN legacy** (correct but
superseded — don't run it for new builds), **NON-WRITING STUB** (dead — don't
use), **HISTORICAL** (archived/older-generation copies — never edit, only
regenerate or read).

## The two rules

1. **Edit the canonical producer, never the artifact directly.** A built .html
   is a build artifact; hand-edits get overwritten and lost on the next run.
2. **When you fix a generated artifact, fix its generator FIRST.** If a defect
   (JS SyntaxError, broken string, wrong data) appears in generated output,
   trace it to the producing script — the .html is a symptom, the generator is
   the disease. Otherwise the next regeneration silently reintroduces the bug.

## Verification after ANY builder edit

1. `python -m py_compile <builder>` — the generator itself parses.
2. Grep the builder for the defect pattern (e.g. `'\\n'` double-escaped join,
   multi-line single-quoted strings).
3. Run the builder → inspect output (real newlines, no literal `\n`).
4. Render-check the REGENERATED artifact (`html-render-verification`) → 0 errors.
5. Update the builder-status map if the picture changed.

## Historical copies

Per the G: historical-record directive, old copies (Documents, archived/,
older-generation mirrors) are a historical record — never edit them; they are
byte-faithful generations and the canonical regeneration path is the only
legitimate writer.

## See also

- `aoa-html-builder` (#1226) — the canonical producer-status map (build.py /
  build_disclosure.py editable; gen_html.py legacy-clean; build_final.py a
  non-writing stub) proving this pattern in-repo
- `azazael-codex-video` — the CODEX producer-status extension
  (`create_dual_pane_video.py` canonical producer of Azazael_DUAL_PANE.html)
- `pre-action-gate-lite` (#1253) — fix-then-reverify after any producer edit