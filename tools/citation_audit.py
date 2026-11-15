#!/usr/bin/env python3
"""Citation audit -- a path named in prose is either present or declared gone.

The class this catches, measured 2026-11-14 on this tree: canon named
``yggdrasil_forest/render_tree.py`` in AGENTS.md and in
docs/agent_orders/04_domain_trees.md, and eight board rows asked for renders by
that tool. No such file existed under any root that was searched, and
``forest_manifest.json`` carried a note asserting the tool draws any descriptor.
Prose that names an instrument is a pointer; a pointer nobody resolved is
indistinguishable from an instrument until someone runs ``find``.

What counts as a citation: an inline-code token (backticks) containing a
directory separator and ending in a known extension. What does not count: a
URL, a wildcard, a bare filename, or a token on a line that already declares the
thing absent -- a citation that says it is gone is not a false citation.

Exit: 0 scanned and reported (advisory), 1 under --strict when a citation does
not resolve, 2 when nothing could be scanned (which is not a pass).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

#: Wall bound the deep-dive leg reads off this module. Measured 2026-11-14: 22
#: documents resolve in 0.4 s, so 60 s is the shape of a hang, not of a slow read.
BUDGET_S = 60

#: Canon and lane documents. Deliberately not `docs/**` wholesale: a historical
#: report is allowed to name files that no longer exist, and auditing it would
#: report the archive rather than the obligation.
SURFACES = (
    "AGENTS.md", "CLAUDE.md", "MANDATES.md", "SOP.md", "SYSTEM_INSTRUCTIONS.md",
    "docs/agent_orders/*.md", "docs/HANDOFF_*.md",
)

EXTENSIONS = {".py", ".sh", ".ps1", ".bat", ".cmd", ".json", ".md", ".toml",
              ".yml", ".yaml", ".csv"}

#: A line that already says the thing is absent is not a false citation.
#: "exists nowhere" was added after the first run flagged MANDATES.md's own
#: sentence saying exactly that -- the marker set is vocabulary, and a vocabulary
#: missing the phrase canon actually uses reports a correct line as a defect.
DECLARED_GONE = ("archived", "does not exist", "exists nowhere", "nowhere on",
                 "no longer", "removed", "deleted", "dead", "absent", "missing")

TOKEN = re.compile(r"`([^`\n]{3,160})`")

#: A dated report is a snapshot of what was true when it was written; holding it to
#: today's tree makes the archive report itself. This is the docstring's own rule
#: made executable -- measured 2026-11-14, three of the five residual findings sat
#: in two dated upgrade reports, which name files that existed on their date.
DATED_REPORT = re.compile(r"_\d{4}-\d{2}-\d{2}\.md$")


def looks_like_path(token: str) -> bool:
    """A citation needs a separator, a known extension, and no wildcard."""
    if any(ch in token for ch in "<>*{}|") or " " in token or "://" in token:
        return False
    if "/" not in token and "\\" not in token:
        return False
    return Path(token.replace("\\", "/")).suffix.lower() in EXTENSIONS


def src_dirs() -> set[str]:
    """Top-level package names under ``src/``, read from the tree."""
    src = ROOT / "src"
    if not src.is_dir():
        return set()
    return {p.name for p in src.iterdir() if p.is_dir()}


def resolves(token: str) -> tuple[str, str]:
    """Resolve against every base this corpus actually cites from.

    Returns ``(state, basis)`` where state is one of ``resolved``,
    ``unresolved`` or ``other-os``. The third state exists because an absence
    claim has to name the surface it was made on: measured 2026-11-14, the first
    version reported ``/root/PYTHON_CONSOLIDATION_2026-09-30.md`` as "does not
    resolve" from a Windows resolver, which says nothing about the Kali lane it
    belongs to. Unverifiable is reported and never counted as a defect.

    Measured on the same run: 94 tokens reported unresolved, and the largest
    group was ``azazael/MANDATES.md``-shaped -- canon written from
    ``C:/Azazael``, one level ABOVE this repo root -- so a repo-only resolver
    called ~70 correct citations broken. The second group was ``CORE/x``-shaped,
    which canon uses for ``src/CORE/x``. Both are conventions, so they are
    resolution bases here instead of findings.
    """
    raw = token.replace("\\", "/")
    if raw.startswith("~"):
        ok = Path(raw).expanduser().exists()
        return ("resolved" if ok else "unresolved"), "home-relative"
    candidate = Path(raw)
    # Checked BEFORE is_absolute(): on Windows `Path("/root/x").is_absolute()`
    # is False (no drive), so the POSIX branch never fired while this test sat
    # inside the absolute branch -- measured 2026-11-14, the token still fell
    # through to a drive-relative join and came back "does not resolve". `//` is
    # excluded because a UNC share is a real Windows path.
    if raw.startswith("/") and not raw.startswith("//") and os.name == "nt":
        if candidate.exists():
            return "resolved", "absolute"
        return "other-os", "/ (POSIX lane, not mounted here)"
    if candidate.is_absolute():
        return ("resolved" if candidate.exists() else "unresolved"), "absolute"
    for base in (ROOT, ROOT.parent, HOME):
        if (base / raw).exists():
            return "resolved", str(base)
    head = raw.split("/", 1)[0]
    if head in src_dirs() and (ROOT / "src" / raw).exists():
        return "resolved", str(ROOT / "src")
    return "unresolved", ""


def surfaces() -> list[Path]:
    found: list[Path] = []
    for pattern in SURFACES:
        found.extend(sorted(ROOT.glob(pattern)))
    return [p for p in found
            if p.is_file() and not DATED_REPORT.search(p.name)]


def audit_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        findings.append({"file": str(path), "line": 0, "token": "",
                         "reason": "unreadable: %s" % exc})
        return findings
    for lineno, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in DECLARED_GONE):
            continue
        for token in TOKEN.findall(line):
            token = token.strip()
            if not looks_like_path(token):
                continue
            state, basis = resolves(token)
            if state != "resolved":
                findings.append({"file": path.relative_to(ROOT).as_posix(),
                                 "line": lineno, "token": token,
                                 "reason": ("does not resolve"
                                            if state == "unresolved"
                                            else "not checkable from this OS"),
                                 "state": state, "basis": basis,
                                 "bases": [str(ROOT), str(ROOT.parent), str(HOME),
                                           str(ROOT / "src") + " (src/<pkg>/...)"]})
    return findings


def classify_ignored(tokens: list[str], notes: list[str]) -> set[str]:
    """Citations a .gitignore rule covers: runtime artifacts, not broken pointers.

    Measured 2026-11-14: `docs/agent_orders/05_hyper_edge_defaults.md` cites
    `logs/golden_arrow_staged.json` while describing what `--staged` writes, and
    `logs/` is deliberately untracked -- so "does not resolve" accused canon of
    naming a file that is produced on demand, and a presence test can never
    settle it. The state is NAMED and COUNTED rather than dropped: a citation
    quietly removed from the denominator is HED-9's defect.
    """
    if not tokens:
        return set()
    try:
        proc = subprocess.run(["git", "check-ignore", "--stdin"], cwd=str(ROOT),
                              input="\n".join(tokens), capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        notes.append("git check-ignore unavailable (%s)" % type(exc).__name__)
        return set()
    if proc.returncode not in (0, 1):
        notes.append("git check-ignore exit %d" % proc.returncode)
        return set()
    return {line.strip() for line in (proc.stdout or "").splitlines()
            if line.strip()}


def run(strict: bool = False) -> tuple[int, list[dict], dict]:
    files = surfaces()
    if not files:
        print("citation_audit: no surface matched -- nothing scanned")
        return 2, [], {"scanned": 0}
    findings: list[dict] = []
    for path in files:
        findings.extend(audit_file(path))
    notes: list[str] = []
    ignored = classify_ignored(
        [f["token"] for f in findings if f["state"] == "unresolved"], notes)
    for f in findings:
        if f["state"] == "unresolved" and f["token"] in ignored:
            f["state"] = "gitignored"
            f["reason"] = ("git-ignored runtime artifact "
                           "(produced on demand, never shipped)")
    unresolved = [f for f in findings if f["state"] == "unresolved"]
    unverifiable = [f for f in findings if f["state"] == "other-os"]
    gitignored = [f for f in findings if f["state"] == "gitignored"]
    stats = {"scanned": len(files), "findings": len(findings),
             "unresolved": len(unresolved), "unverifiable": len(unverifiable),
             "gitignored": len(gitignored)}
    for f in findings:
        if f["state"] == "gitignored":
            continue
        print("  %s:%d  %s  (%s)" % (f["file"], f["line"], f["token"],
                                    f["reason"]))
    for note in notes:
        print("  NOTE %s" % note)
    print("citation_audit: %d file(s), %d citation(s) unresolved, "
          "%d unverifiable, %d git-ignored, %d finding(s) "
          "| bases: repo, parent, home, src/<pkg>"
          % (len(files), len(unresolved), len(unverifiable), len(gitignored),
             len(unresolved) + len(unverifiable)))
    if strict and unresolved:
        return 1, findings, stats
    return 0, findings, stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when a citation does not resolve")
    ap.add_argument("--json", default="", help="write findings to this path")
    args = ap.parse_args(argv)
    code, findings, stats = run(strict=args.strict)
    if args.json:
        import json
        Path(args.json).write_text(json.dumps({"stats": stats,
                                               "findings": findings}, indent=2),
                                   encoding="utf-8")
    return code


if __name__ == "__main__":
    sys.exit(main())
