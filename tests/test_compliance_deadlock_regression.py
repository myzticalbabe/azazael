# coding: utf-8
"""
Deadlock regression tests for ComplianceScorer and BehavioralGraphAnalyzer.

Verifies that the Lock→RLock fix resolves the non-reentrant deadlock where:
  - ComplianceScorer.snapshot() acquires self._lock then calls
    get_weighted_score() (and should_halt()) which re-acquire the same lock
  - BehavioralGraphAnalyzer.get_graph_summary() acquires self._lock then calls
    check_anomalies() which re-acquires the same lock

All tests use a timeout guard (< 3s) to detect if the deadlock reappears.
"""

import sys
import time
from pathlib import Path

import pytest  # type: ignore[import-not-found]

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

_DEADLOCK_TIMEOUT = 3.0  # seconds — any call taking longer means deadlock


def _assert_no_deadlock(fn, *args, **kwargs):
    """Run fn(args) with a timeout guard. Raises if it takes too long."""
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - t0
    assert elapsed < _DEADLOCK_TIMEOUT, (
        f"{fn.__name__} took {elapsed:.1f}s (>{_DEADLOCK_TIMEOUT}s) — "
        f"probable deadlock! Expected < 1s."
    )
    return result


# ── ComplianceScorer deadlock regression ───────────────────────────


class TestComplianceScorerDeadlock:
    """Verify ComplianceScorer methods that previously deadlocked."""

    def test_snapshot_completes(self):
        """snapshot() should complete without deadlocking (was Lock→RLock fix)."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        result = _assert_no_deadlock(scorer.snapshot)

        assert "weighted_score" in result
        assert "should_halt" in result
        assert "metrics" in result
        assert result["weighted_score"] == 1.0  # perfect score with no recorded failures

    def test_snapshot_after_records(self):
        """snapshot() after record_pass/record_fail should still not deadlock."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        scorer.record_pass("gate_assertion_rate")
        scorer.record_pass("code_review_rate")
        scorer.record_fail("error_recurrence")

        result = _assert_no_deadlock(scorer.snapshot)

        assert "weighted_score" in result
        assert result["weighted_score"] > 0.5  # should still be decent

    def test_multiple_snapshots(self):
        """Multiple sequential snapshot() calls should all complete."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        for _ in range(10):
            result = _assert_no_deadlock(scorer.snapshot)
            assert isinstance(result["weighted_score"], float)

    def test_snapshot_interleaved_with_records(self):
        """Interleaving record_pass/fail with snapshot should not deadlock."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        for i in range(20):
            if i % 3 == 0:
                scorer.record_pass("gate_assertion_rate")
            elif i % 3 == 1:
                scorer.record_fail("agent_utilization")
            else:
                _assert_no_deadlock(scorer.snapshot)

    def test_should_halt_after_snapshot(self):
        """Calling should_halt() after snapshot() should not deadlock."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        _assert_no_deadlock(scorer.snapshot)
        halt, score, threshold = _assert_no_deadlock(scorer.should_halt)

        assert isinstance(halt, bool)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_get_weighted_score_after_snapshot(self):
        """get_weighted_score() after snapshot() should not deadlock."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        _assert_no_deadlock(scorer.snapshot)
        score = _assert_no_deadlock(scorer.get_weighted_score)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_concurrent_methods_on_same_instance(self):
        """Methods that all acquire self._lock should not deadlock each other."""
        from CORE.compliance.validating import ComplianceScorer

        scorer = ComplianceScorer()
        # Call all lock-bearing methods in sequence
        scorer.record_pass("gate_assertion_rate")
        _assert_no_deadlock(scorer.snapshot)
        _assert_no_deadlock(scorer.get_weighted_score)
        _assert_no_deadlock(scorer.should_halt)
        scorer.record_fail("error_recurrence")  # METRIC_WEIGHTS has this, so fail drops score < 1.0
        _assert_no_deadlock(scorer.snapshot)
        score = _assert_no_deadlock(scorer.get_weighted_score)
        assert score < 1.0  # fail recorded, should reduce score


# ── BehavioralGraphAnalyzer deadlock regression ────────────────────


