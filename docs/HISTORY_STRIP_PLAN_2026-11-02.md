# History strip plan — the one blocker a commit cannot fix (2026-11-02)

Status: **PROPOSAL. Nothing here has been executed.** Sections 2 and 4 rewrite every
commit hash in this repository. That is irreversible in the sense that matters —
old SHAs stop resolving — so it needs the owner's explicit authorization, not an
agent's judgement.

## 1. Why no amount of new commits fixes this

GitHub's push is rejected by a pre-receive hook on **blob size**, not on tree size.
A normal `git push` uploads every object reachable from the refs it is given,
including blobs that were deleted from the working tree years ago. So the current
state of `archived/` is irrelevant: the bytes are already in the pack, and the hook
reads the pack.

Measured on this tree (2026-11-02):

| blob | size |
| --- | --- |
| `archived/2026-05-31/onnxruntime.tar.gz` | 272.339 MB |
| `archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz` | 228.847 MB |

Exactly 2 blobs exceed 50 MB; together 501.186 MB. The limit is **100 MB per file**;
both are 2.3× and 2.7× over it. `.git` is a **954.92 MiB** pack (32 packs, 38 812
objects), so even ignoring the limit the repository sits at GitHub's 1 GB
soft-warning line.

Consequences of the two routes people reach for first:

- **`git rm` and commit** removes the blob from `HEAD` only. It stays in history and
  the push still fails.
- **`.gitignore`** prevents future additions. It has no effect on existing objects.

The only three real options are: remove the objects from history (A), publish a
history that never contained them (B), or move the bytes to another store (C).

Same problem, smaller: gitleaks reports `generic-api-key` at
`archived/2026-05-31/onnxruntime-source/onnxruntime-1.18.0/onnxruntime/contrib_ops/cuda/bert/flash_attention/flash_api.cc:108`
(commit `0fb52604`). It is almost certainly a false positive in vendored third-party
CUDA source — but it is in history, so it is published by A/B/C alike unless that
path is stripped too. It is one more reason not to publish a vendored compiler tree.

## 2. Option A — rewrite history with `git filter-repo`

### 2.1 Backup first — this is the only undo

```bash
git clone --mirror C:/Azazael/azazael C:/Azazael/azazael-backup-2026-11-02.git
```

A mirror clone copies every ref, tag and object. Do not proceed if this command
fails, and do not treat a normal `git clone` as equivalent — it drops unmerged
branches and tags.

### 2.2 Install the tool

`git filter-repo` is not part of git. It also refuses to run on a repository with a
dirty working tree, so use a separate environment:

```bash
"C:/Azazael/.venvs/py315t/Scripts/python.exe" -m pip install git-filter-repo
```

### 2.3 What to strip

`archived/2026-05-31/` is not only the two tarballs. It contains:

```
archived/2026-05-31/dashboard.html
archived/2026-05-31/onnxruntime.tar.gz            <- 272.339 MB
archived/2026-05-31/onnxruntime-main/             <- vendored source tree
archived/2026-05-31/onnxruntime-source/           <- vendored source tree
archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz   <- 228.847 MB
archived/2026-05-31/onnxruntime_git/
```

**Recommended — strip the whole vendored directory** (removes both oversized blobs,
the 31.1 MB `coreml_Resnet50_ImageNet-dq.onnx`, and the gitleaks hit in one pass):

```bash
cd C:/Azazael/azazael
git filter-repo --invert-paths --path archived/2026-05-31/ --force
```

`dashboard.html` is collateral damage in this form. If it must survive, extract it
before the rewrite (`git show HEAD:archived/2026-05-31/dashboard.html > dashboard.html`)
and re-add it afterwards.

**Narrow alternative — strip only the two tarballs** (keeps the vendored trees and
the 31.1 MB `.onnx`, which is under the limit):

```bash
git filter-repo --invert-paths --force \
  --path archived/2026-05-31/onnxruntime.tar.gz \
  --path archived/2026-05-31/onnxruntime-source/onnxruntime.tar.gz
```

This leaves the gitleaks finding in history. Not recommended.

