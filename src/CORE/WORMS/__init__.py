# CORE/WORMS — Worm Package
#
# Each worm module registers itself via @register_worm at module load time.
# To discover ALL worms, use CORE.worm_registry.discover_worms() which scans
# the registry across all installed packages.
#
# Explicitly export commonly-used worm modules for convenience:
#   from CORE.WORMS import CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTER

from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
from CORE.WORMS.NATURE_CLUSTERS import NatureClusterManager
from CORE.WORMS.METACLUSTER import MetaCluster

__all__ = [
    "ClusterWORMZ",
    "NatureClusterManager",
    "MetaCluster",
]
