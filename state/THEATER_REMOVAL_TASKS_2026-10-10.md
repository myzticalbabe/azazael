# THEATER-REMOVAL EXECUTION LEDGER — 2026-10-10

Order: "remove all theater for production execution". Every task below was either
EXECUTED this session (with verification) or is recorded VERIFY-FIRST / DEFERRED
with its reason. Unverified proposals from worker drafts (e.g. `src/CORE/cascade.py`,
`neural_loop.py`, `redteam.py`, dep-gap faiss/hdbscan tracks) are NOT presented as
fact — see §5. Production interpreter for all probes: `C:/Azazael/.venvs/py315t`.

## A. ARCHIVED (moved to `archive/theater-2026-10-10/`, reversible)

| # | Item | Why theater | Verification |
|---|---|---|---|
| A-1..A-10 | `tools/exercise_*.py` (10 files) | exit-0-only; zero importers repo-wide (subprocess/literal refs only) | post-move grep = 0 outside archive |
| A-11 | `tools/run_technique_exercises.py` | orphan runner (no chain job, dead aggregate JSON) | same |
| A-12 | `state/technique_exercises.json` | generated artifact, zero readers | moved iff present |
| A-13 | repo-root `METACLUSTER.py` (1153L orphan) | zero importers; all live imports use `CORE.WORMS.METACLUSTER` | same |
| A-14 | `azazael/azazael/state/ACTION_REGISTRY_2026-10-10.md` | MISFILED by author (double-nested path) → relocated to `azazael/state/` | Test-Path both sides |

`tools/` directory itself KEPT (other modules import `tools.*`; only the 11 files moved).

PRE_GATE_BACKUP HOLD (2026-10-10): the 11 stale `src/CORE/*.pre_gate_backup`
files (+ `postgres_memory.py.pre_gate_backup`) were NOT moved — grep shows the
rollback mechanism (`sentinel_enforcer.rollback`, `gate_*.py`, `pre_action_gate`)
actively reads/writes that suffix, and validators explicitly ignore the prefix.
Stale ones are clutter, but moving them risks confusing the rollback path for
zero production gain. Revisit only with the rollback owner present.

## B. DELETED FUNCTIONS (tracked files — recoverable via git)

| # | Symbol | File | Evidence of deadness |
|---|---|---|---|
| B-1 | `replan_after_failures` + `__all__` entry | `src/CORE/circuit_breaker.py:24,623` | self-doc admits no caller; 2 repo-wide hits (def + `__all__`) |
| B-2 | `recall_with_feedback` + `__all__` entry | `src/CORE/technique_runtime.py:53,310` | zero `src/` callers; only presence-probed by archived A-8 |
| B-3 | `discover_wirings` + `__all__` entry | `src/CORE/technique_runtime.py:54,147` | zero callers repo-wide (`status()` covers the need) |
| B-4 | `run_read_driven_consolidation` (610) + `consolidate_from_reads` (710) + `_record_read_stats` (733) | `src/CORE/WORMS/expansion/engram.py` | zero callers; live path uses `.consolidate`, not `_from_reads` |
| B-5 | `enforce_replace` (402) | `src/CORE/sentinel_enforcer.py` | zero call sites (twin `enforce_write` untouched) |
| B-6 | `post_validate` (435) | `src/CORE/sentinel_enforcer.py` | zero callers (`rollback` kept — still used by `self_test`) |

KEPT WITH REASON (flagged, not deleted): `DreamConsolidatorWorm.read_pressure`
(public method on a registered worm; needs P10 consumer — now def-only after B-4),
`technique_runtime.run_all`/`status`/`load_slices` (registry machinery the T-15
instrument and forensics use), blind-loop instruments (`evolution_progress`,
`fitness_arm_liveness` — needed by L-2 loop revival; deleting them would re-create
the work), `technique_wiring/` adapters (T-13 absorption moves them; deleting now
would destroy the rescore worklist).

