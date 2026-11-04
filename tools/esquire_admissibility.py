#!/usr/bin/env python3
"""ESQUIRE-ADMISSIBILITY-v1: a proffer instrument for machine-produced opinions.

WHAT THIS IS
    A deterministic checker over a *proffer record*: the structured account a
    party would have to be able to give before offering a machine-produced
    opinion, output, or reproduction as evidence. For each admissibility gate it
    reports one of three states:

        PASS          the record carries what the gate requires
        GAP           the record addresses the gate and contradicts it
        UNVERIFIABLE  the record never addresses the gate

WHAT THIS IS NOT
    It does not decide admissibility. Admissibility is a ruling by a court after
    weighing facts this instrument cannot see (prejudice, confusion, the
    opponent's objections, the judge's gatekeeping discretion). The instrument
    therefore has no verdict named "admissible": its best state is READY, its
    worst reading of a well-formed record is GAPS, and a record it cannot read
    is BLIND, never "inadmissible". An instrument that could output
    "inadmissible" would be asserting a judicial conclusion from a form.

GATES AND AUTHORITY
    G1  qualification and disclosure      FRE 702 (preamble, (a))
    G2  sufficient facts or data          FRE 702(b)
    G3  reliable principles and methods   FRE 702(c); Daubert, 509 U.S. 579
    G4  reliable application + citations  FRE 702(d); Mata v. Avianca
    G5  authentication                     FRE 901(a), 901(b)(9), 902(13)-(14)
    G6  hearsay posture                    FRE 801, 803(6), 902(13)
    G7  human review and candor            Esquire E-1/E-5; ABA Formal Op. 512

    Three points of legal accuracy the implementation is built to respect:

    * The Daubert factors (testing, error rate, peer review, general
      acceptance) are NON-EXHAUSTIVE. A test that required all four would
      encode an error of law as a gate, so peer review and general acceptance
      are reported as supporting notes and can never by themselves fail G3.
    * FRE 702 as amended in December 2023 puts the burden on the proponent to
      demonstrate reliability "more likely than not"; the gate asks whether the
      record makes that demonstration possible, not whether it succeeded.
    * A machine is not a witness. G1 requires a named natural person who has
      reviewed the output, which is the bridge to the Esquire canon's naming
      rule: the mandate installs a human where a machine did the work.
    * FRE 902(13) is an AUTHENTICATION rule, not a hearsay exception. It is read
      here as satisfying G6 only because the certification it requires must
      itself comply with 902(11)/(12) and so carries the 803(6) foundation
      (made at or near the time, by someone with knowledge, in the regular
      course of activity). A record that cannot meet that foundation is not
      made admissible by a certification, and this instrument cannot see the
      difference: a G6 PASS on the 902(13) route is a statement about the
      record's paperwork, never about the record's truth status.

EXIT CODES
    0  READY       every gate PASS
    1  GAPS        at least one gate contradicted
    1  INCOMPLETE  no contradiction, but at least one gate never addressed
    2  BLIND       the record cannot be read; this is not a pass

SCHEMA (v1)
    {
      "proffer":  {"case": str, "offered_by": str, "purpose": str,
                   "ai_assistance_disclosed": bool},
      "witness":  {"kind": "human", "name": str, "qualifications": [str],
                   "reviewed_output": bool},
      "inputs":   {"records": [{"id": str, "source": str, "sha256": hex64}],
                   "sufficiency_statement": str},
      "method":   {"model": {"name": str, "version": str, "provenance": str},
                   "evaluation": {"error_rate": float, "test_set": str},
                   "peer_review": bool, "general_acceptance": str},
      "claims":   [{"id": str, "text": str, "inputs": [str],
                    "citations": [{"locator": str, "verification": str}]}],
      "authentication": {"output_sha256": hex64, "custody": [str],
                         "certification_902_13": {"certifier": str,
                                                  "qualified": bool,
                                                  "notice_given": bool}},
      "hearsay":  {"posture": str, "exception": str, "notice_given": bool,
                   "business_records": {"custodian": str,
                                        "regular_practice": bool}},
      "review":   {"name": str, "authority_to_change": bool,
                   "recorded_at": str, "changes_made": int}
    }
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = "esquire-admissibility/1"

PASS = "PASS"
GAP = "GAP"
UNVERIFIABLE = "UNVERIFIABLE"

VERDICT_READY = "READY"
VERDICT_GAPS = "GAPS"
VERDICT_INCOMPLETE = "INCOMPLETE"
VERDICT_BLIND = "BLIND"

EXIT_READY = 0
EXIT_GAPS = 1
EXIT_BLIND = 2

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

# A citation is only load-bearing if something was actually read. "recalled",
# "model_generated", "unverified" and "fabricated" all land in G4 as gaps.
CITATION_VERIFIED = frozenset({"fetched", "primary_read"})
CITATION_DISQUALIFIED = frozenset({"fabricated", "hallucinated", "invented"})

HEARSAY_POSTURES = frozenset(
    {"not_offered_for_truth", "offered_for_truth_exception", "machine_record"}
)

DISCLAIMER = (
    "This instrument reports whether a proffer record carries what each "
    "admissibility gate requires. It is not a ruling: admissibility is decided "
    "by a court, and no output of this tool may be pleaded as a determination."
)

GATE_METADATA: tuple[dict[str, str], ...] = (
    {
        "id": "G1",
        "title": "Qualification and disclosure",
        "authority": "FRE 702 (preamble and (a)); Esquire E-1",
        "tier": "A (rule text read at source)",
        "falsifier": "A rule or decision allowing a machine, unnamed, to testify as "
        "a qualified expert in its own right.",
        "negative_control": "A named expert adopting the output, with qualifications "
        "on the record, must pass.",
    },
    {
        "id": "G2",
        "title": "Sufficient facts or data",
        "authority": "FRE 702(b)",
        "tier": "A",
        "falsifier": "An opinion admitted on inputs that were neither preserved nor "
        "identifiable.",
        "negative_control": "A sparse but fully hashed input set must pass; scarcity "
        "is not insufficiency.",
    },
    {
        "id": "G3",
        "title": "Reliable principles and methods",
        "authority": "FRE 702(c); Daubert v. Merrell Dow, 509 U.S. 579 (1993)",
        "tier": "A for the rule; A for the case, not re-fetched today",
        "falsifier": "A model with no version, no evaluation and no documented "
        "method admitted as reliable.",
        "negative_control": "A novel method with no peer review but a measured error "
        "rate must pass: the Daubert factors are non-exhaustive.",
    },
    {
        "id": "G4",
        "title": "Reliable application and citation integrity",
        "authority": "FRE 702(d); Mata v. Avianca, 678 F. Supp. 3d 443 (S.D.N.Y. 2023)",
        "tier": "A for the rule; C for the case (confirmed to exist, not read at source)",
        "falsifier": "An opinion resting on a citation that does not resolve, "
        "admitted without consequence.",
        "negative_control": "An opinion with no legal citations at all (a valuation, "
        "a measurement) must pass; citation integrity is conditional.",
    },
    {
        "id": "G5",
        "title": "Authentication",
        "authority": "FRE 901(a), 901(b)(9); 902(13), 902(14)",
        "tier": "A (rule text read at source)",
        "falsifier": "Machine output admitted with no hash, no custody and no "
        "certification of the process that produced it.",
        "negative_control": "Output authenticated by a 902(13) certification with "
        "notice must pass without any custody chain.",
    },
    {
        "id": "G6",
        "title": "Hearsay posture",
        "authority": "FRE 801, 803(6), 902(13)",
        "tier": "A",
        "falsifier": "Output offered for its truth with no statement of posture and "
        "no exception identified.",
        "negative_control": "Output offered only to show what the system emitted "
        "(not for truth) must pass.",
    },
    {
        "id": "G7",
        "title": "Human review and candor",
        "authority": "Esquire E-1, E-5; ABA Formal Opinion 512 (2024)",
        "tier": "B for the conduct rule (not re-fetched today)",
        "falsifier": "A reviewer with no power to alter the output treated as "
        "satisfying a human-review requirement.",
        "negative_control": "A reviewer who changed nothing but held authority must "
        "pass; the absence of changes is a cross-examination fact, not a defect.",
    },
)


@dataclass
class Finding:
    """One gate's reading of the record."""

    gate: str
    state: str
    detail: str
    notes: list[str] = field(default_factory=list)


