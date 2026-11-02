"""Tests for cradle.py -- the front door a stranger actually meets first.

Two properties matter more than coverage:

* `--doctor` FAILS when a part is missing. A doctor that reports READY on a broken
  installation is worse than no doctor, because it sends the user looking elsewhere.
* `--demo` proves the LOOP, including a failed verification and the lesson it writes.
  A demo that only walks the happy path would pass on a chain whose memory is empty --
  which is exactly the state this project shipped in until now.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
CRADLE = HERE / "cradle.py"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def _load():
    spec = importlib.util.spec_from_file_location("cradle_under_test", CRADLE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cradle = _load()


def test_the_four_parts_are_where_the_launcher_says() -> None:
    for name, path in cradle.PARTS.items():
        assert path.exists(), "%s is missing at %s" % (name, path)


def test_doctor_reports_ready_on_this_tree() -> None:
    assert cradle.doctor() == 0


def test_doctor_fails_when_a_part_is_missing(monkeypatch, tmp_path: Path) -> None:
    """The control: a broken installation must NOT report READY."""
    broken = dict(cradle.PARTS)
    broken["sentinel"] = tmp_path / "gone.py"
    monkeypatch.setattr(cradle, "PARTS", broken)
    assert cradle.doctor() == 1


def test_doctor_names_the_model_as_absent_rather_than_failing() -> None:
    """No model is a supported state: /ask says 503, so doctor must not say FAIL."""
    assert cradle.doctor(model_url="") == 0


def test_demo_passes_and_shows_the_failure_path(capsys) -> None:
    assert cradle.demo() == 0
    out = capsys.readouterr().out
    assert "verification FAILED" in out
    assert "lesson recalled" in out
    assert "BLOCKED" in out


def test_demo_json_is_parseable_and_has_every_step(capsys) -> None:
    assert cradle.demo(json_out=True) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    steps = [step["step"] for step in payload["steps"]]
    assert any("ghost" in step for step in steps), steps
    assert any("lesson" in step for step in steps), steps


def test_doctor_prints_the_true_names(capsys) -> None:
    """The vocabulary is visible at the front door, not folklore in a document."""
    assert cradle.doctor() == 0
    out = capsys.readouterr().out
    assert "REAPER (sentinel)" in out, out
    assert "GRIMOIRE (memory)" in out, out


def test_the_names_are_vocabulary_and_not_file_names() -> None:
    """REAPER and GRIMOIRE name the roles; the paths keep their names on purpose.

    Five gates, a task file and three documents quote `sentinel.py` and `lessons.jsonl`.
    A rename to match a story would break the checks that make the story worth telling,
    so the names live in the vocabulary and the disk says what it always said.
    """
    sentinel = cradle._load("sentinel", cradle.PARTS["sentinel"])
    bridge = cradle._load("memory_bridge", cradle.PARTS["memory"])
    assert sentinel.NAME == "REAPER"
    assert bridge.GRIMOIRE_NAME == "GRIMOIRE"
    assert bridge.GRIMOIRE == bridge.LESSONS_FILE == "lessons.jsonl"
    assert cradle.PARTS["sentinel"].name == "sentinel.py"


def test_grimoire_says_no_book_rather_than_nothing_learned(tmp_path: Path, capsys) -> None:
    """A fresh directory has no book; that is not the same as a book with no lessons."""
    assert cradle.grimoire(state_dir=str(tmp_path)) == 0
    out = capsys.readouterr().out
    assert "no book yet" in out, out


def test_grimoire_prints_what_a_failure_wrote(tmp_path: Path, capsys) -> None:
    bridge = cradle._load("memory_bridge", cradle.PARTS["memory"])
    bridge.record_verification("f-test", "pytest -q", 1, observed="1 failed",
                               state_dir=str(tmp_path))
    bridge.record_lesson("a shard whose golden run does not reproduce cannot land",
                         kind="ruleset", trigger="metthew_validate",
                         state_dir=str(tmp_path))
    assert cradle.grimoire(state_dir=str(tmp_path)) == 0
    out = capsys.readouterr().out
    assert "2 lesson(s)" in out, out
    assert "failed-verification" in out and "because: metthew_validate" in out, out
    assert cradle.grimoire(state_dir=str(tmp_path), kind="ruleset") == 0
    filtered = capsys.readouterr().out
    assert "1 of kind 'ruleset'" in filtered, filtered


def test_an_unreadable_grimoire_is_a_failure_not_a_skip(tmp_path: Path, capsys) -> None:
    """The control: a corrupt line must exit 1 and name the line, never be skipped."""
    ledger = tmp_path / "lessons.jsonl"
    ledger.write_text('{"content": "a real lesson about landing"}\nnot json\n',
                      encoding="utf-8")
    assert cradle.grimoire(state_dir=str(tmp_path)) == 1
    out = capsys.readouterr().out
    assert "UNREADABLE" in out and "line 2" in out, out


def test_the_launcher_defaults_to_doctor(monkeypatch) -> None:
    """Running the file with no arguments answers the question a new user has."""
    called = {}

    def fake_doctor(model_url="", json_out=False):
        called["doctor"] = True
        return 0

    monkeypatch.setattr(cradle, "doctor", fake_doctor)
    assert cradle.main([]) == 0
    assert called.get("doctor") is True
