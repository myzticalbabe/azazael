# Git at the bleeding edge — research, three tools, and what they measured

Date: 2026-11-01. Host git: **2.53.0.windows.1**. Repo: 32,597 tracked files, 31 packs,
938.94 MiB packed, 7,958 loose objects before this pass.

Everything below separates three things that are usually conflated: what git *can*
do, what this repo *was* doing, and what changed after it was measured.

---

## 1. What "bleeding edge" actually means in git right now

From the upstream docs and the 2.51 release notes (Aug 18, 2025):

| capability | what it is | status | why it matters here |
| --- | --- | --- | --- |
| `git merge-tree --write-tree` | real three-way merge in the object database; exit 0 clean / 1 conflicts / >1 could not attempt | stable since 2.38 | merge readiness for every branch with no worktree, no index, no `merge --abort` |
| `git replay` | replay commits onto a new base, atomic ref transaction, works on bare repos | **EXPERIMENTAL** (2.46+) | rebase a whole stack with zero checkouts |
| `git multi-pack-index` | one lookup index over many packs; cruft-free handling improved in 2.51 | stable | 31 packs is 31 index probes per missing lookup |
| `git commit-graph` | commit metadata cache; `log`/`merge-base`/rev-walks skip object reads | stable | already present here |
| reftable ref backend | log-structured refs, atomic multi-ref writes, Git 3.0 default | opt-in (`--ref-format=reftable`) | only pays off on large refsets; 13 refs here |
| SHA-256 repositories | future default hash | interoperable, not yet default | planning item, not a win today |
| fsmonitor + untrackedCache + index v4 | daemon/extension that lets `git status` skip stat-ing the whole worktree | stable | the single biggest local win measured below |
| sparse-index / sparse-checkout cone | index that stays O(cone) instead of O(tree) | stable | needs a cone; not free on its own |
| `git backfill` | download missing blobs in a partial clone in batches | new | relevant only with `--filter` clones |
| path-walk repack (2.51) | packing mode producing smaller packs | new | worth a trial on the 939 MiB pack set |

The honest summary: the *frontier* is not a new command to adopt wholesale — it is
that the three expensive operations in this repo (status, object lookup, branch
rebase) each have a newer, cheaper path that was simply not enabled.

---

## 2. What was built

Three tools, stdlib only, each with a test file. `tools/` is the house location and
the tests follow the repo convention (`sys.path.insert` on `tools/`, real temp
repositories, no git mocks).

### `tools/git_repo_doctor.py` — measure, modernise, measure again
Nine checks (version, ref backend, commit-graph, MIDX, pack shape, fsmonitor,
sparse-index, gc state, alternates). Every verdict carries one line of the command
output that produced it; **UNKNOWN** is a state, not a pass. `--fix` prints the
index writes; `--fix --apply` runs them; `--bench` times four read paths before and
after in the same run, so "faster" is a number, not a feeling.

### `tools/git_merge_gate.py` — "would this branch merge?" without touching anything
Per branch: MERGED / SAME / CLEAN / CONFLICTS / ERROR, with ahead/behind and the
conflicted paths from `merge-tree --write-tree`. Exit 0 clean, 1 conflicts, 2 could
not run. The state model is the point: **exit > 1 is not a conflict**, and a gate
that collapses the two reports work that does not exist.

`--queue --branch a --branch b` answers the merge-queue question instead: each
branch judged against the tree the ones ahead of it produced, not against base.
Two branches can each be CLEAN against base and still conflict with each other.
**No runner invokes `--queue`**: this repo has no merge queue (pushes go straight
to a remote), so the mode is the instrument a queue would call and is run by hand
before landing a batch. That is stated rather than papered over -- a mode nobody
executes is a capability, not a gate.

**Wired into `.githooks/pre-push`** (2026-11-01) as `--pre-push`: it reads git's own
stdin protocol (`local ref, local sha, remote ref, remote sha`) and judges only the
pushes that need a merge — a fast-forward cannot conflict, so testing one would cost
a three-way merge on every ordinary push. CONFLICTS aborts the push with the paths;
ERROR (an unreadable tip, a git too old for `merge-tree`) prints why and passes
*late and loud*, never green. Bypass: `MERGE_GATE_PUSH_BYPASS=1`.

