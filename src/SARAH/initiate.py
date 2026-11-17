"""
M11 — Initiation Ladder (Sarah Build Instructions B4)

`Initiate.next_action(task, profile) -> Invitation` names **the next physical
action** — "put a pen and paper in front of you", not "get ready to write" —
and phrases it as an invitation with a choice.

Two rules are enforced in code, not described in prose:

- **Physical.** `_is_physical` gates the action's first word against
  `PHYSICAL_VERBS`. The move tables are written through that gate; an
  `Invitation` built around "get ready" or "plan" raises rather than shipping a
  threshold nobody can cross.
- **Invitation, never a command.** `Invitation.__post_init__` requires a choice
  marker and forbids "!", so an imperative cannot be constructed by accident.
  A decline choice is mandatory and always visible.

`initiation_cost` can only *shrink* the first move. The shipped default is the
small move; a high measured cost gets the tiny one; the larger move exists only
when the caller asks for it by name (`full=True`) and is refused with a reported
`basis` when the axis is high — the same clamp-and-report shape the pacing
governor uses for speed. No axis raises a rung, adds a step, or adds a demand.

Body doubling is offered only when the caller asks (`body_double=True`) and
always carries its label: a self-report tool, not evidence-based practice.
"""

from __future__ import annotations

from dataclasses import dataclass

from .profile import SarahProfile


PHYSICAL_VERBS = frozenset(
    {
        "open", "pick", "put", "place", "press", "lift", "touch", "walk", "go",
        "step", "stand", "sit", "turn", "type", "write", "click", "hold",
        "carry", "reach", "read", "say", "tap", "plug", "slide", "pull",
        "push", "take", "point", "look", "set", "fill", "send", "print",
        "sign", "dial", "knock", "rest", "move", "pour", "stir", "cut",
        "wipe", "hang", "fold", "switch", "close", "bring", "gather", "hand",
        "wash", "rinse", "scrub", "pack", "brush", "dress", "eat", "drink",
        "climb", "run", "throw", "catch",
    }
)
"""First words that name a physical move. A verb absent here is not a rung."""

CHOICE_MARKER = " or "
"""Every invitation offers at least two courses; this is the visible marker."""

DECLINE_CHOICE = "leave it for now"
"""Always present. Declining is a first-class answer, never an omission."""

TINY_COST = 0.66
"""At or above this measured `initiation_cost`, the tiny move is the rung."""

LOW_COST = 0.33
"""At or below this measured cost, `full=True` may show the larger move."""

MAX_RUNGS = 3
SHORT_SPAN = 0.5
"""A measured `attention_span` below this shows two rungs instead of three."""

BODY_DOUBLE_LABEL = (
    "optional: someone sits nearby while you do it — "
    "a self-report tool, not evidence-based practice"
)


def _is_physical(action: str) -> bool:
    """True when the action's first word names a physical move."""
    words = action.strip().lower().split()
    if not words:
        return False
    return words[0] in PHYSICAL_VERBS


@dataclass(frozen=True)
class Invitation:
    """One rung: a physical action, its visible choices, and why it is this size.

    `text` is what a renderer shows. `action` is the move itself, kept separate
    so a caller can log or diff it without parsing prose.
    """

    task: str
    action: str
    text: str
    choices: tuple[str, ...]
    decline_choice: str = DECLINE_CHOICE
    body_double: str | None = None
    basis: str = ""

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise ValueError("an invitation needs a non-empty task")
        if not _is_physical(self.action):
            raise ValueError(
                f"not a physical next action: {self.action!r} "
                "(start with a verb a body can perform)"
            )
        if "!" in self.text:
            raise ValueError("an invitation never uses an exclamation mark")
        if CHOICE_MARKER not in self.text.lower():
            raise ValueError("an invitation must offer a choice")
        if len(self.choices) < 2:
            raise ValueError("an invitation offers at least two choices")
        if self.decline_choice not in self.choices:
            raise ValueError("the decline choice must be visible")
        if self.action == self.decline_choice:
            raise ValueError("the action cannot be the decline choice")

    def is_invitation(self) -> bool:
        """True when this is a physical move offered with a visible choice."""
        return (
            _is_physical(self.action)
            and "!" not in self.text
            and CHOICE_MARKER in self.text.lower()
            and self.decline_choice in self.choices
        )


@dataclass(frozen=True)
class _Move:
    """A task family, ordered smallest first: (tiny, small, full)."""

    tiny: str
    small: str
    full: str


