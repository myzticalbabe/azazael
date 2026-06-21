---
name: azazael-devtools-sources
description: Chrome DevTools Sources panel — JavaScript debugging, breakpoints, snippet execution, source inspection. Load when debugging complex JS logic in HTML apps or troubleshooting script execution order.
metadata:
  category: devtools
  project: azazael
  cdp_domain: Debugger, Runtime, Profiler
---

# Azazael DevTools — Sources Panel

## Purpose
Debug JavaScript execution, set breakpoints, inspect source files, and troubleshoot script loading order in Azazael HTML projects.

## CDP Domains: `Debugger` + `Runtime` + `Profiler`

## Common Audit Commands

### 1. Verify Script Loading Order
```
browser-use prompt: "Navigate to <url>, list all <script> elements in load order, verify no race conditions"
```

### 2. Check for Dead Code
```
browser-use prompt: "Navigate to <url>, verify all defined functions are actually called somewhere"
```

### 3. Debug Event Handlers
```
browser-use prompt: "Navigate to <url>, verify all onclick/onchange handlers reference existing functions"
```

### 4. Inspect Inline Scripts
```
browser-use prompt: "Navigate to <url>, extract all inline scripts, check for syntax errors"
```

## Audit Checklist
- [ ] No `<script>` tags before `<body>` content (blocks render)
- [ ] All external script files load (200 OK in Network)
- [ ] No duplicate function definitions
- [ ] No use of `eval()` or `document.write()`
- [ ] All `addEventListener` calls have matching `removeEventListener` where needed

## Common Sources Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| Script runs before DOM ready | `<script>` in `<head>` | Move to `<body>` end or use `DOMContentLoaded` |
| Function not found | Script load order wrong | Reorder scripts: dependencies first |
| Inline script error | Template literal not escaped | Replace backticks with quotes or escape properly |
| `eval()` usage | Dynamic code execution | Replace with explicit function calls |

## Related Skills
- `azazael-devtools-console` — Runtime errors from script execution
- `azazael-devtools-coverage` — Unused JS detection
- `azazael-devtools-performance` — Script execution time profiling