### `tools/git_stack_plan.py` — derive the stack, plan the rebase, replay it atomically
Parent links come from four sources in descending trust: git's own reflog
("branch: Created from …"), strict tip ancestry, a fork-point distance test, and —
when the graph genuinely cannot say — **AMBIGUOUS**, which refuses to plan. `--check`
pre-flights every hop with `merge-tree`; `--apply` runs `git replay`, one atomic
transaction per branch.

### Tests — `tests/test_git_tools.py`, 16 tests
Real repositories with real commits: clean merge, conflicting merge, merged branch,
same-tip branch, unknown ref, stack derivation, ambiguity, dry-run ref immutability,
and an actual `git replay` that asserts the objects exist while the worktree is
deliberately untouched.

---

## 3. Measurements on this repository

### 3.1 MIDX — absent, then written

`git_repo_doctor.py` reported **FAIL: multi-pack-index absent across 31 packs**.
`--fix --apply` wrote it in **0.029 s** (866 KB index).

| read path | before | after | median of |
| --- | --- | --- | --- |
| `rev-list --count --all` | 0.0432 s | **0.0156 s** | 5, reproduced 0.0148 / 0.0157 / 0.0154 |
| `log --oneline -5000` | 0.0646 s | 0.0611 s | 5, one earlier run showed +9.3% — noise |
| `status --porcelain` | 0.1188 s | 0.1127 s | 5 |
| `diff --stat HEAD` | 0.1377 s | 0.1337 s | 5 |

**−64% on the object/index lookup path.** The others are inside noise and are
reported as such rather than as wins.

### 3.2 fsmonitor + untrackedCache — off, now on

| `git status --porcelain`, median of 7 | |
| --- | --- |
| off | 0.1158 s |
| on | 0.0455 s (and 0.0453 s on a second pass) |
| **delta** | **−60.7%** |

Applied to this repository: `core.fsmonitor=true`, `core.untrackedCache=true`,
`index.version=4`. All three are reversible one-liners; none touches history.

### 3.3 The gate, on the real branches

```
base: origin/master (b32b0ed2a2ca)
  deepseek-engram-813          CLEAN   +816/-0   tree f6836a1ded49
  lane-813-recovery            CLEAN   +303/-0   tree 0f624c926c3d
  migration/baseline-20261001  CLEAN   +304/-0   tree 77cf86de4706
  CLEAN=3
```

### 3.4 The stack planner, on the real branches

```
lane-813-recovery -> migration/baseline-20261001
    lane-813-recovery              root
    migration/baseline-20261001    on lane-813-recovery (2 commits since fork)
    ! deepseek-engram-813          parent AMBIGUOUS: lane-813-recovery|migration/baseline-20261001
                                   tie at fork 91528fdd2cd3 -- not guessed
```

Before the restart/untracked-cache work it reported three unrelated roots; the
reflog and fork-distance passes found the one real stack and correctly refused to
guess the third branch's parent.

---

## 4. Five defects the build itself exposed

Each was found by exercising the tool against a real repo or a real fixture, not by
re-reading it.

1. **`git multi-pack-index verify` exits 0 when there is no index at all.** A
   verify-only health check reported **PASS** on a store with none. Presence is now
   tested on the file; the verify is only the integrity check. The test
   `test_doctor_midx_absent_is_fail` builds a two-pack repo and asserts FAIL *and*
   asserts the verify alone returns 0 — the control for the defect.
2. **`MERGED` was unreachable.** The gate tested `ahead == 0` before
   `merge-base --is-ancestor`, and a merged branch always has zero commits ahead, so
   every merged branch was reported as "contained". Ancestry is now tested first.
3. **The planner replayed the base branch.** A chain that starts at the base
   produced `git replay --onto main main..main`, which fails on an empty range.
   The base is now excluded from its own plan.
4. **Two branches nominated each other as parent.** With both sides inferred by
   "closest merge-base", a stack produced `a→b` and `b→a`, and the cycle breaker
   dropped the wrong edge. The rule is now directional: a candidate must have moved
   *strictly less* since the fork point than the child.
