# WORM CONFIG TRACE — Per-Worm Configuration Audit

> *Generated: May 28, 2026 — Auto-extracted from live WORM_REGISTRY*
> *Total: 77 worms across 17 categories*

---

## Category Breakdown

| Category | Count | Priority Range |
|----------|-------|---------------|
| orchestration | 6 | 3–10 |
| monitor | 5 | 5–8 |
| security | 5 | 5–8 |
| profiling | 5 | 6–7 |
| telemetry | 5 | 5–7 |
| container | 5 | 4–6 |
| communication | 5 | 4–7 |
| backup | 5 | 4–7 |
| config | 5 | 4–6 |
| learning | 5 | 4–6 |
| migration | 5 | 3–6 |
| visualization | 5 | 4–5 |
| utility | 5 | 3–5 |
| diagnostic | 4 | 4–7 |
| analysis | 3 | 5–6 |
| sync | 1 | 5 |
| ml | 2 | 5–6 |

---

## Complete Per-Worm Configuration Trace

### [analysis] — 3 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| BinaryAnalysis | 6 | 60.0s | 1.0.0 | BINARY_ANALYSIS.py |
| ClusterInspector | 5 | 45.0s | 1.0.0 | CLUSTER_INSPECTOR.py |
| ReverseTools | 6 | 60.0s | 1.0.0 | REVERSE_TOOLS.py |

### [backup] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| CheckpointWorm | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ColdArchivist | 4 | 300.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| IncrementalBackupWorm | 6 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RecoveryTester | 5 | 180.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| StateSnapshotter | 7 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [communication] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| IPCBridge | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| MessageBroker | 7 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ProtocolNegotiator | 4 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RPCEndpoint | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| WebhookRelay | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [config] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| ConfigLinter | 5 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DotfileSync | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| EnvValidator | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FeatureFlagCtrl | 4 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| SecretRotator | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [container] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| ComposeValidator | 5 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ContainerOrch | 6 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ImageAuditor | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RegistryPoller | 4 | 180.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ResourceQuotaWatch | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [diagnostic] — 4 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| DiagnosticWorm | 5 | 60.0s | 0.0.0 | DIAGNOSTIC_WORM.py |
| FastErrorScanner | 4 | 45.0s | 0.0.0 | ERROR_SCAN_WORM.py |
| MorphingWormV2 | 4 | 45.0s | 2.0.0 | MORPHING_WORM_V2.py |
| NetworkDiag | 7 | 30.0s | 1.0.0 | NETWORK_DIAG.py |

### [learning] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| ABTestRunner | 4 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DataPipelineWorm | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FeatureEngineer | 5 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ModelVersioner | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RLTrainLoop | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [migration] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| CodeMigrator | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DepUpgrader | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ImportPathFixWorm | 4 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| LegacyShimGen | 3 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| SchemaVersioner | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [ml] — 2 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| SYSTEMZ_ML | 6 | 45.0s | 1.0.0 | SYSTEMZ_ML.py |
| WORMZ_ML | 5 | 60.0s | 1.0.0 | WORMZ_ML.py |

### [monitor] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| DISKZ | 5 | 30.0s | 1.0.0 | DISKZ.py |
| NETWORXZ | 7 | 15.0s | 1.0.0 | NETWORXZ.py |
| OSCongruency | 6 | 30.0s | 0.0.0 | OS_CONGRUENCY.py |
| PROCESSZ | 7 | 15.0s | 1.0.0 | PROCESSZ.py |
| SMARTDISK | 5 | 60.0s | 1.0.0 | SMARTDISK.py |
| SystemZ | 8 | 15.0s | 1.0.0 | SYSTEMZ.py |

### [orchestration] — 6 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| ClusterWORMZ | 8 | 20.0s | 2.0.0 | CLUSTERWORMS.py |
| ConcurrencyManager | 7 | 20.0s | 1.0.0 | CONCURRENCY.py |
| MetaCluster | 10 | 5.0s | 1.0.0 | METACLUSTER.py |
| NatureCluster | 3 | 20.0s | 1.0.0 | NATURE_CLUSTERS.py |
| NatureClusterManager | 9 | 10.0s | 1.0.0 | NATURE_CLUSTERS.py |
| WormFleet | 6 | 30.0s | 0.0.0 | WORM_FLEET.py |

### [profiling] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| CodeProfiler | 7 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| CPUFlameProfiler | 6 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| GILContentionProbe | 7 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| IOBottleneckFinder | 6 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| MemoryLeakDetector | 6 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [security] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| CertMonitor | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FirewallAudit | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| PermissionScanner | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| PortAuditor | 7 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| VulnScanner | 8 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [sync] — 1 worm

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| CLOCKZ | 5 | 30.0s | 1.0.0 | CLOCKZ.py |

### [telemetry] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| AlertEscalator | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| EventRouter | 6 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| LogStreamer | 5 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| MetricAggregator | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| SpanTracer | 7 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

### [utility] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| MemoryBus | 3 | 30.0s | 1.0.0 | MemoryBus.py |
| MorphingWorm | 3 | 30.0s | 1.0.0 | MORPHING_WORM.py |
| OMNIV2 | 4 | 60.0s | 2.0.0 | OMNI_WORM_V2.py |
| PamsRecorder | 3 | 30.0s | 1.0.0 | PamsRecorder.py |
| WORMZ | 5 | 60.0s | 1.0.0 | WORMZ.py |

### [visualization] — 5 worms

| Worm | Priority | Cooldown | Version | Source |
|------|----------|----------|---------|--------|
| DashboardGen | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| GraphRenderer | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| HeatmapBuilder | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ReportCompiler | 4 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| TimelineViz | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

---

## Key Observations

1. **ECOSYSTEM_EXPANSION.py is the dominant source** — 48 of 77 worms (62%) originate from a single file. This is the primary worm factory.

2. **Highest priority worm: MetaCluster (p=10)** — The cluster-of-clusters orchestrator is the top-priority worm, with the shortest cooldown (5s).

3. **Lowest priority worms (p=3):** MemoryBus, MorphingWorm, NatureCluster, PamsRecorder, LegacyShimGen — utility/infrastructure worms.

4. **Longest cooldown: ColdArchivist (300s = 5min)** — Backup operations are intentionally slow.

5. **Shortest cooldown: MetaCluster (5s)** — Orchestration needs near-instant respawn.

6. **Version anomalies:** `ClusterWORMZ` is v2.0.0 (just upgraded), `MorphingWormV2` is v2.0.0, `OMNIV2` is v2.0.0. Most others are v1.0.0. Several are v0.0.0 (pre-release): DiagnosticWorm, FastErrorScanner, OSCongruency, WormFleet.

7. **Zero spawns across all worms** — No worm has been spawned yet. The SpawnDiversityEngine is ready but unused in production.

8. **Data file:** `azazael/worm_config_trace.json` contains the complete JSON dump for programmatic consumption.
