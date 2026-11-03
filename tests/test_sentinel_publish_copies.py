"""The three canonical sentinel.py copies stay byte-identical to the LIVE file.

Provenance, measured 2026-11-03 by sha256 across C:/Azazael:

  canonical (all 237144d722b16e3b...):
    azazael/Project_FLAMING_SWORD/tools/sentinel.py      (the live, edited tree)
    publish/flaming-sword/tools/sentinel.py
    publish_proof/staged_flaming_sword/tools/sentinel.py

  NOT canonical, deliberately ungated:
    publish_clean/*  (e1bbf899... -- a different generation; its drift is named
    here so nobody mistakes the silence below for agreement)
    azazael/Project_CRADLE/tools/sentinel.py  (a different sentinel, different file)

The property patterned here is the one the render-handoff rules already bought:
"a copy you cannot read back did not land". The proof: if a sentinel edit
commits without re-running `tools/stage_publish_repos.py`, the publish and
proof copies silently AGE -- and every guided run inside publish/, which reads
the chain FROM the publish copy, then verifies a tool that no longer exists
byte-for-byte elsewhere. This test fires at exactly that point, and the fix it
names is the same one command -- re-stage the repos.

Copy paths outside the repo root are SKIPPED when absent (a fresh clone or a
different checkout shape), so this gate never blocks a host that never had the
copies; on this host, where they exist, it holds.
"""
from __future__ import annotations

import hashlib
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
AZAZAEL_ROOT = REPO.parent

LIVE = REPO / "Project_FLAMING_SWORD" / "tools" / "sentinel.py"
CANONICAL_COPIES = (
    AZAZAEL_ROOT / "publish" / "flaming-sword" / "tools" / "sentinel.py",
    AZAZAEL_ROOT / "publish_proof" / "staged_flaming_sword" / "tools" / "sentinel.py",
)


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_canonical_copies_are_byte_identical_to_the_live_file():
    assert LIVE.exists(), "the live sentinel is this repo's own tool -- never skip it"
    live_hash = _sha256(LIVE)
    for copy in CANONICAL_COPIES:
        if not copy.exists():
            pytest.skip("canonical copy absent on this host: %s" % copy)
        assert _sha256(copy) == live_hash, (
            "%s drifted from the live sentinel -- re-run "
            "tools/stage_publish_repos.py in the same change" % copy)
