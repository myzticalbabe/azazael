"""Tests for run_tests.py per-file log persistence.

The log exists so a CI-only failure arrives with evidence (workflow comment in
.github/workflows/test-3.15t.yml). On 2026-11-15 the tail alone lost the two
[FAIL] lines from test_clusterworms_unit.py, which reported "Passed: 104,
Failed: 2" with no traceback; these tests pin the fix.
"""
import importlib.util
from pathlib import Path

import pytest


@pytest.fixture()
def rt(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[1] / "run_tests.py"
    spec = importlib.util.spec_from_file_location("run_tests_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "PROJECT_ROOT", str(tmp_path))
    return module


def _log(tmp_path, name):
    return (tmp_path / "logs" / name.replace(".py", ".log")).read_text(encoding="utf-8")


def test_failure_lines_before_the_tail_are_kept(rt, tmp_path):
    lines = ["  [OK] filler_%d" % i for i in range(400)]
    lines[10] = "  [FAIL] TestX.test_y: boom"
    lines[11] = "Traceback (most recent call last):"
    lines[12] = "AssertionError: boom"
    lines.append("  Passed: 104, Failed: 1, Skipped: 2")

    rt._persist_file_log("test_synth.py", "FAIL", 1, 1.0, "\n".join(lines))

    text = _log(tmp_path, "test_synth.py")
    assert "[FAIL] TestX.test_y: boom" in text
    assert "AssertionError: boom" in text
    assert "Passed: 104, Failed: 1, Skipped: 2" in text


def test_short_output_is_not_duplicated(rt, tmp_path):
    out = "  [OK] one\n  Passed: 1, Failed: 0, Skipped: 0"
    rt._persist_file_log("test_short.py", "PASS", 0, 0.1, out)

    text = _log(tmp_path, "test_short.py")
    assert "failure lines from earlier in the run" not in text
    assert text.count("[OK] one") == 1


def test_evidence_is_bounded(rt):
    lines = ["  [FAIL] boom"] * 500 + ["  [OK] filler"] * 400
    assert len(rt._failure_evidence(lines)) <= 120
