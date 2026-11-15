# coding: utf-8
"""The workflow-yaml gate leg must catch silence, not just bad YAML.

Three defects of this shape were found on 2026-11-15 and none of them raised
anything: an unknown Dependabot key, a `branches: [main]` filter that never
matched the working branch, and a `sed` indentation flatten that moved `steps`
out of its job. The first two are silent by construction and the third still
parses, so reading the files proves nothing -- only the leg's own verdict does.

Each fixture is run in its own tree because the leg aggregates every problem it
finds into one detail string: a shared directory would let one fixture's failure
appear in another's, which is how a regression test starts certifying nothing.
"""

import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import mcp_startup_gate as gate  # noqa: E402 - after sys.path
from mcp_startup_gate import FAIL, PASS, check_workflow_yaml  # noqa: E402

#: Verbatim shape of the real `.github/dependabot.yml` defect: the key sits
#: inside an `updates:` entry where GitHub rejects it. There it disabled every
#: update block in the file without printing anything.
DEPENDABOT_UNKNOWN_KEY = """\
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    vulnerability-alerts: true
"""

#: The sed flatten: `build:` keeps no body, so `steps` is promoted to be a
#: sibling job key. This document LOADS cleanly and contains no runnable job.
WORKFLOW_FLATTENED = """\
name: build
on: push
jobs:
  build:
  steps:
    - run: echo hi
"""

WORKFLOW_UNPARSEABLE = """\
name: broken
on: push
jobs:
  build:
    steps: [unclosed
"""

#: A valid workflow, written with a BARE `on:`. PyYAML reads that as boolean
#: True, which is the trap the leg's trigger check exists for.
WORKFLOW_VALID = """\
name: ci
on:
  push:
    branches: [master]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo hi
"""

#: A reusable-workflow caller has no `runs-on` at all; it must not be reported.
WORKFLOW_REUSABLE = """\
name: call
on: push
jobs:
  call:
    uses: owner/repo/.github/workflows/reusable.yml@main
"""


def run_leg(tmp_path, filename, text):
    """One fixture, one tree. Returns (status, detail)."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / filename).write_text(text, encoding="utf-8")
    original = gate._REPO_ROOT
    gate._REPO_ROOT = str(tmp_path)
    try:
        status, detail, _remedy = check_workflow_yaml(False)
    finally:
        gate._REPO_ROOT = original
    return status, detail


def test_unknown_dependabot_key_fails(tmp_path):
    status, detail = run_leg(tmp_path, "dependabot.yml", DEPENDABOT_UNKNOWN_KEY)
    assert status == FAIL
    assert "updates[0] has unknown key(s) vulnerability-alerts" in detail


def test_flattened_job_fails(tmp_path):
    status, detail = run_leg(tmp_path, "build.yml", WORKFLOW_FLATTENED)
    assert status == FAIL
    assert "job 'build' is not a mapping" in detail


def test_unparseable_file_fails(tmp_path):
    status, detail = run_leg(tmp_path, "broken.yml", WORKFLOW_UNPARSEABLE)
    assert status == FAIL
    assert "broken.yml" in detail


def test_bare_on_key_is_not_a_missing_trigger(tmp_path):
    """The control: a valid file must PASS, or every other case is meaningless."""
    status, detail = run_leg(tmp_path, "ci.yml", WORKFLOW_VALID)
    assert status == PASS, detail


def test_reusable_workflow_job_passes(tmp_path):
    status, detail = run_leg(tmp_path, "call.yml", WORKFLOW_REUSABLE)
    assert status == PASS, detail


def test_missing_jobs_fails(tmp_path):
    status, detail = run_leg(tmp_path, "noj.yml", "name: x\non: push\n")
    assert status == FAIL
    assert "no jobs" in detail


def test_leg_reports_this_repository_as_pass():
    """The real tree must be green: fixtures prove the rule, this proves the repo."""
    status, detail, _remedy = check_workflow_yaml(False)
    assert status == PASS, detail
