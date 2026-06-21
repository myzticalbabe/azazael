# coding: utf-8
"""Clusters — Coordinated worm collectives (bundled from CORE/WORMS/).

Provides the cluster infrastructure for the standalone azazael-core package.
Execution methods fall back gracefully when full CORE infrastructure
(PamsRecorder, MemoryBus, individual worm modules) is unavailable.
"""

# ── CLUSTERWORMS ───────────────────────────────────────────────────
try:
    from .CLUSTERWORMS import (
        ClusterWORMZ,
        ClusterResult,
        ClusterState,
        WormConfig,
        CLUSTER_REGISTRY,
        run_popup,
        _resolve_worm_dynamic,
        _execute_worm_class,
    )
    _CLUSTERWORMS_OK = True
except ImportError:
    _CLUSTERWORMS_OK = False
    ClusterWORMZ = None
    CLUSTER_REGISTRY = {}

# ── NATURE_CLUSTERS ────────────────────────────────────────────────
try:
    from .NATURE_CLUSTERS import (
        NatureCluster,
        NatureClusterManager,
        NatureResult,
        CrossNatureRoute,
        NATURE_DEFINITIONS,
    )
    _NATURE_OK = True
except ImportError:
    _NATURE_OK = False
    NatureClusterManager = None
    NATURE_DEFINITIONS = {}

# ── METACLUSTER ────────────────────────────────────────────────────
try:
    from .METACLUSTER import (
        MetaCluster,
        MetaClusterResult,
        MetaClusterState,
        CrossNatureRoutingEngine,
    )
    _META_OK = True
except ImportError:
    _META_OK = False
    MetaCluster = None
    CrossNatureRoutingEngine = None


__all__ = [
    # CLUSTERWORMS
    "ClusterWORMZ", "ClusterResult", "ClusterState", "WormConfig",
    "CLUSTER_REGISTRY", "run_popup",
    # NATURE_CLUSTERS
    "NatureCluster", "NatureClusterManager", "NatureResult",
    "CrossNatureRoute", "NATURE_DEFINITIONS",
    # METACLUSTER
    "MetaCluster", "MetaClusterResult", "MetaClusterState",
    "CrossNatureRoutingEngine",
    # Status flags
    "_CLUSTERWORMS_OK", "_NATURE_OK", "_META_OK",
]
