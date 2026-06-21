# LESSONS — Cross-Platform AZAZAEL 3.14t Development

**Created:** June 4, 2026 | **Session:** Multi-Platform Realignment

---

## Lesson 1: Windows Paths Don't Work on Linux

**Problem:** Python code uses `os.path.join("src", "CORE")` or backslash paths that fail on Linux. `C:\Users\clint\azazael\` is meaningless on Ubuntu.

**Lesson:** Always use `pathlib.Path` for all filesystem operations. Never hardcode `C:\`. Use `get_project_root()` from `CORE/paths.py` which auto-detects the OS.

```python
# ❌ Wrong
path = "src\\CORE\\worm_registry.py"

# ✅ Correct
from pathlib import Path
from CORE.paths import get_project_root
path = get_project_root() / "src" / "CORE" / "worm_registry.py"
```

---

## Lesson 2: G: Drive Is Not Universal

**Problem:** G: drive is mounted on Windows and WSL2 (`/mnt/g/`) but bare metal Ubuntu and Kali need NFS/SMB mounts.

**Lesson:** Always check G: drive availability before assuming it exists. Fall back to local paths.

```python
def get_g_drive():
    """Resolve G: drive path cross-platform."""
    import platform, os
    if platform.system() == "Windows":
        return Path("G:/")
    elif os.path.exists("/mnt/g/"):  # WSL2
        return Path("/mnt/g/")
    elif os.path.exists("/media/g/"):  # NFS/SMB mount
        return Path("/media/g/")
    else:
        return None  # Not available — use local paths
```

---

## Lesson 3: Free-Threading Detection Varies by Platform

**Problem:** Python 3.14t free-threading detection uses `sys._is_gil_enabled()` which may not exist on all builds.

**Lesson:** Always check with a try/except and fall back to `sysconfig.get_config_var('Py_GIL_DISABLED')`.

```python
def is_free_threaded() -> bool:
    try:
        if hasattr(sys, '_is_gil_enabled'):
            return not sys._is_gil_enabled()
    except Exception:
        pass
    try:
        import sysconfig
        return bool(sysconfig.get_config_var('Py_GIL_DISABLED'))
    except Exception:
        return False
```

---

## Lesson 4: Case Sensitivity Kills Imports

**Problem:** `from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ` works on Windows (case-insensitive) but fails on Linux if the file is `CLUSTERWORMS.py` but the import uses lowercase.

**Lesson:** Always match the exact case of filenames. Audit all imports for case correctness before deploying to Linux.

```bash
# Check for case mismatches
find src -name "*.py" | while read f; do
    grep "import.*$(basename "$f" .py)" "$f" 2>/dev/null
done
```

---

## Lesson 5: tkinter Requires Separate Install on Linux

**Problem:** `import tkinter` works on Windows Python but fails on Linux with `ModuleNotFoundError: No module named 'tkinter'`.

**Lesson:** tkinter is a system package on Linux, not a pip package.

```bash
# Ubuntu/Kali
sudo apt-get install python3-tk

# Or if using Python 3.14 from source/PPA
sudo apt-get install tk-dev
# Then rebuild Python with ./configure --with-tcltk-includes=...
```

---

## Lesson 6: WSL2 Filesystem Performance

**Problem:** Accessing Windows files from WSL2 (`/mnt/c/...`) is 5-10x slower than native Linux filesystem. Running AZAZAEL from `/mnt/c/Users/clint/azazael/` in WSL2 is painfully slow.

**Lesson:** Keep the canonical AZAZAEL repository on the native Linux filesystem (`/root/azazael/` or `/home/clint/azazael/`). Only use `/mnt/` paths for G: drive shared state, not for the active codebase.

---

## Lesson 7: Docker Desktop vs Native Docker

**Problem:** Docker Desktop WSL2 backend shares resources with the Ubuntu WSL distro. Running heavy containers can starve AZAZAEL of resources.

**Lesson:** On bare metal Ubuntu, use native Docker. On WSL2, limit Docker Desktop resource allocation. Monitor with `docker stats`.

---

## Lesson 8: pip Install Differences

**Problem:** Some packages install differently on Windows vs Linux (e.g., `pywin32` is Windows-only, `uvloop` is Linux-only).

**Lesson:** Platform-specific dependencies go in `pyproject.toml` extras:

```toml
[project.optional-dependencies]
windows = ["pywin32>=306"]
linux = ["uvloop>=0.19"]
```

Install with: `pip install "azazael[windows]"` or `pip install "azazael[linux]"`

---

## Lesson 9: Systemd vs Windows Service

**Problem:** AZAZAEL needs to run as a daemon/service. Linux uses systemd, Windows uses NSSM or Windows Service.

**Lesson:** Create both service definitions.

**Linux (systemd):**
```ini
# /etc/systemd/system/azazael.service
[Unit]
Description=AZAZAEL ML Ecosystem
After=network.target

[Service]
Type=simple
User=clint
WorkingDirectory=/home/clint/azazael
ExecStart=/usr/bin/python3.14t -m azazael.daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Windows (NSSM):**
```bat
nssm install AZAZAEL "C:\Python314t\python.exe" "-m azazael.daemon"
nssm set AZAZAEL AppDirectory "C:\Users\clint\azazael"
nssm start AZAZAEL
```

---

## Lesson 10: Kali-Specific Security Hardening

**Problem:** Kali Linux is a security distribution. Running AZAZAEL with full worm capabilities requires careful firewall and AppArmor configuration.

**Lesson:** On Kali, run security worms in isolated environments. Use AppArmor profiles for each worm category.

```bash
# Kali: Allow Python 3.14t network access
sudo aa-complain /usr/bin/python3.14

# Or create a custom AppArmor profile
sudo aa-genprof /usr/bin/python3.14
```
