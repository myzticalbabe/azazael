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

# ── NATURE_CLUSTERS (removed, D1/U3) ───────────────────────────── Investigators
# The nature taxonomy was ripped out per MIGRATION_LEDGER D1; execution moved
# to ClusterWORMZ-by-category and METACLUSTER degraded gracefully. D1 flat:
_NATURE_OK = False
NatureClusterManager = None  # type: ignore[assignment]
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
    # NATURE_CLUSTERS removal artifacts (kept importable = error-free no-ops)
    "NatureClusterManager", "NATURE_DEFINITIONS",
    # METACLUSTER
    "MetaCluster", "MetaClusterResult", "MetaClusterState",
    "CrossNatureRoutingEngine",
    # Status flags
    "_CLUSTERWORMS_OK", "_NATURE_OK", "_META_OK",
]
