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

import json  # noqa: E402

from HYPER_EDGE import cli, compat, dream, evolution, microcode, mutate  # noqa: E402


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


# --- microcode that repairs itself ------------------------------------------
#
# The patch engine's failure modes are the quiet ones: a patch admitted without a
# counterexample, a patch that trades one broken reading for another, a ledger
# whose identity drifts with the clock, and a repeated proposal logged twice.

UNDATED = {key: value for key, value in _complete_record().items() if key != "age_days"}


def _case(case_id: str, expected: str, record: dict, code: str = "0x09",
          prove: bool = True) -> dict:
    case = {"id": case_id, "code": code, "record": record, "expected": expected}
    if prove:
        case.update(command="tools/x.py --check", digest="EXIT=0 OK")
    return case


def _blind_patch() -> dict:
    return {"op": "0x09", "knob": "undated",
            "old": microcode.POLICY["0x09"]["undated"], "new": "blind"}


@pytest.fixture()
def skip_undated():
    """The pre-fix policy, so the patch engine has a failing case to repair.

    The live policy is blind because the fix was admitted; a test that assumed
    one or the other would pass or fail on an installation artifact rather than
    on the engine's behaviour.
    """
    saved = microcode.POLICY["0x09"]["undated"]
    microcode.set_policy({"0x09": {"undated": "skip"}})
    try:
        yield
    finally:
        microcode.set_policy({"0x09": {"undated": saved}})


def test_a_patch_with_nothing_to_fix_is_a_preference_not_a_repair():
    verdict = mutate.admit(_blind_patch(), [_case("only", microcode.PASS, _complete_record())])
    assert verdict["admissible"] is False
    assert any("no failing case" in reason for reason in verdict["reasons"])


def test_a_counterexample_without_a_command_cannot_pay_for_a_patch(skip_undated):
    verdict = mutate.admit(_blind_patch(), [_case("undated", "BLIND", UNDATED, prove=False)])
    assert verdict["admissible"] is False
    assert any("command/digest" in reason for reason in verdict["reasons"])


def test_a_patch_that_regresses_a_passing_case_is_refused(skip_undated):
    cases = [_case("undated", "BLIND", UNDATED),
             _case("legacy", "SKIP", UNDATED)]
    verdict = mutate.admit(_blind_patch(), cases)
    assert verdict["admissible"] is False
    assert verdict["regressions"] == ["legacy"]


def test_the_admitted_patch_is_least_severe_and_ledgered(tmp_path, skip_undated):
    cases = [_case("undated", "BLIND", UNDATED)]
    entry = mutate.apply(_blind_patch(), cases,
                         policy_path=tmp_path / "mc.json", log=tmp_path / "led.jsonl")
    assert entry["new"] == "blind"
    assert json.loads((tmp_path / "mc.json").read_text())["policy"]["0x09"]["undated"] == "blind"
    assert mutate.chain(tmp_path / "led.jsonl")["ok"] is True
    microcode.set_policy({"0x09": {"undated": "skip"}})
    with pytest.raises(mutate.PatchRefused) as refusal:
        mutate.apply(_blind_patch(), cases,
                     policy_path=tmp_path / "mc.json", log=tmp_path / "led.jsonl")
    assert any("already entry" in reason for reason in refusal.value.reasons)


def test_a_patch_identity_does_not_move_with_the_clock(tmp_path, skip_undated):
    cases = [_case("undated", "BLIND", UNDATED)]
    first = mutate.apply(_blind_patch(), cases, dry_run=True)
    second = mutate.apply(_blind_patch(), cases, dry_run=True)
    assert first["patch"] == second["patch"]
    assert mutate.chain(Path("nonexistent-log.jsonl"))["entries"] == 0


def test_the_chain_names_a_tampered_line(tmp_path, skip_undated):
    log = tmp_path / "led.jsonl"
    cases = [_case("undated", "BLIND", UNDATED)]
    mutate.apply(_blind_patch(), cases, policy_path=tmp_path / "mc.json", log=log)
    entry = json.loads(log.read_text().splitlines()[0])
    entry["new"] = "cut"
    log.write_text(json.dumps(entry) + "\n")
    verdict = mutate.chain(log)
    assert verdict["ok"] is False and "digest" in verdict["reason"]


# --- dreaming: the model proposes, the ISA grades, evidence decides ----------


def test_a_dream_spelling_a_key_wrong_is_graded_not_dropped():
    dreams, refused = dream.grade([{"id": "d1", "record": {
        "tier": "A", "why": "a nested field the model put in the wrong place"}}])
    assert refused == []
    assert dreams[0]["dropped_keys"] == ["why"]
    assert dreams[0]["record"] == {"tier": "A"}


def test_a_dream_with_no_isa_key_is_refused_by_name():
    dreams, refused = dream.grade([{"id": "d2", "record": {"nonsense": 1}},
                                  {"id": "d3"}])
    assert dreams == []
    assert any("d2" in reason for reason in refused)
    assert any("d3" in reason for reason in refused)


def test_a_malformed_reading_is_graded_blind_not_raised():
    bad = dict(_complete_record(), draws=[1, 2], reproduced=True)
    result = microcode.evaluate(bad)
    assert result["rung"] == microcode.BLIND
    assert "0x0A" in result["faults"]


def test_a_dream_never_carries_an_admissible_verdict():
    dreams, _ = dream.grade([{"id": "d4", "record": UNDATED}])
    rows = dream.discriminate(dreams)
    assert rows, "the undated reading must separate at least one knob"
    assert {row["verdict"] for row in rows} == {"a_dream_is_not_evidence"}


def test_an_environment_without_evidence_is_blind_not_optimised(skip_undated):
    rows = mutate.optimize(["windows", "kali"], {"windows": [_case("u", "BLIND", UNDATED)]},
                           workers=2)
    status = {row["env"]: row["status"] for row in rows}
    assert status["kali"] == "no_evidence"
    assert status["windows"] in ("proposed", "converged")