def _get(obj: Any, *path: str, default: Any = None) -> Any:
    """Walk nested mappings without raising on a missing or wrongly typed key."""
    cur = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _strings(value: Any) -> list[str]:
    """Return the non-empty strings from a list, ignoring any other element."""
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.match(value.strip().lower()))


def _cert_902_13(record: dict[str, Any]) -> dict[str, Any] | None:
    """Return the 902(13) certification if it is complete, else None."""
    cert = _get(record, "authentication", "certification_902_13")
    if not isinstance(cert, dict):
        return None
    if not _text(cert.get("certifier")):
        return None
    if cert.get("qualified") is not True:
        return None
    if cert.get("notice_given") is not True:
        return None
    return cert


def gate_1_qualification(record: dict[str, Any]) -> Finding:
    """G1: a named natural person, qualified and on the record."""
    witness = record.get("witness")
    if not isinstance(witness, dict):
        return Finding("G1", UNVERIFIABLE, "no witness is identified in the record")

    problems: list[str] = []
    if _text(witness.get("kind")).lower() != "human":
        problems.append("the witness is not identified as a natural person")
    if not _text(witness.get("name")):
        problems.append("the witness is unnamed")
    if not _strings(witness.get("qualifications")):
        problems.append("no qualifications are stated")
    if witness.get("reviewed_output") is not True:
        problems.append("the witness has not reviewed the output")

    if problems:
        return Finding("G1", GAP, "; ".join(problems))
    return Finding("G1", PASS, "named human witness, qualified and reviewing")


