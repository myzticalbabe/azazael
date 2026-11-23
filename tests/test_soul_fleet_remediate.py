"""Tests for tools/soul_fleet_remediate.py.

Proves the three safety properties live, not asserted:
1. dry-run mutates nothing (no tags, dead refs stay),
2. --apply snapshots first, then prunes only what was already gone,
   and never touches worktree files,
3. young/unseen findings are not due.
"""

import json
import subprocess

from tools.soul_fleet_remediate import due_findings, main

ID = ["-c", "user.email=t@t.t", "-c", "user.name=t",
      "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false"]


def gg(*a, cwd=None):
    p = subprocess.run(["git", *ID, *a], cwd=cwd, capture_output=True,
                       text=True, timeout=120)
    assert p.returncode == 0, (a, p.stderr)
    return (p.stdout or "") + (p.stderr or "")


def make_pair(tmp_path):
    o = tmp_path / "o.git"
    gg("init", "--bare", str(o))
    d = tmp_path / "fleet" / "d"
    d.mkdir(parents=True)
    gg("init", "-b", "main", cwd=d)
    (d / "f.txt").write_text("x\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "init", cwd=d)
    gg("remote", "add", "origin", str(o), cwd=d)
    gg("push", "-u", "origin", "main", cwd=d)
    gg("checkout", "-b", "feature", cwd=d)
    (d / "g.txt").write_text("y\n", encoding="utf-8")
    gg("add", ".", cwd=d)
    gg("commit", "-m", "feat", cwd=d)
    gg("push", "-u", "origin", "feature", cwd=d)
    # feature dies ON the remote (directly in the bare repo, the way a
    # merged PR does) so the clone's tracking ref goes stale until pruned.
    # NOTE: `git push origin :feature` would delete the tracking ref too.
    gg("checkout", "main", cwd=d)
    subprocess.run(["git", "--git-dir", str(o), "branch", "-D",
                    "feature"], capture_output=True, timeout=120)
    assert "origin/feature" in gg("branch", "-r", cwd=d)
    return d


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def _report_state(tmp_path, finding, first_seen):
    rep = _write(tmp_path / "rep.json",
                 {"repos": [{"name": "d", "findings": [finding]}]})
    st = _write(tmp_path / "st.json", {"d": {finding: first_seen}})
    return rep, st


FINDING = "DIRTY: 1 uncommitted path(s)"


def test_dry_run_mutates_nothing(tmp_path):
    d = make_pair(tmp_path)
    rep, st = _report_state(tmp_path, FINDING, "2020-01-01")
    assert main(["--report", rep, "--state", st,
                 "--root", str(tmp_path / "fleet")]) == 1  # human-side left
    assert gg("tag", "-l", cwd=d).strip() == ""  # no snapshot
    assert "origin/feature" in gg("branch", "-r", cwd=d)  # ref untouched


def test_apply_snapshots_then_prunes_dead_ref_only(tmp_path):
    d = make_pair(tmp_path)
    rep, st = _report_state(tmp_path, FINDING, "2020-01-01")
    out = tmp_path / "res.json"
    assert main(["--report", rep, "--state", st,
                 "--root", str(tmp_path / "fleet"),
                 "--apply", "--json", str(out)]) == 1
    tags = gg("tag", "-l", cwd=d).strip().splitlines()
    assert any(t.startswith("auto-snap-") for t in tags)  # snapshot first
    assert "origin/feature" not in gg("branch", "-r", cwd=d)  # dead ref gone
    assert "origin/main" in gg("branch", "-r", cwd=d)  # live ref kept
    assert (d / "f.txt").read_text(encoding="utf-8") == "x\n"  # files intact
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["applied"] is True
    assert any("snapshot" in line for line in data["results"]["d"])


def test_young_finding_not_due_no_plan(tmp_path):
    d = make_pair(tmp_path)
    rep, st = _report_state(tmp_path, FINDING, "2999-01-01")
    assert main(["--report", rep, "--state", st,
                 "--root", str(tmp_path / "fleet"),
                 "--apply"]) == 0  # nothing due
    assert gg("tag", "-l", cwd=d).strip() == ""
    assert "origin/feature" in gg("branch", "-r", cwd=d)


def test_due_findings_age_gate_unit():
    report = {"repos": [{"name": "r", "findings": ["OLD", "NEW", "UNSEEN"]}]}
    state = {"r": {"OLD": "2020-01-01", "NEW": "2999-01-01"}}
    due, skipped = due_findings(report, state, 14, "2020-02-01")
    assert due == {"r": ["OLD"]}
    assert skipped == []


def test_malformed_date_recorded_not_dropped():
    report = {"repos": [{"name": "r", "findings": ["BAD"]}]}
    state = {"r": {"BAD": "not-a-date"}}
    due, skipped = due_findings(report, state, 14, "2020-02-01")
    assert due == {}
    assert len(skipped) == 1 and "BAD" in skipped[0]


def test_bad_inputs_exit_2(tmp_path):
    assert main(["--report", str(tmp_path / "no.json"),
                 "--state", str(tmp_path / "no.json"),
                 "--root", str(tmp_path)]) == 2
