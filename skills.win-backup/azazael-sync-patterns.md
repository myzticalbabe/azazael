---
name: azazael-sync-patterns
description: Sync infrastructure — sync_all.py and sync_skills.py patterns. 5 environments, 178+ files, integrity checks, environment topology. Critical for multi-environment propagation.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: true
---

# Azazael Sync Patterns — Multi-Environment Propagation

> **Implementation:** `azazael/scripts/sync_all.py`, `azazael/src/SCRIPTS/sync_skills.py`
> **5 environments:** Windows 11, WSL2 Ubuntu-26.04, Desktop Standalone, G: source-of-truth, G: AZAZAEL_ROOT

---

## Environment Topology

| # | Environment | Role | .py Files | Docs | Status Check |
|---|-------------|------|:---------:|:----:|:------------:|
| 1 | **Windows 11** (primary dev) | Development & source of truth | 367 | 47 | `sync_all.py --status` |
| 2 | **WSL2 Ubuntu-26.04** | Linux testing environment | 319 | 47 | `sync_all.py --status` |
| 3 | **Desktop Standalone** (release) | .exe distribution | 52 .exe | 47 | `sync_all.py --status` |
| 4 | **G: source-of-truth** (archive) | Canonical archive | 356 | 47 | `sync_all.py --status` |
| 5 | **G: AZAZAEL_ROOT** (archive) | Full project archive | 635 | 47 | `sync_all.py --status` |

## Sync Scripts

### sync_skills.py — Propagate Skills to .agents/

```bash
python azazael/src/SCRIPTS/sync_skills.py
python azazael/src/SCRIPTS/sync_skills.py --dry-run --verbose  # Check drift
```

**Purpose:** Copies `azazael/skills/*.md` → `.agents/skills/<name>/SKILL.md`
**Trigger:** RULE 0R — MUST run after every canonical skill change
**Output:** Shows UPDATED/UNCHANGED per skill, 106 skills total

### sync_all.py — Propagate to All Environments

```bash
python azazael/scripts/sync_all.py --status          # Check all environments
python azazael/scripts/sync_all.py --sync-to wsl2     # Sync Windows → WSL2 only
python azazael/scripts/sync_all.py --sync-all         # Sync to ALL environments
```

**Purpose:** Copies source code + docs from Windows to all 4 remote environments
**Sync patterns:**
- **Code patterns** (`SYNC_CODE_PATTERNS`): src/CORE/*.py, tests/*.py, scripts/*.py, etc.
- **Script patterns** (`SYNC_SCRIPT_PATTERNS`): scripts/*.py
- **Docs patterns** (`SYNC_DOC_PATTERNS`): azazael/*.md, azazael/skills/*.md

## Typical File Counts

| Sync Direction | Files |
|----------------|:-----:|
| Windows → WSL2 (code + docs) | ~178 |
| Windows → G: paths (docs only) | ~58 |
| Windows → Desktop (docs only) | ~58 |

## Integrity Check

`sync_all.py --status` runs a **subset check** (`win_tests.issubset(wsl_tests)`):
- Passes even if WSL2 has **extra legacy files** (7 legacy test files, `klink.py`)
- Fails if **any Windows file is missing** from a remote environment
- Output: `ALL SYNCED` or identifies which environments are OUT OF SYNC

## RULE 0R: Skills Propagation Mandate

**Trigger:** Any skill file in `azazael/skills/` is modified
**Action:** MUST run `sync_skills.py` in the same session
**RULE 0R Automation:** Runs at session startup via `azazael-system-startup` Step 2.5

## Related Skills

- `azazael-system-startup` — Step 2.5 auto-runs sync at session start
- `azazael-sop` — RULE 0R codification
- `azazael-testing` — Pre-commit checklist includes sync verification
