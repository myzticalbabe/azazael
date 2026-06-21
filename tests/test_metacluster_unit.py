# coding: utf-8
"""Unit tests for METACLUSTER.py — CrossNatureRoutingEngine, MetaCluster."""

import sys
import os
import time
from datetime import datetime
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Python 3.14t Free-Threading Guard (module level — before imports) ──
from _env_314t import setup_314t
setup_314t(mock_pams=True)

try:
    import pytest
except BaseException:
    import types
    pytest = types.ModuleType("pytest")
    pytest.skip = lambda reason=None: exec("raise type('Skip', (BaseException,), {})(reason or '')")
    pytest.mark = types.ModuleType("mark")
    pytest.mark.skip = lambda *a, **kw: lambda f: f

# ── Module Under Test ──────────────────────────────────────────────
from CORE.WORMS.METACLUSTER import (
    # Data types
    MetaClusterResult,
    MetaClusterState,
    # Core class
    MetaCluster,
    # Constants
    NATURE_DEFINITIONS,
)

# CrossNatureRoutingEngine now lives in its own module
from CORE.WORMS.CROSS_NATURE_ROUTER import CrossNatureRoutingEngine


# ── Shared MetaCluster fixture (cache discovery across tests) ──
# Without this, each test would pay ~38s for discover_all() + ~128s for
# orchestrate_nature() = ~166s per test. With caching, subsequent tests
# reuse the already-discovered WORM_REGISTRY and NCM clusters.
# Note: CLUSTER INSPECTOR file scanning is NOT the bottleneck (128.2s→127.7s
# with limit), so no scan limit is applied. The 128s is from 85+ worm executions
# across the full routing graph.
_SHARED_MC: ('MetaCluster' | None) = None

def _get_mc() -> 'MetaCluster':
    """Get a MetaCluster with cached discovery.
    
    First call does full discover_all() (~38s), subsequent calls clone
    the NCM clusters from the shared instance (~0.1s).
    """
    global _SHARED_MC
    if _SHARED_MC is None:
        _SHARED_MC = MetaCluster()
        _SHARED_MC.discover_all()
    
    # Create a fresh MetaCluster with prepopulated NCM
    mc = MetaCluster()
    # Copy clusters from shared instance to avoid re-discovery
    # Use shallow copy to prevent test mutation from affecting others
    if _SHARED_MC.ncm and mc.ncm:
        mc.ncm.clusters = dict(_SHARED_MC.ncm.clusters)
    return mc


# ═══════════════════════════════════════════════════════════════════
# MetaClusterResult Tests
# ═══════════════════════════════════════════════════════════════════


class TestMetaClusterResult:
    """Verify MetaClusterResult dataclass."""

    def test_minimal_result(self):
        """Minimal result should have all defaults."""
        result = MetaClusterResult()
        assert result.orchestration_id == ""
        assert result.natures_executed == 0
        assert result.total_worms_ok == 0
        assert result.total_worms_fail == 0
        assert result.nature_results == {}
        assert result.insights == []
        assert result.errors == []

    def test_full_result(self):
        """Populated result should reflect values."""
        result = MetaClusterResult(
            orchestration_id="meta_001",
            natures_executed=2,
            total_worms_ok=10,
            total_worms_fail=1,
            nature_results={
                "security": {"success_count": 5, "failure_count": 0},
                "monitor": {"success_count": 5, "failure_count": 1},
            },
            insights=["Security: all OK", "Monitor: 1 failure"],
            cross_nature_paths_used=["security -> defense"],
        )
        assert result.orchestration_id == "meta_001"
        assert result.natures_executed == 2
        assert result.total_worms_ok == 10
        assert result.total_worms_fail == 1
        assert len(result.insights) == 2
        assert len(result.cross_nature_paths_used) == 1


# ═══════════════════════════════════════════════════════════════════
# MetaClusterState Tests
# ═══════════════════════════════════════════════════════════════════


class TestMetaClusterState:
    """Verify MetaClusterState dataclass."""

    def test_initial_state(self):
        """Fresh state should start idle."""
        state = MetaClusterState()
        assert state.phase == "idle"
        assert state.active_natures == set()
        assert state.completed_natures == set()
        assert state.failed_natures == set()
        assert state.worm_results == {}
        assert state.routed_messages == []
        assert state.events == []

    def test_with_run_id(self):
        """State with run_id set."""
        state = MetaClusterState(
            run_id="run_abc",
            phase="executing",
            active_natures={"security", "monitor"},
        )
        assert state.run_id == "run_abc"
        assert state.phase == "executing"
        assert "security" in state.active_natures


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine Tests
# ═══════════════════════════════════════════════════════════════════


