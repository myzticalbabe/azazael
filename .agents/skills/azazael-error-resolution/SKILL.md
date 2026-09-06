---
name: azazael-error-resolution
description: Sequential error resolution decision tree for systematic troubleshooting. Load when encountering ANY error to follow a proven step-by-step resolution sequence.
metadata:
  category: quality
  project: azazael
  auto_load: true
---
# Sequential Error Resolution — Decision Tree

> *Canonical troubleshooting procedure for all Azazael errors.*
> *Always resolve errors in SEQUENCE — later steps assume earlier steps passed.*

---

## 🔴 Step 0: First Responder Protocol

**Before ANY debugging — STOP and check these in order:**

1. **Is the error already recorded in `ERROR_LOG.md`?**
   - If YES → Jump to the recorded fix solution for that Error #NN
   - If NO → Continue with Step 1 below

2. **Is the error environment-specific?**
   - Windows 3.14t vs WSL Ubuntu 26.04 vs Docker?
   - Check the relevant platform section below

3. **Is the tool/command running correctly?**
   - `MSYS2_ARG_CONV_EXCL=/mnt wsl ...` — for WSL commands from Git Bash
   - `$TEMP` escaped properly in cmd.exe — `%%i` not `%i` in batch files
   - Python paths correct for 3.14t

---

## 🔴 Step 1: Python Environment Check

### Sequence — Check in THIS order:

```
1.1 → python --version                    # Expected: Python 3.14.5
1.2 → python -c "import sys; print(hasattr(sys, '_is_gil_enabled') and not sys._is_gil_enabled())"  # Expected: True
1.3 → pip list | findstr psutil           # Verify correct wheel
1.4 → python azazael/scripts/check_tooling.py
```

### Decision Tree:

**1.1 — Wrong Python version?**
```
→ Shows 3.13?     → CRITICAL: Using wrong Python. Run `where python` to find 3.13 path. 
                    Fix: Remove 3.13 from PATH, ensure Python314 is first.
→ Shows 3.12/3.11? → System Python, not 3.14t. Fix: Use full path to Python314/python.exe
→ Shows 3.14.x?   → Continue to 1.2
```

**1.2 — Free-threading disabled?**
```
→ False/Error → Non-free-threading build detected.
                 Fix: Use Python 3.14t (free-threading) build only.
                 Verify: python -c "import sysconfig; print(sysconfig.get_config_var('Py_GIL_DISABLED'))"
                 Expected: 1
```

**1.3 — Package issues?**
```
→ psutil missing?        → pip install psutil
→ psutil segfaults?      → pip install --force-reinstall --no-deps psutil (Error #49)
→ psycopg2 fails?        → Use pg8000 instead (Error #50)
→ numpy fails?           → pip install --force-reinstall numpy>=2.1
→ Any C extension fails? → Check wheel tag: must have cp314t (not cp314)
```

**1.4 — check_tooling.py issues?**
```
→ Nuitka not ready?      → Run: python azazael/docs/scripts/patch_nuitka_314t.py --apply
→ psutil not found?      → See 1.3 above
```

---

## 🔴 Step 2: WSL / Cross-Platform Sequence

### Tools running from Git Bash to WSL:

**2.1 — MSYS2 Path Translation Error?**
```
Symptom: "C:/Program Files/Git/..." in error messages
Root Cause: Git Bash translates POSIX paths to Windows paths
Fix: Use one of these methods:

  Method A — MSYS2_ARG_CONV_EXCL:
    MSYS2_ARG_CONV_EXCL=/mnt wsl -d Ubuntu-26.04 -u root bash /mnt/c/path/to/script.sh
  
  Method B — cmd.exe bypass:
    cmd.exe /c "wsl -d Ubuntu-26.04 -u root bash /mnt/c/path/to/script.sh"
  
  Method C — Write script to WSL filesystem:
    wsl -d Ubuntu-26.04 -u root bash -c "cat > /root/script.sh << 'EOF'
    # script content here
    EOF
    bash /root/script.sh"
  
  Method D — MSYS2_ENV_CONV_EXCL:
    MSYS2_ENV_CONV_EXCL='*' cmd.exe //c "wsl -d Ubuntu-26.04 command"
```

