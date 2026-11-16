#!/usr/bin/env python3
r"""soulforge_gate.py -- prove SOULFORGE from the binary that was built.

WHY A SEPARATE STAGE, AND WHY IT RUNS THE EXE. `tools/swarm_arena/` ships a
Nuitka onefile build (`dist/SOULFORGE.exe`, 8,276,480 bytes measured 2026-11-14)
and the source tree never imports it. `python soulforge.py --selftest` therefore
says nothing about the artefact a person installs: it stays green after the
build itself breaks. And `dist/` is gitignored (`.gitignore:8`), so no other
gate in this tree can notice a binary that was never rebuilt after its source
moved. The proof has to be the built exe running its own selftest.

TWO SCOPES, because "the tree" and "this commit" are different questions:

  --staged   what the index is about to land, read through
             `git diff --cached`. No path under `tools/swarm_arena/` -> exit 0
             with the reason printed (a printed skip, never an implied pass).
             Anything there -> the binary must exist, be newer than every build
             input, and pass its own selftest.
  default    the tree, for `tools/evidence_tier.sh` and `preflight_all.py
             --check`: the same proof with no index involved, because the tier
             grades the tree rather than a changeset.

Exit codes in the tier's own vocabulary, because collapsing them is how a
"could not run" becomes a green row:

  0  proved, or nothing in scope to prove (printed)
  1  DEFECT -- the binary is older than its inputs, or its selftest did not pass
  2  BLIND  -- there is no binary to prove from, or it refused to run

A stale binary is a DEFECT and not a rebuild hint: a commit that changes
`soulforge.py` and passes against last week's exe is the gate certifying bytes
that are not in the commit.

THE PASS CRITERION IS THE OUTPUT, NOT THE EXIT CODE. Measured on this tree, a
gate that exits 0 because nothing ran is indistinguishable from a gate that
exited 0 because everything passed, so both markers the binary prints on a real
pass ("selftest    PASS" and "live key untouched") are required literally. The
live-key comparison matters most: a selftest that quietly moved the user's
pointers is a failure, not a pass with a caveat.

Every invocation first runs the classifiers' own fixtures (`--selftest` runs
only those). A verdict produced by a classifier that cannot fail is not a
verdict, and this costs microseconds.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

REPO = Path(__file__).resolve().parent.parent
ARENA = REPO / "tools" / "swarm_arena"
EXE = ARENA / "dist" / "SOULFORGE.exe"
ENTRY = "soulforge.py"
BUILDER = "build_soulforge.py"
DATA_DIR = "cursors"
#: The binary bounds its own children (600 + 180 + 180 s); this outer bound only
#: exists so a wedged exe is named rather than inherited by the commit hook.
SELFTEST_BUDGET = 900
PASS_MARKERS = ("selftest    PASS", "live key untouched")
BUILD_REMEDY = "python tools/swarm_arena/build_soulforge.py"


def _stamp(seconds: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))


def transient(name: str, path: Path) -> bool:
    """True for the artefacts a build writes, which are never build inputs."""
    parts = set(path.parts)
    return name == "dist" or name == "out" or name == "__pycache__" or "target" in parts


def local_imports(path: Path) -> List[str]:
    """Local sibling modules imported by `path`, e.g. soulforge.py -> make_cursors.

    Parsed rather than grepped: `make_cursors.py` imports `json`, `os` and so
    on, and a name-substring sweep would either miss a sibling or invent one.
    A file that will not parse contributes nothing, and the entry point itself
    is always an input, so a broken source file cannot make the list empty.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    names: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.append(node.module.split(".")[0])
    return names


def build_inputs() -> List[Path]:
    """Every file the artefact is built from: the import closure plus the data.

    The closure starts at the entry point Nuitka is handed (build_soulforge.py
    appends `soulforge.py`) and follows local imports, so a module added later
    is picked up without editing this list. The builder is included because its
    flags (onefile, console mode, included data dir) shape the artefact.
    """
    found: List[Path] = []
    seen: set = set()
    queue: List[str] = [ENTRY]
    while queue:
        name = queue.pop(0)
        path = ARENA / name
        if name in seen or not path.is_file():
            continue
        seen.add(name)
        found.append(path)
        queue.extend(module + ".py" for module in local_imports(path))
    builder = ARENA / BUILDER
    if builder.is_file() and builder not in found:
        found.append(builder)
    data = ARENA / DATA_DIR
    if data.is_dir():
        for child in sorted(data.rglob("*")):
            if child.is_file() and not transient(child.parent.name, child):
                found.append(child)
    return found


def newest(paths: Iterable[Path]) -> Tuple[Path, float]:
    """The most recently written input. Deterministic on mtime ties by name."""
    best = max(paths, key=lambda p: (p.stat().st_mtime, str(p)))
    return best, best.stat().st_mtime


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(returncode: int, stdout: str) -> Tuple[str, str]:
    """The binary's result -> (PASS | DEFECT | BLIND, the reason).

    The three states are kept apart on purpose: rc 3 is the binary *refusing*
    to run (a `SOULFORGE_CURSOR_KEY` is already set, so "the live key was
    untouched" would be a claim about somebody else's key), and reporting that
    as a pass is the defect this function exists to prevent.
    """
    if returncode == 3:
        return "BLIND", ("the binary refused to run (rc 3): SOULFORGE_CURSOR_KEY "
                         "is set in this environment, so no live-key proof exists")
    if returncode != 0:
        return "DEFECT", "the binary's selftest exited %d" % returncode
    missing = [marker for marker in PASS_MARKERS if marker not in stdout]
    if missing:
        return "DEFECT", ("exit 0 but the output never said %s -- an exit code "
                          "alone is not a proof" % ", ".join(repr(m) for m in missing))
    return "PASS", "exit 0 and both pass markers present"


