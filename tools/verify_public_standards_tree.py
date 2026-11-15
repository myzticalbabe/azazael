#!/usr/bin/env python3
"""Apply verify_public_standards.py to every publication root in this monorepo.

`verify_public_standards.py` answers "does THIS repository root meet
PROFESSIONAL_PUBLIC_STANDARDS.md".  This tree is a monorepo: its own root is not
one of the twenty published repositories and never will carry per-project
governance files (HARDWARE.md, requiem.py, PUBLIC_MANIFEST.json).  Running the
checker against `.` here is therefore a category error -- it reports 14 missing
files that cannot exist at that path.

So this driver runs the *same* checker, unchanged, against each directory that
declares itself a publication root by carrying a PUBLIC_MANIFEST.json, and
aggregates the verdict.  It defines no rules of its own: every item it prints
comes from verify_public_standards.verify_repo(), so the standard stays in one
place and this file cannot drift from it.

Exit 0 only when at least one publication root was found and every one of them
passed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from verify_public_standards import REQUIRED_GOVERNANCE, REQUIRED_TEMPLATES
from verify_public_standards import REQUIRED_WORKFLOWS, verify_repo

PASS_LINE = "PASS -- Repository meets all professional standards"
BAR = "=" * 66


def publication_roots(root: Path) -> list[Path]:
    return sorted(
        candidate.parent
        for candidate in root.glob("*/PUBLIC_MANIFEST.json")
        if candidate.is_file()
    )


def tracked_files(root: Path) -> set[str] | None:
    """Repository-relative paths git knows about, or None if git is unavailable."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p.replace("\\", "/") for p in out.decode("utf-8", "replace").split("\0") if p}


def uncommitted_required(project: Path, root: Path, tracked: set[str]) -> list[str]:
    """Required files that exist on disk but are not in the repository.

    verify_repo() asks whether a file exists, which is the right question for a
    gate that runs after `tools/publicize.py`. It is not enough on its own: a
    required file that only exists in someone's working tree makes this driver
    print PASS for a tree that a fresh clone renders FAIL. That gap is how six
    scaffolds came to carry verbatim copies of another project's ci.yml without
    anything objecting -- so it is reported here rather than inferred by hand.
    """
    out: list[str] = []
    for name in (*REQUIRED_GOVERNANCE, *REQUIRED_WORKFLOWS, *REQUIRED_TEMPLATES):
        if not (project / name).exists():
            continue
        rel = (project / name).relative_to(root).as_posix()
        if rel not in tracked:
            out.append(name)
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    if not root.is_dir():
        print(f"FAIL -- not a directory: {root}")
        return 2

    roots = publication_roots(root)
    if not roots:
        print(f"FAIL -- no */PUBLIC_MANIFEST.json under {root}; nothing verified")
        return 1

    print(f"verify_public_standards_tree: {root}")
    print(f"  {len(roots)} publication root(s)")

    tracked = tracked_files(root)
    uncommitted: list[tuple[str, list[str]]] = []
    unmet: list[tuple[str, list[str]]] = []
    graded: list[tuple[Path, dict]] = []
    for project in roots:
        result = verify_repo(project)
        graded.append((project, result))
        if result.get("error"):
            unmet.append((project.name, [f"error:{result['error']}"]))
        elif not result["ok"]:
            unmet.append((project.name, list(result["missing"])))

    # Per-root detail, grouped so a log reader sees which project owns what.
    for project, result in graded:
        governance = sum(1 for ok in result.get("governance", {}).values() if ok)
        workflows = sum(1 for ok in result.get("workflows", {}).values() if ok)
        templates = sum(1 for ok in result.get("templates", {}).values() if ok)
        verdict = "PASS" if result.get("ok") else "FAIL"
        print(
            f"  {verdict} {project.name:32s} "
            f"governance {governance}/{len(result.get('governance', {}))} "
            f"workflows {workflows}/{len(result.get('workflows', {}))} "
            f"templates {templates}/{len(result.get('templates', {}))} "
            f"cross-repo {result.get('cross_repo_table')}"
        )
        for item in result.get("missing", []):
            print(f"       MISSING {project.name}: {item}")
        if tracked is not None:
            loose = uncommitted_required(project, root, tracked)
            if loose:
                uncommitted.append((project.name, loose))
                print(
                    f"       NOT COMMITTED {project.name}: {len(loose)} required "
                    f"file(s) exist only in the working tree "
                    f"({', '.join(loose)})"
                )

    print(BAR)
    if uncommitted:
        total = sum(len(items) for _, items in uncommitted)
        print(
            f"WARN -- {len(uncommitted)} root(s) meet the standard on disk with "
            f"{total} required file(s) that are untracked; a fresh clone of "
            f"those roots would FAIL this same check."
        )
        for name, items in uncommitted:
            print(f"  - {name}: {len(items)} untracked")
        print(BAR)
    if unmet:
        print(f"FAIL -- {len(unmet)} of {len(roots)} publication root(s) unmet:")
        for name, items in unmet:
            print(f"  - {name}: {len(items)} item(s)")
        return 1

    print(PASS_LINE)
    print(f"  {len(roots)} publication root(s) verified")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
