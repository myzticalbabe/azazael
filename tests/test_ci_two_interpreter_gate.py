"""Tests for `scripts/ci_two_interpreter_gate.py` — parsing and decisions.

The gate exists because "the suite is green" on one interpreter says nothing
about the other. These tests pin its DECISIONS (collection error -> block, pass
drop -> block, divergence -> block only when asked, incomplete run -> block)
and its summary parsing, without paying for a 20-minute two-interpreter run:
the comparison functions are pure and are exercised directly on real pytest
output strings.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import ci_two_interpreter_gate as gate  # noqa: E402


# A real `pytest -q` summary, including the trailing subtest line the two
# interpreters both produced on 2026-09-30.
SAMPLE = (
    "ERROR tests/test_import_map.py::TestTriage::test_zero - ImportError\n"
    "72 failed, 3570 passed, 42 skipped, 109 warnings, 85 errors, "
    "59 subtests passed in 714.20s (0:11:54)\n"
)


def _record(role: str, passed: int, errors: int = 0, completed: bool = True):
    return {
        "role": role,
        "interpreter": f"/fake/{role}",
        "completed": completed,
        "error": None if completed else "timeout after 10s",
        "counts": {
            "passed": passed,
            "failed": 0,
            "errors": errors,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
            "deselected": 0,
        },
    }


def test_parse_counts_reads_the_summary_line():
    counts = gate.parse_counts(SAMPLE)
    assert counts["passed"] == 3570
    assert counts["failed"] == 72
    assert counts["errors"] == 85
    assert counts["skipped"] == 42


def test_parse_counts_does_not_count_subtests_as_passed():
    # "59 subtests passed" must not shadow the 3570 real passes above.
    counts = gate.parse_counts(SAMPLE)
    assert counts["passed"] == 3570


def test_completed_matching_run_passes():
    results = {"primary": _record("primary", 3570), "gil": _record("gil", 3519)}
    baseline = {"primary": {"passed": 3570}, "gil": {"passed": 3519}}
    assert gate.compare(results, baseline, 0, None, False) == []


def test_collection_error_blocks():
    results = {"primary": _record("primary", 3900, errors=2)}
    baseline = {"primary": {"passed": 3900}}
    problems = gate.compare(results, baseline, 0, None, False)
    assert any("collection error" in p for p in problems)


def test_collection_errors_can_be_explicitly_allowed():
    results = {"primary": _record("primary", 3900, errors=2)}
    baseline = {"primary": {"passed": 3900}}
    assert gate.compare(results, baseline, 0, None, True) == []


def test_pass_regression_blocks_and_tolerance_relaxes_it():
    results = {"primary": _record("primary", 3560)}
    baseline = {"primary": {"passed": 3570}}
    assert gate.compare(results, baseline, 0, None, False)
    assert gate.compare(results, baseline, 10, None, False) == []


def test_divergence_only_blocks_when_configured():
    results = {"primary": _record("primary", 3570), "gil": _record("gil", 3400)}
    baseline = {"primary": {"passed": 3570}, "gil": {"passed": 3400}}
    assert gate.compare(results, baseline, 0, None, False) == []
    problems = gate.compare(results, baseline, 0, 25, False)
    assert any("diverge" in p for p in problems)


def test_incomplete_run_blocks():
    results = {"primary": _record("primary", 0, completed=False)}
    baseline = {"primary": {"passed": 3570}}
    problems = gate.compare(results, baseline, 0, None, False)
    assert any("did not complete" in p for p in problems)


def test_missing_role_baseline_blocks():
    results = {"gil": _record("gil", 3519)}
    baseline = {"primary": {"passed": 3570}}
    problems = gate.compare(results, baseline, 0, None, False)
    assert any("no baseline" in p for p in problems)
