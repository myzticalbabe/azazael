---
name: azazael-comprehensive-testing
description: End-to-end testing procedures for Azazael — compliance self-test, worm health check, mypy audit, import verification, and combined report generation
metadata:
  category: process
  project: azazael
  priority: medium
  auto_load: false
  version: 1.0.0
  created: 2026-06-14
---

# Comprehensive Testing Guide

## Quick Reference

Run ALL checks in sequence:
```bash
cd /c/Users/clint/azazael

# 1. Worm Health Check
python _worm_health_check.py

# 2. Compliance Self-Test
python -c "from CORE.compliance.orchestrator import self_test; self_test()"

# 3. State Machine Verification
python -c "
from CORE.compliance.orchestrator import ComplianceOrchestrator
co = ComplianceOrchestrator()
r = co.check_all(action='check', role='developer', context={'state': 'CODE_EDIT', 'can_edit': True})
print(f'sm_valid={r.rule_0x[\"components\"][\"state_machine\"][\"valid\"]}, score={r.score}')
"

# 4. Full WORMS Import Test
python -c "
import importlib, os
for f in sorted(os.listdir('src/CORE/WORMS')):
    if f.endswith('.py') and not f.startswith('_'):
        importlib.import_module('CORE.WORMS.' + f[:-3])
        print(f'OK: {f}')
"

# 5. mypy on Compliance
python -m mypy src/CORE/compliance/
```

## Expected Results

| Test | Expected | Notes |
|------|----------|-------|
| Worm Health Check | 98/98 FILE, IMPORT, INSTANTIATE | All worms must import |
| Compliance self_test | FAIL (0Y:dual_ledger) | 0Y:dual_ledger is by-design |
| State Machine | sm_valid=True, score=1.0 | IDLE -> GATE_ASSERT -> CODE_EDIT on init |
| WORMS Import | 45/45 OK | All modules via CORE.WORMS. prefix |
| mypy compliance | Errors in validating.py | Pre-existing type annotation gaps |

## Troubleshooting

- **Compliance crash**: Check state machine transitions (StateMachineError)
- **Worm import failure**: Check module path in WORM_REGISTRY
- **Health check timeout**: Some worms have heavy imports (CLUSTERWORMS)
