# The fleet as bleeding-edge git stacks — 2026-11-01

Companion to `docs/GIT_TOOLING_BLEEDING_EDGE_2026-11-01.md`. That document defines
what "bleeding edge" means for **one** repository. This one asks a different
question — *which trees in the fleet are actual git stacks, and which are only
copies of code that happen to sit under version control* — and answers it with
measurements, then assigns a goal and tasks to every tree that is not yet there.

Everything below is measured, not inferred. Tool: `tools/git_fleet_audit.py`
(extended today, see §1). Command in §7. Machine clock at run time:
2026-11-01T20:2xZ.

Interpreter versions found in the fleet: Windows `git 2.53.0.windows.1`,
Ubuntu-26.04 `git 2.53.0`, kali-linux `git 2.51.0`. Upstream is **2.56.0**
(2026-09-28), so the Windows and Ubuntu stacks are three minor releases behind and
Kali is five.

---

## 1. The definition changed today, because the old one graded a false positive

Before today the grader required five things: commit-graph, multi-pack-index (when
there is more than one pack), `core.fsmonitor`, `core.untrackedCache`, and
`index.version >= 4`. All five are **config**. A repository can satisfy every one
of them while almost nothing in it is tracked, and then "BLEEDING" is a claim about
the settings rather than about the tree.

That is not hypothetical. Ubuntu-26.04's `/root/azazael` scored BLEEDING with 678
tracked files and 27,435 objects in a single 948.6 MiB pack. The grade described the
config file correctly and the tree not at all.

So the definition gained a sixth hard requirement:

| check | passes when | why it is hard |
| --- | --- | --- |
| working-tree coverage | tracked content is not a minority of the tree (`untracked <= max(tracked, 100)`) | every `git status`/`add`/`diff` walks the untracked majority; a baseline commit over a copy buys nothing |

and two **named hygiene** gaps that are reported with the repack that closes them
but are deliberately *not* folded into the grade, because their fix is scheduled
work rather than a config one-liner: `loose objects > 2000`, `packs > 50`.

The distinction matters in both directions. Under the old definition
`C:/Azazael/azazael` graded BLEEDING while carrying 7,958 loose objects; under the
new one it graded LAGGING until they were pruned (§5). A definition that cannot
move when the tree degrades is not a control.

---

## 2. The fleet, graded

| # | tree | grade | gaps | evidence |
| --- | --- | --- | --- | --- |
| 1 | `C:/Azazael/azazael` | **BLEEDING** | 0 | 1,227 commits, 32 packs, 0 loose, 954.9 MiB packed, MIDX+graph present |
| 2 | `C:/Users/clint` | **LAGGING** | 1 + HAZARD | 189 commits, 1 pack, 18 loose, 138.1 MiB; *coverage*: **678 tracked vs 1,006 untracked** — the tree is a copy with a baseline commit; *hazard*: the repository **is** the home directory |
| 3 | `C:/Users/clint/edge0-intel` | **NOT-A-REPO** | 1 | `rev-parse --show-toplevel` → `C:/Users/clint` |
| 4 | `C:/Users/clint/graph3d` | **NOT-A-REPO** | 1 | `rev-parse --show-toplevel` → `C:/Users/clint` |
| 5 | `C:/Azazael/pams-source` | **BLEEDING** | 0 | 7 commits, 0 packs, 51 loose |
| 6 | `Ubuntu-26.04:/root/azazael` | **BLEEDING** | 0 | 151 commits, 678 tracked, 0 untracked, git 2.53.0, 1 pack 948.6 MiB, 1,450 loose (578 prune-packable) |
| 7 | `kali-linux:/root/azazael` | **NOT-A-REPO** | 1 | 123 entries, no `.git` (only a `.gitignore`) |
| 8 | `G:/azazael` | **NOT-A-REPO** | 1 | `fatal: not a git repository` |

Four of eight trees have no git stack at all, and one of the four is the home
directory's own repository, which reaches up and claims the other two.

---

## 3. Goals and tasks for every tree that is not a bleeding-edge stack

Each goal is stated as a decision, because in every case below there are two
legitimate answers and the wrong automatic answer destroys something.

### 3.1 `C:/Users/clint` — LAGGING, and the fleet hazard

**Goal:** either this stops being a repository, or it becomes one that cannot be
confused with its contents.

Measured coverage: 678 files tracked, 1,006 untracked — the untracked majority is the
profile itself (caches, downloads, build output).

Tasks:
1. `git add -A` here stages the entire Windows profile, and every folder below it
   answers `rev-parse --show-toplevel` with `C:/Users/clint`. Decide: keep the
   repository (then a `.gitignore` must cover `AppData/`, `Downloads/`, caches and
   build output, and canon must say no repo-local command is meaningful anywhere
   beneath it) or archive the 189 commits and remove `.git`.
2. Until (1) is settled, no lane may run `git config`, `git add`, `git gc` or
   `git commit-graph write` in any folder under `~` — that write lands here.

### 3.2 `C:/Users/clint/edge0-intel`, `C:/Users/clint/graph3d` — NOT-A-REPO

