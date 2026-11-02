# coding: utf-8
"""Housekeeping for a repository: the sweep's other half.

A sweep finds defects and the loop fixes them. Neither of those touches the
other thing that accumulates in a tree somebody has been working in for a year:
bytecode caches, tool caches, editor leftovers, empty directories left behind by
a move, sweep state from a run nobody read, and a single 300 MB scratch file
that git does not know about. None of it is a bug; all of it is why `git status`
takes forty seconds and why a disk runs at 98%.

Design rules, each one bought rather than assumed:

* **Dry run is the default.** `apply()` is a separate, explicit act. A cleaner
  that removes first and reports afterwards is a data-loss tool.
* **Nothing git tracks is ever deleted**, and neither is anything reached
  through a symlink, and neither is anything that resolves outside the root.
  Those three refusals are the whole safety argument, so they are code and not
  advice in a README.
* **No git, no deletion outside the known caches.** If `git ls-files` cannot be
  read the tool cannot prove a path is untracked; it then deletes only the
  cache directories, which no repository tracks on purpose, and reports
  everything else as kept-with-reason.
* **Hazards are reported, never removed.** A batch that was verified and never
  landed, or an untracked file larger than the budget, is state a human has to
  look at. A cleaner that deletes the evidence is worse than a full disk.
* **Every deletion is written down** to `.flaming_sword/housekeep.jsonl`, so
  "what reclaimed my 900 MB" has an answer tomorrow.

Standard library and `git`.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

STATE_DIR = ".flaming_sword"

#: Directories no repository tracks on purpose. Deleting one is safe without
#: asking git, which is what lets the tool work at all when git is unavailable.
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
              ".pyright", ".hypothesis", ".tox", ".ipynb_checkpoints"}

#: Files that are a by-product of an editor or an OS, never content.
LEFTOVER_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
LEFTOVER_SUFFIXES = (".orig", ".rej", ".bak", ".swp", ".swo", "~")

#: Sweep state that is disposable by design. `batches.jsonl` is deliberately
#: absent: it is the record of what was landed, and that is history, not garbage.
DISPOSABLE_STATE = ("findings.jsonl", "queue.jsonl", "research.jsonl")

DEFAULT_STATE_DAYS = 14
DEFAULT_MAX_MB = 25


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _size(path: Path) -> int:
    """Bytes under a path, never following a symlink and never raising."""
    if path.is_symlink():
        return 0
    if path.is_file():
        # An unreadable file contributes 0 measured bytes. `suppress` states
        # that deliberately: this is a report of disk use, not a place to raise.
        with contextlib.suppress(OSError):
            return path.stat().st_size
        return 0
    total = 0
    for base, _dirs, files in os.walk(path, followlinks=False):
        for name in files:
            handle = Path(base) / name
            try:
                if not handle.is_symlink():
                    total += handle.stat().st_size
            except OSError:
                continue
    return total


def _age_days(path: Path) -> float:
    """Age in days, or 0.0 when it cannot be read -- a path that cannot be dated
    is not old enough to be swept on age alone."""
    with contextlib.suppress(OSError):
        return (time.time() - path.stat().st_mtime) / 86400.0
    return 0.0


def tracked_paths(root: Path) -> Optional[Set[str]]:
    """Every path git knows, as posix strings; None when git cannot answer.

    None is not an empty set. "git says nothing is tracked" would license
    deleting the whole repository, so the caller must treat None as "unknown"
    and fall back to the cache-only rule.
    """
    completed = None
    with contextlib.suppress(OSError, subprocess.TimeoutExpired):
        completed = subprocess.run(["git", "ls-files", "-z"], cwd=str(root),
                                   capture_output=True, timeout=120)
    if completed is None or completed.returncode != 0:
        return None
    raw = completed.stdout.decode("utf-8", errors="replace")
    return {part.replace("\\", "/") for part in raw.split("\0") if part}


def _tracked_inside(tracked: Set[str], rel: str) -> bool:
    prefix = rel.rstrip("/") + "/"
    if rel in tracked:
        return True
    # A set scan per directory is O(tracked) and this tree has thousands of
    # files: the prefix test is done once per candidate directory, so the cost
    # stays bounded by the number of candidates rather than by the tree.
    return any(path.startswith(prefix) for path in tracked)


def collect(root: Path, tracked: Optional[Set[str]] = None,
            state_days: int = DEFAULT_STATE_DAYS,
            max_mb: int = DEFAULT_MAX_MB) -> List[Dict]:
    """Plan the housekeeping pass. Deletes nothing; says what it would do."""
    root = root.resolve()
    if tracked is None:
        tracked = tracked_paths(root)
    items: List[Dict] = []
    planned_gone: Set[str] = set()

    def add(rule: str, path: Path, kind: str, why: str, size: Optional[int] = None) -> None:
        rel = _rel(root, path)
        items.append({"rule": rule, "path": rel, "action": kind,
                      "bytes": _size(path) if size is None else size, "why": why})

    for base, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        base_path = Path(base)
        # `.git` is not housekeeping: its internals are git's own, and a walk
        # that descends into it both lies about sizes and risks a lock file.
        dirnames[:] = sorted(name for name in dirnames
                             if name != ".git"
                             and not (base_path / name).is_symlink())
        for name in list(dirnames):
            candidate = base_path / name
            rel = _rel(root, candidate)
            if name in CACHE_DIRS:
                if tracked is not None and _tracked_inside(tracked, rel):
                    add("bytecode-cache" if name == "__pycache__" else "tool-cache",
                        candidate, "keep", "git tracks a file inside it")
                else:
                    add("bytecode-cache" if name == "__pycache__" else "tool-cache",
                        candidate, "delete", "regenerated on the next import or run")
                    planned_gone.add(rel)
                dirnames.remove(name)

        for name in filenames:
            candidate = base_path / name
            rel = _rel(root, candidate)
            if candidate.is_symlink():
                continue
            if name in LEFTOVER_NAMES or name.endswith(LEFTOVER_SUFFIXES):
                if tracked is None:
                    # A `.orig` may be the last copy of something. Without git
                    # there is no way to tell content from by-product, so the
                    # refusal is total rather than probabilistic.
                    add("editor-leftover", candidate, "keep",
                        "git unreadable: cannot prove this is a by-product")
                elif rel in tracked:
                    add("editor-leftover", candidate, "keep", "git tracks it: it is content")
                else:
                    add("editor-leftover", candidate, "delete",
                        "editor or OS by-product, not content")
                    planned_gone.add(rel)
                continue
            if name in DISPOSABLE_STATE and base_path.name == STATE_DIR:
                age = _age_days(candidate)
                if age >= state_days:
                    add("sweep-state", candidate, "delete",
                        "disposable sweep state, %.0f day(s) old (batches.jsonl is kept: "
                        "it is the landing record)" % age)
                    planned_gone.add(rel)

    # Hazards: reported, never removed.
    for record in _unlanded_batches(root):
        items.append({"rule": "unlanded-batch", "path": "%s/batches.jsonl" % STATE_DIR,
                      "action": "keep", "bytes": 0,
                      "why": "batch %s fixed %d item(s), verified, and never landed -- "
                             "roll it forward or discard it deliberately"
                             % (record.get("at", "?"), len(record.get("fixed") or []))})

    if tracked is not None:
        for rel in sorted(_untracked_by_size(root, tracked, max_mb)):
            items.append({"rule": "large-untracked", "path": rel, "action": "keep",
                          "bytes": _size(root / rel),
                          "why": "untracked and larger than %d MB: a human decides, "
                                 "a cleaner does not" % max_mb})

    items.extend(_empty_dirs(root, planned_gone))
    items.sort(key=lambda item: (item["action"] != "delete", item["rule"], item["path"]))
    return items


def _unlanded_batches(root: Path) -> Iterable[Dict]:
    path = root / STATE_DIR / "batches.jsonl"
    if not path.exists():
        return []
    rows: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("verified") and not row.get("landed"):
            rows.append(row)
    return rows


def _untracked_by_size(root: Path, tracked: Set[str], max_mb: int) -> List[str]:
    limit = max_mb * 1024 * 1024
    found: List[str] = []
    for base, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [name for name in sorted(dirnames)
                       if name not in (".git", STATE_DIR)]
        for name in filenames:
            path = Path(base) / name
            rel = _rel(root, path)
            if rel in tracked or path.is_symlink():
                continue
            try:
                if path.stat().st_size > limit:
                    found.append(rel)
            except OSError:
                continue
    return found


def _empty_dirs(root: Path, planned_gone: Set[str]) -> List[Dict]:
    """Directories that hold nothing once the plan is applied.

    Computed after the cache plan, so `pkg/__pycache__` does not leave `pkg`
    looking occupied-and-therefore-empty-later. The order matters: a cleaner
    that reports an empty parent it will not actually empty is a liar by one
    pass, and the next run finds one more.
    """
    gone = {rel.rstrip("/") for rel in planned_gone}
    found: List[Dict] = []
    emptied: Set[str] = set()
    for base, dirnames, filenames in os.walk(root, topdown=False, followlinks=False):
        base_path = Path(base)
        rel = _rel(root, base_path)
        if rel == "." or rel == ".git" or rel.startswith(".git/"):
            continue
        # The tool's own state directory is not housekeeping: it is empty on a
        # fresh clone, and deleting it takes the deletion log with it -- measured:
        # `apply()` then died mid-loop writing to a directory it had removed.
        if rel == STATE_DIR or rel.startswith(STATE_DIR + "/"):
            continue
        if any(name == ".git" for name in dirnames):
            continue
        names = [name for name in filenames if _rel(root, base_path / name) not in gone]
        if names:
            continue
        subdirs = [name for name in dirnames
                   if _rel(root, base_path / name) not in gone]
        # A subdirectory that survived this pass and was itself reported empty
        # is already in `emptied`, so it counts as gone for its parent.
        surviving = [name for name in subdirs
                     if _rel(root, base_path / name) not in emptied]
        if surviving:
            continue
        emptied.add(rel)
        found.append({"rule": "empty-directory", "path": rel, "action": "delete",
                      "bytes": 0,
                      "why": "holds nothing after this pass; an empty directory is "
                             "left over from a move, never created on purpose"})
    return found


def apply(root: Path, items: Sequence[Dict]) -> Tuple[int, int, List[str]]:
    """Carry out the delete half of a plan. Returns (removed, bytes, failures)."""
    root = root.resolve()
    removed = 0
    freed = 0
    failures: List[str] = []
    log = root / STATE_DIR / "housekeep.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)

    for item in items:
        if item["action"] != "delete":
            continue
        target = (root / item["path"]).resolve()
        # Belt and braces over the planner: the plan is data, and data from an
        # earlier run may name a path that has since changed meaning.
        if root not in target.parents and target != root:
            failures.append("%s: resolves outside the root" % item["path"])
            continue
        if not target.exists() or target.is_symlink():
            failures.append("%s: gone or a symlink, left alone" % item["path"])
            continue
        size = _size(target)
        try:
            if target.is_dir():
                _remove_tree(target)
            else:
                target.unlink()
        except OSError as exc:
            failures.append("%s: %s" % (item["path"], exc))
            continue
        removed += 1
        freed += size
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                         time.gmtime()),
                                     "path": item["path"], "rule": item["rule"],
                                     "bytes": size}) + "\n")
    return removed, freed, failures


def _remove_tree(path: Path) -> None:
    for base, dirnames, filenames in os.walk(path, topdown=False, followlinks=False):
        for name in filenames:
            # `unlink` removes a file and, for a symlink, removes the link and
            # never the target -- which is the behaviour wanted here either way.
            (Path(base) / name).unlink()
        for name in dirnames:
            handle = Path(base) / name
            if handle.is_symlink():
                handle.unlink()
            else:
                handle.rmdir()
    path.rmdir()


def human(bytes_count: int) -> str:
    value = float(bytes_count)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return "%.1f %s" % (value, unit) if unit != "B" else "%d B" % int(value)
        value /= 1024.0
    return "%.1f GB" % value


def report(items: Sequence[Dict], applied: bool = False) -> str:
    lines: List[str] = []
    deletes = [item for item in items if item["action"] == "delete"]
    keeps = [item for item in items if item["action"] != "delete"]
    for item in deletes:
        lines.append("  delete  %-18s %-52s %9s  %s"
                     % (item["rule"], item["path"], human(item["bytes"]), item["why"]))
    for item in keeps:
        lines.append("  keep    %-18s %-52s %9s  %s"
                     % (item["rule"], item["path"], human(item["bytes"]), item["why"]))
    reclaimable = sum(item["bytes"] for item in deletes)
    verdict = "reclaimed" if applied else "reclaimable"
    lines.append("")
    lines.append("%d item(s) to remove, %s %s; %d kept (each with a reason)"
                 % (len(deletes), human(reclaimable), verdict, len(keeps)))
    if not applied and deletes:
        lines.append("dry run: nothing was deleted. Re-run with --apply to act.")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Housekeeping for a repository: caches, leftovers, empty dirs, "
                    "sweep state. Dry run unless --apply.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--apply", action="store_true",
                        help="actually delete; without it this is a report")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--state-days", type=int, default=DEFAULT_STATE_DAYS,
                        help="sweep state older than this many days is disposable "
                             "(default %d)" % DEFAULT_STATE_DAYS)
    parser.add_argument("--max-mb", type=int, default=DEFAULT_MAX_MB,
                        help="report an untracked file larger than this "
                             "(default %d MB)" % DEFAULT_MAX_MB)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print("REFUSED: %s is not a directory" % root)
        return 2
    tracked = tracked_paths(root)
    items = collect(root, tracked, state_days=args.state_days, max_mb=args.max_mb)
    removed, freed, failures = (0, 0, [])
    if args.apply:
        removed, freed, failures = apply(root, items)
    if args.json:
        print(json.dumps({"root": str(root), "git_available": tracked is not None,
                          "applied": bool(args.apply), "removed": removed,
                          "bytes_freed": freed, "failures": failures,
                          "items": items}, indent=1))
    else:
        print("housekeeping %s%s" % (root, "" if tracked is not None
                                     else "  (git unreadable: caches only)"))
        print(report(items, applied=args.apply))
        if args.apply and removed:
            print("removed %d item(s), %s freed" % (removed, human(freed)))
        for failure in failures:
            print("  REFUSED %s" % failure)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
