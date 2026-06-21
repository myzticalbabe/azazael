# LESSONS — Task G: Concurrent Nuitka Build Architecture

**Task:** Design and implement concurrent Nuitka builds across Windows 11 + WSL2
**Date:** June 4, 2026
**Reference:** build_all_concurrent.py, LESSONS_TASK_D_NUITKA_BUILD.md, NUITKA_3_14T_SKILL.md

---

## The 39-Target Registry Architecture

The build system registers 39 standalone `.exe` targets across 6 tiers:

| Tier | Count | Examples | Priority |
|------|-------|----------|----------|
| **neural** | 6 | metacognition, evolution, dreaming, learning, race_detector, error_recovery | P0 |
| **core** | 5 | clusterworms, metacluster, concurrency, cross_nature, codex_tools | P0 |
| **monitor** | 8 | systemz, processz, diskz, networxz, clockz, metricz, diagnostic, smartdisk | P1 |
| **security** | 5 | binary_analysis, error_scan, healing, morphing, reverse_tools | P1 |
| **ml** | 5 | systemz_ml, wormz_ml, cain, omni, codex_studio | P2 |
| **expansion** | 9 | db_monitor, backup, config_validator, container_manager, migration_engine, communication_bus, profiling_engine, telemetry_collector, security_auditor | P2 |

Each target has: `entry` (source script path), `output` (`.exe` filename), and `tier`.

---

## Lesson G1: Nuitka 4.1.2 on Python 3.14t — LNK2001 Unresolved External Symbols

**Diagnosis evolution:** The original error appeared as `--output-dir='.' requires an argument`. This was a RED HERRING — the actual failure was deeper in the build pipeline.

**What actually happens (two separate failures on two separate runs):**

**Run 1 (before fixes):** The original script had the `succeed` typo and `cd /root/azazael` patterns. Windows builds failed with `--output-dir='.' requires an argument` — the actual cause is unclear (possibly path construction or Nuitka 4.1.2 experimental support). WSL2 builds failed with `cd /root/azazael: No such file or directory`.

**Run 2 (after fixes):** After fixing the typo and WSL2 paths, a diagnostic test with explicit `--output-dir=C:/Users/clint/azazael/build/test_windows` ran successfully through Python-to-C compilation and into the Scons C backend. The failure THEN was `LNK2001: unresolved external symbol` for `GEN_THRESHOLD`, `GEN_COUNT`, `GEN_INC_COUNT` — a linker failure, not a flag issue.

**The `--output-dir` red herring:** The original error was misleading. With proper paths, Nuitka's argument parser works correctly. The real barrier is linker-level symbol resolution for free-threaded Python 3.14t code.

**Prevention:**
- When a build fails with a mysterious flag error, check the FULL output, not just the last line
- Nuitka builds produce output in stages: Python→C compilation → C compilation → Linking
- Linker errors (`LNK2001`, `undefined reference`) are a different class from flag errors
- Nuitka explicitly warns: "Python 3.14 is only experimentally supported"

---

## Lesson G2: succeed→success Typo — The Cost of Untested Code

**Bug:** `build_concurrent()` printed `{succeed}/{len(results)} succeeded` but `succeed` was never defined. The `NameError` crashed the script AFTER all builds completed, losing the build manifest.

**Root cause:** The variable was `success` (line 313: `success = sum(1 for r in results if r["success"])`), but the f-string referenced `succeed`. This is a classic typo that syntax checkers can't catch (both are valid identifiers) and only manifests at runtime.

**Lesson:** The script was never tested end-to-end. The first actual run crashed at the finish line. **Always dry-run or test orchestration scripts with at least one real build before trusting them with 39 targets.**

**Prevention rule:** Every orchestration script MUST be tested with `--target <single_target> --platform windows` before running `--all`.

---

## Lesson G3: WSL2 Build Command Construction — No `cd`, Absolute Paths

**Original failure:** `bash: line 1: cd /root/azazael: No such file or directory`

**The trap:** Using `cd /root/azazael && python3.14t -m nuitka ...` as a single bash command. When WSL2 starts, the working directory might not be resolvable, making `cd` fail before the build even starts.

