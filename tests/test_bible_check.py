#!/usr/bin/env python3
# coding: utf-8
"""Gate: the canon corpus must be citable, sourced, and capped.

Every test here is a way the text could lie while looking finished:

* a gap in numbering makes "as it is written in Genesis 1:4" unfalsifiable;
* a citation to a verse that does not exist turns a quotation into an invention;
* a figure in a verse with no command behind it is the most quotable possible
  form of a false number;
* a statute with no executable check is a commandment wearing a gate's clothes,
  and a statute whose rule is not in canon makes this file a second source of
  truth;
* no email, phone or forensic deny token, on the same line the disclosure policy
  draws -- methodology ships, people do not;
* a cap the author can raise is not a cap;
* the generations must come from the import graph, so that re-running the command
  is the only way to change them.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import bible_check as B


def _verse(number=1, text="And it was so.", **extra) -> dict:
    verse = {"number": number, "text": text}
    verse.update(extra)
    return verse


def _corpus(*verses_per_chapter, book_id="genesis", genre="etiology", limits=None) -> dict:
    chapters = []
    for index, verses in enumerate(verses_per_chapter, start=1):
        chapters.append({"number": index, "verses": verses})
    data = {
        "schema": B.SCHEMA,
        "title": "Test Canon",
        "status": "seed",
        "updated": "2026-11-01",
        "limits": limits or {"max_books": 12, "max_verses_per_chapter": 60},
        "books": [{"id": book_id, "name": "Genesis", "subtitle": "The Book",
                   "genre": genre, "chapters": chapters}],
    }
    return data


def _raises(data, match, repo=ROOT):
    with pytest.raises(B.CorpusError, match=match):
        B.validate(data, repo)


# -- the corpus in this repository -----------------------------------------

def test_the_shipped_corpus_is_clean():
    data = B.load(B.CORPUS)
    diagnostics = B.validate(data, ROOT)      # must not raise
    assert diagnostics["books"] >= 1


# -- numbering and citation -------------------------------------------------

def test_chapter_numbering_gap_is_refused():
    data = _corpus([_verse(1)])
    data["books"][0]["chapters"].append({"number": 3, "verses": [_verse(1)]})
    _raises(data, "chapter numbering must be contiguous")


def test_verse_numbering_gap_is_refused():
    _raises(_corpus([_verse(2)]), "verse numbering must be contiguous")


def test_dangling_citation_names_the_missing_verse():
    _raises(_corpus([_verse(1, cites=["genesis 1:9"])]),
            "cites genesis 1:9, which does not exist")


def test_citation_to_unknown_book_is_refused():
    _raises(_corpus([_verse(1, cites=["exodus 1:1"])]), "cites unknown book")


def test_forward_citation_resolves():
    data = _corpus([_verse(1, cites=["genesis 1:2"]), _verse(2)])
    B.validate(data, ROOT)          # must not raise


# -- provenance -------------------------------------------------------------

def test_figure_without_a_command_is_refused():
    _raises(_corpus([_verse(1, text="And the recall came back 0.83.")]),
            "a number needs `source`")


def test_source_naming_an_absent_path_is_refused(tmp_path):
    _raises(_corpus([_verse(1, text="It was 0.83.",
                            source="python tools/absent_gate.py")]),
            "source path does not exist here", repo=tmp_path)


def test_source_with_no_path_at_all_is_refused():
    _raises(_corpus([_verse(1, text="It was 0.83.",
                            source="remembered from a session")]),
            "names no repository path")


def test_figure_with_a_real_command_passes():
    data = _corpus([_verse(1, text="The gate passed 3 of 3 times.",
                           source="python tools/bible_check.py --check")])
    B.validate(data, ROOT)          # must not raise


# -- statutes ---------------------------------------------------------------

def test_statute_whose_rule_is_not_in_canon_is_refused():
    _raises(_corpus([_verse(1, statute={"rule": "RULE 99X",
                                       "check": "python tools/bible_check.py"})]),
            "is not in MANDATES.md")


def test_statute_without_a_check_is_refused():
    _raises(_corpus([_verse(1, statute={"rule": "RULE 0B-D", "check": ""})]),
            "a law with nothing executing it is a proverb")


def test_statute_check_that_does_not_exist_is_refused(tmp_path):
    _raises(_corpus([_verse(1, statute={"rule": "RULE 0B-D",
                                       "check": "python tools/absent.py"})]),
            "statute.check does not exist here", repo=tmp_path)


def test_statute_bound_to_canon_and_a_real_check_passes():
    data = _corpus([_verse(1, statute={"rule": "RULE 0B-D",
                                      "check": "python tools/preflight_all.py"})])
    B.validate(data, ROOT)          # must not raise


# -- disclosure ------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "Write to the keeper at someone@example.com.",
    "Call the keeper on 555-123-4567.",
    "And the ledger named in FETCH_LOG was read aloud.",
])
def test_people_and_raw_evidence_are_refused(text):
    _raises(_corpus([_verse(1, text=text)]), "refused|email address|phone number")


# -- caps ------------------------------------------------------------------

def test_book_cap_is_enforced():
    data = _corpus([_verse(1)], limits={"max_books": 1,
                                        "max_verses_per_chapter": 60})
    data["books"].append({"id": "exodus", "name": "Exodus", "subtitle": "The Book",
                          "genre": "law", "chapters": [
                              {"number": 1, "verses": [_verse(1)]}]})
    _raises(data, "retire one to add one")


def test_chapter_cap_is_enforced_below_the_book_cap():
    # The book cap is not the corpus cap: one book with unbounded chapters is an
    # unbounded corpus that passes every limit declared before this one existed.
    chapters = [{"number": index, "verses": [_verse(1)]} for index in range(1, 4)]
    data = _corpus([_verse(1)], limits={"max_books": 12,
                                        "max_chapters_per_book": 2,
                                        "max_verses_per_chapter": 60})
    data["books"][0]["chapters"] = chapters
    _raises(data, "3 chapters, limit is 2")


def test_annotation_cap_is_enforced_per_verse():
    notes = [{"kind": "editorial", "text": "A note."} for _ in range(3)]
    data = _corpus([_verse(1, annotations=notes)],
                   limits={"max_books": 12, "max_verses_per_chapter": 60,
                           "max_annotations_per_verse": 2})
    _raises(data, "3 annotations, limit is 2")


def test_a_chapter_and_note_cap_above_the_ceiling_is_refused():
    _raises(_corpus([_verse(1)], limits={"max_books": 12,
                                         "max_chapters_per_book": 999,
                                         "max_verses_per_chapter": 60}),
            "may not exceed")


def test_limit_above_the_hard_ceiling_is_refused():
    _raises(_corpus([_verse(1)], limits={"max_books": 999,
                                         "max_verses_per_chapter": 60}),
            "may not exceed")


# -- apparatus -------------------------------------------------------------

def test_variant_must_name_where_its_reading_came_from():
    _raises(_corpus([_verse(1, variants=[{"reading": "The circulated reading",
                                          "text": "it said 7.80 GB",
                                          "source": ""}])]),
            "a variant must say where its reading comes from")


def test_variant_with_source_passes_and_is_counted():
    data = _corpus([_verse(1, variants=[{"reading": "The circulated reading",
                                         "text": "it said 7.80 GB",
                                         "source": "another application's venv"}])])
    assert B.validate(data, ROOT)["variants"] == 1


# -- the annotated-edition layer -------------------------------------------

def test_annotation_kind_must_be_declared():
    _raises(_corpus([_verse(1, annotations=[{"kind": "vibes", "note": "it felt right"}])]),
            "kind must be one of")


def test_annotation_carrying_a_figure_needs_its_own_source():
    _raises(_corpus([_verse(1, annotations=[{"kind": "historical",
                                             "note": "this happened in 1983"}])]),
            "a number needs `source`")


def test_annotation_with_a_real_source_passes():
    data = _corpus([_verse(1, annotations=[
        {"kind": "textual", "note": "the divergence read 0.001",
         "source": "Project_Nurse_Ratchet/README.md"}])])
    assert B.validate(data, ROOT)["annotations"] == 1   # must not raise


def test_a_url_is_not_a_repository_path():
    _raises(_corpus([_verse(1, text="It was 0.83.",
                            source="https://example.com/finding.md")]),
            "names no repository path")


def test_section_heading_with_a_digit_is_refused():
    data = _corpus([_verse(1), _verse(2)])
    data["books"][0]["chapters"][0]["sections"] = [{"before_verse": 1,
                                                    "heading": "Of 3 gates"}]
    _raises(data, "a heading is a label, not a claim")


def test_section_before_verse_must_exist_in_the_chapter():
    data = _corpus([_verse(1)])
    data["books"][0]["chapters"][0]["sections"] = [{"before_verse": 4,
                                                    "heading": "Of gates"}]
    _raises(data, "before_verse must name a verse in this chapter")


def test_sections_must_ascend():
    data = _corpus([_verse(1), _verse(2), _verse(3)])
    data["books"][0]["chapters"][0]["sections"] = [
        {"before_verse": 3, "heading": "Later"},
        {"before_verse": 1, "heading": "Earlier"},
    ]
    _raises(data, "sections must ascend")


def test_introduction_carrying_a_figure_must_name_its_sources():
    data = _corpus([_verse(1)])
    data["books"][0]["introduction"] = {"paragraphs": ["It was written in 1983."]}
    _raises(data, "the block must name `sources`")


def test_introduction_prose_without_figures_passes():
    data = _corpus([_verse(1)])
    data["books"][0]["introduction"] = {
        "paragraphs": ["Why the book exists, and how to read it."], "sources": []}
    assert B.validate(data, ROOT)["introductions"] == 1


def test_glossary_see_must_resolve():
    data = _corpus([_verse(1)])
    data["glossary"] = [{"term": "trunk", "gloss": "the canon.", "see": "genesis 1:7"}]
    _raises(data, r"glossary\[0\]: see genesis 1:7, which does not exist")


def test_glossary_entry_must_carry_term_and_gloss():
    data = _corpus([_verse(1)])
    data["glossary"] = [{"term": "trunk", "gloss": ""}]
    _raises(data, "gloss is empty")


def test_unknown_top_level_key_is_refused():
    data = _corpus([_verse(1)])
    data["appendices"] = []
    _raises(data, "unknown top-level key")


def test_edition_must_name_both_its_parts():
    data = _corpus([_verse(1)])
    data["edition"] = {"name": "The Annotated Book"}
    _raises(data, "edition.basis is empty")


# -- genealogy ------------------------------------------------------------

def _tree(root: Path, files) -> Path:
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def test_import_graph_counts_cross_package_edges_only(tmp_path):
    _tree(tmp_path, {
        "alpha/__init__.py": "",
        "beta/__init__.py": "",
        "alpha/user.py": "from beta.core import thing\nimport beta.other\nimport os\n",
        "beta/core.py": "from .local import helper\n",
        "beta/local.py": "helper = 1\n",
    })
    edges, unreadable = B.import_graph(tmp_path)
    assert unreadable == []
    assert edges["alpha"] == {"beta": 2}      # two imports of beta, counted twice
    assert edges["beta"] == {}                # the relative import stays inside


def test_unparsable_module_is_reported_not_raised(tmp_path):
    _tree(tmp_path, {"alpha/__init__.py": "", "alpha/broken.py": "def f(:\n"})
    edges, unreadable = B.import_graph(tmp_path)
    assert "alpha/broken.py" in unreadable
    assert edges["alpha"] == {}


def test_edition_renders_headings_notes_and_glossary():
    data = _corpus([_verse(1, text="And the trunk held the canon.",
                           annotations=[{"kind": "editorial",
                                         "note": "The canon is the trunk."}])])
    data["books"][0]["introduction"] = {"paragraphs": ["Why this book exists."]}
    data["books"][0]["chapters"][0]["sections"] = [
        {"before_verse": 1, "heading": "The trunk"}]
    text = B.render_edition(data)
    assert "# Test Canon" in text
    assert "##### The trunk" in text
    assert "Why this book exists." in text
    assert "**1** And the trunk held the canon." in text
    assert "> **editorial** — The canon is the trunk." in text


def test_edition_is_byte_identical_on_a_second_run():
    data = B.load(B.CORPUS)
    assert B.render_edition(data) == B.render_edition(data)


def test_edition_never_leaves_a_bare_subtitle_heading():
    data = _corpus([_verse(1)])
    data["books"][0].pop("subtitle")
    text = B.render_edition(data)
    assert "### \n" not in text


def test_harvest_ledger_is_readable_and_ids_resolve():
    ids = B.harvest_ids(ROOT)
    assert ids and "error-log-md-L777" in ids


def test_stale_generated_file_is_refused(tmp_path):
    # A generated artefact nobody regenerated answers for a corpus it no longer
    # describes: the exact defect the drift check exists to catch.
    (tmp_path / "src").mkdir()
    for relative in ("docs/bible/GENEALOGY.md", "docs/bible/BOOK_OF_THE_TREE.md"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("stale\n", encoding="utf-8")
    problems = B.generated_drift(tmp_path, B.load(B.CORPUS))
    assert any("GENEALOGY.md" in problem for problem in problems)
    assert any("BOOK_OF_THE_TREE.md" in problem for problem in problems)


def test_absent_generated_file_says_what_to_run(tmp_path):
    (tmp_path / "src").mkdir()
    problems = B.generated_drift(tmp_path, B.load(B.CORPUS))
    assert all("absent" in problem for problem in problems)
    assert len(problems) == 2


# -- the practical layer and the domain books ------------------------------

def _practice(**overrides) -> dict:
    practice = {
        "symptom": "a reading is repeated from an earlier session",
        "cause": "nothing re-derives the reading in the turn that quotes it",
        "detection": "python tools/domain_trees.py --check",
        "remedy": "re-derive it and keep the command beside the number",
        "evidence": ["error-log-md-L777", "error-log-md-L989", "engram-349"],
    }
    practice.update(overrides)
    return practice


def test_practice_needs_three_harnessed_records():
    data = _corpus([_verse(1, practice=_practice(
        evidence=["error-log-md-L777", "error-log-md-L989"]))])
    _raises(data, "at least 3 harvest records")


def test_practice_citing_an_absent_record_is_refused():
    data = _corpus([_verse(1, practice=_practice(
        evidence=["error-log-md-L777", "error-log-md-L989", "no-such-record"]))])
    _raises(data, "which the harvest ledger does not contain")


def test_practice_detection_must_name_a_real_command():
    data = _corpus([_verse(1, practice=_practice(
        detection="python tools/does_not_exist.py --check"))])
    _raises(data, "practice.detection does not exist here")


def test_practice_carrying_a_figure_is_refused():
    data = _corpus([_verse(1, practice=_practice(
        cause="the pool read 341 errors and nobody measured it"))])
    _raises(data, "practice.cause carries a figure")


def test_a_complete_practice_passes_and_is_counted():
    data = _corpus([_verse(1, practice=_practice())])
    diagnostics = B.validate(data, ROOT)
    assert diagnostics["verses"] == 1


def test_domain_book_must_name_a_declared_domain():
    data = _corpus([_verse(1)])
    data["books"][0]["domain"] = "atlantis"
    _raises(data, "is not declared in tools/domain_trees.py")


def test_domain_book_naming_a_declared_domain_passes():
    data = _corpus([_verse(1)])
    data["books"][0]["domain"] = "sentinel"
    B.validate(data, ROOT)          # must not raise


def test_domain_declaration_is_read_by_ast():
    declared = B.declared_domains(ROOT)
    assert declared and {"sentinel", "hives", "cain"} <= declared


def test_edition_prints_the_practice_beside_its_verse():
    data = _corpus([_verse(1, practice=_practice())])
    text = B.render_edition(data)
    assert "**Practice**" in text
    assert "tools/domain_trees.py --check" in text
    assert "error-log-md-L777" in text


def test_genealogy_rendering_is_deterministic_and_biblical():
    edges = {"core": {"psyche": 4, "codex": 1}, "pscyhe": {}, "codex": {"core": 2}}
    first = B.render_genealogy(edges, [])
    second = B.render_genealogy(edges, [])
    assert first == second
    assert "begat" in first
    assert "**psyche**" in first            # the heaviest edge is named first
    assert "begat no other house" in first  # an empty house still speaks
