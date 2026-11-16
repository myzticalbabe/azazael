"""``tools/check_corpus_quotes.py`` must prove quotes, not merely fail to disprove them.

The load-bearing tests are the ones that pin a *defect that was measured*, not a
shape that was imagined:

``test_declaration_validated_even_when_quote_is_verbatim``
    The first version of ``judge()`` returned ``STRICT`` on a verbatim match
    *before* reading ``apparatus``, so a block declaring tokens the source does
    not contain scored as proven (exit 0). The declaration is a claim about the
    document; it is now validated whether or not the quote needed it.

``test_no_text_is_unproven_never_a_pass`` / ``test_cli_blind_when_no_source_text``
    An unresolvable source is ``NO-TEXT`` and a run where nothing resolved exits
    ``2``. Collapsing that into ``0 findings`` is how a coverage gap reads as a
    pass -- the exact failure mode the tool exists to close.

``test_nfkc_would_erase_superscript_callouts``
    A guard on the normaliser: ``NFKC`` folds ``U+00B2``/``U+00B3``/``U+00B9``
    to ASCII digits, which would erase the superscript callouts the corpus
    declares as apparatus. The explicit ligature map must not regress to NFKC.

Fixtures here are synthetic source text written by this file, so they test the
*contract* (which verdict a shape earns), never a claim about a real document.
The one real-corpus test is the denominator invariant, and its source-dependent
leg names itself as skipped rather than passing when no text is on disk.
"""

import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import check_corpus_quotes as qc  # noqa: E402 - after sys.path


# --- helpers ----------------------------------------------------------------

SOURCE_TEXT = (
    "Housing stability is the strongest single predictor of family "
    "reunification in this sample. Participants reported that a stable "
    "address changed how caseworkers treated them, and that the change "
    "was visible within one review cycle. Informa-\n"
    "tion about the waitlist was collected at intake."
)


def block(quote, source_id="S-TEST-01", apparatus=None):
    row = {"source_id": source_id, "quote": quote}
    if apparatus is not None:
        row["apparatus"] = apparatus
    return row


def write_corpus(tmp_path, blocks, name="corpus.json"):
    """One need, one edge per block -- the shape ``run()`` walks."""
    edges = [{"edge_id": "E-1", label: b} for label, b in blocks]
    doc = {"needs": [{"edges": edges}]}
    path = tmp_path / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def write_source(tmp_path, sid="S-TEST-01", text=SOURCE_TEXT, name=None):
    target = tmp_path / (name or ("%s.txt" % sid))
    target.write_text(text, encoding="utf-8")
    return target


# --- normalisation -----------------------------------------------------------

def test_ligature_run_repairs_extractor_split():
    """docling #3057: a ligature followed by the space the extractor inserted."""
    assert qc.normalise_artifacts("classi\uFB01cation") == "classification"
    assert qc.normalise_artifacts("\uFB01 eld") == "field"
    assert qc.normalise_artifacts("e\uFB00 ect") == "effect"


def test_soft_hyphen_and_dashes_are_normalised():
    assert qc.normalise_artifacts("re\u00ADunification") == "reunification"
    assert qc.normalise_artifacts("well\u2013being") == "well-being"
    assert qc.normalise_artifacts("note\u2014here") == "note-here"


def test_nfkc_would_erase_superscript_callouts():
    """A guard, not a style note: NFKC folds these to ASCII and the callout
    apparatus the corpus declares would become indistinguishable from prose."""
    for sup in ("\u00B2", "\u00B3", "\u00B9", "\u2070", "\u2074"):
        assert qc.normalise_artifacts("claim" + sup) == "claim" + sup


def test_readings_offers_both_and_dehyphenates_only_one():
    both = qc.readings("informa-\ntion")
    assert set(both) == set(qc.READINGS) == {"verbatim", "dehyphenated"}
    assert both["verbatim"] == "informa- tion"
    assert both["dehyphenated"] == "information"


# --- judge() contracts -------------------------------------------------------

def test_verbatim_quote_is_strict():
    verdict, reading, why = qc.judge(
        block("a stable address changed how caseworkers treated them"), SOURCE_TEXT)
    assert verdict == "STRICT"
    assert reading == "verbatim"
    assert why == ""


