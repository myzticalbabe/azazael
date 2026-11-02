# coding: utf-8
"""tests for Project FLAMING SWORD's runner.

The point of these tests is the two directions, per detector: it must fire on a
seeded defect and it must stay silent on a healthy tree. A detector tested only on
healthy input is indistinguishable from one that returns nothing.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sword", PROJECT / "tools" / "sword.py")
sword = importlib.util.module_from_spec(_spec)
sys.modules["sword"] = sword
_spec.loader.exec_module(sword)


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


def _configure(root, **config):
    (root / sword.STATE_DIR / "config.json").write_text(json.dumps(config), encoding="utf-8")


def _md(root, name, body):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


# -- the whole instrument ----------------------------------------------------

def test_self_test_passes():
    assert sword.self_test() == 0


def test_scan_persists_what_it_prints_and_clears_a_stale_unrun_list(repo, capsys):
    """The documented state file, checked as a contract rather than assumed.

    A scan that only prints forces the next reader to re-run the sweep to learn
    what the last one already knew. The stale direction matters too: an unrun.txt
    left over from a blind detector reports that detector blind after it started
    seeing, which teaches the reader to skip the section.
    """
    _configure(repo, constants=["FLOOR"],
               claims={"ledger": "claims.json",
                       "command": [sys.executable, "-c", "pass"]})
    (repo / "claims.json").write_text("{}\n", encoding="utf-8")
    (repo / sword.STATE_DIR / "unrun.txt").write_text("duplicate-constant: UNRUN\n",
                                                       encoding="utf-8")
    _md(repo, "docs/install.md", "# Install\n\n```bash\npython tools/commgate.py\n```\n")

    assert sword.cmd_scan(repo, as_json=True) == 0
    persisted = sword.read_jsonl(repo / sword.STATE_DIR / "findings.jsonl")
    fresh, _unrun = sword.scan(repo)
    assert [row["id"] for row in persisted] == [row["id"] for row in fresh]
    assert persisted, "the seeded defect produced no persisted finding"
    assert not (repo / sword.STATE_DIR / "unrun.txt").exists()


def test_clean_repository_produces_no_findings(repo):
    # Every detector must actually RUN on the clean fixture: an unconfigured
    # detector reports UNRUN, and a clean tree that cannot run its instruments
    # proves nothing about a clean tree.
    _configure(repo, constants=["FLOOR"],
               claims={"ledger": "claims.json",
                       "command": [sys.executable, "-c", "pass"]},
               compliance={"required": ["license", "license-header", "security-policy", "contributing", "code-of-conduct", "readme", "changelog", "ci-config"],
                           "optional": ["dependabot", "codeql"]})
    (repo / "claims.json").write_text("{}\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "real.py").write_text("# Copyright (c) 2024\n# MIT License\n\nFLOOR = 0.89\n", encoding="utf-8")
    (repo / "LICENSE").write_text("MIT License\n\nCopyright (c) 2024\n", encoding="utf-8")
    (repo / "SECURITY.md").write_text("# Security Policy\n\nReport security issues to security@example.com\n", encoding="utf-8")
    (repo / "CONTRIBUTING.md").write_text("# Contributing Guidelines\n\nWelcome!\n", encoding="utf-8")
    (repo / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct\n\nBe respectful.\n", encoding="utf-8")
    (repo / "README.md").write_text("# Project\n\nDescription\n", encoding="utf-8")
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## Unreleased\n", encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "dependabot.yml").write_text("version: 2\nupdates:\n  - package-ecosystem: pip\n    directory: /\n    schedule:\n      interval: daily\n", encoding="utf-8")
    (repo / ".github" / "codeql").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "codeql" / "codeql-config.yml").write_text("# CodeQL configuration\n", encoding="utf-8")
    _md(repo, "docs/run.md", "# Run\n\n```bash\npython tools/real.py\n```\n")
    findings, unrun = sword.scan(repo)
    assert findings == []
    assert unrun == []


# -- phantom-reference ------------------------------------------------------

def test_phantom_fires_on_a_fenced_command_that_does_not_exist(repo):
    _configure(repo, constants=[])
    _md(repo, "docs/install.md", "# Install\n\n```bash\npython tools/commgate.py\n```\n")
    findings, _ran, _ = sword.detect_phantom_reference(repo)
    assert [f["detail"] for f in findings] == ["tools/commgate.py"]
    assert findings[0]["severity"] == "high"


def test_phantom_ignores_a_path_mentioned_in_prose(repo):
    """A path in prose may be an example. A path in a block is an instruction."""
    _configure(repo, constants=[])
    _md(repo, "docs/install.md", "# Install\n\nRun `tools/commgate.py` if you like.\n")
    findings, _ran, _ = sword.detect_phantom_reference(repo)
    assert findings == []


def test_phantom_resolves_from_the_document_directory_first(repo):
    """A skill's `bin/x.mjs` is relative to the skill, not the repo root."""
    _configure(repo, constants=[])
    (repo / ".agents" / "skill" / "bin").mkdir(parents=True)
    (repo / ".agents" / "skill" / "bin" / "tool.mjs").write_text("// x\n", encoding="utf-8")
    _md(repo, ".agents/skill/SKILL.md", "```bash\nnode bin/tool.mjs run\n```\n")
    findings, _ran, _ = sword.detect_phantom_reference(repo)
    assert findings == []


