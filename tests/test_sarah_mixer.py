"""
Tests for M3 — Sensory Gain Mixer (Sarah Build Instructions B2, lane 2).

The contract under test is one global control: `Master` scales every modality,
and there is no second path by which a feature escapes it. The negative cases
carry the weight:

* an undeclared modality is refused rather than defaulted, so a feature cannot
  ship with a gain nobody reviewed;
* a gain outside [0, 1] is refused rather than clamped, because a gain is
  authored, and silently clamping it hides an authoring bug;
* `mute_non_critical()` never mutes the critical set — a muted instruction the
  user needs in order to leave is not "less intensity".
"""

import pytest

from SARAH.sensory import (
    CRITICAL_MODALITIES,
    DEFAULT_MASTER,
    DEFAULT_TRIMS,
    MAX_GAIN,
    MIN_GAIN,
    InvalidGain,
    Mixer,
    UndeclaredModality,
)


class TestMasterScalesEverything:
    """One control, every modality — the contract's central claim."""

    def test_master_times_trim_is_the_only_read_path(self):
        """level() is master * trim for every declared modality."""
        mixer = Mixer(master=0.5)
        for modality in mixer.declared():
            assert mixer.level(modality) == pytest.approx(
                0.5 * DEFAULT_TRIMS[modality], abs=1e-6
            )

    def test_master_scales_all_modalities_together(self):
        """Halving the master halves every declared modality's effective gain."""
        mixer = Mixer(master=0.8)
        before = mixer.levels()
        mixer.set_master(0.4)
        after = mixer.levels()
        assert set(after) == set(before)
        for modality in before:
            assert after[modality] == pytest.approx(before[modality] / 2, abs=1e-6)

    def test_master_zero_silences_every_modality(self):
        """A master of 0 reaches every modality, critical ones included."""
        mixer = Mixer(master=0.0)
        assert set(mixer.levels().values()) == {0.0}

    def test_shipped_default_is_the_calm_one(self):
        """The default master is not full intensity."""
        assert 0.0 < DEFAULT_MASTER < 1.0
        assert Mixer().master == DEFAULT_MASTER

    def test_two_mixers_do_not_share_trim_state(self):
        """`trims` is per-instance, so one feature cannot re-trim another's."""
        first = Mixer()
        second = Mixer()
        first.set_trim("audio", 0.1)
        assert second.trims["audio"] == DEFAULT_TRIMS["audio"]


class TestDeclarationRule:
    """A feature declares its gain before it can be driven."""

    def test_undeclared_modality_is_refused_on_read(self):
        """Reading an undeclared modality raises — it is not defaulted."""
        with pytest.raises(UndeclaredModality) as excinfo:
            Mixer().level("smell")
        assert "smell" in str(excinfo.value)
        assert "declare" in str(excinfo.value)

    def test_undeclared_modality_is_refused_on_write(self):
        """A trim cannot be set on a modality nobody declared."""
        with pytest.raises(UndeclaredModality):
            Mixer().set_trim("smell", 0.5)

    def test_undeclared_modality_error_is_not_quoted(self):
        """KeyError's repr wrapper is suppressed so the message reads as advice.

        The modality itself is repr-quoted inside the sentence; what must not
        appear is the second layer KeyError would add (`'"..."'`), which turns
        the message into a quoted string a caller cannot read.
        """
        with pytest.raises(UndeclaredModality) as excinfo:
            Mixer().level("smell")
        message = str(excinfo.value)
        assert message.startswith("'smell' has no declared default")
        assert not message.startswith("'\"")

    def test_declare_registers_a_new_modality(self):
        """After declaring, the modality can be driven like any other."""
        mixer = Mixer(master=0.5)
        mixer.declare("smell", 0.4)
        assert mixer.is_declared("smell")
        assert "smell" in mixer.declared()
        assert mixer.level("smell") == pytest.approx(0.2, abs=1e-6)

    def test_declared_list_is_stable_and_sorted(self):
        """`declared()` is the declaration register, in a reproducible order."""
        mixer = Mixer()
        mixer.declare("zzz", 0.1)
        mixer.declare("aaa", 0.1)
        assert mixer.declared() == tuple(sorted(mixer.trims))

    def test_muted_state_must_reference_a_declared_modality(self):
        """A restored mix cannot carry a mute for a modality it does not declare."""
        with pytest.raises(UndeclaredModality):
            Mixer.from_dict({"master": 0.5, "trims": {"audio": 0.5}, "muted": ["smell"]})