def test_line_broken_quote_needs_the_dehyphenated_reading():
    verdict, reading, _ = qc.judge(
        block("Information about the waitlist was collected"), SOURCE_TEXT)
    assert verdict == "STRICT"
    # The source says "Informa-\ntion"; only the dehyphenated reading joins it.
    assert reading == "dehyphenated"


def test_no_text_is_unproven_never_a_pass():
    verdict, reading, why = qc.judge(block("anything at all"), None)
    assert verdict == "NO-TEXT"
    assert reading == ""
    assert "UNPROVEN" in why


def test_absent_quote_is_absent():
    verdict, _, why = qc.judge(block("a sentence the document never contained"),
                               SOURCE_TEXT)
    assert verdict == "ABSENT"
    assert why == "no reading matches"


def test_undeclared_apparatus_is_named_not_silently_repaired():
    """Superscript callouts in the source, omitted from the quote, no declaration."""
    hay = "Participants reported that a stable address1,2 changed how caseworkers treated them"
    verdict, reading, why = qc.judge(
        block("Participants reported that a stable address changed how "
              "caseworkers treated them"), hay)
    assert verdict == "UNDECLARED"
    assert reading in qc.READINGS
    assert "apparatus.kind" in why


def test_declared_apparatus_is_proven():
    hay = "Participants reported that a stable address1,2 changed how caseworkers treated them"
    verdict, reading, why = qc.judge(
        block("Participants reported that a stable address changed how "
              "caseworkers treated them",
              apparatus={"kind": "superscript-callouts", "removed": ["1,2"]}),
        hay)
    assert verdict == "APPARATUS"
    assert reading in qc.READINGS
    assert why == ""


def test_declaration_validated_even_when_quote_is_verbatim():
    """REGRESSION: a verbatim match must not short-circuit the declaration.

    The quote is present word-for-word, yet the block declares a token the
    source does not contain. Before the fix this scored STRICT and exit 0 --
    an unprovable claim passing as a proven one.
    """
    quote = "a stable address changed how caseworkers treated them"
    verdict, _, why = qc.judge(
        block(quote, apparatus={"kind": "superscript-callouts",
                                "removed": ["99"]}),
        SOURCE_TEXT)
    assert verdict == "ABSENT"
    assert "not in the source text" in why


def test_declared_token_that_also_appears_in_the_quote_is_rejected():
    """A "removed" token still inside the quoted span proves nothing."""
    hay = "address1,2 changed the review1,2 cycle"
    verdict, _, why = qc.judge(
        block("address1,2 changed the review cycle",
              apparatus={"kind": "superscript-callouts", "removed": ["1,2"]}),
        hay)
    assert verdict == "ABSENT"
    assert "also appears in the quote" in why


def test_contiguous_quote_with_a_redundant_declaration_is_proven_with_a_note():
    """The token exists, but outside the quoted span -- the declaration is proven
    and the block is told it was not needed (a note, not a failure)."""
    verdict, _, why = qc.judge(
        block("a stable address changed how caseworkers treated them",
              apparatus={"kind": "superscript-callouts", "removed": ["1,2"]}),
        "a stable address changed how caseworkers treated them1,2 within one review cycle")
    assert verdict == "APPARATUS"
    assert "the removed material sits outside the quoted span" in why


def test_declaration_that_was_actually_needed_carries_no_note():
    """Same shape, token inside the quoted span: proven, and no "redundant" note."""
    verdict, _, why = qc.judge(
        block("a stable address changed how caseworkers treated them",
              apparatus={"kind": "superscript-callouts", "removed": ["1,2"]}),
        "a stable address1,2 changed how caseworkers treated them")
    assert verdict == "APPARATUS"
    assert why == ""


# --- source resolution -------------------------------------------------------

def test_layout_txt_is_never_a_candidate(tmp_path):
    """``pdftotext -layout`` puts a two-column page's columns on one line."""
    (tmp_path / "S-TEST-01.layout.txt").write_text(SOURCE_TEXT, encoding="utf-8")
    assert qc.resolve_source("S-TEST-01", [tmp_path]) is None
    write_source(tmp_path)
    assert qc.resolve_source("S-TEST-01", [tmp_path]) == tmp_path / "S-TEST-01.txt"


def test_first_matching_directory_wins(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "S-TEST-01.txt").write_text("first", encoding="utf-8")
    (second / "S-TEST-01.txt").write_text("second", encoding="utf-8")
    assert qc.resolve_source("S-TEST-01", [first, second]) == first / "S-TEST-01.txt"


