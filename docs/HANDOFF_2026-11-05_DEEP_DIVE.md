# HANDOFF — 2026-11-05, zero-error followups + the pre-backup repair instruction

**HEAD at writing: `0f074751`** (`docs: the repair every lane runs before a clone to D:`).
This file's own commit is its child; `git log --oneline -1 -- docs/HANDOFF_2026-11-05_DEEP_DIVE.md`
names it, and a SHA that does not resolve means the handoff is stale.

---

## 1. Trusted state — each claim with the command that produced it

Every line below was run in `C:/Azazael/azazael` on 2026-11-05. Interpreter
`C:/Azazael/.venvs/py315t/Scripts/python.exe` (3.15t) except where `python` is named.

| claim | command | result |
| --- | --- | --- |
| enum aliases fixed, tests green | `pytest -q tests/test_cain_obsolescence_mark.py tests/test_cain_obsolescence_cli.py` | `19 passed`, `15 passed`, exit 0 |
| every blocking hook stanza resolves | `python tools/control_tiers.py --check` | `PASS -- every blocking stanza invokes an existing script (10 blocking, tiers T1=8, T2=4)`, exit 0 |
| dead_control no longer calls a dispatched gate dead | `python tools/evidence_gate.py --only dead_control` | `[PASS] 42 unreachable (0 new), 3 exported-but-uncalled, 8 dispatch-registered (T2)`, `GATE: PASS`, exit 0 |
| the new tools add no anti-patterns | `python tools/staged_scanner_gate.py` | `6 .py file(s): no new anti-patterns.`, exit 0 |
| one backup ref holds work HEAD cannot reach | `python tools/orphan_watch.py` | exit **1**, `STRANDED refs/backup/orphaned-2026-11-05 -> 2ea4718c63ff holds 15 commit(s)` |
| a destructive verb is reversible before it runs | `python tools/git_safe.py --dry-run reset --hard HEAD` | 18 dirty paths snapshotted as blobs, 19 undo lines, exit 0 |
| a claim is anchored, not positional | `python tools/claim_anchor.py measure --lane freebuff --paths …` then `verify .audit/anchors/20261105T160109Z.json` | `intact 3 changed 0 lost 0`, `VERDICT: SURVIVED`, exit 0 |
| today's harvest lane is schema-clean | `python tools/harvest_now.py --agent freebuff --validate` | `6 row(s)`, `every row in 2026-11-05 satisfies the schema`, exit 0 |
| old harvest debt is real, not hidden | `… --validate --all-dates` | exit 1, `27 defective row(s)` — all dated 2026-10-19, all `missing ['item_id']` |
| three commits landed with stats | `git show --stat 14f336b9 29a129fa 0f074751` | 3 files +116/−7 · 6 files +1385/−3 · 3 files +451 |
| WSL distros | `wsl.exe -l -v` | `Ubuntu-26.04` Stopped (default), `kali-linux` Stopped, `docker-desktop` Stopped |
| `G:` is an archive, not a tree | `ls /mnt/g/AZAZAEL` + `git -C /mnt/g/AZAZAEL rev-parse` | `ubuntu_archive` only; `fatal: not a git repository` |
| `D:` has room | `df -h /d` | 115 G total, 6.3 G used, **109 G avail**, 6 % |
| board store | `python C:/Users/clint/_board.py store` | `telemetry_store.db`, 36 954 112 bytes, 45 288 queue rows |
| freebuff queue | `_board.py stats freebuff` | `available: 1`, `open: 1`; row 47670 claimed then **released** (ELIZA manifest, out of scope for this turn) |

**Defect found and still open at the moment of writing:** `state/head.json` said
`272a4f7c` / `2026-11-04T20:47` while HEAD was `0f074751` — a cached reading answering
for a tree it no longer described. §5 step 4 rewrites it.

## 2. What landed

- `14f336b9` — `VendorArchetype` had three members sharing the value `"cain"`, so two were
  Python aliases and iteration yielded 5 where 7 were declared. The alias was the defect,
  not the test. Also carries cherry-pick `13cc87b3` (+112).