def test_phantom_ignores_placeholders(repo):
    _configure(repo, constants=[])
    _md(repo, "docs/template.md", "```bash\npython path/to/file.py\n```\n")
    findings, _ran, _ = sword.detect_phantom_reference(repo)
    assert findings == []


# -- duplicate-constant, and the honesty rule -------------------------------

def test_constant_detector_is_unrun_without_a_watchlist(repo):
    """UNRUN is not clean. This is the assertion the whole project rests on."""
    _configure(repo, constants=[])
    (repo / "a.py").write_text("FLOOR = 0.89\n", encoding="utf-8")
    (repo / "b.py").write_text("FLOOR = 0.70\n", encoding="utf-8")
    findings, unrun = sword.scan(repo)
    assert not any(f["detector"] == "duplicate-constant" for f in findings)
    assert any("duplicate-constant: UNRUN" in note for note in unrun)


def test_constant_detector_fires_when_the_watchlist_names_a_split_constant(repo):
    _configure(repo, constants=["FLOOR"])
    (repo / "a.py").write_text("FLOOR = 0.89\n", encoding="utf-8")
    (repo / "b.py").write_text("FLOOR = 0.70\n", encoding="utf-8")
    findings, _ran, _ = sword.detect_duplicate_constant(repo)
    assert len(findings) == 1
    assert "2 different values" in findings[0]["remedy"]


def test_constant_detector_sees_an_env_default_copied_into_two_files(repo):
    """The canonical form of a tunable here is an env default, not `NAME = 0.89`.

    Measured on the home tree before this test existed: the detector understood
    only the bare assignment, so every floor, port and budget in the estate was
    invisible to the one detector written for them. The pair below is the exact
    near-miss that cost a session -- the same env name defaulted to 0.70 in one
    tool and 0.62 in another, both correct-looking.
    """
    _configure(repo, constants=["PMB_RECALL_FLOOR"])
    (repo / "a.py").write_text(
        'import os\nFLOOR = float(os.environ.get("PMB_RECALL_FLOOR", "0.70"))\n',
        encoding="utf-8")
    (repo / "b.py").write_text(
        'import os\nROW_FLOOR = float(os.environ.get("PMB_RECALL_FLOOR", "0.62"))\n',
        encoding="utf-8")
    findings, _ran, _ = sword.detect_duplicate_constant(repo)
    assert len(findings) == 1, findings
    assert findings[0]["detail"] == "PMB_RECALL_FLOOR"
    assert "0.70" in findings[0]["remedy"] and "0.62" in findings[0]["remedy"]


def test_constant_detector_is_silent_when_the_env_defaults_agree(repo):
    """The negative control for the test above, and for `0.7` vs `0.70`."""
    _configure(repo, constants=["PMB_RECALL_FLOOR"])
    (repo / "a.py").write_text(
        'import os\nFLOOR = float(os.environ.get("PMB_RECALL_FLOOR", "0.70"))\n',
        encoding="utf-8")
    (repo / "b.py").write_text(
        'import os\nROW_FLOOR = float(os.environ.get("PMB_RECALL_FLOOR", "0.7"))\n',
        encoding="utf-8")
    findings, _ran, _ = sword.detect_duplicate_constant(repo)
    assert findings == [], findings


