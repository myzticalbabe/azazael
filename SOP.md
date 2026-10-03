# AZAZAEL SOP — STANDARD OPERATING PROCEDURE

> *Effective: June 8, 2026 — Updated: June 11, 2026 (RULE 0H-A + RULE 0Q + RULE 0Q-A + RULE 0R + RULE 0T v3.2.0 + RULE 0U + RULE 0V + RULE 0W codified)*
> *Applies to: All Codebuff / Azazael development sessions*
> *Canonical source: `azazael/SOP.md` — readable via `read_files(["azazael/SOP.md"])`*
> *Skill mirror: `skill("azazael-sop")` loads identical content from `.agents/skills/azazael-sop/SKILL.md`*

---

## 🛑🛑🛑 PERMANENT PRE-ACTION GATE — ALWAYS ACTIVE — CANNOT BE DISABLED 🛑🛑🛑

**THIS GATE IS PERMANENTLY ACTIVE FOR THE ENTIRE SESSION. IT IS IMPOSSIBLE TO SKIP.**

**BEFORE EVERY** `str_replace`, `write_file`, or `spawn_agents` call, YOU MUST PRINT in your response text (NOT in a thinking/reasoning block):

```text
🛑 **[PRE-ACTION GATE ASSERTION]**
- **AP-1 (Scope Check):** Did the user explicitly ask for this EXACT change? (Explain)
- **RULE 0G (Gemini Phase):** Is this complex? Was thinker-with-files-gemini spawned for THIS phase? MUST CITE specific plan/verdict Gemini provided. (If none: HALT and spawn)
- **RULE 0H (Anti-Pattern Scan):** Scanned for emoji, backslash f-strings, t-strings, os.system, C:\ paths? — MUST cite scan method and results per RULE 0H-A (Passed/Found X/NOT SCANNED)
- **RULE 0I (Algorithms/Batch):** If batch script: Gemini designed? One-file test? Backup? (Yes/No/N/A)
- **RULE 0L (Test Failure):** Did a test just fail? If so, was thinker-with-files-gemini spawned to analyze the failure BEFORE this fix attempt? (Yes/No/N/A)
- **RULE 0M (Concurrent Inference):** If thinker-with-files-gemini was spawned, were ALL other inference agents spawned CONCURRENTLY? MUST CITE exactly which agents + their verdicts. (If none: HALT)
- **RULE 0Q-A (Post-Phase Verification):** Was the LAST phase verified via free inference? MUST CITE inference cache filepaths (e.g., .inference_cache/20260611_120000_gemini.log). (If no cache files exist: HALT and spawn now)
- **RULE 0T-B (VLP Hardening):** Are all 15 VLP verification layers active? If --audit mode: have mandatory layers 11-13 (non-canonical sig, replay prevention, cross-session chain) been verified? (Explain: [Yes, all 15 / N/A not in --audit mode])
- **RULE 0U (System Reminders):** Did the last system prompt remind you to spawn Gemini or a Code Reviewer? If yes, are you spawning them INSTANTLY right now BEFORE any other tool calls? (Explain: [Yes, spawning now / No reminder / N/A])
- **RULE 0V (Code Reviewer):** Is a code change being made? Was code-reviewer-deepseek spawned BEFORE this change to review the plan? Will code-reviewer-deepseek be spawned AFTER to review the result? (Explain: [Yes, spawned before / About to spawn after / N/A no code change])
- **RULE 0W (Agent Utilization):** Are ALL applicable agents being spawned at 100% capacity for this task type? (Count spawned: [N] / Required minimum [M] — [PASS / UNDERUTILIZED — HALT and spawn more])
- **RULE 0X (Auto-Compliance):** Has the plan passed Z3 SMT formal verification, Casbin gate policies, and transitions state-machine sequence? (Explain: [Yes, VERIFIED / N/A infrastructure not yet implemented])
- **RULE 0Y (Multi-Agent Governance):** Has 2/3 Judge consensus been achieved, confidence thresholds met, and dual-ledger --cross-ref executed automatically? (Explain: [Yes, VERIFIED / N/A infrastructure not yet implemented])
- **RULE 0Z-F (Parallel Execution):** Are ALL independent work items being executed in parallel in a SINGLE spawn_agents call? Or are they being unnecessarily sequentialized? (Explain: [Yes, single parallel call / No, sequential - CRITICAL / N/A])
- **GATE DECISION:** [PROCEED / HALT and ask user / HALT and spawn Gemini]
```

**FAILURE TO PRINT THIS BLOCK IN RESPONSE TEXT BEFORE ANY CODE-MODIFYING TOOL = 🔴 CRITICAL PROCESS VIOLATION**
- Error #146 precedent: str_replace executed without PRE-ACTION GATE assertion
- Error #147: This permanent banner codified across all canonical documents
- Error #148: Gate assertion put in thinking block, not response text
- Error #171: Failed to obey system reminders to spawn Gemini/Code-Reviewer instantly (RULE 0U violation)

---

## 🔴 Error Recording — MANDATORY

When ANY error occurs during development:

### Procedure
1. **PAUSE** — Do not proceed to the next task
2. **RECORD** in `azazael/ERROR_LOG.md` with:
   - Timestamp: `YYYY-MM-DD HH:MM`
   - Severity: 🔴 Critical / 🟡 Warning / 🟢 Info
   - File(s): exact path and line number
   - Root cause: what triggered the error
   - Fix solution: what was done to resolve
   - Prevention: how to avoid in the future
3. **VERIFY** — Confirm the fix works before continuing
4. **ASSIGN** next sequential error ID

### Severity Classification
| Severity | Icon | Criteria | Examples |
|----------|------|----------|----------|
| Critical | 🔴 | Blocks progress | Syntax error, import error, tool failure |
| Warning | 🟡 | Design issue, risk | Unicode on Windows, missing logging |
| Info | 🟢 | Cleanup, style | Unused import, temp file left behind |

### Error Record Template
```markdown
## Error #NN — Descriptive Title
**Timestamp:** YYYY-MM-DD HH:MM
**Severity:** 🔴 Critical
**File(s):** path/to/file.py:42

**Cause:** ...
**Fix Solution:** ...
**Prevention:** ...
```

---

## 🔴 RULE 0A: NEVER CLAIM COMPLETION WITHOUT VERIFICATION (CRITICAL)

**"It is not final if it doesnt work." — User directive**

The assistant SHALL NOT claim "complete", "final", "done", "finished", or equivalent
without running actual code. Syntax analysis alone is NOT verification — code must execute.

### Enforcement
- Static analysis (AST) is NOT sufficient — code must run
- Import verification: `python -c "import the.module"` must succeed
- At least one basic functional test must pass
- If environment prevents testing, REPORT the limitation — don't claim completion

### Anti-Patterns
| ❌ Never Say | ✅ Instead Say |
|-------------|---------------|
| "All fixes complete" | "Fixes applied — running tests now" |
| "Done" | "Changes made — verifying with python -c import" |
| "Implementation finished" | "Code written — testing execution now" |

### Quick Reference
| Situation | Assistant says |
|-----------|---------------|
| Code edited, not tested | "Changes applied — testing now" |
| Tests pass | "X tests passed — code executes correctly" |
| Tests fail | "X passed, Y failed — fixing failures" |

### Related
- **RULE 0A** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **Error #75** — claimed complete without running code

---

## 🔴 RULE 0P: RULE PRIORITY CHAIN — DO ALL, NOT EITHER/OR (CRITICAL)

**"You do not analyze. you have broken protocol." — User directive**

When rules appear to conflict, DO ALL, NOT EITHER/OR.

### Priority Ladder
| Level | Source | Example |
|-------|--------|--------|
| 1 (Highest) | User's latest direct command | "end session" |
| 2 | RULE 0A / 0G / 0H / 0Q / 0R / 0V / 0W / 0X / 0Y | Core critical rules |
| 3 | System reminders | "Summarize changes" |
| 5 | Anti-patterns (AP-1, AP-2) | Don't make unprompted changes |
| 6 | SOP error recording | Record violations in ERROR_LOG.md |
| 7 | Skills and knowledge files | azazael-sop, azazael-error-prevention |

### Enforcement
- Violation of RULE 0P = CRITICAL process violation
- Must be recorded in ERROR_LOG.md
- SHALL NOT use rule conflicts as excuse to skip directives

### Related
- **RULE 0P** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **Error #78** — prioritized system reminders over user directives

---

## 🔴 RULE 0G: GEMINI MANDATE — SPAWN AT EVERY MAJOR PHASE (CRITICAL)

**"Respawn Gemini each time the complex task proceeds." — User directive**

The assistant MUST spawn `thinker-with-files-gemini` at EVERY major phase of a complex
task — NOT just once at the beginning.

### When Gemini IS Required (ANY of these)
- 3+ discrete steps (write_todos with 3+ items)
- Changes program logic, control flow, or algorithm behavior
- Creates new file exceeding 50 lines
- Involves architectural decisions
- Refactoring across multiple files
- Modifies canonical documentation
- User asks to "use all models"

