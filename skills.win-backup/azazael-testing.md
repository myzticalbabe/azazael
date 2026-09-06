---
name: azazael-testing
description: Azazael testing conventions — syntax check, integration test, worm config trace, code review. Load when validating changes, running tests, or preparing to commit.
metadata:
  category: testing
  project: azazael
  auto_load: true
---
# Azazael Testing Conventions

## Quick Start — Run a Worm

Write to `_run_test.py`, then `python _run_test.py && rm _run_test.py`:
```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.worm_registry import discover_worms; discover_worms()
from CORE.WORMS.CLUSTERWORMS import ClusterWORMZ
cluster = ClusterWORMZ.build_from_nature("monitor")
results = cluster.execute_sequential()
print(f"{len(results)} worms executed")
```

## Quick Validation Commands

All commands below avoid nested quotes (per ERROR_LOG.md anti-pattern #1). Write Python scripts to temp files, then execute with `python _tmp.py`.

### Syntax Check (all 485 files)
Write to `_syntax_check.py`:
```python
import ast, os
ok = 0; fail = 0
for r, ds, fs in os.walk('azazael/src'):
    for f in fs:
        if f.endswith('.py'):
            fp = os.path.join(r, f)
            try:
                with open(fp, encoding='utf-8', errors='replace') as ff:
                    ast.parse(ff.read())
                ok += 1
            except SyntaxError as e:
                print('SYNTAX ERROR:', fp, str(e))
                fail += 1
print(f'Syntax OK: {ok}, FAIL: {fail}')
```
Then: `python _syntax_check.py && rm _syntax_check.py`

### Worm Registry Integration Test
Write to `_reg_test.py`:
```python
import sys, os
sys.path.insert(0, 'azazael/src')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from CORE.worm_registry import discover_worms, WORM_REGISTRY, get_all_categories
discover_worms()
cats = sorted(get_all_categories())
total = sum(len(WORM_REGISTRY.get(c,{})) for c in cats)
print(f'Registry: {len(WORM_REGISTRY)} worms, {len(cats)} categories')
```
Then: `python _reg_test.py && rm _reg_test.py`

### Worm Config Trace
Write to `_trace.py`:
```python
import sys, os, json
sys.path.insert(0, 'azazael/src')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from CORE.worm_registry import discover_worms, WORM_REGISTRY, get_all_categories
discover_worms()
cats = sorted(get_all_categories())
data = {'total': len(WORM_REGISTRY), 'categories': cats, 'worms': []}
for k, v in sorted(WORM_REGISTRY.items()):
    data['worms'].append({
        'name': k,
        'category': v.get('category', '?'),
        'priority': v.get('priority', '?'),
        'cooldown': v.get('cooldown_seconds', '?'),
        'version': v.get('version', '?'),
        'source': os.path.basename(v.get('source_file', '?'))
    })
json.dump(data, open('azazael/worm_config_trace.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(f'{len(data["worms"])} worms traced')
```
Then: `python _trace.py && rm _trace.py`

## Related Skills
- `azazael-sop` — Error recording SOP, pre-commit checklist
- `azazael-error-prevention` — 7 anti-patterns, DO-NOT-REPEAT list
- `azazael-git` — Commit conventions and git pre-commit hooks

## Pre-Commit Checklist (Canonical — Referenced by azazael-conventions)
- [ ] Syntax check passes (485 files)
- [ ] Worm registry integration test passes
- [ ] No Unicode emoji in any new code
- [ ] No nested quotes in basher commands (use temp Python files)
- [ ] No f-string backslash escapes
- [ ] All imports at top of files
- [ ] Temp files cleaned up