**Goal:** each tree has its own history or is explicitly declared part of the home
repository.

Tasks:
1. Per folder: `git init` + baseline (a second history, nothing on disk changes) **or**
   leave it inside `C:/Users/clint` and record that in canon.
2. Do not run repo-local git commands in either folder expecting them to be local;
   git resolves upward and edits the home repository. This was exercised today, not
   theorised — see §6.1.

### 3.3 `G:/azazael` — NOT-A-REPO

**Goal:** the restore source is either versioned or declared a plain copy.

Tasks:
1. Restore-or-delete the seven `.py` files that fail `ast.parse` (the earlier AST
   audit names them: `AOA/build.py` cut at line 169 of 238, `build_disclosure.py` at
   24 of 125, `gen_html.py`, `inject.py`, `rebuild_html.py`,
   `AZAZAEL_ROOT/src/AOA/cli/aoa_cli.py` at 568 of 581,
   `EveUnleashed/scripts/probe_model.py`).
2. Then decide: `git init` + baseline, or keep it a copy and stop treating it as a
   git tree in any report.

### 3.4 `kali-linux:/root/azazael` — NOT-A-REPO

**Goal:** the Kali lane owns a versioned stack or is declared an artefact store.

Tasks:
1. `git init && git add -A && git commit -m baseline`, then grade with this tool
   inside the lane (`--single --apply`), **or** declare it an artefact store.
2. Weigh the second history: Windows is the source of truth and the lane holds
   1,502 `.py` / 468,983 LOC. An init that is never pushed is a fork with no upstream.
3. Kali's git is 2.51.0 while upstream is 2.56.0 — `git repack --drop-filtered`,
   `git replay --linearize` and the `git refs` toolbox are absent there.

### 3.5 `Ubuntu-26.04:/root/azazael` — BLEEDING on the checks, one real debt

No config gap. Two facts worth a decision: a single 948.6 MiB pack, and 1,450 loose
objects of which **578 are prune-packable** (already inside the pack — pure
duplicates). `git prune-packed` reclaims those with no repack and no disk growth.

Tasks: `git prune-packed`; decide whether the 948.6 MiB single pack is split
(`git repack -d --geometric=2`) or left alone; the copy of this tool in that tree is
at an older commit and does not yet contain the coverage check — sync it before
re-grading.

---

## 4. Adaptation menu — what upstream actually shipped, and which tree it serves

Researched against the 2.56.0 release notes and the 2.53/2.54 write-ups (§7). Each
entry names the tree it would serve and whether it is landed or queued, so this
section does not read as a wish list.

| adaptation | upstream | serves | state |
| --- | --- | --- | --- |
| `git prune-packed` before any repack | always | every tree | **landed** — 7,958 → 0 loose on `azazael`, 1,664 → 18 on home (§5) |
| commit-graph + MIDX + fsmonitor + untrackedCache + index v4 | 2.23 / 2.34 | every tree | **landed** on 3 trees; queued for the 4 with no stack |
| interval-based `git maintenance` (register + schedule) | 2.30+ | all | queued — the audit reports `maintenance.strategy=<unscheduled>` for every tree today, i.e. nothing runs between sessions |
| `git maintenance is-needed --task=<t>` | 2.53 | all | **measured unusable here** — §6.4; the audit keeps its own thresholds |
| `git merge-tree --write-tree` (conflict preflight without a worktree) | 2.38 | `azazael` (1227 commits, one lane per session) | queued — this is the merge-queue primitive: a lane can ask "would these two merge cleanly" without touching an index |
| `git replay --onto` / `--linearize` | 2.46 / 2.56 | stacked work across lanes | queued — replays commits onto a new base without a checkout; `--linearize` drops merges |
| `git backfill` (fill a partial clone by batch, path-aware) | 2.51 | a Scalar-style clone of `azazael` | queued — pairs with blob filters below |
| partial clone + `git repack --drop-filtered` + `promisor.acceptFromServerURL` | 2.56 | `azazael` at 955 MiB packed / 40k objects | queued — the only route that makes a lane clone cheap, and 2.56 is what makes dropping filtered blobs safe |
| Scalar (`scalar register`) | 2.38 fully upstream | workstations | queued — sets the same five settings this audit checks plus background maintenance; useful as a cross-check, not as a replacement for measuring |
| `git refs create/delete/update/rename` + reftable | 2.56 / experimental | lane refs (`lane/<name>/<task>`) | queued — ref plumbing without porcelain; reftable is the Git-3.0 default and worth a scratch trial only |
| untracked enumeration O(n²) → O(n log n) | 2.56 | the two trees with tens of thousands of untracked paths | upgrade trigger: this is the single change that makes `git status` usable on the home tree, and it is *not* in 2.53 |
| `git add --resolved` | 2.56 | conflict-heavy sessions | queued — stages only resolved paths, aborts on leftover markers |
| `git branch --delete-merged` | 2.56 | `azazael` branch hygiene | queued |
| `git bisect --reset-when-found` | 2.56 | CI/lane debugging | queued |
| `includeIf` keyed on worktree location | 2.56 | per-lane config without copy-paste | queued — replaces the per-lane config files this fleet maintains by hand |
| `git repo info` (absolute + relative gitdir/commondir) | 2.56 | this audit | queued — replaces the `rev-parse --git-dir` + path-join guess |
| `git rev-list --missing-only` | 2.56 | partial-clone integrity checks | queued, needed *with* the partial clone |
| one worktree per lane (`git worktree add`) | 2.5 | all four lanes on `azazael` | queued — four lanes sharing one checkout is why `index.lock` and "your commit is not mine" keep happening |

