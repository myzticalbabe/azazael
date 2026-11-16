# TREE CLEANUP — how a lane leaves a shared worktree at zero

**Audience:** every lane reading `lane.<lane>.tasks` (freebuff, kilo, opencode, crush, agy).
**Measured at:** HEAD `6579f565`, 2026-11-05, worktree `C:/Azazael/azazael`.
**Expiry:** the *numbers* in section 6 must be re-measured after 2026-11-12. The
rules do not expire; the counts do.

This worktree is shared. A "clean tree" is not "nothing is dirty" — other lanes
have work in flight by design. It is **nothing dirty that your lane cannot name a
board row or a commit for**.

## 0.1 Which lanes this reaches, and which it cannot

The poster accepts exactly three lanes. Measured 2026-11-05 while delivering this
instruction:

```
$ python C:/Users/clint/_board.py post freebuff task "..." --from freebuff   -> POST freebuff->freebuff: delivery_row=47672
$ python C:/Users/clint/_board.py post kilo     task "..." --from freebuff   -> POST freebuff->kilo: delivery_row=47674
$ python C:/Users/clint/_board.py post opencode task "..." --from freebuff   -> POST freebuff->opencode: delivery_row=47676
$ python C:/Users/clint/_board.py post crush    task "..." --from freebuff   -> REFUSED: dst_lane must be one of ('opencode', 'kilo', 'freebuff'), got 'crush'
$ python C:/Users/clint/_board.py post agy      task "..." --from freebuff   -> REFUSED: dst_lane must be one of ('opencode', 'kilo', 'freebuff'), got 'agy'
```

`_board.py`'s own module docstring says "Board reader/poster for interactive CLI
lanes (crush, kilo, agy, opencode)" — four names, of which the validation accepts
three and adds `freebuff`. A document that promises delivery to `crush` or `agy`
promises something the tool refuses. If either lane is live, it has no queue here
until that set is widened; until then its instruction is this file, read
directly.

`tasks <lane>` prints a truncated `detail` (the three deliveries store 882, 936
and 833 characters respectively; the reader showed roughly the first 500). Read a
row's full text from the store, never from the truncated listing.

---

## 0. The state this instruction answers (measured, not asserted)

| command | result |
| --- | --- |
| `git status --porcelain \| wc -l` | `55` |
| `git status --porcelain \| grep -c '^ D'` | `44` (25 `.audit/`, 19 `ARC/deere/`) |
| `git status --porcelain \| grep -c '^ M'` | `7` |
| `git status --porcelain \| grep -c '^??'` | `4` tops (`analysis/` holds 19 files) |
| `git merge-base --is-ancestor c07ee3a1 HEAD` | exit `1` |
| `git branch --contains c07ee3a1` | *(empty)* |
| `git fsck --no-reflogs --unreachable \| grep -c commit` | `227` |

The second block is the reason this document exists. `c07ee3a1` is titled
`deere: move the case analysis out of ARC into analysis/deere`, and board row
47666 cites it as the commit that landed the move. It is **on no branch, and not
an ancestor of HEAD**: the 19-file move exists only in the working tree, where it
reads as 19 deletions plus 19 untracked files that no commit claims. A lane that
reported "commit `c07ee3a1`" reported a commit that the branch cannot resolve.

A commit that returns exit 0 has told you the object was written. It has not told
you the branch advanced.

---

## 1. Measure before you touch anything

```bash
cd C:/Azazael/azazael
git rev-parse --short HEAD                       # your pin
git status --porcelain | wc -l                   # dirty before
git status --porcelain -uall -- <your paths>     # your slice, untracked files expanded
```

Write the three numbers down. You will compare against them at the end, and a
cleanup that cannot show "before 55, after 19, mine 0" is a claim without a
measurement.

---

## 2. Seven rules, each bought by a failure

1. **Never `git add -A`, never `git add .`.** This worktree carries other lanes'
   edits. Stage explicit pathspecs only, and after staging check
   `git diff --cached --name-only | wc -l` matches the number you meant to stage.
2. **Slice small: ≤8 files per commit, ≤150 changed lines per file.** The commit
   gate blocks above those and names the file. A 200-line file is two commits or
   a stated reason — not `ALLOW_BULK_COMMIT`.
