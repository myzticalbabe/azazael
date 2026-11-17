"""
M2 — Adaptive Pacing Governor (B2, lane 2)

The governor is clamped to **120–165 wpm** and **5–9 word chunks**, and the
inter-chunk gap is scaled by `processing_speed`. The clause with teeth is the
one that is absent: **there is no speed-up branch**. `target_wpm()` returns the
floor for every profile, including one measured as fast, because "the user
seemed impatient" is not evidence that they can read faster, and a module that
guesses upward is the exact failure this one exists to prevent.

What the profile is allowed to control is *waiting*, never rate. A slower
processor gets a longer gap between chunks; a faster one gets the base gap the
120 wpm floor already requires, never less. Demand can only come down.

M16 integration (lane-2 brief, gap analysis row 5): two readers are exposed for
the clinical seed — `hint_delay_ms_by_profile()` and
`chunk_size_by_processing_speed()` — and both take a `SarahProfile` rather than
a bare number, so a second source of preference cannot grow here.

No I/O, no clock, no model call: pacing is arithmetic over a value surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

MIN_WPM = 120
"""Slowest rate the governor will ever produce. Also the default for everyone."""

MAX_WPM = 165
"""Fastest rate an explicit request may reach. Never reached from a profile."""

DEFAULT_WPM = MIN_WPM
"""The shipped target: the floor, because unmeasured is not 'fast'."""

MIN_CHUNK_WORDS = 5
MAX_CHUNK_WORDS = 9
"""Chunk band. Five words is a phrase, nine is still one glance."""

PROCESSING_MARGIN_MS = 1200
"""Extra wait added at `processing_speed == 0`, tapering to zero at 1.