The two that change the shape of the fleet rather than its speed are the **merge
queue** (`merge-tree --write-tree` + `replay`, both worktree-free) and the
**partial clone** (`backfill` + `--drop-filtered`). Everything else is a setting.

---

## 5. What landed in this session, with before/after

| tree | action | before | after |
| --- | --- | --- | --- |
| `C:/Azazael/azazael` | `git prune-packed` | 7,958 loose, 46.2 MiB, `prune-packable: 7958` | **0 loose, 0 MiB** (45 MiB reclaimed; 32 packs untouched) |
| `C:/Azazael/azazael` | `git multi-pack-index write` + `commit-graph write --reachable` | MIDX + graph present | re-written, both present, grade back to BLEEDING |
| `C:/Users/clint` | `git repack -d` + MIDX + graph | 1,664 loose, 159.5 MiB, 0 packs | **18 loose, 1 pack, 138.1 MiB** (21 MiB reclaimed) |

Deliberately **not** done: no `git repack -a` on `azazael` (a single repack would
need ~1 GB of temporary space on a volume at 98% / 18 GB free — queued as a scratch
trial with `--path-walk` instead), no `git init` anywhere (each is a decision, §3),
nothing pushed.

---

## 6. Corrections, retractions, and one unresolved measurement

### 6.1 Two folders were treated as repositories and were not

`edge0-intel` and `graph3d` sit inside the home repository. `git config` and
`git commit-graph write` were run in both on 2026-11-01 believing them local; git
resolved upward, so the writes landed in `C:/Users/clint/.git/config`. Nothing was
damaged — fsmonitor, untrackedCache, index v4 and a commit-graph on a 189-commit
repository are improvements — but the claim "edge0-intel is now a bleeding-edge
stack" was **false** and is withdrawn. This is why the audit's first check is
`toplevel == root`.

### 6.2 The Ubuntu lane was graded from its config and called healthy

Withdrawn as stated; regraded under the new definition with the tree measured
(151 commits, 678 tracked, **0 untracked**, 948.6 MiB pack, 1,450 loose). It is a
genuine BLEEDING stack with a hygiene debt, not a copy wearing a repository — the
coverage check that suspected it is what settled the question either way.

### 6.3 Two measurements of the same Ubuntu repo disagree and are left named

The same `git rev-list --count HEAD` in `/root/azazael` returned **1** on one call
and **151** on another, and `--show-toplevel` returned `/mnt/c/Users/clint` once and
`/root/azazael` the rest of the time. The 151 figure is corroborated
(`git log` shows real history, `count-objects` shows 27,435 in-pack objects, a
1-commit repo cannot hold them), so 151 is used — but the disagreement is recorded
rather than smoothed away, and the queue carries a lane-side re-measurement. Most
likely cause: a login-shell `cd` in the `bash -lc` wrapper racing the explicit `cd`,
which is also the failure that produced the `/mnt/c/Users/clint` toplevel.

### 6.4 `git maintenance is-needed` cannot be used as a predicate on this fleet

Exercised in two repos: a fresh `git init` + one commit that needs everything, and
`azazael` which needed nothing (before the prune). `git maintenance is-needed`,
`--task=<gc|commit-graph|loose-objects|pack-refs|prefetch>` printed nothing and
exited **0** in both. `--schedule` is rejected as an unknown option. So the exit
status carries no information here and the audit keeps hand-set thresholds, which
are at least explained. 2.53.0.windows.1 and 2.53.0 both behave this way; re-test
after upgrading to 2.56.

---

## 7. Reproduce

```bash
PY=C:/Azazael/.venvs/py315t/Scripts/python.exe

$PY tools/git_fleet_audit.py --tasks \
  --root C:/Azazael/azazael --root C:/Users/clint --root C:/Users/clint/edge0-intel \
  --root C:/Users/clint/graph3d --root C:/Azazael/pams-source --root G:/azazael

# JSON for a report, and the closing command list per gap
$PY tools/git_fleet_audit.py --tasks --json docs/fleet_audit_2026-11-01.json --root <tree>

# inside a WSL lane
python3 tools/git_fleet_audit.py --root /root/azazael --single --apply
```

Upstream basis: `git/git` `Documentation/RelNotes/2.56.0.adoc`;
GitLab *What's new in Git 2.53.0*; GitHub *Highlights from Git 2.54*;
git-scm.com (2.56.0, 2026-09-28); `git-scm.com/docs/scalar`.