- `29a129fa` — five instruments plus the `dead_control` repair:
  `control_tiers.py`, `orphan_watch.py`, `git_safe.py`, `claim_anchor.py`,
  `harvest_now.py`, and `evidence_gate.py`'s dispatch bucket.
- `0f074751` — `docs/TREE_REPAIR_BEFORE_BACKUP_2026-11-05.md` (the all-lane,
  all-environment repair), `docs/DECISION_2026-11-05_ORPHANED_TIP.md` (adopt by slice),
  and today's harvest lane.

## 3. Attempted and failed — what not to re-try

1. **Committing the new tools as written was rejected by the staged scanner** — 8 findings
   in my own code: `subprocess_no_timeout` ×5, `shell_true` ×1, `except_return_default` ×2.
   All real. Fixed structurally: `GIT_TIMEOUT = 120` on every call, the undo plan became
   `(argv, outfile)` so no shell string executes, and `_count()` raises rather than
   returning 0 — because in `orphan_watch` a 0 means "this ref adds nothing", the one
   reading that hides a stranded ref. **Do not rebaseline these.**
2. **`harvest_now.py --validate` scanned all history** and failed on 27 rows dated
   2026-10-19. A gate red from day one gets switched off, so the default is now today's
   lane and `--all-dates` prints the history. Do not "fix" the old rows to make the
   default green.
3. **`control_tiers.py` first resolved stanza 8 to `supervisor_doctor`** — a remediation
   pointer in an `echo`, not the executed gate (`supervisor_mcp --verdict`). Fixed by
   skipping `echo`/`#` lines and reporting `target_source=invoked|mention`.
4. **`orphan_watch.py --json | head` read `exit 0`** while the tool exits 1: `$?` after a
   pipeline is the last command's status. Re-run without the pipe, or read `PIPESTATUS`.
5. **`df -h /mnt/g` answered for the Git Bash root filesystem**, not `G:`. Mount points in
   this shell do not all answer `df`; no free-space figure for `G:` is quoted anywhere.
6. **An earlier read said `G:` and WSL were unresolvable.** `/mnt/g` is in fact present and
   `wsl.exe` enumerates three distros. The earlier claim was wrong and is retracted.

## 4. The queue, in blocking order

1. **Slice the orphaned tip** (`docs/DECISION_2026-11-05_ORPHANED_TIP.md` §4).
   `neurosym_wsp` (20 files) exists nowhere on the branch; the 18 `ARC/esquire/captures`
   pages and `worktree_snapshot.py` likewise. Slice 1 (cain CLI) is already landed.
2. **Run §3.2 and §3.3 of the repair doc in WSL Ubuntu and Kali.** Both are `Stopped`; those
   commands have never been executed. First lane to run them corrects the doc.
3. **The `.audit/` untracking question** (`git ls-files .audit | wc -l` → 1583 tracked and
   ignored). Owner decision, separate commit, must state the bytes stay on disk.
4. **The `D:` backup clone itself**, once 1–3 are decided: bundle `--all`, clone from the
   bundle, verify by running `control_tiers.py --check` *inside the clone*.
5. **Board row 47670** (ELIZA publication manifest, 23 undeclared files) — released back to
   the queue, untouched.

## 5. First commands for the next session

```bash
python C:/Azazael/azazael/tools/mcp_startup_gate.py --fix      # want: exit 0, all [PASS]
python C:/Azazael/azazael/tools/session_start.py "<task>"       # PMB + Engram context
#   then the MCP tool supervisor__verdict                       # want: GO
python C:/Users/clint/_board.py claim freebuff 10

cd C:/Azazael/azazael
python tools/head_state.py --write        # fixes the stale 272a4f7c reading
python tools/orphan_watch.py              # still 1 until the tip is sliced or dropped
python tools/control_tiers.py --check     # baseline: T1=8, T2=4
```

## 6. Expiry

**These numbers are valid until 2026-11-12.** After that, or after any of: a push, a
rebase/reset, a new hook stanza, or a WSL distro starting — re-measure
`control_tiers`, `orphan_watch`, `evidence_gate`, `head_state`, and the branch graph.
The tier table, the 15-commit figure and the 1583 tracked-`.audit` figure all move with
the tree.
