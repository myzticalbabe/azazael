"""tests/test_rule_0b_a_edict.py — the RULE 0B-A hook must actually FAIL.

A gate that has never been seen to reject anything is not a gate; it is
decoration with a green light. These tests exist to prove the sentinel's
0B-A validator rejects the exact three failure modes from 2026-09-30 and
accepts honest output. If someone later loosens the patterns, this fails.

Run:  python -m pytest tests/test_rule_0b_a_edict.py -q
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "src" / "SCRIPTS" / "sentinel_gate.py"


def _load():
    if not GATE.exists():  # pragma: no cover
        raise FileNotFoundError(GATE)
    spec = importlib.util.spec_from_file_location("sentinel_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sentinel_gate"] = mod
    spec.loader.exec_module(mod)
    return mod


sg = _load()
validate = sg.validate_rule_0b_a


CLEAN = """
1. Did I deliver the deliverable the user NAMED? yes, the likeness render.
2. Is my justification for a different answer longer than the delivery? no.
3. Am I claiming ACCEPTANCE? no. Describing only.
4. Did I add a rule the user did not invoke? no.
5. If I disagreed, did I say so in ONE sentence and still build the ask? yes.
"""


def test_clean_block_passes():
    ok, msg = validate(CLEAN)
    assert ok, msg


def test_acceptance_language_fails():
    """Violation 2: self-assessment substituted for acceptance."""
    for phrase in ("this passes", "this clears the rule",
                   "this is good enough", "this is done",
                   "that meets the bar", "i consider this complete"):
        ok, msg = validate(CLEAN + "\nVerdict: %s\n" % phrase)
        assert not ok, "acceptance language not caught: %r" % phrase
        assert "ACCEPTANCE" in msg.upper()


def test_missing_five_item_block_fails():
    """A skipped check must not read as a pass."""
    ok, msg = validate("")
    assert not ok
    assert "five-item" in msg


def test_partial_five_item_block_fails():
    ok, msg = validate("1. named deliverable yes. 2. no. 3. no.")
    assert not ok
    assert "incomplete" in msg


def test_self_reported_fail_is_honoured():
    """If the assistant's own check says FAIL, the gate says FAIL."""
    ok, msg = validate(CLEAN + "\n5. FAIL - I built a different artefact.\n")
    assert not ok
    assert "NOT" in msg


def test_not_delivery_turn_is_na():
    ok, msg = validate("N/A - read-only probe, nothing delivered")
    assert ok, msg


def test_validator_never_raises_on_junk():
    """A validator that crashes is a validator that gets disabled."""
    for junk in (None, 0, [], {}, 3.14, b"\xff\xfe", "x" * 20000):
        ok, msg = validate(junk)
        assert isinstance(ok, bool)
        assert isinstance(msg, str)


def test_real_gate_format_single_line_passes():
    """The format actually used: all five items on ONE line after the label.

    An earlier per-line regex anchored at line start, so it found only item 1
    and failed every honest block in real gate output. This locks that in.
    """
    block = (
        "** 1. Did I deliver the deliverable the user NAMED? yes. "
        "2. Is my justification for a different answer longer than the "
        "delivery? no. 3. Am I claiming ACCEPTANCE? no. 4. Did I add a rule "
        "the user did not invoke? no. 5. If I disagreed, did I say so in ONE "
        "sentence and still build the ask? yes."
    )
    ok, msg = validate(block)
    assert ok, msg


def test_end_to_end_through_the_real_gate():
    """parse_stdin -> SentinelValidator, so the wiring cannot silently rot."""
    gate = (
        "[PRE-ACTION GATE ASSERTION]\n"
        "- **AP-1 (Scope Check):** user asked for this exact render\n"
        "- **RULE 0B-A (Sole Source of Truth):** 1. Did I deliver the "
        "deliverable the user NAMED? yes. 2. Is my justification for a "
        "different answer longer than the delivery? no. 3. Am I claiming "
        "ACCEPTANCE? no. 4. Did I add a rule the user did not invoke? no. "
        "5. If I disagreed, did I say so in ONE sentence and still build the "
        "ask? yes.\n"
        "- **GATE DECISION:** PROCEED"
    )
    data = sg.parse_stdin(gate)
    assert data.get("rule_0b_a_edict"), "0B-A not parsed out of a real gate block"
    v = sg.SentinelValidator(mode="validate", silent=True)
    v.execute_validation(data)
    row = [r for r in v.results if "0B-A" in r["key"]]
    assert row, "0B-A result missing from the validator chain"
    assert row[0]["passed"], row[0]["message"]

    # ...and the same gate with a verdict appended must FAIL. The verdict is
    # parked in GATE DECISION, which is the realistic place to put it, and it
    # is outside the captured 0B-A field -- so this also proves the whole-block
    # acceptance scan works. Before that scan existed, the verdict escaped.
    data2 = sg.parse_stdin(gate.replace("PROCEED", "PROCEED. This passes."))
    v2 = sg.SentinelValidator(mode="validate", silent=True)
    v2.execute_validation(data2)
    row2 = [r for r in v2.results if "0B-A" in r["key"]]
    assert row2 and not row2[0]["passed"], "verdict in GATE DECISION dodged the scan"
    assert not sg.validate_rule_0b_a(data2.get("rule_0b_a_edict", ""),
                                     full_text="\n".join(
                                         str(v) for v in data2.values() if v))[0]
