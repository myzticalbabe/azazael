---
name: azazael-fix-python-314t
description: Quick-reference fixes for Python 3.14t free-threading errors — segfaults, wheel issues, Nuitka patches, and concurrency bugs.
metadata:
  category: fixes
  project: azazael
---

# 🛠️ Skill: Fixes for Python 3.14t Free-Threading

*Quick-reference solutions extracted from ERROR_LOG.md for known errors in Python 3.14t Free-Threading.*

## Error #16 — Nuitka 4.1.2 C-backend failures on Python 3.14t free-threading build
**Symptom:** Nuitka 4.
**Fix Solution:**
Patched all 5 files with 7 targeted fixes (see NUITKA_3_14T_SKILL.md for details).
**Verification:** In progress — rebuild still in testing phase.**Prevention:** Upstream Nuitka 4.2+ may include proper 3.14t support. Monitor https://nuitka.net/changelog/Changelog.html for free-threading fixes. Python 3.13 is not used — all builds are on 3.14t with patches applied via `patch_nuitka_314t.py`.
**Prevention:**
Upstream Nuitka 4.2+ may include proper 3.14t support. Monitor https://nuitka.net/changelog/Changelog.html for free-threading fixes. Python 3.13 is not used — all builds are on 3.14t with patches applied via `patch_nuitka_314t.py`.

---
## Error #48 — pytest 9.0.3 Segfaults on Python 3.14.5t Free-Threading
**Symptom:** pytest 9.
**Fix Solution:**
Requires a pytest release compatible with Python 3.14t free-threading (pytest 10.0+ or patched 9.0.x). Not fixable at the project level.
**Prevention:**
Run tests standalone on 3.14t via `python tests/test_*.py` or `python run_tests.py`.

### Corrected: Previous diagnosis was wrong

The original Error #48 entry incorrectly attributed the 3.14t segfault to module-level `sys.exit()` in test files. That was a *separate* bug on Python 3.13 producing a clean `INTERNALERROR> SystemExit`. The two issues were conflated. The 3.14t segfault is a fundamental

---
## Error #49 — psutil C Extension Segfaults on Python 3.14.5t Free-Threading
**Symptom:** The `psutil` library (Python system/process monitoring) uses C extensions that are incompatible with Python 3.
**Fix Solution:**
`pip install --force-reinstall --no-deps psutil` — pip had installed a non-free-threading wheel. Reinstalling selected the correct `cp314t` wheel (`psutil-7.2.2-cp314-cp314t-win_amd64.whl`), which works on 3.14.5t. After reinstall:
- `import psutil` → OK
- `psutil.cpu_count()` → 16
- `psutil.virtual_memory()` → 15.4 GB
- `ClusterWORMZ.execute_worm('PROCESSZ')` → success=True
**Prevention:**
See ERROR_LOG.md

---
## Error #50 — psycopg2-binary cp314t Wheel Missing Bundled DLLs
**Symptom:** The `psycopg2_binary-2.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
Before relying on a C-extension package on Python 3.14t, verify the wheel contains ALL runtime dependencies, not just the .pyd. Check wheel contents with:
```python
import zipfile
with zipfile.ZipFile('wheel.whl') as z:
    names = z.namelist()
    has_dlls = any(n.endswith('.dll') for n in names)
    print(f'Has bundled DLLs: {has_dlls}')
```

---
## Error #54 — pydantic-core / uuid-utils cp314t Wheel Segfault on Python 3.14.5t
**Symptom:** The installed wheels for `pydantic-core` and `uuid-utils` had broken/incorrect `cp314t` compiled `.
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
1. When upgrading packages on 3.14t, always verify the wheel tag contains `t` (e.g., `cp314t`)
2. If a Rust/C extension segfaults, try `pip install --force-reinstall --no-deps <package>` first — pip may resolve to a newer/better wheel
3. Do NOT patch site-packages with fallback code — fix the actual wheel installation
4. If `pip install --upgrade pydantic` causes a version mismatch (e.g., pydantic

---
## Error #61 — f-string Backslash SyntaxError in hydra_bridge.py
**Symptom:** Attempted to use `{'\n'.
**Fix Solution:**
Reverted to original `chr(10).join(stage_history)` pattern which was already correct. The attempt to "improve" it violated documented anti-pattern.
**Prevention:**
Never use backslashes inside f-string `{...}` expressions. Pre-extract computed values before the f-string. Read MEMORIES.md anti-pattern #3 before editing any f-strings.

---
## Error #62 — Generator-vs-List Bug in TARBABY discover_python_files()
**Symptom:** Introduced `yield from _safe_walk(search_path)` into the function body.
**Fix Solution:**
Removed `yield from` entirely. Made `_safe_walk` a plain recursive function using side-effect `append()` with no yielding. Changed `yield from _safe_walk(search_path)` to `_safe_walk(search_path)`. Removed dead `# Drain generator` / `list(_ for _ in ())` code.
**Prevention:**
Do not introduce `yield`/`yield from` into functions that callers expect to return concrete types. Verify caller expectations (list slicing, len(), iteration patterns) before converting to generator.

---
## Error #68 — 3.14t Lazy-Load Deadlock in PamsRecorder._ensure_local_store()
**Symptom:** `_ensure_local_store()` used double-checked locking with lazy import of LocalMemoryStore inside the lock-release window.
**Fix Solution:**
Moved `from CORE.local_memory import LocalMemoryStore` to module level with `LOCAL_MEMORY_OK` flag. `_ensure_local_store()` now only instantiates, no longer imports. Eliminates deadlock window entirely.
**Prevention:**
Never use lazy imports inside critical sections under 3.14t. All CORE imports should be at module level or in `__init__`.

---
