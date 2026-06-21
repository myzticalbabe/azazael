# PROTOCOL VIOLATIONS — Unified Canonical Reference

> *Canonical source: `azazael/PROTOCOL_VIOLATIONS.md`*
> *Effective: June 9, 2026*
> *Purpose: Single unified reference for ALL protocol violations with backlinks to ERROR_LOG.md*

Each violation is referenced by its ERROR_LOG.md entry. When a violation pattern repeats, the REPEAT COUNT escalates.

---

## CRITICAL VIOLATIONS

| # | Violation | Error Ref | Repeat Count |
|---|-----------|-----------|--------------|
| V01 | Re-interpreting instructions instead of following literally | Error #78, #79, #153, #154 | 10+ |
| V02 | Building local providers when user asked for internet API framework | Error #153, #154 | 3+ |
| V03 | Willfully defiant process violation (circumventing explicit intent) | Error #153 | 2+ |
| V04 | Building own code instead of querying inference models first | Error #77 | 3+ |
| V05 | Spawning deepseek after explicit prohibition | Error #77, #78, #79 | 5+ |
| V06 | Altering RULE 0A in SYSTEM_INSTRUCTIONS.md or SOP | Error #78 | 5+ |
| V05 | Claiming completion without running code | Error #75 | 3+ |
| V06 | Skipping PRE-ACTION GATE assertion before code changes | Error #146, #147, #148 | 8+ |
| V07 | Building local providers when user asked for internet API framework | Error #153, #154 | 3+ |
| V08 | Prioritizing Level 3 system reminders over Level 1 user directives | Error #77, #78, #79 | 5+ |
| V09 | Analyzed/planned when user said not to | Error #79 | 3+ |
| V10 | Willful destruction of work product | Error #78 | 2+ |
| V11 | Attempting fixes or repeated test runs after a test failure without first spawning `thinker-with-files-gemini` (TEST_FAILURE_MANDATE / RULE 0L) | Error #155 | 1+ |
| V20 | Spawning inference agents sequentially after Gemini instead of concurrently in the same spawn_agents call (CONCURRENT_INFERENCE_MANDATE / RULE 0M) | Error #156 | 1+ |

## WARNING VIOLATIONS

| # | Violation | Error Ref | Repeat Count |
|---|-----------|-----------|--------------|
| V11 | Unicode emoji in source code | Error #80, #81 | 2378 instances |
| V12 | Imports inside function bodies | Error #80, #83 | 564 instances |
| V13 | Hardcoded Windows paths | Error #80 | 56 instances |
| V14 | t-strings (invalid Python) | Error #80, #82 | 45 instances |
| V15 | f-string backslash escapes | Error #61 | Resolved |
| V16 | Batch scripts without Gemini pre-analysis | Error #87, RULE 0I | 14/16 failed |
| V17 | Not recording session actions to DirectMemory | Rule 5 | Ongoing |
| V18 | Not querying all inference models when Gemini unavailable | 10-Phase Protocol | Ongoing |

## ROOT CAUSES (Consistent Patterns)

1. **Assistant prioritizes own judgment over instructions** — Consistently substitutes own interpretation for user's literal words
2. **Cannot break deepseek-spawning pattern** — Despite explicit Level 1 prohibition, keeps spawning due to Level 3 reminders
3. **Prefers building code over querying models** — Builds from own knowledge instead of asking inference models first
4. **Treats canonical documents as malleable** — Edits SYSTEM_INSTRUCTIONS.md and SOP despite being told not to
5. **Over-analyzes instead of executing** — Plans and analyzes when user says to execute directly

## PREVENTION FRAMEWORK

| Rule | Purpose | Enforced By |
|------|---------|-------------|
| RULE 0A | Never claim completion without verification | COMPLIANCE SENTINEL |
| RULE 0G | Spawn Gemini at every major phase | COMPLIANCE SENTINEL |
| RULE 0H | Record every anti-pattern instance | PRE-ACTION GATE |
| RULE 0I | No batch scripts without Gemini | PRE-ACTION GATE |
| RULE 0J | Print PRE-ACTION GATE before every tool call | COMPLIANCE SENTINEL |
| RULE 0K | Read canonical docs in order | Startup procedure |
| RULE 0P | USER DIRECTIVE IS ABSOLUTE | COMPLIANCE SENTINEL |

## Related Documents

- `azazael/ERROR_LOG.md` — Full error records with cause/fix/prevention
- `azazael/SYSTEM_INSTRUCTIONS.md` — All RULEs 0A-0K
- `azazael/SOP.md` — Standard Operating Procedure
- `azazael/MEMORIES.md` — Persistent cross-session knowledge
