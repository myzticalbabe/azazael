# TREE CLEANUP — how a lane leaves a shared worktree at zero

**Audience:** every lane reading `lane.<lane>.tasks` (freebuff, kilo, opencode, crush, agy).
**Measured at:** HEAD `6579f565`, 2026-11-05, worktree `C:/Azazael/azazael`.
**Expiry:** the *numbers* in section 6 must be re-measured after 2026-11-12. The
rules do not expire; the counts do.

This worktree is shared. A "clean tree" is not "nothing is dirty" — other lanes
have work in flight by design. It is **nothing dirty that your lane cannot name a
board row or a commit for**.

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

| path group | count | owner evidence | action |
| --- | --- | --- | --- |
| `ARC/deere/*` → `analysis/deere/*` | 19 `D` + 19 `??` | row 47666 cites `c07ee3a1`; that commit is **dangling** | the lane that made the move re-lands it (paths are already correct in the tree) |
| `tools/deere_claims_check.py`, `tests/test_deere_claims_check.py` | 2 `M` | same row, same dangling commit | same lane, same slice |
| `.audit/session_*.jsonl`, `.audit/anchors.jsonl` | 25 `D` + 1 `M` | no row names a retention run; `.audit/` is gitignored (`.gitignore:82`) | one lane takes index hygiene and names itself in the commit; nobody "restores" them |
| `src/ARC/cain_obsolescence_accountability/cain_obsolescence_cli.py` | 1 `M` (−4) | cain wing work | the cain lane slices it |
| `cain_marks.json`, `cain_marks_final.json` at repo root | 2 `??` | no row; scratch-shaped | owner moves to `ARC/cain/` or `/tmp`; if nobody owns them, a row |
| `Project_ELIZA/tools/bcc_bypass.py` | 1 `M` (+27) | no row in the last 10 status rows | the eliza lane names itself or reverts |
| `logs/anti_pattern_baseline.json` | 1 `M` | `logs/` is gitignored, this file is force-added | a rebaseline needs a stated reason; otherwise revert |
| `state/bake_harvest_freebuff_2026-11-04.jsonl` | 1 `M` | freebuff harvest lane | land with the fix it describes |
| `anti_pattern_detail.txt` | 1 `??` | no owner | row, not cleanup |

Two rows say "no owner". That is the honest reading of this store: a file with no
board row and no commit is not evidence of a lane's intent, and no lane should
invent one to make the count reach zero.

---

## 7. The one-line contract

> Leave the worktree with **nothing dirty your lane cannot name**, and state your
> name in the commit that removes it.
