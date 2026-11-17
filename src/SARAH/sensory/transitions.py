"""
M4 — Gradual-Transition Engine (B2, lane 2)

Every state change ramps over a bounded window; the window's floor is honoured
even when a caller asks for something faster, and the clamp is **reported** so
a caller cannot believe its request was taken. Never two modalities change in
one tick, and every change is announced one beat before it starts.

This module plans; it never sleeps and never touches a renderer. A `Ramp`
carries absolute millisecond offsets and the caller owns the clock — which is
what lets the no-simultaneity rule be a test rather than a hope.

The clamp is the point of the module: "we cut straight to the next state because
the user seemed impatient" is the failure the XR comfort evidence names, so a
sub-floor request is refused-as-honoured and says `clamped=True`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

MIN_RAMP_MS = 400
"""Floor. A ramp shorter than this is a cut, and a cut is what this engine exists to prevent."""

MAX_RAMP_MS = 1200
"""Ceiling. Past this the change stops reading as a transition and reads as drift."""

ANNOUNCE_BEAT_MS = 250
"""One beat: how long before the ramp starts the change is announced."""


class SimultaneousChange(ValueError):
    """Two modalities changing in one tick. This raises; it is never a warning."""


class InvalidRamp(ValueError):
    """A ramp whose target or duration cannot describe a transition."""


@dataclass(frozen=True)
class Ramp:
    """One scheduled modality change.

    `requested_ms` is kept beside `duration_ms` so a clamped request leaves a
    record of what was asked for: the caller learns the difference, rather than
    reading a shortened duration as agreement.
    """

    modality: str
    target: float
    requested_ms: int
    duration_ms: int
    announce_at_ms: int
    start_at_ms: int
    clamped: bool

    @property
    def end_at_ms(self) -> int:
        return self.start_at_ms + self.duration_ms

    def overlaps(self, other: "Ramp") -> bool:
        return self.start_at_ms < other.end_at_ms and other.start_at_ms < self.end_at_ms

    @property
    def announcement(self) -> str:
        """Literal, one-sentence, W3C COGA phrasing — no negation, no clock time."""
        return (
            f"next: {self.modality} changes to {self.target:.2f}, "
            f"starting in {self.start_at_ms - self.announce_at_ms} ms and taking "
            f"{self.duration_ms} ms"
        )


def clamp_duration(duration_ms: int | float) -> tuple[int, bool]:
    """Return (honoured duration, was the request clamped)."""
    if isinstance(duration_ms, bool) or not isinstance(duration_ms, (int, float)):
        raise InvalidRamp(f"duration_ms must be a number, got {duration_ms!r}")
    if duration_ms != duration_ms:  # NaN never satisfies the bounds below
        raise InvalidRamp("duration_ms must be finite")
    requested = int(round(float(duration_ms)))
    if requested < MIN_RAMP_MS:
        return MIN_RAMP_MS, True
    if requested > MAX_RAMP_MS:
        return MAX_RAMP_MS, True
    return requested, False


class Transitions:
    """Schedules ramps under the three M4 rules.

    Rules enforced here:
      1. duration is clamped into [MIN_RAMP_MS, MAX_RAMP_MS] and the clamp is reported;
      2. two modalities never share a tick — an overlapping ramp for a different
         modality raises `SimultaneousChange`;
      3. every ramp carries its announcement offset, one beat before its start.
    """

    def __init__(self, beat_ms: int = ANNOUNCE_BEAT_MS) -> None:
        if isinstance(beat_ms, bool) or not isinstance(beat_ms, int):
            raise InvalidRamp(f"beat_ms must be an int, got {beat_ms!r}")
        if beat_ms < 1:
            # A zero-length beat is not an announcement; it is the scene cut.
            raise InvalidRamp(f"beat_ms must be at least 1 ms, got {beat_ms}")
        self.beat_ms = beat_ms
        self._open: list[Ramp] = []
        self._cursor_ms = 0

    # -- clinical seed (M16) ------------------------------------------------

    def ramp_duration_from_recovery_latency(self, recovery_latency: float | None = None) -> int:
        """Ramp length for a recovery-latency axis, in ms (M16).

        A longer recovery latency gets a longer ramp, mapped across the whole
        [MIN_RAMP_MS, MAX_RAMP_MS] band. Unmeasured returns the minimum: the
        band is a floor, and an unmeasured user is not assumed to be slow.
        """
        if recovery_latency is None:
            return MIN_RAMP_MS
        if isinstance(recovery_latency, bool) or not isinstance(recovery_latency, (int, float)):
            raise InvalidRamp(f"recovery_latency must be a number in [0, 1], got {recovery_latency!r}")
        if not 0.0 <= float(recovery_latency) <= 1.0:
            raise InvalidRamp(f"recovery_latency must be in [0, 1], got {recovery_latency!r}")
        span = MAX_RAMP_MS - MIN_RAMP_MS
        return int(round(MIN_RAMP_MS + span * float(recovery_latency)))

    def ramp_for_profile(
        self,
        modality: str,
        target: float,
        profile: object,
        *,
        start_at_ms: int | None = None,
    ) -> Ramp:
        """Schedule a ramp whose duration comes from the profile's recovery latency."""
        latency = getattr(profile, "recovery_latency", None)
        return self.ramp(
            modality,
            target,
            self.ramp_duration_from_recovery_latency(latency),
            start_at_ms=start_at_ms,
        )

    # -- scheduling ---------------------------------------------------------

    def ramp(
        self,
        modality: str,
        target: float,
        duration_ms: int | float,
        *,
        start_at_ms: int | None = None,
    ) -> Ramp:
        """Schedule one ramp, or raise if it would change two modalities at once."""
        if not isinstance(modality, str) or not modality:
            raise InvalidRamp(f"modality must be a non-empty name, got {modality!r}")
        if isinstance(target, bool) or not isinstance(target, (int, float)):
            raise InvalidRamp(f"target must be a number, got {target!r}")
        if not 0.0 <= float(target) <= 1.0:
            raise InvalidRamp(f"target must be in [0, 1], got {target!r}")

        duration, clamped = clamp_duration(duration_ms)
        start = self._cursor_ms if start_at_ms is None else int(start_at_ms)
        if start < 0:
            raise InvalidRamp(f"start_at_ms must be >= 0, got {start}")

        candidate = Ramp(
            modality=modality,
            target=float(target),
            requested_ms=int(round(float(duration_ms))),
            duration_ms=duration,
            announce_at_ms=max(0, start - self.beat_ms),
            start_at_ms=start,
            clamped=clamped,
        )
        for other in self._open:
            if other.modality != modality and other.overlaps(candidate):
                raise SimultaneousChange(
                    f"{modality} would change while {other.modality} is still ramping "
                    f"({other.start_at_ms}..{other.end_at_ms} ms vs "
                    f"{candidate.start_at_ms}..{candidate.end_at_ms} ms); "
                    "stagger them one beat apart with plan()"
                )

        self._open.append(candidate)
        self._cursor_ms = max(self._cursor_ms, candidate.end_at_ms)
        return candidate

    def plan(self, changes: Iterable[Sequence[object]]) -> list[Ramp]:
        """Schedule `(modality, target, duration_ms)` triples one at a time.

        Each change starts when the previous one *ends*, so a batch of changes is
        never simultaneous by construction — the caller cannot express the
        forbidden shape through this entry point.
        """
        planned: list[Ramp] = []
        for change in changes:
            items = tuple(change)
            if len(items) != 3:
                raise InvalidRamp(
                    f"each change must be (modality, target, duration_ms), got {items!r}"
                )
            modality, target, duration_ms = items
            if not isinstance(modality, str) or not modality:
                raise InvalidRamp(f"modality must be a non-empty name, got {modality!r}")
            if isinstance(target, bool) or not isinstance(target, (int, float)):
                raise InvalidRamp(f"target must be a number, got {target!r}")
            if isinstance(duration_ms, bool) or not isinstance(duration_ms, (int, float)):
                raise InvalidRamp(f"duration_ms must be a number, got {duration_ms!r}")
            planned.append(
                self.ramp(modality, float(target), float(duration_ms))
            )
        return planned

    # -- inspection ---------------------------------------------------------

    def pending(self) -> tuple[Ramp, ...]:
        """Every scheduled ramp, in start order."""
        return tuple(sorted(self._open, key=lambda r: r.start_at_ms))

    def announcements(self) -> list[str]:
        """The one-beat-ahead announcements, in start order."""
        return [r.announcement for r in self.pending()]

    def clear(self) -> None:
        self._open.clear()
        self._cursor_ms = 0
