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
import os  # noqa: E402
import time  # noqa: E402

from HYPER_EDGE import cli, compat, dream, evolution, kernel, microcode, mutate  # noqa: E402


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


@pytest.fixture(autouse=True)
def _isolated_converge(tmp_path, monkeypatch):
    """No test may write the committed converge record.

    A test that proves a converge against its own tiny corpus would otherwise
    replace the real per-environment record, and the next real run would read
    "the corpus moved" from a fixture.
    """
    monkeypatch.setattr(mutate, "CONVERGE_FILE", tmp_path / "converge.json")


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


def test_a_serial_run_is_named_whatever_its_rows_claim(monkeypatch):
    """Concurrency is measured by the kernel, never declared by the caller."""
    monkeypatch.setattr(mutate, "parallel_map",
                        lambda fn, items, **kw: [fn(item) for item in items])

    def burn(cases, policy=None):
        end = time.process_time() + 0.12
        while time.process_time() < end:
            sum(range(1000))
        return {"failing": []}

    monkeypatch.setattr(mutate, "replay", burn)
    # Names the converge record cannot already hold: a prior real converge with a
    # different corpus would (correctly) mark these rows stale before the timing
    # guard runs, which would test the other guard.
    rows = mutate.optimize(["t-serial-a", "t-serial-b"],
                           {"t-serial-a": [{"id": "a"}],
                            "t-serial-b": [{"id": "b"}]},
                           workers=2)
    assert {row["status"] for row in rows} == {"serial"}
    assert all("one after another" in " ".join(row["reasons"]) for row in rows)
    assert rows[0]["concurrency"]["verdict"] == "serial"


def test_a_run_too_cheap_to_time_is_unjudged_not_a_failure():
    rows = mutate.optimize(["a", "b"], {"a": [_case("u", "BLIND", UNDATED)],
                                         "b": [_case("u", "BLIND", UNDATED)]},
                           workers=2)
    assert rows[0]["concurrency"]["judged"] is False
    assert rows[0]["concurrency"]["verdict"] == "unjudged"
    assert {row["status"] for row in rows} == {"converged"}


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


def test_a_patch_is_bound_to_the_artefact_it_was_written_into(tmp_path, skip_undated):
    """The chain proves the ledger was not edited; only identity proves the file."""
    log = tmp_path / "led.jsonl"
    target = tmp_path / "mc.json"
    entry = mutate.apply(_blind_patch(), [_case("undated", "BLIND", UNDATED)],
                         policy_path=target, log=log)
    assert entry["artifact"] == str(target) and entry["artifact_id"]
    verdict = mutate.chain(log)
    assert verdict["artifacts"] == {"bound": 1, "unbound": 0, "reissued": []}

    # Byte-identical re-issue: os.replace puts a *different* inode at the same
    # path. Nothing in the file's bytes changed, so no hash can see this.
    replacement = tmp_path / "reissue.json"
    replacement.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
    os.replace(replacement, target)
    again = mutate.chain(log)
    assert len(again["artifacts"]["reissued"]) == 1
    assert again["artifacts"]["reissued"][0]["entry"] == 1


def test_the_chain_names_a_tampered_line(tmp_path, skip_undated):
    log = tmp_path / "led.jsonl"
    cases = [_case("undated", "BLIND", UNDATED)]
    mutate.apply(_blind_patch(), cases, policy_path=tmp_path / "mc.json", log=log)
    entry = json.loads(log.read_text().splitlines()[0])
    entry["new"] = "cut"
    log.write_text(json.dumps(entry) + "\n")
    verdict = mutate.chain(log)
    assert verdict["ok"] is False and "digest" in verdict["reason"]


# --- the kernel layer: identity, leases, accounting -------------------------

def test_a_lease_is_exclusive_until_it_is_released(tmp_path):
    lease = tmp_path / "holder"
    first = kernel.acquire(lease)
    assert first["acquired"] is True
    second = kernel.acquire(lease)
    assert second["acquired"] is False
    assert str(os.getpid()) in second["holder"], second["holder"]
    assert kernel.held(lease)
    assert kernel.release(lease) is True
    assert kernel.held(lease) is None
    assert kernel.acquire(lease)["acquired"] is True
    kernel.release(lease)


