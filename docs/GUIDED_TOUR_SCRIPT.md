# Guided Tour Narrative Design

**Task:** Board 47001 / YGGDRASIL-CLEAVE-K6
**Date:** 2026-11-02
**Author:** opencode lane (max reasoning)

## Problem

The 20-tree codebase has no guided walkthrough. New developers (and auditors) must
discover the structure by exploration. A guided tour would reduce onboarding time
and ensure critical paths are understood.

## Design: 20-Tree Walkthrough

### Tour Structure

1. **Welcome** (30s): What is azazael? 20 trees, 750 modules, 311K lines.
2. **CORE** (2min): The hub — 337 modules, 166K lines. Worm registry, freethreading, compliance.
3. **CODEX** (1min): Video generation — 90 modules, 36K lines. capture_panels.js, templates.
4. **ORCHESTRATION** (1min): Ecosystem crawler — 84 modules, 37K lines. HORUS, HYDRA.
5. **META** (30s): Meta-reflection — 20 modules, 10K lines. Trial distillation.
6. **UTILITIES** (30s): KLINK, PERSEPHONE, POINDEXTER, TARBABY, TERENCE.
7. **SCRIPTS** (30s): Debug runner, archive system.
8. **The 13 remaining trees** (2min): Quick overview of each.
9. **Quiz** (1min): 5 questions about the structure.
10. **Feedback** (30s): What was confusing? What was clear?

### Quiz Questions

1. Which tree has the most modules? (CORE)
2. What is the worm registry's purpose? (register and discover worms)
3. What does the compliance scanner check? (anti-patterns, silent swallows)
4. Which tree handles video generation? (CODEX)
5. What is the purpose of the work-stealing pool? (load balancing across threads)

### Feedback Collection

- Rate each section 1-5
- "What was most confusing?"
- "What would you add?"
- Store feedback in PMB as lessons

### Implementation

- Phase 1: Write tour script (this document)
- Phase 2: Implement interactive tour in graph3d (highlight nodes, show info panel)
- Phase 3: Add quiz with answer validation
- Phase 4: Store feedback in PMB

## Deliverable checklist

- [x] Tour structure defined (10 sections, 20 trees)
- [x] Quiz questions specified (5 questions)
- [x] Feedback collection designed
- [x] Implementation plan defined