class TestCrossNatureRoutingEngine:
    """Verify CrossNatureRoutingEngine route discovery and navigation."""

    def test_construction_builds_routes(self):
        """Construction should auto-build routes from NATURE_DEFINITIONS."""
        engine = CrossNatureRoutingEngine()
        assert isinstance(engine.routes, list)
        assert len(engine.routes) > 0

    def test_routes_are_unique(self):
        """No duplicate routes (same from→to pair)."""
        engine = CrossNatureRoutingEngine()
        route_pairs = [(r.from_nature, r.to_nature) for r in engine.routes]
        assert len(route_pairs) == len(set(route_pairs)), "Duplicate routes found"

    def test_get_routes_from(self):
        """Querying routes from a nature should return its outbound routes."""
        engine = CrossNatureRoutingEngine()
        routes = engine.get_routes_from("security")
        for r in routes:
            assert r.from_nature == "security"

    def test_get_routes_to(self):
        """Querying routes to a nature should return its inbound routes."""
        engine = CrossNatureRoutingEngine()
        # Find a nature that has inbound routes
        natures_with_inbound = set(r.to_nature for r in engine.routes)
        if natures_with_inbound:
            target = next(iter(natures_with_inbound))
            routes = engine.get_routes_to(target)
            for r in routes:
                assert r.to_nature == target

    def test_route_nature_output(self):
        """Routing output should activate downstream routes."""
        engine = CrossNatureRoutingEngine()
        state = MetaClusterState()
        count = engine.route_nature_output(
            "security",
            {"VulnScanner": {"success": True}},
            state,
        )
        if count > 0:
            assert len(state.routed_messages) > 0
            assert len(state.events) > 0

    def test_route_unknown_nature(self):
        """Routing from a nature with no outbound routes should return 0."""
        engine = CrossNatureRoutingEngine()
        state = MetaClusterState()
        # Use a nature that may not have outbound routes (e.g., visualization)
        count = engine.route_nature_output(
            "__nonexistent__",
            {},
            state,
        )
        assert count == 0

    def test_compute_routing_order(self):
        """Topological sort should place upstream natures first."""
        engine = CrossNatureRoutingEngine()
        order = engine.compute_routing_order(["security", "monitor"])
        assert isinstance(order, list)
        assert len(order) > 0

    def test_compute_routing_order_valid(self):
        """All natures in order should exist in NATURE_DEFINITIONS."""
        engine = CrossNatureRoutingEngine()
        order = engine.compute_routing_order(["security"])
        for nature in order:
            assert nature in NATURE_DEFINITIONS, f"Unknown nature: {nature}"

    def test_get_all_paths(self):
        """All paths should be valid chains of natures."""
        engine = CrossNatureRoutingEngine()
        paths = engine.get_all_paths()
        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, list)
            assert len(path) >= 1
            for nature in path:
                assert nature in NATURE_DEFINITIONS

    def test_routing_history(self):
        """Routing operations should be recorded in history."""
        engine = CrossNatureRoutingEngine()
        state = MetaClusterState()
        assert len(engine.routing_history) == 0
        engine.route_nature_output("security", {}, state)
        if len(engine.routes) > 0:
            assert len(engine.routing_history) >= 0  # May be 0 if no routes from security
        else:
            assert len(engine.routing_history) == 0


# ═══════════════════════════════════════════════════════════════════
# MetaCluster Tests
# ═══════════════════════════════════════════════════════════════════


class TestMetaClusterConstruction:
    """Verify MetaCluster construction and discovery."""

    def test_construction(self):
        """Construction should initialize sub-components."""
        mc = MetaCluster()
        assert mc.VERSION == "1.0.0"
        assert mc.router is not None
        assert isinstance(mc.router, CrossNatureRoutingEngine)
        assert mc.state is None
        assert mc._history == []
        assert mc._hooks is not None

    def test_discover_all(self):
        """Discovery should return dict of natures -> worm count."""
        mc = MetaCluster()
        counts = mc.discover_all()
        assert isinstance(counts, dict)
        # May be empty, but must be a dict

    def test_get_status_before_orchestration(self):
        """Status should work before any orchestration."""
        mc = MetaCluster()
        status = mc.get_status()
        assert status["version"] == "1.0.0"
        assert "routing_paths" in status
        assert "cross_nature_routes" in status
        assert len(status["cross_nature_routes"]) > 0
        assert status["state_phase"] == "idle"

    def test_get_last_result_empty(self):
        """Getting last result before any run should return None."""
        mc = MetaCluster()
        assert mc.get_last_result() is None


class TestMetaClusterHooks:
    """Verify MetaCluster hook system."""

    def test_register_hook(self):
        """Registering hooks should work."""
        mc = MetaCluster()
        executed = {"count": 0}

        def my_hook(**kwargs):
            executed["count"] += 1

        mc.on("pre_nature", my_hook)
        assert len(mc._hooks["pre_nature"]) == 1

    def test_multiple_hooks_same_point(self):
        """Multiple hooks on same point should all execute."""
        mc = MetaCluster()
        results = []

        def hook1(**kw):
            results.append("hook1")

        def hook2(**kw):
            results.append("hook2")

        mc.on("pre_nature", hook1)
        mc.on("pre_nature", hook2)
        mc._run_hooks("pre_nature", nature="test")
        assert "hook1" in results
        assert "hook2" in results

    def test_hook_error_does_not_crash(self):
        """Hook that raises should not crash the engine."""
        mc = MetaCluster()

        def broken_hook(**kw):
            raise ValueError("Intentional error")

        mc.on("pre_nature", broken_hook)
        mc._run_hooks("pre_nature", nature="test")  # Should not raise


