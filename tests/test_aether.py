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


# --- A-5: the verdict casts three ways, blind when there is no report ---

import cast_verdict  # noqa: E402
import domain_verify  # noqa: E402
import findings_ledger  # noqa: E402


def _report(tmp_path, legs, verdict="PASS"):
    p = tmp_path / "deep_dive.json"
    p.write_text(json.dumps({"generated": "2026-11-07T00:00:00Z",
                             "elapsed_s": 9.9, "verdict": verdict,
                             "legs": legs}), encoding="utf-8")
    return str(p)


def test_cast_writes_chronicle_and_history(tmp_path):
    rep = _report(tmp_path, [{"leg": "forensics", "status": "ok",
                               "seconds": 1.0, "detail": "clean"}])
    md = str(tmp_path / "verdict.md")
    hist = str(tmp_path / "history.jsonl")
    assert cast_verdict.main(["--report", rep, "--md", md,
                              "--history", hist]) == 0
    text = Path(md).read_text()
    assert "verdict: PASS" in text and "forensics" in text
    rows = Path(hist).read_text().strip().splitlines()
    assert len(rows) == 1 and json.loads(rows[0])["legs"] == {"forensics": "ok"}


def test_cast_blind_without_report(tmp_path):
    assert cast_verdict.main(["--report", str(tmp_path / "missing.json")]) == 2


# --- A-3: findings transition new -> persisting -> fixed ---

def _failing_leg(name, detail="boom"):
    return {"leg": name, "status": "error", "seconds": 1.0, "detail": detail}


def _ok_leg(name):
    return {"leg": name, "status": "ok", "seconds": 1.0, "detail": "ran"}


def test_findings_transition(tmp_path):
    led = str(tmp_path / "ledger.jsonl")
    rep1 = _report(tmp_path, [_failing_leg("x")], verdict="FAIL")
    assert findings_ledger.main(["--report", rep1, "--ledger", led]) == 0
    recs = [json.loads(l) for l in Path(led).read_text().splitlines()]
    assert recs[0]["status"] == "new"
    rep2 = _report(tmp_path, [_failing_leg("x", "still"), _failing_leg("y")],
                    verdict="FAIL")
    findings_ledger.main(["--report", rep2, "--ledger", led])
    by_id = {r["id"]: r for r in
             (json.loads(l) for l in Path(led).read_text().splitlines())}
    assert by_id["x"]["status"] == "persisting"
    assert by_id["y"]["status"] == "new"
    rep3 = _report(tmp_path, [_ok_leg("x"), _failing_leg("y")], verdict="FAIL")
    findings_ledger.main(["--report", rep3, "--ledger", led])
    by_id = {r["id"]: r for r in
             (json.loads(l) for l in Path(led).read_text().splitlines())}
    assert by_id["x"]["status"] == "fixed"
    assert by_id["y"]["status"] == "persisting"


def test_ledger_blind_without_report(tmp_path):
    assert findings_ledger.main(["--report", str(tmp_path / "missing.json"),
                                 "--ledger", str(tmp_path / "l.jsonl")]) == 2


# --- A-6: fail dominates, blind shapes the run, pass holds ---

def test_merge_exit_shapes():
    assert domain_verify.merge({"a": {"status": "pass"}}) == 0
    assert domain_verify.merge({"a": {"status": "pass"},
                                "b": {"status": "blind"}}) == 2
    assert domain_verify.merge({"a": {"status": "blind"},
                                "b": {"status": "fail"}}) == 1


def test_run_maps_child_exit():
    assert domain_verify.run([sys.executable, "-c", "pass"])["status"] == "pass"
    assert domain_verify.run([sys.executable, "-c",
                               "raise SystemExit(3)"])["status"] == "fail"
    assert domain_verify.run(["/nonexistent/binary"])["status"] == "blind"
