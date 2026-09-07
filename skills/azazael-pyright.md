---
name: azazael-pyright
description: Pyright static type checking for the Azazael codebase — complements mypy on optionals, unbound variables, attribute access.
metadata:
  category: quality
  project: azazael
  priority: high
  auto_load: false
---

# azazael-pyright
**Category:** Quality / Type Checking
**Priority:** HIGH
**Dependencies:** pyright>=1.1.410 (via npx), Node.js
**Created:** June 14, 2026

## Purpose
Documents Pyright static type checking usage for the Azazael codebase. Pyright complements mypy by catching additional categories of type errors, particularly around optional values, unbound variables, and attribute access patterns that mypy may miss.

## When To Load
- When running comprehensive type audits
- When fixing Optional/None-related type errors
- When validating import chains and attribute access
- When cross-validating mypy findings with a second type checker
- When debugging `reportPossiblyUnboundVariable` or `reportOptionalMemberAccess` errors

## Configuration

### pyrightconfig.json (created June 14, 2026)
```json
{
    "include": ["src"],
    "exclude": [
        "**/__pycache__",
        "**/node_modules",
        "**/.git",
        "**/build",
        "**/dist",
        "**/ARCHIVE",
        "**/ARTIFACTS",
        "**/OUTPUT",
        "**/OLD_PROJECT",
        "**/CAPABILITIES",
        "**/SESSION_TEMPLATE",
        "**/CODEX_Studio_Output"
    ],
    "pythonVersion": "3.14",
    "typeCheckingMode": "basic",
    "reportMissingImports": false,
    "reportMissingTypeStubs": false,
    "reportOptionalMemberAccess": "warning",
    "reportOptionalCall": "warning",
    "reportOptionalIterable": "warning",
    "reportOptionalSubscript": "warning",
    "reportOptionalOperand": "warning",
    "reportUntypedFunctionDecorator": false,
    "reportUnknownArgumentType": false,
    "reportUnknownVariableType": false,
    "reportUnknownMemberType": false,
    "reportUnknownParameterType": false,
    "reportUnnecessaryTypeIgnoreComment": false,
    "reportPrivateUsage": false
}
```

**Key settings explained:**
- `typeCheckingMode: "basic"` — Balanced strictness (not "strict", not "off")
- `reportMissingImports: false` — Azazael uses many packages without stubs (tkinter, PIL, mygrad, psutil)
- `reportOptionalMemberAccess: "warning"` — Flag None-related bugs without blocking
- `reportUnknown*: false` — Avoid noise from dynamically-typed legacy code
- `exclude` — Skip build artifacts, archives, templates, and output directories

### Canonical Audit Command
```bash
cd azazael && npx --yes pyright --pythonversion 3.14
```

### JSON Output for Analysis
```bash
cd azazael && npx --yes pyright --pythonversion 3.14 --outputjson > pyright_report.json
```

## Common Error Categories (June 14, 2026 Audit)

| Error Code | Count | Typical Cause | Fix Strategy |
|-----------|-------|---------------|-------------|
| `reportPossiblyUnboundVariable` | 370 | `try/except ImportError` for optional deps | Add `else: var = None` or guard with `if 'var' in dir()` |
| `reportArgumentType` | 309 | Wrong type passed to function | Fix call site or add overload |
| `reportCallIssue` | 296 | Call signature mismatch | Fix arguments or function signature |
| `reportAttributeAccessIssue` | 198 | Accessing nonexistent attribute | Fix attribute name or add to class |
| `reportUndefinedVariable` | 172 | Variable never defined | Add import or define variable |
| `reportOptionalMemberAccess` | 91 | Accessing `.attr` on `Optional[T]` | Add `is not None` guard |
| `reportAssignmentType` | 90 | Type mismatch in assignment | Fix type or add cast |
| `reportReturnType` | 45 | Return type doesn't match annotation | Fix return value or annotation |

## Python 3.14t Free-Threading Considerations

Pyright does not model free-threading semantics. When type-checking concurrent code:
- `ThreadPoolExecutor` callbacks may have signature mismatches under free-threading
- Use `# pyright: ignore[reportArgumentType]` for free-threaded patterns
- Prefer explicit type annotations on thread-shared variables

## Quick Diagnostics

### Count errors by category
```bash
cd azazael && npx --yes pyright --outputjson 2>&1 | \
    python -c "import sys,json; d=json.load(sys.stdin); \
    cats={}; [cats.update({x.get('rule','?'): cats.get(x.get('rule','?'),0)+1}) for x in d.get('generalDiagnostics',[])]; \
    [print(f'{c:5d} {r}') for r,c in sorted(cats.items(), key=lambda x:-x[1])[:20]]"
```

### Check a single file
```bash
cd azazael && npx --yes pyright src/PATH/TO/file.py --pythonversion 3.14
```

### Compare mypy vs pyright findings
```bash
# Get mypy file list
python -m mypy src/ --ignore-missing-imports --explicit-package-bases 2>&1 | grep "\.py:" | cut -d: -f1 | sort -u > /tmp/mypy_files.txt

# Get pyright file list
npx pyright --outputjson 2>&1 | python -c "import sys,json; d=json.load(sys.stdin); \
    [print(x['file']) for x in d.get('generalDiagnostics',[])]" | sort -u > /tmp/pyright_files.txt

# Files with errors in BOTH
comm -12 /tmp/mypy_files.txt /tmp/pyright_files.txt
```

## Fixing Common Patterns

### Possibly Unbound Variable (from try/except ImportError)
```python
# BEFORE — pyright flags tk as possibly unbound
try:
    import tkinter as tk
except ImportError:
    pass  # GUI not available

# AFTER — explicit None default
try:
    import tkinter as tk
except ImportError:
    tk = None

# Usage
if tk is not None:
    root = tk.Tk()
```

### Optional Member Access
```python
# BEFORE — pyright flags .grad access on Optional
p.grad *= 0.9

# AFTER — guard with is not None
if p.grad is not None:
    p.grad[:] *= 0.9
```

## Reference
- Pyright documentation: https://microsoft.github.io/pyright/
- Azazael pyrightconfig.json (created June 14, 2026)
- Python 3.14t typing considerations: PEP 703
