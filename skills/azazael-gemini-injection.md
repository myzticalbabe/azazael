# SKILL: azazael-gemini-injection
# PURPOSE: Explicit Rules for Spawning `thinker-with-files-gemini`

Gemini (`thinker-with-files-gemini`) must be injected into the session lifecycle at minimum 4 times per complex task, ideally up to 6 times per the 10-Phase Multi-Tier Protocol. 

### Mandatory Injection Points (7 Total — Aligned with 10-Phase Protocol + RULE 0Q/0Q-A):
1. **Phase 1 — BEFORE ANY OTHER AGENT:** The absolute first cognitive step after receiving a complex user directive is to spawn Gemini. Do not search files first. Do not run researchers first. Ask Gemini to map the context-gathering strategy.
2. **Phase 3 — AFTER RAW CONTEXT, BEFORE 6-APIs:** Once `file-picker` and `basher` return results, spawn Gemini to read the files and build the prompt for `providers.py`.
3. **Phase 5 — AFTER 6-APIs, BEFORE CODE CHANGES:** When the 6 APIs (Mistral, Groq, etc.) return their analysis, they often present conflicting advice. Spawn Gemini to synthesize a singular, convergent action plan.
4. **Phase 6 — PLAN REVIEW BEFORE EDITING:** Spawn Gemini to vet the implementation plan against `ERROR_LOG.md` anti-patterns before any code is changed.
5. **Phase 8 — AFTER CODE CHANGES, BEFORE COMPLETION:** Once edits are made, spawn Gemini to review the final architectural state (Post-Implementation Audit).
6. **Phase 10 — FINAL SYNTHESIS:** Spawn Gemini to draft the final SOP/Memory updates for the session.

**Bonus Injection — DURING ERROR CONDITIONS:** If an error occurs (Syntax, CircuitBreaker, Mypy), immediately spawn Gemini with the error log before attempting a fix.

7. **Post-Phase Boundary Check (RULE 0Q & 0Q-A) — AFTER EVERY COMPLEX PHASE:** Spawn Gemini + ALL concurrent free inference APIs to verify the work before proceeding. You must prove injection by citing specific agent names + 3-word verdict summaries.

**Injection Directory:** Gemini is not just a tool; it is the orchestrator.
