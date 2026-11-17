"""
M5 — Self-Pacing and Unlimited Time (B6, lane 2)

Two rules, both about what does **not** exist:

* **No countdown exists unless the user asks for one.** `Timer()` is
  unrequested by default, and an unrequested timer refuses to start, has no
  remaining time to report, and emits no ticks. There is no implicit "session
  clock" a renderer could accidentally display.
* **A pause must actually pause.** While paused, `tick()` advances nothing and
  returns zero, so a renderer driven by tick count freezes. Elapsed time
  excludes the paused interval, which is what "unlimited time" has to mean in
  arithmetic.

The timer takes a delta rather than reading a clock (`tick(dt_s)`), so it is
deterministic and testable: no I/O, no `time.time()`, no drift between a test and
a session.

M16 integration: `initiation_cost` from the clinical seed is carried on the
timer so a caller knows when to *offer* it sooner. It never enables the timer —
an offer is not a request.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _axis(profile: Any, name: str) -> float | None:
    """Read one profile axis as a float in [0, 1], or None when unmeasured."""
    if profile is None:
        return None
    value = getattr(profile, name, None)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        # Unmeasured, not zero: an absent or non-numeric axis stays `None`, and
        # the branch decides by type rather than swallowing a conversion error.
        return None
    return min(1.0, max(0.0, float(value)))


@dataclass
class Timer:
    """A session timer that only exists when it was requested.

    `enabled` is set at construction by the caller's explicit request. Every
    mutating method is a no-op on a disabled timer and reports that in its
    return value rather than raising: a renderer asking an unrequested timer to
    pause should not crash the session.
    """

    enabled: bool = False
    limit_s: float | None = None
    initiation_cost: float | None = None

    _elapsed_s: float = field(default=0.0, init=False, repr=False)
    _ticks: int = field(default=0, init=False, repr=False)
    _paused: bool = field(default=False, init=False, repr=False)
    _started: bool = field(default=False, init=False, repr=False)

    @classmethod
    def for_user(cls, profile: Any = None, *, requested: bool = False) -> "Timer":
        """Build a timer carrying the profile's `initiation_cost` for the offer."""
        return cls(enabled=bool(requested), initiation_cost=_axis(profile, "initiation_cost"))

    # -- request surface ----------------------------------------------------

    def requested(self) -> bool:
        """Was a timer explicitly requested? False is the shipped default."""
        return bool(self.enabled)

    def offer_sooner(self) -> float:
        """How much earlier to offer the timer: the initiation cost, 0 when unmeasured.

        A user who finds starting costly is offered the timer earlier; the value
        is advisory to the renderer and has no effect on the timer itself.
        """
        return 0.0 if self.initiation_cost is None else float(self.initiation_cost)

    # -- control ------------------------------------------------------------

    def start(self) -> bool:
        """Start only a requested timer. Returns whether it is now running."""
        if not self.enabled:
            return False
        self._started = True
        self._paused = False
        return True

    def pause(self) -> bool:
        """Pause a running timer. Returns whether it is now paused."""
        if not self.enabled or not self._started:
            return False
        self._paused = True
        return True

    def resume(self) -> bool:
        """Resume a paused timer. Returns whether it is now running."""
        if not self.enabled or not self._started or not self._paused:
            return False
        self._paused = False
        return True

    def stop(self) -> None:
        self._started = False
        self._paused = False

    # -- ticks --------------------------------------------------------------

    def tick(self, dt_s: float = 0.0) -> int:
        """Advance by `dt_s`; return ticks emitted (0 or 1).

        While paused, or before `start()`, the clock does not move and nothing
        is emitted — the pause is real, not a label on a still-running clock.
        """
        if not self.enabled or not self._started or self._paused:
            return 0
        if isinstance(dt_s, bool) or not isinstance(dt_s, (int, float)):
            raise TypeError(f"dt_s must be a number, got {dt_s!r}")
        if dt_s < 0:
            raise ValueError(f"dt_s must be >= 0, got {dt_s!r}")
        self._elapsed_s += float(dt_s)
        self._ticks += 1
        return 1

    @property
    def ticks(self) -> int:
        """Ticks emitted so far — the value a renderer animates from."""
        return self._ticks

    @property
    def elapsed_s(self) -> float:
        """Time spent running, with paused intervals excluded."""
        return self._elapsed_s

    @property
    def paused(self) -> bool:
        return self._paused

    def remaining(self) -> float | None:
        """Seconds left, or **None when no countdown exists**.

        `None` is the answer for every timer until a limit is supplied: there is
        no countdown unless one was asked for, and a renderer that formats this
        must handle `None` rather than receive a fabricated number.
        """
        if not self.enabled or self.limit_s is None:
            return None
        return max(0.0, float(self.limit_s) - self._elapsed_s)
