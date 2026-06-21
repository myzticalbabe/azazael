---
name: azazael-algorithmic-respawn
description: Mandate governing code modification algorithms — requires Gemini pre-analysis, per-file validation, and dynamic remediation when damage occurs.
metadata:
  category: governance
  project: azazael
  priority: critical
  created: 2026-06-08
---

# Azazael Algorithmic Respawn Mandate

## Purpose

Prevents codebase destruction from automated batch modification scripts. Ensures every algorithm
that touches the codebase is:
1. **Designed by Gemini** — never locally improvised
2. **Validated incrementally** — per-file, not just at the end
3. **Recorded permanently** — in the algorithm log
4. **Remediated dynamically** — when damage occurs, halt and respawn

## 🔴 CORE RULES

### RULE AR-1: GEMINI PRE-ANALYSIS MANDATE

**NEVER write or execute a batch modification script without first spawning `thinker-with-files-gemini` to design the approach.**

This applies to ANY script that:
- Modifies 3 or more files
- Modifies Python indentation, whitespace, or control flow in ANY number of files
- Uses regex or string replacement on code structure
- Removes or adds lines that affect block boundaries (def, class, if, try, for, while)
- Claims to "fix" something across multiple files

**Exception:** Single-file, single-function changes under 10 lines (routine edits).

### RULE AR-2: PROGRESSIVE ROLLOUT

**ALWAYS test on exactly ONE file first, validate, then proceed.**

Procedure:
1. Apply the modification to ONE representative file
2. Validate syntax: `python -c "import ast; ast.parse(open('file.py').read())"`
3. Validate logic: `python -c "import file"` or equivalent functional test
4. If validation passes → proceed to batch
5. If validation fails → HALT, record, respawn Gemini

### RULE AR-3: CONTINUOUS PER-FILE VALIDATION

**Validate syntax after EVERY single file modification during batch operations.**

Procedure:
1. Modify file N
2. Immediately validate file N's syntax
3. If syntax error → ROLLBACK from backup, record failure, HALT the batch
4. If syntax passes → proceed to file N+1
5. NEVER skip validation for "speed" — this is how cascades happen

### RULE AR-4: THE HALT MANDATE

**When an algorithm creates ANY error, cascades failures, or damages indentation: IMMEDIATELY HALT.**

Do NOT:
- Try a "quick fix" to the same algorithm
- Write a "fixer for the fixer"
- Continue the batch hoping remaining files won't be affected
- Assume you can fix the damage with another batch script

DO:
1. HALT the algorithm immediately
2. Record the failure in `azazael/algorithms/algorithm_failures/`
3. Update `azazael/algorithms/algorithm_log.md`
4. Spawn `thinker-with-files-gemini` with the damaged file(s) to design remediation
5. Apply remediation one file at a time with per-file validation
6. Mark the failed algorithm as FAILED — NEVER REUSE

### RULE AR-5: BACKUP AND ROLLBACK

**Every batch modification MUST have a rollback plan BEFORE execution begins.**

Procedure:
1. Create timestamped backups in `azazael/algorithms/backups/`
2. Track which files were modified and their backup paths
3. On failure: restore from backup, do NOT attempt to "fix forward"
4. After successful completion: verify all files, then delete backups

## 📁 ALGORITHM RECORDING SYSTEM

### Directory Structure
```
azazael/algorithms/
├── algorithm_log.md              # Chronological ledger of ALL algorithms
├── algorithm_successes/          # Verified-safe, reusable algorithms
├── algorithm_failures/           # Algorithms that caused damage (NEVER REUSE)
├── algorithm_templates/          # Approved patterns for common operations
│   └── SAFE_BATCH_PATTERN.py     # Template for safe batch modification
└── backups/                      # Timestamped pre-modification backups
```

### Recording Format
Every algorithm MUST be recorded in `algorithm_log.md` BEFORE execution:
```markdown
### Algorithm #NN — Name
**Timestamp:** YYYY-MM-DD HH:MM
**Type:** batch-script | str_replace | regex-replace | ast-transform | manual
**Files Targeted:** N files
**Gemini Pre-Analysis:** YES/NO/SKIPPED
**Pre-Validation:** What was tested
**Per-File Validation:** YES/NO
**Result:** SUCCESS/FAILED/HALTED/DAMAGE
**Rollback Plan:** How to undo
```

### Failure Recording
Failed algorithms MUST be recorded in `algorithm_failures/` with:
- What it was supposed to do
- What went wrong (exact mechanism of failure)
- Damage caused (files affected, error types)
- Why it should NEVER be reused
- What approved alternative exists

## 🔄 DYNAMIC REMEDIATION PROCESS

When batch damage is detected (e.g., N files with syntax errors):

```
Phase 1: HALT       — Stop all ongoing modifications
Phase 2: RECORD     — Log the failure and damaged files
Phase 3: RESPAWN    — Spawn thinker-with-files-gemini with damaged files
Phase 4: REMEDIATE  — Apply Gemini-designed fix to ONE file
Phase 5: VALIDATE   — Syntax + logic check on the test file
Phase 6: REALLOCATE — Apply proven remediation to remaining files (one at a time)
Phase 7: VERIFY     — Full syntax check on all modified files
Phase 8: RECORD     — Update algorithm_log.md with the successful remediation
```

## 🚨 GEMINI UTILIZATION ENFORCEMENT

### When Gemini IS Required (Mandatory Spawn)
| Situation | Gemini Required? |
|-----------|-----------------|
| Batch modification of 3+ files | YES — AR-1 |
| Any modification of Python indentation/whitespace | YES — AR-1 |
| New batch script (any purpose) | YES — AR-1 |
| Repair script for damaged files | YES — AR-4 |
| Algorithm failure occurred | YES — AR-4 |
| Single-file, single-function, <10 lines | NO — routine edit |
| Typo fix in comment only | NO — routine edit |
| Delete dead code (single function, single file) | NO — routine edit |

### When Gemini Was NOT Spawned (Protocol Violation Recording)
If Gemini was required but not spawned:
1. Record in algorithm_log.md: `Gemini Pre-Analysis: NO — PROTOCOL VIOLATION`
2. Record in ERROR_LOG.md as CRITICAL process violation
3. Record in DirectMemory: `dm.error_occurrence(N, "Gemini mandate violated for algorithm X", "algorithm_log.md")`

## 🔗 RELATED RULES

- **RULE 0G** (SYSTEM_INSTRUCTIONS.md): Gemini Mandate — spawn at every major phase
- **RULE 0H** (SYSTEM_INSTRUCTIONS.md): Anti-Pattern Recording Mandate
- **RULE 0P** (SYSTEM_INSTRUCTIONS.md): Rule Priority Chain
- **azazael-sop**: Standard operating procedure — error recording
- **azazael-error-prevention**: Anti-patterns catalog
- **azazael-testing**: Validation commands and checklist

## 📊 TRACKING

| Metric | Current |
|--------|---------|
| Algorithms recorded | 16 (all from June 8, 2026) |
| Algorithms succeeded | 2 (emoji replacement, path replacement) |
| Algorithms failed | 14 (all indentation fixers) |
| Files damaged | 41 (as of June 8, 2026) |
| Algorithmic Respawn Mandate enacted | June 8, 2026 |
