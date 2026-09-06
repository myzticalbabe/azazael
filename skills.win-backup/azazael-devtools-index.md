---
name: azazael-devtools-index
description: Master index for all 7 Chrome DevTools skills. Loads the appropriate DevTools skill(s) based on trigger keywords. Use when the user asks to audit, verify, or debug any HTML project in the Azazael ecosystem.
metadata:
  category: devtools
  project: azazael
  includes:
    - azazael-devtools-console
    - azazael-devtools-elements
    - azazael-devtools-network
    - azazael-devtools-audit
    - azazael-devtools-sources
    - azazael-devtools-performance
    - azazael-devtools-coverage
---

# Azazael DevTools — Master Index

## Purpose
Route the user to the correct DevTools skill(s) based on what they're asking. Load this skill when any HTML auditing or debugging is needed, then load only the relevant sub-skills.

## Trigger → Skill Routing

| User Says | Load These Skills |
|-----------|-------------------|
| "audit HTML", "check page", "verify app" | `azazael-devtools-audit` + `azazael-devtools-console` |
| "why doesn't X render?", "broken layout", "element missing" | `azazael-devtools-elements` + `azazael-devtools-network` |
| "page is slow", "animation jank", "performance" | `azazael-devtools-performance` + `azazael-devtools-coverage` |
| "debug JS error", "script not working", "trace error" | `azazael-devtools-console` + `azazael-devtools-sources` |
| "404 error", "broken link", "resource not loading" | `azazael-devtools-network` + `azazael-devtools-console` |
| "accessibility check", "a11y audit" | `azazael-devtools-audit` |
| "check all HTML", "full audit", "CI pipeline" | All 7 skills |

## Audit Pipeline (Full)

When a full audit is requested, run this sequence:

```
1. Navigate to page → azazael-devtools-audit
2. Check console → azazael-devtools-console
3. Inspect DOM → azazael-devtools-elements
4. Verify resources → azazael-devtools-network
5. Measure performance → azazael-devtools-performance
6. Check coverage → azazael-devtools-coverage
7. Debug if errors → azazael-devtools-sources
```

## Known Issues

### Browser-Use URL Reliability
Browser-use agents sometimes navigate to wrong URLs when multiple agents are spawned in parallel. The `finalUrl` field in the agent's output is the ground truth — always check it, not the requested URL.

**Mitigation:**
- Spawn only 1-2 browser-use agents at a time
- Always verify `finalUrl` matches the requested file
- If title/content doesn't match, re-run the audit
- Prefer spawning individual browser-use agents sequentially for critical audits

### file:// Protocol Constraint
Chrome blocks external CDN resources on `file://` pages. See `azazael-devtools-network` for the full constraint list and workarounds.

## Priority Files (By Audit Frequency)

| Priority | File | Audit Cadence |
|----------|------|---------------|
| P1 | `AZAZAEL_Standalone/index.html` | Every session |
| P1 | `dashboard/index.html` | Every session |
| P1 | `ULTIMATE_SELECTOR.html` | Every session |
| P1 | `MultiModel_1Click_Launcher.html` | Every session |
| P2 | `MERMAID_GRAPHS.html` | Weekly |
| P2 | `CINEMATIC_SCROLL.html` | Weekly |
| P2 | `INTERACTIVE_GUIDE.html` | Weekly |
| P2 | `CODEX/CAPABILITIES/*.html` | Weekly |
| P3 | All other HTML files | On modification only |

## Related Skills
- `azazael-startup` — Load before any Azazael session
- `azazael-conventions` — Python coding conventions
