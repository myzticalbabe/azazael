# coding: utf-8
"""Tests for `tools/type_check_gate.py` — the basedpyright baseline gate.

Why these tests exist
---------------------
The gate replaced a mypy step that could not run on this tree, and the failure
mode of a quality gate is never "it crashes" -- it is "it reports OK". So the
tests pin the ways this one could reassure while wrong:

* a checker that could not run must not read as a clean tree,
* output that is not JSON must not read as a clean tree,
* a missing baseline must not read as "nothing is wrong",
* rewriting a diagnostic's MESSAGE must not read as a fix,
* and the committed baseline must actually agree with the committed report.

The runner is injected rather than invoked: a real run is ~1 minute and would
make this file's result depend on the tree it is measuring.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import type_check_gate as gate  # noqa: E402


def _diag(line, char, rule, message, severity="error"):
    return {"file": "src/CORE/x.py", "severity": severity,
            "rule": rule, "message": message,
            "range": {"start": {"line": line, "character": char},
                      "end": {"line": line, "character": char + 1}}}


PAYLOAD = {
    "summary": {"filesAnalyzed": 690, "errorCount": 2, "warningCount": 1,
                "informationCount": 0, "timeInSec": 51.6},
    "generalDiagnostics": [
        _diag(10, 4, "reportUndefinedVariable", "'foo' is not defined"),
        _diag(20, 0, "reportArgumentType", 'Argument of type "int" ...'),
        _diag(30, 8, "reportOptionalMemberAccess", '"_x" is not a known '
              'attribute', severity="warning"),
    ],
}


def test_identity_ignores_the_message_so_rewording_is_not_a_fix():
    """A reworded message is the same diagnostic, not a repaired one."""
    reworded = json.loads(json.dumps(PAYLOAD))
    reworded["generalDiagnostics"][0]["message"] = "'foo' is not defined.  Did you mean 'food'?"
    assert gate.diagnostic_ids(PAYLOAD) == gate.diagnostic_ids(reworded)


def test_identity_separates_rule_and_position():
    ids = gate.diagnostic_ids(PAYLOAD)
    assert len(ids) == 3
    assert "src/CORE/x.py:10:4:reportUndefinedVariable" in ids
    # Same position, different rule -> a different diagnostic (this is the case
    # the collapsing trade-off deliberately keeps distinct).
    other = {"generalDiagnostics": [_diag(10, 4, "reportAssignmentType", "m")]}
    assert gate.diagnostic_ids(other) != {i for i in ids if ":10:" in i}


def test_severity_counts_and_top_rules_are_reported():
    assert gate.severity_counts(PAYLOAD) == {"error": 2, "warning": 1,
                                             "information": 0}
    assert gate.rule_histogram(PAYLOAD) == {
        "reportUndefinedVariable": 1, "reportArgumentType": 1,
        "reportOptionalMemberAccess": 1}


def test_diff_splits_new_from_fixed():
    delta = gate.diff_against_baseline(
        ["a:1:0:r1", "a:2:0:r2"], ["a:2:0:r2", "a:3:0:r3"])
    assert delta["new"] == ["a:1:0:r1"]
    assert delta["fixed"] == ["a:3:0:r3"]
    assert delta["unchanged"] == ["a:2:0:r2"]


def test_a_new_diagnostic_blocks_and_a_known_one_does_not(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "base.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "rep.json")
    monkeypatch.setattr(gate, "run_checker",
                        lambda *a, **k: (1, json.dumps(PAYLOAD)))

    assert gate.main(["--baseline"]) == 0
    assert gate.main(["--check"]) == 0
    assert "OK: no new diagnostics" in capsys.readouterr().out

    grown = json.loads(json.dumps(PAYLOAD))
    grown["generalDiagnostics"].append(
        _diag(99, 0, "reportUndefinedVariable", "'bar' is not defined"))
    monkeypatch.setattr(gate, "run_checker",
                        lambda *a, **k: (1, json.dumps(grown)))
    assert gate.main(["--check"]) == 1
    assert ("NEW DIAGNOSTIC: src/CORE/x.py:99:0:reportUndefinedVariable"
            in capsys.readouterr().out)


def test_a_missing_checker_is_a_failure_not_a_clean_tree(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "base.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "rep.json")
    monkeypatch.setattr(gate, "run_checker", lambda *a, **k: (125, ""))
    assert gate.main(["--check"]) == 1
    assert "NO CHECKER" in capsys.readouterr().err


def test_non_json_output_is_a_failure_not_a_clean_tree(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "base.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "rep.json")
    monkeypatch.setattr(gate, "run_checker",
                        lambda *a, **k: (1, "Traceback (most recent call last)"))
    assert gate.main(["--check"]) == 1
    assert "no JSON" in capsys.readouterr().err


def test_no_baseline_refuses_to_reassure(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "absent.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "rep.json")
    monkeypatch.setattr(gate, "run_checker",
                        lambda *a, **k: (0, json.dumps(PAYLOAD)))
    assert gate.main(["--check"]) == 1
    assert "no baseline" in capsys.readouterr().err


def test_the_committed_baseline_agrees_with_the_committed_report():
    """A baseline that drifted from the run it claims to describe is fiction.

    Both files are committed, so this is the check that a stale one cannot
    survive review.
    """
    if not gate.BASELINE.exists():
        pytest.skip("no committed baseline")
    if not gate.REPORT.exists():
        pytest.skip("no committed report")
    base = json.loads(gate.BASELINE.read_text(encoding="utf-8"))
    report = json.loads(gate.REPORT.read_text(encoding="utf-8"))
    # Both files are written from the same payload, so every field they share
    # must agree. Compared field-to-field rather than by re-deriving from raw
    # diagnostics: the report is condensed deliberately, so that a 1.5 MB JSON
    # of prose is not what a reviewer has to diff.
    assert base["severity_counts"] == report["severity_counts"]
    assert base["summary"] == report["summary"]
    assert base["top_rules"] == report["top_rules"]
    assert set(base["diagnostic_ids"]) == set(report["diagnostic_ids"])
    assert base["diagnostic_ids"], "a baseline with no diagnostics proves nothing"
