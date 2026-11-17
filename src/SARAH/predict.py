"""
M6 — Predictability Packet (Sarah Build Instructions B1)

`packet(profile, next_n_steps)` describes what is about to happen *before* it
happens: what it is, when it starts, how long it lasts, what comes after, and
that the exit is reachable. `can_exit` is always True and is never conditional
on session state (B1 rule 5: exit is never gated).

The packet is reduce-only. `prediction_need` changes how much *notice* a person
gets, never how much *stimulus* arrives:

    low need  -> one announcement beat, several steps announced together
    high need -> more announcement beats, one change per beat, wider stagger

`simultaneous_changes` is pinned at 1 for every profile. B1's negative case is
usually stated as "high prediction_need produces fewer simultaneous changes",
but §5's cap forbids more than one modality changing at a time for anybody, so
the value saturates at the cap rather than going from 2 to 1. The axis moves
`announce_beats` up and `changes_per_announcement` / `stagger_s` down and out;
it never adds a step, and `len(steps)` is `next_n_steps` for every profile.

An unmeasured `prediction_need` (None) is reported as None with `basis` naming
it, rather than silently read as 0.5 -- the profile contract forbids a default
that is indistinguishable from a measurement.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


# §5 caps, named once so the packet cannot invent looser ones.
RAMP_S = 0.4
"""Minimum ramp between two changes, in seconds (§5: ramps >= 400 ms)."""

ANNOUNCEMENT_BEAT_S = 2.0
"""One announcement beat. A change is announced at least one beat early."""

STEP_S = 1.5
"""Nominal duration of one announced step."""

MAX_BEATS = 4
MAX_CHANGES_PER_ANNOUNCEMENT = 3
NEUTRAL_NEED = 0.5
"""The reading used ONLY when the axis is unmeasured, and named in `basis`."""

STEP_TEMPLATES = (
    "a change of scene",
    "the next instruction",
    "a short pause",
    "the next piece of information",
    "a change of pace",
)
"""Neutral step descriptions. A packet never invents new demands."""

MODALITIES = ("text", "audio", "visual")
"""The channel a step changes. One per tick, by construction."""


@dataclass(frozen=True)
class Step:
    """One announced change: what, when it starts, and on which single channel.

    `at_ms` is the offset the §5 floor is judged in. `at_s` is the same instant
    as a convenience float: subtracting two floats that are 400 ms apart can
    yield 0.3999999999999999, so a comparison in seconds would fail a packet
    that is exactly at the cap. The integer is the measurement; the float is a
    rendering of it.
    """

    index: int
    what: str
    at_ms: int
    at_s: float
    how_long_s: float
    modality: str


@dataclass(frozen=True)
class PredictabilityPacket:
    """What happens next, and how much notice precedes it."""

    what: str
    when: float
    how_long: float
    what_next: str
    can_exit: bool
    announce_beats: int
    changes_per_announcement: int
    simultaneous_changes: int
    stagger_s: float
    prediction_need: float | None
    basis: str
    steps: tuple[Step, ...]

    def to_dict(self) -> dict[str, Any]:
        """The packet as plain data (steps included), for telemetry or a UI."""
        return {
            "what": self.what,
            "when": self.when,
            "how_long": self.how_long,
            "what_next": self.what_next,
            "can_exit": self.can_exit,
            "announce_beats": self.announce_beats,
            "changes_per_announcement": self.changes_per_announcement,
            "simultaneous_changes": self.simultaneous_changes,
            "stagger_s": self.stagger_s,
            "prediction_need": self.prediction_need,
            "basis": self.basis,
            "steps": [
                {
                    "index": s.index,
                    "what": s.what,
                    "at_ms": s.at_ms,
                    "at_s": s.at_s,
                    "how_long_s": s.how_long_s,
                    "modality": s.modality,
                }
                for s in self.steps
            ],
        }


def _need(profile: Any) -> tuple[float, float | None, str]:
    """Read `prediction_need` without letting an unmeasured axis look measured.

    Returns (value used for pacing, value reported, basis sentence).
    """
    value = getattr(profile, "prediction_need", None)
    if value is None:
        return (
            NEUTRAL_NEED,
            None,
            "prediction_need: not measured yet; neutral notice used and reported",
        )
    return (
        float(value),
        float(value),
        f"prediction_need={float(value):.2f}",
    )


def announcement_beats(prediction_need: float | None) -> int:
    """How many beats of notice a change gets. Non-decreasing in need, 1..4."""
    if prediction_need is None:
        return 2
    return 1 + min(MAX_BEATS - 1, int(float(prediction_need) * 3 + 0.5))


def changes_per_announcement(prediction_need: float | None) -> int:
    """How many steps share one announcement. Non-increasing in need, 1..3."""
    if prediction_need is None:
        return 2
    if prediction_need < 1 / 3:
        return MAX_CHANGES_PER_ANNOUNCEMENT
    if prediction_need < 2 / 3:
        return 2
    return 1


def stagger_s(prediction_need: float | None) -> float:
    """Seconds between step starts. Never below the §5 ramp floor."""
    if prediction_need is None:
        return RAMP_S + NEUTRAL_NEED * (MAX_BEATS - RAMP_S)
    return RAMP_S + float(prediction_need) * (MAX_BEATS - RAMP_S)


def _validate_steps(next_n_steps: Any) -> int:
    # bool is an int subclass; `True` steps is a caller bug, not one step.
    if isinstance(next_n_steps, bool) or not isinstance(next_n_steps, int):
        raise TypeError(f"next_n_steps must be an int, got {type(next_n_steps)}")
    if next_n_steps < 1:
        raise ValueError(f"next_n_steps must be >= 1, got {next_n_steps}")
    return next_n_steps


def packet(profile: Any, next_n_steps: int) -> PredictabilityPacket:
    """Describe the next `next_n_steps` changes before any of them happens.

    Deterministic, no I/O, no model call. The only input that moves this packet
    is `prediction_need`; every other axis is irrelevant to notice.
    """
    n = _validate_steps(next_n_steps)
    value, reported, basis = _need(profile)

    beats = announcement_beats(value)
    per_beat = changes_per_announcement(value)
    stagger = stagger_s(value)

    first_at = beats * ANNOUNCEMENT_BEAT_S
    # Integer milliseconds: the 400 ms floor is exact, and no float error can
    # put two steps closer together than the cap allows.
    first_ms = int(round(first_at * 1000))
    step_ms = max(int(round(RAMP_S * 1000)), int(round(stagger * 1000)))
    steps = tuple(
        Step(
            index=i,
            what=STEP_TEMPLATES[i % len(STEP_TEMPLATES)],
            at_ms=first_ms + i * step_ms,
            at_s=round((first_ms + i * step_ms) / 1000, 3),
            how_long_s=STEP_S,
            modality=MODALITIES[i % len(MODALITIES)],
        )
        for i in range(n)
    )

    what = (
        f"{n} step{'s' if n != 1 else ''}, one change at a time, "
        f"{beats} beat{'s' if beats != 1 else ''} of notice before the first"
    )
    return PredictabilityPacket(
        what=what,
        when=round(first_at, 3),
        how_long=round((step_ms * (n - 1)) / 1000 + STEP_S, 3),
        what_next="nothing else begins until you ask for it; the exit stays open",
        # Always true, never conditional on session state.
        can_exit=True,
        announce_beats=beats,
        changes_per_announcement=per_beat,
        simultaneous_changes=1,
        stagger_s=round(stagger, 3),
        prediction_need=reported,
        basis=basis,
        steps=steps,
    )


__all__ = [
    "ANNOUNCEMENT_BEAT_S",
    "MAX_BEATS",
    "MAX_CHANGES_PER_ANNOUNCEMENT",
    "MODALITIES",
    "PredictabilityPacket",
    "RAMP_S",
    "STEP_S",
    "Step",
    "announcement_beats",
    "changes_per_announcement",
    "packet",
    "stagger_s",
]