def test_constant_detector_ignores_names_outside_the_watchlist(repo):
    """`BLACK = 30` in one module and `BLACK = 0` in another are two settings."""
    _configure(repo, constants=["FLOOR"])
    (repo / "a.py").write_text("BLACK = 0\nFLOOR = 0.89\n", encoding="utf-8")
    (repo / "b.py").write_text("BLACK = 30\nFLOOR = 0.89\n", encoding="utf-8")
    findings, _ran, _ = sword.detect_duplicate_constant(repo)
    assert findings == []


def test_stale_claims_is_unrun_rather_than_clean_without_a_command(repo):
    """Found 2026-11-01: with no `claims.command` the detector returned
    `ran=True, 0 findings`, so a guard that never ran read as clean."""
    _configure(repo, constants=["FLOOR"])
    findings, ran, note = sword.detect_stale_claims(repo)
    assert findings == []
    assert ran is False
    assert "nothing was run" in note


# -- hooks and interpreters -------------------------------------------------

def test_hooks_unwired_fires_and_its_fix_wires_it(repo):
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    findings, ran, _ = sword.detect_hooks_unwired(repo)
    assert ran and len(findings) == 1 and findings[0]["auto"]

    ok, note, touched = sword.apply_fix(repo, findings[0])
    assert ok, note
    assert touched is None, "a git-config fix touches no file, so it cannot be landed"
    after, _, _ = sword.detect_hooks_unwired(repo)
    assert after == []


def test_two_interpreters_proposes_rather_than_guesses_between_candidates(repo):
    """A page naming three interpreters does not say which the bare one meant.

    Measured on the home tree: the "most frequent literal wins" rule would have
    rewritten a production `python -m pytest` to run under a ComfyUI venv.
    """
    _configure(repo, constants=[])
    _md(repo, "docs/run.md",
        "```bash\nC:/venvs/comfy/Scripts/python.exe -m pytest\n```\n"
        "```bash\nC:/Azazael/.venvs/py315t/Scripts/python.exe -m pytest\n```\n"
        "```bash\npython -m pytest tests/ -q\n```\n")
    findings, _, _ = sword.detect_two_interpreters(repo)
    assert len(findings) == 1
    assert findings[0]["auto"] is False
    assert findings[0]["detail"] == "ambiguous"
    assert "2 interpreters" in findings[0]["remedy"]


def test_an_interpreter_that_cannot_import_pytest_is_never_the_fix(repo):
    """Measured on the home tree: `.pmb-venv` python answers "No module named pytest".

    Rewriting a documented test command to an interpreter that cannot run it is
    worse than leaving the bare `python`: it converts an ambiguous line into a
    confidently wrong one.
    """
    _configure(repo, constants=[])
    _md(repo, "docs/run.md",
        "```bash\nC:/definitely/not/here/python.exe -m pytest tests/\n```\n"
        "```bash\npython -m pytest tests/ -q\n```\n")
    findings, _, _ = sword.detect_two_interpreters(repo)
    assert len(findings) == 1
    assert findings[0]["auto"] is False
    assert findings[0]["detail"] == "interpreter-lacks-pytest"


def test_two_interpreters_fires_and_the_fix_uses_the_declared_literal(repo):
    _configure(repo, constants=[])
    # `sys.executable` is real and has pytest, which the detector now probes for:
    # a literal path that does not exist is correctly refused rather than offered.
    path = _md(repo, "docs/run.md",
               "```bash\npython -m pytest tests/ -q\n```\n\n"
               "```bash\n%s -m pytest tests/ -q\n```\n" % sys.executable)
    findings, _, _ = sword.detect_two_interpreters(repo)
    assert len(findings) == 1 and findings[0]["auto"]
    assert findings[0]["detail"].endswith("python.exe")

    ok, _note, touched = sword.apply_fix(repo, findings[0])
    assert ok and touched == "docs/run.md"
    text = path.read_text(encoding="utf-8")
    assert "python -m pytest" not in text.replace("python.exe -m pytest", "")
    after, _, _ = sword.detect_two_interpreters(repo)
    assert after == []