def test_a_baseline_is_one_sided_and_silent_without_one():
    assert kernel.compare_baseline(2.4, {"par_ratio": 2.2})["ok"] is True
    assert kernel.compare_baseline(1.0, {"par_ratio": 2.2})["ok"] is False
    silent = kernel.compare_baseline(1.0, {})
    assert silent["judged"] is False and "no recorded baseline" in silent["reason"]


def test_every_isa_op_states_the_grade_it_can_reach():
    grades = {row["code"]: row["grade"] for row in microcode.grades()}
    assert set(grades) == {op.code for op in microcode.ISA}
    assert [code for code, grade in grades.items() if grade == "ungraded"] == []
    assert grades["0x08"] == "kernel"


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


def test_a_dream_graded_against_a_reissued_artefact_is_named_not_used():
    entry = {"id": "d-stale", "rung": "CUT", "record": UNDATED,
             "artifact": "definitely-not-a-policy.json",
             "artifact_id": "dead:beef"}
    rows = dream.discriminate([entry])
    assert rows[0]["verdict"] == "stale_dropped"
    assert rows[0]["moved"] == ["d-stale"]


def test_a_dream_never_carries_an_admissible_verdict():
    dreams, _ = dream.grade([{"id": "d4", "record": UNDATED}])
    rows = dream.discriminate(dreams)
    assert rows, "the undated reading must separate at least one knob"
    assert {row["verdict"] for row in rows} == {"a_dream_is_not_evidence"}


def test_a_renamed_artefact_keeps_its_kernel_identity(tmp_path):
    if not kernel.available():
        pytest.skip("FILE_ID_INFO is a Windows kernel answer")
    original = tmp_path / "a.json"
    original.write_text("{}\n", encoding="utf-8")
    before = kernel.file_identity(original)
    moved = tmp_path / "b.json"
    original.rename(moved)
    assert before and kernel.file_identity(moved)["id"] == before["id"]


def test_a_reissued_artefact_is_cut_although_its_bytes_are_identical(tmp_path):
    """The one admissibility question a content hash cannot answer."""
    if not kernel.available():
        pytest.skip("FILE_ID_INFO is a Windows kernel answer")
    original = tmp_path / "a.json"
    original.write_text("{}\n", encoding="utf-8")
    identity = kernel.file_identity(original)
    reissued = tmp_path / "a-again.json"
    reissued.write_bytes(original.read_bytes())
    assert identity and kernel.file_identity(reissued)["id"] != identity["id"]

    receipt = dict(_complete_record(), artifact=str(reissued), artifact_id=identity["id"])
    result = microcode.evaluate(receipt)
    assert result["states"]["0x08"] == microcode.CUT
    bound = dict(_complete_record(), artifact=str(original), artifact_id=identity["id"])
    assert microcode.evaluate(bound)["states"]["0x08"] == microcode.PASS


def test_kernel_accounting_sees_concurrency_the_wall_clock_cannot():
    if not kernel.available():
        pytest.skip("GetThreadTimes is a Windows kernel answer")
    measured = kernel.parallelism(workers=4, work_s=0.03)
    # A wall-clock-only instrument reads ~1.0 by construction on an idle box; the
    # kernel numerator is what can exceed it. Under load by other lanes it lands
    # between 2 and 4.6 on this host, so the bar is >1, not ==workers.
    assert measured["par_ratio"] > 1.0


def test_an_environment_without_evidence_is_blind_not_optimised(skip_undated):
    rows = mutate.optimize(["windows", "kali"], {"windows": [_case("u", "BLIND", UNDATED)]},
                           workers=2)
    status = {row["env"]: row["status"] for row in rows}
    assert status["kali"] == "no_evidence"
    assert status["windows"] in ("proposed", "converged")
