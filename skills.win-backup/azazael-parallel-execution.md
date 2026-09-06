---
name: azazael-parallel-execution
description: RULE 0Z-F — Parallel Agent Execution Mandate. Maximum concurrency, batch all independent work into single spawn_agents calls, never sequentialize by default.
metadata:
  category: workflow
  project: azazael
  priority: critical
  auto_load: true
  version: 1.0.0
  created: 2026-06-14
---

# Azazael Parallel Execution Mandate (RULE 0Z-F)

> **Codified:** June 14, 2026
> **Canonical source:** azazael/SYSTEM_INSTRUCTIONS.md (RULE 0Z-F), azazael/SOP.md, azazael/MANDATES.md
> **Violation:** CRITICAL process violation — must be recorded in ERROR_LOG.md

---

## Core Mandate

ALL independent work items MUST be executed in parallel within a SINGLE spawn_agents call.
Never sequentialize tasks that can run in parallel.

## The 4 Rules

1. **Identify ALL independent sub-tasks** before spawning any agent
2. **Batch ALL parallel work into ONE spawn_agents call** — never spawn one agent, wait, then spawn another
3. **Maximum concurrency** — spawn as many agents as there are independent work items
4. **Never "serialize by default"** — the default assumption is parallel; only sequentialize on hard dependency

## Quick Reference

| Situation | Action |
|-----------|--------|
| 5 independent followups | Spawn ALL 5 as parallel agents in ONE call |
| Context gathering + implementation | Gather AND implement in parallel |
| Tests + typecheck + lint | Run ALL 3 in parallel via separate bashers |
| 3 file edits in different files | Edit ALL 3 in parallel (no cross-file dependencies) |
| Code review + test verification | Spawn code reviewer AND basher in ONE call |
| 4 code-searcher queries | Spawn ALL 4 in ONE spawn_agents call |
| 6 file-pickers for context | Spawn ALL 6 in ONE spawn_agents call |

## Anti-Pattern AP-ZF-1: Sequential Default Override

**Pattern:** The assistant defaults to sequential execution ("I'll do X first, then Y") even
when all work items are independent.

**Memory Anchor:** When planning work, ask: "Can these run in parallel?" If yes: ONE spawn_agents call.

**Example transformations:**
| Default Sequential (WRONG) | Parallel (RIGHT) |
|---------------------------|------------------|
| "Let me gather context first, then implement" | Spawn file-pickers AND bashers in ONE call |
| "Run test 1, see result, run test 2" | Spawn 2 basher agents in ONE call |
| "Edit file A, then file B" | Apply both str_replace in parallel if independent |
| "Spawn code reviewer, wait, then spawn basher" | Spawn both in ONE call |

## Mermaid Diagram -- Parallel vs Sequential Flow

## Related

- RULE 0Z-F — Parallel Agent Execution Mandate (canonical source: SYSTEM_INSTRUCTIONS.md)
- RULE 0M — Concurrent Inference Mandate (extends to all agent types)
- RULE 0W — 100% Agent Utilization Mandate
- RULE 0Z — Spawn Mandate
-  — Operating protocols with parallel execution guidelines
- Error #216 — RULE 0Z-F codification
