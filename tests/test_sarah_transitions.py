"""
Tests for M4 — Gradual-Transition Engine (Sarah Build Instructions B2, lane 2).

Three rules, each with the negative case the brief names:

* a ramp under 400 ms is **clamped and reported**, never honoured — "we cut
  straight to the next state because the user seemed impatient" is the failure
  this module exists to prevent;
* two modalities changing in one tick **raise**, never warn;
* every change is announced one beat before it starts.

The module plans and never sleeps, so these tests read absolute millisecond
offsets instead of waiting on a clock.
"""

import pytest

from SARAH.sensory import (
    ANNOUNCE_BEAT_MS,
    MAX_RAMP_MS,
    MIN_RAMP_MS,
    InvalidRamp,
    Ramp,
    SimultaneousChange,
    Transitions,
    clamp_duration,
)


class TestClampDuration:
    """The floor and ceiling are honoured and the clamp is reported."""

    def test_floor_is_400_ms(self):
        assert MIN_RAMP_MS == 400

    def test_ceiling_is_1200_ms(self):
        assert MAX_RAMP_MS == 1200

    @pytest.mark.parametrize("requested", [0, 1, 120, 399])
    def test_sub_floor_request_is_clamped_not_honoured(self, requested):
        """The whole point: a fast request does not become a cut."""
        duration, clamped = clamp_duration(requested)
        assert duration == MIN_RAMP_MS
        assert clamped is True

    @pytest.mark.parametrize("requested", [400, 600, 800, 1200])
    def test_in_range_request_is_honoured(self, requested):
        duration, clamped = clamp_duration(requested)
        assert duration == requested
        assert clamped is False

    @pytest.mark.parametrize("requested", [1201, 2000, 60_000])
    def test_over_ceiling_request_is_clamped(self, requested):
        duration, clamped = clamp_duration(requested)
        assert duration == MAX_RAMP_MS
        assert clamped is True

    def test_float_duration_rounds_before_clamping(self):
        """Rounding happens first, so 399.6 is a 400 ms ramp and 399.4 is clamped."""
        assert clamp_duration(399.6) == (MIN_RAMP_MS, False)
        assert clamp_duration(399.4) == (MIN_RAMP_MS, True)
        assert clamp_duration(800.4) == (800, False)

    @pytest.mark.parametrize("bad", ["400", None, True])
    def test_non_numeric_duration_is_refused(self, bad):
        with pytest.raises(InvalidRamp):
            clamp_duration(bad)

    def test_nan_duration_is_refused(self):
        """NaN compares False against both bounds, so it must be caught first."""
        with pytest.raises(InvalidRamp):
            clamp_duration(float("nan"))


class TestRampRecordsTheClamp:
    """A clamped request leaves a record of what was asked for."""

    def test_sub_floor_ramp_reports_both_requested_and_honoured(self):
        ramp = Transitions().ramp("visual", 0.9, 100)
        assert ramp.clamped is True
        assert ramp.requested_ms == 100
        assert ramp.duration_ms == MIN_RAMP_MS
        assert ramp.duration_ms != ramp.requested_ms

    def test_in_range_ramp_is_not_marked_clamped(self):
        ramp = Transitions().ramp("visual", 0.9, 800)
        assert ramp.clamped is False
        assert ramp.duration_ms == 800

    def test_end_time_is_start_plus_honoured_duration(self):
        ramp = Transitions().ramp("visual", 0.9, 100, start_at_ms=1000)
        assert ramp.end_at_ms == 1000 + MIN_RAMP_MS

    def test_zero_duration_never_produces_a_scene_cut(self):
        """Any duration a caller passes yields a ramp of at least 400 ms."""
        ramp = Transitions().ramp("audio", 0.0, 0)
        assert ramp.end_at_ms - ramp.start_at_ms >= MIN_RAMP_MS


class TestNoSimultaneousChanges:
    """Two modalities in one tick raises — it is never a warning."""

    def test_two_modalities_overlapping_raise(self):
        transitions = Transitions()
        transitions.ramp("visual", 0.9, 800, start_at_ms=0)
        with pytest.raises(SimultaneousChange) as excinfo:
            transitions.ramp("audio", 0.2, 800, start_at_ms=0)
        message = str(excinfo.value)
        assert "audio" in message and "visual" in message
        assert "stagger" in message

    def test_second_change_inside_the_first_ramp_raises(self):
        """A partial overlap is still simultaneous."""
        transitions = Transitions()
        transitions.ramp("visual", 0.9, 800, start_at_ms=0)
        with pytest.raises(SimultaneousChange):
            transitions.ramp("audio", 0.2, 800, start_at_ms=200)

    def test_change_after_the_first_ramp_ends_is_allowed(self):
        transitions = Transitions()
        first = transitions.ramp("visual", 0.9, 800, start_at_ms=0)
        second = transitions.ramp("audio", 0.2, 800, start_at_ms=first.end_at_ms)
        assert second.start_at_ms == first.end_at_ms
        assert not first.overlaps(second)

    def test_same_modality_may_be_rescheduled(self):
        """One modality changing twice is not two modalities changing at once."""
        transitions = Transitions()
        transitions.ramp("visual", 0.9, 800, start_at_ms=0)
        second = transitions.ramp("visual", 0.1, 800, start_at_ms=0)
        assert second.modality == "visual"

    def test_raised_change_is_not_scheduled(self):
        """A refused ramp leaves no partial entry behind."""
        transitions = Transitions()
        transitions.ramp("visual", 0.9, 800, start_at_ms=0)
        with pytest.raises(SimultaneousChange):
            transitions.ramp("audio", 0.2, 800, start_at_ms=0)
        assert [ramp.modality for ramp in transitions.pending()] == ["visual"]


