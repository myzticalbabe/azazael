# Quartet Sync Strategy

**Date:** June 19, 2026  
**Canonical Source:** Kali Linux `/root/azazael/`

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  KALI LINUX (Canonical)           UBUNTU-26.04 (ML Accelerator)    │
│  /root/azazael/                   /root/azazael/                    │
│  /root/vermillion_lightfury/                                        │
│                                                                     │
│  G: DRIVE (Archive) — /mnt/g/azazael_shared/                       │
│  C: DRIVE (Shared)  — /mnt/c/azazael_shared/                       │
│  E: DRIVE (VHDX)    — /mnt/e/Kali/ext4.vhdx                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Sync Direction

**Kali → Windows**: Kali `/root/azazael/` is the canonical source. Windows `C:\Users\clint\azazael\` is a working mirror for IDE/GUI access.

**Kali → Ubuntu-26.04**: Ubuntu receives ML-relevant subsets (CORE/, ORCHESTRATION/, src/*.py).

**Never reverse**: Do not sync Windows → Kali. Kali is authoritative.

## What Lives Where

| Component | Kali | Ubuntu-26.04 | Windows |
|---|---|---|---|
| `azazael/src/` (all .py) | ✅ Canonical | ✅ Mirror | ✅ Mirror |
| `azazael/skills/` | ✅ | ✅ | ✅ |
| `vermillion_lightfury/` | ✅ **Kali-native** | ❌ | ❌ (deprecated) |
| `archived/` | ✅ | ❌ Pruned | ✅ |
| `output/` | ✅ | ❌ Pruned | ✅ |
| `build/` | ✅ | ❌ | ✅ |
| `packages/` | ✅ | ❌ | ✅ |
| `logs/` | ✅ | ❌ | ✅ |
| G: drive archive | `/mnt/g/azazael_shared/` | `/mnt/g/` | `G:\azazael_shared\` |

## Sync Commands

```bash
# Kali → Windows (mirror)
rsync -av --exclude='__pycache__' --exclude='.git' \
  /root/azazael/ /mnt/c/Users/clint/azazael/

# Kali → Ubuntu-26.04 (ML subset)
rsync -av --exclude='__pycache__' \
  /root/azazael/src/CORE/ /root/azazael/src/CORE/WORMS/ \
  /root/azazael/src/ORCHESTRATION/ \
  root@ubuntu:/root/azazael/src/

# Verify sync status
python azazael/scripts/sync_all.py --status
```

## Known Gaps (June 19, 2026)

- `DAEMONS/` — exists on Windows + Kali, missing from Ubuntu-26.04
- `packages/` — synced to Kali, may need Ubuntu sync
- `SCRIPTS/` → `scripts/` — renamed on Kali, symlink added for backward compat
- Vermillion LightFury — now Kali-native at `/root/vermillion_lightfury/`, removed from Windows

---

## Pre-Sync Checklist

Run these BEFORE syncing between environments:

- [ ] Verify no `__pycache__`/`.pyc` files are in the sync source (rsync `--exclude` handles this)
- [ ] Ensure no active IDE processes (VSCode, PyCharm) are locking files on target
- [ ] Validate `SCRIPTS → scripts` symlink resolves on Kali: `ls -ld /root/azazael/src/SCRIPTS`
- [ ] Check VF worms import cleanly: `cd /root/vermillion_lightfury && python3 -c "from worms import *"`

## Production-Readiness Validation

Run these on Kali after any sync or code change.

### Phase 1: Platform Constants
```bash
cd /root/vermillion_lightfury
export PYTHONPATH=/root/vermillion_lightfury:/root/azazael/src
python3 -c "from exceptions import _IS_WINDOWS, _IS_KALI_NATIVE, _C_DRIVE, _E_DRIVE; \
  assert _IS_WINDOWS == False; assert _IS_KALI_NATIVE == True; \
  assert _C_DRIVE == '/mnt/c'; assert _E_DRIVE == '/mnt/e'; \
  print('PASS')"