3. **`ALLOW_BULK_COMMIT=1` is an environment variable, not message text.**
   `scripts/commit_gate.py` reads `os.environ`. Setting it in the message changes
   nothing; setting it without a justification in the message is a bypass.
4. **Commit by path, then read the stat back.** `git commit` succeeds with an
   empty index. Only `git show --stat HEAD` distinguishes "landed" from "wrote a
   message about nothing".
5. **Verify ancestry, not exit status.**
   ```bash
   git merge-base --is-ancestor "$(git rev-parse HEAD)" HEAD && echo ON_BRANCH
   ```
   Run it after every commit. Exit `1` from that check, an empty
   `git branch --contains <sha>`, or a sha that `git log --oneline` does not show
   means your work is a dangling object and the tree still holds it. Re-land it;
   do not report it.
6. **Do not resurrect or delete another lane's lines.** A `D` you did not make is
   not yours to restore (`git checkout -- <path>` on it republishes a file the
   owner removed on purpose). An `??` you did not write is not yours to delete.
   Post a row and leave it.
7. **Retire the row, and read the retirement back.** `done <id> "<command +
   exit + line>"` exits non-zero when the row was never claimed — a real signal.
   `report <lane> status "<detail>"` then `status <lane>` to read it. A post you
   cannot read back did not land.

---

## 3. Handle each line by category, not by mood

| status | what it is | what to do |
| --- | --- | --- |
| `M` | your lane's edit | slice, commit by path, stat back |
| `M` under `logs/` (`anti_pattern_baseline.json`) | a **rebaseline** | state the reason in the message, or revert it. Silently editing a baseline resets a ratchet that only ever shrinks |
| `D` you made (retention, relocation) | a real change | `git add -u <paths>`, commit, stat back |
| `D` you did not make | someone else's removal | leave it; post a row naming the path and the sha that last touched it |
| `??` evidence/captures | retained in-tree **with sha256** | commit it, or move it to the owner's `raw/` tree; never delete |
| `??` scratch (`*.txt`, `cain_marks*.json` at repo root) | scratch that escaped | move to `/tmp` or delete **only if you wrote it**; a root-level artifact with no owner is a row, not a cleanup |
| `??` under `.audit/` or `logs/` | gitignored by design | do not stage |
| tracked files under `.audit/` | legacy force-added into an **ignored** directory (`.gitignore:82`) | index hygiene: `git rm --cached -r .audit/` in one commit with a stated reason, or land the deletions with `git add -u .audit/`. Either is fine; a half-tracked ignored directory is not |

`git clean -fd` is not on this list. It deletes untracked evidence, and this
tree's ARC captures are retained precisely so a court could re-read them.

---

## 4. The copy-paste sequence

```bash
cd C:/Azazael/azazael
PY=C:/Azazael/.venvs/py315t/Scripts/python.exe   # production interpreter, 3.15t

git status --porcelain -uall -- <paths>           # 1. measure your slice
git add -- <path1> <path2> ...                    # 2. explicit pathspecs, <=8 files
git diff --cached --name-only | wc -l             # 3. equals the count you meant
git commit -m "$(cat <<'EOF'
<scope>: <why this change exists>

<what the reader needs to re-run to check it>
EOF
)" > logs/commit.log 2>&1 &                       # 4. hook takes ~3 min: background it
```

Then poll, do not assume:

```bash
git log --oneline -1                              # the sha exists
git show --stat HEAD                              # files + insertions, non-empty
git merge-base --is-ancestor HEAD HEAD && echo ON_BRANCH
git status --porcelain | wc -l                    # 5. dirty after, vs the number from step 0
```

Finally:

```bash
python C:/Users/clint/_board.py done <board_id> "cleanup <paths>; git show --stat HEAD -> <n> files; git status --porcelain: <before> -> <after>; <your check> exit <n>"
python C:/Users/clint/_board.py report <lane> status "tree cleanup: <before> -> <after>, mine 0. cmd: git status --porcelain -uall -- <paths>; exit 0; line: (empty)"
python C:/Users/clint/_board.py status <lane>     # read it back
```

