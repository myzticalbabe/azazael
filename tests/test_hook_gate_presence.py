# coding: utf-8
"""Tests for `tools/hook_gate_presence.py` -- the absent-gate branch, made loud.

The hook guards eleven stanzas on ``[ -f .../gate.py ]`` and then prints a skip
line, so a **deleted** gate script passes the commit. These tests drive the
presence gate to the four states it must separate, and -- the layer that
matters -- prove that the two states in which the gate cannot run are exit 1
rather than a quiet zero.

The classification is tested against an injected tracked-set (so the states are
observable without a repo), and the real tree is tested once at the end, where
the assertion is a live reading rather than a fixture: if a committed gate
script disappears, that test fails.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import hook_gate_presence as hgp  # noqa: E402
import preflight_all as pf  # noqa: E402


def _tree(tmp_path: Path, name: str, *, on_disk: bool, tracked: bool) -> tuple[Path, set]:
    """A root holding ONE script, with **on-disk** and **in-HEAD** set apart.

    They are independent axes and conflating them is what a defect looks like:
    tracked-but-deleted is the regression, untracked-but-present is the WIP.
    """
    script = "tools/%s.py" % name
    (tmp_path / "tools").mkdir(parents=True, exist_ok=True)
    if on_disk:
        (tmp_path / script).write_text("# gate\n", encoding="utf-8")
    return tmp_path, ({script} if tracked else set())


def test_present_and_tracked_is_ok(tmp_path):
    root, tracked = _tree(tmp_path, "alpha", on_disk=True, tracked=True)
    rows = hgp.assess(root, [("alpha", "tools/alpha.py")], tracked)
    assert [row.state for row in rows] == [hgp.PRESENT]
    assert rows[0].ok and not rows[0].fails
    assert hgp.verdict(rows) == 0


def test_deleted_at_head_fails(tmp_path):
    """The defect: a committed gate is gone, so its hook stanza skips silently."""
    root, tracked = _tree(tmp_path, "alpha", on_disk=False, tracked=True)
    rows = hgp.assess(root, [("alpha", "tools/alpha.py")], tracked)
    assert rows[0].state == hgp.DELETED
    assert rows[0].fails
    assert hgp.verdict(rows) == 1


def test_never_committed_fails(tmp_path):
    """Same operational fact -- the gate cannot run -- different repair."""
    root = tmp_path
    (root / "tools").mkdir()
    rows = hgp.assess(root, [("alpha", "tools/alpha.py")], set())
    assert rows[0].state == hgp.NEVER
    assert hgp.verdict(rows) == 1


def test_present_but_untracked_warns_without_failing(tmp_path):
    root, _ = _tree(tmp_path, "alpha", on_disk=True, tracked=True)
    rows = hgp.assess(root, [("alpha", "tools/alpha.py")], set())
    assert rows[0].state == hgp.PRESENT_UNTRACKED
    assert not rows[0].fails
    assert hgp.verdict(rows) == 0
    assert hgp.summarise(rows)["warn"] == ["alpha"]


def test_one_absent_gate_fails_the_whole_set(tmp_path):
    """A single silent skip is the failure; 37 healthy rows must not dilute it."""
    root, _ = _tree(tmp_path, "alpha", on_disk=True, tracked=True)
    tracked = {"tools/alpha.py", "tools/beta.py"}  # beta tracked, absent on disk
    rows = hgp.assess(
        root,
        [("alpha", "tools/alpha.py"), ("beta", "tools/beta.py"),
         ("gamma", "tools/gamma.py")],
        tracked,
    )
    assert [row.state for row in rows] == [
        hgp.PRESENT, hgp.DELETED, hgp.NEVER]
    assert hgp.verdict(rows) == 1
    summary = hgp.summarise(rows)
    assert summary["rows"] == 3
    assert summary["states"][hgp.PRESENT] == 1
    assert summary["failing"] == ["beta", "gamma"]


def test_registry_covers_every_gate_and_names_each_script():
    """The proxy must not silently skip a gate the hook runs."""
    items = hgp.registry_items()
    scripts = {script for _, script in items}
    assert items[0] == ("hook-installed", hgp.HOOK)
    for gate in pf.GATES:
        assert str(gate.argv[0]) in scripts, gate.name
    # bible_check.py is shared by four gates; dedup is by script, not by name.
    assert len(items) == len({str(gate.argv[0]) for gate in pf.GATES}) + 1


def test_real_tree_has_every_registered_gate_present():
    """A live reading, not a fixture: deleting a committed gate breaks this."""
    rows = hgp.assess(ROOT, hgp.registry_items(), hgp.tracked_paths(ROOT))
    absent = [(row.name, row.script, row.state) for row in rows if row.fails]
    assert absent == []
    assert hgp.verdict(rows) == 0
    assert all(row.state != hgp.PRESENT_UNTRACKED for row in rows)


def test_root_that_owns_no_repository_is_blind_not_a_pass(tmp_path):
    """exit 2, because a verdict is worth what the tree it was read from is.

    Measured 2026-11-14: ``git -C <tmpdir> ls-tree HEAD`` SUCCEEDED by walking
    up into an enclosing repository, so this very case used to return rows
    judged against somebody else's HEAD.
    """
    with pytest.raises(hgp.Blindness):
        hgp.tracked_paths(tmp_path)
    assert hgp.main(["--root", str(tmp_path)]) == 2


def test_subdirectory_of_a_real_repo_is_blind_not_a_verdict(capsys):
    """The same trap one level in: that HEAD belongs to the parent."""
    with pytest.raises(hgp.Blindness) as excinfo:
        hgp.tracked_paths(ROOT / "tools")
    assert "not a repository root" in str(excinfo.value)
    assert hgp.main(["--root", str(ROOT / "tools")]) == 2
    assert "BLIND" in capsys.readouterr().err


def test_missing_root_is_blind_not_a_pass(tmp_path):
    absent = tmp_path / "no-such-tree"
    assert hgp.main(["--root", str(absent)]) == 2


def _seed_repo(tmp_path: Path) -> Path:
    """A real git repo whose committed scripts are the real registry's paths."""
    for _, script in hgp.registry_items():
        path = tmp_path / script
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# gate\n", encoding="utf-8")

    def run(*args: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path)] + list(args), check=True,
                       capture_output=True, timeout=120)

    run("init", "-q")
    run("add", "-A")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
    return tmp_path