**2.2 — WSL Distro Not Responding?**
```
→ wsl -l -v                # Check if distro exists
→ wsl -d Ubuntu-26.04      # Try to start it
→ wsl --shutdown           # If stuck, force restart
```

**2.3 — Python 3.14t not found in WSL?**
```
→ Check: /usr/local/python314t/bin/python3.14t --version
→ If missing: Run azazael/scripts/post_install.sh (builds from source)
```

---

## 🔴 Step 3: Nuitka Build Issues

### Sequence:
```
3.1 → Check Python version (3.14t required)
3.2 → Run patch_nuitka_314t.py
3.3 → Check source file exists
3.4 → Check for tkinter dependency
3.5 → Run build with extended timeout
```

**3.1 — Wrong Python version for build:**
```
→ Must use Python 3.14t (not 3.13, not 3.14 non-t)
→ Verify: python -c "import sys; print(sys._is_gil_enabled())"  # Expected: False
```

**3.2 — Nuitka patches not applied:**
```
→ Run: python azazael/docs/scripts/patch_nuitka_314t.py --apply
→ Verifies 9 C-level patches for 3.14t compatibility
→ Run: python azazael/docs/scripts/patch_nuitka_314t.py --check
```

**3.3 — Source file not found:**
```
→ build_all.py maps module names to source paths
→ Check: PYTHON=python; PROJECT_ROOT=C:\Users\clint\azazael\src
→ Source paths are relative to PROJECT_ROOT
```

**3.4 — tk-inter plugin needed:**
```
→ Symptoms: GUI module builds but crashes on launch
→ Fix: Add module name to NEEDS_TKINTER set in build_all.py
→ Rebuild with: --enable-plugin=tk-inter
```

**3.5 — Build timeout:**
```
→ Default Nuitka build: 2-10 min per module
→ build_all.py timeout: 600 seconds (10 min)
→ For large modules (BINARY_ANALYSIS, CODEX_Studio): may need 1200s
```

---

## 🔴 Step 4: Package Installation on 3.14t

### cp314t Wheel Verification Flow:

```
4.1 → pip install <package>
4.2 → Did it succeed?
       ├── YES → Test import in Python 3.14t
       │         ├── Works → Done ✅
       │         └── Segfault → Go to 4.3
       └── NO  → Go to 4.4
4.3 → pip install --force-reinstall --no-deps <package>
       ├── Works → Done ✅ (was cached non-t wheel, Error #49)
       └── Fails → Go to 4.4
4.4 → Does cp314t wheel exist?
       ├── YES → Wheel is broken (missing DLLs, Error #50)
       │         Find alternative package (pure Python)
       └── NO  → Package not available for 3.14t
                 Find alternative or build from source
```

### Known 3.14t Package Status:

