---
name: azazael-agent-utilization
description: Agent Utilization Mandate (RULE 0W) — minimum agent spawns per task type, 100% capacity framework, agent classification matrix. Spawn ALL applicable agents.
metadata:
  category: process
  project: azazael
  priority: critical
  auto_load: true
---

# Azazael Agent Utilization — 100% Capacity Framework

> **Canonical source:** `azazael/SYSTEM_INSTRUCTIONS.md` (RULE 0W)
> **You are underutilizing your available agents if you spawn fewer than the minimum.**

---

## Minimum Agent Spawns Per Task Type

| Task Category | Minimum | Required Agents |
|--------------|:-------:|-----------------|
| **Code Change** (str_replace/write_file) | **3** | code-reviewer-deepseek (BEFORE) + code-reviewer-deepseek (AFTER) + basher (typecheck/tests) |
| **Complex Task** (3+ steps, logic change) | **6** | thinker-with-files-gemini + code-reviewer-deepseek + file-picker + code-searcher + researcher-web + researcher-docs |
| **Web Verification** | **1** | browser-use |
| **CLI Testing** | **1** | tmux-cli |
| **Terminal Command** | **1** | basher with what_to_summarize |
| **New Feature** (>50 lines, multi-file) | **8** | + basher + browser-use |
| **Canonical Doc Change** | **7** | + sync_skills.py + sync_all.py |

---

## Agent Classification Matrix

| # | Agent | Category | Priority | Primary Task Affinity | Speed |
|---|-------|----------|:--------:|----------------------|:-----:|
| 1 | **thinker-with-files-gemini** | Inference | P0-Critical | Complex architecture, canonical doc changes | Medium |
| 2 | **thinker-gpt** | Inference | P0-Critical | Deep thinking w/ conversation history (ChatGPT OAuth) | Medium |
| 3 | **code-reviewer-deepseek-flash** | Review | P0-Critical | Pre/post code change review, anti-pattern detection | Fast |
| 4 | **researcher-web** | Search | P1-Important | Web research, current best practices | Medium |
| 5 | **researcher-docs** | Search | P1-Important | Library/framework documentation | Medium |
| 6 | **file-picker** | Search | P1-Important | Fuzzy file finding, codebase exploration | Fast |
| 7 | **code-searcher** | Search | P1-Important | Pattern search, symbol tracking | Fast |
| 8 | **basher** | Execution | P1-Important | Terminal commands, typechecking, tests | Medium |
| 9 | **browser-use** | Execution | P2-Supplementary | Web UI verification, browser testing | Slow |
| 10 | **tmux-cli** | Execution | P2-Supplementary | Interactive CLI testing, TUI verification | Medium |
| 11 | **context-pruner** | Utility | Auto-Managed | Automatic context window management | Instant |

---

## Anti-Pattern: Single-Agent Reliance

| ❌ Underutilization (10%) | ✅ Full Utilization (100%) |
|---------------------------|---------------------------|
| Complex task: spawn Gemini only | Spawn Gemini + code-reviewer + file-picker + code-searcher + researcher-web + researcher-docs concurrently |
| Code change: edit without review | Spawn code-reviewer BEFORE editing, code-reviewer AFTER, basher for typecheck |
| Terminal command: run inline | Spawn basher with what_to_summarize |
| Web test: guess it works | Spawn browser-use to verify |
| "I already know what the files are" | Spawn file-picker + code-searcher to validate |

## Enforcement

| Violation | Severity |
|-----------|:--------:|
| Spawning fewer than minimum agents | 🔴 CRITICAL |
| Using 1-2 agents when 5-6+ applicable (10% utilization) | 🔴 CRITICAL |
| Failing to spawn file-picker + code-searcher for multi-file tasks | 🔴 CRITICAL |
| Failing to use browser-use for web verification | 🔴 CRITICAL |
| Failing to use tmux-cli for CLI testing | 🔴 CRITICAL |

## Related Skills

- `azazael-pre-action-gate` — Gate assertion includes RULE 0W check
- `azazael-sop` — SOP mirror with agent classification
- `azazael-system-startup` — Startup sequence for agent utilization
