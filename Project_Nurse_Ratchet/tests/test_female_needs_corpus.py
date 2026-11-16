# coding: utf-8
"""Female-needs corpus: the gates must be able to PASS and to FAIL.

The corpus (src/PSYCHE/data/female_needs_hyperedges.json) answers one question --
what do women in, and returning from, behavioural-health and justice systems need --
and its whole value is in the gates attached to each edge. A validator that only
ever reports PASS is decoration, so these tests pin both directions:

  POSITIVE control -- the shipped corpus validates clean.
  NEGATIVE controls -- each named corruption of it is rejected. If a corruption
                       ever passes, the instrument is broken and every clean
                       reading it prints is meaningless.

Three of these corruptions are not hypothetical. They were live in the first draft
of this corpus, written 2026-11-16, and were found by hand before these checks
existed:

  * _meta.counts said edges=20 / sources=15 / verified=17 / lead=3 against a file
    holding 22 / 18 / 13 / 9.
  * E-MOTHER-02 was VERIFIED on the reasoning "its own denominator is stated" --
    a denominator makes a figure checkable, it does not lift a tier-C synthesis.
  * E-MOTHER-03 and E-VOICE-02 named corroborators in `quorum` that their quoted
    evidence did not support. E-VOICE-02's was the sharper case: the named source
    counts state DOCs using a gender-responsive tool and never names WRNA.

Those three edges are pinned below so they cannot quietly be upgraded again.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_female_needs_corpus as V

# The corpus has two homes: the source tree (src/PSYCHE/data) and the published tree
# that tools/publicize.py materialises (nurse_ratchet/psyche/data). Publicize rewrites
# package names, not path strings, so the test resolves both -- otherwise the shipped
# test passes here and fails on the published artifact, after the push.
CORPUS = next(
    p for p in (
        ROOT / "src" / "PSYCHE" / "data" / "female_needs_hyperedges.json",
        ROOT / "nurse_ratchet" / "psyche" / "data" / "female_needs_hyperedges.json",
    )
    if p.is_file()
)


@pytest.fixture(scope="module")
def corpus():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def edges(doc):
    for need in doc["needs"]:
        for edge in need["edges"]:
            yield edge


def find(doc, edge_id):
    for edge in edges(doc):
        if edge["edge_id"] == edge_id:
            return edge
    raise AssertionError(f"{edge_id} not in corpus")


# --------------------------------------------------------------------------
# positive control
# --------------------------------------------------------------------------

def test_shipped_corpus_passes_every_gate(corpus):
    findings = V.validate(corpus)
    assert findings.ok(), "\n".join(findings.errors)
    assert len(findings.checks_run) >= 15  # a run that checks nothing is not a pass


def test_corpus_answers_the_question(corpus):
    """The deliverable is an answer, not a pile of edges."""
    answer = corpus["answer"]
    assert answer["question"].lower().startswith("what do")
    ranked = [item["need"] for item in answer["ranked"]]
    assert sorted(ranked) == sorted(need["need_id"] for need in corpus["needs"])
    assert [item["rank"] for item in answer["ranked"]] == list(range(1, len(ranked) + 1))
    # a rank with no stated basis reads as a measured effect ranking; it is not one
    assert "not" in answer["ordering_note"].lower()


def test_every_need_carries_teaching_material(corpus):
    for need in corpus["needs"]:
        assert len(need["module"]["objectives"]) >= 2, need["need_id"]
        assert need["module"]["misconception"].strip(), need["need_id"]


# --------------------------------------------------------------------------
# negative controls: one per gate
# --------------------------------------------------------------------------

def test_prevalence_claim_without_denominator_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    target = next(e for e in edges(doc) if e["claim_type"] == "prevalence")
    target["denominator"] = ""
    result = V.validate(doc)
    assert not result.ok()
    assert any("denominator" in e for e in result.errors)


def test_prevalence_claim_excused_from_denominator_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    target = next(e for e in edges(doc) if e["claim_type"] == "prevalence")
    target["denominator"] = "n/a - prevalence"
    result = V.validate(doc)
    assert not result.ok()
    assert any("[denominator]" in e for e in result.errors)


def test_tier_c_claim_cannot_be_verified(corpus):
    doc = copy.deepcopy(corpus)
    target = next(e for e in edges(doc) if e["tier"] == "C")
    target["state"] = "VERIFIED"
    result = V.validate(doc)
    assert not result.ok()
    assert any("[verified_needs_tier_ab]" in e for e in result.errors)


def test_claim_cannot_be_stronger_than_its_source(corpus):
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-COOC-02")  # tier C, from a tier-C source
    target["tier"] = "A"
    result = V.validate(doc)
    assert not result.ok()
    assert any("[tier_vs_source]" in e for e in result.errors)


def test_blank_quote_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    next(edges(doc))["ground"]["quote"] = "  "
    result = V.validate(doc)
    assert not result.ok()
    assert any("[ground_quote]" in e for e in result.errors)


def test_unresolvable_source_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    next(edges(doc))["ground"]["source_id"] = "S-DOES-NOT-EXIST"
    result = V.validate(doc)
    assert not result.ok()
    assert any("[ground_source]" in e for e in result.errors)


def test_uncited_corroborator_is_rejected(corpus):
    """Corroboration asserted in prose is not evidence in the file."""
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-SAFETY-01")  # cites S-SAMHSA-TIA only
    target["quorum"] = "corroborated by S-CCJ-2024"
    result = V.validate(doc)
    assert not result.ok()
    assert any("[quorum_sources]" in e for e in result.errors)


def test_corroboration_without_a_quote_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-SAFETY-02")
    target["corroboration"]["quote"] = ""
    result = V.validate(doc)
    assert not result.ok()
    assert any("[corroboration]" in e for e in result.errors)


def test_source_cannot_corroborate_itself(corpus):
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-SAFETY-02")
    target["corroboration"]["source_id"] = target["ground"]["source_id"]
    result = V.validate(doc)
    assert not result.ok()
    assert any("corroborate itself" in e for e in result.errors)


def test_apparatus_declaring_a_removal_still_in_the_quote_is_rejected(corpus):
    """A declaration that names a token the quote still contains describes nothing."""
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-HOUSE-01")
    target["corroboration"]["apparatus"]["removed"].append("conviction")
    result = V.validate(doc)
    assert not result.ok()
    assert any("[corroboration_apparatus]" in e for e in result.errors)


def test_apparatus_with_an_unknown_kind_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-HOUSE-01")
    target["corroboration"]["apparatus"]["kind"] = "footnote-markers"
    result = V.validate(doc)
    assert not result.ok()
    assert any("apparatus.kind" in e for e in result.errors)


def test_apparatus_without_a_note_is_rejected(corpus):
    """An unexplained removal is indistinguishable from a quote edited to fit."""
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-HOUSE-01")
    target["corroboration"].pop("note", None)
    result = V.validate(doc)
    assert not result.ok()
    assert any("no note" in e for e in result.errors)


def test_apparatus_with_an_empty_removal_list_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    target = find(doc, "E-HOUSE-01")
    target["corroboration"]["apparatus"]["removed"] = []
    result = V.validate(doc)
    assert not result.ok()
    assert any("non-empty list" in e for e in result.errors)


def test_hand_typed_counts_that_drift_are_rejected(corpus):
    doc = copy.deepcopy(corpus)
    doc["_meta"]["counts"]["edges"] += 1
    result = V.validate(doc)
    assert not result.ok()
    assert any("[counts_derived]" in e for e in result.errors)


def test_ranked_answer_dropping_a_need_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    doc["answer"]["ranked"].pop()
    result = V.validate(doc)
    assert not result.ok()
    assert any("[answer_ranked]" in e for e in result.errors)


def test_ranked_answer_with_a_gap_in_ranks_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    doc["answer"]["ranked"][0]["rank"] = 99
    result = V.validate(doc)
    assert not result.ok()
    assert any("ranks are not" in e for e in result.errors)


def test_edge_detached_from_its_own_need_is_rejected(corpus):
    doc = copy.deepcopy(corpus)
    next(edges(doc))["nodes"] = ["NEED:N-VOICE", "POP:JUSTICE", "LEVER:X"]
    result = V.validate(doc)
    assert not result.ok()
    assert any("[edge_nodes]" in e for e in result.errors)


# --------------------------------------------------------------------------
# regression pins: the three defects this build caught
# --------------------------------------------------------------------------

def test_denominator_does_not_promote_a_secondary_synthesis(corpus):
    """E-MOTHER-02 stated its denominator; that never made it tier A or B."""
    edge = find(corpus, "E-MOTHER-02")
    assert edge["tier"] == "C"
    assert edge["state"] == "LEAD"
    assert "denominator is stated" not in edge["provenance"], (
        "the false rationale that a stated denominator lifts a C claim was restored"
    )


def test_unquoted_corroboration_stays_downgraded(corpus):
    for edge_id in ("E-MOTHER-03", "E-VOICE-02"):
        edge = find(corpus, edge_id)
        assert edge["state"] == "LEAD", f"{edge_id} was re-upgraded without evidence"
        assert "corroboration" not in edge, (
            f"{edge_id} claims corroboration that its cited line does not support"
        )


def test_wrna_edge_does_not_claim_the_urban_survey_as_support(corpus):
    """The Urban survey counts DOCs using a gender-responsive tool, never WRNA."""
    assert "WRNA" not in find(corpus, "E-SAFETY-03")["ground"]["quote"]
    wrna = find(corpus, "E-VOICE-02")
    assert "S-URBAN-TRAUMA" not in wrna["quorum"], (
        "quorum names a source whose own quoted line does not mention WRNA"
    )


def test_house_corroboration_declares_the_callouts_it_removed(corpus):
    """E-HOUSE-01's quote is contiguous only after two superscript callouts go.

    The validator cannot prove contiguity -- the source text is not in the corpus
    -- so this pins the declaration itself: both tokens, genuinely absent from the
    quoted span, with the reading recorded. Deleting the declaration is the
    regression it guards, and no shape check would notice it.
    """
    corroboration = find(corpus, "E-HOUSE-01")["corroboration"]
    apparatus = corroboration["apparatus"]
    assert apparatus["kind"] == "superscript-callouts"
    assert apparatus["removed"] == ["4,10", "11-14"]
    for token in apparatus["removed"]:
        assert token not in corroboration["quote"], (
            f"{token!r} is declared removed but is still in the quote"
        )
    assert "pdftotext" in corroboration["note"]


def test_voice_quote_carries_the_source_comma_not_an_elision(corpus):
    """The WRNA citation is contiguous: no bracketed elision, the source's comma."""
    quote = find(corpus, "E-VOICE-02")["ground"]["quote"]
    assert "[" not in quote and "]" not in quote
    assert "2010), and is endorsed" in quote


def test_corroborations_that_do_exist_are_quoted(corpus):
    """Where quorum names a second source, that source carries its own line."""
    for edge in edges(corpus):
        named = V.sources_named(edge["quorum"])
        evidenced = V.cited_sources(edge)
        corroboration = edge.get("corroboration") or {}
        if corroboration.get("source_id"):
            evidenced = evidenced + [corroboration["source_id"]]
            assert len(corroboration["quote"].strip()) >= V.MIN_QUOTE_CHARS
        for source_id in named:
            assert source_id in evidenced, f"{edge['edge_id']} names {source_id} but does not cite it"


# --------------------------------------------------------------------------
# the validator's own self-test
# --------------------------------------------------------------------------

def test_validator_self_test_catches_every_mutation(corpus):
    assert V.self_test(corpus) == 0


def test_missing_corpus_is_exit_2_not_a_pass(tmp_path):
    """'Could not run' must never be reported as a clean result."""
    assert V.main(["--corpus", str(tmp_path / "absent.json")]) == 2
