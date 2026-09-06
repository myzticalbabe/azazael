# SKILL: azazael-wsl-canonical
# PURPOSE: WSL Canonical Environment Reference

Documents the WSL Ubuntu canonical environment at `/root/azazael/` — a Linux mirror of the Windows 11 production Azazael codebase at `C:/Users/clint/azazael/`. Use this skill when working in WSL sessions to understand environment differences.

## Environment Differences (WSL vs Windows)

### Python
| Property | Windows Production | WSL Canonical |
|----------|-------------------|---------------|
| **Python version** | 3.14.6t (free-threaded) | 3.14.4 (system python3) |
| **python3.14t** | Available | **NOT available** — use `python3` |
| **mypy** | Installed on 3.14t | Must install via `pip3 install mypy` |
| **psutil** | Installed | Must install via `pip3 install psutil` |
| **Nuitka** | Installed (4.1.2 patched) | Not installed |
| **pytest** | Installed | Not installed |

### Worm Execution
| Property | Windows | WSL |
|----------|---------|-----|
| **Monitor worms** | 2/9 pass | **6/6 pass** (DISKZ, NETWORXZ, PROCESSZ, SystemZ, DatabaseMonitorWorm, ScheduledDbMonitorWorm) |
| **DISKZ/NETWORXZ/PROCESSZ/SystemZ** | Pass on Windows | Need psutil installed |
| **SMARTDISK/OSCongruency/KaliHealth** | Windows-only APIs | Fail on Linux (expected) |
| **WORM_REGISTRY** | 104 keys, 18 categories | 91 keys (worm names as categories) |
| **discover_worms()** | Returns 99 | Returns 30 |

### Metrics (July 8, 2026)
| Metric | Windows Production | WSL Canonical |
|--------|-------------------|---------------|
| **.py files** | 481 | 481 |
| **Syntax check** | — | 481/481 clean |
| **CORE/ files** | 69→70 | 70 |
| **CORE/WORMS/ files** | 47 | 47 |
| **Skills** | 128 | 128 |
| **Tests** | 97 | 97 |
| **DirectMemory events** | 646,925 | 12,351 |
| **DirectMemory DB size** | 1,117.86 MB | 15.45 MB |
| **ERROR_LOG entries** | 138 | 138 |
| **Highest error ID** | #187 | #187 |

### Type Checking
| Property | Value |
|----------|-------|
| **Mypy on CORE/** | 322 errors across 89 files (python3.14 — Sessions 5-7: 416→322, -94, 6 graduated) |
| **Top error files** | learning_pipeline.py (51), providers.py (43), threading_utils.py (33) |
| **Command** | `cd azazael && python3 -m mypy src/CORE/ --ignore-missing-imports --explicit-package-bases` |
| **Pyright** | Not installed |

### G: Archive
| Property | Value |
|----------|-------|
| **Mount point** | `/mnt/g/` |
| **Source of truth** | `/mnt/g/AZAZAEL_SOURCE_OF_TRUTH/` |
| **To mount** | `mkdir -p /mnt/g && mount -t drvfs G: /mnt/g` |

### Compliance
| Component | WSL Status |
|-----------|-----------|
| **FormalVerifier** | Works correctly (4/4 default constraints) |
| **RULE 0J** | Properly detects missing PRE-ACTION GATE |
| **ComplianceStateMachine** | 5-state workflow valid |
| **AST Scanner** | 352 findings across 93 files (6 categories) |

### t-string Clarification (July 8, 2026)
The `CORE/tstrings.py` module and `CODEX/safe_sql.py` use `t'...'` syntax — this is **valid Python 3.14 PEP 750** Template string syntax, NOT an anti-pattern. The AST scanner's t-string detection is a false positive. ERROR_LOG #82 should be marked as resolved or reclassified.

### Nuitka
| Property | Value |
|----------|-------|
| **Patch script** | `/root/azazael/docs/scripts/patch_nuitka_314t.py` |
| **Patches** | allocator.h, SconsPythonBuild.py, code templates |
| **Status** | Not installed on WSL |
| **Blocking issue** | `_PyStackRef` error on 3.14.6t |

### WSL Quick-Start Commands
```bash
# Mount G: drive
mkdir -p /mnt/g && mount -t drvfs G: /mnt/g

# Install required packages
pip3 install psutil mypy

# Run mypy
cd /root/azazael && python3 -m mypy src/CORE/ --ignore-missing-imports --explicit-package-bases

# Restore from G: archive
cp /mnt/g/AZAZAEL_SOURCE_OF_TRUTH/src/PATH/TO/file.py azazael/src/PATH/TO/file.py

# Sync files to G: archive
cp azazael/DISCLOSURE_WHITEPAPER_TODO.md /mnt/g/AZAZAEL_SOURCE_OF_TRUTH/
cp azazael/SESSION_STARTUP.md /mnt/g/AZAZAEL_SOURCE_OF_TRUTH/

# Record session to DirectMemory
python3 -c "import sys; sys.path.insert(0, 'azazael/src'); from CORE.direct_memory import DirectMemory; dm=DirectMemory(); dm.record('session_start', '{}')"
```

**Created:** July 8, 2026 (Session 4)
**Dependencies:** Python 3.14.4+, psutil, mypy
