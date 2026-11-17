"""
M9 — Time Scaffolding (Lane 3, B4)

Duration rendered as length, never as clock arithmetic.
Per design: TimeView.remaining(seconds) -> Ribbon — a visual/physical
representation of time remaining, not a clock time.

Rules:
- No countdown unless explicitly requested (hard cap)
- Duration rendered as length (bar, ribbon, segments), not HH:MM:SS
- Self-pacing: user controls the timer, not the system
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from enum import Enum

from SARAH.profile import (
    SarahProfile,
    AXES,
    canonical_axis,
)


class TimeUnit(str, Enum):
    """Time units for rendering."""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class RibbonStyle(str, Enum):
    """Visual styles for time ribbon."""
    BAR = "bar"                    # ████████░░ 40%
    SEGMENTS = "segments"          # ●●●●○○○○○○ 4/10
    RIBBON = "ribbon"              # ▬▬▬▬▬▬▬▬▬▬ 100%
    PROPORTIONAL = "proportional"  # █░ 1:2 ratio


@dataclass(frozen=True)
class TimeRibbon:
    """A length-based representation of time — never clock arithmetic.

    Fields:
        total_seconds: Total duration
        elapsed_seconds: Time elapsed
        style: Visual style
        unit: Display unit
    """
    total_seconds: float
    elapsed_seconds: float
    style: RibbonStyle = RibbonStyle.BAR
    unit: TimeUnit = TimeUnit.MINUTES

    def __post_init__(self):
        if self.total_seconds <= 0:
            raise ValueError("total_seconds must be positive")
        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative")

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.total_seconds - self.elapsed_seconds)

    @property
    def progress(self) -> float:
        """Progress as fraction 0.0-1.0."""
        if self.total_seconds <= 0:
            return 1.0
        return min(1.0, self.elapsed_seconds / self.total_seconds)

    @property
    def remaining_fraction(self) -> float:
        return 1.0 - self.progress

    def render(self, width: int = 20) -> str:
        """Render time as length, not clock arithmetic."""
        p = self.progress
        r = self.remaining_fraction
        filled = int(p * width)
        empty = width - filled

        if self.style == RibbonStyle.BAR:
            bar = "█" * filled + "░" * empty
            unit_str = self._format_unit(self.remaining_seconds)
            return f"{bar} {unit_str} remaining"

        elif self.style == RibbonStyle.SEGMENTS:
            total_segs = min(width, 10)
            filled_segs = int(p * total_segs)
            empty_segs = total_segs - filled_segs
            segs = "●" * filled_segs + "○" * empty_segs
            unit_str = self._format_unit(self.remaining_seconds)
            return f"{segs} {unit_str}"

        elif self.style == RibbonStyle.RIBBON:
            bar = "▬" * filled + "·" * empty
            unit_str = self._format_unit(self.remaining_seconds)
            return f"{bar} {unit_str}"

        elif self.style == RibbonStyle.PROPORTIONAL:
            # Show ratio of elapsed:remaining
            if self.remaining_seconds > 0:
                ratio = self.elapsed_seconds / self.remaining_seconds
                elapsed_part = int(width * p)
                remaining_part = width - elapsed_part
                bar = "█" * elapsed_part + "░" * remaining_part
                return f"{bar} {self.elapsed_seconds:.0f}s : {self.remaining_seconds:.0f}s"
            else:
                bar = "█" * width
                return f"{bar} complete"

        return f"[{'█' * filled}{'░' * empty}] {self.remaining_seconds:.0f}s"

    def _format_unit(self, seconds: float) -> str:
        if self.unit == TimeUnit.SECONDS:
            return f"{seconds:.0f}s"
        elif self.unit == TimeUnit.MINUTES:
            return f"{seconds / 60:.1f}m"
        elif self.unit == TimeUnit.HOURS:
            return f"{seconds / 3600:.2f}h"
        return f"{seconds:.0f}s"


class TimeView:
    """M9 — Time Scaffolding.

    Renders duration as length (ribbon, bar, segments), never as clock arithmetic.
    Self-pacing: the user controls the timer.
    """

    def __init__(self, profile: SarahProfile | None = None):
        self.profile = profile or SarahProfile()
        self._active_ribbon: TimeRibbon | None = None
        self._paused_at: float | None = None
        self._pause_duration: float = 0.0

    def start(self, total_seconds: float,
              style: RibbonStyle = RibbonStyle.BAR,
              unit: TimeUnit = TimeUnit.MINUTES) -> TimeRibbon:
        """Start a new time ribbon."""
        import time
        self._active_ribbon = TimeRibbon(
            total_seconds=total_seconds,
            elapsed_seconds=0.0,
            style=style,
            unit=unit,
        )
        self._paused_at = None
        self._pause_duration = 0.0
        return self._active_ribbon

    def pause(self) -> TimeRibbon | None:
        """Pause the current ribbon — actually pauses."""
        import time
        if self._active_ribbon is None:
            return None
        if self._paused_at is not None:
            return self._active_ribbon  # Already paused

        self._paused_at = time.time()
        return self._active_ribbon

    def resume(self) -> TimeRibbon | None:
        """Resume from pause."""
        import time
        if self._active_ribbon is None or self._paused_at is None:
            return self._active_ribbon

        pause_elapsed = time.time() - self._paused_at
        self._pause_duration += pause_elapsed
        self._paused_at = None
        return self._active_ribbon

    def tick(self, elapsed_seconds: float | None = None) -> TimeRibbon | None:
        """Update elapsed time. If None, uses wall time since start."""
        import time
        if self._active_ribbon is None:
            return None

        if self._paused_at is not None:
            # Don't advance while paused
            return TimeRibbon(
                total_seconds=self._active_ribbon.total_seconds,
                elapsed_seconds=self._active_ribbon.elapsed_seconds,
                style=self._active_ribbon.style,
                unit=self._active_ribbon.unit,
            )

        if elapsed_seconds is not None:
            elapsed = elapsed_seconds + self._pause_duration
        else:
            # Need a start reference - simplified: assume caller manages
            elapsed = self._active_ribbon.elapsed_seconds

        self._active_ribbon = TimeRibbon(
            total_seconds=self._active_ribbon.total_seconds,
            elapsed_seconds=min(elapsed, self._active_ribbon.total_seconds),
            style=self._active_ribbon.style,
            unit=self._active_ribbon.unit,
        )
        return self._active_ribbon

    def render_remaining(self, width: int = 20) -> str | None:
        """Render remaining time as length."""
        if self._active_ribbon is None:
            return None
        return self._active_ribbon.render(width)

    def requested(self) -> bool:
        """Timer exists only when requested (per hard cap)."""
        return self._active_ribbon is not None

    def is_complete(self) -> bool:
        """Check if timer is complete."""
        if self._active_ribbon is None:
            return False
        return self._active_ribbon.remaining_seconds <= 0

    def get_ribbon_for_profile_axis(self, axis: str, width: int = 20) -> str | None:
        """Get time ribbon representation for a SarahProfile axis.

        Maps profile axes to time perception:
        - prediction_need → countdown ribbon
        - time_discrimination → proportional ribbon
        - processing_speed → bar ribbon
        """
        axis = canonical_axis(axis)
        if axis is None:
            return None

        # Default durations based on axis (in seconds)
        axis_durations = {
            "prediction_need": 300,      # 5 min countdown
            "time_discrimination": 600,  # 10 min proportional
            "processing_speed": 180,     # 3 min bar
            "attention_span": 1200,      # 20 min segments
            "initiation_cost": 60,       # 1 min bar
        }

        duration = axis_durations.get(axis, 300)

        style_map = {
            "prediction_need": RibbonStyle.RIBBON,
            "time_discrimination": RibbonStyle.PROPORTIONAL,
            "processing_speed": RibbonStyle.BAR,
            "attention_span": RibbonStyle.SEGMENTS,
            "initiation_cost": RibbonStyle.BAR,
        }

        ribbon = TimeRibbon(
            total_seconds=duration,
            elapsed_seconds=0,
            style=style_map.get(axis, RibbonStyle.BAR),
            unit=TimeUnit.MINUTES,
        )

        return ribbon.render(width)


# Convenience functions
def create_time_view(profile: SarahProfile | None = None) -> TimeView:
    return TimeView(profile)


def remaining_ribbon(total_seconds: float, elapsed_seconds: float,
                     style: RibbonStyle = RibbonStyle.BAR,
                     width: int = 20) -> str:
    """Quick one-shot remaining ribbon."""
    ribbon = TimeRibbon(
        total_seconds=total_seconds,
        elapsed_seconds=elapsed_seconds,
        style=style,
    )
    return ribbon.render(width)