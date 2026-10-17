---
name: azazael-desktop-projects
description: Complete Desktop project inventory and operability audit — 14 projects, 3 operational, 5 partial, 6 deprecated
metadata:
  category: planning
  project: azazael
  priority: high
---

# AZAZAEL — Desktop Projects Inventory & Audit

## Overview

This skill documents every project on the Desktop — their structure, entry points, dependencies, operability status, and relationship to the main AZAZAEL codebase.

**Canonical reference:** `azazael/DESKTOP_PROJECTS_AUDIT.md` (the detailed report)
**Last audit:** May 29, 2026 — Phase 15

---

## Quick Reference

| # | Project | Type | Status |
|---|---------|------|--------|
| 1 | **AZAZAEL_Standalone** | AZAZAEL | ✅ 49 EXEs operational |
| 2 | **azazael** (C:\Users\clint\azazael) | AZAZAEL | ✅ Source code, 292 files |
| 3 | **PAMS** | AZAZAEL | ✅ Memory/event system |
| 4 | **EveUnleashed_Selector** | External | ⚠️ Multi-agent framework |
| 5 | **PerformanceMonitor** | External | ⚠️ Go+Rust+Python |
| 6 | **Ultimate_Agent_Selector** | External | ⚠️ Agent orchestrator |
| 7 | **WSL_CrossExplorer** | External | ⚠️ Web file explorer |
| 8 | **WSL Models** | External | ⚠️ WSL LLM launchers |
| 9 | **agent_system** | External | ❌ Skeletal stub |
| 10 | **SysTools_JSON_Converter** | External | ❌ Data only |
| 11 | **Azazael_UNIFIED** | AZAZAEL | ❌ Old project copy |
| 12 | **CODEX** | AZAZAEL | ❌ Old output data |
| 13 | **CODEX_Studio_Output** | AZAZAEL | ❌ Old video output |
| 14 | **METAWORMS** | AZAZAEL | ❌ Old output data |

---

## AZAZAEL-Owned Projects (6)

### 1. AZAZAEL_Standalone ✅
- **Path:** `Desktop/AZAZAEL_Standalone/`
- **Contents:** 49 `_314t.exe` files, 46 `.bat` launchers, `build_all.py`, `regenerate_bats.py`
- **Dependencies:** None (self-contained Nuitka EXEs)
- **Build:** `python build_all.py` (requires Python 3.14t, Nuitka patched via `patch_nuitka_314t.py`)
- **Key files:** `build_all.py` orchestrates all 49 EXE builds; `regenerate_bats.py` fixes BAT launchers

### 2. azazael (Main Project) ✅
- **Path:** `C:\Users\clint\azazael/`
- **Contents:** `src/` (292 .py files), `packages/azazael-core/`, `skills/` (24 skills), documentation
- **Entry:** `AZAZAEL_LAUNCHER.bat` (14-menu launcher v5.0.1), `azazael.ps1`
- **Dependencies:** Python 3.14t (preferred), 3.10+ (minimum)
- **G:/ Backup:** `G:/AZAZAEL/AZAZAEL_ROOT/src/`

### 3. PAMS ✅
- **Path:** `Desktop/PAMS/`
- **Contents:** `benchmark_pams.py`, `src/server/pams_server.py`, `config/memory_config.json`
- **Dependencies:** Python 3.10+
- **Role:** Performance & Memory System — event recording, MemoryBus

### 11. Azazael_UNIFIED ❌ (Deprecated)
- **Path:** `Desktop/Azazael_UNIFIED/`
- **Contents:** `ORCHESTRATION_UNIFIED/META/`, `ORCHESTRATION_UNIFIED/UTILITIES/`
- **Action:** Archive to `G:/AZAZAEL/` — partial Phase 14 archive may have left remnants

### 12. CODEX ❌ (Deprecated)
- **Path:** `Desktop/CODEX/`
- **Contents:** `DOCUMENTATION/`, `ENVIRONMENT_INFO.json`, `QTABLE.json`, `comprehensive/`
- **Action:** Archive to `G:/AZAZAEL/`

### 13. CODEX_Studio_Output ❌ (Deprecated)
- **Path:** `Desktop/CODEX_Studio_Output/`
- **Contents:** `validation_scenes.mp4`, `validation_scroll.mp4`, `validation_wmv.wmv`
- **Action:** Archive to `G:/AZAZAEL/`

### 14. METAWORMS ❌ (Data only)
- **Path:** `Desktop/METAWORMS/`
- **Contents:** `output/*.json`, `reports/metaworms_report.html`
- **Action:** Archive to `G:/AZAZAEL/` or delete

---

## External Projects (8)

### 4. EveUnleashed_Selector ⚠️
- **Path:** `Desktop/EveUnleashed_Selector/`
- **Package:** `rani-vl` v1.0.0 — Multi-modal vision-language agent framework
- **Entry:** `setup.py`, `DESKTOP_SELECTOR_GUIDE.md`
- **Stack:** Python 3.11+, numpy, Pillow, requests + optional llama/ollama/transformers/vision
- **Structure:** agents/, build/, config/, tests/, docs/, scripts/
- **Integration potential:** High — agent types can map to AZAZAEL worm categories

