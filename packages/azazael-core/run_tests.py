#!/usr/bin/env python3
"""Integration test runner for azazael-core.

Runs all smoke tests via subprocess and direct imports.

Why not just use pytest?
  pytest 9.0.3 segfaulted on the then-current 3.14t (free-threading) interpreter
  in some environments (cygwin bash, certain CI runners). See ERROR_LOG.md
  Error #48. That interpreter was retired on 2026-10-19 and this package now runs
  on 3.15t; the plain-assertions + subprocess path is kept because it is how this
  package suite has always run, not because a 3.15t segfault was measured.
  Python 3.13 is not used on this system.
"""
import subprocess
import sys


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)


def test(name: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    if not condition:
        sys.exit(1)


def main():
    print("=" * 50)
    print("  azazael-core Integration Tests")
    print("=" * 50)

    # ── Import chain ───────────────────────────────────────────────
    print("\n--- Import Chain ---")
    from azazael_core.worms.clusters import (
        _CLUSTERWORMS_OK, _NATURE_OK, _META_OK,
    )
    test("CLUSTERWORMS import OK", _CLUSTERWORMS_OK)
    test("NATURE_CLUSTERS removed (D1/U3)", _NATURE_OK is False)
    test("METACLUSTER import OK", _META_OK)

    from azazael_core.worm_registry import WORM_REGISTRY
    test("WORM_REGISTRY has entries", len(WORM_REGISTRY) > 0,
         f"{len(WORM_REGISTRY)} worms")

    # ── CLI commands ───────────────────────────────────────────────
    def cli(cmd: str) -> subprocess.CompletedProcess:
        return run([sys.executable, "-m", "azazael_core.cli", cmd])

    print("\n--- CLI: version ---")
    r = cli("version")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    test("shows version", "azazael-core v3.1.0" in r.stdout)

    print("\n--- CLI: paths ---")
    r = cli("paths")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    for section in ["Project Root", "Src Dir", "Output Dir"]:
        test(f"shows {section}", section in r.stdout)

    print("\n--- CLI: registry ---")
    r = cli("registry")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    test("shows Total:", "Total:" in r.stdout)
    test("shows worms", "worms" in r.stdout)

    print("\n--- CLI: clusters ---")
    r = cli("clusters")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    for section in ["Cluster System", "Predefined Clusters"]:
        test(f"shows {section}", section in r.stdout)
    for mod in ["CLUSTERWORMS", "METACLUSTER"]:
        test(f"shows {mod}", mod in r.stdout)
    test("NATURE_CLUSTERS reported removed", "removed" in r.stdout)

    print("\n--- CLI: config ---")
    r = cli("config")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    test("shows AZAZAEL_ROOT", "AZAZAEL_ROOT" in r.stdout)

    print("\n--- CLI: help ---")
    r = cli("help")
    test("exit code 0", r.returncode == 0, f"got {r.returncode}")
    test("shows commands", "clusters" in r.stdout.lower())

    # ── Cluster classes ────────────────────────────────────────────
    print("\n--- Cluster Classes ---")
    from azazael_core.worms.clusters import (
        ClusterWORMZ, NatureClusterManager, MetaCluster,
        CLUSTER_REGISTRY, NATURE_DEFINITIONS,
    )

    cluster = ClusterWORMZ("system")
    status = cluster.get_status()
    test("ClusterWORMZ type", status["cluster_type"] == "system")
    test("ClusterWORMZ has worms", status["worm_count"] > 0,
         f"{status['worm_count']} worms")
    test("ClusterWORMZ version", "version" in status)

    mermaid = cluster.to_mermaid()
    test("ClusterWORMZ Mermaid", "graph TB" in mermaid)

    ncm = NatureClusterManager()
    ncm_status = ncm.get_status()
    test("NatureClusterManager D1 flat shim live",
         ncm_status["mode"] == "D1_flat_registry_categories",
         f"{len(ncm.clusters)} categories")

    mc = MetaCluster()
    mc.discover_all()
    mc_status = mc.get_status()
    test("MetaCluster version", "version" in mc_status)
    test("MetaCluster routing", mc_status["routing_paths"] >= 0,
         f"{mc_status['routing_paths']} paths")

    test("CLUSTER_REGISTRY types", len(CLUSTER_REGISTRY) >= 8,
         f"{len(CLUSTER_REGISTRY)} types")
    test("NATURE_DEFINITIONS empty (D1)", NATURE_DEFINITIONS == {},
         f"{len(NATURE_DEFINITIONS)} leftover defs")

    # ── Summary ────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("  ALL TESTS PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()
