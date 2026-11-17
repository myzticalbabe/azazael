"""
M10 — Working-Memory Offload (Sarah Build Instructions B4)

`Offload.card(task) -> Card` holds **one instruction**. `Card.steps` is a
one-tuple by construction: `Card.__post_init__` raises on any other length, so a
card cannot quietly become a list to remember — which is the thing this module
exists to remove.

Recognition over recall (§4 M10): every choice a card offers is visible in
`Card.options` and printed by `Card.render()`. `recall_required` is False for
every card, and there is no field that asks a person to remember something the
card is not showing. "Show, don't tell" previews are `Card.preview`: the card
says what will be true when it closes.

The scratchpad is in memory and ordered (`park` / `visible` / `take` / `clear`).
No I/O, no clock, no network (§3 rule 9) — a renderer reads it, and nothing here
persists or adapts on its own. `wm_span` is the only profile axis this module
reads, and it can only *reduce* the number of visible options; an unmeasured
axis keeps the shipped default rather than inventing a measurement.
"""

from __future__ import annotations

from dataclasses import dataclass

from .profile import SarahProfile


MAX_OPTIONS = 3
"""Most choices a card may show. More than this is a menu, not a card."""

DEFAULT_VISIBLE_OPTIONS = 3
"""Shipped default, used when `wm_span` is unmeasured."""

REDUCED_VISIBLE_OPTIONS = 2
"""What a small measured `wm_span` shows. Never a larger number."""

SMALL_WM_SPAN = 0.5
"""Below this measured span the card shows fewer options."""


@dataclass(frozen=True)
class Step:
    """One instruction. A card holds exactly one of these."""

    instruction: str
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.instruction.strip():
            raise ValueError("a step needs a non-empty instruction")


@dataclass(frozen=True)
class Card:
    """One visible card: one instruction, its options, and what "done" looks like.

    `options` are alternatives the person can *see*, so choosing never requires
    recalling what the alternatives were. `recall_required` is False and not
    settable.
    """

    task: str
    steps: tuple[Step, ...]
    options: tuple[str, ...] = ()
    preview: str = ""

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("a card needs a non-empty task")
        if len(self.steps) != 1:
            raise ValueError(
                f"a card holds exactly one instruction, got {len(self.steps)}"
            )
        if len(self.options) > MAX_OPTIONS:
            raise ValueError(
                f"a card shows at most {MAX_OPTIONS} options, got {len(self.options)}"
            )
        for option in self.options:
            if not option.strip():
                raise ValueError("an option needs a non-empty label")

    @property
    def instruction(self) -> str:
        """The single instruction this card carries."""
        return self.steps[0].instruction

    @property
    def recall_required(self) -> bool:
        """False always: everything a choice needs is on the card."""
        return False

    def render(self) -> str:
        """Render the card as text: instruction, preview, then the visible options."""
        lines = [f"[{self.task}] {self.instruction}"]
        if self.preview:
            lines.append(f"  when done: {self.preview}")
        if self.options:
            lines.append("  options: " + " | ".join(self.options))
        return "\n".join(lines)


@dataclass(frozen=True)
class _Template:
    """One task family: its atomic moves, visible options, and completion picture."""

    steps: tuple[str, ...]
    options: tuple[str, ...]
    done: str


