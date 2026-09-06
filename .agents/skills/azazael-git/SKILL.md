---
name: azazael-git
description: Azazael git conventions — commit messages, branching strategy, pre-commit checks, CI-ready workflow. Load before committing or branching.
metadata:
  category: conventions
  project: azazael
  auto_load: true
---
# Azazael Git Conventions

## Commit Message Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
| Type | When to Use |
|------|------------|
| `feat` | New worm, new feature, new capability |
| `fix` | Bug fix, error correction |
| `refactor` | Code restructuring without behavior change |
| `perf` | Performance improvement (3.14t, parallel, etc.) |
| `docs` | Documentation or skill files only |
| `test` | Adding or updating tests |
| `chore` | Maintenance, cleanup, tooling |
| `style` | Formatting, linting (no code change) |

### Scopes
| Scope | Covers |
|-------|--------|
| `worms` | Individual worm files |
| `clusters` | CLUSTERWORMS, NATURE_CLUSTERS, METACLUSTER |
| `registry` | worm_registry.py, @register_worm |
| `codex` | CODEX video generation, PAMS, MemoryBus |
| `hydra` | HYDRA/ subsystem |
| `skills` | .agents/skills/ files |
| `docs` | AZAZAEL_INSIGHTS.md, PRODUCTION_TODO.md, etc. |
| `core` | CORE/ infrastructure |
| `build` | Package management, dependencies |

### Examples
```
feat(worms): add FirewallAudit worm with Windows firewall analysis
fix(clusters): replace Unicode checkmark chars with ASCII in Mermaid output
perf(clusters): migrate execute_all to FreeThreadPool for 3.14t
docs(skills): add azazael-worms-data skill for learning/ml/viz worms
refactor(registry): remove unused Set/Tuple imports from TRIMZ.py
chore(skills): create 10-skill system for assistant knowledge transfer
```

## Branching Strategy

```
main ──────────────────────────────────────────────
  │
  ├── feat/worm-<name>         (new worm development)
  ├── fix/<issue-description>  (bug fixes)
  ├── perf/3.14t-<target>      (3.14t optimizations)
  ├── docs/<what>               (documentation updates)
  └── refactor/<what>           (code restructuring)
```

**Rule:** Never commit directly to `main` for changes spanning >1 file. Create a branch.

## Pre-Commit Checklist

Run BEFORE every commit:

1. **Syntax check all .py files:**
```bash
# Write to _syntax_check.py, execute, then remove
python -c "
import ast, os
ok = fail = 0
for r, ds, fs in os.walk('azazael/src'):
    for f in fs:
        if f.endswith('.py'):
            try:
                with open(os.path.join(r,f), encoding='utf-8') as ff:
                    ast.parse(ff.read())
                ok += 1
            except SyntaxError as e:
                print(f'SYNTAX ERROR: {os.path.join(r,f)}: {e}')
                fail += 1
print(f'OK={ok} FAIL={fail}')
"
```

2. **Unicode audit (Windows safety):**
```bash
# Write to _unicode_check.py, execute, then remove
python -c "
import os
for r, ds, fs in os.walk('azazael/src'):
    for f in fs:
        if f.endswith('.py'):
            fp = os.path.join(r,f)
            content = open(fp, encoding='utf-8').read()
            for ch in ['\u2713', '\u2717', '\U0001F537']:
                if ch in content:
                    print(f'UNICODE: {fp} contains {repr(ch)}')
"
```

3. **Registry integration test:**
```bash
# Write to _reg_test.py, execute, then remove
python -c "
import sys; sys.path.insert(0, 'azazael/src')
from CORE.worm_registry import discover_worms, WORM_REGISTRY
discover_worms()
print(f'Registry OK: {len(WORM_REGISTRY)} worms')
"
```

4. **Verify no temp files:**
```bash
# Write to _temp_check.py, execute, then remove
python -c "
import os
temps = [f for f in os.listdir('.') if f.startswith('_test') or f.startswith('_tmp')]
for t in temps:
    print(f'TEMP FILE: {t} — remove before commit')
print('Clean' if not temps else 'HAS TEMP FILES')
"
```

## Commit Frequency

- **Small, atomic commits** — one logical change per commit
- **Commit after each error fix** — per SYSTEM_INSTRUCTIONS.md SOP
- **Commit before switching tasks** — avoid mixed-concern commits
- **Squash before merge** — keep main history clean

## What NOT to Commit

| ❌ Never Commit | Why |
|----------------|-----|
| `_test_*.py` files | Temp test scripts |
| `_tmp_*.py` files | Temp work files |
| `*.pyc` files | Compiled bytecode |
| `__pycache__/` | Python cache |
| `G:/` path references | Machine-specific paths |
| API keys or secrets | Security risk |
| Large binaries | Bloats repo |

## Related Skills
- `azazael-sop` — Error recording SOP, pre-commit checklist
- `azazael-testing` — Full validation commands
- `azazael-conventions` — Python coding patterns
