# G: Drive Mount Checklist — Physical, Network & Credential Requirements

> **Created:** June 12, 2026  
> **Drive Specs:** Removable SD card (DriveType 2) | exFAT | 477 GB total / ~315 GB free  
> **Volume Label:** `android`  
> **Role:** Primary archive & source-of-truth for Azazael project

---

## □ Step 1: Physical Connection

| Check | Action | Pass/Fail |
|-------|--------|-----------|
| **Card present** | SD card inserted into reader/card slot | □ |
| **Reader functional** | Card reader detected in Device Manager (no yellow flags) | □ |
| **No vibration/looseness** | Card seated firmly — partial insertion causes intermittent disconnects | □ |
| **Clean contacts** | If intermittent, remove and re-seat; clean with isopropyl if needed | □ |
| **USB port** | If using USB card reader, try different port (prefer USB 3.0+) | □ |

**Known physical issues:**
- SD cards in cheap readers can lose contact from vibration or desk movement
- exFAT is more sensitive to unclean unmounts than NTFS — always use **Safely Remove Hardware** before unplugging

---

## □ Step 2: Windows Drive Letter Assignment

| Check | Verification Command | Pass/Fail |
|-------|---------------------|-----------|
| **G: assigned** | `fsutil fsinfo drives` — confirm `G:\` appears in list | □ |
| **No conflict** | `powershell -Command "Get-WmiObject Win32_LogicalDisk | Select-Object DeviceID, DriveType, VolumeName"` — check no other device has G: | □ |
| **Volume label matches** | Should show `android` — if label is wrong or missing, check for corruption | □ |
| **Read/write test** | `echo test > G:\_mount_test.txt && del G:\_mount_test.txt` | □ |
| **Free space** | G: should show ~315 GB free — significantly less may indicate undetected usage | □ |

**Drive type reference:**
| Value | Meaning | Expected for G: |
|-------|---------|-----------------|
| 2 | Removable | ✅ SD card |
| 3 | Local (fixed) | ❌ Not expected |
| 4 | Network | ❌ Not expected |

> **Note:** `wmic` is deprecated in Windows 11 24H2+. If `wmic` is unavailable, use the PowerShell alternative:
> `powershell -Command "Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='G:'\" | Format-List"

**If G: is missing:**
1. Open **Disk Management** (`diskmgmt.msc`)
2. Look for the SD card volume in the lower pane
3. Right-click → **Change Drive Letter and Paths** → **Add** → assign `G:`
4. If the volume shows as RAW or uninitialized, the card may be corrupted

---

## □ Step 3: WSL2 Mount Verification

WSL2 auto-mounts Windows drives under `/mnt/`. G: drive appears at `/mnt/g/`.

| Check | Verification Command | Pass/Fail |
|-------|---------------------|-----------|
| **/mnt/g/ exists** | `wsl -d Ubuntu-26.04 -e bash -c "test -d /mnt/g && echo YES || echo NO"` | □ |
| **Root directory listing** | `wsl -d Ubuntu-26.04 -e bash -c "ls /mnt/g/"` — expect `AZAZAEL`, `source-of-truth`, etc. | □ |
| **Key path accessible** | `wsl -d Ubuntu-26.04 -e bash -c "test -d /mnt/g/source-of-truth/azazael && echo YES || echo NO"` | □ |
| **WSL2 file count** | `wsl -d Ubuntu-26.04 -e bash -c "ls /mnt/g/source-of-truth/azazael/docs/*.md 2>/dev/null | wc -l"` — should match Windows | □ |
| **Write test** | `wsl -d Ubuntu-26.04 -e bash -c "echo test > /mnt/g/_wsl_test.txt && rm /mnt/g/_wsl_test.txt"` | □ |

**WSL2 performance notes:**
- `/mnt/g/` accesses **DrvFs** — the Windows drive mapping layer
- Writes through `/mnt/` to exFAT are slower than native Linux FS
- For bulk operations, use `robocopy` on Windows side instead (see sync_all.py)

---

## □ Step 4: Application-Level Access

| Check | Verification Command | Pass/Fail |
|-------|---------------------|-----------|
| **sync_all.py --status** | `python scripts/sync_all.py --status` — G: environments should show `[OK]` | □ |
| **Python Path.exists()** | `python -c "from pathlib import Path; print(Path('G:/').exists())"` — must be `True` | □ |
| **CORE.paths.get_g_drive()** | `python -c "from CORE.paths import get_g_drive; print(get_g_drive())"` — must return Path | □ |

---

## □ Step 5: Network / Remote Access (Optional)

> G: drive is **not a network drive** by default — it's a local removable SD card.  
> The checklist below only applies if you need remote access (e.g., from another machine or VM).

