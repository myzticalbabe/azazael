"""Tests for `tools/aggregate_suite_gate.py` — the parsing and diff logic.

The gate exists because a per-file runner cannot see isolation defects. These
tests pin its DECISIONS (new id -> block; gone id -> report; timeout -> block)
and its parsing, without paying for a 20-minute aggregate run: the runner is
injected via monkeypatch, and the parser is exercised on real pytest output.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import aggregate_suite_gate as gate  # noqa: E402


SAMPLE = """\
................................s....................................... [ 50%]
F.........................................E............................ [100%]
=========================== short test summary info ===========================
FAILED tests/test_a.py::test_one - AssertionError: assert 1 == 2
FAILED tests/test_a.py::TestB::test_two - AttributeError: 'NoneType'
ERROR tests/test_c.py::test_three - PermissionError: CRITICAL: Unauthorized
2 failed, 71 passed, 1 error, 1 skipped in 12.34s
"""


def test_parse_extracts_failures_errors_and_counts():
    parsed = gate.parse_pytest_output(SAMPLE)
    assert parsed["failed_ids"] == ["tests/test_a.py::TestB::test_two",
                                    "tests/test_a.py::test_one"]
    assert parsed["error_ids"] == ["tests/test_c.py::test_three"]
    assert parsed["counts"] == {"failed": 2, "passed": 71, "errors": 1,
                               "skipped": 1}
    assert "2 failed" in parsed["summary_line"]


def test_ids_ignore_the_failure_message_so_only_nodeids_are_compared():
    """A changed assertion message must not read as a new failure."""
    later = SAMPLE.replace("AssertionError: assert 1 == 2",
                           "AssertionError: assert 'x' == 'y'")
    assert gate.all_ids(gate.parse_pytest_output(SAMPLE)) == \
        gate.all_ids(gate.parse_pytest_output(later))


def test_a_new_id_blocks_and_a_disappeared_id_only_reports():
    parsed = gate.parse_pytest_output(SAMPLE)
    delta = gate.diff_against_baseline(
        parsed, ["tests/test_a.py::test_one", "tests/test_gone.py::test_old"])
    assert delta["new"] == ["tests/test_a.py::TestB::test_two",
                            "tests/test_c.py::test_three"]
    assert delta["fixed"] == ["tests/test_gone.py::test_old"]
    assert delta["unchanged"] == ["tests/test_a.py::test_one"]


def test_check_fails_on_a_new_id_and_passes_when_nothing_is_new(
        tmp_path, monkeypatch, capsys):
    baseline = tmp_path / "baseline.json"
    monkeypatch.setattr(gate, "BASELINE", baseline)
    monkeypatch.setattr(gate, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(gate, "run_pytest", lambda *a, **k: (1, SAMPLE))

    assert gate.main(["--baseline"]) == 0
    recorded = json.loads(baseline.read_text(encoding="utf-8"))
    assert recorded["failed_ids"] == ["tests/test_a.py::TestB::test_two",
                                      "tests/test_a.py::test_one"]

    # Same suite again: known ids, so the gate passes.
    assert gate.main(["--check"]) == 0
    assert "OK: no new aggregate failures" in capsys.readouterr().out

    # One MORE failure than the baseline: the gate blocks.
    monkeypatch.setattr(gate, "run_pytest", lambda *a, **k: (
        1, SAMPLE + "FAILED tests/test_z.py::test_new - AssertionError\n"))
    assert gate.main(["--check"]) == 1
    assert "NEW FAILURE: tests/test_z.py::test_new" in capsys.readouterr().out


def test_a_timeout_is_a_failure_not_a_pass(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "baseline.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(gate, "run_pytest", lambda *a, **k: (124, "TIMEOUT"))
    assert gate.main(["--check"]) == 1
    assert "TIMEOUT" in capsys.readouterr().err


def test_missing_baseline_refuses_to_reassure(tmp_path, monkeypatch, capsys):
    """No baseline + no recorded failures must not read as 'all clear'."""
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "absent.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(gate, "run_pytest", lambda *a, **k: (0, "500 passed in 9s"))
    assert gate.main(["--check"]) == 1
    assert "no baseline" in capsys.readouterr().err


def test_baseline_filters_to_the_known_set_with_a_real_subset():
    baseline = gate.baseline_payload(gate.parse_pytest_output(SAMPLE))
    assert baseline["counts"]["failed"] == 2
    assert len(baseline["error_ids"]) == 1
    assert "recorded_at" in baseline


def test_the_isolation_profile_pins_its_own_files_and_baseline(
        tmp_path, monkeypatch):
    """CI must not compare against the full-suite baseline.

    Two different environments (no torch in CI, the full stack locally) would
    otherwise report each other's failures as regressions. The profile is the
    one place that mapping is written down.
    """
    seen = {}

    def fake_run(select, timeout):
        seen["select"] = select
        return 0, "500 passed in 9s"

    monkeypatch.setattr(gate, "run_pytest", fake_run)
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "full.json")
    assert gate.main(["--report", "--profile", "isolation"]) == 0
    assert seen["select"] == list(gate.ISOLATION_PROFILE)
    assert gate.BASELINE.name == "aggregate_isolation_baseline.json"
    assert gate.REPORT.name == "aggregate_isolation_report.json"


def test_an_explicit_only_still_wins_over_the_profile(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(gate, "run_pytest",
                        lambda s, t: (seen.update(select=s), (0, "1 passed in 1s"))[1])
    monkeypatch.setattr(gate, "REPORT", tmp_path / "r.json")
    assert gate.main(["--report", "--profile", "isolation",
                      "--only", "tests/test_x.py"]) == 0
    assert seen["select"] == ["tests/test_x.py"]


def test_the_raw_output_is_persisted_so_a_failure_can_be_diagnosed(
        tmp_path, monkeypatch, capsys):
    """The report stores nodeids; a nodeid names a failure, it does not explain it.

    Measured cost of NOT doing this: five aggregate runs whose ~50 failures could
    be counted but not read, because the only copy of the assertion message was
    in a subprocess pipe that the gate had already closed.
    """
    monkeypatch.setattr(gate, "BASELINE", tmp_path / "b.json")
    monkeypatch.setattr(gate, "REPORT", tmp_path / "report.json")
    monkeypatch.setattr(gate, "run_pytest", lambda *a, **k: (1, SAMPLE))
    assert gate.main(["--report"]) == 0
    raw = tmp_path / "report.raw.txt"
    assert raw.exists() and "AssertionError: assert 1 == 2" in raw.read_text(
        encoding="utf-8")
    payload = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert payload["raw_output"] == "report.raw.txt"
    assert payload["profile"] == "full"
    assert payload["targets"] == ["tests/"]
    assert "raw output:" in capsys.readouterr().out


def test_the_isolation_profile_names_only_files_that_exist():
    """A renamed test file must break the gate, not silently shrink it."""
    missing = [p for p in gate.ISOLATION_PROFILE if not (gate.REPO / p).exists()]
    assert not missing, "isolation profile names absent files: %s" % missing


def test_the_isolation_profile_stays_dependency_light():
    """Rule 2 of the selection rule, enforced rather than documented.

    A heavy import makes the profile's baseline environment-specific, which is
    exactly the failure the profile exists to avoid. Checked on the AST, not on
    the text: `test_mesh_wire_or_cut.py` *discusses* torch in a docstring about
    a lazy proxy because it reads `nerve.py` as data, and a substring test
    cannot tell a discussion of a module from an import of one.
    """
    heavy = {"torch", "stable_baselines3", "transformers", "sklearn",
             "tensorflow", "gymnasium"}
    offenders = {}
    for rel in gate.ISOLATION_PROFILE:
        tree = ast.parse((gate.REPO / rel).read_text(encoding="utf-8",
                                                    errors="replace"))
        hits = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                hits |= {a.name.split(".")[0] for a in node.names} & heavy
            elif isinstance(node, ast.ImportFrom) and node.module:
                hits |= {node.module.split(".")[0]} & heavy
        if hits:
            offenders[rel] = sorted(hits)
    assert not offenders, (
        "isolation profile must stay installable without the ML stack: %s"
        % offenders)
