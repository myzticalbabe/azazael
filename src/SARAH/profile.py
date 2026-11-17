"""
M1 — Cognitive Profile Vector (Sarah Build Instructions B1)

The frozen eight axes (`AXES` — contract names, contract order) plus two
declared extended axes (`EXTENDED_AXES`), each float in [0, 1] with a named
low/high meaning. Precedence: user > probe > telemetry > clinical_seed.
An unknown axis value is represented as None and `explain()` says "not measured
yet" — never silently 0.5, so downstream code cannot mistake a default for a
measurement. `Profile` is the contract's name for `SarahProfile`.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json


AXES = (
    "sensory_gain", "processing_speed", "attention_span", "interoception",
    "masking_load", "recovery_latency", "initiation_cost", "prediction_need",
)
"""The frozen eight, in the order B1's contract names them.

This tuple is the vocabulary lanes 2 and 3 code against. It was previously the
first build's own eight (wm_span / sustained_attention / interoceptive_accuracy /
time_discrimination / initiation_threshold), which shared only three names with
the contract, so a downstream module reading `prediction_need` got "not
measured" forever while the profile quietly held a different axis.
"""

EXTENDED_AXES = ("wm_span", "time_discrimination")
"""Axes this build carries beyond the frozen eight, declared not hidden.

They are neither a second profile nor a silent growth of the contract: the
clinical crosswalk seeds them from the dyslexia / dyscalculia / dyspraxia rows,
and M9 (time scaffolding) and M10 (working-memory offload) consume them, while
no contract axis measures what they measure. Declaring them here keeps
`len(AXES) == 8` a promise lanes 2 and 3 can rely on and still lets `to_dict()`
report every value the build actually holds.
"""

ALL_AXES = AXES + EXTENDED_AXES

CONDITION_AXES = (
    "n_factor",
    "autism_specific",
    "adhd_specific",
    "cortical_hypo_specific",
    "dyslexia_dcd_specific",
)
"""Population-level condition factors, a second declared group.

The 2026-11-17 gap analysis asks for these on the profile. They are not axes:
`N_factor` is a latent neurodevelopmental spectrum factor and the other four are
condition-specific modifiers, so folding them into `ALL_AXES` would break B1's
frozen `len(AXES) == 8` and the equality/to_dict key set that lanes 2 and 3 code
against. They live in `SarahProfile.conditions` instead, and `to_full_dict()`
serialises them alongside the axes -- a factor is a modifier of how an axis is
read, never a measurement of it. A factor left `None` is unmeasured, exactly as
an axis left `None` is, so no consumer can mistake absence for a default.
"""

AXIS_ALIASES = {
    "sustained_attention": "attention_span",
    "interoceptive_accuracy": "interoception",
    "initiation_threshold": "initiation_cost",
}
"""Pre-freeze name -> contract name.

