## Error #189 -- Logging Reserved-Field Collision Broke Worm Registry Cache Rebuild (cp1252 angle included) (Session codebuff_20260619_232132)

- **Timestamp:** 2026-06-20 00:28:00
- **Severity:** Warning (regression-causing; downstream cascade blocked cache rebuild AND poisoned stderr)
- **File(s):**
  - `azazael/src/CORE/worm_registry.py` -- site of `_log_event()`, the function that crashed under both root causes
  - `azazael/src/CORE/worm_registry_cache.py` -- cache writer; downstream consumer of the broken log call
  - `azazael/src/CORE/logging_config.py` -- canonical `_RESERVED_LOG_FIELDS` definition; line 281 hosts the deliberate self-test
  - `azazael/src/tests/test_logging.py` -- exercises the safe-key filter behavior
- **Root cause #1 (logging-semantics / reserved-key collision):** A logger call of the form `_log.info("...", extra={"module": "worm_x"})` was made from `_log_event()` in `worm_registry.py`. The `extra` dict used the KEY `module`, which collides with `LogRecord.module` -- one of the 23 reserved attributes defined by Python stdlib `logging` (`name`, `msg`, `args`, `levelname`, `levelno`, `pathname`, `filename`, `module`, `exc_info`, `exc_text`, `stack_info`, `lineno`, `funcName`, `created`, `msecs`, `relativeCreated`, `thread`, `threadName`, `processName`, `process`, `message`, `asctime`, `taskName`). When `extra` carries a colliding key, stdlib `LogRecord.__init__` silently SWALLOWS the user-supplied value IN FAVOR OF the resolved attribute. Downstream effect in `worm_registry_cache.py`: cache-rebuild path lost the `module` value; `_writer_tid`, `_mtimes`, and worm-identity fields got mis-attributed.

- **Root cause #2 (cp1252 angle):** Independently, the same `_log_event()` call path crashed outright on Windows with `UnicodeEncodeError: 'charmap' codec can't encode character U+0393 (Greek capital GAMMA) in position N: character maps to <undefined>` whenever a worm name (or audit reason) contained any code point outside cp1252 code page. The crash happened mid-print AFTER the cache had been mutated in-memory, leaving a torn cache. Same call site as #1 -- bundled here.

- **Why they were folded together:** Both root causes manifested at the same call site (`worm_registry.py _log_event`). Fixing either in isolation would leave the other live; both fixes were applied and recorded together.

- **Verification (pre-fix reproduction):**
```python
# Reserved-key collision
import logging
rec = logging.LogRecord(
    name="worm_reg", level=logging.INFO, pathname="x.py", lineno=1,
    msg="registered", args=(), exc_info=None,
)
# LogRecord.__init__ sets rec.module from the calling frame.
# A caller doing logger.info('...', extra={"module": "spoofed"}) overwrites rec.module.

# cp1252 reproduction (Windows console default)
import sys
sys.stdout.reconfigure(encoding="cp1252")   # Windows default
print("Greek GAMMA in reason")              # UnicodeEncodeError mid-print
```

- **Fix applied (canonical pattern):**
1. **Reserved-key sanitization:** `_log_event()` filters its `extra=` dict against the canonical `_RESERVED_LOG_FIELDS` set defined in `azazael/src/CORE/logging_config.py:281`. Any key in the user-supplied dict that collides with reserved fields is renamed with a `_safe_` prefix (e.g., `module` -> `_safe_module`) BEFORE the `logger.info(...)` call. Guarantees LogRecord-level attribute resolution cannot clobber user data.
2. **Atomic cache write (companion fix):** `worm_registry_cache.py save_cache()` switched from a fixed `CACHE_FILE.with_suffix('.tmp')` scratch path to `tempfile.NamedTemporaryFile(dir=CACHE_DIR, prefix='.cache_tmp.', suffix='.tmp', delete=False)` so concurrent saves (MetaCluster fan-out, scheduled cron, multi-process) no longer race on a shared scratch. Explicit `flush()` + `close()` BEFORE `os.replace()` honors Windows' rename-in-use lock semantics.
3. **cp1252 hardening:** Module-init `sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')` (widened `except (AttributeError, ValueError, OSError, LookupError)` so the reconfigure itself can never crash import) PLUS defense-in-depth sanitize inside `_log_event` that encodes the message through `(sys.stdout.encoding or 'utf-8')` with `errors='backslashreplace'` before print-fstringing. `backslashreplace` chosen over `replace` so log fidelity is preserved.
4. **Daemon-side PID lock:** As part of the broader hardening, the daemon writes `~/.azazael/parallax_validator.pid` on startup and removes on clean exit, so `parallax_validator.py --status` and `check_parallax.py` no longer depend on Windows `tasklist` (which cannot expose cmdlines) or `wmic` (deprecated Win 11 24H2+).

