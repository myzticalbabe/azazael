#!/usr/bin/env python3
# coding: utf-8
"""Presence gate: does the script the hook guards on actually exist?

Eleven stanzas in `.githooks/pre-commit` are shaped like::

    if [ -f "$SCRIPT_DIR/tools/index_drift_check.py" ]; then
        timeout 120 "$PY" tools/index_drift_check.py || exit 1
    else
        echo "[IndexDrift] guard not found -- passing loud (guard unrunnable)"
    fi

(lines 91, 139, 167, 188, 224, 251, 269, 296, 344, 402, 440 -- measured
2026-11-14). A **deleted or renamed** gate script therefore does not fail the
commit: the hook prints one line and passes. One of the eleven, the preflight
stanza at line 224, has no ``else`` at all, so its gate disappears with no
output whatsoever. Nothing in the tree noticed, because every other check
assumes the gate it names is there.

This tool asks the question those branches do not: for every gate in
``tools/preflight_all.py``'s registry -- the inventory that is re-derived
against the hook text -- is the script on disk, and was it ever in HEAD?

Four states, because the answer routes to different work:

========================  ==========================================  ==========
 state                     meaning                                     verdict
========================  ==========================================  ==========
 ``present``               runs here; tracked at HEAD                  ok
 ``present-untracked``     runs here, in this worktree only            WARN
 ``deleted-at-head``       a committed gate was removed                FAIL
 ``never-committed``       the registry names a file no clone has      FAIL
========================  ==========================================  ==========

Both FAIL states mean the same operational thing -- the gate cannot run -- and
the labels only say who is at fault and which repair applies (restore the file,
or retire the registry row and its stanza). ``present-untracked`` does not fail
because the gate *does* run here; it is printed because a gate that exists only
in one worktree is a gate every other clone silently lacks.

Tracking is read from **one** ``git ls-tree -r HEAD`` call, not one
``cat-file -e`` per gate: 38 subprocesses costs ~1.5 s on Windows and this runs
on every commit.

Exit codes: ``0`` every gate can run (WARNs printed), ``1`` a gate cannot run,
``2`` could not judge -- no git, no repo, no registry. **2 is never a pass**: a
presence verdict is worth exactly what the tree it was read from is worth.

Not wired into the hook yet: `.githooks/pre-commit` was held by another lane on
2026-11-14 (+58/-22 in flight), so the row this tool needs in
``preflight_all.GATES`` cannot be added until that stanza lands -- the registry
self-test fails on a row the hook does not run.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, NamedTuple, Optional, Sequence, Set, Tuple

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

#: The enforcement surface itself. If this is gone, ``core.hooksPath`` points at
#: a directory with nothing in it and *no* gate runs -- the same defect class,
#: one level up, so it is a row like any other.
HOOK = ".githooks/pre-commit"

PRESENT = "present"
PRESENT_UNTRACKED = "present-untracked"
DELETED = "deleted-at-head"
NEVER = "never-committed"

#: States in which the gate cannot run at all.
FAILING = (DELETED, NEVER)


class Blindness(RuntimeError):
    """The question could not be asked. Never a pass, never a failure."""


class Row(NamedTuple):
    name: str
    script: str
    state: str

    @property
    def ok(self) -> bool:
        return self.state == PRESENT

    @property
    def fails(self) -> bool:
        return self.state in FAILING


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(root)] + list(args), capture_output=True, text=True,
            timeout=180, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError as exc:
        raise Blindness("git is not on PATH: %s" % exc) from exc
    except subprocess.TimeoutExpired as exc:
        raise Blindness("git %s did not finish in 180s" % args[0]) from exc


def tracked_paths(root: Path) -> Set[str]:
    """Every path in ``HEAD``, in one call, after proving ``root`` owns that HEAD.

    The root check is not ceremony. Measured 2026-11-14: ``git -C <tmpdir>
    ls-tree HEAD`` **succeeded** because git walked up into an enclosing
    repository, so a tree with no repository of its own would have been judged
    against somebody else's ``HEAD`` -- every row reading ``deleted-at-head``
    for files that were never there. ``--show-toplevel`` must equal the root
    asked about; anything else is blindness, not a verdict.

    ``ls-tree`` returns rc 0 with empty output for a path that is not tracked,
    so absence stays distinguishable from error. ``cat-file -e`` conflates the
    two: a bad revision and a missing path both exit 128.
    """
    toplevel = _git(root, "rev-parse", "--show-toplevel")
    if toplevel.returncode != 0:
        raise Blindness("%s is not a git worktree: %s" % (
            root, (toplevel.stderr or "").strip().splitlines()[:1]))
    resolved = Path(toplevel.stdout.strip())
    # os.path.normcase, not ntpath's: on the Linux lanes it must still fold case
    # only where the filesystem does, instead of being the identity function.
    if os.path.normcase(str(resolved.resolve())) != os.path.normcase(str(root.resolve())):
        raise Blindness(
            "%s is not a repository root (git resolved it to %s); every path this "
            "tool judges is repo-relative" % (root, resolved))

    proc = _git(root, "ls-tree", "-r", "--name-only", "HEAD")
    if proc.returncode != 0:
        raise Blindness(
            "git ls-tree HEAD failed in %s (rc %d): %s"
            % (root, proc.returncode, (proc.stderr or "").strip().splitlines()[:1])
        )
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def assess(
    root: Path,
    items: Iterable[Tuple[str, str]],
    tracked: Set[str],
) -> List[Row]:
    """Classify each ``(name, script)``. Pure: no git, no filesystem writes."""
    rows: List[Row] = []
    for name, script in items:
        exists = (root / script).is_file()
        in_head = script in tracked
        if exists:
            state = PRESENT if in_head else PRESENT_UNTRACKED
        else:
            state = DELETED if in_head else NEVER
        rows.append(Row(name=name, script=script, state=state))
    return rows


def verdict(rows: Sequence[Row]) -> int:
    return 1 if any(row.fails for row in rows) else 0


def summarise(rows: Sequence[Row]) -> dict:
    """Counts, with the denominator named (a count without one is not a reading)."""
    by_state = {state: 0 for state in (PRESENT, PRESENT_UNTRACKED, DELETED, NEVER)}
    for row in rows:
        by_state[row.state] = by_state.get(row.state, 0) + 1
    return {
        "rows": len(rows),
        "states": by_state,
        "failing": [row.name for row in rows if row.fails],
        "warn": [row.name for row in rows if row.state == PRESENT_UNTRACKED],
    }


def registry_items() -> List[Tuple[str, str]]:
    """``(gate name, script)`` from the registry, hook first.

    Imported lazily so ``--help`` works when the registry itself is broken, and
    so an import failure is reported as BLIND (exit 2) rather than crashing.
    """
    sys.path.insert(0, str(TOOLS))
    try:
        import preflight_all  # noqa: PLC0415 -- lazy on purpose
    except Exception as exc:  # noqa: BLE001 -- any failure here is blindness
        raise Blindness("cannot import tools/preflight_all.py: %r" % (exc,)) from exc
    items = [("hook-installed", HOOK)]
    seen = set()
    for gate in preflight_all.GATES:
        if not gate.argv:
            raise Blindness("registry gate %r has an empty argv" % (gate.name,))
        script = str(gate.argv[0])
        if script in seen:
            continue
        seen.add(script)
        items.append((gate.name, script))
    return items


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hook_gate_presence.py",
        description="Prove every registered hook gate script exists.",
    )
    parser.add_argument("--root", default=None,
                        help="repo root to judge (default: this file's repo)")
    parser.add_argument("--all", action="store_true",
                        help="print every row, not just the ones that need work")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root).resolve() if args.root else REPO
    if not root.is_dir():
        print("[gate-presence] BLIND: %s is not a directory" % root, file=sys.stderr)
        return 2

    try:
        items = registry_items()
        rows = assess(root, items, tracked_paths(root))
    except Blindness as exc:
        print("[gate-presence] BLIND: %s" % exc, file=sys.stderr)
        return 2

    summary = summarise(rows)
    code = verdict(rows)

    if args.json:
        print(json.dumps(
            {"verdict": "PASS" if code == 0 else "FAIL",
             "root": str(root), "summary": summary,
             "rows": [row._asdict() for row in rows]},
            indent=2, sort_keys=True))
        return code

    if args.all:
        width = max(len(row.name) for row in rows)
        for row in rows:
            print("  %-*s  %-18s %s" % (width, row.name, row.state, row.script))

    for row in rows:
        if row.state == DELETED:
            print("[gate-presence] FAIL %s: %s is tracked at HEAD but missing from "
                  "the worktree -- the hook's existence guard skips it silently. "
                  "Restore the file, or retire the registry row and its stanza."
                  % (row.name, row.script))
        elif row.state == NEVER:
            print("[gate-presence] FAIL %s: %s is named by the registry and does not "
                  "exist, in HEAD or on disk -- that gate has never run."
                  % (row.name, row.script))
        elif row.state == PRESENT_UNTRACKED:
            print("[gate-presence] WARN %s: %s runs here but is untracked -- every "
                  "other clone lacks this gate." % (row.name, row.script))

    print("[gate-presence] %d gates: %d present (%d untracked), %d absent -> %s"
          % (summary["rows"], summary["states"][PRESENT],
             summary["states"][PRESENT_UNTRACKED],
             summary["states"][DELETED] + summary["states"][NEVER],
             "PASS" if code == 0 else "FAIL %d" % len(summary["failing"])))
    return code


if __name__ == "__main__":
    sys.exit(main())