### 5a — Share the SD Card Over Network

| Check | Action | Pass/Fail |
|-------|--------|-----------|
| **Share folder** | Right-click `G:\` → **Properties** → **Sharing** → **Advanced Sharing** → check **Share this folder** | □ |
| **Share name** | Use `GDrive$` (the `$` suffix hides it from network browse lists) | □ |
| **Permissions** | Set **Everyone** → **Read** (or specific user for Read/Write) | □ |
| **Firewall** | Ensure **File and Printer Sharing** is allowed through Windows Firewall | □ |
| **Test from remote** | `net use X: \\\\HOSTNAME\\GDrive$` on the remote machine | □ |

### 5b — Map as Network Drive on Another Machine

| Check | Command | Pass/Fail |
|-------|---------|-----------|
| **Discovery** | `net view \\\\HOSTNAME` — confirm GDrive$ share is listed | □ |
| **Map** | `net use G: \\\\HOSTNAME\\GDrive$ /persistent:yes` | □ |
| **Test** | `dir G:\` — should show same contents as local SD card | □ |
| **Persist across reboot** | `net use G: \\\\HOSTNAME\\GDrive$ /persistent:yes` (re-run if mapping drops) | □ |

### 5c — WSL2 Remote Mount (NAS/SMB)

If G: is an SMB share (NAS) rather than local SD card:

| Check | Command | Pass/Fail |
|-------|---------|-----------|
| **Credentials file** | Create `~/.smbcredentials` with `username=DOMAIN\\user\npassword=xxx` (`chmod 600`) | □ |
| **Mount test** | `sudo mount -t cifs //NAS_PATH/share /mnt/g -o credentials=~/.smbcredentials,uid=$(id -u),gid=$(id -g)` | □ |
| **fstab entry** | Add to `/etc/fstab`: `//NAS_PATH/share /mnt/g cifs credentials=~/.smbcredentials,uid=1000,gid=1000,noauto 0 0` | □ |

---

## □ Step 6: Credential Management

> The G: drive does not require credentials when connected locally as a removable SD card.  
> Credentials are only needed for **network share scenarios** (Step 5).

| Check | Action | Pass/Fail |
|-------|--------|-----------|
| **Windows saved credentials** | `cmdkey /list` — check for stored `GDrive` or network share credentials | □ |
| **Add credential (if needed)** | `cmdkey /add:HOSTNAME /user:DOMAIN\\user /pass:password` | □ |
| **Remove stale credentials** | `cmdkey /delete:HOSTNAME` (if old credentials cause auth failures) | □ |
| **WSL2 SMB credentials file** | If using SMB mount, verify `~/.smbcredentials` exists and is `chmod 600` | □ |
| **Network drive persistence** | Create `map_g_drive.bat` or scheduled task to re-map on boot if share drops | □ |

---

## □ Step 7: Integrity & Health Checks

| Check | Verification | Pass/Fail |
|-------|-------------|-----------|
| **chkdsk status** | `chkdsk G:` — check for **dirty bit** (`The volume is dirty`) | □ |
| **Run chkdsk /f** | If dirty, run `chkdsk G: /f` — **requires reboot on system volume; may require reboot for removable too** | □ |
| **File system check** | `fsutil dirty query G:` — should return `NOT dirty` | □ |
| **Corrupted files** | `dir /s G:\AZAZAEL` — no `I/O errors` or `CRC mismatch` in output | □ |
| **Consistency with local** | `python scripts/sync_all.py --status` — Integrity should show `ALL SYNCED` | □ |
| **Last verified** | Document the date of last successful full verification: ________ | □ |

---

## □ Step 8: Troubleshooting Quick Reference

### Symptom: G: Drive Not Showing
```
fsutil fsinfo drives     # List all drives
diskmgmt.msc             # Disk Management — look for unlabeled volume
```
**Fix:** Assign drive letter G: in Disk Management.

### Symptom: "The volume is dirty" on chkdsk
```
chkdsk G: /f             # Schedule fix on next reboot
shutdown /r /t 0         # Reboot to execute
```
**Note:** This can take 30-60 minutes on a 477 GB SD card. Plan for downtime.

### Symptom: sync_all.py Shows G: as [XX]
```
python -u -c "from pathlib import Path; print('G: exists:', Path('G:/').exists())"
```
**Fix:** If `False`, check physical connection and drive letter assignment.  
If `True` but sync_all.py fails, the issue is in `get_env_status()` logic for G: drive paths — verify `ENVIRONMENTS["g_source"]["root"].exists()` returns correctly.

