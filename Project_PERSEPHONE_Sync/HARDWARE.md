# Hardware Requirements — Project PERSEPHONE Sync

## Reference platform (the machine the work was done on)

| Component | Specification |
|-----------|---------------|
| **CPU** | Intel Core Ultra 9 285H (16 cores, 22 threads) |
| **iGPU** | Intel Arc 140T (8 GB shared VRAM) |
| **RAM** | 32 GB LPDDR5x-8533 (dual channel) |
| **OS** | Windows 11 Pro 24H2 (build 26100) |
| **Python** | 3.14.7 (free-threaded) / 3.15.0rc3 (free-threaded) |

This table describes where the code was written. It is **not** a validated
configuration, and nothing in this tree was benchmarked for this document.

## What this component needs

| Component | Requirement | Source |
|---|---|---|
| Python | 3.10+ | `tools/PERSEPHONE/lib/*.py` |
| OS | Windows and/or WSL2 Ubuntu; the library exists to bridge them | `tools/PERSEPHONE/lib/path_manager.py` |
| `rsync`, `ssh` | for the transfer paths | `tools/PERSEPHONE/sync_azazael_wsl.sh` |
| GPU | none | this component moves files |

Note that `tools/PERSEPHONE/requirements_wsl.txt` declares a very wide dependency
set — ML, web, database and cloud SDKs — because it was written as an environment
manifest for the whole tree, not as this component's own requirements. It is not a
statement of what the sync library needs.

## What was validated

Nothing was measured. No test file exists in this tree, so the safety criteria above
are open by construction rather than by oversight.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