def gate_2_inputs(record: dict[str, Any]) -> Finding:
    """G2: inputs preserved, identified, and hashed."""
    inputs = record.get("inputs")
    if not isinstance(inputs, dict):
        return Finding("G2", UNVERIFIABLE, "the record does not describe its inputs")

    records = inputs.get("records")
    if not isinstance(records, list) or not records:
        return Finding("G2", UNVERIFIABLE, "no input records are listed")

    problems: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            problems.append(f"input {index} is not an object")
            continue
        ident = _text(item.get("id"))
        if not ident:
            problems.append(f"input {index} has no id")
        elif ident in seen:
            problems.append(f"input id {ident!r} is duplicated")
        else:
            seen.add(ident)
        if not _text(item.get("source")):
            problems.append(f"input {index} has no source")
        if not _is_sha256(item.get("sha256")):
            problems.append(f"input {index} has no valid sha256")

    if not _text(inputs.get("sufficiency_statement")):
        problems.append("no statement of why the inputs are sufficient")

    if problems:
        return Finding("G2", GAP, "; ".join(problems[:4]))
    return Finding("G2", PASS, f"{len(records)} hashed input record(s), sufficiency stated")


def gate_3_method(record: dict[str, Any]) -> Finding:
    """G3: a versioned, evaluated method. Factors are reported, not required."""
    method = record.get("method")
    if not isinstance(method, dict):
        return Finding("G3", UNVERIFIABLE, "the record does not describe the method")

    problems: list[str] = []
    for key in ("name", "version", "provenance"):
        if not _text(_get(method, "model", key, default="")):
            problems.append(f"model {key} is not stated")

    evaluation = method.get("evaluation")
    if not isinstance(evaluation, dict):
        problems.append("no evaluation is reported")
    else:
        rate = evaluation.get("error_rate")
        if isinstance(rate, bool) or not isinstance(rate, (int, float)):
            problems.append("no numeric error rate")
        elif not 0.0 <= float(rate) <= 1.0:
            problems.append("the error rate is outside 0..1")
        if not _text(evaluation.get("test_set")):
            problems.append("the evaluation does not name its test set")

    notes: list[str] = []
    peer = method.get("peer_review")
    if peer is False:
        notes.append("no peer review: a Daubert factor a court may weigh, not a defect")
    acceptance = _text(method.get("general_acceptance")).lower()
    if acceptance in {"novel", "contested"}:
        notes.append(f"general acceptance is {acceptance}: a factor, not a defect")

    if problems:
        return Finding("G3", GAP, "; ".join(problems[:4]), notes)
    return Finding("G3", PASS, "versioned, evaluated method with a measured error rate", notes)


