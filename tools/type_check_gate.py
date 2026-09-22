#!/usr/bin/env python3
# coding: utf-8
"""Type-check gate — fail on NEW diagnostics, over a recorded baseline.

Why basedpyright and not mypy
-----------------------------
mypy was the check the CI file asked for and it does not work on this tree. Two
measured reasons, both fatal rather than cosmetic:

* **It cannot read the repository.** `python -m mypy src/CORE/` aborts with
  `ValueError: path is on mount '\\\\.\\nul'` because two literal files named
  `nul` sat in the tree (junk from a `dir /b src\\... > nul` run inside Git Bash,
  where `> nul` is a real file and not the Windows device). Removed
  2026-09-22; the crash was never a mypy bug, but it is why "type safety is
  unmeasured" was true for months.
* **It answers a narrower question.** On the same tree mypy reports 655 errors
  in 134 files over `src/CORE/`; basedpyright reports 1,191 errors + 252 warnings
  over 690 files in 64 seconds, and the classes it adds are the ones this
  codebase actually suffers from — `reportUndefinedVariable` (94),
  `reportPossiblyUnboundVariable` (17), `reportOptionalMemberAccess` (120)
  against try/except-ImportError and Optional returns. mypy's run took ~6
  minutes; this took ~1.

So the instrument is `basedpyright`, which the venv already had installed
(1.40.1) and which reads the repo's existing `pyrightconfig.json`. mypy is kept
installed and is still useful as a *second* opinion on a single file; it is no
longer the gate.

Why a baseline rather than a clean run
--------------------------------------
1,191 errors are a real debt, not a regression, and this project's own rule is
that a check failing on facts gets switched off. So the gate compares against
`logs/basedpyright_baseline.json`:

* a diagnostic identity not in the baseline -> exit 1,
* a baseline identity no longer reported     -> reported, exit 0, with a hint,
* a checker that could not run               -> exit 1 (no output is not a pass).

Identity is `file:line:col:rule` -- the message text is deliberately NOT part of
it, so rewording a message is not a "fix" and a changed message is not a
regression.

Usage
-----
    python tools/type_check_gate.py --check      # CI + pre-commit: exit 1 on new
    python tools/type_check_gate.py --baseline   # record what is known
    python tools/type_check_gate.py --report     # run, write report, no gate
    python tools/type_check_gate.py --check --only src/CORE/neural_loop.py
    python tools/type_check_gate.py --diff-from logs/type_report.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "logs" / "basedpyright_baseline.json"
REPORT = REPO / "logs" / "basedpyright_report.json"

#: Console script next to the running interpreter, then the module, then the
#: Node build. The venv is preferred because it pins the version; `npx` is the
#: fallback so the gate still works from a bare checkout in CI.
_TOOL_CANDIDATES = ("basedpyright", "pyright")


def resolve_checker() -> Optional[List[str]]:
    """Command prefix that runs the checker, or None if none is available."""
    bindir = Path(sys.executable).resolve().parent
    for name in _TOOL_CANDIDATES:
        exe = bindir / (name + (".exe" if sys.platform == "win32" else ""))
        if exe.exists():
            return [str(exe)]
    for name in _TOOL_CANDIDATES:
        found = shutil.which(name)
        if found:
            return [found]
    if shutil.which("npx"):
        return ["npx", "--yes", "pyright"]
    return None


def run_checker(targets: Optional[Sequence[str]] = None,
                timeout: int = 1200) -> Tuple[int, str]:
    """Run the checker. Returns (returncode, stdout). 125 = could not run."""
    cmd = resolve_checker()
    if cmd is None:
        return 125, ""
    cmd = cmd + ["--outputjson"]
    if targets:
        cmd += list(targets)
    try:
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True,
                              text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print("checker failed to run: %s" % exc, file=sys.stderr)
        return 125, ""
    return proc.returncode, proc.stdout or ""


def diagnostic_ids(payload: Dict[str, object]) -> Set[str]:
    """Stable identity per diagnostic: file:line:col:rule (never the message).

    A message is prose; prose gets reworded, and a gate that treats rewording as
    a change teaches people to ignore it.

    ACCEPTED TRADE-OFF, measured: identity is positional, so two diagnostics
    sharing a position AND a rule collapse into one id -- 1,443 diagnostics
    became 1,377 ids on the 2026-09-22 run. The alternative (an index per
    position) would renumber every later diagnostic in a file whenever one is
    added or removed, turning one real change into hundreds of false "NEW"
    reports. A gate that cries wolf gets switched off, so the collapsing form is
    chosen knowingly: a second diagnostic at a position that already has one of
    the same rule is not counted as new. The severity counts recorded alongside
    the ids are what still make a growing pile visible.
    """
    out: Set[str] = set()
    for diag in payload.get("generalDiagnostics") or []:  # type: ignore[union-attr]
        rng = diag.get("range") or {}
        start = rng.get("start") or {}
        out.add("%s:%s:%s:%s" % (
            str(diag.get("file") or "").replace("\\", "/"),
            start.get("line", -1), start.get("character", -1),
            diag.get("rule") or "no-rule"))
    return out


def severity_counts(payload: Dict[str, object]) -> Dict[str, int]:
    """Errors and warnings, counted, so a growing warning pile is visible."""
    counts = {"error": 0, "warning": 0, "information": 0}
    for diag in payload.get("generalDiagnostics") or []:  # type: ignore[union-attr]
        key = str(diag.get("severity") or "error")
        counts[key] = counts.get(key, 0) + 1
    return counts


def rule_histogram(payload: Dict[str, object], top: int = 10) -> Dict[str, int]:
    tally: Dict[str, int] = {}
    for diag in payload.get("generalDiagnostics") or []:  # type: ignore[union-attr]
        rule = str(diag.get("rule") or "no-rule")
        tally[rule] = tally.get(rule, 0) + 1
    return dict(sorted(tally.items(), key=lambda kv: -kv[1])[:top])


def contract_summary(payload: Dict[str, object]) -> Dict[str, object]:
    """The summary fields that describe the TREE, not the stopwatch.

    `timeInSec` is excluded on purpose. The report is rewritten by every run and
    the baseline only by `--baseline`, so the two files legitimately come from
    different runs; if wall-clock time were part of the contract, the two would
    ALWAYS disagree and the agreement test would have to be deleted. Keeping the
    field in the report (where it is useful) and out of the contract (where it is
    noise) is what lets the baseline and the report be compared at all.
    """
    summary = dict(payload.get("summary") or {})
    summary.pop("timeInSec", None)
    return summary


def baseline_payload(payload: Dict[str, object]) -> Dict[str, object]:
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checker": "basedpyright (pyrightconfig.json, typeCheckingMode basic)",
        "summary": contract_summary(payload),
        "severity_counts": severity_counts(payload),
        "top_rules": rule_histogram(payload),
        "diagnostic_ids": sorted(diagnostic_ids(payload)),
    }


def load_ids(path: Path) -> Set[str]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return set(data.get("diagnostic_ids") or ())


def diff_against_baseline(current: Iterable[str],
                          known: Iterable[str]) -> Dict[str, List[str]]:
    cur, base = set(current), set(known)
    return {"new": sorted(cur - base), "fixed": sorted(base - cur),
            "unchanged": sorted(cur & base)}


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    global BASELINE, REPORT
    parser = argparse.ArgumentParser(
        description="Gate the type checker on NEW diagnostics")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="exit 1 when a diagnostic is not in the baseline")
    group.add_argument("--baseline", action="store_true",
                       help="record the current diagnostics as known")
    group.add_argument("--report", action="store_true",
                       help="run and write the report without gating")
    group.add_argument("--diff-from", metavar="JSON",
                       help="skip the run and diff a saved report")
    parser.add_argument("--only", nargs="+", metavar="PATH",
                        help="paths to check (default: pyrightconfig include)")
    parser.add_argument("--baseline-file", metavar="JSON")
    parser.add_argument("--report-file", metavar="JSON")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args(argv)

    if args.baseline_file:
        BASELINE = Path(args.baseline_file).resolve()
    if args.report_file:
        REPORT = Path(args.report_file).resolve()

    if args.diff_from:
        payload = {"generalDiagnostics": [
            {"file": i.rsplit(":", 3)[0], "range": {"start": {}},
             "rule": i.rsplit(":", 1)[-1]} for i in sorted(
                load_ids(Path(args.diff_from)))]}
        rc = 0
    else:
        rc, out = run_checker(args.only, args.timeout)
        if rc == 125:
            print("NO CHECKER: neither basedpyright nor pyright could be run; "
                  "treating this as a failure because an unchecked tree must "
                  "not read as a clean one", file=sys.stderr)
            return 1
        try:
            payload = json.loads(out)
        except ValueError:
            print("checker produced no JSON (exit %s); not a pass" % rc,
                  file=sys.stderr)
            return 1

    ids = diagnostic_ids(payload)
    counts = severity_counts(payload)
    summary = payload.get("summary") or {}
    files = summary.get("filesAnalyzed")
    print("type check: %s errors / %s warnings over %s files"
          % (counts.get("error"), counts.get("warning"), files))
    for rule, n in rule_histogram(payload).items():
        print("  %5d %s" % (n, rule))

    if not args.diff_from:
        _write_json(REPORT, {
            "recorded_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "checker": "basedpyright",
            "summary": contract_summary(payload), "severity_counts": counts,
            "top_rules": rule_histogram(payload),
            "diagnostic_ids": sorted(ids)})

    if args.baseline:
        _write_json(BASELINE, baseline_payload(payload))
        print("baseline recorded: %d known diagnostics -> %s" % (len(ids),
                                                                 BASELINE))
        return 0

    if not args.check:
        return 0

    known = load_ids(BASELINE)
    if not known and not BASELINE.exists():
        print("no baseline at %s -- run --baseline first" % BASELINE,
              file=sys.stderr)
        return 1

    delta = diff_against_baseline(ids, known)
    for ident in delta["new"]:
        print("NEW DIAGNOSTIC: %s" % ident)
    for ident in delta["fixed"]:
        print("no longer reported: %s" % ident)
    if delta["fixed"]:
        print("(%d baseline diagnostic(s) are gone -- re-run --baseline to "
              "tighten the gate)" % len(delta["fixed"]))
    if delta["new"]:
        print("FAIL: %d new diagnostic(s) vs %s" % (len(delta["new"]), BASELINE))
        return 1
    print("OK: no new diagnostics (%d known, %d unchanged)"
          % (len(known), len(delta["unchanged"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
