"""
Tests for M12 — Masking-Load Meter and Burnout Guard (Lane 3)

Per design:
- LoadMeter.should_stop(session) -> bool driven by recovery_latency
- Post-session offer is low-demand "people-adjacent" mode
- Hard cap: load threshold from recovery_latency axis
- A module that raises load score while raising completion has made the task compulsory
"""

from __future__ import annotations

import pytest

from SARAH.affect.load import (
    LoadMeter,
    LoadEvent,
    SessionLoad,
    LoadDomain,
    create_load_meter,
    quick_should_stop,
)
from SARAH.profile import SarahProfile


class TestLoadEvent:
    """Test LoadEvent validation."""

    def test_valid_event(self):
        """Valid load event."""
        event = LoadEvent(
            domain=LoadDomain.SOCIAL,
            intensity=0.5,
            duration_seconds=300,
            description="meeting",
        )
        assert event.domain == LoadDomain.SOCIAL
        assert event.intensity == 0.5
        assert event.duration_seconds == 300

    def test_intensity_validation(self):
        """Intensity must be in [0, 1]."""
        with pytest.raises(ValueError, match="intensity must be in"):
            LoadEvent(domain=LoadDomain.SOCIAL, intensity=-0.1, duration_seconds=100)
        with pytest.raises(ValueError, match="intensity must be in"):
            LoadEvent(domain=LoadDomain.SOCIAL, intensity=1.1, duration_seconds=100)

    def test_duration_validation(self):
        """Duration cannot be negative."""
        with pytest.raises(ValueError, match="duration_seconds cannot be negative"):
            LoadEvent(domain=LoadDomain.SOCIAL, intensity=0.5, duration_seconds=-10)


class TestSessionLoad:
    """Test SessionLoad accumulation."""

    def test_add_event(self):
        """Add events to session."""
        session = SessionLoad()
        event = LoadEvent(LoadDomain.SOCIAL, 0.5, 300)
        session.add_event(event)
        assert len(session.events) == 1

    def test_total_load_calculation(self):
        """Total load = sum(intensity * duration * domain_weight)."""
        session = SessionLoad()
        session.add_event(LoadEvent(LoadDomain.SOCIAL, 1.0, 3600))  # weight 1.2
        session.add_event(LoadEvent(LoadDomain.SENSORY, 1.0, 3600))  # weight 1.0
        session.add_event(LoadEvent(LoadDomain.EMOTIONAL, 1.0, 3600))  # weight 1.3

        total = session.total_load()
        # 3600*1.2 + 3600*1.0 + 3600*1.3 = 3600 * 3.5 = 12600
        assert total == 12600.0

    def test_load_by_domain(self):
        """Load broken down by domain."""
        session = SessionLoad()
        session.add_event(LoadEvent(LoadDomain.SOCIAL, 0.5, 1000))
        session.add_event(LoadEvent(LoadDomain.SOCIAL, 0.5, 1000))

        by_domain = session.load_by_domain()
        assert by_domain[LoadDomain.SOCIAL] == 1200.0  # 1000 * 0.5 * 1.2 * 2
        assert by_domain[LoadDomain.SENSORY] == 0.0

    def test_end_session(self):
        """End session records timestamp."""
        session = SessionLoad()
        assert session.ended_at is None
        session.end_session()
        assert session.ended_at is not None


class TestLoadMeterThreshold:
    """Test threshold computation from recovery_latency."""

    def test_base_threshold_at_mid_recovery(self):
        """recovery_latency=0.5 gives base threshold."""
        profile = SarahProfile(recovery_latency=0.5)
        meter = LoadMeter(profile)
        assert meter._compute_threshold() == 3600.0

    def test_high_threshold_fast_recovery(self):
        """recovery_latency=0.0 (fast) -> 2x threshold."""
        profile = SarahProfile(recovery_latency=0.0)
        meter = LoadMeter(profile)
        assert meter._compute_threshold() == 7200.0  # 2x base

    def test_low_threshold_slow_recovery(self):
        """recovery_latency=1.0 (slow) -> 0.5x threshold."""
        profile = SarahProfile(recovery_latency=1.0)
        meter = LoadMeter(profile)
        assert meter._compute_threshold() == 1800.0  # 0.5x base

    def test_conservative_when_not_measured(self):
        """None recovery_latency -> conservative 0.75x."""
        profile = SarahProfile(recovery_latency=None)
        meter = LoadMeter(profile)
        assert meter._compute_threshold() == 2700.0  # 0.75x base

    def test_linear_scaling(self):
        """Linear scaling between extremes."""
        # 0.0 -> 2.0, 0.5 -> 1.0, 1.0 -> 0.5
        for recovery, expected_mult in [
            (0.0, 2.0),
            (0.25, 1.5),
            (0.5, 1.0),
            (0.75, 0.75),
            (1.0, 0.5),
        ]:
            profile = SarahProfile(recovery_latency=recovery)
            meter = LoadMeter(profile)
            threshold = meter._compute_threshold()
            expected = 3600.0 * expected_mult
            assert abs(threshold - expected) < 0.01, f"recovery={recovery}: {threshold} != {expected}"