### Symptom: Robocopy / File Copy Times Out
```
# Use background robocopy with extended timeout:
start /b cmd.exe /c "robocopy C:\azazael G:\source-of-truth\azazael /E /NP > G:\robocopy.log"
# Check progress:
findstr /i "Files\|Copied" G:\robocopy.log
```
**Root cause:** SD card write speeds are slow (5-15 MB/s). Large transfers (>1 GB) take 5-10+ minutes. Always use background robocopy with `/NP` (no progress) to avoid timeout.

### Symptom: WSL2 /mnt/g/ Is Empty or Not Accessible
```
wsl -d Ubuntu-26.04 -e bash -c "mount | grep /mnt/g"
```
**Fix:** If G: is not mounted in WSL2, restart WSL: `wsl --shutdown` then re-open WSL2.

### Symptom: Intermittent Disconnects During Sync
**Fix:** 
1. Check physical connection (Step 1)
2. Run `chkdsk G: /f` (requires reboot)
3. If using a USB card reader, try a different port or cable
4. For large transfers, use the background robocopy pattern above

---

## □ Appendix: Key G: Drive Paths

| Path | Purpose | Required for |
|------|---------|-------------|
| `G:\AZAZAEL\` | Primary archive root | Archive operations |
| `G:\AZAZAEL\AZAZAEL_ROOT\` | Full project mirror | `sync_all.py` → G: AZAZAEL_ROOT |
| `G:\source-of-truth\azazael\` | Canonical source of truth | `sync_all.py` → G: source-of-truth |
| `G:\AZAZAEL\memory\` | Memory store database (tiered storage) | LocalMemoryStore |
| `G:\AZAZAEL\standalone\` | Desktop standalone EXE backups | Desktop sync |
| `G:\AZAZAEL\archive\` | Archived old builds and data | Cleanup operations |
| `G:\AZAZAEL\CODEX_VIDEOS\` | CODEX video output | Video generation |
| `G:\AZAZAEL\cp314t_wheels\` | Python 3.14t compatible wheels | Build system |

---

## □ Appendix: Quick Verification Script

Run this to verify all key criteria in one shot:

```python
import sys, os, subprocess
sys.stdout.reconfigure(encoding="utf-8")

print("=== G: Drive Mount Checklist ===\n")

# 1. Physical / Drive letter
print(f"[{'OK' if os.path.exists('G:/') else 'XX'}] G: drive exists")

# 2. Drive type
r = subprocess.run(["powershell", "-Command",
    "Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='G:'\" | Select-Object -ExpandProperty DriveType"],
    capture_output=True, text=True, timeout=10)
dt = r.stdout.strip()
types = {"2": "Removable (SD)", "3": "Local disk", "4": "Network"}
print(f"[{'OK' if dt == '2' else '?'}] Drive type: {types.get(dt, f'Unknown ({dt})')}")

# 3. Volume label
r = subprocess.run(["powershell", "-Command",
    "Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='G:'\" | Select-Object -ExpandProperty VolumeName"],
    capture_output=True, text=True, timeout=10)
print(f"[{'OK' if 'android' in r.stdout.lower() else '?'}] Volume name: {r.stdout.strip() or '(empty)'}")

# 4. Free space
r = subprocess.run(["powershell", "-Command",
    "[math]::Round((Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='G:'\").FreeSpace / 1GB, 1)"],
    capture_output=True, text=True, timeout=10)
free = r.stdout.strip()
print(f"[{'OK' if free and float(free) > 100 else '?'}] Free space: {free} GB")

# 5. WSL2 accessibility
r = subprocess.run(["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c",
    "test -d /mnt/g && echo YES || echo NO"],
    capture_output=True, text=True, timeout=10)
wsl_ok = r.stdout.strip() == "YES"
print(f"[{'OK' if wsl_ok else 'XX'}] WSL2 /mnt/g/ accessible")

# 6. Key path: source-of-truth
r = subprocess.run(["wsl", "-d", "Ubuntu-26.04", "-e", "bash", "-c",
    "test -d /mnt/g/source-of-truth/azazael && echo YES || echo NO"],
    capture_output=True, text=True, timeout=10)
sot_ok = r.stdout.strip() == "YES"
print(f"[{'OK' if sot_ok else 'XX'}] G:/source-of-truth/azazael readable via WSL2")

# 7. Dirty bit
r = subprocess.run(["fsutil", "dirty", "query", "G:"], capture_output=True, text=True, timeout=10)
dirty = "NOT dirty" in r.stdout or "is not" in r.stdout
print(f"[{'OK' if dirty else 'XX'}] Volume dirty bit: {'clean' if dirty else 'DIRTY — run chkdsk /f'}")

print(f"\n--- Overall: {'PASS' if all([os.path.exists('G:/'), wsl_ok, sot_ok, dirty]) else 'ISSUES FOUND'} ---")
```