Unmeasured speed is treated as needing the **full** margin: the conservative
reading of "we do not know" is more time, never less.
"""

BASE_HINT_DELAY_MS = 1500
"""How long a hint waits before appearing, before any profile is considered."""

HINT_DELAY_SPEED_MS = 3000
"""Extra hint delay at `processing_speed == 0` — a slow processor is interrupted
less often, not more."""

HINT_DELAY_PREDICTION_MS = 1200
"""Extra hint delay at `prediction_need == 1` — a user who needs to predict gets
a longer uninterrupted run before the screen changes under them."""

MAX_HINT_DELAY_MS = 6000
"""Ceiling on the hint delay, so 'less interruption' cannot become 'never'."""


def _axis(profile: Any, name: str) -> float | None:
    """Read one axis as a float in [0, 1], or None when it is unmeasured.

    `None` is preserved rather than defaulted: the profile contract represents an
    unmeasured axis as `None`, and coercing it to 0.5 here is how a default
    becomes indistinguishable from a measurement.
    """
    if profile is None:
        return None
    value = getattr(profile, name, None)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        # Unmeasured, not zero. A missing axis, a string, or a bool stays `None`
        # so it cannot be read downstream as a low measurement, and the branch
        # decides by type rather than swallowing a conversion error.
        return None
    return min(1.0, max(0.0, float(value)))


def _clamp_wpm(requested: float) -> tuple[float, bool, str | None]:
    """Clamp a requested rate into [MIN_WPM, MAX_WPM] and say why, if it moved."""
    if requested > MAX_WPM:
        return MAX_WPM, True, f"requested {requested:g} wpm is above the {MAX_WPM} ceiling"
    if requested < MIN_WPM:
        return MIN_WPM, True, f"requested {requested:g} wpm is below the {MIN_WPM} floor"
    return float(requested), False, None


@dataclass(frozen=True)
class Paced:
    """One pacing decision: the chunks, the rate actually used, and the gap.

    `requested_wpm` and `clamp_reason` are carried on the result rather than
    logged elsewhere, because a clamp nobody can read is indistinguishable from
    a request that was honoured.
    """

    chunks: tuple[str, ...]
    wpm: float
    requested_wpm: float
    chunk_words: int
    gap_ms: int
    clamped: bool
    clamp_reason: str | None = None

    @property
    def words(self) -> int:
        return sum(len(chunk.split()) for chunk in self.chunks)

    def text(self) -> str:
        """The chunks rejoined — always the input words, never a summary."""
        return " ".join(self.chunks)

    def __len__(self) -> int:
        return len(self.chunks)

    def __iter__(self) -> Iterator[str]:
        return iter(self.chunks)


class Pacing:
    """Clamped chunking plus the two clinical-seed readers (M2 + M16).

    The object holds no session state: every call is a pure function of the text
    and the profile, so a replayed session paces identically.
    """

    def target_wpm(self, profile: Any = None) -> float:
        """The rate this module will use on its own: always the floor.

        A measured `processing_speed` does **not** raise it. This method exists
        so callers do not hand-roll a mapping that does.
        """
        return float(MIN_WPM)

    def chunk_size_by_processing_speed(self, profile: Any = None) -> int:
        """Words per chunk, 5–9, from `processing_speed`; unmeasured reads as 5."""
        speed = _axis(profile, "processing_speed")
        if speed is None:
            return MIN_CHUNK_WORDS
        span = MAX_CHUNK_WORDS - MIN_CHUNK_WORDS
        return int(min(MAX_CHUNK_WORDS, max(MIN_CHUNK_WORDS, MIN_CHUNK_WORDS + round(span * speed))))

    def hint_delay_ms_by_profile(self, profile: Any = None) -> int:
        """How long a hint waits, in ms — longer for a slow or prediction-needy user.

        Delay is the demand-reducing lever: the screen stays still for longer, so
        the user is interrupted less. It is capped at `MAX_HINT_DELAY_MS` so the
        help cannot disappear.
        """
        delay = float(BASE_HINT_DELAY_MS)
        speed = _axis(profile, "processing_speed")
        if speed is None:
            delay += HINT_DELAY_SPEED_MS
        else:
            delay += HINT_DELAY_SPEED_MS * (1.0 - speed)
        prediction = _axis(profile, "prediction_need")
        if prediction is not None:
            delay += HINT_DELAY_PREDICTION_MS * prediction
        return int(min(MAX_HINT_DELAY_MS, max(0.0, round(delay))))

    def gap_ms(self, wpm: float, chunk_words: int, profile: Any = None) -> int:
        """Reading time for one chunk at `wpm`, plus the processing margin."""
        if chunk_words <= 0:
            return 0
        read_ms = 60_000.0 / float(wpm) * float(chunk_words)
        speed = _axis(profile, "processing_speed")
        margin = PROCESSING_MARGIN_MS if speed is None else PROCESSING_MARGIN_MS * (1.0 - speed)
        return int(round(read_ms + margin))

    def pace(self, text: str, profile: Any = None, wpm: float | None = None) -> Paced:
        """Chunk `text` at a clamped rate. `wpm` is a request, not an instruction."""
        if not isinstance(text, str):
            raise TypeError(f"text must be a str, got {type(text).__name__}")
        requested = self.target_wpm(profile) if wpm is None else wpm
        if isinstance(requested, bool) or not isinstance(requested, (int, float)):
            raise TypeError(f"wpm must be a number, got {requested!r}")
        rate, clamped, reason = _clamp_wpm(float(requested))

        size = self.chunk_size_by_processing_speed(profile)
        words = text.split()
        if not words:
            return Paced((), rate, float(requested), size, 0, clamped, reason)

        chunks = tuple(" ".join(words[i:i + size]) for i in range(0, len(words), size))
        last = len(chunks[-1].split())
        return Paced(chunks, rate, float(requested), size, self.gap_ms(rate, last, profile), clamped, reason)

    def chunk(self, text: str, profile: Any = None, wpm: float | None = None) -> Paced:
        """The B2 contract name. Same decision as `pace()`."""
        return self.pace(text, profile, wpm)
