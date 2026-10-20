#!/usr/bin/env python3
"""commit_gate.py -- bulk-diff gate for commits (2026-09-28).

Why this exists: three straight forensic-fix commits swept pre-existing
worktree dirt into their messages (260-line local_memory.py for a 6-line
hunk, dead .bats, 470-line retention files). Nothing broke, but a commit
message that describes 5 lines while carrying 400 is a lie in the ledger,
and the ledger is load-bearing here.

Two parts:
  1. `commit_gate.py --hook` (pre-commit): fail when the STAGED changeset
     exceeds bulk thresholds unless ALLOW_BULK_COMMIT=1. Small focused
     commits always pass; deliberate bulk ops (frame untracking, snapshots)
     pass by declaring intent in the env.
  2. `commit_gate.py review`: interactive worktree review -- groups changed
     files (source vs generated), shows per-file +/- and lets the operator
     stage exactly what the commit message will describe.

Thresholds via env: COMMIT_GATE_MAX_LINES (default 150 changed lines in one
file), COMMIT_GATE_MAX_FILES (default 8 staged files).

Exit codes: 0 pass / 1 block (--hook) or user abort (review).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_LINES = 150
DEFAULT_MAX_FILES = 8

GENERATED_SUFFIXES = (".ppm", ".png", ".log", ".jsonl", ".html")
GENERATED_DIRS = ("output/", "graphify-out/", "backup/")


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       timeout=60, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError("git %s failed: %s" % (" ".join(args), r.stderr[:200]))
    return r.stdout


def staged_numstat() -> list[tuple[int, int, str]]:
    """[(added, deleted, path)] for the index. Binary files report -/-."""
    rows = []
    for line in _git("diff", "--cached", "--numstat").splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        try:
            added, deleted = int(parts[0]), int(parts[1])
        except ValueError:
            added, deleted = -1, -1  # binary
        rows.append((added, deleted, parts[2]))
    return rows


def staged_statuses() -> dict[str, str]:
    """path -> XY status for staged entries (A = newly created)."""
    out: dict[str, str] = {}
    for line in _git("status", "--short").splitlines():
        if len(line) > 3 and line[0] != " " and line[0] != "?":
            out[line[3:].strip()] = line[:2]
    return out


def worktree_status() -> list[tuple[str, str]]:
    """[(xy, path)] for worktree + index (porcelain)."""
    rows = []
    for line in _git("status", "--short").splitlines():
        if len(line) > 3:
            rows.append((line[:2].strip(), line[3:].strip()))
    return rows


def is_generated(path: str) -> bool:
    p = path.replace("\\", "/")
    if any(p.startswith(d) for d in GENERATED_DIRS):
        return True
    return p.lower().endswith(GENERATED_SUFFIXES)


def evaluate(rows: list[tuple[int, int, str]], max_lines: int,
             max_files: int, created: set[str] | None = None) -> list[str]:
    """Bulk violations, human-readable. Empty means pass.

    Newly created files are exempt from the per-file line cap: a create
    carries no hidden dirt (everything in it is new by definition), while
    a 400-line modification to a tracked file is exactly the sweep this
    gate exists to catch. Creates still count toward the file tally.

    Generated artifacts (is_generated) are exempt from BOTH tallies: the
    advisory `review` command already reports them separately, so the
    blocking path must not demand a bulk declaration for bytes no human
    wrote. Generated files cannot rescue an otherwise-blocked changeset --
    the source rows are judged exactly as if the generated rows were
    absent.
    """
    created = created or set()
    problems = []
    tracked = [r for r in rows if r[2] and not r[2].startswith("(")]
    tracked = [r for r in tracked if not is_generated(r[2])]
    if len(tracked) > max_files:
        problems.append(
            "%d staged files exceed the bulk limit (%d). Stage a focused "
            "set, or set ALLOW_BULK_COMMIT=1 to declare a bulk op."
            % (len(tracked), max_files))
    for added, deleted, path in tracked:
        if added < 0:
            continue  # binary: counted in the file tally, not line tally
        if path in created:
            continue  # new file: nothing hidden inside
        if added + deleted > max_lines:
            problems.append(
                "%s changes %d lines (limit %d/file). Split it, or set "
                "ALLOW_BULK_COMMIT=1." % (path, added + deleted, max_lines))
    return problems


def cmd_hook() -> int:
    max_lines = int(os.environ.get("COMMIT_GATE_MAX_LINES",
                                   str(DEFAULT_MAX_LINES)))
    max_files = int(os.environ.get("COMMIT_GATE_MAX_FILES",
                                   str(DEFAULT_MAX_FILES)))
    if os.environ.get("ALLOW_BULK_COMMIT") == "1":
        print("commit-gate: bulk declared via ALLOW_BULK_COMMIT=1, passing")
        return 0
    try:
        rows = staged_numstat()
        created = {p for p, s in staged_statuses().items() if "A" in s}
    except Exception as exc:
        # A broken gate must never block all commits; be loud instead.
        print("commit-gate: cannot read staged diff (%s) -- passing loud" % exc)
        return 0
    if not rows:
        return 0
    gen_count = len([r for r in rows if r[2] and is_generated(r[2])])
    if gen_count:
        print("commit-gate: %d generated file(s) staged -- exempt from bulk "
              "caps (review: python scripts/commit_gate.py review)" % gen_count)
    problems = evaluate(rows, max_lines, max_files, created)
    if not problems:
        return 0
    print("commit-gate: BULK CHANGESET BLOCKED")
    for p in problems:
        print("  - " + p)
    print("  Review with: python scripts/commit_gate.py review")
    return 1


def cmd_review() -> int:
    rows = worktree_status()
    if not rows:
        print("worktree clean")
        return 0
    src = [(s, p) for s, p in rows if not is_generated(p)]
    gen = [(s, p) for s, p in rows if is_generated(p)]
    print("=== source (%d) ===" % len(src))
    for s, p in src:
        print("  [%s] %s" % (s or "?", p))
    if gen:
        print("=== generated (%d, never stage these) ===" % len(gen))
        for s, p in gen[:15]:
            print("  [%s] %s" % (s or "?", p))
        if len(gen) > 15:
            print("  ... and %d more" % (len(gen) - 15))
    print()
    print("Stage exactly what your message will describe, e.g.:")
    print("  git add <file> ... && git commit -m \"...\"")
    print("Bulk ops: ALLOW_BULK_COMMIT=1 git commit ...")
    return 0


def main(argv=None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    if "--hook" in args:
        return cmd_hook()
    if "review" in args:
        return cmd_review()
    print(__doc__.strip().splitlines()[0])
    print("usage: commit_gate.py [--hook | review]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
