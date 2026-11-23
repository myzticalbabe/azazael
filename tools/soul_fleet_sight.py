#!/usr/bin/env python3
"""Soul fleet sight -- the eyes the 2026-11-23 hygiene round proved missing.

Every deficiency closed that day was invisible to the existing instruments
until a human tripped over it:

  unlanded fix     forensics carried a complete licence remediation as
                   ` M` lines while every committed-tree scan read clean.
  false DIRTY      core.autocrlf smudged a byte-identical REUSE.toml as
                   forever-modified; status said M, diff said nothing.
  dead origin      vermillion's origin was a WSL-only path -- pushes failed
                   from Git Bash while the worktree read healthy.
  blind tracking   ten repos resolved `@{u}` to nothing, so ahead/behind
                   was unknowable (not zero -- unknowable).
  stale heads      Eve carried master + fb + a graph-regen branch next to
                   a converged main; nothing counted heads.
  blind monitor    the sweep's own scheduler result was unreadable from the
                   CLI the operator actually uses.

Sight answers all six with git truth only -- no filename heuristics, no
content scans, nothing the vermillion false-positive could recur in. It is
the daily lens; the licence sweep stays the weekly corrective leg.

Legs per repo:
  DIRTY            `git status --porcelain` non-empty (with the count).
  SYNC             ahead/behind vs @{u}; NO-UPSTREAM when it unresolvable;
                   AHEAD(n)/BEHIND(n) findings. A repo with no `origin`
                   remote at all is NO-ORIGIN (nothing can land it).
  ORIGIN           `git ls-remote origin HEAD`: rc != 0 is
                   UNREACHABLE-ORIGIN with the configured URL named.
  DEFAULT          remote default (fetch-fresh ls-remote --symref, local
                   symref fallback) vs checked-out branch: DEFAULT-MISMATCH
                   names both sides.
  HEADS            remote head count, info only -- feature branches are
                   legitimate; the daily reading makes stale ones visible.

Box legs (once per run):
  SCHED            SoulFleetSweep's LastTaskResult (Windows task scheduler;
                   SKIP with reason elsewhere). Non-zero is SCHED-FAIL --
                   the monitor reporting red is itself a finding.

Usage:
    python tools/soul_fleet_sight.py [--root C:/Azazael] [--json out.json]
    python tools/soul_fleet_sight.py --root <dir> --repos a,b,c  # subset

Exit status: 0 sight clean, 1 any finding, 2 no root.
A scheduled/manual leg, never a commit-hook gate.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from tools.soul_fleet_sweep import (  # noqa: E402
        parse_lsremote_default,
        remote_default_branch,
        run,
    )
except ImportError:  # standalone: python tools/soul_fleet_sight.py
    from soul_fleet_sweep import (  # noqa: E402
        parse_lsremote_default,
        remote_default_branch,
        run,
    )

SIGHT_TASK = "SoulFleetSweep"


def sight_repo(path: Path) -> dict:
    """One repo, git truth only. Every subprocess bounded (see run())."""
    entry: dict = {
        "path": path.name, "branch": None, "dirty": 0,
        "ahead": None, "behind": None, "upstream": None,
        "origin_ok": None, "origin_url": None,
        "origin_default": None, "heads": None, "findings": [],
    }
    rc, out = run(["git", "branch", "--show-current"], path)
    entry["branch"] = out.strip() or None

    rc, out = run(["git", "status", "--porcelain"], path)
    if rc == 0:
        dirty = [ln for ln in out.splitlines() if ln.strip()]
        entry["dirty"] = len(dirty)
        if dirty:
            entry["findings"].append(
                "DIRTY: %d uncommitted path(s)" % len(dirty))

    rc, out = run(["git", "remote", "get-url", "origin"], path)
    url = out.strip() if rc == 0 else None
    entry["origin_url"] = url
    if not url:
        entry["findings"].append("NO-ORIGIN: no origin remote; nothing can land")
        return entry

    rc, out = run(["git", "ls-remote", "origin", "HEAD"], path)
    if rc != 0:
        entry["origin_ok"] = False
        entry["findings"].append(
            "UNREACHABLE-ORIGIN: %s (%s)" % (url, out.strip()[:120]))
    else:
        entry["origin_ok"] = True

    default, _src = remote_default_branch(path)
    entry["origin_default"] = default
    if default and entry["branch"] and default != entry["branch"]:
        entry["findings"].append(
            "DEFAULT-MISMATCH: local %s vs remote default %s"
            % (entry["branch"], default))

    rc, out = run(["git", "rev-list", "--count", "HEAD..@{u}"], path)
    if rc != 0:
        entry["upstream"] = None
        entry["findings"].append(
            "NO-UPSTREAM: @{u} unresolvable; ahead/behind unknowable, not zero")
    else:
        behind = int(out.strip())
        rc2, out2 = run(["git", "rev-list", "--count", "@{u}..HEAD"], path)
        ahead = int(out2.strip()) if rc2 == 0 else 0
        entry["behind"], entry["ahead"] = behind, ahead
        entry["upstream"] = True
        if behind:
            entry["findings"].append("BEHIND: %d commit(s) unpulled" % behind)
        if ahead:
            entry["findings"].append("AHEAD: %d commit(s) unpushed" % ahead)

    rc, out = run(["git", "ls-remote", "--heads", "origin"], path)
    if rc == 0:
        heads = [ln for ln in out.splitlines() if ln.strip()]
        entry["heads"] = len(heads)
    return entry


def sight_sched() -> dict:
    """The monitor's own health. Windows task scheduler; SKIP elsewhere."""
    leg: dict = {"leg": "SCHED", "findings": [], "info": None}
    if sys.platform != "win32":
        leg["info"] = "SKIP: task scheduler leg is Windows-only"
        return leg
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "Get-ScheduledTask -TaskName %s | Get-ScheduledTaskInfo | "
             "Select-Object -ExpandProperty LastTaskResult" % SIGHT_TASK],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as exc:
        leg["findings"].append("SCHED-UNKNOWN: %s" % type(exc).__name__)
        return leg
    if proc.returncode != 0:
        leg["findings"].append(
            "SCHED-UNKNOWN: query failed (%s)" % (proc.stderr or "").strip()[:100])
        return leg
    try:
        code = int((proc.stdout or "").strip())
    except ValueError:
        leg["findings"].append(
            "SCHED-UNKNOWN: unparsable result %r" % (proc.stdout or "")[:60])
        return leg
    leg["info"] = "LastTaskResult=%d" % code
    if code != 0:
        leg["findings"].append(
            "SCHED-FAIL: %s last exited %d; the monitor is red"
            % (SIGHT_TASK, code))
    return leg


