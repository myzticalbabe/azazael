"""
Tests for M2 — the Adaptive Pacing Governor (B2, lane 2).

The three claims that could be false are asserted directly: the clamp holds at
both ends and is *reported*, a well-measured user is never paced faster than a
poorly-measured one, and the profile's only lever is waiting (gap), never rate.
"""

from __future__ import annotations

import pytest

from SARAH.profile import Profile
from SARAH.sensory.pacing import (
    MAX_CHUNK_WORDS,
    MAX_HINT_DELAY_MS,
    MAX_WPM,
    MIN_CHUNK_WORDS,
    MIN_WPM,
    Paced,
    Pacing,
)

TEXT = (
    "one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty"
)

FAST = Profile(processing_speed=1.0)
SLOW = Profile(processing_speed=0.0)


def test_constructs_with_no_arguments():
    pacer = Pacing()
    assert hasattr(pacer, "hint_delay_ms_by_profile")
    assert hasattr(pacer, "chunk_size_by_processing_speed")


def test_default_target_is_the_floor_and_a_fast_profile_does_not_raise_it():
    pacer = Pacing()
    assert pacer.target_wpm() == MIN_WPM
    assert pacer.target_wpm(FAST) == MIN_WPM
    assert pacer.target_wpm(SLOW) == MIN_WPM


def test_no_profile_produces_a_rate_above_the_ceiling():
    pacer = Pacing()
    for speed in (None, 0.0, 0.25, 0.5, 0.75, 1.0):
        profile = Profile() if speed is None else Profile(processing_speed=speed)
        paced = pacer.chunk(TEXT, profile)
        assert paced.wpm <= MAX_WPM
        assert paced.wpm >= MIN_WPM


def test_upper_clamp_is_applied_and_reported():
    paced = Pacing().chunk(TEXT, wpm=400)
    assert paced.wpm == MAX_WPM
    assert paced.clamped is True
    assert "ceiling" in (paced.clamp_reason or "")


def test_lower_clamp_is_applied_and_reported():
    paced = Pacing().chunk(TEXT, wpm=40)
    assert paced.wpm == MIN_WPM
    assert paced.clamped is True
    assert "floor" in (paced.clamp_reason or "")


def test_request_inside_the_band_is_not_clamped():
    paced = Pacing().chunk(TEXT, wpm=150)
    assert paced.wpm == 150
    assert paced.clamped is False
    assert paced.clamp_reason is None


def test_good_reading_is_not_paced_faster_than_poor_reading():
    pacer = Pacing()
    good = pacer.chunk(TEXT, FAST)
    poor = pacer.chunk(TEXT, SLOW)
    assert good.wpm <= poor.wpm


def test_gap_scales_with_processing_speed():
    pacer = Pacing()
    good = pacer.gap_ms(MIN_WPM, 5, FAST)
    poor = pacer.gap_ms(MIN_WPM, 5, SLOW)
    assert poor > good


def test_unmeasured_processing_speed_gets_the_full_margin():
    pacer = Pacing()
    unmeasured = pacer.gap_ms(MIN_WPM, 5, Profile())
    assert unmeasured > pacer.gap_ms(MIN_WPM, 5, FAST)


def test_chunk_sizes_stay_inside_the_band():
    pacer = Pacing()
    for speed in (0.0, 0.3, 0.5, 0.8, 1.0):
        size = pacer.chunk_size_by_processing_speed(Profile(processing_speed=speed))
        assert MIN_CHUNK_WORDS <= size <= MAX_CHUNK_WORDS
    assert pacer.chunk_size_by_processing_speed(SLOW) == MIN_CHUNK_WORDS
    assert pacer.chunk_size_by_processing_speed(FAST) == MAX_CHUNK_WORDS


def test_hint_delay_is_longer_for_a_slower_user_and_capped():
    pacer = Pacing()
    slow_delay = pacer.hint_delay_ms_by_profile(SLOW)
    fast_delay = pacer.hint_delay_ms_by_profile(FAST)
    assert slow_delay > fast_delay
    assert slow_delay <= MAX_HINT_DELAY_MS
    assert pacer.hint_delay_ms_by_profile() <= MAX_HINT_DELAY_MS


def test_hint_delay_rises_with_prediction_need():
    pacer = Pacing()
    low = pacer.hint_delay_ms_by_profile(Profile(processing_speed=0.5, prediction_need=0.0))
    high = pacer.hint_delay_ms_by_profile(Profile(processing_speed=0.5, prediction_need=1.0))
    assert high > low


def test_every_word_survives_the_chunking():
    paced = Pacing().chunk(TEXT, SLOW)
    assert paced.text() == " ".join(TEXT.split())
    assert paced.words == len(TEXT.split())


def test_chunks_are_no_larger_than_the_declared_size():
    paced = Pacing().chunk(TEXT, SLOW)
    assert paced.chunk_words == MIN_CHUNK_WORDS
    for chunk in paced:
        assert len(chunk.split()) <= paced.chunk_words


def test_result_reads_like_a_sequence():
    paced = Pacing().chunk(TEXT, FAST)
    assert isinstance(paced, Paced)
    assert len(paced) == len(paced.chunks)
    assert list(paced) == list(paced.chunks)


def test_empty_text_yields_no_chunks_and_no_gap():
    paced = Pacing().chunk("", SLOW)
    assert paced.chunks == ()
    assert paced.gap_ms == 0
    assert paced.words == 0


def test_non_string_text_is_refused():
    with pytest.raises(TypeError):
        Pacing().chunk(["not", "a", "string"])  # type: ignore[arg-type]


def test_boolean_rate_is_refused():
    with pytest.raises(TypeError):
        Pacing().chunk(TEXT, wpm=True)  # type: ignore[arg-type]
