"""G1 test for src/eve_unleashed/redress.py.

A grievance filed must be listed back with its id; the FOIA draft must
carry the agency, the requester and the redress; the tutorial must teach
filing; referrals must always include the national directory. Docket
search is network-bound and stays out of the gate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed import redress


def test_file_and_list_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(redress, "GRIEVANCE_DIR", tmp_path)
    rec = redress.file_grievance("Acme", "consumer", "Billed wrongly.",
                                 "Refund.", evidence=["bill.pdf"])
    recs = redress.list_grievances()
    assert len(recs) == 1 and recs[0]["id"] == rec["id"]
    assert recs[0]["status"] == "filed"


def test_bad_category_rejected(tmp_path, monkeypatch):
    import pytest
    monkeypatch.setattr(redress, "GRIEVANCE_DIR", tmp_path)
    with pytest.raises(ValueError):
        redress.file_grievance("X", "nope", "n", "r")


def test_foia_draft_carries_parties_and_redress():
    rec = {"id": "grv-t", "category": "consumer", "narrative": "N",
           "redress_sought": "R"}
    letter = redress.draft_foia(rec, "EPA", "J. Doe")
    for needle in ("EPA", "J. Doe", "grv-t", "R", "5 U.S.C"):
        assert needle in letter, needle


def test_tutorial_teaches_filing_and_referral_lists_lawhelp():
    steps = redress.tutorial()
    assert any("eve grievance file" in s for s in steps)
    urls = [u for _, u in redress.legal_referral("pa")]
    assert "https://www.lawhelp.org/" in urls
    assert any("lawhelp.org/states/pa" in u for u in urls)
