"""
M2-M5, M15 — Sensory Substrate (B2, lane 2)

B2 ships the two modules whose contract is testable without a renderer:

* `mixer.Mixer` (M3) — one master gain scaling every modality, per-modality
  trims, and the declaration rule that a feature must register its default
  before it can be driven.
* `transitions.Transitions` (M4) — 400-1200 ms ramps clamped and reported, one
  modality per tick, every change announced one beat ahead.

`Pacing` (M2/B2), `Timer` (M5/B6) and `Redundancy` (M15/B6) are declared in the
build instructions but are not built yet; they are absent rather than stubbed so
an importer fails loudly instead of getting a placeholder that does nothing.
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
]
