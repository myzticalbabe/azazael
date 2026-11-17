"""
Tests for M6 — Predictability Packet, and M7 — Exit-Anywhere (B1).

The negative case B1 mandates lives here: a profile with `prediction_need` high
produces *more* announcement beats and *fewer* simultaneous changes — never more
stimulus. `simultaneous_changes` saturates at the §5 cap of one, so the evidence
that the axis did anything is in `announce_beats` up and
`changes_per_announcement` / `stagger_s` spread out, with `len(steps)` unchanged.

Run:
    C:/Azazael/.venvs/py316t/Scripts/python.exe -m pytest tests/test_sarah_predict.py -q
"""

import pytest

from SARAH import exit as exit_mod
from SARAH.profile import ExitTicket, Profile
from SARAH.predict import (
    ANNOUNCEMENT_BEAT_S,
    MODALITIES,
    RAMP_S,
    PredictabilityPacket,
    announcement_beats,
    changes_per_announcement,
    packet,
    stagger_s,
)


def profile_with_need(need):
    """A profile whose only measured axis is prediction_need."""
    return Profile.from_signals({"prediction_need": need}, source="probe")


LOW = profile_with_need(0.1)
HIGH = profile_with_need(0.9)


class TestPacketShape:
    """The contract fields exist and mean what B1 says."""

    def test_packet_returns_the_contract_type(self):
        pkt = packet(LOW, 3)
        assert isinstance(pkt, PredictabilityPacket)

    def test_contract_fields_are_present(self):
        pkt = packet(LOW, 3)
        for field in ("what", "when", "how_long", "what_next"):
            assert getattr(pkt, field) not in (None, ""), f"{field} is empty"

    def test_can_exit_is_always_true(self):
        """Rule 5: the exit is never gated by session state or by the profile."""
        for need in (None, 0.0, 0.5, 1.0):
            assert packet(profile_with_need(need), 5).can_exit is True
        # Even a profile that is maximally loaded on every axis keeps the exit.
        loaded = Profile.from_signals({axis: 1.0 for axis in Profile().axes()})
        assert packet(loaded, 5).can_exit is True

    def test_steps_are_next_n_steps_not_more(self):
        """The packet announces the plan; it never adds a step to it."""
        for n in (1, 2, 5, 12):
            pkt = packet(HIGH, n)
            assert len(pkt.steps) == n
            assert [s.index for s in pkt.steps] == list(range(n))

    def test_one_modality_per_step(self):
        """§5: at most one channel changes at a time, so each step names one."""
        pkt = packet(LOW, 9)
        assert all(s.modality in MODALITIES for s in pkt.steps)

    def test_steps_are_at_least_one_ramp_apart(self):
        """§5's 400 ms floor holds at every prediction_need, including 0.

        Judged in integer milliseconds on purpose: two float seconds 400 ms
        apart subtract to 0.3999999999999999, which would fail a packet that is
        exactly at the cap. The floor is a millisecond reading.
        """
        floor_ms = int(round(RAMP_S * 1000))
        for need in (0.0, 0.5, 1.0):
            pkt = packet(profile_with_need(need), 6)
            gaps = [b.at_ms - a.at_ms for a, b in zip(pkt.steps, pkt.steps[1:])]
            assert all(gap >= floor_ms for gap in gaps), (need, gaps)

    def test_first_step_is_announced_before_it_happens(self):
        pkt = packet(HIGH, 2)
        assert pkt.when == pkt.announce_beats * ANNOUNCEMENT_BEAT_S
        assert pkt.steps[0].at_s >= pkt.when

    def test_to_dict_carries_every_field(self):
        data = packet(LOW, 2).to_dict()
        assert data["can_exit"] is True
        assert len(data["steps"]) == 2
        assert data["steps"][0]["modality"] in MODALITIES


