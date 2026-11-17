"""
Tests for M1 — Cognitive Profile Vector (Sarah Build Instructions B1).

These assert the frozen contract rather than the first build's spelling: the
eight axis names and their order, the alias resolution that keeps a caller
written before the freeze working, and the rule that an unmeasured axis is
None with an explicit "not measured yet" — never a silent 0.5.
"""

import pytest

from SARAH.profile import (
    ALL_AXES,
    AXES,
    AXIS_ALIASES,
    AXIS_MEANING,
    EXTENDED_AXES,
    Profile,
    SarahProfile,
    canonical_axis,
)


CONTRACT_AXES = (
    "sensory_gain",
    "processing_speed",
    "attention_span",
    "interoception",
    "masking_load",
    "recovery_latency",
    "initiation_cost",
    "prediction_need",
)


class TestAxisVocabulary:
    """The vocabulary is the contract, and it is frozen."""

    def test_axes_match_contract_exactly(self):
        """AXES is the contract tuple, in the contract's order."""
        assert AXES == CONTRACT_AXES

    def test_eight_frozen_axes(self):
        """Lanes 2 and 3 may rely on exactly eight frozen axes."""
        assert len(AXES) == 8

    def test_all_axes_is_frozen_plus_declared_extras(self):
        """The two extras are declared, not hidden inside AXES."""
        assert ALL_AXES == AXES + EXTENDED_AXES
        assert set(EXTENDED_AXES) == {"wm_span", "time_discrimination"}

    def test_every_axis_has_a_low_and_high_meaning(self):
        """A float with no direction cannot be rendered or explained."""
        assert set(AXIS_MEANING) == set(ALL_AXES)
        for axis, (low, high) in AXIS_MEANING.items():
            assert low and high, f"{axis} has an empty meaning"
            assert low != high, f"{axis} has no direction"

    def test_aliases_are_pre_freeze_names_only(self):
        """Each alias points at a frozen axis and is not itself an axis."""
        assert set(AXIS_ALIASES) == {
            "sustained_attention",
            "interoceptive_accuracy",
            "initiation_threshold",
        }
        for old, new in AXIS_ALIASES.items():
            assert new in AXES, f"{old} -> {new} is not a frozen axis"
            assert old not in ALL_AXES, f"{old} is both alias and axis"

    def test_canonical_axis_resolves_alias_and_rejects_stranger(self):
        """Resolution is total: an alias resolves, a stranger returns None."""
        assert canonical_axis("sustained_attention") == "attention_span"
        assert canonical_axis("masking_load") == "masking_load"
        assert canonical_axis("not_an_axis") is None


class TestProfileConstruction:
    """Unknown is None; measured carries its source."""

    def test_profile_is_the_contract_name(self):
        """B1's smoke command imports Profile."""
        assert Profile is SarahProfile

    def test_empty_signals_measure_nothing(self):
        """An empty probe leaves every axis unknown, and says so."""
        profile = SarahProfile.from_signals({})
        assert all(value is None for value in profile.to_dict().values())
        assert profile.explain("sensory_gain") == "sensory_gain: not measured yet"

    def test_signal_is_stored_and_attributed(self):
        """A measured axis records the source that produced it."""
        profile = SarahProfile.from_signals({"sensory_gain": 0.8}, source="probe")
        assert profile.sensory_gain == 0.8
        assert "from probe" in profile.explain("sensory_gain")

    def test_alias_signal_writes_the_canonical_field(self):
        """A pre-freeze caller fills the contract field, not a dead one."""
        profile = SarahProfile.from_signals({"sustained_attention": 0.4})
        assert profile.attention_span == 0.4
        assert profile.explain("sustained_attention").startswith("attention_span=0.40")

    def test_unknown_signal_is_ignored_not_an_error(self):
        """A different vocabulary is a caller bug, not a profile crash."""
        profile = SarahProfile.from_signals({"not_an_axis": 0.5})
        assert profile.to_dict()["sensory_gain"] is None

    def test_out_of_range_signal_is_rejected(self):
        """A value outside [0, 1] is a defect and must not reach a profile."""
        with pytest.raises(ValueError):
            SarahProfile.from_signals({"sensory_gain": 1.5})

    def test_non_numeric_value_is_rejected(self):
        """A non-float is a TypeError, not a coerced value."""
        with pytest.raises(TypeError):
            SarahProfile(interoception="high")

    def test_axes_returns_the_frozen_eight_only(self):
        """axes() is the contract surface; all_axes() is what is stored."""
        profile = SarahProfile()
        assert profile.axes() == list(AXES)
        assert profile.all_axes() == list(ALL_AXES)


class TestDictRoundTrip:
    """Stored profiles and stale tables resolve instead of vanishing."""

    def test_from_dict_resolves_alias(self):
        profile = SarahProfile.from_dict({"interoceptive_accuracy": 0.6})
        assert profile.interoception == 0.6

    def test_from_dict_ignores_unknown_keys(self):
        profile = SarahProfile.from_dict({"sensory_gain": 0.2, "nonsense": 1.0})
        assert profile.sensory_gain == 0.2
        assert "nonsense" not in profile.to_dict()

    def test_to_dict_carries_frozen_eight_first_then_extras(self):
        keys = list(SarahProfile().to_dict())
        assert keys[:8] == list(AXES)
        assert keys[8:] == list(EXTENDED_AXES)
        assert len(keys) == 10

    def test_equality_is_by_value(self):
        assert SarahProfile(sensory_gain=0.5) == SarahProfile(sensory_gain=0.5)
        assert SarahProfile(sensory_gain=0.5) != SarahProfile(sensory_gain=0.6)


class TestAxisIndependence:
    """One axis moves without dragging another."""

    def test_prediction_need_moves_alone(self):
        base = SarahProfile.from_signals({axis: 0.5 for axis in AXES})
        nudged = SarahProfile.from_dict({**base.to_dict(), "prediction_need": 0.9})
        assert nudged.prediction_need == 0.9
        for axis in AXES:
            if axis != "prediction_need":
                assert getattr(nudged, axis) == getattr(base, axis)
