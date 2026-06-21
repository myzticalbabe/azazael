"""Tests for CORE/WORMS/METACLUSTER.py.

These tests use class-level @patch decorators to keep all heavy dependencies
(PamsRecorder DB, config, breakers, logging) mocked for the entire test
lifetime. Previously these tests took 800s+ (now <2s).
"""
import sys, os, unittest, threading
from unittest.mock import MagicMock, patch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from CORE.WORMS.METACLUSTER import (
    MetaCluster, MetaClusterResult, MetaClusterState,
)
from CORE.WORMS.NATURE_CLUSTERS import NatureResult


# ── Shared mock factories ──────────────────────────────────────────

DEFAULT_NATURES = {
    "orchestration": 2,
    "monitor": 3,
    "security": 5,
    "defense": 4,
}


def _make_mock_ncm(natures=None):
    """Create a mock NatureClusterManager that never discovers real worms."""
    if natures is None:
        natures = DEFAULT_NATURES

    mock_ncm = MagicMock()
    mock_ncm.clusters = {n: MagicMock() for n in natures}
    mock_ncm.discover_all_natures.return_value = natures
    mock_ncm.get_status.return_value = {
        "version": "1.0.0",
        "natures": len(natures),
        "total_worms": sum(natures.values()),
    }

    def fake_execute_nature(nature, parallel=False):
        count = natures.get(nature, 2)
        return NatureResult(
            nature=nature,
            worm_results={f"worm_{i}": {"success": True, "method": "get_status"} for i in range(count)},
            success_count=count,
            failure_count=0,
            duration_ms=12.5,
            started_at="2025-01-01T00:00:00",
            completed_at="2025-01-01T00:00:01",
            cluster_id=f"nature_{nature}_test",
        )

    mock_ncm.execute_nature.side_effect = fake_execute_nature
    mock_ncm._score_natures.return_value = {n: float(i + 1) for i, n in enumerate(natures)}
    mock_ncm._diversity = None
    mock_ncm.to_mermaid.return_value = 'graph TB\n    test["test"]'
    mock_ncm.to_mermaid_functions.return_value = "classDiagram\n    %% test"
    return mock_ncm


def _make_mock_router():
    """Create a mock CrossNatureRoutingEngine."""
    mock_router = MagicMock()
    mock_router.routes = []
    mock_router.get_all_paths.return_value = {}
    mock_router.compute_routing_order.side_effect = lambda natures: natures
    mock_router.get_routes_to.return_value = []
    mock_router.route_nature_output.return_value = 0
    return mock_router


def _make_mc(natures=None):
    """Create a MetaCluster with mocked ncm and router.

    IMPORTANT: Lazy singletons (_get_pams, _get_config, etc.) are patched
    at the CLASS level in TestMetaCluster via setUp/tearDown, so they
    remain active for the entire test method. This function only handles
    NCM and router patching.
    """
    mock_ncm = _make_mock_ncm(natures)
    mock_router = _make_mock_router()

    with patch("CORE.WORMS.METACLUSTER.NatureClusterManager", return_value=mock_ncm), \
         patch("CORE.WORMS.METACLUSTER.CrossNatureRoutingEngine", return_value=mock_router):
        mc = MetaCluster()

    return mc


# ── Data types tests (no patches needed) ───────────────────────────

class TestMetaClusterResult(unittest.TestCase):
    def test_defaults(self):
        r = MetaClusterResult()
        self.assertEqual(r.orchestration_id, "")
        self.assertEqual(r.natures_executed, 0)
        self.assertEqual(r.total_worms_ok, 0)
        self.assertEqual(r.total_worms_fail, 0)
        self.assertEqual(r.nature_results, {})
        self.assertEqual(r.insights, [])
        self.assertEqual(r.errors, [])

    def test_fields(self):
        r = MetaClusterResult(
            orchestration_id="test_123",
            natures_executed=3,
            total_worms_ok=10,
            total_worms_fail=2,
        )
        self.assertEqual(r.orchestration_id, "test_123")
        self.assertEqual(r.natures_executed, 3)
        self.assertEqual(r.total_worms_ok, 10)
        self.assertEqual(r.total_worms_fail, 2)


