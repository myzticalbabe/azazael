# azazael-deep-analysis
**Category:** Mandatory Guardrail
**Priority:** CRITICAL
**Dependencies:** azazael-system-startup, azazael-session-recording
**Created:** June 7, 2026

## Purpose
Mandates the DEEP API Analysis Standard — ALL analysis tasks must use 5 free inference APIs (Groq, OpenRouter, NVIDIA NIM, Mistral, GitHub) with cross-referenced findings.

## When To Load
- At every session startup (loaded via `skill("azazael-system-startup")`)
- Before any analysis task: architecture review, security audit, performance review
- When user says "analyze", "review", "use all api", "deep analysis"

## Core Mandate
Every analysis task uses ALL 5 inference APIs, each from a different angle:
- Groq → Architecture & Design
- OpenRouter → Security & Lifecycle
- NVIDIA NIM → Performance & Parallelism
- Mistral → Code Quality & Anti-patterns
- GitHub → Testing Strategy & Edge Cases

Findings flagged by 3+ APIs are CRITICAL priority.
Single-model analysis is deprecated.

## Reference
See `azazael/DEEP_API_ANALYSIS_STANDARD.md` for the complete protocol.