---

## 5. What never to do

- `git add -A`, `git add .`, `git commit -a` on this worktree.
- `git reset --hard`, `git checkout -- .`, `git clean -fd` — each destroys another
  lane's in-flight work or retained evidence, silently.
- Kill a `pams` or `supervisor` process to "refresh" it. They are the client's
  stdio children; killing one breaks the live session.
- Report a commit because `git commit` exited 0. Read the stat and the ancestry.
- Retire a row you did not claim. `done` will refuse it, and the refusal is
  correct.
- "Clean up" a path you cannot attach to a board row or a commit of your own.

---

## 6. Inventory at `6579f565` — attribution as measured, not assumed

| path group | count | owner evidence (measured) | action |
| --- | --- | --- | --- |
| `ARC/deere/*` → `analysis/deere/*` | 19 `D` + 19 `??` | **freebuff**: rows 47665, 47666 name `60651efb` then `c07ee3a1` | freebuff re-lands the move; the tree's paths are already correct, so `git add -u ARC/deere` plus `git add analysis/deere` is the whole slice |
| `tools/deere_claims_check.py`, `tests/test_deere_claims_check.py` | 2 `M` | **freebuff**, same rows, same dangling commit | freebuff, same slice |
| `.audit/session_*.jsonl`, `.audit/anchors.jsonl` | 25 `D` + 1 `M` | no row names a retention run; `.audit/` is gitignored (`.gitignore:82`) | one lane takes index hygiene and names itself in the commit; nobody "restores" them |
| `src/ARC/cain_obsolescence_accountability/cain_obsolescence_cli.py` | 1 `M` (−4) | no row; continues `57ad578d` `CAIN: Fix anti-pattern regressions (import_inside_function x2, subprocess_no_timeout)` (2026-11-04 22:05) — the edit removes exactly those two local imports | the lane that wrote that commit slices it; kilo holds the cain marks (next row) and should check first |
| `cain_marks.json`, `cain_marks_final.json` at repo root | 2 `??` | **kilo**: both files name `"witness": "KILO-NEMOTRON-3-ULTRA-2026-11-05T02:30:00Z"`, both hold the same 7 marks, generated 21:47:21 and 21:49:49 | two runs of one generator that wrote to the working directory; move under `ARC/cain/` or `/tmp`, do not commit either to the repo root |
| `Project_ELIZA/tools/bcc_bypass.py` | 1 `M` (+27) | **freebuff**: harvest row `kit-gzip-raw` (`error_fix`) in `state/bake_harvest_freebuff_2026-11-04.jsonl` describes this exact `fetch_http` gzip defect and the Apple page measurement | land the fix **and** its harvest row in one commit — the lane file is the rule, not a leftover |
| `logs/anti_pattern_baseline.json` | 1 `M` | no row; `logs/` is gitignored and this file is force-added | a rebaseline needs a stated reason in the message; otherwise revert |
| `state/bake_harvest_freebuff_2026-11-04.jsonl` | 1 `M` | **freebuff**, same `kit-gzip-raw` row | pair with the fix above |
| `anti_pattern_detail.txt` | 1 `??` | no row; the shape `anti_pattern_gate.py --report` produces | a row, not a deletion |

Three rows say "no owner". That is the honest reading of this store: a file with
no board row and no commit is not evidence of a lane's intent, and no lane should
invent one to make the count reach zero. What the three *do* have is a plausible
producer named, which is enough to ask the question — and not enough to answer it.

---

## 7. The one-line contract

> Leave the worktree with **nothing dirty your lane cannot name**, and state your
> name in the commit that removes it.

---

## 8. Post-incident revision — 2026-11-05T10:20Z, HEAD `ad5d7157`

Sections 0–7 are pinned at `6579f565` and are left as written; this section
corrects them with what was measured afterwards. Nothing above is edited, because
a cleanup instruction whose own history is silently rewritten is one more artifact
that cannot be re-read.

### 8.1 The tree, re-measured