## C. RELABELED (claims fixed, behavior untouched)

| # | File:line | Was | Now |
|---|---|---|---|
| C-1 | `technique_runtime.py:2` | "the production call path" | exercise registry + fail-open boundary helpers |
| C-2 | `technique_runtime.py:230-234` | "four entry points real code should call" | two (after B-2/B-3) |
| C-3 | `sentinel_enforcer.py:1-21` header | "cannot be skipped, bypassed… Every edit flows through" | opt-in gate + in-process `open()` tripwire; bypass paths named |
| C-4 | `compliance/orchestrator.py:40-44` | "All unauthorized writes will raise" | advisory aggregator; import side-effect described honestly |
| C-5..C-7 | (prior session, verified clean) CAPABILITIES §9, outlier-diagnosis :33, review :213 | 5→4, 5→4, EP113 zero→2 | grep confirms zero stale strings |

Wiring `// production call site` shim comments (`_l1_memory.py` et al) LEFT for T-13
(the absorption diff deletes/moves them anyway; separate churn now = noise).

## D. POST-REMOVAL VERIFICATION (executed 2026-10-10 — all pass)

- [x] venv import probes PASS: `CORE.circuit_breaker`, `CORE.technique_runtime`,
  `CORE.WORMS.expansion.engram`, `CORE.sentinel_enforcer`,
  `CORE.compliance.orchestrator` (5/5 under py315t)
- [x] `load_slices()` still 9/9 ok, 181 wired (registry untouched by deletions)
- [x] repo-wide grep for removed names = 0 in `src/`+`tools/` (only distinct
  `sentinel_gate.post_validate_mode` remains, verified different function;
  doc mentions in registry/ledger/diagnosis are historical record, not refs)
- [x] `git diff --stat` reviewed (41 files, +878/−2230 incl. pre-existing dirt),
  NO commit (not requested)

## E. REMAINING THEATER (not removed — needs a decision or a loop)

- Blind instruments stay until L-2 fires them (E-1); `technique-wiring` citations stay
  until T-15 names their consumer (E-2); `ModelVersioner` "models" wording stays until
  H-4 lands (E-3); dashboard snapshots stay until render-job ownership is proven (E-4).
- Subsystem wire-or-cut (HYDRA, META-4, CODEX generator, gateways, AOA-outward, HORUS,
  sidecar) is DECISION work, not deletion work — in ACTION_REGISTRY §4.

## F. VERIFY-FIRST (worker-proposed, NOT verified this session — do not execute blind)

- `src/CORE/cascade.py`, `neural_loop.py`, `redteam.py` paths; dep-gap faiss/hdbscan/
  igraph/rustworkx tracks; `~/.audit` and `~/.engram` absolute paths in task text;
  T-08 `src/SCRIPTS/sentinel_gate.py` identity (confirmed exists; role unverified).
  Verify existence + role before writing tasks against them.

---

## Reach audit 2026-10-10 (post-SOTA-wave)

Re-checked this ledger against the tree AFTER the 2026-10-10 SOTA absorption wave, by
content search for every symbol named in §A and §B, then reading each hit. No code file
edited. This pass had no terminal, so nothing below is a test run.

**Counts: 33 ledger items (§A 14 archived / §B 6 deleted / §C 7 relabelled / §E 4
remaining / §F 6 verify-first) → 3 CUTs REVERSED AND PRESENT AGAIN / 3 CUTs HOLD /
§A holds and is uncommitted / 1 §D verification result INVALIDATED.
The cleanup is worth keeping — do not re-run the §B pass thinking it was never done.**

### 1. §B deletions that are PRESENT AGAIN in the tree (3 of 6)

