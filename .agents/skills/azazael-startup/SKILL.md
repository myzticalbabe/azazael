---
name: azazael-startup
description: Reference catalog for Azazael sessions. 24-skill catalog, environment setup, project numbers. Delegates startup execution to `skill("azazael-system-startup")`. Load first before any code changes.
metadata:
  category: workflow
  project: azazael
  priority: critical
---
# Azazael Startup — Reference Catalog

## 🔴 THIS SKILL MUST BE LOADED FIRST

## 🛑 PRE-ACTION GATE — PERMANENTLY ACTIVE

**THE PRE-ACTION GATE (RULE 0J) IS NOW ACTIVE.** Before EVERY `str_replace`, `write_file`, or `spawn_agents` call, you MUST print in your response text (NOT in a thinking/reasoning block):

```text
🛑 **[PRE-ACTION GATE ASSERTION]**
- **AP-1 (Scope Check):** Did the user explicitly ask for this EXACT change? (Explain)
- **RULE 0G (Gemini Phase):** Is this complex? Was thinker-with-files-gemini spawned for THIS phase? (Explain)
- **RULE 0H (Anti-Pattern Scan):** Scanned for emoji, backslash f-strings, t-strings, os.system, C:\ paths? (Passed/Found)
- **RULE 0I (Algorithms/Batch):** If batch script: Gemini designed? One-file test? Backup? (Yes/No/N/A)
- **GATE DECISION:** [PROCEED / HALT and ask user / HALT and spawn Gemini]
```

