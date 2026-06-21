# coding: utf-8
"""
ECOSYSTEM_EXPANSION — 50 New Worm Classes (split into 10 category modules)

Categories:
  security    (5):  VulnScanner, PortAuditor, CertMonitor, FirewallAudit, PermissionScanner
  profiling   (5):  CodeProfiler, MemoryLeakDetector, IOBottleneckFinder, GILContentionProbe, CPUFlameProfiler
  telemetry   (5):  SpanTracer, MetricAggregator, LogStreamer, EventRouter, AlertEscalator
  container   (5):  ContainerOrch, ComposeValidator, ImageAuditor, RegistryPoller, ResourceQuotaWatch
  config      (5):  ConfigLinter, EnvValidator, DotfileSync, SecretRotator, FeatureFlagCtrl
  backup      (5):  StateSnapshotter, IncrementalBackupWorm, RecoveryTester, ColdArchivist, CheckpointWorm
  migration   (5):  CodeMigrator, DepUpgrader, SchemaVersioner, ImportPathFixWorm, LegacyShimGen
  communication (5): MessageBroker, RPCEndpoint, WebhookRelay, IPCBridge, ProtocolNegotiator
  learning    (5):  RLTrainLoop, ModelVersioner, DataPipelineWorm, ABTestRunner, FeatureEngineer
  visualization (5): DashboardGen, GraphRenderer, ReportCompiler, HeatmapBuilder, TimelineViz
"""

from .security import VulnScanner, PortAuditor, CertMonitor, FirewallAudit, PermissionScanner
from .profiling import CodeProfiler, MemoryLeakDetector, IOBottleneckFinder, GILContentionProbe, CPUFlameProfiler
from .telemetry import SpanTracer, MetricAggregator, LogStreamer, EventRouter, AlertEscalator
from .container import ContainerOrch, ComposeValidator, ImageAuditor, RegistryPoller, ResourceQuotaWatch
from .config import ConfigLinter, EnvValidator, DotfileSync, SecretRotator, FeatureFlagCtrl
from .backup import StateSnapshotter, IncrementalBackupWorm, RecoveryTester, ColdArchivist, CheckpointWorm
from .migration import CodeMigrator, DepUpgrader, SchemaVersioner, ImportPathFixWorm, LegacyShimGen
from .communication import MessageBroker, RPCEndpoint, WebhookRelay, IPCBridge, ProtocolNegotiator
from .learning import RLTrainLoop, ModelVersioner, DataPipelineWorm, ABTestRunner, FeatureEngineer
from .visualization import DashboardGen, GraphRenderer, ReportCompiler, HeatmapBuilder, TimelineViz

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


def get_all_expansion_worms():
    """Return all worm class names defined in this package."""
    return list(__all__)


def main():
    """Print expansion summary."""
    from collections import defaultdict
    cats = defaultdict(list)
    for name in __all__:
        cls = globals().get(name)
        if cls and hasattr(cls, "VERSION"):
            cats[cls.__module__].append(name)
    print("=" * 70)
    print("  ECOSYSTEM EXPANSION — 50 New Worm Classes")
    print("=" * 70)
    for cat in sorted(cats):
        print(f"  [{cat}] ({len(cats[cat])} worms):")
        for name in sorted(cats[cat]):
            print(f"    {name}")
    print(f"  Total: {len(__all__)} worm classes")
    print("=" * 70)


if __name__ == "__main__":
    main()