**The fix — absolute paths everywhere:**
```python
# BEFORE (fragile — depends on cd working):
cmd = "cd /root/azazael && python3.14t -m nuitka --script src/CORE/WORMS/expansion/meta_cognition.py ..."

# AFTER (robust — no cd dependency):
entry_wsl = f"/root/azazael/{target['entry']}"
cmd = f"python3.14t -m nuitka --script {entry_wsl} --output-dir {out_wsl} ..."
```

**Also needed:** `--include-plugin-directory /root/azazael/src` so Nuitka can find CORE imports during compilation.

**Prevention:** Never use `cd` in WSL build commands. Always use absolute paths. The WSL environment's starting directory is not guaranteed to be accessible.

---

## Lesson G4: `shlex.join()` for Safe WSL Command Construction

**Pattern:** Build command parts as a Python list, then `shlex.join()` for safe shell escaping:

```python
cmd_parts = [
    "python3.14t", "-m", "nuitka",
    "--standalone", "--assume-yes-for-downloads",
    "--output-dir", out_wsl,
    "--output-filename", target["output"],
    "--nofollow-import-to", "psycopg2",
    "--nofollow-import-to", "CORE.postgres_memory",
    "--include-plugin-directory", "/root/azazael/src",
    "--script", entry_wsl,
]
cmd = shlex.join(cmd_parts)  # Safe: handles spaces, special chars
```

**Why not string concatenation:** Paths can contain spaces, parentheses, or special characters. `shlex.join()` properly quotes each argument.

**Prevention:** Always use list-based command construction + `shlex.join()` for WSL subprocess commands. Never use f-string or `+` concatenation for shell commands.

---

## Lesson G5: Dual-Platform Build Architecture — Windows + WSL2 in ThreadPoolExecutor

**Design:** `build_concurrent()` uses `ThreadPoolExecutor` to run Windows and WSL2 builds simultaneously:

```python
with ThreadPoolExecutor(max_workers=max_workers) as pool:
    for name in targets:
        if platform in ("windows", "both"):
            futures.append(pool.submit(build_target_windows, name, t, win_dir))
        if platform in ("wsl", "both"):
            futures.append(pool.submit(build_target_wsl, name, t, wsl_dir))

    for future in as_completed(futures):
        r = future.result()
        results.append(r)
```

**Why ThreadPoolExecutor not ProcessPoolExecutor:** Nuitka builds are I/O-bound (file writing, subprocess calls), not CPU-bound. Threads are sufficient and avoid serialization overhead.

**Output separation:** Windows builds go to `build/standalone/<timestamp>/windows/`, WSL2 builds to `build/standalone/<timestamp>/wsl/`. The timestamped directory isolates each build run.

**Build manifest:** `build_manifest.json` records every build attempt with target, platform, status, duration, and error. This is critical for CI/CD traceability.

---

## Lesson G6: `--include-plugin-directory` — The Missing Piece for WSL2

**Discovery:** WSL2 Nuitka builds failed because the CORE package couldn't be found during compilation. The solution was `--include-plugin-directory /root/azazael/src` which adds the source directory to Nuitka's plugin search path.

**Why this matters:** Nuitka's `--include-package=CORE` looks for CORE in the Python path, but `--include-plugin-directory` tells Nuitka where to find module source files during C compilation. Both are needed for standalone builds.

---

## Session Actions Recorded

| Action | File | Result |
|--------|------|--------|
| Diagnosed LNK2001 as root cause (not --output-dir) | build_all_concurrent.py | Linker failure, not flag issue |
| Fixed succeed→success typo | build_all_concurrent.py line 323 | Script no longer crashes at finish |
| Fixed WSL2 cd→absolute paths | build_all_concurrent.py `build_target_wsl()` | WSL builds use absolute paths |
| Added --include-plugin-directory | build_all_concurrent.py `build_target_wsl()` | CORE package resolution |
| Verified Nuitka 4.1.2 on both platforms | build_all_concurrent.py `--verify` | Both platforms OK |
| Tested neural tier build (6 targets x 2 platforms) | build_all_concurrent.py `--tier neural --platform both` | 0/12 passed (LNK2001 for all) |

**Cross-reference:** LESSONS_TASK_D_NUITKA_BUILD.md (initial build attempt), LESSONS_TASK_F_ENVIRONMENT_ALIGNMENT.md (sync prerequisite). The concurrent build depends on environment sync being done first.