def sight(root: Path, only: set[str] | None) -> list[dict]:
    entries: list[dict] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if only and child.name not in only:
            continue
        if not child.is_dir() or not (child / ".git").is_dir():
            continue
        entries.append(sight_repo(child))
    return entries


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="C:/Azazael")
    ap.add_argument("--repos", default=None,
                    help="comma-separated subset of dir names")
    ap.add_argument("--json", default=None, help="write report JSON here")
    args = ap.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print("soul-fleet-sight: no such root %s" % root, file=sys.stderr)
        return 2
    only = set(args.repos.split(",")) if args.repos else None
    entries = sight(root, only)
    sched = sight_sched()
    bad = sum(1 for e in entries if e["findings"]) + \
        (1 if sched["findings"] else 0)
    for e in entries:
        state = "CLEAN" if not e["findings"] else \
            "FINDINGS(%d)" % len(e["findings"])
        print("%-32s %-8s dirty=%d up=%s o=%s heads=%s %s" % (
            e["path"], e["branch"], e["dirty"], e["upstream"],
            e["origin_ok"], e["heads"], state))
        for f in e["findings"]:
            print("    ! %s" % f)
    print("sched: %s %s" % (
        sched["info"],
        "FINDINGS(%d)" % len(sched["findings"]) if sched["findings"] else "clean"))
    for f in sched["findings"]:
        print("    ! %s" % f)
    print("\n%d repositorie(s): %d clean, %d with findings"
          % (len(entries), len(entries) - sum(1 for e in entries if e["findings"]),
             sum(1 for e in entries if e["findings"])))
    if args.json:
        Path(args.json).write_text(
            json.dumps({"repos": entries, "sched": sched}, indent=2),
            encoding="utf-8")
        print("report: %s" % args.json)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
