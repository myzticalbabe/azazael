"""
M15 — Cross-Modal Redundancy (B6, lane 2)

Redundancy is **not simultaneity**. The same content is rendered over three
independent channels — text, audio, pictogram — so that any one of them can be
switched off and the content still arrives. A design that requires all three at
once is a design that fails the moment a user turns one down.

Two guarantees are enforced rather than documented:

* `deliver(content, off=(...))` returns one rendition per remaining channel and
  raises `NoChannelAvailable` when every channel is off — it never returns an
  empty dict, because "delivered nothing" must not be confusable with "delivered
  quietly".
* Every rendition carries the **same** content. A channel may present it
  differently (a pictogram is a glyph, not a paragraph), but it may not carry a
  shortened version, because a shortened copy is a second message.

M16 integration: `interoceptive_accuracy` sets the channel order. A user who
reads their own state poorly gets the explicit, re-readable channels first; a
user with accurate interoception gets audio first so the visual channel is not
spent on something they already track.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

CHANNELS: tuple[str, ...] = ("text", "audio", "pictogram")
"""The three declared channels. At least three, by contract: one can always be off."""

DEFAULT_PRIORITY: tuple[str, ...] = ("text", "audio", "pictogram")
"""Order used when interoception is unmeasured — explicit first, ambient last."""

LOW_INTEROCEPTION_PRIORITY: tuple[str, ...] = ("text", "pictogram", "audio")
"""When interoception is poor: the two re-readable channels lead."""

HIGH_INTEROCEPTION_PRIORITY: tuple[str, ...] = ("audio", "text", "pictogram")
"""When interoception is accurate: audio leads, freeing the visual channel."""

INTEROCEPTION_SPLIT = 0.5
"""Above this the audio-first order is used; at or below it, the explicit order."""


class NoChannelAvailable(ValueError):
    """Every channel was switched off, so the content cannot be delivered."""


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


@dataclass(frozen=True)
class Rendition:
    """One channel's copy of the content."""

    channel: str
    content: str

    def __str__(self) -> str:
        return f"{self.channel}:{self.content}"


class Redundancy:
    """Fan one message out over the channels that are still on."""

    def available(self, off: Iterable[str] = ()) -> tuple[str, ...]:
        """Channels still on, in priority order. Unknown names in `off` are ignored."""
        disabled = {str(name) for name in off}
        return tuple(channel for channel in CHANNELS if channel not in disabled)

    def prioritise(self, profile: Any = None) -> tuple[str, ...]:
        """Channel order for this profile. `interoceptive_accuracy` decides it."""
        accuracy = _axis(profile, "interoception")
        if accuracy is None:
            return DEFAULT_PRIORITY
        return HIGH_INTEROCEPTION_PRIORITY if accuracy > INTEROCEPTION_SPLIT else LOW_INTEROCEPTION_PRIORITY

    def deliver(self, content: str, off: Iterable[str] = (), profile: Any = None) -> dict[str, str]:
        """Same content over every channel that is on, keyed by channel.

        Raises `NoChannelAvailable` when nothing is left on: a silent empty
        result would read downstream as "no content to show", which is a
        different and much worse state than "you turned everything off".
        """
        if not isinstance(content, str):
            raise TypeError(f"content must be a str, got {type(content).__name__}")
        disabled = {str(name) for name in off}
        order = [channel for channel in self.prioritise(profile) if channel not in disabled]
        if not order:
            raise NoChannelAvailable(
                f"all channels switched off ({sorted(disabled)}); leave one on — "
                "redundancy means one may be off, never all"
            )
        return {channel: content for channel in order}

    def renditions(self, content: str, off: Iterable[str] = (), profile: Any = None) -> tuple[Rendition, ...]:
        """`deliver()` as ordered objects, for a renderer that wants the order."""
        return tuple(Rendition(channel, text) for channel, text in self.deliver(content, off, profile).items())
