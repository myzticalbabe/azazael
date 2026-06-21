# DEEP API ANALYSIS STANDARD — Mandatory Multi-Inference Analysis Protocol

> **Effective:** June 7, 2026
> **Applies to:** All Codebuff / Azazael development sessions
> **Loaded at startup via:** `skill("azazael-deep-analysis")` or direct read by assistant

---

## 🔴 RULE 0: DEEP ANALYSIS IS THE ONLY ANALYSIS

**Every analysis task MUST use ALL available inference APIs.** Single-model analysis is deprecated.
Local agents (code-reviewer-deepseek, thinker-gpt) are NOT substitutes for multi-inference
API analysis. They are complementary validation steps.

### The 5 Free Inference APIs (use in order of priority)

| # | Provider | Model | Latency | Best For |
|---|----------|-------|---------|----------|
| 1 | **Groq** | llama-3.3-70b | ~1s | Architecture, rapid iteration |
| 2 | **OpenRouter** | llama-3.3-70b | ~8s | Security, lifecycle analysis |
| 3 | **NVIDIA NIM** | llama-3.3-70b | ~30s | Performance, parallelism |
| 4 | **Mistral** | mistral-large | ~9s | Code quality, anti-patterns |
| 5 | **GitHub** | gpt-4o-mini | ~6s | Testing strategy, edge cases |

---

## 📐 DEEP ANALYSIS PROTOCOL

### Phase 1: Prepare the Prompt

For each analysis target, prepare a prompt containing:

```python
prompt = f"""
You are analyzing the Azazel AI framework. Analyze the following code deeply.
Respond with structured findings in this EXACT format:

## 1. ARCHITECTURE
- Component relationships, cohesion score (1-10), coupling issues

## 2. SECURITY
- Vulnerabilities, key exposure risks, input validation gaps

## 3. PERFORMANCE
- Bottlenecks, optimization opportunities, parallelism analysis

## 4. CODE QUALITY
- Anti-patterns, dead code, error handling gaps, thread safety

## 5. TESTING STRATEGY
- What to test, how to test, edge cases, integration points

## 6. IMPROVEMENTS (prioritized)
- Top 3 specific, actionable improvements with estimated effort

CODE TO ANALYZE:
=== {filename} ===
{content[:3000]}
"""
```

### Phase 2: Assign Analysis Angles

Each API analyzes the SAME code but from a different PRIMARY angle:

| API | Primary Angle | Secondary Angle | Prompt Directive |
|-----|--------------|-----------------|------------------|
| Groq | Architecture & Design | Improvement prioritization | "Focus on architectural patterns, cohesion, and the 3 most impactful improvements" |
| OpenRouter | Security & Lifecycle | Error handling | "Focus on security risks, key management, and the worm lifecycle" |
| NVIDIA NIM | Performance & Parallelism | Bottleneck analysis | "Focus on threading, parallelism, bottlenecks, and 3.14t optimization" |
| Mistral | Code Quality & Anti-patterns | Thread safety | "Focus on code quality, anti-patterns, thread safety, and maintainability" |
| GitHub | Testing Strategy & Edge Cases | Failover design | "Focus on what to test, edge cases, integration testing, and failover" |

### Phase 3: Execute — Send to ALL 5 APIs Sequentially

```python
from CORE.inference.providers import get_provider

providers = ["groq", "openrouter", "nvidia_nim", "mistral", "github"]
angles = {
    "groq": "Focus on architectural patterns, cohesion score, and top 3 impactful improvements.",
    "openrouter": "Focus on security risks, key management, error lifecycle, and input validation.",
    "nvidia_nim": "Focus on threading, parallelism, bottlenecks, and Python 3.14t optimization.",
    "mistral": "Focus on code quality, anti-patterns, thread safety, and maintainability.",
    "github": "Focus on testing strategy, edge cases, integration testing, and failover design.",
}

results = {}
for pid in providers:
    prov = get_provider(pid)
    full_prompt = f"{angles[pid]}\n\n{code_prompt}"
    result = prov.chat(full_prompt, max_tokens=1500)
    results[pid] = result
```

