# coding: utf-8
"""Unit tests for NATURE_CLUSTERS.py — NatureCluster, NatureClusterManager.

Flags:
    Set AZAZAEL_TEST_QUICK=1 to skip slow worm execution tests.
    Runs only pure dataclass/config/definition tests (~18 tests).
"""

import sys
import os
from typing import Any
from pathlib import Path

_QUICK_MODE = os.environ.get("AZAZAEL_TEST_QUICK") == "1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ── Python 3.14t Free-Threading Guard (module level — before imports) ──
from _env_314t import setup_314t
setup_314t(mock_pams=False)

try:
    import pytest
except BaseException:
    import types
    pytest = types.ModuleType("pytest")
    pytest.skip = lambda reason=None: exec("raise type('Skip', (BaseException,), {})(reason or '')")
    pytest.mark = types.ModuleType("mark")
    pytest.mark.skip = lambda *a, **kw: lambda f: f

# ── Module Under Test ──────────────────────────────────────────────
from CORE.WORMS.NATURE_CLUSTERS import (
    # Data types
    NatureResult,
    CrossNatureRoute,
    # Core classes
    NatureCluster,
    NatureClusterManager,
    # Definitions
    NATURE_DEFINITIONS,
)


# ═══════════════════════════════════════════════════════════════════
# NatureResult Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureResult:
    """Verify NatureResult dataclass."""

    def test_minimal_result(self):
        """Minimal result should have defaults for optional fields."""
        result = NatureResult(nature="security")
        assert result.nature == "security"
        assert result.worm_results == {}
        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.duration_ms == 0.0
        assert result.errors == []
        assert result.insights == []

    def test_full_result(self):
        """Result with all fields populated."""
        result = NatureResult(
            nature="monitor",
            worm_results={"SYSTEMZ": {"success": True}},
            success_count=1,
            failure_count=0,
            duration_ms=250.5,
            cluster_id="cluster_abc",
            errors=[],
            insights=["All worms healthy"],
        )
        assert result.nature == "monitor"
        assert result.success_count == 1
        assert result.duration_ms == 250.5
        assert result.insights == ["All worms healthy"]


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoute Tests
# ═══════════════════════════════════════════════════════════════════


class TestCrossNatureRoute:
    """Verify CrossNatureRoute dataclass."""

    def test_minimal_route(self):
        """Minimal route should have defaults."""
        route = CrossNatureRoute(from_nature="security", to_nature="defense")
        assert route.from_nature == "security"
        assert route.to_nature == "defense"
        assert route.data_mapping == {}
        assert route.description == ""

    def test_full_route(self):
        """Route with all fields."""
        route = CrossNatureRoute(
            from_nature="profiling",
            to_nature="optimization",
            data_mapping={"bottleneck": "target"},
            description="Profiling results drive optimization",
        )
        assert route.data_mapping["bottleneck"] == "target"
        assert "Profiling" in route.description


# ═══════════════════════════════════════════════════════════════════
# NATURE_DEFINITIONS Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureDefinitions:
    """Verify NATURE_DEFINITIONS structure."""

    def test_has_essential_natures(self):
        """Core natures should be defined."""
        for nature in ("monitor", "security", "defense", "orchestration",
                       "diagnostic", "analysis", "profiling", "telemetry"):
            assert nature in NATURE_DEFINITIONS, f"Missing nature: {nature}"

    def test_each_nature_has_purpose(self):
        """Every nature should have a purpose."""
        for name, definition in NATURE_DEFINITIONS.items():
            assert "purpose" in definition, f"Missing purpose for {name}"
            assert len(definition["purpose"]) > 0

    def test_each_nature_has_triggers(self):
        """Every nature should have triggers."""
        for name, definition in NATURE_DEFINITIONS.items():
            assert "triggers" in definition, f"Missing triggers for {name}"

    def test_feeds_into_connectivity(self):
        """Feeds_into should reference valid natures."""
        for name, definition in NATURE_DEFINITIONS.items():
            for target in definition.get("feeds_into", []):
                assert target in NATURE_DEFINITIONS, \
                    f"Nature '{name}' feeds into '{target}' which doesn't exist"

    def test_no_self_reference(self):
        """No nature should feed into itself."""
        for name, definition in NATURE_DEFINITIONS.items():
            assert name not in definition.get("feeds_into", []), \
                f"Nature '{name}' feeds into itself"


