---
name: azazael-fix-file-operations
description: Quick-reference fixes for file system and data safety errors — shutil data loss, robocopy timeouts, and cross-drive operations.
metadata:
  category: fixes
  project: azazael
---

# 🛠️ Skill: Fixes for File System & Data Safety

*Quick-reference solutions extracted from ERROR_LOG.md for known errors in File System & Data Safety.*

## Error #53 — G: Drive Robocopy Times Out on Large Transfers
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
For G: drive operations, always use timeouts >= 600s (10 min). Consider running archive updates during idle time.

---
## Error #58 — shutil.copytree + shutil.rmtree Causes Silent Data Loss on Timeout
**Symptom:** See ERROR_LOG.md.
**Fix Solution:**
NEVER use `copytree` + `rmtree` as a move pattern in timed scripts.

Safe patterns:
```python
# FOR SAME FILESYSTEM: use shutil.move
shutil.move(src, dst)  # Atomic, no data loss risk

# FOR CROSS FILESYSTEM (C: to G:):
# 1. Copy completely
shutil.copytree(src, dst)
# 2. Verify destination is complete
src_total = sum(f.stat().st_size for f in src.rglob('*') if f.is_file())
dst_total = sum(f.stat().st_size for f in dst.rglob('*') if f.is_file())
if src_total == dst_total:
    shutil.rmtree(src)
e
**Prevention:**
1. Never use `copytree` + `rmtree` pattern in timed scripts (they're compiled together)
2. Always verify destination completeness before deleting source (size + file count check)
3. For G: drive (SD card), use timeouts >= 600s or background robocopy (Start-Process)
4. Use `shutil.move()` for same-filesystem moves (atomic, no data loss risk)
5. Add data integrity checks to ALL file move operations


---
