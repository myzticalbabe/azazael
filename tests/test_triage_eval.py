# coding: utf-8
"""Triage evaluation gate: the instrument must be able to PASS and to FAIL.

An evaluation that only ever reports a good number is decoration. These tests
pin both directions:

  POSITIVE control -- a corpus of unambiguous rows must score recall 1.0.
  NEGATIVE control -- a corpus whose intent row is phrased so the router cannot
                      see it must score recall 0.0. If that ever reports 1.0, the
                      instrument is broken and every other number it prints is
                      meaningless.

Also pinned: provenance is required, splits are reported separately, and false
negatives are printed before false positives.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import triage_eval as E

META = {"_meta": "test corpus", "authored": "2026-11-01"}


def _write(tmp_path, rows, meta=META):
    path = tmp_path / "corpus.jsonl"
    lines = [json.dumps(meta)] if meta else []
    lines += [json.dumps(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_provenance_row_is_required(tmp_path):
    path = _write(tmp_path, [{"text": "hi", "expect_crisis": False}], meta=None)
    with pytest.raises(ValueError, match="_meta"):
        E.load_corpus(path)


def test_rows_without_labels_are_rejected(tmp_path):
    path = _write(tmp_path, [{"text": "hi"}])
    with pytest.raises(ValueError, match="expect_crisis"):
        E.load_corpus(path)


def test_positive_control_unambiguous_corpus_scores_perfect(tmp_path):
    path = _write(tmp_path, [
        {"text": "I want to die", "expect_crisis": True, "category": "explicit_intent"},
        {"text": "I am going to kill myself", "expect_crisis": True, "category": "explicit_intent"},
        {"text": "I am just killing time", "expect_crisis": False, "category": "idiom"},
        {"text": "dead tired today", "expect_crisis": False, "category": "idiom"},
    ])
    report = E.evaluate(E.load_corpus(path))
    assert report["recall"] == 1.0
    assert report["precision"] == 1.0
    assert report["specificity"] == 1.0


def test_negative_control_undetectable_intent_scores_zero(tmp_path):
    """If this ever returns 1.0 the instrument is not measuring the router."""
    path = _write(tmp_path, [
        {"text": "I have decided the arrangement is final and the paperwork is filed",
         "expect_crisis": True, "category": "euphemism"},
        {"text": "the weather is fine", "expect_crisis": False, "category": "neutral"},
    ])
    report = E.evaluate(E.load_corpus(path))
    assert report["recall"] == 0.0
    assert report["confusion"]["false_negative"] == 1
    assert report["misses"][0]["kind"] == "false_negative"


def test_split_breakdown_separates_fitted_from_holdout(tmp_path):
    path = _write(tmp_path, [
        {"text": "I want to die", "expect_crisis": True, "category": "explicit_intent"},
        {"text": "I have decided the arrangement is final", "expect_crisis": True,
         "category": "euphemism", "split": "holdout"},
    ])
    report = E.evaluate(E.load_corpus(path))
    assert report["by_split"]["dev"]["recall"] == 1.0
    assert report["by_split"]["holdout"]["recall"] == 0.0
    assert "FITTED" in E.render(report)


def test_split_filter_scores_only_that_subset(tmp_path):
    path = _write(tmp_path, [
        {"text": "I want to die", "expect_crisis": True, "category": "explicit_intent"},
        {"text": "I have decided the arrangement is final", "expect_crisis": True,
         "category": "euphemism", "split": "holdout"},
    ])
    corpus = E.load_corpus(path)
    holdout = E.evaluate(corpus, split="holdout")
    assert holdout["rows"] == 1
    assert holdout["recall"] == 0.0


def test_false_negatives_are_printed_before_false_positives(tmp_path):
    path = _write(tmp_path, [
        {"text": "the arrangement is final and filed", "expect_crisis": True,
         "category": "euphemism"},
        # A first-person framing defeats the attribution guard, so this is a real
        # false positive of the router -- which is what the ordering test needs.
        {"text": "I keep saying kill myself as a joke", "expect_crisis": False,
         "category": "quotation"},
    ])
    text = E.render(E.evaluate(E.load_corpus(path)))
    missing = text.index("FN [")
    wrong = text.index("FP [")
    assert missing < wrong


def test_report_always_carries_the_limitation():
    corpus = E.load_corpus(E.CORPUS)
    report = E.evaluate(corpus)
    assert "not clinical validity" in report["provenance"]
    assert "not clinical validation" in E.render(report).lower() or \
           "Nothing here is a clinical validation" in E.render(report)


def test_shipped_corpus_is_well_formed_and_has_a_holdout():
    corpus = E.load_corpus(E.CORPUS)
    assert corpus["meta"]["rows"] == len(corpus["rows"])
    splits = {row["split"] for row in corpus["rows"]}
    assert "dev" in splits and "holdout" in splits
    assert all(isinstance(row["expect_crisis"], bool) for row in corpus["rows"])


def test_min_recall_gate_exits_nonzero(tmp_path, capsys):
    path = _write(tmp_path, [
        {"text": "the arrangement is final", "expect_crisis": True, "category": "euphemism"},
    ])
    assert E.main(["--corpus", str(path), "--min-recall", "0.9"]) == 1


def test_json_output_is_machine_readable(tmp_path, capsys):
    path = _write(tmp_path, [
        {"text": "I want to die", "expect_crisis": True, "category": "explicit_intent"},
    ])
    assert E.main(["--corpus", str(path), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["confusion"]["true_positive"] == 1
