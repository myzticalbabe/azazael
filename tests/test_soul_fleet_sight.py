"""Sight detectors: each fires on its fixture, quiet on clean trees.

Every git invocation carries timeout=120 (repo testing mandate) and
-c identity flags (no global config assumed). Origins are local bare
repos -- no network, deterministic.
"""
import subprocess

import tools.soul_fleet_sight as sight

GIT_ENV_ID = ["-c", "user.email=t@t.t", "-c", "user.name=t",
              "-c", "init.defaultBranch=main",
              "-c", "commit.gpgsign=false"]


def gg(*args, cwd=None):
    return subprocess.run(["git", *GIT_ENV_ID, *args], cwd=cwd,
                          capture_output=True, text=True, timeout=120)


def make_repo(base, name, branch="main"):
    d = base / name
    d.mkdir()
    assert gg("init", "-b", branch, cwd=d).returncode == 0
    (d / "f.txt").write_text("x\n", encoding="utf-8")
    assert gg("add", ".", cwd=d).returncode == 0
    assert gg("commit", "-m", "init", cwd=d).returncode == 0
    return d


def make_origin(base, name="origin.git"):
    o = base / name
    assert gg("init", "--bare", str(o)).returncode == 0
    return o


def link(d, origin, push=True):
    assert gg("remote", "add", "origin", str(origin), cwd=d).returncode == 0
    if push:
        assert gg("push", "-u", "origin", "main", cwd=d).returncode == 0
        gg("remote", "set-head", "origin", "-a", cwd=d)


def test_clean_repo_no_findings(tmp_path):
    d = make_repo(tmp_path, "clean")
    link(d, make_origin(tmp_path))
    e = sight.sight_repo(d)
    assert e["findings"] == [], e
    assert e["origin_ok"] is True and e["upstream"] is True


def test_dirty_flagged(tmp_path):
    d = make_repo(tmp_path, "dirty")
    link(d, make_origin(tmp_path))
    (d / "f.txt").write_text("changed\n", encoding="utf-8")
    e = sight.sight_repo(d)
    assert any("DIRTY" in f for f in e["findings"]), e


def test_ahead_flagged(tmp_path):
    d = make_repo(tmp_path, "ahead")
    link(d, make_origin(tmp_path))
    (d / "g.txt").write_text("y\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "second", cwd=d)
    e = sight.sight_repo(d)
    assert any("AHEAD" in f for f in e["findings"]), e


def test_behind_flagged(tmp_path):
    o = make_origin(tmp_path)
    d = make_repo(tmp_path, "behind")
    link(d, o)
    # second clone moves the remote forward
    d2 = tmp_path / "behind2"
    assert gg("clone", str(o), str(d2)).returncode == 0
    (d2 / "h.txt").write_text("z\n", encoding="utf-8")
    gg("add", ".", cwd=d2)
    gg("commit", "-m", "remote-side", cwd=d2)
    gg("push", "origin", "main", cwd=d2)
    gg("fetch", "origin", cwd=d)
    e = sight.sight_repo(d)
    assert any("BEHIND" in f for f in e["findings"]), e


def test_no_upstream_flagged(tmp_path):
    d = make_repo(tmp_path, "lonely")
    gg("remote", "add", "origin", str(make_origin(tmp_path)), cwd=d)
    e = sight.sight_repo(d)
    assert any("NO-UPSTREAM" in f for f in e["findings"]), e


def test_no_origin_flagged(tmp_path):
    d = make_repo(tmp_path, "orphan")
    e = sight.sight_repo(d)
    assert any("NO-ORIGIN" in f for f in e["findings"]), e


def test_unreachable_origin_flagged(tmp_path):
    d = make_repo(tmp_path, "dead")
    gg("remote", "add", "origin", str(tmp_path / "nope.git"), cwd=d)
    e = sight.sight_repo(d)
    assert e["origin_ok"] is False
    assert any("UNREACHABLE-ORIGIN" in f for f in e["findings"]), e


def test_default_mismatch_flagged(tmp_path):
    o = make_origin(tmp_path)
    gg("symbolic-ref", "HEAD", "refs/heads/master", cwd=o)
    d = make_repo(tmp_path, "mismatch")
    gg("remote", "add", "origin", str(o), cwd=d)
    gg("push", "-u", "origin", "main", cwd=d)
    e = sight.sight_repo(d)
    assert e["origin_default"] == "master"
    assert any("DEFAULT-MISMATCH" in f for f in e["findings"]), e


def test_heads_counted_not_failed(tmp_path):
    o = make_origin(tmp_path)
    d = make_repo(tmp_path, "twohead")
    link(d, o)
    gg("branch", "feature", cwd=d)
    gg("push", "origin", "feature", cwd=d)
    e = sight.sight_repo(d)
    assert e["heads"] == 2
    assert e["findings"] == [], e


def test_exit_codes(tmp_path):
    assert sight.main(["--root", str(tmp_path)]) == 0
    d = make_repo(tmp_path, "bad")
    link(d, make_origin(tmp_path))
    (d / "f.txt").write_text("changed\n", encoding="utf-8")
    assert sight.main(["--root", str(tmp_path)]) == 1
    assert sight.main(["--root", str(tmp_path / "missing")]) == 2