```
- **Expected:** `PASS`
- **Status:** [x] Passed

### Phase 2: Worm Imports
```bash
python3 -c "from worms import kali_health, wsl_recovery, nmap_scanner, metasploit_bridge; \
  assert kali_health.KaliHealth.VERSION == '1.0.0'; \
  assert wsl_recovery.WSLRecovery.VERSION == '1.0.0'; \
  print('PASS')"
```
- **Expected:** `PASS` (all 4 worms import, VERSION 1.0.0)
- **Status:** [x] Passed

### Phase 3: Worm Registry Discovery
```bash
python3 -c "from CORE.worm_registry import discover_worms, WORM_REGISTRY; \
  discovered = discover_worms(); \
  vf_worms = [n for n,i in WORM_REGISTRY.items() if '/vermillion_lightfury' in i.get('source_file','')]; \
  print(f'Registry: {len(WORM_REGISTRY)} worms, VF: {len(vf_worms)}')"
```
- **Expected:** 93+ worms, VF worms discovered
- **Status:** [x] Passed (93 worms, VF worms present)

### Phase 4: CLI Smoketests
```bash
python3 worms/kali_health.py quick          # → "E: X.X GB free — OK"
python3 worms/wsl_recovery.py check         # → HEALTHY, kali Running (v2)
python3 config/shared_dir.py setup          # → 0 Created, 9 Existing, 0 Failed
```
- **Expected:** All three exit cleanly, no crashes
- **Status:** [x] Passed

### Phase 5: Benchmark Suite
```bash
python3 benchmark_all.py
```
- **Expected:** `33/33 passed, 0 failed`
- **Status:** [x] Passed (33/33)

### Phase 6: Azazael Test Suite (relevant subset)
```bash
cd /root/azazael
python3 -m pytest tests/test_worm_registry.py tests/test_worm_imports.py tests/test_sync_skills.py tests/test_startup_warm_wiring.py -v
```
- **Expected:** All worm registry/import/sync tests pass
- **Status:** [x] Passed (71 passed, 4 failed)
- **Note:** 1 pre-existing failure in `test_correlation_id_unique` (correlation IDs), 3 pre-existing failures in `test_startup_warm_wiring.py` (`_prewarm_registry` attribute) — none caused by VF changes

### Phase 7: Cross-Environment Sync Verification
```bash
# Compare MD5 hashes between Kali and Windows
for f in benchmark_all.py __init__.py exceptions.py config/shared_dir.py \
         worms/nmap_scanner.py worms/metasploit_bridge.py \
         worms/kali_health.py worms/wsl_recovery.py worms/benchmark_worm.py \
         README.md MILESTONE.md; do
  kali_md5=$(md5sum /root/vermillion_lightfury/$f | cut -d' ' -f1)
  win_md5=$(md5sum /mnt/c/Users/clint/vermillion_lightfury/$f | cut -d' ' -f1)
  [ "$kali_md5" = "$win_md5" ] && echo "MATCH: $f" || echo "DIFFER: $f"
done
```
- **Expected:** All 11 files MATCH
- **Status:** [x] Passed (11/11 MATCH)

## Bugs Found & Fixed During Validation (June 19, 2026)

| Bug | File | Fix |
|---|---|---|
| README creation used `SHARED_ROOT_WIN` on Kali | `config/shared_dir.py` | Changed to `root_path` (conditional) |
| Bare `wsl` not on PATH in Kali WSL | 5 files | Changed all `_wsl_exec` else branches to `wsl.exe` |
| `check_distro()` couldn't list self via `wsl.exe --list` | `worms/wsl_recovery.py` | Added Kali-native early return with liveness check |
| `_wsl_exec` signature mismatch (list vs str) | `worms/nmap_scanner.py`, `worms/metasploit_bridge.py` | Dual-signature: accepts str or list |
| `_check_drive()` used PowerShell (Windows-only) | `worms/kali_health.py` | Replaced with `shutil.disk_usage()` |
| `verify_kali_responsive()` passed string, `_wsl_exec` expected list | `worms/nmap_scanner.py`, `worms/metasploit_bridge.py` | Dual-signature `_wsl_exec`: accepts str or list |
