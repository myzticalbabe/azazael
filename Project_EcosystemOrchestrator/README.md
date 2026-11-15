# Project Ecosystem Orchestrator

**ML platform installation and orchestration — the ECOSYSTEM-ORCHESTRATOR component of the Azazael tree.**

## Overview

ECOSYSTEM-ORCHESTRATOR manages the deployment, configuration, and operation of the Azazael ML platform across environments. It handles service lifecycle, dependency resolution, and health monitoring.

## Components

| Component | Role |
|-----------|------|
| `orchestrator/deploy/` | Service deployment, config templating, rollout |
| `orchestrator/lifecycle/` | Start/stop/restart, health checks, drain |
| `orchestrator/resolve/` | Dependency graph, version pinning, conflict resolution |
| `orchestrator/observe/` | Metrics, logs, traces, alerting integration |

## Quickstart

```bash
python -m pytest tests/ -q
python -m orchestrator.deploy --plan platform.yaml
```

## License

This project is licensed under the **Soul Forge License v1.0** — a covenant, not a
contract. The full text is in [LICENSE](LICENSE).

You may use, copy, modify, merge, publish, distribute, sublicense and/or
sell copies of the software, provided you keep the maker's mark intact,
do not wrap the code in DRM or obfuscation, and return your modifications
under this same license.

```
    Soul Forge License v1.0
    Author: myzticalbabe
    Forged: 2026-11-14
    Source: https://github.com/myzticalbabe/Project_EcosystemOrchestrator
    Spirit: "Code is crystallized intention. Tend the fire."
```

Author: myzticalbabe · Forged: 2026-11-14 · Spirit: "Code is crystallized intention. Tend the fire."

## Related Repositories

| Repo | Description | Status |
|------|-------------|--------|
| azazael | Monorepo: worm registry, cluster system, agent harness | Active |
| azazael-core | Installable, interpreter-agnostic repackaging | Active |
| nurse-ratchet | Behavioural package: person state modelled | Active |
| esquire-admissibility | AI-evidence admissibility gates | Active |
| cradle | Composition over FLAMING SWORD, REAPER, GRIMOIRE | Active |
| jaeger | Durable spans, JSONL ledger, stdlib only | Active |
| madi | Browsing instrument: fetch, challenge taxonomy, scorer | Active |
| grantforge | AI-native grant tooling | Active |
| krampus | Composition: MellifluousML, Madi, Gamora, Eve, Lilith | Active |
| shardex | Shard execution engine | Active |
| flaming-sword | Defensive instrument: sentinel, compliance, formal verification | Active |
| hydra-mlcluster | Adaptive ML cluster processing | Active |
| persephone-sync | Cross-platform env sync | Active |
| scribe | Documentation generation | Active |
| ecosystem-orchestrator | ML platform install/orchestration | Active |
| codex-video-engine | CODEX Studio desktop app + video engine | Active |
| eliza | Companion runtime: shards, adopted trees | Active |
| EveUnleashed | Gamora, Lucy, Jaeger, Berzerker AIO native on 3.16t | Active |
| wasm-education | WASM Education Platform | Active |
| myzticalbabe.github.io | Landing Hub + Domain Atlas | Active |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Links

- **Monorepo**: https://github.com/myzticalbabe/azazael
- **Landing Hub**: https://myzticalbabe.github.io
- **Domain Atlas**: https://myzticalbabe.github.io/index.html