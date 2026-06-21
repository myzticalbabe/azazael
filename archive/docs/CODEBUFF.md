# CODEX BUFF — Project Configuration & Mandatory Startup

## 🚨 EVERY SESSION MUST START WITH THIS

**Assistant, before you do ANYTHING else, load the startup skill:**

```
skill("azazael-startup")
```

This skill will instruct you to read the canonical files and load all necessary domain skills in the correct order.

**User, to enforce this, start every Codebuff session by saying:**

> "Load skill azazael-startup before doing anything."

## Complete Skill System — 24 Skills

### Workflow (1)
| Skill | Purpose |
|-------|---------|
| `azazael-startup` | **Mandatory first skill** — startup procedure, 24-skill catalog |

### Quality (3)
| Skill | Purpose |
|-------|---------|
| `azazael-error-prevention` | 7 anti-patterns, DO-NOT-REPEAT list |
| `azazael-sop` | Error recording SOP, pre-commit checklist |
| `azazael-testing` | Validation commands, canonical checklist |

### Architecture (13)
| Skill | Purpose |
|-------|---------|
| `azazael-architecture` | Project layout, key numbers |
| `azazael-registry` | Worm registry API, @register_worm |
| `azazael-paths` | Path resolution, get_project_root |
| `azazael-files` | File index, import resolution |
| `azazael-threading` | 3.14t threading patterns (Lock, Event, Queue) |
| `azazael-mermaid` | Mermaid graph generation patterns |
| `azazael-worms` | **Parent:** 77 worms, 17 categories |
| `azazael-worms-core` | orchestration + utility + diagnostic (15 worms) |
| `azazael-worms-monitor` | monitor + profiling + telemetry (16 worms) |
| `azazael-worms-security` | security + config + backup (15 worms) |
| `azazael-worms-devops` | container + communication + migration (15 worms) |
| `azazael-worms-data` | learning + ml + analysis + viz + sync (16 worms) |
| `azazael-clusters` | ClusterWORMZ, NatureClusters, MetaCluster |
| `azazael-parallel` | 3.14t parallel execution optimization |

### Domain (3)
| Skill | Purpose |
|-------|---------|
| `azazael-codex` | CODEX video, PAMS/MemoryBus |
| `azazael-conventions` | Python coding patterns, style |
| `azazael-environment` | Python 3.10+/3.14t, deps, path setup |

### Conventions & Planning (4)
| Skill | Purpose |
|-------|---------|
| `azazael-git` | Commit conventions, branching |
| `azazael-deploy` | Docker, CLI packaging, scheduling |
| `azazael-production` | 12-section production roadmap |

## Why This Exists

Previous Codebuff sessions on this project repeatedly made the same 15+ preventable mistakes:
- JSON escaping errors in tool calls (3 occurrences)
- Unicode emoji crashing Windows terminals (3 occurrences)  
- Python f-string backslash syntax errors (2 occurrences)
- Factory methods using cls.__new__() bypassing __init__ (1 occurrence)
- Imports inside function bodies (1 occurrence)
- Temp files accumulating in repo (multiple occurrences)
- Unused imports accumulating (multiple occurrences)

Each mistake was recorded, diagnosed, and fixed. Each has a verified prevention rule.

## Canonical Files

| File | Contents |
|------|----------|
| `azazael/MEMORIES.md` | Anti-pattern catalog, architectural knowledge, decisions (canonical) |
| `azazael/ERROR_LOG.md` | Raw error ledger — 15 entries with timestamps, root causes, fixes, prevention |
| `azazael/SYSTEM_INSTRUCTIONS.md` | Mandatory SOP — record every error BEFORE proceeding |

**Skipping these files means repeating these mistakes. Read them.**
