# LESSONS_DEV_TOOLS.md — Effective Dev Commands for Codebase Remediation

> **Created:** June 5, 2026
> **Purpose:** One-stop reference for commands that fix, verify, and maintain the Azazael codebase.
> **Companions:** LESSONS_MASTER.md (insights), ERROR_LOG.md (errors), MEMORIES.md (anti-patterns)

---

## TABLE OF CONTENTS

1. [Syntax & Compilation Checks](#1-syntax--compilation-checks)
2. [Type Checking (mypy)](#2-type-checking-mypy)
3. [Worm Registry & Discovery](#3-worm-registry--discovery)
4. [Import Hygiene](#4-import-hygiene)
5. [Test Suite](#5-test-suite)
6. [Code Formatting & Linting](#6-code-formatting--linting)
7. [Build System](#7-build-system)
8. [Memory & Database](#8-memory--database)
9. [Environment Verification](#9-environment-verification)
10. [Performance Profiling](#10-performance-profiling)
11. [Crash Diagnosis & Monitoring](#11-crash-diagnosis--monitoring)
12. [Git & Code Review](#12-git--code-review)
13. [Quick-Reference Cheat Sheet](#13-quick-reference-cheat-sheet)

---

## 1. Syntax & Compilation Checks

### 1.1 Full Syntax Audit (All .py files)

```bash
cd azazael
python -c "
import py_compile, sys
from pathlib import Path
src = Path('src')
py_files = list(src.rglob('*.py'))
total = len(py_files)
print(f'Checking {total} .py files...')
errors = []
for f in py_files:
    try:
        py_compile.compile(str(f), doraise=True)
    except py_compile.PyCompileError as e:
        errors.append((str(f), str(e)))
print(f'Result: {total - len(errors)} passed, {len(errors)} failed')
for path, err in errors[:20]:
    print(f'  {path}: {err[:120]}')
sys.exit(1 if errors else 0)
"
```

| What | When | Expected |
|------|------|----------|
| Checks ALL `.py` files compile | After any refactoring or import changes | 313+ passed, 0 failed |

**⚠️ Pitfall:** `SyntaxWarning` for invalid escape sequences (e.g., `\d` in strings) does NOT fail compilation. Use `-W error` to treat warnings as errors if desired.

### 1.2 Single File Syntax Check

```bash
python -m py_compile src/CORE/WORMS/CLUSTERWORMS.py && echo "Syntax OK"
```

| What | When | Expected |
|------|------|----------|
| Quick check on one file | After editing a specific file | `Syntax OK` |

### 1.3 Project-Level Script

```bash
cd azazael
python -c "
import py_compile
for path in __import__('pathlib').Path('src').rglob('*.py'):
    py_compile.compile(str(path), doraise=True)
print('All files syntax-clean')
"
```

---

## 2. Type Checking (mypy)

### 2.1 Check Specific Files (Recommended)

```bash
cd azazael
python -m mypy src/CORE/WORMS/CLUSTERWORMS.py --ignore-missing-imports --no-error-summary
```

| What | When | Expected |
|------|------|----------|
| Targeted type check | After editing a specific file | 0 errors |

**Why `--ignore-missing-imports`:** The project has optional dependencies (psutil, psycopg2, tkinter) and non-standard module layouts. Without this flag, mypy reports hundreds of false-positive "Cannot find module" errors.

### 2.2 Check a Whole Directory

```bash
cd azazael
python -m mypy src/CORE/WORMS/ --ignore-missing-imports --no-error-summary 2>&1 | grep -c "error:"
```

### 2.3 Find Files With Most Errors

```bash
cd azazael
python -m mypy src/CORE/ --ignore-missing-imports --no-error-summary 2>&1 | \
  grep "\.py:" | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

**Note:** For a total error count across all files, append `| awk '{sum+=$1} END {print sum}'` instead of `head -10`.

| What | When | Expected |
|------|------|----------|
| Rank files by error count | Prioritizing mypy cleanup | Top offenders listed |

### 2.4 Common mypy Fix Patterns

| Error | Fix |
|-------|-----|
| `Name "X" is not defined` | Add missing import |
| `Incompatible default for parameter` | Change `param = None` to `param: Optional[Type] = None` |
| `"object" has no attribute "X"` | Add type annotation, use `isinstance()` guard, or use `.get()` |
| `Too many arguments for "ModuleSpec"` | Missing `@dataclass` decorator or import |
| `"Collection[str]" has no attribute "append"` | Change `Collection` to `List` for mutable sequences |
| `All conditional function variants must have identical signatures` | Add `# type: ignore[misc]` on fallback function |

---

## 3. Worm Registry & Discovery

### 3.1 Full Registry Discovery

```bash
cd azazael
python -c "
import sys, time
sys.path.insert(0, 'src')
start = time.time()
from CORE.worm_registry import discover_worms, get_worms_by_category, get_all_categories
n = discover_worms()
print(f'Discovery: {n} worms in {time.time()-start:.1f}s')
cats = get_all_categories()
print(f'Categories: {len(cats)} -> {sorted(cats)}')
for cat in sorted(cats):
    worms = get_worms_by_category(cat)
    names = sorted(worms.keys())
    print(f'  {cat} ({len(worms)}): {chr(44).join(names)}')
"
```

| What | When | Expected |
|------|------|----------|
| Full worm census | After adding/removing worms, or session startup | ~226 worms, 35 categories, <15s (clean rebuild; stale pickle cache under-reports — delete `~/.azazael/worm_registry_cache.pkl` if counts look old) |

**⚠️ Pitfall:** First call takes ~10s (cold start imports all worm modules). Second call is <1s (cached). See Lesson #30.

### 3.2 Quick Worm Count

```bash
cd azazael
python -c "import sys; sys.path.insert(0,'src'); from CORE.worm_registry import discover_worms; print(f'{discover_worms()} worms registered')"
```

### 3.3 Verify a Specific Worm Imports

```bash
cd azazael
python -c "import sys; sys.path.insert(0,'src'); from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ; print('OK')"
```

---

## 4. Import Hygiene

### 4.1 Check for Unused Imports

```bash
cd azazael
python -m autoflake --check --remove-all-unused-imports --recursive src/ 2>&1 | head -20
```

| What | When | Expected |
|------|------|----------|
| Find unused imports | Before committing, to reduce clutter | List of files with unused imports |

### 4.2 Auto-Remove Unused Imports

```bash
python -m autoflake --in-place --remove-all-unused-imports src/CORE/WORMS/DISKZ.py
```

**⚠️ Pitfall:** `autoflake` is pure-Python and works on 3.14t (despite past misdiagnosis — see Lesson #36). Never use `--recursive` blindly — test one file first.

### 4.3 Find Function-Body Imports (Thread-Safety Risk)

```bash
cd azazael
grep -rPn "^[[:space:]]+(import |from )" src/ --include="*.py" | grep -v "__init__.py" | head -20
```

**Note:** `-P` (Perl regex) is available in GNU grep (Git Bash on Windows ships this). Without `-P`, use `grep -E "^[[:space:]]+(import |from )"`.

| What | When | Expected |
|------|------|----------|
| Find imports inside functions | 3.14t thread-safety audit | Empty or very few results |

**Why this matters:** Function-body imports called from thread pools cause deadlocks under Python 3.14t free-threading (Lesson #28, #29).

### 4.4 Find Bare `except:` Clauses

```bash
cd azazael
grep -rn "except:" src/ --include="*.py" | grep -v "except Exception" | grep -v "except (" | head -20
```

---

## 5. Test Suite

### 5.1 Run All Standalone Tests

```bash
cd azazael
python run_tests.py --skip-slow
```

| What | When | Expected |
|------|------|----------|
| Full test suite (fast) | After any code change | All passing (87+ tests) |

**⚠️ Pitfall:** `pytest` segfaults on Python 3.14t (Error #48). Use standalone execution: `python tests/test_*.py` or `run_tests.py`.

### 5.2 Run Specific Test Files

```bash
cd azazael
python tests/test_clusterworms_unit.py
python tests/test_config_and_breaker.py
python tests/test_nature_clusters_unit.py
```

### 5.3 Run a Single Test Manually

```bash
cd azazael
python -c "
import sys; sys.path.insert(0, 'src')
from CORE.worm_registry import discover_worms
n = discover_worms()
assert n >= 80, f'Expected >=80 worms, got {n}'
print(f'OK: {n} worms')
"
```

### 5.4 Test With Coverage

```bash
cd azazael
python -m coverage run -m pytest tests/ -x 2>/dev/null || \
python -m coverage run run_tests.py --skip-slow
python -m coverage report -m 2>/dev/null | head -30
```

**⚠️ Pitfall:** `pytest` on 3.14t segfaults. Use `run_tests.py` as fallback. Coverage with standalone execution may not capture all paths.

---

## 6. Code Formatting & Linting

### 6.1 Check for Unicode Emoji (Windows Terminal Crash Risk)

```bash
cd azazael
grep -rnP "[\x{2705}\x{2717}\x{1F537}\x{26A1}\x{2714}\x{274C}]" src/ --include="*.py" | head -20
```

| What | When | Expected |
|------|------|----------|
| Find emoji chars that crash Windows terminals | Before commit | Empty (no emoji) |

**Fix:** Replace `✓` → `OK`, `✗` → `FAIL`, `🔷` → `*`, `⚡` → `>>` (MEMORIES.md Anti-Pattern #2).

### 6.2 Find Trailing Whitespace

```bash
cd azazael
grep -rn " $" src/ --include="*.py" | head -20
```

### 6.3 Find Hardcoded Paths

```bash
cd azazael
grep -rn "C:\\\\Users\\\\clint" src/ --include="*.py" | head -20
```

| What | When | Expected |
|------|------|----------|
| Find hardcoded user paths | Refactoring, portability audit | Should use `CORE.paths` or `Path.home()` |

---

## 7. Build System

### 7.1 Build All Standalone EXEs

```bash
cd C:/Users/clint/Desktop/AZAZAEL_Standalone
python build_all.py
```

| What | When | Expected |
|------|------|----------|
| Build 52 standalone .exe files | After source changes that affect built modules | 52 built, 0 failed |

### 7.2 Build a Single EXE

```bash
cd C:/Users/clint/Desktop/AZAZAEL_Standalone
python build_all.py CLUSTERWORMS
```

### 7.3 Smoke Test All EXEs

```bash
cd C:/Users/clint/Desktop/AZAZAEL_Standalone
python build_all.py --smoke-test
```

| What | When | Expected |
|------|------|----------|
| Run --help on every built EXE | After build, to verify executables work | Pass/fail/skip counts |

**⚠️ Pitfall:** Smoke tests take 10+ minutes for 52 EXEs. CODEX_Studio (Tkinter) may timeout. Use 600s timeout.

### 7.4 Regenerate BAT Launchers

```bash
cd C:/Users/clint/Desktop/AZAZAEL_Standalone
python regenerate_bats.py
```

### 7.5 Verify Nuitka 3.14t Patches

```bash
python azazael/docs/scripts/patch_nuitka_314t.py --verify
```

**⚠️ Pitfall:** Must run `--apply` before any build. Patches fix 7 C-level incompatibilities between Nuitka 4.1.2 and Python 3.14t free-threading (Error #16).

---

## 8. Memory & Database

### 8.1 Initialize Memory Store (After LocalMemoryStore Fix)

```bash
cd azazael
python -c "
import sys; sys.path.insert(0, 'src')
from CORE.local_memory import LocalMemoryStore
store = LocalMemoryStore()
store.start_session(source='Codebuff')
print(f'Session: {store.current_session_id}')
stats = store.get_stats()
print(f'Memories: {stats[\"total_memories\"]}, Sessions: {stats[\"total_sessions\"]}')
"
```

| What | When | Expected |
|------|------|----------|
| Quick memory store health check | Session startup | Instant (0.00-0.01s per operation) |

### 8.2 Query Recent Memories

```bash
cd azazael
python -c "
import sys; sys.path.insert(0, 'src')
from CORE.local_memory import LocalMemoryStore
store = LocalMemoryStore()
for m in store.recall_recent(5):
    print(f'[{m[\"source\"]}] {m[\"event_type\"]} — {m[\"timestamp\"][:19]}')
"
```

### 8.3 Database Health Check

```bash
cd azazael
python -c "
import sys; sys.path.insert(0, 'src')
from CORE.local_memory import LocalMemoryStore
store = LocalMemoryStore()
health = store.health_check()
print(f'Score: {health[\"score\"]}/100 (Grade: {health[\"grade\"]})')
for dim, d in health['details'].items():
    print(f'  {dim}: {d[\"score\"]}/{d[\"max\"]}')
if health['warnings']:
    for w in health['warnings']:
        print(f'  WARN: {w}')
"
```

### 8.5 Sync Status Across Environments (Lesson #54)

```bash
cd azazael
python scripts/sync_all.py --status     # Check drift across 5 environments
python scripts/sync_all.py --verify     # Verify all environments aligned
python scripts/sync_all.py --sync-all   # Full sync from Windows → all targets
```

| What | When | Expected |
|------|------|----------|
| Check env alignment | After cross-machine work | All environments synced |

### 8.6 Direct SQLite Access (Emergency Bypass)

```bash
sqlite3 ~/.azazael/memory_store.db "SELECT COUNT(*) FROM memories; SELECT COUNT(*) FROM sessions;"
```

---

## 9. Environment Verification

### 9.1 Full Tooling Check (Session Startup)

```bash
cd azazael
python scripts/check_tooling.py
```

| What | When | Expected |
|------|------|----------|
| Verify all CLI tools, pip packages, and npm globals | Every session start | All critical tools pass |

### 9.2 Verify Python 3.14t

```bash
python -c "import sys; v=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'; ft=hasattr(sys,'_is_gil_enabled') and not sys._is_gil_enabled(); print(f'Python {v} — Free-threaded: {ft}')"
```

Expected: `Python 3.14.5 — Free-threaded: True`

### 9.3 Check Key Dependencies

```bash
python -c "import PIL; print(f'Pillow: OK')"
python -c "import psutil; print(f'psutil: {psutil.__version__}')"
python -c "import numpy; print(f'numpy: {numpy.__version__}')"
```

### 9.4 Fix Broken 3.14t Package

```bash
pip install --force-reinstall --no-deps psutil
```

| What | When | Expected |
|------|------|----------|
| Fix C-extension segfault on 3.14t | Import crashes with segfault/SIGSEGV | Package works after reinstall |

**When to use:** psutil, pydantic-core, uuid-utils, or any C/Rust extension that segfaults on 3.14t (Errors #49, #54).

### 9.5 Verify FreeBuff/Bun

```bash
export PATH="$HOME/.bun/bin:$PATH"
bun --version        # Expected: >=1.3.14
freebuff --version   # Expected: 0.0.103
```

---

## 10. Performance Profiling

### 10.1 Profile Worm Discovery

```bash
cd azazael
python -c "
import sys, time, cProfile, pstats
sys.path.insert(0, 'src')
profiler = cProfile.Profile()
profiler.enable()
from CORE.worm_registry import discover_worms
n = discover_worms()
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumtime')
stats.print_stats(20)
print(f'\\n{n} worms discovered')
"
```

### 10.2 Profile Slow Import

```bash
cd azazael
python -c "
import sys, time
sys.path.insert(0, 'src')
t = time.time()
import CORE.WORMS.BINARY_ANALYSIS
print(f'BINARY_ANALYSIS import: {time.time()-t:.2f}s')
"
```

### 10.3 Find Slowest Imports

```bash
cd azazael
python -c "
import sys, time
sys.path.insert(0, 'src')
from pathlib import Path
worms = sorted(Path('src/CORE/WORMS').glob('*.py'))
for w in worms:
    mod = w.stem
    t = time.time()
    try:
        __import__(f'CORE.WORMS.{mod}', fromlist=[mod])
        print(f'{mod}: {time.time()-t:.2f}s')
    except Exception as e:
        print(f'{mod}: FAIL ({e})')
" | sort -t: -k2 -rn | head -10
```

---

## 11. Crash Diagnosis & Monitoring

### 11.1 Check WER Crash Dumps

```bash
ls -la "$LOCALAPPDATA/CrashDumps/freebuff*.dmp" 2>/dev/null || echo "No crash dumps"
```

### 11.2 Launch FreeBuff With Crash Monitoring

```batch
:: From Desktop
freebuff_monitor.bat
```

### 11.3 Check Bun Version in Binary

```bash
strings ~/.config/manicode/freebuff.exe | grep -i "bun.*v\?[0-9]" | head -5
```

---

## 12. Git & Code Review

### 12.1 Check What Changed

```bash
cd azazael
git diff --stat
git diff src/CORE/local_memory.py
```

### 12.2 View Recent Commits

```bash
cd azazael
git log --oneline -10
```

### 12.3 Find All Modified Python Files

```bash
cd azazael
git diff --name-only | grep "\.py$"
```

### 12.4 Syntax Check Only Changed Files

```bash
cd azazael
git diff --name-only | grep "\.py$" | xargs -I{} python -m py_compile "{}" 2>&1
```

**Or one file at a time with status:**
```bash
cd azazael
git diff --name-only | grep "\.py$" | while IFS= read -r f; do
    python -m py_compile "$f" 2>/dev/null && echo "OK: $f" || echo "FAIL: $f"
done
```

---

## 13. Quick-Reference Cheat Sheet

### Session Startup (Run Every Session)

```bash
# 1. Verify environment
cd azazael && python scripts/check_tooling.py

# 2. Syntax audit
python -c "import py_compile; [py_compile.compile(str(f),doraise=True) for f in __import__('pathlib').Path('src').rglob('*.py')]; print('All clean')"

# 3. Worm registry
python -c "import sys;sys.path.insert(0,'src');from CORE.worm_registry import discover_worms;print(f'{discover_worms()} worms')"
```

### After Editing a File

```bash
# 1. Syntax
python -m py_compile src/CORE/WORMS/edited_file.py

# 2. Type check
python -m mypy src/CORE/WORMS/edited_file.py --ignore-missing-imports --no-error-summary

# 3. Import check
python -c "import sys;sys.path.insert(0,'src');from CORE.WORMS.edited_file import *" 2>&1

# 4. Run related tests
python tests/test_clusterworms_unit.py 2>&1 | tail -5
```

### When Things Break

| Symptom | Command |
|---------|---------|
| Import segfault (3.14t) | `pip install --force-reinstall --no-deps <package>` |
| Worm not found | `python -c "import sys;sys.path.insert(0,'src');from CORE.worm_registry import discover_worms;print(discover_worms())"` |
| Memory store hangs | Check `~/.azazael/` exists: `ls ~/.azazael/memory_store.db` |
| Nuitka build fails | `python azazael/docs/scripts/patch_nuitka_314t.py --apply` |
| pytest segfault | Use `python tests/test_*.py` instead (standalone execution) |
| SyntaxError on f-string | Extract computed expressions to variables before f-string |
| UnicodeEncodeError | Replace emoji with ASCII: ✓→OK, ✗→FAIL, 🔷→* |
| Mypy "name not defined" | Add missing import or `# type: ignore[name-defined]` |
| FreeBuff crash | Check `ls "$LOCALAPPDATA/CrashDumps/freebuff*.dmp"` |

### Package Management Decision Tree

```
Is the package pure-Python (no .pyd/.so)?
├── YES → Standard install: pip install <pkg>
└── NO (has C/Rust extension)
    └── Does it segfault on import?
        ├── YES → pip install --force-reinstall --no-deps <pkg>
        └── NO  → Check wheel: does tag contain 'cp314t'?
            ├── YES → Standard install
            └── NO  → No 3.14t wheel exists — use alternative
```

---

## Related Files

| File | Purpose |
|------|---------|
| `LESSONS_MASTER.md` | 57 hard-won insights across all domains |
| `ERROR_LOG.md` | 55+ errors with root cause + fix + prevention |
| `MEMORIES.md` | Anti-patterns, architecture, session metrics |
| `CODEBASE_AUDIT_TODO.md` | Production roadmap (12 Steps + 12 AR items) |
| `SESSION_STARTUP.md` | Next-session congruency marker |
| `scripts/check_tooling.py` | Automated environment verification |

## Companion Skills

| Skill | Load with | Covers |
|-------|-----------|--------|
| `azazael-testing` | `skill azazael-testing` | Pre-commit checklist, validation commands |
| `azazael-error-resolution` | `skill azazael-error-resolution` | Error diagnosis decision tree |
| `azazael-conventions` | `skill azazael-conventions` | Coding patterns, anti-patterns |
| `azazael-environment` | `skill azazael-environment` | Python 3.14t setup, dependencies |