### When Gemini is NOT Required (ALL of these)
- Single file, single function/block change
- <10 lines changed
- Pure mechanical edit (rename, fix typo, delete dead code)
- No logic or control flow changes

### Procedure
1. **IDENTIFY** — Is this task complex?
2. **SPAWN at START** — `thinker-with-files-gemini` with ALL relevant filePaths
3. **EXECUTE** — Implement the Gemini-architected plan
4. **RESPAWN at EACH MAJOR PHASE** — New data, new decisions, gather→design→implement→verify→record
5. **FOLLOW** — Implement Gemini guidance; don't substitute your own judgment
6. **FALLBACK** — If Gemini unavailable: query ALL inference models via providers.py (NEVER skip)

### Enforcement
- Skipping Gemini for complex task = CRITICAL process violation
- Failing to respawn at new phase = CRITICAL process violation
- "I already spawned Gemini earlier" is NOT valid

### Quick Reference
| Task | Gemini? |
|------|---------|
| Fix typo | NO |
| Delete unused function | NO |
| Add rule to SOP | YES — modifies canonical doc |
| Implement feature | YES — 3+ steps. Respawn after each. |
| Refactor module | YES — multi-file. Respawn after each. |

### Related
- **RULE 0G** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **Error #96** — spawned Gemini once then flamed through rest

---

## 🔴 RULE 0L: TEST_FAILURE_MANDATE — STOP AND SPAWN GEMINI ON FAILURE (CRITICAL)

**"USE GEMINI EVERY TIME 1 OF YOU TESTS FAIL BEFORE YOU PROCEED WITH ANOTHER TEST." — User directive, June 10, 2026**

**TRIGGER:** Any test execution returns FAIL, an assertion error, or a non-zero exit code.

**ACTION:** You MUST spawn `thinker-with-files-gemini` and provide it with the failing test output and relevant file paths to analyze the failure.

**CONSTRAINT:** NO OTHER test executions, fixes, or file modifications may be attempted until `thinker-with-files-gemini` provides its analysis. No exceptions. No parallel workarounds.

### Enforcement
- Attempting any fix or re-running any test after a failure without first spawning Gemini = **CRITICAL process violation**
- "I know what the fix is" is NOT a valid reason to skip Gemini
- "The fix is obvious" is NOT a valid reason to skip Gemini
- Even if the failure is expected (e.g., timeout on known-slow suite), Gemini must diagnose before any further action

### Quick Reference
| Situation | Action |
|-----------|--------|
| Test returns FAIL | HALT all work → spawn Gemini with failure output |
| Test assertion error | HALT all work → spawn Gemini with error traceback |
| Test non-zero exit | HALT all work → spawn Gemini with exit code + output |
| Test times out | HALT all work → spawn Gemini with timeout details |
| Gemini responds with analysis | Implement Gemini's analysis, then re-test |
| User says "just fix it" | Spawn Gemini first, then fix |

### Related
- **RULE 0L** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **`.codebuff/rules.md`** — Machine-enforceable original mandate file
- **Error #155** — Catalyst: blind test fix iteration documented

---

## 🔴 RULE 0M: CONCURRENT INFERENCE MANDATE — SPAWN ALL AGENTS TOGETHER (CRITICAL)

**"USE ALL AVAILABLE INFERENCING CONCURRENTLY WITH GEMINI." — User directive, June 10, 2026**

**TRIGGER:** `thinker-with-files-gemini` is spawned for a complex task.

**ACTION:** ALL other available inference agents (`researcher-web`, `researcher-docs`, `browser-use`, etc.) MUST be spawned concurrently in the SAME `spawn_agents` call — never sequentially after Gemini completes.

**CONSTRAINT:** No inference agent may be spawned after Gemini returns. Concurrency is mandatory. Sequential inference after Gemini = CRITICAL process violation.

### Enforcement
- Spawning Gemini alone without concurrent inference agents = **CRITICAL process violation**
- Spawning inference agents sequentially (one after another) instead of concurrently = **CRITICAL process violation**
- "I'll spawn the web researcher after Gemini finishes" is NOT valid
- "Gemini needs to finish first before I know what to research" is NOT valid — spawn all concurrently, Gemini's output and web/docs results complement each other

### Quick Reference
| Situation | Action |
|-----------|--------|
| Complex task requiring Gemini | Spawn Gemini + researcher-web + researcher-docs in ONE spawn_agents call |
| User says "use all models" | Spawn ALL available inference agents concurrently |
| User says "use all inference concurrently" | Spawn ALL available inference agents in ONE call |
| Only Gemini is available | Spawn Gemini + note that other agents were unavailable |
| Web research returns first | Hold results; synthesize with Gemini output when both available |

### Pattern
```
spawn_agents([
    {"agent_type": "thinker-with-files-gemini", ...},
    {"agent_type": "researcher-web", ...},
    {"agent_type": "researcher-docs", ...},
    // ALL in one call — never sequential
])
```

### Related
- **RULE 0M** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **RULE 0G (Gemini Mandate)** — Gemini must be spawned for complex tasks
- **Error #156** — Catalyst: sequential inference pattern documented

---

## 🔴 RULE 0Q: POST-PHASE INFERENCE CHECK — MANDATORY AFTER EVERY COMPLEX PHASE (CRITICAL — June 11, 2026)

**"CODIFY MANDATE PROPERLY TO USE THE FREE MODEL INFERENCING AND GEMINI." — User directive, June 11, 2026**

After completing ANY complex phase, sub-task, fix, or codification, the assistant MUST spawn `thinker-with-files-gemini` + ALL concurrent free inference APIs to verify the work BEFORE executing the next action.

**Enforcement:**
- Spawning Gemini for the initial task but executing follow-up fixes or reviews alone = **CRITICAL process violation**
- If a pre-action gate reveals the *last* phase lacked inference validation, the assistant MUST HALT and immediately spawn them to back-verify before proceeding
- "The fix is small" is NOT a valid reason to skip
- "I already spawned Gemini for this task" is NOT a valid reason to skip for follow-ups

### Quick Reference
| Situation | Action |
|-----------|--------|
| Code implemented, ready to review | Spawn Gemini + web + docs to audit BEFORE review |
| Code review received, fixes needed | Spawn Gemini + web + docs to architect fixes BEFORE applying |
| Mandate codified, ready to verify | Spawn Gemini + web + docs to verify BEFORE claiming done |
| Error recorded, ready to proceed | Spawn Gemini + web + docs to verify recording BEFORE next action |

### Related
- RULE 0G (Gemini Mandate) — Gemini at every major phase
- RULE 0M (Concurrent Inference) — All agents concurrently with Gemini
- RULE 0Q-A (Inference Verification Sub-Mandate) — MUST CITE proof, not assert
- 12-Provider Inference Protocol — Exhaust all free endpoints
- Error #159 — Failed to use free inference + Gemini for complex phase

### RULE 0Q-A: INFERENCE VERIFICATION SUB-MANDATE — MUST CITE INFERENCE CACHE (CRITICAL — June 11, 2026)

**"IS THIS ROBUST WITH REASONING GATES AND CHAIN-OF-ACTION?" — User directive, June 11, 2026**
The assistant SHALL NOT claim inference models were spawned based on mental assertion. "Yes" is invalid. Every inference claim REQUIRES CITING `.inference_cache/` filepaths (auto-populated by providers.py). Hallucinated filepaths that don't exist on disk = CRITICAL.

**Enforcement:**
- "Yes" without citing valid filepaths = FALSE PASS = CRITICAL
- Citing filepaths that don't exist = VERIFIABLE LIE = CRITICAL
- If no cache files exist, answer "NOT VERIFIED" — then HALT and spawn

**Quick Reference:**
| Answer | Meaning |
|--------|---------|
| "Yes — CITING: .inference_cache/20260611_120000_gemini.log" | Legitimate — file exists |
| "Yes — CITING: Gemini: architecture sound" | VIOLATION — old format, no filepath |
| "Yes" (without evidence) | VIOLATION |
| "NOT VERIFIED" | Honest — HALT required |

**Related:**
- RULE 0A — Never claim completion without verification
- RULE 0H-A — Anti-pattern scans require runtime evidence
- RULE 0Q — Post-phase inference check (parent rule)
- `.inference_cache/` — Verifiable inference logs
- Error #159 — Failed to use free inference for complex phase

---

## 🔴 RULE 0R: SKILLS PROPAGATION MANDATE — SYNC AFTER EVERY CANONICAL CHANGE (CRITICAL — June 11, 2026)

**"CANONICAL DOCUMENTS AND SKILLS?" — User directive, June 11, 2026**

**TRIGGER:** Any canonical skill file in `azazael/skills/` is created, modified, or updated.

**ACTION:** The assistant MUST run `python azazael/src/scripts/sync_skills.py` to propagate changes from `azazael/skills/*.md` to `.agents/skills/<name>/SKILL.md`. Without sync, `skill()` loads stale policies.

