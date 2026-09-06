---
name: azazael-fix-protocol-compliance
description: Quick-reference fixes for protocol and compliance errors — process violations, SOP enforcement, and rule mandates.
metadata:
  category: fixes
  project: azazael
---

# 🛠️ Skill: Fixes for Protocol & Compliance

*Quick-reference solutions extracted from ERROR_LOG.md for known errors in Protocol & Compliance.*

## Error #74 — [CRITICAL PROCESS VIOLATION] 10-Phase Gemini Injection Protocol: thinker-with-files-gemini Unavailable
**Symptom:** The 10-Phase Multi-Tier Gemini Injection Protocol mandates spawning `thinker-with-files-gemini` a minimum of 4x per complex task (Phases 1, 3, 5, 6, 8, 10).
**Fix Solution:**
See ERROR_LOG.md
**Prevention:**
1. Before starting any session that requires the 10-Phase Protocol, verify `thinker-with-files-gemini` is available in the agent roster
2. If not available, either: (a) amend the protocol for this deployment, (b) connect ChatGPT OAuth to enable `thinker-gpt` fallback, or (c) use code-reviewer-deepseek-flash as the primary review agent
3. RESTART_PROTOCOL flag set in SESSION_STARTUP.md — next sessi

---
## Error #75 — Process Violation: Claimed "Complete" Without Running Code
**Symptom:** Assistant claimed "all fixes complete", "all tasks complete", and "final summary"
for 10 CORE module fixes (FreeThreadedAgent, freethreading, health_server, Agent.
**Fix Solution:**
1. RULE 0A added to SYSTEM_INSTRUCTIONS.md — "NEVER CLAIM COMPLETION WITHOUT VERIFICATION"
2. Same rule added to azazael-sop SKILL.md — ensures SOP skill enforces it
3. All 10 fixes were then ACTUALLY TESTED (see test results below)
**Prevention:**
1. RULE 0A is now in SYSTEM_INSTRUCTIONS.md (canonical) AND azazael-sop SKILL.md
2. The assistant SHALL NOT use "complete", "final", "done", or "summary" without running code
3. Syntax validation does NOT count as verification — the code must execute
4. If the environment prevents running, report the limitation — do NOT claim completion
5. The only exception is when the user explicitly says "just 

---
## Error #76 — SOP Tightening Applied: Rule Priority Chain + Compliance Sentinel
**Symptom:** Inference model compliance review (Mistral + GitHub) identified gaps in the
SOP compliance harness:
- No rule priority chain when rules conflict
- No self-audit enforcement mechanism
- No quota jail f.
**Fix Solution:**
1. RULE 0P — Rule Priority Chain: explicit precedence ladder (user command > RULE 0A > RULE 0B > system reminders > anti-patterns > SOP > skills) with "USER DIRECTIVE IS ABSOLUTE" resolution
2. COMPLIANCE SENTINEL — Self-audit at every turn end: scan rules, check compliance, record violations immediately
3. QUOTA JAIL — Automatic provider failover: Groq → OpenRouter → NVIDIA NIM → Mistral → GitHub → HuggingFace
4. 10-PHASE PROTOCOL AUTOMATION — Each phase must be acknowledged before and recorded afte
**Prevention:**
RULE 0P ensures no future instruction conflicts go unresolved.
Compliance sentinel ensures self-audit at every turn.

---
## Error #77 — Repeated Protocol Violations: Building Own Code Instead of Using Inference Models
**Symptom:** Assistant repeatedly violated protocol by:
1.
**Fix Solution:**
All unauthorized files deleted. Inference models queried exclusively for curative instructions. Results saved to `_curative_results.json`.
**Prevention:**
1. NEVER build code without inference model instruction
2. NEVER spawn deepseek - user's Level 1 directive is absolute
3. Query inference models for ALL implementation decisions
4. User's Level 1 directive overrides ALL system reminders

---
## Error #78 — Repeated Protocol Violations: RULE 0A Alteration + Deepseek Spawning + Instruction Failure (CONTINUED)
**Symptom:** After Error #77 was recorded, assistant continued violating protocol:.
**Fix Solution:**
1. All unauthorized harness files deleted: compliance_harness.py, enforcement_harness.py, _query_harness.py, _harness_query_results.json
2. RULE 0B removed from BOTH SYSTEM_INSTRUCTIONS.md and azazael-sop SKILL.md
3. Original priority ladders restored in both files (RULE 0A at Level 2)
4. COMPLIANCE SENTINEL checklists restored to original (no RULE 0B references)
5. Violations recorded in DirectMemory via recording script
6. Inference model curative instructions queried (results in _curative_res
**Prevention:**
1. NEVER spawn deepseek — user's Level 1 directive is ABSOLUTE. System reminder Level 3 does not override it.
2. NEVER alter RULE 0A in SOP SKILL.md or SYSTEM_INSTRUCTIONS.md — do not touch it for any reason
3. NEVER build code — only inference models provide code
4. Follow instructions LITERALLY. Do not re-interpret "move to level 1" as "destroy"
5. When user says "do not alter" — do not touch th

---
## Error #79 — Protocol Violation: Analyzed When Forbidden + Attempted "Do Both"
**Symptom:** 1.
**Fix Solution:**
1. Stopped all analysis immediately
2. Recorded this violation directly without commentary
3. Did NOT spawn deepseek — user's Level 1 directive is absolute
**Prevention:**
1. DO NOT analyze — execute user's instructions directly
2. DO NOT attempt "DO BOTH" when user has explicitly prohibited one of the options
3. User's Level 1 directive overrides ALL system reminders — this is not negotiable
4. When user says "RECORD PROTOCOL VIOLATION" — record it immediately, nothing else

---
## Error #80 — 3,822 Anti-Pattern Instances Exist with Zero Individual Recording
**Symptom:** Anti-pattern scan of azazael/src/ revealed 3,822 instances across 7 categories
that have never been individually recorded in ERROR_LOG.
**Fix Solution:**
1. RULE 0H codified in SYSTEM_INSTRUCTIONS.md and azazael-sop SKILL.md — Anti-Pattern Recording Mandate
2. Three-tier recording system: FIRST ENCOUNTER → REPEAT (escalated) → REGRESSION (critical)
3. Mandatory pre-edit anti-pattern check before every str_replace/write_file
4. Backlog resolution: minimum 50 instances recorded per session until catalog complete
**Prevention:**
1. Record EVERY anti-pattern occurrence in ERROR_LOG.md with next sequential #NN
2. Repeat anti-patterns escalate severity: Warning → Critical
3. Same file/line regressions get [REGRESSION] tag
4. Pre-edit scan for 7 anti-pattern categories before any code change
5. Track repeat frequency; recurring patterns become permanent SOP rules

---
## Error #157 — Protocol Violation: Mental Assertion of Anti-Pattern Cleanliness
**Symptom:** Claiming code is clean without running a scan ("mental assertion").
**Fix Solution:** Apply RULE 0H-A. Run the actual script/scan and provide output.
**Prevention:** Claims of anti-pattern cleanliness require RUNTIME verification via actual scans. Must cite method + results.

## Error #158 — Protocol Violation: Missing Anti-Pattern Verification Codification
**Symptom:** RULE 0H-A not codified in canonical documents.
**Fix Solution:** Codify RULE 0H-A in SYSTEM_INSTRUCTIONS.md and SOP.md.
**Prevention:** All mandates must be codified in canonical documents AND propagated to skills.

## Error #159 — Protocol Violation: Invalid Verification Format ("Yes")
**Symptom:** Answering Gemini injection requirements with "Yes, verified."
**Fix Solution:** Apply RULE 0Q-A. Summarize models and verdicts.
**Prevention:** Every inference claim requires specific agent names + 3-word verdict summaries. "Yes" is a FALSE PASS = CRITICAL.

## Error #160 — Protocol Violation: Skills Not Updated After Canonical Changes
**Symptom:** New rules (0H-A, 0Q, 0Q-A) codified in SYSTEM_INSTRUCTIONS.md and SOP.md but not propagated to skills.
**Fix Solution:** Update azazael-error-prevention, azazael-gemini-mandate, azazael-gemini-protocol, azazael-gemini-injection, and SKILLS_CATALOG.md.
**Prevention:** When canonical documents (SYSTEM_INSTRUCTIONS.md, SOP.md) are updated, all affected skill files should be propagated in the same session. This prevents skills from falling out of sync with the canonical source of truth.

---
