"""
M12 — Masking-Load Meter and Burnout Guard (Lane 3, B5)

Measures masking load (social camouflage effort) against recovery_latency.
Stops a session before the recovery-latency axis is breached.
A module that raises the load score while raising completion has made the
task compulsory, not bridged a deficit.

Per design:
- LoadMeter.should_stop(session) -> bool driven by recovery_latency
- Post-session offer is low-demand "people-adjacent" mode
- Hard cap: load threshold from recovery_latency axis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from datetime import datetime

from SARAH.profile import (
    SarahProfile,
    AXES,
    canonical_axis,
)


class LoadDomain(str, Enum):
    """Domains contributing to masking load."""
    SOCIAL = "social"           # Social interaction demand
    SENSORY = "sensory"         # Sensory processing demand
    COGNITIVE = "cognitive"     # Executive function demand
    EMOTIONAL = "emotional"     # Emotional regulation demand
    COMMUNICATION = "communication"  # Verbal/nonverbal demand


@dataclass(frozen=True)
class LoadEvent:
    """A single load-contributing event."""
    domain: LoadDomain
    intensity: float  # 0.0 - 1.0
    duration_seconds: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""

    def __post_init__(self):
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError("intensity must be in [0, 1]")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds cannot be negative")


@dataclass
class SessionLoad:
    """Accumulated load for a session."""
    events: list[LoadEvent] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    ended_at: str | None = None

    def add_event(self, event: LoadEvent) -> None:
        self.events.append(event)

    def total_load(self) -> float:
        """Total load as weighted sum of intensity * duration."""
        if not self.events:
            return 0.0
        # Weight by domain (some domains cost more recovery)
        domain_weights = {
            LoadDomain.SOCIAL: 1.2,
            LoadDomain.SENSORY: 1.0,
            LoadDomain.COGNITIVE: 1.1,
            LoadDomain.EMOTIONAL: 1.3,
            LoadDomain.COMMUNICATION: 1.0,
        }
        total = 0.0
        for event in self.events:
            weight = domain_weights.get(event.domain, 1.0)
            total += event.intensity * event.duration_seconds * weight
        return total

    def load_by_domain(self) -> dict[LoadDomain, float]:
        """Load broken down by domain."""
        domain_weights = {
            LoadDomain.SOCIAL: 1.2,
            LoadDomain.SENSORY: 1.0,
            LoadDomain.COGNITIVE: 1.1,
            LoadDomain.EMOTIONAL: 1.3,
            LoadDomain.COMMUNICATION: 1.0,
        }
        result: dict[LoadDomain, float] = {d: 0.0 for d in LoadDomain}
        for event in self.events:
            weight = domain_weights.get(event.domain, 1.0)
            result[event.domain] += event.intensity * event.duration_seconds * weight
        return result

    def end_session(self) -> None:
        self.ended_at = datetime.now().isoformat()


class LoadMeter:
    """M12 — Masking-Load Meter and Burnout Guard.

    Driven by SarahProfile.recovery_latency axis:
    - High recovery_latency (slow recovery) = lower threshold
    - Low recovery_latency (fast recovery) = higher threshold
    - should_stop() returns True when threshold breached
    - Post-session offer: low-demand "people-adjacent" mode
    """

    # Base threshold (seconds of weighted load) at recovery_latency = 0.5
    BASE_THRESHOLD = 3600.0  # 1 hour of weighted load

    # Threshold scaling: recovery_latency 0.0 (fast) -> 2x base, 1.0 (slow) -> 0.5x base
    THRESHOLD_MIN_MULTIPLIER = 0.5
    THRESHOLD_MAX_MULTIPLIER = 2.0

    def __init__(self, profile: SarahProfile | None = None):
        self.profile = profile or SarahProfile()
        self.current_session: SessionLoad | None = None

    def start_session(self) -> SessionLoad:
        """Start a new load-tracking session."""
        self.current_session = SessionLoad()
        return self.current_session

    def record_event(
        self,
        domain: LoadDomain,
        intensity: float,
        duration_seconds: float,
        description: str = ""
    ) -> LoadEvent:
        """Record a load event in current session."""
        if self.current_session is None:
            self.start_session()
        event = LoadEvent(
            domain=domain,
            intensity=intensity,
            duration_seconds=duration_seconds,
            description=description,
        )
        self.current_session.add_event(event)
        return event

    def _compute_threshold(self) -> float:
        """Compute load threshold from recovery_latency axis.

        Piecewise linear scaling (per test expectations):
        - recovery <= 0.5: multiplier = 2.0 - 2.0 * recovery  (slope -2.0)
          0.0 -> 2.0x, 0.25 -> 1.5x, 0.5 -> 1.0x
        - recovery > 0.5: multiplier = 1.5 - recovery  (slope -1.0)
          0.75 -> 0.75x, 1.0 -> 0.5x
        """
        recovery = self.profile.recovery_latency
        if recovery is None:
            # Not measured -> conservative (low threshold)
            return self.BASE_THRESHOLD * 0.75

        if recovery <= 0.5:
            multiplier = 2.0 - 2.0 * recovery
        else:
            multiplier = 1.5 - recovery

        return self.BASE_THRESHOLD * multiplier

    def current_load(self) -> float:
        """Current session load."""
        if self.current_session is None:
            return 0.0
        return self.current_session.total_load()

    def should_stop(self) -> bool:
        """Should the session stop? True when load >= threshold."""
        if self.current_session is None:
            return False
        threshold = self._compute_threshold()
        load = self.current_load()
        return load >= threshold

    def remaining_load(self) -> float:
        """Load remaining before threshold."""
        if self.current_session is None:
            return self._compute_threshold()
        threshold = self._compute_threshold()
        load = self.current_load()
        return max(0.0, threshold - load)

    def load_fraction(self) -> float:
        """Current load as fraction of threshold (0.0 - 1.0+)."""
        threshold = self._compute_threshold()
        if threshold <= 0:
            return 1.0
        return min(2.0, self.current_load() / threshold)

    def end_session(self) -> SessionLoad | None:
        """End current session, return it for post-session offer."""
        if self.current_session is None:
            return None
        self.current_session.end_session()
        session = self.current_session
        self.current_session = None
        return session

    def post_session_offer(self) -> dict[str, Any]:
        """Generate post-session offer (low-demand people-adjacent mode)."""
        return {
            "mode": "people_adjacent",
            "description": (
                "Session complete. Offering low-demand presence mode: "
                "quiet companionship, no demands, no questions, just available."
            ),
            "load_at_end": self.current_load() if self.current_session else 0.0,
            "threshold": self._compute_threshold(),
            "recovery_latency": self.profile.recovery_latency,
            "recommended_recovery_seconds": self._recommended_recovery(),
        }

    def _recommended_recovery(self) -> float:
        """Recommended recovery time based on load and recovery_latency."""
        load = self.current_load()
        recovery = self.profile.recovery_latency or 0.5
        # More load + slower recovery = more recovery time
        base_recovery = load * 0.1  # 10% of load time
        recovery_multiplier = 1.0 + recovery  # 1.0x to 2.0x
        return base_recovery * recovery_multiplier

    def explain_load(self) -> str:
        """Explain current load state."""
        threshold = self._compute_threshold()
        load = self.current_load()
        fraction = self.load_fraction()
        recovery = self.profile.recovery_latency
        recovery_str = f"{recovery:.2f}" if recovery is not None else "not measured"

        if fraction >= 1.0:
            status = "THRESHOLD BREACHED"
        elif fraction >= 0.8:
            status = "APPROACHING THRESHOLD"
        elif fraction >= 0.5:
            status = "MODERATE LOAD"
        else:
            status = "LOW LOAD"

        return (
            f"Load: {load:.0f}s weighted / {threshold:.0f}s threshold "
            f"({fraction:.0%}) — {status}\n"
            f"Recovery latency: {recovery_str}\n"
            f"Recommended recovery: {self._recommended_recovery():.0f}s"
        )


def create_load_meter(profile: SarahProfile | None = None) -> LoadMeter:
    """Factory function."""
    return LoadMeter(profile)


def quick_should_stop(
    profile: SarahProfile,
    events: list[tuple[LoadDomain, float, float]]
) -> bool:
    """Quick one-shot should_stop check."""
    meter = LoadMeter(profile)
    meter.start_session()
    for domain, intensity, duration in events:
        meter.record_event(domain, intensity, duration)
    return meter.should_stop()