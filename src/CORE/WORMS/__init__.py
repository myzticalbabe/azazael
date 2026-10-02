# CORE/WORMS — Worm Package
#
# Each worm module registers itself via @register_worm at module load time.
# To discover ALL worms, use CORE.worm_registry.discover_worms() which scans
# the registry across all installed packages.
#
# Explicitly export commonly-used worm modules for convenience:
#   from CORE.WORMS import CLUSTERWORMS, METACLUSTER

# Lazy re-exports (PEP 562): importing this package root must not pay for
# cluster modules up front. 2026-10-01: 175 files execute this
# file via `from CORE.WORMS.<submodule> import ...` while needing none of
# these names.
# U3: NatureClusterManager was removed with the taxonomy (D1);
# execution moved to ClusterWORMZ-by-category, DLQ to DeadLetterQueue.
__all__ = [
    "ClusterWORMZ",
    "MetaCluster",
]


def __getattr__(name: str):
    if name == "ClusterWORMZ":
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

        return ClusterWORMZ
    if name == "NatureClusterManager":
        raise ImportError(
            "NatureClusterManager was removed with the nature taxonomy (U3/D1). "
            "Execute by category: ClusterWORMZ.build_from_registry(worms); "
            "dead letters: DeadLetterQueue.")
    if name == "MetaCluster":
        from CORE.WORMS.METACLUSTER import MetaCluster

        return MetaCluster
    raise AttributeError("module 'CORE.WORMS' has no attribute %r" % (name,))