# ═══════════════════════════════════════════════════════════════════
# NatureCluster Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterConstruction:
    """Verify NatureCluster construction and discovery."""

    def test_construction(self):
        """Construction should initialize with given nature."""
        cluster = NatureCluster("security")
        assert cluster.nature == "security"
        assert cluster.cluster_id.startswith("nature_security_")
        assert cluster.worms == {}
        assert cluster.instances == {}
        assert cluster.results == {}
        assert cluster.VERSION == "1.0.0"

    def test_get_status_before_discovery(self):
        """Status should work even before discovery."""
        cluster = NatureCluster("monitor")
        status = cluster.get_status()
        assert status["nature"] == "monitor"
        assert status["worm_count"] == 0
        assert status["version"] == "1.0.0"

    def test_set_parallel(self):
        """Setting parallel flag should work."""
        cluster = NatureCluster("security")
        assert cluster._parallel is False
        cluster.set_parallel(True)
        assert cluster._parallel is True

    def test_set_timeout(self):
        """Setting timeout should work."""
        cluster = NatureCluster("security")
        cluster.set_timeout(120)
        assert cluster._timeout == 120

    def test_discover_worms(self):
        """Discovery should find worms or return 0."""
        cluster = NatureCluster("security")
        count = cluster.discover_worms()
        assert isinstance(count, int)
        assert count >= 0

    def test_get_worm_info_structure(self):
        """Worm info list should have expected keys."""
        cluster = NatureCluster("security")
        cluster.discover_worms()
        info_list = cluster.get_worm_info()
        if info_list:
            info = info_list[0]
            assert "name" in info
            assert "priority" in info
            assert "description" in info
            assert "version" in info

    def test_execute_discovered_worms(self):
        """Executing discovered worms should not crash."""
        cluster = NatureCluster("security")
        cluster.discover_worms()
        # Some worms may fail due to dependencies, but should not crash
        result = cluster.execute()
        assert isinstance(result, NatureResult)
        assert result.nature == "security"
        assert result.success_count + result.failure_count >= 0


class TestNatureClusterMermaid:
    """Verify NatureCluster Mermaid generation."""

    def test_to_mermaid_structure(self):
        """Mermaid graph should have expected structure."""
        cluster = NatureCluster("security")
        cluster.discover_worms()
        mermaid = cluster.to_mermaid()
        assert isinstance(mermaid, str)
        assert "subgraph" in mermaid
        assert "security" in mermaid.lower()


