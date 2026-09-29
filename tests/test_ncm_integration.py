# coding: utf-8
"""
Integration tests for NatureClusterManager full discovery workflow.

Exercises the complete pipeline: worm_registry.discover_worms() →
NatureCluster discovery → NCM aggregation. Verifies that all
optimizations (lazy imports, PAMS caching, registry fast-path)
work correctly end-to-end.
"""
import sys
import time
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))


def test_discover_worms_smoke():
    """Exercise full worm discovery and verify registry is populated.

    `discover_worms()` returns a DELTA (newly registered this call), not the
    fleet size: it is 0 on every call after the first in one process, which made
    this test order-dependent -- it passed alone and failed in the full suite.
    The registry is the invariant, so it is what is asserted.
    """
    from CORE.worm_registry import discover_worms, WORM_REGISTRY

    newly = discover_worms()
    assert len(WORM_REGISTRY) > 0, "WORM_REGISTRY should be populated"
    print(f"  discover_worms(): {newly} new this call, "
          f"{len(WORM_REGISTRY)} entries in the registry")


def test_ncm_discover_all_natures():
    """Exercise NCM.discover_all_natures() and verify cluster state."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    counts = ncm.discover_all_natures()

    assert len(counts) > 0, "Should discover at least one nature"
    assert sum(counts.values()) > 0, "Should discover at least one worm"

    status = ncm.get_status()
    assert status["natures"] == len(counts)
    assert status["total_worms"] == sum(counts.values())
    print(f"  Natures: {status['natures']}, Worms: {status['total_worms']}")


def test_ncm_get_cluster():
    """Verify get_cluster returns populated clusters."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    ncm.discover_all_natures()

    cluster = ncm.get_cluster("security")
    assert cluster is not None, "security nature should exist"
    assert len(cluster.worms) > 0, "security should have worms"

    info = cluster.get_worm_info()
    assert len(info) > 0, "get_worm_info should return data"

    status = cluster.get_status()
    assert status["worm_count"] == len(cluster.worms)
    print(f"  Cluster 'security': {len(cluster.worms)} worms")


def test_ncm_routes():
    """Verify cross-nature routes are generated."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    routes = ncm.get_cross_nature_routes()

    assert len(routes) > 0, "Should have cross-nature routes"
    for r in routes:
        assert r.from_nature
        assert r.to_nature
    print(f"  Cross-nature routes: {len(routes)}")


def test_ncm_status():
    """Verify NCM get_status() works after discovery."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    ncm.discover_all_natures()

    status = ncm.get_status()
    assert "version" in status
    assert "natures" in status
    assert "total_worms" in status
    assert "natures_list" in status
    assert "execution_history_count" in status
    assert "cross_nature_routes" in status
    print(f"  Status: v{status['version']}, {status['natures']} natures")


def test_ncm_list_worms():
    """Verify list_all_worms returns grouped results."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    ncm.discover_all_natures()

    all_worms = ncm.list_all_worms()
    assert len(all_worms) > 0
    for nature, worms in all_worms.items():
        assert len(worms) > 0, f"{nature} should have worms"
    print(f"  Worms grouped: {len(all_worms)} natures")


def test_ncm_mermaid():
    """Verify Mermaid graph generation works without error."""
    from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

    ncm = NatureClusterManager()
    ncm.discover_all_natures()

    graph = ncm.to_mermaid()
    assert "graph TB" in graph
    assert len(graph) > 100
    print(f"  Mermaid graph: {len(graph)} chars")


def test_lazy_imports():
    """Verify lazy import patterns work after discovery."""
    from CORE.WORMS.NATURE_CLUSTERS import _get_pams
    from CORE.WORMS.METACLUSTER import _get_pams as mc_pams, _get_mem_bus as mc_bus
    from CORE.WORMS.CLUSTERWORMS import _get_pams as cw_pams, _get_mem_bus as cw_bus, _get_breaker_registry as cw_breaker

    # Lazy getters should return valid objects without hanging
    for name, fn in [
        ("NATURE_CLUSTERS._get_pams", _get_pams),
        ("METACLUSTER._get_pams", mc_pams),
        ("METACLUSTER._get_mem_bus", mc_bus),
        ("CLUSTERWORMS._get_pams", cw_pams),
        ("CLUSTERWORMS._get_mem_bus", cw_bus),
        ("CLUSTERWORMS._get_breaker_registry", cw_breaker),
    ]:
        try:
            result = fn()
            assert result is not None, f"{name}() returned None"
            print(f"  OK: {name}()")
        except Exception as e:
            print(f"  FAIL: {name}(): {e}")
            raise


# ── Standalone execution ────────────────────────────────────────────

if __name__ == "__main__":
    import traceback

    tests = [
        test_discover_worms_smoke,
        test_ncm_discover_all_natures,
        test_ncm_get_cluster,
        test_ncm_routes,
        test_ncm_status,
        test_ncm_list_worms,
        test_ncm_mermaid,
        test_lazy_imports,
    ]

    passed = 0
    failed = 0
    for test in tests:
        name = test.__name__
        try:
            test()
            print(f"  PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} - {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