### Phase 4: Synthesize — Cross-Reference Findings

After all 5 APIs respond, synthesize:

1. **CONVERGENCE POINTS** — Issues flagged by 3+ APIs → CRITICAL priority
2. **UNIQUE INSIGHTS** — Issues flagged by only 1 API → validate separately
3. **DISAGREEMENTS** — Contradictory findings → flag for human review
4. **PRIORITY MATRIX** — Sort all findings by severity × consensus

### Phase 5: Report

Output format:

```
### 🎯 Architecture — Groq (1.2s)
**Rating: X/10**
| # | Finding | Impact |
...

### 🔒 Security — OpenRouter (8s)
| # | Risk | Mitigation |
...

### ⚡ Performance — NVIDIA NIM (30s)
| # | Bottleneck | Optimization |
...

### 📋 Code Quality — Mistral (9s)
| # | Issue | Fix |
...

### 🧪 Testing — GitHub (6s)
| # | Test | What It Validates |
...

### 🔬 CONVERGENCE (3+ APIs Agree)
| # | Finding | APIs | Priority |
...

### 📊 PRIORITY MATRIX
| Priority | Finding | Consensus | Effort |
...
```

---

## 🔄 DEEP ANALYSIS PIPELINE — STANDARD SEQUENCE

Every deep analysis task follows this sequence:

```
1. PREPARE  — Write the analysis script to a temp Python file
2. DRY RUN   — Test with 1 API (Groq) to verify prompt and connection
3. FULL RUN  — Execute all 5 APIs sequentially
4. SYNTHESIZE — Cross-reference findings for convergence
5. REPORT    — Format results using the standard template above
6. SKILL     — Create/update a skill file with the analysis results
7. RECORD    — Log to DirectMemory with all 5 API responses
```

---

## 🚨 ENFORCEMENT

| Scenario | Requirement |
|----------|------------|
| Any analysis request | Use 3+ APIs minimum |
| "deep analysis" requested | Use ALL 5 APIs, no exceptions |
| Architecture review | ALL 5 with architecture angle emphasis |
| Security audit | ALL 5 with security angle emphasis |
| Performance review | ALL 5 with performance angle emphasis |
| New module analysis | ALL 5, then create skill from synthesis |
| "use all api" | Send same prompt to ALL 5 APIs |

### What "DEEP" Analysis Is NOT

- ❌ A single code-reviewer-deepseek call
- ❌ A single thinker-gpt call
- ❌ Reading files and giving your own opinion
- ❌ Using only 1-2 inference APIs
- ❌ Skipping the cross-reference synthesis step

### What "DEEP" Analysis IS

- ✅ All 5 inference APIs receive the same code + analysis prompt
- ✅ Each API analyzes from a different primary angle
- ✅ Findings are cross-referenced for convergence (3+ APIs = critical)
- ✅ Results are formatted in the standard template
- ✅ A skill is created/updated with the synthesis
- ✅ All responses are recorded to DirectMemory

---

## 📁 Integration with System Startup

This standard is loaded at session startup via:

```python
# In SYSTEM_INSTRUCTIONS.md startup procedure
skill("azazael-deep-analysis")  # Loads this standard
```

The corresponding skill file is `azazael/skills/azazael-deep-analysis.md`.

---

## 📊 Quality Metrics

Each deep analysis session tracks:

- **APIs Used**: Count (goal: 5/5)
- **Convergence Score**: % of findings flagged by 3+ APIs
- **Unique Insights**: Count of findings flagged by exactly 1 API
- **Time to Complete**: Total analysis pipeline duration
- **Actionable Improvements**: Count of specific, implementable suggestions

---

## 🔗 Related Standards

- `SYSTEM_INSTRUCTIONS.md` — Core SOP, error recording, 3.14t rules
- `DIRECT_MEMORY_INSTRUCTIONS.md` — Session recording mandate
- `azazael/skills/azazael-system-startup.md` — Session startup procedure
- `azazael/skills/azazael-session-recording.md` — DirectMemory recording

---

**This standard is MANDATORY for all analysis tasks. Violations are PROCESS VIOLATIONS.**