### 2.4 Reclaim the space (history rewrite alone does not shrink `.git`)

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git count-objects -vH          # expect size-pack near ~450 MiB
```

### 2.5 Restore the remote — `filter-repo` deletes it by design

```bash
git remote add origin C:/Users/clint/azazael
git push --force --all  origin
git push --force --tags origin
```

### 2.6 The honest cost

**Every commit hash from the first commit that touched `archived/2026-05-31/`
onward changes.** `archived/2026-05-31/` is a May-2026 path, so that is most or all
of the 151 commits, on all four local branches (`deepseek-engram-813 [renamed to azazael-intel-ultra-9-evo 2026-11-04]`,
`lane-813-recovery`, `migration/baseline-20261001`, plus the `origin/*` refs) and all
4 tags. `HEAD` is `58fe78a5` today; it will not be `58fe78a5` afterwards.

Anything outside git that recorded a SHA becomes a dangling reference — see §5.

## 3. Option B — publish a squashed snapshot (history untouched)

The local repository keeps its full archaeology; the public repository starts at one
commit that contains the tree as it is today.

```bash
cd C:/Azazael/azazael
git switch --orphan public-snapshot-2026-11-02
# stage by path, never `git add -A` -- the worktree carries ~200 unrelated
# modifications from other lanes
git add <explicit paths>
git commit -m "Public snapshot 2026-11-02"
```

Then create the GitHub repository and push that branch as `main`. `--orphan` is what
makes this cheap: no parent, so no reachable old blobs, so nothing over 100 MB and
nothing for gitleaks to trip over.

- **Public loses:** commit archaeology, per-file blame older than the snapshot, the
  four tags, and the other branches. Anyone auditing "how did this decision change"
  cannot.
- **Public keeps:** the entire current tree, the README/docs, the test suite, the
  licences, and a working `git log` from that point forward.
- **Local keeps:** everything, including the two tarballs, at zero cost.

The catches are real and worth naming: the snapshot commit is a single opaque
"everything at once", so the repo's own commit-message discipline (one coherent
changeset per commit, with a declared `ALLOW_BULK_COMMIT=1` when it is not) is
violated by construction; and a future `git pull --rebase` against the old local
branch will not line up with the snapshot history.

## 4. Option C — Git LFS: why it does not solve this

```bash
git lfs migrate import --everything --include="archived/2026-05-31/*.tar.gz"
```

This **also rewrites history** (it must, to replace the blobs with pointers), so it
carries every cost in §2.6. It additionally:

- uploads 501 MB against a 1 GB free LFS quota — it "works" and leaves no headroom;
- requires every clone to have `git-lfs` installed, or the checkout is silent
  pointer files;
- does not help at all if the migration is skipped: LFS only affects blobs committed
  *after* the pointer rules exist. The historical blobs still block the push.

So C is A with a quota bill attached. It is the right tool for a binary that must
stay in the tree; it is the wrong tool for a vendored compiler tarball that should
not be in the repository in the first place.

## 5. What breaks under A — in-repo SHA citations

Every one of these quotes a hash that will no longer resolve. Verified by reading
the files:

| file:line | cites |
| --- | --- |
| `docs/RESTART_HANDOFF_2026-11-02.md:4` | `7a6a2da3` ("its parent is `7a6a2da3`") |
| `docs/RESTART_HANDOFF_2026-11-02.md:8` | `a876c781` — pick-driven mutation, bible dossier, DJT audit |
| `docs/RESTART_HANDOFF_2026-11-02.md:9` | `0dbd384` — AI→SI decree |
| `docs/RESTART_HANDOFF_2026-11-02.md:10` | `ed96f5fe` — improvement pass |
| `docs/RESTART_HANDOFF_2026-11-02.md:11` | `7a6a2da3` — checks-and-balances gap analysis |
| `docs/agent_orders/03_lane_queue.md:42` | `69a48d7f` — what `tasks` returns and why |

`docs/agent_orders/03_lane_queue.md` is a **generated** file: the same
`commit 69a48d7f` line is stamped into `~/AGENTS.md:536` and
`~/.claude/CLAUDE.md:280` by `tools/agent_orders_sync.py`. Those two are outside the
repository and will not be regenerated by a history rewrite.

Outside git entirely, and therefore invisible to any rewrite:

- board rows and PMB/Engram activity records citing `eb10a862`, `0dbd384`,
  `1e8ce6f6`, `a876c781`, `69da48d7f` — the lane protocol requires evidence strings
  like `done <id> "<command + result>"`, and those strings already contain SHAs;
- `graphify-out/` reports carry a `built_at_commit` stamp.

**This table is a lower bound, not a census.** This worker has no terminal, so it
could not grep the whole repository; it read the files it could name. Run this
before committing to A, and expect more rows:

```bash
git grep -nE '\b[0-9a-f]{7,40}\b' -- '*.md' '*.json' \
  | grep -viE 'sha256|md5|fingerprint|integrity'
```

## 6. Recommendation

**Option A, stripping `archived/2026-05-31/` in full, and repairing §5 in the same
change.**

Reasoning, stated so it can be argued with:

- The blocker is a vendored ONNX Runtime compiler tree from 2026-05-31. It is not
  source this project wrote, it is not referenced by anything that runs, and it is
  501 MB of the 955 MB pack. Deleting it is a correct outcome on its own merits, not
  a concession to a host's limits — which is the test for whether a rewrite is worth
  its cost.
- A is the only option that keeps one public history, which is the thing the backlog
  and the docs both assume exists. B's single opaque commit forfeits exactly the
  archaeology that `docs/` spends its time citing, and it would immediately
  contradict every SHA in §5 anyway — the repair work is the same, so B pays the
  cost without the benefit.
- Once the vendored tree is gone, 955 MB becomes ~450 MB, which is inside the
  1 GB soft line with room for the 199 uncommitted changes to land.

If commit archaeology is not worth anything to the owner, **Option B is strictly
safer** and should be preferred — it touches nothing that already exists.

### Authorization

Section 2 changes every commit hash in the repository and cannot be undone except
from the mirror in §2.1. **The owner must authorize it explicitly.** This document
is the argument for the change, not consent to perform it.

### Prerequisite, independent of the option chosen

`git status` shows **199 uncommitted paths** (83 modified, 114 untracked, 2 deleted)
and `origin` points at a local path (`C:\Users\clint\azazael`), not GitHub. Neither
option addresses either fact. Publish in this order:

1. commit or explicitly park the 199 paths, in coherent slices, staging by path;
2. run the history strip (A) or create the orphan snapshot (B);
3. **then** create the GitHub repository and add the remote;
4. push, and confirm the size of what arrived rather than trusting the local count.
