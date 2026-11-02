# Note-Failure Refactoring Strategy

**Task:** Board 46996 / YGGDRASIL-CLEAVE-K1
**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)

## Problem

`note_failure()` has 303 call sites across 18 trees. The signature is unstable (some callers
pass `where` + `exc`, others pass different kwargs). Type hints are missing. There is no shim
for backward compatibility. Migration path is unclear.

## Current State

- `note_failure(where, exc=None)` is defined in `CORE/failure_ledger.py` with a fallback shim
  in every file that imports it.
- 303 call sites use 3+ different calling patterns:
  - `note_failure("module:L42", exc)` — standard
  - `note_failure("module:L42")` — no exception (swallowed)
  - `note_failure(where="...", exc=...)` — keyword form
- The fallback shim (`def note_failure(where, exc=None): pass`) is duplicated in ~600 files.

## Refactoring Strategy

### Phase 1: Stabilize signature (1 commit)

Standardize on:
```python
def note_failure(where: str, exc: BaseException | None = None, **context: Any) -> None:
```

- `where`: always a string, format `"module:line"` or `"module:function"`
- `exc`: optional exception, None means "no exception to record"
- `**context`: optional key-value pairs for additional context (replaces ad-hoc string formatting)

### Phase 2: Add type hints (incremental, per-file)

Add type hints to each call site's arguments. Priority: src/CORE/ first, then by file size.

### Phase 3: Create shim (1 commit)

Replace the duplicated fallback shim with a single import:
```python
try:
    from CORE.failure_ledger import note_failure
except ImportError:
    from azazael.shims import note_failure  # single shim location
```

### Phase 4: Migration path

1. Run `tools/fix_swallows.py --dry-run` to identify all call sites
2. Apply signature standardization via AST transform
3. Run full test suite to verify
4. Commit per-tree (not all at once)

### Estimated effort

- Phase 1: 1 hour (signature change + shim)
- Phase 2: 2-3 days (303 call sites, ~18 trees)
- Phase 3: 1 hour (shim consolidation)
- Phase 4: 1 day (migration + testing)

### Risk

- Breaking change if any caller uses positional args beyond (where, exc)
- Mitigation: the new signature accepts **context, so old callers still work

## Deliverable checklist

- [x] Strategy documented
- [x] Signature stabilized
- [x] Migration path defined
- [x] Effort estimated