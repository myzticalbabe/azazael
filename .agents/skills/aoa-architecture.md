---
name: aoa-architecture
description: AOA (Armorie-of-Anubis) project architecture — umbrella orchestrator,
  quartet neural core (Azazael/CODEX/Eve/Libra), 9 arms, 5 support arms
  (incl. Kali Toolchain over WSL), 71 capabilities, cross-arm routing, event
  bus, session lifecycle, DirectMemory integration.
metadata:
  category: architecture
  projects: aoa, azazael, codex-studio, eve-unleashed, libra
---

# AOA — Armorie-of-Anubis Architecture

## Overview

AOA is the umbrella orchestrator v1.1.0 that wires together four independent
projects (Azazael, CODEX Studio, Eve Unleashed, Libra) plus five support arms
(including the Kali Toolchain arm over WSL) into a unified neural architecture.

### Key Numbers
- 9 arms (4 quartet + 5 support)
- 71 capabilities total (31 core/support + 40 Kali toolchain: 39 tools 1:1 + get_status)
- 56 cross-arm routes (computed dynamically at runtime from registry x capabilities; not a static table)
- 5 event priority levels
- Python 3.14.6 free-threaded
- 77 worms (via Azazael)

## Project Layout

```
Desktop/AOA/
├── AOA_STRUCTURE.html          # Architecture disclosure (7 Mermaid diagrams)
├── benchmark_data.json          # Live system metrics
├── build.py / build_final.py / build_disclosure.py  # HTML builder scripts (also gen_html.py, rebuild_html.py, inject.py)
├── core/
│   ├── arm_registry.py          # @register_arm, ARM_REGISTRY, discover_arms()
│   ├── event_bus.py             # EventPriority (LOW/NORMAL/MEDIUM/HIGH/CRITICAL)
│   ├── router.py                # CrossArmRouter, dynamic cross-arm routing (no static table)
│   └── session_manager.py       # Session lifecycle management
├── arms/
│   ├── azazael_arm.py           # AzazaelArm (p=10) — 77 worms, 17 categories
│   ├── codex_arm.py             # CodexArm (p=8) — HTML→MP4 rendering
│   ├── eve_arm.py               # EveArm (p=7) — AI model selector
│   ├── libra_arm.py             # LibraArm (p=9) — Legal automation
│   └── support_arms.py          # PAMS, PerfMon, Llama, AgentSelector
└── cli/
    └── aoa_cli.py               # cmd_init, cmd_arms_list, cmd_arms_status
```

## Quartet Neural Core (Priority 7-10)

| Arm | Priority | Category | Key Capability |
|-----|----------|----------|----------------|
| Azazael | 10 | orchestration | discover_worms, run_cluster |
| CODEX | 8 | rendering | render_mermaid, render_video |
| EveUnleashed | 7 | ai | select_model, run_inference |
| Libra | 9 | legal | generate_document, calculate_deadline |

## Support Arms (Priority 5-8)

| Arm | Priority | Category | Key Capability |
|-----|----------|----------|----------------|
| PAMS | 8 | memory | record_event, get_memories |
| PerfMon | 6 | monitoring | get_metrics (psutil) |
| LlamaServer | 5 | ai-server | infer, get_status |
| AgentSelector | 6 | routing | select_agent |

## Event System

### EventPriority Enum
```python
class EventPriority:
    LOW = 0
    NORMAL = 1
    MEDIUM = 1  # alias for NORMAL
    HIGH = 2
    CRITICAL = 3
```

### Cross-Arm Event Flow
PerfMon → PAMS → Azazael → Azazael → CODEX → MP4 output
(get_metrics → record_event → discover_worms → run_cluster → render_mermaid)

## Session Lifecycle

State machine: SESSION_INIT → ARM_DISCOVERY → ARM_INITIALIZE →
CAPABILITY_CHECK → READY (IDLE/EXECUTING/ERROR) → RENDERING →
SHUTDOWN → MILESTONE_RECORD

## Common Operations

### Arm Discovery (must import modules first!)
```python
import arms.azazael_arm, arms.codex_arm, arms.eve_arm
import arms.libra_arm, arms.support_arms, arms.kali_arm
from core.arm_registry import ArmRegistry
reg = ArmRegistry()  # Now has 9 arms (kali added 2026-09-02)
```

### CLI Commands
```bash
python -c "from cli.aoa_cli import cmd_init, cmd_arms_list
cmd_init(args); cmd_arms_list(args)"
```

## Integration Points

- **Azazael**: sys.path + subprocess (worm registry, cluster execution)
- **CODEX Studio**: subprocess (PIL+FFmpeg rendering)
- **Eve Unleashed**: subprocess (AI model benchmarks)
- **Libra**: sys.path (legal index/search)
- **PAMS**: DirectMemory import (SQLite event store)
- **PerfMon**: psutil (live system metrics)
- **Kali**: WSL bridge (wsl -d kali-linux) — 39 verified tool capabilities (see skill #1247 aoa-kali-arm)

## Known Issues

1. **CLI shows 0 arms** — cmd_init must import arm modules BEFORE ArmRegistry()
   to trigger @register_arm decorators
2. **EventPriority.MEDIUM crash** — Added MEDIUM=1 alias; code references MEDIUM
   but enum only had NORMAL

## Related Skills

- `aoa-html-builder` — Build professional Mermaid architecture disclosure HTML
- `azazael-architecture` — Azazael project structure (worms, clusters, paths)
- `azazael-clusters` — CLUSTERWORMS, MetaCluster routing
- `azazael-worms` — Full 77-worm catalog
- `azazael-mermaid` — Mermaid graph patterns (ASCII-safe, color, types)
- `azazael-crossplat-fileops` — Windows/Git Bash safe file operations
- `output/aoa_atlas/AOA_AUDIT_MAP.md` — 5-generation hash audit + 9-arm / 71-capability map (extracted from source; kali arm added 2026-09-02)
- `output/aoa_atlas/AOA_EVOLUTION_CATALOG.md` — Desktop-vs-gen-1 diff, +6 runtime capabilities cataloged

> Corrections applied 2026-09-01, verified against `src/AOA/` source (see AOA_LIBRA_GAP_CATALOG.md §1):
> `build_html.py` never existed (real set: build.py / build_final.py / build_disclosure.py / gen_html.py / rebuild_html.py / inject.py);
> Libra caps are `generate_document` etc., not `index_terms`/`search_dict`; Eve cap is `select_model`, not `select_agent`
> (that one lives on AgentSelector, where it is fully implemented, not a stub); Llama arm exposes `infer`/`get_status`
> (start/stop live as `Desktop/LlamaServer/` scripts); worms = 77 (17 categories); routes are runtime-derived.
