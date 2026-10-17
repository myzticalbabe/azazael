---
name: azazael-toolkit
description: AZAZAEL_TOOLKIT — core framework, QL analysis, environment manager, comprehensive fix tools. 7 .py files for cross-cutting system operations.
metadata:
  category: system
  project: azazael
  priority: standard
  auto_load: true
---

# Azazael TOOLKIT — Core Framework Tools

> **Implementation:** `src/AZAZAEL_TOOLKIT/`
> **7 .py files**

---

## Overview

The AZAZAEL_TOOLKIT provides core framework utilities for system-wide operations
including environment management, QL analysis, documentation path updates, and
comprehensive fixes.

---

## Components

| File | Purpose |
|------|---------|
| `azazael_toolkit.py` | Core toolkit framework |
| `environment_manager.py` | System environment configuration |
| `QL_ANALYSIS.py` | QL (Quality/Learning) analysis |
| `math_certainty.py` | Mathematical certainty calculations |
| `COMPREHENSIVE_FIX.py` | Multi-issue comprehensive fix tool |
| `update_docs_paths.py` | Documentation path updates |
| `REAL_FRAMEWORK_TEST.py` | Framework integration tests |

### Import Pattern
```python
import sys; sys.path.insert(0, 'src')
from AZAZAEL_TOOLKIT.azazael_toolkit import AzazaelToolkit
from AZAZAEL_TOOLKIT.environment_manager import EnvironmentManager
```

## Related Skills

- `azazael-orchestration` — Parent orchestration system
- `azazael-utilities` — UTILITIES sub-systems
- `azazael-testing` — Testing conventions and validation