# Ordered: the first key found in the task wins, so the specific noun
# ("letter") is listed above the general verb ("write").
_TEMPLATES: tuple[tuple[str, _Template], ...] = (
    ("letter", _Template(
        ("write the first line", "write the next line", "sign it"),
        ("write the first line", "dictate the first line", "copy the address from the envelope"),
        "one line exists on the page",
    )),
    ("email", _Template(
        ("write the first sentence", "write the next sentence", "send it"),
        ("write the first sentence", "dictate the first sentence", "reply with one word"),
        "one sentence exists in the draft",
    )),
    ("reply", _Template(
        ("write the first sentence", "send it"),
        ("write the first sentence", "dictate the first sentence", "reply with one word"),
        "one sentence exists in the draft",
    )),
    ("wash", _Template(
        ("pick up one plate", "wash one plate", "put it on the rack"),
        ("pick up one plate", "fill the sink", "put one plate by the sink"),
        "one plate is clean",
    )),
    ("dish", _Template(
        ("pick up one plate", "wash one plate", "put it on the rack"),
        ("pick up one plate", "fill the sink", "put one plate by the sink"),
        "one plate is clean",
    )),
    ("clean", _Template(
        ("pick up one thing", "put it where it belongs"),
        ("pick up one thing", "wipe one surface", "put one thing away"),
        "one thing is back in place",
    )),
    ("tidy", _Template(
        ("pick up one thing", "put it where it belongs"),
        ("pick up one thing", "clear one surface", "put one thing away"),
        "one surface is clear",
    )),
    ("call", _Template(
        ("open the phone to the number", "press call"),
        ("open the phone to the number", "write the number on paper", "open the contact"),
        "the call is placed",
    )),
    ("phone", _Template(
        ("open the phone to the number", "press call"),
        ("open the phone to the number", "write the number on paper", "open the contact"),
        "the call is placed",
    )),
    ("pay", _Template(
        ("open the bill", "pay it"),
        ("open the bill", "write the amount on paper", "open the payment page"),
        "the bill is paid",
    )),
    ("form", _Template(
        ("open the form", "fill in the first box"),
        ("open the form", "read the first question", "fill in the first box"),
        "one box is filled",
    )),
    ("read", _Template(
        ("open to page one", "read the first paragraph"),
        ("open to page one", "read the first sentence", "listen to the first minute"),
        "one paragraph is read",
    )),
    ("study", _Template(
        ("open the book", "read the first paragraph"),
        ("open the book", "read the first sentence", "write one heading"),
        "one page is open",
    )),
    ("pack", _Template(
        ("put one item in the bag", "put the next item in"),
        ("put one item in the bag", "write the packing list", "lay the bag open"),
        "one item is in the bag",
    )),
    ("cook", _Template(
        ("take one ingredient out", "read the first line of the recipe"),
        ("take one ingredient out", "open the fridge", "read the first line of the recipe"),
        "one ingredient is on the counter",
    )),
    ("walk", _Template(
        ("put your shoes where you can see them", "put your shoes on"),
        ("put your shoes where you can see them", "open the door", "put your shoes on"),
        "your shoes are on",
    )),
    ("appointment", _Template(
        ("open the calendar to the date", "write down the time"),
        ("open the calendar to the date", "write the date on paper", "set a reminder"),
        "the date and time are written down",
    )),
    ("shop", _Template(
        ("pick up the pen", "write one item on the list"),
        ("pick up the pen", "write one item on the list", "open the shop list"),
        "one item is on the list",
    )),
    ("shower", _Template(
        ("touch the tap", "turn the water on"),
        ("touch the tap", "turn the water on", "put a towel within reach"),
        "the water is running",
    )),
    ("bed", _Template(
        ("touch the blanket", "pull the blanket back"),
        ("touch the blanket", "pull the blanket back", "turn the light down"),
        "the blanket is back",
    )),
    ("exercise", _Template(
        ("put your shoes where you can see them", "put your shoes on"),
        ("put your shoes where you can see them", "fill a water bottle", "put your shoes on"),
        "your shoes are on",
    )),
    ("write", _Template(
        ("write the first line", "write the next line"),
        ("write the first line", "dictate the first line", "open the page"),
        "one line exists on the page",
    )),
)

_DEFAULT_TEMPLATE = _Template(
    ("put the thing you need where you can see it", "pick it up"),
    (
        "put the thing you need where you can see it",
        "open the place the task happens in",
        "pick up the one object the task starts with",
    ),
    "the thing is in front of you",
)


def _template_for(task: str) -> _Template:
    """Pick the family template for a task, deterministically. Never returns None."""
    lowered = task.lower()
    for key, template in _TEMPLATES:
        if key in lowered:
            return template
    return _DEFAULT_TEMPLATE


def _visible_options(profile: SarahProfile | None) -> int:
    """How many options to show. `wm_span` can only lower this number."""
    if profile is None:
        return DEFAULT_VISIBLE_OPTIONS
    span = profile.wm_span
    if span is not None and span < SMALL_WM_SPAN:
        return REDUCED_VISIBLE_OPTIONS
    return DEFAULT_VISIBLE_OPTIONS


class Offload:
    """M10 — the card factory plus a visible, ordered scratchpad.

    `card()` and `split()` are class-level: the acceptance command in B4 calls
    them on the class, and neither needs state. The scratchpad needs state, so
    `park` / `visible` / `take` / `clear` are instance methods.
    """

    def __init__(self) -> None:
        self._parked: list[str] = []

    # ── cards ────────────────────────────────────────────────────────────────

    @classmethod
    def card(cls, task: str, profile: SarahProfile | None = None) -> Card:
        """One task, one card, one instruction."""
        template = _template_for(task)
        limit = _visible_options(profile)
        return Card(
            task=task,
            steps=(Step(instruction=template.steps[0]),),
            options=template.options[:limit],
            preview=f"{template.done}",
        )

    @classmethod
    def split(cls, task: str, profile: SarahProfile | None = None) -> list[Card]:
        """The task as a series of cards, each still holding exactly one instruction."""
        template = _template_for(task)
        limit = _visible_options(profile)
        return [
            Card(
                task=task,
                steps=(Step(instruction=instruction),),
                options=template.options[:limit],
                preview=f"{template.done}",
            )
            for instruction in template.steps
        ]

    # ── scratchpad ───────────────────────────────────────────────────────────

    def park(self, item: str) -> int:
        """Put an item on the visible scratchpad. Returns its 1-based position."""
        if not item.strip():
            raise ValueError("cannot park an empty item")
        self._parked.append(item)
        return len(self._parked)

    def visible(self) -> tuple[str, ...]:
        """Everything on the scratchpad, in the order it was parked."""
        return tuple(self._parked)

    def take(self, item: str) -> bool:
        """Remove the first exact match. True if it was there."""
        for index, parked in enumerate(self._parked):
            if parked == item:
                del self._parked[index]
                return True
        return False

    def clear(self) -> None:
        """Empty the scratchpad."""
        self._parked.clear()

    def __len__(self) -> int:
        return len(self._parked)


__all__ = [
    "Card",
    "DEFAULT_VISIBLE_OPTIONS",
    "MAX_OPTIONS",
    "Offload",
    "REDUCED_VISIBLE_OPTIONS",
    "SMALL_WM_SPAN",
    "Step",
]
