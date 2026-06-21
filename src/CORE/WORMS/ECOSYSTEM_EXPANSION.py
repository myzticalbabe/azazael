# coding: utf-8
"""
ECOSYSTEM_EXPANSION — 50 New Worm Classes

[!] DEPRECATION NOTICE: This monolithic file has been split into 10 
category modules under expansion/. This shim re-exports all 50 worm 
classes for backward compatibility.

New canonical location: CORE/WORMS/expansion/
  security.py, profiling.py, telemetry.py, container.py, config.py,
  backup.py, migration.py, communication.py, learning.py, visualization.py

This shim will be removed in a future release.
"""

import sys
import warnings
from pathlib import Path

warnings.warn(
    "CORE.WORMS.ECOSYSTEM_EXPANSION is deprecated. "
    "Use CORE.WORMS.expansion (split into 10 category modules). "
    "This shim re-exports all 50 worm classes for backward compatibility.",
    DeprecationWarning, stacklevel=2
)

# Ensure parent src/ is on path
_src_dir = Path(__file__).resolve().parent.parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

# Re-export all 50 worms from the split expansion package
from CORE.WORMS.expansion import *  # noqa: E402, F401

__all__ = [
    # security
    "VulnScanner", "PortAuditor", "CertMonitor", "FirewallAudit", "PermissionScanner",
    # profiling
    "CodeProfiler", "MemoryLeakDetector", "IOBottleneckFinder", "GILContentionProbe", "CPUFlameProfiler",
    # telemetry
    "SpanTracer", "MetricAggregator", "LogStreamer", "EventRouter", "AlertEscalator",
    # container
    "ContainerOrch", "ComposeValidator", "ImageAuditor", "RegistryPoller", "ResourceQuotaWatch",
    # config
    "ConfigLinter", "EnvValidator", "DotfileSync", "SecretRotator", "FeatureFlagCtrl",
    # backup
    "StateSnapshotter", "IncrementalBackupWorm", "RecoveryTester", "ColdArchivist", "CheckpointWorm",
    # migration
    "CodeMigrator", "DepUpgrader", "SchemaVersioner", "ImportPathFixWorm", "LegacyShimGen",
    # communication
    "MessageBroker", "RPCEndpoint", "WebhookRelay", "IPCBridge", "ProtocolNegotiator",
    # learning
    "RLTrainLoop", "ModelVersioner", "DataPipelineWorm", "ABTestRunner", "FeatureEngineer",
    # visualization
    "DashboardGen", "GraphRenderer", "ReportCompiler", "HeatmapBuilder", "TimelineViz",
    # db_monitor
    "DatabaseMonitorWorm",
]
