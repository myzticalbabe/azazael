# BM Ubuntu supersede runbook (bare-metal replay, FREEBUFF LANE ONLY)

> Sole execution authority: the freebuff lane. This brief binds to exactly
> one lane and one worktree; no BM lane exists for this work, no handoff
> is written, and pushing any step to another lane is forbidden. The
> freebuff lane claims it, executes it on the BM boot, verifies it, and
> retires it. One lane executing this brief, never two.
>
> Same tool, same doctrine as WSL. BM is a third estate: do NOT reuse WSL
> captures. Every number below must be re-measured on BM.

## 0. Preconditions (all must hold)

- Freebuff lane claims this brief first:
  `python C:/Users/clint/_board.py claim freebuff` (never work unclaimed).
- Bare-metal Ubuntu boots, network up, `python3.14t` present at the same
  `/usr/local/bin/python3.14t` path (or adjust paths below).
- `tools/env_supersede.py` synced from this repo at the committed revision.
- A capture dir, e.g. `/tmp/bm_pkg/`, writable.

## 1. Capture (BM-owned, live)

```bash
CAP=/tmp/bm_pkg; TOOLS=<repo>/tools/bm_capture
mkdir -p $CAP
apt list --installed > $CAP/apt_installed.txt
apt-mark showmanual > $CAP/apt_manual.txt
python3 $TOOLS/probe_pip.py > $CAP/pip_14t.txt
python3 $TOOLS/probe_tree.py <repo-checkout> > $CAP/tree_imports.json
python3 $TOOLS/probe_revdeps.py > $CAP/revdeps.json
python3 $TOOLS/probe_env.py entry_points > $CAP/entry_points.json
python3 $TOOLS/probe_env.py locations > $CAP/locations.json
```

Probes are committed in `tools/bm_capture/` (stdlib only, 3.8+; proven on
3.16t/3.14t/3.15t). `locations.json` is REQUIRED: without it the tool
falls back to legacy behavior and SYSTEM-owned dists become pip
candidates (this deleted files out from under 80 apt packages on Kali;
repaired via reinstall). `tree_imports.json` needs the repo checkout path
as its argument (what the BM lane actually imports).

## 2. Classify (dry run, no changes)

```bash
python tools/env_supersede.py --captures /tmp/bm_pkg --check
```

Expect: `keep=N remove=M` lines plus the reason for every REMOVE.
`remove=0` on a fresh estate means steady state; anything listed is a
candidate with its evidence attached.

## 3. Review gates (human, before any uninstall)

1. Every apt REMOVE has clean `rdepends` AND an absorber named.
2. Every pip REMOVE is ENV-located (check `locations.json`, never assume).
3. No baseline/toolchain/self dist in any REMOVE list.
4. Recon/dev CLIs (`nxc`, `bloodhound-python`, build tools) smoke-tested
   AFTER, not before.

## 4. Execute (scripts, file-based, never inline quoting)

```bash
python tools/env_supersede.py --captures /tmp/bm_pkg \
  --emit-manifest docs/BM_SUPERSEDE_MANIFEST.md \
  --emit-script scripts/bm_shrink.sh
bash scripts/bm_shrink.sh   # apt side, review first
# pip side: uninstall listed orphans one tool run at a time
```

## 5. Verify (each claim carries its command)

- `apt-get check && dpkg --audit` -> clean (no output).
- `dpkg -V` over `python3*` -> zero `missing` lines.
- Re-run `--check` -> `remove=0` (steady state).
- Import + CLI smoke through the touched paths.

## 6. Record and retire (freebuff lane closes its own brief)

- Append an execution record to the BM manifest (before/after counts,
  repair if any, smoke commands + results).
- Bake rows at encounter time into `state/bake_harvest_bm_<date>.jsonl`;
  validate with `tools/merge_bake_lane.py --lane <file> --apply`.
- Commit by path (`<=8` files, new files exempt from the line cap);
  read `git show --stat HEAD` back.
- Retire the board row in the same turn:
  `python C:/Users/clint/_board.py done <id> "<command + result>"`
  or `block <id> "<exact blocker>"`. A claim the freebuff lane cannot
  retire did not happen. Never hand the row to another lane.
