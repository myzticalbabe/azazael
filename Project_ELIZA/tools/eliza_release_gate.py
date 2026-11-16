#!/usr/bin/env python3
# coding: utf-8
"""Fail a publication whose paperwork, allowlist or disclosures are incomplete.

WHY THIS IS A GATE AND NOT A CHECKLIST
--------------------------------------
Publishing is the one operation in this project that cannot be undone. Three
failure modes are all silent, and each one is mechanical enough to check:

  1. **A missing community file.** GitHub's own community-profile checklist
     defines the set (README, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY,
     issue templates with valid keys, PR template). A repository without them is
     not read as minimal; it is read as abandoned.
  2. **Fails-open evidence.** A deny-list ships whatever nobody remembered to
     add. So publication is an ALLOWLIST: every shipped path must be declared in
     PUBLIC_MANIFEST.json, and an undeclared path above the size floor fails.
  3. **A silent secret.** One key in one file is the whole cost of the mistake.

And one check exists for a reason that is not mechanical. `--require-disclosure`
fails when the README has lost its Limitations section. This project's crisis
router measured **0.18 recall on one holdout and 0.83 on another**; a public therapeutic
project that hides that number is worse than one that does not exist, because a
reader would trust it. The gate refuses to let the disclosure be deleted.

Usage:
  python tools/eliza_release_gate.py --check
  python tools/eliza_release_gate.py --check --json
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
#: The gate runs in two layouts: the monorepo, where the public tree is a
#: subdirectory, and the materialised public tree itself, where it is the root.
#: Resolving by existence rather than by rewriting keeps one copy of the file
#: honest in both -- a rewrite applied at copy time is a second version of the
#: gate that nobody tests.
PROJECT = ROOT / "Project_ELIZA" if (ROOT / "Project_ELIZA").is_dir() else ROOT
MANIFEST = PROJECT / "PUBLIC_MANIFEST.json"

#: GitHub's community-profile checklist, plus the four files this project adds
#: because a forensic-adjacent project owes a reader more than a code README.
REQUIRED_FILES: Tuple[str, ...] = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "DISCLOSURE_POLICY.md",
    "PUBLIC_MANIFEST.json",
    "docs/index.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
)

#: Headings the README must carry. Limitations and the negative results are
#: required, not encouraged -- see the module docstring.
README_REQUIRED_HEADINGS: Tuple[str, ...] = (
    "## What this is",
    "## What this is not",
    "## Limitations",
    "## Negative results and open problems",
    "## Ethics",
    "## Status",
)

#: Issue templates must carry these keys in their frontmatter. GitHub's checklist
#: reads them, so a template without them shows as MISSING in the profile even
#: though the file exists -- a failure that looks like success.
ISSUE_TEMPLATE_KEYS: Tuple[str, ...] = ("name:", "description:")

SECRET_PATTERNS: Tuple[Tuple[str, str], ...] = (
    ("private_key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("aws_access_key", r"\bAKIA[0-9A-Z]{16}\b"),
    ("github_token", r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    ("slack_token", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ("openai_key", r"\bsk-[A-Za-z0-9]{32,}\b"),
    ("assigned_secret", r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*"
                        r"[\"']?[A-Za-z0-9_\-]{16,}[\"']?"),
)

#: Extensions worth reading for secrets. Binary and vendored blobs are skipped.
TEXT_SUFFIXES = (".py", ".md", ".json", ".yml", ".yaml", ".cff", ".toml", ".cfg",
                 ".ini", ".txt", ".sh", ".js", ".ts", ".html")

#: Files below this size are not demanded in the manifest: a licence, a template
#: or a small config is not where evidence hides.
MANIFEST_SIZE_FLOOR = 4096

#: A git inventory that takes longer than this is not a reading, it is a hang.
INVENTORY_TIMEOUT_S = 120

#: Why a git-based inventory could not be taken, when it could not. Returned and
#: printed with the report, so a fallback reading is never presented as the wider
#: one (HED-9: a denominator is part of the reading).
_INVENTORY_NOTES: List[str] = []


def load_manifest(path: Path = MANIFEST) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_required_files(project: Path = PROJECT) -> List[str]:
    missing = []
    for relative in REQUIRED_FILES:
        if not (project / relative).exists():
            missing.append(relative)
    return missing


def check_readme_disclosure(project: Path = PROJECT) -> List[str]:
    """The Limitations section is load-bearing, so its absence is a failure."""
    readme = project / "README.md"
    if not readme.exists():
        return ["README.md is absent"]
    text = readme.read_text(encoding="utf-8")
    return ["README.md is missing the %r section" % heading
            for heading in README_REQUIRED_HEADINGS if heading not in text]


def check_issue_templates(project: Path = PROJECT) -> List[str]:
    problems = []
    directory = project / ".github" / "ISSUE_TEMPLATE"
    for path in sorted(directory.glob("*.yml")) + sorted(directory.glob("*.md")):
        if path.name == "config.yml":
            continue
        text = path.read_text(encoding="utf-8")
        for key in ISSUE_TEMPLATE_KEYS:
            if not re.search(r"(?m)^%s" % re.escape(key), text):
                problems.append("%s lacks frontmatter key %r" % (path.name, key))
    return problems


def check_manifest_paths(manifest: Dict, project: Path = PROJECT) -> Tuple[List[str], List[str]]:
    """Every declared path exists, and no declared path matches a deny rule."""
    problems: List[str] = []
    denied: List[str] = []
    for entry in manifest.get("ship", []):
        source = (project / entry["from"]).resolve()
        if not source.exists():
            problems.append("manifest declares a path that does not exist: %s"
                            % entry["from"])
            continue
        if _denied(str(source), manifest):
            denied.append("%s matches a never_ship rule" % entry["from"])
    return problems, denied


def _denied(path_text: str, manifest: Dict) -> bool:
    lowered = path_text.replace("\\", "/").lower()
    if any(token.lower() in lowered for token in manifest.get("deny_substrings", [])):
        return True
    name = Path(lowered).name
    for rule in manifest.get("never_ship", []):
        glob = rule["glob"].lower()
        if fnmatch.fnmatch(name, glob) or fnmatch.fnmatch(lowered, "*/" + glob):
            return True
    return False


def scan_secrets(path: Path) -> List[Dict]:
    """Report secret-shaped text with the value masked.

    The finding names the file and line and the RULE, never the secret: a scanner
    that prints what it found has copied the secret into the log.
    """
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                findings.append({"file": str(path), "line": number, "rule": name,
                                 "masked": match.group(0)[:4] + "..." + "(%d chars)"
                                 % len(match.group(0))})
    return findings


def _git_ls(root: Path, spec: str, flags: List[str]) -> Optional[List[Path]]:
    """Paths `git ls-files` reports under `spec`, or None when git cannot answer."""
    try:
        out = subprocess.run(
            ["git", "ls-files", *flags, "--exclude-standard", "-z", "--", spec],
            cwd=str(root), capture_output=True, timeout=INVENTORY_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        _INVENTORY_NOTES.append("git ls-files %s failed: %s: %s"
                                % (" ".join(flags), type(exc).__name__, exc))
        return None
    if out.returncode != 0:
        _INVENTORY_NOTES.append(
            "git ls-files %s exits %d: %s"
            % (" ".join(flags), out.returncode,
               out.stderr.decode("utf-8", "replace").strip()[:200]))
        return None
    text = out.stdout.decode("utf-8", "replace")
    return [(root / chunk).resolve() for chunk in text.split("\0") if chunk]


def publication_inventory(project: Path = PROJECT) -> Tuple[List[Path], str, int]:
    """The files the repository carries, plus how that set was decided.

    A walk of the working tree counts a git-ignored local mirror as published
    content. Measured 2026-11-14: `Project_ELIZA/adopted/kali` holds 2,529 files
    that `Project_ELIZA/.gitignore:10` excludes, and the walk asked the manifest
    to declare every one of them -- 2,047 undeclared findings, none of which the
    repository contains. Publication is about what the REPOSITORY carries, so the
    inventory is `git ls-files -c -o --exclude-standard`: tracked files, plus
    untracked files that are not ignored.

    The materialised public tree is not a repository, so the walk stays as the
    fallback. Which one ran is returned and printed, and the ignored count is
    returned with it: an inventory that hides how much it skipped is a defect in
    the reading.
    """
    del _INVENTORY_NOTES[:]
    top = None
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(project), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=INVENTORY_TIMEOUT_S,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            top = proc.stdout.strip()
        else:
            _INVENTORY_NOTES.append("git rev-parse exits %d: %s"
                                    % (proc.returncode, proc.stderr.strip()[:200]))
    except (OSError, subprocess.SubprocessError) as exc:
        _INVENTORY_NOTES.append("git rev-parse failed: %s: %s"
                                % (type(exc).__name__, exc))
    if top:
        root = Path(top).resolve()
        try:
            spec = str(project.resolve().relative_to(root))
        except ValueError:
            _INVENTORY_NOTES.append("%s is not under the git root %s"
                                    % (project, root))
        else:
            carried = _git_ls(root, spec, ["-c", "-o"])
            ignored = _git_ls(root, spec, ["-o", "-i"])
            if carried is not None:
                excluded = len(ignored) if ignored is not None else 0
                return ([p for p in carried if ".git" not in p.parts],
                        "git", excluded)
    files = [p.resolve() for p in sorted(project.rglob("*"))
             if p.is_file() and ".git" not in p.parts]
    return files, "filesystem", 0


def check_undeclared(manifest: Dict, project: Path = PROJECT,
                     files: Optional[List[Path]] = None) -> List[str]:
    """Files above the size floor that no manifest entry claims.

    This is the half that fails CLOSED: a new evidence directory shows up here
    the moment it is added, without anyone remembering to deny it.

    A `never_ship` match counts as claimed. The manifest has decided about such a
    file, and demanding a `ship` entry for a path the same file forbids
    publishing would be asking for a contradiction -- measured 2026-11-14:
    `tools/bcc_bypass.py` matched the `bcc_*.py` deny rule and was still reported
    undeclared.
    """
    if files is None:
        files = publication_inventory(project)[0]
    declared = set()
    for entry in manifest.get("ship", []):
        source = (project / entry["from"]).resolve()
        declared.add(source)
        # The DESTINATION of a declared entry is declared by definition. Leaving
        # it out made every materialised tree fail its own gate: `publicize.py`
        # wrote eliza/psyche/affect.py exactly as the manifest said, and the gate
        # then called it undeclared, because only `from` was collected. The
        # monorepo looked clean only because nothing had been materialised yet.
        declared.add((project / str(entry["to"])).resolve())
        if source.exists() and source.is_dir():
            declared.update(p.resolve() for p in source.rglob("*") if p.is_file())
    problems = []
    for path in sorted(files):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        # Byte-compiled, cached and build output is not content: it is derived
        # from declared files and differs per interpreter. Demanding it be
        # declared would produce a manifest that no longer means anything.
        if any(part in {"__pycache__", ".pytest_cache", ".mypy_cache",
                        ".ruff_cache", "build", "dist"} for part in path.parts):
            continue
        if path.suffix == ".pyc" or ".egg-info" in str(path):
            continue
        if path.stat().st_size < MANIFEST_SIZE_FLOOR:
            continue
        resolved = path.resolve()
        if resolved in declared or _denied(str(resolved), manifest):
            continue
        problems.append("undeclared file above %d bytes: %s"
                        % (MANIFEST_SIZE_FLOOR, path.relative_to(project)))
    return problems


def run_checks(project: Path = PROJECT, manifest_path: Optional[Path] = None) -> Dict:
    manifest = load_manifest(manifest_path or MANIFEST)
    missing = check_required_files(project)
    disclosure = check_readme_disclosure(project)
    templates = check_issue_templates(project)
    manifest_problems, denied = check_manifest_paths(manifest, project)
    inventory, inventory_source, ignored_excluded = publication_inventory(project)
    undeclared = check_undeclared(manifest, project, inventory)
    secrets_found: List[Dict] = []
    for path in sorted(inventory):
        if path.is_file():
            secrets_found.extend(scan_secrets(path))
    checks = {
        "required_files": missing,
        "readme_disclosure": disclosure,
        "issue_templates": templates,
        "manifest_paths": manifest_problems,
        "denied_paths": denied,
        "undeclared_files": undeclared,
        "secrets": secrets_found,
    }
    failures = sum(len(v) for v in checks.values())
    return {"project": str(project),
            "inventory": {"source": inventory_source, "files": len(inventory),
                          "ignored_excluded": ignored_excluded,
                          "notes": list(_INVENTORY_NOTES)},
            "checks": checks, "failures": failures,
            "result": "PASS" if failures == 0 else "FAIL"}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--project", default=str(PROJECT))
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = run_checks(Path(args.project),
                        Path(args.manifest) if args.manifest else None)
    if args.json:
        print(json.dumps(report, indent=1))
    else:
        print("eliza publication gate -- %s" % report["project"])
        seen = report["inventory"]
        if seen["source"] == "git":
            print("  %-18s git: %d file(s), tracked plus untracked-not-ignored; "
                  "%d ignored file(s) not scanned"
                  % ("inventory", seen["files"], seen["ignored_excluded"]))
        else:
            print("  %-18s filesystem walk: %d file(s); git answered nothing (%s)"
                  % ("inventory", seen["files"],
                     "; ".join(seen["notes"]) or "no reason recorded"))
        for name, findings in report["checks"].items():
            status = "ok" if not findings else "%d problem(s)" % len(findings)
            print("  %-18s %s" % (name, status))
            for finding in findings[:12]:
                print("      %s" % (finding if isinstance(finding, str)
                                    else json.dumps(finding)))
        print("\n%s: %d failure(s)" % (report["result"], report["failures"]))
        if report["failures"]:
            print("Publication is blocked. An undeclared file is not necessarily "
                  "forbidden -- declare it in PUBLIC_MANIFEST.json, or remove it.")
    return 0 if report["failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
