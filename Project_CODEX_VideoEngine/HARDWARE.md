# Hardware Requirements — Project CODEX Video Engine

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
| Node | any LTS; ES modules | capture dependencies in `tools/CODEX/package.json` |
| Chromium | downloaded/managed by Puppeteer | `puppeteer` ^19 |
| Python | the version in `tools/CODEX/TESTING/pyproject.toml` | that file |
| RAM | must hold whole video frames; capture is memory-bound, not CPU-bound | inferred from the capture model |
| GPU | not required; there is no hardware-encode step in this tree | — |

## What was validated

Nothing in this file was measured for this document. No render exists in the tree
with its parameters recorded, so there is no frame rate, duration or encode setting
to quote. The table above states dependencies, not performance.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
