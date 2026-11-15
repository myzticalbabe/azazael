# Hardware Requirements — Project Ecosystem Orchestrator

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
| Python | 3.10+ | f-strings and `from __future__` usage across `tools/ORCHESTRATION` |
| ML platforms | whatever the orchestrator is told to manage; none is bundled | `tools/ORCHESTRATION` |
| Network | required at run time: install and health checks talk to the platforms | — |
| GPU | not needed by the orchestrator itself | it schedules work, it does not run it |

## What was validated

Nothing here was measured. No dependency manifest (no `requirements.txt`, no
`pyproject.toml`) exists in this tree, so the Python version above is read from the
source's syntax rather than declared. That is a gap, not a specification.

## Development machine caveat

The same box appears in every tree's `HARDWARE.md`, because it is one machine. Its
presence here says nothing about whether this component runs on it.