class TestLoadMeterShouldStop:
    """Test should_stop logic."""

    def test_no_session_returns_false(self):
        """No active session -> should_stop is False."""
        meter = LoadMeter()
        assert not meter.should_stop()

    def test_below_threshold_returns_false(self):
        """Load below threshold -> should_stop is False."""
        profile = SarahProfile(recovery_latency=0.5)  # threshold 3600
        meter = LoadMeter(profile)
        meter.start_session()
        # Add small load
        meter.record_event(LoadDomain.SOCIAL, 0.1, 60)  # 60 * 1.2 * 0.1 = 7.2
        assert not meter.should_stop()

    def test_at_threshold_returns_true(self):
        """Load at threshold -> should_stop is True."""
        profile = SarahProfile(recovery_latency=0.5)  # threshold 3600
        meter = LoadMeter(profile)
        meter.start_session()
        # Add load equal to threshold
        # SOCIAL weight 1.2: need 3600 / 1.2 = 3000 intensity-seconds
        meter.record_event(LoadDomain.SOCIAL, 1.0, 3000)
        assert meter.should_stop()

    def test_above_threshold_returns_true(self):
        """Load above threshold -> should_stop is True."""
        profile = SarahProfile(recovery_latency=0.5)
        meter = LoadMeter(profile)
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 1.0, 4000)  # > 3600
        assert meter.should_stop()

    def test_should_stop_uses_profile_axis(self):
        """Different profiles give different should_stop for same load."""
        # Fast recovery (high threshold)
        fast = SarahProfile(recovery_latency=0.0)  # threshold 7200
        meter_fast = LoadMeter(fast)
        meter_fast.start_session()
        meter_fast.record_event(LoadDomain.SOCIAL, 1.0, 5000)  # 6000 load
        assert not meter_fast.should_stop()

        # Slow recovery (low threshold)
        slow = SarahProfile(recovery_latency=1.0)  # threshold 1800
        meter_slow = LoadMeter(slow)
        meter_slow.start_session()
        meter_slow.record_event(LoadDomain.SOCIAL, 1.0, 5000)  # 6000 load
        assert meter_slow.should_stop()


class TestLoadMeterFractions:
    """Test load fraction and remaining load."""

    def test_load_fraction(self):
        """Load fraction = current / threshold."""
        profile = SarahProfile(recovery_latency=0.5)  # 3600
        meter = LoadMeter(profile)
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 1.0, 1800)  # 2160 load
        assert abs(meter.load_fraction() - 0.6) < 0.01

    def test_remaining_load(self):
        """Remaining = threshold - current."""
        profile = SarahProfile(recovery_latency=0.5)
        meter = LoadMeter(profile)
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 1.0, 1000)  # 1200 load
        remaining = meter.remaining_load()
        assert abs(remaining - 2400.0) < 0.01

    def test_remaining_load_zero_when_exceeded(self):
        """Remaining is 0 when load exceeds threshold."""
        profile = SarahProfile(recovery_latency=0.5)
        meter = LoadMeter(profile)
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 1.0, 5000)  # 6000 load
        assert meter.remaining_load() == 0.0


class TestLoadMeterPostSession:
    """Test post-session offer."""

    def test_end_session_returns_session(self):
        """end_session returns completed session."""
        meter = LoadMeter()
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 0.5, 100)
        session = meter.end_session()
        assert session is not None
        assert session.ended_at is not None

    def test_post_session_offer_structure(self):
        """Post-session offer has required fields."""
        meter = LoadMeter()
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 0.5, 100)
        offer = meter.post_session_offer()

        assert offer["mode"] == "people_adjacent"
        assert "description" in offer
        assert "load_at_end" in offer
        assert "threshold" in offer
        assert "recovery_latency" in offer
        assert "recommended_recovery_seconds" in offer

    def test_post_session_offer_people_adjacent(self):
        """Offer is low-demand people-adjacent mode."""
        meter = LoadMeter()
        meter.start_session()
        offer = meter.post_session_offer()
        assert "people_adjacent" in offer["mode"]
        assert "no demands" in offer["description"].lower()
        assert "no questions" in offer["description"].lower()


class TestLoadMeterExplain:
    """Test load explanation."""

    def test_explain_load_contains_status(self):
        """Explain includes load status."""
        profile = SarahProfile(recovery_latency=0.5)
        meter = LoadMeter(profile)
        meter.start_session()
        meter.record_event(LoadDomain.SOCIAL, 1.0, 3000)  # 3600 load = 100%

        explanation = meter.explain_load()
        assert "THRESHOLD BREACHED" in explanation or "APPROACHING" in explanation
        assert "Load:" in explanation
        assert "Recovery latency:" in explanation


class TestQuickShouldStop:
    """Test quick_should_stop convenience."""

    def test_quick_check(self):
        """One-shot should_stop."""
        profile = SarahProfile(recovery_latency=0.5)
        # Below threshold
        result = quick_should_stop(profile, [
            (LoadDomain.SOCIAL, 0.1, 60),
        ])
        assert not result

        # Above threshold
        result = quick_should_stop(profile, [
            (LoadDomain.SOCIAL, 1.0, 4000),
        ])
        assert result


class TestCreateLoadMeter:
    """Test factory function."""

    def test_factory(self):
        """create_load_meter returns LoadMeter."""
        meter = create_load_meter()
        assert isinstance(meter, LoadMeter)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])