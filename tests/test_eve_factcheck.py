"""G1 test for src/eve_unleashed/factcheck.py.

Live checks hit the network at check time, so tests patch urlopen:
receipts hash the bytes seen, Wikipedia misses read ABSENT, entity
extraction feeds lookups, and grievance cross-checks measure shared
terms. Deterministic under patch; live proof runs separately.
"""
import hashlib
import io
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed import factcheck as F


class _Resp:
    def __init__(self, body, status=200):
        self._body = body
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _wiki_payload(title="Springfield"):
    return json.dumps({"title": title, "description": "city",
                       "extract": "Springfield is a city."}).encode()


def test_fetch_url_receipt_hashes_bytes():
    body = b"hello docket"
    with patch.object(F.urllib.request, "urlopen",
                      return_value=_Resp(body)):
        r = F.fetch_url("http://example.test/filing")
    assert r["status"] == "ok"
    assert r["bytes"] == len(body)
    assert r["sha256"] == hashlib.sha256(body).hexdigest()
    assert r["fetched_utc"].endswith("Z")


def test_fetch_url_failure_receipted():
    with patch.object(F.urllib.request, "urlopen",
                      side_effect=TimeoutError("slow")):
        r = F.fetch_url("http://example.test/down")
    assert r["status"] == "failed"
    assert "slow" in r["error"]


def test_wikipedia_found_and_absent():
    with patch.object(F.urllib.request, "urlopen",
                      return_value=_Resp(_wiki_payload())):
        hit = F.wikipedia_lookup("Springfield")
    assert hit["found"] and hit["title"] == "Springfield"
    with patch.object(F.urllib.request, "urlopen",
                      return_value=_Resp(b"{}", status=404)):
        miss = F.wikipedia_lookup("No Such Place Xyz")
    assert miss["found"] is False


def test_extract_entities_picks_names():
    ents = F.extract_entities(
        "The Springfield Dam hearing included Jane Adams twice.")
    assert "Springfield Dam" in ents
    assert "Jane Adams" in ents


def test_factcheck_corroborated_under_patch():
    with patch.object(F.urllib.request, "urlopen",
                      return_value=_Resp(_wiki_payload("Springfield Dam"))):
        res = F.factcheck_claim("The Springfield Dam holds water.")
    assert res["verdict"] == "CORROBORATED"
    assert len(res["receipts"]) == len(res["entity_lookups"]) >= 1


def test_factcheck_refuted_beats_lookups():
    res = F.factcheck_claim("This always stands except when it falls.")
    assert res["verdict"] == "REFUTED"
    assert res["debunk"]["verdict"] == "REFUTED"


def test_factcheck_grievance_crosscheck(tmp_path, monkeypatch):
    import eve_unleashed.redress as R
    monkeypatch.setattr(R, "GRIEVANCE_DIR", tmp_path)
    rec = R.file_grievance("Acme Water", "environment",
                           "The Springfield Dam leaks into the river nightly.",
                           "Repair the dam.")
    with patch.object(F.urllib.request, "urlopen",
                      side_effect=TimeoutError("offline")):
        res = F.factcheck_claim("The Springfield Dam leaks nightly.",
                                grievance_id=rec["id"])
    cc = res["grievance_crosscheck"]
    assert cc["matched"] and cc["consistent"]
    assert res["verdict"] == "UNCORROBORATED"
