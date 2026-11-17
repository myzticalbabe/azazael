"""Tests for WORKER_AUTOMATION module."""

from __future__ import annotations

import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from WORKER_AUTOMATION import (
    WorkerAutomation,
    HealthMonitor,
    HeartbeatSender,
    DependencyDispatcher,
    TaskNode,
    WorkStealer,
    LessonBus,
    LocalLLMRouter,
    AutoCodeReview,
    TestAggregator,
    MetricsCollector,
    LANE_CONFIGS,
)


class TestHealthMonitor:
    """Test HealthMonitor."""

    def test_health_monitor_init(self):
        """HealthMonitor initializes correctly."""
        monitor = HealthMonitor()
        assert monitor.missing_threshold.total_seconds() == 60

    def test_health_check(self):
        """Health check runs without error."""
        monitor = HealthMonitor()
        monitor._check_health()  # Should not raise


class TestHeartbeatSender:
    """Test HeartbeatSender."""

    def test_heartbeat_sender_init(self):
        """HeartbeatSender initializes correctly."""
        sender = HeartbeatSender("kilo")
        assert sender.lane == "kilo"
        assert sender.interval == 30


class TestDependencyDispatcher:
    """Test DependencyDispatcher."""

    def setup_method(self):
        self.dispatcher = DependencyDispatcher()

    def test_register_and_get_ready(self):
        """Register tasks and get ready ones."""
        self.dispatcher.register_task(TaskNode("T1", "kilo", "a", "d", []))
        self.dispatcher.register_task(TaskNode("T2", "kilo", "a", "d", ["T1"]))

        ready = self.dispatcher.get_ready_tasks("kilo")
        assert len(ready) == 1
        assert ready[0].task_id == "T1"

    def test_dependency_resolution(self):
        """Dependencies are resolved correctly."""
        self.dispatcher.register_task(TaskNode("T1", "kilo", "a", "d", []))
        self.dispatcher.register_task(TaskNode("T2", "kilo", "a", "d", ["T1"]))

        self.dispatcher.mark_done("T1")
        ready = self.dispatcher.get_ready_tasks("kilo")
        assert len(ready) == 1
        assert ready[0].task_id == "T2"


class TestWorkStealer:
    """Test WorkStealer."""

    def test_steal_work(self):
        """Steal work runs without error."""
        stealer = WorkStealer()
        stolen = stealer.steal_work("kilo", max_items=1)
        assert isinstance(stolen, list)


class TestLessonBus:
    """Test LessonBus."""

    def setup_method(self):
        self.bus = LessonBus()

    def test_publish_and_subscribe(self):
        """Publish and subscribe to lessons."""
        self.bus.publish_lesson("kilo", {"title": "test", "content": "lesson"})
        lessons = self.bus.subscribe("freebuff", since_id=0)
        assert isinstance(lessons, list)


class TestLocalLLMRouter:
    """Test LocalLLMRouter."""

    def test_route_coding_task(self):
        """Route coding tasks to swarm."""
        router = LocalLLMRouter()
        result = router.route_coding_task(["test task"], workers=2)
        assert "answered" in result
        assert "tally" in result


class TestAutoCodeReview:
    """Test AutoCodeReview."""

    def test_review_changes(self):
        """Review code changes."""
        review = AutoCodeReview()
        result = review.review_changes(["file1.py"], "diff")
        assert "answered" in result


class TestTestAggregator:
    """Test TestAggregator."""

    def test_aggregate_sarah(self):
        """Aggregate SARAH tests."""
        agg = TestAggregator()
        result = agg.aggregate_sarah()
        assert "total_collected" in result
        assert result["total_collected"] > 0


class TestMetricsCollector:
    """Test MetricsCollector."""

    def test_collect(self):
        """Collect metrics."""
        collector = MetricsCollector()
        result = collector.collect()
        assert "kilo_queue" in result
        assert "freebuff_queue" in result


class TestLaneConfigs:
    """Test LANE_CONFIGS."""

    def test_lane_configs_exist(self):
        """All four lanes configured."""
        assert "kilo" in LANE_CONFIGS
        assert "freebuff" in LANE_CONFIGS
        assert "opencode" in LANE_CONFIGS
        assert "clinical" in LANE_CONFIGS

    def test_lane_configs_have_models(self):
        """Each lane has a model assigned."""
        for lane, config in LANE_CONFIGS.items():
            assert config.model
            assert config.specialty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])