| # | symbol | claimed | found now |
|---|---|---|---|
| B-2 | `recall_with_feedback` | deleted (zero `src/` callers) | **PRESENT** `src/CORE/technique_runtime.py:362`, and now genuinely wired: it resolves `engram.run_read_driven_consolidation` at `:403` |
| B-4 | `run_read_driven_consolidation` (778) + `consolidate_from_reads` (711) + `_record_read_stats` (738) | deleted (zero callers) | **ALL THREE PRESENT** `src/CORE/WORMS/expansion/engram.py`; `_record_read_stats` is now CALLED at `:517` and `:734`, so it is no longer def-only |
| B-6 | `post_validate` | deleted (zero callers) | **PRESENT, re-implemented** `src/CORE/sentinel_enforcer.py:422`, called from the write path at `:494`, with its own `_post_validate_failures` counter (`:165`, surfaced in `get_status` at `:616`) |

B-4 and B-6 are the D-2 / EP125 work of this session landing on exactly the symbols §B
had cut — and both are now reachable rather than dead, which is the outcome the
registry's `"remove OR wire"` wording allows. B-2 is the same shape. The distinction
that matters for whoever reads this next: these are **wired re-additions, not stale
residue**, so do not "re-delete" them without re-measuring their callers first.

### 2. §B deletions that HOLD (3 of 6)

- B-1 `replan_after_failures` — zero matches repo-wide. Holds.
- B-3 `discover_wirings` — zero matches repo-wide. Holds.
- B-5 `enforce_replace` — zero matches in `sentinel_enforcer.py` or anywhere else.
  Holds. (Note `sentinel_enforcer.py:419` documents that the sibling
  `SCRIPTS.sentinel_gate.post_validate_mode` at `:1264` is a DIFFERENT function — that
  separation is real and was re-confirmed.)

### 3. §A / §C / §D disposition

- §A's archive holds: `archive/theater-2026-10-10/` exists on disk (untracked). The 11
  exercise/runner files and the orphan `METACLUSTER.py` are out of the live path.
- **§D's verification item `[x] repo-wide grep for removed names = 0` is no longer a
  true statement about the tree** — see §1 above. It was true when measured; the SOTA
  wave then re-introduced three of the six. Re-measure before citing it.
- §D's remaining items stand unrefuted: the 5 venv import probes, `load_slices()` 9/9
  with 181 wired, and the review that no commit was made. **The whole §A/§B cleanup
  is still UNCOMMITTED**, which is why a later session could re-add a cut symbol without
  ever seeing a conflict.

### 4. §E / §F re-scored

- §E-2 (`technique-wiring` citations stay until T-15 names their consumer) — HALF CLOSED
  this wave: the `read_pressure` citation now has a real reader at
  `src/CORE/technique_runtime.py:483`, so that one no longer needs T-15.
- §E-1 (blind instruments stay until L-2 fires them) — still open; `tools/evolution_progress.py`
  and `tools/fitness_arm_liveness.py` are still the live-but-blind instruments.
- §F's first item (`cascade.py`, `neural_loop.py`, `redteam.py` are unverified
  worker-proposed paths) is now SUPERSEDED: all three were opened and edited by workers
  in the SOTA wave, each with a dedicated test file. Treat them as verified paths — but
  note §E-4's caution still applies to them (cascade's own `select_mode` half already
  existed and was already pinned by `tests/test_cascade_mode_select.py`, so one worker
  deleted a duplicate test it had written rather than add second coverage).
- §F's remaining items (dep-gap faiss/hdbscan/igraph/rustworkx tracks, `~/.audit` and
  `~/.engram` absolute paths, T-08 `src/SCRIPTS/sentinel_gate.py` role) are UNTOUCHED by
  this wave and stay VERIFY-FIRST.

### 5. Invalidated evidence

- `sentinel_enforcer.post_validate:435` (ACTION_REGISTRY D-1) and `enforce_replace:402`
  (§B-5/§B-6 here) cite lines that no longer hold those symbols: `post_validate` is at
  `:422` as a fresh implementation whose guards start at `:431`, and `enforce_replace`
  does not exist. Both citations should be corrected to symbols, not line numbers.
- §D's zero-grep verification, as described in §3 above.
