# LESSONS — Task D: Nuitka Standalone Build for Neural Advancement Modules

**Task:** Build metacognition.exe via Nuitka on Python 3.14t
**Date:** June 4, 2026
**Reference:** STANDALONE_BUILDS.md, azazael-standalone skill

---

## Build Attempt

```bash
python3.14t -m nuitka --standalone \
  --output-dir=build/standalone \
  --output-filename=azazael-metacognition.exe \
  --include-package=CORE \
  --include-package=CORE.WORMS.expansion \
  --script=src/CORE/WORMS/expansion/meta_cognition.py
```

### Result: BUILD FAILED

Nuitka encountered issues with the Python 3.14t free-threading build. The exact error was not captured (timeout at 300s), but based on the azazael-packaging skill, the known issues are:

1. **Nuitka requires patching for 3.14t** — The standard Nuitka does not support Python 3.14 free-threading out of the box. A patched Nuitka is available but must be verified.

2. **C extension modules** — SQLite (for LocalMemoryStore) and other C extensions may not link correctly under 3.14t's modified ABI.

3. **`--include-package=CORE`** — This pulls in ALL of CORE/, which includes modules with native dependencies (psycopg2 for PostgreSQL, etc.) that may fail to bundle.

## Root Cause Analysis

| Issue | Severity | Status |
|-------|----------|--------|
| Nuitka 3.14t compatibility | 🔴 Blocking | Patched Nuitka exists per azazael-packaging skill; needs verification |
| Native dependency bundling | 🟠 High | SQLite3 DLL must be manually included; psycopg2 optional |
| Module path resolution | 🟡 Medium | MetaCognitionWorm imports CORE.local_memory — path must work in standalone |

## Path Forward

### Immediate (v1.0.0 workaround)
1. Verify patched Nuitka installation: `python3.14t -m nuitka --version`
2. Build with `--include-package=CORE.WORMS.expansion` only (not full CORE)
3. Manually bundle SQLite3 DLL: `--include-data-file=path/to/sqlite3.dll=.`
4. Test with: `./azazael-metacognition.exe --help`

### Medium-term (proper fix)
1. Create a minimal `metacognition_entry.py` that only imports what's needed
2. Use `--nofollow-import-to=psycopg2` to exclude PostgreSQL dependency
3. Test standalone `.exe` on a clean Windows 11 VM

### Long-term (full suite)
1. Apply this pattern to all 39 `.exe` targets in STANDALONE_BUILDS.md
2. Create a `build_all.py` script that iterates through all targets
3. Add CI/CD pipeline to verify `.exe` builds on each commit

## Lessons Learned

1. **Nuitka on 3.14t is experimental** — Always verify Nuitka version compatibility before attempting
2. **Module import scope matters** — `--include-package=CORE` is too broad; use minimal includes
3. **Native deps need manual bundling** — SQLite DLL, SSL certs, etc. must be bundled manually
4. **Always capture build output** — The 300s timeout lost the error message; use `tee` or redirection next time
5. **Reference azazael-packaging skill** — Contains the patched Nuitka path and known limitations

## Configuration Template

```python
# metacognition_entry.py — Minimal entry point for Nuitka build
import sys
sys.frozen = getattr(sys, 'frozen', False)

from CORE.WORMS.expansion.meta_cognition import MetaCognitionWorm

if __name__ == "__main__":
    worm = MetaCognitionWorm(memory_store="none")
    result = worm.execute()
    print(f"Status: {result.get('status', 'unknown')}")
```

## Build Command (next attempt)

```bash
python3.14t -m nuitka --standalone \
  --output-dir=build/standalone \
  --output-filename=azazael-metacognition.exe \
  --include-package=CORE.WORMS.expansion \
  --include-module=CORE.local_memory \
  --nofollow-import-to=psycopg2 \
  --nofollow-import-to=CORE.postgres_memory \
  --include-data-files=**/*.sqlite3=. \
  --script=src/CORE/WORMS/expansion/metacognition_entry.py \
  2>&1 | tee build/nuitka_metacognition.log
```