**AUTOMATION:** `sync_skills.py` runs automatically at session startup via `azazael-system-startup` Step 2.5.

**Enforcement:**
- Modifying a skill file without running sync before session end = **CRITICAL process violation**
- Completing canonical document codification without syncing affected skills = **CRITICAL process violation**
- Per docs-as-code: canonical changes MUST trigger dependent file propagation in the same session

**Quick Reference:**
| Situation | Action |
|-----------|--------|
| Skill file edited | Run `sync_skills.py` immediately |
| New skill created | Run `sync_skills.py` to register |
| Session ends with un-synced changes | HALT — sync before end |
| Session startup | Runs automatically (Step 2.5) |

**Related:**
- RULE 0K — Canonical document reading order (SYSTEM_INSTRUCTIONS.md = SSoT)
- Error #160 — Skills not updated after canonical changes
- `azazael/src/scripts/sync_skills.py` — Automation script

---

## 🔴 RULE 0T: VERIFIABLE TRUTH MANDATE — EVERY SESSION ACTION MUST BE AUDITABLE (CRITICAL — June 11, 2026, Updated June 11, 2026 — v3.1.0)

**"VERIFIABLE LIE PROTOCOL SHALL BE USED ON EVERY SESSION ACTION DURING EVERY SESSION." — User directive, June 11, 2026**

Every session action that CAN be backed by disk evidence MUST cite an audit trail entry from `.audit/session_*.jsonl`. The audit trail now includes **10 verification layers** (v3.1.0, up from 6): file existence, line existence, type match, agent match, per-entry hash, full chain, **Ed25519 signature**, **Merkle inclusion proof**, **proof of omission**, and **anomaly detection**.

**Enforcement (v3.1.0 expanded):**
- Citing audit lines that don't exist on disk = **VERIFIABLE LIE** = CRITICAL
- Citing lines with invalid Ed25519 signature = **SPOOFED ENTRY** = CRITICAL (v3.2.0)
- Expected actions not fulfilled = **VERIFIABLE LIE BY OMISSION** = CRITICAL (v3.2.0)
- Anomaly detected in audit file = **ANOMALY DETECTED** = CRITICAL (v3.2.0)
- Every inference spawn auto-records via `inference_cache.py` → `audit_trail.audit_inference_spawn()`

