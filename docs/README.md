# Azazael Documentation Index

**Last Updated:** June 4, 2026 (Session: Neural Advancement + Worm Audit + Platform Deploy)

## Session Documents (June 4, 2026)

| Document | Description | Status |
|----------|-------------|--------|
| [LESSONS_SESSION_JUNE4.md](LESSONS_SESSION_JUNE4.md) | 10 lessons: injection pattern, FP precision, NSGA-II elitism, thread safety, auto-save, WSL2 sync, data-driven dreams | 🟢 v1.0.0 |
| [WORM_AUDIT.md](WORM_AUDIT.md) | Full audit of 38 worms: sub-agent capability, race conditions, error recovery, session persistence gaps | 🟢 v1.0.0 |
| [WORM_PROPOSALS.md](WORM_PROPOSALS.md) | 7 new worm proposals for 3.14t: RaceConditionDetector, ErrorRecoveryOrchestrator, SubAgentPoolManager, etc. | 🟢 v1.0.0 |
| [STANDALONE_BUILDS.md](STANDALONE_BUILDS.md) | 39 .exe build targets via Nuitka on Python 3.14t — per-worm build commands and batch strategy | 🟢 v1.0.0 |

## Conversion Plans

| Document | Description | Status |
|----------|-------------|--------|
| [RUST_CONVERSION_PLAN.md](RUST_CONVERSION_PLAN.md) | 5-phase plan converting 124K lines of Python to Rust crates | 🟢 v1.1.0 |
| [RUST_CONVERSION_TRACKER.md](RUST_CONVERSION_TRACKER.md) | Living progress dashboard tracking Rust conversion + Python progress | 🟢 v1.0.0 |

## Multi-Platform

| Document | Description |
|----------|-------------|
| [PLATFORM_DEPLOYMENT.md](../PLATFORM_DEPLOYMENT.md) | 4-platform deployment TODO: Windows 11, WSL2, Bare Metal Ubuntu 26.04, Kali Linux |
| [LESSONS_PLATFORM.md](../LESSONS_PLATFORM.md) | Platform-specific lessons: paths, G: drive, free-threading, case sensitivity, WSL2 perf |
| [MEMORIES_PLATFORM.md](../MEMORIES_PLATFORM.md) | Anti-patterns: G: drive assumptions, WSL2/Windows separation, case sensitivity |
| [PROJECT_STRUCTURES.md](../PROJECT_STRUCTURES.md) | Directory templates per platform with rsync sync strategy |

## Architecture & Specs

| Document | Description |
|----------|-------------|
| [architecture/7-tier-system.md](architecture/7-tier-system.md) | GOSP 7-tier DoctoralThesisEngine architecture |
| [specs/GOSP-specification.md](specs/GOSP-specification.md) | GOSP specification |

## Academic

| Document | Description |
|----------|-------------|
| [academic/doctoral-thesis-blueprint.md](academic/doctoral-thesis-blueprint.md) | Doctoral thesis blueprint |
| [academic/review-framework.md](academic/review-framework.md) | Academic review framework |

## Project Governance

| Document | Description |
|----------|-------------|
| [ARCHITECTURE_DECISION_RECORDS.md](ARCHITECTURE_DECISION_RECORDS.md) | Architecture Decision Records |
| [TASK_REGISTRY.md](TASK_REGISTRY.md) | Task registry and tracking |
| [CHANGELOG.md](CHANGELOG.md) | Project changelog |
| [INSTALL_GUIDE.md](INSTALL_GUIDE.md) | Installation guide |

## Master Task Tracking

| Document | Description |
|----------|-------------|
| [MASTER_TASKS.md](../MASTER_TASKS.md) | 10-lesson sequential plan for Python 3.14t development |

## Source of Truth

All canonical documents reside at: **`G:/source-of-truth/`**

- `MANIFEST.json` — Master manifest of all source-of-truth entries
- `azazael/` — Azazael project mirror
- `GOSP/` — GOSP Rust project (in conversion)
