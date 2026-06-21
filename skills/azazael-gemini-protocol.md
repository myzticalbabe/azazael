# SKILL: azazael-gemini-protocol
# PURPOSE: Mandatory 10-Phase Multi-Tier Protocol Enforcement

The 6-Phase Protocol has been permanently expanded to the **10-Phase Multi-Tier Protocol** to mandate a 400% increase in Gemini-driven deep analysis. Gemini (`thinker-with-files-gemini`) is the apex architectural node. 

## Protocol Phases
**Phase 1: Pre-Analysis Deep Thinking (Gemini)** - Before gathering context, Gemini analyzes the innate user request and defines the search vectors.
**Phase 2: Context Gathering** - Fast agents (`file-picker`, `basher`, `researcher-web`) fetch data.
**Phase 3: Post-Context Synthesis (Gemini)** - Gemini synthesizes the raw context and formulates the master prompt for the 6 Inference APIs.
**Phase 4: 6-API Cross-Validation** - `providers.py` runs the prompt through Groq, OpenRouter, NIM, Mistral, GitHub, HF.
**Phase 5: Cross-Validation Synthesis (Gemini)** - Gemini performs convergence analysis on the 6 API responses and extracts the optimal unified plan.
**Phase 6: Implementation Plan Review (Gemini)** - A separate Gemini spawn strictly audits the finalized plan against `ERROR_LOG.md` and `MEMORIES.md` anti-patterns before ANY code changes occur.
**Phase 7: Implementation** - The agent makes the definitive code edits.
**Phase 8: Post-Implementation Audit (Gemini)** - Gemini reviews the `git diff` / edited files to ensure exact compliance with the plan.
**Phase 9: Verification Run** - Code execution, test running, and 6-API post-verification.
**Phase 10: Final Synthesis (Gemini)** - Gemini spawns to draft the final SOP updates, recording the precise architectural patterns injected.

**Failure to strictly follow this 10-Phase structure is a SEVERE process violation.**

## Phase Boundary Enforcement (RULE 0Q & 0Q-A)
Per the June 11 mandate codified in `SYSTEM_INSTRUCTIONS.md`:
- **RULE 0Q:** After EVERY complex phase, you must spawn Gemini + ALL concurrent free inference APIs to verify the work before advancing. 
- **RULE 0Q-A:** You cannot mentally assert "Yes" for verification. You MUST CITE specific agent names + 3-word verdict summaries.

## Gemini Unavailability Fallback Protocol

When `thinker-with-files-gemini` is NOT available in the environment, the agent MUST follow this alternative procedure for EVERY Gemini phase (1, 3, 5, 6, 8, 10):

1. **QUERY ALL MODELS** — Send the phase's prompt to ALL configured inference providers via `providers.py` (Groq, OpenRouter, NVIDIA NIM, Mistral, GitHub, HuggingFace, and any others with valid API keys)
2. **SYNTHESIZE** — Collect all model responses, identify consensus, and use the majority recommendation as the architectural authority
3. **RECORD** — Log to DirectMemory: which models responded, how many agreed, the consensus plan
4. **NEVER SKIP** — Do not skip the phase, do not substitute your own analysis, do not query only one model

The collective inference models serve as the replacement Gemini architectural authority. Use ALL of them — not one, not some, ALL.
