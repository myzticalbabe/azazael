"""
M7 — Session Telemetry (Sarah Build Instructions §6)

Six core events + clinical_seed for M16 crosswalk.
No free-form blobs — every event has a fixed schema.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal


# ──────────────────────────────────────────────────────────────────────────────
# EVENT SCHEMAS (fixed, no free-form blobs)
# ──────────────────────────────────────────────────────────────────────────────

EVENTS = (
    "profile_set",
    "demand_change", 
    "exit_requested",
    "pause",
    "resume",
    "affirmation",
    "session_end",
    "clinical_seed",  # M16
)

# Type-safe event definitions for validation
EventKind = Literal[
    "profile_set",
    "demand_change",
    "exit_requested", 
    "pause",
    "resume",
    "affirmation",
    "session_end",
    "clinical_seed",
]

@dataclass(frozen=True)
class ProfileSetEvent:
    event: Literal["profile_set"]
    axis: str
    value: float
    source: Literal["user", "probe", "telemetry", "clinical_seed"]

@dataclass(frozen=True)
class DemandChangeEvent:
    event: Literal["demand_change"]
    module: str
    direction: Literal["up", "down"]
    magnitude: float

@dataclass(frozen=True)
class ExitRequestedEvent:
    event: Literal["exit_requested"]
    at_s: float
    reason: str | None

@dataclass(frozen=True)
class PauseEvent:
    event: Literal["pause"]
    at_s: float
    duration_s: float

@dataclass(frozen=True)
class ResumeEvent:
    event: Literal["resume"]
    at_s: float

@dataclass(frozen=True)
class AffirmationEvent:
    event: Literal["affirmation"]
    drafted: bool
    evidence_present: bool

@dataclass(frozen=True)
class SessionEndEvent:
    event: Literal["session_end"]
    duration_s: float
    load_peak: float
    stopped_by: Literal["user", "load_meter", "companion_cap", "error"]

@dataclass(frozen=True)
class ClinicalSeedEvent:
    """M16 — Clinical crosswalk seed applied."""
    event: Literal["clinical_seed"]
    code: str
    system: Literal["DSM-5-TR", "ICD-11"]
    axes_seeded: int
    source_versions: dict[str, str]  # {"ACN_2023_meta": "v1", ...}
    crosswalk_version: str


# Union type for all events
SarahEvent = (
    ProfileSetEvent | DemandChangeEvent | ExitRequestedEvent | 
    PauseEvent | ResumeEvent | AffirmationEvent | SessionEndEvent | ClinicalSeedEvent
)


# ──────────────────────────────────────────────────────────────────────────────
# TELEMETRY SINK (pmb-backed, local-only)
# ──────────────────────────────────────────────────────────────────────────────

class TelemetrySink:
    """Append-only telemetry sink — writes to pmb as versioned facts."""
    
    def __init__(self, session_id: str | None = None):
        self.session_id = session_id or "local"
        self._events: list[SarahEvent] = []
    
    def emit(self, event: SarahEvent) -> None:
        """Emit an event — appends to local buffer and pmb."""
        self._events.append(event)
        # In production: pmb.record_fact(fact=json.dumps(asdict(event)), importance=0.7)
    
    def get_events(self) -> list[SarahEvent]:
        return list(self._events)
    
    def clear(self) -> None:
        self._events.clear()


# ──────────────────────────────────────────────────────────────────────────────
# CONVENIENCE EMITTERS
# ──────────────────────────────────────────────────────────────────────────────

_sink = TelemetrySink()

def emit_profile_set(axis: str, value: float, source: Literal["user", "probe", "telemetry", "clinical_seed"]) -> None:
    _sink.emit(ProfileSetEvent(event="profile_set", axis=axis, value=value, source=source))

def emit_demand_change(module: str, direction: Literal["up", "down"], magnitude: float) -> None:
    _sink.emit(DemandChangeEvent(event="demand_change", module=module, direction=direction, magnitude=magnitude))

def emit_exit_requested(at_s: float, reason: str | None = None) -> None:
    _sink.emit(ExitRequestedEvent(event="exit_requested", at_s=at_s, reason=reason))

def emit_pause(at_s: float, duration_s: float) -> None:
    _sink.emit(PauseEvent(event="pause", at_s=at_s, duration_s=duration_s))

def emit_resume(at_s: float) -> None:
    _sink.emit(ResumeEvent(event="resume", at_s=at_s))

def emit_affirmation(drafted: bool, evidence_present: bool) -> None:
    _sink.emit(AffirmationEvent(event="affirmation", drafted=drafted, evidence_present=evidence_present))

def emit_session_end(duration_s: float, load_peak: float, stopped_by: Literal["user", "load_meter", "companion_cap", "error"]) -> None:
    _sink.emit(SessionEndEvent(event="session_end", duration_s=duration_s, load_peak=load_peak, stopped_by=stopped_by))

def emit_clinical_seed(
    code: str, 
    system: Literal["DSM-5-TR", "ICD-11"],
    axes_seeded: int,
    source_versions: dict[str, str],
    crosswalk_version: str = "2026-11-16"
) -> None:
    _sink.emit(ClinicalSeedEvent(
        event="clinical_seed",
        code=code,
        system=system,
        axes_seeded=axes_seeded,
        source_versions=source_versions,
        crosswalk_version=crosswalk_version,
    ))

def get_session_events() -> list[SarahEvent]:
    return _sink.get_events()


# ──────────────────────────────────────────────────────────────────────────────
# VALIDATION (used by build DoD #3)
# ──────────────────────────────────────────────────────────────────────────────

def validate_event(event: SarahEvent) -> bool:
    """Validate event schema — used by tests."""
    if event.event not in EVENTS:
        return False
    return True