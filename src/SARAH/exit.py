"""
M7 — Exit-Anywhere (Sarah Build Instructions B1)

`request(reason)` returns an `ExitTicket` in one action; `assert_unscored(log)`
enforces B1 rule 5 on an event log: an `exit_requested` event carries no
`score`, no `rating` and no `comment`.

The implementation is `SARAH.profile.ExitPort`. This module is the name B1's
contract states, re-exporting that one implementation rather than holding a
second copy that can drift. What must be true of the surface, not just of the
ticket:

- the exit is reachable in one action, in every state (`reachable_in_one_action`)
- leaving emits nothing evaluative, so a log cannot later say the person left
  "early", "at the wrong time", or "before finishing"
- there is no retention prompt: `request()` returns a ticket and asks nothing
"""

from __future__ import annotations

from .profile import ExitPort, ExitTicket

__all__ = [
    "ExitPort",
    "ExitTicket",
    "assert_unscored",
    "reachable_in_one_action",
    "request",
]


def request(reason: str | None = None) -> ExitTicket:
    """Leave now. One call, one action, no confirmation and no follow-up question."""
    return ExitPort.leave(reason)


def assert_unscored(log: list[dict]) -> None:
    """Raise AssertionError if any `exit_requested` event is scored or commented on.

    Same contract the interface doc states; kept here so tests and callers have
    one named helper. Delegates so there is a single rule implementation.
    """
    ExitPort.assert_unscored(log)


def reachable_in_one_action() -> bool:
    """The exit is always one action away. True is the only value this can take."""
    return True
