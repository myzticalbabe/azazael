# INCIDENT 2026-11-05 — a restore destroyed uncommitted work, and nothing recorded it

**Written:** 2026-11-05, after the loss. **Status:** losses confirmed, culprit
unattributed, recovery exhausted by four independent routes, prevention not yet
installed.

Numbers here are readings with a command behind them, taken in the session that
observed the loss. A number without its command is narrative; this file keeps
them paired.

---

## 1. What happened, as observed

Between **09:56:43 and 09:57:03 EST** a bulk restore ran over the worktree. It
reverted tracked files to HEAD, deleted untracked files, and re-created tracked
files whose deletions were staged. Nothing announced it: no lane posted a
`lane.<lane>.status` row naming a clean or restore operation in that window, and
`git reflog` shows only the ordinary commits of the session (a `git checkout --`
/ `git restore` leaves no reflog entry, which is why the reflog cannot name it).

What the worktree looked like afterwards, by mtime:

| path | before | after |
| --- | --- | --- |
| `Project_ELIZA/tools/bcc_bypass.py` | a gzip decode fix was believed present (+27) | worktree is byte-identical to HEAD; mtime 09:57:03 |
| `src/ARC/deere/**` | edited tree | restored to HEAD, mtime 09:56:43 |
| `analysis/deere/**` | appeared deleted (19 files) | **not a loss — see §1.1** |
| `cain_marks.json`, `cain_marks_*.json` (repo root) | present | deleted |
| `.audit/**` | deletions staged by an earlier pass | re-created (1583 tracked files) |
| `state/bake_harvest_freebuff_2026-11-04.jsonl` | rewritten with 2 `kit-gzip` rows | rewritten, `grep -c kit-gzip` = **0** |

### 1.1 Corrections made in this same session, after checking

Two of the rows above were wrong when first written. They are kept with their
correction rather than deleted, because a record that quietly drops a claim
cannot be audited.

- **`analysis/deere` was not destroyed.** `git show --name-status 5e98e9d0`
  lists 19 `R100` renames `ARC/deere/ -> analysis/deere/` — another lane landed
  the move as a commit at 10:03:59, four minutes after the restore window. The
  files were "missing" from `analysis/deere` because they had been put back at
  `ARC/deere` by the restore and then moved by a commit. What looked like a
  deletion was a rename landing. This is the exact failure mode the canon warns
  about: a transient read of one tree state read as destruction.
- **The `bcc_bypass.py` gzip fix is *absent*, and the two candidate explanations
  cannot be separated now.** `git diff HEAD -- Project_ELIZA/tools/bcc_bypass.py`
  is empty and both sides are 540 lines, so the worktree equals HEAD. The file's
  mtime (09:57:03) sits inside the restore window, which is *consistent with* a
  loss but is not proof of one — a fix that was never written leaves the same
  content and a different mtime.
  **What is certain, and matters more:** HEAD's `bcc_bypass.py` advertises
  compressed bodies and has no decoder —
  `grep -n 'Accept-Encoding\|gzip\|decode_body' Project_ELIZA/tools/bcc_bypass.py`
  prints only line 50, `"Accept-Encoding": "gzip, deflate, br"`, and no
  `decode_body` anywhere. Any response served compressed is stored or parsed as
  bytes that are not the document. That is a live defect at HEAD independent of
  the incident, and it is the next item for the ELIZA lane whichever way the
  loss question resolves.

The last row is the one that matters for the next session: **the harvest rows had
never been committed.** `git show HEAD:state/bake_harvest_freebuff_2026-11-04.jsonl
| grep -c kit-gzip` also prints `0`, so HEAD never held them and the file's
re-creation from HEAD is loss, not restoration.

## 2. Recovery attempts — all negative, each with its command

1. **Git's own lost-object store.** `grep -rl "def decode_body" .git/lost-found/other`
   over 131 objects: no match. An uncommitted edit is not an object, so this
   could not have worked; it was checked because a `git add` earlier in the
   session would have made one.
