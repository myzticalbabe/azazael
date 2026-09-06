---
name: pre-action-gate-lite
description: Minimum verify-before-declaring-done discipline — after fixing any
  defect, RE-VERIFY the fix actually works (render/compile/test the fixed
  artifact, not the pre-fix state), then scan for siblings of the defect class
  across the corpus before closing. Proven 2026-09-02 (AOA literal-\n + CODEX
  multi-line-string fixes).
metadata:
  category: process
  projects: azazael, aoa, codex
  priority: high
  audit_date: 2026-09-02
  auto_load: false
---

# Pre-Action Gate — Lite (Verify-Before-Done)

The heavy version lives in the Azazael compliance stack; this is the lite gate:
three minimum checks before declaring ANY defect fixed.

## Gate 0 — GUI-automation trigger (routing)

If the next action is SYNTHETIC GUI INPUT on a live window (pyautogui clicks /
typewrite / hotkeys — not headless scripts, not file edits), this gate does not
cover it: load **`desktop-automation-safety`** and pass its GUI-AUTOMATION GATE
first — especially the content-verified-focus rule. Reason: file-edit gates
cannot see keystrokes, and one lost-focus event sent input into a
Facebook/Messenger window (2026-09-04). Prefer the headless/deterministic path
the safety skill recommends whenever the engine result is what matters.

> **Action-class routing map:** this lite gate owns the verify-before-done
> discipline for FILE EDITS (Gates 1–3) and ROUTES the three action classes the
> file-edit gates cannot see — **Gate 0** synthetic GUI input →
> `desktop-automation-safety`; **Gate 0b** live web collection / network pulls
> → `investigation-osint` (DATA-COLLECTION GATE); **Gate 0c** batch / long
> background runs → `background-sweep-resilience` (LONG-RUN GATE). Print the
> routed skill's assertion before the action; file edits keep using Gates 1–3.
> **Classes already covered WITHOUT a new gate (Sep-4(65) audit):**
> - **External sends / filings** (emails, complaints, RTK/FOIA, records requests)
>   → user-executed ONLY — absolute rule, never an agent action. Route: the
>   corpus send matrix (COMPLAINT_TODO_LIST / DOS_BCO10 / PACOURTS_CP
>   RECORDS_REQUEST / SAMHSA_CCBHC_FOIA) with every item DRAFT/UNSENT until the
>   user executes. "BCC excluded from all recipient lists" is part of this rule.
> - **Tool / package installs** (pip / winget / apt / go install) →
>   `azazael-environment` (3.14t-only install discipline) + `azazael-error-resolution`
>   Step 4 (cp314t wheel selection; force-reinstall on segfault).
> - **Agent spawns** (`spawn_agents`) → inside the permanent gate's RULE 0I / 0W / 0Z
>   checks — no separate lite-gate route needed.

## Gate 0b — Live web collection trigger (routing)

If the next action is LIVE NETWORK DATA COLLECTION against third-party
systems (web scraping / curl-API fetches / headed-browser CDP pulls / bulk
export sweeps — not one-off `read_url`/`web_search`), this gate does not
cover it: load **`investigation-osint`** and pass its **DATA-COLLECTION GATE**
first — especially the 404-≠-blocked-≠-absent rule and the no-second-pull-at-
the-same-wall rule. Reason: file-edit gates cannot see what a fetch hits or
how many times it loops, and unproven pulls wasted hours on 2026-09-04
(portal CAPTCHA walls, 404 deep-link confusion, headless-session artifacts).
Prefer the official-export / records-request path when public channels are
exhausted.

## Gate 0c — Batch / long-run trigger (routing)

If the next action is a BATCH or LONG BACKGROUND RUN (expected runtime
approaching the command timeout: sweeps, refreshes, graph regenerations,
fetcher batches, model pilots — anything launched with `&` or est. > ~2 min),
load **`background-sweep-resilience`** and pass its **LONG-RUN GATE** first:
size the run from a pilot, choose background + log over a foreground hold,
per-unit try/except isolation, resume-from-crash-point. Reason: file-edit
gates cannot see a run's duration or silent mid-sweep death; the 2,754-file
crash-at-2,598 and the 10-hour no-result runs are the precedent.

## Gate 1 — Fix, then PROVE the fix

Run the artifact through its REAL verification (render harness / tests /
compile) AFTER the fix and show the PASS. Proof = the fixed artifact passes the
check that caught it. Statement "it should work now" is not proof; a green run
is. 2026-09-02: both real defects (literal-`\n` join in build.py → SyntaxError;
multi-line single-quoted alert in Azazael_DUAL_PANE.html → SyntaxError) were only
declared fixed after the regenerated/rebuilt output passed the CDP render check
with 0 console errors / 0 exceptions.

## Gate 2 — Fix the generator, not just the artifact

If the artifact is generated, the fix must go into the generator too (see
`builder-status-discipline`). A fix to the .html alone is undone on the next
rebuild. Verify by REGENERATING and re-rendering.

## Gate 3 — Sibling scan before closure

Before marking the defect class closed, scan the whole corpus for OTHER instances
of the same signature (e.g. literal `\n` in a single-line HTML, or
single-quoted strings containing real newlines across all generator scripts). A
defect found in isolation is rarely alone; the scan converts "I fixed one" into
"I fixed the class" (or honestly reports the remaining instances). 2026-09-02:
static signature scan of all 2,754 project HTML files = 0 literal-`\n` siblings,
and the old-builder sweep proved gen_html/build_final clean of the join trap.

## Minimal checklist

- [ ] Fixed artifact passes the SAME check that caught the defect
- [ ] Generator (if any) fixed and regeneration re-verified
- [ ] Sibling scan across the corpus shows ZERO (or documented remainder) of the
      defect class
- [ ] Fix + verification recorded (milestone/skill) with dates + hashes

## See also

- `desktop-automation-safety` — Gate 0 routes GUI-automation actions to this skill's assertions.
- `html-render-verification` — the render gate used for the proofs above.
- `corpus-reference-integrity` — the sweep-shaped cousin (same verify-the-class idea).
- `aoa-html-builder` (#1226) — the builders whose outputs this gate verifies.
- `builder-status-discipline` (#1252) — which producer to fix when the gate fails.