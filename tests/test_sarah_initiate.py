"""
Tests for M11 — the Initiation Ladder (B4).

The falsifiable claims: the rung is physical, the phrasing is an invitation with
a visible decline, `initiation_cost` only ever shrinks the move, and the
body-double offer carries its self-report label.
"""

from __future__ import annotations

import pytest

from SARAH.initiate import (
    BODY_DOUBLE_LABEL,
    DECLINE_CHOICE,
    MAX_RUNGS,
    PHYSICAL_VERBS,
    Invitation,
    Initiate,
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


def first_word(action: str) -> str:
    return action.split()[0].lower()


def test_default_is_an_invitation_with_a_choice():
    invitation = Initiate.next_action("wash the dishes")
    assert invitation.is_invitation()
    assert invitation.decline_choice in invitation.choices
    assert " or " in invitation.text.lower()


def test_every_task_gets_a_physical_action():
    for task in TASKS:
        invitation = Initiate.next_action(task)
        assert first_word(invitation.action) in PHYSICAL_VERBS, invitation.action


def test_high_initiation_cost_shrinks_to_the_tiny_move():
    small = Initiate.next_action("wash the dishes", Profile(initiation_cost=0.1))
    tiny = Initiate.next_action("wash the dishes", Profile(initiation_cost=0.9))
    assert small.action == "pick up one plate"
    assert tiny.action == "touch the tap"
    assert "high" in tiny.basis


def test_full_is_shown_only_when_the_axis_allows_it():
    full = Initiate.next_action("wash the dishes", Profile(initiation_cost=0.1), full=True)
    assert full.action == "wash one plate"
    assert "requested" in full.basis


def test_full_is_refused_and_reported_when_cost_is_high():
    full = Initiate.next_action("wash the dishes", Profile(initiation_cost=0.9), full=True)
    assert full.action == "touch the tap"
    assert "kept the smallest move" in full.basis


def test_no_axis_adds_a_demand():
    base = Initiate.next_action("wash the dishes", Profile())
    for cost in (0.0, 0.2, 0.5, 0.8, 1.0):
        invitation = Initiate.next_action("wash the dishes", Profile(initiation_cost=cost))
        assert invitation.action in (base.action, "touch the tap"), cost


def test_command_phrasing_is_rejected():
    with pytest.raises(ValueError):
        Invitation(
            task="t",
            action="open the lid",
            text="Open the lid.",
            choices=("open the lid", DECLINE_CHOICE),
        )


def test_non_physical_action_is_rejected():
    with pytest.raises(ValueError):
        Invitation(
            task="t",
            action="get ready",
            text="You could get ready — or leave it for now.",
            choices=("get ready", DECLINE_CHOICE),
        )


def test_exclamation_is_rejected():
    with pytest.raises(ValueError):
        Invitation(
            task="t",
            action="open the lid",
            text="You could open the lid — or not!",
            choices=("open the lid", "not"),
        )


def test_decline_choice_must_be_visible():
    with pytest.raises(ValueError):
        Invitation(
            task="t",
            action="open the lid",
            text="You could open the lid — or not.",
            choices=("open the lid", "not"),
        )


def test_blank_action_is_not_physical():
    with pytest.raises(ValueError):
        Invitation(
            task="t",
            action="   ",
            text="You could x — or y.",
            choices=("x", DECLINE_CHOICE),
        )


def test_ladder_is_smallest_first_and_bounded():
    rungs = Initiate.ladder("wash the dishes")
    assert 2 <= len(rungs) <= MAX_RUNGS
    for invitation in rungs:
        assert invitation.is_invitation()
    assert rungs[0].action == "touch the tap"
    assert rungs[-1].action == "wash one plate"


def test_every_rung_of_every_family_is_physical():
    for task in TASKS:
        rungs = Initiate.ladder(task, rungs=MAX_RUNGS)
        assert rungs, task
        for invitation in rungs:
            assert first_word(invitation.action) in PHYSICAL_VERBS, (
                task,
                invitation.action,
            )
            assert invitation.is_invitation(), (task, invitation.action)


def test_short_attention_span_shortens_the_ladder():
    short = Initiate.ladder("wash the dishes", Profile(attention_span=0.1))
    assert len(short) == 2


def test_body_double_is_off_by_default_and_labelled_when_asked():
    assert Initiate.next_action("wash the dishes").body_double is None
    offered = Initiate.next_action("wash the dishes", body_double=True)
    assert offered.body_double == BODY_DOUBLE_LABEL
    assert "self-report" in (offered.body_double or "")
    assert "not evidence" in (offered.body_double or "")


def test_unknown_task_still_gets_a_physical_rung():
    invitation = Initiate.next_action("something nobody wrote a template for")
    assert first_word(invitation.action) in PHYSICAL_VERBS
    assert invitation.is_invitation()


def test_no_text_shouts():
    for task in TASKS:
        assert "!" not in Initiate.next_action(task).text
