# DECISION — the orphaned tip `2ea4718c` (2026-11-05)

**Question:** after the branch was reset backwards from `2ea4718c` to `4b0ace17` and
fifteen commits lost their ref, do we **adopt** that tip (reset the branch forward to it)
or **drop** it (delete `refs/backup/orphaned-2026-11-05`)?

**Decision: neither wholesale verb. Adopt by slice.** The ref stays; the branch does not
move to it; the valuable content is cherry-picked commit by commit, each with its own test
run. Reasoning and the impact that produced it are below.

---

## 1. What the tip actually contains

`git diff --name-status 4b0ace17 2ea4718c`: **46 A / 1583 D / 21 M / 19 R100**. A
46/1583 summary reads as "+46 files", which is why the number had to be broken open.

### The 46 additions, by group

| group | count | what it is |
| --- | --- | --- |
| `ARC/esquire/captures/` | 19 | 18 captured PA procedural-rule HTML pages (`P1_rule_801.html` … `P20_rule_403.html`) plus `CAPTURES.json` |
| `Project_SHARDEX/neurosym_wsp/` + `neurosym_wsp_main.py` + `wsp_harness.py` | 20 | a whole symbolic spec/verify subsystem: `.lp` / `.smt2` / `.json` specs for `inference_router`, `memory_consolidator`, `swarm_policy`; `smt_verifier.py`, `symbolic_tracer.py`, `worm_spec.py`, `benchmark_suite.py`, `audit_trail.py`, `wsp_editor.py` |
| `docs/` | 4 | `HANDOFF_2026-11-05_ARC.md`, `INCIDENT_2026-11-05_WORKTREE_RESTORE.md`, `TREE_CLEANUP_2026-11-05.md`, `ZERO_ERROR_ARCHITECTURE_ARC_ESQUIRE_2026-11-05.md` |
| `tests/` | 3 | `test_bcc_bypass_encoding.py`, `test_eliza_release_gate.py`, `test_esquire_capture.py` |
| `tools/` | 2 | `esquire_capture.py`, `worktree_snapshot.py` |
| other | 2 | `src/spitfire/__main__.py`, `Project_SHARDEX/…` remainder |

The `neurosym_wsp` subsystem is 20 files with no counterpart on the branch: it is
**capability that exists only in the orphaned tip**. Two of the four docs are the ones
recovered byte-identically into `e2bfa3c6` from the blob store, which proves the recovery
path works and that the tip's content was worth recovering.

### The 1583 deletions are one decision, not 1583 losses

Every deletion is `.audit/session_*.jsonl`. At HEAD those files are **tracked**:

```
git ls-files .audit | wc -l   -> 1583
git ls-tree -r --name-only HEAD .audit | wc -l -> 1583
grep -n '^\.audit/' .gitignore -> 82:.audit/
```

So this tree **tracks 1583 files it also ignores** — the tracked-ignored-directory defect.
The tip's move was to untrack them (`git rm -r --cached .audit`), which leaves the bytes on
disk and merely stops committing them. That is probably correct (a session-audit trail that
adds ~1500 files per session cannot live in git), but it is a **policy decision about the
audit trail**, and it should not be taken as a rider on "adopt the tip".

### The 21 modifications include live gates

`.githooks/pre-commit`, `tools/preflight_all.py`, `tools/arc_check.py`,
`tools/arc_pin_audit.py`, `tools/arc_provenance.py`, `src/CORE/LaneMessageBoard.py`,
`Project_ELIZA/tools/eliza_release_gate.py`, `Project_ELIZA/tools/bcc_bypass.py`, and 7
tests. A `reset --hard` onto the tip would rewrite the commit hook and the preflight
registry in one move that no test covers before it happens.

---

## 2. Why not `reset --hard refs/backup/orphaned-2026-11-05`

1. **It moves the branch backwards over new work.** `e2bfa3c6` is a descendant of
   `4b0ace17` and not of `2ea4718c`; resetting to the tip discards `e2bfa3c6` (3 files,
   +795) and this session's commits. `git_safe.py` would snapshot them, so the loss is
   recoverable — but a recoverable loss is still work spent twice.
2. **It applies 1583 index deletions and a hook rewrite atomically, unmeasured.** The
   blast radius is the audit trail and the commit gate, which are the two surfaces this
   tree uses to prove anything.
3. **The value is separable.** All 46 additions are *additive* — they cannot conflict with
   the branch. Cherry-picking is the lower-risk verb and it has already been demonstrated:
   `git cherry-pick -n 13cc87b3` applied clean and produced 112 insertions / 3 deletions
   in `cain_obsolescence_cli.py` + its test, both of which now pass (19 and 15 tests).

## 3. Why not `git update-ref -d refs/backup/orphaned-2026-11-05`

Because `neurosym_wsp` (20 files) and the 18 rule captures exist nowhere else. Deleting the
ref puts them one `gc` away from gone, and `gc.reflogExpireUnreachable` is 30 days — the
silent-loss window. `orphan_watch.py` exists to make exactly that state loud; it currently
reports it:

```
STRANDED  refs/backup/orphaned-2026-11-05 -> 2ea4718c63ff holds 15 commit(s)
          HEAD does not reach (HEAD is 1 behind it)
```

## 4. The slicing order

Each slice is a separate commit with its own test run; a slice that fails its tests is
reported, not forced.

| # | slice | files | gate before landing |
| --- | --- | --- | --- |
| 1 | `13cc87b3` cain CLI | 2 | **landed** — `test_cain_obsolescence_mark.py` 19 passed, `test_cain_obsolescence_cli.py` 15 passed |
| 2 | `neurosym_wsp` subsystem | 20 | `pytest tests/ -k wsp`; import the module and run one spec through `smt_verifier` |
| 3 | esquire captures + `esquire_capture.py` | 20 | `test_esquire_capture.py` |
| 4 | `worktree_snapshot.py` → `tools/` (not inside a snapshot dir) | 1 | `python tools/worktree_snapshot.py --help`, then `git ls-files tools/worktree_snapshot.py` is non-empty |
| 5 | docs (2 of 4 already recovered in `e2bfa3c6`) | 2 | byte-compare against the blob already recovered |
| 6 | `.gitignore` / `.audit` untracking | 1584 | **owner decision**, not a slicing item: separate commit, separate justification, and it must state that the bytes stay on disk |

Order matters only for 4: the snapshotter should be on the tree before slices 2–3 are used
to snapshot anything.

## 5. State of the ref, after this decision

- `refs/backup/orphaned-2026-11-05` → `2ea4718c` — **kept**, untouched.
- The branch stays at this session's HEAD; the decision is **reversible** because both
  endpoints are still named. That reversibility is the point of recording it rather than
  performing it.
- `orphan_watch.py` will keep exiting 1 until the tip is fully sliced or deliberately
  dropped. That is the intended signal: an unadopted ref is a standing question, and a
  check that stopped reporting it would be the silence that lost it the first time.
