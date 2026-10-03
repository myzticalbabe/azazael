# coding: utf-8
"""Tests for vacuous-audit repeat grouping (pattern findings)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import vacuous_check_audit as audit  # noqa: E402


def _row(detector, path, code, line, sev="MED"):
    return {"detector": detector, "path": path, "code": code, "line": line,
            "severity": sev, "why": "w"}


def test_groups_repeated_idiom():
    rows = [_row("assert_true", "a.py", "assert True", 10),
            _row("assert_true", "a.py", "assert True", 20),
            _row("assert_true", "a.py", "assert True", 30)]
    groups = audit.group_repeats(rows)
    assert len(groups) == 1
    g = groups[0]
    assert g["kind"] == "pattern"
    assert g["count"] == 3
    assert g["locations"] == [10, 20, 30]


def test_singles_and_cross_file_not_grouped():
    rows = [_row("assert_true", "a.py", "assert True", 10),
            _row("assert_true", "b.py", "assert True", 10),
            _row("bare_except", "a.py", "except:", 40)]
    assert audit.group_repeats(rows) == []


def test_whitespace_normalized():
    rows = [_row("assert_true", "a.py", "assert   True", 10),
            _row("assert_true", "a.py", "assert True", 20)]
    groups = audit.group_repeats(rows)
    assert len(groups) == 1 and groups[0]["count"] == 2


def test_empty_code_never_grouped():
    rows = [_row("assert_true", "a.py", "", 10),
            _row("assert_true", "a.py", "", 20)]
    assert audit.group_repeats(rows) == []