def gate_4_application(record: dict[str, Any]) -> Finding:
    """G4: claims tied to inputs; every citation either verified or a gap."""
    claims = record.get("claims")
    if not isinstance(claims, list) or not claims:
        return Finding("G4", UNVERIFIABLE, "no claims are stated")

    known_inputs = {
        _text(item.get("id"))
        for item in _get(record, "inputs", "records", default=[]) or []
        if isinstance(item, dict) and _text(item.get("id"))
    }

    problems: list[str] = []
    citation_count = 0
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            problems.append(f"claim {index} is not an object")
            continue
        label = _text(claim.get("id")) or f"claim {index}"
        if not _text(claim.get("text")):
            problems.append(f"{label} has no text")
        linked = _strings(claim.get("inputs"))
        if not linked:
            problems.append(f"{label} is not tied to any input")
        for ident in linked:
            if ident not in known_inputs:
                problems.append(f"{label} cites unknown input {ident!r}")

        citations = claim.get("citations")
        if citations is None:
            continue
        if not isinstance(citations, list):
            problems.append(f"{label} citations are not a list")
            continue
        for citation in citations:
            citation_count += 1
            if not isinstance(citation, dict):
                problems.append(f"{label} has a citation that is not an object")
                continue
            locator = _text(citation.get("locator")) or "an unnamed citation"
            if not _text(citation.get("locator")):
                problems.append(f"{label} has a citation with no locator")
            state = _text(citation.get("verification")).lower()
            if state in CITATION_DISQUALIFIED:
                problems.append(
                    f"{locator} is marked {state}: a fabricated authority cannot "
                    "carry an opinion (Mata v. Avianca)"
                )
            elif state not in CITATION_VERIFIED:
                problems.append(
                    f"{locator} is {state or 'unmarked'}: no fetched or "
                    "primary-read verification is recorded"
                )

    if problems:
        return Finding("G4", GAP, "; ".join(problems[:4]))
    detail = f"{len(claims)} claim(s) tied to inputs"
    if citation_count:
        detail += f", {citation_count} citation(s) verified"
    return Finding("G4", PASS, detail)


def gate_5_authentication(record: dict[str, Any]) -> Finding:
    """G5: the output is identified, and its provenance is certified or held."""
    auth = record.get("authentication")
    if not isinstance(auth, dict):
        return Finding(
            "G5", UNVERIFIABLE, "the record does not authenticate the machine output"
        )

    problems: list[str] = []
    if not _is_sha256(auth.get("output_sha256")):
        problems.append("the output has no valid sha256")

    custody = _strings(auth.get("custody"))
    cert = _cert_902_13(record)
    if not custody and cert is None:
        problems.append(
            "neither a custody chain nor a complete 902(13) certification is present"
        )
        incomplete = auth.get("certification_902_13")
        if isinstance(incomplete, dict):
            for key in ("certifier", "qualified", "notice_given"):
                if not incomplete.get(key):
                    problems.append(f"the 902(13) certification lacks {key}")

    if problems:
        return Finding("G5", GAP, "; ".join(problems[:4]))

    if cert is not None:
        return Finding("G5", PASS, "output hashed and certified under FRE 902(13)")
    return Finding("G5", PASS, f"output hashed with a {len(custody)}-step custody chain")


