# Python Version Compatibility Matrix

## Azazael Ecosystem - Version Support

| Project | 3.6 | 3.7 | 3.8 | 3.9 | 3.10 | 3.11 | 3.12 | 3.13 | 3.14t | 3.15t | 3.16t |
|---------|-----|-----|-----|-----|------|------|------|------|-------|-------|-------|
| azazael (monorepo) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| azazael-core | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| eve-unleashed | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| edge0-intel | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| nurse-ratchet | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| flaming-sword | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| krampus | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| grantforge | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| wasm-education | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| codex-video-engine | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| eliza | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| persephone-sync | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| hydra-mlcluster | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| shardex | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| madi | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| jaeger | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| cradle | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| esquire-admissibility | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| scribe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ecosystem-orchestrator | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Legend
- ✅ = Fully tested and supported
- ❌ = Not supported / not tested

## Branch Strategy
- `main` / `py3.16t` - Production free-threaded (3.16t)
- `py3.15t` - Free-threaded GIL sidecar
- `py3.14t` - Original free-threaded target
- `py3.13` - Latest stable GIL
- `py3.12` - LTS
- `py3.11` - LTS
- `py3.10` - LTS
- `py3.9` - Legacy
- `py3.8` - Legacy
- `py3.7` - Legacy
- `py3.6` - Minimum

## Free-Threaded Notes
- Python 3.14t/3.15t/3.16t use free-threaded builds (no GIL)
- Requires native extensions built for free-threaded ABI
- Use `py3.15t` as GIL sidecar for packages without free-threaded wheels
- `azazael-core` provides interpreter-agnostic core
- `eve-unleashed` and `edge0-intel` require 3.15t+

## Installation Per Version

```bash
# Free-threaded (3.14t+)
pip install --index-url https://download.pytorch.org/whl/nightly/cpu torch  # if needed
pip install azazael-core

# GIL versions (3.6-3.13)
pip install azazael-core

# Development with specific version
py -3.10 -m pip install -e .
py -3.16t -m pip install -e .
```
