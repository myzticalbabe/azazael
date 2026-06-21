# Environment Alignment — Permanent Cross-Environment Sync

**Created:** June 4, 2026 — Environment realignment session
**Status:** Active — keep updated after every session

---

## The 5 Environments

| # | Environment | Path | Purpose | Nuitka |
|---|------------|------|---------|--------|
| 1 | **Windows 11** | `C:\Users\clint\azazael` | Primary development | 4.1.2 ✓ |
| 2 | **WSL2** | `/root/azazael` (Ubuntu-26.04) | Linux build target | 4.1.2 ✓ |
| 3 | **Desktop** | `C:\Users\clint\Desktop\AZAZAEL_Standalone` | Release artifacts (52 .exe) | N/A |
| 4 | **G: source-of-truth** | `G:\source-of-truth\azazael` | Canonical archive | N/A |
| 5 | **G: AZAZAEL_ROOT** | `G:\AZAZAEL\AZAZAEL_ROOT` | Primary archive | N/A |

---

## Sync Direction

```
Windows 11 (primary dev)
    │
    ├──▶ WSL2 (/root/azazael)          [code + docs + tests]
    ├──▶ Desktop (AZAZAEL_Standalone)   [docs only]
    ├──▶ G: source-of-truth            [docs + configs]
    └──▶ G: AZAZAEL_ROOT               [docs + configs]
```

**Windows 11 is the source of truth for CODE.**
**G: source-of-truth is the archive for DOCS and CONFIGS.**

---

## Sync Command

```bash
# After every session:
python3.14t scripts/sync_all.py --sync-all

# Check status:
python3.14t scripts/sync_all.py --status

# Verify integrity:
python3.14t scripts/sync_all.py --verify
```

---

## Concurrent Build

```bash
# Build all targets on both Windows + WSL2:
python3.14t scripts/build_all_concurrent.py --all

# Build specific tier:
python3.14t scripts/build_all_concurrent.py --tier neural

# Build single target on specific platform:
python3.14t scripts/build_all_concurrent.py --target metacognition --platform windows

# Verify Nuitka patches before building:
python3.14t scripts/build_all_concurrent.py --verify
```

---

## What Gets Synced

| Content | Windows → WSL2 | Windows → G: | Windows → Desktop |
|---------|:---:|:---:|:---:|
| `src/CORE/WORMS/expansion/*.py` | ✓ | — | — |
| `src/CORE/WORMS/CLUSTERWORMS.py` | ✓ | — | — |
| `src/CORE/WORMS/METACLUSTER.py` | ✓ | — | — |
| `src/CORE/WORMS/NETWORK_DIAG.py` | ✓ | — | — |
| `src/ORCHESTRATION/hydra_bridge.py` | ✓ | — | — |
| `docs/*.md` | ✓ | ✓ | ✓ |
| `docs/scripts/*.py` | ✓ | ✓ | — |
| `tests/*.py` | ✓ | — | — |
| `LESSONS_*.md` | — | ✓ | ✓ |
| `MEMORIES*.md` | — | ✓ | ✓ |
| `MASTER_TASKS.md` | ✓ | ✓ | ✓ |

---

## Nuitka Configuration

| Platform | Python | Nuitka | Status |
|----------|--------|--------|--------|
| Windows 11 | 3.14.5t | 4.1.2 | Working |
| WSL2 | 3.14.5t | 4.1.2 | Working (reinstalled June 4) |

**Patch script:** `docs/scripts/patch_nuitka_314t.py`
Run `--verify` before any build. Apply `--apply` if Nuitka is reinstalled.

---

## Integrity Checks

Run after every session:
```bash
# Check expansion/ file parity
python3.14t scripts/sync_all.py --verify

# Quick manual check
diff <(ls src/CORE/WORMS/expansion/) <(wsl ls /root/azazael/src/CORE/WORMS/expansion/)
```

**Expected:** 18 expansion/ .py files in BOTH Windows and WSL2.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| WSL2 out of sync | `python3.14t scripts/sync_all.py --sync-to wsl2` |
| Nuitka not found in WSL | `pip install nuitka` in WSL Python 3.14t |
| Nuitka editable install broken | `pip uninstall nuitka -y && pip install nuitka` |
| G: drive not accessible | Check mount: `ls /g/` |
| Patch script missing | Created: `docs/scripts/patch_nuitka_314t.py` |

---

## Session Checklist

After every coding session:
- [ ] Run `sync_all.py --verify`
- [ ] Run `sync_all.py --sync-all` (or specific targets)
- [ ] Verify Nuitka: `build_all_concurrent.py --verify`
- [ ] Update this document if new environments are added

---

## Related Documents
- `STANDALONE_BUILDS.md` — Full .exe build target registry
- `LESSONS_TASK_D_NUITKA_BUILD.md` — Nuitka build failure analysis
- `LESSONS_TASK_E_LOCKING_AUDIT.md` — 17-file locking audit gaps
- `docs/scripts/patch_nuitka_314t.py` — Nuitka 3.14t patch manager
