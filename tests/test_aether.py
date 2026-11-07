# coding: utf-8
"""Aether tests, part 1: A-4 adversarial auditors, A-1 agreement leg, A-2 floor.

A-4's rule: a gate nobody has seen fail is an assertion, not a control. Every
case below feeds an auditor a sabotaged artifact -- a verdict it must catch,
not a fixture written to agree with it. The sabotage fixtures are transcribed
from each auditor's own violation classes (its docstring), never invented.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import agreement_floor  # noqa: E402
import claim_agreement  # noqa: E402
import leg_ledger  # noqa: E402
import reading_audit  # noqa: E402
import settings_shadow  # noqa: E402


# --- A-4: reading_audit must catch denominator-free and collapsed verdicts ---

def test_sabotaged_pass_without_counts_is_denominator_free():
    findings = []
    n = reading_audit.audit_verdicts({"verdict": "PASS"}, "sabotage", findings)
    assert n == 1
    assert findings and findings[0]["class"] == "denominator_free"


def test_pass_over_zero_counts_is_collapsed():
    findings = []
    reading_audit.audit_verdicts({"verdict": "ok", "files": 0}, "sabotage", findings)
    assert findings and findings[0]["class"] == "collapsed"


def test_control_counted_pass_is_clean():
    findings = []
    n = reading_audit.audit_verdicts({"verdict": "PASS", "files": 40}, "control",
                                     findings)
    assert (n, findings) == (1, [])


# --- A-4: leg_ledger must catch verdict and state sabotage ---

def _leg(name, status, seconds=1.2, detail="ran"):
    return {"leg": name, "status": status, "seconds": seconds, "detail": detail}


def test_pass_over_failed_leg_is_verdict_mismatch():
    bad = leg_ledger.audit({"legs": [_leg("forensics", "error", detail="boom")],
                            "verdict": "PASS"})
    assert any(v["class"] == "verdict_mismatch" for v in bad)


def test_fail_with_no_failing_leg_is_verdict_mismatch():
    bad = leg_ledger.audit({"legs": [_leg("forensics", "ok")], "verdict": "FAIL"})
    assert any(v["class"] == "verdict_mismatch" for v in bad)


def test_invented_state_is_unknown_state():
    bad = leg_ledger.audit({"legs": [_leg("web", "maybe")], "verdict": "FAIL"})
    assert any(v["class"] == "unknown_state" for v in bad)


def test_control_clean_ledger_is_empty():
    assert leg_ledger.audit({"legs": [_leg("forensics", "ok")],
                             "verdict": "PASS"}) == []


# --- A-4: settings_shadow wrapper rule, from its own measured false finding ---

def test_param_passthrough_is_a_wrapper_literal_is_not():
    tree = ast.parse("def setting(key, fb):\n    return read_default(key, fb)\n"
                     "def main():\n    return read_default('some.key', 1)\n")
    assert settings_shadow.local_wrappers(tree) == {"setting"}


def test_flatten_names_dotted_leaves():
    assert ("a.b", 1) in settings_shadow.flatten({"a": {"b": 1}})


# --- A-1: agreement leg replays the log, blind when there is nothing ---

def _log(tmp_path, pairs):
    p = tmp_path / "live.jsonl"
    with open(p, "w", encoding="utf-8") as fh:
        for i in range(pairs):
            fh.write(json.dumps({"phase": "fetch", "event": "intuition",
                                 "url": "http://h/%d" % i, "ts": i * 2,
                                 "guess": "guess", "predicted": None}) + "\n")
            fh.write(json.dumps({"phase": "fetch", "event": "answer",
                                 "url": "http://h/%d" % i, "ts": i * 2 + 1,
                                 "rung": 5, "state": "ok"}) + "\n")
    return str(p)


def test_agreement_measures_replayed_rate(tmp_path):
    m = claim_agreement.measure(_log(tmp_path, 4))
    assert (m["pairs"], m["hits"], m["hit_rate"]) == (4, 4, 1.0)


def test_agreement_holds_and_rots_by_floor(tmp_path):
    log = _log(tmp_path, 4)
    assert claim_agreement.main(["--log", log, "--floor", "0.5"]) == 0
    assert claim_agreement.main(["--log", log, "--floor", "1.1"]) == 1


def test_agreement_blind_without_pairs(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    assert claim_agreement.main(["--log", str(p)]) == 2
    assert claim_agreement.main(["--log", str(tmp_path / "missing.jsonl")]) == 2


# --- A-2: floor tunes from evidence, refuses on noise ---

def _cfg(tmp_path):
    c = tmp_path / "defaults.json"
    c.write_text(json.dumps({"hyper_edge": {}}), encoding="utf-8")
    return str(c)


def test_floor_writes_measured_rate(tmp_path):
    cfg = _cfg(tmp_path)
    rc = agreement_floor.main(["--log", _log(tmp_path, 20), "--config", cfg])
    assert rc == 0
    assert json.loads(Path(cfg).read_text())["hyper_edge"]["agreement_floor"] == 1.0


def test_floor_refuses_thin_evidence(tmp_path):
    cfg = _cfg(tmp_path)
    before = Path(cfg).read_text()
    assert agreement_floor.main(["--log", _log(tmp_path, 3),
                                 "--config", cfg]) == 2
    assert Path(cfg).read_text() == before