# ═══════════════════════════════════════════════════════════════════
# NatureClusterManager Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterManager:
    """Verify NatureClusterManager orchestration."""

    def test_construction(self):
        """Construction should initialize empty state."""
        ncm = NatureClusterManager()
        assert ncm.clusters == {}
        assert ncm.VERSION == "1.0.0"
        assert ncm.get_status()["natures"] == 0

    def test_discover_all_natures(self):
        """Discovery should find natures or return empty."""
        ncm = NatureClusterManager()
        counts = ncm.discover_all_natures()
        assert isinstance(counts, dict)
        # May be empty if registry not available, but should not crash

    def test_get_cluster(self):
        """Getting a cluster should create it on demand."""
        ncm = NatureClusterManager()
        cluster = ncm.get_cluster("security")
        if cluster is not None:
            assert isinstance(cluster, NatureCluster)
            assert cluster.nature == "security"

    def test_execute_nature(self):
        """Executing a nature should return result or None."""
        ncm = NatureClusterManager()
        result = ncm.execute_nature("security")
        if result is not None:
            assert isinstance(result, NatureResult)
            assert result.nature == "security"

    def test_execute_nature_unknown(self):
        """Unknown nature should return None."""
        ncm = NatureClusterManager()
        result = ncm.execute_nature("__nonexistent__")
        assert result is None

    def test_list_all_worms_structure(self):
        """Listing worms should return {nature: [worm_names]}."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        listing = ncm.list_all_worms()
        assert isinstance(listing, dict)
        for nature, worms in listing.items():
            assert isinstance(worms, list)
            assert len(worms) > 0

    def test_get_cross_nature_routes(self):
        """Cross-nature routes should be derived from definitions."""
        ncm = NatureClusterManager()
        routes = ncm.get_cross_nature_routes()
        assert isinstance(routes, list)
        if routes:
            route = routes[0]
            assert isinstance(route, CrossNatureRoute)
            assert route.from_nature in NATURE_DEFINITIONS
            assert route.to_nature in NATURE_DEFINITIONS


class TestNatureClusterManagerStatus:
    """Verify NatureClusterManager status reporting."""

    def test_get_status_structure(self):
        """Status should have expected fields."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        status = ncm.get_status()
        assert "version" in status
        assert "natures" in status
        assert "total_worms" in status
        assert "natures_list" in status
        assert "execution_history_count" in status
        assert "cross_nature_routes" in status
        assert "free_threaded" in status

    def test_execute_all_natures(self):
        """Executing all natures should return results dict."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        results = ncm.execute_all_natures()
        assert isinstance(results, dict)


class TestNatureClusterManagerMermaid:
    """Verify NatureClusterManager Mermaid generation."""

    def test_to_mermaid_structure(self):
        """Full Mermaid graph should have expected elements."""
        ncm = NatureClusterManager()
        ncm.discover_all_natures()
        mermaid = ncm.to_mermaid(include_routes=True)
        assert isinstance(mermaid, str)
        assert "graph TB" in mermaid or "graph" in mermaid


# ═══════════════════════════════════════════════════════════════════
# NatureClusterManager._score_natures() Scoring Tests
# ═══════════════════════════════════════════════════════════════════


class TestNatureScoring:
    """Verify NatureClusterManager._score_natures() priority scoring.

    Uses synthetic clusters and a stubbed psutil so every branch is
    deterministic — no live system state, no registry dependency.
    """

    # -- helpers (not collected as tests) -------------------------
    def _make_manager(self, worm_counts):
        """Build a manager with empty synthetic clusters by worm count."""
        ncm = NatureClusterManager()
        ncm._diversity = None
        ncm.clusters = {}
        for nature, count in worm_counts.items():
            cluster = NatureCluster(nature)
            for i in range(count):
                cluster.worms["WORM_%d" % i] = type("WORM_%d" % i, (), {})
            ncm.clusters[nature] = cluster
        return ncm

    def _patch_psutil(self, cpu=50.0, mem=50.0):
        """Stub psutil CPU/mem so scoring is independent of live state."""
        import psutil
        self._real_cpu = psutil.cpu_percent
        self._real_mem = psutil.virtual_memory

        class _Mem:
            percent = mem

        psutil.cpu_percent = lambda interval=0.5: cpu
        psutil.virtual_memory = lambda: _Mem()
        return self._restore_psutil

    def _restore_psutil(self):
        """Restore the real psutil functions after a test."""
        import psutil
        psutil.cpu_percent = self._real_cpu
        psutil.virtual_memory = self._real_mem

    def _append_history(self, ncm, nature, failures, when_ago):
        """Append an execution-history entry at a fixed relative age."""
        from datetime import datetime, timedelta
        ncm._execution_history.append({
            "nature": nature,
            "success": 0,
            "failures": failures,
            "duration_ms": 0.0,
            "timestamp": (datetime.now() - timedelta(seconds=when_ago)).isoformat(),
        })

    # -- tests -----------------------------------------------------
    def test_basic_scores_worm_bonus(self):
        """Score = base 5 + capped worm-count bonus at nominal load."""
        ncm = self._make_manager({
            "security": 4,
            "monitor": 2,
            "optimization": 1,
        })
        restore = self._patch_psutil(cpu=50.0, mem=50.0)
        try:
            scores = ncm._score_natures()
        finally:
            restore()
        # base 5.0 + min(count * 0.5, 3.0)
        assert scores["security"] == 7.0
        assert scores["monitor"] == 6.0
        assert scores["optimization"] == 5.5

    def test_cpu_boost(self):
        """High CPU boosts monitor/profiling (+15) and optimization (+8)."""
        ncm = self._make_manager({
            "monitor": 0, "profiling": 0,
            "optimization": 0, "security": 0,
        })
        restore = self._patch_psutil(cpu=90.0, mem=50.0)
        try:
            scores = ncm._score_natures()
        finally:
            restore()
        assert scores["monitor"] == 20.0
        assert scores["profiling"] == 20.0
        assert scores["optimization"] == 13.0
        assert scores["security"] == 5.0

    def test_mem_boost(self):
        """High memory boosts monitor and optimization (+10)."""
        ncm = self._make_manager({"monitor": 0, "optimization": 0, "security": 0})
        restore = self._patch_psutil(cpu=50.0, mem=90.0)
        try:
            scores = ncm._score_natures()
        finally:
            restore()
        assert scores["monitor"] == 15.0
        assert scores["optimization"] == 15.0
        assert scores["security"] == 5.0

    def test_error_driven_boost(self):
        """3+ recent failures add +12; stale adds +5; defense adds +5 more."""
        ncm = self._make_manager({"security": 0, "defense": 0})
        # 7 filler rows then 3 security + 3 defense rows, so the last-10
        # window contains all 6 failure rows for both natures.
        for _ in range(7):
            self._append_history(ncm, "monitor", failures=0, when_ago=7200)
        for _ in range(3):
            self._append_history(ncm, "security", failures=1, when_ago=3600)
        for _ in range(3):
            self._append_history(ncm, "defense", failures=1, when_ago=3600)
        restore = self._patch_psutil(cpu=50.0, mem=50.0)
        try:
            scores = ncm._score_natures()
        finally:
            restore()
        # security: 5 + 12 (errors) + 5 (stale)
        assert scores["security"] == 22.0
        # defense: ... + 5 defensive-attention bonus
        assert scores["defense"] == 27.0

    def test_recency_penalty(self):
        """Recent execution (<60s) subtracts 5."""
        ncm = self._make_manager({"security": 0})
        restore = self._patch_psutil(cpu=50.0, mem=50.0)
        try:
            self._append_history(ncm, "security", failures=0, when_ago=10)
            scores = ncm._score_natures()
        finally:
            restore()
        assert scores["security"] == 0.0

    def test_staleness_boost(self):
        """Long-unexecuted nature (>600s) adds 5."""
        ncm = self._make_manager({"security": 0})
        restore = self._patch_psutil(cpu=50.0, mem=50.0)
        try:
            self._append_history(ncm, "security", failures=0, when_ago=3600)
            scores = ncm._score_natures()
        finally:
            restore()
        assert scores["security"] == 10.0


# ═══════════════════════════════════════════════════════════════════
# NatureClusterManager.execute_priority_natures() Tests
# ═══════════════════════════════════════════════════════════════════


class TestNaturePriorityExecution:
    """Verify execute_priority_natures() top-N selection logic.

    Scoring and worm execution are stubbed so only the selection /
    iteration contract is exercised deterministically.
    """

    def _make_manager(self):
        ncm = NatureClusterManager()
        ncm._diversity = None
        ncm.clusters = {}
        return ncm

    def test_selects_top_scores(self):
        """Should execute natures in descending score order, capped at max."""
        ncm = self._make_manager()
        ncm._score_natures = lambda: {"a": 10.0, "b": 7.5, "c": 3.0, "d": 1.0}
        executed = []
        ncm.execute_nature = lambda n: executed.append(n) or NatureResult(nature=n)
        results = ncm.execute_priority_natures(max_natures=2)
        assert executed == ["a", "b"]
        assert set(results) == {"a", "b"}

    def test_max_natures_caps(self):
        """max_natures limits how many natures run."""
        ncm = self._make_manager()
        ncm._score_natures = lambda: {"a": 5.0, "b": 4.0, "c": 3.0}
        ncm.execute_nature = lambda n: NatureResult(nature=n)
        results = ncm.execute_priority_natures(max_natures=1)
        assert list(results) == ["a"]

    def test_skips_none_results(self):
        """Natures whose execution returns None are omitted."""
        ncm = self._make_manager()
        ncm._score_natures = lambda: {"a": 9.0, "b": 8.0}
        ncm.execute_nature = lambda n: None
        assert ncm.execute_priority_natures(max_natures=3) == {}

    def test_empty_scores(self):
        """Empty scoring returns an empty result dict."""
        ncm = self._make_manager()
        ncm._score_natures = lambda: {}
        ncm.execute_nature = lambda n: NatureResult(nature=n)
        assert ncm.execute_priority_natures() == {}


# ── Quick-mode skips: worm execution tests that time out under 3.14t ──
_QUICK_SKIPS = {
    "TestNatureClusterConstruction.test_execute_discovered_worms",
    "TestNatureClusterManager.test_discover_all_natures",
    "TestNatureClusterManager.test_execute_nature",
    "TestNatureClusterManager.test_list_all_worms_structure",
    "TestNatureClusterManagerStatus.test_execute_all_natures",
    "TestNatureDiscoveryEdgeCases.test_discover_all_natures_repeatable",
    "TestNatureDiscoveryEdgeCases.test_manager_status_after_execution",
}

if __name__ == "__main__":
    p = f = s = 0
    for name, obj in list(globals().items()):
        if isinstance(obj, type) and name.startswith("Test"):
            inst = obj()
            for mn in dir(inst):
                if mn.startswith("test_"):
                    test_key = f"{name}.{mn}"
                    if _QUICK_MODE and test_key in _QUICK_SKIPS:
                        print(f"  [SKIP] {test_key} (quick mode)")
                        s += 1
                        continue
                    try:
                        getattr(inst, mn)()
                        print(f"  [OK] {test_key}")
                        p += 1
                    except Exception as e:
                        print(f"  [FAIL] {test_key}: {e}")
                        f += 1
    print(f"  Passed: {p}, Failed: {f}, Skipped: {s}")