def test_cli_fails_on_a_real_repo_with_one_deleted_gate(tmp_path, capsys):
    """End-to-end negative control: commit the gates, delete one, run the CLI."""
    root = _seed_repo(tmp_path)
    assert hgp.main(["--root", str(root)]) == 0, "seeded repo must start clean"
    capsys.readouterr()

    victim = "tools/canon_drift_check.py"
    (root / victim).unlink()
    code = hgp.main(["--root", str(root)])
    out = capsys.readouterr().out

    assert code == 1
    assert "FAIL canon-drift" in out, out
    assert victim in out
    assert "1 absent" in out, out


def test_cli_recovers_when_the_deleted_gate_is_restored(tmp_path, capsys):
    """A ratchet that cannot go back to green is a wall, not a gate."""
    root = _seed_repo(tmp_path)
    victim = root / "tools" / "canon_drift_check.py"
    body = victim.read_text(encoding="utf-8")
    victim.unlink()
    assert hgp.main(["--root", str(root)]) == 1
    victim.write_text(body, encoding="utf-8")
    capsys.readouterr()
    assert hgp.main(["--root", str(root)]) == 0
    assert "-> PASS" in capsys.readouterr().out


def test_json_output_is_machine_readable(capsys):
    code = hgp.main(["--root", str(ROOT), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "PASS"
    assert payload["summary"]["rows"] == len(payload["rows"])
    assert code == 0
