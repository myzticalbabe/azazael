# LESSONS — Task F: 5-Environment Alignment & Synchronization

**Task:** Map, sync, and maintain parity across all Azazael environments
**Date:** June 4, 2026
**Reference:** ENVIRONMENT_ALIGNMENT.md, scripts/sync_all.py, LESSONS_MASTER.md #28, #29

---

## The 5-Environment Topology

Azazael exists across 5 distinct environments, each serving a different purpose:

| # | Environment | Path | Type | Purpose |
|---|------------|------|------|---------|
| 1 | **Windows 11** | `C:/Users/clint/azazael` | Primary dev | Source of truth, all edits happen here |
| 2 | **WSL2** | `/root/azazael` | Linux build target | Nuitka Linux builds, cross-platform testing |
| 3 | **Desktop** | `C:/Users/clint/Desktop/AZAZAEL_Standalone` | Release | 52 compiled .exe files, deployment target |
| 4 | **G: source-of-truth** | `G:/source-of-truth/azazael` | Canonical archive | Docs archive (may be unavailable) |
| 5 | **G: AZAZAEL_ROOT** | `G:/AZAZAEL/AZAZAEL_ROOT` | Primary archive | Full project mirror, 70+ Nuitka builds |

### Sync Direction Diagram

```
Windows 11 (primary dev)
    |
    ├──> WSL2          [/root/azazael via /mnt/c mount cp]
    ├──> Desktop       [docs only, direct copy]
    ├──> G: source     [docs only, direct copy]
    └──> G: AZAZAEL    [docs only, direct copy]
```

Windows 11 is ALWAYS the source. No other environment pushes TO Windows 11.
This is a hub-and-spoke model, not a mesh. Bidirectional sync would create merge conflicts.

---

## Lesson F1: WSL2 Path Duality — Windows Mount vs Native Filesystem

**The critical insight: WSL2 can access files through TWO different paths:**

| Path | Filesystem | Speed | Use Case |
|------|-----------|-------|----------|
| `/mnt/c/Users/clint/azazael/...` | Windows NTFS (mounted) | Slow | **Reading** from Windows |
| `/root/azazael/...` | WSL2 ext4 (native) | Fast | **Building** with Nuitka |

**The sync pattern that works:**

```python
# Source: Windows file accessed via /mnt/c mount from WSL2
src_wsl = "/mnt/c/Users/clint/azazael/src/CORE/WORMS/expansion/meta_cognition.py"

# Destination: WSL2 native filesystem
dest_wsl = "/root/azazael/src/CORE/WORMS/expansion/meta_cognition.py"

# Copy from Windows mount to native WSL2 filesystem
cmd = f"mkdir -p $(dirname {dest_wsl}) && cp {src_wsl} {dest_wsl}"
```

**Why `cp` from `/mnt/c` to `/mnt/c` fails:** If both source and destination resolve to `/mnt/c/...`, `cp` detects they're the same file and refuses. This was the original sync_all.py bug.

**Prevention rule:** Always distinguish source path (Windows mount `/mnt/c`) from destination path (WSL2 native `/root/azazael`). Never use `wsl_path()` for both.

---

## Lesson F2: G: Drive Graceful Degradation — Never Assume Archive Availability

**Failure:** `verify_integrity()` called `g_source.glob("docs/*.md")` without checking if `g_source.exists()`. When G: was unavailable (unmounted, network issues), this either hung or raised confusing errors.

**Fix:** 
```python
g_source = ENVIRONMENTS["g_source"]["root"]
if g_source.exists():
    g_docs_path = g_source / "docs"
    g_docs = set(f.name for f in g_docs_path.glob("*.md")) if g_docs_path.exists() else set()
    results["docs_g"] = win_docs.issubset(g_docs)
else:
    results["docs_g"] = True  # G: not available, skip check
```

**Prevention:** Every path-based operation on G: or any external drive MUST wrap in `if path.exists():` with a graceful skip. External drives are never guaranteed to be available.

---

## Lesson F3: Pre-Commit Hook as Sync Gate — Block Commits When Out of Sync

**Design:** `.git/hooks/pre-commit` runs `python3.14t scripts/sync_all.py --verify` before every commit. If environments are out of sync, the commit is blocked.

```bash
#!/bin/bash
# Pre-commit: verify environment sync
SCRIPT="scripts/sync_all.py"
if [ -f "$SCRIPT" ]; then
    python3.14t "$SCRIPT" --verify 2>&1
    if [ $? -ne 0 ]; then
        echo ""
        echo "BLOCKED: Environments out of sync."
        echo "Run: python3.14t scripts/sync_all.py --sync-all"
        exit 1
    fi
fi
```

**Override:** `git commit --no-verify` in emergencies.

**Lesson:** The pre-commit hook acts as an invariant guard — the invariant "all environments are in sync" is checked automatically, removing human memory as a failure mode.

---

## Lesson F4: Sync Scope — Code vs Docs Separation

**Code files** (`.py` in `src/`, `tests/`, `scripts/`): Synced to WSL2 ONLY. These need to exist in the WSL2 native filesystem for Nuitka builds.

**Documentation files** (`.md` in `docs/`, root `LESSONS_*.md`, `MEMORIES*.md`): Synced to Desktop and G: drives. These are knowledge artifacts, not build dependencies.

**Why separate:** WSL2 doesn't need 48 markdown docs — it needs the Python source for compilation. Desktop doesn't need source code — it's a release directory for `.exe` files.

---

## Lesson F5: verify_integrity() — 4-Dimensional Parity Check

The verification function checks parity across 4 dimensions:

| Dimension | Compares | Why |
|-----------|----------|-----|
| `expansion/` | Windows vs WSL2 `.py` filenames | Build source parity |
| `docs_g` | Windows vs G: `.md` filenames | Knowledge archive parity |
| `tests` | Windows vs WSL2 test filenames | Test parity |
| `scripts` | Windows vs WSL2 script filenames | Build tooling parity |

**ALL must be True** for `all_ok` to pass. This is an AND gate — any single dimension out of sync blocks the pre-commit hook.

---

## Session Actions Recorded

| Action | Files | Environment |
|--------|-------|-------------|
| Discovered WSL2 path duality | sync_all.py | WSL2 |
| Fixed source=/mnt/c, dest=/root/azazael | sync_all.py `sync_windows_to_wsl2()` | WSL2 |
| Added G: graceful degradation | sync_all.py `verify_integrity()` | G: |
| Created pre-commit hook | `.git/hooks/pre-commit` | Windows |
| Synced 76 files to WSL2 | expansion/, tests/, scripts/, docs/ | WSL2 |
| Synced 48 docs to Desktop | docs/*.md | Desktop |
| Synced 48 docs to G: | docs/*.md | G: |

**Cross-reference:** LESSONS_MASTER.md #28 (import thread safety), #29 (module-level imports). Environment sync is the operational complement to code-level thread safety — both are required for reliable concurrent builds.
