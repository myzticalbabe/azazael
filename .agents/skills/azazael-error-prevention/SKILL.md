---
name: azazael-error-prevention
description: Anti-patterns, prevention checklists, and process guardrails to prevent repeating costly mistakes. Covers basher shell-escaping, false 3.14t diagnoses, and tool-validation protocols.
metadata:
  category: process
  project: azazael
  version: 1.0.0
---

# Azazael Error Prevention

## Overview

This skill documents **known failure modes** and their **prevention strategies**,
drawn from real incidents documented in `ERROR_LOG.md`. Load this before
running any terminal commands or debugging subprocess failures.

---

## Anti-Pattern #1: Basher/Subprocess Shell Escaping (HIGH SEVERITY)

**Incident Reference:** `ERROR_LOG.md #55`

**Symptom:** A `basher` command with nested quotes or complex string interpolation
fails silently. The error is misattributed to "Python 3.14t incompatibility"
instead of investigated as a command-line syntax issue.

**Prevention Checklist (BEFORE running any basher command):**

```
□ Use direct subprocess.call([sys.executable, '-m', 'module', arg]) — AVOID shell=True
□ If shell=True is required, use shlex.quote() on all dynamic arguments
□ Test the command directly in python -c "..." first to verify syntax
□ Run python -m module --version to confirm the tool loads before declaring it broken
□ Check if the tool is pure-Python (no C extensions) — if so, it CANNOT be a 3.14t issue
```

**Root Cause:** Subprocess commands with `shell=True` interpret the command string
through the shell, which can mangle paths with spaces, nested quotes, or special
characters. Using `subprocess.call([...])` (no `shell=True`) passes arguments
directly to the OS without shell interpretation.

**Fix Checklist (WHEN a subprocess fails unexpectedly):**

```
□ Isolate: run the exact same command in a terminal manually
□ Verify: python -m <tool> --version (confirms tool loads)
□ Check: is the tool pure-Python or C-extension?
   - Pure-Python: works on 3.14t (autoflake, pyflakes, isort, black, ruff)
   - C-extension: needs cp314t wheel (psutil, pydantic-core, numpy)
□ Test: subprocess.run([sys.executable, '-m', 'tool', '--check', path])
□ If it works directly but not via basher → shell escaping issue, not 3.14t
```

---

## Anti-Pattern #2: Declaring Tools "Broken on 3.14t" Without Isolation (HIGH SEVERITY)

**Incident Reference:** `ERROR_LOG.md #55`, `LESSONS_MASTER.md #36`

**Symptom:** A tool fails via a subprocess call and is immediately labeled
as "incompatible with Python 3.14t free-threading" without isolating the
actual failure mode. This can cost hours of unnecessary workarounds.

**Prevention Checklist (BEFORE declaring ANY tool broken on 3.14t):**

```
□ Step 1: Direct Python test
   python -c "import subprocess; r = subprocess.run([sys.executable, '-m', 'tool', '--version']); print(r.returncode)"

□ Step 2: Check if tool is pure-Python or C-extension
   - Pure-Python: pip show tool | findstr Requires
   - C-extension: check if site-packages/tool/*.pyd exists

□ Step 3: Check pip wheel tags
   pip list --format=columns | findstr tool
   # If C-extension, verify wheel has 't' in tag (e.g., cp314t)

□ Step 4: Check if tool was used successfully in PRIOR sessions
   grep -rn "tool" SESSION_INSIGHTS_*.md

□ Step 5: Only after all the above → declare tool broken on 3.14t
   And log to ERROR_LOG.md with full evidence chain
```

**Pure-Python tools that work on 3.14t (NO C extensions needed):**
- autoflake, pyflakes, isort, black, ruff
- all flake8 plugins, mypy, pydocstyle, darglint
- jinja2, markupsafe (pure Python paths), pyyaml (pure Python fallback)
- httpx, requests (pure Python), urllib3, certifi, chardet
- SQLAlchemy (pure Python), alembic

**C-extension tools that NEED cp314t wheels on 3.14t:**
- psutil (fixed via reinstall — see Error #49)
- pydantic-core (fixed via reinstall — see Error #54)
- numpy, scipy, pandas (may have cp314t wheels)
- psycopg2-binary (broken wheel — see Error #50)
- orjson, ujson, msgpack (Rust/C extensions)

---

## Anti-Pattern #3: Unused Import Accumulation (MEDIUM SEVERITY)

**Incident Reference:** `SKILLS_CATALOG.md`, `mypy` audit sessions

**Symptom:** Unused imports accumulate over time, bloating files and
creating import-time overhead. This is especially costly in projects
with many files (Azazael: ~450+ .py files).

**Prevention:**
```
□ Before committing: run autoflake_314t.py --check on changed files
□ Weekly: run autoflake_314t.py --check src/ --recursive --quiet
□ Add to pre-commit checklist: unused imports cleaned
```

---

## Anti-Pattern #4: Missing Session-End Recording (LOW SEVERITY)

**Incident Reference:** SOP Rule 5, CodebuffTracker pattern

**Symptom:** Session ends without calling `tracker.record_session_end()`,
leaving incomplete audit trails in PAMS/MemoryBus.

**Prevention:**
```
□ Before ending a session: record milestone via CodebuffTracker
□ Log errors to ERROR_LOG.md with severity classification
□ Update MEMORIES.md with session metrics
□ Add lessons to LESSONS_MASTER.md
```

---

## Related Skills

- `azazael-sop` — Standard Operating Procedure, mandatory error recording
- `azazael-autoflake` — Batch autoflake wrapper for import cleanup
- `azazael-testing` — Pre-commit checklist, validation commands
- `azazael-conventions` — Python coding conventions (import style)
