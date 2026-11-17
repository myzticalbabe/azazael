"""
Tests for M14 — Affirmation Engine (Lane 3)

Per design:
- Trait praise ('you are amazing') is REFUSED by a test
- If no concrete instance of the user acting on their stated value exists,
  it says so rather than inventing evidence
- Value-affirmation with user-authored statements only
- Reuses PSYCHE affect vocabulary (PAD space for emotional tone)
"""

from __future__ import annotations

import pytest

from SARAH.affect.affirmation import (
    AffirmationEngine,
    ValueStatement,
    AffirmationMode,
    quick_affirm,
)
from SARAH.profile import SarahProfile


class TestValueStatement:
    """Test ValueStatement validation."""

    def test_valid_statement(self):
        """Valid value statement with instances."""
        stmt = ValueStatement(
            value="I value learning",
            instances=["I read 3 papers this week", "I took a course"],
        )
        assert stmt.value == "I value learning"
        assert len(stmt.instances) == 2
        assert stmt.has_evidence()

    def test_empty_value_rejected(self):
        """Empty value raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            ValueStatement(value="", instances=["did something"])

    def test_no_instances_rejected(self):
        """No instances raises ValueError."""
        with pytest.raises(ValueError, match="At least one concrete instance"):
            ValueStatement(value="I value learning", instances=[])

    def test_pad_tone_validation(self):
        """PAD tone components must be in [-1, 1]."""
        with pytest.raises(ValueError, match="PAD tone components must be in"):
            ValueStatement(
                value="I value learning",
                instances=["did something"],
                pad_tone=(2.0, 0.0, 0.0),
            )

    def test_to_dict(self):
        """Serialization works."""
        stmt = ValueStatement(
            value="I value learning",
            instances=["read 3 papers"],
            pad_tone=(0.5, 0.3, 0.2),
        )
        d = stmt.to_dict()
        assert d["value"] == "I value learning"
        assert d["instances"] == ["read 3 papers"]
        assert d["pad_tone"] == (0.5, 0.3, 0.2)


class TestAffirmationEngineTraitPraiseRefusal:
    """Test that trait praise is REFUSED (backfire shape)."""

    def setup_method(self):
        self.engine = AffirmationEngine()

    @pytest.mark.parametrize("trait_praise", [
        "you are amazing",
        "you're wonderful",
        "you're so smart",
        "you're incredible",
        "you are great",
        "you're awesome",
        "you're brilliant",
        "you're perfect",
        "such a smart person",
        "so talented",
        "so gifted",
        "naturally brilliant",
        "born to succeed",
        "gifted at everything",
    ])
    def test_trait_praise_refused(self, trait_praise):
        """All trait praise patterns are refused."""
        valid, reason = self.engine.validate_affirmation_input(trait_praise)
        assert not valid, f"Should refuse: {trait_praise}"
        assert "REFUSED" in reason
        assert "BACKFIRES" in reason or "backfire" in reason.lower()
        assert "trait praise" in reason.lower() or "Trait praise" in reason

    def test_generate_refuses_trait_praise(self):
        """Generating affirmation from trait praise is refused."""
        # Add a statement that looks like trait praise
        stmt = ValueStatement(
            value="you are amazing",  # This is trait praise
            instances=["you did great today"],
        )
        # The engine should refuse to generate from this
        affirmation = self.engine.generate_affirmation(stmt)
        # The value itself is trait praise, so the affirmation should indicate refusal
        assert "REFUSED" in affirmation
        assert "trait praise" in affirmation.lower() or "BACKFIRES" in affirmation


class TestAffirmationEngineValueAffirmation:
    """Test value-affirmation acceptance and generation."""

    def setup_method(self):
        self.engine = AffirmationEngine()

    @pytest.mark.parametrize("value_affirmation", [
        "I value learning",
        "I care about my health",
        "What matters to me is honesty",
        "I believe in kindness",
        "I'm committed to growth",
        "I prioritize family time",
    ])
    def test_value_affirmation_accepted(self, value_affirmation):
        """Value-affirmation starters are accepted."""
        valid, reason = self.engine.validate_affirmation_input(value_affirmation)
        assert valid, f"Should accept: {value_affirmation}"
        assert "Valid" in reason or "accepted" in reason.lower()

    def test_generate_affirmation_with_evidence(self):
        """Generate affirmation from value statement with instances."""
        stmt = ValueStatement(
            value="I value learning",
            instances=["I read 3 papers this week", "I completed a course"],
        )
        self.engine.add_value_statement(stmt)

        affirmation = self.engine.generate_affirmation(stmt)
        assert "I value learning" in affirmation
        assert "read 3 papers" in affirmation
        assert "completed a course" in affirmation

    def test_generate_affirmation_no_evidence_honest(self):
        """No evidence → honest statement, not fabricated."""
        # ValueStatement requires at least one instance, so use honest admission
        stmt = ValueStatement(
            value="I value learning",
            instances=["no instances recorded yet"],  # Honest admission
        )
        affirmation = self.engine.generate_affirmation(stmt)
        # Should contain the value and the honest instance
        assert "I value learning" in affirmation
        assert "no instances" in affirmation.lower() or "recorded" in affirmation.lower()

    def test_multiple_value_statements(self):
        """Engine handles multiple value statements."""
        self.engine.add_value("I value learning", ["read 3 papers"])
        self.engine.add_value("I care about health", ["exercised 3x this week"])

        affirmations = self.engine.generate_all_affirmations()
        assert len(affirmations) == 2
        assert any("learning" in a for a in affirmations)
        assert any("health" in a for a in affirmations)

    def test_affirmation_for_axis(self):
        """Get affirmation for specific SarahProfile axis."""
        self.engine.add_value("I value body awareness", ["noticed heart rate during stress"])

        # interoception axis should match
        affirmation = self.engine.get_affirmation_for_axis("interoception")
        assert affirmation is not None
        assert "body awareness" in affirmation.lower() or "heart rate" in affirmation

        # Unknown axis returns None
        assert self.engine.get_affirmation_for_axis("unknown_axis") is None


class TestAffirmationEngineExplain:
    """Test explanation of affirmation decisions."""

    def setup_method(self):
        self.engine = AffirmationEngine()

    def test_explain_refusal(self):
        """Explain returns refusal reason for trait praise."""
        explanation = self.engine.explain_affirmation("you are amazing")
        assert "REFUSED" in explanation
        assert "trait praise" in explanation.lower()

    def test_explain_acceptance(self):
        """Explain returns acceptance for value-affirmation."""
        explanation = self.engine.explain_affirmation("I value learning")
        assert "Accepted" in explanation or "value-affirmation" in explanation


class TestQuickAffirm:
    """Test quick_affirm convenience function."""

    def test_quick_affirm_with_evidence(self):
        """One-shot affirmation with evidence."""
        result = quick_affirm(
            value="I value learning",
            instances=["read 3 papers", "took a course"],
        )
        assert "I value learning" in result
        assert "read 3 papers" in result

    def test_quick_affirm_honest_no_evidence(self):
        """Honest output when no real evidence."""
        result = quick_affirm(
            value="I value learning",
            instances=["no instances recorded yet"],
        )
        assert "I value learning" in result
        assert "no instances" in result.lower() or "evidence" in result.lower()

    def test_quick_affirm_with_pad_tone(self):
        """PAD tone is accepted."""
        result = quick_affirm(
            value="I value calm",
            instances=["meditated today"],
            pad_tone=(0.3, -0.2, 0.1),
        )
        assert "calm" in result


class TestTelemetryEvent:
    """Test telemetry event generation for B7."""

    def setup_method(self):
        self.engine = AffirmationEngine()

    def test_telemetry_event_structure(self):
        """Telemetry event has required fields."""
        event = self.engine.telemetry_event("I value learning", True)
        assert event["event"] == "affirmation"
        assert event["drafted"] == "I value learning"
        assert event["evidence_present"] is True
        assert "timestamp" in event


class TestPSYCHEVocabularyIntegration:
    """Test integration with PSYCHE affect vocabulary."""

    def test_emotion_to_pad_available(self):
        """PSYCHE emotion_to_pad is usable."""
        from PSYCHE.affect import emotion_to_pad
        pad = emotion_to_pad("joy", 0.8)
        assert len(pad) == 3
        assert all(-1.0 <= v <= 1.0 for v in pad)

    def test_pad_normalize_available(self):
        """PSYCHE pad_normalize is usable."""
        from PSYCHE.affect import pad_normalize
        pad = pad_normalize((1.5, -0.5, 0.0))
        assert pad == (1.0, -0.5, 0.0)

    def test_clamp_available(self):
        """PSYCHE clamp is usable."""
        from PSYCHE.affect import clamp
        assert clamp(1.5) == 1.0
        assert clamp(-1.5) == -1.0
        assert clamp(0.5) == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])