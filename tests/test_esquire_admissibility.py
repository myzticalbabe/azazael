"""Tests for tools/esquire_admissibility.py.

Two directions are tested on purpose. A gate that rejects everything is as
useless as a gate that accepts everything, so several tests here are NEGATIVE
CONTROLS: a record that a careless test would fail must pass. The controls match
the ones published in GATE_METADATA and in docs/ESQUIRE_ADMISSIBILITY_2026-11-04.md.
"""

from __future__ import annotations

import copy
import json

import pytest

from tools.esquire_admissibility import (
    EXIT_BLIND,
    EXIT_GAPS,
    EXIT_READY,
    GAP,
    GATE_METADATA,
    PASS,
    UNVERIFIABLE,
    VERDICT_BLIND,
    VERDICT_GAPS,
    VERDICT_INCOMPLETE,
    VERDICT_READY,
    evaluate,
    main,
    record_sha256,
    render,
    render_gates,
)

SHA = "a" * 64
SHA2 = "b" * 64


def clean() -> dict:
    """A record that satisfies every gate. Each test perturbs one thing."""
    return {
        "proffer": {
            "case": "Test v. Fixture",
            "offered_by": "proponent",
            "purpose": "to show the valuation on which the offer rested",
            "ai_assistance_disclosed": True,
        },
        "witness": {
            "kind": "human",
            "name": "A. Expert",
            "qualifications": ["valuation", "ten years in the field"],
            "reviewed_output": True,
        },
        "inputs": {
            "records": [
                {"id": "r1", "source": "ledger export", "sha256": SHA},
                {"id": "r2", "source": "audited accounts", "sha256": SHA2},
            ],
            "sufficiency_statement": "both years of records, complete and hashed",
        },
        "method": {
            "model": {
                "name": "valuation-model",
                "version": "3.2.1",
                "provenance": "internal weights, frozen build, checksum on file",
            },
            "evaluation": {"error_rate": 0.04, "test_set": "240 held-out filings"},
            "peer_review": True,
            "general_acceptance": "accepted",
        },
        "claims": [
            {
                "id": "c1",
                "text": "the enterprise value on the offer date",
                "inputs": ["r1", "r2"],
                "citations": [],
            }
        ],
        "authentication": {
            "output_sha256": SHA,
            "custody": ["generated", "exported", "stored"],
        },
        "hearsay": {
            "posture": "machine_record",
            "business_records": {
                "custodian": "D. Recordskeeper",
                "regular_practice": True,
            },
        },
        "review": {
            "name": "A. Expert",
            "authority_to_change": True,
            "recorded_at": "2026-11-04",
            "changes_made": 2,
        },
    }


def gate_state(report: dict, gate_id: str) -> str:
    for gate in report["gates"]:
        if gate["gate"] == gate_id:
            return gate["state"]
    raise AssertionError(f"gate {gate_id} missing from report")


def test_clean_record_is_ready():
    report = evaluate(clean())
    assert report["verdict"] == VERDICT_READY
    assert report["counts"] == {PASS: 7, GAP: 0, UNVERIFIABLE: 0}


def test_negative_control_daubert_factors_are_not_a_checklist():
    """A novel, unreviewed method with a measured error rate must still pass.

    The Daubert factors are non-exhaustive; requiring all four would encode an
    error of law as a test. This is the control that keeps G3 honest.
    """
    record = clean()
    record["method"]["peer_review"] = False
    record["method"]["general_acceptance"] = "novel"

    report = evaluate(record)

    assert report["verdict"] == VERDICT_READY
    assert gate_state(report, "G3") == PASS
    notes = [n for gate in report["gates"] for n in gate["notes"]]
    assert any("peer review" in note for note in notes)
    assert any("novel" in note for note in notes)


def test_negative_control_opinion_without_citations_passes():
    """Citation integrity is conditional: a measurement carries no authorities."""
    record = clean()
    assert record["claims"][0]["citations"] == []
    assert gate_state(evaluate(record), "G4") == PASS