| Package | Status | Action |
|---------|--------|--------|
| torch (CPU) | ✅ cp314t works | `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| numpy | ✅ cp314t works | `pip install numpy>=2.1` |
| openvino | ✅ cp314t works | `pip install openvino` |
| psutil | ✅ Fixed (Error #49) | `pip install --force-reinstall --no-deps psutil` |
| psycopg2-binary | ❌ Broken (Error #50) | Use `pg8000` instead |
| psycopg v3 | ❌ No cp314t wheel | Use `pg8000` instead |
| scipy | ❌ No cp314t wheel | Try `--no-binary :all:` source build |
| scikit-learn | ❌ No cp314t wheel | Try `--no-binary :all:` source build |
| pandas | ❌ No cp314t wheel | Try `--no-binary :all:` source build |
| onnx | ❌ Segfaults | Try WSL with `--no-binary :all:` (g++ build) |
| onnxruntime | ❌ Segfaults | Try WSL with `--no-binary :all:` (g++ build) |
| pytest | ❌ Segfaults (Error #48) | Use `python tests/test_*.py` instead |

---

## 🔴 Step 5: Disk / Space Issues

### Sequence:
```
5.1 → Check C: drive space (target: >10% free)
5.2 → Check TEMP directory size
5.3 → Check pip cache
5.4 → Check build artifacts (.build dirs)
5.5 → Check G: drive archive completeness
```

### Decision Tree:

**5.1 — C: drive < 10% free?**
```
→ Clean pip cache:      pip cache purge (frees ~700 MB)
→ Clean Windows TEMP:   del /f /s /q %TEMP%\*.* (frees ~2.5 GB)
→ Clean .build dirs:    Delete Nuitka build artifacts (~300 MB)
→ Move LM Studio models: 82 GB — move to G: and symlink
```

**5.2 — G: drive archive incomplete?**
```
→ Check G:\AZAZAEL\AZAZAEL_ROOT\ against C:\azazael\
→ If missing planning docs/scripts/.agents: use robocopy
→ Use: MSYS2_ARG_CONV_EXCL='*' cmd.exe //c "robocopy ..."
→ Set timeout >300s for large copies (G: may be slow)
```

---

## 🔴 Step 6: Test Failures

### Sequence:
```
6.1 → Syntax check: Write _syntax_check.py → python _syntax_check.py
6.2 → Registry test: Write _reg_test.py → python _reg_test.py
6.3 → Run unit tests: python tests/test_*.py
6.4 → Run integration: python run_tests.py --skip-slow
```

### Decision Tree:

**6.1 — Syntax errors?**
```
→ Fix syntax first before any other testing
→ Common: f-string backslashes, unclosed brackets, missing imports
```

**6.2 — Registry test fails?**
```
→ discover_worms() returns count, not collection
→ WORM_REGISTRY dict contains worms by name
→ Common: import path issues, missing @register_worm decorator
```

**6.3 — pytest segfaults?**
```
→ DON'T use pytest on 3.14t (Error #48 — fundamental incompatibility)
→ Use: python tests/test_<name>.py directly
→ Or: python run_tests.py (standalone test runner)
```

**6.4 — Integration tests timeout?**
```
→ test_metacluster_unit.py needs 1200s timeout (76 worm imports, 85+ worms)
→ CLUSTER_INSPECTOR scans 473 files — main time sink
→ Use: timeout 1200 python tests/test_metacluster_unit.py
→ Quick: python run_tests.py --skip-slow
```

---

## 🔴 Step 7: Error Resolution Post-Mortem

After resolving ANY error, ALWAYS:

```
7.1 → Record in ERROR_LOG.md with sequential #NN ID
7.2 → Add lesson to LESSONS_MASTER.md if new knowledge
7.3 → Add prevention rule to SYSTEM_INSTRUCTIONS.md if applicable
7.4 → Update check_tooling.py if the error is checkable
7.5 → Update SESSION_STARTUP.md for next-session awareness
```

### Error Record Template:
```markdown
## Error #NN — Descriptive Title
**Timestamp:** YYYY-MM-DD HH:MM
**Severity:** 🔴 Critical / 🟡 Warning / 🟢 Info
**File(s):** path/to/file.py:line

**Symptom:** What the user/assistant observed
**Root Cause:** What triggered the error (at system level)
**Detection:** How the error was identified (tool output, crash, manual)
**Fix Solution:** Exactly what was done to resolve
**Prevention:** How to avoid this error in future (process change, guard, check tooling)
**Decision Tree Reference:** Which Step in this guide applies (Step 1-7)
```

---

## 🔴 Decision Tree Quick Reference Card

```
ERROR OCCURS
│
├─ Python issue?          → Step 1: Python Environment Check
├─ WSL/Cross-platform?    → Step 2: WSL Path Translation
├─ Nuitka build?          → Step 3: Nuitka Build Issues
├─ Package install?       → Step 4: Package Installation on 3.14t
├─ Disk/Space?            → Step 5: Disk Issues
├─ Test failure?          → Step 6: Test Failures
└─ None of above?         → Step 7: Post-Mortem + Record
```

---

## Related Skills
- `azazael-sop` — Parent: mandatory error recording, severity classification
- `azazael-error-prevention` — Anti-pattern catalog, DO-NOT-REPEAT list
- `azazael-testing` — Pre-commit checklist, validation commands
- `azazael-system-startup` — Session initiation and congruency
- `azazael-environment` — Python 3.14t setup and verification
