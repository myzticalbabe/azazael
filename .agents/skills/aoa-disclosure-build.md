---
name: aoa-disclosure-build
description: AOA Architecture Disclosure HTML and MP4 build pipeline - 14 diagram whitepaper with 12-color semantic Mermaid palette, Puppeteer scroll capture, HEVC encoding. Load when building or updating the AOA architecture disclosure.
metadata:
  category: domain
  project: aoa
  priority: high
  version: 2.0.0
---

# AOA Architecture Disclosure - Build Pipeline

## Overview

This skill documents the complete AOA (Armorie-of-Anubis) Architecture Disclosure
build pipeline. Produces a single-scroll whitepaper HTML with 14 Mermaid diagrams
and renders to 1080p HEVC MP4 via Puppeteer scroll capture.

## Output Files

| File | Size | Description |
|------|------|-------------|
| AOA_STRUCTURE.html | ~35KB | 7-section whitepaper, 14 diagrams |
| AOA_Architecture_Disclosure.mp4 | ~1.2MB | 1080p HEVC, 85s scroll video |
| AOA_Architecture_Disclosure_2.5x.mp4 | ~1.1MB | 34s 2.5x speed version |

## Prerequisites

- Python 3.14t with src on path
- Node.js v24+ with puppeteer installed
- ffmpeg with libx265 support
- benchmark_data.json in AOA directory

## Build Pipeline

### Phase 1: Build HTML
Run the builder script that reads benchmark_data.json and generates the full
whitepaper with 12-classDef global semantic palette.

### Phase 2: Verify in Browser
Open HTML in Chrome. Verify all 14 Mermaid diagrams render. Check zero JS errors.
Verify colors: blue (core), orange (cog), violet (comply), rose (fleet), gold (wire),
teal (codex).

### Phase 3: Render to Video
Use Puppeteer to capture 17 scroll frames (18,336px body at 1080p viewport).
Wait 8 seconds for all Mermaid diagrams to render before starting capture.
Encode with ffmpeg: HEVC CRF 28, -tune grain, 1080p, 25fps.

### Phase 4: Distribute
Copy HTML to WSL Ubuntu, Kali Linux, G: AZAZAEL/AOA/.
Copy MP4s to G: AZAZAEL/AOA/.

## 12-Color Semantic Palette

| classDef | Color | Hex | Systems |
|----------|-------|-----|---------|
| core | Deep Blue | #0f4c75 | VF, METACLUSTER, W11 Master |
| env | Sky Blue | #3b82f6 | Quartet environments |
| sync | Amber | #f59e0b | SHA-256, doc sync |
| cog | Burnt Orange | #d65a31 | Dreaming, MetaCognition |
| evolve | Emerald | #10b981 | Evolution, genetic |
| infer | Pink | #ec4899 | Parallel inference |
| comply | Violet | #7c3aed | RULE 0X/0Y, governance |
| fleet | Rose | #f43f5e | SpawnDiversity, cooldown |
| wire | Gold | #d97706 | Cross-project, EXEs |
| codex | Teal | #0e918c | CAIN, CODEX, video |
| data | Slate | #475569 | PAMS, MemoryBus, audit |
| doc | Stone | #78716c | Documents, templates |

## CRITICAL: Mermaid classDef Ordering

classDef MUST appear AFTER the graph TB/LR declaration. Placing classDef before
graph causes all diagrams to show "Syntax error in text." Fix with regex that
moves classDef blocks after graph declaration.

## 7-Section Whitepaper Structure

1. Executive Summary and Benchmarks (16 stat cards)
2. Core Ecosystem (VF, Quartet, 3-Tier Clusters, Arm Matrix)
3. Advanced Cognition (Dreaming, MetaCognition, Neural Advancement)
4. CAIN and CODEX Pipelines (Puppeteer, PIL, Dual Recording)
5. Compliance and Fleet Management (RULE 0X/0Y, SpawnDiversity)
6. Cross-Project Wiring (49 EXEs, Skills Catalog)
7. Verified Architecture Specifications (14 specs with sources)

## Key Numbers

| Metric | Value |
|--------|-------|
| Worms | 129 |
| Categories | 23 |
| Diagrams | 14 |
| Arms | 8 |
| Compliance components | 13 |
| Standalone EXEs | 49 |
| Skills | 25 |
| Quartet pillars | 4 |
| Canonical docs | 8 |
| Routes | 46 |
| Paths | 264 |
| Specs | 14 |

## Related Skills

- azazael-cain-pipeline - CAIN video rendering pipeline
- azazael-cain-template - Template optimization patterns
- azazael-codex - CODEX video and memory systems
- azazael-compliance-infrastructure - RULE 0X/0Y details
- azazael-clusters - 3-tier cluster architecture
- azazael-worms - Full worm registry
- azazael-full-wiring - Cross-project wiring

## Lessons Learned

1. Mermaid classDef must be AFTER graph declaration
2. Professional docs = single scroll, not tabs
3. Striktethrough corrections are unprofessional for disclosure
4. Heredoc with single-quoted delimiter prevents bash expansion on Windows
5. Puppeteer needs 5-8s for 14 Mermaid diagrams to render
6. min-height on Mermaid wrappers prevents layout shifts during capture


## Diagram Width Fix (July 2, 2026)

### Problem
Mermaid generates SVGs with explicit inline `width` attributes that can be as small as 275px even in 1680px containers. CSS `width:100% !important` is overridden by these inline attributes.

### Solution
Inject a `MutationObserver` after `mermaid.initialize()` to strip inline `width` attributes and force `style.width = "100%"` on all `.mw svg` elements:

```html
<script>
document.addEventListener("DOMContentLoaded", () => {
  const observer = new MutationObserver(() => {
    document.querySelectorAll('.mw svg').forEach(svg => {
      if (svg.hasAttribute('width')) {
        svg.removeAttribute('width');
        svg.style.width = '100%';
        svg.style.maxWidth = '100%';
        svg.style.height = 'auto';
      }
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
});
</script>
```

### Verification
Browser-verified: all 16 diagrams render at full container width, zero JS errors, MutationObserver confirmed working.

## Recording Speeds

| Scroll Rate | Duration | Use Case |
|-------------|----------|----------|
| 80 px/s | ~350s | Detailed viewing |
| 140 px/s | ~286s | Balanced readability/speed |
| 200+ px/s | <200s | Quick overview |
