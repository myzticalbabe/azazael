"""soul_fleet_reaper: delete merged remote branches, report unmerged ones.

The signal is merge-status, never age: a remote branch whose tip is
reachable from the default branch contains nothing that would be lost,
regardless of age; an unmerged branch may hold the only copy of real
work, regardless of staleness. (Two independent fleet writeups paid for
this lesson; cradle's stale dependabot branches paid for it here.)

Safety rules:
- DRY-RUN DEFAULT: without --reap nothing is deleted; the plan prints.
- NOTHING LOST: only branches `merge-base --is-ancestor` proves reachable
  from the default are reaped. Unmerged branches are NEVER deleted, only
  reported with committer, last date and unique-commit count.
- NEVER the default branch or the HEAD symref target, even if listed.
- SNAPSHOT FIRST: with --reap, a `reap-snap-<utc-ts>` tag lands in each
  touched repo before any deletion (deleted tips stay reachable locally
  until gc; the tag names the restore point).
- FETCH FIRST: `git fetch --prune origin` refreshes tracking refs so the
  merged check reads the live remote, not a stale cache. A repo whose
  fetch fails is skipped with the reason recorded, never judged blind.

Usage:
  python tools/soul_fleet_reaper.py --root <fleet-root> [--reap]
      [--keep <regex>]... [--json <out.json>]

Exit: 0 ran with no UNMERGED branches needing a human,
      1 unmerged branches remain (decisions for a human),
      2 bad inputs / nothing reapable scanned.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git(args: list[str], cwd: Path, timeout: int = 180) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True,
            timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, f"git failed: {exc}"
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


def remote_heads(path: Path) -> tuple[list[str], str]:
    """(branch names incl. 'HEAD-target' knowledge, default branch or '')."""
    rc, out = run_git(["ls-remote", "--symref", "origin", "HEAD"], path)
    default = ""
    for line in out.splitlines():
        if line.startswith("ref:"):
            ref = line.split()[1]
            if ref.startswith("refs/heads/"):
                default = ref[len("refs/heads/"):]
    rc2, out2 = run_git(["ls-remote", "--heads", "origin"], path)
    heads = []
    if rc2 == 0:
        for line in out2.splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1].startswith("refs/heads/"):
                heads.append(parts[1][len("refs/heads/"):])
    return heads, default


def is_merged(path: Path, branch: str, default: str) -> bool:
    rc, _ = run_git(["merge-base", "--is-ancestor",
                     f"origin/{branch}", f"origin/{default}"], path)
    return rc == 0


def branch_info(path: Path, branch: str, default: str) -> dict:
    rc, out = run_git(["log", "-1", "--format=%ci|%an",
                       f"origin/{branch}"], path)
    parts = (out.split("|") + ["?", "?"])[:2] if rc == 0 else ["?", "?"]
    last, who = parts
    rc2, out2 = run_git(["rev-list", "--count",
                         f"origin/{default}..origin/{branch}"], path)
    unique = out2.strip() if rc2 == 0 else "?"
    return {"branch": branch, "last_commit": last, "author": who,
            "unique_commits": unique}


def reap_repo(path: Path, keep: list[str], do_reap: bool) -> dict:
    """Scan one repo. Never raises; failures are recorded in the result."""
    result: dict = {"repo": path.name, "merged": [], "unmerged": [],
                    "skipped": "", "reaped": [], "snapshot": ""}
    if not ((path / ".git").is_dir() or (path / "HEAD").is_file()):
        result["skipped"] = "not a repo dir"
        return result
    rc, out = run_git(["fetch", "--prune", "origin"], path)
    if rc != 0:
        result["skipped"] = f"fetch failed: {out[:200]}"
        return result
    heads, default = remote_heads(path)
    if not default:
        result["skipped"] = "remote default unknown (empty ls-remote?)"
        return result
    keep_res = [re.compile(k) for k in keep]
    for branch in sorted(heads):
        if branch == default:
            continue
        if any(rx.search(branch) for rx in keep_res):
            continue
        if is_merged(path, branch, default):
            result["merged"].append(branch)
        else:
            result["unmerged"].append(branch_info(path, branch, default))
    if do_reap and result["merged"]:
        tag = "reap-snap-" + datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ")
        rc, out = run_git(["tag", tag], path)
        if rc != 0:
            result["skipped"] = f"snapshot tag failed: {out[:200]}"
            result["merged"] = []
            return result
        result["snapshot"] = tag
        for branch in list(result["merged"]):
            rc, out = run_git(["push", "origin", "--delete", branch], path)
            if rc == 0:
                result["reaped"].append(branch)
            else:
                result["unmerged"].append(
                    {"branch": branch, "last_commit": "?",
                     "author": "?", "unique_commits": "?",
                     "note": f"delete failed: {out[:200]}"})
        result["merged"] = [b for b in result["merged"]
                            if b not in result["reaped"]]
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Reap merged remote branches.")
    ap.add_argument("--root", required=True)
    ap.add_argument("--reap", action="store_true")
    ap.add_argument("--keep", action="append", default=[])
    ap.add_argument("--repos", nargs="*", default=None)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"reaper: no root {root}", file=sys.stderr)
        return 2
    names = args.repos
    if names is None:
        names = sorted(p.name for p in root.iterdir()
                       if p.is_dir() and not p.name.startswith("."))
    results = [reap_repo(root / n, args.keep, args.reap) for n in names]
    if not results:
        print("reaper: no repos scanned")
        return 2

    n_reaped = sum(len(r["reaped"]) for r in results)
    n_unmerged = sum(len(r["unmerged"]) for r in results)
    for r in results:
        bits = []
        if r["skipped"]:
            bits.append(f"SKIPPED: {r['skipped']}")
        if r["merged"]:
            bits.append(f"MERGED-safe: {', '.join(r['merged'])}")
        if r["reaped"]:
            bits.append(f"REAPED (snapshot {r['snapshot']}): "
                        f"{', '.join(r['reaped'])}")
        for u in r["unmerged"]:
            bits.append(f"UNMERGED kept: {u['branch']} "
                        f"({u['unique_commits']} unique, "
                        f"{u['last_commit']} {u['author']})")
        if bits:
            print(f"{r['repo']}:")
            for b in bits:
                print(f"  - {b}")
    print(f"{len(results)} repo(s), {n_reaped} reaped, "
          f"{n_unmerged} unmerged kept, "
          f"{'REAPED' if args.reap else 'PLANNED'}")
    if args.json:
        Path(args.json).write_text(json.dumps({"results": results}, indent=2),
                                    encoding="utf-8")
    return 1 if n_unmerged else 0


if __name__ == "__main__":
    raise SystemExit(main())
