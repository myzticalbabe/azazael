---
name: azazael-standalone
description: AZAZAEL Standalone Suite — 39 independent .exe files for every AZAZAEL function, built with Nuitka. Zero-dependency Windows 11 executables.
---

# AZAZAEL Standalone Suite Skill

## Overview
Every AZAZAEL function packaged as standalone Windows .exe files.
No Python required. No environment setup. Double-click to run.

**Location:** `Desktop/AZAZAEL_Standalone/`
**Version:** 3.1.0
**Total:** 39 .exe + 39 .bat launchers + build script + visual index

## Quick Reference

### Core Applications
| .exe | What it does |
|------|-------------|
| `CODEX_Studio.exe` | HTML→MP4/WMV video generator (GUI+CLI) |
| `AZAZAEL_CLI.exe` | Main terminal interface — bootstrap, worms, LLM |
| `AZAZAEL_Toolkit.exe` | All-in-one toolkit CLI |

### Build System
```bash
# Rebuild all (requires Python 3.14t)
python build_all.py

# Build single module
python build_all.py CODEX_Studio
```

### Packaging Approach
- **Compiler:** Nuitka 4.1.2 (patched for 3.14t, --standalone --onefile)
- **Build Python:** CPython 3.14.5t (free-threading)
- **Runtime:** 3.14.5t (same Python, free-threading)
- **Note:** Nuitka requires 9 C-level patches for 3.14t support. Run `docs/scripts/patch_nuitka_314t.py --apply` before building.

## Module Inventory
- **Tier 1:** Core Apps (3)
- **Tier 2:** CODEX CORE Utilities (8)
- **Tier 3:** Analysis + TOOLKIT (6)
- **Tier 4:** VIDEO Scripts (4)
- **Tier 5:** POPUPS GUI (4)
- **Tier 6:** WORMS Diagnostics (13)
