"""Pin the admissibility ISA in `src/HYPER_EDGE/microcode.py` and its engine.

The properties worth pinning are the ones whose failure is silent:

  * a split vote must not obtain a verdict -- at exactly 0.50 a 3-2-1 split's top
    share equals quorum, and `>=` would let it through (`legacy` mode is the old
    behaviour kept on purpose, so migration can be watched);
  * every op must carry its legacy column, or the migration instrument reports
    parity it never had;
  * a complete reading reaches VERIFIED and an incomplete one does not, so the
    ladder is not a constant.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# The repo's own convention: `tests/` bootstraps `src` itself.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from HYPER_EDGE import cli, compat, evolution, microcode  # noqa: E402


def _complete_record() -> dict:
    """The selftest's own complete reading, not a re-invented one.

    A fixture written from the ops' field names validates the test author's
    assumptions; this one is the reading the engine's own selftest grades, so the
    test fails when the ISA and the selftest disagree.
    """
    return dict(cli.GOOD)


def test_isa_has_twelve_unique_codes():
    table = microcode.isa_table()
    assert len(table) == 12
    codes = [row["code"] for row in table]
    assert len(set(codes)) == 12


def test_every_op_documents_its_legacy_behaviour():
    for row in microcode.isa_table():
        assert row["legacy"].strip(), "op %s has no legacy column" % row["code"]


def test_a_quorum_that_cannot_exclude_a_split_is_refused():
    with pytest.raises(ValueError, match="cannot exclude a 0.50 split"):
        microcode.quorum_state(0.50, 0.50)


def test_legacy_mode_is_no_excuse_for_an_impossible_quorum():
    with pytest.raises(ValueError):
        microcode.quorum_state(0.50, 0.50, legacy=True)


def test_a_split_below_the_threshold_obtains_no_verdict():
    state, reason = microcode.quorum_state(0.50, 0.501)
    assert state == microcode.NO_QUORUM, reason


def test_legacy_mode_still_reports_the_split_as_obtained():
    state, reason = microcode.quorum_state(0.50, 0.501, legacy=True)
    assert state == microcode.PASS, reason
    assert "legacy" in reason


def test_complete_reading_reaches_verified():
    result = microcode.evaluate(_complete_record(), quorum=0.66, max_age_days=30.0)
    assert result["rung"] == "VERIFIED", microcode.summarize(result)


def test_a_claim_without_its_command_is_cut():
    record = _complete_record()
    record.pop("command")
    assert microcode.evaluate(record, quorum=0.66, max_age_days=30.0)["rung"] == "CUT"


def test_engine_refuses_a_quorum_that_cannot_exclude_a_split():
    evidence = {"rows": []}
    with pytest.raises(Exception):
        evolution.score(evidence, {"quorum": 0.50, "max_age_days": 30.0,
                                   "truncation_strict": True})


def test_engine_tally_agrees_with_the_judge():
    """The engine must not own a second definition of 'share'."""
    # The judge's own vocabulary, read from the judge not guessed: a 2/3 top share.
    rows = [{"pin": "p1", "grade": "SUPPORTED"},
            {"pin": "p1", "grade": "SUPPORTED"},
            {"pin": "p1", "grade": "UNSUPPORTED"}]
    verdict = evolution.crosscheck({"rows": rows},
                                   {"p1": {"share": 2.0 / 3.0, "verdicts": 3}})
    if not verdict["available"]:
        pytest.skip("arena_llm_judge not importable in this environment")
    assert verdict["mismatches"] == []


def test_parallel_map_preserves_input_order():
    assert compat.parallel_map(lambda n: n * n, list(range(32))) == [n * n for n in range(32)]