5. **`git checkout -b` does not write "Created from"** — it writes
   `branch: Created from HEAD`, which resolves to nothing once HEAD moves. Reading
   only the documented form made every `checkout -b` stack look unrelated; both
   forms are parsed now, and the reflog is the highest-trust source because it is
   git's own record rather than an inference.
6. **`--task=loose-objects` does not reduce the loose-object count.** Measured:
   it packed copies of all 7,958 loose objects into a 32nd pack in 4.05 s
   (in-pack 30,854 → 38,812) and left every loose file exactly where it was —
   `count` stayed 7,958. The name of the task implies the opposite, and the
   doctor's own WARN recommended it as though it were the fix. Only a prune
   reclaims the 46 MiB, and `git prune` also deletes unreachable objects (dangling
   commits from aborted rebases), so the advice now names both halves and leaves
   the trade-off to the operator. **Not run here**: destroying recoverable history
   to save 46 MiB is not a decision a health check gets to make.
7. **A tool's verdict and the repo's state must be re-read after a fix.** After
   MIDX was written the doctor still said FAIL until the checks were re-evaluated;
   `--fix --apply` now re-runs the checks it targeted and reports the new state in
   the same run, so "applied" and "healthy" cannot drift apart.

---

## 5. Refinements, ranked

0. **Decide the 46 MiB.** 7,958 loose objects now also exist in pack 32; the only
   reclaiming step is a prune, which is destructive to unreachable history. Either
   accept the space or prune deliberately after checking `git fsck --unreachable`.
1. **Trial reftable on a copy.** `git init --ref-format=reftable` in a scratch clone,
   run the lane scripts, measure. Not worth switching at 13 refs; worth knowing
   before Git 3.0 makes it the default.
2. **Trial path-walk repack** (2.51) on the 939 MiB pack set — but note this disk is
   at 98% (18 GB free), so the repack needs headroom; `--repack` is opt-in in the
   doctor for exactly that reason.
3. ~~Wire `git_merge_gate.py --base origin/master` into the pre-commit hook~~ —
   **done differently, 2026-11-01**: wired into `.githooks/pre-push` instead. A merge
   conflict is a property of the pair (branch, remote tip) and moves when the other
   side moves, so per-commit re-answers the same question while the push is the
   moment the pair actually meets. Still open from this item: a merge-queue
   chainwise mode (item 5).
4. **`git maintenance start`** to schedule commit-graph/MIDX/loose-object refreshes
   instead of relying on `gc --auto` at 6,700 loose objects (currently 7,958 — over
   the threshold, so a gc is already pending).
5. ~~Merge queue semantics~~ — **done, 2026-11-01**: `--queue --branch a --branch b`
   judges each branch against the tree the ones ahead of it produced. The chain
   needs a commit per intermediate tree, so each clean step writes one dangling
   `git commit-tree` object (no ref, index or worktree touched; `git gc` collects
   them). It earns its keep on the two-branch fixture where both are CLEAN against
   the base and CONFLICT with each other, and on this repo's own queue, where
   `lane-813-recovery` conflicts on 3 paths with HEAD while being nothing special
   on its own. States: CLEAN / CONFLICTS / ALREADY-IN / ERROR / UNJUDGED — behind
   a stop, later branches are UNJUDGED, never clean.
6. **SHA-256 planning**: audit for 40-character assumptions (this repo has 8,372
   Python files, several of which hash strings). Nothing to change today; something
   to know before 3.0.

---

## 6. Reproduce

```bash
python tools/git_repo_doctor.py --bench                 # report + timings
python tools/git_repo_doctor.py --fix                   # show the writes (dry run)
python tools/git_repo_doctor.py --fix --apply --bench   # apply + measured delta

python tools/git_merge_gate.py --base origin/master      # every local branch
python tools/git_stack_plan.py                           # derived stacks
python tools/git_stack_plan.py --onto origin/master --check
python tools/git_stack_plan.py --onto origin/master --apply   # git replay

python -m pytest tests/test_git_tools.py -q
```