def gate_6_hearsay(record: dict[str, Any]) -> Finding:
    """G6: the record says what the output is offered to prove."""
    hearsay = record.get("hearsay")
    if not isinstance(hearsay, dict):
        return Finding("G6", UNVERIFIABLE, "no hearsay posture is stated")

    posture = _text(hearsay.get("posture")).lower()
    if posture not in HEARSAY_POSTURES:
        return Finding(
            "G6",
            GAP,
            f"posture {posture!r} is not one of {sorted(HEARSAY_POSTURES)}",
        )

    if posture == "not_offered_for_truth":
        return Finding("G6", PASS, "offered for a non-truth purpose")

    if posture == "offered_for_truth_exception":
        problems = []
        if not _text(hearsay.get("exception")):
            problems.append("no exception is identified")
        if hearsay.get("notice_given") is not True:
            problems.append("no notice of the exception is recorded")
        if problems:
            return Finding("G6", GAP, "; ".join(problems))
        return Finding("G6", PASS, f"exception stated: {_text(hearsay.get('exception'))}")

    business = hearsay.get("business_records")
    complete_business = isinstance(business, dict) and bool(
        _text(business.get("custodian"))
    ) and business.get("regular_practice") is True
    if _cert_902_13(record) is not None or complete_business:
        return Finding("G6", PASS, "machine record with a qualifying predicate")
    return Finding(
        "G6",
        GAP,
        "machine record without a 902(13) certification or business-records predicate",
    )


def gate_7_review(record: dict[str, Any]) -> Finding:
    """G7: disclosure, and a reviewer with authority to change the output."""
    proffer = record.get("proffer")
    review = record.get("review")
    problems: list[str] = []
    notes: list[str] = []

    if isinstance(proffer, dict) and proffer.get("ai_assistance_disclosed") is not True:
        problems.append("AI assistance is not disclosed")

    if not isinstance(review, dict):
        if problems:
            return Finding("G7", GAP, "; ".join(problems))
        return Finding("G7", UNVERIFIABLE, "no human review is recorded")

    if not _text(review.get("name")):
        problems.append("the reviewer is unnamed")
    if review.get("authority_to_change") is not True:
        problems.append("the reviewer had no authority to change the output")
    if not _text(review.get("recorded_at")):
        problems.append("the review is undated")

    changes = review.get("changes_made")
    if isinstance(changes, int) and not isinstance(changes, bool) and changes == 0:
        notes.append(
            "the reviewer changed nothing while holding authority: a fact for "
            "cross-examination, not a defect in the record"
        )

    if problems:
        return Finding("G7", GAP, "; ".join(problems[:4]), notes)
    return Finding("G7", PASS, "disclosed, reviewed by an authorised named human", notes)


GATES = (
    gate_1_qualification,
    gate_2_inputs,
    gate_3_method,
    gate_4_application,
    gate_5_authentication,
    gate_6_hearsay,
    gate_7_review,
)


def canonical(record: Any) -> str:
    """Stable serialisation, so the record hash does not depend on key order."""
    return json.dumps(record, sort_keys=True, separators=(",", ":"), default=str)


def record_sha256(record: Any) -> str:
    return hashlib.sha256(canonical(record).encode("utf-8")).hexdigest()


