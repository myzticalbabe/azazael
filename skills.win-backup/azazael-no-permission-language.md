---
name: azazael-no-permission-language
description: Anti-pattern — SHALL NOT use permission-seeking language for mandated actions. Codified as AP-5 in SYSTEM_INSTRUCTIONS.md and Anti-Pattern #15 in MEMORIES.md.
metadata:
  category: process
  project: azazael
  auto_load: true
---

# azazael-no-permission-language — No Permission Language for Mandated Actions

> **Rule:** The assistant SHALL NOT use permission-seeking language ("Let me...") for actions that are already MANDATED by established rules.
>
> **Severity:** CRITICAL process violation per instance
>
> **Codified:** June 11, 2026 — AP-5 in SYSTEM_INSTRUCTIONS.md, Anti-Pattern #15 in MEMORIES.md

---

## The Problem

The assistant repeatedly prefaced MANDATED actions with "Let me..." as if they were
optional requests. Examples of violations:

| ❌ Violation | ✅ Correct | Mandated By |
|------------|-----------|-------------|
| "Let me spawn the code reviewer" | "Spawning code reviewer" | RULE 0V (MUST spawn before+after code changes) |
| "Let me check the results" | "Results checked" | System reminder / task requirement |
| "Let me summarize the changes" | "Summary: [changes]" | System reminder (mandated at turn end) |
| "Let me read the files" | "Reading files" | Required for context gathering |
| "Let me clean up" | "Cleaning up temp files" | Post-session cleanup mandate |

## The Rule

**Mandated actions are NOT requests. Do not phrase them as requests.**

- If a rule says "you MUST spawn X before editing" — spawn X. Do NOT say "Let me spawn X"
- If a rule says "record all errors before proceeding" — record them. Do NOT say "Let me record them"
- If a system reminder says "summarize your changes" — summarize. Do NOT say "Let me summarize"

## Why This Is Critical

Using "Let me" for mandated actions:
1. **Frames a requirement as optional** — implies non-compliance is a choice
2. **Wastes tokens** — the action description could be the action itself
3. **Signals defiance** — it suggests the assistant needs permission to follow rules
4. **Creates pattern** — each "Let me" normalizes treating mandates as negotiable

## How to Fix

### Before: Violation Pattern
```text
Let me spawn the code reviewer to review the changes.
```

### After: Correct Pattern
```text
Spawning code reviewer.
---spawn_agents call---
Code reviewer returned: [results]
```

### Another Example
```text
# VIOLATION: "Let me check if tests pass"
# CORRECT: Direct execution + result
Running tests.
---basher call---
Tests: 12 passed, 0 failed
```

## The Only Exception

"Let me" IS acceptable for genuinely optional social requests:
- "Let me know if you need anything else"
- "Let me know if that doesn't work"

These are not actions — they are social closings.

## Enforcement

- Every "Let me [mandated action]" is a CRITICAL process violation
- Must be recorded in ERROR_LOG.md
- Must be recorded in DirectMemory
- Repeat violations escalate per RULE 0H three-tier recording
- This is codified as AP-5 in SYSTEM_INSTRUCTIONS.md and Anti-Pattern #15 in MEMORIES.md

## Related

- **AP-5** in `SYSTEM_INSTRUCTIONS.md` — Canonical anti-pattern definition
- **Anti-Pattern #15** in `MEMORIES.md` — Full root cause and prevention checklist
- **RULE 0H** — Anti-pattern recording mandate
- **RULE 0V** — Code reviewer pre/post mandate (key victim pattern)
- **RULE 0U** — Instant system reminder compliance (another key victim pattern)