def test_negative_control_reviewer_who_changed_nothing_passes():
    record = clean()
    record["review"]["changes_made"] = 0

    report = evaluate(record)

    assert report["verdict"] == VERDICT_READY
    notes = [n for gate in report["gates"] for n in gate["notes"]]
    assert any("changed nothing" in note for note in notes)


def test_fully_certified_output_passes_without_custody_chain():
    """FRE 902(13) is an alternative route to G5, not a supplement."""
    record = clean()
    record["authentication"] = {
        "output_sha256": SHA,
        "custody": [],
        "certification_902_13": {
            "certifier": "C. Custodian",
            "qualified": True,
            "notice_given": True,
        },
    }

    report = evaluate(record)

    assert report["verdict"] == VERDICT_READY
    assert gate_state(report, "G5") == PASS


def test_model_as_witness_is_a_gap():
    record = clean()
    record["witness"] = {"kind": "model", "name": "valuation-model-3"}

    report = evaluate(record)

    assert gate_state(report, "G1") == GAP
    assert report["verdict"] == VERDICT_GAPS
    assert "natural person" in render(report)


def test_absent_witness_is_unaddressed_not_failed():
    record = clean()
    del record["witness"]

    report = evaluate(record)

    assert gate_state(report, "G1") == UNVERIFIABLE
    assert report["verdict"] == VERDICT_INCOMPLETE


def test_fabricated_citation_is_a_gap_naming_mata():
    record = clean()
    record["claims"][0]["citations"] = [
        {"locator": "999 F.3d 1 (2099)", "verification": "fabricated"}
    ]

    report = evaluate(record)

    assert gate_state(report, "G4") == GAP
    detail = next(g["detail"] for g in report["gates"] if g["gate"] == "G4")
    assert "Mata" in detail


def test_unverified_citation_is_a_gap():
    record = clean()
    record["claims"][0]["citations"] = [
        {"locator": "410 U.S. 113", "verification": "recalled"}
    ]

    assert gate_state(evaluate(record), "G4") == GAP


def test_citation_read_at_source_passes():
    record = clean()
    record["claims"][0]["citations"] = [
        {"locator": "509 U.S. 579", "verification": "primary_read"}
    ]

    assert gate_state(evaluate(record), "G4") == PASS


def test_claim_tied_to_unknown_input_is_a_gap():
    record = clean()
    record["claims"][0]["inputs"] = ["r1", "r-does-not-exist"]

    report = evaluate(record)

    assert gate_state(report, "G4") == GAP
    assert "unknown input" in render(report)


def test_unversioned_model_is_a_gap():
    record = clean()
    del record["method"]["model"]["version"]

    assert gate_state(evaluate(record), "G3") == GAP


def test_impossible_error_rate_is_a_gap():
    record = clean()
    record["method"]["evaluation"]["error_rate"] = 1.5

    assert gate_state(evaluate(record), "G3") == GAP


def test_input_without_hash_is_a_gap():
    record = clean()
    record["inputs"]["records"][0]["sha256"] = "not-a-hash"

    assert gate_state(evaluate(record), "G2") == GAP


def test_no_inputs_is_unaddressed():
    record = clean()
    record["inputs"]["records"] = []

    assert gate_state(evaluate(record), "G2") == UNVERIFIABLE


def test_unauthenticated_output_is_unaddressed():
    record = clean()
    del record["authentication"]

    assert gate_state(evaluate(record), "G5") == UNVERIFIABLE


def test_incomplete_certification_names_the_missing_element():
    record = clean()
    record["authentication"] = {
        "output_sha256": SHA,
        "custody": [],
        "certification_902_13": {
            "certifier": "C. Custodian",
            "qualified": True,
            "notice_given": False,
        },
    }

    report = evaluate(record)

    assert gate_state(report, "G5") == GAP
    assert "notice_given" in render(report)


def test_hearsay_exception_without_notice_is_a_gap():
    record = clean()
    record["hearsay"] = {
        "posture": "offered_for_truth_exception",
        "exception": "FRE 803(6)",
        "notice_given": False,
    }

    assert gate_state(evaluate(record), "G6") == GAP


