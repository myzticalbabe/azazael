"""
M2-M5, M15 — Sensory Substrate (B2 + B6, lane 2)

* `mixer.Mixer` (M3) — one master gain scaling every modality, per-modality
  trims, and the declaration rule that a feature must register its default
  before it can be driven.
* `transitions.Transitions` (M4) — 400–1200 ms ramps clamped and reported, one
  modality per tick, every change announced one beat ahead.
* `pacing.Pacing` (M2) — 120–165 wpm and 5–9 word chunks, a gap scaled by
  `processing_speed`, and no speed-up branch.
* `timer.Timer` (M5) — absent unless requested, a pause that actually pauses,
  and no countdown unless one was asked for.
* `redundancy.Redundancy` (M15) — the same content over text, audio and
  pictogram so any one of them can be off.

Importing the package imports no model stack and performs no I/O: this is a
value surface a renderer reads.
"""

from .mixer import (
    CRITICAL_MODALITIES,
    DEFAULT_MASTER,
    DEFAULT_TRIMS,
    MAX_GAIN,
    MIN_GAIN,
    InvalidGain,
    Mixer,
    UndeclaredModality,
)
from .pacing import (
    DEFAULT_WPM,
    MAX_CHUNK_WORDS,
    MAX_HINT_DELAY_MS,
    MAX_WPM,
    MIN_CHUNK_WORDS,
    MIN_WPM,
    Paced,
    Pacing,
)
from .redundancy import (
    CHANNELS,
    DEFAULT_PRIORITY,
    HIGH_INTEROCEPTION_PRIORITY,
    LOW_INTEROCEPTION_PRIORITY,
    NoChannelAvailable,
    Redundancy,
    Rendition,
)
from .timer import Timer
from .transitions import (
    ANNOUNCE_BEAT_MS,
    MAX_RAMP_MS,
    MIN_RAMP_MS,
    InvalidRamp,
    Ramp,
    SimultaneousChange,
    Transitions,
    clamp_duration,
)

__all__ = [
    # M3 — Sensory Gain Mixer
    "Mixer",
    "DEFAULT_TRIMS",
    "DEFAULT_MASTER",
    "CRITICAL_MODALITIES",
    "MIN_GAIN",
    "MAX_GAIN",
    "InvalidGain",
    "UndeclaredModality",
    # M4 — Gradual-Transition Engine
    "Transitions",
    "Ramp",
    "clamp_duration",
    "MIN_RAMP_MS",
    "MAX_RAMP_MS",
    "ANNOUNCE_BEAT_MS",
    "InvalidRamp",
    "SimultaneousChange",
    # M2 — Adaptive Pacing Governor
    "Pacing",
    "Paced",
    "MIN_WPM",
    "MAX_WPM",
    "DEFAULT_WPM",
    "MIN_CHUNK_WORDS",
    "MAX_CHUNK_WORDS",
    "MAX_HINT_DELAY_MS",
    # M5 — Self-Pacing Timer
    "Timer",
    # M15 — Cross-Modal Redundancy
    "Redundancy",
    "Rendition",
    "CHANNELS",
    "DEFAULT_PRIORITY",
    "LOW_INTEROCEPTION_PRIORITY",
    "HIGH_INTEROCEPTION_PRIORITY",
    "NoChannelAvailable",
]
