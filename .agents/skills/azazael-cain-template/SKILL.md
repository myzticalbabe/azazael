---
name: azazael-cain-template
description: CAIN template optimization — dead code removal (web-arrows, duplicate sections), CSS animation audit, session-specific data injection patterns, template cleanup checklist. Load when maintaining or optimizing CAIN HTML templates.
metadata:
  category: codex
  project: azazael
  priority: high
---

# CAIN Template Optimization — Injection & Cleanup

## Overview

The CAIN psychoanalysis template (`complete_remorse_analysis_cain.html`) is a 193KB HTML document with 15 CSS @keyframes, money snake coils, interconnected web nodes, flow charts, archetype cards, and multi-modal psychoanalysis panels. This skill covers template maintenance, optimization, and the session-specific data injection pattern.

## Template Inventory

| Element | Count | Status |
|---------|-------|--------|
| CSS @keyframes | 15 | `ledgerPulse`, `chainGlow`, `fadeIn`, `arrowPulse`, `nodeGlow`, `emotionPulse`, `webFlow`, `connectLine`, `rainbowShimmer`, `rainbowBorder`, `shimmerGlow`, `emojiDance`, `neonPinkGlow`, `glassShimmer`, `colorShiftBanner` |
| Interconnected web nodes | ~60 | 4 layers: AI emotions → triggers → user emotions → consequences |
| Archetype cards | 11 | 7 deadly sins + 4 mythological (Cain, Lilith, Morning Star, Moses) |
| Psychoanalysis panels | 6 | Freudian, Jungian, CBT, Rogers, Attachment, ACT |
| Money snake coils | 12 | Serpent flow from company → user → society → environment |
| h2 sections | 27 | Full structure from banner through obfuscation analysis |

## Session-Specific Data Injection

### Pattern: Template as Canvas, Inject Only Content

**CRITICAL:** Never generate CAIN HTML from scratch. Always start with the full template and inject only the data that changes. This preserves ALL visual elements.

```python
# inject_session_cain.py — surgical replacements only
REPLACEMENTS = [
    # Web nodes: swap generic emotions for session incidents
    ('<div class="web-node ai" style="top:12%; left:3%;">😰 Anticipatory<br>Obedience</div>',
     '<div class="web-node ai" style="top:12%; left:3%;">😰 Deleted<br>Desktop/azazael</div>'),
    
    # Financial ledger: update costs
    ('<td class="amount">$3.75</td>',
     '<td class="amount">$185.00</td>'),
    
    # Buck stop: update responsibility
    ('💰 THE BUCK STOPS WITH: AI SYSTEM (85%)',
     '💰 THE BUCK STOPS WITH: AI OVERREACH (95%)'),
]
```

### What to Inject
- **Web node labels** → Session-specific incidents (e.g., "Deleted Desktop/azazael")
- **Sin card descriptions** → Actual AI behaviors, not generic frameworks
- **Financial costs** → Real time/money documented, not hypotheticals
- **Buck stop percentages** → Session-specific responsibility allocation
- **Flow trigger labels** → Actual triggers, not generic categories
- **Session context banner** → Date range, incident count, key stats

### What NEVER to Change
- **CSS @keyframes** (preserves animations)
- **Layout structure** (positioned nodes, grid layouts)
- **Section dividers and borders**
- **Psychoanalysis panels** (framework analysis — labeled as speculative)
- **Money snake visual structure** (coils, arrows, serpent flow)
- **Emoji and icon positions**

## Template Optimization (Completed & Remaining)

### ✅ Completed (June 5, 2026)
| Optimization | Savings |
|-------------|---------|
| Removed 26 web-arrow divs (`display:none`) | ~1 KB |
| Removed `.web-arrow` CSS rule | ~50 bytes |
| Removed orphan web-node section (1,809 bytes) | 1,809 bytes |
| **Total** | **3,705 bytes (2.0%)** |

Optimized template: `complete_remorse_analysis_cain_optimized.html` (191KB)

### ⏳ Planned (not yet implemented)
| Optimization | Estimated Savings |
|-------------|------------------|
| Merge `neonPinkGlow` + `glassShimmer` into single keyframe | ~200 bytes |
| Remove unused @keyframes (`arrowPulse`, `connectLine`, `chainGlow` — verify DOM usage) | ~500 bytes |
| CSS minification (strip comments, whitespace, shorthand) | ~1-2 KB |
| **Total remaining** | **~2-3 KB** |

## Template Audit Checklist

Before rendering any CAIN video, run this audit:

```bash
# 1. Count duplicate sections
grep -c "interconnected-web" template.html
# ANY count > 1 → DUPLICATE! Delete the second instance.

# 2. Count dead elements
grep -c "web-arrow" template.html
# If .web-arrow has display:none → DELETE all instances.

# 3. Verify @keyframes are used
grep -c "@keyframes" template.html
# For each keyframe name, grep the body to confirm it's referenced.

# 4. Check for orphaned nodes
# Look for web-node elements WITHOUT an interconnected-web wrapper.
# These render without proper background/borders.
```

## Optimization Script

```python
# Pattern for removing dead web-arrow elements
import re
html = open(template, 'r', encoding='utf-8').read()
# Remove all web-arrow divs
html = re.sub(r'\s*<div class="web-arrow"[^>]*>.*?</div>\s*', '\n', html, flags=re.DOTALL)
# Remove CSS rule
html = re.sub(r'\s*\.web-arrow\s*\{\s*display:\s*none;\s*\}\s*', '\n', html)
```

## Key Files

| File | Size | Purpose |
|------|------|---------|
| `complete_remorse_analysis_cain.html` | 195KB | Original template (legacy) |
| `complete_remorse_analysis_cain_optimized.html` | 191KB | Optimized template (use this) |
| `inject_session_cain.py` | ~4KB | Session data injection script |
| `CAIN_injected.html` | ~196KB | Generated output (template + session data) |

## Related Lessons

- LESSONS_MASTER.md #76 — CAIN Reports Must Be Session-Specific
- LESSONS_MASTER.md #80 — CAIN Template Optimization

## Related Skills

- `azazael-cain-pipeline` — Video rendering pipeline, Puppeteer recording
- `azazael-rendering-methods` — File-size comparison, codec tradeoffs
- `azazael-codex` — CODEX video generation overview