class TestNegativeCase:
    """High prediction_need buys notice, never stimulus."""

    def test_high_need_gets_more_announcement_beats(self):
        assert packet(HIGH, 4).announce_beats > packet(LOW, 4).announce_beats

    def test_high_need_bundles_fewer_changes_per_announcement(self):
        assert (
            packet(HIGH, 4).changes_per_announcement
            < packet(LOW, 4).changes_per_announcement
        )

    def test_high_need_spreads_the_steps_further(self):
        assert packet(HIGH, 4).stagger_s > packet(LOW, 4).stagger_s
        assert packet(HIGH, 4).when > packet(LOW, 4).when

    def test_high_need_does_not_add_stimulus(self):
        """The total number of announced changes is the caller's, not the axis's."""
        low, high = packet(LOW, 7), packet(HIGH, 7)
        assert len(low.steps) == len(high.steps) == 7
        assert [s.modality for s in low.steps] == [s.modality for s in high.steps]
        assert [s.how_long_s for s in low.steps] == [s.how_long_s for s in high.steps]

    def test_simultaneous_changes_saturates_at_the_cap(self):
        """§5 certifies one modality changing at a time. The axis cannot buy two."""
        for need in (0.0, 0.1, 0.5, 0.9, 1.0):
            assert packet(profile_with_need(need), 5).simultaneous_changes == 1
        assert packet(Profile(), 5).simultaneous_changes == 1


class TestMonotonicity:
    """Sweeping the axis moves notice one way only."""

    def test_beats_are_non_decreasing(self):
        values = [announcement_beats(i / 20) for i in range(21)]
        assert values == sorted(values)
        assert values[0] == 1 and values[-1] == 4

    def test_changes_per_announcement_is_non_increasing(self):
        values = [changes_per_announcement(i / 20) for i in range(21)]
        assert values == sorted(values, reverse=True)
        assert values[0] == 3 and values[-1] == 1

    def test_stagger_is_non_decreasing(self):
        values = [stagger_s(i / 20) for i in range(21)]
        assert values == sorted(values)


class TestUnknownAxis:
    """An unmeasured axis is reported, not silently treated as a measurement."""

    def test_none_need_is_reported_as_none(self):
        pkt = packet(Profile(), 3)
        assert pkt.prediction_need is None
        assert "not measured" in pkt.basis

    def test_measured_need_is_reported_with_its_value(self):
        pkt = packet(HIGH, 3)
        assert pkt.prediction_need == pytest.approx(0.9)
        assert "prediction_need=0.90" in pkt.basis


class TestArgumentValidation:
    """A caller bug is named, not coerced."""

    @pytest.mark.parametrize("bad", [0, -1])
    def test_non_positive_steps_raise(self, bad):
        with pytest.raises(ValueError):
            packet(LOW, bad)

    @pytest.mark.parametrize("bad", [1.5, "3", True, None])
    def test_non_integer_steps_raise(self, bad):
        with pytest.raises(TypeError):
            packet(LOW, bad)


class TestExitAnywhere:
    """M7: leaving is one action and is never scored."""

    def test_request_returns_a_ticket(self):
        ticket = exit_mod.request("overload")
        assert isinstance(ticket, ExitTicket)
        assert ticket.reason == "overload"
        assert ticket.at_s > 0

    def test_request_needs_no_reason(self):
        """Leaving without explaining is a first-class path."""
        assert exit_mod.request().reason is None

    def test_exit_is_reachable_in_one_action(self):
        assert exit_mod.reachable_in_one_action() is True

    def test_clean_log_passes(self):
        exit_mod.assert_unscored(
            [
                {"event": "exit_requested", "at_s": 12.0, "reason": None},
                {"event": "session_end", "duration_s": 12.0},
            ]
        )

    @pytest.mark.parametrize("field", ["score", "rating", "comment"])
    def test_scored_or_commented_exit_is_rejected(self, field):
        with pytest.raises(AssertionError):
            exit_mod.assert_unscored(
                [{"event": "exit_requested", "at_s": 12.0, field: 1}]
            )
