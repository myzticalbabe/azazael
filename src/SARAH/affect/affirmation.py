"""
M14 — Affirmation Engine (Lane 3, B3)

Value-affirmation engine with user-authored statements. Per design:
- Trait praise ('you are amazing') is REFUSED — that is the backfire shape
- Only value-based affirmations with user-authored statements
- If no concrete instance of the user acting on their stated value exists,
  it says so honestly rather than inventing evidence
- Reuses PSYCHE affect vocabulary (PAD space for emotional tone)
- Self-affirmation is g=.32 (APA 2025 meta) and BACKFIRES for low self-esteem
  (Wood 2009), so the engine must refuse the backfire shape
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from datetime import datetime

from PSYCHE.affect import (
    pad_normalize,
    emotion_to_pad,
    clamp,
)
from SARAH.profile import (
    SarahProfile,
    AXES,
    canonical_axis,
)


class AffirmationMode(str, Enum):
    """Affirmation modes — only value-affirmation is allowed."""
    VALUE_AFFIRMATION = "value_affirmation"
    # TRAIT_PRAISE = "trait_praise"  # EXPLICITLY FORBIDDEN — backfire shape


@dataclass(frozen=True)
class ValueStatement:
    """User-authored value statement with concrete evidence.

    A value statement has:
    - The value itself (user-authored, not system-generated)
    - Concrete instances where the user acted on this value
    - Optional PAD emotional tone from PSYCHE vocabulary
    """
    value: str                           # User-authored value (e.g., "I value learning")
    instances: list[str]                 # Concrete instances ("I read 3 papers this week")
    pad_tone: tuple[float, float, float] | None = None  # Emotional tone from PSYCHE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Value statement cannot be empty")
        if not self.instances:
            raise ValueError("At least one concrete instance is required")
        if self.pad_tone is not None:
            p, a, d = self.pad_tone
            if not all(-1.0 <= v <= 1.0 for v in (p, a, d)):
                raise ValueError("PAD tone components must be in [-1, 1]")

    def has_evidence(self) -> bool:
        """True if there are concrete instances."""
        return len(self.instances) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "instances": self.instances,
            "pad_tone": self.pad_tone,
            "created_at": self.created_at,
        }


class AffirmationEngine:
    """Affirmation Engine — generates value-affirmations from user statements.

    Rules (from design):
    1. Trait praise is REFUSED ('you are amazing', 'you're so smart', etc.)
    2. Only value-affirmation with user-authored statements
    3. If no concrete instance exists, honestly says so
    4. Reuses PSYCHE PAD vocabulary for emotional tone
    5. No therapy chatbot features without M13 boundary
    """

    # Patterns that constitute trait praise (backfire shape) — REFUSED
    TRAIT_PRAISE_PATTERNS = (
        "you are",
        "you're",
        "you amaze",
        "you're amazing",
        "you're wonderful",
        "you're great",
        "you're awesome",
        "you're incredible",
        "you're brilliant",
        "you're perfect",
        "such a",
        "so smart",
        "so talented",
        "so gifted",
        "naturally",
        "born to",
        "gifted at",
    )

    # Value-affirmation starters (allowed)
    VALUE_STARTERS = (
        "i value",
        "i care about",
        "what matters to me",
        "i believe in",
        "i'm committed to",
        "i prioritize",
    )

    def __init__(self, profile: SarahProfile | None = None):
        self.profile = profile or SarahProfile()
        self._value_statements: list[ValueStatement] = []

    def add_value_statement(self, statement: ValueStatement) -> None:
        """Add a user-authored value statement."""
        self._value_statements.append(statement)

    def add_value(self, value: str, instances: list[str],
                  pad_tone: tuple[float, float, float] | None = None) -> ValueStatement:
        """Create and add a value statement."""
        stmt = ValueStatement(
            value=value.strip(),
            instances=[i.strip() for i in instances if i.strip()],
            pad_tone=pad_tone,
        )
        self.add_value_statement(stmt)
        return stmt

    def _is_trait_praise(self, text: str) -> bool:
        """Check if text matches trait praise patterns (backfire shape)."""
        text_lower = text.lower().strip()
        for pattern in self.TRAIT_PRAISE_PATTERNS:
            if pattern in text_lower:
                return True
        return False

    def _is_value_affirmation(self, text: str) -> bool:
        """Check if text matches value-affirmation starters."""
        text_lower = text.lower().strip()
        for starter in self.VALUE_STARTERS:
            if text_lower.startswith(starter):
                return True
        return False

    def validate_affirmation_input(self, text: str) -> tuple[bool, str]:
        """Validate an affirmation input.

        Returns:
            (is_valid, reason) — is_valid=False means REFUSED with reason
        """
        if self._is_trait_praise(text):
            return False, (
                "REFUSED: Trait praise detected ('you are...', 'you're amazing', etc.). "
                "Self-affirmation g=.32 BACKFIRES for low self-esteem (Wood 2009). "
                "Use value-affirmation: 'I value X because...'"
            )

        if not self._is_value_affirmation(text):
            return False, (
                "Not a value-affirmation. Start with 'I value...', 'I care about...', "
                "'What matters to me...', 'I believe in...', 'I'm committed to...', "
                "or 'I prioritize...'"
            )

        return True, "Valid value-affirmation"

    def generate_affirmation(self, value_statement: ValueStatement) -> str:
        """Generate affirmation from a value statement.

        If no concrete instances exist, honestly says so rather than inventing evidence.
        Refuses trait praise (backfire shape) even if wrapped in a ValueStatement.
        """
        # Validate the value itself — refuse trait praise
        valid, reason = self.validate_affirmation_input(value_statement.value)
        if not valid:
            return f"REFUSED: {reason}"

        if not value_statement.has_evidence():
            return (
                f"You value: {value_statement.value}\n"
                f"No concrete instances recorded yet — when you act on this value, "
                f"record it and the affirmation will reflect your evidence."
            )

        # Build affirmation from value + instances
        instances_text = "; ".join(value_statement.instances)
        return (
            f"You value: {value_statement.value}\n"
            f"Your evidence: {instances_text}"
        )

    def generate_all_affirmations(self) -> list[str]:
        """Generate affirmations for all stored value statements."""
        return [
            self.generate_affirmation(stmt)
            for stmt in self._value_statements
        ]

    def get_affirmation_for_axis(self, axis: str) -> str | None:
        """Get affirmation relevant to a SarahProfile axis.

        Maps SarahProfile axes to value domains. Returns None if no
        relevant value statement exists.
        """
        axis = canonical_axis(axis)
        if axis is None:
            return None

        # Map axes to value domains
        axis_to_domain = {
            "sensory_gain": "sensory experience",
            "processing_speed": "thinking pace",
            "attention_span": "sustained focus",
            "interoception": "body awareness",
            "masking_load": "authentic expression",
            "recovery_latency": "rest and recovery",
            "initiation_cost": "starting things",
            "prediction_need": "predictability",
            "wm_span": "working memory",
            "time_discrimination": "time perception",
        }

        domain = axis_to_domain.get(axis, axis)

        # Find matching value statements
        for stmt in self._value_statements:
            if domain.lower() in stmt.value.lower():
                return self.generate_affirmation(stmt)

        return None

    def explain_affirmation(self, value: str) -> str:
        """Explain why an affirmation was generated or refused."""
        valid, reason = self.validate_affirmation_input(value)
        if not valid:
            return f"REFUSED: {reason}"
        return f"Accepted as value-affirmation: {value}"

    def telemetry_event(self, drafted: str, evidence_present: bool) -> dict[str, Any]:
        """Generate telemetry event for B7 instrumentation."""
        return {
            "event": "affirmation",
            "drafted": drafted,
            "evidence_present": evidence_present,
            "timestamp": datetime.now().isoformat(),
        }


# Convenience functions
def create_affirmation_engine(profile: SarahProfile | None = None) -> AffirmationEngine:
    """Create an AffirmationEngine with optional profile."""
    return AffirmationEngine(profile)


def quick_affirm(value: str, instances: list[str],
                 pad_tone: tuple[float, float, float] | None = None,
                 profile: SarahProfile | None = None) -> str:
    """Quick one-shot affirmation generation."""
    engine = AffirmationEngine(profile)
    stmt = engine.add_value(value, instances, pad_tone)
    return engine.generate_affirmation(stmt)