#!/usr/bin/env python
# coding: utf-8
"""Negative control for tools/prose_forensics.py.

RULE 0B-C: an oracle ships a known-healthy fixture it MUST NOT fire on, and a known-bad one it
MUST. Here the "oracle" is a measuring instrument, so the controls are: a text whose counts are
known by hand (the instrument must reproduce them exactly) and a call with an absent trim marker
(the instrument must refuse rather than measure the whole page).

Why this file exists at all: the audit it serves makes claims about a public figure's prose, and
an instrument that quietly miscounts is indistinguishable from an argument. The fixture below is
deliberately trivial so the arithmetic can be checked by eye in ten seconds.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import prose_forensics as P     # noqa: E402

# 3 + 4 + 10 + 2 words = 19; four sentences. Counted by hand, asserted below.
FIXTURE = ("One two three. Four five six seven. "
           "This is not very good and it is not bad. Eight nine.")


def test_counts_match_the_hand_count():
    m = P.measure(FIXTURE, "fixture")
    assert m["words"] == 19
    assert m["sentences"] == 4
    assert m["sentence_len"]["mean"] == 4.75
    assert m["sentence_len"]["pct_under_9"] == 75.0, "three of four sentences are 8 words or fewer"
    assert m["sentence_len"]["pct_over_39"] == 0.0
    assert m["sentence_len"]["max"] == 10


def test_rates_are_per_thousand_and_exact():
    m = P.measure(FIXTURE, "fixture")
    assert m["negation_per_1000"] == round(2 * 1000 / 19, 2)      # "not" twice
    assert m["intensifier_per_1000"] == round(1000 / 19, 2)       # "very" once
    assert m["very_count"] == 1
    assert m["pronouns_per_1000"]["second"] == 0.0
    assert m["sentence_initial"]["but"] == 0


def test_stage_directions_are_removed_and_counted():
    """The cue is a sentence unless stripped -- which is exactly why the flag exists."""
    text = FIXTURE.replace("Eight nine.", "Eight nine. (Applause.)")
    assert text != FIXTURE, "the fixture marker must exist or the control proves nothing"
    untouched = P.measure(text, "with-cue")
    stripped = P.measure(text, "with-cue", strip_cues=True)
    assert untouched["sentences"] == 5, "(Applause.) scores as a one-word sentence when left in"
    assert stripped["stage_directions_removed"] == 1
    assert stripped["sentences"] == 4


def test_measurement_is_deterministic():
    first = P.measure(FIXTURE, "fixture")
    second = P.measure(FIXTURE, "fixture")
    assert first == second


def test_missing_trim_marker_is_refused_not_ignored(tmp_path):
    """The bad control: an absent boundary must stop the run, not silently measure everything."""
    path = tmp_path / "text.txt"
    path.write_text(FIXTURE, encoding="utf-8")
    assert P.main(["--file", str(path), "--start-after", "MARKER-THAT-IS-NOT-THERE"]) == 3
    assert P.main(["--file", str(path), "--end-before", "ALSO-ABSENT"]) == 3


def test_present_marker_trims(tmp_path):
    path = tmp_path / "text.txt"
    path.write_text("chrome chrome. " + FIXTURE, encoding="utf-8")
    out = tmp_path / "m.json"
    assert P.main(["--file", str(path), "--label", "trimmed", "--start-after", "chrome chrome.",
                   "--out", str(out)]) == 0
    import json
    m = json.loads(out.read_text(encoding="utf-8"))
    assert m["words"] == 19, "the chrome before the marker must not be counted"