def test_untested_ci_ignores_a_workflow_that_never_checks_out(repo):
    """A labeler cannot run tests, so it is not a CI-without-tests defect."""
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "label.yml").write_text(
        "name: label\non: [pull_request]\njobs:\n  l:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: echo label\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    findings, ran, _ = sword.detect_untested_ci(repo)
    assert ran and findings == []


def test_untested_ci_accepts_a_workflow_that_runs_a_real_gate(repo):
    """Measured on the home tree: both "untested" workflows run real ratchets.

    The predicate is "this CI runs nothing", not "this CI does not spell pytest".
    A gate step is only accepted when the script it names actually exists, so a
    workflow that runs a deleted script is still reported.
    """
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "gate.yml").write_text(
        "name: gate\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v4\n"
        "      - run: python tools/gate.py --check\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "gate.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    findings, ran, _ = sword.detect_untested_ci(repo)
    assert ran and findings == [], findings


def test_untested_ci_still_fires_when_the_gate_script_does_not_exist(repo):
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "gate.yml").write_text(
        "name: gate\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v4\n"
        "      - run: python tools/deleted_gate.py --check\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    findings, _, _ = sword.detect_untested_ci(repo)
    assert len(findings) == 1, findings


def test_untested_ci_fires_when_a_checkout_workflow_runs_no_tests(repo):
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "name: ci\non: [push]\njobs:\n  b:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: actions/checkout@v4\n      - run: echo hi\n",
        encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("def test_x():\n    pass\n", encoding="utf-8")
    findings, _, _ = sword.detect_untested_ci(repo)
    assert len(findings) == 1


# -- research ---------------------------------------------------------------

def _research_line(**over):
    record = {
        "theme": "replacement for the copied floor",
        "query": "single source of truth for configuration constants",
        "url": "https://example.invalid/doc",
        "tier": "A",
        "finding": "a generated file beats a second copy",
        "adaptation": "generate the constant table from the corpus",
        "removes": "tools/pmb_floor_proxy.py",
        "verify_command": "python -m pytest tests/ -q",
    }
    record.update(over)
    return json.dumps(record)


def test_research_record_is_queued_as_a_proposal_never_auto(repo):
    _configure(repo, constants=[])
    source = repo / "research.jsonl"
    source.write_text(_research_line() + "\n", encoding="utf-8")
    assert sword.record_research(repo, source) == 0
    queue = sword.read_jsonl(repo / sword.STATE_DIR / "queue.jsonl")
    assert len(queue) == 1
    assert queue[0]["status"] == "proposed"
    assert queue[0]["auto"] is False


def test_research_record_without_a_verification_command_is_refused(repo):
    _configure(repo, constants=[])
    source = repo / "research.jsonl"
    source.write_text(_research_line(verify_command="") + "\n", encoding="utf-8")
    assert sword.record_research(repo, source) == 1


def test_research_record_with_an_invented_tier_is_refused(repo):
    _configure(repo, constants=[])
    source = repo / "research.jsonl"
    source.write_text(_research_line(tier="Z") + "\n", encoding="utf-8")
    assert sword.record_research(repo, source) == 1


# -- the spec the brief prints ---------------------------------------------

def test_brief_prints_thirteen_followups_and_both_decision_blocks(capsys):
    assert sword.brief() == 0
    out = capsys.readouterr().out
    assert "exactly 14" in out
    # The baker's dozen has two fixed cards. A brief that prints the count but
    # not the cards leaves the abyss slot to the agent's memory -- which is how
    # the slot gets dropped while the count still reads correct.
    assert "Build, land, in the abyss" in out
    assert "Hyper-edge adaptive upgrade" in out
    assert "Zero-shot reasoning" in out
    assert "before-write" in out
    assert "before-land" in out
    assert "rollback" in out


def test_the_spec_declares_every_detector_the_runner_implements():
    spec = json.loads(sword.SPEC.read_text(encoding="utf-8"))
    declared = {detector["id"] for detector in spec["detectors"]}
    implemented = {name for name, _fn in sword.DETECTORS}
    assert implemented - declared == set(), "implemented but undeclared: %s" % (implemented - declared)
    assert declared - implemented == set(), "declared but unimplemented: %s" % (declared - implemented)
