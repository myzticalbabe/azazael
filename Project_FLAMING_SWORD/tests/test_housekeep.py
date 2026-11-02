# coding: utf-8
"""tests for the housekeeping pass: both directions, and the three refusals.

A cleaner is the one tool in this project that can destroy work, so every safety
rule is tested as a refusal rather than trusted because it is written down: a
tracked file, a symlink, and a path outside the root. Each of those must survive
an `apply()`, not merely be excluded from a printed list.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sword", PROJECT / "tools" / "sword.py")
sword = importlib.util.module_from_spec(_spec)
sys.modules["sword"] = sword
_spec.loader.exec_module(sword)

housekeep = sword.housekeep


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=str(root), check=True, timeout=120)
    subprocess.run(["git", "config", "user.email", "t@example.invalid"], cwd=str(root),
                   timeout=60)
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(root), timeout=60)
    (root / sword.STATE_DIR).mkdir()
    return root


def _tracked(repo, *names):
    subprocess.run(["git", "add", *names], cwd=str(repo), check=True, timeout=120)


def _rules(items):
    return {(item["rule"], item["path"], item["action"]) for item in items}


# -- the deletes it is for ---------------------------------------------------

def test_it_plans_caches_leftovers_and_empty_directories(repo):
    (repo / "pkg" / "__pycache__").mkdir(parents=True)
    (repo / "pkg" / "__pycache__" / "m.cpython-315.pyc").write_bytes(b"x" * 2048)
    (repo / "pkg" / "mod.py").write_text("X = 1\n", encoding="utf-8")
    (repo / ".pytest_cache").mkdir()
    (repo / ".pytest_cache" / "CACHEDIR.TAG").write_text("x\n", encoding="utf-8")
    (repo / "notes.md.orig").write_text("x\n", encoding="utf-8")
    (repo / "gone").mkdir()

    items = housekeep.collect(repo)
    planned = _rules(items)
    assert ("bytecode-cache", "pkg/__pycache__", "delete") in planned
    assert ("tool-cache", ".pytest_cache", "delete") in planned
    assert ("editor-leftover", "notes.md.orig", "delete") in planned
    assert ("empty-directory", "gone", "delete") in planned
    # The directory holding real content is not empty and is not offered.
    assert not any(path == "pkg" for _rule, path, _action in planned)


def test_nothing_is_deleted_without_apply(repo):
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "a.pyc").write_bytes(b"x")
    housekeep.collect(repo)
    assert (repo / "__pycache__").exists(), "planning must not delete"


def test_apply_deletes_and_writes_the_deletion_log(repo):
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "a.pyc").write_bytes(b"x" * 1000)
    items = housekeep.collect(repo)
    removed, freed, failures = housekeep.apply(repo, items)
    assert failures == []
    assert removed == 1 and freed >= 1000
    assert not (repo / "__pycache__").exists()
    log = repo / sword.STATE_DIR / "housekeep.jsonl"
    rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert rows and rows[0]["path"] == "__pycache__" and rows[0]["rule"] == "bytecode-cache"


# -- the three refusals ------------------------------------------------------

def test_a_tracked_file_inside_a_cache_directory_is_never_deleted(repo):
    """The refusal that matters: git owns that file, so the whole directory stays."""
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "kept.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "__pycache__" / "a.pyc").write_bytes(b"x")
    _tracked(repo, "__pycache__/kept.py")

    items = housekeep.collect(repo)
    assert ("bytecode-cache", "__pycache__", "keep") in _rules(items)
    housekeep.apply(repo, items)
    assert (repo / "__pycache__" / "kept.py").exists()


def test_a_tracked_leftover_file_is_content_and_survives(repo):
    (repo / "config.bak").write_text("real content\n", encoding="utf-8")
    _tracked(repo, "config.bak")
    items = housekeep.collect(repo)
    assert ("editor-leftover", "config.bak", "keep") in _rules(items)
    housekeep.apply(repo, items)
    assert (repo / "config.bak").exists()


def test_a_symlinked_directory_is_not_followed_or_removed(repo, tmp_path):
    outside = tmp_path / "outside"
    (outside / "__pycache__").mkdir(parents=True)
    (outside / "__pycache__" / "precious.pyc").write_bytes(b"x")
    try:
        os.symlink(str(outside), str(repo / "linked"))
    except (OSError, NotImplementedError):
        pytest.skip("this host cannot create a directory symlink without privileges")

    items = housekeep.collect(repo)
    assert not any(item["path"].startswith("linked") for item in items)
    housekeep.apply(repo, items)
    assert (outside / "__pycache__" / "precious.pyc").exists()


def test_git_being_unreadable_does_not_license_deleting_content(repo, monkeypatch):
    """No git, no proof, so only well-known caches are touched."""
    monkeypatch.setattr(housekeep, "tracked_paths", lambda _root: None)
    (repo / "__pycache__").mkdir()
    (repo / "__pycache__" / "a.pyc").write_bytes(b"x")
    (repo / "thing.md.orig").write_text("x\n", encoding="utf-8")
    (repo / "big.bin").write_bytes(b"x" * 1024)

    items = housekeep.collect(repo)
    planned = _rules(items)
    assert ("bytecode-cache", "__pycache__", "delete") in planned
    assert not any(rule == "editor-leftover" and action == "delete"
                   for rule, _path, action in planned)
    # Without a tracked set there is no untracked set either, so no size hazard
    # is invented: the tool does not guess what git would have said.
    assert not any(rule == "large-untracked" for rule, _path, _action in planned)


# -- the hazards it reports and never removes --------------------------------

def test_an_unlanded_batch_is_reported_and_kept(repo):
    rows = [{"at": "2026-11-01T00:00:00Z", "fixed": ["a", "b"], "failed": [],
             "touched": ["x.py"], "test": "pytest", "verified": "6 passed",
             "landed": None},
            {"at": "2026-11-02T00:00:00Z", "fixed": ["c"], "failed": [],
             "touched": ["y.py"], "test": "pytest", "verified": "6 passed",
             "landed": "abc1234"}]
    (repo / sword.STATE_DIR / "batches.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    items = housekeep.collect(repo)
    hazards = [item for item in items if item["rule"] == "unlanded-batch"]
    assert len(hazards) == 1, hazards
    assert hazards[0]["action"] == "keep"
    assert "2 item(s)" in hazards[0]["why"]
    housekeep.apply(repo, items)
    assert (repo / sword.STATE_DIR / "batches.jsonl").exists()


def test_an_oversized_untracked_file_is_reported_not_removed(repo):
    (repo / "scratch.bin").write_bytes(b"x" * (2 * 1024 * 1024))
    items = housekeep.collect(repo, max_mb=1)
    hazards = [item for item in items if item["rule"] == "large-untracked"]
    assert [item["path"] for item in hazards] == ["scratch.bin"]
    assert hazards[0]["action"] == "keep"
    housekeep.apply(repo, items)
    assert (repo / "scratch.bin").exists()


def test_disposable_state_is_aged_out_but_the_landing_record_is_not(repo):
    state = repo / sword.STATE_DIR
    for name in ("findings.jsonl", "queue.jsonl"):
        (state / name).write_text("{}\n", encoding="utf-8")
        os.utime(state / name, (0, 0))          # epoch: older than any threshold
    (state / "batches.jsonl").write_text("", encoding="utf-8")
    os.utime(state / "batches.jsonl", (0, 0))

    items = housekeep.collect(repo)
    planned = {item["path"] for item in items if item["rule"] == "sweep-state"}
    assert planned == {".flaming_sword/findings.jsonl", ".flaming_sword/queue.jsonl"}
    housekeep.apply(repo, items)
    assert (state / "batches.jsonl").exists(), "the landing record is history, not garbage"


def test_fresh_state_is_left_alone(repo):
    state = repo / sword.STATE_DIR
    (state / "findings.jsonl").write_text("{}\n", encoding="utf-8")
    items = housekeep.collect(repo, state_days=14)
    assert not any(item["rule"] == "sweep-state" for item in items)


# -- the parent-directory direction -----------------------------------------

def test_a_parent_is_only_called_empty_when_the_pass_would_really_empty_it(repo):
    """`pkg/` holds only a cache dir: after the pass it holds nothing, so it goes.

    The pairing matters: reporting `pkg` as empty while leaving `pkg/__pycache__`
    behind would be wrong by one pass, and the next run would find one more.
    """
    (repo / "pkg" / "__pycache__").mkdir(parents=True)
    items = housekeep.collect(repo)
    housekeep.apply(repo, items)
    assert not (repo / "pkg").exists()

    (repo / "kept" / "__pycache__").mkdir(parents=True)
    (repo / "kept" / "real.py").write_text("X = 1\n", encoding="utf-8")
    items = housekeep.collect(repo)
    housekeep.apply(repo, items)
    assert (repo / "kept" / "real.py").exists()
    assert (repo / "kept").exists()


def test_the_cli_refuses_apply_without_housekeep(tmp_path):
    assert sword.main(["--root", str(tmp_path), "--apply"]) == 2


def test_the_cli_reports_without_deleting(tmp_path, capsys):
    root = tmp_path / "tree"
    (root / "__pycache__").mkdir(parents=True)
    assert sword.main(["--root", str(root), "--housekeep"]) == 0
    assert "dry run" in capsys.readouterr().out
    assert (root / "__pycache__").exists()
