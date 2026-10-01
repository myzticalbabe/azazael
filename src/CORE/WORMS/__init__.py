# CORE/WORMS — Worm Package
#
# Each worm module registers itself via @register_worm at module load time.
# To discover ALL worms, use CORE.worm_registry.discover_worms() which scans
# the registry across all installed packages.
#
# Explicitly export commonly-used worm modules for convenience:
#   from CORE.WORMS import CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTER

# Lazy re-exports (PEP 562): importing this package root must not pay for
# all three cluster modules up front. 2026-10-01: 175 files execute this
# file via `from CORE.WORMS.<submodule> import ...` while needing none of
# these names; eager imports also hard-couple the root to NATURE_CLUSTERS,
# which is scheduled for removal (rip-out plan Stage 1).
__all__ = [
    "ClusterWORMZ",
    "NatureClusterManager",
    "MetaCluster",
]


def __getattr__(name: str):
    if name == "ClusterWORMZ":
        from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

        return ClusterWORMZ
    if name == "NatureClusterManager":
        from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager

        return NatureClusterManager
    if name == "MetaCluster":
        from CORE.WORMS.METACLUSTER import MetaCluster

        return MetaCluster
    raise AttributeError("module 'CORE.WORMS' has no attribute %r" % (name,))
