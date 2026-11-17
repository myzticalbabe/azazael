"""
Tests for M1 — Cognitive Profile Vector (Sarah Profile B1)

Per SARAH_INTERFACE_2026-11-16.md frozen contract:
- AXES length = 8, order = contract order
- Validation: range [0,1], type float|None
- canonical_axis resolves pre-freeze aliases
- from_signals, from_dict, to_dict work
- explain() returns "not measured yet" for None
- Profile alias = SarahProfile
- Extended axes (wm_span, time_discrimination) in to_dict
"""

from __future__ import annotations

import pytest

from SARAH.profile import (
    SarahProfile,
    Profile,
    AXES,
    ALL_AXES,
    AXIS_MEANING,
    AXIS_ALIASES,
    canonical_axis,
    SOURCE_PRECEDENCE,
)


class TestAxesContract:
    """Test the frozen eight axes contract."""

    def test_axes_length_eight(self):
        """AXES tuple has exactly 8 items."""
        assert len(AXES) == 8

    def test_axes_order_contract(self):
        """AXES order matches B1 contract order."""
        expected = (
            "sensory_gain",
            "processing_speed",
            "attention_span",
            "interoception",
            "masking_load",
            "recovery_latency",
            "initiation_cost",
            "prediction_need",
        )
        assert AXES == expected

    def test_all_axes_includes_extended(self):
        """ALL_AXES = AXES + EXTENDED_AXES."""
        assert ALL_AXES == AXES + ("wm_span", "time_discrimination")

    def test_axis_meaning_complete(self):
        """Every axis in ALL_AXES has a meaning entry."""
        for axis in ALL_AXES:
            assert axis in AXIS_MEANING
            low, high = AXIS_MEANING[axis]
            assert isinstance(low, str)
            assert isinstance(high, str)
            assert len(low) > 0
            assert len(high) > 0


class TestValidation:
    """Test __post_init__ validation."""

    def test_valid_profile(self):
        """Valid profile instantiation."""
        p = SarahProfile()
        assert all(getattr(p, axis) is None for axis in ALL_AXES)

    def test_valid_values(self):
        """Values in [0, 1] accepted."""
        p = SarahProfile(sensory_gain=0.5, processing_speed=1.0, attention_span=0.0)
        assert p.sensory_gain == 0.5
        assert p.processing_speed == 1.0
        assert p.attention_span == 0.0

    def test_none_accepted(self):
        """None values accepted (not measured)."""
        p = SarahProfile(sensory_gain=None)
        assert p.sensory_gain is None

    def test_out_of_range_rejected(self):
        """Values > 1.0 rejected."""
        with pytest.raises(ValueError, match="must be in \\[0, 1\\]"):
            SarahProfile(sensory_gain=1.5)

    def test_negative_rejected(self):
        """Values < 0.0 rejected."""
        with pytest.raises(ValueError, match="must be in \\[0, 1\\]"):
            SarahProfile(sensory_gain=-0.1)

    def test_wrong_type_rejected(self):
        """Non-numeric values rejected."""
        with pytest.raises(TypeError, match="must be float or None"):
            SarahProfile(sensory_gain="high")

    def test_all_axes_validated(self):
        """All axes validated, not just first."""
        for axis in AXES:
            with pytest.raises(ValueError):
                kwargs = {axis: 1.5}
                SarahProfile(**kwargs)


class TestCanonicalAxis:
    """Test canonical_axis alias resolution."""

    def test_canonical_returns_self(self):
        """Canonical names resolve to themselves."""
        for axis in ALL_AXES:
            assert canonical_axis(axis) == axis

    def test_alias_resolution(self):
        """Pre-freeze aliases resolve to contract names."""
        assert canonical_axis("sustained_attention") == "attention_span"
        assert canonical_axis("interoceptive_accuracy") == "interoception"
        assert canonical_axis("initiation_threshold") == "initiation_cost"

    def test_unknown_returns_none(self):
        """Unknown axis names return None."""
        assert canonical_axis("unknown_axis") is None
        assert canonical_axis("completely_fake") is None
        assert canonical_axis("") is None

    def test_alias_not_in_axes_returns_none(self):
        """Alias that doesn't map to an axis returns None."""
        # If an alias existed but mapped to a non-existent axis
        # (not the case currently, but defensive)
        pass


class TestConstruction:
    """Test SarahProfile construction methods."""

    def test_from_signals_basic(self):
        """from_signals creates profile with values."""
        signals = {"sensory_gain": 0.8, "attention_span": 0.6}
        p = SarahProfile.from_signals(signals, source="probe")
        assert p.sensory_gain == 0.8
        assert p.attention_span == 0.6
        assert p._sources["sensory_gain"] == "probe"
        assert p._sources["attention_span"] == "probe"

    def test_from_signals_ignores_unknown(self):
        """from_signals ignores unknown axis names."""
        signals = {"sensory_gain": 0.8, "fake_axis": 0.5}
        p = SarahProfile.from_signals(signals)
        assert p.sensory_gain == 0.8
        assert "fake_axis" not in p._sources

    def test_from_signals_none_skipped(self):
        """None values in signals are skipped."""
        signals = {"sensory_gain": None, "attention_span": 0.6}
        p = SarahProfile.from_signals(signals)
        assert p.sensory_gain is None
        assert p.attention_span == 0.6

    def test_from_signals_resolves_aliases(self):
        """from_signals resolves pre-freeze aliases."""
        signals = {"sustained_attention": 0.7}
        p = SarahProfile.from_signals(signals)
        assert p.attention_span == 0.7

    def test_from_dict_basic(self):
        """from_dict creates profile from dict."""
        data = {"sensory_gain": 0.9, "processing_speed": 0.3}
        p = SarahProfile.from_dict(data)
        assert p.sensory_gain == 0.9
        assert p.processing_speed == 0.3

    def test_from_dict_resolves_aliases(self):
        """from_dict resolves pre-freeze aliases."""
        data = {"sustained_attention": 0.7, "initiation_threshold": 0.4}
        p = SarahProfile.from_dict(data)
        assert p.attention_span == 0.7
        assert p.initiation_cost == 0.4

    def test_from_dict_ignores_unknown(self):
        """from_dict ignores unknown keys."""
        data = {"sensory_gain": 0.5, "unknown_key": 0.1}
        p = SarahProfile.from_dict(data)
        assert p.sensory_gain == 0.5
        assert not hasattr(p, "unknown_key")

    def test_to_dict_includes_all_axes(self):
        """to_dict includes frozen eight + extended."""
        p = SarahProfile(sensory_gain=0.5, wm_span=0.8)
        d = p.to_dict()
        assert set(d.keys()) == set(ALL_AXES)
        assert d["sensory_gain"] == 0.5
        assert d["wm_span"] == 0.8

    def test_to_dict_none_for_unset(self):
        """to_dict returns None for unset axes."""
        p = SarahProfile()
        d = p.to_dict()
        assert all(v is None for v in d.values())


