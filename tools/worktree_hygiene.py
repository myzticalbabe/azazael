"""worktree_hygiene.py -- hygiene scanner + safe backup for the repos on this box.

Reads box_trees.json (or scans --repos roots) and reports per repo:
  branch, upstream, ahead/behind (vs last-known remote, NO fetch),
  tracked-dirty count, untracked count, and a suggested action.

Flags: NO-UPSTREAM, UNPUSHED, BEHIND, DIVERGED, DIRTY, UNTRACKED,
       DUP-REMOTE (two checkouts, same origin, different HEAD).

  --bundle DIR   write `git bundle create` backups for every repo with
                 ahead>0 (keep-local stacks). Non-destructive, additive.
  --json         machine-readable output.

Exit 0 always unless the inventory cannot be read (exit 2, never a pass-lie).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from CORE.failure_ledger import note_failure
except ImportError:  # never break the host
    def note_failure(where, exc=None):
        pass


def _run(cmd, cwd, timeout=30):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception as exc:
        note_failure("tools/worktree_hygiene._run", exc)
        return None


def inspect_repo(path):
    info = {"path": str(path)}
    info["branch"] = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], path)
    info["head"] = _run(["git", "rev-parse", "HEAD"], path)
    info["origin"] = _run(["git", "remote", "get-url", "origin"], path)
    info["upstream"] = _run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name",
         "@{upstream}"], path)
    if info["upstream"]:
        cnt = _run(["git", "rev-list", "--left-right", "--count",
                    "HEAD...@{upstream}"], path)
        try:
            fwd, back = (int(x) for x in cnt.split())
        except (ValueError, AttributeError) as exc:
            note_failure("tools/worktree_hygiene.aheadbehind", exc)
            fwd, back = 0, 0
        info["ahead"], info["behind"] = fwd, back
    else:
        info["ahead"], info["behind"] = 0, 0
    dirty, untracked, paths = 0, 0, []
    try:
        r = subprocess.run(["git", "status", "--porcelain"], cwd=path,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if line.startswith("??"):
                    untracked += 1
                else:
                    dirty += 1
                if len(paths) < 8:
                    paths.append(line.strip())
    except OSError as exc:
        note_failure("tools/worktree_hygiene.status", exc)
    info["dirty"], info["untracked"], info["sample"] = dirty, untracked, paths
    flags = []
    if not info["origin"]:
        flags.append("NO-UPSTREAM")
    if info["ahead"] and info["behind"]:
        flags.append("DIVERGED")
    elif info["ahead"]:
        flags.append("UNPUSHED")
    elif info["behind"]:
        flags.append("BEHIND")
    if dirty:
        flags.append("DIRTY")
    if untracked:
        flags.append("UNTRACKED")
    info["flags"] = flags
    if "DIVERGED" in flags:
        info["action"] = "STOP: diverged, needs a human merge plan, never silent"
    elif "NO-UPSTREAM" in flags:
        info["action"] = "decide remote (create private repo or archive), then push"
    elif "UNPUSHED" in flags:
        info["action"] = "bundle backup, then push-to-fork / PR / keep-local+record"
    elif "BEHIND" in flags:
        info["action"] = "ff-pull if clean, else pin with reason"
    elif "DIRTY" in flags or "UNTRACKED" in flags:
        info["action"] = "review sample, commit by pathspec or document keep-dirty"
    else:
        info["action"] = "clean"
    return info


def find_dups(repos):
    by_origin = {}
    for r in repos:
        if r.get("origin"):
            key = r["origin"].strip().lower().rstrip(".git")
            by_origin.setdefault(key, []).append(r)
    for key, group in by_origin.items():
        heads = {g.get("head") for g in group}
        if len(group) > 1 and len(heads) > 1:
            for g in group:
                if "DUP-REMOTE" not in g["flags"]:
                    g["flags"].append("DUP-REMOTE")
                    g["action"] = ("same origin, different HEAD than sibling "
                                   "checkout; pick canonical, never delete blind")


def bundle_repo(path, dest_dir):
    dest_dir = Path(dest_dir)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        note_failure("tools/worktree_hygiene.bundle_mkdir", exc)
        return None
    name = os.path.basename(os.path.abspath(path)) + ".bundle"
    dest = dest_dir / name
    try:
        r = subprocess.run(["git", "bundle", "create", str(dest), "--all"],
                           cwd=path, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        if r.returncode == 0 and dest.exists():
            return str(dest)
        note_failure("tools/worktree_hygiene.bundle",
                     RuntimeError(r.stderr.strip()[:200]))
        return None
    except OSError as exc:
        note_failure("tools/worktree_hygiene.bundle", exc)
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", default=str(
        Path.home() / "yggdrasil_forest" / "box_trees.json"))
    ap.add_argument("--repos", nargs="*", default=[],
                    help="explicit repo paths (skip inventory)")
    ap.add_argument("--bundle-dir", default=None,
                    help="write git bundles for ahead>0 repos here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.repos:
        paths = args.repos
    else:
        try:
            with open(args.inventory, encoding="utf-8") as fh:
                inv = json.load(fh)
            paths = [t["path"] for t in inv.get("trees", [])
                     if t.get("kind") == "git"]
        except (OSError, ValueError) as exc:
            note_failure("tools/worktree_hygiene.inventory", exc)
            print(f"cannot read inventory {args.inventory}: {exc}",
                  file=sys.stderr)
            return 2

    repos = [inspect_repo(p) for p in paths if os.path.isdir(p)]
    find_dups(repos)
    if args.bundle_dir:
        for r in repos:
            if r["ahead"] > 0:
                dest = bundle_repo(r["path"], args.bundle_dir)
                r["bundle"] = dest or "FAILED"

    if args.json:
        print(json.dumps({"repos": repos}, indent=1))
    else:
        for r in repos:
            print(f'{r["path"]} | br={r["branch"]} up={r["upstream"]} '
                  f'ab={r["ahead"]}/{r["behind"]} '
                  f'dirty={r["dirty"]} untracked={r["untracked"]} '
                  f'[{" ".join(r["flags"]) or "CLEAN"}] -> {r["action"]}'
                  + (f' | bundle={r["bundle"]}' if r.get("bundle") else ""))
        flagged = sum(1 for r in repos if r["flags"])
        print(f"\n{len(repos)} repos, {flagged} flagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