# Specific nouns before general verbs, as in offload.py.
_MOVES: tuple[tuple[str, _Move], ...] = (
    ("letter", _Move(
        "touch the pen",
        "put a pen and paper in front of you",
        "write the first line",
    )),
    ("email", _Move(
        "rest your hand on the mouse",
        "open the draft",
        "write the first sentence of the reply",
    )),
    ("reply", _Move(
        "rest your hand on the mouse",
        "open the draft",
        "write the first sentence of the reply",
    )),
    ("wash", _Move(
        "touch the tap",
        "pick up one plate",
        "wash one plate",
    )),
    ("dish", _Move(
        "touch the tap",
        "pick up one plate",
        "wash one plate",
    )),
    ("clean", _Move(
        "touch one object that is out of place",
        "pick up one thing",
        "put one thing away",
    )),
    ("tidy", _Move(
        "touch one object that is out of place",
        "pick up one thing",
        "clear one surface",
    )),
    ("call", _Move(
        "hold the phone",
        "open the phone to the number",
        "dial the number",
    )),
    ("phone", _Move(
        "hold the phone",
        "open the phone to the number",
        "dial the number",
    )),
    ("pay", _Move(
        "touch the bill",
        "open the bill",
        "press the pay button",
    )),
    ("form", _Move(
        "touch the pen",
        "open the form",
        "fill in the first box",
    )),
    ("read", _Move(
        "touch the book",
        "open to page one",
        "read the first paragraph",
    )),
    ("study", _Move(
        "touch the book",
        "open the book",
        "read the first paragraph",
    )),
    ("pack", _Move(
        "touch the bag",
        "put one item in the bag",
        "pack the bag",
    )),
    ("cook", _Move(
        "open the fridge door",
        "take one ingredient out",
        "read the first line of the recipe",
    )),
    ("walk", _Move(
        "put your shoes where you can see them",
        "put your shoes on",
        "step outside the door",
    )),
    ("appointment", _Move(
        "open the calendar",
        "open the calendar to the date",
        "put the appointment in the calendar",
    )),
    ("shop", _Move(
        "pick up the pen",
        "write one item on the list",
        "go to the first aisle",
    )),
    ("shower", _Move(
        "touch the tap",
        "turn the water on",
        "step into the shower",
    )),
    ("bed", _Move(
        "touch the blanket",
        "pull the blanket back",
        "pull the blanket over you",
    )),
    ("exercise", _Move(
        "put your shoes where you can see them",
        "put your shoes on",
        "stand up once",
    )),
    ("write", _Move(
        "touch the pen",
        "put a pen and paper in front of you",
        "write the first line",
    )),
)

_DEFAULT_MOVE = _Move(
    "put your hand on the thing you need",
    "pick the thing up",
    "lift the thing in your hand",
)
"""An unknown task still gets a physical rung. It never gets a spoken one."""


def _move_for(task: str) -> _Move:
    """Pick the family move for a task, deterministically. Never returns None."""
    lowered = task.lower()
    for key, move in _MOVES:
        if key in lowered:
            return move
    return _DEFAULT_MOVE


def _invitation(
    task: str,
    action: str,
    smaller: str | None,
    basis: str,
    body_double: bool,
) -> Invitation:
    """Build one validated invitation around an already-physical action."""
    choices = [action]
    if smaller is not None and smaller != action:
        choices.append(f"an even smaller move: {smaller}")
    choices.append(DECLINE_CHOICE)

    text = f"You could {action} — or {DECLINE_CHOICE}."
    if len(choices) == 3:
        text += f" There is a smaller step if you want it: {smaller}."

    return Invitation(
        task=task,
        action=action,
        text=text,
        choices=tuple(choices),
        body_double=BODY_DOUBLE_LABEL if body_double else None,
        basis=basis,
    )


class Initiate:
    """M11 — the initiation ladder: one physical move, offered as a choice."""

    @staticmethod
    def next_action(
        task: str,
        profile: SarahProfile | None = None,
        full: bool = False,
        body_double: bool = False,
    ) -> Invitation:
        """The next physical action, as an invitation with a choice.

        Default is the small move. A high measured `initiation_cost` gets the
        tiny move. `full=True` shows the larger move only when the axis is not
        high; otherwise it is refused and `basis` says so.
        """
        move = _move_for(task)
        cost = profile.initiation_cost if profile is not None else None

        if cost is None:
            if full:
                return _invitation(
                    task, move.full, move.small,
                    "initiation_cost not measured; larger move requested → shown",
                    body_double,
                )
            return _invitation(
                task, move.small, move.tiny,
                "initiation_cost not measured → small move",
                body_double,
            )

        if cost >= TINY_COST:
            if full:
                return _invitation(
                    task, move.tiny, None,
                    f"initiation_cost={cost:.2f} is high; larger move requested → "
                    "kept the smallest move",
                    body_double,
                )
            return _invitation(
                task, move.tiny, None,
                f"initiation_cost={cost:.2f} is high → smallest move",
                body_double,
            )

        if full and cost <= LOW_COST:
            return _invitation(
                task, move.full, move.small,
                f"initiation_cost={cost:.2f} is low; larger move requested → shown",
                body_double,
            )

        if full:
            return _invitation(
                task, move.small, move.tiny,
                f"initiation_cost={cost:.2f} is mid-range; larger move requested → "
                "kept the small move",
                body_double,
            )

        return _invitation(
            task, move.small, move.tiny,
            f"initiation_cost={cost:.2f} → small move",
            body_double,
        )

    @staticmethod
    def ladder(
        task: str,
        profile: SarahProfile | None = None,
        rungs: int = MAX_RUNGS,
        body_double: bool = False,
    ) -> list[Invitation]:
        """The task as 2-3 rungs, smallest first. Never more than `MAX_RUNGS`."""
        move = _move_for(task)
        ordered = [rung for rung in (move.tiny, move.small, move.full) if rung]
        # Remove duplicates while keeping the smallest-first order.
        unique: list[str] = []
        for action in ordered:
            if action not in unique:
                unique.append(action)

        count = max(1, min(rungs, MAX_RUNGS, len(unique)))
        span = profile.attention_span if profile is not None else None
        if span is not None and span < SHORT_SPAN:
            count = min(count, 2)

        result: list[Invitation] = []
        for index in range(count):
            action = unique[index]
            smaller = unique[index - 1] if index > 0 else None
            basis = f"rung {index + 1} of {count}, smallest first"
            result.append(_invitation(task, action, smaller, basis, body_double))
        return result


__all__ = [
    "BODY_DOUBLE_LABEL",
    "CHOICE_MARKER",
    "DECLINE_CHOICE",
    "Invitation",
    "Initiate",
    "LOW_COST",
    "MAX_RUNGS",
    "PHYSICAL_VERBS",
    "SHORT_SPAN",
    "TINY_COST",
]
