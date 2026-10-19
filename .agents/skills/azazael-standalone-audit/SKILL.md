---
name: azazael-standalone-audit
description: Desktop Standalone Suite audit — EXE inventory, BAT validation, build system health, naming conventions, error detection. Load when auditing or maintaining Desktop/AZAZAEL_Standalone.
---
# AZAZAEL Standalone Suite Audit Skill
## Overview
Systematic audit and maintenance procedures for the AZAZAEL Standalone Suite at `Desktop/AZAZAEL_Standalone/`.
**Version:** 1.0.0
**Created:** 2026-05-29 (Phase 19 Audit)
**Last Audit:** 2026-05-29
## Quick Health Check
```bash
# Count EXEs, BATs, check 0-byte files
echo "EXEs: $(ls -1 Desktop/AZAZAEL_Standalone/*_314t.exe 2>/dev/null | wc -l)"
echo "BATs: $(ls -1 Desktop/AZAZAEL_Standalone/*_314t.bat 2>/dev/null | wc -l)"
echo "0-byte: $(find Desktop/AZAZAEL_Standalone -name '*.exe' -size 0 | wc -l)"
echo "Old BATs: $(ls -1 Desktop/AZAZAEL_Standalone/*.bat 2>/dev/null | grep -v '_314t' | wc -l)"
```
## Audit Checklist
### 1. EXE Inventory
- [ ] All `_314t.exe` files exist and are > 5 MB (except known small ones)
- [ ] No 0-byte files
- [ ] EXEs match `build_all.py` MODULES keys
- [ ] Untracked EXEs identified and sourced
### 2. BAT Validation
- [ ] All BATs use `_314t` naming convention
- [ ] No old-style Python-launcher BATs (should call `.exe` directly)
- [ ] No `$path` template residue
- [ ] Every `_314t.exe` has a companion `_314t.bat`
- [ ] Every `_314t.bat` has a companion `_314t.exe` (no orphans)
- [ ] BAT content: `"%~dp0NAME_314t.exe" %*` pattern
### 3. Build System Health
- [ ] `build_all.py` MODULES dict matches on-disk `_314t.exe` names
- [ ] All source paths in MODULES resolve correctly
- [ ] `NEEDS_TKINTER` includes all GUI modules
- [ ] `NEEDS_PYTHONPATH` includes all CORE-dependent modules
- [ ] `regenerate_bats.py` ORPHANED set is up-to-date
### 4. Naming Conventions
- [ ] Module keys in build_all.py match EXE filenames (minus `_314t.exe`)
- [ ] No duplicate modules (e.g., `Changelog_Gen` / `Changelog_Generator`)
- [ ] External projects use correct relative paths from PROJECT_ROOT
## Known Issues (2026-05-29 Audit)
1. **4 small EXEs (< 5 MB):** Auto_Doc_Gen (4.1 MB), Changelog_Generator (4.1 MB), Complete_Systems (4.0 MB), Twitler_Analysis (3.8 MB) — may need dependency review
2. **Changelog_Gen vs Changelog_Generator:** Both exist on disk, build_all.py only tracks `Changelog_Generator`
3. **QL_Optimizer vs QL_File_Optimizer:** Disk uses `QL_Optimizer`, build_all.py fixed to match
4. **HYDRA_Bridge:** EXE exists (16.6 MB) but source path unclear — `HYDRAMETA_UV.py` or `HYDRA_CONTAINER.py`?
5. **Auto_Doc_Gen vs Auto_Doc_Generator:** Disk uses `Auto_Doc_Gen`, build_all.py fixed to match
6. **G: drive archive:** 39 old-style BATs archived to `G:/AZAZAEL/archive/old_bats_20260529/`
## Maintenance Procedures
### Adding a New Module
1. Add entry to `build_all.py` MODULES dict with correct source path
2. Determine if tk-inter plugin needed → add to NEEDS_TKINTER
3. Determine if PYTHONPATH needed → add to NEEDS_PYTHONPATH
4. Build: `python build_all.py MODULE_NAME`
5. Run: `python regenerate_bats.py` to create `.bat` launcher
### Removing a Module
1. Delete `MODULE_314t.exe` and `MODULE_314t.bat`
2. Remove from `build_all.py` MODULES dict
3. Add to `regenerate_bats.py` ORPHANED set if BAT lingers
### G: Drive Sync
- Source of truth: `G:/AZAZAEL/standalone/` — archive old files there
- Archive path: `G:/AZAZAEL/archive/old_bats_YYYYMMDD/`
- Run audit before syncing to G:
## Module Inventory (50 EXEs as of 2026-05-29)
| Tier | Count | Modules |
|------|-------|---------|
| Core Apps | 3 | CODEX_Studio, AZAZAEL_CLI, AZAZAEL_Toolkit |
| CODEX CORE | 8 | ASCII_Flowchart, Auto_Downloader, Emoji_Maker, Enhanced_Animations, File_Manifest, Changelog_Generator, Matrix_Animation, QL_Optimizer |
| Analysis | 5 | Complete_Systems, Twitler_Analysis, Animation_Protocols, Auto_Doc_Gen, Changelog_Gen |
| Toolkit | 4 | Azazael_Logger, Comprehensive_Fix, QL_Analysis, Math_Certainty, Environment_Manager |
| VIDEO | 4 | Create_Video, Matrix_Video, Compress_Video, Video_Popup |
| POPUPS | 4 | POPUP_Simple, POPUP_Clickable, POPUP_Immersive, POPUP_Bugfree |
| WORMS | 13 | BINARY_Analysis, CLOCKZ, CLUSTERWORMS, CONCURRENCY, DISKZ, ERROR_Scan, HEALING_WORM, METACLUSTER, NATURE_Clusters, NETWORK_Diag, NETWORXZ, OMNI_WORM, OS_Congruency, PROCESSZ, SMARTDISK |
| Orchestration | 3 | HYDRA, HYDRA_Analyzer, NODE |
| Standalone GUI | 2 | AZAZAEL_Inference_Studio, Eve_Unleashed |
| Unclear Source | 1 | HYDRA_Bridge |
**Version:** 1.1.0
**Measured state:** 2026-10-19 — see "Module Inventory" below. The 2026-05-29
numbers are HISTORICAL: **zero `.exe` files exist under
`Desktop/AZAZAEL_Standalone/` today**, so every EXE/BAT checkbox in this skill
audits artifacts that are not on disk. The checklist is kept as the target
shape, not as a description of the current tree.
> Annotated 2026-10-19: these boxes assume a built tree. With 0 `.exe` on disk
them all fail for one reason ("not built"), not for the reasons the wording
implies. Audit the BUILD first, then the artifacts.
> Historical: recorded against the 2026-05-29 tree. The items below describe
> EXEs that are no longer on disk; they are kept because they are still the
> expected shape of the next build (naming collisions, small binaries, unclear
> source). None can be re-measured until the suite builds again.
> **HISTORICAL — read the measurement first.** Measured 2026-10-19:
> `Desktop/AZAZAEL_Standalone/` holds **0 `.exe`** and **0 `.bat`**. What is
> there is build residue: `nuitka-crash-report.xml`, `build_eve_2026-08-27.log`,
> and `eve_unleashed_app.{build,dist}/`. The table below is the 2026-05-29
> inventory and is retained as the build TARGET, not as present state.
> Status of the suite itself is PLANNED / NOT BUILT: the Nuitka build fails on a
> transformers plugin (`azazael-standalone`, `SKILLS_CATALOG.md`).
>
> Consequence for the checklist above: sections 1, 2 and 3 cannot pass or fail
> today — they enumerate files that do not exist. Run the Quick Health Check
> first; if it prints 0/0/0/0, the audit is "not built", not "broken".