class TestGainValidation:
    """An authored gain outside [0, 1] is refused, not clamped."""

    @pytest.mark.parametrize("bad", [-0.01, 1.01, 2, -1])
    def test_out_of_range_master_is_refused(self, bad):
        with pytest.raises(InvalidGain):
            Mixer(master=bad)

    @pytest.mark.parametrize("bad", [-0.1, 1.5])
    def test_out_of_range_trim_is_refused(self, bad):
        with pytest.raises(InvalidGain):
            Mixer(trims={"audio": bad})

    def test_out_of_range_set_master_is_refused(self):
        mixer = Mixer()
        with pytest.raises(InvalidGain):
            mixer.set_master(1.5)
        assert mixer.master == DEFAULT_MASTER

    @pytest.mark.parametrize("bad", ["0.5", None, True, False])
    def test_non_numeric_gain_is_refused(self, bad):
        """A bool is an int in Python and must still be refused as a gain."""
        with pytest.raises(InvalidGain):
            Mixer(master=bad)

    def test_bounds_are_inclusive(self):
        """0.0 and 1.0 are legal gains; the bounds are the contract's."""
        assert Mixer(master=MIN_GAIN).master == 0.0
        assert Mixer(master=MAX_GAIN).master == 1.0
        assert MIN_GAIN == 0.0 and MAX_GAIN == 1.0


class TestMuteNonCritical:
    """XAUR REQ 3b — mute everything except what the user needs to leave."""

    def test_critical_set_survives_the_mute(self):
        mixer = Mixer(master=0.5)
        levels = mixer.mute_non_critical()
        for modality in CRITICAL_MODALITIES:
            assert levels[modality] > 0.0
            assert mixer.level(modality) > 0.0

    def test_non_critical_modalities_go_to_zero(self):
        mixer = Mixer(master=0.5)
        mixer.mute_non_critical()
        for modality in mixer.declared():
            if modality not in CRITICAL_MODALITIES:
                assert mixer.level(modality) == 0.0

    def test_text_is_a_critical_modality(self):
        """Legibility is the floor this rule exists to protect."""
        assert "text" in CRITICAL_MODALITIES

    def test_mute_is_reversible(self):
        mixer = Mixer(master=0.5)
        before = mixer.levels()
        mixer.mute_non_critical()
        restored = mixer.unmute()
        assert restored == before
        assert mixer.muted() == ()

    def test_setting_a_trim_unmutes_that_modality(self):
        """A write the caller made must be observable, not held at zero."""
        mixer = Mixer(master=0.5)
        mixer.mute_non_critical()
        assert mixer.level("audio") == 0.0
        mixer.set_trim("audio", 0.4)
        assert mixer.level("audio") == pytest.approx(0.2, abs=1e-6)
        assert "audio" not in mixer.muted()

    def test_mute_leaves_the_configured_trim_intact(self):
        """Muting is a display state; it does not overwrite the authored trim."""
        mixer = Mixer(master=0.5)
        mixer.mute_non_critical()
        assert mixer.trims["audio"] == DEFAULT_TRIMS["audio"]


class TestSerialisation:
    """A mix round-trips, and a corrupt one is refused."""

    def test_round_trip_preserves_master_trims_and_mutes(self):
        mixer = Mixer(master=0.3)
        mixer.declare("smell", 0.2)
        mixer.mute_non_critical()
        restored = Mixer.from_dict(mixer.to_dict())
        assert restored.to_dict() == mixer.to_dict()
        assert restored.level("audio") == 0.0
        assert restored.level("text") == mixer.level("text")

    def test_to_dict_is_json_shaped(self):
        """Every value is a plain dict/list/float — no dataclass objects."""
        data = Mixer().to_dict()
        assert set(data) == {"master", "trims", "muted"}
        assert isinstance(data["trims"], dict)
        assert isinstance(data["muted"], list)

    def test_non_mapping_trims_is_refused(self):
        with pytest.raises(InvalidGain):
            Mixer.from_dict({"master": 0.5, "trims": ["audio"]})

    def test_restored_out_of_range_gain_is_refused(self):
        """A persisted mix cannot reintroduce a gain the constructor forbids."""
        with pytest.raises(InvalidGain):
            Mixer.from_dict({"master": 3.0, "trims": {"audio": 0.5}})