class TestPlanStaggers:
    """The batch entry point cannot express the forbidden shape."""

    def test_plan_schedules_changes_sequentially(self):
        transitions = Transitions()
        planned = transitions.plan(
            [("visual", 0.3, 800), ("audio", 0.1, 600), ("haptic", 0.0, 400)]
        )
        assert [ramp.modality for ramp in planned] == ["visual", "audio", "haptic"]
        for previous, current in zip(planned, planned[1:]):
            assert current.start_at_ms == previous.end_at_ms
            assert not previous.overlaps(current)

    def test_plan_never_raises_simultaneous_change(self):
        transitions = Transitions()
        planned = transitions.plan([(f"m{index}", 0.5, 400) for index in range(6)])
        assert len(planned) == 6
        assert len({ramp.start_at_ms for ramp in planned}) == 6

    def test_plan_clamps_each_item_independently(self):
        transitions = Transitions()
        planned = transitions.plan([("visual", 0.5, 50), ("audio", 0.5, 900)])
        assert planned[0].clamped is True and planned[0].duration_ms == MIN_RAMP_MS
        assert planned[1].clamped is False and planned[1].duration_ms == 900

    @pytest.mark.parametrize(
        "bad", [("visual", 0.5), ("visual", 0.5, 800, "extra"), ()]
    )
    def test_plan_refuses_malformed_items(self, bad):
        with pytest.raises(InvalidRamp):
            Transitions().plan([bad])


class TestAnnouncement:
    """Every change is announced one beat before it starts."""

    def test_default_beat_is_250_ms(self):
        assert ANNOUNCE_BEAT_MS == 250

    def test_announcement_precedes_the_start_by_one_beat(self):
        ramp = Transitions().ramp("visual", 0.8, 800, start_at_ms=1000)
        assert ramp.announce_at_ms == 1000 - ANNOUNCE_BEAT_MS
        assert ramp.announce_at_ms < ramp.start_at_ms

    def test_first_ramp_announcement_does_not_go_negative(self):
        ramp = Transitions().ramp("visual", 0.8, 800, start_at_ms=0)
        assert ramp.announce_at_ms == 0

    def test_custom_beat_is_applied(self):
        transitions = Transitions(beat_ms=100)
        ramp = transitions.ramp("visual", 0.8, 800, start_at_ms=500)
        assert ramp.announce_at_ms == 400

    def test_zero_beat_is_refused(self):
        """A zero-length beat is not an announcement; it is the scene cut."""
        with pytest.raises(InvalidRamp):
            Transitions(beat_ms=0)

    def test_announcement_names_modality_target_and_duration(self):
        ramp = Transitions().ramp("visual", 0.75, 800, start_at_ms=1000)
        text = ramp.announcement
        assert "visual" in text
        assert "0.75" in text
        assert "800 ms" in text

    def test_announcements_are_returned_in_start_order(self):
        transitions = Transitions()
        transitions.plan([("visual", 0.3, 800), ("audio", 0.1, 600)])
        lines = transitions.announcements()
        assert len(lines) == 2
        assert "visual" in lines[0] and "audio" in lines[1]


class TestValidationAndInspection:
    """A ramp that cannot describe a transition is refused."""

    @pytest.mark.parametrize("bad", [-0.1, 1.1, 2])
    def test_target_outside_unit_range_is_refused(self, bad):
        with pytest.raises(InvalidRamp):
            Transitions().ramp("visual", bad, 800)

    @pytest.mark.parametrize("bad", ["0.5", None, True])
    def test_non_numeric_target_is_refused(self, bad):
        with pytest.raises(InvalidRamp):
            Transitions().ramp("visual", bad, 800)

    @pytest.mark.parametrize("bad", ["", None, 3])
    def test_modality_must_be_a_non_empty_name(self, bad):
        with pytest.raises(InvalidRamp):
            Transitions().ramp(bad, 0.5, 800)

    def test_negative_start_is_refused(self):
        with pytest.raises(InvalidRamp):
            Transitions().ramp("visual", 0.5, 800, start_at_ms=-1)

    def test_pending_is_sorted_by_start(self):
        transitions = Transitions()
        transitions.ramp("visual", 0.5, 800, start_at_ms=4000)
        transitions.ramp("audio", 0.5, 800, start_at_ms=0)
        assert [ramp.start_at_ms for ramp in transitions.pending()] == [0, 4000]

    def test_clear_drops_every_ramp_and_resets_the_cursor(self):
        transitions = Transitions()
        transitions.ramp("visual", 0.5, 800)
        transitions.clear()
        assert transitions.pending() == ()
        fresh = transitions.ramp("audio", 0.5, 800)
        assert fresh.start_at_ms == 0

    def test_ramp_is_immutable(self):
        """A scheduled ramp is a record, not a mutable handle."""
        ramp = Transitions().ramp("visual", 0.5, 800)
        with pytest.raises(Exception):
            ramp.duration_ms = 10  # type: ignore[misc]
        assert isinstance(ramp, Ramp)
