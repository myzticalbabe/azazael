---
name: azazael-startup
description: Load this first in every Azazael session. Mandatory startup procedure, file-reading order, and complete 24-skill loading sequence. Start here before making any code changes.
metadata:
  category: workflow
  project: azazael
  priority: critical
---
# Azazael Startup — Mandatory Session Initiation

## 🔴 THIS SKILL MUST BE LOADED FIRST

Before writing any code, spawning any agent, or reading any file, execute the following in exact order:

### Step 1: Read the Three Canonical Files
```
read_files(["azazael/MEMORIES.md", "azazael/ERROR_LOG.md", "azazael/SYSTEM_INSTRUCTIONS.md"])
```

### Step 2: Verify External CLI Tools + Auto-Record Session Events (Mandatory)
```
# Records session_start + tooling_verify events in LocalMemoryStore (azazael-sop Rule 5)
python scripts/check_tooling.py
```

The checker (`scripts/check_tooling.py`) verifies:
- CLI tools: Python, Git, Node.js, npm, FreeBuff
- pip packages: Pillow, psutil, psycopg2, numpy
- npm globals: freebuff, pnpm, node-gyp
- Python 3.14t paths
- `freebuff_ready` events in LocalMemoryStore
- **Auto-records** `session_start` + `tooling_verify` events via CodebuffTracker

**Every Codebuff session MUST record in LocalMemoryStore:**
- `session_start` — auto-done by check_tooling.py
- `tooling_verify` — auto-done by check_tooling.py
- `session_end` — call at session completion using `CodebuffTracker.record_session_end()`
- **ALL file edits, creates, deletes, code reviews, test runs, milestones** — via CodebuffTracker dedicated methods

See **azazael-sop Rule 5** for the complete session recording mandate.

### Step 3: Load Core Skills (in order)
```
skill("azazael-error-prevention")  # Anti-patterns, DO-NOT-REPEAT list
skill("azazael-sop")               # Error recording SOP, pre-commit checklist
skill("azazael-environment")       # Python 3.10+/3.14t, deps, path setup
skill("azazael-architecture")      # Project layout, key numbers
skill("azazael-testing")           # Validation commands, canonical checklist
```

### Step 4: Load Architecture Skills
```
skill("azazael-registry")          # Worm registry API, @register_worm
skill("azazael-paths")             # Path resolution, get_project_root
skill("azazael-files")             # File index, import resolution
skill("azazael-threading")         # 3.14t threading patterns
skill("azazael-mermaid")           # Mermaid graph generation
```

### Step 5: Load Domain Skills (Decision Table)

**Load only what's relevant to your task. Don't load all 12.**

| If you're working on... | Load... |
|--------------------------|---------|
| Any worm code | `azazael-worms` (parent overview), then the specific sub-skill below |
| orchestration, utility, diagnostic worms | `azazael-worms-core` (15 worms) |
| monitor, profiling, telemetry worms | `azazael-worms-monitor` (16 worms) |
| security, config, backup worms | `azazael-worms-security` (15 worms) |
| container, communication, migration worms | `azazael-worms-devops` (15 worms) |
| learning, ml, analysis, visualization, sync | `azazael-worms-data` (16 worms) |
| ClusterWORMZ, NatureClusters, MetaCluster | `azazael-clusters` |
| Parallel execution, 3.14t optimization | `azazael-parallel` |
| CODEX video, PAMS/MemoryBus | `azazael-codex` |
| Python coding style, patterns | `azazael-conventions` |

### Step 6: Load Planning Skills (Decision Table)

| If you're working on... | Load... |
|--------------------------|---------|
| Production gaps, roadmap | `azazael-production` |
| Committing or branching | `azazael-git` |
| Docker, CLI packaging, deployment | `azazael-deploy` |

## Complete Skill Catalog (24 Skills)

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

`freebuff_ready` events are recorded in LocalMemoryStore for cross-session continuity. Query them dynamically:
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
| Skills available | 24 |

## Error Recording SOP

When ANY error occurs: **PAUSE → RECORD in azazael/ERROR_LOG.md → VERIFY fix → PROCEED**

Record: timestamp, severity (🔴/🟡/🟢), file path, root cause, fix solution, prevention rule.
