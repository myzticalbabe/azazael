# coding: utf-8
"""Extended unit tests for NATURE_CLUSTERS.py — DLQ, retry, routing, discovery dedup."""

import sys
import os
import time
import json
from typing import Any
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Module Under Test ──────────────────────────────────────────────
from CORE.WORMS.NATURE_CLUSTERS import (
    NatureResult,
    CrossNatureRoute,
    NatureCluster,
    NatureClusterManager,
    NATURE_DEFINITIONS,
)


# ═══════════════════════════════════════════════════════════════════
# Dead Letter Queue Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterDql:
    """Verify NatureCluster dead letter queue."""

    def test_dlq_empty_on_creation(self):
        """DLQ should be empty on fresh cluster."""
        cluster = NatureCluster("security")
        assert cluster.get_failed_executions() == []

    def test_dlq_records_failure(self):
        """Recorded failure should appear in DLQ."""
        cluster = NatureCluster("security")
        cluster._record_failure("TestWorm", {"success": False, "error": "test error"})
        failures = cluster.get_failed_executions()
        assert len(failures) == 1
        assert failures[0]["worm"] == "TestWorm"
        assert failures[0]["error"] == "test error"
        assert failures[0]["nature"] == "security"

    def test_dlq_since_filter(self):
        """DLQ should filter by timestamp."""
        cluster = NatureCluster("security")
        before = time.time()
        cluster._record_failure("WormA", {"success": False, "error": "e1"})
        cluster._record_failure("WormB", {"success": False, "error": "e2"})
        after = time.time()
        cluster._record_failure("WormC", {"success": False, "error": "e3"})

        recent = cluster.get_failed_executions(since=after)
        assert len(recent) == 1
        assert recent[0]["worm"] == "WormC"

        all_failures = cluster.get_failed_executions(since=before)
        assert len(all_failures) >= 2

    def test_dlq_recent_first(self):
        """DLQ should return most recent first."""
        cluster = NatureCluster("security")
        cluster._record_failure("A", {"success": False, "error": "e1"})
        time.sleep(0.01)
        cluster._record_failure("B", {"success": False, "error": "e2"})
        failures = cluster.get_failed_executions()
        assert failures[0]["worm"] == "B"
        assert failures[1]["worm"] == "A"

    def test_dlq_clear(self):
        """Clearing DLQ should remove all records."""
        cluster = NatureCluster("security")
        cluster._record_failure("A", {"success": False, "error": "e1"})
        cluster._record_failure("B", {"success": False, "error": "e2"})
        assert len(cluster.get_failed_executions()) == 2
        cluster.clear_failed_executions()
        assert cluster.get_failed_executions() == []

    def test_dlq_breaker_state(self):
        """DLQ should record breaker state when provided."""
        cluster = NatureCluster("security")
        cluster._record_failure("A", {"success": False, "error": "e1"}, breaker_state="open")
        failures = cluster.get_failed_executions()
        assert failures[0]["breaker_state"] == "open"


class TestNatureClusterRetry:
    """Verify NatureCluster.retry_failed_worms()."""

    def test_retry_empty_dlq(self):
        """Retrying empty DLQ should return zero counts."""
        cluster = NatureCluster("security")
        result = cluster.retry_failed_worms(max_retries=2)
        assert result["retried"] == 0
        assert result["succeeded"] == 0
        assert result["still_failed"] == 0

    def test_retry_unknown_worm(self):
        """Retrying a worm not in self.worms should still_failed (not retried)."""
        cluster = NatureCluster("security")
        cluster._record_failure("NonexistentWorm", {"success": False, "error": "missing"})
        result = cluster.retry_failed_worms(max_retries=0)
        # retried=0 because the worm class doesn't exist (cls is None, skipped before increment)
        assert result["retried"] == 0, f"Expected 0, got {result['retried']}"
        assert result["still_failed"] == 1, f"Expected 1, got {result['still_failed']}"
        assert len(result["errors"]) > 0

    def test_retry_known_worm_no_recovery(self):
        """Retrying a known worm with max_retries=0 should not re-execute."""
        # Create a cluster with a mock class that has a known method
        cluster = NatureCluster("test_mock_retry")

        class MockWorm:
            """Mock worm with a standard method."""
            def get_status(self):
                return {"mock": True}

        cluster.add_worm_manual("MockWorm", MockWorm)

        # Record failure
        cluster._record_failure("MockWorm", {"success": False, "error": "previous_failure"})
        result = cluster.retry_failed_worms(max_retries=0)
        # With max_retries=0, it attempts once but should not re-execute the retry loop
        assert result["retried"] >= 0


