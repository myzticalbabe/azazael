# coding: utf-8
"""Unit tests for NATURE_CLUSTERS category discovery and the METACLUSTER
routing engine (CrossNatureRoutingEngine).

Coverage:
  - NATURE_DEFINITIONS structure validation (18 Natures, feeds_into integrity)
  - NatureCluster.discover_worms() — registry-based category discovery,
    class filtering, dedup on repeat calls
  - NatureClusterManager.discover_all_natures() / get_cluster() /
    list_all_worms() / get_worm_info() — category grouping and metadata
  - NatureCluster execution: priority ordering, subset execution, DLQ
    dead-letter recording for failures
  - Cross-nature static routes and route_results() data mapping
  - CrossNatureRoutingEngine: route construction, from/to lookups,
    route_nature_output, compute_routing_order (topological), cycle
    detection, shortest_path, optimize_pipeline, get_all_paths
  - analyze_routing() static fallback when inference is unavailable
  - MetaClusterState dataclass defaults
  - MetaCluster.orchestrate() with a stubbed NatureClusterManager:
    state transitions, routing activation, insights, recommendations, hooks

All infra (PAMS, MemoryBus, loggers, breakers, registry discovery) is
patched out so tests are hermetic and fast.
"""

import sys
import os
import time
from dataclasses import dataclass
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# ── Modules Under Test ────────────────────────────────────────────
import CORE.WORMS.NATURE_CLUSTERS as NC          # the OBJECT the imports below bind

from CORE.WORMS.NATURE_CLUSTERS import (
    NatureCluster,
    NatureClusterManager,
    NatureResult,
    NATURE_DEFINITIONS,
    CrossNatureRoute,
    WORM_REGISTRY,
)
from CORE.WORMS.CROSS_NATURE_ROUTER import CrossNatureRoutingEngine
from CORE.WORMS.METACLUSTER import (
    MetaCluster,
    MetaClusterState,
    MetaClusterResult,
)

# ── Mock Worms ─────────────────────────────────────────────────────

@dataclass
class _Payload:
    value: int = 7


class _MockWormOK:
    """Mock worm with a standard method that succeeds."""

    VERSION = "1.0.0"

    def get_summary(self):
        return {"status": "ok"}


class _MockWormFail:
    """Mock worm whose method raises."""

    VERSION = "1.0.0"

    def get_summary(self):
        raise RuntimeError("mock worm exploded")


class _MockWormDataclass:
    """Mock worm returning a dataclass payload."""

    VERSION = "1.0.0"

    def get_summary(self):
        return _Payload(value=42)


class _MockWormRun:
    """Mock worm exposing only 'run' (later in method priority order)."""

    VERSION = "1.0.0"

    def run(self):
        return {"ran": True}


# ═══════════════════════════════════════════════════════════════════
# NATURE_DEFINITIONS Structure
# ═══════════════════════════════════════════════════════════════════


class TestNatureDefinitions:
    """Verify NATURE_DEFINITIONS integrity."""

    def test_has_all_expected_natures(self):
        """The 18 documented Natures should all be defined."""
        for nature in ("monitor", "diagnostic", "analysis", "defense",
                       "optimization", "orchestration", "sync", "repair",
                       "security", "profiling", "telemetry", "container",
                       "config", "backup", "migration", "communication",
                       "learning", "visualization"):
            assert nature in NATURE_DEFINITIONS, f"Missing Nature: {nature}"

    def test_each_definition_has_required_keys(self):
        """Every Nature definition needs purpose/triggers/feeds_into/icon."""
        for nature, definition in NATURE_DEFINITIONS.items():
            for key in ("purpose", "triggers", "feeds_into", "icon"):
                assert key in definition, f"{nature}: missing '{key}'"

    def test_feeds_into_targets_are_known_natures(self):
        """Every feeds_into target must itself be a defined Nature."""
        for nature, definition in NATURE_DEFINITIONS.items():
            for target in definition.get("feeds_into", []):
                assert target in NATURE_DEFINITIONS, \
                    f"{nature} feeds into unknown Nature '{target}'"

    def test_icons_unique_per_nature(self):
        """Each Nature should have a distinct icon."""
        icons = [d["icon"] for d in NATURE_DEFINITIONS.values()]
        assert len(set(icons)) == len(icons), "Duplicate Nature icons"


# ═══════════════════════════════════════════════════════════════════
# NatureCluster.discover_worms() — Category Discovery
# ═══════════════════════════════════════════════════════════════════


def _patch_registry_discovery(get_worms=None, categories=None):
    """Patch module-level registry functions for hermetic discovery tests.

    Patched through the module OBJECT this file imported, not by name. A string
    target is resolved against `sys.modules` at patch time, and this module is a
    WORM HOST — so `worm_registry.reset_registry()` re-imports it and the name
    then resolves to a different object than the one whose classes this file
    holds. Measured 2026-09-22: with a string target the patch landed on the
    re-imported module, the classes under test fell through to the REAL
    `get_worms_by_category`, and 13 tests failed in-suite (74 passed alone) with
    counts of 25 instead of 2. `CORE.WORMS.NATURE_CLUSTERS` is the same object
    the `from ... import` above bound, so `mock.patch.object` cannot drift.
    """
    patchers = [
        mock.patch.object(NC, "discover_worms", return_value=0),
        mock.patch.object(NC, "get_worms_by_category",
                          side_effect=get_worms if get_worms else (lambda c: {})),
        mock.patch.object(NC, "get_all_categories",
                          return_value=categories if categories is not None else set()),
        mock.patch.object(NC, "mark_spawned"),
        mock.patch.object(NC, "_get_pams", return_value=None),
        mock.patch.object(NC, "_get_breakers", return_value=None),
        mock.patch.object(NC, "_get_config", return_value=None),
        mock.patch.object(NC, "_get_log", return_value=None),
    ]
    for p in patchers:
        p.start()
    return patchers


