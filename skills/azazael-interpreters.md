---
name: azazael-interpreters
description: INTERPRETERS — Go and Rust language runners for executing non-Python code within the Azazael ecosystem. 3 .py files.
metadata:
  category: process
  project: azazael
  priority: standard
  auto_load: true
---

# Azazael INTERPRETERS — Go & Rust Runners

> **Implementation:** `azazael/src/INTERPRETERS/`
> **3 .py files**

---

## Overview

The INTERPRETERS system provides language-specific runners to execute Go and Rust
code within the Azazael ecosystem, enabling cross-language analysis and automation.

---

## Components

| File | Purpose |
|------|---------|
| `go_runner.py` | Go language execution runner — compiles and runs Go code |
| `rust_runner.py` | Rust language execution runner — compiles and runs Rust code |

### Import Pattern
```python
import sys; sys.path.insert(0, 'azazael/src')
from INTERPRETERS.go_runner import GoRunner
from INTERPRETERS.rust_runner import RustRunner
```

## When to Use

| Language | Runner | Use Case |
|----------|--------|----------|
| **Go** | `GoRunner` | Running Go analysis tools, Go-based ML infrastructure |
| **Rust** | `RustRunner` | Running Rust tools, performance-critical analysis |

## Related Skills

- `azazael-orchestration` — Parent orchestration system
- `azazael-toolkit` — Core framework tools
- `azazael-testing` — Testing conventions
