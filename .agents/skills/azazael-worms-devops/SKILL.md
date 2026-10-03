---
name: azazael-worms-devops
description: Azazael DevOps worms — container (5), communication (6), migration (5). Load when working with Docker, IPC, RPC, message brokering, code migration, or schema versioning.
metadata:
  category: architecture
  project: azazael
  parent: azazael-worms
---
# Azazael Worms — DevOps (Container, Communication, Migration)

## container (5 worms) — Priority 4–6, Cooldown 30s–180s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **ContainerOrch** | 6 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ComposeValidator | 5 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ImageAuditor | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ResourceQuotaWatch | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RegistryPoller | 4 | 180.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** ContainerOrch is the anchor — multi-container lifecycle, health checks, restart policies. RegistryPoller has a 180s cooldown (polling container registries for new tags).

## communication (5 worms) — Priority 4–7, Cooldown 15s–45s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **MessageBroker** | 7 | 15.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| RPCEndpoint | 6 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| IPCBridge | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| WebhookRelay | 5 | 30.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ProtocolNegotiator | 4 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** MessageBroker (p=7) is the highest-priority communication worm — in-process pub/sub with topic routing and persistence. RPCEndpoint uses JSON-RPC 2.0. ProtocolNegotiator auto-detects best protocol (JSON, MessagePack, gRPC).

## migration (5 worms) — Priority 3–6, Cooldown 45s–120s

| Worm | P | Cooldown | Ver | Source |
|------|---|----------|-----|--------|
| **CodeMigrator** | 6 | 120.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| DepUpgrader | 5 | 90.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| ImportPathFixWorm | 4 | 45.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| SchemaVersioner | 4 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |
| LegacyShimGen | 3 | 60.0s | 1.0.0 | ECOSYSTEM_EXPANSION.py |

**Key:** CodeMigrator (p=6) is the anchor — Python 2→3 migration with lib2to3 fixers. LegacyShimGen (p=3) is the lowest priority in this group — backward-compatibility wrappers for renamed APIs.

## DevOps Pipeline Architecture

```
container (orchestration)    communication (messaging)    migration (evolution)
    │                              │                            │
    ├─ ContainerOrch              ├─ MessageBroker             ├─ CodeMigrator (2→3)
    ├─ ComposeValidator           ├─ RPCEndpoint               ├─ DepUpgrader
    ├─ ImageAuditor               ├─ IPCBridge                 ├─ ImportPathFixWorm
    ├─ ResourceQuotaWatch         ├─ WebhookRelay              ├─ SchemaVersioner
    └─ RegistryPoller             └─ ProtocolNegotiator        └─ LegacyShimGen
         │                              │                            │
         └──────────────────────────────┴────────────────────────────┘
                                    │
                            WORM_REGISTRY (226 worms)
```

## Usage Pattern

```python
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Container health check
cluster = ClusterWORMZ.build_from_nature("container")
container_status = cluster.execute_all()

# Communication infrastructure test
cluster = ClusterWORMZ.build_from_nature("communication")
comms = cluster.execute_all()

# Migration audit
cluster = ClusterWORMZ.build_from_nature("migration")
migrations = cluster.execute_sequential()  # Sequential — migrations are destructive
```

## Related Skills
- `azazael-worms` — Full 77-worm catalog, registry API
- `azazael-worms-core` — Orchestration + utility + diagnostic worms
- `azazael-deploy` — Docker deployment, CLI packaging

Total: **15 DevOps worms** (container 5 + communication 5 + migration 5)