class TestMetaClusterState(unittest.TestCase):
    def test_defaults(self):
        state = MetaClusterState()
        self.assertEqual(state.phase, "idle")
        self.assertEqual(state.active_natures, set())
        self.assertEqual(state.completed_natures, set())
        self.assertEqual(state.failed_natures, set())

    def test_thread_safety(self):
        state = MetaClusterState()
        def add_nature(n):
            with state.lock:
                state.active_natures.add(n)
        threads = [threading.Thread(target=add_nature, args=(f"n{i}",)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        self.assertEqual(len(state.active_natures), 20)

    def test_set_fields(self):
        state = MetaClusterState()
        state.phase = "executing"
        state.active_natures = {"security", "monitor"}
        state.completed_natures = {"security"}
        state.failed_natures = {"monitor"}
        self.assertEqual(state.phase, "executing")
        self.assertIn("security", state.active_natures)
        self.assertIn("security", state.completed_natures)
        self.assertIn("monitor", state.failed_natures)


# ── MetaCluster tests ──────────────────────────────────────────────

@patch("CORE.WORMS.METACLUSTER._get_log", return_value=None)
@patch("CORE.WORMS.METACLUSTER._get_breakers", return_value=None)
@patch("CORE.WORMS.METACLUSTER._get_config", return_value=None)
@patch("CORE.WORMS.METACLUSTER._get_mem_bus", return_value=None)
@patch("CORE.WORMS.METACLUSTER._get_pams", return_value=None)
class TestMetaCluster(unittest.TestCase):
    """All tests run with lazy singletons patched to prevent PamsRecorder
    DB connections, config file reads, breaker initialization, etc.
    The 5 @patch decorators above keep these mocks active for every method.
    """

    def test_init(self, *_):
        """MetaCluster init sets up hooks, history, and version."""
        mc = _make_mc()
        self.assertIsNotNone(mc.ncm)
        self.assertIsNotNone(mc.router)
        self.assertEqual(mc._history, [])
        self.assertEqual(mc.VERSION, "1.0.0")
        self.assertIsInstance(mc._hooks, dict)

    def test_discover_all(self, *_):
        mc = _make_mc()
        counts = mc.discover_all()
        self.assertGreater(len(counts), 0)
        self.assertGreater(sum(counts.values()), 0)
        self.assertEqual(counts["orchestration"], 2)
        self.assertEqual(counts["security"], 5)

    def test_orchestrate_single_nature(self, *_):
        mc = _make_mc()
        result = mc.orchestrate(natures=["orchestration"])
        self.assertIsInstance(result, MetaClusterResult)
        self.assertEqual(result.natures_executed, 1)
        self.assertGreater(result.duration_ms, 0)
        self.assertIsNotNone(result.orchestration_id)
        self.assertEqual(result.total_worms_ok, 2)
        self.assertEqual(result.total_worms_fail, 0)

    def test_orchestrate_multiple_natures(self, *_):
        mc = _make_mc()
        result = mc.orchestrate(natures=["orchestration", "monitor"])
        self.assertGreaterEqual(result.natures_executed, 1)
        # 2 orchestration + 3 monitor = 5 worms
        self.assertEqual(result.total_worms_ok, 5)

    def test_orchestrate_nature_convenience(self, *_):
        mc = _make_mc()
        result = mc.orchestrate_nature("security")
        self.assertIsInstance(result, MetaClusterResult)
        self.assertEqual(result.natures_executed, 1)
        self.assertEqual(result.total_worms_ok, 5)

    def test_orchestrate_adaptive(self, *_):
        mc = _make_mc()
        result = mc.orchestrate_adaptive(max_natures=2)
        self.assertIsInstance(result, MetaClusterResult)
        self.assertLessEqual(result.natures_executed, 2)

    def test_get_status(self, *_):
        mc = _make_mc()
        status = mc.get_status()
        self.assertIn("version", status)
        self.assertIn("ncm", status)
        self.assertIn("routing_paths", status)
        self.assertIn("free_threaded", status)
        self.assertEqual(status["version"], "1.0.0")

    def test_get_last_result_none(self, *_):
        mc = _make_mc()
        self.assertIsNone(mc.get_last_result())

    def test_get_last_result_after_orchestrate(self, *_):
        mc = _make_mc()
        result = mc.orchestrate(natures=["orchestration"])
        last = mc.get_last_result()
        self.assertIsNotNone(last)
        self.assertEqual(last.orchestration_id, result.orchestration_id)

    def test_hooks_pre_and_post(self, *_):
        mc = _make_mc()
        hook_called = []
        mc.on("pre_nature", lambda nature, state, **kw: hook_called.append(("pre", nature)))
        mc.on("post_nature", lambda nature, result, state, **kw: hook_called.append(("post", nature)))
        mc.orchestrate(natures=["orchestration"])
        pre_calls = [h for h in hook_called if h[0] == "pre"]
        post_calls = [h for h in hook_called if h[0] == "post"]
        self.assertGreater(len(pre_calls), 0)
        self.assertGreater(len(post_calls), 0)

    def test_hooks_insight(self, *_):
        mc = _make_mc(natures={"orchestration": 3, "monitor": 2})
        insights_received = []
        mc.on("on_insight", lambda insight, state, **kw: insights_received.append(insight))
        mc.orchestrate(natures=["orchestration", "monitor"])
        self.assertGreater(len(insights_received), 0)

    def test_hooks_error(self, *_):
        """Error hook fires when a nature execution raises."""
        mc = _make_mc(natures={"orchestration": 2})
        mc.ncm.execute_nature.side_effect = RuntimeError("test error")
        errors_received = []
        mc.on("on_error", lambda nature, error, state, **kw: errors_received.append((nature, error)))
        result = mc.orchestrate(natures=["orchestration"])
        self.assertGreater(len(errors_received), 0)
        self.assertIn("orchestration", mc.state.failed_natures)

    def test_history_limit(self, *_):
        mc = _make_mc()
        for i in range(105):
            mc._history.append(MetaClusterResult(orchestration_id=f"run_{i}"))
        self.assertEqual(len(mc._history), 105)
        mc.orchestrate(natures=["orchestration"])
        self.assertLessEqual(len(mc._history), 100)

    def test_to_mermaid(self, *_):
        mc = _make_mc()
        mermaid = mc.to_mermaid()
        self.assertIsInstance(mermaid, str)
        self.assertGreater(len(mermaid), 0)

    def test_to_mermaid_no_ncm(self, *_):
        """to_mermaid with no NCM returns error graph."""
        mc = _make_mc()
        mc.ncm = None
        mermaid = mc.to_mermaid()
        self.assertIn("not available", mermaid.lower())

    def test_to_mermaid_execution_flow_empty(self, *_):
        mc = _make_mc()
        flow = mc.to_mermaid_execution_flow()
        self.assertIn("No orchestration", flow)

    def test_to_mermaid_execution_flow_with_result(self, *_):
        mc = _make_mc()
        mc.orchestrate(natures=["orchestration"])
        flow = mc.to_mermaid_execution_flow()
        self.assertIn("graph LR", flow)

    def test_to_mermaid_routing_topology(self, *_):
        mc = _make_mc()
        topo = mc.to_mermaid_routing_topology()
        self.assertIn("graph TB", topo)

    def test_repr(self, *_):
        mc = _make_mc()
        r = repr(mc)
        self.assertIn("MetaCluster", r)
        self.assertIn("1.0.0", r)

    def test_state_lifecycle(self, *_):
        """Verify state transitions through orchestration."""
        mc = _make_mc()
        result = mc.orchestrate(natures=["orchestration"])
        self.assertIsNotNone(mc.state)
        self.assertEqual(mc.state.phase, "complete")
        self.assertIn("orchestration", mc.state.completed_natures)

    def test_insights_generation(self, *_):
        """Insights are generated from orchestration results."""
        mc = _make_mc(natures={"orchestration": 3, "security": 2})
        result = mc.orchestrate(natures=["orchestration", "security"])
        self.assertGreater(len(result.insights), 0)
        has_rate = any("success rate" in i.lower() for i in result.insights)
        self.assertTrue(has_rate)

    def test_recommendations_generation(self, *_):
        """Recommendations are generated for unused natures."""
        mc = _make_mc(natures={"orchestration": 2, "monitor": 3, "security": 5})
        result = mc.orchestrate(natures=["orchestration"])
        self.assertGreater(len(result.recommendations), 0)

    def test_no_ncm_returns_error(self, *_):
        """MetaCluster with no NCM returns error result."""
        mc = _make_mc()
        mc.ncm = None
        result = mc.orchestrate()
        self.assertIn("not available", result.errors[0])

    def test_on_invalid_hook(self, *_):
        """Registering an invalid hook name is a no-op."""
        mc = _make_mc()
        mc.on("nonexistent_hook", lambda: None)
        self.assertNotIn("nonexistent_hook", mc._hooks)

    def test_full_pipeline(self, *_):
        mc = _make_mc()
        result = mc.orchestrate_full_pipeline("security")
        self.assertIsInstance(result, MetaClusterResult)

    def test_export_state(self, *_):
        import tempfile, json
        mc = _make_mc()
        mc.orchestrate(natures=["orchestration"])
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            returned = mc.export_state(path)
            self.assertEqual(returned, path)
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(data["version"], "1.0.0")
            self.assertGreater(len(data["orchestration_history"]), 0)
        finally:
            os.unlink(path)

    def test_multiple_orchestrations(self, *_):
        """Multiple orchestrations accumulate in history."""
        mc = _make_mc()
        mc.orchestrate(natures=["orchestration"])
        mc.orchestrate(natures=["monitor"])
        mc.orchestrate(natures=["security"])
        self.assertEqual(len(mc._history), 3)
        self.assertEqual(mc._history[0].total_worms_ok, 2)
        self.assertEqual(mc._history[1].total_worms_ok, 3)
        self.assertEqual(mc._history[2].total_worms_ok, 5)

    def test_error_result_tracking(self, *_):
        """Errors from failed natures are captured in the result."""
        mc = _make_mc(natures={"orchestration": 2, "security": 3})

        def selective_fail(nature, parallel=False):
            if nature == "security":
                raise RuntimeError("security scan failed")
            return NatureResult(
                nature=nature,
                worm_results={f"worm_{i}": {"success": True} for i in range(2)},
                success_count=2,
                failure_count=0,
                duration_ms=10.0,
            )

        mc.ncm.execute_nature.side_effect = selective_fail
        result = mc.orchestrate(natures=["orchestration", "security"])
        self.assertGreater(len(result.errors), 0)
        self.assertIn("security", result.errors[0])
        self.assertEqual(result.total_worms_ok, 2)  # only orchestration succeeded

    def test_orchestrate_with_routing(self, *_):
        """Cross-nature routing data is tracked."""
        mc = _make_mc(natures={"security": 3, "defense": 2})
        # Configure router to report routing
        mc.router.route_nature_output.return_value = 1
        result = mc.orchestrate(natures=["security", "defense"])
        self.assertGreater(len(result.cross_nature_paths_used), 0)

    def test_to_mermaid_all_functions(self, *_):
        mc = _make_mc()
        mermaid = mc.to_mermaid_all_functions()
        self.assertIsInstance(mermaid, str)

    def test_orchestrate_auto_discover(self, *_):
        """Orchestrate with no natures auto-discovers."""
        mc = _make_mc()
        mc.ncm.clusters = {}
        # Make discover_all_natures populate clusters
        def fake_discover():
            mc.ncm.clusters = {"orchestration": MagicMock()}
            return {"orchestration": 2}
        mc.ncm.discover_all_natures.side_effect = fake_discover
        result = mc.orchestrate()
        # discover_all should have been called
        mc.ncm.discover_all_natures.assert_called()


if __name__ == "__main__":
    unittest.main()
