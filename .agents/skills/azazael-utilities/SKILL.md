---
name: azazael-utilities
description: UTILITIES sub-systems catalog — KLINK, PERSEPHONE (environment/sync), POINDEXTER (indexing), TARBABY (file search), TERENCE. Quick reference for all utility tools.
metadata:
  category: process
  project: azazael
  priority: high
  auto_load: true
---

# Azazael UTILITIES — Sub-System Catalog

> **Implementation:** `azazael/src/UTILITIES/`
> **5 sub-systems:** KLINK, PERSEPHONE, POINDEXTER, TARBABY, TERENCE (~20 files)

---

## Overview

The UTILITIES directory contains specialized sub-systems for environment management,
indexing, file operations, and analysis tools.

---

## KLINK (2 .py files)

| File | Purpose |
|------|---------|
| `klink.py` | KLINK system — cross-environment linking |

**Location:** `azazael/src/UTILITIES/KLINK/`

---

## PERSEPHONE (9+ .py files)

Persephone is an environment management system with CLI interface.

### Core

| File | Purpose |
|------|---------|
| `persephone.py` | Main Persephone module |
| `version.py` | Version tracking |

### CLI & Setup

| File | Purpose |
|------|---------|
| `persephone_cli.py` | Command-line interface |
| `setup_wizard.py` | Interactive setup wizard |

### Library (lib/)

| File | Purpose |
|------|---------|
| `environment.py` | Environment configuration |
| `path_manager.py` | Path resolution management |
| `sync_manager.py` | Environment synchronization |

**Location:** `azazael/src/UTILITIES/PERSEPHONE/`

### Quick Start
```python
import sys; sys.path.insert(0, 'azazael/src')
from UTILITIES.PERSEPHONE.lib.environment import Environment
from UTILITIES.PERSEPHONE.lib.path_manager import PathManager
from UTILITIES.PERSEPHONE.lib.sync_manager import SyncManager
```

---

## POINDEXTER (2 .py files)

| File | Purpose |
|------|---------|
| `POINDEXTER.py` | Indexing tool — codebase indexing and search |

**Location:** `azazael/src/UTILITIES/POINDEXTER/`

---

## TARBABY (3 .py files)

| File | Purpose |
|------|---------|
| `TARBABY.py` | File searching and binary compilation |
| `tarbaby_enhanced.py` | Enhanced TARBABY capabilities |

**Location:** `azazael/src/UTILITIES/TARBABY/`

---

## TERENCE (3 .py files)

| File | Purpose |
|------|---------|
| `TERENCE.py` | Analysis tool |
| `terence_enhanced.py` | Enhanced TERENCE capabilities |

**Location:** `azazael/src/UTILITIES/TERENCE/`

---

## Related Skills

- `azazael-orchestration` — Parent orchestration system (TARBABY also in ORCHESTRATION)
- `azazael-sync-patterns` — Environment sync infrastructure
- `azazael-environment` — Environment setup and configuration