class TestExplain:
    """Test explain() output."""

    def test_explain_known_axis(self):
        """explain for set axis returns value + meaning + source."""
        p = SarahProfile(sensory_gain=0.75)
        p._sources["sensory_gain"] = "probe"
        result = p.explain("sensory_gain")
        assert "0.75" in result
        assert "low→high" in result
        assert "probe" in result

    def test_explain_unset_axis(self):
        """explain for None axis says 'not measured yet'."""
        p = SarahProfile()
        result = p.explain("sensory_gain")
        assert "not measured yet" in result.lower()

    def test_explain_unknown_axis(self):
        """explain for unknown axis says 'Unknown axis'."""
        p = SarahProfile()
        result = p.explain("fake_axis")
        assert "unknown axis" in result.lower()

    def test_explain_resolves_alias(self):
        """explain resolves pre-freeze aliases."""
        p = SarahProfile(attention_span=0.5)
        result = p.explain("sustained_attention")
        assert "0.5" in result
        assert "attention_span" in result or "not measured" in result.lower()


class TestProfileAlias:
    """Test Profile type alias."""

    def test_profile_is_sarahprofile(self):
        """Profile is SarahProfile."""
        assert Profile is SarahProfile

    def test_profile_instantiation(self):
        """Profile() works."""
        p = Profile(sensory_gain=0.5)
        assert isinstance(p, SarahProfile)


class TestAxesMethods:
    """Test axes() and all_axes() methods."""

    def test_axes_returns_frozen_eight(self):
        """axes() returns the frozen eight in contract order."""
        p = SarahProfile()
        assert p.axes() == list(AXES)

    def test_all_axes_returns_all(self):
        """all_axes() returns frozen + extended."""
        p = SarahProfile()
        assert p.all_axes() == list(ALL_AXES)


class TestSourcePrecedence:
    """Test SOURCE_PRECEDENCE constant."""

    def test_precedence_order(self):
        """Precedence is user > probe > telemetry > clinical_seed."""
        assert SOURCE_PRECEDENCE == ("user", "probe", "telemetry", "clinical_seed")


class TestEquality:
    """Test __eq__ implementation."""

    def test_equal_profiles(self):
        """Profiles with same values are equal."""
        p1 = SarahProfile(sensory_gain=0.5, attention_span=0.6)
        p2 = SarahProfile(sensory_gain=0.5, attention_span=0.6)
        assert p1 == p2

    def test_unequal_profiles(self):
        """Profiles with different values are not equal."""
        p1 = SarahProfile(sensory_gain=0.5)
        p2 = SarahProfile(sensory_gain=0.6)
        assert p1 != p2

    def test_equal_to_other_type(self):
        """Comparison to non-SarahProfile returns NotImplemented."""
        p = SarahProfile()
        assert p.__eq__("not a profile") is NotImplemented


class TestProfileStore:
    """Test ProfileStore stub methods."""

    def test_save_returns_string(self):
        """save returns version string."""
        p = SarahProfile()
        from SARAH.profile import ProfileStore
        result = ProfileStore.save(p, "v1")
        assert isinstance(result, str)
        assert "v1" in result

    def test_load_returns_none(self):
        """load returns None (stub)."""
        from SARAH.profile import ProfileStore
        result = ProfileStore.load()
        assert result is None

    def test_delete_returns_bool(self):
        """delete returns bool."""
        from SARAH.profile import ProfileStore
        result = ProfileStore.delete()
        assert isinstance(result, bool)


class TestPreviewExit:
    """Test Preview/ExitPort dataclasses."""

    def test_preview_creation(self):
        """Preview dataclass works."""
        from SARAH.profile import Preview
        prev = Preview(what="test", duration_s=30.0, how_to_leave="press q")
        assert prev.what == "test"
        assert prev.duration_s == 30.0

    def test_exit_ticket_creation(self):
        """ExitTicket dataclass works."""
        from SARAH.profile import ExitTicket
        ticket = ExitTicket(at_s=123.0, reason="done", resume_token="token")
        assert ticket.at_s == 123.0
        assert ticket.reason == "done"

    def test_exit_port_leave(self):
        """ExitPort.leave returns ExitTicket."""
        from SARAH.profile import ExitPort, ExitTicket
        ticket = ExitPort.leave("test")
        assert isinstance(ticket, ExitTicket)
        assert ticket.reason == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])