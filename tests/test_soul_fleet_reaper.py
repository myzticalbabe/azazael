"""Tests for tools/soul_fleet_reaper.py.

The one property that matters: merge-status decides, nothing else.
A merged branch is reaped; an unmerged branch survives --reap; the
default branch is never touched.
"""

import subprocess

from tools.soul_fleet_reaper import main, reap_repo

ID = ["-c", "user.email=t@t.t", "-c", "user.name=t",
      "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false"]


def gg(*a, cwd=None):
    p = subprocess.run(["git", *ID, *a], cwd=cwd, capture_output=True,
                       text=True, timeout=120)
    assert p.returncode == 0, (a, p.stderr)
    return (p.stdout or "") + (p.stderr or "")


def make_fleet(tmp_path):
    root = tmp_path / "fleet"
    root.mkdir()
    o = tmp_path / "o.git"
    gg("init", "--bare", str(o))
    d = root / "d"
    gg("clone", str(o), str(d))
    gg("checkout", "-b", "main", cwd=d)
    (d / "f.txt").write_text("x\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "init", cwd=d)
    gg("push", "-u", "origin", "main", cwd=d)
    # merged feature: real merge commit on main, pushed
    gg("checkout", "-b", "feature", cwd=d)
    (d / "g.txt").write_text("y\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "feat", cwd=d)
    gg("push", "-u", "origin", "feature", cwd=d)
    gg("checkout", "main", cwd=d)
    gg("merge", "--no-ff", "feature", "-m", "merge feat", cwd=d)
    gg("push", "origin", "main", cwd=d)
    # unmerged side work, pushed but never merged
    gg("checkout", "-b", "side", cwd=d)
    (d / "h.txt").write_text("z\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "side", cwd=d)
    gg("push", "-u", "origin", "side", cwd=d)
    gg("checkout", "main", cwd=d)
    return root, d, o


def test_dry_run_plans_merged_lists_unmerged(tmp_path):
    root, d, o = make_fleet(tmp_path)
    r = reap_repo(d, [], do_reap=False)
    assert r["skipped"] == ""
    assert r["merged"] == ["feature"]
    assert [u["branch"] for u in r["unmerged"]] == ["side"]
    assert "main" not in r["merged"]  # default never listed
    # dry-run deleted nothing remotely
    assert "feature" in gg("branch", "-a", cwd=d)


def test_reap_deletes_merged_keeps_unmerged(tmp_path):
    root, d, o = make_fleet(tmp_path)
    rc = main(["--root", str(root), "--repos", "d", "--reap"])
    assert rc == 1  # unmerged work remains for a human
    out = gg("ls-remote", "--heads", str(o))
    assert "feature" not in out  # reaped on the remote
    assert "side" in out  # kept
    assert "main" in out  # default untouched
    tags = gg("tag", "-l", cwd=d)
    assert "reap-snap-" in tags  # snapshot preceded deletion


def test_unmerged_never_reaped_even_old(tmp_path):
    root, d, o = make_fleet(tmp_path)
    r = reap_repo(d, [], do_reap=True)
    assert [u["branch"] for u in r["unmerged"]] == ["side"]
    assert "side" not in r["reaped"]
    info = r["unmerged"][0]
    assert info["unique_commits"] == "1" and info["author"] == "t"


def test_keep_pattern_protects_branch(tmp_path):
    root, d, o = make_fleet(tmp_path)
    r = reap_repo(d, [r"feat.*"], do_reap=False)
    assert r["merged"] == []  # feature kept by pattern, not by age


def test_bad_root_exit_2(tmp_path):
    assert main(["--root", str(tmp_path / "nope")]) == 2
