---
name: azazael-devtools-console
description: Chrome DevTools Console panel — JavaScript error detection, console.log inspection, runtime evaluation. Load when auditing HTML apps for JS errors or debugging browser-side code.
metadata:
  category: devtools
  project: azazael
  cdp_domain: Runtime, Console
---

# Azazael DevTools — Console Panel

## Purpose
Use Chrome DevTools Console to detect JavaScript errors, inspect runtime state, and evaluate code in any HTML project across the Azazael ecosystem (192 HTML files).

## CDP Domains: `Runtime` + `Console`

## Common Audit Commands

### 1. Check Console Errors
```
browser-use prompt: "Navigate to <url>, wait 3 seconds, check console for errors"
```
The browser-use agent automatically reports `consoleErrors` in its output.

### 2. Evaluate JavaScript in Page Context
```
browser-use prompt: "Navigate to <url> and execute: JSON.stringify(Object.keys(window).filter(k => k.startsWith('azazael')))"
```

### 3. Check for Missing Dependencies
```
browser-use prompt: "Navigate to <url>, check console for 404 errors or failed resource loads"
```

### 4. Test Interactive Elements
```
browser-use prompt: "Navigate to <url>, click all tier filter buttons, verify no console errors after each click"
```

## Audit Checklist for Every HTML File
- [ ] Zero console errors on page load
- [ ] Zero console errors after clicking all interactive elements
- [ ] No deprecated API warnings
- [ ] No CORS errors on local file:// resources
- [ ] All `console.log()` calls are intentional (not debug leftovers)

## Target Files (Priority)
| File | Purpose | Console Check |
|------|---------|---------------|
| `AZAZAEL_Standalone/index.html` | 52-app launcher | Tier filter clicks |
| `dashboard/index.html` | Live observability | Live data refresh |
| `src/CODEX/CAPABILITIES/*.html` | 10 capability modules | Tab/section switching |
| `MERMAID_GRAPHS.html` | 10 diagram types | Diagram rendering |
| `ULTIMATE_SELECTOR.html` | Card grid launcher | Card hover/click |

## Common Console Errors & Fixes
| Error | Cause | Fix |
|-------|-------|-----|
| `ReferenceError: X is not defined` | Missing script or typo | Add missing `<script>` or fix variable name |
| `Failed to load resource: file:///...` | Broken relative path | Use relative paths from HTML location |
| `TypeError: Cannot read properties of null` | Element not in DOM yet | Wrap in `DOMContentLoaded` or move script to bottom |
| `Uncaught SyntaxError` | JS syntax error in inline script | Fix syntax, escape template literals |

## Related Skills
- `azazael-devtools-elements` — DOM inspection for broken selectors
- `azazael-devtools-network` — Resource loading diagnostics
- `azazael-devtools-audit` — Lighthouse comprehensive audit
