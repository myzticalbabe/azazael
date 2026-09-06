---
name: azazael-autoflake
description: Free-threaded autoflake wrapper for Python 3.14t — batch unused import detection, removal, and reporting. Created June 2026.
metadata:
  category: tooling
  project: azazael
  version: 1.0.0
---
# Azazael Autoflake — Free-Threaded Import Cleanup (3.14t)

## Overview

`scripts/autoflake_314t.py` is a robust wrapper around `autoflake` (v2.3.3+) that
works reliably on Python 3.14t free-threading. It provides:

- Batch scanning of entire directories
- Dry-run (`--check`) and in-place fix (`--fix`) modes
- Recursive directory traversal
- Human-readable summary reports
- Graceful error handling per file (one bad file doesn't block the batch)

## Why This Exists

Autoflake v2.3.3 **does work** on Python 3.14t — it's a pure-Python tool that
doesn't use C extensions. However, earlier sessions incorrectly attributed
subprocess-level issues (nested quotes in basher commands, shell escaping)
to a 3.14t incompatibility. This wrapper eliminates those failure modes by:

1. Using direct `sys.executable` subprocess calls (no shell intermediates)
2. Normalizing Windows paths via `Path.resolve()`
3. Setting explicit timeouts per file (30s)
4. Capturing stdout/stderr separately for clean error reporting

## Usage

### Check for unused imports (dry-run):
```bash
# Single file
python scripts/autoflake_314t.py --check src/CORE/Agent.py

# Entire directory (recursive)
python scripts/autoflake_314t.py --check src/ --recursive

# Multiple paths
python scripts/autoflake_314t.py --check src/CORE/ src/META/
```

### Fix unused imports in-place:
```bash
python scripts/autoflake_314t.py --fix src/CORE/WORMS/
```

### Verbose output:
```bash
python scripts/autoflake_314t.py --check src/ --recursive --verbose
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files clean (or all successfully fixed) |
| 1 | Some files have unused imports (check mode only) |
| 2 | Errors occurred (autoflake crashed on some files) |

## Batch Workflow

For a full project-wide import hygiene pass:

```bash
# Step 1: Check everything
python scripts/autoflake_314t.py --check src/ --recursive > _autoflake_report.txt

# Step 2: Fix each directory
python scripts/autoflake_314t.py --fix src/CORE/
python scripts/autoflake_314t.py --fix src/META/
python scripts/autoflake_314t.py --fix src/CODEX/

# Step 3: Verify everything is clean
python scripts/autoflake_314t.py --check src/ --recursive --quiet
```

## Design

The wrapper runs autoflake as a subprocess for each file independently.
This provides:

- **Process isolation**: Each file is checked in its own Python process,
  preventing any single file's import errors from crashing the batch
- **Free-threading safe**: No shared state between subprocess calls
- **Predictable timeouts**: Each file has a 30s timeout
- **Graceful degradation**: Files that crash autoflake are reported as
  errors without halting the batch

## Known Limitations

- `--expand-star-import` is always enabled (safe for 3.14t)
- Files with syntax errors will be reported as errors (not issues)
- Very large files (>5000 lines) may need longer timeouts (edit `autoflake_314t.py` line 58)

## Integration

Update the pre-commit checklist to include:

```
- [ ] Unused imports cleaned: `python scripts/autoflake_314t.py --check src/ --recursive --quiet`
```

## Related Skills
- `azazael-error-prevention` — Anti-pattern #7: Unused imports accumulate
- `azazael-testing` — Pre-commit checklist, validation commands
- `azazael-conventions` — Import style rules
