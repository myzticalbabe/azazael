---
name: azazael-6api-analysis
description: Multi-API convergence analysis protocol — query all 6 inference APIs (Groq, OpenRouter, NIM, Mistral, GitHub, HF) with distinct angles, synthesize convergence report, implement findings.
metadata:
  category: process
  project: azazael
  auto_load: true
---

# Azazael 6-API Analysis Protocol

## Overview
All deep analyses must query ALL 6 inference APIs (not 5) with distinct angles:

| API | Angle | Model |
|-----|-------|-------|
| Groq | Architecture patterns | llama-3.3-70b |
| OpenRouter | Training pipeline | llama-3.3-70b |
| NVIDIA NIM | Inference providers | llama-3.3-70b |
| Mistral | Evolutionary optimization | mistral-large |
| GitHub | System-level wiring | gpt-4o-mini |
| HuggingFace | Cross-validation | Llama-3.3-70B |

## Mandatory Process
1. Read ALL relevant source files
2. Build a comprehensive analysis prompt
3. Send to all 6 APIs in parallel (or sequential with 0.5s gaps)
4. Synthesize a convergence report: APIs responded, avg scores, std deviation
5. Score convergence: HIGH (< 1.5 std), MEDIUM (1.5-3.0), LOW (> 3.0)
6. Implement concrete improvements from every API's findings
7. Create new skills for each analyzed facet
8. Record everything to DirectMemory
9. Update SYSTEM_INSTRUCTIONS.md

## Gemini Deep Thinker
Always spawn `thinker-with-files-gemini` BEFORE implementing complex changes.
Pass ALL relevant filePaths. The thinker has no conversation history.

## API Key Configuration
Ensure keys are configured via env vars or `~/.azazael/{provider}_config.json`:
- GROQ_API_KEY, OPENROUTER_API_KEY, NVIDIA_NIM_API_KEY
- MISTRAL_API_KEY, GITHUB_TOKEN, HF_TOKEN