def test_machine_record_without_a_predicate_is_a_gap():
    record = clean()
    record["hearsay"] = {"posture": "machine_record"}

    assert gate_state(evaluate(record), "G6") == GAP


def test_nominal_reviewer_is_a_gap():
    """A reviewer with no power to change the output is the fig leaf E-5 names."""
    record = clean()
    record["review"]["authority_to_change"] = False

    report = evaluate(record)

    assert gate_state(report, "G7") == GAP
    assert "authority" in render(report)


def test_undisclosed_ai_assistance_is_a_gap():
    record = clean()
    record["proffer"]["ai_assistance_disclosed"] = False

    assert gate_state(evaluate(record), "G7") == GAP


def test_unreadable_record_is_blind_never_a_pass():
    for bad in ({}, {"proffer": "not-an-object"}, [], None):
        report = evaluate(bad)
        assert report["verdict"] == VERDICT_BLIND
        assert report["gates"] == []
        assert "admissibility is decided" in report["disclaimer"]


def test_evaluation_is_deterministic_and_key_order_independent():
    first = clean()
    second = copy.deepcopy(first)
    # Rebuild with reversed insertion order to prove the hash ignores ordering.
    second = {key: second[key] for key in reversed(list(second))}

    report_a = evaluate(first)
    report_b = evaluate(second)

    assert record_sha256(first) == record_sha256(second)
    assert report_a == report_b


def test_render_never_claims_admissibility():
    for record in (clean(), {}, {**clean(), "witness": {"kind": "model"}}):
        text = render(evaluate(record)).lower()
        assert "admissible" not in text.replace("admissibility", "")


def test_cli_ready_exits_zero(tmp_path, capsys):
    path = tmp_path / "proffer.json"
    path.write_text(json.dumps(clean()), encoding="utf-8")

    assert main([str(path)]) == EXIT_READY
    assert "READY" in capsys.readouterr().out


def test_cli_gaps_exit_one_and_json_mode(tmp_path, capsys):
    record = clean()
    record["review"]["authority_to_change"] = False
    path = tmp_path / "proffer.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    assert main([str(path), "--json"]) == EXIT_GAPS
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == VERDICT_GAPS


def test_cli_missing_file_is_blind_and_never_zero(tmp_path, capsys):
    assert main([str(tmp_path / "absent.json")]) == EXIT_BLIND
    assert "BLIND" in capsys.readouterr().out


def test_cli_invalid_json_is_blind(tmp_path, capsys):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    assert main([str(path)]) == EXIT_BLIND
    assert "BLIND" in capsys.readouterr().out


def test_gate_table_covers_every_gate_and_states_a_falsifier():
    assert [meta["id"] for meta in GATE_METADATA] == [f"G{i}" for i in range(1, 8)]
    for meta in GATE_METADATA:
        assert meta["authority"]
        assert meta["falsifier"]
        assert meta["negative_control"]
    text = render_gates()
    assert "negative control" in text
    assert "G7" in text


@pytest.mark.parametrize("gate_id", [f"G{i}" for i in range(1, 8)])
def test_every_gate_can_fail(gate_id):
    """Each gate must be able to return GAP, or it is not a test.

    Without this, a gate that silently returns PASS for everything would keep
    the clean-record test green while testing nothing.
    """
    perturbations = {
        "G1": lambda r: r["witness"].update({"kind": "model"}),
        "G2": lambda r: r["inputs"]["records"][0].update({"sha256": "x"}),
        "G3": lambda r: r["method"]["model"].pop("version"),
        "G4": lambda r: r["claims"][0].update({"inputs": ["nope"]}),
        "G5": lambda r: r["authentication"].update({"output_sha256": "x"}),
        "G6": lambda r: r.update({"hearsay": {"posture": "machine_record"}}),
        "G7": lambda r: r["review"].update({"authority_to_change": False}),
    }
    record = clean()
    perturbations[gate_id](record)

    assert gate_state(evaluate(record), gate_id) == GAP
