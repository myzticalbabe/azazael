# coding: utf-8
"""Tests for tools/staged_scanner_gate.py.

The gate replaces the old pre-commit check 2, which failed on ANY finding in a
temp snapshot at --severity warning and so blocked every commit touching a
legacy file. The contract these tests lock:

  * a pre-existing finding must NOT block a commit (the old bug),
  * a NEW finding of the same category MUST block (the check's actual job),
  * `--severity error` ignores warning-level findings.
"""
import sys
from pathlib import Path

import tools.staged_scanner_gate as gate


_CLEAN = "x = 1\n"
_WITH_SILENT_PASS = "def f():\n    try:\n        x = 1\n    except:\n        pass\n"


def test_counts_detects_a_warning_level_finding():
    counts = gate._counts(_WITH_SILENT_PASS, "x.py", "warning")
    assert counts.get("silent_except_pass", 0) >= 1


def test_severity_error_ignores_warning_level_findings():
    counts = gate._counts(_WITH_SILENT_PASS, "x.py", "error")
    assert counts.get("silent_except_pass", 0) == 0


def _stage(monkeypatch, before, after):
    monkeypatch.setattr(gate, "_staged_py_files", lambda: ["x.py"])
    monkeypatch.setattr(gate, "_show",
                        lambda rev: after if rev == ":0:x.py" else before)
    monkeypatch.setattr(sys, "argv", ["staged_scanner_gate"])


def test_pre_existing_finding_does_not_block(monkeypatch, capsys):
    """The exact bug: an unchanged legacy finding must pass."""
    _stage(monkeypatch, before=_WITH_SILENT_PASS, after=_WITH_SILENT_PASS)
    assert gate.main() == 0
    assert "no new anti-patterns" in capsys.readouterr().out


def test_added_finding_blocks(monkeypatch, capsys):
    """The actual job: adding a warning-level finding must fail."""
    _stage(monkeypatch, before=_CLEAN, after=_WITH_SILENT_PASS)
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "silent_except_pass" in out
    assert "+1" in out


def test_added_warning_ignored_at_error_severity(monkeypatch, capsys):
    _stage(monkeypatch, before=_CLEAN, after=_WITH_SILENT_PASS)
    monkeypatch.setattr(sys, "argv",
                        ["staged_scanner_gate", "--severity", "error"])
    assert gate.main() == 0


def test_new_file_is_compared_against_empty(monkeypatch, capsys):
    """A new file's findings are all new, so a dirty new file must fail."""
    _stage(monkeypatch, before="", after=_WITH_SILENT_PASS)
    assert gate.main() == 1


def test_git_returns_bytes(monkeypatch):
    """`_git` must not decode with the OS locale (regression: cp1252 crash)."""
    out = gate._git("rev-parse", "--is-inside-work-tree")
    assert isinstance(out, bytes)
    assert out.strip() == b"true"
