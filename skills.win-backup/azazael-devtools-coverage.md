---
name: azazael-devtools-coverage
description: Chrome DevTools Coverage panel — unused CSS/JS detection, dead code elimination, payload optimization. Load when optimizing HTML project payload sizes or cleaning up legacy code.
metadata:
  category: devtools
  project: azazael
  cdp_domain: CSS, Profiler
---

# Azazael DevTools — Coverage Panel

## Purpose
Detect unused CSS and JavaScript, identify dead code, and optimize payload sizes across Azazael HTML projects.

## CDP Domains: `CSS` + `Profiler`

## Common Audit Commands

### 1. CSS Coverage Audit
```
browser-use prompt: "Navigate to <url>, click every interactive element, then check what percentage of CSS is unused"
```

### 2. JavaScript Coverage Audit
```
browser-use prompt: "Navigate to <url>, interact with all features, then check what percentage of JS is unused"
```

### 3. Dead Selector Detection
```
browser-use prompt: "Navigate to <url>, list CSS selectors that never match any DOM element"
```

## Audit Checklist
- [ ] CSS usage > 60% in all stylesheets
- [ ] JS usage > 70% across all scripts
- [ ] No CSS selectors targeting non-existent elements
- [ ] No unused CSS custom properties
- [ ] Inline <style> blocks contain only page-specific rules

## Common Coverage Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| 80%+ CSS unused | Stylesheet shared across pages | Split into common.css + page-specific.css |
| Dead selectors | Removed elements, kept CSS | Audit after DOM changes |
| Unused JS functions | Legacy code from prior versions | Remove functions with zero call sites |
| Overly broad selectors | `*` or `div` without context | Add class or ID qualifiers |

## Target Files (Priority)
| File | Coverage Focus |
|------|---------------|
| `ULTIMATE_SELECTOR.html` | Inline styles after card template changes |
| `AZAZAEL_Standalone/index.html` | Inline CSS for 52 cards |
| `dashboard/index.html` | Particle canvas JS, metrics display |
| `src/CODEX/CAPABILITIES/*.html` | Shared vs specific styles |

## Related Skills
- `azazael-devtools-performance` — Payload size impacts load time
- `azazael-devtools-sources` — Unused JS function detection
- `azazael-devtools-elements` — Dead CSS selector detection
