# Hardware Requirements — Project Scribe

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
| Python | 3.10+ | `scribe.py`, `tools/*.py` |
| Network | required: the census fetches portal pages | `tools/portal_census.py` |
| Disk | must hold the page captures under `evidence/` | `evidence/` |
| GPU | none | this component writes documents |

## What was validated

Nothing was measured. The census is a claim about the world, not a performance
number, and the open criterion above is the one that matters: counts without stored
captures are assertions.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
