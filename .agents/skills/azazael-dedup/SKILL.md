---
name: azazael-dedup
description: Azazael deduplication procedures — find and eliminate duplicate files using MD5 hash comparison, established patterns for deprecation shims.
metadata:
  category: maintenance
  project: azazael
---

# Azazael Deduplication Skill

## Overview

This skill documents the procedures for finding and eliminating duplicate files in the Azazael codebase. As of May 29, 2026, **13 deprecation shims** have been created across 3 directories, eliminating ~3,500+ lines of duplicate code.

---

## Dedup Audit Procedure

### Step 1: Find All .py Files
```bash
find azazael/src -name "*.py" | sort > /tmp/all_py_files.txt
```

### Step 2: Compute MD5 Hashes
```python
import hashlib
from pathlib import Path

def md5(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()

hashes = {}
for line in Path('/tmp/all_py_files.txt').read_text().splitlines():
    h = md5(line)
    if h not in hashes:
        hashes[h] = []
    hashes[h].append(line)

duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
```

### Step 3: Compare Line Counts
For files with same hash: they're exact duplicates.
For files with same name but different hash: compare line counts and first 5 diffs.

```python
import difflib
for hash_val, files in duplicates.items():
    print(f"IDENTICAL: {files}")
    
# For same-named files with different hashes
def show_diffs(file1, file2, max_diffs=5):
    lines1 = Path(file1).read_text().splitlines()
    lines2 = Path(file2).read_text().splitlines()
    for i, (a, b) in enumerate(zip(lines1, lines2)):
        if a != b:
            print(f"  Line {i+1}: {a[:100]} -> {b[:100]}")
```

### Step 4: Determine Canonical Source
- If one version has `from CORE.paths import ...` → that's canonical (dynamic paths)
- If one version has hardcoded `C:/Users/clint/Desktop/...` → that's stale
- If both identical → either can be canonical, prefer root-level

### Step 5: Check Import References
```bash
rg "from <DIR>\.<MODULE>|import <DIR>\.<MODULE>" azazael/src/
```
If 0 results → safe to replace with deprecation shim.

---

## Dedup Results (Historical Record)

### Phase 1-2: META/ Directory (6 shims)
| File | Canonical | Type | Lines |
|------|----------|------|-------|
| META/TRIMZ.py | TRIMZ.py | Identical | ~200 |
| META/DOCKERZ.py | DOCKERZ.py | Identical | ~200 |
| META/HEALTHZ.py | HEALTHZ.py | Identical | ~200 |
| META/UVZ.py | UVZ.py | Identical | ~200 |
| META/OPTIMIZ.py | OPTIMIZ.py | Near-duplicate (missing @register_worm) | ~300 |
| META/METAWORMS_POPUP.py | METAWORMS_POPUP.py | Identical | ~200 |

### Phase 5: HYDRA/ml_platforms/ (3 shims)
| File | Canonical | Type | Lines |
|------|----------|------|-------|
| HYDRA/ml_platforms/config.py | ORCHESTRATION/ml_platforms/config.py | Identical | ~200 |
| HYDRA/ml_platforms/launcher.py | ORCHESTRATION/ml_platforms/launcher.py | Identical | ~50 |
| HYDRA/ml_platforms/__init__.py | ORCHESTRATION/ml_platforms | Fixed broken import | ~30 |

### Phase 6: CODEX/CORE/ (8 shims)
| File | Canonical | Type | Lines |
|------|----------|------|-------|
| CODEX/CORE/ANIMATION_PROTOCOLS.py | ANIMATION_PROTOCOLS.py | Identical | 313 |
| CODEX/CORE/CHANGELOG_GENERATOR.py | CHANGELOG_GENERATOR.py | Stale (hardcoded paths) | 144→149 |
| CODEX/CORE/ECOSYSTEM_HEALTH_CHECK.py | ECOSYSTEM_HEALTH_CHECK.py | Stale (hardcoded base_path) | 127→134 |
| CODEX/CORE/enrichment_display.py | enrichment_display.py | Near-duplicate (CSS typo) | 476 |
| CODEX/CORE/FILE_MANIFEST_GENERATOR.py | FILE_MANIFEST_GENERATOR.py | Stale (hardcoded paths) | 145→154 |
| CODEX/CORE/HORUS_INTEGRATION.py | HORUS_INTEGRATION.py | Stale (hardcoded+broken paths) | 202→206 |
| CODEX/CORE/matrix_animation.py | matrix_animation.py | Identical | 242 |
| CODEX/CORE/QL_FILE_OPTIMIZER.py | QL_FILE_OPTIMIZER.py | Identical | 537 |

---

## Remaining Known Duplicates (Not Yet Shimmed)

| Location | Pairs | Reason Left |
|----------|-------|-------------|
| AZAZAEL_TOOLKIT/ | 4 | Likely intentional packaging copies |
| CODEX/SESSION_TEMPLATE/ | 4 | Nested directory structure |
| ORCHESTRATION/HYDRA/ | 1 | harness.py cross-location |

---

## When NOT to Dedup

1. **Intentional packaging copies**: Files in standalone distribution directories
2. **Testing fixtures**: Test-specific copies with different configurations
3. **Documentation metadata paths**: Paths in docstrings/examples that describe, not execute
4. **Template directories**: Session templates meant to be copied

---

## Anti-Patterns

| ❌ Never | ✅ Always |
|----------|----------|
| Copy-paste files between directories | Use imports or deprecation shims |
| Leave duplicates as-is | At minimum, document them |
| Delete canonical before shim creation | Create shim first, verify, then archive canonical |
| Assume all duplicates are bad | Check if intentional (packaging, templates) |

---

## Related Skills
- `azazael-shims` — Deprecation shim pattern and testing
- `azazael-separation` — Project extraction playbooks
- `azazael-architecture` — Project structure and module organization
