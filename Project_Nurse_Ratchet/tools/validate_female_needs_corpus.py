#!/usr/bin/env python3
"""Validate the female-needs hyper-edge corpus.

Why this exists
---------------
The corpus records what published sources say about what women in (and returning
from) behavioural-health and justice systems need. Its value is entirely in its
gates: a claim that lost its denominator, or that got labelled VERIFIED off a
tier-C review, is worse than no claim at all, because it reads as settled.

Four defects were found by hand on 2026-11-16, in a file this author had just
written, using the checks below:

  * _meta.counts said edges=20 / sources=15 / verified=17 / lead=3 against a file
    holding 22 / 18 / 13 / 9. A hand-typed count block always drifts.
  * E-MOTHER-02 was VERIFIED on the reasoning "its own denominator is stated".
    A denominator makes a figure checkable; it does not raise a secondary
    synthesis to tier A or B. The corpus' own states rule caps VERIFIED at A/B.
  * E-MOTHER-03 named S-NIJ-EMPLOY in `quorum` as a corroborator. The cited NIJ
    line is about transport and childcare, not stigma. The corroboration was
    asserted in prose and absent from the evidence.
  * E-VOICE-02 named S-URBAN-TRAUMA as corroborating a WRNA claim. That source's
    quoted line counts DOCs using "a risk assessment tool that is either gender
    responsive and/or assesses for past trauma" and never names WRNA.

The lesson was not "fix four edges"; it was that each of those four is
mechanically detectable. So they are checks now.

Read-only by design
-------------------
There is deliberately no --write-counts. A validator that can rewrite the file
it is judging can launder a defect into a pass. When counts disagree, the error
prints the exact block to paste.

Exit codes
----------
  0  every check passed
  1  at least one check failed (findings printed with edge id and reason)
  2  the run could not be performed (missing file, bad JSON) -- never a pass

Usage
-----
  python tools/validate_female_needs_corpus.py
  python tools/validate_female_needs_corpus.py --corpus <path>
  python tools/validate_female_needs_corpus.py --self-test
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = REPO_ROOT / "src" / "PSYCHE" / "data" / "female_needs_hyperedges.json"

TIERS = ("A", "B", "C", "D")
STATES = ("VERIFIED", "LEAD", "BLIND", "CUT")
CLAIM_TYPES = ("guidance", "prevalence", "policy", "qualitative")
MIN_QUOTE_CHARS = 15
SOURCE_ID_RE = re.compile(r"S-[A-Z0-9]+(?:-[A-Z0-9]+)*")


class Findings:
    """Collects failures so one pass reports every problem, not just the first."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks_run: set[str] = set()

    def check(self, name: str) -> None:
        self.checks_run.add(name)

    def fail(self, name: str, where: str, reason: str) -> None:
        self.check(name)
        self.errors.append(f"[{name}] {where}: {reason}")

    def ok(self) -> bool:
        return not self.errors


