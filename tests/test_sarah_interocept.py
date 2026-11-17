"""
Tests for M8 — Interoception Bridge (Lane 3)

Per design:
- 'not sure' is a first-class answer in every emotion prompt
- Free text is never required
- Uses PSYCHE affect vocabulary (PAD, OCC, regulation)
- Maps to SarahProfile.interoception axis
"""

from __future__ import annotations

import pytest

from SARAH.affect.interocept import (
    Interocept,
    BodySignal,
    InteroceptVocabulary,
    interoception_from_signals,
)
from SARAH.profile import SarahProfile
from PSYCHE.elicitation import SCALE


class TestInteroceptVocabulary:
    """Test the vocabulary mapping between body signals and PSYCHE affect."""

    def test_all_signals_have_pad(self):
        """Every body signal has a PAD tuple."""
        for signal in BodySignal:
            pad = InteroceptVocabulary.pad_for(signal)
            assert isinstance(pad, tuple)
            assert len(pad) == 3
            assert all(isinstance(v, (int, float)) for v in pad)
            assert all(-1.0 <= v <= 1.0 for v in pad)

    def test_all_signals_have_occ_family(self):
        """Every body signal has an OCC family."""
        for signal in BodySignal:
            family = InteroceptVocabulary.occ_family(signal)
            assert isinstance(family, str)
            assert len(family) > 0

    def test_all_signals_have_intensity(self):
        """Every body signal has a typical intensity."""
        for signal in BodySignal:
            intensity = InteroceptVocabulary.typical_intensity(signal)
            assert isinstance(intensity, (int, float))
            assert 0.0 <= intensity <= 1.0

    def test_signal_names_match_enum(self):
        """All enum values are covered in SIGNAL_MAP."""
        assert set(InteroceptVocabulary.SIGNAL_MAP.keys()) == set(BodySignal)


class TestInteroceptElicitation:
    """Test the elicitation logic."""

    def setup_method(self):
        self.profile = SarahProfile()
        self.interocept = Interocept(self.profile)

    def test_elicit_signal_accepts_scale(self):
        """Valid scale responses are accepted."""
        for val in SCALE:
            intensity = self.interocept.elicit_signal(BodySignal.HEART_RATE, val)
            expected = float(val) / max(SCALE)
            assert intensity == expected

    def test_elicit_signal_not_sure_returns_none(self):
        """'not sure' (None) is a first-class answer — returns None."""
        intensity = self.interocept.elicit_signal(BodySignal.HEART_RATE, None)
        assert intensity is None

    def test_elicit_signal_rejects_invalid(self):
        """Invalid responses raise ValueError."""
        with pytest.raises(ValueError):
            self.interocept.elicit_signal(BodySignal.HEART_RATE, 5)
        with pytest.raises(ValueError):
            self.interocept.elicit_signal(BodySignal.HEART_RATE, -1)
        with pytest.raises(ValueError):
            self.interocept.elicit_signal(BodySignal.HEART_RATE, "invalid")

    def test_record_signal_validates_range(self):
        """Recording validates intensity is in [0, 1]."""
        import time
        now = time.time()
        self.interocept.record_signal(BodySignal.HEART_RATE, 0.5, now)
        assert len(self.interocept._signal_history) == 1

        with pytest.raises(ValueError):
            self.interocept.record_signal(BodySignal.HEART_RATE, -0.1, now)
        with pytest.raises(ValueError):
            self.interocept.record_signal(BodySignal.HEART_RATE, 1.1, now)

    def test_vocabulary_prompt_contains_not_sure(self):
        """Elicitation prompt includes 'not sure' option."""
        for signal in BodySignal:
            prompt = self.interocept.get_vocabulary_prompt(signal)
            assert "not sure" in prompt.lower()
            assert "skip" in prompt.lower() or "not sure" in prompt.lower()


class TestInteroceptScoring:
    """Test interoception score computation."""

    def setup_method(self):
        self.profile = SarahProfile()
        self.interocept = Interocept(self.profile)

    def test_no_signals_returns_none(self):
        """No signals in window returns None."""
        score = self.interocept.compute_interoception_score(window_seconds=3600.0)
        assert score is None

    def test_compute_score_from_signals(self):
        """Signals produce a score in [0, 1]."""
        import time
        now = time.time()
        # Add some signals
        self.interocept.record_signal(BodySignal.HEART_RATE, 0.8, now)
        self.interocept.record_signal(BodySignal.BREATH, 0.6, now)
        self.interocept.record_signal(BodySignal.ENERGY, 0.9, now)

        score = self.interocept.compute_interoception_score(window_seconds=3600.0)
        assert score is not None
        assert 0.0 <= score <= 1.0

    def test_update_profile_populates_axis(self):
        """Updating profile populates interoception axis."""
        import time
        now = time.time()
        self.interocept.record_signal(BodySignal.HEART_RATE, 0.8, now)

        updated = self.interocept.update_profile(window_seconds=3600.0)
        assert updated.interoception is not None
        assert 0.0 <= updated.interoception <= 1.0

    def test_explain_interoception(self):
        """Explain returns readable string."""
        import time
        now = time.time()
        self.interocept.record_signal(BodySignal.HEART_RATE, 0.8, now)
        self.interocept.update_profile()

        explanation = self.interocept.explain_interoception()
        assert "interoception" in explanation.lower()
        assert "=" in explanation

    def test_full_elicitation(self):
        """Full elicitation runs all signals."""
        responses = {
            BodySignal.HEART_RATE: 3,
            BodySignal.BREATH: 2,
            BodySignal.MUSCLE_TENSION: 1,
            BodySignal.TEMPERATURE: None,  # "not sure"
            BodySignal.GUT_SENSATION: 2,
            BodySignal.FATIGUE: 1,
            BodySignal.ENERGY: 3,
        }

        updated = self.interocept.run_full_elicitation(responses)
        assert updated.interoception is not None
        assert 0.0 <= updated.interoception <= 1.0


class TestInteroceptFromSignals:
    """Test convenience function."""

    def test_convenience_function(self):
        """interoception_from_signals creates profile."""
        signals = {
            BodySignal.HEART_RATE: 0.8,
            BodySignal.BREATH: 0.6,
        }
        profile = interoception_from_signals(signals)
        assert isinstance(profile, SarahProfile)
        assert profile.interoception is not None
        assert 0.0 <= profile.interoception <= 1.0

    def test_updates_existing_profile(self):
        """Can update existing profile."""
        existing = SarahProfile(interoception=0.3)
        signals = {BodySignal.HEART_RATE: 0.9}
        updated = interoception_from_signals(signals, existing)
        # Should blend or replace based on implementation
        assert updated.interoception is not None


class TestPSYCHEVocabularyIntegration:
    """Test integration with PSYCHE affect vocabulary."""

    def test_pad_normalize_used(self):
        """PSYCHE pad_normalize is used in vocabulary."""
        from PSYCHE.affect import pad_normalize
        pad = pad_normalize((0.5, 0.5, 0.5))
        assert pad == (0.5, 0.5, 0.5)

    def test_emotion_to_pad_used(self):
        """PSYCHE emotion_to_pad is available."""
        from PSYCHE.affect import emotion_to_pad
        pad = emotion_to_pad("joy", 0.8)
        assert len(pad) == 3

    def test_occ_families_available(self):
        """OCC families from PSYCHE are accessible."""
        from PSYCHE.affect import appraise_event
        result = appraise_event(0.8, likelihood=0.7)
        assert isinstance(result, list)
        assert all(len(r) == 3 for r in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])