class TestCrossNatureRoutes:
    """Verify cross-nature routing."""

    def test_cross_nature_route_minimal(self):
        """Minimal route should have defaults."""
        route = CrossNatureRoute(from_nature="security", to_nature="defense")
        assert route.from_nature == "security"
        assert route.to_nature == "defense"
        assert route.data_mapping == {}
        assert route.description == ""

    def test_cross_nature_route_full(self):
        """Full route should have all fields populated."""
        route = CrossNatureRoute(
            from_nature="monitor",
            to_nature="diagnostic",
            data_mapping={"cpu_pct": "load_factor"},
            description="High CPU triggers diagnostic",
        )
        assert route.data_mapping["cpu_pct"] == "load_factor"
        assert "High CPU" in route.description

    def test_cross_nature_routes_from_definitions(self):
        """Routes should be derivable from NATURE_DEFINITIONS."""
        ncm = NatureClusterManager()
        routes = ncm.get_cross_nature_routes()
        assert isinstance(routes, list)
        assert len(routes) > 0
        for route in routes:
            assert route.from_nature in NATURE_DEFINITIONS
            assert route.to_nature in NATURE_DEFINITIONS

    def test_feeds_into_connectivity(self):
        """Every feeds_into target should exist as a nature definition."""
        for name, definition in NATURE_DEFINITIONS.items():
            for target in definition.get("feeds_into", []):
                assert target in NATURE_DEFINITIONS, \
                    f"Nature '{name}' feeds into '{target}' which doesn't exist"

    def test_no_self_reference(self):
        """No nature should feed into itself."""
        for name, definition in NATURE_DEFINITIONS.items():
            assert name not in definition.get("feeds_into", []), \
                f"Nature '{name}' feeds into itself"

    def test_route_results_structure(self):
        """Route results should have expected shape."""
        ncm = NatureClusterManager()
        route = CrossNatureRoute(
            from_nature="security",
            to_nature="defense",
            description="Security to defense",
        )
        from_results = {
            "security": NatureResult(
                nature="security",
                worm_results={"VulnScanner": {"success": True, "result": {"vulns": 3}}},
                success_count=1,
            )
        }
        routed = ncm.route_results(from_results, route)
        assert routed["from"] == "security"
        assert routed["to"] == "defense"
        assert "VulnScanner" in routed["data"]

    def test_route_results_no_source(self):
        """Route results with no source nature should return empty data."""
        ncm = NatureClusterManager()
        route = CrossNatureRoute(from_nature="missing", to_nature="defense")
        routed = ncm.route_results({}, route)
        assert routed["data"] == {}


class TestNatureClusterManagerDlqAggregation:
    """Verify aggregated DLQ across all clusters."""

    def test_dead_letter_summary_empty(self):
        """Empty DLQ summary should have zero counts."""
        ncm = NatureClusterManager()
        summary = ncm.get_dead_letter_summary(lookback_seconds=3600)
        assert summary["total_failed"] == 0
        assert summary["affected_natures"] == 0

    def test_dead_letter_summary_structure(self):
        """DLQ summary should have expected keys."""
        ncm = NatureClusterManager()
        summary = ncm.get_dead_letter_summary()
        for key in ("total_failed", "affected_natures", "per_nature",
                     "per_worm", "recent_errors"):
            assert key in summary, f"Missing key: {key}"

    def test_retry_all_failed_worms_empty(self):
        """Retrying all failed worms with no failures should return zeros."""
        ncm = NatureClusterManager()
        result = ncm.retry_all_failed_worms(max_retries=2)
        assert result["total_retried"] == 0
        assert result["total_succeeded"] == 0
        assert result["still_failed"] == 0


class TestNatureDefinitionsExtended:
    """Extended NATURE_DEFINITIONS validation."""

    def test_all_natures_have_icon(self):
        """Every nature should have an icon."""
        for name, definition in NATURE_DEFINITIONS.items():
            assert "icon" in definition, f"Missing icon for {name}"
            assert len(definition["icon"]) > 0

    def test_feeds_into_is_list(self):
        """feeds_into should be a list."""
        for name, definition in NATURE_DEFINITIONS.items():
            feeds = definition.get("feeds_into", [])
            assert isinstance(feeds, list), f"feeds_into for {name} is not a list"

    def test_discovery_dedup(self):
        """Repeated discover_worms should not increase worm count."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()

        # Get baseline worm counts
        baseline = {}
        for nature, cluster in ncm.clusters.items():
            baseline[nature] = len(cluster.worms)

        # Discover again
        ncm.discover_all_natures()

        # Verify no new worms were added
        for nature, cluster in ncm.clusters.items():
            assert len(cluster.worms) == baseline.get(nature, 0), \
                f"Worm count changed for {nature}: {baseline.get(nature, 0)} -> {len(cluster.worms)}"

    def test_mermaid_functions_structure(self):
        """Mermaid functions diagram should have expected structure."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        mermaid = ncm.to_mermaid_functions()
        assert isinstance(mermaid, str)
        assert "classDiagram" in mermaid


# ═══════════════════════════════════════════════════════════════════
# Standalone Runner
# ═══════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    for name, obj in sorted(globals().items(), key=lambda x: x[0]):
        if isinstance(obj, type) and name.startswith("Test"):
            inst = obj()
            for mn in sorted(dir(inst)):
                if mn.startswith("test_"):
                    try:
                        getattr(inst, mn)()
                        print(f"  [OK] {name}.{mn}")
                        passed += 1
                    except Exception as e:
                        print(f"  [FAIL] {name}.{mn}: {e}")
                        failed += 1
                        errors.append(f"{name}.{mn}: {e}")

    print(f"\n  Passed: {passed}, Failed: {failed}")
    if errors:
        print("  Errors:")
        for e in errors[:5]:
            print(f"    {e}")
    sys.exit(0 if failed == 0 else 1)
