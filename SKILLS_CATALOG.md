# AZAZAEL SKILLS CATALOG
# Complete Inventory of Codebuff Skills for the Azazael Project

> Generated: May 29, 2026
> Last Updated: June 14, 2026 (Session 2) — mypy + pyright skills created (#59-60); type auditing infra established
> Purpose: Single source of truth for all available Azazael skills

---

## Loading Order

For every Azazael session, load skills in this order:

### Mandatory (Every Session)
1. `azazael-system-startup` — **BUNDLED ENTRY POINT** — Single call reads 5 files, loads sop + error-prevention + pams-memory + mandates guardrails, runs FreeBuff/Bun diagnostic, initializes memory
2. `azazael-sop` — Standard operating procedure — error recording, severity classification, post-session cleanup
3. `azazael-mandates` — Complete codification of all 36 active mandates (30 RULEs 0A-0Z-B + enforcement + promoted RULEs 0B-0F)
4. `azazael-error-prevention` — Anti-pattern catalog (loaded by system-startup)

### Architecture (When Navigating/Modifying Structure)
4. `azazael-architecture` — Project layout, module organization
5. `azazael-files` — Complete file index, import resolution
6. `azazael-paths` — Dynamic path resolution

### Cluster System (When Working with Worms/Execution)
7. `azazael-clusters` — ClusterWORMZ, NatureClusters, MetaCluster API
8. `azazael-registry` — @register_worm decorator, WORM_REGISTRY
9. `azazael-worms` — All 77 worms across 17 categories
10. `azazael-worms-core` — Orchestration worms
11. `azazael-worms-data` — Data & insight worms
12. `azazael-worms-devops` — DevOps worms
13. `azazael-worms-monitor` — Observability worms
14. `azazael-worms-security` — Security & integrity worms

### Quality (When Making Changes)
15. `azazael-conventions` — Python coding patterns, style rules
16. `azazael-testing` — Syntax check, integration test, code review
17. `azazael-compliance-infrastructure` — RULE 0X/0Y: ComplianceOrchestrator, 13 components, sentinel_gate integration (NEW June 11, 2026)
18. `azazael-git` — Commit messages, branching

### Specialized Systems
19. `azazael-codex` — CODEX video generation, PAMS/MemoryBus
20. `azazael-codex-studio` — CODEX Studio desktop app
21. `azazael-codex-video` — Video generation workflow
22. `azazael-cain-pipeline` — CAIN video rendering pipeline, Puppeteer capture, optimal encoding
23. `azazael-cain-template` — CAIN template optimization, session data injection, cleanup patterns
24. `azazael-rendering-methods` — File-size comparison, codec tradeoffs, format recommendations
25. `azazael-mermaid` — Mermaid graph generation
26. `azazael-parallel` — Free-threading optimization, FreeThreadPool
27. `azazael-threading` — Threading patterns, Python 3.14t
28. `azazael-pams-memory` — Persistent AI memory across coding sessions, query/recall/search API (NEW Phase 19)

### Neural Wiring (NEW June 7, 2026)
29. `azazael-neural-architecture` — RL + SB3 + GRPO integration patterns
30. `azazael-training-pipeline` — ETL to model training data flow
31. `azazael-inference-providers` — 14-provider multi-API routing
32. `azazael-evolutionary-optimization` — NSGA-II + genetic algorithms
33. `azazael-system-wiring` — Cross-module neural integration map
34. `azazael-neural-pipeline` — Unified end-to-end ML orchestrator (NeuralPipeline v1.0.0)
35. `azazael-nsga2-testing` — NSGA-II unit tests (9 classes, 16 tests)
36. `azazael-6api-analysis` — 6-API deep analysis protocol

### Gemini Protocol (10-Phase Multi-Tier — NEW June 7, 2026)
37. `azazael-gemini-mandate` — Enforcement rules for Gemini spawning frequency (OFTEN, FREQUENTLY, CONSISTENTLY), minimum 4x per complex task
38. `azazael-gemini-protocol` — 10-Phase Multi-Tier Protocol with 6 Gemini injection points (400% increase over 6-Phase)
39. `azazael-gemini-injection` — 6 explicit injection point rules for spawning thinker-with-files-gemini

### Startup & Session Management (NEW Phase 19)
40. `azazael-system-startup` — Auto-loaded session startup guide for coding session congruency

### Deployment
41. `azazael-deploy` — Docker, CLI packaging, G: archive
42. `azazael-packaging` — Nuitka .exe builds
43. `azazael-standalone` — Standalone Suite (50 independent .exes)
44. `azazael-standalone-audit` — Standalone EXE/BAT audit and maintenance (NEW Phase 19)
45. `azazael-environment` — Python 3.10+/3.14t, dependencies
46. `azazael-production` — Production readiness roadmap

### Process and Tooling (When Auditing/Optimizing)
47. `azazael-error-resolution` — Sequential error resolution decision tree — 7-step troubleshooting flow
48. `azazael-curative` — CurativePool 3.14t — CAIN psychological framework, free-threaded evaluation
49. `azazael-autoflake` — Free-threaded autoflake wrapper for Python 3.14t import cleanup
50. `azazael-architecture-review` — Systematic architecture review — 3-pass inventory, 12-dimension scoring
51. `azazael-todo-management` — TODO document management — versioning, cross-referencing, classification

---

## Skill Quick Reference

| # | Skill | Category | When to Load |
|---|-------|----------|-------------|
| 1 | `azazael-system-startup` | Mandatory | Every session — FIRST |
| 2 | `azazael-sop` | Mandatory | Every session |
| 3 | `azazael-mandates` | Mandatory | Every session — full mandate reference |
| 4 | `azazael-error-prevention` | Mandatory | Before any code changes |
| 5 | `azazael-architecture` | Architecture | Navigating project structure |
| 6 | `azazael-files` | Architecture | Finding files, import paths |
| 7 | `azazael-paths` | Architecture | Path resolution, G: drive |
| 8 | `azazael-clusters` | Clusters | ClusterWORMZ/NatureCluster/MetaCluster |
| 9 | `azazael-registry` | Clusters | Worm registration, discovery |
| 10 | `azazael-worms` | Worms | Full worm catalog |
| 11 | `azazael-worms-core` | Worms | Orchestration + utility worms |
| 12 | `azazael-worms-data` | Worms | Data + insight worms |
| 13 | `azazael-worms-devops` | Worms | DevOps worms |
| 14 | `azazael-worms-monitor` | Worms | Observability worms |
| 15 | `azazael-worms-security` | Worms | Security worms |
| 16 | `azazael-conventions` | Quality | Coding style, error handling |
| 17 | `azazael-testing` | Quality | Validation, pre-commit checks |
| 18 | `azazael-compliance-infrastructure` | Quality | RULE 0X/0Y compliance: 13 components, ComplianceOrchestrator, sentinel_gate |
| 19 | `azazael-git` | Quality | Git conventions |
| 20 | `azazael-codex` | Specialized | Video generation, PAMS/MemoryBus |
| 21 | `azazael-codex-studio` | Specialized | CODEX Studio desktop app |
| 22 | `azazael-codex-video` | Specialized | Video generation workflow |
| 23 | `azazael-cain-pipeline` | Specialized | CAIN video rendering — Puppeteer capture, optimal encoding |
| 24 | `azazael-cain-template` | Specialized | CAIN template optimization, session data injection |
| 25 | `azazael-rendering-methods` | Specialized | File-size comparison, codec tradeoffs, format recs |
| 26 | `azazael-mermaid` | Specialized | Mermaid diagrams |
| 27 | `azazael-parallel` | Specialized | Free-threading optimization |
| 28 | `azazael-threading` | Specialized | Threading patterns |
| 29 | `azazael-pams-memory` | Specialized | Offline AI memory, query/recall/search |
| 30 | `azazael-neural-architecture` | Neural | **NEW** RL + SB3 + GRPO integration patterns |
| 31 | `azazael-training-pipeline` | Neural | **NEW** ETL to model training data flow |
| 32 | `azazael-inference-providers` | Neural | **NEW** 14-provider multi-API routing |
| 33 | `azazael-evolutionary-optimization` | Neural | **NEW** NSGA-II + genetic algorithms |
| 34 | `azazael-system-wiring` | Neural | **NEW** Cross-module neural integration map |
| 35 | `azazael-neural-pipeline` | Neural | **NEW** NeuralPipeline v1.0.0 orchestrator |
| 36 | `azazael-nsga2-testing` | Neural | **NEW** NSGA-II unit tests (9 classes, 16 tests) |
| 37 | `azazael-6api-analysis` | Neural | **NEW** 6-API deep analysis protocol |
| 38 | `azazael-gemini-mandate` | Gemini | **NEW** Enforces Gemini spawning OFTEN, FREQUENTLY, CONSISTENTLY — min 4x per complex task |
| 39 | `azazael-gemini-protocol` | Gemini | **NEW** 10-Phase Multi-Tier Protocol — 6 Gemini injection points (400% increase) |
| 40 | `azazael-gemini-injection` | Gemini | **NEW** Explicit injection point rules for thinker-with-files-gemini |
| 41 | `azazael-system-startup` | Startup | **ALWAYS FIRST** — Bundled startup: reads 5 files, loads 3 guardrails, runs FreeBuff/Bun diagnostic, initializes memory. Single entry point. |
| 42 | `azazael-deploy` | Deployment | Docker, G: archive |
| 43 | `azazael-packaging` | Deployment | Nuitka builds (3.14t only, patched) |
| 44 | `azazael-standalone` | Deployment | Standalone exe catalog (3.14t builds) |
| 45 | `azazael-environment` | Deployment | Python 3.14t-only environment setup |
| 46 | `azazael-production` | Deployment | Roadmap, gaps (3.14t-only mandate) |
| 47 | `azazael-standalone-audit` | Deployment | Standalone suite audit, EXE/BAT validation (3.14t) |
| 48 | `azazael-error-resolution` | Quality | **NEW** Sequential error resolution decision tree — 7-step flow for Python env, WSL/MSYS2, Nuitka builds, packages, disk, tests |
| 49 | `azazael-curative` | Architecture | **NEW** CurativePool 3.14t — CAIN psychological framework, free-threaded concurrent evaluation, 3-pool governance architecture |
| 50 | `azazael-autoflake` | Tooling | Free-threaded autoflake wrapper for Python 3.14t — batch unused import detection/removal, recursive scanning, subprocess isolation |
| 51 | `azazael-architecture-review` | Architecture | **NEW** Systematic architecture review methodology — 3-pass inventory, 12-dimension quality scoring, coupling/cohesion analysis, TODO cross-referencing |
| 52 | `azazael-todo-management` | Process | **NEW** TODO document management methodology — versioning, cross-referencing, ADDITIVE/REINFORCES/DUPLICATE classification, multi-document consistency |
| 53 | `azazael-compliance-infrastructure` | Quality | **NEW June 11, 2026** — RULE 0X/0Y compliance: 13 components, ComplianceOrchestrator API, sentinel_gate integration, Step 4.5 auto-load |
| 54 | `azazael-eleven-followups` | Workflow | **NEW June 12, 2026** — RULE 0Z-B: 11 followups mandate. `auto_load: true`. |
| 55 | `azazael-autodiff-forward` | Algorithm | **NEW June 14, 2026** — Forward-mode autodiff via mygrad: JVP, Jacobian-via-seeding, HVP. `auto_load: true`. |
| 56 | `azazael-autodiff-backprop` | Algorithm | **NEW June 14, 2026** — Reverse-mode backprop via mygrad: gradients, seeds, batch, MLP, accumulation, clipping. `auto_load: true`. |
| 57 | `azazael-autodiff-gradient` | Algorithm | **NEW June 14, 2026** — Gradient descent optimizers via mygrad: SGD, Momentum, Nesterov, AdaGrad, RMSprop, Adam, AdamW + LR schedules. `auto_load: true`. |
| 58 | `azazael-autodiff-higher-order` | Algorithm | **NEW June 14, 2026** — Higher-order derivatives via mygrad: HVP, Hessian, Jacobian, Gauss-Newton, Newton-CG, derivatives. `auto_load: true`. |
| 59 | `azazael-mypy` | Quality | **NEW June 14, 2026** — mypy 2.1.0 static type checking: configuration, error categories, 3.14t considerations, audit commands. `auto_load: true`. |
| 60 | `azazael-pyright` | Quality | **NEW June 14, 2026** — Pyright 1.1.410 static type checking: pyrightconfig.json, error patterns, Optional guards, free-threading patterns. `auto_load: true`. |
| 61 | `azazael-operating-protocols` | Workflow | **NEW June 14, 2026** — Operating protocols: 11 followups, max parallel agents, proactive skill creation, full tool arsenal usage. `auto_load: true`. |
| 62 | `azazael-audit-infrastructure` | Quality | **NEW June 14, 2026** — VLP 15-layer audit trail: .audit/ JSONL hash-chained sessions, DirectMemory dual-ledger cross-validation, anchors/Merkle proofs. `auto_load: true`. |
| 63 | `azazael-worm-registry-fixes` | Architecture | **NEW June 14, 2026** — Worm registry module path fixes: discover_worms() two-path correction, already_has_classes root cause, 28 affected worms, cache fix, pre-existing import issues. `auto_load: false`. |
| 64 | `azazael-dlv-divergence` | Architecture | **NEW June 14, 2026** — DualLedgerValidator expected divergence: file_edit, file_create, inference_spawn by-design discrepancies between DirectMemory and .audit/ JSONL. `auto_load: false`. |
| 65 | `azazael-auto-downloader-fix` | Architecture | **NEW June 14, 2026** — CODEX/CORE bug chain documentation: AUTO_DOWNLOADER main() restructuring, CAIN_ANALYZER `_sys` to `sys`, enhanced_animations indent fixes, `_log_event` KeyError fix. `auto_load: false`. |
| 66 | `azazael-compliance-deep-dive` | Architecture | **NEW June 14, 2026** — Deep diagnostic of ComplianceOrchestrator self_test: 0X 8/8 pass, 0Y 4/5 pass (dual_ledger by-design), state machine startup wiring analysis (IDLE→CODE_EDIT). `auto_load: false`. |

| 67 | `azazael-state-machine` | Architecture | **NEW June 14, 2026** — ComplianceStateMachine reference: 7 states, legal transitions, is_in_sequence() check, startup wiring fix. `auto_load: false`. |
| 68 | `azazael-dual-ledger` | Architecture | **NEW June 14, 2026** — DualLedgerValidator discrepancy catalog: file_edit, file_create, test_run by-design divergences, severity levels, matching_sessions=0 root cause. `auto_load: false`. |
| 69 | `azazael-catalog-maintenance` | Process | **NEW June 14, 2026** — SKILLS_CATALOG.md format, numbering convention, Sections pattern, maintenance procedures, common issues (bash backtick escaping). `auto_load: false`. |
## New Tools — Created Phase 19 Followups (May 29, 2026)

| Tool | Path | Purpose | Priority |
|------|------|---------|----------|
| `codebuff_tracker.py` | `CORE/codebuff_tracker.py` | Auto-records Codebuff session events (file edits, creates, reviews, tests, milestones) to LocalMemoryStore with singleton pattern and query helpers | ✅ Created |

---

## Skills Updated — June 11, 2026

| Skill | Path | Update |
|-------|------|--------|
| `azazael-compliance-infrastructure` | `skills/azazael-compliance-infrastructure.md` | **NEW** — RULE 0X/0Y compliance: ComplianceOrchestrator API, 13 components, sentinel_gate integration documentation |
| `azazael-system-startup` | `skills/azazael-system-startup.md` | Added Step 4.5: ComplianceOrchestrator initialization with state machine transition to GATE_ASSERT |
| `azazael-error-prevention` | `skills/azazael-error-prevention.md` | Added Anti-Pattern #6 (False Verification Passes) with RULE 0H-A + 0Q-A checklists |
| `azazael-gemini-mandate` | `skills/azazael-gemini-mandate.md` | Added operational rules #4 (RULE 0Q Post-Phase Inference) and #5 (RULE 0Q-A MUST CITE) |
| `azazael-gemini-protocol` | `skills/azazael-gemini-protocol.md` | Added Phase Boundary Enforcement section (RULE 0Q & 0Q-A) |
| `azazael-gemini-injection` | `skills/azazael-gemini-injection.md` | Added injection point #7 (Post-Phase Boundary Check per RULE 0Q/0Q-A) |
| `azazael-fix-protocol-compliance` | `skills/azazael-fix-protocol-compliance.md` | Added errors #157-160 (mental assertion, missing codification, invalid verification, skills propagation) |

## Skills Updated — June 12, 2026

| Skill | Path | Update |
|-------|------|--------|
| `azazael-mandates` | `skills/azazael-mandates.md` | Changed `auto_load: false` → `auto_load: true` — now pre-loaded at every session start via `skill()` |
| `azazael-system-startup` | `skills/azazael-system-startup.md` | Updated Step 1 note: `skill("azazael-mandates")` now loads directly (no longer a workaround) |

---

## RULE 0R — Skills Propagation Mandate (June 11, 2026)

**Trigger:** Any skill file in `azazael/skills/` is created or modified.

**Action:** Run `python azazael/src/scripts/sync_skills.py` to propagate changes to `.agents/skills/<name>/SKILL.md`.

**Automation:** `sync_skills.py` is hooked into `azazael-system-startup` (Step 2.5) and runs at every session start.

**Tool:** `azazael/src/scripts/sync_skills.py` — Pathlib-based, content-aware (uses `filecmp.cmp` for change detection). Reports: synced, unchanged, new, errors.

---

## New Skills — Created June 14, 2026 (Session 2)

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-mypy` | `skills/azazael-mypy.md` | mypy 2.1.0 static type checking for Azazael — configuration (pyproject.toml [tool.mypy]), canonical audit command, error category reference (1,466 errors across 174 files diagnosed), 3.14t free-threading considerations, `__init__.py` gap detection. `auto_load: true`. | ✅ Created |
| `azazael-pyright` | `skills/azazael-pyright.md` | Pyright 1.1.410 static type checking via npx — pyrightconfig.json with balanced strictness (basic mode), error pattern fixes (reportPossiblyUnboundVariable, reportOptionalMemberAccess), free-threading patterns, quick diagnostic commands. `auto_load: true`. | ✅ Created |

## New Skills — Created June 14, 2026 (Session 3)

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-operating-protocols` | `skills/azazael-operating-protocols.md` | Operating protocols codification: 11 followups mandate, max parallel agent execution, proactive skill creation, full tool arsenal, on-the-fly skill creation. `auto_load: true`. | ✅ Created |
| `azazael-audit-infrastructure` | `skills/azazael-audit-infrastructure.md` | VLP 15-layer audit trail system: .audit/ JSONL hash-chained sessions, DirectMemory dual-ledger cross-validation, anchors/Merkle proofs, audit review procedures. `auto_load: true`. | ✅ Created |
| `azazael-dedup` | `skills/azazael-dedup.md` | Deduplication procedures: MD5 hash comparison, duplicate file detection, deprecation shim creation, cleanup patterns. `auto_load: false`. | ✅ Created |
| `azazael-shims` | `skills/azazael-shims.md` | Deprecation shim pattern: FutureWarning, re-export, testing lifecycle, cleanup. `auto_load: false`. | ✅ Created |
| `azazael-worm-registry-fixes` | `skills/azazael-worm-registry-fixes.md` | Worm registry module path fix: how discover_worms() stores module names, 28 affected worms, fix pattern. `auto_load: false`. | ✅ Created |
| `azazael-dlv-divergence` | `skills/azazael-dlv-divergence.md` | DualLedgerValidator expected divergence: file_edit, file_create, inference_spawn by-design discrepancies. `auto_load: false`. | ✅ Created |
| `azazael-compliance-deep-dive` | `skills/azazael-compliance-deep-dive.md` | Deep diagnostic of ComplianceOrchestrator self_test: 0X 8/8 pass, 0Y 4/5 pass (dual_ledger by-design), state machine startup wiring analysis. `auto_load: false`. | ✅ Created |
| `azazael-state-machine` | `skills/azazael-state-machine.md` | ComplianceStateMachine reference: 7 states, legal transitions, is_in_sequence() check, startup wiring fix. `auto_load: false`. | ✅ Created |
| `azazael-dual-ledger` | `skills/azazael-dual-ledger.md` | DLV discrepancy catalog: file_edit, file_create, test_run divergences, severity, matching_sessions=0 root cause. `auto_load: false`. | ✅ Created |
| `azazael-catalog-maintenance` | `skills/azazael-catalog-maintenance.md` | SKILLS_CATALOG.md format, numbering convention, Sections pattern, maintenance procedures. `auto_load: false`. | ✅ Created |

## New Tools — Created June 14, 2026 (Session 2)

| Tool | Path | Purpose | Priority |
|------|------|---------|----------|
| `pyrightconfig.json` | `pyrightconfig.json` | Pyright configuration — Python 3.14, basic typeCheckingMode, excludes build artifacts/archives, disables noisy unknown-type reports | ✅ Created |
| `__init__.py` (×7) | `src/__init__.py`, `src/AZAZAEL_TOOLKIT/__init__.py`, `src/CODEX/CORE/__init__.py`, `src/META/__init__.py`, `src/ORCHESTRATION/BIBL/__init__.py`, `src/SCRIPTS/__init__.py`, `src/UTILITIES/PERSEPHONE/bin/__init__.py` | Package markers for proper module resolution by mypy/pyright | ✅ Created |

## New Skills — Created June 14, 2026 (Session 1)

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-autodiff-forward` | `skills/azazael-autodiff-forward.md` | Forward-mode automatic differentiation via mygrad 2.3.0 — JVP, Jacobian-via-input-seeding, HVP via finite differences. Documents mygrad limitations (.grad is detached numpy, requires_grad as attribute not kwarg). `auto_load: true`. | ✅ Created |
| `azazael-autodiff-backprop` | `skills/azazael-autodiff-backprop.md` | Reverse-mode back-propagation via mygrad 2.3.0 — scalar/vector gradients, seeding, batch computation, MLP backprop, gradient accumulation, clipping. `auto_load: true`. | ✅ Created |
| `azazael-autodiff-gradient` | `skills/azazael-autodiff-gradient.md` | 7 gradient descent optimizers from scratch via mygrad — SGD, Momentum, Nesterov, AdaGrad, RMSprop, Adam, AdamW + StepLR, CosineAnnealing, ReduceLROnPlateau. `auto_load: true`. | ✅ Created |
| `azazael-autodiff-higher-order` | `skills/azazael-autodiff-higher-order.md` | Higher-order derivatives via mygrad 2.3.0 — HVP (finite diff), Hessian diag/full, Jacobian, Gauss-Newton, Newton-CG, derivatives up to order 3. Documents mygrad .grad-is-numpy limitation. `auto_load: true`. | ✅ Created |

## New Skills — Created June 12, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-mandates` | `skills/azazael-mandates.md` | Complete codification of all 36 active mandates (30 RULEs 0A-0Z-B + enforcement + promoted RULEs 0B-0F). Created as mirrored skill from canonical MANDATES.md with `auto_load: true` for session-start availability. | ✅ Created |
| `azazael-eleven-followups` | `skills/azazael-eleven-followups.md` | RULE 0Z-B — Mandates exactly 11 followup suggestions at the end of EVERY assistant response. Permanent, never disableable. `auto_load: true`. | ✅ Created |

## New Skills — Created June 7, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-neural-architecture` | `skills/azazael-neural-architecture.md` | RL + SB3 + GRPO integration patterns for free-threaded neural agents. Covers GRPOTrainer wiring, SB3 algorithm configuration, and 3.14t compatibility. | ✅ Created |
| `azazael-training-pipeline` | `skills/azazael-training-pipeline.md` | End-to-end ML training pipeline — ETL data flow, model training orchestration, checkpoint management. Covers data preprocessing through model export. | ✅ Created |
| `azazael-inference-providers` | `skills/azazael-inference-providers.md` | 14-provider multi-API routing system with circuit breaker integration. Covers provider selection, health checking, and failover strategies. | ✅ Created |
| `azazael-evolutionary-optimization` | `skills/azazael-evolutionary-optimization.md` | NSGA-II multi-objective genetic algorithm implementation. Covers population management, Pareto front optimization, and fitness evaluation. | ✅ Created |
| `azazael-system-wiring` | `skills/azazael-system-wiring.md` | Cross-module neural integration map connecting RL training, inference providers, and worm execution. Covers inter-module communication and data flow. | ✅ Created |
| `azazael-neural-pipeline` | `skills/azazael-neural-pipeline.md` | Unified end-to-end ML orchestrator (NeuralPipeline v1.0.0). Covers pipeline stages, error recovery, and parallel execution on 3.14t. | ✅ Created |
| `azazael-nsga2-testing` | `skills/azazael-nsga2-testing.md` | NSGA-II unit test suite — 9 test classes, 16 test cases. Covers population initialization, selection, crossover, mutation, and convergence testing. | ✅ Created |
| `azazael-6api-analysis` | `skills/azazael-6api-analysis.md` | 6-API deep analysis protocol for cross-validating system changes. Covers provider selection, prompt construction, and convergence scoring methodology. | ✅ Created |
| `azazael-gemini-mandate` | `skills/azazael-gemini-mandate.md` | Enforcement rules for Gemini spawning frequency (OFTEN, FREQUENTLY, CONSISTENTLY). Minimum 4 Gemini spawns per complex task. Covers when Gemini is MANDATORY vs optional, counting rules, and violation classification. | ✅ Created |
| `azazael-gemini-protocol` | `skills/azazael-gemini-protocol.md` | Expanded 10-Phase Multi-Tier Protocol with 6 Gemini injection points (400% increase over 6-Phase). Covers all 10 phases from Pre-Analysis to Final Synthesis, Gemini injection point map, and pipeline execution patterns. | ✅ Created |
| `azazael-gemini-injection` | `skills/azazael-gemini-injection.md` | Explicit injection point rules for spawning thinker-with-files-gemini at 6 specific phases. Covers when to spawn, what filePaths to provide, what prompt format to use, and anti-patterns to avoid. | ✅ Created |

## New Skills — Created June 5, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-cain-pipeline` | `skills/azazael-cain-pipeline.md` | CAIN video rendering pipeline — Puppeteer browser capture (NOT PIL), session-specific HTML injection, optimal encoding settings (HEVC 720p CRF 26-28 2.5x), inject→record→encode workflow. Covers why Puppeteer beats PIL (browser compositor vs sub-pixel noise), complete 3-stage pipeline, anti-patterns, and related lessons #76-79. | ✅ Created |
| `azazael-cain-template` | `skills/azazael-cain-template.md` | CAIN template optimization & injection — dead code removal (web-arrows, duplicate sections), CSS animation audit (15 @keyframes), session-specific data injection patterns (36 surgical replacements), template cleanup checklist, and optimization script. Covers completed (3,705 bytes saved) and planned (~2-3KB remaining) optimizations. | ✅ Created |
| `azazael-rendering-methods` | `skills/azazael-rendering-methods.md` | CAIN video rendering method comparison — file sizes across 6 pipelines (PIL 318MB → Puppeteer 120MB → Panels 8.4MB), codec tradeoffs (H.264 vs HEVC vs VP9 vs AV1), format recommendations by use case, optimal encoding settings for smallest file size (~45MB HEVC 720p 2.5x). Includes CRF guide for text content and resolution comparison. | ✅ Created |

## New Skills — Created June 2, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-error-resolution` | `skills/azazael-error-resolution.md` | Sequential error resolution decision tree — systematic troubleshooting across 7 steps covering Python 3.14t environment, WSL/MSYS2 path translation, Nuitka builds, package installation on cp314t, disk space, test failures, and post-mortem recording. Includes decision flowcharts and quick reference card. | ✅ Created |

## New Skills — Created Phase 19 (May 29, 2026)

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-pams-memory` | `skills/azazael-pams-memory.md` | Persistent AI memory via LocalMemoryStore (SQLite) with query/recall/search. Works offline without PAMS server. Includes API reference and usage patterns. | ✅ Created |
| `azazael-system-startup` | `skills/azazael-system-startup.md` | Auto-loaded session startup guide ensuring coding session congruency. Covers mandatory skill loading order, memory initialization, and project path verification. | ✅ Created |
| `azazael-standalone-audit` | `skills/azazael-standalone-audit.md` | Desktop Standalone Suite audit and maintenance — EXE inventory, BAT validation, build system health, naming conventions, known issues. Includes health check commands and module inventory. | ✅ Created |

## New Skills — Future Development

Based on the May 29, 2026 session findings, these skills should be created:

| Proposed Skill | Purpose | Priority |
|---------------|---------|----------|
| `azazael-dedup` | Deduplication procedure — MD5 hash comparison, shim creation, file cleanup | High |
| `azazael-shims` | Deprecation shim pattern, UserWarning usage, testing procedure | High |
| `azazael-g-sync` | G: drive sync procedure — what to copy, when, verification | Medium |
| `azazael-separation` | Monolith separation plan — 6 layers, 27 programs, migration steps | High |