### 5. PerformanceMonitor ⚠️
- **Path:** `Desktop/PerformanceMonitor/`
- **Brand:** "Ultraviolet Performance Nexus"
- **Entry:** `start.bat` orchestrates all 4 services
- **Stack:** Go (WebSocket hub) + Rust (sysinfo) + Python (Flask) + HTML (frontend)
- **Dependencies:** Go 1.21+, Rust, Python 3.14t
- **Integration potential:** High — telemetry -> AZAZAEL SystemZ/NETWORXZ worms

### 6. Ultimate_Agent_Selector ⚠️
- **Path:** `Desktop/Ultimate_Agent_Selector/`
- **Entry:** `launcher/agent_orchestrator.py`
- **Registry:** `config/agent_registry.json` (7 agent types)
- **Stack:** Python + Go/Rust scaffolding (empty)
- **Integration potential:** Medium — MemoryBridge -> PAMS event recording

### 7. WSL_CrossExplorer ⚠️
- **Path:** `Desktop/WSL_CrossExplorer/`
- **Entry:** `src/wsl_explorer_server.py` + `frontend/index.html`
- **Stack:** Python backend + HTML/CSS frontend
- **Dependency:** WSL context required
- **Integration potential:** Low

### 8. WSL Models ⚠️
- **Path:** `Desktop/WSL Models/`
- **Entry:** `1CLICK_VERIFIED_LAUNCH_gemma.bat` (llama-cli + Gemma 4 GGUF)
- **Dependencies:** WSL, llama-cli, GGUF models
- **Integration potential:** Medium — add to AZAZAEL_LAUNCHER menu

### 9. agent_system ❌
- **Path:** `Desktop/agent_system/`
- **Contents:** 3 empty `__init__.py` files (api_agent, data_handler, utils)
- **Decision needed:** Develop into real agent system or delete

### 10. SysTools_JSON_Converter ❌
- **Path:** `Desktop/SysTools_JSON_Converter/`
- **Contents:** `ExportReport.csv`, `grants_data/`
- **Decision needed:** Archive or keep (data only, no executable code)

---

## Loose Desktop Scripts

### Launchers
- `AZAZAEL_LAUNCHER.bat` — v5.0.1 14-menu ecosystem launcher
- `azazael.ps1` — PowerShell launcher (defaults to `status` command)
- `CODEX_Studio.bat` / `CODEX_Studio_Launcher.bat` — CODEX Studio launchers

### Model/Inference Utilities
- `llama_client.py` — OpenAI-compatible llama server interface
- `full_inference_test.py` — Multi-backend inference test
- `max_ctx.py` — GGUF metadata extractor
- `probe_all.py` / `probe_model.py` — LM Studio model scanners
- `create_memories.py` — Vector embeddings

### Build Scripts
- `build_llama_all_backends.bat` — Multi-backend llama build
- `build_tensorflow_intel.bat` — Intel TensorFlow build
- `install_nvidia_ncg_python314.bat` — NVIDIA NCG install
- `test_oneapi.bat` — Intel oneAPI test
- `launch_llama_stack.ps1` — LLaMA Stack launcher

### Documentation
- `AZAZAEL_MASTER.md`, `AZAZAEL_IMPROVEMENTS.md`, `AZAZAEL_STANDALONE_GUIDE.md`
- `CODEX_COMPLETE_SUMMARY.md`, `ENVIRONMENT_WIRING_PLAN.md`
- `NEXT_STEPS_FULL_WIRING.md`, `PAMS_INCOMPATIBLE_FILES.md`, `SESSION_REFLECTION.md`

---

## Cross-Project Wiring Plan

### Priority 1: Archive Deprecated Projects
```
Azazael_UNIFIED  -> G:/AZAZAEL/Desktop_Azazael_UNIFIED_archive_2026-05-29/
CODEX            -> G:/AZAZAEL/Desktop_CODEX_archive_2026-05-29/
CODEX_Studio_Output -> G:/AZAZAEL/Desktop_CODEX_Studio_Output_archive_2026-05-29/
METAWORMS        -> G:/AZAZAEL/Desktop_METAWORMS_archive_2026-05-29/
```

### Priority 2: Wire Active External Projects
1. Add EveUnleashed_Selector to AZAZAEL_LAUNCHER menu
2. Connect PerformanceMonitor telemetry to SystemZ/NETWORXZ worms
3. Wire Ultimate_Agent_Selector MemoryBridge to PAMS event recording
4. Add WSL Models launchers to AZAZAEL_LAUNCHER menu

### Priority 3: Clean Up Stubs
1. Decide: develop or delete `agent_system`
2. Archive `SysTools_JSON_Converter` data
3. Consolidate loose scripts into `tools/`

---

## Audit Commands

### List All Desktop Projects
```bash
ls -d /c/Users/clint/Desktop/*/ 
```

### Check Project Structure
```bash
find /c/Users/clint/Desktop/PROJECT_NAME -name "*.py" -o -name "*.md" -o -name "*.json" | head -20
```

### Find Entry Points
```bash
find /c/Users/clint/Desktop/PROJECT_NAME -name "*.bat" -o -name "setup.py" -o -name "main.*" -o -name "server.py"
```
