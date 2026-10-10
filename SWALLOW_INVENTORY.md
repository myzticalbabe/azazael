# Swallow inventory — everything that discards an exception without recording it

> **SUPERSEDED (2026-10-10).** The counts below are a **2026-10-09 point-in-time
> snapshot taken before** commit `30836145` (*"Record every swallowed failure
> tree-wide: 2152 sites across 431 files"*, 2026-10-09 18:38) swept the tree. That
> sweep converted the shapes this document counted. Re-running the same tool on
> today's tree reports **3 rows, not 2,994** — so the numbers in §"The inventory"
> are history, not a backlog, and must not be re-cited as outstanding work.
>
> This is the *confidently-incomplete artifact* class: a generated census that
> keeps answering for a tree it no longer describes. Its line numbers silently
> drifted onto unrelated code (e.g. rows recorded as `spine.py:80` landed on a
> `return` inside a `try`, while the handler they named was already recording via
> `note_failure`). Any plan item quoting these counts must be re-measured first.
>
> **Measured residue, 2026-10-10** (`python tools/swallow_inventory.py --json SWALLOW_INVENTORY.json`),
> 3 rows in 3 files — all three **by design**, none a remediation target:
>
> | file:line | shape | why it stays |
> |---|---|---|
> | `src/CORE/failure_ledger.py:43` | `unlogged_handler` | The recorder *itself*. Its `except Exception: _LOST_NOTES[0] += 1` counts the loss; that is the terminal sink, and `tools/fix_swallows.py` is fixture-guarded never to convert inside a recorder. |
> | `src/CORE/inference/sequential_analyzer.py:47` | `unlogged_handler` | `try: from CORE.cascade import CascadeRouter / except ImportError: CascadeRouter = None` — an optional-dependency guard. Its failure is a missing module, surfaced by the `None`, not an error to record. |
> | `src/CORE/local_memory.py:66` | `unlogged_handler` | Same shape, for `CORE.verification_gate.epistemic_state` (added 2026-10-10 with the EP370 relocation). |
>
> The 23 remaining `src/`-wide remediation sites found on 2026-10-10 were repaired
> in the fan-out recorded below (26 → 3).

Date of the snapshot below: 2026-10-09. Tool: `tools/swallow_inventory.py` (AST,
stdlib only). Raw rows: `SWALLOW_INVENTORY.json` (regenerated 2026-10-10; the
2026-10-09 raw rows are preserved verbatim as
`SWALLOW_INVENTORY_2026-10-09_pre_refactor.json`).

---

## 2026-10-10 remediation pass (this is what closed it)

Eight parallel workers, disjoint file ownership, one shared repair shape: add the
module's existing `note_failure(where, exc)` recording call inside the handler body
and change nothing else — the fail-open path stays behaviourally identical
(`silent_continue` still continues, every return keeps its value).

| module | rows repaired |
|---|---|
| `src/CORE/audit_trail.py` | 856, 870, 918 (chain parse loop), 926 |
| `src/CORE/technique_runtime.py` | 60, 65, 382 (the failure-ledger import was hoisted above the guarded imports it is used by — otherwise `note_failure` would have raised `NameError` from inside its own handler) |
| `src/CORE/local_memory.py` | 2200, 2214, 2973 |
| `src/CORE/compliance/policy.py` | 325 |
| `src/CORE/reward_scales.py` | 210 |
| `src/CORE/training_intake.py` | 86, 97 |
| `src/META/DebugZ.py` | 117 |
| `src/META/DistillZ.py` | 110 |
| `src/UTILITIES/TERENCE/TERENCE.py` | 883, 921 (two `contextlib.suppress` sites converted to recording `try/except` with identical control flow) |
| `src/CORE/WORMS/expansion/learning_grpo.py` | 803 |
| `src/CORE/WORMS/expansion/learning_pipeline.py` | 713 |
| `src/CORE/WORMS/expansion/learning_replay.py` | 214 |
| `src/CORE/WORMS/expansion/learning_versioner.py` | 253 |
| `src/CORE/WORMS/expansion/queens.py` | 835 |
| `src/CORE/WORMS/expansion/reflexion.py` | 144 |

Verified centrally, not by the workers: `python tools/swallow_inventory.py --json`
re-run on the edited tree reports **3** rows (the by-design three above), and the
anti-pattern ratchet stays green.

---

## What was already counted, and what was invisible *(2026-10-09 — history)*

`src/CORE/compliance/scanner.py` flags exactly two shapes, and only when the
handler body is a **single** statement:

| shape | scanner sees it? |
|---|---|
| `except ...: pass` | yes (`silent_except_pass`) |
| `except ...: return None / <const>` | yes (`except_return_default`) |

Everything else discards the error just as completely and no counter reports it.

## The inventory *(src/, 452 files — 2026-10-09 snapshot, superseded)*

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

So the headline **at that time**: 1,075 of these were known; 2,561 certainly
discarded an exception without recording it; 433 more needed review. All but three
were resolved the same day by `30836145` and the modules listed in the worked
example below; the 2026-10-10 pass closed the rest.

## Why the 2026-10-09 numbers were trustworthy for *that tree* (and where they were not)

- **Oracle.** `--self-test` builds a fixture with one of every shape above *plus*
  handlers that legitimately act (one `log.error(...)` + `raise`, one
  `note_failure(...)`). It must report exactly the silent set and exclude the
  acting ones. It passes: 8/8 silent shapes found, both acting handlers excluded.
  A fixture I wrote myself only validates my assumption, which is why:
- **Cross-validation against the producer.** The detector implements the scanner's
  two rules independently and reported `silent_pass 800` / `return_default 275`,
  which was **exactly** the project scanner's own count for the same tree
  (`tools/anti_pattern_gate.py --check` at the time: "silent_except_pass 800",
  "except_return_default 275"). Two instruments, same numbers.
- **Limits.** `unlogged_handler` is deliberately inclusive: the matcher treats a
  handler as acting only if it sees a call whose name reads as a recorder, so a
  handler that stashes the error in an attribute and moves on is still counted
  (correctly — that is not observable), but 433 rows mention *some* record-ish
  token and must be read individually. Only `src/` was scanned (not `tools/`,
  `scripts/`, the Kali tree). `except X: return <non-constant expression>` is not
  classified. Blanket-fixing these would be wrong: this repo fails open at
  boundaries **on purpose**, so the defect is the missing *record*, not the
  swallow.
- **The limit that actually bit:** the snapshot carried **line numbers but no tree
  identity**. When the tree moved 15 hours later, the file survived and the line
  numbers did not, and nothing in the artifact said so. Regenerate, never re-cite.

## Worst offenders *(2026-10-09 — superseded)*

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

`src/CORE/worm_registry.py` was the sharpest single finding: **30 of its 42** were
`marker_hidden` — the module that discovers every worm hid its swallow sites from
the counter with `# scanner:ignore`. (Re-measured 2026-10-10: 0 rows.)

## The worked example (applied 2026-10-09, extended 2026-10-10)

Ten modules were converted on 2026-10-09 to the record-instead-of-swallow
pattern — `dispatch_plan`, `circuit_breaker`, `METACLUSTER`, `engram`,
`latent_align`, `latent_refine`, `rubric_evolution`, `skill_library`,
`structured_action`, `verification_gate` (then `local_memory`, `direct_memory`) —
via a module-level guarded import of `CORE.technique_runtime.note_failure` plus a
`_note_failure(where, exc)` wrapper. `failure_notes()` is the read side: a
non-empty ledger means something degraded. `direct_memory.py` deliberately keeps a
**local-only** tally because its contract is stdlib-only with zero CORE imports.

Remediation shape, for the record: same pattern, per module, with a per-module
verification — not a blanket sweep, because each handler has to be read to decide
whether the failure is *expected* (a probe that trips a breaker on purpose) or
*degradation* (a ledger write that silently did not happen).