2. **The audit trail.** `grep -rl bcc_bypass` across 1728 `.audit/*.jsonl` files:
   no match. The audit lane recorded file events for other paths in the same
   window, so this is an absence with evidence behind it, not a guess.
3. **The G: archive.** `G:/AZAZAEL`, `G:/AZAZAEL_SOURCE_OF_TRUTH` — no mirror of
   these paths at depth 4.
4. **WSL.** `//wsl.localhost` resolves empty; the Linux lane's copy was not
   reachable from this host in this session.

Nothing was fabricated to refill the gaps. The two `kit-gzip` harvest rows are
**gone**, and this file says so rather than reconstructing them from memory (a
reconstruction would carry today's understanding, not the encounter's).

## 3. A retracted attribution, and why it is in this file

Two `cain_marks*.json` files at the repository root stamped
`KILO-NEMOTRON-3-ULTRA-2026-11-05T02:30:00Z`, and that stamp was read as evidence
that the kilo lane had produced them. It was not: the string was a **literal in
`cain_obsolescence_cli.py`**, so every run by every lane stamped it.
`git show HEAD:.../cain_obsolescence_cli.py | grep -n KILO` shows the constant.

Two consequences, both now fixed in the same file (see §4):

- A witness field that is a constant attributes nothing and, worse, produces a
  confident wrong attribution — which is exactly the failure mode an attribution
  field exists to prevent.
- The marks defaulted to the process working directory, which is how they landed
  beside the tracked tree where a restore deleted them. They were never part of
  the tree, so they were never protectable by git.

## 4. What changed in response

- `cain_obsolescence_cli.py`: witness from `--witness`, then `CAIN_WITNESS`, then
  `UNATTRIBUTED`; default output now `<package>/marks/`; an explicit `-o` into a
  repository root (a directory with `pyproject.toml` or `.git`) is refused with
  the remedy named, instead of silently writing untracked evidence at the root.
- `tests/test_cain_obsolescence_cli.py`: four tests pinning each of those
  behaviours, including that a caller-supplied witness reaches `compute_marks`.
- `src/CORE/LaneMessageBoard.py` + `docs/scripts/lane_kit.py`: the lane set is
  now `opencode, kilo, freebuff, crush, agy` (was three) in **both** copies, with
  a parity test, so crush and agy can receive and read rows instead of refusing
  them. A restore cannot be reported to a lane whose board will not accept the
  post.

## 5. What is still missing (the reason this file exists)

The loss itself is prevented by nothing yet. The open items, in the order they
would have helped in this incident:

1. **A snapshot before any bulk restore.** `tools/worktree_snapshot.py` does not
   exist. It should copy every dirty and untracked file to
   `.worktree-snapshots/<timestamp>/` with a manifest, and `--restore <ts>` to put
   them back. This is the only item that would have made §2 unnecessary.
2. **A machine-checkable record of who ran what.** The board accepts status rows;
   nothing obliges a lane to post one before a tree-wide operation. The rule to
   adopt is the one the canon already uses elsewhere: an operation that can
   destroy another lane's work must name itself first — a row naming the paths,
   the verb, and the expected effect.
3. **Commit early, in slices.** Every destroyed item in §1 was a completed,
   tested change that sat uncommitted while the next item was started. The hook
   is slow (~3 min) and that is *why* work accumulated; the answer is
   background commits with a `git log` poll (already the documented practice),
   not a bigger working set.

## 6. How to read this file later

Expiry: the mtimes and counts above are readings of 2026-11-05 and will not
survive another restore. If you are reading this after a later loss, re-measure
(`git status --porcelain`, `ls -l --time-style=full-iso`) instead of quoting
these; the *method* — timestamp window, per-path evidence, four recovery routes,
retraction of a constant-backed attribution — is the part that transfers.
