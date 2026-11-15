# AZAZAEL Core

Standalone core package extracted from the AZAZAEL monorepo.

## What is azazael-core?

`azazael-core` is the foundational layer of the AZAZAEL Native Intelligence 
Artifacts platform. It provides:

- **Dynamic Path Resolution** — `paths.py` resolves project roots, desktop directories,
  G: drive mounts, and environment-specific paths without hardcoding.
- **Worm Registry** — `@register_worm` decorator, `WORM_REGISTRY` dict, `discover_worms()`,
  and category management for 77+ diagnostic worm classes.
- **Free-Threading Awareness** — Python 3.14t GIL-disabled support with 
  `FreeThreadPool`, `ThreadSafeDict`, and `ThreadSafeList`.
- **Configuration** — Centralized config loading with YAML/JSON support.
- **Circuit Breaker** — Failure isolation pattern for worm execution.

## Installation

```bash
pip install -e packages/azazael-core
```

Requirements: Python >= 3.14 (free-threading build, 3.14t)

## Quick Start

```python
from azazael_core import get_project_root, discover_worms, get_all_categories

# Resolve project paths dynamically
root = get_project_root()
print(f"Project root: {root}")

# Discover and inspect worms
discover_worms()
for cat in get_all_categories():
    print(f"  {cat}")
```

## CLI Usage

```bash
# After pip install:
azazael-core paths     # Show dynamic project paths
azazael-core registry  # List worm registry contents
azazael-core config    # Show current configuration
azazael-core version   # Print version info
```

## Building Standalone .exe

**Important:** Build with Python 3.14t (free-threading). Python 3.13 is not used.
Nuitka 4.1.2 requires patches for 3.14t support — run
`azazael/docs/scripts/patch_nuitka_314t.py --apply` before building.
Optional imports (torch, optree, openvino) must be excluded since they are
not available in the build environment.

```bash
pip install nuitka

# Apply 3.14t patches first:
python azazael/docs/scripts/patch_nuitka_314t.py --apply

# Build on 3.14t (default python):
python -m nuitka --standalone --onefile src/azazael_core/cli.py \
    -o azazael-core.exe \
    --nofollow-import-to=torch \
    --nofollow-import-to=optree \
    --nofollow-import-to=openvino
```

Result: ~6.8 MB compressed .exe (from ~21.8 MB uncompressed build tree).

## License

MIT — See LICENSE file in parent project.

## Related Repositories

| Repo | Description |
|------|-------------|
| [azazael](https://github.com/myzticalbabe/azazael) | Monorepo: worm registry, cluster system, agent harness |
| [EveUnleashed](https://github.com/myzticalbabe/EveUnleashed) | Gamora, Lucy, Jaeger, Berzerker AIO native on 3.16t |
| [eliza](https://github.com/myzticalbabe/eliza) | Companion runtime: shards, adopted trees |
| [codex-video-engine](https://github.com/myzticalbabe/codex-video-engine) | CODEX Studio desktop app + video engine |
| [ecosystem-orchestrator](https://github.com/myzticalbabe/ecosystem-orchestrator) | ML platform install/orchestration |
| [scribe](https://github.com/myzticalbabe/scribe) | Documentation generation |
| [persephone-sync](https://github.com/myzticalbabe/persephone-sync) | Cross-platform env sync |
| [hydra-mlcluster](https://github.com/myzticalbabe/hydra-mlcluster) | Adaptive ML cluster processing |
| [flaming-sword](https://github.com/myzticalbabe/flaming-sword) | Defensive instrument: sentinel, compliance, formal verification |
| [shardex](https://github.com/myzticalbabe/shardex) | Shard execution engine |
| [krampus](https://github.com/myzticalbabe/krampus) | Composition: MellifluousML, Madi, Gamora, Eve, Lilith |
| [azazael-core](https://github.com/myzticalbabe/azazael-core) | Installable, interpreter-agnostic repackaging |
| [grantforge](https://github.com/myzticalbabe/grantforge) | AI-native grant tooling |
| [madi](https://github.com/myzticalbabe/madi) | Browsing instrument: fetch, challenge taxonomy, scorer |
| [jaeger](https://github.com/myzticalbabe/jaeger) | Durable spans, JSONL ledger, stdlib only |
| [cradle](https://github.com/myzticalbabe/cradle) | Composition over FLAMING SWORD, REAPER, GRIMOIRE |
| [esquire-admissibility](https://github.com/myzticalbabe/esquire-admissibility) | AI-evidence admissibility gates |
| [nurse-ratchet](https://github.com/myzticalbabe/nurse-ratchet) | Behavioural package: person state modelled |
| [wasm-education](https://github.com/myzticalbabe/wasm-education) | WASM Education Platform |
| [myzticalbabe.github.io](https://github.com/myzticalbabe/myzticalbabe.github.io) | Landing Hub + Domain Atlas |
