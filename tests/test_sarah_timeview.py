"""
Tests for M9 — Time Scaffolding (Lane 3)

Per design:
- Duration rendered as length, never as clock arithmetic
- TimeView.remaining(seconds) -> Ribbon (visual/physical representation)
- Timer exists only when requested (Timer.requested() false by default)
- Timer.pause() actually pauses
- No countdown unless requested (hard cap)
"""

from __future__ import annotations

import pytest
import time

from SARAH.affect.timeview import (
    TimeView,
    TimeRibbon,
    TimeUnit,
    RibbonStyle,
    remaining_ribbon,
    create_time_view,
)
from SARAH.profile import SarahProfile


class TestTimeRibbon:
    """Test TimeRibbon rendering as length."""

    def test_ribbon_creation_valid(self):
        """Valid ribbon creation."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=60)
        assert ribbon.total_seconds == 300
        assert ribbon.elapsed_seconds == 60
        assert ribbon.remaining_seconds == 240
        assert ribbon.progress == 0.2

    def test_ribbon_rejects_invalid_total(self):
        """Zero or negative total_seconds rejected."""
        with pytest.raises(ValueError, match="total_seconds must be positive"):
            TimeRibbon(total_seconds=0, elapsed_seconds=0)
        with pytest.raises(ValueError, match="total_seconds must be positive"):
            TimeRibbon(total_seconds=-1, elapsed_seconds=0)

    def test_ribbon_rejects_negative_elapsed(self):
        """Negative elapsed_seconds rejected."""
        with pytest.raises(ValueError, match="elapsed_seconds cannot be negative"):
            TimeRibbon(total_seconds=300, elapsed_seconds=-10)

    def test_render_bar_style(self):
        """BAR style renders as length."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=150, style=RibbonStyle.BAR)
        rendered = ribbon.render(width=20)
        assert "█" in rendered
        assert "░" in rendered
        assert "remaining" in rendered

    def test_render_segments_style(self):
        """SEGMENTS style renders as segments."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=150, style=RibbonStyle.SEGMENTS)
        rendered = ribbon.render(width=20)
        assert "●" in rendered or "○" in rendered

    def test_render_ribbon_style(self):
        """RIBBON style renders as ribbon."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=150, style=RibbonStyle.RIBBON)
        rendered = ribbon.render(width=20)
        assert "▬" in rendered or "·" in rendered

    def test_render_proportional_style(self):
        """PROPORTIONAL style renders ratio."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=100, style=RibbonStyle.PROPORTIONAL)
        rendered = ribbon.render(width=20)
        assert ":" in rendered or "complete" in rendered

    def test_render_complete(self):
        """Complete ribbon shows full."""
        ribbon = TimeRibbon(total_seconds=300, elapsed_seconds=300, style=RibbonStyle.BAR)
        rendered = ribbon.render(width=20)
        assert "█" in rendered
        assert "remaining" in rendered

    def test_different_units(self):
        """Different time units format correctly."""
        ribbon = TimeRibbon(total_seconds=3600, elapsed_seconds=1800, unit=TimeUnit.HOURS)
        rendered = ribbon.render(width=10)
        assert "h" in rendered

        ribbon = TimeRibbon(total_seconds=60, elapsed_seconds=30, unit=TimeUnit.SECONDS)
        rendered = ribbon.render(width=10)
        assert "s" in rendered


class TestTimeView:
    """Test TimeView scaffolding."""

    def setup_method(self):
        self.profile = SarahProfile()
        self.timeview = TimeView(self.profile)

    def test_requested_false_by_default(self):
        """Timer exists only when requested."""
        assert not self.timeview.requested()

    def test_start_creates_ribbon(self):
        """Start creates active ribbon."""
        ribbon = self.timeview.start(300)
        assert self.timeview.requested()
        assert ribbon.total_seconds == 300
        assert ribbon.elapsed_seconds == 0

    def test_pause_actually_pauses(self):
        """pause() actually pauses the timer."""
        self.timeview.start(300)
        ribbon_before = self.timeview.pause()
        assert ribbon_before is not None

        # Wait a bit
        time.sleep(0.01)

        # Tick should not advance while paused
        ribbon_after = self.timeview.tick()
        assert ribbon_after is not None
        # Progress should be same (within floating point)
        assert abs(ribbon_after.progress - ribbon_before.progress) < 0.001

    def test_resume_after_pause(self):
        """resume() continues from pause."""
        self.timeview.start(300)
        self.timeview.pause()
        time.sleep(0.01)
        ribbon = self.timeview.resume()
        assert ribbon is not None

    def test_is_complete(self):
        """Timer completes when elapsed >= total."""
        self.timeview.start(1)  # 1 second
        time.sleep(1.1)
        ribbon = self.timeview.tick(1.5)
        assert self.timeview.is_complete()

    def test_get_ribbon_for_axis(self):
        """Get ribbon for SarahProfile axis."""
        for axis in ["prediction_need", "time_discrimination", "processing_speed",
                     "attention_span", "initiation_cost"]:
            rendered = self.timeview.get_ribbon_for_profile_axis(axis, width=10)
            assert rendered is not None
            assert len(rendered) > 0

    def test_unknown_axis_returns_none(self):
        """Unknown axis returns None."""
        result = self.timeview.get_ribbon_for_profile_axis("unknown_axis")
        assert result is None


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_remaining_ribbon(self):
        """One-shot remaining ribbon."""
        result = remaining_ribbon(300, 150, RibbonStyle.BAR, width=10)
        assert "█" in result
        assert "░" in result

    def test_create_time_view(self):
        """Factory function."""
        tv = create_time_view()
        assert isinstance(tv, TimeView)
        assert not tv.requested()


class TestHardCaps:
    """Test hard caps from design §5."""

    def setup_method(self):
        self.timeview = TimeView()

    def test_no_countdown_unless_requested(self):
        """Timer only exists when explicitly started."""
        assert not self.timeview.requested()
        self.timeview.start(60)
        assert self.timeview.requested()

    def test_duration_as_length_not_clock(self):
        """Render shows length (bar/segments), not HH:MM:SS."""
        self.timeview.start(3661)  # 1h 1m 1s
        rendered = self.timeview.render_remaining(width=20)
        # Should NOT contain clock format
        assert ":" not in rendered or rendered.count(":") == 0
        # Should contain length representation
        assert any(c in rendered for c in ["█", "░", "●", "○", "▬", "·"])

    def test_self_pacing_user_controls(self):
        """User controls timer via start/pause/resume."""
        self.timeview.start(300)
        self.timeview.pause()
        # Timer should not advance during pause
        time.sleep(0.01)
        ribbon = self.timeview.tick()
        assert ribbon is not None
        self.timeview.resume()
        # Now it can advance again


if __name__ == "__main__":
    pytest.main([__file__, "-v"])