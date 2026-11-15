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

import sys
from pathlib import Path

from verify_public_standards import verify_repo

PASS_LINE = "PASS -- Repository meets all professional standards"
BAR = "=" * 66


def publication_roots(root: Path) -> list[Path]:
    return sorted(
        candidate.parent
        for candidate in root.glob("*/PUBLIC_MANIFEST.json")
        if candidate.is_file()
    )


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
