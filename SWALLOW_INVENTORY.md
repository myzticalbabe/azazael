# Swallow inventory — everything that discards an exception without recording it

Date: 2026-10-09. Tool: `tools/swallow_inventory.py` (AST, stdlib only).
Raw rows: `SWALLOW_INVENTORY.json`. Repro: `python tools/swallow_inventory.py --json SWALLOW_INVENTORY.json`

## What was already counted, and what was invisible

`src/CORE/compliance/scanner.py` flags exactly two shapes, and only when the
handler body is a **single** statement:

| shape | scanner sees it? |
|---|---|
| `except ...: pass` | yes (`silent_except_pass`) |
| `except ...: return None / <const>` | yes (`except_return_default`) |

Everything else discards the error just as completely and no counter reports it.

## The inventory (src/, 452 files)

| shape | count | visible to the scanner | what it hides |
|---|---|---|---|
| `silent_pass` | **800** | yes | single `pass` body |
| `return_default` | **275** | yes | single `return None`/constant body |
| `unlogged_handler` | **1641** | **no** | multi-statement body that never raises, logs, audits or records — `x = None; continue`, `handle(); pass`, … (1,208 of these are *provably* silent: no recorder-ish call anywhere in the body) |
| `silent_continue` | **153** | **no** | the loop skips the failure and carries on |
| `marker_hidden` | **59** | **no — hidden on purpose** | a silent swallow carrying `# scanner:ignore`, i.e. suppressed from the count by the scanner's own marker (107 markers exist repo-wide; 59 sit on a silent swallow) |
| `empty_literal_return` | **51** | **no** | single `return []` / `{}` / `()` — success-shaped default, and not an `ast.Constant`, so the scanner's rule misses it |
| `silent_break` | **12** | **no** | the loop abandons early |
| `suppress_context` | **2** | **no** | `contextlib.suppress(...)` — no handler at all |
| `base_exception` | **1** | **no** | explicit `except BaseException` |
| **total rows** | **2994** | | |
| **certified-silent floor** | **2561** | 1075 | the 1,919 the scanner cannot see, minus 433 `unlogged_handler` rows whose body mentions something record-ish and therefore need a human look |

So the honest headline: **1,075 of these were known; 2,561 certainly discard an
exception without recording it; 433 more need review.**

## Why this number is trustworthy (and where it is not)

- **Oracle.** `--self-test` builds a fixture with one of every shape above *plus*
  handlers that legitimately act (one `log.error(...)` + `raise`, one
  `note_failure(...)`). It must report exactly the silent set and exclude the
  acting ones. It passes: 8/8 silent shapes found, both acting handlers excluded.
  A fixture I wrote myself only validates my assumption, which is why:
- **Cross-validation against the producer.** My detector implements the scanner's
  two rules independently and reports `silent_pass 800` / `return_default 275`,
  which is **exactly** the project scanner's own count for the same tree
  (`tools/anti_pattern_gate.py --check`: "silent_except_pass 800",
  "except_return_default 275"). Two instruments, same numbers → the shapes the
  scanner cannot see are measured by a rule set that is known to agree with it.
- **Limits.** `unlogged_handler` is deliberately inclusive: the matcher treats a
  handler as acting only if it sees a call whose name reads as a recorder, so a
  handler that stashes the error in an attribute and moves on is still counted
  (correctly — that is not observable), but 433 rows mention *some* record-ish
  token and must be read individually. Only `src/` was scanned (not `tools/`,
  `scripts/`, the Kali tree). `except X: return <non-constant expression>` is not
  classified. Blanket-fixing these would be wrong: this repo fails open at
  boundaries **on purpose**, so the defect is the missing *record*, not the
  swallow.

## Worst offenders (all shapes)

| file | rows | mix |
|---|---|---|
| `src/CORE/WORMS/expansion/spine.py` | 140 | unlogged 103, pass 15, continue 9 |
| `src/CORE/spine_registry.py` | 88 | pass 34, unlogged 31, return_default 17 |
| `src/CORE/WORMS/NETWORK_DIAG.py` | 51 | pass 29, unlogged 20 |
| `src/CORE/direct_memory.py` | 43 | pass 18, unlogged 12, default 6 |
| `src/CORE/worm_registry.py` | 42 | **marker_hidden 30**, unlogged 11 |
| `src/CORE/WORMS/CLUSTERWORMS.py` | 41 | unlogged 27, pass 13 |
| `src/CORE/data_retention.py` | 40 | unlogged 26, pass 6, continue 5 |
| `src/CORE/inference/providers.py` | 36 | unlogged 21, pass 8, default 4 |
| `src/CORE/local_memory.py` | 29 | pass 18, unlogged 9 |

`src/CORE/worm_registry.py` is the sharpest single finding: **30 of its 42** are
`marker_hidden` — the module that discovers every worm hides its swallow sites
from the counter with `# scanner:ignore`.

## The worked example (already applied)

Ten modules were converted on 2026-10-09 to the record-instead-of-swallow
pattern — `dispatch_plan`, `circuit_breaker`, `METACLUSTER`, `engram`,
`latent_align`, `latent_refine`, `rubric_evolution`, `skill_library`,
`structured_action`, `verification_gate` (then `local_memory`,
`direct_memory`) — via a module-level guarded import of
`CORE.technique_runtime.note_failure` plus a `_note_failure(where, exc)` wrapper.
`failure_notes()` is the read side: a non-empty ledger means something degraded.
`direct_memory.py` deliberately keeps a **local-only** tally because its contract
is stdlib-only with zero CORE imports.

Remediation shape for the remaining 2,561: same pattern, per module, with a
per-module verification — not a blanket sweep, because each handler has to be
read to decide whether the failure is *expected* (a probe that trips a breaker on
purpose) or *degradation* (a ledger write that silently did not happen).