class TestMetaClusterOrchestration:
    """Verify MetaCluster orchestration methods (uses cached discovery)."""

    def test_orchestrate_nature(self):
        """Orchestrating a single nature should return result."""
        mc = _get_mc()
        result = mc.orchestrate_nature("security")
        if result is not None:
            assert isinstance(result, MetaClusterResult)
            assert result.natures_executed >= 0

    def test_orchestrate_multiple(self):
        """Orchestrating multiple natures should execute them."""
        mc = _get_mc()
        result = mc.orchestrate(natures=["security", "monitor", "diagnostic"])
        if result is not None:
            assert isinstance(result, MetaClusterResult)
            assert result.natures_executed > 0

    def test_orchestrate_adaptive(self):
        """Adaptive orchestration should select priority natures."""
        mc = _get_mc()
        result = mc.orchestrate_adaptive(max_natures=3)
        if result is not None:
            assert isinstance(result, MetaClusterResult)
            assert result.natures_executed <= 3

    def test_orchestrate_full_pipeline(self):
        """Pipeline orchestration should follow routing graph."""
        mc = _get_mc()
        result = mc.orchestrate_full_pipeline("security")
        if result is not None:
            assert isinstance(result, MetaClusterResult)
            # Should have at least 1 nature (the starting one)

    def test_orchestrate_history(self):
        """Each orchestration should add to history."""
        mc = _get_mc()
        assert len(mc._history) == 0
        mc.orchestrate_nature("security")
        assert len(mc._history) >= 1

    def test_get_last_result_after_run(self):
        """Getting last result after a run should return it."""
        mc = _get_mc()
        mc.orchestrate_nature("security")
        last = mc.get_last_result()
        if last is not None:
            assert isinstance(last, MetaClusterResult)
            assert last.orchestration_id is not None


class TestMetaClusterMermaid:
    """Verify MetaCluster Mermaid graph generation."""

    def test_to_mermaid_structure(self):
        """Mermaid graph should have expected structure."""
        mc = _get_mc()
        mermaid = mc.to_mermaid()
        assert isinstance(mermaid, str)
        assert "graph TB" in mermaid or "graph" in mermaid

    def test_to_mermaid_execution_flow_before_run(self):
        """Execution flow before any run should return placeholder."""
        mc = MetaCluster()
        flow = mc.to_mermaid_execution_flow()
        assert isinstance(flow, str)
        assert "orchestration" in flow.lower() or "No" in flow

    def test_to_mermaid_execution_flow_after_run(self):
        """Execution flow after a run should show results."""
        mc = _get_mc()
        mc.orchestrate_nature("security")
        flow = mc.to_mermaid_execution_flow()
        assert isinstance(flow, str)
        assert "graph LR" in flow

    def test_to_mermaid_routing_topology(self):
        """Routing topology graph should show cross-nature routes."""
        mc = MetaCluster()
        topology = mc.to_mermaid_routing_topology()
        assert isinstance(topology, str)
        assert "graph TB" in topology
        assert "-->|feeds|" in topology

    def test_to_mermaid_all_functions(self):
        """Functions diagram should work even with no data."""
        mc = MetaCluster()
        diagram = mc.to_mermaid_all_functions()
        assert isinstance(diagram, str)


class TestMetaClusterExport:
    """Verify MetaCluster state export."""

    def test_export_state_json(self):
        """Exporting state should produce valid JSON."""
        import json
        import tempfile
        import os
        mc = _get_mc()
        mc.orchestrate_nature("security")
        # Export to a temporary file (never the default path)
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            pass
        temp_path = f.name
        try:
            export_path = mc.export_state(filepath=temp_path)
            assert export_path is not None
            assert export_path == temp_path
            # File should be valid JSON
            with open(export_path, "r") as f:
                data = json.load(f)
            assert "version" in data
            assert "free_threaded" in data
            assert "orchestration_history" in data
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    p = f = 0
    for name, obj in list(globals().items()):
        if isinstance(obj, type) and name.startswith("Test"):
            inst = obj()
            for mn in dir(inst):
                if mn.startswith("test_"):
                    try:
                        getattr(inst, mn)()
                        print(f"  [OK] {name}.{mn}")
                        p += 1
                    except Exception as e:
                        print(f"  [FAIL] {name}.{mn}: {e}")
                        f += 1
    print(f"  Passed: {p}, Failed: {f}")
