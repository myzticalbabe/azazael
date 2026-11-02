"""Tests for sentinel.py, memory_bridge.py and the AIO path through defender.py.

Three properties, each with a failure behind it:

* a frame about files that do not exist must be BLOCKED, not praised (sentinel S2/S3);
* a memory backend that did not answer must be UNMEMORED, never "no lessons" (bridge);
* no AIO prompt may be rendered when either of the above fails, because a model handed
  a prompt built on a hole fills the hole with prose (to_aio).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
TOOLS = HERE / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def _load(filename: str, name: str):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


sentinel = _load("sentinel.py", "flaming_sword_sentinel")
bridge = _load("memory_bridge.py", "flaming_sword_memory_bridge")
defender = _load("defender.py", "flaming_sword_defender")


GOOD = dict(
    intent="refuse a shard whose golden run does not reproduce",
    target="tools/sword.py",
    must_not_break=["tests/test_defender.py"],
    defends=["the golden run's state_sha256 token"],
    refusal="BLOCK when the acceptance command exits non-zero",
    acceptance="pytest -q exits 0 and prints 76 passed",
    evidence="tests/test_defender.py",
)


# --------------------------------------------------------------------------- #
# Sentinel
# --------------------------------------------------------------------------- #

def test_a_resolvable_action_is_allowed():
    verdict = sentinel.check(**GOOD)
    assert verdict["verdict"] == "SENTINEL OK"
    assert "tools/sword.py" in verdict["resolved"]


def test_resolved_paths_are_not_listed_twice():
    verdict = sentinel.check(**{**GOOD, "must_not_break": ["tools/sword.py"]})
    assert verdict["resolved"].count("tools/sword.py") == 1


def test_a_topic_is_not_a_task():
    verdict = sentinel.check(**{**GOOD, "intent": "the shard validator situation"})
    assert any(p.startswith("S1 intent-scoped") for p in verdict["problems"])


def test_a_ghost_target_is_blocked():
    verdict = sentinel.check(**{**GOOD, "target": "tools/ghost.py"})
    assert any("does not exist" in p for p in verdict["problems"])


def test_declaring_new_on_a_present_file_is_blocked():
    verdict = sentinel.check(**{**GOOD, "target": "new:tools/sword.py"})
    assert any("already exists" in p for p in verdict["problems"])


def test_a_prose_break_list_is_blocked():
    verdict = sentinel.check(**{**GOOD, "must_not_break": ["don't break anything"]})
    assert any(p.startswith("S3 break-resolves") for p in verdict["problems"])


def test_a_placeholder_defence_is_blocked():
    verdict = sentinel.check(
        **{**GOOD, "defends": ["<name what survives: a test, a claim, a gate>"]})
    assert any("placeholder" in p for p in verdict["problems"])


def test_preservation_posture_is_delegated_not_reimplemented():
    verdict = sentinel.check(**{**GOOD, "preserve": True, "posture": {}})
    assert any(p.startswith("S7 posture-intact") for p in verdict["problems"])


def test_selftest_passes():
    failures, lines = sentinel.selftest()
    assert failures == 0, "\n".join(lines)


# --------------------------------------------------------------------------- #
# Memory bridge
# --------------------------------------------------------------------------- #

def test_no_backend_is_unmemored_with_a_reason():
    state = bridge.probe()
    assert state["state"] == bridge.UNMEMORED
    assert "no memory backend" in state["reason"]


def test_a_missing_ledger_is_unmemored_not_empty():
    state = bridge.probe(jsonl="does/not/exist.jsonl")
    assert state["state"] == bridge.UNMEMORED
    assert "does not exist" in state["reason"]


def test_recall_labels_its_backend(tmp_path: Path):
    ledger = tmp_path / "lessons.jsonl"
    ledger.write_text(json.dumps({"content": "a stale state_sha256 must be refused"}) + "\n",
                      encoding="utf-8")
    found = bridge.recall("stale state_sha256", jsonl=str(ledger))
    assert found["state"] == bridge.MEMORY
    assert found["matches"][0]["backend"] == "jsonl"


def test_a_malformed_ledger_line_is_an_error(tmp_path: Path):
    ledger = tmp_path / "bad.jsonl"
    ledger.write_text('{"content": "ok"}\n{oops}\n', encoding="utf-8")
    state = bridge.probe(jsonl=str(ledger))
    assert state["state"] == bridge.UNMEMORED
    assert "line 2" in state["reason"]


def test_frames_append(tmp_path: Path):
    wrote = bridge.record({"intent": "x", "shape": "defensive-v1"}, state_dir=str(tmp_path))
    bridge.record({"intent": "y", "shape": "defensive-v1"}, state_dir=str(tmp_path))
    path = Path(wrote["path"])
    assert len([line for line in path.read_text(encoding="utf-8").splitlines() if line]) == 2


def test_bridge_selftest_passes():
    failures, lines = bridge.selftest()
    assert failures == 0, "\n".join(lines)


# --------------------------------------------------------------------------- #
# AIO
# --------------------------------------------------------------------------- #

def aio_kwargs(**overrides):
    kwargs = dict(
        target="tools/sword.py",
        acceptance="pytest -q exits 0 and prints 76 passed",
        evidence="tests/test_defender.py",
        defends=["the golden run's state_sha256 token"],
        must_not_break=["tests/test_defender.py"],
        control="flip one byte in state_sha256 and require a REFUSAL",
    )
    kwargs.update(overrides)
    return kwargs


def test_a_complete_prompt_becomes_an_instruction_object():
    result = defender.to_aio("refuse a shard whose golden run does not reproduce",
                             **aio_kwargs())
    assert result["state"] == "READY-UNMEMORED"
    assert "AIO  defensive-aio-v1" in result["aio"]
    assert "USER PROMPT (verbatim, and it governs)" in result["aio"]


def test_unmemored_is_explained_rather_than_implied():
    result = defender.to_aio("refuse a shard whose golden run does not reproduce",
                             **aio_kwargs())
    assert "NOT an absence of lessons" in result["aio"]


def test_a_ghost_target_renders_no_prompt():
    result = defender.to_aio("refuse a shard whose golden run does not reproduce",
                             **aio_kwargs(target="tools/ghost.py"))
    assert result["state"] == "BLOCKED"
    assert result["aio"] == ""


def test_no_finish_line_renders_no_prompt():
    result = defender.to_aio("refuse a shard whose golden run does not reproduce",
                             **aio_kwargs(acceptance=""))
    assert result["state"] == "REFUSED"
    assert result["aio"] == ""


def test_recalled_lessons_reach_the_prompt():
    memory = {"state": "MEMORY", "backend": "jsonl",
              "matches": [{"backend": "jsonl", "score": 1,
                           "content": "a stale state_sha256 must be refused"}]}
    result = defender.to_aio("refuse a shard whose golden run does not reproduce",
                             memory=memory, **aio_kwargs())
    assert result["state"] == "READY"
    assert "stale state_sha256" in result["aio"]


def test_the_aio_carries_the_posture_for_preservation_work():
    result = defender.to_aio("convert the cartridge into a rules shard",
                             **aio_kwargs(preserve=True))
    assert result["state"] in ("READY", "READY-UNMEMORED")
    assert "POSTURE" in result["aio"]
    assert "bytes of the original: 0" in result["aio"]


def test_defender_selftest_passes():
    failures, lines = defender.selftest()
    assert failures == 0, "\n".join(lines)
