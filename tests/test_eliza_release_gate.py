# coding: utf-8
"""Publication-gate tests: every rule must be shown to fire, not just to pass.

The ELIZA gate's 2026-11-15 reading was 2,052 "undeclared files" and 6 "secrets",
and both numbers were the gate's own defect:

* every undeclared path was under `adopted/`, which `.gitignore` excludes -- it is
  not published, so declaring it in PUBLIC_MANIFEST.json would assert a false
  thing, and no correct edit to the project could clear the finding;
* four of the six secrets were a class (`token = CancellationToken()`) and a call
  (`api_key = _read_config_key(name)`) matched by a rule that accepted any bare
  run of 16+ word characters.

So each test below drives both directions: the narrowed rule is silent on the
shapes every credentialed module uses, and still fires on a quoted literal. A
check that has only ever been seen to pass has not been tested.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Project_ELIZA" / "tools"))

import eliza_release_gate as G

PROJECT = ROOT / "Project_ELIZA"


# --- the real tree ----------------------------------------------------------


def test_the_real_project_passes():
    """The gate is green on this tree, and says so with zero failures."""
    report = G.run_checks()
    assert report["failures"] == 0, report["checks"]
    assert report["result"] == "PASS"


def test_the_real_tree_reports_how_much_it_skipped():
    """A skip that is not counted is a silent pass: the count is part of the report."""
    report = G.run_checks()
    assert report["git_ignored_skipped"] > 0
    assert report["checks"]["undeclared_files"] == []
    assert report["checks"]["not_published"] == []


# --- git-ignored paths ------------------------------------------------------


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Bounded: a hung git in a test is a hung suite, not a slow one."""
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, timeout=60)


def _repo(tmp_path: Path) -> Path:
    """A project directory that is a repository with one ignored subtree."""
    if shutil.which("git") is None:
        pytest.skip("git is required to read ignore rules")
    project = tmp_path / "Project_ELIZA"
    (project / "ignored").mkdir(parents=True)
    (project / ".gitignore").write_text("/ignored/\n", encoding="utf-8")
    (project / "ignored" / "mirror.py").write_text("#" * 5000, encoding="utf-8")
    (project / "evidence.py").write_text("#" * 5000, encoding="utf-8")
    if _git("init", "-q", cwd=project).returncode != 0:
        pytest.skip("git init failed in the temporary directory")
    return project


def test_ignored_paths_are_exactly_the_ones_git_ignores(tmp_path):
    project = _repo(tmp_path)
    files = [path for path in project.rglob("*") if path.is_file()]
    ignored = G.ignored_paths(files, project)
    assert ignored == {(project / "ignored" / "mirror.py").resolve()}


def test_undeclared_check_skips_ignored_paths_but_not_the_rest(tmp_path):
    """Both directions: the mirror is exempted by the ignore list, and only by it."""
    project = _repo(tmp_path)
    files = [path for path in project.rglob("*") if path.is_file()]
    manifest = {"ship": []}
    without = G.check_undeclared(manifest, project)
    assert any("mirror.py" in problem for problem in without)
    with_ignore = G.check_undeclared(manifest, project, ignored=G.ignored_paths(files, project))
    assert any("evidence.py" in problem for problem in with_ignore)
    assert not any("mirror.py" in problem for problem in with_ignore)


def test_ignored_paths_is_empty_when_git_cannot_read_the_tree(tmp_path):
    """Fail closed: a git that cannot read the tree must not exempt anything.

    The existence of a repository is not something this test can arrange here --
    pytest's temporary directory sits inside the developer's home repository -- so
    the reading is aimed at the branch that matters: git refuses (`-C` on a path
    that does not exist, like a checkout without one), the set is empty, and every
    path is judged as before. An unavailable git must never widen what ships.
    """
    (tmp_path / "kept.py").write_text("#" * 5000, encoding="utf-8")
    files = [path for path in tmp_path.rglob("*") if path.is_file()]
    assert G.ignored_paths(files, tmp_path / "absent-tree") == set()


# --- not_published ----------------------------------------------------------


def test_not_published_entry_without_a_reason_is_reported():
    manifest = {"not_published": [{"path": "HARDWARE.md", "why": ""}]}
    problems = G.check_not_published(manifest, PROJECT)
    assert len(problems) == 1
    assert "without saying why" in problems[0]


def test_not_published_entry_for_a_missing_path_is_reported():
    manifest = {"not_published": [{"path": "GONE.md", "why": "a reason that is long enough"}]}
    problems = G.check_not_published(manifest, PROJECT)
    assert len(problems) == 1
    assert "does not exist" in problems[0]


def test_not_published_exempts_a_path_from_undeclared(tmp_path):
    (tmp_path / "internal.py").write_text("#" * 5000, encoding="utf-8")
    manifest = {"ship": [], "not_published": [
        {"path": "internal.py", "why": "substrate state, never published"},
    ]}
    assert G.check_undeclared(manifest, tmp_path)  # undeclared while undecided
    assert G.check_undeclared(
        manifest, tmp_path, exempt=G.not_published_paths(manifest, tmp_path)
    ) == []


# --- the assigned-secret rule -----------------------------------------------


def _scan(tmp_path: Path, text: str):
    path = tmp_path / "module.py"
    path.write_text(text, encoding="utf-8")
    return G.scan_secrets(path)


def test_secret_rule_is_silent_on_a_class_and_a_call(tmp_path):
    """`CancellationToken()` and `_read_config_key(name)` were 4 of 6 false findings."""
    text = (
        "token = CancellationToken()\n"
        "api_key = _read_config_key(name)\n"
        "secret = os.environ['OPENAI_API_KEY']\n"
    )
    assert _scan(tmp_path, text) == []


def test_secret_rule_fires_on_a_quoted_literal(tmp_path):
    findings = _scan(tmp_path, 'api_key = "sk-live-0123456789abcdefABCDEF"\n')
    assert len(findings) == 1
    assert findings[0]["rule"] == "assigned_secret"
    # The finding names the rule and a length, never the secret: a scanner that
    # prints what it found has copied the secret into the log.
    assert "sk-live" not in findings[0]["masked"]
    assert "0123456789" not in findings[0]["masked"]
