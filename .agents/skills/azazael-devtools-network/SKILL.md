---
name: azazael-devtools-network
description: Chrome DevTools Network panel — resource loading, broken links, 404 detection, MIME type verification. Load when auditing HTML apps for missing assets, slow resources, or incorrect file references.
metadata:
  category: devtools
  project: azazael
  cdp_domain: Network, Fetch
---

# Azazael DevTools — Network Panel

## Purpose
Monitor resource loading, detect broken links, verify MIME types, and audit asset delivery across all Azazael HTML projects.

## CDP Domains: `Network` + `Fetch`

## Common Audit Commands

### 1. Check All Resources Load
```
browser-use prompt: "Navigate to <url>, wait for network idle, list all failed requests (status 404, 500)"
```

### 2. Verify MIME Types
```
browser-use prompt: "Navigate to <url>, check that .html files return text/html, .css returns text/css, .js returns application/javascript"
```

### 3. Detect Slow Resources
```
browser-use prompt: "Navigate to <url>, list any resources taking > 1 second to load"
```

### 4. Audit Local File References
```
browser-use prompt: "Navigate to file:///C:/Users/clint/Desktop/AZAZAEL_Standalone/index.html, check all file:// links resolve without errors"
```

## Audit Checklist for Every HTML File
- [ ] Zero 404 errors for linked resources
- [ ] All `<link>` stylesheets load (check Network tab for failures)
- [ ] All `<script>` sources load without errors
- [ ] No mixed content warnings (http resources in file:// context)
- [ ] Font files load if custom fonts used
- [ ] Image references resolve (check for broken image icons)
- [ ] Total page load < 5 seconds for local files

## Common Network Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| 404 on .css file | Wrong relative path | Use `./styles/main.css` or absolute from HTML |
| 404 on .js file | Script src typo | Verify filename exactly matches |
| file:// protocol restrictions | Chrome blocks cross-file access | Use relative paths only |
| MIME type warning | Server serves wrong Content-Type | For local files, Chrome infers from extension |
| Slow resource | Large inline base64 or big JSON | Externalize to separate file |

## Target Files (Priority)
| File | Network Check |
|------|-------------|
| `AZAZAEL_Standalone/index.html` | All 52 .exe href links resolve |
| `dashboard/index.html` | Live data fetch endpoints |
| `MultiModel_1Click_Launcher.html` | Model path references |
| `MERMAID_GRAPHS.html` | Mermaid.js CDN or local load |

## Related Skills
- `azazael-devtools-console` — JS errors from failed script loads
- `azazael-devtools-elements` — CSS not applying due to missing stylesheets
- `azazael-devtools-audit` — Lighthouse performance audit
