# coding: utf-8
"""Tests for the git tooling: `tools/git_merge_gate.py`, `tools/git_stack_plan.py`,
`tools/git_repo_doctor.py`.

Why this file exists
--------------------
All three tools claim something about a repository that nobody can see by reading
the code: "this branch would merge", "this stack rebases cleanly", "this store is
healthy". Each of those is only true if the command underneath says what the tool
thinks it says, and one of them did not: measured 2026-11-01, `git multi-pack-index
verify` **exits 0 when no multi-pack-index exists at all**, so a verify-only health
check reported PASS on a store with none. `test_doctor_midx_absent_is_fail` is the
negative control for that exact defect -- it builds a two-pack repo with no MIDX and
asserts FAIL, which a verify-only check cannot pass.

Every test builds a real repository with real commits and real refs. Mocking git here
would test the mock: the behaviours under test (three-way merge in the object
database, ref updates in a transaction) are the reason the tools exist.

Skipping is explicit: a git too old for `merge-tree --write-tree` or `replay` skips
the tests that need it, and says why, rather than passing silently.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import git_fleet_audit as fleet  # noqa: E402
import git_merge_gate as gate  # noqa: E402
import git_repo_doctor as doctor  # noqa: E402
import git_stack_plan as stack  # noqa: E402

GIT = "git"


def git(repo, *args, check=True):
    # timeout= keeps the staged anti-pattern gate green (subprocess_no_timeout):
    # 120s is far beyond any fixture command here, so a hang is a defect worth a
    # failure rather than a wait.
    p = subprocess.run([GIT, "-c", "commit.gpgsign=false", *args], cwd=str(repo),
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120)
    if check and p.returncode != 0:
        raise AssertionError("git %s failed (%d): %s %s"
                             % (" ".join(args), p.returncode, p.stdout, p.stderr))
    return p


def init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "main", ".")
    git(path, "config", "user.email", "t@example.invalid")
    git(path, "config", "user.name", "Test")
    git(path, "config", "commit.gpgsign", "false")
    return path


def commit(repo: Path, filename: str, content: str, message: str) -> None:
    target = repo / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", filename)
    git(repo, "commit", "-q", "-m", message)


CAPS = doctor.check_capabilities()
needs_merge_tree = pytest.mark.skipif(
    not CAPS["merge-tree --write-tree"]["present"],
    reason="git merge-tree --write-tree needs git >= 2.38")
needs_replay = pytest.mark.skipif(
    not CAPS["replay"]["present"], reason="git replay is experimental (git >= 2.46)")


@pytest.fixture()
def clean_repo(tmp_path):
    """main + a branch that touches a different file: merges with no conflict."""
    repo = init_repo(tmp_path / "clean")
    commit(repo, "shared.txt", "base\n", "base")
    git(repo, "checkout", "-q", "-b", "feature")
    commit(repo, "feature.txt", "feature\n", "feature work")
    git(repo, "checkout", "-q", "main")
    commit(repo, "main.txt", "main\n", "main work")
    return repo


@pytest.fixture()
def conflict_repo(tmp_path):
    """main and branch edit the same line: a real three-way conflict."""
    repo = init_repo(tmp_path / "conflict")
    commit(repo, "shared.txt", "base\n", "base")
    git(repo, "checkout", "-q", "-b", "feature")
    commit(repo, "shared.txt", "feature\n", "feature edit")
    git(repo, "checkout", "-q", "main")
    commit(repo, "shared.txt", "main\n", "main edit")
    return repo


# ── merge gate ────────────────────────────────────────────────────────────────
@needs_merge_tree
def test_gate_clean_branch_is_clean_and_does_not_touch_worktree(clean_repo):
    before = git(clean_repo, "status", "--porcelain").stdout
    head_before = git(clean_repo, "rev-parse", "HEAD").stdout
    result = gate.gate(str(clean_repo), "main", ["feature"])
    row = result["branches"][0]
    assert row["state"] == "CLEAN", row
    assert row["ahead"] == 1 and row["behind"] == 1, row
    assert git(clean_repo, "status", "--porcelain").stdout == before
    assert git(clean_repo, "rev-parse", "HEAD").stdout == head_before


@needs_merge_tree
def test_gate_conflict_lists_the_path(conflict_repo):
    result = gate.gate(str(conflict_repo), "main", ["feature"])
    row = result["branches"][0]
    assert row["state"] == "CONFLICTS", row
    assert "shared.txt" in row["paths"], row


@needs_merge_tree
def test_gate_behind_and_same_are_not_merge_tested(clean_repo):
    # negative control for "ahead": a branch that adds no commits must never be
    # reported CLEAN. One behind base is MERGED (everything on it is already in
    # base, which is what a merge would achieve), and a branch whose tip IS base
    # is SAME. Reporting either as CLEAN would put a no-op in a merge queue.
    git(clean_repo, "branch", "behind-main", "main^")
    result = gate.gate(str(clean_repo), "main", ["behind-main"])
    assert result["branches"][0]["state"] == "MERGED", result["branches"][0]

    git(clean_repo, "branch", "same-as-main", "main")
    result = gate.gate(str(clean_repo), "main", ["same-as-main"])
    assert result["branches"][0]["state"] == "SAME", result["branches"][0]


@needs_merge_tree
def test_gate_merged_branch_is_reported_merged(clean_repo):
    git(clean_repo, "merge", "-q", "--no-ff", "-m", "merge feature", "feature")
    result = gate.gate(str(clean_repo), "main", ["feature"])
    assert result["branches"][0]["state"] == "MERGED", result["branches"][0]


def test_gate_unknown_branch_is_error_not_conflict(clean_repo):
    # exit > 1 from git is "could not attempt", not "conflicts"; a gate that
    # collapses the two reports work that does not exist.
    result = gate.gate(str(clean_repo), "main", ["no-such-branch"])
    row = result["branches"][0]
    assert row["state"] == "ERROR", row
    assert row["paths"] == []


def test_gate_cli_exit_codes(clean_repo, conflict_repo, capsys):
    assert gate.main(["--repo", str(clean_repo), "--base", "main"]) == 0
    assert gate.main(["--repo", str(conflict_repo), "--base", "main"]) == 1
    assert gate.main(["--repo", str(clean_repo), "--base", "no-such-base"]) == 2


# ── stack planner ─────────────────────────────────────────────────────────────
def test_stack_parents_are_derived_from_the_graph(clean_repo):
    # main moved after feature was cut, so the strict "is it an ancestor" test
    # fails -- the fork relation is what has to find main.
    git(clean_repo, "checkout", "-q", "feature")
    commit(clean_repo, "second.txt", "second\n", "second level")
    git(clean_repo, "checkout", "-q", "-b", "feature-two")
    commit(clean_repo, "third.txt", "third\n", "third level")
    git(clean_repo, "checkout", "-q", "main")

    branch_tips = stack.tips(str(clean_repo))
    parents = stack.derive_parents(str(clean_repo), branch_tips)
    assert parents["feature"]["parent"] == "main", parents["feature"]
    assert parents["feature"]["via"] == "fork", parents["feature"]
    assert parents["feature-two"]["parent"] == "feature", parents["feature-two"]
    assert parents["feature-two"]["via"] == "tip-ancestor", parents["feature-two"]
    chains = stack.stacks(branch_tips, parents)
    assert ["main", "feature", "feature-two"] in chains, chains


def test_stack_ambiguous_parent_is_reported_not_guessed(tmp_path):
    """Negative control: three branches off one commit, equal distance, no ancestry.

    There is no fact of the matter about which is the parent, so the planner must
    say AMBIGUOUS and refuse to replay. A tool that picks alphabetically would
    rebase real work onto an unrelated branch and call it a stack.
    """
    repo = init_repo(tmp_path / "ambiguous")
    commit(repo, "base.txt", "base\n", "base")
    for name in ("alpha", "beta", "gamma"):
        git(repo, "checkout", "-q", "-b", name, "main")
        commit(repo, name + ".txt", name + "\n", name + " work")
    # main advances, so no branch tip is an ancestor of another: the strict test
    # cannot help, and all three are equidistant from the fork point
    git(repo, "checkout", "-q", "main")
    commit(repo, "moved.txt", "moved\n", "main moves on")

    tips = stack.tips(str(repo))
    parents = stack.derive_parents(str(repo), tips)
    ambiguous = [b for b, p in parents.items() if p.get("via") == "ambiguous"]
    assert ambiguous, parents
    for b in ambiguous:
        assert parents[b]["parent"] is None
        assert len(parents[b]["candidates"]) >= 2


@needs_merge_tree
def test_stack_plan_reports_conflict_before_anything_is_written(conflict_repo):
    git(conflict_repo, "checkout", "-q", "feature")
    commit(conflict_repo, "top.txt", "top\n", "top of stack")
    git(conflict_repo, "branch", "feature-top")
    git(conflict_repo, "checkout", "-q", "main")

    before = {b: git(conflict_repo, "rev-parse", b).stdout.strip()
              for b in ("feature", "feature-top", "main")}
    tips = stack.tips(str(conflict_repo))
    parents = stack.derive_parents(str(conflict_repo), tips)
    chains = stack.stacks(tips, parents)
    chain = [c for c in chains if "feature" in c][0]
    steps = stack.plan_for(chain, "main", str(conflict_repo), tips)

    states = {s["branch"]: s["state"] for s in steps}
    assert states.get("feature") == "CONFLICT", steps
    # dry-run must not have moved a single ref
    after = {b: git(conflict_repo, "rev-parse", b).stdout.strip() for b in before}
    assert before == after


@needs_replay
def test_stack_apply_replays_a_clean_stack(tmp_path):
    repo = init_repo(tmp_path / "apply")
    commit(repo, "a.txt", "a\n", "base")
    git(repo, "checkout", "-q", "-b", "one")
    commit(repo, "one.txt", "1\n", "one")
    git(repo, "checkout", "-q", "-b", "two")
    commit(repo, "two.txt", "2\n", "two")
    git(repo, "checkout", "-q", "main")
    commit(repo, "main.txt", "m\n", "main moves")

    tips = stack.tips(str(repo))
    parents = stack.derive_parents(str(repo), tips)
    chains = stack.stacks(tips, parents)
    chain = [c for c in chains if "two" in c][0]

    steps = stack.plan_for(chain, "main", str(repo), tips)
    done = stack.apply_plan(str(repo), steps)
    assert all(row["rc"] == 0 for row in done), done

    main_sha = git(repo, "rev-parse", "main").stdout.strip()
    one_sha = git(repo, "rev-parse", "one").stdout.strip()
    two_sha = git(repo, "rev-parse", "two").stdout.strip()
    # each rebased branch now contains the new base, and the stack order survived
    assert git(repo, "merge-base", "--is-ancestor", main_sha, one_sha).returncode == 0
    assert git(repo, "merge-base", "--is-ancestor", one_sha, two_sha).returncode == 0
    # replay is object-database only: the commits exist under the new refs, and
    # the worktree is deliberately NOT updated (checking out is the caller's job).
    assert git(repo, "cat-file", "-e", "two:two.txt").returncode == 0
    assert not (repo / "two.txt").exists()


@needs_merge_tree
def test_stack_cli_check_mode_is_read_only(clean_repo):
    before = git(clean_repo, "rev-parse", "feature").stdout.strip()
    rc = stack.main(["--repo", str(clean_repo), "--onto", "main", "--check"])
    assert rc in (0, 1, 2)
    assert git(clean_repo, "rev-parse", "feature").stdout.strip() == before


# ── repo doctor ───────────────────────────────────────────────────────────────
def test_doctor_capabilities_are_probed_not_inferred():
    caps = doctor.check_capabilities()
    assert set(caps) == set(doctor.CAPABILITY_PROBES)
    for label, info in caps.items():
        assert isinstance(info["present"], bool), label
        assert "evidence" in info


def test_doctor_lone_pack_has_no_midx_requirement(tmp_path):
    repo = init_repo(tmp_path / "one-pack")
    commit(repo, "a.txt", "a\n", "one")
    git(repo, "repack", "-d", "-q")
    obj = doctor.check_objects()
    git_dir = str(repo / ".git")
    res = doctor.check_midx(git_dir, 1)
    assert res["status"] == "INFO", res
    assert obj["detail"]["packs"] >= 1


def test_doctor_midx_absent_is_fail(tmp_path):
    """The control for the defect this tool was rewritten to fix.

    Two packs, no MIDX. `git multi-pack-index verify` exits 0 here, so a
    verify-only check says PASS; the doctor must say FAIL.
    """
    repo = init_repo(tmp_path / "two-pack")
    commit(repo, "a.txt", "a\n", "one")
    git(repo, "repack", "-d", "-q")
    commit(repo, "b.txt", "b\n", "two")
    git(repo, "repack", "-d", "-q")
    git_dir = str(repo / ".git")
    packs = doctor.check_objects()["detail"]["packs"]
    assert packs >= 2, "fixture needs 2+ packs, got %d" % packs

    res = doctor.check_midx(git_dir, packs)
    assert res["status"] == "FAIL", res
    # and the verify alone would have passed -- the reason the check exists
    rc, _out, _err = doctor.run(["multi-pack-index", "verify"], cwd=str(repo))
    assert rc == 0


def test_doctor_fix_apply_writes_the_indexes_it_reported_missing(tmp_path):
    repo = init_repo(tmp_path / "fix")
    commit(repo, "a.txt", "a\n", "one")
    git(repo, "repack", "-d", "-q")
    commit(repo, "b.txt", "b\n", "two")
    git(repo, "repack", "-d", "-q")

    assert doctor.main(["--repo", str(repo), "--fix", "--apply"]) in (0, 1)
    assert (repo / ".git" / "objects" / "info" / "commit-graph").exists()
    assert (repo / ".git" / "objects" / "pack" / "multi-pack-index").exists()
    assert doctor.check_commit_graph(str(repo / ".git"))["status"] == "PASS"
    assert doctor.check_midx(str(repo / ".git"),
                             doctor.check_objects()["detail"]["packs"])["status"] == "PASS"


# ── fleet audit ───────────────────────────────────────────────────────────────
def test_fleet_grades_a_non_repository_as_not_a_repo(tmp_path):
    """A plain directory has no stack to modernise, so it must not be graded COLD.

    The fix for "not a repository" is a decision, not four config one-liners, and
    G:/azazael is exactly this case (measured 2026-11-01).
    """
    plain = tmp_path / "artefact-store"
    plain.mkdir()
    (plain / "file.txt").write_text("x", encoding="utf-8")
    entry = fleet.check_tree(str(plain))
    assert entry["grade"] == "NOT-A-REPO", entry
    assert entry["tasks"] and "git init" in entry["tasks"][0]


def test_fleet_does_not_grade_a_folder_inside_another_repo(tmp_path):
    """git resolves upward, so a subfolder must not inherit its parent's grade.

    Measured 2026-11-01: `C:/Users/clint/edge0-intel` and `C:/Users/clint/graph3d`
    were graded as healthy repositories because `C:/Users/clint` is itself a git
    repository -- and the "fix" applied to those folders edited the home repo's
    config instead. This test builds that exact shape.
    """
    outer = init_repo(tmp_path / "outer")
    commit(outer, "a.txt", "a\n", "one")
    git(outer, "config", "core.fsmonitor", "true")
    inner = outer / "inner"
    inner.mkdir()
    (inner / "b.txt").write_text("b", encoding="utf-8")

    entry = fleet.check_tree(str(inner))
    assert entry["grade"] == "NOT-A-REPO", entry
    assert "sits inside" in entry["gaps"][0]
    assert str(outer).split("\\")[-1] in entry["tasks"][0]


def test_fleet_grades_missing_path(tmp_path):
    entry = fleet.check_tree(str(tmp_path / "does-not-exist"))
    assert entry["grade"] == "MISSING", entry


def test_fleet_cold_then_bleeding_after_apply(tmp_path):
    repo = init_repo(tmp_path / "cold")
    commit(repo, "a.txt", "a\n", "one")
    before = fleet.check_tree(str(repo))
    assert before["grade"] == "COLD", before
    assert len(before["gaps"]) >= 3, before
    assert any("commit-graph" in t for t in before["tasks"])

    assert fleet.main(["--root", str(repo), "--apply"]) in (0, 1)
    after = fleet.check_tree(str(repo))
    assert after["grade"] == "BLEEDING", after
    assert after["gaps"] == []


def test_fleet_refuses_to_call_an_untracked_copy_bleeding(tmp_path):
    """Config alone must not earn BLEEDING: the tree has to be tracked.

    Measured 2026-11-01: Ubuntu-26.04's /root/azazael satisfied every config check
    with 678 tracked files, and only the coverage check could tell that apart from a
    real stack. This is the positive case for that check.
    """
    repo = init_repo(tmp_path / "copy")
    commit(repo, "a.txt", "a\n", "baseline")
    for i in range(150):
        (repo / ("extra_%03d.txt" % i)).write_text("x", encoding="utf-8")
    fleet.main(["--root", str(repo), "--apply"])  # configures it; cannot track it

    entry = fleet.check_tree(str(repo))
    assert any("tracked vs" in g for g in entry["gaps"]), entry
    assert entry["grade"] != "BLEEDING", entry
    assert any(t.startswith("decide per tree") for t in entry["tasks"]), entry


def test_fleet_tracked_tree_with_the_same_config_is_bleeding(tmp_path):
    """Negative control: the coverage check must NOT fire on a fully tracked tree.

    Without this, the new check could pass the positive case by failing everything.
    """
    repo = init_repo(tmp_path / "tracked")
    commit(repo, "a.txt", "a\n", "baseline")
    for i in range(150):
        (repo / ("extra_%03d.txt" % i)).write_text("x", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "track everything")
    fleet.main(["--root", str(repo), "--apply"])

    entry = fleet.check_tree(str(repo))
    assert entry["grade"] == "BLEEDING", entry
    assert not any("tracked vs" in g for g in entry["gaps"]), entry


def test_doctor_dry_run_does_not_write(tmp_path):
    repo = init_repo(tmp_path / "dry")
    commit(repo, "a.txt", "a\n", "one")
    commit(repo, "b.txt", "b\n", "two")
    doctor.main(["--repo", str(repo), "--fix"])
    assert not (repo / ".git" / "objects" / "info" / "commit-graph").exists()