**FAILURE = 🔴 CRITICAL process violation (Error #146 precedent).**

---

## 🚀 Startup Execution — Delegates to `azazael-system-startup`

**The canonical startup procedure is executed by `azazael-system-startup`.** Load it now:

```
skill("azazael-system-startup")
```

This handles: RULE 0K 7-file reading, guardrail skills, FreeBuff/Bun check, DirectMemory init, domain skill guidance.

> **Note:** `azazael-system-startup` and `azazael-startup` were consolidated June 9, 2026. This skill is now a reference catalog; execution lives in `azazael-system-startup`.

## Complete Skill Catalog (25 Skills)

| # | Skill | Category | Purpose |
|---|-------|----------|---------|
| 1 | azazael-startup | workflow | **Mandatory first skill** |
| 2 | azazael-error-prevention | quality | 7 anti-patterns, DO-NOT-REPEAT |
| 3 | azazael-sop | quality | Error recording SOP, checklist |
| 4 | azazael-environment | domain | Python 3.10+/3.14t, deps |
| 5 | azazael-architecture | architecture | Project layout, key numbers |
| 6 | azazael-testing | quality | Validation commands, canonical checklist |
| 7 | azazael-registry | architecture | Worm registry API, @register_worm |
| 8 | azazael-paths | architecture | Path resolution, get_project_root |
| 9 | azazael-files | architecture | File index, import resolution |
| 10 | azazael-threading | architecture | 3.14t threading patterns |
| 11 | azazael-mermaid | domain | Mermaid graph generation |
| 12 | azazael-worms | architecture | Parent: 77 worms, 17 categories |
| 13 | azazael-worms-core | architecture | orchestration + utility + diagnostic (15) |
| 14 | azazael-worms-monitor | architecture | monitor + profiling + telemetry (16) |
| 15 | azazael-worms-security | architecture | security + config + backup (15) |
| 16 | azazael-worms-devops | architecture | container + communication + migration (15) |
| 17 | azazael-worms-data | architecture | learning + ml + analysis + viz + sync (16) |
| 18 | azazael-clusters | architecture | ClusterWORMZ, NatureClusters, MetaCluster |
| 19 | azazael-parallel | architecture | 3.14t parallel execution optimization |
| 20 | azazael-codex | domain | CODEX video, PAMS/MemoryBus |
| 21 | azazael-conventions | domain | Python coding patterns, style |
| 22 | azazael-git | conventions | Commit conventions, branching |
| 23 | azazael-deploy | planning | Docker, CLI packaging, scheduling |
| 24 | azazael-production | planning | 12-section production roadmap |
| 25 | azazael-eleven-followups | workflow | RULE 0Z-B: 11 followups mandate |

## Environment

### Python Version
**Python 3.10+ required** (some features use `match`/`case` and `|` union types).
**Python 3.14t** preferred for free-threading optimization.

### Key Dependencies
| Package / Tool | Purpose | Install | Package Manager |
|----------------|---------|---------|-----------------|
| `Pillow` (PIL) | CODEX video frame generation | `pip install Pillow` | pip (PyPI) |
| `psutil` | System monitoring worms | `pip install psutil` | pip (PyPI) |
| ffmpeg | CODEX .mp4 video encoding | `winget install ffmpeg` | winget |
| **FreeBuff** | AI coding agent (CLI) | `npm install -g freebuff` | **npm** (NOT pip!) |

### External CLI Tools (Verified June 2, 2026)
| Tool | Version | Package Manager | Verified |
|------|---------|-----------------|----------|
| Node.js | v24.14.0 | system | ✅ |
| npm | 11.9.0 | Node bundled | ✅ |
| FreeBuff | 0.0.100 | **npm** (not pip) | ✅ (`freebuff --version` works) |
| Python 3.14t | 3.14.5 | system | ✅ at `C:\...\Python314\python3.14t.exe` |

**🚨 CRITICAL: FreeBuff is NOT a pip package.** Do NOT try `pip install freebuff` with any Python (3.14t or otherwise) — it will fail with "could not find package."
**Correct install:** `npm install -g freebuff` (already done — v0.0.100 installed and working)
**Verify:** `freebuff --version`
**Usage:** `freebuff --continue [id] --cwd <dir>`

**Startup auto-verify:** Run the following at session start to confirm FreeBuff is available:
```
npm list -g freebuff 2>&1 && freebuff --version
```

`freebuff_ready` events are recorded via DirectMemory for cross-session continuity. Query them dynamically:
```
# In Python:
store.search_memories("freebuff_ready", source="Codebuff")

# Latest event includes: package_manager="npm (NOT pip)", pip_note, version
```

### Python 3.14t Package Note
Packages for 3.14t may need `--force-reinstall --no-deps` to get correct `cp314t` wheels (see Error #49 in ERROR_LOG.md).

### Project Path Setup
```python
import sys
sys.path.insert(0, 'azazael/src')  # Required before any imports
```

## Quick Start — Run Your First Worm
```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.worm_registry import discover_worms; discover_worms()
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ

# Run all monitor worms
cluster = ClusterWORMZ.build_from_nature("monitor")
results = cluster.execute_sequential()
print(f"{len(results)} worms executed")
for r in results:
    print(f"  {r['name']}: {'OK' if r.get('success') else 'FAIL'}")
```

## Why This Exists

Previous sessions repeatedly made 15+ preventable mistakes:
- JSON escaping errors in tool calls (3x)
- Unicode emoji crashing Windows terminals (3x)
- f-string backslash syntax errors (2x)
- cls.__new__() bypassing __init__
- Temp files accumulating in repo

**Every mistake is documented with root cause, fix, and prevention rule. Read them or repeat them.**

## Key Project Numbers (Quick Reference)

| Metric | Value |
|--------|-------|
| Total Python files | 256 (all syntax-clean) |
| Worms in registry | 77 |
| Categories | 17 |
| MetaCluster routes | 46 |
| MetaCluster paths | 264 |
| Worms from ECOSYSTEM_EXPANSION.py | 48 (62%) |
| Skills available | 25 |

## Error Recording SOP

When ANY error occurs: **PAUSE → RECORD in azazael/ERROR_LOG.md → VERIFY fix → PROCEED**

Record: timestamp, severity (🔴/🟡/🟢), file path, root cause, fix solution, prevention rule.