def _stop_patchers(patchers):
    for p in patchers:
        p.stop()


class TestNatureClusterDiscovery:
    """Verify NatureCluster.discover_worms() registry discovery."""

    def test_discovers_worms_from_category(self):
        """Worms with a class in the registry should be added."""
        patchers = _patch_registry_discovery(get_worms=lambda c: {
            "MockA": {"class": _MockWormOK, "category": c},
            "MockB": {"class": _MockWormRun, "category": c},
        })
        try:
            cluster = NatureCluster("security")
            count = cluster.discover_worms()
            assert count == 2
            assert "MockA" in cluster.worms
            assert "MockB" in cluster.worms
            assert cluster.worms["MockA"] is _MockWormOK
        finally:
            _stop_patchers(patchers)

    def test_skips_non_class_entries(self):
        """Registry entries without a class should be skipped."""
        patchers = _patch_registry_discovery(get_worms=lambda c: {
            "MockClass": {"class": _MockWormOK, "category": c},
            "MockNotClass": {"class": "not-a-class", "category": c},
            "MockNoClass": {"category": c},
        })
        try:
            cluster = NatureCluster("defense")
            count = cluster.discover_worms()
            assert count == 1
            assert "MockClass" in cluster.worms
            assert "MockNotClass" not in cluster.worms
            assert "MockNoClass" not in cluster.worms
        finally:
            _stop_patchers(patchers)

    def test_empty_category_returns_zero(self):
        """A category with no worms should return 0 and stay empty."""
        patchers = _patch_registry_discovery(get_worms=lambda c: {})
        try:
            cluster = NatureCluster("migration")
            count = cluster.discover_worms()
            assert count == 0
            assert cluster.worms == {}
        finally:
            _stop_patchers(patchers)

    def test_discover_is_idempotent(self):
        """Second discovery call must not duplicate existing worms."""
        patchers = _patch_registry_discovery(get_worms=lambda c: {
            "MockA": {"class": _MockWormOK, "category": c},
        })
        try:
            cluster = NatureCluster("telemetry")
            first = cluster.discover_worms()
            second = cluster.discover_worms()
            assert first == 1
            assert second == 1
            assert len(cluster.worms) == 1
            assert "MockA" in cluster.worms
        finally:
            _stop_patchers(patchers)

    def test_add_worm_manual(self):
        """Manually added worms should appear in the cluster."""
        cluster = NatureCluster("analysis")
        cluster.add_worm_manual("ManualWorm", _MockWormOK)
        assert "ManualWorm" in cluster.worms
        assert cluster.worms["ManualWorm"] is _MockWormOK


