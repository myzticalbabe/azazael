"""Tests for tools/defender.py -- the prompter that frames a change defensively.

Both directions matter here more than usual. The prompter's whole claim is that a
frame cannot be produced without naming what it defends, so the tests must show a
good frame ACCEPTED and put a rendered prompt in the executor's hands, not only that
bad frames are refused. The draft/landing distinction gets the same treatment: a
draft must render with its holes marked, and the strict checker must refuse that same
document -- otherwise "draft" is a label with no consequence.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
if str(HERE / "tools") not in sys.path:
    sys.path.insert(0, str(HERE / "tools"))


def _load(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name,
                                                  HERE / "tools" / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


defender = _load("defender.py", "flaming_sword_defender")


def good_frame(**overrides):
    kwargs = dict(
        intent="refuse a shard whose golden run does not reproduce",
        target="docs/METTHEW/shard.schema.json",
        evidence="python tools/metthew_validate.py --shard docs/METTHEW/reference-shards/highend_ladder",
        defends=["the golden run's state_sha256 token"],
        must_not_break=["tests/test_metthew_families.py"],
        acceptance="`python tools/metthew_validate.py --shard s` exits 0 and prints PASS for 3 fixtures",
        control="flip one byte in state_sha256 and require the gate to refuse it",
        preserve=False,
    )
    kwargs.update(overrides)
    return defender.frame(**kwargs)


# --------------------------------------------------------------------------- #
# The healthy direction
# --------------------------------------------------------------------------- #

def test_a_good_frame_is_accepted_and_renders():
    frame = good_frame()
    assert frame["problems"] == []
    assert "DEFENSIVE FRAME" in frame["prompt"]
    assert "DRAFT" not in frame["prompt"]


def test_the_prompt_puts_the_frame_before_the_task():
    prompt = good_frame()["prompt"]
    assert prompt.index("what survives") < prompt.index("TASK:")


def test_the_prompt_forbids_deleting_evidence_and_describing_acceptance():
    prompt = good_frame()["prompt"]
    assert "Do not delete a test, a claim or a gate" in prompt
    assert "Run the acceptance command and quote it" in prompt


def test_preservation_frame_carries_posture():
    frame = good_frame(preserve=True, posture=defender.default_posture())
    assert frame["problems"] == []
    assert "POSTURE" in frame["prompt"]
    assert "sony-v-connectix" in frame["prompt"]
    assert frame["posture"]["bytes_of_original"] == 0


# --------------------------------------------------------------------------- #
# Refusals
# --------------------------------------------------------------------------- #

def test_no_defence_is_refused():
    frame = good_frame(defends=[])
    assert any(p.startswith("D2 defends-something") for p in frame["problems"])
    assert frame["prompt"] == ""


def test_adjectival_acceptance_is_refused():
    frame = good_frame(acceptance="the validator looks right")
    assert any(p.startswith("D7 no-wishes") for p in frame["problems"])


def test_acceptance_without_command_is_refused():
    frame = good_frame(acceptance="twelve shards validate and seven pass")
    assert any("names no command" in p for p in frame["problems"])


def test_happy_path_control_is_refused():
    frame = good_frame(control="run it again with the real fixture")
    assert any(p.startswith("D5 control-refuses") for p in frame["problems"])


def test_vague_break_list_is_refused():
    frame = good_frame(must_not_break=["don't break anything important"])
    assert any(p.startswith("D3 break-list") for p in frame["problems"])


def test_deferred_evidence_is_refused():
    frame = good_frame(evidence="TBD")
    assert any(p.startswith("D6 evidence-lands") for p in frame["problems"])


def test_preservation_without_posture_is_refused():
    frame = good_frame(preserve=True)
    assert any(p.startswith("D9 posture-declared") for p in frame["problems"])


def test_posture_carrying_original_bytes_is_refused():
    posture = defender.default_posture()
    posture["bytes_of_original"] = 4096
    frame = good_frame(preserve=True, posture=posture)
    assert any("bytes_of_original is 4096" in p for p in frame["problems"])


def test_posture_citing_an_unregistered_authority_is_refused():
    posture = defender.default_posture()
    posture["authority"] = "everyone does it"
    frame = good_frame(preserve=True, posture=posture)
    assert any("not one of" in p for p in frame["problems"])


# --------------------------------------------------------------------------- #
# Draft vs frame
# --------------------------------------------------------------------------- #

def test_draft_marks_every_hole():
    skeleton = defender.draft("convert a cartridge", "<cartridge>", preserve=True)
    assert skeleton["prompt"].count("<<FILL:") >= len(skeleton["unfilled"])
    assert skeleton["prompt"].startswith("DRAFT -- NOT A FRAME")


def test_strict_checker_refuses_a_draft():
    skeleton = defender.draft("convert a cartridge", "<cartridge>")
    strict = {k: v for k, v in skeleton.items() if k not in ("prompt", "draft", "unfilled")}
    assert defender.problems_in(strict)


# --------------------------------------------------------------------------- #
# The tool's own controls
# --------------------------------------------------------------------------- #

def test_selftest_passes():
    failures, lines = defender.selftest()
    assert failures == 0, "\n".join(lines)


def test_the_cli_refuses_a_frame_missing_its_evidence():
    assert defender.main(["--intent", "delete the dead detector",
                          "--target", "tools/sword.py"]) == 1


def test_the_cli_emits_a_draft_without_evidence():
    assert defender.main(["--draft", "--intent", "delete the dead detector"]) == 0


def test_json_output_round_trips():
    frame = good_frame()
    assert json.loads(json.dumps(frame))["shape"] == "defensive-v1"