An alias keeps a stored profile, a crosswalk table or a caller written before
the interface doc resolving into the canonical field. Without it those keys
would be filtered out as unknown and the axis would read "not measured yet" --
the exact failure that made the contract mismatch invisible in the first place.
"""

AXIS_MEANING = {
    "sensory_gain": ("low", "high"),
    "processing_speed": ("slow", "fast"),
    "attention_span": ("short", "long"),
    "interoception": ("low", "high"),
    "masking_load": ("low", "high"),
    "recovery_latency": ("fast", "slow"),
    "initiation_cost": ("low", "high"),
    "prediction_need": ("low", "high"),
    "wm_span": ("small", "large"),
    "time_discrimination": ("poor", "good"),
}


def canonical_axis(name: str) -> str | None:
    """Resolve an axis name -- canonical or pre-freeze alias -- to its field.

    Returns None for a name this profile does not carry, so callers can tell a
    different vocabulary from a typo instead of guessing.
    """
    name = AXIS_ALIASES.get(name, name)
    return name if name in ALL_AXES else None

SOURCE_PRECEDENCE = ("user", "probe", "telemetry", "clinical_seed")


@dataclass(frozen=True)
class ConditionFactors:
    """The five condition factors, each optional and each in [0, 1].

    `None` means "not measured", never 0.5: the same rule the axes follow. A
    consumer that turns `None` into a default would be reporting a measurement
    nobody made.
    """

    n_factor: float | None = None
    autism_specific: float | None = None
    adhd_specific: float | None = None
    cortical_hypo_specific: float | None = None
    dyslexia_dcd_specific: float | None = None

    def __post_init__(self) -> None:
        for name in CONDITION_AXES:
            val = getattr(self, name)
            if val is None:
                continue
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                raise TypeError(f"{name} must be float or None, got {type(val)}")
            if not 0.0 <= float(val) <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")

    def to_dict(self) -> dict[str, float | None]:
        return {name: getattr(self, name) for name in CONDITION_AXES}

    def is_empty(self) -> bool:
        """True when no factor was measured."""
        return all(getattr(self, name) is None for name in CONDITION_AXES)


@dataclass
class SarahProfile:
    """Immutable 8-axis cognitive profile vector."""
    
    # The frozen eight, in contract order (None = not measured)
    sensory_gain: float | None = None
    processing_speed: float | None = None
    attention_span: float | None = None
    interoception: float | None = None
    masking_load: float | None = None
    recovery_latency: float | None = None
    initiation_cost: float | None = None
    prediction_need: float | None = None

    # Extended axes (EXTENDED_AXES) -- outside the freeze, still carried
    wm_span: float | None = None
    time_discrimination: float | None = None

    # Condition factors (CONDITION_AXES) -- modifiers, not axes
    conditions: ConditionFactors | None = None
    
    # Source tracking per axis
    _sources: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    
    def __post_init__(self):
        # Validate axes
        for axis in ALL_AXES:
            val = getattr(self, axis)
            if val is not None:
                if not isinstance(val, (int, float)):
                    raise TypeError(f"{axis} must be float or None, got {type(val)}")
                if not 0.0 <= val <= 1.0:
                    raise ValueError(f"{axis} must be in [0, 1], got {val}")

        # A dict here would be accepted by the field and unread by every
        # consumer, so the type is checked where it enters the profile.
        if self.conditions is not None and not isinstance(
            self.conditions, ConditionFactors
        ):
            raise TypeError(
                "conditions must be a ConditionFactors or None, got "
                f"{type(self.conditions).__name__}"
            )
    
    @classmethod
    def from_signals(cls, signals: dict[str, float | None], source: str = "probe") -> SarahProfile:
        """Create profile from signal dict (deterministic, no I/O, no model call)."""
        profile = cls()
        for axis, val in signals.items():
            target = canonical_axis(axis)
            if target is None or val is None:
                continue
            setattr(profile, target, float(val))
            profile._sources[target] = source
        # A signal that names an unknown axis is ignored (a caller from another
        # vocabulary is not a profile error), but a value out of [0, 1] is a
        # real defect and must not reach a profile unvalidated.
        profile.__post_init__()
        return profile
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SarahProfile:
        """Create profile from dict (for merge operations)."""
        # Filter to known axes, resolving pre-freeze aliases on the way in
        valid: dict[str, Any] = {}
        for key, value in data.items():
            target = canonical_axis(key)
            if target is not None:
                valid[target] = value
        return cls(**valid)
    
    def to_dict(self) -> dict[str, float | None]:
        """Return every axis this profile carries: the frozen eight, then extras."""
        return {axis: getattr(self, axis) for axis in ALL_AXES}
    
    def explain(self, axis: str) -> str:
        """Why the value is what it is, in one sentence."""
        target = canonical_axis(axis)
        if target is None:
            return f"Unknown axis: {axis}"
        val = getattr(self, target)
        if val is None:
            return f"{target}: not measured yet"
        low, high = AXIS_MEANING[target]
        source = self._sources.get(target, "unknown")
        return f"{target}={val:.2f} ({low}→{high}) from {source}"
    
    def axes(self) -> list[str]:
        """Return the eight frozen axis names, in contract order."""
        return list(AXES)

    def all_axes(self) -> list[str]:
        """Return the frozen eight plus the extended axes this build carries."""
        return list(ALL_AXES)

    # -- condition factors, readable without reaching through `.conditions` --

    def factor(self, name: str) -> float | None:
        """One condition factor by name, or None for an unknown name.

        Returns None for a name this build does not carry, mirroring
        `canonical_axis`: a caller can tell a different vocabulary from a typo.
        """
        if name not in CONDITION_AXES or self.conditions is None:
            return None
        return getattr(self.conditions, name)

    def has_conditions(self) -> bool:
        """True when at least one condition factor was measured."""
        return self.conditions is not None and not self.conditions.is_empty()

    @property
    def n_factor(self) -> float | None:
        return self.factor("n_factor")

    @property
    def N_factor(self) -> float | None:
        """The gap analysis spells this factor `N_factor`; one value, two names."""
        return self.factor("n_factor")

    @property
    def autism_specific(self) -> float | None:
        return self.factor("autism_specific")

    @property
    def adhd_specific(self) -> float | None:
        return self.factor("adhd_specific")

    @property
    def cortical_hypo_specific(self) -> float | None:
        return self.factor("cortical_hypo_specific")

    @property
    def dyslexia_dcd_specific(self) -> float | None:
        return self.factor("dyslexia_dcd_specific")

    def to_full_dict(self) -> dict[str, Any]:
        """Every axis plus the condition factors.

        `to_dict()` deliberately keeps its ALL_AXES key set: B1 froze it and
        `__eq__` rides on it. Persisting a profile means this method, not that
        one, or the factors are dropped on the way to disk with no error.
        """
        data: dict[str, Any] = dict(self.to_dict())
        data["conditions"] = (
            self.conditions.to_dict() if self.conditions is not None else None
        )
        return data
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SarahProfile):
            return NotImplemented
        return self.to_dict() == other.to_dict()


# The B1 contract calls this type `Profile`; the first build called it
# `SarahProfile`. Both names resolve to one class, so the contract's own smoke
# command works without a second definition to drift.
Profile = SarahProfile


# ──────────────────────────────────────────────────────────────────────────────
# PROFILE STORE (pmb-backed, versioned, inspectable, deletable)
# ──────────────────────────────────────────────────────────────────────────────

class ProfileStore:
    """Versioned profile storage in pmb."""
    
    @staticmethod
    def save(profile: SarahProfile, version: str, user_id: str = "local") -> str:
        """Save profile as versioned record in pmb."""
        # In production: pmb.record_fact(fact=json.dumps({...}), importance=0.8)
        return f"sarah_profile_{user_id}_{version}"
    
    @staticmethod
    def load(user_id: str = "local", version: str | None = None) -> SarahProfile | None:
        """Load latest or specific version."""
        # In production: pmb.recall(...)
        return None
    
    @staticmethod
    def delete(user_id: str = "local", version: str | None = None) -> bool:
        """Delete profile record(s)."""
        # In production: pmb.forget(...)
        return True


# ──────────────────────────────────────────────────────────────────────────────
# PREVIEW / EXIT PORT (M6/M7)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Preview:
    """What happens, how long, how to leave — before any state change."""
    what: str
    duration_s: float
    how_to_leave: str

@dataclass
class ExitTicket:
    """Exit-anywhere ticket — one keystroke to low-stimulation hub."""
    at_s: float
    reason: str | None
    resume_token: str  # For state restoration via pmb

class ExitPort:
    """M7 — Exit is never scored, timed, commented on, or followed by retention prompt."""
    
    @staticmethod
    def leave(reason: str | None = None) -> ExitTicket:
        import time
        return ExitTicket(at_s=time.time(), reason=reason, resume_token="pmb_token_stub")
    
    @staticmethod
    def resume(token: str) -> SarahProfile | None:
        return ProfileStore.load()
    
    @staticmethod
    def assert_unscored(log: list[dict]) -> None:
        """Assertion helper for tests — exit events carry no score."""
        for entry in log:
            if entry.get("event") == "exit_requested":
                assert "score" not in entry
                assert "rating" not in entry
                assert "comment" not in entry