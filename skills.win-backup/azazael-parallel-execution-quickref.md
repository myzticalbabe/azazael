---
name: azazael-parallel-execution-quickref
description: Quick-reference cheat sheet for RULE 0Z-F Parallel Agent Execution — anti-pattern table, agent spawn patterns, verification checklist
metadata:
  category: workflow
  project: azazael
  priority: critical
  auto_load: true
  version: 1.0.0
  created: 2026-06-14
---

# RULE 0Z-F Quick Reference — Parallel Agent Execution

## Anti-Pattern Table

| Sequential (WRONG) | Parallel (RIGHT) |
|-------------------|------------------|
| Spawn file-picker -> wait -> spawn code-searcher -> wait | ONE spawn_agents: file-picker + code-searcher + basher |
| Read file A -> read file B -> read file C in separate read_files calls | ONE read_files call with all 3 paths |
| Edit file 1 -> validate -> edit file 2 -> validate | Edit ALL independent files in parallel |
| Run test 1 -> see result -> run test 2 | Spawn 2 bashers in ONE call |
| "Let me gather context first, then implement" | Gather AND implement in parallel |
| "First I'll fix X, then Y, then Z" | Fix X, Y, Z in parallel (independent) |
| Spawn code reviewer -> wait -> spawn basher | Spawn BOTH in ONE call |

## Agent Spawn Patterns

| Phase | Agents to Spawn in ONE Call |
|-------|---------------------------|
| Context | 4-10 agents: file-pickers + code-searchers + bashers |
| Implementation | 2-6 agents: all independent file edits in parallel |
| Verification | 3-8 agents: tests + typecheck + lint + code reviewer |

## Pre-Check: Before Every spawn_agents Call

1. List ALL work items
2. Identify dependencies between them
3. Group ALL independent items into ONE spawn_agents call
4. NEVER spawn one agent, wait for result, then spawn another

## Enforcement Points

- **PRE-ACTION GATE** — check line: "Are ALL independent work items being executed in parallel?"
- **COMPLIANCE SENTINEL** — checklist item #23
- **Startup Step 4.8** — memory anchor at every session start
- **AP-ZF-1** — anti-pattern MEMORIES.md entry (#17)

## Related

- `azazael-parallel-execution` — Full RULE 0Z-F skill
- `azazael-operating-protocols` — Section 2: Maximum Parallel Agent Velocity
- `azazael-system-startup` — Step 4.8 enforcement
