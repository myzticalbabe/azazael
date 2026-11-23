#!/usr/bin/env python3
"""Scaffold a SOUL LICENCE ONLY repo shell from monorepo canonicals.

Usage: soul_repo_scaffold.py <target-dir> <repo-name>

Creates the proven gate-shell shape (checker + audits + gate workflow +
licence declarations + bytecode-proof .gitignore) so a newly adopted or
minted repo can never be born without the triple gate or without
__pycache__ exclusion (measured 2026-11-23: all five stem/audit adoptions
needed a post-hoc .gitignore because no template existed).

Copies canonicals VERBATIM from this monorepo (LICENSE excepted: the
licence text itself instructs replacing the Author and Source fields, so
the Source line is repointed at the new repo). Generated files
(CITATION.cff, PUBLIC_MANIFEST.json, .gitignore, README.md) carry the
repo name. Stdlib only. Never touches the network, never inits git.
"""
import shutil
import sys
from pathlib import Path

MONOREPO = Path(__file__).resolve().parents[1]
COPY_FILES = [
    "tools/soul_licence_check.py",
    "tools/audit_inclusion.py",
    "tools/audit_accessibility.py",
    ".github/workflows/soul-forge-gate.yml",
    "REUSE.toml",
]
GITIGNORE = """\
# Bytecode and build outputs are regenerable: never track them.
# (Measured 2026-11-23: adoptions staged verbatim worktrees tracked
# __pycache__ because their shells had no exclusion.)
__pycache__/
*.pyc
dist/
*.egg-info/
.venv/
"""
README_TMPL = """\
# {repo}

SOUL LICENCE ONLY -- this repository is licensed under the
Soul Forge License v1.0 (`LICENSE`, `LicenseRef-SoulForge-1.0`).
"""
CITATION_TMPL = """\
cff-version: 1.2.0
title: {repo}
authors:
  - name: myzticalbabe
license: LicenseRef-SoulForge-1.0
repository-code: https://github.com/myzticalbabe/{repo}
"""
MANIFEST_TMPL = """\
{{
  "name": "{repo}",
  "version": "0.1.0",
  "description": "{repo} repository",
  "repository": {{
    "type": "git",
    "url": "https://github.com/myzticalbabe/{repo}.git"
  }},
  "homepage": "https://github.com/myzticalbabe/{repo}",
  "license": "LicenseRef-SoulForge-1.0",
  "author": "myzticalbabe"
}}
"""


def scaffold(target: Path, repo: str) -> list[str]:
    written: list[str] = []
    target.mkdir(parents=True, exist_ok=True)
    lic = (MONOREPO / "LICENSE").read_text(encoding="utf-8")
    lic = lic.replace(
        "Source: https://github.com/myzticalbabe/azazael",
        f"Source: https://github.com/myzticalbabe/{repo}",
    )
    (target / "LICENSE").write_text(lic, encoding="utf-8")
    written.append("LICENSE")
    for rel in COPY_FILES:
        src = MONOREPO / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        written.append(rel)
    (target / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (target / "README.md").write_text(
        README_TMPL.format(repo=repo), encoding="utf-8"
    )
    (target / "CITATION.cff").write_text(
        CITATION_TMPL.format(repo=repo), encoding="utf-8"
    )
    (target / "PUBLIC_MANIFEST.json").write_text(
        MANIFEST_TMPL.format(repo=repo), encoding="utf-8"
    )
    written += [".gitignore", "README.md", "CITATION.cff",
                "PUBLIC_MANIFEST.json"]
    return written


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <target-dir> <repo-name>", file=sys.stderr)
        return 2
    for f in scaffold(Path(argv[1]), argv[2]):
        print(f"  wrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
