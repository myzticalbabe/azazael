---
name: azazael-error-index
description: Master index mapping error symptoms to dedicated fix skill files. Load this first when troubleshooting.
metadata:
  category: fixes
  project: azazael
  auto_load: true
---

# 🗂️ Azazael Error Fix Index

*Load the relevant skill file using `skill()` or `read_files()` when you encounter one of these symptoms.*

## Skill Files

### `azazael-fix-python-314t.md` — Python 3.14t Free-Threading (8 errors)
**Symptoms include:** pytest 9.0.3 Segfaults on Python 3.14.5t Free-Thre / psutil C Extension Segfaults on Python 3.14.5t Fre
**Load:** `skill("azazael-fix-python-314t")` or `read_files(["azazael/skills/azazael-fix-python-314t.md"])`

### `azazael-fix-gitbash-paths.md` — Environment & Path Handling (7 errors)
**Symptoms include:** MSYS2 Path Translation Breaks WSL Commands from Gi / Python 3.14t Source Build on Ubuntu 26.04 (apt_pkg
**Load:** `skill("azazael-fix-gitbash-paths")` or `read_files(["azazael/skills/azazael-fix-gitbash-paths.md"])`

### `azazael-fix-data-recording.md` — Database & Session Recording (10 errors)
**Symptoms include:** CodebuffTracker/LocalMemoryStore Session Recording / PAMS Server DOWN Blocks All Memory Recording
**Load:** `skill("azazael-fix-data-recording")` or `read_files(["azazael/skills/azazael-fix-data-recording.md"])`

### `azazael-fix-file-operations.md` — File System & Data Safety (2 errors)
**Symptoms include:** G: Drive Robocopy Times Out on Large Transfers / shutil.copytree + shutil.rmtree Causes Silent Data
**Load:** `skill("azazael-fix-file-operations")` or `read_files(["azazael/skills/azazael-fix-file-operations.md"])`

### `azazael-fix-protocol-compliance.md` — Protocol & Compliance (7 errors)
**Symptoms include:** SOP Tightening Applied: Rule Priority Chain + Comp / Process Violation: Claimed "Complete" Without Runn
**Load:** `skill("azazael-fix-protocol-compliance")` or `read_files(["azazael/skills/azazael-fix-protocol-compliance.md"])`


## Quick Lookup
| Error # | Domain | Title (truncated) |
|---------|--------|-------------------|
| #16 | Python 3.14t Free-Threading | Nuitka 4.1.2 C-backend failures on Python 3.14t free-threading build |
| #48 | Python 3.14t Free-Threading | pytest 9.0.3 Segfaults on Python 3.14.5t Free-Threading |
| #49 | Python 3.14t Free-Threading | psutil C Extension Segfaults on Python 3.14.5t Free-Threading |
| #50 | Python 3.14t Free-Threading | psycopg2-binary cp314t Wheel Missing Bundled DLLs |
| #54 | Python 3.14t Free-Threading | pydantic-core / uuid-utils cp314t Wheel Segfault on Python 3.14.5t |
| #61 | Python 3.14t Free-Threading | f-string Backslash SyntaxError in hydra_bridge.py |
| #62 | Python 3.14t Free-Threading | Generator-vs-List Bug in TARBABY discover_python_files() |
| #68 | Python 3.14t Free-Threading | 3.14t Lazy-Load Deadlock in PamsRecorder._ensure_local_store() |
| #51 | Environment & Path Handling | MSYS2 Path Translation Breaks WSL Commands from Git Bash |
| #52 | Environment & Path Handling | Python 3.14t Source Build on Ubuntu 26.04 (apt_pkg + libdb) |
| #55 | Environment & Path Handling | False Diagnosis: "Autoflake Doesn't Work on 3.14t" — Actually a Shell- |
| #56 | Environment & Path Handling | PowerShell Cmdlet Escaping in Git Bash basher Commands |
| #59 | Environment & Path Handling | Windows Backslash Path Interpretation in Git Bash |
| #60 | Environment & Path Handling | Worm Registry Test Returns 0 Worms Due to Shell Escaping |
| #63 | Environment & Path Handling | Unicode Escape Crash in DirectMemory Basher Command |
| #57 | Database & Session Recording | CodebuffTracker/LocalMemoryStore Session Recording Times Out |
| #64 | Database & Session Recording | PAMS Server DOWN Blocks All Memory Recording |
| #65 | Database & Session Recording | Session Lifecycle: ended_at=NULL on Hard Kills |
| #66 | Database & Session Recording | Deprecated CodebuffTracker + SessionRecorder Still Importable |
| #67 | Database & Session Recording | Recording Path Fragmentation: 3 Different session_id Formats |
| #69 | Database & Session Recording | DELETE Journal Mode Causes "database is locked" on Concurrent Writes |
| #70 | Database & Session Recording | MemoryBus Ephemeral Data Loss: In-Memory List on PAMS Downtime |
| #71 | Database & Session Recording | 38s Worm Registry Discovery Blocks CodebuffTracker Initialization |
| #72 | Database & Session Recording | 6/6 Session Recording Failures Due to 38s Timeout |
| #73 | Database & Session Recording | PamsRecorder Fallback Layers 3 and 4 Broken |
| #53 | File System & Data Safety | G: Drive Robocopy Times Out on Large Transfers |
| #58 | File System & Data Safety | shutil.copytree + shutil.rmtree Causes Silent Data Loss on Timeout |
| #74 | Protocol & Compliance | [CRITICAL PROCESS VIOLATION] 10-Phase Gemini Injection Protocol: think |
| #75 | Protocol & Compliance | Process Violation: Claimed "Complete" Without Running Code |
| #76 | Protocol & Compliance | SOP Tightening Applied: Rule Priority Chain + Compliance Sentinel |
| #77 | Protocol & Compliance | Repeated Protocol Violations: Building Own Code Instead of Using Infer |
| #78 | Protocol & Compliance | Repeated Protocol Violations: RULE 0A Alteration + Deepseek Spawning + |
| #79 | Protocol & Compliance | Protocol Violation: Analyzed When Forbidden + Attempted "Do Both" |
| #80 | Protocol & Compliance | 3,822 Anti-Pattern Instances Exist with Zero Individual Recording |

---
*Generated from ERROR_LOG.md — 34 errors across 5 domains*
