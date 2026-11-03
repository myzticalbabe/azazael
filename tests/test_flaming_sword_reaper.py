"""Main-suite controls for the REAPER (`Project_FLAMING_SWORD/tools/sentinel.py`).

The reaper already carries its own selftest with a positive control (a correct action
must stay allowed) and ten mutations (each known-bad frame must be BLOCKED for the
named S-check) -- satisfying the negative-control rule. These tests make that control
run reachable from the main suite by loading the LIVE production file by path, and add
only what the selftest cannot express:

* the CLI exit contract is exactly {ok: 0, blocked: 1, cannot-run >= 2} and exit 1 is
  never reported as an OK verdict (a reaper that praises what it reaped is worse than
  none);
* the S-checks fire on a bad root, not a good one -- the reaper must be able to be
  pointed at any tree, not just its own.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TOOL = REPO / "Project_FLAMING_SWORD" / "tools" / "sentinel.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("flaming_sword_reaper", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def reaper():
    return load_tool()


# --------------------------------------------------------------------------- #
# The reaper's own controls, run against the live production file
# --------------------------------------------------------------------------- #

def test_selftest_passes_on_the_live_file(reaper):
    failures, lines = reaper.selftest()
    assert failures == 0, "\n".join(lines)


def test_healthy_action_is_allowed(reaper):
    verdict = reaper.check(
        intent="refuse a shard whose golden run does not reproduce",
        target="tools/sword.py",
        must_not_break=["tests/test_defender.py"],
        defends=["the golden run's state_sha256 token"],
        refusal="BLOCK when the acceptance command exits non-zero",
        root=TOOL.parent.parent,
    )
    assert verdict["verdict"] == "SENTINEL OK"
    assert not verdict["problems"]


def test_checks_resolve_against_a_stated_root(reaper, tmp_path: pathlib.Path):
    # A healthy frame relative to an empty tree MUST block: everything it names is
    # a ghost there. Answers "can the reaper be pointed at any tree" and is the
    # positive control for `root=` not silently defaulting to here.
    (tmp_path / "tools").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "tools" / "sword.py").write_bytes(b"# kept\n")
    verdict = reaper.check(
        intent="add an S8 check to the extras",
        target="new:tools/extras.py",
        must_not_break=["tests/test_extras.py"],
        defends=["the S8 note in CHANGELOG.md"],
        refusal="BLOCK when S8 answers a topic instead of an act",
        root=tmp_path,
    )
    # target is honestly `new:` (no file), but the break list names a ghost.
    assert any(p.startswith("S3 break-resolves") for p in verdict["problems"])
    (tmp_path / "tests" / "test_extras.py").write_bytes(b"def test_s8(): pass\n")
    ok = reaper.check(
        intent="add an S8 check to the extras",
        target="new:tools/extras.py",
        must_not_break=["tests/test_extras.py"],
        defends=["the S8 note in CHANGELOG.md"],
        refusal="BLOCK when S8 answers a topic instead of an act",
        root=tmp_path,
    )
    assert ok["verdict"] == "SENTINEL OK"


def test_topic_intent_and_ghost_target_are_both_reaped(reaper):
    bad = reaper.check(
        intent="the validation situation",
        target="tools/ghost.py",
        must_not_break=["tests/test_ghost.py"],
        defends=[],
        refusal="",
        root=TOOL.parent.parent,
    )
    prefixes = [p.split(":", 1)[0] for p in bad["problems"]]
    for expected in ("S1 intent-scoped", "S2 target-resolves", "S3 break-resolves",
                     "S4 defence-named", "S5 landing-stated"):
        assert any(p == expected for p in prefixes), prefixes
    assert bad["verdict"] == "SENTINEL BLOCKED"


# --------------------------------------------------------------------------- #
# CLI exit contract
# --------------------------------------------------------------------------- #

def _ok_root(base: pathlib.Path) -> pathlib.Path:
    """A minimal tree the exit-0 frame can honestly resolve against."""
    root = base / "okroot"
    (root / "tools").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "tools" / "cmd_ok.py").write_bytes(b"\n")
    (root / "tests" / "keep.md").write_bytes(b"# kept\n")
    return root


def _run(argv: list[str], cwd: pathlib.Path):
    proc = subprocess.run([sys.executable, str(TOOL), *argv],
                          capture_output=True, text=True, cwd=str(cwd), timeout=60)
    return proc


def test_cli_exit_0_on_an_allowed_action(tmp_path: pathlib.Path):
    # Run with an isolated --root so the check cannot pass by accident: the fixture
    # tree is built as the frame claims it.
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "cmd_ok.py").write_bytes(b"\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "keep.md").write_bytes(b"# kept\n")
    proc = _run(["--intent", "verify the cli exit contract",
                 "--target", "tools/cmd_ok.py",
                 "--break", "tests/keep.md",
                 "--defends", "the exit contract in this module's docstring",
                 "--refusal", "BLOCK when the exit code disagrees with the verdict",
                 "--root", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SENTINEL OK" in proc.stdout, proc.stdout


def test_cli_exit_code_agrees_with_the_verdict(tmp_path: pathlib.Path):
    # The property the selftest cannot express: exit 0 IFF the verdict is OK. A
    # non-zero exit printed alongside 'SENTINEL OK' (or the reverse) is the one
    # way a reaper can lie to a shell pipeline.
    module = load_tool()
    bad_argv = ["--intent", "the situation with the exits",  # S1: topic, not act
                "--target", "tools/ghost.py",                # S2: ghost
                "--break", "prose about the tests",           # S3: no path
                "--refusal", "",                              # S5: nothing
                "--root", str(tmp_path)]
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        rc_blocked = module.main(bad_argv)
    out_blocked = buf.getvalue()
    assert rc_blocked == 1, out_blocked
    assert "SENTINEL BLOCKED" in out_blocked
    assert "SENTINEL OK" not in out_blocked, "exit 1 must never read as OK"
    good_argv = ["--intent", "verify the cli exit contract",
                 "--target", "tools/cmd_ok.py",
                 "--break", "tests/keep.md",
                 "--defends", "the exit contract in this module's docstring",
                 "--refusal", "BLOCK when the exit code disagrees with the verdict",
                 "--root", str(_ok_root(tmp_path))]
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        rc_ok = module.main(good_argv)
    assert rc_ok == 0, buf.getvalue()


def test_cli_blocked_frame_exits_1_with_the_deadly_claims(
        reaper, tmp_path: pathlib.Path):
    proc = _run(["--intent", "the situation with the exits",   # S1: topic, not act
                 "--target", "tools/ghost.py",                # S2: ghost
                 "--break", "prose about the tests",           # S3: no path
                 "--refusal", "",                              # S5: nothing
                 "--root", str(tmp_path), "--json"], cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["verdict"] == "SENTINEL BLOCKED"
    assert payload["problems"], "a BLOCKED verdict must name at least one claim"
    prefixes = [p.split(":", 1)[0] for p in payload["problems"]]
    assert "S1 intent-scoped" in prefixes and "S2 target-resolves" in prefixes


def test_cli_selftest_exit_0_and_its_json_reports_zero_failures(
        tmp_path: pathlib.Path):
    proc = _run(["--selftest", "--json"], cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    # The positive control must be present BEFORE the mutations: a healthy fixture
    # runs and stays allowed -- otherwise '0 failures' could mean 'ran nothing'.
    assert payload["failures"] == 0
    assert any(l.startswith("PASS healthy control") for l in payload["lines"]), payload["lines"][:2]
