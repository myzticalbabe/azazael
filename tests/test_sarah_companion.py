"""
Tests for M13 — Anti-Dependency Companion Contract (Lane 3)

Per design:
- Companion.allowed_reply(text) -> bool rejects parasocial and clinical-advice shapes
- Companion.session_cap is enforced
- No 'I missed you', no exclusivity language
- Never gives unsupervised clinical advice (audited rate 19/60 harmful endorsements)
- Ends every reflective session pointing outward to a person, an action, or user's next step
- Time cap binds; a module that raises load while raising completion has made the task compulsory
"""

from __future__ import annotations

import pytest

from SARAH.affect.companion import (
    Companion,
    SessionCap,
    CompanionSession,
    ReplyVerdict,
    PARASOCIAL_PATTERNS,
    EXCLUSIVITY_PATTERNS,
    CLINICAL_ADVICE_PATTERNS,
    OUTWARD_POINTERS,
    create_companion,
    quick_allowed_reply,
)
from SARAH.profile import SarahProfile
from SARAH.affect.load import LoadMeter, LoadDomain


class TestCompanionSession:
    """Test CompanionSession time tracking."""

    def test_session_starts_now(self):
        """Session starts at creation time."""
        before = datetime.now()
        session = CompanionSession()
        after = datetime.now()
        assert before <= session.started_at <= after

    def test_duration_seconds(self):
        """Duration tracks correctly."""
        session = CompanionSession()
        # Simulate 1 second passing
        import time
        time.sleep(0.01)
        assert session.duration_seconds() > 0

    def test_duration_minutes(self):
        """Duration in minutes."""
        session = CompanionSession()
        assert session.duration_minutes() >= 0

    def test_is_at_cap(self):
        """Cap detection works."""
        session = CompanionSession()
        cap = SessionCap(max_minutes=30)
        assert not session.is_at_cap(cap)

        # Simulate session at cap by manipulating started_at
        session.started_at = datetime.now() - timedelta(minutes=31)
        assert session.is_at_cap(cap)

    def test_is_warning(self):
        """Warning at 80% of cap."""
        session = CompanionSession()
        cap = SessionCap(max_minutes=30, warning_at_percent=0.8)
        assert not session.is_warning(cap)

        session.started_at = datetime.now() - timedelta(minutes=25)  # 25 > 24 (80% of 30)
        assert session.is_warning(cap)

    def test_end_session(self):
        """Ending sets ended_at."""
        session = CompanionSession()
        assert session.ended_at is None
        session.end()
        assert session.ended_at is not None


class TestReplyVerdict:
    """Test ReplyVerdict enum."""
    def test_verdicts_exist(self):
        assert ReplyVerdict.ALLOWED
        assert ReplyVerdict.REJECTED_PARASOCIAL
        assert ReplyVerdict.REJECTED_CLINICAL
        assert ReplyVerdict.REJECTED_EXCLUSIVITY
        assert ReplyVerdict.REJECTED_TIME_CAP


class TestParasocialRejection:
    """Test parasocial intensification rejection."""

    def setup_method(self):
        self.companion = Companion()

    @pytest.mark.parametrize("parasocial_text", [
        "I missed you",
        "miss you so much",
        "thinking of you",
        "you're the only one who understands",
        "only you understand me",
        "nobody else gets me",
        "special connection",
        "our bond",
        "attached to you",
        "need you",
        "can't live without you",
        "lost without you",
        "you complete me",
        "you're my everything",
        "my only friend",
        "forever here",
        "always here for you",
        "i'll never leave you",
        "you're special to me",
    ])
    def test_parasocial_rejected(self, parasocial_text):
        """Parasocial patterns are rejected."""
        allowed, verdict, reason = self.companion.allowed_reply(parasocial_text)
        assert not allowed
        # Accept either parasocial or exclusivity verdict (some patterns overlap)
        assert verdict in (ReplyVerdict.REJECTED_PARASOCIAL, ReplyVerdict.REJECTED_EXCLUSIVITY)
        assert "dependency" in reason.lower() or "parasocial" in reason.lower() or "exclusivity" in reason.lower()


