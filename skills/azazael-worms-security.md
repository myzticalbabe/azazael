---
name: azazael-worms-security
description: Azazael security & integrity worms — security (24), config (5), backup (5). Load when working with VulnScanner, PortAuditor, secret rotation, config validation, or backup/recovery.
metadata:
  category: architecture
  project: azazael
  parent: azazael-worms
---
# Azazael Worms — Security & Integrity

## security (5 worms) — Priority 5–8, Cooldown 45s–120s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **VulnScanner** | 8 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| PortAuditor | 7 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| CertMonitor | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FirewallAudit | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| PermissionScanner | 5 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** VulnScanner (p=8) is the highest-priority security worm — CVE lookup, dependency audit, known-vulnerability detection. CertMonitor has the longest cooldown (120s) — SSL/TLS cert expiry tracking is expensive.

## config (5 worms) — Priority 4–6, Cooldown 30s–120s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **SecretRotator** | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ConfigLinter | 5 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| EnvValidator | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DotfileSync | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| FeatureFlagCtrl | 4 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** SecretRotator handles credential rotation with backup and validation. ConfigLinter validates JSON/YAML/TOML schemas. EnvValidator checks consistency across .env, system env, and docker-compose.

## backup (5 worms) — Priority 4–7, Cooldown 30s–300s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **StateSnapshotter** | 7 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| IncrementalBackupWorm | 6 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| CheckpointWorm | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RecoveryTester | 5 | 180.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ColdArchivist | 4 | 300.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** ColdArchivist has the longest cooldown in the entire ecosystem (300s = 5min) — cold storage compression is expensive. StateSnapshotter is the highest-priority backup worm (p=7). CheckpointWorm saves worm execution state for resume-after-failure.

## Security Pipeline

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Full security audit
cluster = ClusterWORMZ.build_from_nature("security")
vulns = cluster.execute_sequential()  # Sequential — port scanning is noisy

# Config validation
cluster = ClusterWORMZ.build_from_nature("config")
config_issues = cluster.execute_all()

# Backup integrity
cluster = ClusterWORMZ.build_from_nature("backup")
backup_status = cluster.execute_sequential()  # Sequential — avoid I/O contention
```

## Threat Model Coverage

| Layer | Worms | What's Covered |
|-------|-------|---------------|
| Network | PortAuditor, FirewallAudit | Open ports, service fingerprinting, firewall rules |
| Application | VulnScanner, CertMonitor | CVE detection, dependency audit, SSL/TLS certs |
| Config | ConfigLinter, EnvValidator, SecretRotator | Schema validation, env consistency, credential rotation |
| Filesystem | PermissionScanner, DotfileSync | File permissions, writable paths, dotfile sync |
| Data | StateSnapshotter, IncrementalBackupWorm, CheckpointWorm | Full/incremental backups, state checkpoints |
| Recovery | RecoveryTester, ColdArchivist | Restore validation, cold storage, retention |

## Related Skills
- `azazael-worms` — Full 77-worm catalog, registry API
- `azazael-worms-core` — Orchestration + utility + diagnostic worms
- `azazael-worms-monitor` — Monitor + profiling + telemetry worms

Total: **15 security & integrity worms** (security 5 + config 5 + backup 5)
