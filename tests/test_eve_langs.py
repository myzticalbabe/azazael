"""G1 test for src/eve_unleashed/langs.py.

Real toolchains, tiny files: good files check clean, bad files fail by
name, formatting fixes formatting, and backups exist before any write.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from eve_unleashed.langs import check, detect, fix, fmt, have_tools

GOOD_RS = 'pub fn add(a: i32, b: i32) -> i32 {\n    a + b\n}\n'
BAD_RS = 'pub fn add(a: i32, b: i32) -> i32 {\n    a + \n}\n'
GOOD_GO = 'package main\n\nfunc Add(a, b int) int {\n\treturn a + b\n}\n'
BADFMT_GO = 'package main\n\nfunc Add(a, b int) int {\nreturn a + b\n}\n'


def test_detect_three_ways():
    from eve_unleashed.langs import detect as d
    assert d("x.rs") == "rust" and d("x.go") == "go"
    with pytest.raises(ValueError):
        d("x.py")


def test_good_files_check_clean(tmp_path):
    rs = tmp_path / "a.rs"
    rs.write_text(GOOD_RS, encoding="utf-8")
    assert check(rs)["ok"], check(rs)["diagnostics"]
    go = tmp_path / "a.go"
    go.write_text(GOOD_GO, encoding="utf-8")
    assert check(go)["ok"], check(go)["diagnostics"]


def test_bad_rust_fails_naming_the_bug(tmp_path):
    rs = tmp_path / "b.rs"
    rs.write_text(BAD_RS, encoding="utf-8")
    rep = check(rs)
    assert not rep["ok"]
    assert "expected" in rep["diagnostics"].lower()


def test_fmt_fixes_go_layout_with_backup(tmp_path):
    go = tmp_path / "c.go"
    go.write_text(BADFMT_GO, encoding="utf-8")
    assert fmt(go) is True
    assert (tmp_path / "c.go.evelang.bak").is_file()
    assert check(go)["ok"]


def test_fix_report_shape(tmp_path):
    go = tmp_path / "d.go"
    go.write_text(BADFMT_GO, encoding="utf-8")
    rep = fix(go)
    assert rep["fixed_by_format"] and rep["clean"] is True
