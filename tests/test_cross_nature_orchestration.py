# coding: utf-8
"""Integration tests for cross-nature orchestration.

Tests NatureClusterManager + MetaCluster cross-nature routing and data flow:
  - NatureClusterManager discovers all 17+ natures
  - MetaCluster orchestrates Natures with routing
  - CrossNatureRoutingEngine computes correct execution order
  - Data routing between Natures (upstream -> downstream flow)
  - MetaClusterState tracks execution phases
  - Integration between CLUSTERWORMS, NATURE_CLUSTERS, and METACLUSTER

Run standalone (3.14t compatible):
  python tests/test_cross_nature_orchestration.py

Run with pytest:
  python -m pytest tests/test_cross_nature_orchestration.py -v
"""

import sys
import os
import time
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ["PYTHONIOENCODING"] = "utf-8"

import pytest
import threading


# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def ncm():
    """Module-level NatureClusterManager — discovered once."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
    from CORE.worm_registry import discover_worms
    print("  Discovering worms for NCM...", end=" ", flush=True)
    t0 = time.time()
    discover_worms()
    ncm = NatureClusterManager()
    ncm.discover_all_natures()
    elapsed = time.time() - t0
    print(f"({len(ncm.clusters)} natures, {elapsed:.1f}s)")
    return ncm


@pytest.fixture(scope="module")
def metaclust():
    """Module-level MetaCluster — discovered once."""
    from CORE.WORMS.METACLUSTER import MetaCluster
    print("  Creating MetaCluster...", end=" ", flush=True)
    t0 = time.time()
    mc = MetaCluster()
    mc.discover_all()
    elapsed = time.time() - t0
    print(f"({elapsed:.1f}s)")
    return mc


# ── NatureClusterManager Tests ─────────────────────────────────────


class TestNatureClusterManagerDiscovery:
    """Verify NatureClusterManager discovers all natures."""

    def test_all_categories_have_clusters(self, ncm):
        """Every worm category should have a NatureCluster."""
        from CORE.worm_registry import get_all_categories
        categories = get_all_categories()
        missing = [c for c in categories if c not in ncm.clusters]
        assert not missing, f"Natures without clusters: {missing}"
        assert len(ncm.clusters) >= 17, f"Expected >=17 natures, got {len(ncm.clusters)}"

    def test_each_cluster_has_worms(self, ncm):
        """Every NatureCluster should have at least 1 worm."""
        empty = [n for n, c in ncm.clusters.items() if len(c.worms) == 0]
        assert not empty, f"Empty clusters: {empty}"

    def test_cluster_get_status(self, ncm):
        """Every cluster should return valid status."""
        for nature, cluster in ncm.clusters.items():
            status = cluster.get_status()
            assert status["nature"] == nature
            assert status["worm_count"] > 0
            assert "cluster_id" in status
            assert "version" in status

    def test_get_cluster_creates_on_demand(self, ncm):
        """get_cluster() should create clusters for any valid nature."""
        cluster = ncm.get_cluster("monitor")
        assert cluster is not None
        assert cluster.nature == "monitor"
        assert len(cluster.worms) > 0


class TestNatureClusterManagerExecution:
    """Verify NatureClusterManager can execute individual natures."""

    def test_execute_nature_sequential(self, ncm):
        """execute_nature() should return results for any nature."""
        for nature in list(ncm.clusters.keys())[:3]:
            result = ncm.execute_nature(nature, parallel=False)
            assert result is not None, f"{nature}: returned None"
            assert result.success_count + result.failure_count > 0
            assert result.duration_ms > 0

    def test_execute_nature_parallel(self, ncm):
        """execute_nature() should work in parallel mode."""
        result = ncm.execute_nature("monitor", parallel=True)
        assert result is not None
        assert result.success_count + result.failure_count > 0

    def test_execute_priority_natures(self, ncm):
        """execute_priority_natures() should select top-N natures."""
        results = ncm.execute_priority_natures(max_natures=3)
        assert len(results) >= 1
        assert len(results) <= 3
        for nature, r in results.items():
            assert r.success_count + r.failure_count > 0

    def test_list_all_worms(self, ncm):
        """list_all_worms() should return worms grouped by nature."""
        all_worms = ncm.list_all_worms()
        assert len(all_worms) >= 17
        total = sum(len(w) for w in all_worms.values())
        assert total >= 75


class TestNatureClusterDeadLetterQueue:
    """Verify DLQ aggregation across natures."""

    def test_get_dead_letter_summary(self, ncm):
        """get_dead_letter_summary() should return valid aggregated stats."""
        summary = ncm.get_dead_letter_summary(lookback_seconds=86400)
        assert "total_failed" in summary
        assert "affected_natures" in summary
        assert "per_nature" in summary
        assert "per_worm" in summary
        assert "recent_errors" in summary


# ── MetaCluster Tests ──────────────────────────────────────────────


class TestMetaClusterDiscovery:
    """Verify MetaCluster discovers and initializes properly."""

    def test_metacluster_has_ncm(self, metaclust):
        """MetaCluster should have a NatureClusterManager."""
        assert metaclust.ncm is not None
        assert len(metaclust.ncm.clusters) >= 17

    def test_metacluster_has_router(self, metaclust):
        """MetaCluster should have a CrossNatureRoutingEngine."""
        assert metaclust.router is not None
        routes = metaclust.router.routes
        assert len(routes) > 0, "No cross-nature routes found"

    def test_metacluster_status(self, metaclust):
        """get_status() should return valid status."""
        status = metaclust.get_status()
        assert status["version"] == "1.0.0"
        assert "ncm" in status
        assert "routing_paths" in status
        assert "cross_nature_routes" in status
        assert status["cross_nature_routes"] > 0


class TestMetaClusterOrchestration:
    """Verify MetaCluster orchestrates single and multiple natures."""

    def test_orchestrate_single_nature(self, metaclust):
        """orchestrate_nature() should work for a single nature. (Marked slow — executes real worms.)"""
        result = metaclust.orchestrate_nature("monitor")
        if result is None:
            pytest.skip("Nature 'monitor' not available")
        assert result.natures_executed == 1
        assert result.total_worms_ok + result.total_worms_fail > 0
        assert result.duration_ms > 0
        assert result.orchestration_id

    def test_orchestrate_multiple_natures(self, metaclust):
        """orchestrate() with 3 natures should route between them."""
        result = metaclust.orchestrate(
            natures=["monitor", "diagnostic", "orchestration"]
        )
        assert result is not None
        assert result.natures_executed >= 1
        assert len(result.nature_results) >= 1
        assert len(result.insights) > 0

    def test_orchestration_generates_insights(self, metaclust):
        """Orchestration should always generate insights."""
        result = metaclust.orchestrate(max_natures=2)
        assert len(result.insights) > 0, "No insights generated"
        assert isinstance(result.insights[0], str)

    def test_orchestration_generates_recommendations(self, metaclust):
        """Orchestration should always generate recommendations."""
        result = metaclust.orchestrate(max_natures=2)
        assert isinstance(result.recommendations, list)

    def test_orchestration_tracks_cross_nature_paths(self, metaclust):
        """Orchestration should track cross-nature routing paths."""
        result = metaclust.orchestrate(max_natures=3)
        assert isinstance(result.cross_nature_paths_used, list)

    def test_orchestration_result_has_errors_field(self, metaclust):
        """MetaClusterResult should always have an errors list."""
        result = metaclust.orchestrate(max_natures=2)
        assert isinstance(result.errors, list)
        # Errors are informational about natures that couldn't execute

    def test_adaptive_orchestration(self, metaclust):
        """orchestrate_adaptive() should auto-select natures."""
        result = metaclust.orchestrate_adaptive(max_natures=3)
        assert result.natures_executed >= 1
        assert result.natures_executed <= 3


class TestMetaClusterMermaidGraphs:
    """Verify Mermaid graph generation."""

    def test_to_mermaid(self, metaclust):
        """to_mermaid() should generate a valid Mermaid graph."""
        graph = metaclust.to_mermaid()
        assert "graph TB" in graph or "graph TD" in graph
        assert "subgraph" in graph.lower()

    def test_to_mermaid_execution_flow(self, metaclust):
        """to_mermaid_execution_flow() should graph the last orchestration."""
        metaclust.orchestrate(max_natures=1)
        graph = metaclust.to_mermaid_execution_flow()
        assert "graph LR" in graph
        assert "OK" in graph or "FAIL" in graph

    def test_to_mermaid_routing_topology(self, metaclust):
        """to_mermaid_routing_topology() should show routing graph."""
        graph = metaclust.to_mermaid_routing_topology()
        assert "graph TB" in graph
        assert "feeds" in graph.lower()


class TestMetaClusterState:
    """Verify MetaClusterState tracks phases correctly."""

    def test_state_phases(self, metaclust):
        """State should progress through correct phases.
        
        Note: phase is checked immediately after orchestration to avoid
        order-dependence with other tests that also call orchestrate().
        """
        result = metaclust.orchestrate(max_natures=1)
        # Check state right after orchestration — before any other test runs
        phase_after = metaclust.state.phase if metaclust.state else "none"
        assert phase_after == "complete", f"Expected 'complete', got '{phase_after}'"
        assert metaclust.state.completed_natures or metaclust.state.failed_natures

    def test_history_tracks_results(self, metaclust):
        """Orchestration history should accumulate exactly one new result."""
        before = len(metaclust._history)
        metaclust.orchestrate(max_natures=1)
        after = len(metaclust._history)
        assert after == before + 1, (
            f"Expected history to grow by 1, but went from {before} to {after}"
        )

    def test_get_last_result(self, metaclust):
        """get_last_result() should return the most recent orchestration."""
        metaclust.orchestrate(max_natures=1)
        last = metaclust.get_last_result()
        assert last is not None
        assert last.orchestration_id


class TestCrossNatureRouting:
    """Verify cross-nature routing engine routes data correctly."""

    def test_router_has_paths(self, metaclust):
        """Router should have at least some cross-nature paths."""
        paths = metaclust.router.get_all_paths()
        assert len(paths) > 0

    def test_routing_order(self, metaclust):
        """compute_routing_order() should produce a valid order."""
        order = metaclust.router.compute_routing_order(
            ["monitor", "diagnostic", "orchestration"]
        )
        assert len(order) >= 1
        assert all(isinstance(n, str) for n in order)

    def test_routes_to_nature(self, metaclust):
        """get_routes_to() should return upstream routes for at least some natures."""
        # Check multiple natures — at least one should have routes
        found_any = False
        for nature in list(metaclust.ncm.clusters.keys())[:5]:
            routes = metaclust.router.get_routes_to(nature)
            if routes:
                found_any = True
                assert hasattr(routes[0], "from_nature")
                assert hasattr(routes[0], "to_nature")
                break
        assert found_any, "No nature has upstream routes"


class TestIntegrationClusterToMetaCluster:
    """Verify end-to-end integration from worm to meta-orchestration."""

    def test_full_pipeline(self, metaclust):
        """Execute a full pipeline: security -> downstream natures."""
        result = metaclust.orchestrate_full_pipeline("monitor")
        assert result is not None
        assert result.natures_executed >= 1
        assert len(result.cross_nature_paths_used) >= 0

    def test_discover_then_orchestrate(self, metaclust):
        """Multiple orchestration runs should work on same MetaCluster."""
        for i in range(2):
            result = metaclust.orchestrate(max_natures=2)
            assert result is not None
            assert result.natures_executed >= 1


# ── Standalone runner ──────────────────────────────────────────────


def _run_standalone():
    """Run all tests standalone (for 3.14t where pytest segfaults)."""
    print("Cross-Nature Orchestration Integration Tests")
    print("=" * 60)
    print()

    from CORE.worm_registry import discover_worms
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
    from CORE.WORMS.METACLUSTER import MetaCluster

    print("  Initializing...", end=" ", flush=True)
    t0 = time.time()
    discover_worms()
    ncm = NatureClusterManager()
    ncm.discover_all_natures()
    mc = MetaCluster()
    mc.discover_all()
    elapsed = time.time() - t0
    print(f"({len(ncm.clusters)} natures, {elapsed:.1f}s)")
    print()

    passed = 0
    failed = 0

    # Run test classes
    test_classes = [
        TestNatureClusterManagerDiscovery,
        TestNatureClusterManagerExecution,
        TestNatureClusterDeadLetterQueue,
        TestMetaClusterDiscovery,
        TestMetaClusterOrchestration,
        TestMetaClusterMermaidGraphs,
        TestMetaClusterState,
        TestCrossNatureRouting,
        TestIntegrationClusterToMetaCluster,
    ]

    for cls in test_classes:
        print(f"[{cls.__name__}]")
        inst = cls()
        # Inject fixtures
        for attr in dir(inst):
            if attr.startswith("test_"):
                try:
                    fn = getattr(inst, attr)
                    # Auto-inject ncm/mc based on parameter names
                    import inspect
                    sig = inspect.signature(fn)
                    params = {}
                    if "ncm" in sig.parameters:
                        params["ncm"] = ncm
                    if "metaclust" in sig.parameters:
                        params["metaclust"] = mc
                    fn(**params)
                    print(f"  [OK] {attr}")
                    passed += 1
                except AssertionError as e:
                    lines = str(e).split("\n")[:3]
                    print(f"  [FAIL] {attr}: {lines[0]}")
                    for line in lines[1:]:
                        print(f"         {line}")
                    failed += 1
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"  [FAIL] {attr}: {type(e).__name__}: {e}")
                    failed += 1
        print()

    print("=" * 60)
    print(f"  Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_standalone())
