---
name: azazael-inference-protocol
description: Inference Protocol (RULE 0D/0Z-A) — 12-provider automatic failover chain, auto-fallback procedure when thinker-gpt unavailable, providers.py usage patterns.
metadata:
  category: process
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael Inference Protocol — 12-Provider Failover

> **Canonical source:** `SYSTEM_INSTRUCTIONS.md` (RULE 0D, RULE 0Z-A)
> **Implementation:** `src/CORE/inference/`, `src/CORE/inference/providers.py`

---

## RULE 0D: Quota Jail — Automatic Provider Failover

When ANY inference provider fails, MUST IMMEDIATELY fall through to the next
working provider. No manual intervention. No waiting for permission.

### Automatic Failover Order

Groq → OpenRouter → NVIDIA NIM → Mistral → GitHub → HuggingFace → Cloudflare → SiliconFlow → Zhipu AI → Cohere → (any additional configured endpoints)

### Failover Procedure

1. **ATTEMPT** primary provider
2. **ON FAILURE** (429/402/404/timeout/any error):
   - Record to DirectMemory IMMEDIATELY
   - Try next provider in order
   - Keep trying until one succeeds or ALL fail
3. **IF ALL FAIL**: report raw errors to user — do NOT substitute with own analysis
4. **MANDATORY**: Do NOT block. Do NOT wait. Do NOT ask permission.

## RULE 0Z-A: Auto-Fallback (When thinker-gpt Unavailable)

### Trigger

`thinker-gpt` returns "ChatGPT OAuth credentials unavailable" or any error
indicating OAuth is not connected.

### Action

MUST IMMEDIATELY execute fallback before any other work on the sub-task.

### Fast Path (3 providers) — Quick sub-tasks

```python
python -c "
import sys; sys.path.insert(0, 'src')
from CORE.inference import providers
for name in ['groq', 'mistral', 'openrouter']:
    p = providers.get_provider(name)
    print(f'{name}: {\"OK\" if p else \"FAIL\"}')"
```

### Full Path (12 providers) — Complex tasks (3+ steps, canonical doc changes)

Query ALL 12 providers: Groq, NVIDIA NIM, Mistral, OpenRouter, Gemini, Cerebras,
GitHub, HuggingFace, Cloudflare, SiliconFlow, Zhipu, Cohere

### Auto-Fallback Procedure

1. **PAUSE** — Stop all work on the current sub-task
2. **QUERY** — Run fast path (3) or full path (12) depending on task complexity
3. **COLLECT** — Capture fallback responses
4. **SYNTHESIZE** — Use responses in place of thinker-gpt analysis
5. **RECORD** — Log to DirectMemory:
   ```python
   dm.record("thinker_gpt_fallback", {"models_queried": [...], "status": "completed"})
   ```
6. **PROCEED** — Only after fallback responses received

## Quick Reference

| Situation | Action |
|-----------|--------|
| Primary provider returns 429/402/404 | Fail over to next provider in order |
| thinker-gpt OAuth unavailable | Execute auto-fallback immediately |
| Task is quick (<3 steps) | Fast path: Groq + Mistral + OpenRouter |
| Task is complex (3+ steps, canonical docs) | Full path: ALL 12 providers |
| ALL providers fail | Report raw errors to user — do NOT substitute own analysis |

## Enforcement

| Violation | Severity |
|-----------|:--------:|
| Blocking/waiting instead of failing over | 🔴 CRITICAL |
| Skipping auto-fallback when thinker-gpt unavailable | 🔴 CRITICAL |
| Substituting own analysis for fallback models | 🔴 CRITICAL |
| Reporting "all failed" without trying all providers | 🔴 CRITICAL |

## Related Skills

- `azazael-6api-analysis` — 6-API analysis protocol
- `azazael-inference-providers` — Inference provider configuration
- `azazael-system-startup` — Startup inference provider initialization