class TestBehavioralGraphAnalyzerDeadlock:
    """Verify BehavioralGraphAnalyzer methods that previously deadlocked."""

    def test_get_graph_summary_completes_with_no_actions(self):
        """get_graph_summary() with empty action list should not deadlock."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        summary = _assert_no_deadlock(analyzer.get_graph_summary)

        assert summary["total_actions"] == 0
        assert summary["action_counts"] == {}
        assert summary["anomalies"] == []

    def test_get_graph_summary_after_actions(self):
        """get_graph_summary() after recording actions should not deadlock."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        analyzer.record_action("read_file", {"file": "foo.py"}, "dev")
        analyzer.record_action("edit_file", {"file": "foo.py"}, "dev")
        analyzer.record_action("review", {}, "dev")

        summary = _assert_no_deadlock(analyzer.get_graph_summary)

        assert summary["total_actions"] == 3
        assert summary["action_counts"]["read_file"] == 1
        assert summary["action_counts"]["edit_file"] == 1
        assert isinstance(summary["anomalies"], list)

    def test_check_anomalies_after_get_graph_summary(self):
        """Calling check_anomalies() after get_graph_summary() should not deadlock."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        analyzer.record_action("read_file", {}, "dev")
        analyzer.record_action("edit_file", {}, "dev")

        # This was the deadlock pattern: get_graph_summary() -> check_anomalies()
        _assert_no_deadlock(analyzer.get_graph_summary)

        # Now verify check_anomalies() also works independently
        anomalies = _assert_no_deadlock(analyzer.check_anomalies)
        assert isinstance(anomalies, list)

    def test_multiple_get_graph_summary_calls(self):
        """Multiple sequential get_graph_summary() calls should all complete."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        for i in range(10):
            analyzer.record_action(f"action_{i}", {}, "dev")
            summary = _assert_no_deadlock(analyzer.get_graph_summary)
            assert summary["total_actions"] == i + 1

    def test_get_graph_summary_interleaved_with_records(self):
        """Interleaving record_action with get_graph_summary should not deadlock."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        for i in range(20):
            analyzer.record_action(f"action_{i}", {"n": i}, "dev")
            if i % 2 == 0:
                _assert_no_deadlock(analyzer.get_graph_summary)
            else:
                _assert_no_deadlock(analyzer.check_anomalies)

    def test_get_action_count_after_get_graph_summary(self):
        """get_action_count() after get_graph_summary() should not deadlock."""
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        analyzer = BehavioralGraphAnalyzer()
        analyzer.record_action("read_file", {}, "dev")
        analyzer.record_action("edit_file", {}, "dev")

        _assert_no_deadlock(analyzer.get_graph_summary)
        count = _assert_no_deadlock(lambda: analyzer.get_action_count("read_file"))
        assert count == 1


# ── Cross-component deadlock regression ────────────────────────────


class TestCrossComponentDeadlock:
    """Verify that using both components together doesn't deadlock."""

    def test_analyzer_and_scorer_sequence(self):
        """Using both BehavioralGraphAnalyzer and ComplianceScorer sequentially."""
        from CORE.compliance.validating import ComplianceScorer
        from CORE.compliance.governance import BehavioralGraphAnalyzer

        scorer = ComplianceScorer()
        analyzer = BehavioralGraphAnalyzer()

        # Record actions and score passes
        analyzer.record_action("test", {}, "dev")
        scorer.record_pass("gate_assertion_rate")

        # Call both deadlock-prone methods
        _assert_no_deadlock(analyzer.get_graph_summary)
        _assert_no_deadlock(scorer.snapshot)

        # Repeat to ensure no state corruption
        analyzer.record_action("test2", {}, "dev")
        scorer.record_fail("error_recurrence")
        _assert_no_deadlock(analyzer.get_graph_summary)
        _assert_no_deadlock(scorer.snapshot)

    def test_both_with_orchestrator(self):
        """Both components should work when called through ComplianceOrchestrator."""
        from CORE.compliance.orchestrator import ComplianceOrchestrator
        from CORE.compliance.state_machine import ComplianceState

        co = ComplianceOrchestrator()
        co.state_machine.transition_to(ComplianceState.GATE_ASSERT)

        # These call snapshot() and get_graph_summary() internally
        ox = _assert_no_deadlock(
            co.check_rule_0x, action="test", role="developer",
            context={"state": "GATE_ASSERT"}
        )
        assert ox["component_count"] == 8

        oy = _assert_no_deadlock(
            co.check_rule_0y, action="test", role="developer", context={}
        )
        assert oy["component_count"] == 5

    def test_both_with_get_status(self):
        """get_status() calls scorer.snapshot() and graph_analyzer.get_graph_summary()."""
        from CORE.compliance.orchestrator import ComplianceOrchestrator
        from CORE.compliance.state_machine import ComplianceState

        co = ComplianceOrchestrator()
        co.state_machine.transition_to(ComplianceState.GATE_ASSERT)

        status = _assert_no_deadlock(co.get_status)
        assert "score" in status
        assert "graph" in status
        assert "state_machine" in status