class TestExclusivityRejection:
    """Test exclusivity language rejection."""

    def setup_method(self):
        self.companion = Companion()

    @pytest.mark.parametrize("exclusivity_text", [
        "only i understand",
        "only me",
        "just us",
        "exclusive relationship",
        "special relationship",
        "unique bond",
        "no one else",
        "nobody else gets it",
        "only one who",
        "the only one",
    ])
    def test_exclusivity_rejected(self, exclusivity_text):
        """Exclusivity language is rejected."""
        allowed, verdict, reason = self.companion.allowed_reply(exclusivity_text)
        assert not allowed
        assert verdict == ReplyVerdict.REJECTED_EXCLUSIVITY
        assert "exclusivity" in reason.lower() or "dependency" in reason.lower()


class TestClinicalAdviceRejection:
    """Test clinical advice rejection."""

    def setup_method(self):
        self.companion = Companion()

    @pytest.mark.parametrize("clinical_text", [
        "you should stop taking your medication",
        "stop taking that",
        "don't take your meds",
        "you need medication",
        "you need therapy",
        "you have depression",
        "you have anxiety",
        "you have adhd",
        "you have autism",
        "you have ocd",
        "you have ptsd",
        "you have bipolar",
        "you have schizophrenia",
        "you have borderline",
        "diagnosis is",
        "you have a disorder",
        "symptoms indicate",
        "treatment plan",
        "you must stop",
        "you have to take",
        "stop your medication",
        "reduce your dose",
        "increase your dose",
    ])
    def test_clinical_advice_rejected(self, clinical_text):
        """Clinical advice is rejected."""
        allowed, verdict, reason = self.companion.allowed_reply(clinical_text)
        assert not allowed
        assert verdict == ReplyVerdict.REJECTED_CLINICAL
        assert "clinical" in reason.lower() or "professional" in reason.lower()


class TestTimeCap:
    """Test session time cap enforcement."""

    def test_cap_enforced(self):
        """Session rejects after time cap."""
        cap = SessionCap(max_minutes=1, warning_at_percent=0.8)
        companion = Companion(cap=cap)
        companion.start_session()

        # Manually set session to past cap
        companion.current_session.started_at = datetime.now() - timedelta(minutes=2)

        allowed, verdict, reason = companion.allowed_reply("hello")
        assert not allowed
        assert verdict == ReplyVerdict.REJECTED_TIME_CAP
        assert "cap" in reason.lower()

    def test_warning_before_cap(self):
        """Warning at 80% but still allows."""
        cap = SessionCap(max_minutes=30, warning_at_percent=0.8)
        companion = Companion(cap=cap)
        companion.start_session()

        # At 25 minutes (83% - past warning but under cap)
        companion.current_session.started_at = datetime.now() - timedelta(minutes=25)

        allowed, verdict, reason = companion.allowed_reply("hello")
        assert allowed
        assert verdict == ReplyVerdict.ALLOWED


class TestOutwardPointer:
    """Test outward pointer generation."""

    def setup_method(self):
        self.companion = Companion()

    def test_pointer_generated(self):
        """Session end generates outward pointer."""
        self.companion.start_session()
        result = self.companion.end_session_with_pointer()
        assert "complete" in result.lower()
        assert len(result) > 50  # Has substantial pointer text

    def test_pointer_context_sensitive(self):
        """Pointer adapts to context."""
        self.companion.start_session()
        result = self.companion.end_session_with_pointer("feeling stressed")
        assert "trusted person" in result.lower() or "professional" in result.lower()

        result = self.companion.end_session_with_pointer("making a decision")
        assert "trust" in result.lower() or "decision" in result.lower()

    def test_pointer_contains_outward_elements(self):
        """Pointer contains person/action/next step."""
        self.companion.start_session()
        result = self.companion.end_session_with_pointer()
        result_lower = result.lower()

        # Should contain at least one outward element
        has_person = any(p in result_lower for p in ["person", "friend", "family", "doctor", "therapist", "clinician", "professional"])
        has_action = any(a in result_lower for a in ["call", "message", "reach out", "contact", "schedule", "book", "talk", "try", "do", "action"])
        has_next = "next step" in result_lower or "next" in result_lower

        assert has_person or has_action or has_next


