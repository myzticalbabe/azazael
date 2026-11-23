#!/usr/bin/env python3
"""Soul fleet sweep -- the corrective leg the 2026-11-23 hygiene round paid for.

The per-repo gate (tools/soul_licence_check.py) needs a .git directory, so it
is blind to exactly three things, each of which bit this fleet on 2026-11-23:

  UNBORN        a project-like directory that is not a repository at all
                (myzticalbabe.github.io shipped a full CDDL LICENSE while the
                gate reported nothing -- there was no repo to run it in; four
                stem/audit working copies sat in the same blind spot).
  DIRTY         a correct fix sitting uncommitted in a worktree
                (publish/flame-engine's NOTICE+pyproject purge waited as
                ` M` lines while every committed-tree scan read clean).
  STALE-BUILD   generated paths tracked in a public repo carrying superseded
                licence metadata (publish/shardex build/tmp PKG-INFO copies
                predated the purge; the worktree scan kept passing them
                because nobody asked whether they should be tracked at all).

Plus one convention signal, fetch-fresh:

  ORIGIN-MASTER  the remote default branch is still `master` while the fleet
                default is `main`. Read live via ls-remote --symref (the
                local origin/HEAD symref goes stale after a switch --
                measured 2026-11-23 on EveUnleashed); local symref is the
                offline fallback.

Declared artefacts (--exclude-from FILE, one dir name per line) are
skipped by decision, not by blindness: the file is the record.

Usage:
    python tools/soul_fleet_sweep.py [--root C:/Azazael] [--json out.json]
    python tools/soul_fleet_sweep.py --root <dir> --repos a,b,c  # subset

Exit status: 0 every repo clean and nothing unborn, 1 any finding, 2 no root.
Slow by design (one checker subprocess per repo); a scheduled/manual leg,
never a commit-hook gate.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

CHECKER_NAME = "soul_licence_check.py"
PROJECT_MARKERS = (
    "pyproject.toml", "setup.py", "setup.cfg", "package.json",
    "README.md", "LICENSE", "NOTICE", "CITATION.cff",
    "PUBLIC_MANIFEST.json", "src",
)
# A lone LICENSE is a text file, not a project (measured 2026-11-23:
# tools_bin/ holds only LICENSE+bin+gh.zip and is a tool cache).
# Require a code marker or at least two markers before calling it unborn.
CODE_MARKERS = (
    "pyproject.toml", "setup.py", "setup.cfg", "package.json", "src",
)
GENERATED_DIR_PARTS = ("build", "dist", "__pycache__")
GENERATED_DIR_SUFFIXES = (".egg-info", ".dist-info")


def _generated(path: str) -> bool:
    """A tracked path that smells like build output. Parts, not substrings:
    a substring test on "/build/" misses a root-level build/ dir (no
    leading slash -- measured 2026-11-23: shardex's build/tmp hits)."""
    parts = PurePosixPath(path.replace("\\", "/")).parts
    return any(p in GENERATED_DIR_PARTS for p in parts) or \
        any(p.endswith(GENERATED_DIR_SUFFIXES) for p in parts)


def run(args, cwd):
    """Subprocess with a timeout; a transport failure is data, not a crash."""
    try:
        proc = subprocess.run(
            args, cwd=str(cwd), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "sweep transport failure: %s" % exc


def own_toplevel(root: Path, path: Path) -> bool:
    """True when path's repo toplevel IS path (not an ancestor's)."""
    rc, out = run(["git", "rev-parse", "--show-toplevel"], path)
    if rc != 0:
        return False
    with contextlib.suppress(OSError):
        same = os.path.normcase(os.path.realpath(out.strip())) == \
            os.path.normcase(os.path.realpath(path))
        return bool(same)
    return False


def parse_lsremote_default(out: str) -> str | None:
    """Read the true remote default from `git ls-remote --symref` output.
    First line looks like `ref: refs/heads/main\tHEAD`. Returns None when
    the server did not advertise a symref (or the output is empty)."""
    for ln in out.splitlines():
        if ln.startswith("ref: "):
            ref = ln[4:].split()[0]
            if ref.startswith("refs/heads/"):
                return ref[len("refs/heads/"):]
    return None


def remote_default_branch(path: Path) -> tuple[str | None, str]:
    """(branch, source). Live ls-remote first (fetch-fresh: the local
    origin/HEAD symref goes stale after a default-branch switch --
    measured 2026-11-23 on EveUnleashed), local symref as the offline
    fallback, (None, source) when neither answers."""
    try:
        proc = subprocess.run(
            ["git", "ls-remote", "--symref", "origin", "HEAD"],
            cwd=str(path), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        proc = None
        print("soul-fleet-sweep: ls-remote unreachable for %s (%s); "
              "using local origin/HEAD" % (path.name, type(exc).__name__),
              file=sys.stderr)
    if proc is not None and proc.returncode == 0:
        branch = parse_lsremote_default(proc.stdout or "")
        if branch:
            return branch, "remote"
    rc, out = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], path)
    if rc == 0 and out.strip():
        return out.strip().rsplit("/", 1)[-1], "local"
    return None, "none"


def load_excludes(path: str) -> set[str]:
    """Declared-artefact names, one per line; `#` comments and blanks out.
    The file itself is the visibility: an excluded dir is a decision with
    a reason, not a blind spot."""
    names: set[str] = set()
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            names.add(ln)
    return names


def check_repo(path: Path, checker: Path) -> dict:
    """Run the per-repo gate plus the three fleet-only signals."""
    entry: dict = {"path": path.name, "kind": "repo", "findings": []}
    rc, out = run([sys.executable, str(checker)], path)
    if rc == 2:
        entry["findings"].append("UNRUNNABLE: checker exit 2: %s" % out.strip()[:160])
    elif rc != 0:
        entry["findings"].append("LICENCE-DEFECTS: %s" % out.strip()[:400])
    rc, out = run(["git", "status", "--porcelain"], path)
    dirty = [ln for ln in out.splitlines() if ln.strip()] if rc == 0 else []
    if dirty:
        entry["findings"].append("DIRTY: %d uncommitted path(s), e.g. %s"
                                 % (len(dirty), dirty[0].strip()[:80]))
    rc, out = run(["git", "ls-files"], path)
    if rc == 0:
        stale = sorted({ln for ln in out.splitlines()
                        if ln.strip() and _generated(ln)})
        if stale:
            entry["findings"].append(
                "STALE-BUILD: %d tracked generated path(s), e.g. %s"
                % (len(stale), stale[0][:100]))
    default, source = remote_default_branch(path)
    if default:
        entry["origin_default"] = default
        if default == "master":
            entry["findings"].append(
                "ORIGIN-MASTER: remote default is master (%s read); "
                "fleet convention is main" % source)
    return entry


def sweep(root: Path, checker: Path, only: set[str],
          excluded: set[str] | None = None) -> list[dict]:
    entries = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if only and child.name not in only:
            continue
        if excluded and child.name in excluded:
            continue
        if (child / ".git").is_dir() and own_toplevel(root, child):
            entries.append(check_repo(child, checker))
            continue
        markers = [m for m in PROJECT_MARKERS if (child / m).exists()]
        if len(markers) >= 2 or any(m in CODE_MARKERS for m in markers):
            entries.append({"path": child.name, "kind": "unborn", "findings": [
                "UNBORN: project-like (%s) but not a repository -- invisible "
                "to every gate; git init + adopt, or declare it an artefact "
                "store" % ", ".join(markers[:4])]})
    return entries


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Fleet-wide SOUL LICENCE ONLY sweep.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]),
                    help="fleet directory (default: parent of this repo)")
    ap.add_argument("--repos", default="",
                    help="comma-separated subset of directory names")
    ap.add_argument("--exclude-from", default="",
                    help="file of declared-artefact dir names to skip")
    ap.add_argument("--json", default="", help="write the full report here")
    a = ap.parse_args(argv)

    root = Path(a.root)
    if not root.is_dir():
        print("soul-fleet-sweep: no such root %s" % root, file=sys.stderr)
        return 2
    checker = Path(__file__).resolve().parent / CHECKER_NAME
    if not checker.is_file():
        print("soul-fleet-sweep: no checker at %s" % checker, file=sys.stderr)
        return 2

    only = {r.strip() for r in a.repos.split(",") if r.strip()}
    excluded: set[str] = set()
    if a.exclude_from:
        excluded = load_excludes(a.exclude_from)
        print("soul-fleet-sweep: %d declared artefact(s) excluded"
              % len(excluded))
    entries = sweep(root, checker, only, excluded)
    if not entries:
        print("soul-fleet-sweep: nothing project-like under %s" % root)
        return 2
    bad = 0
    for e in entries:
        state = "CLEAN" if not e["findings"] else "FINDINGS(%d)" % len(e["findings"])
        if e["findings"]:
            bad += 1
        print("%-32s %-10s %s" % (e["path"], e["kind"], state))
        for f in e["findings"]:
            print("    ! %s" % f)
    print("\n%d directorie(s): %d clean, %d with findings" % (len(entries), len(entries) - bad, bad))
    if a.json:
        Path(a.json).write_text(json.dumps(entries, indent=1), encoding="utf-8")
        print("report: %s" % a.json)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