# ═══════════════════════════════════════════════════════════════════
# NatureClusterManager — Category Discovery & Grouping
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterManagerDiscovery:
    """Verify NatureClusterManager.discover_all_natures() grouping."""

    def _build_manager(self, category_worms):
        """Return (manager, patchers) with registry patched per category."""
        patchers = _patch_registry_discovery(
            get_worms=lambda c: category_worms.get(c, {}),
            categories=set(category_worms.keys()),
        )
        patchers.append(mock.patch(
            "CORE.WORMS.NATURE_CLUSTERS.SpawnDiversityEngine", None))
        manager = NatureClusterManager()
        return manager, patchers

    def test_discover_all_natures_groups_by_category(self):
        """Worms should be grouped into one cluster per category."""
        category_worms = {
            "security": {"VulnScanner": {"class": _MockWormOK, "category": "security"}},
            "monitor": {"SystemZ": {"class": _MockWormRun, "category": "monitor"}},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            counts = manager.discover_all_natures()
            assert counts == {"security": 1, "monitor": 1}
            assert set(manager.clusters.keys()) == {"security", "monitor"}
            assert "VulnScanner" in manager.clusters["security"].worms
            assert "SystemZ" in manager.clusters["monitor"].worms
        finally:
            _stop_patchers(patchers)

    def test_discover_all_natures_skips_empty_categories(self):
        """Categories with zero worms should not become clusters."""
        category_worms = {
            "security": {"VulnScanner": {"class": _MockWormOK, "category": "security"}},
            "empty_nature": {},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            counts = manager.discover_all_natures()
            assert counts == {"security": 1}
            assert "empty_nature" not in manager.clusters
        finally:
            _stop_patchers(patchers)

    def test_discover_all_natures_reuses_clusters(self):
        """Repeated discovery should reuse clusters (no worm duplication)."""
        category_worms = {
            "security": {"VulnScanner": {"class": _MockWormOK, "category": "security"}},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            first = manager.discover_all_natures()
            second = manager.discover_all_natures()
            assert first == second == {"security": 1}
            assert len(manager.clusters["security"].worms) == 1
        finally:
            _stop_patchers(patchers)

    def test_get_cluster_returns_existing(self):
        """get_cluster should return the same instance for an existing Nature."""
        category_worms = {
            "security": {"VulnScanner": {"class": _MockWormOK, "category": "security"}},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            manager.discover_all_natures()
            c1 = manager.get_cluster("security")
            c2 = manager.get_cluster("security")
            assert c1 is c2
            assert c1.nature == "security"
        finally:
            _stop_patchers(patchers)

    def test_get_cluster_creates_on_demand(self):
        """get_cluster should discover a Nature not yet clustered."""
        category_worms = {
            "defense": {"FirewallAudit": {"class": _MockWormOK, "category": "defense"}},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            cluster = manager.get_cluster("defense")
            assert cluster is not None
            assert cluster.nature == "defense"
            assert "FirewallAudit" in cluster.worms
        finally:
            _stop_patchers(patchers)

    def test_get_cluster_empty_returns_none(self):
        """get_cluster for an empty Nature should return None."""
        manager, patchers = self._build_manager({})
        try:
            cluster = manager.get_cluster("nowhere")
            assert cluster is None
        finally:
            _stop_patchers(patchers)

    def test_list_all_worms_groups_sorted(self):
        """list_all_worms should return {nature: sorted worm names}."""
        category_worms = {
            "security": {
                "Zulu": {"class": _MockWormOK, "category": "security"},
                "Alpha": {"class": _MockWormRun, "category": "security"},
            },
            "monitor": {"SystemZ": {"class": _MockWormOK, "category": "monitor"}},
        }
        manager, patchers = self._build_manager(category_worms)
        try:
            manager.discover_all_natures()
            listing = manager.list_all_worms()
            assert listing["security"] == ["Alpha", "Zulu"]
            assert listing["monitor"] == ["SystemZ"]
        finally:
            _stop_patchers(patchers)

    def test_get_worm_info_reads_registry_metadata(self):
        """get_worm_info should surface registry priority/description/spawn count."""
        patchers = _patch_registry_discovery(get_worms=lambda c: {
            "MockA": {"class": _MockWormOK, "category": c},
        })
        try:
            cluster = NatureCluster("security")
            cluster.discover_worms()
            # Inject registry metadata for the discovered worm
            saved = WORM_REGISTRY.get("MockA")
            WORM_REGISTRY["MockA"] = {
                "priority": 9,
                "cooldown_seconds": 5.0,
                "description": "mock scanner",
                "spawn_count": 3,
                "source_file": "mock.py",
            }
            try:
                info = cluster.get_worm_info()
                assert len(info) == 1
                entry = info[0]
                assert entry["name"] == "MockA"
                assert entry["priority"] == 9
                assert entry["cooldown_seconds"] == 5.0
                assert entry["description"] == "mock scanner"
                assert entry["spawn_count"] == 3
                assert entry["source_file"] == "mock.py"
            finally:
                if saved is None:
                    WORM_REGISTRY.pop("MockA", None)
                else:
                    WORM_REGISTRY["MockA"] = saved
        finally:
            _stop_patchers(patchers)


# ═══════════════════════════════════════════════════════════════════
# NatureCluster Execution — Priority Ordering, Subsets, DLQ
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterExecution:
    """Verify NatureCluster.execute() behavior."""

    def test_execute_runs_all_worms(self):
        """Sequential execution should return per-worm results and counts."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("security")
            cluster.add_worm_manual("OK", _MockWormOK)
            cluster.add_worm_manual("RUN", _MockWormRun)
            result = cluster.execute()
            assert isinstance(result, NatureResult)
            assert result.nature == "security"
            assert result.success_count == 2
            assert result.failure_count == 0
            assert set(result.worm_results.keys()) == {"OK", "RUN"}
            assert result.duration_ms >= 0
        finally:
            _stop_patchers(patchers)

    def test_execute_subset_by_names(self):
        """execute(worm_names=[...]) should run only the requested worms."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("security")
            cluster.add_worm_manual("A", _MockWormOK)
            cluster.add_worm_manual("B", _MockWormOK)
            result = cluster.execute(worm_names=["A"])
            assert list(result.worm_results.keys()) == ["A"]
            assert result.success_count == 1
        finally:
            _stop_patchers(patchers)

    def test_execute_orders_by_registry_priority(self):
        """Worms should execute in descending registry priority order."""
        patchers = _patch_registry_discovery()
        saved_a = WORM_REGISTRY.get("LowPrio")
        saved_b = WORM_REGISTRY.get("HighPrio")
        WORM_REGISTRY["LowPrio"] = {"priority": 1}
        WORM_REGISTRY["HighPrio"] = {"priority": 9}
        try:
            cluster = NatureCluster("security")
            cluster.add_worm_manual("LowPrio", _MockWormOK)
            cluster.add_worm_manual("HighPrio", _MockWormOK)
            result = cluster.execute()
            keys = list(result.worm_results.keys())
            assert keys == ["HighPrio", "LowPrio"], f"Order was {keys}"
        finally:
            for name, saved in (("LowPrio", saved_a), ("HighPrio", saved_b)):
                if saved is None:
                    WORM_REGISTRY.pop(name, None)
                else:
                    WORM_REGISTRY[name] = saved
            _stop_patchers(patchers)

    def test_execute_records_failure_to_dead_letter(self):
        """A failing worm should be counted and recorded in the DLQ."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("defense")
            cluster.add_worm_manual("OK", _MockWormOK)
            cluster.add_worm_manual("BAD", _MockWormFail)
            result = cluster.execute()
            assert result.success_count == 1
            assert result.failure_count == 1
            assert len(result.errors) == 1
            assert "mock worm exploded" in result.errors[0]
            failures = cluster.get_failed_executions()
            assert len(failures) == 1
            assert failures[0]["worm"] == "BAD"
        finally:
            _stop_patchers(patchers)

    def test_parallel_execution_matches_sequential_counts(self):
        """Parallel execution should produce the same aggregate counts."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("telemetry")
            cluster.add_worm_manual("A", _MockWormOK)
            cluster.add_worm_manual("B", _MockWormRun)
            cluster.add_worm_manual("C", _MockWormDataclass)
            cluster.set_parallel(True)
            cluster.set_timeout(5)
            result = cluster.execute()
            assert result.success_count == 3
            assert result.failure_count == 0
            assert len(result.worm_results) == 3
        finally:
            _stop_patchers(patchers)

    def test_dataclass_result_converted(self):
        """A dataclass worm result should be converted to a dict."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("learning")
            cluster.add_worm_manual("DC", _MockWormDataclass)
            result = cluster.execute()
            wr = result.worm_results["DC"]
            assert wr["success"] is True
            assert wr["result"] == {"value": 42}
        finally:
            _stop_patchers(patchers)

    def test_get_status_reports_cluster(self):
        """get_status should report nature, worm names, and execution info."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("security")
            cluster.add_worm_manual("A", _MockWormOK)
            status = cluster.get_status()
            assert status["nature"] == "security"
            assert status["worm_names"] == ["A"]
            assert status["worm_count"] == 1
            assert status["version"] == "1.0.0"
            assert status["parallel"] is False
        finally:
            _stop_patchers(patchers)


# ═══════════════════════════════════════════════════════════════════
# Dead Letter Queue — Record / Query / Retry / Clear
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterDeadLetter:
    """Verify DLQ recording, retry, and clear semantics."""

    def test_retry_failed_worms_success(self):
        """A worm fixed to succeed should be retried and removed from DLQ."""
        patchers = _patch_registry_discovery()
        try:
            calls = {"n": 0}

            class _Flaky:
                VERSION = "1.0.0"

                def get_summary(self):
                    calls["n"] += 1
                    if calls["n"] < 2:
                        raise RuntimeError("first attempt fails")
                    return {"ok": True}

            cluster = NatureCluster("repair")
            cluster.add_worm_manual("Flaky", _Flaky)
            result = cluster.execute()
            assert result.failure_count == 1
            assert len(cluster.get_failed_executions()) == 1

            retry = cluster.retry_failed_worms(max_retries=2)
            assert retry["retried"] == 1
            assert retry["succeeded"] == 1
            assert retry["still_failed"] == 0
            assert cluster.get_failed_executions() == []
        finally:
            _stop_patchers(patchers)

    def test_retry_failed_worms_still_failing(self):
        """A persistently failing worm should remain in the DLQ.

        Note: each retry attempt records a new failure (observability
        design), so the DLQ grows beyond the original single entry.
        """
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("repair")
            cluster.add_worm_manual("BAD", _MockWormFail)
            cluster.execute()
            retry = cluster.retry_failed_worms(max_retries=1)
            assert retry["retried"] == 1
            assert retry["succeeded"] == 0
            assert retry["still_failed"] == 1
            # original failure + 2 retry attempts all recorded
            assert len(cluster.get_failed_executions()) == 3
        finally:
            _stop_patchers(patchers)

    def test_clear_failed_executions(self):
        """clear_failed_executions should empty the DLQ."""
        patchers = _patch_registry_discovery()
        try:
            cluster = NatureCluster("repair")
            cluster.add_worm_manual("BAD", _MockWormFail)
            cluster.execute()
            assert len(cluster.get_failed_executions()) == 1
            cluster.clear_failed_executions()
            assert cluster.get_failed_executions() == []
        finally:
            _stop_patchers(patchers)

    def test_manager_dead_letter_summary_aggregates(self):
        """Manager summary should aggregate DLQs across clusters."""
        patchers = _patch_registry_discovery()
        try:
            manager = NatureClusterManager()
            c1 = NatureCluster("defense")
            c1.add_worm_manual("BAD", _MockWormFail)
            c1.execute()
            manager.clusters["defense"] = c1

            summary = manager.get_dead_letter_summary(lookback_seconds=3600)
            assert summary["total_failed"] == 1
            assert summary["affected_natures"] == 1
            assert summary["per_nature"] == {"defense": 1}
            assert summary["per_worm"].get("BAD") == 1
            assert len(summary["recent_errors"]) == 1
        finally:
            _stop_patchers(patchers)

    def test_manager_retry_all_failed_worms(self):
        """retry_all_failed_worms should delegate to each cluster."""
        patchers = _patch_registry_discovery()
        try:
            manager = NatureClusterManager()
            c1 = NatureCluster("defense")
            c1.add_worm_manual("BAD", _MockWormFail)
            c1.execute()
            manager.clusters["defense"] = c1

            results = manager.retry_all_failed_worms(max_retries=1)
            assert results["total_retried"] == 1
            assert results["total_succeeded"] == 0
            assert results["still_failed"] == 1
            assert "defense" in results["per_nature"]
        finally:
            _stop_patchers(patchers)


# ═══════════════════════════════════════════════════════════════════
# Cross-Nature Static Routes (manager-level)
# ═══════════════════════════════════════════════════════════════════


class TestNatureClusterManagerRoutes:
    """Verify get_cross_nature_routes() and route_results()."""

    def test_routes_built_from_feeds_into(self):
        """Every feeds_into entry should produce one CrossNatureRoute."""
        manager = NatureClusterManager()
        routes = manager.get_cross_nature_routes()
        expected = sum(len(d["feeds_into"]) for d in NATURE_DEFINITIONS.values())
        assert len(routes) == expected
        for route in routes:
            assert isinstance(route, CrossNatureRoute)
            assert route.from_nature in NATURE_DEFINITIONS
            assert route.to_nature in NATURE_DEFINITIONS

    def test_routes_are_ordered_by_definition(self):
        """Routes should iterate Natures in definition order."""
        manager = NatureClusterManager()
        routes = manager.get_cross_nature_routes()
        # First routes belong to the first Nature ("monitor")
        assert routes[0].from_nature == "monitor"

    def test_route_results_maps_data(self):
        """route_results should map worm results from source to target."""
        manager = NatureClusterManager()
        source = NatureResult(
            nature="security",
            worm_results={
                "VulnScanner": {"success": True, "result": {"ports": [80]}},
                "PortAuditor": {"success": True, "result": {"open": 443}},
            },
        )
        route = CrossNatureRoute(from_nature="security", to_nature="defense")
        routed = manager.route_results({"security": source}, route)
        assert routed["from"] == "security"
        assert routed["to"] == "defense"
        assert routed["data"]["VulnScanner"] == {"ports": [80]}
        assert routed["data"]["PortAuditor"] == {"open": 443}

    def test_route_results_missing_source(self):
        """route_results with no source result should return empty data."""
        manager = NatureClusterManager()
        route = CrossNatureRoute(from_nature="security", to_nature="defense")
        routed = manager.route_results({}, route)
        assert routed["data"] == {}


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine — Route Construction & Lookups
# ═══════════════════════════════════════════════════════════════════


class TestRoutingEngineRoutes:
    """Verify route construction and from/to lookups."""

    def test_routes_built_from_definitions(self):
        """Engine routes should mirror NATURE_DEFINITIONS feeds_into."""
        engine = CrossNatureRoutingEngine()
        expected = sum(len(d["feeds_into"]) for d in NATURE_DEFINITIONS.values())
        assert len(engine.routes) == expected

    def test_get_routes_from(self):
        """get_routes_from should return only routes originating there."""
        engine = CrossNatureRoutingEngine()
        security_routes = engine.get_routes_from("security")
        assert len(security_routes) > 0
        for route in security_routes:
            assert route.from_nature == "security"
        targets = {r.to_nature for r in security_routes}
        assert targets == set(NATURE_DEFINITIONS["security"]["feeds_into"])

    def test_get_routes_to(self):
        """get_routes_to should return only routes targeting that Nature."""
        engine = CrossNatureRoutingEngine()
        defense_routes = engine.get_routes_to("defense")
        assert len(defense_routes) > 0
        for route in defense_routes:
            assert route.to_nature == "defense"

    def test_get_routes_unknown_nature(self):
        """Unknown Natures should return empty route lists."""
        engine = CrossNatureRoutingEngine()
        assert engine.get_routes_from("nowhere") == []
        assert engine.get_routes_to("nowhere") == []


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine — route_nature_output
# ═══════════════════════════════════════════════════════════════════


class TestRoutingEngineRouteOutput:
    """Verify route_nature_output() message routing."""

    def _fresh_state(self):
        return MetaClusterState(run_id="test")

    def test_routes_output_to_all_downstream(self):
        """security has 3 downstream targets — all should be routed."""
        engine = CrossNatureRoutingEngine()
        state = self._fresh_state()
        count = engine.route_nature_output(
            "security", {"W1": {"success": True}}, state)
        assert count == 3
        assert len(state.routed_messages) == 3
        assert len(state.events) == 3
        targets = {m["to_nature"] for m in state.routed_messages}
        assert targets == {"defense", "orchestration", "telemetry"}

    def test_route_output_records_history(self):
        """Routed messages should appear in engine routing_history."""
        engine = CrossNatureRoutingEngine()
        state = self._fresh_state()
        engine.route_nature_output("monitor", {"M": {}}, state)
        assert len(engine.routing_history) == 3
        assert engine.routing_history[0]["from_nature"] == "monitor"

    def test_route_output_no_routes_returns_zero(self):
        """A Nature with no defined downstream routes should activate zero.

        Every real Nature has feeds_into entries, so an unknown Nature name
        is used to exercise the zero-route path.
        """
        engine = CrossNatureRoutingEngine()
        state = self._fresh_state()
        count = engine.route_nature_output("__no_such_nature__", {"V": {}}, state)
        assert count == 0
        assert state.routed_messages == []
        assert state.events == []


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine — compute_routing_order (Topological)
# ═══════════════════════════════════════════════════════════════════


class TestRoutingEngineOrder:
    """Verify compute_routing_order() topological sorting."""

    def test_order_includes_all_natures(self):
        """Every defined Nature must appear exactly once in the order."""
        engine = CrossNatureRoutingEngine()
        order = engine.compute_routing_order(["security"])
        assert len(order) == len(NATURE_DEFINITIONS)
        assert set(order) == set(NATURE_DEFINITIONS.keys())

    def test_dependencies_come_before_dependents(self):
        """security feeds defense, so security must precede defense."""
        engine = CrossNatureRoutingEngine()
        order = engine.compute_routing_order(["security"])
        assert order.index("security") < order.index("defense")

    def test_acyclic_graph_orders_dependencies_first(self):
        """On an acyclic synthetic graph, order must respect all edges.

        Uses a synthetic NATURE_DEFINITIONS to test the topological sort
        deterministically (the real graph's cycle-breaking removes some
        edges, so only partial invariants hold there).
        """
        synthetic = {
            "alpha": {"feeds_into": ["beta", "gamma"]},
            "beta": {"feeds_into": ["delta"]},
            "gamma": {"feeds_into": ["delta"]},
            "delta": {"feeds_into": []},
        }
        # Start from the leaf delta: compute_routing_order walks the
        # UPSTREAM closure (dependencies) from the start natures, so this
        # yields a full topological order alpha -> {beta,gamma} -> delta.
        with mock.patch("CORE.WORMS.CROSS_NATURE_ROUTER.NATURE_DEFINITIONS",
                        synthetic):
            engine = CrossNatureRoutingEngine()
            order = engine.compute_routing_order(["delta"])
        # alpha before beta/gamma before delta
        assert order.index("alpha") < order.index("beta")
        assert order.index("alpha") < order.index("gamma")
        assert order.index("beta") < order.index("delta")
        assert order.index("gamma") < order.index("delta")

    def test_acyclic_graph_cycle_breaking(self):
        """Cycles must be broken so ordering completes without hanging."""
        synthetic = {
            "a": {"feeds_into": ["b"]},
            "b": {"feeds_into": ["c"]},
            "c": {"feeds_into": ["a"]},  # a -> b -> c -> a cycle
        }
        with mock.patch("CORE.WORMS.CROSS_NATURE_ROUTER.NATURE_DEFINITIONS",
                        synthetic):
            engine = CrossNatureRoutingEngine()
            order = engine.compute_routing_order(["a"])
        assert set(order) == {"a", "b", "c"}
        assert len(order) == 3

    def test_order_is_deterministic(self):
        """Same input must produce identical order across runs."""
        engine = CrossNatureRoutingEngine()
        o1 = engine.compute_routing_order(["security", "monitor"])
        o2 = engine.compute_routing_order(["security", "monitor"])
        assert o1 == o2

    def test_detect_cycles_finds_cycles(self):
        """The real routing graph has cycles (e.g., defense<->repair)."""
        engine = CrossNatureRoutingEngine()
        cycles = engine.detect_cycles()
        assert isinstance(cycles, list)
        assert len(cycles) >= 1
        # Each cycle must contain at least 2 distinct natures
        for cycle in cycles:
            assert len(cycle) >= 2

    def test_detect_cycles_contains_known_cycle(self):
        """defense and repair appear together in a detected cycle."""
        engine = CrossNatureRoutingEngine()
        cycles = engine.detect_cycles()
        flat = [n for cycle in cycles for n in cycle]
        assert "defense" in flat
        assert "repair" in flat


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine — Paths
# ═══════════════════════════════════════════════════════════════════


class TestRoutingEnginePaths:
    """Verify shortest_path, optimize_pipeline, get_all_paths."""

    def test_shortest_path_security_to_repair(self):
        """security → defense → repair is the shortest path."""
        engine = CrossNatureRoutingEngine()
        path = engine.shortest_path("security", "repair")
        assert path == ["security", "defense", "repair"]

    def test_shortest_path_same_nature(self):
        """Path from a Nature to itself is a single-element list."""
        engine = CrossNatureRoutingEngine()
        assert engine.shortest_path("security", "security") == ["security"]

    def test_shortest_path_unreachable(self):
        """An unreachable pair should return None."""
        engine = CrossNatureRoutingEngine()
        assert engine.shortest_path("security", "migration") is None

    def test_shortest_path_direct_edge(self):
        """A direct feeds_into edge is a 2-node path."""
        engine = CrossNatureRoutingEngine()
        path = engine.shortest_path("security", "defense")
        assert path == ["security", "defense"]

    def test_optimize_pipeline_with_targets(self):
        """optimize_pipeline should include all natures on the target paths."""
        engine = CrossNatureRoutingEngine()
        order = engine.optimize_pipeline("security", ["repair", "orchestration"])
        assert set(order) == set(NATURE_DEFINITIONS.keys())
        # security -> defense survives cycle-breaking; assert that edge only
        # (defense -> repair is removed by cycle-breaking in the real graph)
        assert order.index("security") < order.index("defense")
        # repair and orchestration must both be reachable from security
        assert "repair" in order
        assert "orchestration" in order

    def test_optimize_pipeline_no_targets(self):
        """optimize_pipeline without targets falls back to routing order."""
        engine = CrossNatureRoutingEngine()
        order = engine.optimize_pipeline("security")
        assert len(order) == len(NATURE_DEFINITIONS)

    def test_get_all_paths_returns_many_paths(self):
        """The real graph should yield a large set of complete paths."""
        engine = CrossNatureRoutingEngine()
        paths = engine.get_all_paths()
        assert len(paths) >= 100
        for path in paths:
            assert len(path) >= 1
            assert path[0] in NATURE_DEFINITIONS

    def test_get_all_paths_are_valid_chains(self):
        """Consecutive natures in each path must be connected by a route."""
        engine = CrossNatureRoutingEngine()
        edges = {(r.from_nature, r.to_nature) for r in engine.routes}
        for path in engine.get_all_paths():
            for i in range(len(path) - 1):
                assert (path[i], path[i + 1]) in edges, \
                    f"No edge {path[i]} -> {path[i + 1]}"


# ═══════════════════════════════════════════════════════════════════
# CrossNatureRoutingEngine — analyze_routing (static fallback)
# ═══════════════════════════════════════════════════════════════════


class TestRoutingEngineAnalyze:
    """Verify analyze_routing() static fallback when inference is absent."""

    def test_static_fallback_suggests_downstream(self):
        """Without inference, suggestions come from static routes."""
        with mock.patch(
            "CORE.WORMS.CROSS_NATURE_ROUTER._get_inference", return_value=None):
            engine = CrossNatureRoutingEngine()
            result = engine.analyze_routing(
                {"security": {"success_count": 1, "failure_count": 0,
                              "duration_ms": 5}},
                ["defense", "orchestration", "monitor"],
            )
            assert result["confidence"] == "low"
            assert "Static routing" in result["routing_insight"]
            assert "defense" in result["suggested_next"]
            assert "orchestration" in result["suggested_next"]

    def test_static_fallback_limits_to_available(self):
        """Suggestions must be restricted to available Natures."""
        with mock.patch(
            "CORE.WORMS.CROSS_NATURE_ROUTER._get_inference", return_value=None):
            engine = CrossNatureRoutingEngine()
            result = engine.analyze_routing(
                {"security": {"success_count": 1, "failure_count": 0,
                              "duration_ms": 5}},
                ["defense"],  # only defense is available
            )
            assert "defense" in result["suggested_next"]
            for suggestion in result["suggested_next"]:
                assert suggestion in ["defense"]

    def test_static_fallback_empty_results(self):
        """No executed Natures should produce an empty suggestion list."""
        with mock.patch(
            "CORE.WORMS.CROSS_NATURE_ROUTER._get_inference", return_value=None):
            engine = CrossNatureRoutingEngine()
            result = engine.analyze_routing({}, ["defense"])
            assert result["suggested_next"] == []
            assert result["confidence"] == "low"


# ═══════════════════════════════════════════════════════════════════
# MetaClusterState Dataclass
# ═══════════════════════════════════════════════════════════════════


class TestMetaClusterState:
    """Verify MetaClusterState defaults and mutation."""

    def test_defaults(self):
        """Fresh state should start idle with empty collections."""
        state = MetaClusterState()
        assert state.run_id == ""
        assert state.phase == "idle"
        assert state.active_natures == set()
        assert state.completed_natures == set()
        assert state.failed_natures == set()
        assert state.worm_results == {}
        assert state.routed_messages == []
        assert state.events == []
        assert state.metrics == {}

    def test_phase_transitions(self):
        """Phase should track the run lifecycle."""
        state = MetaClusterState(run_id="r1")
        state.phase = "discovering"
        assert state.phase == "discovering"
        state.phase = "complete"
        assert state.phase == "complete"

    def test_tracks_sets(self):
        """completed/failed sets should track nature outcomes."""
        state = MetaClusterState(run_id="r1")
        state.completed_natures.add("security")
        state.failed_natures.add("monitor")
        assert state.completed_natures == {"security"}
        assert state.failed_natures == {"monitor"}


# ═══════════════════════════════════════════════════════════════════
# MetaCluster.orchestrate() — Routing Integration (stubbed NCM)
# ═══════════════════════════════════════════════════════════════════


class _StubNCM:
    """Stub NatureClusterManager that returns synthetic results."""

    def __init__(self, clusters):
        # clusters: {nature: NatureCluster-like with .worms}
        self.clusters = clusters

    def discover_all_natures(self):
        return {n: len(c.worms) for n, c in self.clusters.items()}

    def execute_nature(self, nature, parallel=False):
        return NatureResult(
            nature=nature,
            worm_results={"W1": {"success": True, "result": {"n": 1}}},
            success_count=1,
            failure_count=0,
            duration_ms=1.0,
        )

    def _score_natures(self):
        return {n: 5.0 for n in self.clusters}

    def get_status(self):
        return {
            "version": "stub",
            "natures": len(self.clusters),
            "total_worms": sum(len(c.worms) for c in self.clusters.values()),
        }


def _make_meta_cluster(natures):
    """Build a MetaCluster with a stubbed NCM over the given natures."""
    clusters = {
        n: NatureCluster(n) for n in natures
    }
    for n, c in clusters.items():
        c.add_worm_manual("W1", _MockWormOK)
    mc = MetaCluster()
    mc.ncm = _StubNCM(clusters)
    return mc


class TestMetaClusterOrchestrate:
    """Verify MetaCluster.orchestrate() routing integration."""

    def test_orchestrate_executes_requested_natures(self):
        """orchestrate(natures=[...]) should execute exactly those Natures."""
        mc = _make_meta_cluster(["security", "defense"])
        result = mc.orchestrate(natures=["security", "defense"])
        assert isinstance(result, MetaClusterResult)
        assert result.natures_executed == 2
        assert set(result.nature_results.keys()) == {"security", "defense"}
        assert result.total_worms_ok == 2

    def test_orchestrate_updates_state(self):
        """State should track the run to 'complete' with results."""
        mc = _make_meta_cluster(["security"])
        result = mc.orchestrate(natures=["security"])
        assert mc.state is not None
        assert mc.state.phase == "complete"
        assert mc.state.completed_natures == {"security"}
        assert "security" in mc.state.worm_results

    def test_orchestrate_routes_downstream(self):
        """Security's output should be routed to its downstream Natures."""
        mc = _make_meta_cluster(["security", "defense", "monitor"])
        result = mc.orchestrate(natures=["security"])
        # security feeds defense/orchestration/telemetry — routes activated
        assert len(result.cross_nature_paths_used) >= 1
        assert mc.state.routed_messages, "Expected routed messages"

    def test_orchestrate_generates_insights(self):
        """Insights should summarize execution success."""
        mc = _make_meta_cluster(["security"])
        result = mc.orchestrate(natures=["security"])
        assert len(result.insights) >= 1
        assert any("success rate" in i for i in result.insights)

    def test_orchestrate_records_history(self):
        """Each orchestration should append to history and be retrievable."""
        mc = _make_meta_cluster(["security"])
        mc.orchestrate(natures=["security"])
        assert len(mc._history) == 1
        last = mc.get_last_result()
        assert last is not None
        assert last.natures_executed == 1

    def test_orchestrate_hooks_fire(self):
        """pre/post_nature hooks should fire for each executed Nature."""
        mc = _make_meta_cluster(["security", "defense"])
        pre = []
        post = []
        mc.on("pre_nature", lambda **kw: pre.append(kw.get("nature")))
        mc.on("post_nature", lambda **kw: post.append(kw.get("nature")))
        mc.orchestrate(natures=["security", "defense"])
        assert pre == ["security", "defense"]
        assert post == ["security", "defense"]

    def test_orchestrate_on_insight_hook(self):
        """on_insight hooks should fire per generated insight."""
        mc = _make_meta_cluster(["security"])
        seen = []
        mc.on("on_insight", lambda **kw: seen.append(kw.get("insight")))
        result = mc.orchestrate(natures=["security"])
        assert len(seen) == len(result.insights) >= 1

    def test_orchestrate_generates_recommendations(self):
        """Unused Natures should be flagged as recommendations."""
        mc = _make_meta_cluster(["security", "monitor"])
        result = mc.orchestrate(natures=["security"])
        assert any("monitor" in r for r in result.recommendations), \
            f"Expected monitor recommendation, got {result.recommendations}"

    def test_orchestrate_single_nature_convenience(self):
        """orchestrate_nature should run a single Nature."""
        mc = _make_meta_cluster(["security", "defense"])
        result = mc.orchestrate_nature("security")
        assert result.natures_executed == 1
        assert set(result.nature_results.keys()) == {"security"}

    def test_orchestrate_adaptive_caps_natures(self):
        """orchestrate_adaptive(max_natures=1) should run only one Nature."""
        mc = _make_meta_cluster(["security", "defense", "monitor"])
        result = mc.orchestrate_adaptive(max_natures=1)
        assert result.natures_executed == 1

    def test_orchestrate_full_pipeline_routes(self):
        """orchestrate_full_pipeline should follow the routing graph."""
        mc = _make_meta_cluster(["security", "defense", "repair"])
        result = mc.orchestrate_full_pipeline("security")
        # security -> defense -> repair must all be executed
        assert "security" in result.nature_results
        assert "defense" in result.nature_results
        assert "repair" in result.nature_results

    def test_get_status_reports_meta_state(self):
        """get_status should surface routing and state info."""
        mc = _make_meta_cluster(["security"])
        status = mc.get_status()
        assert status["version"] == "1.0.0"
        assert status["cross_nature_routes"] >= 1
        assert status["state_phase"] == "idle"
        mc.orchestrate(natures=["security"])
        status = mc.get_status()
        assert status["state_phase"] == "complete"
        assert status["orchestration_history"] == 1

    def test_to_mermaid_execution_flow(self):
        """Mermaid flow should render after an orchestration."""
        mc = _make_meta_cluster(["security"])
        before = mc.to_mermaid_execution_flow()
        assert "No orchestration results yet" in before
        mc.orchestrate(natures=["security"])
        after = mc.to_mermaid_execution_flow()
        assert "graph LR" in after
        assert "security" in after


# ═══════════════════════════════════════════════════════════════════
# Standalone Runner (pytest-free — safe on Python 3.14t, see Error #48)
# ═══════════════════════════════════════════════════════════════════


def _run_standalone():
    """Run all Test* classes in-process (no subprocesses needed — hermetic)."""
    passed = 0
    failed = 0
    errors = []

    for name, obj in sorted(globals().items(), key=lambda x: x[0]):
        if isinstance(obj, type) and name.startswith("Test"):
            inst = obj()
            methods = sorted(m for m in dir(inst) if m.startswith("test_"))
            print(f"[{name}] ({len(methods)} tests)")
            for method_name in methods:
                try:
                    getattr(inst, method_name)()
                    print(f"  [OK] {name}.{method_name}")
                    passed += 1
                except BaseException as exc:
                    print(f"  [FAIL] {name}.{method_name}: {exc}")
                    failed += 1
                    errors.append(f"{name}.{method_name}: {exc}")

    print(f"\n  Passed: {passed}, Failed: {failed}")
    if errors:
        print("  Errors:")
        for e in errors[:10]:
            print(f"    {e}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(_run_standalone())