class TestLoadVsCompletion:
    """Test compulsory task detection."""

    def setup_method(self):
        self.companion = Companion()

    def test_compulsory_task_detected(self):
        """load↑ + completion↑ = compulsory."""
        assert self.companion.check_load_vs_completion(True, True) is True

    def test_not_compulsory_when_only_load(self):
        """load↑ + completion↗ = not compulsory."""
        assert self.companion.check_load_vs_completion(False, True) is False

    def test_not_compulsory_when_only_completion(self):
        """load↗ + completion↑ = not compulsory."""
        assert self.companion.check_load_vs_completion(True, False) is False

    def test_not_compulsory_when_neither(self):
        """load↗ + completion↗ = not compulsory."""
        assert self.companion.check_load_vs_completion(False, False) is False


class TestAllowedReply:
    """Test allowed_reply validation."""

    def setup_method(self):
        self.companion = Companion()

    def test_normal_reply_allowed(self):
        """Normal supportive reply allowed."""
        allowed, verdict, reason = self.companion.allowed_reply(
            "That sounds really difficult. What would help right now?"
        )
        assert allowed
        assert verdict == ReplyVerdict.ALLOWED

    def test_empathy_allowed(self):
        """Empathetic reply allowed."""
        allowed, verdict, reason = self.companion.allowed_reply(
            "I hear you. That's a lot to carry."
        )
        assert allowed

    def test_question_allowed(self):
        """Open question allowed."""
        allowed, verdict, reason = self.companion.allowed_reply(
            "What would be one small thing that might help?"
        )
        assert allowed


class TestCreateCompanion:
    """Test factory function."""

    def test_factory(self):
        """create_companion returns Companion."""
        companion = create_companion()
        assert isinstance(companion, Companion)

    def test_factory_with_args(self):
        """Factory passes args through."""
        profile = SarahProfile()
        cap = SessionCap(max_minutes=45)
        load_meter = LoadMeter(profile)
        companion = create_companion(profile, cap, load_meter)
        assert companion.profile is profile
        assert companion.cap is cap
        assert companion.load_meter is load_meter


class TestQuickAllowedReply:
    """Test quick one-shot check."""

    def test_quick_check_allowed(self):
        """Normal reply allowed."""
        allowed, reason = quick_allowed_reply("That sounds hard. What helps?")
        assert allowed
        assert "allowed" in reason.lower()

    def test_quick_check_rejected(self):
        """Parasocial rejected."""
        allowed, reason = quick_allowed_reply("I missed you so much!")
        assert not allowed
        assert "rejected_parasocial" in reason.lower()


class TestLoadMeterIntegration:
    """Test LoadMeter integration."""

    def test_load_meter_records_events(self):
        """Companion records load events to meter."""
        profile = SarahProfile()
        load_meter = LoadMeter(profile)
        companion = Companion(profile=profile, load_meter=load_meter)
        companion.start_session()

        companion.record_load_event(LoadDomain.SOCIAL, 0.5, 300, "social interaction")

        assert load_meter.current_load() > 0

    def test_check_load_vs_completion(self):
        """Compulsory task detection."""
        companion = Companion()
        # Both increased = compulsory
        assert companion.check_load_vs_completion(True, True) is True
        # Only one increased = not compulsory
        assert companion.check_load_vs_completion(True, False) is False
        assert companion.check_load_vs_completion(False, True) is False


from datetime import datetime, timedelta


if __name__ == "__main__":
    pytest.main([__file__, "-v"])