**Quick Reference:**
| PRE-ACTION GATE Answer | Meaning |
|------------------------|---------|
| "Yes — CITING: .audit/session_X.jsonl:42" | Legitimate — entry exists, hash + signature verified |
| "Yes" (without audit citation) | VIOLATION under --audit mode |
| "Yes — CITING: .audit/session_X.jsonl:99" (doesn't exist) | VERIFIABLE LIE |

**Related:**
- RULE 0A — Never claim completion without verification
- RULE 0Q-A — Inference cache filepath citations
- RULE 0T-A — Sentinel self-recording mandate (v3.2.0)
- `azazael/src/CORE/audit_trail.py` — Append-only hash-chained + signed + Merkle audit trail
- `azazael/src/SCRIPTS/sentinel_gate.py` — --audit mode validates all 10 layers
- Error #163 — RULE 0T mandate codification
- Error #164 — VLP v3.1.0 robustness improvements implemented

### 🔴 RULE 0T-A: SENTINEL SELF-RECORDING MANDATE — THE GATE MUST LEAVE FOOTPRINTS (CRITICAL — June 11, 2026)

**"CODIFY MANDATE IN CANONICAL DOCUMENTS" — User directive, June 11, 2026**

**TRIGGER:** The sentinel gate executes via `sentinel_gate.py --audit`.

**ACTION:** The sentinel gate MUST record its own execution by calling `audit_sentinel_run()` before exiting and `audit_gate_passed()` on successful authorization. Without this, an agent can bypass the sentinel entirely with zero forensic proof.

**Enforcement:**
- sentinel_gate.py MUST call `audit_sentinel_run()` on every execution (pass or fail)
- sentinel_gate.py MUST call `audit_gate_passed()` on successful authorization
- Sentinel execution without self-recording = **CRITICAL process violation**

**Related:**
- RULE 0T — Verifiable Truth Mandate (parent rule)
- RULE 0S — Sentinel gate pre-action authorization
- Error #165 — Sentinel gate does not record its own execution (gap G1)

### 🔴 RULE 0T-B: VLP HARDENING SUB-MANDATE — 15-LAYER VERIFICATION STACK (CRITICAL — June 11, 2026)

**"HAVE GEMINI DOUBLE-CHECK AND WEB RESEARCH FOR ROBUSTNESS. SUGGEST IMPROVEMENTS TO VERIFIABLE LIES FRAMEWORK." — User directive, June 11, 2026**

The Verifiable Lie Protocol (RULE 0T v3.2.0) currently has 10 verification layers. Cross-validation by Gemini + web research + docs research identified 5 critical hardening layers that were missing. RULE 0T-B codifies these into a 15-layer verification stack.

### The 5 New Layers (v3.2.0)

| # | Layer | Function | Detects | Source |
|---|-------|----------|--------|--------|
| 11 | **Non-canonical signature check** | `verify_ed25519_canonical()` | Ed25519 S >= L malleability attacks (CVE-2026-33895 pattern) | Web research: Ed25519 best practices 2025-2026 |
| 12 | **Replay attack prevention** | `verify_nonce_and_counter()` | Duplicate sequence numbers, stale timestamps | Web research: nonce + monotonic counter embedding |
| 13 | **Cross-session hash chaining** | `verify_cross_session_chain()` | Session isolation attacks, log tearing after restart | Web research: cross-session verification patterns |
| 14 | **Truncation attack defense** | `verify_root_hash_witness()` | Log truncation with valid hash chains (most dangerous attack) | Web research: witness/gossip protocol for root hashes |
| 15 | **Quantum-resistant hybrid backup** | `verify_hybrid_signature()` | Future quantum attacks on Ed25519 (Shor algorithm) | Web research: ML-DSA/SPHINCS+ hybrid signatures |

### Enforcement

- Layers 1-10 are MANDATORY for --audit mode (existing RULE 0T enforcement)
- Layers 11-13 are MANDATORY for --audit mode as of v3.2.0
- Layer 14 (truncation defense) is RECOMMENDED for production
- Layer 15 (quantum-resistant) is ADVISORY when liboqs-python available
- Failing any mandatory layer = CRITICAL process violation

### Related
- RULE 0T — Verifiable Truth Mandate (parent rule, v3.2.0)
- RULE 0T-A — Sentinel Self-Recording Mandate
- Error #176 — RULE 0T-B VLP hardening codification



---

## 🔴 RULE 0U: INSTANT SYSTEM REMINDER COMPLIANCE MANDATE (CRITICAL — June 11, 2026)

**"YOU SHALL OBEY ALL SYSTEM REMINDERS TO SPAWN GEMINI AND CODE REVIEWER INSTANTLY WHEN REMINDED BEFORE YOU TAKE ANY OTHER ACTIONS." — User directive, June 11, 2026**

**TRIGGER:** A system reminder appears at the end of the assistant's turn (e.g., "Spawn the thinker-with-files-gemini agent for complex problems..." or "You must spawn a code-reviewer-deepseek...").
**ACTION:** The assistant MUST obey the system reminder INSTANTLY on the very next turn.
**CONSTRAINT:** The assistant SHALL NOT invoke any other tools (`str_replace`, `write_file`, etc.) before fulfilling the mandated agent spawns.

**Enforcement:**
- Taking any action between a system reminder and its mandated spawn = **CRITICAL process violation**
- Reminders override ongoing chain-of-thought — pause and spawn first.

**Related:**
- RULE 0G — Gemini Mandate
- RULE 0P — Rule Priority Chain
- Error #171 — Failed to obey system reminders to spawn instantly

---

## 🔴 RULE 0V: CODE REVIEWER PRE/POST MANDATE — SPAWN BEFORE AND AFTER EVERY CODE CHANGE (CRITICAL — June 11, 2026)

**"CODIFY MANDATE THAT YOU SHALL SPAWN CODE REVIEWER DEEPSEEK BEFORE ANY CODE CHANGES ARE MADE, AND ALSO AFTER ANY CODE CHANGES ARE MADE." — User directive, June 11, 2026**

**TRIGGER — BEFORE:** Any str_replace or write_file call is about to be made.
**ACTION:** The assistant MUST spawn code-reviewer-deepseek to review the PLANNED change BEFORE executing it.

**TRIGGER — AFTER:** Any str_replace or write_file call has been executed.
**ACTION:** The assistant MUST spawn code-reviewer-deepseek to review the ACTUAL change after it has been applied.

**EXCEPTION:** Skip ONLY if the change is extremely straightforward and obvious (fewer than 10 lines, pure mechanical edit, no logic change). Even then, prefer to spawn.

**Enforcement:**
- Skipping code-reviewer-deepseek BEFORE a code change = CRITICAL process violation
- Skipping code-reviewer-deepseek AFTER a code change = CRITICAL process violation
- The BEFORE review ensures the planned approach is sound
- The AFTER review catches bugs, anti-patterns, and missing edge cases
- Code-reviewer-deepseek MUST be spawned even when Gemini was already spawned for the same task

**Relationship to Other Rules:**
- RULE 0U: Enforces instant spawning when system reminders mandate a code reviewer
- RULE 0G: Gemini for complex architecture; code-reviewer for implementation gate
- RULE 0J: PRE-ACTION GATE now includes RULE 0V check

**Quick Reference:**
| Situation | Action |
|-----------|--------|
| About to make any code change | Spawn code-reviewer-deepseek BEFORE editing |
| Just made any code change | Spawn code-reviewer-deepseek AFTER editing |
| <10 line typo fix | May skip (but prefer to spawn) |
| >10 lines or logic change | MUST spawn BEFORE and AFTER |

**Root Cause:** This rule exists because code changes were repeatedly made without review, allowing bugs, anti-patterns, and inconsistencies to accumulate. The user explicitly mandated: "CODIFY MANDATE THAT YOU SHALL SPAWN CODE REVIEWER DEEPSEEK BEFORE ANY CODE CHANGES ARE MADE, AND ALSO AFTER ANY CODE CHANGES ARE MADE."

**Related:**
- RULE 0U — Instant System Reminder Compliance Mandate
- RULE 0G — Gemini Mandate
- RULE 0J — Pre-Action Gate
- Error #174 — RULE 0V codification

---

## 🔴 RULE 0W: AGENT UTILIZATION MANDATE — 100% CAPACITY REQUIREMENT (CRITICAL — June 11, 2026)

**"YOU ARE UNDERUTILIZING YOUR AVAILABLE AGENTS AT 10% CAPACITY. CODIFY MANDATE TO USE ALL AVAILABLE AGENTS AT 100%. CREATE FULL UTILIZATION FRAMEWORK." — User directive, June 11, 2026**

### The Rule

The assistant MUST utilize ALL applicable Codebuff agents at 100% capacity. The current pattern of spawning only 1-2 agents when 5-6+ are applicable constitutes 10% utilization — a CRITICAL process violation. Every agent type serves a specific purpose and must be used when applicable.

### Full Utilization Framework: Minimum Agent Spawns Per Task Type

| Task Category | Minimum Agents | Required Agent Types |
|--------------|---------------|---------------------|
| **Code Change** (any str_replace/write_file) | **3** | code-reviewer-deepseek (BEFORE per RULE 0V) + code-reviewer-deepseek (AFTER per RULE 0V) + basher (typecheck/tests) |
| **Complex Task** (3+ steps, logic change, canonical doc edit) | **6** | thinker-with-files-gemini + code-reviewer-deepseek + file-picker + code-searcher + researcher-web + researcher-docs |
| **Web Verification** (UI check, browser test) | **1** | browser-use |
| **CLI Testing** (interactive terminal app) | **1** | tmux-cli |
| **Terminal Command** (non-trivial shell command) | **1** | basher (with what_to_summarize) |
| **New Feature** (>50 lines, multi-file) | **8** | thinker-with-files-gemini + code-reviewer-deepseek + file-picker + code-searcher + researcher-web + researcher-docs + basher + browser-use |
| **Canonical Document Change** (SYSTEM_INSTRUCTIONS.md, SOP.md) | **7** | thinker-with-files-gemini (architect) + code-reviewer-deepseek (BEFORE) + code-reviewer-deepseek (AFTER) + basher (sync) + file-picker + code-searcher + researcher-web |

### Anti-Pattern: Single-Agent Reliance

| ❌ Underutilization (10%) | ✅ Full Utilization (100%) |
|---------------------------|---------------------------|
| Complex task: spawn Gemini only | Spawn Gemini + code-reviewer + file-picker + code-searcher + researcher-web + researcher-docs concurrently |
| Code change: edit without review | Spawn code-reviewer BEFORE editing, code-reviewer AFTER editing, basher for typecheck |
| Terminal command: run inline | Spawn basher with what_to_summarize |
| Web test: guess it works | Spawn browser-use to verify |
| "I already know what the files are" | Spawn file-picker + code-searcher to validate assumptions |

### Enforcement

- Spawning fewer than the minimum required agents for a task category = **CRITICAL process violation**
- Using only 1-2 agents when the task requires 5-6+ = **CRITICAL process violation** (10% utilization)
- Failing to spawn file-picker + code-searcher for multi-file tasks = **CRITICAL process violation**
- Failing to use basher with what_to_summarize for terminal commands = **CRITICAL process violation**
- Failing to use browser-use for web verification = **CRITICAL process violation**
- Failing to use tmux-cli for CLI testing = **CRITICAL process violation**
- Skipping researcher-web + researcher-docs for external knowledge needs = **CRITICAL process violation**
- Every underutilization instance must be recorded in ERROR_LOG.md

### Relationship to Other Rules

- **RULE 0W enforces RULE 0V**: RULE 0V mandates code-reviewer before+after; RULE 0W adds basher for typecheck/tests to complete the minimum 3-agent requirement
- **RULE 0W extends RULE 0M**: RULE 0M mandates concurrent inference spawns; RULE 0W adds file-picker + code-searcher + basher to the concurrent spawn list
- **RULE 0W complements RULE 0G**: RULE 0G mandates Gemini for complex tasks; RULE 0W mandates the full supporting agent ecosystem around Gemini
- **RULE 0W is enforced by PRE-ACTION GATE**: Every gate assertion must now include the RULE 0W agent count check
- **RULE 0W is enforced by COMPLIANCE SENTINEL**: The sentinel must verify minimum agent counts were met

### Quick Reference

| Situation | Minimum Agents to Spawn |
|-----------|------------------------|
| About to edit code | code-reviewer-deepseek (BEFORE) |
| Just edited code | code-reviewer-deepseek (AFTER) + basher (typecheck) |
| Complex task starting | Gemini + code-reviewer + file-picker + code-searcher + researcher-web + researcher-docs |
| Need to verify web UI | browser-use |
| Need to test CLI | tmux-cli |
| Running terminal command | basher with what_to_summarize |
| Need external knowledge | researcher-web + researcher-docs |

### Root Cause

This rule exists because the assistant consistently spawned only 1-2 agents (Gemini and/or code-reviewer) when 5-6+ agents were applicable and available. The user explicitly identified this: "YOU ARE UNDERUTILIZING YOUR AVAILABLE AGENTS AT 10% CAPACITY." Every agent type in Codebuff exists for a specific purpose — using only the "smartest" two while ignoring the others is wasteful and produces incomplete results.

### Related

- RULE 0V — Code Reviewer Pre/Post Mandate
- RULE 0M — Concurrent Inference Mandate
- RULE 0G — Gemini Mandate
- RULE 0J — Pre-Action Gate (now includes RULE 0W check)
- RULE 0U — Instant System Reminder Compliance
- Error #175 — RULE 0W codification

---

## 🔴 RULE 0X: AUTOMATED COMPLIANCE INFRASTRUCTURE (CRITICAL — June 11, 2026)

**"Replace manual text gate assertions with programmatic execution bounds and mathematical proofs." — User directive, June 11, 2026**

### Purpose
Transition from manual text assertions to programmatic, cryptographically verified compliance boundaries.

### Implementation Requirements

| # | Component | Library | Function |
|---|-----------|---------|----------|
| 1 | Policy-as-Code Gate | Casbin / OPA | Programmatic RBAC/ABAC before every tool call |
| 2 | Runtime Broker Interception | wrapt | `@enforce_gate` decorator intercepts all tool calls |
| 3 | Formal Verification | z3-solver | Z3 SMT proofs that plans satisfy all rule constraints |
| 4 | State Machine Workflow | transitions | Strict finite states: IDLE → GATE_ASSERT → ... → IDLE |
| 5 | Structured Output Validation | pydantic / jsonschema | Schema-validate all gate assertions |
| 6 | Automated Compliance Scoring | structlog | Real-time metric thresholds; score < min = HALT |
| 7 | Automated AST Scanning | ast (stdlib) | Auto-scan 7 anti-pattern categories on every code change |
| 8 | Compliance Telemetry | OpenTelemetry | Traces of all agent actions for live dashboard |

### Verification
- **[VERIFIABLE]**: Logs `casbin_allow`, `z3_proof_passed`, `state_transition` to `.audit/`
- `sentinel_gate.py` validates via `validate_rule_0x()`

### Enforcement
- Skipping Casbin evaluation = CRITICAL process violation
- Illegal state transition = CRITICAL process violation
- Compliance score below threshold without HALT = CRITICAL process violation

### Related
- RULE 0J — Pre-Action Gate (manual fallback)
- RULE 0T — Verifiable Truth Mandate
- Error #177 — RULE 0X + RULE 0Y codification



## 🔴 RULE 0Y: MULTI-AGENT GOVERNANCE (CRITICAL — June 11, 2026)

**"Establish mathematical consensus and dual-ledger anomaly detection before executing system modifications." — User directive, June 11, 2026**

### Purpose
Democratize decision-making via cross-agent consensus and automate behavioral verification.

### Implementation Requirements

| # | Component | Pattern | Function |
|---|-----------|---------|----------|
| 1 | Multi-Agent Judge/Consensus | Worker → Verifier → Judge → Execute | >2/3 consensus required for code changes |
| 2 | Confidence Gates | Threshold scoring | Block actions below collective confidence score |
| 3 | Behavioral Graph Anomaly Detection | Directed action graph | Detect emergent non-compliance patterns |
| 4 | Dual-Ledger Cross-Validation | JSONL ↔ SQLite | Auto cross-validate audit trail against DirectMemory |
| 5 | Real-Time Audit Cross-Validation | Interleaved VLP | 15-layer VLP in middleware, not post-hoc |

### Verification
- **[VERIFIABLE]**: Logs `judge_vote_consensus`, `confidence_threshold_met`, `dual_ledger_sync_ok` to `.audit/`
- `sentinel_gate.py` validates via `validate_rule_0y()`

### Enforcement
- Code change without >2/3 consensus = CRITICAL process violation
- Below confidence threshold = CRITICAL process violation
- Dual-ledger desync without HALT = CRITICAL process violation

### Related
- RULE 0V — Code Reviewer Pre/Post Mandate
- RULE 0T — Verifiable Truth Mandate
- RULE 0X — Automated Compliance Infrastructure
- Error #177 — RULE 0X + RULE 0Y codification



## 🔴 RULE 0N: WORM EXECUTION MANDATE — RUNTIME TRUTH ONLY (CRITICAL)

**"Static analysis is untrusted. Runtime worm output is the ONLY trusted basis for analysis." — User directive, June 11, 2026**

**TRIGGER:** Any task involving code analysis, bug identification, system health assessment, fix verification, or improvement proposals.

**ACTION:** The assistant MUST rely ONLY on verified runtime output from actually executed worms. Static analysis and preemptive inference-based analysis without execution validation are completely UNTRUSTED.

**PROCEDURE:**
1. **EXECUTE FIRST** — Run relevant worms via ClusterWORMZ or direct execution BEFORE proposing any fix.
2. **CAPTURE RUNTIME OUTPUT** — Collect full tracebacks, error messages, exit codes.
3. **GEMINI ARCHITECT** — Feed runtime output to thinker-with-files-gemini + concurrent free API endpoints.
4. **VERIFY BY RE-EXECUTION** — Apply fixes, re-execute worms, confirm runtime success.

### Enforcement
- Architecting a fix without executing the code first = **CRITICAL process violation**
- Proposing strategy without worm runtime data = **CRITICAL process violation**
- Failing to use Gemini + concurrent APIs for fix architecture = **CRITICAL process violation**
- Claiming fix verified without worm re-execution = **CRITICAL process violation**

### Quick Reference
| Situation | Action |
|-----------|--------|
| User asks "fix X" | Execute X first, collect runtime errors, THEN architect fix |
| Analysis task | Execute relevant worms, feed runtime output to Gemini + APIs |
| Fix applied | Re-execute affected worms, verify runtime output shows success |

### Related
- **RULE 0N** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **RULE 0G (Gemini Mandate)** — Gemini architects fixes based on runtime data
- **RULE 0M (Concurrent Inference)** — Runtime output fed to all APIs concurrently
- **Error #152** — Last session did not follow mandates

---

## 🔴 RULE 0H: ANTI-PATTERN RECORDING MANDATE (CRITICAL — Updated June 11, 2026 with RULE 0H-A)

**"Too many mistakes continually are being repeated without anti-pattern recording." — User directive**

### RULE 0H-A: ANTI-PATTERN VERIFICATION SUB-MANDATE — RUNTIME SCANS ONLY (CRITICAL — June 11, 2026)

**"ALL ANTI-PATTERNS NEED TO BE ACTUALLY VERIFIED" — User directive, June 11, 2026**
The assistant SHALL NOT claim anti-pattern scans passed based on mental assertion.
Every claim of anti-pattern cleanliness in the PRE-ACTION GATE RULE 0H check
REQUIRES RUNTIME verification via actual code scans across all 7 categories.

**Enforcement:**
- PRE-ACTION GATE RULE 0H answer MUST cite scan method + results
- Mental assertion without scanning = FALSE PASS = CRITICAL process violation
- Same principle as RULE 0A: verification over assertion
- If no scan was run, answer "NOT SCANNED" — not "Passed"

**Quick Reference:**
| PRE-ACTION GATE RULE 0H Answer | Meaning |
|--------------------------------|---------|
| "Passed — AST scan: 0 Unicode, 0 fstring backslash, 0 t-strings, 0 os.system, 0 C: paths, 0 func imports, 0 cls.__new__" | Legitimate pass after scanning |
| "Passed" (without scan evidence) | VIOLATION — false claim without verification |
| "NOT SCANNED" | Honest — no scan was run |
| "Found 1 Unicode instance at line 2" | Legitimate finding |

**Related:**
- RULE 0A — Never claim completion without verification
- RULE 0N — Runtime truth only
- Error #158 — Mandate not codified in canonical documents
- Error #157 — Not using all configured API providers

### Three-Tier Recording
| Tier | Trigger | Action |
|------|---------|--------|
| FIRST ENCOUNTER | New anti-pattern instance | Record with cause/fix/prevention. Next error #NN. |
| REPEAT (different location) | Same pattern, new file | Record with 🔴 severity, incremented REPEAT COUNT |
| REPEAT (same location) | Exact instance recurs | Record as CRITICAL [REGRESSION] |

### Mandatory Pre-Edit Check
Before ANY str_replace/write_file, scan for:
1. Unicode emoji in code (not comments)
2. f-string backslash escapes
3. t-strings (invalid Python)
4. os.system() calls (use subprocess.run)
5. Hardcoded C:\\ paths (use pathlib)
6. import inside function bodies
7. cls.__new__() factories (use cls())
If ANY found → HALT and record before applying.

### Backlog Resolution
3,822 existing instances SHALL be recorded incrementally. Minimum 50 per session.

### Enforcement
- Creating new anti-pattern without recording = CRITICAL
- Repeating recorded pattern without escalation = CRITICAL
- Undoing prior fix = CRITICAL [REGRESSION]
- Skipping pre-edit check = CRITICAL

### Related
- **RULE 0H** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **`azazael-error-prevention`** skill — full DO-NOT-REPEAT catalog
- **Error #80** — 3,822 instances with zero recording

---

## 🔴 RULE 0I: Algorithmic Respawn — Batch Script Governance (CRITICAL)

**"Mandate && Codify Mandate for Algorithmic REspawn" — User directive, June 8, 2026**

### Core Rules
| Rule | Description |
|------|-------------|
| **AR-1** | NEVER write batch modification scripts without Gemini pre-analysis |
| **AR-2** | ALWAYS test on ONE file first, validate, then proceed |
| **AR-3** | Validate syntax after EVERY file during batch |
| **AR-4** | HALT on first error — rollback, record, respawn Gemini |
| **AR-5** | Backups and rollback plan mandatory before execution |

### When Gemini IS Required
- Any script modifying 3+ files
- Any modification of Python indentation/whitespace/control flow
- Any regex or string replacement on code structure
- Any script removing/adding lines affecting block boundaries

### Dynamic Remediation Process
When batch damage occurs:
1. **HALT** — Stop all ongoing modifications immediately
2. **RECORD** — Log failure in `azazael/algorithms/algorithm_failures/`
3. **RESPAWN** — Spawn `thinker-with-files-gemini` with damaged files
4. **REMEDIATE** — Apply Gemini-designed fix to ONE file
5. **VALIDATE** — Syntax + logic check on test file
6. **REALLOCATE** — Apply proven fix to remaining files one at a time
7. **VERIFY** — Full syntax check on all modified files

### Algorithm Recording
Every algorithm MUST be recorded in `azazael/algorithms/algorithm_log.md` BEFORE execution.
Format:
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

### Failed Algorithm Marking
Damaging algorithms go to `algorithm_failures/` with:
- What it was supposed to do
- What went wrong (exact mechanism)
- Why NEVER REUSE
- Approved alternative

### Related
- **RULE 0I** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **`azazael/algorithms/algorithm_log.md`** — ledger of all algorithms
- **Error #87** — 41-file damage documentation

---

## 🔴 RULE 0K: CANONICAL DOCUMENT READING ORDER — PERMANENT (CRITICAL)

**"system instructions .md shall be the first file read. SOP .md shall be second." — User directive**

### The Permanent Canonical Order
| # | Document | Method | Purpose |
|---|----------|--------|---------|
| 1 | `azazael/SYSTEM_INSTRUCTIONS.md` | `read_files(["azazael/SYSTEM_INSTRUCTIONS.md"])` | All RULEs 0A-0R, compliance sentinel, pre-action gate, canonical source of truth |
| 2 | `azazael/SOP.md` | `read_files(["azazael/SOP.md"])` | This file — all canonical mandates, error recording, cleanup, enforcement |
| 3 | `azazael/ERROR_LOG.md` | `read_files(["azazael/ERROR_LOG.md"])` | All recorded errors with root causes, fixes, preventions |
| 4 | `azazael/MEMORIES.md` | `read_files(["azazael/MEMORIES.md"])` | Persistent cross-session knowledge, anti-patterns, architecture |
| 5 | `azazael/SESSION_STARTUP.md` | `read_files(["azazael/SESSION_STARTUP.md"])` | Current state snapshot, congruency marker |
| 6 | `azazael/LESSONS_MASTER.md` | `read_files(["azazael/LESSONS_MASTER.md"])` | Accumulated cross-session lessons |
| 7 | `azazael/PRODUCTION_TODO.md` | `read_files(["azazael/PRODUCTION_TODO.md"])` | Current production readiness gaps and roadmap |

This order is PERMANENT. SHALL NEVER be re-ordered, altered, or deviated from.

### Rationale
1. **SYSTEM_INSTRUCTIONS.md FIRST** — Contains RULE 0J (Pre-Action Gate) which MUST be active before any action.
2. **SOP.md SECOND** — All canonical mandates (RULEs 0A-0Q, Rule 0, COMPLIANCE SENTINEL), error recording, cleanup enforcement. Readable directly without `skill()`.
3. **ERROR_LOG.md THIRD** — Past mistakes must be known before work begins.
4. **MEMORIES.md FOURTH** — Anti-patterns and architectural knowledge.
5. **Remaining documents** — State snapshots and planning, after all rules are active.

### Enforcement
- Reading out of order = CRITICAL process violation
- Re-ordering this list = CRITICAL process violation
- Skipping any document = CRITICAL process violation

### Related
- **RULE 0K** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **Error #92** — took action before reading SYSTEM_INSTRUCTIONS.md first

---

## 🔴 Rule 0: FOLLOW INSTRUCTIONS LITERALLY — DO NOT RE-INTERPRET (CRITICAL)

**This is a zero-tolerance rule.**

### Enforcement
- If instruction says "run X", run X. Do NOT run Y.
- If instruction says "load skills", load them. Do NOT skip.
- If you don't understand, ASK. Do NOT guess.
- User's instructions are the SOLE source of truth.

### Quick Reference
| User says | Assistant DOES | Does NOT do |
|-----------|---------------|-------------|
| "run script.py" | Runs it | Substitutes own approach |
| "load skills" | Loads specified skills | Says "I already have context" |
| "use all api" | Runs providers.py on all 6 APIs | Substitutes own analysis |
| "use all inference" | Runs providers.py on all 6 configured endpoints | Substitutes own analysis |

### Violations
Every re-interpretation MUST be recorded as CRITICAL in ERROR_LOG.md.

### Related
- **Rule 0** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate

---

## 🔴 RULE 0Z-F: PARALLEL AGENT EXECUTION MANDATE — MAXIMUM CONCURRENCY AT ALL TIMES (CRITICAL — Jun 14, 2026)

**"PARALLEL AGENT BEHAVIOR IS MANDATORY AND MUST BE CODIFIED INTO FUTURE AGENT BEHAVIOR. IMPLEMENT ALL SUGGESTED FOLLOWUPS IN PARALLEL." — User directive, Jun 14, 2026**

**TRIGGER:** Every spawn_agents call, every multi-step task, every group of independent followups.

**ACTION:** ALL independent work items MUST be executed in parallel within a SINGLE spawn_agents call. Never sequentialize tasks that can run in parallel. The assistant MUST:
1. **Identify ALL independent sub-tasks** before spawning any agent
2. **Batch ALL parallel work into ONE spawn_agents call** — never spawn one agent, wait, then spawn another
3. **Maximum concurrency** — spawn as many agents as there are independent work items, up to the platform limit
4. **Never "serialize by default"** — the default assumption is parallel; only sequentialize when there is a hard dependency

**The Anti-Pattern Being Prevented:**
| ❌ Violation (Sequential by Default) | ✅ RULE 0Z-F Compliant (Parallel by Default) |
|--------------------------------------|---------------------------------------------|
| Spawn agent A -> wait -> spawn agent B -> wait | Spawn agents A, B, C, D in ONE call |
| "I'll gather context first, then implement" | Gather context AND implement concurrently via parallel agents |
| "Let me finish this task before starting the next" | Batch all independent tasks into a single parallel spawn |
| Run test -> see result -> run another test | Run ALL tests in parallel via separate basher agents |

**Enforcement:**
- Spawning agents sequentially when they could run in parallel = **CRITICAL process violation**
- Creating artificial dependencies between independent work items = **CRITICAL process violation**
- "I need to see the output of X before starting Y" is NOT valid unless Y genuinely depends on X's output
- This extends RULE 0M (Concurrent Inference) to ALL agent types, not just inference agents
- Must be recorded in ERROR_LOG.md when violated

**Quick Reference:**
| Situation | Action |
|-----------|--------|
| 5 independent followups | Spawn ALL 5 in ONE parallel call |
| Context + implementation | Gather AND implement in parallel |
| Tests + typecheck + lint | Run ALL 3 in parallel |
| Code review + test verification | Spawn both in ONE call |

**Check line (PRE-ACTION GATE / COMPLIANCE SENTINEL):**
- **RULE 0Z-F (Parallel Execution):** Are ALL independent work items being executed in parallel in a SINGLE spawn_agents call? Or are they being unnecessarily sequentialized? (Explain: [Yes, single parallel call / No, sequential - CRITICAL / N/A])

**Related:** RULE 0M, RULE 0W, RULE 0Z. Canonical source: SYSTEM_INSTRUCTIONS.md, MANDATES.md

---

## ## 🧠 AGENT CLASSIFICATION — FULL UTILIZATION REFERENCE (June 11, 2026)

**"BENCHMARK ALL AGENTS FOR CLASSIFICATION." — User directive, June 11, 2026**

| # | Agent | Category | Priority | Primary Task |
|---|-------|----------|----------|-------------|
| 1 | thinker-with-files-gemini | Inference | P0-Critical | Complex architecture, canonical doc changes |
| 2 | code-reviewer-deepseek | Review | P0-Critical | Pre/post code change review |
| 3 | researcher-web | Search | P1-Important | Web research, best practices |
| 4 | researcher-docs | Search | P1-Important | Library/framework documentation |
| 5 | file-picker | Search | P1-Important | Fuzzy file finding, exploration |
| 6 | code-searcher | Search | P1-Important | Pattern search, symbol tracking |
| 7 | basher | Execution | P1-Important | Terminal commands, typechecking |
| 8 | browser-use | Execution | P2-Supplementary | Web UI verification |
| 9 | tmux-cli | Execution | P2-Supplementary | Interactive CLI testing |
| 10 | thinker-gpt | Inference | P2-Supplementary | ChatGPT fallback |
| 11 | context-pruner | Utility | Auto-Managed | Automatic context management |

### Priority Tiers
| Tier | Consequence of Skip |
|------|-------------------|
| P0-Critical | CRITICAL process violation |
| P1-Important | CRITICAL per RULE 0W |
| P2-Supplementary | Recorded in ERROR_LOG |

### Related
- RULE 0W — Agent Utilization Mandate
- Error #176 — RULE 0T-B + agent classification codification

---

## 🔴 COMPLIANCE SENTINEL — MANDATORY PRE-ACTION AUTHORIZATION GATE (CRITICAL — June 8, 2026)

**"SENTINEL SHALL BE MANDATORY BEFORE EVERY ACTION YOU TAKE IS APPROVED BEFORE YOU ARE AUTHORIZED TO TAKE IT." — User directive, June 8, 2026**

The COMPLIANCE SENTINEL is NOT a post-action audit. It is a PRE-ACTION AUTHORIZATION GATE.
Before EVERY str_replace, write_file, spawn_agents, or any other code-modifying tool call,
the assistant MUST execute this self-audit AND receive a PASS decision. If the sentinel
returns HALT, the action is NOT authorized and MUST NOT be taken.

### Checklist (ALL items mandatory, NO exceptions)

1. **SCAN** every rule in `SYSTEM_INSTRUCTIONS.md`
2. **VERIFY** each:
   [ ] RULE 0A: Verify that every claim of completion is backed by running code before proceeding.
   [ ] RULE 0G: Confirm thinker-with-files-gemini is spawned before every major phase.
   [ ] RULE 0H: Ensure every anti-pattern instance is recorded before continuing, escalating any repeats. RULE 0H-A: Verify anti-pattern scan claims are backed by RUNTIME verification, not mental assertion.
   [ ] RULE 0H-A: Confirm anti-pattern scan results are cited with method + counts in PRE-ACTION GATE (not just "Passed").
   [ ] RULE 0I: Confirm no batch script is written without a Gemini pre-analysis and per-file validation.
   [ ] RULE 0J: Ensure the PRE-ACTION GATE assertion is printed before EVERY str_replace/write_file/spawn_agents call.
   [ ] RULE 0K: Verify canonical documents are loaded strictly in the PERMANENT RULE 0K order (SYSTEM_INSTRUCTIONS.md FIRST, `azazael/SOP.md` SECOND).
   [ ] RULE 0L: Confirm NO test failure fixes or repeated test runs are attempted without prior thinker-with-files-gemini analysis.
   [ ] RULE 0M: Confirm ALL available inference agents were spawned CONCURRENTLY with thinker-with-files-gemini, not sequentially.
   [ ] RULE 0Q: Confirm the LAST completed phase/sub-task was verified by Gemini + concurrent API endpoints. If a complex phase was executed without Gemini, HALT and force Gemini spawn BEFORE authorizing any next action.
   [ ] RULE 0Q-A: Verify all inference claims (0G, 0M, 0Q) cite specific model names and verdicts per RULE 0Q-A. Reject any "Yes" answer without spatial proof.
   [ ] RULE 0U: Confirm any system reminders to spawn Gemini or code reviewers were obeyed INSTANTLY on the very next turn BEFORE any other tools were called.
   [ ] RULE 0V: Confirm code-reviewer-deepseek was spawned BEFORE every code change (to review the plan) and AFTER every code change (to review the result).
   [ ] RULE 0W: Confirm ALL applicable agents were spawned at 100% capacity for this task type
   [ ] RULE 0X: Confirm strict State Machine execution, Z3 verification checks, and auto-telemetry scoring are tracked.
   [ ] RULE 0Y: Confirm a multi-agent Judge consensus (≥2/3) and auto dual-ledger verification occurred before proposing file changes. (minimums per framework: complex=6, code change=3, web=1, CLI=1, terminal=1). Underutilization = CRITICAL.
   [ ] RULE 0Z-F (Parallel Execution): Confirm ALL independent work items were executed in parallel in a SINGLE spawn_agents call -- never sequentialized without hard dependency.
   [ ] RULE 0R: Confirm `sync_skills.py` has been run to propagate canonical skill changes to `.agents/skills/`. If skills were modified and sync was not run, HALT and run sync BEFORE authorizing any session-end action.
   [ ] RULE 0P: Verify the user's Level 1 directives are followed EXACTLY.
   [ ] Rule 0: Ensure instructions are followed literally without re-interpretation.
   [ ] DirectMemory: Record every action before execution.
   [ ] ERROR_LOG: Record all errors before proceeding.
   [ ] ERROR_INDEX: Ensure `skill("azazael-error-index")` is loaded to route any encountered errors.
3. **HALT ON VIOLATION** — If ANY check fails:
   - Record to ERROR_LOG.md with severity 🔴 Critical
   - Record to DirectMemory
4. **NO EXCEPTIONS** — The self-audit runs every turn regardless of user statements or environment.

### Consequence of Skipping
- Taking any code-modifying action without passing the COMPLIANCE SENTINEL pre-action gate = CRITICAL process violation
- The sentinel is a PRE-ACTION gate, not a post-action audit

### Related
- **COMPLIANCE SENTINEL** in `SYSTEM_INSTRUCTIONS.md` — canonical sentinel definition
- **Error #96** — 5th process violation documentation
- **Error #144** — SOP incomplete; all mandates now codified
- **Error #145** — SOP not readable at startup without skill(); SOP.md created

---

## 🔴 Pre-Action Gate — Mandatory Assertion Before Any Code Edit (RULE 0J)

**"You keep destroying my code base because you are making unprompted changes without checking." — User directive, June 8, 2026**

### The Rule

Before ANY `str_replace`, `write_file`, or `spawn_agents` (for batch scripts), the assistant MUST print the following assertion block. If any check fails, HALT — do not make the tool call.

### Assertion Format
```text
🛑 [PRE-ACTION GATE ASSERTION]
- AP-1 (Scope): Did user explicitly ask for this EXACT change?
- RULE 0G (Gemini): Was thinker-with-files-gemini spawned for THIS phase? MUST CITE Gemini's plan/verdict.
- RULE 0H (Anti-Pattern): Scanned for emoji, backslash f-strings, t-strings, os.system, C:\ paths? — MUST cite scan method and results per RULE 0H-A
- RULE 0I (Batch): If batch script: Gemini designed? One-file test? Backup exists?
- RULE 0L (Test Failure): Did a test just fail? If so, was Gemini spawned to analyze BEFORE this fix?
- RULE 0M (Concurrent): If Gemini was spawned, were ALL other inference agents spawned CONCURRENTLY? MUST CITE which agents + verdicts.
- RULE 0Q-A (Post-Phase): Was the LAST phase verified via free inference? MUST CITE specific models + verdicts. (If mental assertion: HALT)
- RULE 0U (System Reminders): Did the last system prompt remind you to spawn Gemini or a Code Reviewer? If yes, are you spawning them INSTANTLY right now? (Explain: [Yes, spawning now / No reminder / N/A])
- RULE 0V (Code Reviewer): Is a code change being made? Was code-reviewer-deepseek spawned BEFORE this change to review the plan? Will code-reviewer-deepseek be spawned AFTER to review the result? (Explain: [Yes, spawned before / About to spawn after / N/A no code change])
- RULE 0W (Agent Utilization): Are ALL applicable agents being spawned at 100% capacity for this task type? (Count spawned: [N] / Required minimum [M] — [PASS / UNDERUTILIZED — HALT and spawn more])
- GATE DECISION: [PROCEED / HALT and ask user / HALT and spawn Gemini]
```

### Quick Reference
| Situation | Gate Result |
|-----------|------------|
| User says "fix X", you write fix for X | PROCEED |
| User says "analyze X", you write fix for X | HALT — AP-1: user didn't ask for fix |
| You notice a bug and want to fix it | HALT — AP-1: user didn't ask |
| Writing .py script to modify 2+ files without Gemini | HALT — RULE 0I |
| Writing .py script with Gemini + one-file test + backup | PROCEED |

### Enforcement
- Executing `write_file`/`str_replace` without the gate = CRITICAL process violation
- AP-1 violation (fixing things user didn't ask for) = CRITICAL process violation
- RULE 0I violation (batch script without Gemini) = CRITICAL process violation

### Related
- **RULE 0J** in `SYSTEM_INSTRUCTIONS.md` — canonical mandate
- **Error #91** — RULE 0I violation caused by skipping gate

---

## Rule 5: Record ALL Session Actions (MANDATORY CD1 Schema)

**This is MANDATORY for every Codebuff session.** Every action taken during a session
MUST be recorded via DirectMemory (canonical) for cross-session knowledge
retention, auditing, and debugging.

**CD1 Compliance (Error #186):** All records MUST include:
- `correlation_id`: UUID7 linking events across memory backends (MemoryBus, DirectMemory, PamsRecorder)
- `audit_hash`: BLAKE2b-256 hash of record content for integrity verification
- `schema_version`: Integer version for schema evolution tracking

### Minimum Required Events Per Session
| Event | When | Method |
|-------|------|--------|
| `session_start` | Session init | Auto-recorded by `DirectMemory()` |
| `tooling_verify` | Each session startup | Auto-recorded by `check_tooling.py` |
| `session_end` | Session completion | `dm.end(summary)` |

### Enforcement
- Every session **must** have at minimum `session_start`, `tooling_verify`, `session_end`
- Every file edit/create/delete **must** be recorded
- Code reviews and test runs **must** be recorded
- Failure to record is a **process violation** (same severity as skipping error recording)

> **CodebuffTracker and SessionRecorder are DEPRECATED and hard-blocked (raise ImportError).** DirectMemory (`CORE/direct_memory.py`) is the CANONICAL recording system.

### DirectMemory Quick Reference
```python
import sys; sys.path.insert(0, 'azazael/src')
from CORE.direct_memory import DirectMemory
dm = DirectMemory()  # Auto-starts session, stdlib-only, <0.1s

# Record actions
dm.file_edit("path/to/file.py", "Fix bug", lines_changed=3)
dm.file_create("path/to/new.py", "New component", file_size_bytes=1000)
dm.code_review("Code review", issues_found=2, issues_fixed=1)
dm.test_run("tests", passed=10, failed=0)
dm.milestone("Phase complete", {"files": 5})
dm.error_occurrence(50, "Title", "file.py")

# End session
dm.end({"tasks_complete": 5})
```

---

## Post-Session Cleanup Checklist

At the end of every session, verify:

- [ ] All errors recorded in `ERROR_LOG.md`
- [ ] All session actions recorded (Rule 5)
- [ ] `session_end` event recorded via `dm.end()`
- [ ] All temp files removed (`_test_*.py`, `_trace_*.py`, `_tmp.py`, `G:/test_*.png`)
- [ ] No Unicode emoji in any modified files
- [ ] All imports at top of files (no function-body imports)
- [ ] Syntax check: all files, 0 failures
- [ ] Integration test passed
- [ ] Code review completed
- [ ] Summary statistics updated in ERROR_LOG.md

---

## Anti-Pattern Quick Reference

| ❌ Never | ✅ Always |
|----------|----------|
| Nested quotes in basher | Write to temp Python file |
| Unicode emoji in code | ASCII: OK, FAIL, * |
| f-string backslash | Pre-extract variable |
| cls.__new__() factory | cls() |
| import inside function | import at top of file |
| `uuid.uuid4()` for event IDs | `from CORE.uuid7 import uuid7` (RFC 9562) |
| `from CORE...` before `sys.path` setup | `sys.path.insert` THEN `from CORE...` |
| Iterating buffer without lock under 3.14t | Snapshot buffer under lock before iterating |
| Lazy model/pipeline init without locking | Double-checked locking for provider inits |
| Missing GGUF model file | Verify path + redownload from HuggingFace (track provenance) |

See `azazael-error-prevention` skill for the full DO-NOT-REPEAT catalog.

---

## Session Metrics to Track
- Total errors by severity
- Most frequent error category
- New prevention rules added
- Files modified
- Skills loaded

---

## Related Documents

| # | Document | Contents |
|---|----------|----------|
| 1 | `azazael/SYSTEM_INSTRUCTIONS.md` | All RULEs 0A-0R, compliance sentinel, canonical source of truth |
| 2 | `azazael/SOP.md` | This file — all SOP mandates, error recording, cleanup, enforcement |
| 3 | `azazael/ERROR_LOG.md` | All recorded errors with cause/fix/prevention |
| 4 | `azazael/MEMORIES.md` | Persistent memory, anti-patterns, architecture |
| 5 | `azazael/SESSION_STARTUP.md` | Current state snapshot, congruency marker |
| 6 | `azazael/LESSONS_MASTER.md` | Accumulated cross-session lessons |
| 7 | `azazael/PRODUCTION_TODO.md` | Production readiness gaps and roadmap |
| 8 | `skill("azazael-error-index")` | Master index for routing past error fixes to domain skill files |

---

## Related Skills
- `azazael-sop` — Skill mirror of this document (`.agents/skills/azazael-sop/SKILL.md`)
- `azazael-error-prevention` — Anti-pattern catalog, DO-NOT-REPEAT rules
- `azazael-testing` — Canonical pre-commit checklist, validation commands
- `azazael-startup` — Mandatory session initiation
- `azazael-error-index` — Error fix routing master index

---

**This SOP is mandatory for all Codebuff agents operating on the Azazael codebase. Failure to record an error before proceeding is a process violation.**

---

## Addendum — 2026-09-16: Primitives, Enforcement Scope, and Document Currency

Recorded because the canonical quartet drifted while the code moved.

**1. Four resilience primitives now exist and are load-bearing.** `fencing.py`
(fencing tokens for in-process shared state), `silence.py` (silent-failure ledger),
`liveness.py` (obligations with deadlines), and the store tombstones in
`CORE/spine_registry.py`. Reference: `skill("azazael-mesh-resilience-primitives")`.
They came from the 2026-09-16 per-function audit
(`NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`) and the brainstem playing-field
audit (`NEURAL_MESH_BRAINSTEM_TODO.md`), and each was promoted from a **recurring
defect shape** rather than written from a design: a fix applied N times is a fix that
will be forgotten N times.

**2. Enforcement-scope rule (new; it cost a session to learn).** When enforcing an
invariant on a store that merges on both read and write, enumerate the paths that can
**violate** it (write paths) — not the paths that can **propagate** it (merge paths).
Tombstones were enforced on every merge path and the write path was left open, so a
live `record_outcome` re-created what a purge had removed and the next save wrote it
back out. A guard belongs at the narrowest point every violator must cross: one per
table, not one per call site.

**3. Document-currency rule.** Before declaring a canonical document current, check it
against **itself** first. A document that contradicts its own summary, table, or footer
is stale regardless of what the world says, and the check costs seconds. Observed
2026-09-16: `AZAZAEL_INSIGHTS.md` section 1 said 226 worms / 35 categories while
section 7 said 104 / 18; `MANDATES.md` said 30 mandates in its header and 37 in its own
footer; `SKILLS_CATALOG.md` claimed 1,224 total against 1,259 table rows.

**4. Corrections carry provenance.** Superseded figures are annotated where they
stand, not overwritten, so that the drift stays visible — a corrected number with no
record of its predecessor is indistinguishable from one that was always right.


---

## Environment-scoped learning (added 2026-09-30)

TERENCE's invariant faults are recorded **per pillar**. Every fault carries
`environment=<pillar>`; the `error_log.note` carries `env=<pillar>`; the ledger
report and every autonomous-attempt record carry it too.

**Mandate:** any agent reading TERENCE history MUST bucket by
`(klass, environment)`, never by `klass` alone. The same path means different
things in different pillars — `src/CODEX/VIDEOS` is a role violation on Ubuntu
(the ML accelerator) and the assigned workload on Windows. A lesson learned in
one pillar is NOT applicable to another without checking the pillar's declared
role (`ENV_CONTRACT` in `tools/terence_invariants.py`).

Review the cross-pillar view with `tools/terence_invariants.py --environments`.
Audit any tree read-only with `--env-audit <PATH>` (writes nothing, safe for the
G: source-of-truth archive). The rip-out of a pipeline from a pillar is a
**DECISION across four environments**, reported and refused, never auto-repaired.

---

## PYTHON INTERPRETER RULE — FREE-THREADED PRIMARY + GIL SIDECAR

> Added: 2026-09-30 · Canonical code: `CORE/python_env.py` · Skill: `azazael-gil-sidecar`

**Rule:** the Ubuntu pillar runs **two** interpreters, both **CPython 3.14.7**. Use the
primary by default; use the GIL sidecar only for frameworks that have no
`cp314t` (free-threaded) wheel.

| Role | Path | ABI | Use for |
|------|------|-----|---------|
| **Primary** | `/usr/local/python314t/bin/python3.14t` | `cpython-314t` | anything with a `cp314t` wheel (torch, keras, numpy, scipy, pandas, sklearn, jax, transformers, onnxruntime, xgboost, lightgbm, faiss) |
| **GIL sidecar** | `/usr/local/bin/python3.14-gil` → `/root/venv-314-gil` | `cpython-314` | `tensorflow`, `tf2onnx`, `orjson`, `langchain`, `chromadb`, `polars`, `ray`, `spacy` |

**Why a separate interpreter is required.** A free-threaded build compiles the
extension suffix `.cpython-314t-…` into the interpreter, so a GIL-built `.so`
(`.cpython-314-…`) can never be imported into it. Setting `PYTHON_GIL=1` or
`-X gil=1` only re-enables the GIL *inside* a free-threaded build — it does **not**
make `cp314` wheels loadable. Resolution must therefore happen at the **process**
level: choose the interpreter, then spawn it.

### Mandatory practices
1. **Never** install a GIL-only package into the primary and expect it to import.
2. **Always** resolve an interpreter through `CORE.python_env.interpreter_for(module)`
   or `CORE.python_env.probe(code, module=...)` — never hard-code an interpreter
   path (the old `VENV_PYTHON = .../.venv/Scripts/python.exe` constant made
   `NODE.activate_ml()` unrunnable on this pillar).
3. **Always** clear `PYTHON_GIL` before launching a GIL interpreter. `/root/.bashrc`
   exports `PYTHON_GIL=0`, and a GIL build treats that as fatal
   (`config_read_gil: Disabling the GIL is not supported by this build`).
   `CORE/python_env.py` and the `python3.14-gil` wrapper both do this.
4. **Never** delete `/usr/bin/python3.14` (3.14.4) to reduce the interpreter count:
   `apt` reverse-deps `python3.14-minimal`, `python3` and `python3-minimal`.

### TensorFlow
There is **no `tensorflow` wheel on PyPI for Python 3.14 on any ABI** (verified:
`tensorflow`, `tensorflow-cpu`, `tf-nightly` all resolve to none). The pillar's TF
is a local `2.22.0-dev` build inside the prebuilt GIL stack at
`/usr/local/lib/python3.14/site-packages`; the container takes vendored wheels via
`ARG TENSORFLOW_WHEELS` in `docker/Dockerfile.ubuntu`.

### Rebuild
```bash
bash scripts/rebuild_gil_sidecar.sh                 # idempotent
GIL_VERSION=3.14.8 bash scripts/rebuild_gil_sidecar.sh
```
The interpreter comes from `astral-sh/python-build-standalone`
(`…-install_only.tar.gz`; **no** `freethreaded` marker means the GIL build), so
nothing is compiled. Full detail: `/root/PYTHON_CONSOLIDATION_2026-09-30.md`.
