# Environment Audit — 2026-08-29

## Graphify
- Refreshed all 4 repos (azazael, vermillion_lightfury, aoa_g, aoa_source) via scripts/graphify_refresh_all.sh --no-desktop
- Atlas: C:/Users/clint/Desktop/Graphify_Codebase_Atlas_2026-08-27 (fresh 19:22-19:23)

## Dedup scan (MD5, source text only, <5MB files, cache/archive dirs excluded)
| Root | Files | Dup groups | Wasted |
|---|---|---|---|
| win (C:/Users/clint/azazael) | ~26k | many | — |
| g_root (G:/AZAZAEL) | 2653 | 546 | 10.6 MB |
| g_sot (G:/AZAZAEL_SOURCE_OF_TRUTH) | 6945 | 555 | 15.4 MB |
| desktop (AZAZAEL_Standalone) | 60 | 0 | 0 |

Cross-root duplicate groups: 5411 (36.8 MB redundant text total)
- 4260 groups g_sot+win, 842 groups g_root+g_sot+win
- Worst: .nox site-packages pip copies, native/worm_manifest target/doc js, SESSION_TEMPLATE html x7-8, .agents/skills SKILL.md x8

## src/src double-nesting (G:/AZAZAEL/AZAZAEL_ROOT)
- inner src/src: 305 .py (67 identical, 238 divergent), 1390 files total
- ACTION TAKEN: all 1390 backed up to src_src_divergent_backup_20260829, 305 .py replaced with deprecation shims (depth-aware canonical resolution), 851 identical non-py deleted
- Verified: 0 syntax errors, 0 missing canonical targets, live import OK with DeprecationWarning
- Log: G:/AZAZAEL/AZAZAEL_ROOT/src_src_dedup_log_20260829.json

## Drive status
- C: 96% (722/756G) — .ollama 21G, _bazel_clint ~3.1G, disclosure_frames 1G, temp_build 661M, tf-build 605M, llama.cpp 1.2G+, venv-interpreter 644M, nuitka_* 530M
- G: 99% (472/477G) — archive_ollama 21G (dup of C:/.ollama), Desktop_Archive 3.2G, kali_recovery.vhdx 67G, FOUND.000-003, duplicate archive_* pairs
- E: 2% (1.9/97G) — Kali_build (store Kali was installed here, then unregistered)

## Kali rebuild status- Store kali-linux installed to E:\Kali_build\rootfs, then UNREGISTERED per user request ("not the store kali")
- G:/kali_recovery.vhdx (67G, Aug 23) is valid vhdxfile magic — crashed Kali recovery disk- Store fresh disk preserved at E:\Kali_build\rootfs\ext4_store_fresh.vhdx.bak (E: rootfs dir vanished after unregister — needs re-check)- NEXT: restore recovery vhdx to E:, wsl --import-in-place kali-linux E:\Kali_build\rootfs ext4.vhdx

## Sync status
- WSL2 Ubuntu-26.04: FAIL (expansion/tests/scripts) — re-sync after Kali restore
- Integrity: OUT OF SYNC overall
