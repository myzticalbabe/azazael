"""
Tests for M10 — the Working-Memory Offload (B4).

The claims that could be false are asserted directly: a card ever holds more than
one instruction, a choice ever needs recall, `wm_span` ever *adds* options, and
the module ever reaches a clock or a network.
"""

from __future__ import annotations

import inspect

import pytest

from SARAH.offload import (
    DEFAULT_VISIBLE_OPTIONS,
    MAX_OPTIONS,
    Card,
    Offload,
    Step,
)
from SARAH.profile import Profile

TASKS = (
    "write a letter",
    "wash the dishes",
    "send an email",
    "pay the bill",
    "clean the kitchen",
    "read a chapter",
    "pack a bag",
    "cook dinner",
    "go for a walk",
    "something nobody wrote a template for",
)


def test_acceptance_command_holds():
    assert len(Offload.card("write a letter").steps) == 1


def test_every_task_gets_exactly_one_instruction():
    for task in TASKS:
        card = Offload.card(task)
        assert len(card.steps) == 1, task
        assert card.instruction.strip(), task


def test_every_option_is_visible_and_recall_is_never_required():
    card = Offload.card("wash the dishes")
    assert card.recall_required is False
    assert 1 <= len(card.options) <= MAX_OPTIONS
    rendered = card.render()
    assert card.instruction in rendered
    for option in card.options:
        assert option in rendered


def test_card_is_deterministic():
    assert Offload.card("write a letter") == Offload.card("write a letter")


def test_unknown_task_still_gets_a_real_card():
    card = Offload.card("something nobody wrote a template for")
    assert len(card.steps) == 1
    assert card.options


def test_low_wm_span_reduces_options_and_high_never_adds():
    low = Offload.card("write a letter", Profile(wm_span=0.1))
    high = Offload.card("write a letter", Profile(wm_span=0.9))
    unmeasured = Offload.card("write a letter", Profile())
    assert len(unmeasured.options) == DEFAULT_VISIBLE_OPTIONS
    assert len(low.options) < len(unmeasured.options)
    assert len(high.options) <= MAX_OPTIONS
    assert not len(high.options) > len(unmeasured.options)


def test_two_steps_raise():
    with pytest.raises(ValueError):
        Card(task="t", steps=(Step("first"), Step("second")))


def test_more_than_max_options_raise():
    with pytest.raises(ValueError):
        Card(
            task="t",
            steps=(Step("one"),),
            options=tuple(f"option {i}" for i in range(MAX_OPTIONS + 1)),
        )


def test_blank_instruction_raises():
    with pytest.raises(ValueError):
        Step("   ")


def test_split_yields_one_instruction_per_card():
    cards = Offload.split("wash the dishes")
    assert len(cards) > 1
    for card in cards:
        assert len(card.steps) == 1
    assert cards[0].instruction == Offload.card("wash the dishes").instruction


def test_scratchpad_is_ordered_and_visible():
    pad = Offload()
    assert pad.park("call the dentist") == 1
    assert pad.park("buy stamps") == 2
    assert pad.visible() == ("call the dentist", "buy stamps")
    assert len(pad) == 2


def test_take_removes_one_match_and_reports():
    pad = Offload()
    pad.park("a")
    pad.park("a")
    pad.park("b")
    assert pad.take("a") is True
    assert pad.visible() == ("a", "b")
    assert pad.take("missing") is False
    pad.clear()
    assert pad.visible() == ()


def test_empty_park_raises():
    with pytest.raises(ValueError):
        Offload().park("   ")


def test_no_clock_and_no_network_in_the_module():
    module = __import__("SARAH.offload", fromlist=["Offload"])
    source = inspect.getsource(module)
    for forbidden in ("import time", "import socket", "import requests", "import urllib", "time.time"):
        assert forbidden not in source, forbidden
