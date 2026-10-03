#!/usr/bin/env python3
# coding: utf-8
"""Anti-pattern gate — fail on NEW anti-patterns, over a recorded baseline.

The problem this exists to close
--------------------------------
`reports/ERROR_LESSON_AUDIT_2026-10-03.md` measured the anti-pattern backlog
cluster (54 ERROR_LOG entries, #81-#86) and found the mechanism built but not
enforced:

    `src/CORE/compliance/scanner.py` is a full RULE 0X-7 AST scanner covering
    exactly the seven categories, with `tests/test_scanner.py`, a `--fail-on`
    exit code, and a `scripts/worm_pre_commit_hook.sh`.  What is actually true,
    measured: the hook is NOT installed, and the default `pytest` suite does not
    gate on the scanner.  A commit that adds 500 emoji still passes.

Running the scanner over `src/` right now reports 2,224 findings. That is a real
debt, not a regression, and this project's own rule is that a check failing on
facts gets switched off (Lesson #86). So this gate does what
`tools/type_check_gate.py` does for type diagnostics: it records what is known
and fails only on an INCREASE.

Why counts-by-category and not finding identities
-------------------------------------------------
`type_check_gate.py` anchors on source lines because a type diagnostic is a
property of a line. An anti-pattern is a property of a (file, category) pair,
and the same emoji appears thousands of times; an identity scheme over 2,224
findings would be position-dependent (invalidated by any edit above it, Lesson
#97) and noisy. The ratchet only needs to answer "did this class get worse",
which per-category totals answer exactly, cheaply, and without a fragile key.

A category that disappears entirely is recorded as gone and reported, never a
failure -- driving a category to zero is the goal (`t_string`, `os_system` and
`cls_new_factory` were each driven to zero and this keeps them there).

Usage
-----
    python tools/anti_pattern_gate.py --baseline   # record what is known
    python tools/anti_pattern_gate.py --check      # pre-commit/CI: exit 1 on new
    python tools/anti_pattern_gate.py --report     # run, print, no gate
    python tools/anti_pattern_gate.py --check --dir src/CORE
    python tools/anti_pattern_gate.py --check --baseline-file logs/x.json

A narrowed run writes somewhere else (same rule as type_check_gate.py)
----------------------------------------------------------------------
`--dir` selects a SUBSET, so its counts are not the whole-`src/` baseline's
counts. A narrowed `--baseline` with no explicit `--baseline-file` is redirected
to a `.partial` sibling and says so; an explicit path is obeyed as written.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

#: Bump only when the meaning of a recorded count changes (e.g. a new scanner
#: category), so an old baseline is refused rather than diffed across.
IDENTITY_SCHEME = "category-counts-v1"

DEFAULT_DIR = "src"
BASELINE = ROOT / "logs" / "anti_pattern_baseline.json"


def scan(target: str) -> tuple[Counter, int]:
    """Return (per-category counts, files scanned) for a directory.

    Imports the scanner programmatically rather than shelling out, so the gate
    and the hook measure the SAME instrument the audit measured.
    """
    from CORE.compliance.scanner import ASTAntiPatternScanner  # noqa: PLC0415

    results = ASTAntiPatternScanner().scan_directory(str(ROOT / target))
    counts: Counter = Counter()
    for r in results:
        for _line, category, _snippet in r.findings:
            counts[category] += 1
    return counts, len(results)


def baseline_payload(counts: Counter, files: int, target: str) -> dict:
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "identity_scheme": IDENTITY_SCHEME,
        "scanner": "CORE.compliance.scanner",
        "target": target,
        "files_scanned": files,
        "category_counts": dict(sorted(counts.items())),
        "total_findings": sum(counts.values()),
    }


def load_baseline(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("no baseline at %s -- run --baseline first" % path, file=sys.stderr)
        raise SystemExit(2)
    except (OSError, ValueError) as exc:
        print("baseline at %s is unreadable: %s" % (path, exc), file=sys.stderr)
        raise SystemExit(2)


def _resolve_out(path_arg: str | None, narrowed: bool, kind: str) -> Path:
    """Obey an explicit path; redirect a narrowed run to a `.partial` sibling."""
    if path_arg:
        return Path(path_arg).resolve()
    if narrowed:
        return BASELINE.with_name(BASELINE.stem + ".partial" + BASELINE.suffix)
    return BASELINE


def cmd_baseline(target: str, out: Path, narrowed: bool) -> int:
    counts, files = scan(target)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline_payload(counts, files, target), indent=2),
                   encoding="utf-8")
    print("baseline written: %s" % out)
    if narrowed:
        print("  (narrowed to %r -- whole-tree --check will not read this file)"
              % target)
    print("  %d file(s), %d finding(s)" % (files, sum(counts.values())))
    for cat, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-26s %5d" % (cat, n))
    return 0


def cmd_report(target: str) -> int:
    counts, files = scan(target)
    print("anti-pattern report -- %s" % (ROOT / target))
    print("  %d file(s), %d finding(s)" % (files, sum(counts.values())))
    for cat, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-26s %5d" % (cat, n))
    return 0


def cmd_check(target: str, baseline_path: Path) -> int:
    base = load_baseline(baseline_path)
    if base.get("identity_scheme") != IDENTITY_SCHEME:
        print("baseline %s uses identity_scheme=%r, this gate uses %r -- re-run "
              "--baseline to convert (counts are not comparable across schemes)"
              % (baseline_path, base.get("identity_scheme"), IDENTITY_SCHEME),
              file=sys.stderr)
        return 2

    recorded: dict = base.get("category_counts") or {}
    current, files = scan(target)

    regressions = []
    for cat, n in current.items():
        was = recorded.get(cat, 0)
        if n > was:
            regressions.append((cat, was, n))

    improved = []
    for cat, was in recorded.items():
        n = current.get(cat, 0)
        if n < was:
            improved.append((cat, was, n))

    new_categories = sorted(set(current) - set(recorded))
    gone_categories = sorted(set(recorded) - set(current))

    total_now = sum(current.values())
    total_was = sum(recorded.values())

    print("anti-pattern gate -- %s" % (ROOT / target))
    print("  now:      %d finding(s) in %d file(s)" % (total_now, files))
    print("  baseline: %d finding(s) (%s)"
          % (total_was, base.get("recorded_at", "?")))

    if new_categories:
        print("\n  NEW category/categories (not in baseline):")
        for cat in new_categories:
            print("    %-26s %5d" % (cat, current[cat]))

    if regressions:
        print("\n  REGRESSIONS (count increased):")
        for cat, was, n in sorted(regressions, key=lambda t: -(t[2] - t[1])):
            print("    %-26s %5d -> %5d  (+%d)" % (cat, was, n, n - was))

    if improved:
        print("\n  improved (count decreased -- re-run --baseline to ratchet down):")
        for cat, was, n in sorted(improved, key=lambda t: t[2] - t[1]):
            print("    %-26s %5d -> %5d  (%d)" % (cat, was, n, n - was))

    if gone_categories:
        print("\n  cleared (recorded, now zero): %s" % ", ".join(gone_categories))

    if regressions or new_categories:
        print("\nFAIL: %d regression(s) and %d new category/categories. New "
              "anti-patterns are not allowed; fix them, or -- if a count is a "
              "deliberate, reviewed increase -- re-run --baseline."
              % (len(regressions), len(new_categories)))
        return 1

    print("\nOK: no anti-pattern regressions.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Fail on NEW anti-patterns, over a recorded baseline.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--baseline", action="store_true",
                       help="record the current counts as the baseline")
    group.add_argument("--check", action="store_true",
                       help="exit 1 on a count increase or a new category")
    group.add_argument("--report", action="store_true",
                       help="run and print, do not gate")
    ap.add_argument("--dir", default=DEFAULT_DIR,
                    help="directory to scan, repo-relative (default: %s)" % DEFAULT_DIR)
    ap.add_argument("--baseline-file", metavar="JSON")
    args = ap.parse_args(argv)

    target = args.dir.replace("\\", "/")
    narrowed = target.strip("/") != DEFAULT_DIR

    if args.baseline:
        out = _resolve_out(args.baseline_file, narrowed, "baseline")
        return cmd_baseline(target, out, narrowed)
    if args.report:
        return cmd_report(target)
    path = Path(args.baseline_file).resolve() if args.baseline_file else BASELINE
    return cmd_check(target, path)


if __name__ == "__main__":
    sys.exit(main())