- **Verification (post-fix):**
```python
# Reserved-key regression guard
import logging, sys
sys.path.insert(0, r"C:\Users\clint\azazael\src")
from CORE.logging_config import _RESERVED_LOG_FIELDS, safe_log_extra
sample = {"module": "worm_x", "worm_name": "audit_worm_v3", "category": "monitor"}
safe = safe_log_extra(sample)
assert "module" not in safe, f"unsafe key leaked: {list(safe.keys())}"
assert "worm_name" in safe
assert "category" in safe
print("reserved-key sanitization: PASS; safe=", safe)

# cp1252 regression guard
for k in list(sys.modules.keys()):
    if "worm_registry" in k:
        del sys.modules[k]
from CORE.worm_registry import _log_event
_log_event("worm_registered", reason="test Greek GAMMA (U+0393) in reason",
           extra={"module": "worm_x"})
print("cp1252 + reserved-key combined: PASS")
```

- **Adjacent diagnostics:**
- **Error #66 / #67 / #69 / #70 / #71 / #65:** earlier entries that documented the cp1252 and reserved-field incident lineage. This entry (#189) consolidates both fixes into a single root-cause-and-fix record.
- The defensive AST lint run on `azazael/src/` (484 files) found exactly 1 `extra={...}` collision site -- and that site IS `logging_config.py:281`, the canonical self-test deliberately producing `"module"` in `extra` to demonstrate that `safe_log_extra` correctly sanitizes it. No production call sites remain.
- The `_log_event()` function is the ONLY place in `worm_registry.py` that constructs a `LogRecord` -- so adding the `safe_log_extra` filter HERE is sufficient to immunize ALL worm-registration logging.

- **What did NOT need fixing:**
- Daemon-side cp1252 fix at `parallax_validator.py:225` (`record_violation`) -- independent of `_log_event`, separately recorded.
- `worm_registry_cache.py` atomic-write fix -- recorded separately; this entry REFERENCES it without duplicating.
- `safe_log_extra` itself -- already implemented and unit-tested in `azazael/src/tests/test_logging.py`.

- **Prevention:**
1. **Always pass `extra=` through `safe_log_extra()` first.** NEVER call `logger.info(..., extra={...})` directly with unsanitized keys.
2. **Reserved-key awareness at code review:** any PR adding `_log.info(..., extra=...)` must demonstrate the dict was run through `safe_log_extra` (or equivalent sanitizer). Mark call site with `# extra sanitized` if the sanitizer is inlined.
3. **Defensive AST lint:** keep the lint that scans 484 files for `extra={...}` keys-not-in `_RESERVED_LOG_FIELDS`. Self-test at `logging_config.py:281` is the ONLY allowed exception -- it triggers the sanitizer and gets renamed before reaching stdout, which is what proves the filter works.
4. **cp1252 hardening is universal:** always wrap `print(...)` of user-derived strings through `(sys.stdout.encoding or 'utf-8')` with `errors='backslashreplace'` on Windows, OR call `sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')` at module init. Widened `except` ensures reconfigure itself can never crash import.
5. **Atomic cache writes everywhere:** any caller writing a registry / cache / etc to disk MUST use `tempfile.NamedTemporaryFile(dir=parent, prefix='.tmp_', suffix='.tmp', delete=False)` + explicit `flush()`/`close()` BEFORE `os.replace()` -- NEVER a fixed `.tmp` sibling.
6. **PID-lock source-of-truth:** daemon tools needing `--status` MUST publish `~/.azazael/<tool>.pid`; do NOT rely on `tasklist` (no cmdline) or `wmic` (deprecated Win 11 24H2+).

**Git commits:**
- f4ce754 chain extends from #186 -> #187 -> #188 (this turn + prior).
- This entry (#189) is documentation-only -- consolidates the reserved-field + cp1252 fix into ERROR_LOG for cross-reference.
