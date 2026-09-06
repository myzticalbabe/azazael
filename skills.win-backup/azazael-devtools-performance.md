---
name: azazael-devtools-performance
description: Chrome DevTools Performance panel — frame rate, animation smoothness, layout thrashing, paint timing. Load when auditing animation-heavy HTML projects or debugging slow UI interactions.
metadata:
  category: devtools
  project: azazael
  cdp_domain: Tracing, Profiler, IO
---

# Azazael DevTools — Performance Panel

## Purpose
Profile runtime performance, measure frame rates, detect layout thrashing, and audit animation smoothness across Azazael HTML projects.

## CDP Domains: `Tracing` + `Profiler` + `IO`

## Common Audit Commands

### 1. Measure Page Load Performance
```
browser-use prompt: "Navigate to <url>, measure: Time to First Paint, DOMContentLoaded, total load time"
```

### 2. Check Animation Frame Rate
```
browser-use prompt: "Navigate to CINEMATIC_SCROLL.html, scroll slowly, measure frames per second — should be > 30fps"
```

### 3. Detect Layout Thrashing
```
browser-use prompt: "Navigate to <url>, interact with all filter buttons, verify no forced reflows (> 50ms layout operations)"
```

### 4. Memory Usage
```
browser-use prompt: "Navigate to <url>, click all interactive elements 5 times each, check for memory leaks (increasing JS heap size)"
```

## Audit Checklist
- [ ] Page load < 5 seconds on local file://
- [ ] First paint < 1 second
- [ ] Scroll animations maintain > 30fps
- [ ] No forced synchronous layouts during interaction
- [ ] JS heap size stable after repeated interactions (no leaks)
- [ ] Total page weight < 5MB (inline resources)

## Common Performance Issues & Fixes
| Issue | Cause | Fix |
|-------|-------|-----|
| Slow page load | Large inline SVGs or base64 images | Move to external files with lazy loading |
| Janky scroll | Expensive `scroll` event handlers | Use `requestAnimationFrame` or `IntersectionObserver` |
| Layout thrashing | Read/write interleaving in DOM | Batch reads then writes |
| Memory leak | Event listeners not removed | Clean up in pagehide/beforeunload events |

## Target Files (Priority)
| File | Performance Focus |
|------|------------------|
| `CINEMATIC_SCROLL.html` | Parallax, particle trails, scroll smoothness |
| `dashboard/index.html` | Live data refresh, particle canvas FPS |
| `MERMAID_GRAPHS.html` | Diagram rendering time |
| `STRUCTURE_VISUALIZER.html` | Force-directed graph physics |

## Related Skills
- `azazael-devtools-audit` — Lighthouse performance score
- `azazael-devtools-sources` — Script execution profiling
- `azazael-devtools-coverage` — Unused code reduction
