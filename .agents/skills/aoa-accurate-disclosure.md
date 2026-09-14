---
name: aoa-accurate-disclosure
description: AOA Accurate Architecture Disclosure — source-code audited
  diagrams reflecting real 3-tier architecture, DreamingModule,
  MetaCognitionWorm, 17 worm categories, correct Quartet meaning.
  Created after audit found previous disclosure was inaccurate.
metadata:
  category: documentation
  projects: aoa, azazael
  audit_date: 2026-07-02
---

# AOA Accurate Architecture Disclosure

## Audit Background

Previous AOA_STRUCTURE.html + AOA_Structure_Disclosure.mp4 contained:
- Incorrect worm counts (101 vs actual 77)
- Invented architectural divisions (Core vs Support quadrant)
- Modified Quartet meaning (VF cross-platform paths, not arm grouping)
- Complete omission of DreamingModule, MetaCognitionWorm,
  HypnagogicSynthesizer, EvolutionEngine
- Understated arm capabilities

## Correct Architecture (Code-Verified)

### 3-Tier Cluster System
1. CLUSTERWORMS v2.0.0 — Dynamic worm resolution, parallel execution
2. NATURE_CLUSTERS — Auto-discovered 35 nature (category) groups
3. METACLUSTER — CrossNatureRoutingEngine (runtime-derived; engine computes routes dynamically via `get_routes_from()` — 70 routes / 594 paths is a measured snapshot, not a static table)

### 8 Wired Arms
| Arm | Priority | Real Capabilities (from source) |
|-----|----------|-------------------------------|
| Azazael | 10 | discover_worms, run_cluster, run_metacluster, get_status |
| Libra | 9 | list_templates, generate_document, get_filing_types,
  calculate_fees, calculate_deadline, get_status |
| CODEX | 8 | render_mermaid, render_video, get_status |
| PAMS | 8 | record_event, query_memories, get_milestones, get_status |
| EveUnleashed | 7 | select_model, run_benchmark, run_inference, get_status |
| PerfMon | 6 | get_metrics, get_status |
| AgentSelector | 6 | select_agent, get_status |
| LlamaServer | 5 | start_server, stop_server, get_status |

### 226 Worms, 35 Categories
35 categories: analysis, axon, backup, communication, config, consensus,
consolidation, container, defense, dendrite, diagnostic, engram, envmesh,
federated, glia, immune, learning, mesh, metabolic, migration, ml, monitor,
network, orchestration, plasticity, profiling, security, servemesh, synapse,
sync, telemetry, thalamus, utility, visualization, xenomorph

### Expansion Modules (CORE/WORMS/expansion/)
- DreamingModule — Tier 6 offline simulation (802 lines)
- MetaCognitionWorm — Self-reflection engine (830 lines)
- HypnagogicSynthesizer — Cross-domain pattern blending
- EvolutionEngine — Population-based optimization
- GeneticOptimizer — Selection/crossover/mutation per-worm
- RaceConditionDetector — 3.14t thread safety
- ErrorRecoveryOrchestrator — Autonomous error recovery

### Real Quartet Meaning
From worm_registry.py:102:
"VF (Vermillion LightFury) worm discovery — cross-platform
Quartet paths"

4 pillars with 8 canonical documents:
- Architecture: ARCHITECTURE.md, BUILD.md
- Operations: SYSTEM_INSTRUCTIONS.md, SESSION_STARTUP.md
- Knowledge: MEMORIES.md, LESSONS_MASTER.md
- Quality: ERROR_LOG.md, CODEBASE_AUDIT_TODO.md

## Build Strategy

Use the short-line heredoc strategy from aoa-html-builder skill:
- Every Python line under 100 characters
- String fragments joined at Python level via list.append
- Base64 can also work for very long lines
- Never use bare heredocs for Mermaid content on Windows Git Bash

## Verification Checklist
- [ ] 7 Mermaid diagrams render with correct classDef colors
- [ ] Zero JS errors in console
- [ ] DOCTYPE at position 0-1
- [ ] CDN script tag intact (no newline in URL)
- [ ] Stats match code: 226 worms, 35 cats, 70 routes, 594 paths (both route stats are runtime-derived snapshots, not constants)
- [ ] Arm capabilities match source arms/*.py
- [ ] DreamingModule pipeline shown
- [ ] MetaCognitionWorm loop shown
- [ ] Real Quartet (VF + 4 pillars) shown
- [ ] Corrections log table present
- [ ] Footer clean — no session artifacts
- [ ] Particle JS active
