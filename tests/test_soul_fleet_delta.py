"""Tests for tools/soul_fleet_delta.py -- pure-logic + CLI exit contract."""

import json

import pytest

from tools.soul_fleet_delta import (
    apply_first_seen,
    diff_reports,
    findings_map,
    main,
)


def _report(rows):
    return {"repos": [{"name": n, "findings": f} for n, f in rows]}


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_new_and_resolved_detected():
    prev = findings_map(_report([("a", ["X", "Y"])]))
    cur = findings_map(_report([("a", ["Y", "Z"])]))
    d = diff_reports(prev, cur)
    assert d["a"]["new"] == ["Z"]
    assert d["a"]["resolved"] == ["X"]
    assert d["a"]["persisting"] == ["Y"]


def test_identical_means_persisting_not_new():
    m = findings_map(_report([("a", ["X"])]))
    d = diff_reports(m, m)
    assert d["a"]["new"] == [] and d["a"]["resolved"] == []
    assert d["a"]["persisting"] == ["X"]


def test_repo_appearing_and_vanishing():
    d = diff_reports({}, findings_map(_report([("b", ["Q"])])))
    assert d["b"]["new"] == ["Q"]


def test_first_seen_stamps_and_ages(tmp_path):
    diff = {"a": {"new": ["N"], "resolved": [],
                  "persisting": ["P"]}}
    state = {"a": {"P": "2020-01-01"}}
    out, new_state = apply_first_seen(diff, state, "2020-02-01", 14)
    persisting = out["a"]["persisting"]
    assert persisting[0]["finding"] == "P"
    assert persisting[0]["age_days"] == 31
    assert persisting[0]["due"] is True
    assert new_state["a"]["N"] == "2020-02-01"  # stamped today
    assert "P" in new_state["a"]


def test_not_due_when_young(tmp_path):
    diff = {"a": {"new": [], "resolved": [], "persisting": ["P"]}}
    out, _ = apply_first_seen(diff, {"a": {"P": "2020-02-01"}},
                               "2020-02-05", 14)
    assert out["a"]["persisting"][0]["due"] is False


def test_cli_exit_contract(tmp_path):
    prev = _write(tmp_path / "p.json", _report([("a", ["X"])]))
    same = _write(tmp_path / "s.json", _report([("a", ["X"])]))
    assert main(["--prev", prev, "--cur", same]) == 0
    changed = _write(tmp_path / "c.json", _report([("a", ["X", "Y"])]))
    assert main(["--prev", prev, "--cur", changed,
                 "--state", str(tmp_path / "st.json")]) == 1
    assert main(["--prev", str(tmp_path / "nope.json"),
                 "--cur", changed]) == 2


def test_cli_writes_json_and_state(tmp_path):
    prev = _write(tmp_path / "p.json", _report([("a", ["X"])]))
    cur = _write(tmp_path / "c.json", _report([("a", ["X", "Y"])]))
    out = tmp_path / "d.json"
    st = tmp_path / "st.json"
    assert main(["--prev", prev, "--cur", cur, "--json", str(out),
                 "--state", str(st)]) == 1
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["new"] == 1
    assert data["diff"]["a"]["new"] == ["Y"]
    assert "Y" in json.loads(st.read_text(encoding="utf-8"))["a"]