def evaluate(record: Any) -> dict[str, Any]:
    """Read a proffer record and return a report. Never raises on bad input."""
    if not isinstance(record, dict) or not isinstance(record.get("proffer"), dict):
        return {
            "schema": SCHEMA_VERSION,
            "verdict": VERDICT_BLIND,
            "reason": "the record is not an object with a 'proffer' section",
            "gates": [],
            "counts": {PASS: 0, GAP: 0, UNVERIFIABLE: 0},
            "disclaimer": DISCLAIMER,
        }

    findings = [gate(record) for gate in GATES]
    counts = {PASS: 0, GAP: 0, UNVERIFIABLE: 0}
    for finding in findings:
        counts[finding.state] += 1

    if counts[GAP]:
        verdict = VERDICT_GAPS
    elif counts[UNVERIFIABLE]:
        verdict = VERDICT_INCOMPLETE
    else:
        verdict = VERDICT_READY

    return {
        "schema": SCHEMA_VERSION,
        "verdict": verdict,
        "case": _text(_get(record, "proffer", "case")),
        "record_sha256": record_sha256(record),
        "gates": [
            {
                "gate": finding.gate,
                "state": finding.state,
                "detail": finding.detail,
                "notes": finding.notes,
            }
            for finding in findings
        ],
        "counts": counts,
        "disclaimer": DISCLAIMER,
    }


def render(report: dict[str, Any]) -> str:
    """One screen: verdict, then one line per gate, then notes."""
    verdict = report["verdict"]
    lines = [f"ESQUIRE-ADMISSIBILITY-v1  {verdict}"]
    case = report.get("case")
    if case:
        lines.append(f"case: {case}")
    if verdict == VERDICT_BLIND:
        lines.append(f"reason: {report.get('reason', 'unreadable record')}")
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    counts = report["counts"]
    lines.append(
        f"gates: {counts[PASS]} pass, {counts[GAP]} gap, "
        f"{counts[UNVERIFIABLE]} unaddressed"
    )
    lines.append("")
    for gate in report["gates"]:
        lines.append(f"{gate['gate']}  {gate['state']:<12} {gate['detail']}")
        for note in gate["notes"]:
            lines.append(f"                          note: {note}")
    lines.append("")
    lines.append(f"record sha256: {report['record_sha256']}")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def render_gates() -> str:
    """The gate table, for audit and for the document that cites it."""
    lines = ["ESQUIRE-ADMISSIBILITY-v1 gate table", ""]
    for meta in GATE_METADATA:
        lines.append(f"{meta['id']}  {meta['title']}")
        lines.append(f"    authority:        {meta['authority']}")
        lines.append(f"    evidence tier:    {meta['tier']}")
        lines.append(f"    falsifier:        {meta['falsifier']}")
        lines.append(f"    negative control: {meta['negative_control']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def load_record(path: str) -> Any:
    """Read JSON from a path, or from stdin for '-'."""
    if path == "-":
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Test a proffer record against the Esquire admissibility gates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes: 0 READY, 1 GAPS or INCOMPLETE, 2 BLIND.\n"
            "This instrument never reports a record as admissible or inadmissible."
        ),
    )
    parser.add_argument("record", nargs="?", help="proffer JSON path, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="emit the report as JSON")
    parser.add_argument(
        "--gates", action="store_true", help="print the gate table and exit"
    )
    args = parser.parse_args(argv)

    if args.gates:
        print(render_gates())
        return EXIT_READY

    if not args.record:
        parser.error("a record path is required unless --gates is used")

    try:
        record = load_record(args.record)
    except (OSError, json.JSONDecodeError) as error:
        report = {
            "schema": SCHEMA_VERSION,
            "verdict": VERDICT_BLIND,
            "reason": f"{type(error).__name__}: {error}",
            "gates": [],
            "counts": {PASS: 0, GAP: 0, UNVERIFIABLE: 0},
            "disclaimer": DISCLAIMER,
        }
        print(json.dumps(report, indent=2) if args.json else render(report))
        return EXIT_BLIND

    report = evaluate(record)
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else render(report))

    if report["verdict"] == VERDICT_BLIND:
        return EXIT_BLIND
    if report["verdict"] == VERDICT_READY:
        return EXIT_READY
    return EXIT_GAPS


if __name__ == "__main__":
    raise SystemExit(main())