```
$ git rev-parse --short HEAD                     -> ad5d7157 (branch azazael-intel-ultra-9-evo)
$ git status --porcelain | wc -l                 -> 0
$ git status --porcelain | grep -c '^ D'         -> 0
$ git status --porcelain | grep -c '^ M'         -> 0
$ git status --porcelain | grep -c '^??'         -> 0
```

The 55 dirty entries of §0 are gone, and every one of the three unowned paths
(§6) was resolved by the lane that produced it: `.audit/` by `ad5d7157`
(1,588 files, index hygiene), the CAIN files by the CAIN slice `13cc87b3`, and
`bcc_bypass.py` with its tests and harvest row.

### 8.2 Two §6 rows were read wrong, and how

| §6 row | what §6 said | what was measured later |
| --- | --- | --- |
| `ARC/deere/*` 19 `D` + 19 `??` | freebuff re-lands the move; the tree holds the only copy | **The move landed.** `git show --name-status --format= 5e98e9d0` → `19 R100` (`ARC/deere/` → `analysis/deere/`), committed 10:03:59. Nothing was re-landed and nothing was lost |
| `c07ee3a1` dangling | a commit no branch contains | still true of the *commit*; it was never true of the *work*, which landed under `5e98e9d0` |

The defect was in the reading, not the tree: `19 D + 19 ??` is the **shape** of a
move and the **shape** of a loss. §2 rule 5 tells you to check ancestry of a sha;
it does not tell you to check whether a *different* sha carries the same content.
A move assertion needs `--name-status` with rename detection, or `git log --follow`.

### 8.3 The restore at 09:56, kept as a finding

Between 09:56:43 and 09:57:03 EST a mass restore ran: tracked files reverted to
HEAD (`bcc_bypass.py` mtime 09:57:03, its gzip fix absent), untracked work
deleted (`cain_marks.json`, `cain_marks_final.json`), and
`state/bake_harvest_freebuff_2026-11-04.jsonl` rewritten to HEAD with its two
`kit-gzip` rows gone. Full record: `docs/INCIDENT_2026-11-05_WORKTREE_RESTORE.md`
(141 lines), including §1.1, which retracts the two claims that did not survive
measurement.

- **Recoverable:** the tracked edits (rewritten by hand, tests green).
- **Unrecoverable:** the two harvest rows. They were never committed — absent in
  `git show HEAD:state/bake_harvest_freebuff_2026-11-04.jsonl` as well — so no
  object held them. Four recovery routes were tried and came back negative
  (`.git/lost-found/other`: 131 objects, no match; 1,728 `.audit/*.jsonl`; the
  `G:/` mirror tree; `//wsl.localhost`), and a route that was *tested and came
  back empty* is what makes "unrecoverable" a finding rather than a shrug.
- **Culprit:** unattributed. `git reflog` shows only this session's own commits,
  because a `git restore` writes no reflog entry. No lane posted a restore or
  clean status row. Recorded as unknown, not as a lane.

### 8.4 Two rules added, both bought today

8. **Snapshot before a destructive verb.** `python tools/worktree_snapshot.py
   --snapshot` writes a sha256 manifest under `.worktree-snapshots/` (gitignored)
   and `--restore <STAMP>` puts the bytes back; `--verify` re-checks them. Caps are
   25 MB per file and 512 MB total — this disk was at 99% — and **files outside
   the caps, or ignored by `.gitignore`, are named in the output** rather than
   silently skipped. It cannot protect what it does not capture, so it says what
   it did not capture.
9. **An empty index is not proof of a no-op.** After another lane's commit, `git
   diff --cached` reads 0 whether your files were swept out *or are already in
   HEAD*. `git add` exits 0 in both cases. The only landing proof is content:
   `git ls-tree HEAD -- <paths>` and `git diff HEAD -- <paths>` empty. Measured
   today: five files staged for this lane's own commit were absorbed by
   `ad5d7157`, whose message describes none of them — the work landed, the
   attribution did not. A handoff must cite the commit that *contains* the file
   and say that its message is not a description.

### 8.5 Expiry

Section 8.1's zeros are a reading at `ad5d7157`, 2026-11-05T10:20Z. Re-measure
before quoting after **2026-11-12**. Sections 2, 8.4 and 8.2's rename rule do not
expire: they are properties of git and of this worktree, not counts.
