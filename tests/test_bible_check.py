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
    B.validate(data, ROOT)          # must not raise
    assert data["_diagnostics"]["books"] >= 1


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
    B.validate(data, ROOT)
    assert data["_diagnostics"]["variants"] == 1


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


def test_genealogy_rendering_is_deterministic_and_biblical():
    edges = {"core": {"psyche": 4, "codex": 1}, "pscyhe": {}, "codex": {"core": 2}}
    first = B.render_genealogy(edges, [])
    second = B.render_genealogy(edges, [])
    assert first == second
    assert "begat" in first
    assert "**psyche**" in first            # the heaviest edge is named first
    assert "begat no other house" in first  # an empty house still speaks