# --- run() denominator -------------------------------------------------------

def test_run_counts_every_block_and_never_drops_a_need(tmp_path):
    corpus = write_corpus(tmp_path, [
        ("ground", block("a stable address")),
        ("corroboration", block("a sentence the document never contained")),
    ])
    write_source(tmp_path)
    rows, counts = qc.run(corpus, [tmp_path])
    assert len(rows) == 2
    assert counts == {"ABSENT": 1, "STRICT": 1}
    assert [r["block"] for r in rows] == ["ground", "corroboration"]


# --- CLI exit codes ----------------------------------------------------------

def test_cli_clean_exit_0(tmp_path, capsys):
    corpus = write_corpus(tmp_path, [("ground", block("a stable address"))])
    write_source(tmp_path)
    assert qc.main(["--corpus", str(corpus), "--sources-dir", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "proven 1/1 (0 unproven, 0 NO-TEXT)" in out


def test_cli_absent_exit_1(tmp_path, capsys):
    corpus = write_corpus(tmp_path, [("ground", block("never in the document"))])
    write_source(tmp_path)
    assert qc.main(["--corpus", str(corpus), "--sources-dir", str(tmp_path)]) == 1
    assert "proven 0/1 (1 unproven, 0 NO-TEXT)" in capsys.readouterr().out


def test_cli_blind_when_no_source_text(tmp_path, capsys):
    """No text resolved is exit 2 -- never a clean run over unread documents."""
    corpus = write_corpus(tmp_path, [("ground", block("a stable address"))])
    empty = tmp_path / "sources"
    empty.mkdir()
    assert qc.main(["--corpus", str(corpus), "--sources-dir", str(empty)]) == 2
    assert "BLIND: no source text resolved" in capsys.readouterr().err


def test_cli_missing_corpus_exit_2(tmp_path, capsys):
    assert qc.main(["--corpus", str(tmp_path / "nope.json")]) == 2
    assert "BLIND: corpus not found" in capsys.readouterr().err


def test_cli_empty_corpus_exit_2(tmp_path, capsys):
    corpus = write_corpus(tmp_path, [])
    write_source(tmp_path)
    assert qc.main(["--corpus", str(corpus), "--sources-dir", str(tmp_path)]) == 2
    assert "BLIND: the corpus yielded no quotes" in capsys.readouterr().err


def test_cli_manifest_records_the_denominator(tmp_path):
    corpus = write_corpus(tmp_path, [
        ("ground", block("a stable address")),
        ("corroboration", block("never in the document")),
    ])
    write_source(tmp_path)
    target = tmp_path / "manifest.json"
    qc.main(["--corpus", str(corpus), "--sources-dir", str(tmp_path),
             "--manifest", str(target)])
    manifest = json.loads(target.read_text(encoding="utf-8"))
    assert manifest["denominator"] == {
        "total": 2, "proven": 1, "unproven": 1, "no_text": 0}
    assert manifest["counts"] == {"ABSENT": 1, "STRICT": 1}
    assert len(manifest["rows"]) == 2
    # Every row carries the sha256 of the text it was judged against.
    assert all(len(r["source_sha256"]) == 64 for r in manifest["rows"])


# --- the tracked corpus: denominator first, verdicts only if text resolves ----

def test_tracked_corpus_denominator_is_26_blocks():
    rows, _ = qc.run(qc.DEFAULT_CORPUS, [])
    assert len(rows) == 26
    # With no sources supplied every block is UNPROVEN -- the tool refuses to
    # read an absent document as agreement.
    assert {r["verdict"] for r in rows} == {"NO-TEXT"}


def test_tracked_corpus_is_fully_proven_when_source_text_is_present():
    dirs = [d for d in qc.DEFAULT_SOURCE_DIRS if d.is_dir()]
    if not any(qc.resolve_source(r["source_id"], dirs)
               for r in qc.run(qc.DEFAULT_CORPUS, [])[0]):
        pytest.skip("no source cache on this machine (state/fn_* and C:/tmp/fn_* "
                    "are all absent); the tracked corpus cannot be proven here")
    rows, counts = qc.run(qc.DEFAULT_CORPUS, dirs)
    failing = [r for r in rows if r["verdict"] not in ("STRICT", "APPARATUS")]
    assert failing == []
    assert counts.get("NO-TEXT", 0) == 0
