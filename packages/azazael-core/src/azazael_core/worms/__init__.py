# coding: utf-8
"""
WORMS — Bundled expansion worm modules for azazael-core standalone package.

Imports all 50 expansion worms from the expansion/ subdirectory,
triggering @register_worm decorators to populate WORM_REGISTRY.
"""

from .expansion import *

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
]
