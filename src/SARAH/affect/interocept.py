"""
M8 — Interoception Bridge (Lane 3, B3)

Maps body signals to the SarahProfile interoception axis using the PSYCHE
affect vocabulary (PAD, OCC, regulation). The interoception axis in SarahProfile
measures internal body awareness (low ↔ high). This module does NOT mint a
second vocabulary; it reuses PSYCHE.affect + PSYCHE.elicitation and provides
a structured bridge for Sarah-specific signal elicitation.

Rules (from design):
- 'not sure' is a first-class answer in every prompt; free text is never required
- All elicitation uses the PAD/OCC vocabulary from PSYCHE.affect
- Interoception signals are mapped to the SarahProfile.interoception axis [0, 1]
- No diagnostic-gated features; no therapy chatbot without M13 boundary
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from enum import Enum

from PSYCHE.affect import (
    pad_normalize,
    pad_distance,
    pad_blend,
    appraise_event,
    appraise_action,
    appraise_object,
    emotion_to_pad,
    temperament,
    reappraise_desirability,
    suppress_display,
    express,
    td_appraisal,
    clamp,
)
from PSYCHE.elicitation import (
    INSTRUMENT_VERSION,
    SCALE,
    SCALE_LABELS,
    SCALE_MIDPOINT,
    CONSTRUCTS,
    ITEMS,
    AFFECT_ITEMS,
    Session,
    Record,
    IncompleteSession,
    score_session,
    new_session,
    homogeneity,
    as_pad_construct_pairs,
)
from SARAH.profile import (
    SarahProfile,
    AXES,
    ALL_AXES,
    AXIS_MEANING,
    canonical_axis,
)


class BodySignal(str, Enum):
    """Body signals for interoceptive elicitation — mapped to PAD space."""
    HEART_RATE = "heart_rate"          # high arousal, variable valence
    BREATH = "breath"                  # arousal regulation anchor
    MUSCLE_TENSION = "muscle_tension"  # high arousal, negative valence
    TEMPERATURE = "temperature"        # physiological state
    GUT_SENSATION = "gut_sensation"    # interoceptive valence signal
    FATIGUE = "fatigue"                # low arousal, negative valence
    ENERGY = "energy"                  # high arousal, positive valence


@dataclass(frozen=True)
class InteroceptVocabulary:
    """Maps body signals to PAD space using PSYCHE affect vocabulary.

    The mapping uses OCC families from PSYCHE.affect as the semantic bridge.
    Each body signal has a canonical PAD direction and intensity range.
    """
    # Body signal -> (PAD tuple, OCC family, typical intensity)
    SIGNAL_MAP = {
        BodySignal.HEART_RATE:      ((0.0, 0.8, 0.1), "fear", 0.7),
        BodySignal.BREATH:          ((0.1, 0.3, 0.5), "relief", 0.5),
        BodySignal.MUSCLE_TENSION:  ((-0.4, 0.7, -0.2), "distress", 0.6),
        BodySignal.TEMPERATURE:     ((0.0, 0.4, 0.0), "hope", 0.3),
        BodySignal.GUT_SENSATION:   ((-0.3, 0.5, -0.1), "fear", 0.5),
        BodySignal.FATIGUE:         ((-0.6, -0.3, -0.4), "distress", 0.7),
        BodySignal.ENERGY:          ((0.7, 0.6, 0.5), "joy", 0.6),
    }

    @classmethod
    def pad_for(cls, signal: BodySignal) -> tuple[float, float, float]:
        """Return canonical PAD tuple for a body signal."""
        return cls.SIGNAL_MAP[signal][0]

    @classmethod
    def occ_family(cls, signal: BodySignal) -> str:
        """Return canonical OCC family for a body signal."""
        return cls.SIGNAL_MAP[signal][1]

    @classmethod
    def typical_intensity(cls, signal: BodySignal) -> float:
        """Return typical intensity for a body signal."""
        return cls.SIGNAL_MAP[signal][2]

    @classmethod
    def all_signals(cls) -> list[BodySignal]:
        return list(cls.SIGNAL_MAP.keys())


class Interocept:
    """Interoception Bridge — maps body signals to SarahProfile.interoception axis.

    Uses PSYCHE affect vocabulary (PAD, OCC, regulation) as the semantic layer.
    The interoception axis in SarahProfile measures internal body awareness
    (0.0 = low awareness, 1.0 = high awareness).
    """

    # The interoception axis index in SarahProfile.AXES
    AXIS_NAME = "interoception"
    AXIS_INDEX = AXES.index(AXIS_NAME)

    def __init__(self, profile: SarahProfile | None = None):
        self.profile = profile or SarahProfile()
        self._signal_history: list[tuple[BodySignal, float, float]] = []  # (signal, intensity, timestamp)

    def elicit_signal(self, signal: BodySignal, user_response: float | None) -> float | None:
        """Elicit one body signal from user.

        Args:
            signal: The body signal to elicit
            user_response: User's 0-4 rating (None = "not sure" / skipped)

        Returns:
            Normalized intensity in [0, 1] or None if skipped
        """
        if user_response is None:
            return None  # "not sure" is a first-class answer

        # Validate response is in scale
        if not isinstance(user_response, (int, float)) or user_response not in SCALE:
            raise ValueError(f"Response must be in {SCALE}, got {user_response}")

        # Normalize 0-4 to 0-1
        intensity = float(user_response) / max(SCALE)
        return intensity

    def record_signal(self, signal: BodySignal, intensity: float, timestamp: float) -> None:
        """Record a body signal observation."""
        if not 0.0 <= intensity <= 1.0:
            raise ValueError(f"Intensity must be in [0, 1], got {intensity}")
        self._signal_history.append((signal, intensity, timestamp))

    def compute_interoception_score(self, window_seconds: float = 3600.0) -> float | None:
        """Compute interoception axis value from recent signals.

        Uses PSYCHE affect vocabulary: maps body signals to PAD, then to
        interoception axis via the semantic mapping in SarahProfile.

        Args:
            window_seconds: Time window for recent signals (default 1 hour)

        Returns:
            Interoception score in [0, 1] or None if no signals in window
        """
        import time
        now = time.time()
        cutoff = now - window_seconds

        recent = [
            (signal, intensity)
            for signal, intensity, ts in self._signal_history
            if ts >= cutoff
        ]

        if not recent:
            return None

        # Map each signal through PSYCHE vocabulary to PAD, then aggregate
        pad_sum = (0.0, 0.0, 0.0)
        total_weight = 0.0

        for signal, intensity in recent:
            pad = InteroceptVocabulary.pad_for(signal)
            weight = intensity * InteroceptVocabulary.typical_intensity(signal)
            pad_sum = tuple(pad_sum[i] + pad[i] * weight for i in range(3))
            total_weight += weight

        if total_weight == 0:
            return None

        avg_pad = tuple(v / total_weight for v in pad_sum)

        # Map PAD to interoception axis: Pleasure dimension is the primary
        # correlate (positive body awareness → high interoception). Arousal
        # and Dominance modulate.
        p, a, d = avg_pad
        # Pleasure (valence) is primary: -1..1 → 0..1
        valence_score = (p + 1.0) / 2.0
        # Arousal contributes: moderate arousal = better awareness
        arousal_score = 1.0 - abs(a - 0.5) * 2.0
        # Dominance contributes: agency over body = awareness
        dominance_score = (d + 1.0) / 2.0

        # Weighted combination: valence 50%, arousal 25%, dominance 25%
        interoception = (
            0.5 * valence_score +
            0.25 * max(0.0, arousal_score) +
            0.25 * dominance_score
        )

        return clamp(interoception, 0.0, 1.0)

    def update_profile(self, window_seconds: float = 3600.0) -> SarahProfile:
        """Update the SarahProfile with computed interoception score."""
        score = self.compute_interoception_score(window_seconds)
        if score is not None:
            # Create new profile with updated interoception
            current_dict = self.profile.to_dict()
            current_dict[self.AXIS_NAME] = score
            self.profile = SarahProfile.from_dict(current_dict)
        return self.profile

    def get_vocabulary_prompt(self, signal: BodySignal) -> str:
        """Get the elicitation prompt for a body signal.

        Uses PSYCHE.elicitation AFFECT_ITEMS style: direct self-report,
        'not sure' always available, no free text required.
        """
        signal_names = {
            BodySignal.HEART_RATE: "your heart rate",
            BodySignal.BREATH: "your breathing",
            BodySignal.MUSCLE_TENSION: "muscle tension in your body",
            BodySignal.TEMPERATURE: "your body temperature",
            BodySignal.GUT_SENSATION: "sensations in your gut/stomach",
            BodySignal.FATIGUE: "fatigue or exhaustion",
            BodySignal.ENERGY: "energy or vitality",
        }
        name = signal_names.get(signal, signal.value)
        return (
            f"Right now, how noticeable is {name}?\n"
            f"0 = not at all, 1 = barely, 2 = somewhat, 3 = quite, 4 = extremely\n"
            f"(You can skip any signal — 'not sure' is always a valid answer)"
        )

    def run_full_elicitation(self, responses: dict[BodySignal, float | None]) -> SarahProfile:
        """Run full interoception elicitation for all body signals.

        Args:
            responses: Dict mapping BodySignal to user response (0-4 or None)

        Returns:
            Updated SarahProfile with interoception axis populated
        """
        import time
        now = time.time()

        for signal in InteroceptVocabulary.all_signals():
            response = responses.get(signal)
            intensity = self.elicit_signal(signal, response)
            if intensity is not None:
                self.record_signal(signal, intensity, now)

        return self.update_profile()

    def explain_interoception(self) -> str:
        """Return explanation of current interoception axis value."""
        return self.profile.explain(self.AXIS_NAME)


# Convenience function for direct use
def interoception_from_signals(
    signals: dict[BodySignal, float],
    profile: SarahProfile | None = None
) -> SarahProfile:
    """Create/update profile from body signal dict.

    Args:
        signals: Dict of BodySignal -> normalized intensity (0-1)
        profile: Optional existing profile to update

    Returns:
        SarahProfile with interoception axis populated
    """
    interp = Interocept(profile)
    import time
    now = time.time()
    for signal, intensity in signals.items():
        interp.record_signal(signal, intensity, now)
    return interp.update_profile()