# Invisible / orphaned work inventory

Date: 2026-10-02. Companion to `FORENSIC_ENVIRONMENTS_2026-10-02.md` and
`GENOME_SEED_SCHEMA_DIAGNOSIS_2026-10-02.md`.

After the reconciliation revealed that a whole fix (EV-4 + instruments) lived
only in the hub's uncommitted working tree, this inventories **all** the ways
work in this project is currently invisible to the tree and to the branches.

An item is *invisible* if it exists on disk but is not reachable from
`migration/baseline-20261001`; *orphaned* if it exists in a branch or store but
no working tree consumes it.

## 1. Hub working tree — uncommitted (`C:\Users\clint\azazael`, @ `1e30c2c1`)

`git status --porcelain`: **54 modified, 658 untracked, 7 deleted** — none on any
branch (`origin/master`, `origin/migration/baseline-20261001`,
`origin/r15/...` all checked).

Modified **code** files by directory (tracked files whose committed content the
working tree no longer matches):

| dir | modified |
|---|---|
| `src/` | 17 |
| `tests/` | 14 |
| `scripts/` | 10 |
| `tools/` | 1 |

Notable modified code includes `src/CORE/WORMS/expansion/proteus_hooks.py`,
`.../allocation.py`, `.../evolution.py`, `.../dreaming.py`,
`src/CORE/freethreading.py`, `src/CORE/secrets_manager.py`,
`src/ORCHESTRATION/HYDRA.py`, `src/AOA/core/{event_bus,router}.py`,
`scripts/chain_controller.py`, many `tests/test_*.py`.
The adopted EV-4 diff was one entry in this set.

Untracked code (`.py` under `src/scripts/tools/tests`): **334 files**
(`src` 137, `tools` 68, `tests` 65, `scripts` 64). Examples:
`tools/cain_*.py` (~40 CAIN figure scripts), `tools/_tmp_*.py` (scratch probes),
`scripts/gosp_*`, `scripts/rani_*`, `tools/evolution_progress.py` (adopted),
`tools/evolution_backfill.py` (adopted), `tools/fitness_arm_liveness.py`
(adopted). Untracked non-code: `state/` 98, `logs/` 79, `reports/` 20,
`dashboard/` 19, `skills/` 8, and loose root docs
(`RECOVERY_REMEDIATION_PLAN_2026-09-30.md`, `ROADMAP.md`, `RULE_FORENSICS.md`, …).

Uncommitted **deletions**: `scripts/live_monitor.py` and six
`graphify-out/<date>/GRAPH_REPORT.md` — deletions that were never committed.

## 2. Failing / incomplete uncommitted work (adopt with caution)

Not all hub working-tree edits are validated. The candidate counter-example:

- `src/CORE/WORMS/expansion/proteus_hooks.py` (uncommitted, +44) **removes
  `use_schema_features` from `MORPH_CANDIDATES`** (leaving only `by_session`),
  on the argument that halving the candidate list makes the schema constant.
  It also adds a `PROTEUS_EXPLORE` env override.
- Measured: applying it to this tree **fails 17 existing tests**
  (`tests/test_proteus_hooks.py`, `tests/test_exmachina_mutagen.py`) which the
  hub never updated for a single-candidate rotation. It was **reverted** here
  and not committed.

So the hub's uncommitted set is a mix: some entries are validated (the EV-4
unit, proven by replay + 238 green tests), some are **incomplete changes that
break their own suite**. Status must be proven per entry, not assumed from the
fact that it is sitting in the hub.

## 3. Unmerged branch commit (orphaned)

`origin/master` carries **one** commit not reachable from HEAD:

- `ef8ac9a8` "Migration complete: flat dispatch, 9/9 units, pillars converged
  (see MIGRATION_LEDGER)", 2026-10-02 15:29, **120 files, +14339/−11658** —
  deletes many `tests/test_nature_*.py` / `tests/test_metacluster*.py`, adds
  `tools/terence_invariants.py` (2612 lines) and `tests/test_mesh_transport_e2e.py`.

HEAD is **9 commits ahead** of `origin/master`. `origin/r15/wiring-gate-perf-calibration`
is fully merged (0 unique commits). So the divergence is a single branch point
with one unmerged commit on each side — a real fork that no working tree holds
in full.

## 4. WSL Ubuntu-26.04 — diverged and dirty

`/root/azazael`, `master @ 7d883ba`, **1066 dirty files**. Roughly two months
behind the hub and carrying its own uncommitted edits: *a third* body of
invisible work, with no relationship checked to the 658 hub files.

## 5. Archives

- `G:/source-of-truth/azazael`: `git rev-parse HEAD` does not resolve (unborn
  HEAD) and `git status` reports clean — consistent with the earlier D-7 note;
  the canonical archive cannot be compared by revision.
- `G:/AZAZAEL/AZAZAEL_ROOT`: unborn HEAD (D-7).
- Kali (`wsl -d kali-linux`): no `.git` by decision (D-4, see §9 of the forensic
  report) — a mirror, not a history.

## Summary of the invisibility mechanisms

| # | mechanism | scale | reachable from the branch? |
|---|---|---|---|
| 1 | hub uncommitted edits to tracked files | 54 | no |
| 2 | hub untracked files | 658 | no |
| 3 | hub uncommitted deletions | 7 | no |
| 4 | unmerged `origin/master` commit | 1 commit / 120 files | no |
| 5 | WSL Ubuntu dirty tree | 1066 | no |
| 6 | G: archives unborn HEAD | 2 | n/a |

The common shape: **the thing that would make the work visible (a commit, a
push, a merge) did not happen**, and every instrument that reads git
(`git status`, `git log`, the freshness guard) is correct and silent because it
reports on the committed graph only.

## Recommended disposition (not yet done, needs review each)

1. Hub: separate the 54 modified + 334 untracked code files into (a) validated
   work worth committing and (b) scratch/WIP/product-specific debris; commit (a)
   so the live tree can fetch it. Start with the coupled morph pair
   (`proteus_hooks.py` + its tests) once the 17 failing tests are addressed.
2. Decide `origin/master` `ef8ac9a8`: merge into the migration branch or record
   why it stays a fork.
3. WSL Ubuntu: either commit/reconcile its 1066 dirty files or declare it a
   scratch mirror; it cannot stay an unchecked third body indefinitely.
4. G: archives: initialise HEAD (or document why they are object stores, not
   repos) so a revision comparison exists.
