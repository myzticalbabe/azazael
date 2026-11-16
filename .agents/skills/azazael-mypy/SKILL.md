# azazael-mypy
**Category:** Quality / Type Checking
**Priority:** HIGH
**Dependencies:** mypy>=2.1.0, Python 3.16t (`C:/Azazael/.venvs/py316t`); the 3.14t venv was retired 2026-10-19
**Created:** June 14, 2026
**Reoriented:** 2026-09-22 — SECOND OPINION ONLY; the gate is basedpyright (`azazael-pyright`, `tools/type_check_gate.py`)
> **This skill is no longer the type-checking gate.**
>
> `tools/type_check_gate.py` runs **basedpyright 1.40.1** (installed in the
> production 3.16t venv `C:/Azazael/.venvs/py316t`, already configured by the committed `pyrightconfig.json`) and
> compares against a committed baseline. Measured 2026-09-22, same tree:
> | tool | files | findings | wall |
> |---|---|---|---|
> | basedpyright | 690 | 1,191 errors + 252 warnings | **64 s** |
> | mypy (`src/CORE/`, `--check-untyped-defs`) | 329 | 655 errors | ~6 min |
> Two reasons mypy stopped being the gate, both measured:
> 1. **It could not read the tree.** `mypy src/CORE/` aborted with a `ValueError:
>    path is on mount` naming the Windows null device, because two literal files
>    named `nul` sat at the repo root and in `src/CORE/WORMS/` — residue of a
>    cmd.exe redirect run inside Git Bash, untracked and unmatchable by any git
>    pathspec. Both were removed 2026-09-22 (`ERROR_LOG.md` #193); mypy then
>    reported 655 errors immediately.
> 2. **It answers a narrower question.** The findings only basedpyright reports
>    are the ones this codebase has: `reportUndefinedVariable` 94,
>    `reportOptionalMemberAccess` 120, `reportPossiblyUnboundVariable` 17.
> mypy is still installed and the patterns in this skill remain valid for it.
> Use it for a second opinion on one file:
> ```bash
> python -m mypy src/CORE/path/file.py --ignore-missing-imports --check-untyped-defs
> ```
> See `docs/ARCHITECTURE_DECISION_RECORDS.md` ADR-011.
## Purpose
Documents mypy static type checking usage for the Azazael codebase. Covers configuration, common error patterns, free-threading considerations, and the canonical command for type-checking the project.
## When To Load
- When running type audits on the codebase
- When fixing type errors
- When adding type annotations to new code
- When validating changes before commit
- When diagnosing `[name-defined]` or `[attr-defined]` errors
## Configuration
### pyproject.toml (existing)
```toml
[tool.mypy]
exclude = [
"src/azazael_toolkit.py",
"src/COMPREHENSIVE_FIX.py",
"src/environment_manager.py",
"src/math_certainty.py",
"src/QL_ANALYSIS.py",
"src/REAL_FRAMEWORK_TEST.py",
"src/update_docs_paths.py",
]
```
### Canonical Audit Command
```bash
cd azazael && python -m mypy src/ \
--ignore-missing-imports \
--explicit-package-bases \
--show-error-codes
**Flags explained:**
- `--ignore-missing-imports`: Skip third-party packages that lack stubs (tkinter, PIL, psutil, mygrad, etc.)
- `--explicit-package-bases`: Resolve module naming conflicts when `__init__.py` files are present in some but not all directories
- `--show-error-codes`: Display the mypy error code for each issue (e.g., `[name-defined]`, `[attr-defined]`)
## Common Error Categories (June 14, 2026 Audit)
| Error Code | Count | Typical Cause | Fix Strategy |
|-----------|-------|---------------|-------------|
| `[name-defined]` | 306 | Undefined variable/class names | Add imports or fix typos |
| `[annotation-unchecked]` | 265 | Missing stubs or unchecked types | Add type annotations or `# type: ignore` |
| `[assignment]` | 214 | Incompatible type assignment | Fix type variance or add cast |
| `[call-arg]` | 179 | Wrong number/types of arguments | Fix call signature |
| `[attr-defined]` | 174 | Accessing undefined attributes | Add attribute or fix typo |
| `[misc]` | 138 | Various (module naming, etc.) | Case-by-case |
| `[index]` | 109 | Indexing with wrong type | Fix index expression |
| `[var-annotated]` | 90 | Variable annotation issues | Add missing annotation |
| `[arg-type]` | 78 | Argument type mismatch | Fix or cast argument |
## Python 3.14t Free-Threading Considerations
mypy does not currently model free-threading semantics. When type-checking code that uses `threading` or `concurrent.futures`:
- Callback signatures may not match due to GIL-removal patterns
- Use `# type: ignore[call-arg]` for free-threaded callback mismatches
- Prefer explicit `Callable[[...], ...]` annotations for thread targets
## Quick Diagnostics
### Count errors by file
cd azazael && python -m mypy src/ --ignore-missing-imports --explicit-package-bases 2>&1 | \
grep "\.py:" | cut -d: -f1 | sort | uniq -c | sort -rn | head -20
### Check a single file
cd azazael && python -m mypy src/PATH/TO/file.py --ignore-missing-imports --explicit-package-bases
### Find files with __init__.py gaps
find src -type d | while read d; do
if ls "$d"/*.py 2>/dev/null | grep -qv __init__; then
[ ! -f "$d/__init__.py" ] && echo "Missing: $d"
fi
done
## Fixing the Module Naming Conflict
The `[misc]` error "Source file found twice under different module names" occurs when mypy can't determine the canonical module path. Fix:
1. Add `__init__.py` to the parent directory, OR
2. Use `--explicit-package-bases` flag (preferred for Azazael)
## Reference
- mypy documentation: https://mypy.readthedocs.io/
- Azazael pyproject.toml `[tool.mypy]` section
- Python 3.14t typing considerations: PEP 703
**Dependencies:** mypy>=2.1.0, Python 3.14t
> `tools/type_check_gate.py` runs **basedpyright 1.40.1** (already installed in
> `venv-314t`, already configured by the committed `pyrightconfig.json`) and
**Dependencies:** mypy>=2.1.0, Python 3.15t (`C:/Azazael/.venvs/py315t`); the 3.14t venv was retired 2026-10-19
> production 3.15t venv `C:/Azazael/.venvs/py315t`, already configured by the committed `pyrightconfig.json`) and
