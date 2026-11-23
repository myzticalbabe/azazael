# coding: utf-8
"""Tests for tools/soul_fleet_sweep.py -- the corrective leg.

Each test builds one fixture tree class the 2026-11-23 hygiene round met
in the wild: a clean repo, a licence-defect repo, an unborn project dir
(github.io's class: invisible to every gate), a dirty worktree
(flame-engine's class: the fix sits uncommitted), a repo tracking
generated paths (shardex build/tmp's class), and a non-project dir that
must be skipped, not flagged.
"""
import shutil
import subprocess

import pytest

import tools.soul_fleet_sweep as sweep

SOUL_LICENSE = (
    "Soul Forge License v1.0\n"
    "Source: https://github.com/myzticalbabe/fixture-x\n"
)

NEEDS_GIT = pytest.mark.skipif(
    shutil.which("git") is None, reason="fleet sweep shells out to git")


def _git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    *args], cwd=str(cwd), check=True, capture_output=True,
                    timeout=120)


@NEEDS_GIT
def test_clean_repo_passes(tmp_path):
    repo = tmp_path / "clean-repo"
    repo.mkdir()
    (repo / "LICENSE").write_text(SOUL_LICENSE, encoding="utf-8")
    _git("init", "-b", "main", cwd=repo)
    _git("add", "LICENSE", cwd=repo)
    _git("commit", "-m", "base", cwd=repo)
    entries = sweep.sweep(tmp_path, sweep.Path(__file__).resolve().parent
                          .parent / "tools" / "soul_licence_check.py", set())
    match = [e for e in entries if e["path"] == "clean-repo"]
    assert len(match) == 1 and match[0]["findings"] == []


@NEEDS_GIT
def test_defect_repo_flagged(tmp_path):
    repo = tmp_path / "defect-repo"
    repo.mkdir()
    (repo / "LICENSE").write_text(SOUL_LICENSE, encoding="utf-8")
    (repo / "CITATION.cff").write_text('license: "CDDL-1.1"\n', encoding="utf-8")
    _git("init", "-b", "main", cwd=repo)
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    entry = sweep.check_repo(repo, checker)
    assert any(f.startswith("LICENCE-DEFECTS") for f in entry["findings"])


def test_unborn_project_dir_flagged(tmp_path):
    d = tmp_path / "unborn-proj"
    d.mkdir()
    (d / "pyproject.toml").write_text('[project]\nname = "x"\n', encoding="utf-8")
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    entries = sweep.sweep(tmp_path, checker, set())
    match = [e for e in entries if e["path"] == "unborn-proj"]
    assert len(match) == 1 and match[0]["kind"] == "unborn"
    assert any("UNBORN" in f for f in match[0]["findings"])


def test_license_only_dir_skipped(tmp_path):
    """A lone LICENSE is a text file, not a project (tools_bin class)."""
    d = tmp_path / "license-only"
    d.mkdir()
    (d / "LICENSE").write_text(SOUL_LICENSE, encoding="utf-8")
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    assert sweep.sweep(tmp_path, checker, set()) == []


def test_non_project_dir_skipped(tmp_path):
    (tmp_path / "notes").mkdir()
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    assert sweep.sweep(tmp_path, checker, set()) == []


@NEEDS_GIT
def test_dirty_worktree_flagged(tmp_path):
    repo = tmp_path / "dirty-repo"
    repo.mkdir()
    (repo / "LICENSE").write_text(SOUL_LICENSE, encoding="utf-8")
    _git("init", "-b", "main", cwd=repo)
    _git("add", "LICENSE", cwd=repo)
    (repo / "LICENSE").write_text(SOUL_LICENSE + "touched\n", encoding="utf-8")
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    entry = sweep.check_repo(repo, checker)
    assert any(f.startswith("DIRTY") for f in entry["findings"])


@NEEDS_GIT
def test_tracked_build_flagged(tmp_path):
    repo = tmp_path / "build-repo"
    (repo / "build").mkdir(parents=True)
    (repo / "LICENSE").write_text(SOUL_LICENSE, encoding="utf-8")
    (repo / "build" / "stale.txt").write_text("x", encoding="utf-8")
    _git("init", "-b", "main", cwd=repo)
    _git("add", "LICENSE", "build/stale.txt", cwd=repo)
    checker = sweep.Path(__file__).resolve().parents[1] / "tools" / "soul_licence_check.py"
    entry = sweep.check_repo(repo, checker)
    assert any(f.startswith("STALE-BUILD") for f in entry["findings"])


def test_empty_root_returns_2(tmp_path, capsys):
    assert sweep.main(["--root", str(tmp_path)]) == 2