def load_corpus(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_edges(doc: dict):
    for need in doc.get("needs", []):
        for edge in need.get("edges", []):
            yield need, edge


def sources_named(text: str) -> list[str]:
    """Every S-* identifier mentioned in a free-text field, in order, deduped."""
    seen: list[str] = []
    for match in SOURCE_ID_RE.findall(text or ""):
        if match not in seen:
            seen.append(match)
    return seen


def cited_sources(edge: dict) -> list[str]:
    ground = edge.get("ground") or {}
    raw = ground.get("source_id") or ""
    return [part for part in raw.split("+") if part]


def validate(doc: dict) -> Findings:
    f = Findings()

    # ---- root shape -------------------------------------------------------
    f.check("root_keys")
    for key in ("_meta", "sources", "needs", "answer"):
        if key not in doc:
            f.fail("root_keys", "root", f"missing required key {key!r}")
    if not f.ok():
        return f  # nothing below can be trusted without the root shape

    sources: dict = doc["sources"]
    needs: list = doc["needs"]
    answer: dict = doc["answer"]

    # ---- sources ----------------------------------------------------------
    for sid, record in sources.items():
        f.check("source_record")
        if not isinstance(record, dict):
            f.fail("source_record", sid, "source is not an object")
            continue
        for key in ("publisher", "title", "url", "tier", "kind"):
            if not str(record.get(key) or "").strip():
                f.fail("source_record", sid, f"empty or missing {key!r}")
        if record.get("tier") not in TIERS:
            f.fail("source_record", sid, f"tier {record.get('tier')!r} not one of {TIERS}")
        if not str(record.get("url") or "").startswith("http"):
            f.fail("source_record", sid, f"url is not http(s): {record.get('url')!r}")

    # ---- needs + edges ----------------------------------------------------
    seen_edge_ids: set[str] = set()
    derived = {"needs": len(needs), "edges": 0, "verified": 0, "lead": 0,
               "blind": 0, "cut": 0, "sources": len(sources)}

    for need in needs:
        need_id = need.get("need_id")
        label = need_id or "<no need_id>"
        f.check("need_shape")
        for key in ("need_id", "label", "domain", "module"):
            if key not in need:
                f.fail("need_shape", label, f"missing {key!r}")

        module = need.get("module") or {}
        f.check("need_module")
        if len(module.get("objectives") or []) < 2:
            f.fail("need_module", label, "fewer than 2 learning objectives")
        if not str(module.get("misconception") or "").strip():
            f.fail("need_module", label, "no named misconception (the educational payload)")

        edges = need.get("edges") or []
        f.check("need_has_edges")
        if not edges:
            f.fail("need_has_edges", label, "need carries zero edges")
        derived["edges"] += len(edges)

        for edge in edges:
            eid = edge.get("edge_id") or "<no edge_id>"
            f.check("edge_id_unique")
            if eid in seen_edge_ids:
                f.fail("edge_id_unique", eid, "duplicate edge_id")
            seen_edge_ids.add(eid)

            f.check("edge_shape")
            for key in ("edge_id", "nodes", "claim_type", "claim", "intervention",
                        "tier", "state", "ground", "denominator", "universe",
                        "quorum", "blind", "trunc", "provenance"):
                if key not in edge:
                    f.fail("edge_shape", eid, f"missing {key!r}")
            if not str(edge.get("claim") or "").strip():
                f.fail("edge_shape", eid, "empty claim")
            if not str(edge.get("provenance") or "").strip():
                f.fail("edge_shape", eid, "empty provenance (a claim with no retrieval trail)")

            # state / claim_type vocabulary
            if edge.get("state") not in STATES:
                f.fail("state_vocab", eid, f"state {edge.get('state')!r} not one of {STATES}")
            if edge.get("claim_type") not in CLAIM_TYPES:
                f.fail("claim_type_vocab", eid,
                       f"claim_type {edge.get('claim_type')!r} not one of {CLAIM_TYPES}")

            state = edge.get("state")
            if state == "VERIFIED":
                derived["verified"] += 1
            elif state == "LEAD":
                derived["lead"] += 1
            elif state == "BLIND":
                derived["blind"] += 1
            elif state == "CUT":
                derived["cut"] += 1

            # hyper-edge must actually touch its own need
            f.check("edge_nodes")
            nodes = edge.get("nodes") or []
            if len(nodes) < 3:
                f.fail("edge_nodes", eid, f"hyper-edge has {len(nodes)} nodes, needs 3")
            if need_id and f"NEED:{need_id}" not in nodes:
                f.fail("edge_nodes", eid, f"nodes do not include NEED:{need_id}")
            if not any(str(n).startswith("POP:") for n in nodes):
                f.fail("edge_nodes", eid, "no POP: node")
            if not any(str(n).startswith("LEVER:") for n in nodes):
                f.fail("edge_nodes", eid, "no LEVER: node")

            # ---- GROUND: a quote, from a resolvable source ----------------
            ground = edge.get("ground") or {}
            quote = str(ground.get("quote") or "").strip()
            f.check("ground_quote")
            if len(quote) < MIN_QUOTE_CHARS:
                f.fail("ground_quote", eid,
                       f"quote is {len(quote)} chars, minimum {MIN_QUOTE_CHARS}")

            f.check("ground_source")
            cited = cited_sources(edge)
            if not cited:
                f.fail("ground_source", eid, "ground.source_id is empty")
            for sid in cited:
                if sid not in sources:
                    f.fail("ground_source", eid, f"source_id {sid!r} is not in sources")

            # ---- CORROBORATION: a named second source carries its own line -
            f.check("corroboration")
            corroboration = edge.get("corroboration")
            corroborated: list[str] = []
            if corroboration is not None:
                if not isinstance(corroboration, dict):
                    f.fail("corroboration", eid, "corroboration is not an object")
                else:
                    csid = str(corroboration.get("source_id") or "")
                    cquote = str(corroboration.get("quote") or "").strip()
                    if csid not in sources:
                        f.fail("corroboration", eid,
                               f"corroboration source {csid!r} is not in sources")
                    else:
                        corroborated.append(csid)
                    if len(cquote) < MIN_QUOTE_CHARS:
                        f.fail("corroboration", eid,
                               "corroboration carries no transcribed line")
                    if csid and csid in cited:
                        f.fail("corroboration", eid,
                               f"{csid} is cited as both the ground source and its own "
                               "corroborator -- a source cannot corroborate itself")

            # ---- TIER: never better than the weakest source cited --------
            f.check("tier_vs_source")
            cite_tiers = [sources[s]["tier"] for s in cited if s in sources]
            if cite_tiers:
                weakest = max(cite_tiers)  # C is weaker than A in this vocabulary
                if edge.get("tier") not in TIERS:
                    f.fail("tier_vs_source", eid, f"tier {edge.get('tier')!r} invalid")
                elif TIERS.index(edge["tier"]) < TIERS.index(weakest):
                    f.fail("tier_vs_source", eid,
                           f"edge tier {edge['tier']} is stronger than its weakest source "
                           f"({weakest}); a claim may be weaker than its source, never stronger")

            # ---- VERIFIED is capped at A/B -------------------------------
            f.check("verified_needs_tier_ab")
            if state == "VERIFIED" and edge.get("tier") not in ("A", "B"):
                f.fail("verified_needs_tier_ab", eid,
                       f"state VERIFIED on tier {edge.get('tier')}; the states rule caps "
                       "VERIFIED at tier A or B (a stated denominator does not lift a "
                       "secondary synthesis)")

            # ---- DENOM: prevalence claims carry a countable denominator ---
            f.check("denominator")
            denom = str(edge.get("denominator") or "").strip()
            if edge.get("claim_type") == "prevalence":
                if not denom:
                    f.fail("denominator", eid, "prevalence claim with no denominator")
                elif denom.lower().startswith("n/a"):
                    f.fail("denominator", eid,
                           f"prevalence claim excused from a denominator: {denom!r}")
                elif not re.search(r"\d", denom):
                    f.fail("denominator", eid,
                           f"denominator carries no figure: {denom!r}")
            elif not denom:
                f.fail("denominator", eid, "denominator is empty (write 'n/a - <why>')")

            # ---- UNIVERSE: whose population the claim is about -----------
            f.check("universe")
            if not str(edge.get("universe") or "").strip():
                f.fail("universe", eid, "no universe named")

            # ---- QUORUM: a named corroborator must be in the evidence ----
            f.check("quorum_sources")
            named = sources_named(str(edge.get("quorum") or ""))
            evidenced = cited + corroborated
            for sid in named:
                if sid not in evidenced:
                    f.fail("quorum_sources", eid,
                           f"quorum names {sid} as a corroborator but ground.source_id "
                           f"cites only {cited or 'nothing'} -- corroboration asserted "
                           "in prose is not evidence in the file")

            # ---- BLIND/TRUNC must be declared, not implied ---------------
            f.check("blind_trunc")
            for flag in ("blind", "trunc"):
                if not isinstance(edge.get(flag), bool):
                    f.fail("blind_trunc", eid, f"{flag} is not a boolean")
            if state == "BLIND" and not edge.get("blind"):
                f.fail("blind_trunc", eid, "state BLIND but blind=false")
            if state in ("VERIFIED", "LEAD") and edge.get("blind") and not edge.get("trunc"):
                # blind-but-not-trunc is allowed only when the source was retrieved
                pass

    # ---- ANSWER: the ranked answer must cover the needs -------------------
    f.check("answer_ranked")
    ranked = answer.get("ranked") or []
    ranked_ids = [item.get("need") for item in ranked]
    need_ids = [need.get("need_id") for need in needs]
    if sorted(ranked_ids) != sorted(need_ids):
        missing = [n for n in need_ids if n not in ranked_ids]
        extra = [n for n in ranked_ids if n not in need_ids]
        f.fail("answer_ranked", "answer.ranked",
               f"does not match needs (missing={missing}, extra={extra}, "
               f"duplicates={[n for n in ranked_ids if ranked_ids.count(n) > 1]})")
    ranks = [item.get("rank") for item in ranked]
    if ranks and sorted(ranks) != list(range(1, len(ranked) + 1)):
        f.fail("answer_ranked", "answer.ranked", f"ranks are not 1..{len(ranked)}: {ranks}")
    for item in ranked:
        if not str(item.get("why") or "").strip():
            f.fail("answer_ranked", f"rank {item.get('rank')}", "no reason given")
    f.check("answer_order_note")
    if not str(answer.get("ordering_note") or "").strip():
        f.fail("answer_order_note", "answer",
               "no ordering_note; a rank without a stated basis reads as a measurement")

    # ---- COUNTS: derived, then compared -----------------------------------
    f.check("counts_derived")
    declared = (doc.get("_meta") or {}).get("counts") or {}
    for key, value in derived.items():
        if declared.get(key) != value:
            f.fail("counts_derived", "_meta.counts",
                   f"{key}: declared {declared.get(key)!r}, actual {value!r}")
    unknown = sorted(set(declared) - set(derived))
    if unknown:
        f.fail("counts_derived", "_meta.counts", f"unknown count keys {unknown}")

    return f


# ---------------------------------------------------------------------------
# self-test: every mutation below MUST be caught
# ---------------------------------------------------------------------------

def _mut_strip_prevalence_denominator(doc: dict) -> str:
    for _need, edge in iter_edges(doc):
        if edge.get("claim_type") == "prevalence":
            edge["denominator"] = ""
            return edge["edge_id"]
    raise AssertionError("no prevalence edge to mutate")


def _mut_upgrade_c_tier_to_verified(doc: dict) -> str:
    for _need, edge in iter_edges(doc):
        if edge.get("tier") == "C":
            edge["state"] = "VERIFIED"
            return edge["edge_id"]
    raise AssertionError("no tier-C edge to mutate")


def _mut_blank_quote(doc: dict) -> str:
    for _need, edge in iter_edges(doc):
        edge["ground"]["quote"] = "   "
        return edge["edge_id"]
    raise AssertionError("no edge to mutate")


def _mut_uncited_corroborator(doc: dict) -> str:
    for _need, edge in iter_edges(doc):
        edge["quorum"] = "corroborated by S-CCJ-2024"
        corrob = (edge.get("corroboration") or {}).get("source_id")
        if "S-CCJ-2024" not in cited_sources(edge) and corrob != "S-CCJ-2024":
            return edge["edge_id"]
    raise AssertionError("no edge without S-CCJ-2024 to mutate")


def _mut_wrong_counts(doc: dict) -> str:
    doc["_meta"]["counts"]["edges"] += 1
    return "_meta.counts"


def _mut_ranked_drops_a_need(doc: dict) -> str:
    doc["answer"]["ranked"].pop()
    return "answer.ranked"


MUTATORS = [
    ("prevalence claim with its denominator stripped", _mut_strip_prevalence_denominator),
    ("tier-C edge relabelled VERIFIED", _mut_upgrade_c_tier_to_verified),
    ("ground quote blanked", _mut_blank_quote),
    ("corroborator named in quorum but absent from evidence", _mut_uncited_corroborator),
    ("count block off by one", _mut_wrong_counts),
    ("ranked answer silently drops a need", _mut_ranked_drops_a_need),
]


def self_test(doc: dict) -> int:
    print("self-test: the unmutated corpus must pass")
    baseline = validate(copy.deepcopy(doc))
    if not baseline.ok():
        print("  FAIL - the corpus itself is invalid, so no mutation result would mean anything")
        for error in baseline.errors:
            print("    " + error)
        return 1
    print(f"  PASS - {len(baseline.checks_run)} checks ran clean")

    print("\nself-test: every mutation must be caught")
    blind = 0
    for label, mutator in MUTATORS:
        mutated = copy.deepcopy(doc)
        target = mutator(mutated)
        result = validate(mutated)
        if result.ok():
            blind += 1
            print(f"  BLIND - {label} ({target}) passed validation")
        else:
            print(f"  caught - {label} ({target}): {result.errors[0]}")

    if blind:
        print(f"\nself-test FAILED: {blind} mutation(s) went undetected")
        return 1
    print(f"\nself-test PASSED: {len(MUTATORS)}/{len(MUTATORS)} mutations caught")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--self-test", action="store_true",
                        help="prove the validator catches the defects it exists for")
    parser.add_argument("--quiet", action="store_true", help="print only failures")
    args = parser.parse_args(argv)

    try:
        doc = load_corpus(args.corpus)
    except FileNotFoundError:
        print(f"CANNOT RUN: corpus not found at {args.corpus}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"CANNOT RUN: corpus is not valid JSON: {exc}", file=sys.stderr)
        return 2

    if args.self_test:
        return self_test(doc)

    findings = validate(doc)

    derived = {"needs": len(doc.get("needs", [])),
               "edges": sum(len(n.get("edges", [])) for n in doc.get("needs", [])),
               "sources": len(doc.get("sources", {}))}
    for need in doc.get("needs", []):
        for edge in need.get("edges", []):
            if edge.get("state") == "VERIFIED":
                derived["verified"] = derived.get("verified", 0) + 1
            elif edge.get("state") == "LEAD":
                derived["lead"] = derived.get("lead", 0) + 1

    if not args.quiet:
        print(f"corpus: {args.corpus}")
        print(f"  needs={derived['needs']} edges={derived['edges']} "
              f"sources={derived['sources']} "
              f"verified={derived.get('verified', 0)} lead={derived.get('lead', 0)}")
        print(f"  checks run: {len(findings.checks_run)}")

    if findings.errors:
        print(f"\nFAIL - {len(findings.errors)} finding(s):")
        for error in findings.errors:
            print("  " + error)
        if any(e.startswith("[counts_derived]") for e in findings.errors):
            print("\n  paste this block into _meta.counts (derived, do not hand-adjust):")
            print("    " + json.dumps(derived, indent=2).replace("\n", "\n    "))
        return 1

    if not args.quiet:
        print(f"\nPASS - {len(findings.checks_run)} checks, 0 findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
