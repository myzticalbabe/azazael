# MEMORIES — Cross-Platform Anti-Patterns

**Created:** June 4, 2026 | **Related:** PLATFORM_DEPLOYMENT.md, LESSONS_PLATFORM.md

---

## Memory 1: Don't Assume G: Drive Exists

**Anti-Pattern:** Hardcoding `G:/source-of-truth/` paths without fallback.

**Incident:** Multiple CI failures when G: drive wasn't mounted. CI runners on GitHub Actions don't have access to network drives.

**Prevention:**
```python
g_drive = get_g_drive()
if g_drive is None:
    log.warning("G: drive not available — using local paths")
    source_of_truth = Path.home() / "azazael" / "source-of-truth"
else:
    source_of_truth = g_drive / "source-of-truth"
```

---

## Memory 2: WSL2 and Windows Share a Filesystem but Not a Python

**Anti-Pattern:** Assuming `pip install` in WSL2 affects Windows Python or vice versa. They're completely separate installations.

**Incident:** Installed azazael packages in WSL2, tried to import them from Windows Python — ModuleNotFoundError.

**Prevention:** Always check which Python you're using: `which python3 && python3 --version`. WSL2 Python is at `/usr/bin/python3`, Windows Python is at `/mnt/c/.../python.exe`. They don't share site-packages.

---

## Memory 3: Case Sensitivity Bit Us

**Anti-Pattern:** Using `from core.worm_registry import ...` (lowercase 'core') on Windows, then failing on Linux.

**Incident:** 17+ import errors when first deploying to WSL2 because Windows filesystem is case-insensitive and hides mismatches.

**Prevention:** 
- Run `find . -name "*.py" -exec grep -l "from [a-z]" {} \;` to find lowercase imports
- Always import with exact case: `from CORE.worm_registry import WORM_REGISTRY`
- Add CI check: `python -c "import sys; sys.path.insert(0,'src'); from CORE.worm_registry import WORM_REGISTRY"`

---

## Memory 4: numpy/scipy Wheel Availability

**Anti-Pattern:** Assuming `pip install numpy` works identically on all platforms. Some platforms need compilation.

**Incident:** `pip install numpy` on Kali Linux tried to compile from source (30+ minutes) because no pre-built wheel for Python 3.14t on that platform.

**Prevention:**
```bash
# Check wheel availability first
pip index versions numpy

# On Ubuntu 26.04, numpy may come from apt
sudo apt-get install python3-numpy

# Or use conda for binary packages
conda install numpy scipy
```

---

## Memory 5: Threading Differences Across Platforms

**Anti-Pattern:** Assuming `threading.Lock()` behavior is identical. Lock contention patterns differ between Windows and Linux.

**Incident:** A deadlock that never reproduced on Windows happened consistently on Linux due to different thread scheduling priorities.

**Prevention:**
- Use `threading.RLock()` (reentrant) for complex lock patterns
- Add `timeout=` to all `Lock.acquire()` calls
- Test multi-threaded code on both Windows and Linux before release

---

## Memory 6: Kali's Default Firewall Blocks Everything

**Anti-Pattern:** Assuming port 8420 (PAMS) or 18080 (llama-server) are accessible on Kali.

**Incident:** PAMS and llama-server worked on Ubuntu but were unreachable on Kali because `ufw` blocks all incoming by default.

**Prevention:**
```bash
# On Kali, explicitly allow AZAZAEL ports
sudo ufw allow 8420/tcp  # PAMS
sudo ufw allow 18080/tcp # llama-server
sudo ufw allow 8080/tcp  # Web dashboard
```
