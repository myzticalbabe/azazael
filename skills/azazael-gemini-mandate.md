---
name: azazael-gemini-mandate
description: Operational enforcement of Gemini spawning frequency for complex tasks.
metadata:
  category: protocol
  project: azazael
  priority: critical
  auto_load: false
---

# SKILL: azazael-gemini-mandate
# PURPOSE: Operational Enforcement of the Gemini Spawning Frequency

### The Directives:
- **"Gemini is spawned OFTEN."**
- **"Gemini is spawned FREQUENTLY."**
- **"Gemini is spawned CONSISTENTLY."**

### Operational Rules:
1. **Never aggregate too much context without Gemini.** If you have run 3 tools without spawning Gemini to analyze the output, you are flying blind. Stop and spawn Gemini.
2. **Never commit to a complex implementation without a Gemini Plan Review.** 
3. **Gemini is the designated Synthesizer.** `thinker-gpt` or `code-reviewer-deepseek` are secondary validators. Gemini MUST be the engine that merges findings from external sources, 6-APIs, and local logs.
4. **RULE 0Q (Post-Phase Inference Check):** After every complex phase, you MUST spawn Gemini + ALL concurrent free inference APIs to verify the work before proceeding to the next action.
5. **RULE 0Q-A (Inference Verification):** "Yes" is invalid. Every inference claim (0G, 0M, 0Q) MUST CITE specific agent names + 3-word verdict summaries. Mental assertion = FALSE PASS = CRITICAL.

**Enforcement:** An agent executing a session without spawning `thinker-with-files-gemini` at least 4 times has failed their prime directive. End the task, log a CRITICAL process violation in `ERROR_LOG.md`, and restart the multi-tier protocol.

**Gemini Unavailability Fallback:** When `thinker-with-files-gemini` is NOT available in the environment, the agent MUST query ALL available inference models via `providers.py` (Groq, OpenRouter, NVIDIA NIM, Mistral, GitHub, HuggingFace — all configured providers with API keys) for EVERY Gemini phase. The models collectively serve as the architectural authority. NEVER skip, NEVER substitute with manual analysis, NEVER use a single model as replacement. Query ALL of them, synthesize their responses, and record which models were used. This is NOT optional — it is the MANDATORY fallback when the primary Gemini agent is unavailable.
