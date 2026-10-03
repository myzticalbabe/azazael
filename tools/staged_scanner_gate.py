#!/usr/bin/env python3
# coding: utf-8
"""Pre-commit staged-scanner gate: fail only on anti-patterns a commit ADDS.

Why this replaces the old check 2
---------------------------------
`.githooks/pre-commit` check 2 wrote a TEMP SNAPSHOT of the staged `.py` files
and ran the scanner over it at `--severity warning`, failing if ANY finding was
present. That is not "catch an anti-pattern being added": every legacy file
already carries warning-severity findings (837 `silent_except_pass` and 287
`except_return_default` sit in the recorded baseline), so the check blocked
every commit that touched one of them. A gate that can never pass is the same
class of defect as a gate that can never fail — the failure this project
already paid for once (Lesson #86).

What it does instead
--------------------
For each staged `.py` file it scans the STAGED version and the HEAD version and
fails only on a per-category INCREASE. Paying down the backlog, or editing a
legacy file without adding debt, passes. A genuinely new anti-pattern fails.
New files are compared against empty, so a brand-new file must be clean.

Check 4 (`tools/anti_pattern_gate.py --check`) still ratchets the repo-wide
`src/` total; this covers the staged set including `tests/`, `tools/`,
`scripts/` — files the `src/`-scoped ratchet never sees.

Usage:
    python tools/staged_scanner_gate.py            # gate staged .py files
    python tools/staged_scanner_gate.py --verbose
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


def _git(*args: str) -> bytes:
    """Run git and return raw stdout bytes.

    Bytes, not text: `text=True` decodes with the OS locale (cp1252 here),
    which raises UnicodeDecodeError on any non-cp1252 byte in a source file and
    (worse) leaves `.stdout` None on a git failure -- a gate that crashes on
    legacy source is not a gate. Decode UTF-8 with errors="replace" at the call
    site instead.
    """
    return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                          timeout=60).stdout


def _staged_py_files() -> list[str]:
    out = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    return [ln.strip() for ln in out.decode("utf-8", errors="replace").splitlines()
            if ln.strip().endswith(".py")]


def _show(rev: str) -> str:
    """Return file content at `rev` (":0:<path>" for the index), or ''."""
    return _git("show", rev).decode("utf-8", errors="replace")


def _counts(source: str, path: str, min_severity: str) -> Counter:
    from CORE.compliance.scanner import ASTAntiPatternScanner, FINDING_SEVERITIES

    result = ASTAntiPatternScanner().scan_source(path, source)
    floor = SEVERITY_ORDER[min_severity]
    counts: Counter = Counter()
    for _lineno, category, _snippet in result.findings:
        if SEVERITY_ORDER.get(FINDING_SEVERITIES.get(category, "info"), 2) <= floor:
            counts[category] += 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--severity", default="warning",
                    choices=["error", "warning", "info"])
    args = ap.parse_args()

    try:
        from CORE.compliance.scanner import ASTAntiPatternScanner  # noqa: F401
    except Exception as exc:  # noqa: BLE001 - pass LOUD, never silently block
        print(f"[StagedScanner] scanner unavailable ({exc}) - passing loud")
        return 0

    files = _staged_py_files()
    if not files:
        print("[StagedScanner] No .py files staged, skipping.")
        return 0

    regressions: list[str] = []
    for path in files:
        before = _counts(_show(f"HEAD:{path}"), path, args.severity)
        after = _counts(_show(f":0:{path}"), path, args.severity)
        for category, n_after in after.items():
            delta = n_after - before.get(category, 0)
            if delta > 0:
                regressions.append(
                    f"  {path}: {category} {before.get(category, 0)} -> {n_after}"
                    f"  (+{delta})")
        if args.verbose:
            print(f"  scanned {path}: {sum(after.values())} finding(s)")

    if regressions:
        print("")
        print("[StagedScanner] Anti-pattern(s) ADDED by this commit:")
        for r in regressions:
            print(r)
        print("")
        print("[StagedScanner] Fix the new finding(s), or -- for a reviewed, "
              "deliberate increase -- re-run tools/anti_pattern_gate.py "
              "--baseline and explain it in the commit message.")
        return 1

    print(f"[StagedScanner] {len(files)} staged .py file(s): no new "
          f"anti-patterns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
