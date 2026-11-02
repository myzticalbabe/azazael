# coding: utf-8
"""tests for the disposition ledger: one error, one task, recorded at encounter time.

The ledger is the part of the sweep that outlives the run, so the tests are about
the properties that make it usable a day later: distinct errors stay distinct, a
repeat is counted rather than duplicated, a recurrence after a decision is a new
fact, and a closed task cannot be closed twice into two different stories.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sword", PROJECT / "tools" / "sword.py")
sword = importlib.util.module_from_spec(_spec)
sys.modules["sword"] = sword
_spec.loader.exec_module(sword)

disposition = sword.disposition


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True, timeout=120)
    subprocess.run(["git", "config", "user.email", "t@example.invalid"], cwd=str(root),
                   timeout=60)
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(root), timeout=60)
    (root / sword.STATE_DIR).mkdir()
    (root / sword.STATE_DIR / "config.json").write_text(
        json.dumps({"constants": []}), encoding="utf-8")
    return root


# -- one error, one task -----------------------------------------------------

def test_an_error_becomes_one_task(repo):
    row = disposition.record(repo, "scan", "detector-unrun", "stale-claims",
                             "stale-claims could not run: no claims.command")
    assert row["id"] == "t-0001"
    assert row["status"] == "open" and row["seen"] == 1
    assert row["stage"] == "scan" and row["kind"] == "detector-unrun"
    assert disposition.tasks(repo) == [row]


def test_two_different_errors_are_two_tasks(repo):
    first = disposition.record(repo, "scan", "detector-unrun", "stale-claims", "a")
    second = disposition.record(repo, "scan", "detector-unrun", "duplicate-constant", "b")
    assert {first["id"], second["id"]} == {"t-0001", "t-0002"}
    assert len(disposition.tasks(repo)) == 2


def test_the_same_error_twice_is_counted_not_duplicated(repo):
    """A scan that runs every minute must not make a thousand identical rows."""
    disposition.record(repo, "scan", "detector-unrun", "stale-claims", "first")
    row = disposition.record(repo, "scan", "detector-unrun", "stale-claims", "second")
    rows = disposition.tasks(repo)
    assert len(rows) == 1
    assert row["seen"] == 2
    assert row["what"] == "second", "the latest evidence replaces the stale one"
    assert row["last_seen"] >= row["first_seen"]


def test_the_same_message_with_a_changing_count_stays_one_task(repo):
    """Identity is stage+kind+subject, never the message: a count inside the
    message changes while the defect does not."""
    disposition.record(repo, "fix", "fix-failed", "two-interpreters:abc", "3 item(s) failed")
    row = disposition.record(repo, "fix", "fix-failed", "two-interpreters:abc",
                             "4 item(s) failed")
    assert len(disposition.tasks(repo)) == 1
    assert row["seen"] == 2


# -- disposition -------------------------------------------------------------

def test_a_disposed_task_leaves_the_open_list_and_keeps_its_reason(repo):
    row = disposition.record(repo, "scan", "detector-unrun", "stale-claims", "no ledger")
    closed = disposition.dispose(repo, row["id"], "wontfix", "the ledger is being rebuilt")
    assert closed["status"] == "disposed"
    assert closed["disposition"] == "wontfix"
    assert closed["note"] == "the ledger is being rebuilt"
    assert closed["disposed_at"]
    assert disposition.tasks(repo) == []
    assert [item["id"] for item in disposition.tasks(repo, include_disposed=True)] == [row["id"]]


def test_a_recurrence_after_a_decision_is_a_new_task(repo):
    """The error came back, so it is a new fact about the tree, not a new opinion."""
    first = disposition.record(repo, "scan", "detector-unrun", "stale-claims", "no ledger")
    disposition.dispose(repo, first["id"], "fixed", "added the ledger")
    second = disposition.record(repo, "scan", "detector-unrun", "stale-claims", "no ledger")
    assert second["id"] != first["id"]
    assert second["identity"] == first["identity"]
    assert [item["id"] for item in disposition.tasks(repo)] == [second["id"]]


def test_a_task_cannot_be_disposed_twice_into_two_stories(repo):
    row = disposition.record(repo, "scan", "detector-unrun", "x", "y")
    disposition.dispose(repo, row["id"], "fixed")
    with pytest.raises(ValueError):
        disposition.dispose(repo, row["id"], "wontfix")


def test_disposing_an_unknown_id_returns_none(repo):
    assert disposition.dispose(repo, "t-9999", "fixed") is None


def test_an_invalid_disposition_is_refused(repo):
    row = disposition.record(repo, "scan", "detector-unrun", "x", "y")
    with pytest.raises(ValueError):
        disposition.dispose(repo, row["id"], "because i said so")


# -- wired into the sweep ----------------------------------------------------

def test_a_crashing_detector_is_recorded_as_a_task(repo, monkeypatch):
    def exploding(_root):
        raise RuntimeError("the instrument fell over")

    monkeypatch.setattr(sword, "DETECTORS", (("exploder", exploding),))
    findings, unrun = sword.scan(repo)
    assert findings == [] and any("UNRUN" in note for note in unrun)
    rows = disposition.tasks(repo)
    assert [row["kind"] for row in rows] == ["detector-crashed"]
    assert rows[0]["subject"] == "exploder"
    assert "RuntimeError" in rows[0]["what"]


def test_an_unrun_detector_is_recorded_as_its_own_task(repo):
    """The real case: stale-claims with no claims.command configured."""
    sword.scan(repo)
    rows = {row["subject"]: row for row in disposition.tasks(repo)}
    assert "stale-claims" in rows
    assert rows["stale-claims"]["kind"] == "detector-unrun"
    assert "claims" in rows["stale-claims"]["remedy"]


def test_a_refused_landing_is_recorded_with_its_reason(repo):
    assert sword.land(repo, None) == 1
    rows = disposition.tasks(repo)
    assert [row["subject"] for row in rows] == ["no-test-command"]
    assert rows[0]["stage"] == "land" and rows[0]["kind"] == "refused"


def test_a_second_scan_does_not_multiply_the_same_unrun(repo):
    sword.scan(repo)
    before = len(disposition.tasks(repo))
    sword.scan(repo)
    rows = disposition.tasks(repo)
    assert len(rows) == before
    assert all(row["seen"] >= 2 for row in rows)


# -- the CLI ----------------------------------------------------------------

def test_the_cli_lists_open_tasks(repo, capsys):
    disposition.record(repo, "scan", "detector-unrun", "stale-claims", "no claims company")
    assert sword.main(["--root", str(repo), "--tasks"]) == 0
    out = capsys.readouterr().out
    assert "t-0001" in out and "stale-claims" in out


def test_the_cli_refuses_dispose_without_a_decision(repo, capsys):
    row = disposition.record(repo, "scan", "detector-unrun", "x", "y")
    assert sword.main(["--root", str(repo), "--dispose", row["id"]]) == 2
    assert "REFUSED" in capsys.readouterr().out


def test_the_cli_disposes_and_the_task_leaves_the_queue(repo, capsys):
    row = disposition.record(repo, "scan", "detector-unrun", "x", "y")
    assert sword.main(["--root", str(repo), "--dispose", row["id"], "--as", "duplicate",
                       "--note", "same as t-0001"]) == 0
    assert disposition.tasks(repo) == []
    assert "disposed" in capsys.readouterr().out


def test_the_ledger_is_one_json_object_per_line(repo):
    """The format is the contract: a reader tails it, an editor appends to it."""
    disposition.record(repo, "scan", "detector-unrun", "x", "y")
    disposition.record(repo, "fix", "fix-failed", "z", "w")
    path = repo / sword.STATE_DIR / "tasks.jsonl"
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert len(lines) == 2
    assert all(isinstance(json.loads(line), dict) for line in lines)
