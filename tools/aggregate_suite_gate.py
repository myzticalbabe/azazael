#!/usr/bin/env python3
# coding: utf-8
"""Aggregate pytest gate — fail on NEW aggregate-only failures.

Why this exists
---------------
`run_tests.py` and the CI job run each test FILE in its own process. That shape
cannot see the defect class this repository actually has: measured 2026-09-22, a
single-process run of `tests/` returned 72 failures and 69 errors while **every
failing file passed green when run alone** (test_sb3_agent 42, test_nature_
metacluster_unit 74, test_fs_probe_backend 13, test_wiring_cycle 19,
test_evolution_gates 61, test_import_map 8, ...). Isolation defects — shared
registry/discovery state, a process-global write guard, module identity — only
exist *across* time inside one interpreter, so a per-file runner is blind to
them by construction.

Why a baseline rather than a plain exit code
--------------------------------------------
The remaining failures are known facts, and this project's own principle is that
"a check that fails on facts gets switched off". So the gate compares against
`logs/aggregate_suite_baseline.json`:

* a failure id that is NOT in the baseline -> exit 1 (a regression),
* a baseline id that no longer fails      -> reported, exit 0 (an improvement),
  with a hint to re-baseline,
* a run that never completed              -> exit 1 (a timeout is not a pass).

Usage
-----
    python tools/aggregate_suite_gate.py --check       # CI: exit 1 on new ids
    python tools/aggregate_suite_gate.py --baseline    # record the known set
    python tools/aggregate_suite_gate.py --report      # run + write the report
    python tools/aggregate_suite_gate.py --check --only test_wiring  # subset
    python tools/aggregate_suite_gate.py --diff-from logs/report.json

CI uses the isolation profile, which is the same contract over the
 dependency-light subset whose cross-file failures are reproducible off the
development machine (see ISOLATION_PROFILE for the selection rule):

    python tools/aggregate_suite_gate.py --check --profile isolation

Both entry points are intentionally the SAME script. A second, thinner
implementation for CI is how a gate stops describing what runs locally.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parent.parent
BASELINE = REPO / "logs" / "aggregate_suite_baseline.json"
REPORT = REPO / "logs" / "aggregate_suite_report.json"

#: The dependency-light ISOLATION PROFILE, for CI.
#:
#: The full suite cannot gate in CI: it needs torch / stable-baselines3 /
#: transformers, and a missing dependency shows up as hundreds of collection
#: errors indistinguishable from real regressions. But the defect class this
#: gate exists for -- two files that are green alone and red together -- does
#: not need the heavy stack. These files were MEASURED to fail in the aggregate
#: run of 2026-09-22 while passing alone, and they import only stdlib + CORE, so
#: the same set gates identically on a laptop and on a CI runner.
#:
#: Selection rule, applied when extending the list: (1) the file failed in a
#: single-process run and passed alone, (2) `grep -lE "torch|stable_baselines3|
#: transformers|sklearn"` does not match it, (3) it imports no other test file's
#: help except through CORE. Rule 2 is what makes the CI baseline honest.
ISOLATION_PROFILE = (
    "tests/test_nature_metacluster_unit.py",
    "tests/test_wiring_cycle.py",
    "tests/test_registry_importable.py",
    "tests/test_spine_mesh.py",
    "tests/test_import_map.py",
    "tests/test_evolution_gates.py",
    "tests/test_mesh_wire_or_cut.py",
    "tests/test_learning_closure.py",
)

#: `pytest -q` prints `FAILED tests/test_x.py::test_y - AssertionError: ...`
#: and `ERROR tests/test_x.py::TestY::test_z - ...`. Ids are the nodeid only,
#: so a message change does not read as a new failure.
_ID_RE = re.compile(r"^(?P<kind>FAILED|ERROR)\s+(?P<nodeid>\S+)")
_SUMMARY_RE = re.compile(
    r"(?P<failed>\d+) failed|(?P<passed>\d+) passed|(?P<errors>\d+) error|"
    r"(?P<skipped>\d+) skipped")
_FINAL_RE = re.compile(r"^(?P<line>.*\b(?:failed|passed|error).*)\s+in\s+[\d.]+s")


def parse_pytest_output(text: str) -> Dict[str, object]:
    """Extract failing nodeids and the summary counts from pytest output.

    Pure function so the gate's decision logic is testable without a 20-minute
    run: the caller supplies the text.
    """
    failures: Set[str] = set()
    errors: Set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        match = _ID_RE.match(line)
        if not match:
            continue
        nodeid = match.group("nodeid")
        (failures if match.group("kind") == "FAILED" else errors).add(nodeid)
    counts = {"failed": 0, "passed": 0, "errors": 0, "skipped": 0}
    final = ""
    for line in text.splitlines():
        if _FINAL_RE.match(line.strip()):
            final = line.strip()
    for match in _SUMMARY_RE.finditer(final):
        for key in ("failed", "passed", "errors", "skipped"):
            value = match.group(key)
            if value:
                counts[key] += int(value)
    return {
        "failed_ids": sorted(failures),
        "error_ids": sorted(errors),
        "counts": counts,
        "summary_line": final,
    }


def all_ids(parsed: Dict[str, object]) -> Set[str]:
    """Every blocking nodeid: failures and errors, as one set."""
    return set(parsed.get("failed_ids") or []) | set(parsed.get("error_ids") or [])


def diff_against_baseline(parsed: Dict[str, object],
                          baseline_ids: Iterable[str]) -> Dict[str, List[str]]:
    """New (regressed) ids, fixed (disappeared) ids, and the unchanged count."""
    current = all_ids(parsed)
    known = set(baseline_ids or ())
    new = sorted(current - known)
    fixed = sorted(known - current)
    return {"new": new, "fixed": fixed,
            "unchanged": sorted(current & known)}


def baseline_payload(parsed: Dict[str, object]) -> Dict[str, object]:
    """The JSON body written by `--baseline`."""
    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "suite": "tests/ (single process, -p no:randomly)",
        "counts": parsed.get("counts"),
        "summary_line": parsed.get("summary_line"),
        "failed_ids": parsed.get("failed_ids") or [],
        "error_ids": parsed.get("error_ids") or [],
    }


def load_ids(path: Path) -> List[str]:
    """Baseline/report ids, tolerating a missing or malformed file."""
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return sorted(set(payload.get("failed_ids") or [])
                  | set(payload.get("error_ids") or []))


def run_pytest(select: Optional[Sequence[str]] = None,
               timeout: int = 2400) -> Tuple[int, str]:
    """One aggregate pytest process. Returns (returncode, combined output).

    A single process on purpose: chunking it would recreate exactly the
    per-file blind spot this gate exists to remove.
    """
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:randomly"]
    if select:
        cmd += list(select)
    else:
        cmd += ["tests/"]
    try:
        proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return 124, "TIMEOUT after %ss\n%s" % (timeout, exc)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _write_json(path: Path, payload: Dict[str, object]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    # Declared first: the `--*-file` defaults read the module-level names, and
    # Python rejects a `global` that follows a use in the same function.
    global BASELINE, REPORT
    parser = argparse.ArgumentParser(
        description="Run the aggregate suite and gate on NEW failures")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="exit 1 when an id is not in the baseline")
    group.add_argument("--baseline", action="store_true",
                       help="record the current failing ids as known")
    group.add_argument("--report", action="store_true",
                       help="run and write the report without gating")
    group.add_argument("--diff-from", metavar="JSON",
                       help="skip the run and diff a saved report/baseline")
    # Deliberately NOT in the mutually-exclusive group: this one selects the
    # INPUT (a saved run instead of a fresh one) and composes with --check,
    # --baseline and --report, which select what to DO with it.
    parser.add_argument("--parse-from", metavar="RAW",
                        help="parse a saved RAW pytest output instead of "
                             "running; composes with --check/--baseline/--report")
    parser.add_argument("--only", nargs="+", metavar="PATH",
                        help="pytest targets (default: tests/)")
    parser.add_argument("--profile", choices=("full", "isolation"),
                        default="full",
                        help="'isolation' runs the dependency-light CI subset "
                             "that reproduces the cross-file defect class")
    parser.add_argument("--baseline-file", metavar="JSON",
                        help="where --baseline writes / --check reads "
                             "(default: %s)" % BASELINE.name)
    parser.add_argument("--report-file", metavar="JSON",
                        help="where the run report is written "
                             "(default: %s)" % REPORT.name)
    parser.add_argument("--timeout", type=int, default=2400,
                        help="seconds for the whole aggregate run")
    args = parser.parse_args(argv)

    # Module-level names, overridable: `--check` MUST read the same file
    # `--baseline` wrote, including when a profile pinned it elsewhere, so the
    # two resolve through one place rather than repeating the default.
    if args.baseline_file:
        BASELINE = Path(args.baseline_file).resolve()
    elif args.profile == "isolation":
        BASELINE = REPO / "logs" / "aggregate_isolation_baseline.json"
    if args.report_file:
        REPORT = Path(args.report_file).resolve()
    elif args.profile == "isolation":
        REPORT = REPO / "logs" / "aggregate_isolation_report.json"

    select = args.only
    if select is None and args.profile == "isolation":
        select = list(ISOLATION_PROFILE)

    if args.diff_from:
        parsed = {"failed_ids": load_ids(Path(args.diff_from)), "error_ids": []}
        rc = 0
        out = ""
    elif args.parse_from:
        # A run that was streamed to a file (so its progress was watchable) is
        # the same evidence as a captured one; re-running it just to re-parse it
        # is the cost this option exists to remove -- ADR-010 rule 5.
        raw_path = Path(args.parse_from)
        try:
            out = raw_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print("cannot read raw output %s: %s" % (raw_path, exc),
                  file=sys.stderr)
            return 1
        parsed = parse_pytest_output(out)
        rc = 0
    else:
        rc, out = run_pytest(select, args.timeout)
        parsed = parse_pytest_output(out)
        if rc == 124:
            print("TIMEOUT: the aggregate run did not finish -- treated as a "
                  "failure, because a killed run is not a pass", file=sys.stderr)
            return 1

    # The RAW OUTPUT is persisted next to the report, unconditionally.
    # Reason: the report stores nodeids only, and a nodeid names the failure but
    # says nothing about its cause -- so the previous runs left ~50 failures that
    # could be counted and not diagnosed, and re-paying 22 minutes was the only
    # way to read an assertion message. 1.5 MB of text is cheaper than that.
    if not args.diff_from and not args.parse_from:
        raw = REPORT.with_suffix(".raw.txt")
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text(out, encoding="utf-8", errors="replace")
        print("raw output: %s" % raw)
    elif args.parse_from:
        # Not copied: the streamed file IS the evidence, and duplicating it under
        # the report's name would suggest the gate had produced it.
        print("parsed from: %s" % args.parse_from)

    counts = parsed.get("counts") or {}
    ids = all_ids(parsed)
    print("aggregate suite: %s failed / %s passed / %s errors / %s skipped"
          % (counts.get("failed"), counts.get("passed"),
             counts.get("errors"), counts.get("skipped")))
    print("blocking ids: %d" % len(ids))

    if not args.diff_from:
        _write_json(REPORT, {"recorded_at": datetime.now(
            timezone.utc).isoformat(timespec="seconds"),
            "profile": args.profile,
            "targets": list(select or ["tests/"]),
            "raw_output": REPORT.with_suffix(".raw.txt").name,
            "counts": counts, "summary_line": parsed.get("summary_line"),
            "failed_ids": parsed.get("failed_ids") or [],
            "error_ids": parsed.get("error_ids") or []})

    if args.baseline:
        _write_json(BASELINE, baseline_payload(parsed))
        print("baseline recorded: %d known ids -> %s" % (len(ids), BASELINE))
        return 0

    if not args.check:
        return 0

    baseline_ids = load_ids(BASELINE)
    if not baseline_ids and not BASELINE.exists():
        print("no baseline at %s -- run --baseline first" % BASELINE,
              file=sys.stderr)
        return 1

    delta = diff_against_baseline(parsed, baseline_ids)
    for nodeid in delta["new"]:
        print("NEW FAILURE: %s" % nodeid)
    for nodeid in delta["fixed"]:
        print("no longer failing: %s" % nodeid)
    if delta["fixed"]:
        print("(%d baseline id(s) are gone -- re-run --baseline to tighten the "
              "gate)" % len(delta["fixed"]))
    if delta["new"]:
        print("FAIL: %d new aggregate failure(s) vs %s"
              % (len(delta["new"]), BASELINE))
        return 1
    print("OK: no new aggregate failures (%d known, %d unchanged)"
          % (len(baseline_ids), len(delta["unchanged"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
