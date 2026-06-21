---
name: azazael-devtools-elements
description: Chrome DevTools Elements panel — DOM inspection, CSS validation, layout debugging, selector verification. Load when auditing HTML structure, checking for broken selectors, or verifying element rendering.
metadata:
  category: devtools
  project: azazael
  cdp_domain: DOM, CSS
---

# Azazael DevTools — Elements Panel

## Purpose
Inspect DOM structure, verify CSS rendering, debug broken selectors, and validate element visibility across all Azazael HTML projects.

## CDP Domains: `DOM` + `CSS`

## Common Audit Commands

### 1. Verify Element Count
```
browser-use prompt: "Navigate to <url>, count all .card elements — should be 52 for standalone index"
```

### 2. Check Hidden Elements
```
browser-use prompt: "Navigate to <url>, check if any elements have display:none or visibility:hidden on page load"
```

### 3. Validate Responsive Layout
```
browser-use prompt: "Navigate to <url> at viewport 1920x1080, then resize to 768x1024 (tablet), verify the grid adapts"
```

### 4. Check Broken Selectors
```
browser-use prompt: "Navigate to <url>, click each tier button, verify the correct cards show/hide"
```

### 5. Verify CSS Custom Properties
```
browser-use prompt: "Navigate to <url>, evaluate: getComputedStyle(document.documentElement).getPropertyValue('--accent')"
```

## Audit Checklist for Every HTML File
- [ ] All tier/category filter buttons toggle correct elements
- [ ] No orphaned elements (visible but not linked)
- [ ] CSS custom properties resolve correctly (no fallback to black/white)
- [ ] Dark theme renders correctly (background, text, accent colors)
- [ ] Hover states work on interactive elements
- [ ] Grid layout doesn't break at narrow viewports
- [ ] All `<a href="">` links point to existing files (no 404)

## Common Elements Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| Cards invisible | `display:none` class not removed | Remove `.hidden` class in JS render function |
| Filter buttons not working | JS onclick references wrong function | Verify function name matches `onclick` attribute |
| Links broken | `href` points to non-existent file | Check filename case sensitivity on Windows |
| Dark theme broken | CSS variable not set | Add `:root { --bg: #0a0a14; }` fallback |
| Grid collapses | `grid-template-columns` too narrow | Add `minmax(280px, 1fr)` to prevent collapse |

## Target Files (Priority)
| File | Elements Check |
|------|---------------|
| `AZAZAEL_Standalone/index.html` | 52 cards, 7 tier buttons, launch links |
| `dashboard/index.html` | Health cards, metrics display, particle canvas |
| `src/CODEX/CAPABILITIES/*.html` | Tab panels, content sections |
| `ULTIMATE_SELECTOR.html` | 31+ card grid, category filters |

## Related Skills
- `azazael-devtools-console` — JS errors from DOM manipulation
- `azazael-devtools-audit` — Lighthouse accessibility/layout checks
- `azazael-devtools-coverage` — Unused CSS detection