def self_check() -> List[str]:
    """Prove the classifiers can fail, on fixtures, before trusting a verdict."""
    good = "selftest    PASS  build, install, check and uninstall; live key untouched (12 value(s))"
    cases = (
        (0, good, "PASS"),
        (0, "", "DEFECT"),
        (0, "selftest    PASS  but the key moved", "DEFECT"),
        (1, good, "DEFECT"),
        (3, "", "BLIND"),
    )
    defects = []
    for returncode, stdout, want in cases:
        got, reason = classify(returncode, stdout)
        if got != want:
            defects.append("classify(%d, %r) -> %s, expected %s (%s)"
                           % (returncode, stdout[:40], got, want, reason))
    with tempfile.TemporaryDirectory(prefix="soulforge-gate-selftest-") as tmp:
        older, newer = Path(tmp) / "older.py", Path(tmp) / "newer.py"
        older.write_text("", encoding="utf-8")
        newer.write_text("", encoding="utf-8")
        stamp = time.time()
        os.utime(older, (stamp - 60, stamp - 60))
        os.utime(newer, (stamp, stamp))
        picked, _ = newest([older, newer])
        if picked != newer:
            defects.append("newest() picked %s from a two-file fixture" % picked.name)
    return defects


def staged_paths() -> Tuple[List[str], str]:
    """The index's paths, or ([], reason) when git cannot be read.

    -z keeps a path with a space or a quote intact; `--name-only` without it
    would split such a path and quietly stop matching the archive prefix.
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "-z",
             "--diff-filter=ACMRDT"],
            cwd=str(REPO), capture_output=True, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [], "git could not be run (%s)" % exc
    if proc.returncode != 0:
        return [], "git diff --cached exited %d (%s)" % (
            proc.returncode, proc.stderr.decode("utf-8", "replace")[:200])
    raw = proc.stdout.decode("utf-8", "replace")
    return [p for p in raw.split("\0") if p], ""


def in_arena(paths: Sequence[str]) -> List[str]:
    prefix = "tools/swarm_arena/"
    return [p.replace("\\", "/") for p in paths
            if p.replace("\\", "/").startswith(prefix)]


def prove(scope: str) -> int:
    print("soulforge-gate  scope: %s" % scope)
    defects = self_check()
    if defects:
        for line in defects:
            print("DEFECT      %s" % line)
        print("soulforge-gate  the classifiers do not fail as required -- no verdict")
        return 1
    if not EXE.is_file():
        print("BLIND       %s is absent, so there is no built artefact to prove"
              % EXE.relative_to(REPO).as_posix())
        print("            build it: %s" % BUILD_REMEDY)
        return 2
    inputs = build_inputs()
    newest_path, newest_time = newest(inputs)
    exe_time = EXE.stat().st_mtime
    print("soulforge-gate  binary %d bytes  sha256 %s  built %s"
          % (EXE.stat().st_size, sha256_of(EXE), _stamp(exe_time)))
    print("soulforge-gate  inputs %d file(s); newest %s at %s"
          % (len(inputs), newest_path.relative_to(REPO).as_posix(),
             _stamp(newest_time)))
    if newest_time > exe_time:
        print("DEFECT      the binary is older than its inputs by %.0f s -- it does "
              "not contain this source" % (newest_time - exe_time))
        print("            rebuild first: %s" % BUILD_REMEDY)
        return 1
    started = time.monotonic()
    try:
        proc = subprocess.run([str(EXE), "--selftest"], cwd=str(REPO),
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=SELFTEST_BUDGET)
    except subprocess.TimeoutExpired:
        print("DEFECT      %s --selftest exceeded %d s -- a run that never "
              "completed is not a pass" % (EXE.name, SELFTEST_BUDGET))
        return 1
    except OSError as exc:
        print("BLIND       %s could not be spawned (%s)" % (EXE.name, exc))
        return 2
    seconds = time.monotonic() - started
    for line in (proc.stdout or "").strip().splitlines()[-6:]:
        print("   | %s" % line)
    state, reason = classify(proc.returncode, proc.stdout or "")
    print("%-11s %s in %.1fs" % (state, reason, seconds))
    if state == "PASS":
        return 0
    return 2 if state == "BLIND" else 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulforge_gate.py",
        description="Prove SOULFORGE from the built binary; see the module docstring.",
    )
    parser.add_argument("--staged", action="store_true",
                        help="judge the git index; exit 0 when it does not touch "
                             "tools/swarm_arena/")
    parser.add_argument("--selftest", action="store_true",
                        help="run only the classifier fixtures")
    args = parser.parse_args(argv)
    if args.selftest:
        defects = self_check()
        for line in defects:
            print("DEFECT      %s" % line)
        print("soulforge-gate  self-check: %s" % ("PASS" if not defects else "FAIL"))
        return 0 if not defects else 1
    if not args.staged:
        return prove("the tree (tools/evidence_tier.sh / preflight_all.py --check)")
    paths, reason = staged_paths()
    if reason:
        print("BLIND       the index could not be read: %s" % reason)
        return 2
    touched = in_arena(paths)
    print("soulforge-gate  scope: the staged index (%d path(s))" % len(paths))
    if not touched:
        print("SKIP        no staged path under tools/swarm_arena/ -- nothing to prove")
        return 0
    print("soulforge-gate  %d staged path(s) under tools/swarm_arena/: %s"
          % (len(touched), ", ".join(touched[:6])))
    return prove("the commit that touches tools/swarm_arena/")


if __name__ == "__main__":
    sys.exit(main())
