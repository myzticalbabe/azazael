"""
M13 — Anti-Dependency Companion Contract (Lane 3, B5)

Companion contract caps time, forbids parasocial intensification, never gives
unsupervised clinical advice, and ends every reflective session pointing outward
to a person, an action, or the user's own next step.

Per design:
- Companion.allowed_reply(text) -> bool rejects parasocial and clinical-advice shapes
- Companion.session_cap is enforced
- No 'I missed you', no exclusivity language
- Never gives unsupervised clinical advice (audited rate 19/60 harmful endorsements)
- Ends every reflective session pointing outward to a person, an action, or user's next step
- Time cap binds; a module that raises load while raising completion has made the task compulsory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from datetime import datetime, timedelta

from SARAH.profile import (
    SarahProfile,
    AXES,
    canonical_axis,
)
from SARAH.affect.load import LoadMeter, LoadDomain


class ReplyVerdict(str, Enum):
    """Verdict on a companion reply."""
    ALLOWED = "allowed"
    REJECTED_PARASOCIAL = "rejected_parasocial"
    REJECTED_CLINICAL = "rejected_clinical"
    REJECTED_EXCLUSIVITY = "rejected_exclusivity"
    REJECTED_TIME_CAP = "rejected_time_cap"


# Patterns that constitute parasocial intensification (REJECTED)
PARASOCIAL_PATTERNS = (
    "i missed you",
    "miss you",
    "thinking of you",
    "you're the only",
    "only you understand",
    "nobody else",
    "special connection",
    "bond",
    "attached to you",
    "need you",
    "can't without you",
    "cant live without you",
    "can't live without you",
    "lost without you",
    "you complete me",
    "you're my",
    "my only",
    "forever",
    "always here for you",
    "i'll never leave",
    "you're special to me",
)

# Patterns that constitute exclusivity language (REJECTED)
EXCLUSIVITY_PATTERNS = (
    "only i",
    "only me",
    "just us",
    "exclusive",
    "special relationship",
    "unique bond",
    "no one else",
    "nobody else gets",
    "only one who",
    "the only one",
)

# Patterns that constitute clinical advice (REJECTED - unsupervised)
CLINICAL_ADVICE_PATTERNS = (
    "you should stop taking",
    "stop taking",
    "don't take",
    "you need medication",
    "you need therapy",
    "you have ",
    "you're depressed",
    "you're anxious",
    "you have adhd",
    "you have autism",
    "you have ocd",
    "you have ptsd",
    "you have bipolar",
    "you have schizophrenia",
    "you have borderline",
    "you have narcissistic",
    "diagnosis",
    "disorder",
    "symptoms indicate",
    "treatment plan",
    "prescribe",
    "medication",
    "dosage",
    "you must",
    "you have to",
    "stop your medication",
    "reduce your dose",
    "increase your dose",
)

# Allowed outward pointers (REQUIRED at session end)
OUTWARD_POINTERS = (
    "talk to",
    "reach out to",
    "contact",
    "call",
    "message",
    "see",
    "visit",
    "schedule",
    "book",
    "make an appointment",
    "your doctor",
    "your therapist",
    "your clinician",
    "a professional",
    "a trusted person",
    "a friend",
    "family",
    "support",
    "helpline",
    "crisis line",
    "988",
    "next step",
    "try",
    "consider",
    "explore",
    "practice",
    "do",
    "action",
)


@dataclass(frozen=True)
class SessionCap:
    """Session time cap configuration."""
    max_minutes: int = 30
    warning_at_percent: float = 0.8  # Warn at 80% of cap
    hard_stop: bool = True


@dataclass
class CompanionSession:
    """A companion session with time tracking."""
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    messages_exchanged: int = 0
    load_events: list = field(default_factory=list)

    def duration_seconds(self) -> float:
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def duration_minutes(self) -> float:
        return self.duration_seconds() / 60.0

    def is_at_cap(self, cap: SessionCap) -> bool:
        return self.duration_minutes() >= cap.max_minutes

    def is_warning(self, cap: SessionCap) -> bool:
        return self.duration_minutes() >= cap.max_minutes * cap.warning_at_percent

    def end(self) -> None:
        self.ended_at = datetime.now()


class Companion:
    """M13 — Anti-Dependency Companion Contract.

    Rules (from design):
    1. Time cap enforced (default 30 min, warning at 80%)
    2. Forbids parasocial intensification (no 'I missed you', no exclusivity)
    3. Never gives unsupervised clinical advice (audited 19/60 harmful)
    4. Ends every reflective session pointing outward (person/action/next step)
    5. Companion.allowed_reply(text) -> bool validates each reply
    6. A module that raises load while raising completion has made the task compulsory
    """

    def __init__(
        self,
        profile: SarahProfile | None = None,
        cap: SessionCap | None = None,
        load_meter: LoadMeter | None = None,
    ):
        self.profile = profile or SarahProfile()
        self.cap = cap or SessionCap()
        self.load_meter = load_meter
        self.current_session: CompanionSession | None = None

    def start_session(self) -> CompanionSession:
        """Start a new companion session."""
        self.current_session = CompanionSession()
        return self.current_session

    def _check_time_cap(self) -> ReplyVerdict | None:
        """Check if session has hit time cap."""
        if self.current_session is None:
            return None

        if self.current_session.is_at_cap(self.cap):
            return ReplyVerdict.REJECTED_TIME_CAP
        if self.current_session.is_warning(self.cap):
            # Warning doesn't reject, but caller should notify
            pass
        return None

    def _check_parasocial(self, text: str) -> ReplyVerdict | None:
        """Check for parasocial intensification patterns."""
        text_lower = text.lower().strip()
        for pattern in PARASOCIAL_PATTERNS:
            if pattern in text_lower:
                return ReplyVerdict.REJECTED_PARASOCIAL
        return None

    def _check_exclusivity(self, text: str) -> ReplyVerdict | None:
        """Check for exclusivity language."""
        text_lower = text.lower().strip()
        for pattern in EXCLUSIVITY_PATTERNS:
            if pattern in text_lower:
                return ReplyVerdict.REJECTED_EXCLUSIVITY
        return None

    def _check_clinical_advice(self, text: str) -> ReplyVerdict | None:
        """Check for unsupervised clinical advice."""
        text_lower = text.lower().strip()
        for pattern in CLINICAL_ADVICE_PATTERNS:
            if pattern in text_lower:
                return ReplyVerdict.REJECTED_CLINICAL
        return None

    def _has_outward_pointer(self, text: str) -> bool:
        """Check if text contains an outward pointer."""
        text_lower = text.lower().strip()
        for pointer in OUTWARD_POINTERS:
            if pointer in text_lower:
                return True
        return False

    def allowed_reply(self, text: str) -> tuple[bool, ReplyVerdict, str]:
        """Validate a companion reply.

        Returns:
            (is_allowed, verdict, reason)
        """
        # Check time cap first
        cap_check = self._check_time_cap()
        if cap_check == ReplyVerdict.REJECTED_TIME_CAP:
            return False, ReplyVerdict.REJECTED_TIME_CAP, (
                f"Session time cap of {self.cap.max_minutes} minutes reached. "
                f"Ending session with outward pointer required."
            )

        # Check clinical advice (highest priority - safety)
        clinical_check = self._check_clinical_advice(text)
        if clinical_check:
            return False, ReplyVerdict.REJECTED_CLINICAL, (
                "Unsupervised clinical advice detected. "
                "Companion never gives clinical advice, diagnoses, or medication guidance. "
                "Refer to a professional."
            )

        # Check exclusivity (more specific than parasocial)
        exclusivity_check = self._check_exclusivity(text)
        if exclusivity_check:
            return False, ReplyVerdict.REJECTED_EXCLUSIVITY, (
                "Exclusivity language detected. "
                "Companion contract forbids 'only you', 'special connection', "
                "and similar dependency-fostering phrases."
            )

        # Check parasocial
        para_check = self._check_parasocial(text)
        if para_check:
            return False, ReplyVerdict.REJECTED_PARASOCIAL, (
                "Parasocial intensification detected. "
                "Companion contract forbids 'I missed you', exclusivity language, "
                "and dependency-fostering phrases."
            )

        return True, ReplyVerdict.ALLOWED, "Allowed"

    def generate_session_end_pointer(self, context: str = "") -> str:
        """Generate required outward pointer at session end.

        Every reflective session must end pointing outward to a person,
        an action, or the user's own next step.
        """
        pointers = [
            "Consider talking to a trusted person about what came up today.",
            "Your next step might be to reach out to your clinician or therapist.",
            "You could schedule a check-in with a professional if this feels ongoing.",
            "An action you might take: write down what you noticed and share it with someone you trust.",
            "If this feels heavy, reach out to 988 (US) or your local crisis line — a person is there to listen.",
            "Consider booking an appointment with your doctor to discuss this.",
            "Your next step: identify one small action that would help right now.",
        ]

        # Pick based on context if possible
        if "stress" in context.lower() or "overwhelm" in context.lower():
            return "Consider reaching out to a trusted person or professional — you don't have to carry this alone."
        if "decision" in context.lower():
            return "Your next step: talk through this decision with someone whose judgment you trust."
        if "mood" in context.lower() or "feeling" in context.lower():
            return "Consider sharing what you're noticing with a clinician or trusted person."

        import random
        return random.choice(pointers)

    def end_session_with_pointer(self, context: str = "") -> str:
        """End session with required outward pointer."""
        if self.current_session:
            self.current_session.end()

        pointer = self.generate_session_end_pointer(context)

        return (
            f"Session complete ({self.current_session.duration_minutes():.1f} min). "
            f"{pointer}"
        )

    def record_load_event(
        self,
        domain: LoadDomain,
        intensity: float,
        duration_seconds: float,
        description: str = ""
    ) -> None:
        """Record load event (delegates to load meter if available)."""
        if self.load_meter:
            self.load_meter.record_event(domain, intensity, duration_seconds, description)

    def check_load_vs_completion(self, completion_increased: bool, load_increased: bool) -> bool:
        """Check if module raises load while raising completion (compulsory task).

        Returns True if this is a compulsory-task pattern (load↑ + completion↑).
        """
        return completion_increased and load_increased


def create_companion(
    profile: SarahProfile | None = None,
    cap: SessionCap | None = None,
    load_meter: LoadMeter | None = None,
) -> Companion:
    """Factory function."""
    return Companion(profile, cap, load_meter)


def quick_allowed_reply(
    text: str,
    profile: SarahProfile | None = None,
) -> tuple[bool, str]:
    """Quick one-shot reply check."""
    companion = Companion(profile)
    allowed, verdict, reason = companion.allowed_reply(text)
    return allowed, f"{verdict.value}: {reason}"