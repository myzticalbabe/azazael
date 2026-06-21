---
name: azazael-devtools-audit
description: Chrome DevTools Lighthouse — performance, accessibility, SEO, best practices auditing. Load when running comprehensive quality audits on HTML projects or CI verification.
metadata:
  category: devtools
  project: azazael
  cdp_domain: Page, Target, Emulation
---

# Azazael DevTools — Audit (Lighthouse)

## Purpose
Run comprehensive Lighthouse audits on all Azazael HTML projects to measure performance, accessibility, best practices, and SEO scores.

## CDP Domains: `Page` + `Target` + `Emulation`

## Common Audit Commands

### 1. Full Lighthouse Audit
```
browser-use prompt: "Navigate to <url>, run a full audit checking for: console errors, broken elements, accessibility issues, slow rendering"
```

### 2. Accessibility Check
```
browser-use prompt: "Navigate to <url>, verify: all images have alt text, all buttons have labels, color contrast meets WCAG AA, all interactive elements are keyboard-accessible"
```

### 3. Performance Check
```
browser-use prompt: "Navigate to <url>, measure page load time, verify no render-blocking resources, check total page weight"
```

### 4. Mobile Responsiveness
```
browser-use prompt: "Navigate to <url> at mobile viewport (375x812), verify all content is visible without horizontal scroll, tap targets are > 48px"
```

## Audit Scorecard Template

For each HTML file, record:
| Metric | Target | Actual | Pass? |
|--------|--------|--------|-------|
| Console errors | 0 | | |
| Broken links | 0 | | |
| Load time | < 5s | | |
| Accessibility | No critical issues | | |
| Mobile layout | No horizontal scroll | | |
| Color contrast | WCAG AA | | |
| All buttons functional | Yes | | |

## Target Files (Priority Audit Order)

| # | File | Key Audit Focus |
|---|------|----------------|
| 1 | `AZAZAEL_Standalone/index.html` | 52 cards, tier filters, launch links |
| 2 | `dashboard/index.html` | Real-time metrics, particle canvas |
| 3 | `ULTIMATE_SELECTOR.html` | 31+ card grid, all links working |
| 4 | `src/CODEX/CAPABILITIES/*.html` | 10 modules, tab navigation |
| 5 | `MERMAID_GRAPHS.html` | 10 diagram types rendering |
| 6 | `CINEMATIC_SCROLL.html` | Parallax, animations, scroll |
| 7 | `MultiModel_1Click_Launcher.html` | Windows path fixes needed |
| 8 | Coverage reports | Table rendering, navigation |

## Post-Audit Actions
1. Fix all console errors
2. Fix all broken links
3. Add missing `alt` attributes
4. Add `aria-label` to interactive elements
5. Add `<meta name="viewport">` for mobile
6. Minify inline CSS/JS if > 10KB

## Related Skills
- `azazael-devtools-console` — JS error baseline
- `azazael-devtools-elements` — DOM structure verification
- `azazael-devtools-network` — Resource loading audit
- `azazael-devtools-performance` — Frame rate and animation audit
