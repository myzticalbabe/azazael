# AZAZAEL SKILLS CATALOG
# Complete Inventory of Codebuff Skills for the Azazael Project

> Generated: May 29, 2026
> Last Updated: September 14, 2026 — recounted from disk (`C:\Users\clint\.agents\skills`: 1,224 dirs, all with SKILL.md). Prior Aug-23 claim of 1,259 was stale (+35 over actual).
> Current: 1,224 total = 968 `azazael-pkg-*` + 74 `azazael-pkg314t-*` + 46 `azazael-bin-*` + 133 core `azazael-*` + 3 misc (`azazael_314t_master`, `azazael_314t_optimum`, `azazael_insights_2026-05-28`). (Historical note: Aug-23 edition listed 1,259 incl. 39 session skills #1221–#1259; numbering below predates this recount — full table regeneration via `skills_staging/regenerate_catalog.py` still pending.)
> Purpose: Single source of truth for all available Azazael skills
> Reconciliation: **the Inventory Summary near the top is stale.** It claims 1,224 while the Skill Quick Reference table holds 1,259 rows and the mirror holds 1,261 entries. Measured numbers, bucket-sum, and the unresolved 2-entry gap are in the final section of this file (2026-09-16).

---

## Inventory Summary

| Metric | Count |
|--------|-------|
| Total canonical skills | 1,224 (recounted 2026-09-14; was stale 1,259) |
| Core skills (non-package) | 136 (133 `azazael-*` + 3 misc) |
| Package skills (Kali 3.13 env, `azazael-pkg-*`) | 968 |
| Package skills (Azazael 3.14t env, `azazael-pkg314t-*`) | 74 |
| Binary-tool skills (`azazael-bin-*`) | 46 |

---

## New Skills — Created September 4, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `desktop-automation-safety` | `.agents/skills/desktop-automation-safety.md` | Safe desktop GUI automation on Windows sessions where other apps (terminal client, Chrome/Facebook, modal dialogs) fight for foreground focus — single-process execution, content-verified focus before ANY keystroke, window-minimize discipline, physical-DPI coordinate handling, keystroke-leak incident protocol, headless-over-GUI preference. Proven 2026-09-04 (Gephi end-to-end verify; Facebook keystroke-leak incident Sep-4(55)). | ✅ Created |

---

## Skill Quick Reference — Core Skills (1-132)
| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 1 | `azazael-autodiff-backprop` | Algorithm / Automatic Differentiation | **Created:** June 14, 2026 |
| 2 | `azazael-autodiff-forward` | Algorithm / Automatic Differentiation | **Created:** June 14, 2026 |
| 3 | `azazael-autodiff-higher-order` | Algorithm / Automatic Differentiation | **Created:** June 14, 2026 |
| 4 | `azazael-autodiff-gradient` | Algorithm / Optimization | **Created:** June 14, 2026 |
| 5 | `azazael-curative` | Architecture | CurativePool 3.14t — CAIN psychological framework, free-threaded agent governance, 3-pool concurrent evalua... |
| 6 | `azazael-packaging` | Deployment | Python packaging insight — Nuitka builds on Python 3.14t free-threading. Strategy for standalone .exe build... |
| 7 | `azazael-platform-deploy` | Deployment | ## Description |
| 8 | `azazael-standalone` | Deployment | AZAZAEL Standalone Suite — 39 independent .exe files for every AZAZAEL function, built with Nuitka. Zero-de... |
| 9 | `azazael-standalone-audit` | Deployment | Desktop Standalone Suite audit — EXE inventory, BAT validation, build system health, naming conventions, er... |
| 10 | `azazael-api-client` | Domain Knowledge | **Created:** June 7, 2026 |
| 11 | `azazael-dead-letter-queue` | Domain Knowledge | **Created:** June 7, 2026 |
| 12 | `azazael-inference-analysis` | Domain Knowledge | **Created:** June 7, 2026 |
| 13 | `azazael-work-stealing` | Domain Knowledge | **Created:** June 7, 2026 |
| 14 | `azazael-worm-analysis` | Domain Knowledge | **Created:** June 7, 2026 |
| 15 | `azazael-gemini-injection` | Gemini | Gemini (`thinker-with-files-gemini`) must be injected into the session lifecycle at minimum 4 times per com... |
| 16 | `azazael-gemini-mandate` | Gemini | ### The Directives: |
| 17 | `azazael-gemini-protocol` | Gemini | The 6-Phase Protocol has been permanently expanded to the **10-Phase Multi-Tier Protocol** to mandate a 400... |
| 18 | `azazael-sync-kali` | Infrastructure | Kali WSL2 sync integration — cross-distro sync via E: drive bridge, run_wsl_kali(), batch copy patterns, ge... |
| 19 | `azazael-wsl-canonical` | Infrastructure | Documents the WSL Ubuntu canonical environment at `/root/azazael/` — a Linux mirror of the Windows 11 produ... |
| 20 | `azazael-deep-analysis` | Mandatory Guardrail | **Created:** June 7, 2026 |
| 21 | `azazael-6api-analysis` | Neural | ## Overview |
| 22 | `azazael-evolutionary-optimization` | Neural | ## Overview |
| 23 | `azazael-inference-providers` | Neural | ## Overview |
| 24 | `azazael-nsga2-testing` | Neural | ## Overview |
| 25 | `azazael-python3.14-ml` | Neural | Python 3.14 free-threading ML compatibility — which packages work, which don't, and how to work within 3.14... |
| 26 | `azazael-system-wiring` | Neural | ## Complete Neural Subsystem Map |
| 27 | `azazael-no-permission-language` | Process | --- |
| 28 | `azazael-mypy-fix-patterns` | Quality | Common mypy fix patterns — no-redef, Optional annotations, type narrowing, float casts, union-attr ignores.... |
| 29 | `azazael-mypy` | Quality / Type Checking | **Created:** June 14, 2026 |
| 30 | `azazael-pyright` | Quality / Type Checking | **Created:** June 14, 2026 |
| 31 | `azazael-codex-studio` | Specialized | CODEX Studio standalone desktop app v3.1 — HTML to MP4/WMV video generation with Tkinter GUI, scene managem... |
| 32 | `azazael-codex-video` | Specialized | CODEX video generation workflow — HTML templates, animation patterns, ffmpeg encoding, PIL frame rendering,... |
| 33 | `azazael-eve-unleashed` | Specialized | Eve Unleashed standalone desktop app — local AI inferencing with Python REPL, system monitor, multi-backend... |
| 34 | `azazael-architecture` | architecture | Azazael project architecture — worm registry, cluster system, paths, module organization. Load when navigat... |
| 35 | `azazael-architecture-review` | architecture | Systematic project architecture review methodology — 3-pass inventory, 12-dimension quality scoring, coupli... |
| 36 | `azazael-auto-downloader-fix` | architecture | AUTO_DOWNLOADER.py main() restructuring fix with CODEX/CORE bug chain documentation |
| 37 | `azazael-cloud-tab` | architecture | Extracted Cloud inference tab module for Inference Studio — reduces God Object anti-pattern |
| 38 | `azazael-clusters` | architecture | Azazael cluster system — ClusterWORMZ v2.0.0 API, NatureClusters, MetaCluster, CrossNatureRoutingEngine, pa... |
| 39 | `azazael-compliance-deep-dive` | architecture | Deep diagnostic of ComplianceOrchestrator self_test — 0X: 8/8 pass, 0Y: 4/5 pass (dual_ledger by-design fai... |
| 40 | `azazael-dlv-divergence` | architecture | DualLedgerValidator expected divergence pattern — why file_edit, file_create, and inference_spawn counts di... |
| 41 | `azazael-dual-ledger` | architecture | DLV discrepancy catalog — all known by-design divergences between DirectMemory and .audit/ JSONL ledgers, b... |
| 42 | `azazael-files` | architecture | Azazael file index — complete module map, what lives where, import resolution, key files by function, file ... |
| 43 | `azazael-parallel` | architecture | Azazael 3.14t parallel execution — FreeThreadPool, work-stealing, batch collection, GIL-free optimization. ... |
| 44 | `azazael-paths` | architecture | Azazael path resolution — centralized dynamic paths via CORE/paths.py, get_project_root, get_g_drive, cachi... |
| 45 | `azazael-registry` | architecture | Azazael worm registry — @register_worm decorator, WORM_REGISTRY dict, discover_worms(), category management... |
| 46 | `azazael-separation` | architecture | Azazael project separation — extraction playbooks, dependency analysis, sub-project inventory, standalone p... |
| 47 | `azazael-state-machine` | architecture | ComplianceStateMachine reference — 7 states, legal transitions, is_in_sequence rules, and the startup wirin... |
| 48 | `azazael-worm-registry` | architecture | Full API reference for worm_registry.py — @register_worm, WORM_REGISTRY, discover_worms() with progress_cal... |
| 49 | `azazael-worm-registry-fixes` | architecture | Worm registry module path fixes — how discover_worms() stores module names incorrectly, the 28 affected wor... |
| 50 | `azazael-worms` | architecture | Azazael worm registry — all 226 worms across 35 categories, @register_worm decorator, how to add/register wo... |
| 51 | `azazael-worms-core` | architecture | Azazael core infrastructure worms — orchestration (6), utility (5), diagnostic (4). Load when working with ... |
| 52 | `azazael-worms-data` | architecture | Azazael data & insight worms — learning (5), ml (2), analysis (3), visualization (5), sync (1). Load when w... |
| 53 | `azazael-worms-devops` | architecture | Azazael DevOps worms — container (5), communication (5), migration (5). Load when working with Docker, IPC,... |
| 54 | `azazael-worms-monitor` | architecture | Azazael observability worms — monitor (6), profiling (5), telemetry (5). Load when working with SystemZ, NE... |
| 55 | `azazael-worms-security` | architecture | Azazael security & integrity worms — security (5), config (5), backup (5). Load when working with VulnScann... |
| 56 | `azazael-cain-pipeline` | codex | CAIN video rendering pipeline — Puppeteer browser capture (NOT PIL), session-specific HTML injection, optim... |
| 57 | `azazael-cain-template` | codex | CAIN template optimization — dead code removal (web-arrows, duplicate sections), CSS animation audit, sessi... |
| 58 | `azazael-codex` | codex | Azazael CODEX systems — video generation with PIL/ffmpeg, PAMS/MemoryBus memory systems, session audit trai... |
| 59 | `azazael-neural-architecture` | codex | Neural architecture reference — RL pipelines (RLTrainLoop, SB3Agent, GRPOTrainer), Mixture of Experts patte... |
| 60 | `azazael-neural-pipeline` | codex | NeuralPipeline v1.0.0 — unified end-to-end ML orchestrator. 6-step lifecycle (Extract → Featurize → Train →... |
| 61 | `azazael-rendering-methods` | codex | **[OBSOLETE MATH]** CAIN video rendering method comparison — see `azazael/CAIN_DELIVERABLE_MATH_2026-06-05.... |
| 62 | `azazael-training-pipeline` | codex | Training data pipeline — ETL (DataPipelineWorm), feature extraction (SchemaAwareFeatureExtractor), RL train... |
| 63 | `azazael-conventions` | conventions | Azazael Python coding conventions — patterns, style rules, import style, error handling patterns, threading... |
| 64 | `azazael-git` | conventions | Azazael git conventions — commit messages, branching strategy, pre-commit checks, CI-ready workflow. Load b... |
| 65 | `azazael-mermaid` | conventions | Azazael Mermaid graph generation — diagram patterns (graph TD, sequenceDiagram), ASCII safety rules, graph ... |
| 66 | `azazael-threading` | conventions | Azazael threading patterns — Python 3.14t free-threading design, threading.Lock, threading.Event, ThreadPoo... |
| 67 | `azazael-devtools-audit` | devtools | Chrome DevTools Lighthouse — performance, accessibility, SEO, best practices auditing. Load when running co... |
| 68 | `azazael-devtools-console` | devtools | Chrome DevTools Console panel — JavaScript error detection, console.log inspection, runtime evaluation. Loa... |
| 69 | `azazael-devtools-coverage` | devtools | Chrome DevTools Coverage panel — unused CSS/JS detection, dead code elimination, payload optimization. Load... |
| 70 | `azazael-devtools-elements` | devtools | Chrome DevTools Elements panel — DOM inspection, CSS validation, layout debugging, selector verification. L... |
| 71 | `azazael-devtools-index` | devtools | Master index for all 7 Chrome DevTools skills. Loads the appropriate DevTools skill(s) based on trigger key... |
| 72 | `azazael-devtools-network` | devtools | Chrome DevTools Network panel — resource loading, broken links, 404 detection, MIME type verification. Load... |
| 73 | `azazael-devtools-performance` | devtools | Chrome DevTools Performance panel — frame rate, animation smoothness, layout thrashing, paint timing. Load ... |
| 74 | `azazael-devtools-sources` | devtools | Chrome DevTools Sources panel — JavaScript debugging, breakpoints, snippet execution, source inspection. Lo... |
| 75 | `azazael-compliance-infrastructure` | domain | RULE 0X + 0Y compliance infrastructure — ComplianceOrchestrator API, 13 components, sentinel_gate.py integr... |
| 76 | `azazael-314t-insights` | environment | Discoveries from 3.14t migration — ABI incompatibility, g++ vs MSVC, ffmpeg workarounds, Go/Node safety, WS... |
| 77 | `azazael-314t-master` | environment | Master reference for Python 3.14t free-threading setup — paths, package status, compiler strategy, video ge... |
| 78 | `azazael-314t-optimum` | environment | Optimum free-threaded agent configuration for Python 3.14t — inference backends, model selection, import st... |
| 79 | `azazael-error-index` | fixes | Master index mapping error symptoms to dedicated fix skill files. Load this first when troubleshooting. |
| 80 | `azazael-fix-data-recording` | fixes | Quick-reference fixes for database and session recording errors — SQLite WAL mode, PAMS fallback, and memor... |
| 81 | `azazael-fix-file-operations` | fixes | Quick-reference fixes for file system and data safety errors — shutil data loss, robocopy timeouts, and cro... |
| 82 | `azazael-fix-gitbash-paths` | fixes | Quick-reference fixes for Git Bash/MSYS2 environment errors — path translation, PowerShell escaping, and sh... |
| 83 | `azazael-fix-protocol-compliance` | fixes | Quick-reference fixes for protocol and compliance errors — process violations, SOP enforcement, and rule ma... |
| 84 | `azazael-fix-python-314t` | fixes | Quick-reference fixes for Python 3.14t free-threading errors — segfaults, wheel issues, Nuitka patches, and... |
| 85 | `azazael-algorithmic-respawn` | governance | Mandate governing code modification algorithms — requires Gemini pre-analysis, per-file validation, and dyn... |
| 86 | `azazael-secrets-manager` | infrastructure | Unified secrets manager for all Azazael API keys — audit, .env management, provider registry, consolidation |
| 87 | `azazael-sync-wsl` | infrastructure | WSL-aware sync_all.py — bidirectional sync (WSL→Windows, WSL→G:), get_env_status + verify_integrity from WS... |
| 88 | `azazael-pams-memory` | memory | Persistent AI memory system — LocalMemoryStore (SQLite), PamsRecorder with local fallback, MemoryBus pub/su... |
| 89 | `azazael-exe-build` | packaging | Nuitka .exe building procedures — Python 3.14t required, patched Nuitka, common gotchas, build.bat patterns... |
| 90 | `azazael-optimization-session` | performance | Lazy import optimization patterns — module splitting, PAMS HTTP cache, fast-path registry discovery. Patter... |
| 91 | `azazael-deploy` | planning | Azazael deployment — Docker, CLI packaging, scheduled runs, G:/ archive, production readiness. Load for dep... |
| 92 | `azazael-desktop-projects` | planning | Complete Desktop project inventory and operability audit — 14 projects, 3 operational, 5 partial, 6 deprecated |
| 93 | `azazael-full-wiring` | planning | Complete AZAZAEL production wiring guide — all 17 areas, 70 tasks, priority ordering, and cross-project int... |
| 94 | `azazael-production` | planning | Azazael production readiness — critical gaps (testing, error recovery, config), high-priority items (perfor... |
| 95 | `azazael-agent-utilization` | process | Agent Utilization Mandate (RULE 0W) — minimum agent spawns per task type, 100% capacity framework, agent cl... |
| 96 | `azazael-catalog-maintenance` | process | SKILLS_CATALOG.md format, numbering convention, Sections pattern, and maintenance procedures for adding new... |
| 97 | `azazael-comprehensive-testing` | process | End-to-end testing procedures for Azazael — compliance self-test, worm health check, mypy audit, import ver... |
| 98 | `azazael-dedup` | process | Deduplication procedures — MD5 hash comparison, duplicate file detection, deprecation shim creation, cleanu... |
| 99 | `azazael-error-prevention` | process | Anti-patterns, prevention checklists, and process guardrails to prevent repeating costly mistakes. Covers b... |
| 100 | `azazael-inference-protocol` | process | Inference Protocol (RULE 0D/0Z-A) — 12-provider automatic failover chain, auto-fallback procedure when thin... |
| 101 | `azazael-interpreters` | process | INTERPRETERS — Go and Rust language runners for executing non-Python code within the Azazael ecosystem. 3 .... |
| 102 | `azazael-ml-platforms` | process | ML platform infrastructure — LM Studio integration, Q-learning, ONNX, Ray, harness, diagnostics, health mon... |
| 103 | `azazael-model-compression` | process | Model compression techniques — quantization (GPTQ, AWQ, GGUF), knowledge distillation, and pruning. Integra... |
| 104 | `azazael-shims` | process | Deprecation shim pattern — when to create shims, how to use FutureWarning, re-export patterns, testing proc... |
| 105 | `azazael-sync-patterns` | process | Sync infrastructure — sync_all.py and sync_skills.py patterns. 5 environments, 178+ files, integrity checks... |
| 106 | `azazael-todo-management` | process | TODO document management methodology — versioning strategy, cross-referencing, ADDITIVE/REINFORCES/DUPLICAT... |
| 107 | `azazael-tools` | process | TOOLS directory — debug_runner (multi-agent test runner), archive_system (file archiving), COMPREHENSIVE_FI... |
| 108 | `azazael-utilities` | process | UTILITIES sub-systems catalog — KLINK, PERSEPHONE (environment/sync), POINDEXTER (indexing), TARBABY (file ... |
| 109 | `azazael-audit-infrastructure` | quality | VLP 15-layer audit trail system — .audit/ JSONL hash-chained sessions, DirectMemory dual-ledger cross-valid... |
| 110 | `azazael-crossplat-fileops` | quality | Safe Windows file operations from Git Bash/bash environment — avoid path escaping, data loss, and timeout i... |
| 111 | `azazael-error-resolution` | quality | Sequential error resolution decision tree for systematic troubleshooting. Load when encountering ANY error ... |
| 112 | `azazael-powershell-escape` | quality | Safe PowerShell command patterns from basher/Git Bash — avoid cmdlet escaping, $variable mangling, and pars... |
| 113 | `azazael-session-recording` | quality | Session recording — DEPRECATED: CodebuffTracker and SessionRecorder are hard-blocked. Use DirectMemory (COR... |
| 114 | `azazael-compliance-orchestrator` | system | Automated Compliance Infrastructure (RULE 0X/0Y) — 13 compliance components, policy engine, formal verifier... |
| 115 | `azazael-direct-memory` | system | DirectMemory — Canonical session recording system. Stdlib-only, <0.1s init, WAL mode, signal-safe, atexit-s... |
| 116 | `azazael-mandates` | system | Complete Codification of ALL active mandates — 37 total (31 RULEs 0A-0Z-C + 1 mandatory enforcement mechani... |
| 117 | `azazael-neural-integration` | system | Cross-system integration architecture — data flow, training-to-deployment pipeline, and coupling points bet... |
| 118 | `azazael-orchestration` | system | ORCHESTRATION + HYDRA systems — ecosystem crawler, HORUS monitoring, HYDRA adaptive ML cluster, ML platform... |
| 119 | `azazael-pre-action-gate` | system | PERMANENT PRE-ACTION GATE (RULE 0J/0S) — 13-question mandatory assertion block. MUST be printed before EVER... |
| 120 | `azazael-sentinel-gate` | system | COMPLIANCE SENTINEL (RULE 0C/0S) — Mandatory PRE-ACTION AUTHORIZATION GATE. 25-item self-audit checklist. N... |
| 121 | `azazael-sop` | system | Standard Operating Procedure — ALL canonical mandates (RULEs 0A-0Z, Rule 0, COMPLIANCE SENTINEL), error rec... |
| 122 | `azazael-system-startup` | system | Auto-load startup instructions for coding session congruency. Mandatory file reading order, skill loading s... |
| 123 | `azazael-toolkit` | system | AZAZAEL_TOOLKIT — core framework, QL analysis, environment manager, comprehensive fix tools. 7 .py files fo... |
| 124 | `azazael-verifiable-truth` | system | Verifiable Truth Mandate (RULE 0T/0T-A/0T-B) — 15-layer VLP verification stack, audit trail format, Ed25519... |
| 125 | `azazael-testing` | testing | Azazael testing conventions — syntax check, integration test, worm config trace, code review. Load when val... |
| 126 | `azazael-autoflake` | tooling | Free-threaded autoflake wrapper for Python 3.14t — batch unused import detection, removal, and reporting. C... |
| 127 | `azazael-eleven-followups` | workflow | RULE 0Z-B — Mandates exactly 11 followup suggestions at the end of EVERY assistant response. Permanent, nev... |
| 128 | `azazael-environment` | workflow | Azazael environment setup — Python 3.10+/3.14t requirements, dependency installation, project path configur... |
| 129 | `azazael-operating-protocols` | workflow | Operating protocols for Codebuff/AI agents working on Azazael — 11 followups mandate, max parallel agent ex... |
| 130 | `azazael-parallel-execution` | workflow | RULE 0Z-F — Parallel Agent Execution Mandate. Maximum concurrency, batch all independent work into single s... |
| 131 | `azazael-parallel-execution-quickref` | workflow | Quick-reference cheat sheet for RULE 0Z-F Parallel Agent Execution — anti-pattern table, agent spawn patter... |
| 132 | `azazael-startup` | workflow | Reference catalog for Azazael sessions. 24-skill catalog, environment setup, project numbers. Delegates sta... |

## Skill Quick Reference — Kali Package Skills (133-1100)
| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 133 | `azazael-pkg-aadict` | packages | Callable skill for Python package aadict 0.2.3 — An auto-attribute dict (and a couple of other useful dict ... |
| 134 | `azazael-pkg-about-time` | packages | Callable skill for Python package about-time 4.2.1 — Easily measure timing and throughput of code blocks, w... |
| 135 | `azazael-pkg-above` | packages | Callable skill for Python package above 2.8.1 — Network Security Sniffer |
| 136 | `azazael-pkg-acstore` | packages | Callable skill for Python package acstore 20240407 — Attribute Container Storage (ACStore). |
| 137 | `azazael-pkg-adblockparser` | packages | Callable skill for Python package adblockparser 0.7 — Parser for Adblock Plus rules |
| 138 | `azazael-pkg-aesedb` | packages | Callable skill for Python package aesedb 0.1.4 — NTDS parser toolkit |
| 139 | `azazael-pkg-aiocmd` | packages | Callable skill for Python package aiocmd 0.1.2 — Coroutine-based CLI generator using prompt_toolkit |
| 140 | `azazael-pkg-aioconsole` | packages | Callable skill for Python package aioconsole 0.8.2 — Asynchronous console and interfaces for asyncio |
| 141 | `azazael-pkg-aiodns` | packages | Callable skill for Python package aiodns 4.0.0 — Simple DNS resolver for asyncio |
| 142 | `azazael-pkg-aiofiles` | packages | Callable skill for Python package aiofiles 25.1.0 — File support for asyncio. |
| 143 | `azazael-pkg-aioftp` | packages | Callable skill for Python package aioftp 0.27.2 — ftp client/server for asyncio |
| 144 | `azazael-pkg-aiohappyeyeballs` | packages | Callable skill for Python package aiohappyeyeballs 2.7.0 — Happy Eyeballs for asyncio |
| 145 | `azazael-pkg-aiohttp` | packages | Callable skill for Python package aiohttp 3.13.5 — Async http client/server framework (asyncio) |
| 146 | `azazael-pkg-aiohttp-apispec` | packages | Callable skill for Python package aiohttp-apispec 3.0.0b2 — Build and document REST APIs with aiohttp and a... |
| 147 | `azazael-pkg-aiohttp-jinja2` | packages | Callable skill for Python package aiohttp-jinja2 1.6 — jinja2 template renderer for aiohttp.web (http serve... |
| 148 | `azazael-pkg-aiohttp-security` | packages | Callable skill for Python package aiohttp-security 0.5.0 — security for aiohttp.web |
| 149 | `azazael-pkg-aiohttp-session` | packages | Callable skill for Python package aiohttp-session 2.12.1 — sessions for aiohttp.web |
| 150 | `azazael-pkg-aiohttp-socks` | packages | Callable skill for Python package aiohttp_socks 0.10.1 — Proxy connector for aiohttp |
| 151 | `azazael-pkg-aiomultiprocess` | packages | Callable skill for Python package aiomultiprocess 0.9.0 — AsyncIO version of the standard multiprocessing m... |
| 152 | `azazael-pkg-aioquic` | packages | Callable skill for Python package aioquic 1.2.0 — An implementation of QUIC and HTTP/3 |
| 153 | `azazael-pkg-aiosignal` | packages | Callable skill for Python package aiosignal 1.4.0 — aiosignal: a list of registered asynchronous callbacks |
| 154 | `azazael-pkg-aiosmb` | packages | Callable skill for Python package aiosmb 0.4.4 — Asynchronous SMB protocol implementation |
| 155 | `azazael-pkg-aiosqlite` | packages | Callable skill for Python package aiosqlite 0.21.0 — asyncio bridge to the standard sqlite3 module |
| 156 | `azazael-pkg-aiowinreg` | packages | Callable skill for Python package aiowinreg 0.0.7 — Windows registry file reader |
| 157 | `azazael-pkg-ajpy` | packages | Callable skill for Python package ajpy 0.0.5 — AJP package crafting library |
| 158 | `azazael-pkg-alabaster` | packages | Callable skill for Python package alabaster 1.0.0 — A light, configurable Sphinx theme |
| 159 | `azazael-pkg-alive-progress` | packages | Callable skill for Python package alive-progress 3.2.0 — A new kind of Progress Bar, with real-time through... |
| 160 | `azazael-pkg-altgraph` | packages | Callable skill for Python package altgraph 0.17.5 — Python graph (network) package |
| 161 | `azazael-pkg-aniso8601` | packages | Callable skill for Python package aniso8601 10.0.1 — A library for parsing ISO 8601 strings. |
| 162 | `azazael-pkg-annotated-doc` | packages | Callable skill for Python package annotated-doc 0.0.4 — Document parameters, class attributes, return types... |
| 163 | `azazael-pkg-annotated-types` | packages | Callable skill for Python package annotated-types 0.7.0 — Reusable constraint types to use with typing.Anno... |
| 164 | `azazael-pkg-antlr4-python3-runtime` | packages | Callable skill for Python package antlr4-python3-runtime 4.9.2 — ANTLR 4.9.2 runtime for Python 3.7 |
| 165 | `azazael-pkg-anyio` | packages | Callable skill for Python package anyio 4.12.1 — High-level concurrency and networking framework on top of ... |
| 166 | `azazael-pkg-apispec` | packages | Callable skill for Python package apispec 6.10.0 — A pluggable API specification generator. Currently suppo... |
| 167 | `azazael-pkg-arc4` | packages | Callable skill for Python package arc4 0.4.0 — A small and insanely fast ARCFOUR (RC4) cipher implementatio... |
| 168 | `azazael-pkg-argcomplete` | packages | Callable skill for Python package argcomplete 3.6.3 — Bash tab completion for argparse |
| 169 | `azazael-pkg-argon2-cffi` | packages | Callable skill for Python package argon2-cffi 25.1.0 — Argon2 for Python |
| 170 | `azazael-pkg-argon2-cffi-bindings` | packages | Callable skill for Python package argon2-cffi-bindings 25.1.0 — Low-level CFFI bindings for Argon2 |
| 171 | `azazael-pkg-arjun` | packages | Callable skill for Python package arjun 2.2.7 — HTTP parameter discovery suite |
| 172 | `azazael-pkg-arpy` | packages | Callable skill for Python package arpy 1.1.1 — Library for accessing "ar" files |
| 173 | `azazael-pkg-arrow` | packages | Callable skill for Python package arrow 1.4.0 — Better dates & times for Python |
| 174 | `azazael-pkg-artifacts` | packages | Callable skill for Python package artifacts 20230928 — ForensicArtifacts.com Artifact Repository. |
| 175 | `azazael-pkg-asciitree` | packages | Callable skill for Python package asciitree 0.3.3 — Draws ASCII trees. |
| 176 | `azazael-pkg-asgiref` | packages | Callable skill for Python package asgiref 3.11.1 — ASGI specs, helper code, and adapters |
| 177 | `azazael-pkg-asn1crypto` | packages | Callable skill for Python package asn1crypto 1.5.1 — Fast ASN.1 parser and serializer with definitions for ... |
| 178 | `azazael-pkg-asn1tools` | packages | Callable skill for Python package asn1tools 0.166.0 — ASN.1 parsing, encoding and decoding. |
| 179 | `azazael-pkg-asset` | packages | Callable skill for Python package asset 0.6.13 — A package resource and symbol loading helper library. |
| 180 | `azazael-pkg-astroid` | packages | Callable skill for Python package astroid 4.1.1 — An abstract syntax tree for Python with inference support. |
| 181 | `azazael-pkg-asttokens` | packages | Callable skill for Python package asttokens 3.0.1 — Annotate AST trees with source code positions |
| 182 | `azazael-pkg-asyauth` | packages | Callable skill for Python package asyauth 0.0.20 — Unified authentication library |
| 183 | `azazael-pkg-async-timeout` | packages | Callable skill for Python package async-timeout 5.0.1 — Timeout context manager for asyncio programs |
| 184 | `azazael-pkg-asyncssh` | packages | Callable skill for Python package asyncssh 2.23.0 — AsyncSSH: Asynchronous SSHv2 client and server library |
| 185 | `azazael-pkg-asysocks` | packages | Callable skill for Python package asysocks 0.2.12 — No summary available. |
| 186 | `azazael-pkg-atomic-operator` | packages | Callable skill for Python package atomic-operator 0.9.1 — A python package to execute security tests on rem... |
| 187 | `azazael-pkg-atomic-operator-runner` | packages | Callable skill for Python package atomic-operator-runner 0.2.1 — atomic-operator-runner |
| 188 | `azazael-pkg-attrs` | packages | Callable skill for Python package attrs 26.1.0 — Classes Without Boilerplate |
| 189 | `azazael-pkg-autocommand` | packages | Callable skill for Python package autocommand 2.2.2 — A library to create a command-line program from a fun... |
| 190 | `azazael-pkg-automat` | packages | Callable skill for Python package Automat 25.4.16 — Self-service finite-state machines for the programmer o... |
| 191 | `azazael-pkg-awscli` | packages | Callable skill for Python package awscli 2.31.35 — Universal Command Line Environment for AWS. |
| 192 | `azazael-pkg-awscrt` | packages | Callable skill for Python package awscrt 1.0.0.dev0 — A common runtime for AWS Python projects |
| 193 | `azazael-pkg-babel` | packages | Callable skill for Python package babel 2.17.0 — Internationalization utilities |
| 194 | `azazael-pkg-backoff` | packages | Callable skill for Python package backoff 2.2.1 — Function decoration for backoff and retry |
| 195 | `azazael-pkg-backports-zstd` | packages | Callable skill for Python package backports.zstd 1.5.0 — Backport of compression.zstd |
| 196 | `azazael-pkg-bcrypt` | packages | Callable skill for Python package bcrypt 5.0.0 — Modern password hashing for your software and your servers |
| 197 | `azazael-pkg-beautifulsoup4` | packages | Callable skill for Python package beautifulsoup4 4.14.3 — Screen-scraping library |
| 198 | `azazael-pkg-bidict` | packages | Callable skill for Python package bidict 0.23.1 — The bidirectional mapping library for Python. |
| 199 | `azazael-pkg-binwalk` | packages | Callable skill for Python package binwalk 2.4.3 — Firmware analysis tool |
| 200 | `azazael-pkg-bitstruct` | packages | Callable skill for Python package bitstruct 8.22.1 — This module performs conversions between Python values... |
| 201 | `azazael-pkg-blinker` | packages | Callable skill for Python package blinker 1.9.0 — Fast, simple object-to-object and broadcast signaling |
| 202 | `azazael-pkg-bloodhound` | packages | Callable skill for Python package bloodhound 1.9.0 — Python based ingestor for BloodHound |
| 203 | `azazael-pkg-bloodhound-ce` | packages | Callable skill for Python package bloodhound-ce 1.9.1 — Python based ingestor for BloodHound Community Edition |
| 204 | `azazael-pkg-blosc` | packages | Callable skill for Python package blosc 1.11.2 — Blosc data compressor |
| 205 | `azazael-pkg-bluepy` | packages | Callable skill for Python package bluepy 1.3.0 — Python module for interfacing with BLE devices through Bluez |
| 206 | `azazael-pkg-bopscrk` | packages | Callable skill for Python package bopscrk 2.4.7 — Generate smart and powerful wordlists |
| 207 | `azazael-pkg-boto3` | packages | Callable skill for Python package boto3 1.40.72 — The AWS SDK for Python |
| 208 | `azazael-pkg-botocore` | packages | Callable skill for Python package botocore 1.40.72 — Low-level, data-driven core of boto 3. |
| 209 | `azazael-pkg-bottle` | packages | Callable skill for Python package bottle 0.13.2 — Fast and simple WSGI-framework for small web-applications. |
| 210 | `azazael-pkg-bottleneck` | packages | Callable skill for Python package Bottleneck 1.4.2 — Fast NumPy array functions written in C |
| 211 | `azazael-pkg-brotli` | packages | Callable skill for Python package Brotli 1.2.0 — Python bindings for the Brotli compression library |
| 212 | `azazael-pkg-browser-cookie3` | packages | Callable skill for Python package browser-cookie3 0.20.1 — Loads cookies from your browser into a cookiejar... |
| 213 | `azazael-pkg-cairocffi` | packages | Callable skill for Python package cairocffi 1.7.1 — cffi-based cairo bindings for Python |
| 214 | `azazael-pkg-capstone` | packages | Callable skill for Python package capstone 5.0.7 — Capstone disassembly engine |
| 215 | `azazael-pkg-censys` | packages | Callable skill for Python package censys 2.2.19 — An easy-to-use and lightweight API wrapper for Censys API... |
| 216 | `azazael-pkg-cerberus` | packages | Callable skill for Python package Cerberus 1.3.7 — Lightweight, extensible schema and data validation tool ... |
| 217 | `azazael-pkg-certi` | packages | Callable skill for Python package certi 0.1.0 — Tool to ask certificates to ADCS and discover templates |
| 218 | `azazael-pkg-certifi` | packages | Callable skill for Python package certifi 2026.5.20 — Python package for providing Mozilla's CA Bundle. |
| 219 | `azazael-pkg-certipy-ad` | packages | Callable skill for Python package certipy-ad 5.0.4 — Active Directory Certificate Services enumeration and ... |
| 220 | `azazael-pkg-cffi` | packages | Callable skill for Python package cffi 2.0.0 — Foreign Function Interface for Python calling C code. |
| 221 | `azazael-pkg-cfscrape` | packages | Callable skill for Python package cfscrape 1.9.5 — A simple Python module to bypass Cloudflare's anti-bot p... |
| 222 | `azazael-pkg-chardet` | packages | Callable skill for Python package chardet 5.2.0 — Universal encoding detector for Python 3 |
| 223 | `azazael-pkg-charset-normalizer` | packages | Callable skill for Python package charset-normalizer 3.4.7 — The Real First Universal Charset Detector. Ope... |
| 224 | `azazael-pkg-cheroot` | packages | Callable skill for Python package cheroot 11.1.2+ds1 — Highly-optimized, pure-python HTTP server |
| 225 | `azazael-pkg-cherrypy` | packages | Callable skill for Python package CherryPy 18.10.0 — Object-Oriented HTTP framework |
| 226 | `azazael-pkg-cherrypy-cors` | packages | Callable skill for Python package cherrypy-cors 1.6 — CORS handling as a cherrypy tool. |
| 227 | `azazael-pkg-chirp` | packages | Callable skill for Python package chirp 20251108 — A cross-platform cross-radio programming tool |
| 228 | `azazael-pkg-click` | packages | Callable skill for Python package click 8.1.8 — Composable command line interface toolkit |
| 229 | `azazael-pkg-click-default-group` | packages | Callable skill for Python package click-default-group 1.2.4 — click_default_group |
| 230 | `azazael-pkg-cloudpickle` | packages | Callable skill for Python package cloudpickle 3.1.2 — Pickler class to extend the standard pickle.Pickler f... |
| 231 | `azazael-pkg-cloudscraper` | packages | Callable skill for Python package cloudscraper 1.2.71 — A Python module to bypass Cloudflare's anti-bot page. |
| 232 | `azazael-pkg-coercer` | packages | Callable skill for Python package coercer 2.4.3 — No summary available. |
| 233 | `azazael-pkg-colorama` | packages | Callable skill for Python package colorama 0.4.6 — Cross-platform colored terminal text. |
| 234 | `azazael-pkg-colorclass` | packages | Callable skill for Python package colorclass 2.2.2 — Colorful worry-free console applications for Linux, Ma... |
| 235 | `azazael-pkg-colored-traceback` | packages | Callable skill for Python package colored-traceback 0.4.2 — Automatically color uncaught exception tracebacks |
| 236 | `azazael-pkg-colorlog` | packages | Callable skill for Python package colorlog 6.10.1 — Add colours to the output of Python's logging module. |
| 237 | `azazael-pkg-commandparse` | packages | Callable skill for Python package commandparse 1.1.2 — CLI application commands parser |
| 238 | `azazael-pkg-commonmark` | packages | Callable skill for Python package commonmark 0.9.1 — Python parser for the CommonMark Markdown spec |
| 239 | `azazael-pkg-condense-json` | packages | Callable skill for Python package condense-json 0.1.3 — Python function for condensing JSON using replaceme... |
| 240 | `azazael-pkg-configargparse` | packages | Callable skill for Python package ConfigArgParse 1.7 — A drop-in replacement for argparse that allows optio... |
| 241 | `azazael-pkg-constantly` | packages | Callable skill for Python package constantly 23.10.4 — Symbolic constants in Python |
| 242 | `azazael-pkg-contourpy` | packages | Callable skill for Python package contourpy 1.3.3 — Python library for calculating contours of 2D quadrilat... |
| 243 | `azazael-pkg-crackmapexec` | packages | Callable skill for Python package crackmapexec 5.4.0 — A swiss army knife for pentesting networks |
| 244 | `azazael-pkg-crcelk` | packages | Callable skill for Python package crcelk 1.3 — CrcElk is an updated fork of the CrcMoose module for recent ... |
| 245 | `azazael-pkg-crit` | packages | Callable skill for Python package crit 4.2 — CRiu Image Tool |
| 246 | `azazael-pkg-croniter` | packages | Callable skill for Python package croniter 6.0.0 — croniter provides iteration for datetime object with cro... |
| 247 | `azazael-pkg-crowbar` | packages | Callable skill for Python package crowbar 4.1 — No summary available. |
| 248 | `azazael-pkg-cryptography` | packages | Callable skill for Python package cryptography 46.0.7 — cryptography is a package which provides cryptograp... |
| 249 | `azazael-pkg-cssselect` | packages | Callable skill for Python package cssselect 1.4.0 — cssselect parses CSS3 Selectors and translates them to ... |
| 250 | `azazael-pkg-cssselect2` | packages | Callable skill for Python package cssselect2 0.9.0 — CSS selectors for Python ElementTree |
| 251 | `azazael-pkg-ctypescrypto` | packages | Callable skill for Python package ctypescrypto 0.5 — CTypes-based interface for some OpenSSL libcrypto feat... |
| 252 | `azazael-pkg-cupshelpers` | packages | Callable skill for Python package cupshelpers 1.0 — Helper functions and classes for using CUPS |
| 253 | `azazael-pkg-cx-oracle` | packages | Callable skill for Python package cx_Oracle 8.3.0 — Python interface to Oracle |
| 254 | `azazael-pkg-cycler` | packages | Callable skill for Python package cycler 0.12.1 — Composable style cycles |
| 255 | `azazael-pkg-dacite` | packages | Callable skill for Python package dacite 1.9.2 — Simple creation of data classes from dictionaries. |
| 256 | `azazael-pkg-dask` | packages | Callable skill for Python package dask 2024.12.1+dfsg — Parallel PyData with Task Scheduling |
| 257 | `azazael-pkg-dbus-python` | packages | Callable skill for Python package dbus-python 1.4.0 — Python bindings for libdbus |
| 258 | `azazael-pkg-decorator` | packages | Callable skill for Python package decorator 5.2.1 — Decorators for Humans |
| 259 | `azazael-pkg-defusedcsv` | packages | Callable skill for Python package defusedcsv 3.0.0 — Drop-in replacement for Python's CSV library that trie... |
| 260 | `azazael-pkg-defusedxml` | packages | Callable skill for Python package defusedxml 0.7.1 — XML bomb protection for Python stdlib modules |
| 261 | `azazael-pkg-deprecated` | packages | Callable skill for Python package Deprecated 1.3.1 — Python @deprecated decorator to deprecate old python c... |
| 262 | `azazael-pkg-dfdatetime` | packages | Callable skill for Python package dfdatetime 20251018 — Digital Forensics date and time (dfDateTime). |
| 263 | `azazael-pkg-dfvfs` | packages | Callable skill for Python package dfvfs 20251019 — Digital Forensics Virtual File System (dfVFS). |
| 264 | `azazael-pkg-dfwinreg` | packages | Callable skill for Python package dfwinreg 20240316 — Digital Forensics Windows Registry (dfWinReg). |
| 265 | `azazael-pkg-dhcpig` | packages | Callable skill for Python package dhcpig 0.0.0 — DHCP exhaustion script using scapy network library |
| 266 | `azazael-pkg-dhcplib` | packages | Callable skill for Python package dhcplib 0.1.1 — Pure-Python, spec-compliant DHCP-packet-processing library |
| 267 | `azazael-pkg-dicttoxml` | packages | Callable skill for Python package dicttoxml 1.7.16 — Converts a Python dictionary or other native data type... |
| 268 | `azazael-pkg-dirsearch` | packages | Callable skill for Python package dirsearch 0.4.3 — Advanced web path scanner |
| 269 | `azazael-pkg-diskcache` | packages | Callable skill for Python package diskcache 5.6.3 — Disk Cache -- Disk and file backed persistent cache. |
| 270 | `azazael-pkg-dissect-cstruct` | packages | Callable skill for Python package dissect.cstruct 0.0.0 — A Dissect module implementing a parser for C-like... |
| 271 | `azazael-pkg-distlib` | packages | Callable skill for Python package distlib 0.4.0 — Distribution utilities |
| 272 | `azazael-pkg-distorm3` | packages | Callable skill for Python package distorm3 3.5.2 — The goal of diStorm3 is to decode x86/AMD64 binary strea... |
| 273 | `azazael-pkg-distributed` | packages | Callable skill for Python package distributed 2024.12.1 — Distributed scheduler for Dask |
| 274 | `azazael-pkg-distro` | packages | Callable skill for Python package distro 1.9.0 — Distro - an OS platform information API |
| 275 | `azazael-pkg-django` | packages | Callable skill for Python package Django 4.2.30 — A high-level Python web framework that encourages rapid d... |
| 276 | `azazael-pkg-dnsgen` | packages | Callable skill for Python package dnsgen 1.0.4 — Generates DNS possibilities from existing domain names. |
| 277 | `azazael-pkg-dnslib` | packages | Callable skill for Python package dnslib 0.9.25 — Simple library to encode/decode DNS wire-format packets |
| 278 | `azazael-pkg-dnspython` | packages | Callable skill for Python package dnspython 2.8.0 — DNS toolkit |
| 279 | `azazael-pkg-dnstwist` | packages | Callable skill for Python package dnstwist 20250130 — Domain name permutation engine for detecting homograp... |
| 280 | `azazael-pkg-docker` | packages | Callable skill for Python package docker 7.1.0 — A Python library for the Docker Engine API. |
| 281 | `azazael-pkg-docopt` | packages | Callable skill for Python package docopt 0.6.2 — Pythonic argument parser, that will make you smile |
| 282 | `azazael-pkg-docutils` | packages | Callable skill for Python package docutils 0.22.4 — Docutils -- Python Documentation Utilities |
| 283 | `azazael-pkg-docxcompose` | packages | Callable skill for Python package docxcompose 2.2.0 — Compose .docx documents |
| 284 | `azazael-pkg-docxtpl` | packages | Callable skill for Python package docxtpl 0.20.1 — Python docx template engine |
| 285 | `azazael-pkg-donut-shellcode` | packages | Callable skill for Python package donut-shellcode 1.1 — Donut shellcode Python C extension |
| 286 | `azazael-pkg-dploot` | packages | Callable skill for Python package dploot 3.1.2 — DPAPI looting remotely in Python |
| 287 | `azazael-pkg-dronekit` | packages | Callable skill for Python package dronekit 2.9.2 — Developer Tools for Drones. |
| 288 | `azazael-pkg-dropbox` | packages | Callable skill for Python package dropbox 12.0.2 — Official Dropbox API Client |
| 289 | `azazael-pkg-dscan-4e656f` | packages | Callable skill for Python package dscan-4E656F 0.1.5 — ('Wrapper around nmap allow nmap scans to be distrib... |
| 290 | `azazael-pkg-dsinternals` | packages | Callable skill for Python package dsinternals 1.2.4 — No summary available. |
| 291 | `azazael-pkg-dsnap` | packages | Callable skill for Python package dsnap 1.0.1 — Utility for downloading EBS snapshots using the EBS Direct ... |
| 292 | `azazael-pkg-dtfabric` | packages | Callable skill for Python package dtfabric 20251118 — Data type fabric (dtfabric) |
| 293 | `azazael-pkg-duckpy` | packages | Callable skill for Python package duckpy 3.2.0 — A simple module for searching on DuckDuckGo |
| 294 | `azazael-pkg-dunamai` | packages | Callable skill for Python package dunamai 1.25.0 — Dynamic version generation |
| 295 | `azazael-pkg-easygui` | packages | Callable skill for Python package easygui 0.98.3 — EasyGUI is a module for very simple, very easy GUI progr... |
| 296 | `azazael-pkg-elastic-transport` | packages | Callable skill for Python package elastic-transport 9.4.1 — Transport classes and utilities shared among Py... |
| 297 | `azazael-pkg-elasticsearch` | packages | Callable skill for Python package elasticsearch 9.4.1 — Python client for Elasticsearch |
| 298 | `azazael-pkg-email-validator` | packages | Callable skill for Python package email_validator 2.2.0 — A robust email address syntax and deliverability ... |
| 299 | `azazael-pkg-enum4linux-ng` | packages | Callable skill for Python package enum4linux-ng 1.3.10 — A next generation version of enum4linux |
| 300 | `azazael-pkg-envs` | packages | Callable skill for Python package envs 1.2.6 — Easy access of environment variables from Python with suppor... |
| 301 | `azazael-pkg-et-xmlfile` | packages | Callable skill for Python package et_xmlfile 2.0.0 — An implementation of lxml.xmlfile for the standard lib... |
| 302 | `azazael-pkg-evdev` | packages | Callable skill for Python package evdev 1.9.3 — Bindings to the Linux input handling subsystem |
| 303 | `azazael-pkg-eventlet` | packages | Callable skill for Python package eventlet 0.40.4 — Highly concurrent networking library |
| 304 | `azazael-pkg-evil-winrm-py` | packages | Callable skill for Python package evil-winrm-py 1.6.0 — Execute commands interactively on remote Windows ma... |
| 305 | `azazael-pkg-executing` | packages | Callable skill for Python package executing 2.2.1 — Get the currently executing AST node of a frame, and ot... |
| 306 | `azazael-pkg-exifread` | packages | Callable skill for Python package ExifRead 3.0.0 — Read Exif metadata from tiff and jpeg files. |
| 307 | `azazael-pkg-extproxy` | packages | Callable skill for Python package ExtProxy 1.0.2 — ExtProxy extend urllib2's ProxyHandler to support extra ... |
| 308 | `azazael-pkg-fake-useragent` | packages | Callable skill for Python package fake-useragent 2.2.0 — Up-to-date simple useragent faker with real world ... |
| 309 | `azazael-pkg-faker` | packages | Callable skill for Python package Faker 39.0.0 — Faker is a Python package that generates fake data for you. |
| 310 | `azazael-pkg-faraday-agent-dispatcher` | packages | Callable skill for Python package faraday-agent-dispatcher 3.2.1 — Faraday agent dispatcher to communicate ... |
| 311 | `azazael-pkg-faraday-agent-parameters-types` | packages | Callable skill for Python package faraday_agent_parameters_types 1.9.1 — The faraday agents run code remote... |
| 312 | `azazael-pkg-faraday-plugins` | packages | Callable skill for Python package faraday_plugins 1.27.2 — Faraday plugins package |
| 313 | `azazael-pkg-fastapi` | packages | Callable skill for Python package fastapi 0.135.3 — FastAPI framework, high performance, easy to learn, fas... |
| 314 | `azazael-pkg-fastjsonschema` | packages | Callable skill for Python package fastjsonschema 2.21.1 — Fastest Python implementation of JSON schema |
| 315 | `azazael-pkg-feedparser` | packages | Callable skill for Python package feedparser 6.0.12 — Universal feed parser, handles RSS 0.9x, RSS 1.0, RSS... |
| 316 | `azazael-pkg-fierce` | packages | Callable skill for Python package fierce 1.6.0 — A DNS reconnaissance tool for locating non-contiguous IP s... |
| 317 | `azazael-pkg-filebytes` | packages | Callable skill for Python package filebytes 0.10.2 — Scripts to parse the following file formats - Executab... |
| 318 | `azazael-pkg-filelock` | packages | Callable skill for Python package filelock 3.29.0 — A platform independent file lock. |
| 319 | `azazael-pkg-fire` | packages | Callable skill for Python package fire 0.7.1 — A library for automatically generating command line interfaces. |
| 320 | `azazael-pkg-flasgger` | packages | Callable skill for Python package flasgger 0.9.7.2.dev2 — Extract swagger specs from your flask project |
| 321 | `azazael-pkg-flask` | packages | Callable skill for Python package Flask 3.1.3 — A simple framework for building complex web applications. |
| 322 | `azazael-pkg-flask-jsglue` | packages | Callable skill for Python package Flask-JSGlue 0.3.1 — Flask-JSGlue helps hook up your Flask application ni... |
| 323 | `azazael-pkg-flask-restful` | packages | Callable skill for Python package Flask-RESTful 0.3.10 — Simple framework for creating REST APIs |
| 324 | `azazael-pkg-flask-socketio` | packages | Callable skill for Python package Flask-SocketIO 5.6.0 — Socket.IO integration for Flask applications |
| 325 | `azazael-pkg-fleep` | packages | Callable skill for Python package fleep 1.0.1 — File format determination library |
| 326 | `azazael-pkg-flor` | packages | Callable skill for Python package Flor 1.1.3 — Flor - An efficient Bloom filter implementation in Python |
| 327 | `azazael-pkg-fonttools` | packages | Callable skill for Python package fonttools 4.62.1 — Tools to manipulate font files |
| 328 | `azazael-pkg-fpdf2` | packages | Callable skill for Python package fpdf2 2.8.7 — Simple & fast PDF generation for Python |
| 329 | `azazael-pkg-fqdn` | packages | Callable skill for Python package fqdn 1.5.1 — Validates fully-qualified domain names against RFC 1123, so ... |
| 330 | `azazael-pkg-freetype-py` | packages | Callable skill for Python package freetype-py 2.5.1 — Freetype python bindings |
| 331 | `azazael-pkg-freezegun` | packages | Callable skill for Python package freezegun 1.5.5 — Let your Python tests travel through time |
| 332 | `azazael-pkg-frozenlist` | packages | Callable skill for Python package frozenlist 1.8.0 — A list-like structure which implements collections.abc... |
| 333 | `azazael-pkg-fs` | packages | Callable skill for Python package fs 2.4.16 — Python's filesystem abstraction layer |
| 334 | `azazael-pkg-fsspec` | packages | Callable skill for Python package fsspec 2025.12.0 — File-system specification |
| 335 | `azazael-pkg-fuzzywuzzy` | packages | Callable skill for Python package fuzzywuzzy 0.18.0 — Fuzzy string matching in python |
| 336 | `azazael-pkg-gattlib` | packages | Callable skill for Python package gattlib 0.20210616 — Library to access Bluetooth LE devices |
| 337 | `azazael-pkg-gdal` | packages | Callable skill for Python package GDAL 3.13.1 — GDAL: Geospatial Data Abstraction Library |
| 338 | `azazael-pkg-gensim` | packages | Callable skill for Python package gensim 4.3.3 — Python framework for fast Vector Space Modelling |
| 339 | `azazael-pkg-geoip` | packages | Callable skill for Python package GeoIP 1.3.2 — MaxMind GeoIP Legacy Database - Python API |
| 340 | `azazael-pkg-geoip2` | packages | Callable skill for Python package geoip2 2.9.0 — MaxMind GeoIP2 API |
| 341 | `azazael-pkg-getsploit` | packages | Callable skill for Python package getsploit 2.0.2 — Command line search and download tool for Vulners Datab... |
| 342 | `azazael-pkg-ghp-import` | packages | Callable skill for Python package ghp-import 2.1.0 — Copy your docs directly to the gh-pages branch. |
| 343 | `azazael-pkg-gitdb` | packages | Callable skill for Python package gitdb 4.0.12 — Git Object Database |
| 344 | `azazael-pkg-gitpython` | packages | Callable skill for Python package GitPython 3.1.50 — GitPython is a Python library used to interact with Gi... |
| 345 | `azazael-pkg-gitxray` | packages | Callable skill for Python package gitxray 1.0.20 — A multifaceted security tool which leverages Public GitH... |
| 346 | `azazael-pkg-globre` | packages | Callable skill for Python package globre 0.1.5 — A glob matching library, providing an interface similar to... |
| 347 | `azazael-pkg-gmplot` | packages | Callable skill for Python package gmplot 1.4.1 — A matplotlib-like interface to plot data with Google Maps. |
| 348 | `azazael-pkg-goofile` | packages | Callable skill for Python package goofile 1.6 — Update of https://code.google.com/archive/p/goofile/ for Py... |
| 349 | `azazael-pkg-google` | packages | Callable skill for Python package google 2.0.3 — Python bindings to the Google search engine. |
| 350 | `azazael-pkg-gps` | packages | Callable skill for Python package gps 3.27.5 — Python libraries for the gpsd service daemon |
| 351 | `azazael-pkg-gps3` | packages | Callable skill for Python package gps3 0.33.0 — Python 2.7-3.5 clients for gpsd |
| 352 | `azazael-pkg-grapheme` | packages | Callable skill for Python package grapheme 0.5.0 — Unicode grapheme helpers |
| 353 | `azazael-pkg-greenbone-feed-sync` | packages | Callable skill for Python package greenbone-feed-sync 25.1.3.dev1 — A tool for downloading the Greenbone Co... |
| 354 | `azazael-pkg-greenlet` | packages | Callable skill for Python package greenlet 3.3.2 — Lightweight in-process concurrent programming |
| 355 | `azazael-pkg-grokevt` | packages | Callable skill for Python package grokevt 0.5 — No summary available. |
| 356 | `azazael-pkg-gssapi` | packages | Callable skill for Python package gssapi 1.11.1 — Python GSSAPI Wrapper |
| 357 | `azazael-pkg-gvm-tools` | packages | Callable skill for Python package gvm-tools 25.4.6 — Tools to control a GSM/GVM over GMP or OSP |
| 358 | `azazael-pkg-h11` | packages | Callable skill for Python package h11 0.16.0 — A pure-Python, bring-your-own-I/O implementation of HTTP/1.1 |
| 359 | `azazael-pkg-h2` | packages | Callable skill for Python package h2 4.3.0 — Pure-Python HTTP/2 protocol implementation |
| 360 | `azazael-pkg-h8mail` | packages | Callable skill for Python package h8mail 2.5.6 — Email OSINT and password breach hunting. Use h8mail to fin... |
| 361 | `azazael-pkg-hashid` | packages | Callable skill for Python package hashID 3.1.4 — Software to identify the different types of hashes |
| 362 | `azazael-pkg-hekatomb` | packages | Callable skill for Python package hekatomb 1.5.2.3 — Python library to extract and decrypt all credentials ... |
| 363 | `azazael-pkg-hostsman` | packages | Callable skill for Python package hostsman 1.1.5 — A tool to manage hosts file |
| 364 | `azazael-pkg-hpack` | packages | Callable skill for Python package hpack 4.0.0 — Pure-Python HPACK header compression |
| 365 | `azazael-pkg-html2text` | packages | Callable skill for Python package html2text 2025.4.15 — Turn HTML into equivalent Markdown-structured text. |
| 366 | `azazael-pkg-html5lib-modern` | packages | Callable skill for Python package html5lib-modern 1.2 — HTML parser based on the WHATWG HTML specification |
| 367 | `azazael-pkg-httpagentparser` | packages | Callable skill for Python package httpagentparser 1.9.1 — Extracts OS Browser etc information from http use... |
| 368 | `azazael-pkg-httpcore` | packages | Callable skill for Python package httpcore 1.0.9 — A minimal low-level HTTP client. |
| 369 | `azazael-pkg-httpie` | packages | Callable skill for Python package httpie 3.2.4 — HTTPie: modern, user-friendly command-line HTTP client for... |
| 370 | `azazael-pkg-httplib2` | packages | Callable skill for Python package httplib2 0.31.2 — A comprehensive HTTP client library. |
| 371 | `azazael-pkg-httpx` | packages | Callable skill for Python package httpx 0.28.1 — The next generation HTTP client. |
| 372 | `azazael-pkg-httpx-ntlm` | packages | Callable skill for Python package httpx_ntlm 1.4.0 — This package allows for HTTP NTLM authentication using... |
| 373 | `azazael-pkg-httpx-sse` | packages | Callable skill for Python package httpx-sse 0.4.3 — Consume Server-Sent Event (SSE) messages with HTTPX. |
| 374 | `azazael-pkg-hupper` | packages | Callable skill for Python package hupper 1.12 — Integrated process monitor for developing and reloading dae... |
| 375 | `azazael-pkg-hypercorn` | packages | Callable skill for Python package Hypercorn 0.17.3 — A ASGI Server based on Hyper libraries and inspired by... |
| 376 | `azazael-pkg-hyperframe` | packages | Callable skill for Python package hyperframe 6.1.0 — Pure-Python HTTP/2 framing |
| 377 | `azazael-pkg-hyperlink` | packages | Callable skill for Python package hyperlink 21.0.0 — A featureful, immutable, and correct URL for Python. |
| 378 | `azazael-pkg-idna` | packages | Callable skill for Python package idna 3.11 — Internationalized Domain Names in Applications (IDNA) |
| 379 | `azazael-pkg-imagesize` | packages | Callable skill for Python package imagesize 2.0.0 — Get image size from headers (BMP/PNG/JPEG/JPEG2000/GIF/... |
| 380 | `azazael-pkg-imapclient` | packages | Callable skill for Python package IMAPClient 3.1.0 — Easy-to-use, Pythonic and complete IMAP client library |
| 381 | `azazael-pkg-impacket` | packages | Callable skill for Python package impacket 0.14.0.dev0 — Network protocols Constructors and Dissectors |
| 382 | `azazael-pkg-incremental` | packages | Callable skill for Python package incremental 24.7.2 — A small library that versions your Python projects. |
| 383 | `azazael-pkg-infinity` | packages | Callable skill for Python package infinity 1.5 — All-in-one infinity value for Python. Can be compared to a... |
| 384 | `azazael-pkg-inflect` | packages | Callable skill for Python package inflect 7.5.0 — Correctly generate plurals, singular nouns, ordinals, ind... |
| 385 | `azazael-pkg-iniconfig` | packages | Callable skill for Python package iniconfig 2.1.0 — brain-dead simple config-ini parsing |
| 386 | `azazael-pkg-instaloader` | packages | Callable skill for Python package instaloader 4.15.1 — Download pictures (or videos) along with their capti... |
| 387 | `azazael-pkg-intervaltree` | packages | Callable skill for Python package intervaltree 3.0.2 — Editable interval tree data structure for Python 2 a... |
| 388 | `azazael-pkg-invoke` | packages | Callable skill for Python package invoke 2.2.1 — Pythonic task execution |
| 389 | `azazael-pkg-ip2proxy` | packages | Callable skill for Python package IP2Proxy 3.4.0 — Python API for IP2Proxy database. It can be used to quer... |
| 390 | `azazael-pkg-ipwhois` | packages | Callable skill for Python package ipwhois 1.3.0 — Retrieve and parse whois data for IPv4 and IPv6 addresses. |
| 391 | `azazael-pkg-ipy` | packages | Callable skill for Python package IPy 1.1 — Class and tools for handling of IPv4 and IPv6 addresses and net... |
| 392 | `azazael-pkg-ipython` | packages | Callable skill for Python package ipython 9.11.0 — IPython: Productive Interactive Computing |
| 393 | `azazael-pkg-ipython-pygments-lexers` | packages | Callable skill for Python package ipython_pygments_lexers 1.1.1 — Defines a variety of Pygments lexers for ... |
| 394 | `azazael-pkg-isc-dhcp-leases` | packages | Callable skill for Python package isc_dhcp_leases 0.10.0 — Small python module for reading /var/lib/dhcp/dh... |
| 395 | `azazael-pkg-isoduration` | packages | Callable skill for Python package isoduration 20.11.0 — Operations with ISO 8601 durations |
| 396 | `azazael-pkg-itsdangerous` | packages | Callable skill for Python package itsdangerous 2.2.0 — Safely pass data to untrusted environments and back. |
| 397 | `azazael-pkg-ivre` | packages | Callable skill for Python package ivre 0.9.21+kali — Network recon framework |
| 398 | `azazael-pkg-jaraco-collections` | packages | Callable skill for Python package jaraco.collections 5.1.0 — Collection objects similar to those in stdlib ... |
| 399 | `azazael-pkg-jaraco-context` | packages | Callable skill for Python package jaraco.context 6.0.1 — Useful decorators and context managers |
| 400 | `azazael-pkg-jaraco-functools` | packages | Callable skill for Python package jaraco.functools 4.1.0 — Functools like those found in stdlib |
| 401 | `azazael-pkg-jaraco-text` | packages | Callable skill for Python package jaraco.text 4.0.0 — Module for text manipulation |
| 402 | `azazael-pkg-jedi` | packages | Callable skill for Python package jedi 0.19.1 — An autocompletion tool for Python that can be used for text... |
| 403 | `azazael-pkg-jeepney` | packages | Callable skill for Python package jeepney 0.9.0 — Low-level, pure Python DBus protocol wrapper. |
| 404 | `azazael-pkg-jefferson` | packages | Callable skill for Python package jefferson 0.4.7 — JFFS2 filesystem extraction tool. |
| 405 | `azazael-pkg-jinja2` | packages | Callable skill for Python package Jinja2 3.1.6 — A very fast and expressive template engine. |
| 406 | `azazael-pkg-jmespath` | packages | Callable skill for Python package jmespath 1.0.1 — JSON Matching Expressions |
| 407 | `azazael-pkg-joblib` | packages | Callable skill for Python package joblib 1.5.2 — Lightweight pipelining with Python functions |
| 408 | `azazael-pkg-jq` | packages | Callable skill for Python package jq 1.11.0 — jq is a lightweight and flexible JSON processor. |
| 409 | `azazael-pkg-jsmin` | packages | Callable skill for Python package jsmin 3.0.1 — JavaScript minifier. |
| 410 | `azazael-pkg-json5` | packages | Callable skill for Python package json5 0.10.0 — A Python implementation of the JSON5 data format. |
| 411 | `azazael-pkg-jsonpointer` | packages | Callable skill for Python package jsonpointer 2.4 — Identify specific nodes in a JSON document (RFC 6901) |
| 412 | `azazael-pkg-jsonschema` | packages | Callable skill for Python package jsonschema 4.26.0 — An implementation of JSON Schema validation for Python |
| 413 | `azazael-pkg-jsonschema-specifications` | packages | Callable skill for Python package jsonschema-specifications 2023.12.1 — The JSON Schema meta-schemas and vo... |
| 414 | `azazael-pkg-jupyter-core` | packages | Callable skill for Python package jupyter_core 5.9.1 — Jupyter core package. A base package on which Jupyte... |
| 415 | `azazael-pkg-kaitaistruct` | packages | Callable skill for Python package kaitaistruct 0.11 — Kaitai Struct declarative parser generator for binary... |
| 416 | `azazael-pkg-kali-tweaks` | packages | Callable skill for Python package kali-tweaks 2025.4.0 — Kali Linux GUI tool to ease configuration |
| 417 | `azazael-pkg-keystone-engine` | packages | Callable skill for Python package keystone-engine 0.9.2 — Keystone assembler engine |
| 418 | `azazael-pkg-kiwisolver` | packages | Callable skill for Python package kiwisolver 1.5.0 — A fast implementation of the Cassowary constraint solver |
| 419 | `azazael-pkg-krb5` | packages | Callable skill for Python package krb5 0.9.0 — Kerberos API bindings for Python |
| 420 | `azazael-pkg-lark` | packages | Callable skill for Python package lark 1.3.1 — a modern parsing library |
| 421 | `azazael-pkg-ldap3` | packages | Callable skill for Python package ldap3 2.9.1 — A strictly RFC 4510 conforming LDAP V3 pure Python client l... |
| 422 | `azazael-pkg-ldap3-bleeding-edge` | packages | Callable skill for Python package ldap3-bleeding_edge 2.10.1.1337 — A strictly RFC 4510 conforming LDAP V3 ... |
| 423 | `azazael-pkg-ldapdomaindump` | packages | Callable skill for Python package ldapdomaindump 0.9.4 — Active Directory information dumper via LDAP |
| 424 | `azazael-pkg-ldeep` | packages | Callable skill for Python package ldeep 2.0.3 — In-depth ldap enumeration utility |
| 425 | `azazael-pkg-legacy-cgi` | packages | Callable skill for Python package legacy-cgi 2.6.4 — Fork of the standard library cgi and cgitb modules rem... |
| 426 | `azazael-pkg-legacycrypt` | packages | Callable skill for Python package legacycrypt 0.3 — Wrapper to the POSIX crypt library call and associated ... |
| 427 | `azazael-pkg-levenshtein` | packages | Callable skill for Python package Levenshtein 0.27.1 — Python extension for computing string edit distances... |
| 428 | `azazael-pkg-libarchive-c` | packages | Callable skill for Python package libarchive-c 5.1 — Python interface to libarchive |
| 429 | `azazael-pkg-libpass` | packages | Callable skill for Python package libpass 1.9.3 — Fork of passlib, a comprehensive password hashing framewo... |
| 430 | `azazael-pkg-libtaxii` | packages | Callable skill for Python package libtaxii 1.1.119 — TAXII 1.X Library. |
| 431 | `azazael-pkg-libvmdk-python` | packages | Callable skill for Python package libvmdk-python 20240510 — Python bindings module for libvmdk |
| 432 | `azazael-pkg-lief` | packages | Callable skill for Python package lief 0.16.1 — Library to instrument executable formats |
| 433 | `azazael-pkg-limits` | packages | Callable skill for Python package limits 4.4.1 — Rate limiting utilities |
| 434 | `azazael-pkg-linkify-it-py` | packages | Callable skill for Python package linkify-it-py 2.1.0 — Links recognition library with FULL unicode support. |
| 435 | `azazael-pkg-livereload` | packages | Callable skill for Python package livereload 2.7.1 — Python LiveReload is an awesome tool for web developers |
| 436 | `azazael-pkg-llm` | packages | Callable skill for Python package llm 0.30 — CLI utility and Python library for interacting with Large Lang... |
| 437 | `azazael-pkg-llvmlite` | packages | Callable skill for Python package llvmlite 0.47.0 — lightweight wrapper around basic LLVM functionality |
| 438 | `azazael-pkg-lml` | packages | Callable skill for Python package lml 0.1.0 — Load me later. A lazy plugin management system. |
| 439 | `azazael-pkg-locket` | packages | Callable skill for Python package locket 1.0.0 — File-based locks for Python on Linux and Windows |
| 440 | `azazael-pkg-loguru` | packages | Callable skill for Python package loguru 0.7.3 — Python logging made (stupidly) simple |
| 441 | `azazael-pkg-logutils` | packages | Callable skill for Python package logutils 0.3.5 — Logging utilities |
| 442 | `azazael-pkg-lsassy` | packages | Callable skill for Python package lsassy 3.1.11 — Tool to remotely extract credentials |
| 443 | `azazael-pkg-lunr` | packages | Callable skill for Python package lunr 0.8.0 — A Python implementation of Lunr.js |
| 444 | `azazael-pkg-lxml` | packages | Callable skill for Python package lxml 6.1.0 — Powerful and Pythonic XML processing library combining libxm... |
| 445 | `azazael-pkg-lz4` | packages | Callable skill for Python package lz4 4.4.5+dfsg — LZ4 Bindings for Python |
| 446 | `azazael-pkg-lzallright` | packages | Callable skill for Python package lzallright 0.1.0 — No summary available. |
| 447 | `azazael-pkg-mako` | packages | Callable skill for Python package Mako 1.3.10.dev0 — A super-fast templating language that borrows the best... |
| 448 | `azazael-pkg-manuf` | packages | Callable skill for Python package manuf 1.1.5 — Parser library for Wireshark's OUI database |
| 449 | `azazael-pkg-markdown` | packages | Callable skill for Python package Markdown 3.10.2 — Python implementation of John Gruber's Markdown. |
| 450 | `azazael-pkg-markdown-it-py` | packages | Callable skill for Python package markdown-it-py 4.2.0 — Python port of markdown-it. Markdown parsing, done... |
| 451 | `azazael-pkg-markupsafe` | packages | Callable skill for Python package MarkupSafe 3.0.3 — Safely add untrusted strings to HTML/XML markup. |
| 452 | `azazael-pkg-marshmallow` | packages | Callable skill for Python package marshmallow 3.26.1 — A lightweight library for converting complex datatyp... |
| 453 | `azazael-pkg-maryam` | packages | Callable skill for Python package maryam 2.5.2.post2 — OWASP Maryam is a modular/optional open-source frame... |
| 454 | `azazael-pkg-masky` | packages | Callable skill for Python package masky 0.2.1 — Python library with CLI allowing to remotely dump domain us... |
| 455 | `azazael-pkg-matplotlib` | packages | Callable skill for Python package matplotlib 3.10.7+dfsg1 — Python plotting package |
| 456 | `azazael-pkg-matplotlib-inline` | packages | Callable skill for Python package matplotlib-inline 0.2.1 — Inline Matplotlib backend for Jupyter |
| 457 | `azazael-pkg-maxminddb` | packages | Callable skill for Python package maxminddb 3.0.0 — Reader for the MaxMind DB format |
| 458 | `azazael-pkg-mcp` | packages | Callable skill for Python package mcp 1.22.0 — Model Context Protocol SDK |
| 459 | `azazael-pkg-mdit-py-plugins` | packages | Callable skill for Python package mdit-py-plugins 0.6.1 — Collection of plugins for markdown-it-py |
| 460 | `azazael-pkg-mdurl` | packages | Callable skill for Python package mdurl 0.1.2 — Markdown URL utilities |
| 461 | `azazael-pkg-mechanize` | packages | Callable skill for Python package mechanize 0.4.10 — Stateful, programmatic web browsing |
| 462 | `azazael-pkg-mercurial` | packages | Callable skill for Python package mercurial 7.2.2 — Fast scalable distributed SCM (revision control, versio... |
| 463 | `azazael-pkg-mergedeep` | packages | Callable skill for Python package mergedeep 1.3.4 — A deep merge function for 🐍. |
| 464 | `azazael-pkg-minidump` | packages | Callable skill for Python package minidump 0.0.21 — Python library to parse Windows minidump file format |
| 465 | `azazael-pkg-minikerberos` | packages | Callable skill for Python package minikerberos 0.4.4 — Kerberos manipulation library in pure Python |
| 466 | `azazael-pkg-mistune` | packages | Callable skill for Python package mistune 3.1.4 — A sane and fast Markdown parser with useful plugins and r... |
| 467 | `azazael-pkg-mitm6` | packages | Callable skill for Python package mitm6 0.3.0 — Pwning IPv4 via IPv6 |
| 468 | `azazael-pkg-mitmproxy` | packages | Callable skill for Python package mitmproxy 12.2.3 — An interactive, SSL/TLS-capable intercepting proxy for... |
| 469 | `azazael-pkg-mkdocs` | packages | Callable skill for Python package mkdocs 1.6.1 — Project documentation with Markdown. |
| 470 | `azazael-pkg-mkdocs-get-deps` | packages | Callable skill for Python package mkdocs-get-deps 0.2.0 — MkDocs extension that lists all dependencies acco... |
| 471 | `azazael-pkg-mock` | packages | Callable skill for Python package mock 5.2.0 — Rolling backport of unittest.mock for all Pythons |
| 472 | `azazael-pkg-monotonic` | packages | Callable skill for Python package monotonic 1.6 — An implementation of time.monotonic() for Python 2 & < 3.3 |
| 473 | `azazael-pkg-more-itertools` | packages | Callable skill for Python package more-itertools 10.8.0 — More routines for operating on iterables, beyond ... |
| 474 | `azazael-pkg-more-termcolor` | packages | Callable skill for Python package more-termcolor 1.1.3 — All colors, with support for nested colors, conven... |
| 475 | `azazael-pkg-mpmath` | packages | Callable skill for Python package mpmath 1.4.1 — Python library for arbitrary-precision floating-point arit... |
| 476 | `azazael-pkg-msgpack` | packages | Callable skill for Python package msgpack 1.1.2 — MessagePack serializer |
| 477 | `azazael-pkg-msldap` | packages | Callable skill for Python package msldap 0.5.10 — Python library to play with MS LDAP |
| 478 | `azazael-pkg-msoffcrypto-tool` | packages | Callable skill for Python package msoffcrypto-tool 6.0.0 — Python tool and library for decrypting and encry... |
| 479 | `azazael-pkg-mssqlpwner` | packages | Callable skill for Python package mssqlpwner 1.3.2 — Seamlessly interact and pwn MSSQL servers |
| 480 | `azazael-pkg-multidict` | packages | Callable skill for Python package multidict 6.4.3 — multidict implementation |
| 481 | `azazael-pkg-mypy-boto3-ebs` | packages | Callable skill for Python package mypy-boto3-ebs 1.26.0.post1 — Type annotations for boto3.EBS 1.26.0 servi... |
| 482 | `azazael-pkg-mypy-extensions` | packages | Callable skill for Python package mypy_extensions 1.1.0 — Type system extensions for programs checked with ... |
| 483 | `azazael-pkg-mysqlclient` | packages | Callable skill for Python package mysqlclient 1.4.6 — Python interface to MySQL |
| 484 | `azazael-pkg-myst-parser` | packages | Callable skill for Python package myst-parser 5.1.0 — An extended [CommonMark](https://spec.commonmark.org/... |
| 485 | `azazael-pkg-name-that-hash` | packages | Callable skill for Python package name-that-hash 1.11.0 — The Modern Hash Identification System |
| 486 | `azazael-pkg-nassl` | packages | Callable skill for Python package nassl 5.4.0 — Experimental OpenSSL wrapper for Python 3.10+ and SSLyze. |
| 487 | `azazael-pkg-nbformat` | packages | Callable skill for Python package nbformat 5.10.4 — The Jupyter Notebook format |
| 488 | `azazael-pkg-ndiff` | packages | Callable skill for Python package ndiff 7.99 — Nmap scan diff tool |
| 489 | `azazael-pkg-neo4j` | packages | Callable skill for Python package neo4j 5.2.dev0 — Neo4j Bolt driver for Python |
| 490 | `azazael-pkg-neobolt` | packages | Callable skill for Python package neobolt 1.7.17 — Neo4j Bolt connector for Python |
| 491 | `azazael-pkg-neotime` | packages | Callable skill for Python package neotime 1.7.4 — Nanosecond resolution temporal types |
| 492 | `azazael-pkg-netaddr` | packages | Callable skill for Python package netaddr 1.3.0 — A network address manipulation library for Python |
| 493 | `azazael-pkg-netexec` | packages | Callable skill for Python package netexec 1.5.1 — The Network Execution tool |
| 494 | `azazael-pkg-netifaces` | packages | Callable skill for Python package netifaces 0.11.0 — Portable network interface information. |
| 495 | `azazael-pkg-netmiko` | packages | Callable skill for Python package netmiko 4.6.0 — Multi-vendor library to simplify legacy CLI connections t... |
| 496 | `azazael-pkg-networkx` | packages | Callable skill for Python package networkx 3.4.2 — Python package for creating and manipulating graphs and ... |
| 497 | `azazael-pkg-nltk` | packages | Callable skill for Python package nltk 3.9.3 — Natural Language Toolkit |
| 498 | `azazael-pkg-notus-scanner` | packages | Callable skill for Python package notus-scanner 22.7.2 — A vulnerability scanner for creating results from ... |
| 499 | `azazael-pkg-ntc-templates` | packages | Callable skill for Python package ntc_templates 3.5.0 — TextFSM Templates for Network Devices, and Python w... |
| 500 | `azazael-pkg-ntlm-auth` | packages | Callable skill for Python package ntlm-auth 1.5.0 — Creates NTLM authentication structures |
| 501 | `azazael-pkg-ntpsec` | packages | Callable skill for Python package ntpsec 1.2.4 — The NTP reference implementation, refactored |
| 502 | `azazael-pkg-numba` | packages | Callable skill for Python package numba 0.65.1 — compiling Python code using LLVM |
| 503 | `azazael-pkg-numexpr` | packages | Callable skill for Python package numexpr 2.14.1 — Fast numerical expression evaluator for NumPy |
| 504 | `azazael-pkg-numpy` | packages | Callable skill for Python package numpy 2.3.5 — Fundamental package for array computing in Python |
| 505 | `azazael-pkg-oauthlib` | packages | Callable skill for Python package oauthlib 3.3.1 — A generic, spec-compliant, thorough implementation of th... |
| 506 | `azazael-pkg-odfpy` | packages | Callable skill for Python package odfpy 1.4.2 — Python API and tools to manipulate OpenDocument files |
| 507 | `azazael-pkg-olefile` | packages | Callable skill for Python package olefile 0.47 — Python package to parse, read and write Microsoft OLE2 fil... |
| 508 | `azazael-pkg-oletools` | packages | Callable skill for Python package oletools 0.60.2 — Python tools to analyze security characteristics of MS ... |
| 509 | `azazael-pkg-openai` | packages | Callable skill for Python package openai 2.21.0 — The official Python library for the openai API |
| 510 | `azazael-pkg-openpyxl` | packages | Callable skill for Python package openpyxl 3.1.5 — A Python library to read/write Excel 2010 xlsx/xlsm files |
| 511 | `azazael-pkg-opentaxii` | packages | Callable skill for Python package opentaxii 0.9.3 — TAXII server implementation in Python from EclecticIQ |
| 512 | `azazael-pkg-orjson` | packages | Callable skill for Python package orjson 3.11.7 — Fast, correct Python JSON library supporting dataclasses,... |
| 513 | `azazael-pkg-oscrypto` | packages | Callable skill for Python package oscrypto 1.3.0 — TLS (SSL) sockets, key generation, encryption, decryptio... |
| 514 | `azazael-pkg-ospd-openvas` | packages | Callable skill for Python package ospd-openvas 22.10.0 — ospd based scanner for openvas |
| 515 | `azazael-pkg-osrframework` | packages | Callable skill for Python package osrframework 0.20.5 — OSRFramework - A set of AGPLv3+ OSINT tools develop... |
| 516 | `azazael-pkg-outcome` | packages | Callable skill for Python package outcome 1.3.0.post0 — Capture the outcome of Python function calls. |
| 517 | `azazael-pkg-packaging` | packages | Callable skill for Python package packaging 26.2 — Core utilities for Python packages |
| 518 | `azazael-pkg-pacu` | packages | Callable skill for Python package pacu 1.6.0 — The AWS exploitation framework, designed for testing the sec... |
| 519 | `azazael-pkg-paho-mqtt` | packages | Callable skill for Python package paho-mqtt 2.1.0 — MQTT version 5.0/3.1.1 client class |
| 520 | `azazael-pkg-pandas` | packages | Callable skill for Python package pandas 2.3.3 — Powerful data structures for data analysis, time series, a... |
| 521 | `azazael-pkg-paramiko` | packages | Callable skill for Python package paramiko 4.0.0 — SSH2 protocol library |
| 522 | `azazael-pkg-paramspider` | packages | Callable skill for Python package paramspider 0.1.0 — Mining parameters from dark corners of Web Archives |
| 523 | `azazael-pkg-parso` | packages | Callable skill for Python package parso 0.8.7 — A Python Parser |
| 524 | `azazael-pkg-partd` | packages | Callable skill for Python package partd 1.4.2 — Appendable key-value storage |
| 525 | `azazael-pkg-passwordmeter` | packages | Callable skill for Python package passwordmeter 0.1.8 — A password strength measuring library. |
| 526 | `azazael-pkg-paste` | packages | Callable skill for Python package Paste 3.10.1 — Tools for using a Web Server Gateway Interface stack |
| 527 | `azazael-pkg-pastedeploy` | packages | Callable skill for Python package PasteDeploy 3.1.0 — Load, configure, and compose WSGI applications and se... |
| 528 | `azazael-pkg-pastescript` | packages | Callable skill for Python package PasteScript 3.7.0 — A pluggable command-line frontend, including commands... |
| 529 | `azazael-pkg-patator` | packages | Callable skill for Python package patator 1.1.0 — Multi-purpose brute-forcer |
| 530 | `azazael-pkg-pathspec` | packages | Callable skill for Python package pathspec 1.0.4 — Utility library for gitignore style pattern matching of ... |
| 531 | `azazael-pkg-pbkdf2` | packages | Callable skill for Python package pbkdf2 1.3 — PKCS#5 v2.0 PBKDF2 Module |
| 532 | `azazael-pkg-pcapy` | packages | Callable skill for Python package pcapy 0.11.5.dev0 — Python pcap extension |
| 533 | `azazael-pkg-pcodedmp` | packages | Callable skill for Python package pcodedmp 1.2.6 — A VBA p-code disassembler |
| 534 | `azazael-pkg-pefile` | packages | Callable skill for Python package pefile 2024.8.26 — Python PE parsing module |
| 535 | `azazael-pkg-penelope-shell-handler` | packages | Callable skill for Python package penelope-shell-handler 0.20.0 — Post-exploitation shell handler for autho... |
| 536 | `azazael-pkg-pexpect` | packages | Callable skill for Python package pexpect 4.9.0 — Pexpect allows easy control of interactive console applic... |
| 537 | `azazael-pkg-phonenumbers` | packages | Callable skill for Python package phonenumbers 8.12.57 — Python version of Google's common library for pars... |
| 538 | `azazael-pkg-phpserialize` | packages | Callable skill for Python package phpserialize 1.3 — a port of the serialize and unserialize functions of p... |
| 539 | `azazael-pkg-pick` | packages | Callable skill for Python package pick 2.4.0 — Pick an option in the terminal with a simple GUI |
| 540 | `azazael-pkg-pillow` | packages | Callable skill for Python package pillow 12.2.0 — Python Imaging Library (fork) |
| 541 | `azazael-pkg-ping3` | packages | Callable skill for Python package ping3 4.0.4 — A pure python3 version of ICMP ping implementation using ra... |
| 542 | `azazael-pkg-pip` | packages | Callable skill for Python package pip 26.1.1 — The PyPA recommended tool for installing Python packages. |
| 543 | `azazael-pkg-pipx` | packages | Callable skill for Python package pipx 1.14.0 — Install and Run Python Applications in Isolated Environments |
| 544 | `azazael-pkg-plaso` | packages | Callable skill for Python package plaso 20260119 — Plaso (log2timeline) - Super timeline all the things |
| 545 | `azazael-pkg-plaster` | packages | Callable skill for Python package plaster 1.1.2 — A loader interface around multiple config file formats. |
| 546 | `azazael-pkg-plaster-pastedeploy` | packages | Callable skill for Python package plaster_pastedeploy 0.5 — A loader implementing the PasteDeploy syntax to... |
| 547 | `azazael-pkg-platformdirs` | packages | Callable skill for Python package platformdirs 4.10.0 — A small Python package for determining appropriate ... |
| 548 | `azazael-pkg-playwright` | packages | Callable skill for Python package playwright 1.55.0+ds — A high-level API to automate web browsers |
| 549 | `azazael-pkg-plotext` | packages | Callable skill for Python package plotext 5.2.8 — plotext plots directly on terminal |
| 550 | `azazael-pkg-plotly` | packages | Callable skill for Python package plotly 5.20.0 — An open-source, interactive data visualization library fo... |
| 551 | `azazael-pkg-pluggy` | packages | Callable skill for Python package pluggy 1.6.0 — plugin and hook calling mechanisms for python |
| 552 | `azazael-pkg-pluginbase` | packages | Callable skill for Python package pluginbase 1.0.1 — PluginBase is a module for Python that enables the dev... |
| 553 | `azazael-pkg-plumbum` | packages | Callable skill for Python package plumbum 1.10.0 — Plumbum: shell combinators library |
| 554 | `azazael-pkg-ply` | packages | Callable skill for Python package ply 3.11 — Python Lex & Yacc |
| 555 | `azazael-pkg-pocsuite3` | packages | Callable skill for Python package pocsuite3 2.1.0 — Open-sourced remote vulnerability testing framework. |
| 556 | `azazael-pkg-poetry-core` | packages | Callable skill for Python package poetry-core 2.3.1 — Poetry PEP 517 Build Backend |
| 557 | `azazael-pkg-poetry-dynamic-versioning` | packages | Callable skill for Python package poetry-dynamic-versioning 1.9.1 — Plugin for Poetry to enable dynamic ver... |
| 558 | `azazael-pkg-policyuniverse` | packages | Callable skill for Python package policyuniverse 1.5.1.20231109 — Parse and Process AWS IAM Policies, State... |
| 559 | `azazael-pkg-pooch` | packages | Callable skill for Python package pooch 1.9.0 — A friend to fetch your data files |
| 560 | `azazael-pkg-portend` | packages | Callable skill for Python package portend 3.2.0 — TCP port monitoring and discovery |
| 561 | `azazael-pkg-prettytable` | packages | Callable skill for Python package prettytable 3.17.0 — A simple Python library for easily displaying tabula... |
| 562 | `azazael-pkg-priority` | packages | Callable skill for Python package priority 2.0.0 — A pure-Python implementation of the HTTP/2 priority tree |
| 563 | `azazael-pkg-prompt-toolkit` | packages | Callable skill for Python package prompt_toolkit 3.0.52 — Library for building powerful interactive command... |
| 564 | `azazael-pkg-propcache` | packages | Callable skill for Python package propcache 0.5.2 — Accelerated property cache |
| 565 | `azazael-pkg-protobuf` | packages | Callable skill for Python package protobuf 4.21.12 — Protocol Buffers |
| 566 | `azazael-pkg-psutil` | packages | Callable skill for Python package psutil 7.1.0 — Cross-platform lib for process and system monitoring. |
| 567 | `azazael-pkg-psycopg2` | packages | Callable skill for Python package psycopg2 2.9.12 — psycopg2 - Python-PostgreSQL Database Adapter |
| 568 | `azazael-pkg-ptyprocess` | packages | Callable skill for Python package ptyprocess 0.7.0 — Run a subprocess in a pseudo terminal |
| 569 | `azazael-pkg-publicsuffix2` | packages | Callable skill for Python package publicsuffix2 2.20191221 — Get a public suffix for a domain name using th... |
| 570 | `azazael-pkg-publicsuffixlist` | packages | Callable skill for Python package publicsuffixlist 0.9.3 — publicsuffixlist implement |
| 571 | `azazael-pkg-pure-eval` | packages | Callable skill for Python package pure_eval 0.2.3 — Safely evaluate AST nodes without side effects |
| 572 | `azazael-pkg-puremagic` | packages | Callable skill for Python package puremagic 2.2.0 — Pure python implementation of magic file detection |
| 573 | `azazael-pkg-pwncat` | packages | Callable skill for Python package pwncat 0.1.2 — Netcat on steroids with Firewall, IDS/IPS evasion, bind an... |
| 574 | `azazael-pkg-pwntools` | packages | Callable skill for Python package pwntools 4.15.0 — Pwntools CTF framework and exploit development library. |
| 575 | `azazael-pkg-py-cpuinfo` | packages | Callable skill for Python package py-cpuinfo 9.0.0 — Get CPU info with pure Python |
| 576 | `azazael-pkg-pyasn1` | packages | Callable skill for Python package pyasn1 0.6.3 — Pure-Python implementation of ASN.1 types and DER/BER/CER ... |
| 577 | `azazael-pkg-pyasn1-modules` | packages | Callable skill for Python package pyasn1_modules 0.4.1 — A collection of ASN.1-based protocols modules |
| 578 | `azazael-pkg-pyasyncore` | packages | Callable skill for Python package pyasyncore 1.0.2 — Make asyncore available for Python 3.12 onwards |
| 579 | `azazael-pkg-pybluez` | packages | Callable skill for Python package PyBluez 0.23 — Bluetooth Python extension module |
| 580 | `azazael-pkg-pycairo` | packages | Callable skill for Python package pycairo 1.27.0 — Python interface for cairo |
| 581 | `azazael-pkg-pycares` | packages | Callable skill for Python package pycares 5.0.1 — Python interface for c-ares |
| 582 | `azazael-pkg-pycognito` | packages | Callable skill for Python package pycognito 2024.5.1 — Python class to integrate Boto3's Cognito client so ... |
| 583 | `azazael-pkg-pycparser` | packages | Callable skill for Python package pycparser 3.0 — C parser in Python |
| 584 | `azazael-pkg-pycriu` | packages | Callable skill for Python package pycriu 4.2 — Python bindings for CRIU |
| 585 | `azazael-pkg-pycryptodomex` | packages | Callable skill for Python package pycryptodomex 3.20.0 — Cryptographic library for Python |
| 586 | `azazael-pkg-pycups` | packages | Callable skill for Python package pycups 2.0.4 — Python bindings for libcups |
| 587 | `azazael-pkg-pycurl` | packages | Callable skill for Python package pycurl 7.46.0 — PycURL -- A Python Interface To The cURL library |
| 588 | `azazael-pkg-pydantic` | packages | Callable skill for Python package pydantic 2.13.4 — Data validation using Python type hints |
| 589 | `azazael-pkg-pydantic-core` | packages | Callable skill for Python package pydantic_core 2.46.4 — Core functionality for Pydantic validation and ser... |
| 590 | `azazael-pkg-pydantic-settings` | packages | Callable skill for Python package pydantic-settings 2.14.1 — Settings management using Pydantic |
| 591 | `azazael-pkg-pydot` | packages | Callable skill for Python package pydot 4.0.1 — Python interface to Graphviz's Dot |
| 592 | `azazael-pkg-pydotplus` | packages | Callable skill for Python package pydotplus 2.0.2 — Python interface to Graphviz's Dot language |
| 593 | `azazael-pkg-pyee` | packages | Callable skill for Python package pyee 13.0.0 — A rough port of Node.js's EventEmitter to Python with a few... |
| 594 | `azazael-pkg-pyelftools` | packages | Callable skill for Python package pyelftools 0.33 — Library for analyzing ELF files and DWARF debugging inf... |
| 595 | `azazael-pkg-pyenchant` | packages | Callable skill for Python package pyenchant 3.3.0 — Python bindings for the Enchant spellchecking system |
| 596 | `azazael-pkg-pyexcel` | packages | Callable skill for Python package pyexcel 0.7.0 — A wrapper library that provides one API to read, manipula... |
| 597 | `azazael-pkg-pyexcel-io` | packages | Callable skill for Python package pyexcel-io 0.6.6 — A python library to read and write structured data in ... |
| 598 | `azazael-pkg-pyexcel-ods` | packages | Callable skill for Python package pyexcel-ods 0.6.0 — A wrapper library to read, manipulate and write data ... |
| 599 | `azazael-pkg-pyexcel-text` | packages | Callable skill for Python package pyexcel-text 0.2.7.1 — A plugin to pyexcel and provides the capability to... |
| 600 | `azazael-pkg-pyexcel-xls` | packages | Callable skill for Python package pyexcel-xls 0.7.0 — A wrapper library to read, manipulate and write data ... |
| 601 | `azazael-pkg-pyexcel-xlsx` | packages | Callable skill for Python package pyexcel-xlsx 0.6.0 — A wrapper library to read, manipulate and write data... |
| 602 | `azazael-pkg-pyfatfs` | packages | Callable skill for Python package pyfatfs 1.1.0 — FAT12/FAT16/FAT32 implementation with VFAT support |
| 603 | `azazael-pkg-pyfiglet` | packages | Callable skill for Python package pyfiglet 1.0.4 — Pure-python FIGlet implementation |
| 604 | `azazael-pkg-pygccxml` | packages | Callable skill for Python package pygccxml 3.0.2 — Python package for easy C++ declarations navigation. |
| 605 | `azazael-pkg-pygexf` | packages | Callable skill for Python package pygexf 0.2.2 — UNKNOWN |
| 606 | `azazael-pkg-pygit2` | packages | Callable skill for Python package pygit2 1.19.2 — Python bindings for libgit2. |
| 607 | `azazael-pkg-pygments` | packages | Callable skill for Python package Pygments 2.19.2 — Pygments is a syntax highlighting package written in Py... |
| 608 | `azazael-pkg-pygobject` | packages | Callable skill for Python package PyGObject 3.56.2 — Python bindings for GObject Introspection |
| 609 | `azazael-pkg-pygraphviz` | packages | Callable skill for Python package pygraphviz 1.14 — Python interface to Graphviz |
| 610 | `azazael-pkg-pyhamcrest` | packages | Callable skill for Python package PyHamcrest 2.1.0 — Hamcrest framework for matcher objects |
| 611 | `azazael-pkg-pyinotify` | packages | Callable skill for Python package pyinotify 0.9.6 — Linux filesystem events monitoring |
| 612 | `azazael-pkg-pyinstaller` | packages | Callable skill for Python package pyinstaller 6.18.0 — PyInstaller bundles a Python application and all its... |
| 613 | `azazael-pkg-pyinstaller-hooks-contrib` | packages | Callable skill for Python package pyinstaller-hooks-contrib 2026.4 — Community maintained hooks for PyInsta... |
| 614 | `azazael-pkg-pyjwt` | packages | Callable skill for Python package PyJWT 2.12.1 — JSON Web Token implementation in Python |
| 615 | `azazael-pkg-pykerberos` | packages | Callable skill for Python package pykerberos 1.1.14 — High-level interface to Kerberos |
| 616 | `azazael-pkg-pylnk3` | packages | Callable skill for Python package pylnk3 0.4.3 — Windows LNK File Parser and Creator |
| 617 | `azazael-pkg-pylsqpack` | packages | Callable skill for Python package pylsqpack 0.3.23 — Python wrapper for the ls-qpack QPACK library |
| 618 | `azazael-pkg-pymavlink` | packages | Callable skill for Python package pymavlink 2.4.37 — Python MAVLink code |
| 619 | `azazael-pkg-pymdown-extensions` | packages | Callable skill for Python package pymdown-extensions 10.19.1 — Extension pack for Python Markdown. |
| 620 | `azazael-pkg-pymongo` | packages | Callable skill for Python package pymongo 4.16.0 — PyMongo - the Official MongoDB Python driver |
| 621 | `azazael-pkg-pymssql` | packages | Callable skill for Python package pymssql 2.3.10 — DB-API interface to Microsoft SQL Server for Python. (ne... |
| 622 | `azazael-pkg-pynacl` | packages | Callable skill for Python package PyNaCl 1.6.2 — Python binding to the Networking and Cryptography (NaCl) l... |
| 623 | `azazael-pkg-pynfsclient` | packages | Callable skill for Python package pyNfsClient 0.1.5 — Pure python NFS client |
| 624 | `azazael-pkg-pynput` | packages | Callable skill for Python package pynput 1.8.2 — Monitor and control user input devices |
| 625 | `azazael-pkg-pyodbc` | packages | Callable skill for Python package pyodbc 5.3.0 — DB API module for ODBC |
| 626 | `azazael-pkg-pyopengl` | packages | Callable skill for Python package PyOpenGL 3.1.10 — Standard OpenGL bindings for Python |
| 627 | `azazael-pkg-pyopenssl` | packages | Callable skill for Python package pyOpenSSL 26.2.0 — Python wrapper module around the OpenSSL library |
| 628 | `azazael-pkg-pyparsing` | packages | Callable skill for Python package pyparsing 3.3.2 — pyparsing - Classes and methods to define and execute p... |
| 629 | `azazael-pkg-pypdf` | packages | Callable skill for Python package pypdf 6.9.2 — A pure-python PDF library capable of splitting, merging, cr... |
| 630 | `azazael-pkg-pyperclip` | packages | Callable skill for Python package pyperclip 1.11.0 — A cross-platform clipboard module for Python. (Only ha... |
| 631 | `azazael-pkg-pyperscan` | packages | Callable skill for Python package pyperscan 0.3.0 — No summary available. |
| 632 | `azazael-pkg-pyppeteer` | packages | Callable skill for Python package pyppeteer 2.0.0 — Headless chrome/chromium automation library (unofficial... |
| 633 | `azazael-pkg-pypsrp` | packages | Callable skill for Python package pypsrp 0.8.1 — PowerShell Remoting Protocol and WinRM for Python |
| 634 | `azazael-pkg-pypykatz` | packages | Callable skill for Python package pypykatz 0.6.13 — Python implementation of Mimikatz |
| 635 | `azazael-pkg-pyqt5` | packages | Callable skill for Python package PyQt5 5.15.11 — Python bindings for the Qt cross platform application too... |
| 636 | `azazael-pkg-pyqt5-sip` | packages | Callable skill for Python package PyQt5_sip 12.18.0 — The sip module support for PyQt5 |
| 637 | `azazael-pkg-pyqt6` | packages | Callable skill for Python package PyQt6 6.11.0 — Python bindings for the Qt cross platform application toolkit |
| 638 | `azazael-pkg-pyqt6-sip` | packages | Callable skill for Python package PyQt6_sip 13.11.1 — The sip module support for PyQt6 |
| 639 | `azazael-pkg-pyqtgraph` | packages | Callable skill for Python package pyqtgraph 0.14.0 — Scientific Graphics and GUI Library for Python |
| 640 | `azazael-pkg-pyramid` | packages | Callable skill for Python package pyramid 2.0.2 — The Pyramid Web Framework, a Pylons project |
| 641 | `azazael-pkg-pyregfi` | packages | Callable skill for Python package pyregfi 1.0.1.0 — No summary available. |
| 642 | `azazael-pkg-pyric` | packages | Callable skill for Python package PyRIC 0.1.6.4 — Python Wireless Library |
| 643 | `azazael-pkg-pyserial` | packages | Callable skill for Python package pyserial 3.5 — Python Serial Port Extension |
| 644 | `azazael-pkg-pyshark` | packages | Callable skill for Python package pyshark 0.6 — Python wrapper for tshark, allowing python packet parsing u... |
| 645 | `azazael-pkg-pyside6` | packages | Callable skill for Python package PySide6 6.10.3 — Python bindings for the Qt cross-platform application an... |
| 646 | `azazael-pkg-pysigma` | packages | Callable skill for Python package pySigma 1.0.2 — Sigma rule processing and conversion tools |
| 647 | `azazael-pkg-pysmb` | packages | Callable skill for Python package pysmb 1.1.19 — pysmb is an experimental SMB/CIFS library written in Pytho... |
| 648 | `azazael-pkg-pysmbc` | packages | Callable skill for Python package pysmbc 1.0.25.1 — Python bindings for libsmbclient |
| 649 | `azazael-pkg-pysnmp` | packages | Callable skill for Python package pysnmp 7.1.22 — A Python library for SNMP |
| 650 | `azazael-pkg-pysocks` | packages | Callable skill for Python package PySocks 1.7.1 — A Python SOCKS client module. See https://github.com/Anor... |
| 651 | `azazael-pkg-pyspnego` | packages | Callable skill for Python package pyspnego 0.10.2 — Windows Negotiate Authentication Client and Server |
| 652 | `azazael-pkg-pytest` | packages | Callable skill for Python package pytest 9.0.3 — pytest: simple powerful testing with Python |
| 653 | `azazael-pkg-python-apt` | packages | Callable skill for Python package python-apt 3.1.0 — Python bindings for APT |
| 654 | `azazael-pkg-python-dateutil` | packages | Callable skill for Python package python-dateutil 2.9.0 — Extensions to the standard Python datetime module |
| 655 | `azazael-pkg-python-discovery` | packages | Callable skill for Python package python-discovery 1.4.0 — Python interpreter discovery |
| 656 | `azazael-pkg-python-docx` | packages | Callable skill for Python package python-docx 1.2.0 — Create, read, and update Microsoft Word .docx files. |
| 657 | `azazael-pkg-python-dotenv` | packages | Callable skill for Python package python-dotenv 1.2.1 — Read key-value pairs from a .env file and set them ... |
| 658 | `azazael-pkg-python-emailahoy3` | packages | Callable skill for Python package python-emailahoy3 0.1.3 — A Python3 email utility that verifies existence... |
| 659 | `azazael-pkg-python-engineio` | packages | Callable skill for Python package python-engineio 4.13.0 — Engine.IO server and client for Python |
| 660 | `azazael-pkg-python-gnupg` | packages | Callable skill for Python package python-gnupg 0.5.4 — A wrapper for the Gnu Privacy Guard (GPG or GnuPG) |
| 661 | `azazael-pkg-python-gvm` | packages | Callable skill for Python package python-gvm 26.11.0 — Library to communicate with remote servers over GMP ... |
| 662 | `azazael-pkg-python-ldap` | packages | Callable skill for Python package python-ldap 3.4.5 — Python modules for implementing LDAP clients |
| 663 | `azazael-pkg-python-libnmap` | packages | Callable skill for Python package python-libnmap 0.7.3 — Python NMAP library enabling you to start async nm... |
| 664 | `azazael-pkg-python-magic` | packages | Callable skill for Python package python-magic 0.4.28 — File type identification using libmagic |
| 665 | `azazael-pkg-python-magic-ahupp` | packages | Callable skill for Python package python-magic-ahupp 0.4.13 — File type identification using libmagic |
| 666 | `azazael-pkg-python-memcached` | packages | Callable skill for Python package python-memcached 1.60 — Pure python memcached client |
| 667 | `azazael-pkg-python-multipart` | packages | Callable skill for Python package python-multipart 0.0.26 — A streaming multipart parser for Python |
| 668 | `azazael-pkg-python-nmap` | packages | Callable skill for Python package python-nmap 0.7.1 — This is a python class to use nmap and access scan re... |
| 669 | `azazael-pkg-python-owasp-zap-v2-4` | packages | Callable skill for Python package python-owasp-zap-v2.4 0.0.20 — OWASP ZAP 2.11 API client |
| 670 | `azazael-pkg-python-pptx` | packages | Callable skill for Python package python-pptx 0.6.18 — Generate and manipulate Open XML PowerPoint (.pptx) ... |
| 671 | `azazael-pkg-python-socketio` | packages | Callable skill for Python package python-socketio 5.16.0 — Socket.IO server and client for Python |
| 672 | `azazael-pkg-python-socks` | packages | Callable skill for Python package python-socks 2.8.1 — Proxy (SOCKS4, SOCKS5, HTTP CONNECT) client for Python |
| 673 | `azazael-pkg-python-ulid` | packages | Callable skill for Python package python-ulid 2.2.0 — Universally unique lexicographically sortable identifier |
| 674 | `azazael-pkg-python-whois` | packages | Callable skill for Python package python-whois 0.9.3 — Whois querying and parsing of domain registration in... |
| 675 | `azazael-pkg-python-xlib` | packages | Callable skill for Python package python-xlib 0.33 — Python X Library |
| 676 | `azazael-pkg-pythonping` | packages | Callable skill for Python package pythonping 1.1.4 — A simple way to ping in Python |
| 677 | `azazael-pkg-pytsk3` | packages | Callable skill for Python package pytsk3 20250801 — Python bindings for the SleuthKit |
| 678 | `azazael-pkg-pytz` | packages | Callable skill for Python package pytz 2025.2 — World timezone definitions, modern and historical |
| 679 | `azazael-pkg-pyusb` | packages | Callable skill for Python package pyusb 1.2.1.post2 — Python USB access module |
| 680 | `azazael-pkg-pyuserinput` | packages | Callable skill for Python package PyUserInput 0.1.11 — A simple, cross-platform module for mouse and keyboa... |
| 681 | `azazael-pkg-pyvirtualdisplay` | packages | Callable skill for Python package PyVirtualDisplay 3.0 — python wrapper for Xvfb, Xephyr and Xvnc |
| 682 | `azazael-pkg-pywerview` | packages | Callable skill for Python package pywerview 0.3.3 — A Python port of PowerSploit's PowerView |
| 683 | `azazael-pkg-pyxdg` | packages | Callable skill for Python package pyxdg 0.28 — PyXDG contains implementations of freedesktop.org standards ... |
| 684 | `azazael-pkg-pyyaml` | packages | Callable skill for Python package PyYAML 6.0.3 — YAML parser and emitter for Python |
| 685 | `azazael-pkg-pyyaml-env-tag` | packages | Callable skill for Python package pyyaml_env_tag 1.1 — A custom YAML tag for referencing environment variab... |
| 686 | `azazael-pkg-pyzipper` | packages | Callable skill for Python package pyzipper 0.3.6 — AES encryption for zipfile. |
| 687 | `azazael-pkg-pyzmq` | packages | Callable skill for Python package pyzmq 27.1.0 — Python bindings for 0MQ |
| 688 | `azazael-pkg-qrcode` | packages | Callable skill for Python package qrcode 8.2 — QR Code image generator |
| 689 | `azazael-pkg-qscintilla` | packages | Callable skill for Python package QScintilla 2.14.1 — Python bindings for the QScintilla programmers editor... |
| 690 | `azazael-pkg-quart` | packages | Callable skill for Python package quart 0.20.0 — A Python ASGI web framework with the same API as Flask |
| 691 | `azazael-pkg-rapidfuzz` | packages | Callable skill for Python package RapidFuzz 3.12.2 — rapid fuzzy string matching |
| 692 | `azazael-pkg-rarfile` | packages | Callable skill for Python package rarfile 4.2 — RAR archive reader for Python |
| 693 | `azazael-pkg-ratelimit` | packages | Callable skill for Python package ratelimit 2.2.1 — API rate limit decorator |
| 694 | `azazael-pkg-raven` | packages | Callable skill for Python package raven 1.1.0 — A lightweight file upload service used for penetration test... |
| 695 | `azazael-pkg-recommonmark` | packages | Callable skill for Python package recommonmark 0.7.1 — A docutils-compatibility bridge to CommonMark, enabl... |
| 696 | `azazael-pkg-redis` | packages | Callable skill for Python package redis 6.4.0 — Python client for Redis database and key-value store |
| 697 | `azazael-pkg-referencing` | packages | Callable skill for Python package referencing 0.37.0 — JSON Referencing + Python |
| 698 | `azazael-pkg-regex` | packages | Callable skill for Python package regex 2025.9.18 — Alternative regular expression module, to replace re. |
| 699 | `azazael-pkg-rel` | packages | Callable skill for Python package rel 0.4.9.19 — Registered Event Listener. Provides standard (pyevent) int... |
| 700 | `azazael-pkg-reportlab` | packages | Callable skill for Python package reportlab 4.4.10 — The Reportlab Toolkit |
| 701 | `azazael-pkg-repoze-lru` | packages | Callable skill for Python package repoze.lru 0.7 — A tiny LRU cache implementation and decorator |
| 702 | `azazael-pkg-requests` | packages | Callable skill for Python package requests 2.32.5 — Python HTTP for Humans. |
| 703 | `azazael-pkg-requests-file` | packages | Callable skill for Python package requests-file 3.0.1 — File transport adapter for Requests |
| 704 | `azazael-pkg-requests-futures` | packages | Callable skill for Python package requests-futures 1.0.2 — Asynchronous Python HTTP for Humans. |
| 705 | `azazael-pkg-requests-ntlm` | packages | Callable skill for Python package requests_ntlm 1.3.0 — This package allows for HTTP NTLM authentication us... |
| 706 | `azazael-pkg-requests-toolbelt` | packages | Callable skill for Python package requests-toolbelt 1.0.0 — A utility belt for advanced users of python-req... |
| 707 | `azazael-pkg-responses` | packages | Callable skill for Python package responses 0.26.1 — A utility library for mocking out the `requests` Pytho... |
| 708 | `azazael-pkg-retrying` | packages | Callable skill for Python package retrying 1.4.2 — Retrying |
| 709 | `azazael-pkg-rfc3339-validator` | packages | Callable skill for Python package rfc3339-validator 0.1.4 — A pure python RFC3339 validator |
| 710 | `azazael-pkg-rfc3986-validator` | packages | Callable skill for Python package rfc3986-validator 0.1.1 — Pure python rfc3986 validator |
| 711 | `azazael-pkg-rfc3987` | packages | Callable skill for Python package rfc3987 1.3.8 — Parsing and validation of URIs (RFC 3986) and IRIs (RFC 3... |
| 712 | `azazael-pkg-rfcat` | packages | Callable skill for Python package rfcat 2.0.1 — the swiss army knife of subGHz |
| 713 | `azazael-pkg-rich` | packages | Callable skill for Python package rich 15.0.0 — Render rich text, tables, progress bars, syntax highlightin... |
| 714 | `azazael-pkg-rjsmin` | packages | Callable skill for Python package rjsmin 1.2.5 — Javascript Minifier |
| 715 | `azazael-pkg-rlpycairo` | packages | Callable skill for Python package rlPyCairo 0.3.0 — Plugin backend renderer for reportlab.graphics.renderPM |
| 716 | `azazael-pkg-roguehostapd` | packages | Callable skill for Python package roguehostapd 1.1.2 — Hostapd wrapper for hostapd |
| 717 | `azazael-pkg-roman-numerals` | packages | Callable skill for Python package roman-numerals 4.1.0 — Manipulate well-formed Roman numerals |
| 718 | `azazael-pkg-ropgadget` | packages | Callable skill for Python package ROPGadget 7.7 — This tool lets you search your gadgets on your binaries t... |
| 719 | `azazael-pkg-ropper` | packages | Callable skill for Python package ropper 1.13.8 — Show information about files in different file formats an... |
| 720 | `azazael-pkg-routersploit` | packages | Callable skill for Python package routersploit 3.4.7 — Exploitation Framework for Embedded Devices |
| 721 | `azazael-pkg-routes` | packages | Callable skill for Python package Routes 2.5.1 — Routing Recognition and Generation Tools |
| 722 | `azazael-pkg-rpds-py` | packages | Callable skill for Python package rpds-py 0.30.0 — Python bindings to Rust's persistent data structures (rpds) |
| 723 | `azazael-pkg-rpyc` | packages | Callable skill for Python package rpyc 6.0.2 — Remote Python Call (RPyC) is a transparent and symmetric dis... |
| 724 | `azazael-pkg-rq` | packages | Callable skill for Python package rq 2.9.1 — RQ is a simple, lightweight, library for creating background j... |
| 725 | `azazael-pkg-ruamel-yaml` | packages | Callable skill for Python package ruamel.yaml 0.18.14 — ruamel.yaml is a YAML parser/emitter that supports ... |
| 726 | `azazael-pkg-ruamel-yaml-clib` | packages | Callable skill for Python package ruamel.yaml.clib 0.2.15 — C version of reader, parser and emitter for rua... |
| 727 | `azazael-pkg-s3transfer` | packages | Callable skill for Python package s3transfer 0.14.0 — An Amazon S3 Transfer Manager |
| 728 | `azazael-pkg-sara` | packages | Callable skill for Python package sara 1.3 — RouterOS Security Inspector |
| 729 | `azazael-pkg-scapy` | packages | Callable skill for Python package scapy 2.7.1 — Scapy: interactive packet manipulation tool |
| 730 | `azazael-pkg-schema` | packages | Callable skill for Python package schema 0.7.7 — Simple data validation library |
| 731 | `azazael-pkg-scikit-learn` | packages | Callable skill for Python package scikit-learn 1.8.0 — A set of python modules for machine learning and dat... |
| 732 | `azazael-pkg-scipy` | packages | Callable skill for Python package scipy 1.16.3 — Fundamental algorithms for scientific computing in Python |
| 733 | `azazael-pkg-scp` | packages | Callable skill for Python package scp 0.15.0 — scp module for paramiko |
| 734 | `azazael-pkg-secure` | packages | Callable skill for Python package secure 1.0.1 — A lightweight package that adds security headers for Pytho... |
| 735 | `azazael-pkg-selenium` | packages | Callable skill for Python package selenium 4.24.0 — Official Python bindings for Selenium WebDriver. |
| 736 | `azazael-pkg-service-identity` | packages | Callable skill for Python package service-identity 24.2.0 — Service identity verification for pyOpenSSL & c... |
| 737 | `azazael-pkg-setproctitle` | packages | Callable skill for Python package setproctitle 1.3.7 — A Python module to customize the process title |
| 738 | `azazael-pkg-setuptools` | packages | Callable skill for Python package setuptools 78.1.1 — Easily download, build, install, upgrade, and uninsta... |
| 739 | `azazael-pkg-sgmllib3k` | packages | Callable skill for Python package sgmllib3k 1.0.0 — Py3k port of sgmllib. |
| 740 | `azazael-pkg-shell-gpt` | packages | Callable skill for Python package shell_gpt 1.5.1 — A command-line productivity tool powered by large langu... |
| 741 | `azazael-pkg-shellfire` | packages | Callable skill for Python package shellfire 0.14 — shellfire is an exploitation shell focusing on exploitin... |
| 742 | `azazael-pkg-shellingham` | packages | Callable skill for Python package shellingham 1.5.4 — Tool to Detect Surrounding Shell |
| 743 | `azazael-pkg-sherlock-project` | packages | Callable skill for Python package sherlock-project 0 — Hunt down social media accounts by username across s... |
| 744 | `azazael-pkg-shiboken6` | packages | Callable skill for Python package shiboken6 6.10.3 — Python / C++ bindings helper module |
| 745 | `azazael-pkg-shiboken6-generator` | packages | Callable skill for Python package shiboken6-generator 6.10.3 — Python / C++ bindings generator |
| 746 | `azazael-pkg-shodan` | packages | Callable skill for Python package shodan 1.31.0 — Python library and command-line utility for Shodan (https... |
| 747 | `azazael-pkg-shtab` | packages | Callable skill for Python package shtab 1.8.0 — Automagic shell tab completion for Python CLI applications |
| 748 | `azazael-pkg-sickle-pdk` | packages | Callable skill for Python package sickle-pdk 4.1.1 — Payload Development Kit |
| 749 | `azazael-pkg-sigma-cli` | packages | Callable skill for Python package sigma-cli 3.0.2 — Sigma Command Line Interface (conversion, check etc.) b... |
| 750 | `azazael-pkg-simple-websocket` | packages | Callable skill for Python package simple-websocket 1.1.0 — Simple WebSocket server and client for Python |
| 751 | `azazael-pkg-simplejson` | packages | Callable skill for Python package simplejson 4.1.1 — Simple, fast, extensible JSON encoder/decoder for Python |
| 752 | `azazael-pkg-sippts` | packages | Callable skill for Python package sippts 4.1.dev0 — SIPPTS is a set of tools for auditing VoIP systems base... |
| 753 | `azazael-pkg-six` | packages | Callable skill for Python package six 1.17.0 — Python 2 and 3 compatibility utilities |
| 754 | `azazael-pkg-skia-pathops` | packages | Callable skill for Python package skia-pathops 0.9.2 — Python access to operations on paths using the Skia ... |
| 755 | `azazael-pkg-slowapi` | packages | Callable skill for Python package slowapi 0.1.9 — A rate limiting extension for Starlette and Fastapi |
| 756 | `azazael-pkg-smart-open` | packages | Callable skill for Python package smart_open 7.5.1 — Utils for streaming large files (S3, HDFS, GCS, SFTP, ... |
| 757 | `azazael-pkg-smbmap` | packages | Callable skill for Python package smbmap 1.10.7 — SMBMap is a handy SMB enumeration tool |
| 758 | `azazael-pkg-smmap` | packages | Callable skill for Python package smmap 6.0.0 — A pure Python implementation of a sliding window memory map... |
| 759 | `azazael-pkg-smoke-zephyr` | packages | Callable skill for Python package smoke-zephyr 2.0.1 — This project provides a collection of miscellaneous ... |
| 760 | `azazael-pkg-sniffio` | packages | Callable skill for Python package sniffio 1.3.1 — Sniff out which async library your code is running under |
| 761 | `azazael-pkg-snowballstemmer` | packages | Callable skill for Python package snowballstemmer 3.1.1 — This package provides 36 stemmers for 34 language... |
| 762 | `azazael-pkg-sortedcontainers` | packages | Callable skill for Python package sortedcontainers 2.4.0 — Sorted Containers -- Sorted List, Sorted Dict, S... |
| 763 | `azazael-pkg-soupsieve` | packages | Callable skill for Python package soupsieve 2.8.4 — A modern CSS selector implementation for Beautiful Soup. |
| 764 | `azazael-pkg-specan` | packages | Callable skill for Python package specan 1 — A tool for reading spectrum analyzer data from an Ubertooth de... |
| 765 | `azazael-pkg-sphinx` | packages | Callable skill for Python package Sphinx 9.1.0 — Python documentation generator |
| 766 | `azazael-pkg-sphinx-rtd-theme` | packages | Callable skill for Python package sphinx_rtd_theme 3.1.0 — Read the Docs theme for Sphinx |
| 767 | `azazael-pkg-sphinxcontrib-jquery` | packages | Callable skill for Python package sphinxcontrib-jquery 4.1 — Extension to include jQuery on newer Sphinx re... |
| 768 | `azazael-pkg-sploitscan` | packages | Callable skill for Python package sploitscan 0.14.3 — SploitScan is a cybersecurity utility designed to pro... |
| 769 | `azazael-pkg-sprayhound` | packages | Callable skill for Python package sprayhound 0.0.4 — Password spraying with BloodHound integration |
| 770 | `azazael-pkg-sqlalchemy` | packages | Callable skill for Python package SQLAlchemy 2.0.48 — Database Abstraction Library |
| 771 | `azazael-pkg-sqlalchemy-utils` | packages | Callable skill for Python package SQLAlchemy-Utils 0.42.1 — Various utility functions for SQLAlchemy. |
| 772 | `azazael-pkg-sqlite-fts4` | packages | Callable skill for Python package sqlite-fts4 1.0.3 — Python functions for working with SQLite FTS4 search |
| 773 | `azazael-pkg-sqlite-migrate` | packages | Callable skill for Python package sqlite-migrate 0.1b0 — A simple database migration system for SQLite, bas... |
| 774 | `azazael-pkg-sqlite-utils` | packages | Callable skill for Python package sqlite-utils 3.38 — CLI tool and Python library for manipulating SQLite d... |
| 775 | `azazael-pkg-sqlmc` | packages | Callable skill for Python package sqlmc 1.1.0 — SQL Injection Massive Checker for a domain |
| 776 | `azazael-pkg-sqlparse` | packages | Callable skill for Python package sqlparse 0.5.5 — A non-validating SQL parser. |
| 777 | `azazael-pkg-ssdeep` | packages | Callable skill for Python package ssdeep 3.4.1 — Python wrapper for the ssdeep library |
| 778 | `azazael-pkg-sse-starlette` | packages | Callable skill for Python package sse-starlette 3.4.1 — SSE plugin for Starlette |
| 779 | `azazael-pkg-sshuttle` | packages | Callable skill for Python package sshuttle 1.3.2 — Transparent proxy server that works as a poor man's VPN.... |
| 780 | `azazael-pkg-sslyze` | packages | Callable skill for Python package sslyze 6.3.1 — Fast and powerful SSL/TLS scanning library. |
| 781 | `azazael-pkg-stack-data` | packages | Callable skill for Python package stack_data 0.6.3 — Extract data from python stack frames and tracebacks f... |
| 782 | `azazael-pkg-starlette` | packages | Callable skill for Python package starlette 1.1.0 — The little ASGI library that shines. |
| 783 | `azazael-pkg-stegcracker` | packages | Callable skill for Python package stegcracker 2.1.0 — Steganography brute-force utility to uncover hidden d... |
| 784 | `azazael-pkg-stem` | packages | Callable skill for Python package stem 1.8.2 — Stem is a Python controller library that allows applications... |
| 785 | `azazael-pkg-stix2` | packages | Callable skill for Python package stix2 3.0.1 — Produce and consume STIX 2 JSON content |
| 786 | `azazael-pkg-stix2-patterns` | packages | Callable skill for Python package stix2-patterns 2.0.0 — Validate STIX 2 Patterns. |
| 787 | `azazael-pkg-stone` | packages | Callable skill for Python package stone 3.3.9 — Stone is an interface description language (IDL) for APIs. |
| 788 | `azazael-pkg-stringdist` | packages | Callable skill for Python package StringDist 1.0.9 — This package provides the stringdist module, which inc... |
| 789 | `azazael-pkg-structlog` | packages | Callable skill for Python package structlog 25.5.0 — Structured Logging for Python |
| 790 | `azazael-pkg-sublist3r` | packages | Callable skill for Python package Sublist3r 1.0 — Subdomains enumeration tool for penetration testers |
| 791 | `azazael-pkg-suds-community` | packages | Callable skill for Python package suds-community 1.2.0 — Lightweight SOAP client (community fork) |
| 792 | `azazael-pkg-svglib` | packages | Callable skill for Python package svglib 1.5.1 — A pure-Python library for reading and converting SVG |
| 793 | `azazael-pkg-sympy` | packages | Callable skill for Python package sympy 1.14.0 — Computer algebra system (CAS) in Python |
| 794 | `azazael-pkg-syslog-rfc5424-formatter` | packages | Callable skill for Python package syslog-rfc5424-formatter 1.2.3 — Logging formatter which produces well-fo... |
| 795 | `azazael-pkg-tables` | packages | Callable skill for Python package tables 3.11.1 — Hierarchical datasets for Python |
| 796 | `azazael-pkg-tabulate` | packages | Callable skill for Python package tabulate 0.9.0 — Pretty-print tabular data |
| 797 | `azazael-pkg-tblib` | packages | Callable skill for Python package tblib 3.2.2 — Traceback serialization library. |
| 798 | `azazael-pkg-telnetlib` | packages | Callable skill for Python package telnetlib 0.0.0 — No summary available. |
| 799 | `azazael-pkg-tempita` | packages | Callable skill for Python package Tempita 0.6.0 — A very small text templating language |
| 800 | `azazael-pkg-tempora` | packages | Callable skill for Python package tempora 5.7.0 — Objects and routines pertaining to date and time (tempora) |
| 801 | `azazael-pkg-tenacity` | packages | Callable skill for Python package tenacity 9.1.4 — Retry code until it succeeds |
| 802 | `azazael-pkg-termcolor` | packages | Callable skill for Python package termcolor 2.4.0 — ANSI color formatting for output in terminal |
| 803 | `azazael-pkg-terminaltables3` | packages | Callable skill for Python package terminaltables3 4.0.0 — Generate simple tables in terminals from a nested... |
| 804 | `azazael-pkg-termineter` | packages | Callable skill for Python package termineter 1.0.6 — Termineter is a Python framework which provides a plat... |
| 805 | `azazael-pkg-textfsm` | packages | Callable skill for Python package textfsm 2.1.0 — Python module for parsing semi-structured text into pytho... |
| 806 | `azazael-pkg-texttable` | packages | Callable skill for Python package texttable 1.7.0 — module to create simple ASCII tables |
| 807 | `azazael-pkg-theharvester` | packages | Callable skill for Python package theHarvester 4.10.1 — theHarvester is a very simple, yet effective tool d... |
| 808 | `azazael-pkg-threadpoolctl` | packages | Callable skill for Python package threadpoolctl 3.1.0 — threadpoolctl |
| 809 | `azazael-pkg-thrift` | packages | Callable skill for Python package thrift 0.23.0 — Python bindings for the Apache Thrift RPC system |
| 810 | `azazael-pkg-tinycss2` | packages | Callable skill for Python package tinycss2 1.5.1 — A tiny CSS parser |
| 811 | `azazael-pkg-tinydb` | packages | Callable skill for Python package tinydb 4.8.2 — TinyDB is a tiny, document oriented database optimized for... |
| 812 | `azazael-pkg-tld` | packages | Callable skill for Python package tld 0.13 — Extract the top-level domain (TLD) from the URL given. |
| 813 | `azazael-pkg-tldextract` | packages | Callable skill for Python package tldextract 5.3.1 — Accurately separates a URL's subdomain, domain, and pu... |
| 814 | `azazael-pkg-tls-parser` | packages | Callable skill for Python package tls-parser 1.2.2 — Small library to parse TLS records. |
| 815 | `azazael-pkg-tlsh` | packages | Callable skill for Python package tlsh 4.5.0 — TLSH (C++ Python extension) |
| 816 | `azazael-pkg-toml` | packages | Callable skill for Python package toml 0.10.2 — Python Library for Tom's Obvious, Minimal Language |
| 817 | `azazael-pkg-tomlkit` | packages | Callable skill for Python package tomlkit 0.13.3 — Style preserving TOML library |
| 818 | `azazael-pkg-toolz` | packages | Callable skill for Python package toolz 1.1.0.post1 — List processing tools and functional utilities |
| 819 | `azazael-pkg-tornado` | packages | Callable skill for Python package tornado 6.5.5 — Tornado is a Python web framework and asynchronous networ... |
| 820 | `azazael-pkg-tqdm` | packages | Callable skill for Python package tqdm 4.67.3 — Fast, Extensible Progress Meter |
| 821 | `azazael-pkg-traitlets` | packages | Callable skill for Python package traitlets 5.14.3 — Traitlets Python configuration system |
| 822 | `azazael-pkg-translationstring` | packages | Callable skill for Python package translationstring 1.4 — Utility library for i18n relied on by various Rep... |
| 823 | `azazael-pkg-treelib` | packages | Callable skill for Python package treelib 1.8.0 — A Python implementation of tree structure. |
| 824 | `azazael-pkg-trio` | packages | Callable skill for Python package trio 0.33.0 — A friendly Python library for async concurrency and I/O |
| 825 | `azazael-pkg-trio-websocket` | packages | Callable skill for Python package trio-websocket 0.12.2 — WebSocket library for Trio |
| 826 | `azazael-pkg-twisted` | packages | Callable skill for Python package Twisted 26.4.0 — An asynchronous networking framework written in Python |
| 827 | `azazael-pkg-typeguard` | packages | Callable skill for Python package typeguard 4.4.4 — Run-time type checker for Python |
| 828 | `azazael-pkg-typer` | packages | Callable skill for Python package typer 0.20.0 — Typer, build great CLIs. Easy to code. Based on Python typ... |
| 829 | `azazael-pkg-types-aiofiles` | packages | Callable skill for Python package types-aiofiles 25.1 — Typing stubs for aiofiles |
| 830 | `azazael-pkg-types-antlr4-python3-runtime` | packages | Callable skill for Python package types-antlr4-python3-runtime 4.13 — Typing stubs for antlr4-python3-runtime |
| 831 | `azazael-pkg-types-assertpy` | packages | Callable skill for Python package types-assertpy 1.1 — Typing stubs for assertpy |
| 832 | `azazael-pkg-types-atheris` | packages | Callable skill for Python package types-atheris 3.0 — Typing stubs for atheris |
| 833 | `azazael-pkg-types-auth0-python` | packages | Callable skill for Python package types-auth0-python 4.10 — Typing stubs for auth0-python |
| 834 | `azazael-pkg-types-authlib` | packages | Callable skill for Python package types-Authlib 1.6.6 — Typing stubs for Authlib |
| 835 | `azazael-pkg-types-aws-xray-sdk` | packages | Callable skill for Python package types-aws-xray-sdk 2.15 — Typing stubs for aws-xray-sdk |
| 836 | `azazael-pkg-types-binaryornot` | packages | Callable skill for Python package types-binaryornot 0.4 — Typing stubs for binaryornot |
| 837 | `azazael-pkg-types-bleach` | packages | Callable skill for Python package types-bleach 6.3 — Typing stubs for bleach |
| 838 | `azazael-pkg-types-boltons` | packages | Callable skill for Python package types-boltons 25.0 — Typing stubs for boltons |
| 839 | `azazael-pkg-types-braintree` | packages | Callable skill for Python package types-braintree 4.42 — Typing stubs for braintree |
| 840 | `azazael-pkg-types-cachetools` | packages | Callable skill for Python package types-cachetools 6.2 — Typing stubs for cachetools |
| 841 | `azazael-pkg-types-capturer` | packages | Callable skill for Python package types-capturer 3.0 — Typing stubs for capturer |
| 842 | `azazael-pkg-types-cffi` | packages | Callable skill for Python package types-cffi 1.17 — Typing stubs for cffi |
| 843 | `azazael-pkg-types-channels` | packages | Callable skill for Python package types-channels 4.3 — Typing stubs for channels |
| 844 | `azazael-pkg-types-chevron` | packages | Callable skill for Python package types-chevron 0.14 — Typing stubs for chevron |
| 845 | `azazael-pkg-types-click-default-group` | packages | Callable skill for Python package types-click-default-group 1.2 — Typing stubs for click-default-group |
| 846 | `azazael-pkg-types-click-log` | packages | Callable skill for Python package types-click-log 0.4 — Typing stubs for click-log |
| 847 | `azazael-pkg-types-click-shell` | packages | Callable skill for Python package types-click-shell 2.1 — Typing stubs for click-shell |
| 848 | `azazael-pkg-types-click-spinner` | packages | Callable skill for Python package types-click-spinner 0.1 — Typing stubs for click-spinner |
| 849 | `azazael-pkg-types-click-web` | packages | Callable skill for Python package types-click-web 0.8 — Typing stubs for click-web |
| 850 | `azazael-pkg-types-colorama` | packages | Callable skill for Python package types-colorama 0.4 — Typing stubs for colorama |
| 851 | `azazael-pkg-types-colorful` | packages | Callable skill for Python package types-colorful 0.5 — Typing stubs for colorful |
| 852 | `azazael-pkg-types-console-menu` | packages | Callable skill for Python package types-console-menu 0.8 — Typing stubs for console-menu |
| 853 | `azazael-pkg-types-convertdate` | packages | Callable skill for Python package types-convertdate 2.4 — Typing stubs for convertdate |
| 854 | `azazael-pkg-types-croniter` | packages | Callable skill for Python package types-croniter 6.0.0 — Typing stubs for croniter |
| 855 | `azazael-pkg-types-dateparser` | packages | Callable skill for Python package types-dateparser 1.2.2 — Typing stubs for dateparser |
| 856 | `azazael-pkg-types-decorator` | packages | Callable skill for Python package types-decorator 5.2 — Typing stubs for decorator |
| 857 | `azazael-pkg-types-defusedxml` | packages | Callable skill for Python package types-defusedxml 0.7 — Typing stubs for defusedxml |
| 858 | `azazael-pkg-types-deprecated` | packages | Callable skill for Python package types-Deprecated 1.3.1 — Typing stubs for Deprecated |
| 859 | `azazael-pkg-types-dirhash` | packages | Callable skill for Python package types-dirhash 0.5 — Typing stubs for dirhash |
| 860 | `azazael-pkg-types-django-filter` | packages | Callable skill for Python package types-django-filter 25.2 — Typing stubs for django-filter |
| 861 | `azazael-pkg-types-django-import-export` | packages | Callable skill for Python package types-django-import-export 4.4 — Typing stubs for django-import-export |
| 862 | `azazael-pkg-types-docker` | packages | Callable skill for Python package types-docker 7.1 — Typing stubs for docker |
| 863 | `azazael-pkg-types-dockerfile-parse` | packages | Callable skill for Python package types-dockerfile-parse 2.0 — Typing stubs for dockerfile-parse |
| 864 | `azazael-pkg-types-docutils` | packages | Callable skill for Python package types-docutils 0.22.3 — Typing stubs for docutils |
| 865 | `azazael-pkg-types-editdistance` | packages | Callable skill for Python package types-editdistance 0.8 — Typing stubs for editdistance |
| 866 | `azazael-pkg-types-entrypoints` | packages | Callable skill for Python package types-entrypoints 0.4 — Typing stubs for entrypoints |
| 867 | `azazael-pkg-types-ephem` | packages | Callable skill for Python package types-ephem 4.2 — Typing stubs for ephem |
| 868 | `azazael-pkg-types-et-xmlfile` | packages | Callable skill for Python package types-et_xmlfile 2.0 — Typing stubs for et_xmlfile |
| 869 | `azazael-pkg-types-fanstatic` | packages | Callable skill for Python package types-fanstatic 1.6 — Typing stubs for fanstatic |
| 870 | `azazael-pkg-types-first` | packages | Callable skill for Python package types-first 2.0 — Typing stubs for first |
| 871 | `azazael-pkg-types-flake8` | packages | Callable skill for Python package types-flake8 7.3 — Typing stubs for flake8 |
| 872 | `azazael-pkg-types-flake8-bugbear` | packages | Callable skill for Python package types-flake8-bugbear 25.11.29 — Typing stubs for flake8-bugbear |
| 873 | `azazael-pkg-types-flake8-builtins` | packages | Callable skill for Python package types-flake8-builtins 3.1 — Typing stubs for flake8-builtins |
| 874 | `azazael-pkg-types-flake8-docstrings` | packages | Callable skill for Python package types-flake8-docstrings 1.7 — Typing stubs for flake8-docstrings |
| 875 | `azazael-pkg-types-flake8-rst-docstrings` | packages | Callable skill for Python package types-flake8-rst-docstrings 0.4 — Typing stubs for flake8-rst-docstrings |
| 876 | `azazael-pkg-types-flake8-simplify` | packages | Callable skill for Python package types-flake8-simplify 0.30 — Typing stubs for flake8-simplify |
| 877 | `azazael-pkg-types-flake8-typing-imports` | packages | Callable skill for Python package types-flake8-typing-imports 1.17 — Typing stubs for flake8-typing-imports |
| 878 | `azazael-pkg-types-flask-cors` | packages | Callable skill for Python package types-Flask-Cors 6.0 — Typing stubs for Flask-Cors |
| 879 | `azazael-pkg-types-flask-migrate` | packages | Callable skill for Python package types-Flask-Migrate 4.1 — Typing stubs for Flask-Migrate |
| 880 | `azazael-pkg-types-flask-socketio` | packages | Callable skill for Python package types-Flask-SocketIO 5.6 — Typing stubs for Flask-SocketIO |
| 881 | `azazael-pkg-types-fpdf2` | packages | Callable skill for Python package types-fpdf2 2.8.4 — Typing stubs for fpdf2 |
| 882 | `azazael-pkg-types-gdb` | packages | Callable skill for Python package types-gdb 16.3 — Typing stubs for gdb |
| 883 | `azazael-pkg-types-geopandas` | packages | Callable skill for Python package types-geopandas 1.1.2 — Typing stubs for geopandas |
| 884 | `azazael-pkg-types-gevent` | packages | Callable skill for Python package types-gevent 25.9 — Typing stubs for gevent |
| 885 | `azazael-pkg-types-google-cloud-ndb` | packages | Callable skill for Python package types-google-cloud-ndb 2.4 — Typing stubs for google-cloud-ndb |
| 886 | `azazael-pkg-types-greenlet` | packages | Callable skill for Python package types-greenlet 3.3 — Typing stubs for greenlet |
| 887 | `azazael-pkg-types-grpcio` | packages | Callable skill for Python package types-grpcio 1 — Typing stubs for grpcio |
| 888 | `azazael-pkg-types-grpcio-channelz` | packages | Callable skill for Python package types-grpcio-channelz 1 — Typing stubs for grpcio-channelz |
| 889 | `azazael-pkg-types-grpcio-health-checking` | packages | Callable skill for Python package types-grpcio-health-checking 1 — Typing stubs for grpcio-health-checking |
| 890 | `azazael-pkg-types-grpcio-reflection` | packages | Callable skill for Python package types-grpcio-reflection 1 — Typing stubs for grpcio-reflection |
| 891 | `azazael-pkg-types-grpcio-status` | packages | Callable skill for Python package types-grpcio-status 1 — Typing stubs for grpcio-status |
| 892 | `azazael-pkg-types-gunicorn` | packages | Callable skill for Python package types-gunicorn 25.0 — Typing stubs for gunicorn |
| 893 | `azazael-pkg-types-hdbcli` | packages | Callable skill for Python package types-hdbcli 2.25 — Typing stubs for hdbcli |
| 894 | `azazael-pkg-types-hnswlib` | packages | Callable skill for Python package types-hnswlib 0.8 — Typing stubs for hnswlib |
| 895 | `azazael-pkg-types-html5lib` | packages | Callable skill for Python package types-html5lib 1.1 — Typing stubs for html5lib |
| 896 | `azazael-pkg-types-httplib2` | packages | Callable skill for Python package types-httplib2 0.31.2 — Typing stubs for httplib2 |
| 897 | `azazael-pkg-types-hvac` | packages | Callable skill for Python package types-hvac 2.4 — Typing stubs for hvac |
| 898 | `azazael-pkg-types-ibm-db` | packages | Callable skill for Python package types-ibm-db 3.2.6 — Typing stubs for ibm-db |
| 899 | `azazael-pkg-types-icalendar` | packages | Callable skill for Python package types-icalendar 6.3.2 — Typing stubs for icalendar |
| 900 | `azazael-pkg-types-inifile` | packages | Callable skill for Python package types-inifile 0.4 — Typing stubs for inifile |
| 901 | `azazael-pkg-types-jack-client` | packages | Callable skill for Python package types-JACK-Client 0.5 — Typing stubs for JACK-Client |
| 902 | `azazael-pkg-types-jetson-gpio` | packages | Callable skill for Python package types-Jetson.GPIO 2.1.12 — Typing stubs for Jetson.GPIO |
| 903 | `azazael-pkg-types-jmespath` | packages | Callable skill for Python package types-jmespath 1.1 — Typing stubs for jmespath |
| 904 | `azazael-pkg-types-jsonnet` | packages | Callable skill for Python package types-jsonnet 0.21 — Typing stubs for jsonnet |
| 905 | `azazael-pkg-types-jsonschema` | packages | Callable skill for Python package types-jsonschema 4.26.0 — Typing stubs for jsonschema |
| 906 | `azazael-pkg-types-jwcrypto` | packages | Callable skill for Python package types-jwcrypto 1.5 — Typing stubs for jwcrypto |
| 907 | `azazael-pkg-types-keyboard` | packages | Callable skill for Python package types-keyboard 0.13 — Typing stubs for keyboard |
| 908 | `azazael-pkg-types-ldap3` | packages | Callable skill for Python package types-ldap3 2.9 — Typing stubs for ldap3 |
| 909 | `azazael-pkg-types-libsass` | packages | Callable skill for Python package types-libsass 0.23 — Typing stubs for libsass |
| 910 | `azazael-pkg-types-lunardate` | packages | Callable skill for Python package types-lunardate 0.2 — Typing stubs for lunardate |
| 911 | `azazael-pkg-types-lupa` | packages | Callable skill for Python package types-lupa 2.6 — Typing stubs for lupa |
| 912 | `azazael-pkg-types-lzstring` | packages | Callable skill for Python package types-lzstring 1.0 — Typing stubs for lzstring |
| 913 | `azazael-pkg-types-m3u8` | packages | Callable skill for Python package types-m3u8 6.0 — Typing stubs for m3u8 |
| 914 | `azazael-pkg-types-markdown` | packages | Callable skill for Python package types-Markdown 3.10 — Typing stubs for Markdown |
| 915 | `azazael-pkg-types-mock` | packages | Callable skill for Python package types-mock 5.2 — Typing stubs for mock |
| 916 | `azazael-pkg-types-mypy-extensions` | packages | Callable skill for Python package types-mypy-extensions 1.1 — Typing stubs for mypy-extensions |
| 917 | `azazael-pkg-types-mysqlclient` | packages | Callable skill for Python package types-mysqlclient 2.2 — Typing stubs for mysqlclient |
| 918 | `azazael-pkg-types-nanoid` | packages | Callable skill for Python package types-nanoid 2.0.0 — Typing stubs for nanoid |
| 919 | `azazael-pkg-types-nanoleafapi` | packages | Callable skill for Python package types-nanoleafapi 2.1 — Typing stubs for nanoleafapi |
| 920 | `azazael-pkg-types-netaddr` | packages | Callable skill for Python package types-netaddr 1.3 — Typing stubs for netaddr |
| 921 | `azazael-pkg-types-netifaces` | packages | Callable skill for Python package types-netifaces 0.11 — Typing stubs for netifaces |
| 922 | `azazael-pkg-types-networkx` | packages | Callable skill for Python package types-networkx 3.6.1 — Typing stubs for networkx |
| 923 | `azazael-pkg-types-oauthlib` | packages | Callable skill for Python package types-oauthlib 3.3 — Typing stubs for oauthlib |
| 924 | `azazael-pkg-types-objgraph` | packages | Callable skill for Python package types-objgraph 3.6 — Typing stubs for objgraph |
| 925 | `azazael-pkg-types-olefile` | packages | Callable skill for Python package types-olefile 0.47 — Typing stubs for olefile |
| 926 | `azazael-pkg-types-openpyxl` | packages | Callable skill for Python package types-openpyxl 3.1.5 — Typing stubs for openpyxl |
| 927 | `azazael-pkg-types-opentracing` | packages | Callable skill for Python package types-opentracing 2.4 — Typing stubs for opentracing |
| 928 | `azazael-pkg-types-paramiko` | packages | Callable skill for Python package types-paramiko 4.0 — Typing stubs for paramiko |
| 929 | `azazael-pkg-types-parsimonious` | packages | Callable skill for Python package types-parsimonious 0.11 — Typing stubs for parsimonious |
| 930 | `azazael-pkg-types-passlib` | packages | Callable skill for Python package types-passlib 1.7 — Typing stubs for passlib |
| 931 | `azazael-pkg-types-passpy` | packages | Callable skill for Python package types-passpy 1.0 — Typing stubs for passpy |
| 932 | `azazael-pkg-types-peewee` | packages | Callable skill for Python package types-peewee 3.19.0 — Typing stubs for peewee |
| 933 | `azazael-pkg-types-pep8-naming` | packages | Callable skill for Python package types-pep8-naming 0.15 — Typing stubs for pep8-naming |
| 934 | `azazael-pkg-types-pexpect` | packages | Callable skill for Python package types-pexpect 4.9 — Typing stubs for pexpect |
| 935 | `azazael-pkg-types-pika-ts` | packages | Callable skill for Python package types-pika-ts 1.3 — Typing stubs for pika |
| 936 | `azazael-pkg-types-polib` | packages | Callable skill for Python package types-polib 1.2 — Typing stubs for polib |
| 937 | `azazael-pkg-types-pony` | packages | Callable skill for Python package types-pony 0.7 — Typing stubs for pony |
| 938 | `azazael-pkg-types-portpicker` | packages | Callable skill for Python package types-portpicker 1.6 — Typing stubs for portpicker |
| 939 | `azazael-pkg-types-protobuf` | packages | Callable skill for Python package types-protobuf 6.32.1 — Typing stubs for protobuf |
| 940 | `azazael-pkg-types-psutil` | packages | Callable skill for Python package types-psutil 7.2.2 — Typing stubs for psutil |
| 941 | `azazael-pkg-types-psycopg2` | packages | Callable skill for Python package types-psycopg2 2.9.11 — Typing stubs for psycopg2 |
| 942 | `azazael-pkg-types-punq` | packages | Callable skill for Python package types-punq 0.7 — Typing stubs for punq |
| 943 | `azazael-pkg-types-pyasn1` | packages | Callable skill for Python package types-pyasn1 0.6 — Typing stubs for pyasn1 |
| 944 | `azazael-pkg-types-pyaudio` | packages | Callable skill for Python package types-pyaudio 0.2 — Typing stubs for pyaudio |
| 945 | `azazael-pkg-types-pyautogui` | packages | Callable skill for Python package types-PyAutoGUI 0.9 — Typing stubs for PyAutoGUI |
| 946 | `azazael-pkg-types-pycocotools` | packages | Callable skill for Python package types-pycocotools 2.0 — Typing stubs for pycocotools |
| 947 | `azazael-pkg-types-pycurl` | packages | Callable skill for Python package types-pycurl 7.45.7 — Typing stubs for pycurl |
| 948 | `azazael-pkg-types-pyfarmhash` | packages | Callable skill for Python package types-pyfarmhash 0.4 — Typing stubs for pyfarmhash |
| 949 | `azazael-pkg-types-pyflakes` | packages | Callable skill for Python package types-pyflakes 3.4 — Typing stubs for pyflakes |
| 950 | `azazael-pkg-types-pygments` | packages | Callable skill for Python package types-Pygments 2.19 — Typing stubs for Pygments |
| 951 | `azazael-pkg-types-pyinstaller` | packages | Callable skill for Python package types-pyinstaller 6.18 — Typing stubs for pyinstaller |
| 952 | `azazael-pkg-types-pyjks` | packages | Callable skill for Python package types-pyjks 20.0 — Typing stubs for pyjks |
| 953 | `azazael-pkg-types-pyluach` | packages | Callable skill for Python package types-pyluach 2.3 — Typing stubs for pyluach |
| 954 | `azazael-pkg-types-pymeeus` | packages | Callable skill for Python package types-PyMeeus 0.5 — Typing stubs for PyMeeus |
| 955 | `azazael-pkg-types-pymysql` | packages | Callable skill for Python package types-PyMySQL 1.1 — Typing stubs for PyMySQL |
| 956 | `azazael-pkg-types-pynput` | packages | Callable skill for Python package types-pynput 1.8.1 — Typing stubs for pynput |
| 957 | `azazael-pkg-types-pyperclip` | packages | Callable skill for Python package types-pyperclip 1.9 — Typing stubs for pyperclip |
| 958 | `azazael-pkg-types-pyrfc3339` | packages | Callable skill for Python package types-pyRFC3339 2.0.1 — Typing stubs for pyRFC3339 |
| 959 | `azazael-pkg-types-pyscreeze` | packages | Callable skill for Python package types-PyScreeze 1.0.1 — Typing stubs for PyScreeze |
| 960 | `azazael-pkg-types-pyserial` | packages | Callable skill for Python package types-pyserial 3.5 — Typing stubs for pyserial |
| 961 | `azazael-pkg-types-pysftp` | packages | Callable skill for Python package types-pysftp 0.2 — Typing stubs for pysftp |
| 962 | `azazael-pkg-types-pysocks` | packages | Callable skill for Python package types-PySocks 1.7.1 — Typing stubs for PySocks |
| 963 | `azazael-pkg-types-pytest-lazy-fixture` | packages | Callable skill for Python package types-pytest-lazy-fixture 0.6 — Typing stubs for pytest-lazy-fixture |
| 964 | `azazael-pkg-types-python-crontab` | packages | Callable skill for Python package types-python-crontab 3.3 — Typing stubs for python-crontab |
| 965 | `azazael-pkg-types-python-dateutil` | packages | Callable skill for Python package types-python-dateutil 2.9 — Typing stubs for python-dateutil |
| 966 | `azazael-pkg-types-python-http-client` | packages | Callable skill for Python package types-python-http-client 3.3.7 — Typing stubs for python-http-client |
| 967 | `azazael-pkg-types-python-jenkins` | packages | Callable skill for Python package types-python-jenkins 1.8.3 — Typing stubs for python-jenkins |
| 968 | `azazael-pkg-types-python-jose` | packages | Callable skill for Python package types-python-jose 3.5 — Typing stubs for python-jose |
| 969 | `azazael-pkg-types-python-nmap` | packages | Callable skill for Python package types-python-nmap 0.7 — Typing stubs for python-nmap |
| 970 | `azazael-pkg-types-python-xlib` | packages | Callable skill for Python package types-python-xlib 0.33 — Typing stubs for python-xlib |
| 971 | `azazael-pkg-types-pytz` | packages | Callable skill for Python package types-pytz 2025.2 — Typing stubs for pytz |
| 972 | `azazael-pkg-types-pywin32` | packages | Callable skill for Python package types-pywin32 311 — Typing stubs for pywin32 |
| 973 | `azazael-pkg-types-pyxdg` | packages | Callable skill for Python package types-pyxdg 0.28 — Typing stubs for pyxdg |
| 974 | `azazael-pkg-types-pyyaml` | packages | Callable skill for Python package types-PyYAML 6.0 — Typing stubs for PyYAML |
| 975 | `azazael-pkg-types-qrbill` | packages | Callable skill for Python package types-qrbill 1.2 — Typing stubs for qrbill |
| 976 | `azazael-pkg-types-qrcode` | packages | Callable skill for Python package types-qrcode 8.2 — Typing stubs for qrcode |
| 977 | `azazael-pkg-types-ratelimit` | packages | Callable skill for Python package types-ratelimit 2.2 — Typing stubs for ratelimit |
| 978 | `azazael-pkg-types-regex` | packages | Callable skill for Python package types-regex 2026.1.15 — Typing stubs for regex |
| 979 | `azazael-pkg-types-reportlab` | packages | Callable skill for Python package types-reportlab 4.4.9 — Typing stubs for reportlab |
| 980 | `azazael-pkg-types-requests` | packages | Callable skill for Python package types-requests 2.32.4 — Typing stubs for requests |
| 981 | `azazael-pkg-types-requests-oauthlib` | packages | Callable skill for Python package types-requests-oauthlib 2.0 — Typing stubs for requests-oauthlib |
| 982 | `azazael-pkg-types-retry` | packages | Callable skill for Python package types-retry 0.9 — Typing stubs for retry |
| 983 | `azazael-pkg-types-rfc3339-validator` | packages | Callable skill for Python package types-rfc3339-validator 0.1 — Typing stubs for rfc3339-validator |
| 984 | `azazael-pkg-types-rpi-gpio` | packages | Callable skill for Python package types-RPi.GPIO 0.7 — Typing stubs for RPi.GPIO |
| 985 | `azazael-pkg-types-s2clientprotocol` | packages | Callable skill for Python package types-s2clientprotocol 5 — Typing stubs for s2clientprotocol |
| 986 | `azazael-pkg-types-seaborn` | packages | Callable skill for Python package types-seaborn 0.13.2 — Typing stubs for seaborn |
| 987 | `azazael-pkg-types-send2trash` | packages | Callable skill for Python package types-Send2Trash 2.1 — Typing stubs for Send2Trash |
| 988 | `azazael-pkg-types-setuptools` | packages | Callable skill for Python package types-setuptools 80.10 — Typing stubs for setuptools |
| 989 | `azazael-pkg-types-shapely` | packages | Callable skill for Python package types-shapely 2.1 — Typing stubs for shapely |
| 990 | `azazael-pkg-types-simple-websocket` | packages | Callable skill for Python package types-simple-websocket 1.1 — Typing stubs for simple-websocket |
| 991 | `azazael-pkg-types-simplejson` | packages | Callable skill for Python package types-simplejson 3.20 — Typing stubs for simplejson |
| 992 | `azazael-pkg-types-singledispatch` | packages | Callable skill for Python package types-singledispatch 4.1 — Typing stubs for singledispatch |
| 993 | `azazael-pkg-types-six` | packages | Callable skill for Python package types-six 1.17 — Typing stubs for six |
| 994 | `azazael-pkg-types-slumber` | packages | Callable skill for Python package types-slumber 0.7 — Typing stubs for slumber |
| 995 | `azazael-pkg-types-str2bool` | packages | Callable skill for Python package types-str2bool 1.1 — Typing stubs for str2bool |
| 996 | `azazael-pkg-types-tabulate` | packages | Callable skill for Python package types-tabulate 0.9 — Typing stubs for tabulate |
| 997 | `azazael-pkg-types-tensorflow` | packages | Callable skill for Python package types-tensorflow 2.18.0 — Typing stubs for tensorflow |
| 998 | `azazael-pkg-types-tgcrypto` | packages | Callable skill for Python package types-TgCrypto 1.2 — Typing stubs for TgCrypto |
| 999 | `azazael-pkg-types-toml` | packages | Callable skill for Python package types-toml 0.10 — Typing stubs for toml |
| 1000 | `azazael-pkg-types-toposort` | packages | Callable skill for Python package types-toposort 1.10 — Typing stubs for toposort |
| 1001 | `azazael-pkg-types-tqdm` | packages | Callable skill for Python package types-tqdm 4.67.3 — Typing stubs for tqdm |
| 1002 | `azazael-pkg-types-translationstring` | packages | Callable skill for Python package types-translationstring 1.4 — Typing stubs for translationstring |
| 1003 | `azazael-pkg-types-ttkthemes` | packages | Callable skill for Python package types-ttkthemes 3.3 — Typing stubs for ttkthemes |
| 1004 | `azazael-pkg-types-tzdata` | packages | Callable skill for Python package types-tzdata 2025 — Typing stubs for tzdata |
| 1005 | `azazael-pkg-types-ujson` | packages | Callable skill for Python package types-ujson 5.10 — Typing stubs for ujson |
| 1006 | `azazael-pkg-types-unidiff` | packages | Callable skill for Python package types-unidiff 0.7 — Typing stubs for unidiff |
| 1007 | `azazael-pkg-types-untangle` | packages | Callable skill for Python package types-untangle 1.2 — Typing stubs for untangle |
| 1008 | `azazael-pkg-types-usersettings` | packages | Callable skill for Python package types-usersettings 1.1 — Typing stubs for usersettings |
| 1009 | `azazael-pkg-types-uwsgi` | packages | Callable skill for Python package types-uWSGI 2.0 — Typing stubs for uWSGI |
| 1010 | `azazael-pkg-types-vobject` | packages | Callable skill for Python package types-vobject 0.9.9 — Typing stubs for vobject |
| 1011 | `azazael-pkg-types-waitress` | packages | Callable skill for Python package types-waitress 3.0.1 — Typing stubs for waitress |
| 1012 | `azazael-pkg-types-watchpoints` | packages | Callable skill for Python package types-watchpoints 0.2.5 — Typing stubs for watchpoints |
| 1013 | `azazael-pkg-types-webencodings` | packages | Callable skill for Python package types-webencodings 0.5 — Typing stubs for webencodings |
| 1014 | `azazael-pkg-types-webob` | packages | Callable skill for Python package types-WebOb 1.8 — Typing stubs for WebOb |
| 1015 | `azazael-pkg-types-whatthepatch` | packages | Callable skill for Python package types-whatthepatch 1.0 — Typing stubs for whatthepatch |
| 1016 | `azazael-pkg-types-workalendar` | packages | Callable skill for Python package types-workalendar 17.0 — Typing stubs for workalendar |
| 1017 | `azazael-pkg-types-wtforms` | packages | Callable skill for Python package types-WTForms 3.2.1 — Typing stubs for WTForms |
| 1018 | `azazael-pkg-types-wurlitzer` | packages | Callable skill for Python package types-wurlitzer 3.1 — Typing stubs for wurlitzer |
| 1019 | `azazael-pkg-types-www-authenticate` | packages | Callable skill for Python package types-www-authenticate 0.9 — Typing stubs for www-authenticate |
| 1020 | `azazael-pkg-types-xdgenvpy` | packages | Callable skill for Python package types-xdgenvpy 3.0 — Typing stubs for xdgenvpy |
| 1021 | `azazael-pkg-types-xlrd` | packages | Callable skill for Python package types-xlrd 2.0 — Typing stubs for xlrd |
| 1022 | `azazael-pkg-types-xmldiff` | packages | Callable skill for Python package types-xmldiff 2.7 — Typing stubs for xmldiff |
| 1023 | `azazael-pkg-types-xmltodict` | packages | Callable skill for Python package types-xmltodict 1.0.1 — Typing stubs for xmltodict |
| 1024 | `azazael-pkg-types-yt-dlp` | packages | Callable skill for Python package types-yt-dlp 2026.1.31 — Typing stubs for yt-dlp |
| 1025 | `azazael-pkg-types-zstd` | packages | Callable skill for Python package types-zstd 1.5.7.3 — Typing stubs for zstd |
| 1026 | `azazael-pkg-types-zxcvbn` | packages | Callable skill for Python package types-zxcvbn 4.5 — Typing stubs for zxcvbn |
| 1027 | `azazael-pkg-typing-extensions` | packages | Callable skill for Python package typing_extensions 4.15.0 — Backported and Experimental Type Hints for Pyt... |
| 1028 | `azazael-pkg-typing-inspection` | packages | Callable skill for Python package typing-inspection 0.4.2 — Runtime typing introspection tools |
| 1029 | `azazael-pkg-ubi-reader` | packages | Callable skill for Python package ubi-reader 0.8.5 — Extract files from UBI and UBIFS images. |
| 1030 | `azazael-pkg-uc-micro-py` | packages | Callable skill for Python package uc-micro-py 2.0.0 — Micro subset of unicode data files for linkify-it-py ... |
| 1031 | `azazael-pkg-ufolib2` | packages | Callable skill for Python package ufoLib2 0.18.1 — ufoLib2 is a UFO font processing library. |
| 1032 | `azazael-pkg-uharfbuzz` | packages | Callable skill for Python package uharfbuzz 0.53.3 — Streamlined Cython bindings for the harfbuzz shaping e... |
| 1033 | `azazael-pkg-ujson` | packages | Callable skill for Python package ujson 5.11.0 — Ultra fast JSON encoder and decoder for Python |
| 1034 | `azazael-pkg-unblob` | packages | Callable skill for Python package unblob 26.3.30 — Extract files from any kind of container formats |
| 1035 | `azazael-pkg-unicodedata2` | packages | Callable skill for Python package unicodedata2 17.0.1 — Unicodedata backport updated to the latest Unicode ... |
| 1036 | `azazael-pkg-unicorn` | packages | Callable skill for Python package unicorn 0.0.0 — Unicorn CPU emulator engine |
| 1037 | `azazael-pkg-unicrypto` | packages | Callable skill for Python package unicrypto 0.0.12 — Unified interface for cryptographic libraries |
| 1038 | `azazael-pkg-uritemplate` | packages | Callable skill for Python package uritemplate 4.2.0 — Implementation of RFC 6570 URI Templates |
| 1039 | `azazael-pkg-urllib3` | packages | Callable skill for Python package urllib3 2.6.3 — HTTP library with thread-safe connection pooling, file po... |
| 1040 | `azazael-pkg-uro` | packages | Callable skill for Python package uro 1.0.2 — A python tool to declutter url lists for crawling/pentesting |
| 1041 | `azazael-pkg-urwid` | packages | Callable skill for Python package urwid 3.0.4 — A full-featured console (xterm et al.) user interface library |
| 1042 | `azazael-pkg-userpath` | packages | Callable skill for Python package userpath 1.9.2 — Cross-platform tool for adding locations to the user PATH |
| 1043 | `azazael-pkg-uvicorn` | packages | Callable skill for Python package uvicorn 0.38.0 — The lightning-fast ASGI server. |
| 1044 | `azazael-pkg-uvloop` | packages | Callable skill for Python package uvloop 0.22.1 — Fast implementation of asyncio event loop on top of libuv |
| 1045 | `azazael-pkg-vadersentiment` | packages | Callable skill for Python package vaderSentiment 3.3.2 — VADER Sentiment Analysis. VADER (Valence Aware Dic... |
| 1046 | `azazael-pkg-validators` | packages | Callable skill for Python package validators 0.20.0 — Python Data Validation for Humans™. |
| 1047 | `azazael-pkg-venusian` | packages | Callable skill for Python package venusian 3.1.1 — A library for deferring decorator actions |
| 1048 | `azazael-pkg-vinetto` | packages | Callable skill for Python package vinetto 0.9.15 — Vinetto: The Thumbnail File Parser |
| 1049 | `azazael-pkg-virtualenv` | packages | Callable skill for Python package virtualenv 21.4.1 — Virtual Python Environment builder |
| 1050 | `azazael-pkg-volatility3` | packages | Callable skill for Python package volatility3 2.28.0 — Memory forensics framework |
| 1051 | `azazael-pkg-wafw00f` | packages | Callable skill for Python package wafw00f 2.4.2 — The Web Application Firewall Fingerprinting Toolkit |
| 1052 | `azazael-pkg-wapiti-swagger` | packages | Callable skill for Python package wapiti-swagger 0.1.9 — A library for parsing and generating request bodie... |
| 1053 | `azazael-pkg-wapiti3` | packages | Callable skill for Python package wapiti3 3.2.10 — A web application vulnerability scanner |
| 1054 | `azazael-pkg-watchdog` | packages | Callable skill for Python package watchdog 6.0.0 — Filesystem events monitoring |
| 1055 | `azazael-pkg-waybackpy` | packages | Callable skill for Python package waybackpy 3.0.6 — Python package that interfaces with the Internet Archiv... |
| 1056 | `azazael-pkg-wcwidth` | packages | Callable skill for Python package wcwidth 0.2.14 — Measures the displayed width of unicode strings in a ter... |
| 1057 | `azazael-pkg-webargs` | packages | Callable skill for Python package webargs 8.7.1 — Declarative parsing and validation of HTTP request object... |
| 1058 | `azazael-pkg-webcolors` | packages | Callable skill for Python package webcolors 25.10.0 — A library for working with the color formats defined ... |
| 1059 | `azazael-pkg-webdriver-manager` | packages | Callable skill for Python package webdriver-manager 4.1.0 — Add your description here |
| 1060 | `azazael-pkg-webencodings` | packages | Callable skill for Python package webencodings 0.5.1 — Character encoding aliases for legacy web content |
| 1061 | `azazael-pkg-webob` | packages | Callable skill for Python package WebOb 1.8.9 — WSGI request and response object |
| 1062 | `azazael-pkg-websocket-client` | packages | Callable skill for Python package websocket-client 1.9.0 — WebSocket client for Python with low level API o... |
| 1063 | `azazael-pkg-websockets` | packages | Callable skill for Python package websockets 16.0 — An implementation of the WebSocket Protocol (RFC 6455 &... |
| 1064 | `azazael-pkg-websploit` | packages | Callable skill for Python package websploit 4.0.4 — Websploit is a high level MITM framework |
| 1065 | `azazael-pkg-werkzeug` | packages | Callable skill for Python package Werkzeug 3.1.8 — The comprehensive WSGI web application library. |
| 1066 | `azazael-pkg-wfuzz` | packages | Callable skill for Python package wfuzz 3.1.0 — Wfuzz - The web fuzzer |
| 1067 | `azazael-pkg-wget` | packages | Callable skill for Python package wget 3.2 — pure python download utility |
| 1068 | `azazael-pkg-wheel` | packages | Callable skill for Python package wheel 0.47.0 — Command line tool for manipulating wheel files |
| 1069 | `azazael-pkg-wifiphisher` | packages | Callable skill for Python package wifiphisher 1.4 — Automated phishing attacks against Wi-Fi networks |
| 1070 | `azazael-pkg-wifipumpkin3` | packages | Callable skill for Python package wifipumpkin3 1.1.7 — Powerful framework for rogue access point attack. |
| 1071 | `azazael-pkg-wifite` | packages | Callable skill for Python package wifite 2.8.1 — Wireless Network Auditor for Linux & Android |
| 1072 | `azazael-pkg-wig-ng` | packages | Callable skill for Python package wig-ng 0.1 — WIG-ng is a free and open source utility for WiFi device fin... |
| 1073 | `azazael-pkg-winacl` | packages | Callable skill for Python package winacl 0.1.9 — ACL/ACE/Security Descriptor manipulation library in pure P... |
| 1074 | `azazael-pkg-witnessme` | packages | Callable skill for Python package witnessme 1.5.0 — Web Inventory tool that uses Pyppeteer (headless Chrome... |
| 1075 | `azazael-pkg-wordcloud` | packages | Callable skill for Python package wordcloud 1.9.4+dfsg — A little word cloud generator |
| 1076 | `azazael-pkg-wordlistraider` | packages | Callable skill for Python package wordlistraider 1.0 — Returns a selection of words that matches the passed... |
| 1077 | `azazael-pkg-wrapt` | packages | Callable skill for Python package wrapt 2.1.1 — Module for decorators, wrappers and monkey patching. |
| 1078 | `azazael-pkg-wsgidav` | packages | Callable skill for Python package WsgiDAV 4.3.3 — Generic and extendable WebDAV server based on WSGI |
| 1079 | `azazael-pkg-wsproto` | packages | Callable skill for Python package wsproto 1.3.2 — Pure-Python WebSocket protocol implementation |
| 1080 | `azazael-pkg-wxpython` | packages | Callable skill for Python package wxPython 4.2.4 — Cross platform GUI toolkit for Python, "Phoenix" version |
| 1081 | `azazael-pkg-xattr` | packages | Callable skill for Python package xattr 1.3.0 — Python wrapper for extended filesystem attributes |
| 1082 | `azazael-pkg-xcffib` | packages | Callable skill for Python package xcffib 1.5.0 — A drop in replacement for xpyb, an XCB python binding |
| 1083 | `azazael-pkg-xdg` | packages | Callable skill for Python package xdg 5 — wrapper for PyXDG to provide the API of xdg |
| 1084 | `azazael-pkg-xlrd` | packages | Callable skill for Python package xlrd 2.0.2 — Library for developers to extract data from Microsoft Excel ... |
| 1085 | `azazael-pkg-xlsxwriter` | packages | Callable skill for Python package XlsxWriter 3.1.9 — A Python module for creating Excel XLSX files. |
| 1086 | `azazael-pkg-xlwt` | packages | Callable skill for Python package xlwt 1.3.0 — Library to create spreadsheet files compatible with MS Excel... |
| 1087 | `azazael-pkg-xmltodict` | packages | Callable skill for Python package xmltodict 0.13.0 — Makes working with XML feel like you are working with ... |
| 1088 | `azazael-pkg-xsrfprobe` | packages | Callable skill for Python package xsrfprobe 2.3.0 — The Prime Cross Site Request Forgery (CSRF) Audit & Exp... |
| 1089 | `azazael-pkg-yara-python` | packages | Callable skill for Python package yara-python 4.5.4 — Python interface for YARA |
| 1090 | `azazael-pkg-yarl` | packages | Callable skill for Python package yarl 1.23.0 — Yet another URL library |
| 1091 | `azazael-pkg-yattag` | packages | Callable skill for Python package yattag 1.16.1 — Generate HTML or XML in a pythonic way. Pure python alter... |
| 1092 | `azazael-pkg-zc-lockfile` | packages | Callable skill for Python package zc.lockfile 4.0 — Basic inter-process locks |
| 1093 | `azazael-pkg-zict` | packages | Callable skill for Python package zict 3.0.0 — Mutable mapping tools |
| 1094 | `azazael-pkg-zim` | packages | Callable skill for Python package zim 0.76.3 — Zim desktop wiki |
| 1095 | `azazael-pkg-zipp` | packages | Callable skill for Python package zipp 3.23.0 — Backport of pathlib-compatible object wrapper for zip files |
| 1096 | `azazael-pkg-zope-deprecation` | packages | Callable skill for Python package zope.deprecation 6.0 — Zope Deprecation Infrastructure |
| 1097 | `azazael-pkg-zope-interface` | packages | Callable skill for Python package zope.interface 8.5 — Interfaces for Python |
| 1098 | `azazael-pkg-zopfli` | packages | Callable skill for Python package zopfli 0.4.2 — Zopfli module for python |
| 1099 | `azazael-pkg-zstandard` | packages | Callable skill for Python package zstandard 0.25.0 — Zstandard bindings for Python |
| 1100 | `azazael-pkg-zstd` | packages | Callable skill for Python package zstd 1.5.7.3 — ZSTD Bindings for Python |

## Skill Quick Reference — 3.14t Package Skills (1101-1174)
| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 1101 | `azazael-pkg314t-anyio` | packages | Callable skill for Python package anyio 4.14.2 — High-level concurrency and networking framework on top of ... |
| 1102 | `azazael-pkg314t-ast-serialize` | packages | Callable skill for Python package ast_serialize 0.5.0 — Python bindings for mypy AST serialization |
| 1103 | `azazael-pkg314t-attrs` | packages | Callable skill for Python package attrs 26.1.0 — Classes Without Boilerplate |
| 1104 | `azazael-pkg314t-autoflake` | packages | Callable skill for Python package autoflake 2.3.3 — Removes unused imports and unused variables |
| 1105 | `azazael-pkg314t-azazael-core` | packages | Callable skill for Python package azazael-core 3.1.0 — AZAZAEL Core — Path resolution, worm registry, free-... |
| 1106 | `azazael-pkg314t-beautifulsoup4` | packages | Callable skill for Python package beautifulsoup4 4.15.0 — Screen-scraping library |
| 1107 | `azazael-pkg314t-blinker` | packages | Callable skill for Python package blinker 1.9.0 — Fast, simple object-to-object and broadcast signaling |
| 1108 | `azazael-pkg314t-bs4` | packages | Callable skill for Python package bs4 0.0.2 — Dummy package for Beautiful Soup (beautifulsoup4) |
| 1109 | `azazael-pkg314t-certifi` | packages | Callable skill for Python package certifi 2026.7.22 — Python package for providing Mozilla's CA Bundle. |
| 1110 | `azazael-pkg314t-charset-normalizer` | packages | Callable skill for Python package charset-normalizer 3.5.0 — The Real First Universal Charset Detector. Ope... |
| 1111 | `azazael-pkg314t-click` | packages | Callable skill for Python package click 8.4.2 — Composable command line interface toolkit |
| 1112 | `azazael-pkg314t-colorama` | packages | Callable skill for Python package colorama 0.4.6 — Cross-platform colored terminal text. |
| 1113 | `azazael-pkg314t-dnspython` | packages | Callable skill for Python package dnspython 2.8.0 — DNS toolkit |
| 1114 | `azazael-pkg314t-flask` | packages | Callable skill for Python package Flask 3.1.3 — A simple framework for building complex web applications. |
| 1115 | `azazael-pkg314t-gevent` | packages | Callable skill for Python package gevent 26.8.0 — Coroutine-based network library |
| 1116 | `azazael-pkg314t-greenlet` | packages | Callable skill for Python package greenlet 3.5.5 — Lightweight in-process concurrent programming |
| 1117 | `azazael-pkg314t-h11` | packages | Callable skill for Python package h11 0.16.0 — A pure-Python, bring-your-own-I/O implementation of HTTP/1.1 |
| 1118 | `azazael-pkg314t-holehe` | packages | Callable skill for Python package holehe 1.61 — holehe allows you to check if the mail is used on different... |
| 1119 | `azazael-pkg314t-httpcore` | packages | Callable skill for Python package httpcore 1.0.9 — A minimal low-level HTTP client. |
| 1120 | `azazael-pkg314t-httpx` | packages | Callable skill for Python package httpx 0.28.1 — The next generation HTTP client. |
| 1121 | `azazael-pkg314t-hypothesis` | packages | Callable skill for Python package hypothesis 6.155.6 — The property-based testing library for Python |
| 1122 | `azazael-pkg314t-idna` | packages | Callable skill for Python package idna 3.18 — Internationalized Domain Names in Applications (IDNA) |
| 1123 | `azazael-pkg314t-iniconfig` | packages | Callable skill for Python package iniconfig 2.3.0 — brain-dead simple config-ini parsing |
| 1124 | `azazael-pkg314t-itsdangerous` | packages | Callable skill for Python package itsdangerous 2.2.0 — Safely pass data to untrusted environments and back. |
| 1125 | `azazael-pkg314t-jinja2` | packages | Callable skill for Python package Jinja2 3.1.6 — A very fast and expressive template engine. |
| 1126 | `azazael-pkg314t-joblib` | packages | Callable skill for Python package joblib 1.5.3 — Lightweight pipelining with Python functions |
| 1127 | `azazael-pkg314t-librt` | packages | Callable skill for Python package librt 0.11.0 — Mypyc runtime library |
| 1128 | `azazael-pkg314t-markupsafe` | packages | Callable skill for Python package MarkupSafe 3.0.3 — Safely add untrusted strings to HTML/XML markup. |
| 1129 | `azazael-pkg314t-mypy` | packages | Callable skill for Python package mypy 2.1.0 — Optional static typing for Python |
| 1130 | `azazael-pkg314t-mypy-extensions` | packages | Callable skill for Python package mypy_extensions 1.1.0 — Type system extensions for programs checked with ... |
| 1131 | `azazael-pkg314t-narwhals` | packages | Callable skill for Python package narwhals 2.24.0 — Extremely lightweight compatibility layer between dataf... |
| 1132 | `azazael-pkg314t-nuitka` | packages | Callable skill for Python package Nuitka 4.1.2 — Python compiler with full language support and CPython com... |
| 1133 | `azazael-pkg314t-numpy` | packages | Callable skill for Python package numpy 2.4.6 — Fundamental package for array computing in Python |
| 1134 | `azazael-pkg314t-outcome` | packages | Callable skill for Python package outcome 1.3.0.post0 — Capture the outcome of Python function calls. |
| 1135 | `azazael-pkg314t-packaging` | packages | Callable skill for Python package packaging 26.2 — Core utilities for Python packages |
| 1136 | `azazael-pkg314t-patchelf` | packages | Callable skill for Python package patchelf 0.17.2.4 — A small utility to modify the dynamic linker and RPAT... |
| 1137 | `azazael-pkg314t-patchelf-wrapper` | packages | Callable skill for Python package patchelf-wrapper 1.2.0 — A wrapper for patchelf |
| 1138 | `azazael-pkg314t-pathspec` | packages | Callable skill for Python package pathspec 1.1.1 — Utility library for gitignore style pattern matching of ... |
| 1139 | `azazael-pkg314t-phonenumbers` | packages | Callable skill for Python package phonenumbers 9.0.36 — Python version of Google's common library for parsi... |
| 1140 | `azazael-pkg314t-pip` | packages | Callable skill for Python package pip 26.1.2 — The PyPA recommended tool for installing Python packages. |
| 1141 | `azazael-pkg314t-pluggy` | packages | Callable skill for Python package pluggy 1.6.0 — plugin and hook calling mechanisms for python |
| 1142 | `azazael-pkg314t-progress` | packages | Callable skill for Python package progress 1.6.1 — Easy to use progress bars |
| 1143 | `azazael-pkg314t-psutil` | packages | Callable skill for Python package psutil 7.2.2 — Cross-platform lib for process and system monitoring. |
| 1144 | `azazael-pkg314t-pyflakes` | packages | Callable skill for Python package pyflakes 3.4.0 — passive checker of Python programs |
| 1145 | `azazael-pkg314t-pygments` | packages | Callable skill for Python package Pygments 2.20.0 — Pygments is a syntax highlighting package written in Py... |
| 1146 | `azazael-pkg314t-pysocks` | packages | Callable skill for Python package PySocks 1.7.1 — A Python SOCKS client module. See https://github.com/Anor... |
| 1147 | `azazael-pkg314t-pytest` | packages | Callable skill for Python package pytest 9.1.0 — pytest: simple powerful testing with Python |
| 1148 | `azazael-pkg314t-python-dotenv` | packages | Callable skill for Python package python-dotenv 1.2.2 — Read key-value pairs from a .env file and set them ... |
| 1149 | `azazael-pkg314t-pytz` | packages | Callable skill for Python package pytz 2026.3.post1 — World timezone definitions, modern and historical |
| 1150 | `azazael-pkg314t-pyyaml` | packages | Callable skill for Python package PyYAML 6.0.3 — YAML parser and emitter for Python |
| 1151 | `azazael-pkg314t-requests` | packages | Callable skill for Python package requests 2.34.2 — Python HTTP for Humans. |
| 1152 | `azazael-pkg314t-scikit-learn` | packages | Callable skill for Python package scikit-learn 1.9.0 — A set of python modules for machine learning and dat... |
| 1153 | `azazael-pkg314t-scipy` | packages | Callable skill for Python package scipy 1.18.0 — Fundamental algorithms for scientific computing in Python |
| 1154 | `azazael-pkg314t-six` | packages | Callable skill for Python package six 1.17.0 — Python 2 and 3 compatibility utilities |
| 1155 | `azazael-pkg314t-sniffio` | packages | Callable skill for Python package sniffio 1.3.1 — Sniff out which async library your code is running under |
| 1156 | `azazael-pkg314t-socksio` | packages | Callable skill for Python package socksio 1.0.0 — Sans-I/O implementation of SOCKS4, SOCKS4A, and SOCKS5. |
| 1157 | `azazael-pkg314t-sortedcontainers` | packages | Callable skill for Python package sortedcontainers 2.4.0 — Sorted Containers -- Sorted List, Sorted Dict, S... |
| 1158 | `azazael-pkg314t-soupsieve` | packages | Callable skill for Python package soupsieve 2.9.2 — A modern CSS selector implementation for Beautiful Soup. |
| 1159 | `azazael-pkg314t-tabulate` | packages | Callable skill for Python package tabulate 0.10.0 — Pretty-print tabular data |
| 1160 | `azazael-pkg314t-termcolor` | packages | Callable skill for Python package termcolor 3.3.0 — ANSI color formatting for output in terminal |
| 1161 | `azazael-pkg314t-threadpoolctl` | packages | Callable skill for Python package threadpoolctl 3.6.0 — threadpoolctl |
| 1162 | `azazael-pkg314t-toml` | packages | Callable skill for Python package toml 0.10.2 — Python Library for Tom's Obvious, Minimal Language |
| 1163 | `azazael-pkg314t-torbot` | packages | Callable skill for Python package torbot 4.3.0 — TorBot is an OSINT tool for the dark web. |
| 1164 | `azazael-pkg314t-tqdm` | packages | Callable skill for Python package tqdm 4.70.0 — Fast, Extensible Progress Meter |
| 1165 | `azazael-pkg314t-treelib` | packages | Callable skill for Python package treelib 1.8.0 — A Python implementation of tree structure. |
| 1166 | `azazael-pkg314t-trio` | packages | Callable skill for Python package trio 0.34.0 — A friendly Python library for async concurrency and I/O |
| 1167 | `azazael-pkg314t-typing-extensions` | packages | Callable skill for Python package typing_extensions 4.15.0 — Backported and Experimental Type Hints for Pyt... |
| 1168 | `azazael-pkg314t-unipath` | packages | Callable skill for Python package Unipath 1.1 — Object-oriented alternative to os/os.path/shutil |
| 1169 | `azazael-pkg314t-urllib3` | packages | Callable skill for Python package urllib3 2.7.0 — HTTP library with thread-safe connection pooling, file po... |
| 1170 | `azazael-pkg314t-validators` | packages | Callable skill for Python package validators 0.35.0 — Python Data Validation for Humans™ |
| 1171 | `azazael-pkg314t-werkzeug` | packages | Callable skill for Python package Werkzeug 3.1.8 — The comprehensive WSGI web application library. |
| 1172 | `azazael-pkg314t-yt-dlp` | packages | Callable skill for Python package yt-dlp 2026.7.4 — A feature-rich command-line audio/video downloader |
| 1173 | `azazael-pkg314t-zope-event` | packages | Callable skill for Python package zope.event 6.2 — Very basic event publishing system |
| 1174 | `azazael-pkg314t-zope-interface` | packages | Callable skill for Python package zope.interface 8.5 — Interfaces for Python |

## Skill Quick Reference — Binary Tool Skills (1175-1220)
| # | Skill | Category | Description |
|---|-------|----------|-------------|
| 1175 | `azazael-bin-amass` | recon | Callable skill for amass — OWASP attack-surface enumeration and mapping |
| 1176 | `azazael-bin-bettercap` | intercept | Callable skill for bettercap — Swiss-army knife for MITM attacks, network recon, and monitoring |
| 1177 | `azazael-bin-dirb` | web | Callable skill for dirb — Web content scanner / directory brute-forcer |
| 1178 | `azazael-bin-dnsx` | recon | Callable skill for dnsx — Fast and multi-purpose DNS toolkit (ProjectDiscovery) |
| 1179 | `azazael-bin-exiftool` | osint | Callable skill for exiftool — Read/write/edit EXIF metadata in image/audio/video files (Phil Harvey) |
| 1180 | `azazael-bin-feroxbuster` | web | Callable skill for feroxbuster — Fast, simple content discovery tool |
| 1181 | `azazael-bin-ffmpeg` | media | Callable skill for ffmpeg — Universal audio/video transcoding and processing (FFmpeg) |
| 1182 | `azazael-bin-ffuf` | web | Callable skill for ffuf — Fast web fuzzer written in Go |
| 1183 | `azazael-bin-foremost` | forensics | Callable skill for foremost — File carving / data recovery from disk images (foremost) |
| 1184 | `azazael-bin-ghunt` | osint | Callable skill for ghunt — Google account OSINT (requires cookies) |
| 1185 | `azazael-bin-gitleaks` | security | Callable skill for gitleaks — Scan git repos for secrets and credentials |
| 1186 | `azazael-bin-gobuster` | web | Callable skill for gobuster — Directory/file and DNS subdomain brute-forcer |
| 1187 | `azazael-bin-hashcat` | cracking | Callable skill for hashcat — Advanced password recovery / GPU hash cracking |
| 1188 | `azazael-bin-httpx` | recon | Callable skill for httpx — Fast HTTP probe tool (ProjectDiscovery Go) — discover working HTTP hosts. NOTE: ... |
| 1189 | `azazael-bin-hydra` | cracking | Callable skill for hydra — Online password cracking (network services brute-force) |
| 1190 | `azazael-bin-john` | cracking | Callable skill for john — John the Ripper — offline password cracker |
| 1191 | `azazael-bin-joomscan` | web | Callable skill for joomscan — Joomla CMS vulnerability scanner (OWASP) |
| 1192 | `azazael-bin-llama-cpp` | ai | Callable skill for llama-cpp — LLM inference engine for GGUF models (llama.cpp) |
| 1193 | `azazael-bin-maigret` | osint | Callable skill for maigret — Username OSINT across 3,000+ sites |
| 1194 | `azazael-bin-masscan` | recon | Callable skill for masscan — Internet-scale port scanner (scans entire internet in <5 min) |
| 1195 | `azazael-bin-mitmproxy` | intercept | Callable skill for mitmproxy — Interactive HTTPS man-in-the-middle proxy |
| 1196 | `azazael-bin-naabu` | recon | Callable skill for naabu — Fast port scanner (ProjectDiscovery) |
| 1197 | `azazael-bin-nikto` | web | Callable skill for nikto — Web server scanner for misconfigurations and known vulnerabilities |
| 1198 | `azazael-bin-nmap` | recon | Callable skill for nmap — Network discovery and security scanning |
| 1199 | `azazael-bin-nuclei` | recon | Callable skill for nuclei — Fast vulnerability scanner based on YAML templates (ProjectDiscovery) |
| 1200 | `azazael-bin-ollama` | ai | Callable skill for ollama — Run open-source LLMs locally with one command (170K+ stars) |
| 1201 | `azazael-bin-open-webui` | ai | Callable skill for open-webui — Self-hosted AI chat web UI (works with Ollama/OpenAI) |
| 1202 | `azazael-bin-osintgram` | osint | Callable skill for osintgram — Instagram OSINT via public API |
| 1203 | `azazael-bin-phoneinfoga` | osint | Callable skill for phoneinfoga — Phone number OSINT and footprinting |
| 1204 | `azazael-bin-responder` | intercept | Callable skill for responder — LLMNR/NBT-NS/mDNS responder for credential capture |
| 1205 | `azazael-bin-rustscan` | recon | Callable skill for rustscan — Ultra-fast port scanner written in Rust (feeds nmap) |
| 1206 | `azazael-bin-seclists` | data | Callable skill for seclists — SecLists — massive collection of wordlists for security testing (Daniel Miess... |
| 1207 | `azazael-bin-sglang` | ai | Callable skill for sglang — Fast serving framework for LLMs and VLMs |
| 1208 | `azazael-bin-sherlock` | osint | Callable skill for sherlock — Hunt down social media accounts by username |
| 1209 | `azazael-bin-snort` | ids | Callable skill for snort — Open-source network intrusion detection/prevention system (Cisco) |
| 1210 | `azazael-bin-social-analyzer` | osint | Callable skill for social-analyzer — Social media analysis and API-free lookup |
| 1211 | `azazael-bin-spiderfoot` | osint | Callable skill for spiderfoot — Automated OSINT correlation across 200+ sources |
| 1212 | `azazael-bin-sqlmap` | web | Callable skill for sqlmap — Automatic SQL injection and database takeover tool |
| 1213 | `azazael-bin-subfinder` | recon | Callable skill for subfinder — Passive subdomain discovery (ProjectDiscovery) |
| 1214 | `azazael-bin-syft` | security | Callable skill for syft — Generate SBOM (Software Bill of Materials) from container images/filesystems (Anc... |
| 1215 | `azazael-bin-theHarvester` | osint | Callable skill for theHarvester — Email, subdomain and hostname enumeration |
| 1216 | `azazael-bin-trivy` | security | Callable skill for trivy — Comprehensive vulnerability scanner for containers, filesystems, git repos (Aqua... |
| 1217 | `azazael-bin-trufflehog` | security | Callable skill for trufflehog — Find leaked credentials across repos/files/APIs |
| 1218 | `azazael-bin-tshark` | network | Callable skill for tshark — CLI packet analyzer (Wireshark terminal edition) |
| 1219 | `azazael-bin-vllm` | ai | Callable skill for vllm — High-throughput LLM serving engine (PagedAttention) |
| 1220 | `azazael-bin-wpscan` | web | Callable skill for wpscan — WordPress vulnerability scanner |
| 1221 | `azazael-kali-graph-protocol` | process | Established Kali → atlas graph protocol — rsync mirror, .git boundary sealing the home-gitignore leak, go/+venv exclusions, extract (NOT update) → cluster-only → tree → cosmos. Encode of 4h of stalled runs: 2,004 files scanned → 41,524 nodes in ~3 min. |
| 1222 | `azazael-archive-restore` | process | Archive-restore provenance pattern — restoring old-only functionality from the G: historical archive as reference copies: copy-don't-move, generation labels, byte-verification (robocopy + SHA-256 + cmp), inherited-defect documentation in the provenance README, post-restore sanity passes (syntax, safe-import, guarded dry-run). Encode of Session 28's restored trees. |
| 1223 | `aoa-architecture` | architecture | AOA (Armorie-of-Anubis) project architecture — umbrella orchestrator, quartet neural core (Azazael/CODEX/Eve/Libra), 8 arms, 4 support arms, cross-arm routing, event bus, session lifecycle, DirectMemory integration. Atlas artifacts: `output/aoa_atlas/AOA_AUDIT_MAP.md` (5-generation hash audit + 8-arm/32-cap map) + `output/aoa_atlas/AOA_EVOLUTION_CATALOG.md` (Desktop-vs-gen-1 diff, +6 caps). |
| 1224 | `aoa-accurate-disclosure` | documentation | AOA Accurate Architecture Disclosure — source-code audited diagrams reflecting the real 3-tier architecture, DreamingModule, MetaCognitionWorm, 17 worm categories, correct Quartet meaning. Created after audit found the previous disclosure was inaccurate. `audit_date: 2026-07-02`. |
| 1225 | `aoa-disclosure-build` | domain | AOA Architecture Disclosure HTML and MP4 build pipeline — 14-diagram whitepaper with 12-color semantic Mermaid palette, Puppeteer scroll capture, HEVC encoding. Load when building or updating the AOA architecture disclosure. `priority: high`, v2.0.0. |
| 1226 | `aoa-html-builder` | documentation | AOA Architecture HTML Builder — generates professional Mermaid-based architecture disclosure documents. Windows Git Bash heredoc workaround (short-line strategy), colorized classDef patterns, 7-diagram layout, particle JS, benchmark cards, arm capability tables. Related: `html-render-verification` (#1248), `aoa-artifact-cross-check` (#1250), `builder-status-discipline` (#1252), `pre-action-gate-lite` (#1253). |
| 1227 | `azazael-inference` | architecture | Azazael multi-provider AI inference — 11 free LLM providers, OpenAI-compatible API, NimClient, InferenceBusPublisher, provider registry. Load when working with AI inference, LLM integration, or the inference module. `created: 2026-06-06`. |
| 1228 | `azazael-inference-integration` | architecture | Azazael inference integration — 10-point strategy, P0-P2 implementations (MetaCluster LLM insights, adaptive routing, InferenceSubscriberWorm), audit findings. Load when wiring inference into existing systems. Parent: `azazael-inference`. `created: 2026-06-06`. |
| 1229 | `azazael-inference-worms` | architecture | Azazael inference worms — InferenceWorm (provider-agnostic) and NimInferenceWorm (multi-provider). Load when using or modifying inference worm implementations. Parent: `azazael-inference`. `created: 2026-06-06`. |
| 1230 | `investigation-990-forensics` | investigation | Nonprofit Form 990 forensic analysis — Schedule D investment tracking, Schedule L related-party detection, CFO/CEO compensation inversion, single-program reporting, contribution anomaly detection, multi-year z-score analysis. Distilled from the BCC investigation. `auto_load: false`. |
| 1231 | `investigation-board-governance` | investigation | Board governance forensics — conflict of interest detection, board composition mapping, hidden network analysis, Schedule L cross-referencing, fiduciary duty breach patterns. Distilled from the BCC investigation. `auto_load: false`. |
| 1232 | `investigation-document-construction` | investigation | HTML evidence document construction standards — citation patterns, cross-referencing, styling conventions, document structure, evidence anchoring, deliverable taxonomy. Distilled from 60+ investigation documents. `auto_load: false`. |
| 1233 | `investigation-evidence-location` | investigation | Evidence location mapping and gap management — IRC § 6104(d) disclosure requests, FOIA/Right-to-Know procedures, government portal navigation with blocked-method workarounds, gap classification system. Distilled from the BCC investigation. `auto_load: false`. |
| 1234 | `investigation-financial-tracing` | investigation | Nonprofit financial anomaly detection — Z-score analysis, 990 forensics, investment tracing, CCBHC regime-change analysis. Distilled from the BCC investigation (activate_bcc_analysis.py). Created August 1, 2026. |
| 1235 | `investigation-legal-referral` | investigation | Legal referral construction — FCA qui tam packaging, IRS fraud referral (Forms 13909, 211, 3949-A), PA Ethics Act complaints, multi-agency submission strategies, evidence anchoring patterns. Distilled from the BCC investigation. `auto_load: false`. |
| 1236 | `investigation-osint` | investigation | Open-source intelligence techniques for investigations — web scraping patterns, API discovery, blocked portal workarounds, CAPTCHA bypass documentation, OSINT toolkit. Distilled from the BCC investigation. `auto_load: false`. |
| 1237 | `investigation-people-discovery` | investigation | Board member & key person employer verification — 14-channel discovery protocol (990 Part VII, employer confirmation, negative-result documentation). Distilled from the BCC investigation (23 people, 34 data sources). Created August 1, 2026. |
| 1238 | `investigation-regulatory-crossref` | investigation | Multi-agency regulatory cross-referencing — FINRA, IRS, HUD, SAMHSA, state ethics, charitable trusts; agency-by-agency protocol (clean in one agency ≠ clean across all). Distilled from the BCC investigation (6 agencies, 5 complaint channels). Created August 1, 2026. |
| 1239 | `investigation-regulatory-licenses` | investigation | Regulatory license investigation — FINRA BrokerCheck API querying, PA PALS license verification, professional license revocation procedures (FINRA, CPA, medical). Distilled from the BCC investigation. `auto_load: false`. |
| 1240 | `azazael-catalog-reconciliation` | process | SKILLS_CATALOG.md numbering reconciliation pattern — master table as source of truth, bucket-sum verify, cascading-undercount trap (the #1221 off-by-one that propagated through +19 rows). Load before auditing or correcting catalog counts. `auto_load: false`. |
| 1241 | `investigation-channel-map` | investigation | Master channel register for investigations — which portals/APIs work, which are blocked, exact workaround for each (search-engine failures, government portal 503 recovery, CAPTCHA-gated ports, keyless JSON APIs). Distilled from the BCC investigation. Generalized from `bcc-channel-register`. `auto_load: false`. |
| 1242 | `investigation-990-data-access` | investigation | Form 990 data access patterns — ProPublica Nonprofit Explorer JSON endpoints vs the JS-rendered `/full` view (browser required), IRS bulk-XML 302/404 handling, EIN-keyed lookups. Distilled from the BCC investigation. Generalized from `bcc-propublica-990`. `auto_load: false`. |
| 1243 | `investigation-survey-enumeration` | investigation | Complete regulatory survey-portal enumeration — retrieve and classify EVERY record (detail-page URL pattern, verbatim official-field classification, keyword traps in agency phrasing, published-correction records). Distilled from the BCC DDAP investigation. Generalized from `bcc-ddap-portal-enumeration`. `auto_load: false`. |
| 1244 | `investigation-provider-registry` | investigation | Regulated-provider registry lookups — keyless API direct queries (CMS NPI), provider-identity hygiene audits (stale authorized official, address drift, taxonomy gaps), org-vs-practitioner record distinction. Distilled from the BCC investigation. Generalized from `bcc-npi-registry`. `auto_load: false`. |
| 1245 | `investigation-server-extraction` | investigation | Server-rendered website text extraction when automated fetchers fail — sitemap-first inventory with lastmods, curl + Python strip-script/style, browser fallback only when genuinely needed, post-extraction identity check. Distilled from the BCC investigation. Generalized from `bcc-website-extraction`. `auto_load: false`. |
| 1246 | `investigation-fetch-verification` | investigation | Accuracy discipline for scripted fetching — persist raw before classifying, match keywords to real phrasing (keyword traps), browser spot-check evidence, corrections register (C1–C4) so corrected claims are never repeated. Distilled from the BCC investigation. Generalized from `scripted-fetch-verification`. `auto_load: false`. |
| 1247 | `aoa-kali-arm` | architecture | AOA Kali Toolchain arm (arm_id=kali) — 39 verified Kali Linux tools over WSL mapped 1:1 to AOA capabilities (recon, web, osint, security, cracking, intercept, network, ids, forensics, ai, media), dry-run-safe WSL bridge, per-tool `azazael-bin-*` cross-reference. AOA went 8 arms/31 caps → 9 arms/71 caps (2026-09-02). Related: `aoa-artifact-cross-check` (#1250), `background-sweep-resilience` (#1251), `builder-status-discipline` (#1252). `auto_load: false`. |
| 1248 | `html-render-verification` | process | HTML render verification via headless-Chrome CDP (`verify_aoa_cdp.py`) — structural audits cannot catch JS-level defects (literal-`\n` joins, unterminated multi-line strings — both REAL INCIDENTS 2026-09-02; raw-`.then()` clipboard promises = unhandled rejections invisible to exceptionThrown/Log channels — REAL INCIDENT 2026-09-04, 10 letters / 44 rejections), so built or edited HTML must also pass a real browser render check; deterministic clipboard probe (in-page `unhandledrejection` listener + no-user-gesture clicks, `navigator.clipboard` is read-only so mocking is impossible) + canonical `.catch(legacy)` safe handler; trap catalog with byte-exact forms + fix-then-reverify loop. `auto_load: false`. |
| 1249 | `corpus-reference-integrity` | process | Phantom-reference sweep of documentation corpora (`sweep_corpus_refs.py`) — classify backticked skill/file cites vs real trees (false-positive discipline), verify phantoms with an existence PROOF, resolve by creating the skill (make-them-real two-location pattern: case-scoped original + generalized registered version) or dated doc correction. Applied to the 63-doc BCC corpus 2026-09-02 (6 phantoms found + made real; corpus since reconciled to 64 — FINAL_STATUS_REPORT inventory verified 2026-09-03). `auto_load: false`. |
| 1250 | `aoa-artifact-cross-check` | process | Four-surface artifact consistency check — live registry ↔ `AOA_AUDIT_MAP.md` §3 ↔ rebuilt diagrams (AOA_STRUCTURE/AOA_DISCLOSURE) ↔ audit JSON, comparing arm set, per-arm fields, capability NAMES, totals and tool-family breakdowns. Proven on 2026-09-02: all nine arms / 71 caps consistent across every surface (JSON name-lists match `get_capabilities()` exactly). Run after ANY rebuild or map edit. Related: `aoa-architecture` (#1223), `aoa-html-builder` (#1226), `aoa-kali-arm` (#1247), `html-render-verification` (#1248). `auto_load: false`. |
| 1251 | `background-sweep-resilience` | process | Crash-resilient long-running sweeps — per-file try/except so one slow file can't kill the run, log-to-file + resume-from-crash-point (deterministic sorted order), basename-dedup pitfalls across dirs, Windows temp-path vs bash `/tmp` gotchas, monotonic per-file progress. Proven on the 2,754-file project-wide CDP sweep (2026-09-02): a ws timeout at 2,599/2,754 was resumed from the exact crash index instead of restarting. Related: `html-render-verification` (#1248), `corpus-reference-integrity` (#1249), `aoa-kali-arm` (#1247). `auto_load: false`. |
| 1252 | `builder-status-discipline` | process | Producer-status map for multi-builder codebases — tag every generator as CANONICAL / legacy-clean / non-writing-stub with its output target, so future edits go to the right file and dead variants are never extended. Proven on the AOA builder set (build.py + build_disclosure.py canonical, gen_html.py legacy-clean, build_final.py non-writing stub) and the CODEX generator (`create_dual_pane_video.py` canonical producer of Azazael_DUAL_PANE.html). Related: `aoa-html-builder` (#1226), `azazael-codex-video`, `pre-action-gate-lite` (#1253). `auto_load: false`. |
| 1253 | `pre-action-gate-lite` | process | Fix-then-REVERIFY + static-isolation discipline before declaring a defect closed — after any HTML/JS/Python fix, re-run the rendering or execution check that caught it, then scan the wider corpus for sibling instances of the same trap (literal-`\n` signature scan, unterminated-string regex, generator-source regression check). Both 2026-09-02 real defects (literal-`\n` AOA rebuild, Azazael_DUAL_PANE unterminated string INCLUDING its generator) were proven isolation-complete this way. Related: `html-render-verification` (#1248), `aoa-html-builder` (#1226), `builder-status-discipline` (#1252). `auto_load: false`. |
| 1254 | `asof-qualifier-protocol` | process | As-of qualifier protocol for investigations — detect role/title drift (officer/board changes after a dated sour
| 1255 | `timesfm-314t` | investigation | TimesFM 3 second-opinion anomaly layer + Bai-Perron structural-break dating on the 3.14t free-threaded venv — 990-series financial analysis (proven Sep 4, 2026): venv-314t setup (cp314t torch wheel), timesfm_pilot_314t.py + bai_perron_breakpoints.py (numpy-only, Monte-Carlo finite-sample critical values), dated results (FY2018 CCBHC regime, FY2017 comp break), and the traps (statsmodels has NO structural_break module; its compiled extensions break under 3.14t)ce filing), insert a uniform dated banner (real-id rule: id attr, not a comment marker), and sweep the corpus for stale-role assertions. Covers the banner-doesn't-travel-with-pasted-text trap: send-ready letter/email/script bodies need INLINE qualifiers (`as of the FY2025 Form 990, filed May 8, 2026`) because the page banner is left behind on copy; routing/action items get re-directed to current office-holders; verify with residual-scan + structural audit + CDP render probe (#scroll-container.innerText, not body.innerText) + hash-verified archive sync. Proven 2026-09-03: 11 templates, 45+ cites qualified, 11/11 hash-MATCH. Related: `html-render-verification` (#1248), `corpus-reference-integrity` (#1249), `background-sweep-resilience` (#1251), `pre-action-gate-lite` (#1253). `auto_load: false`. |
| 1256 | `desktop-automation-safety` | process | Safe desktop GUI automation on Windows sessions where other apps fight for foreground focus — single-process execution, content-verified focus before ANY keystroke, headless-over-GUI preference, keystroke-leak incident protocol. Proven 2026-09-04. (Master row added 2026-09-05 — was registered only in its date section.) |
| 1257 | `azazael-venv-tooling-policy` | process | Dual-venv policy — 3.14t default stack, `venv-313-tools/` fallback for cp314t wheel-gap tools; verified version table + API gotchas (kuzu dict params, rustworkx PyDiGraph, splink 4.0 namespaces). Proven 2026-09-05. (Master row added 2026-09-05.) |
| 1258 | `azazael-embed-link-sna` | process | Lead-layer network analysis — chromadb embeddings vs TF-IDF to isolate embedding-only doc links, SNA hub ranking (degree + rustworkx PageRank), pyvis lead viewer, hubs→gap-ID anchoring. Proven 2026-09-05 (211 links, 386-edge graph, 10 hubs). (Master row added 2026-09-05.) |
| 1259 | `azazael-gap-index-anchoring` | process | Machine-readable gap-index maintenance — canonical JSON + rendered-table lockstep in the gaps doc (`build_gap_index.py` extract/write/anchors), semantic freshness checks that never rewrite a healthy doc, hub anchor-line verification. Proven 2026-09-05 (45 gaps, 10 hub docs × 3 anchors, 0 dangling). Related: `corpus-reference-integrity`, `html-render-verification`. |

## New Skills — Created September 2, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `aoa-architecture` | `output/aoa_atlas/AOA_AUDIT_MAP.md` · `output/aoa_atlas/AOA_EVOLUTION_CATALOG.md` (companion artifacts) | AOA umbrella architecture (8 arms · 32 capabilities). Catalog registration cross-links the Sep 2 audit+map and evolution catalog: 5-generation hash verification (23/23 repo↔Desktop, 20/20 g1↔g2↔restored), 8 arms AST-extracted, +6 runtime caps from the Desktop generation, aoa_g/aoa_source atlas graphs regenerated (193/349/19). `auto_load: true`. | ✅ Registered |
| `aoa-accurate-disclosure` | `.agents/skills/aoa-accurate-disclosure.md` | Source-code audited architecture disclosure — real 3-tier structure, DreamingModule, MetaCognitionWorm, 17 worm categories, corrected Quartet meaning. `audit_date: 2026-07-02`. | ✅ Registered |
| `aoa-disclosure-build` | `.agents/skills/aoa-disclosure-build.md` | 14-diagram whitepaper build pipeline with 12-color semantic Mermaid palette, Puppeteer scroll capture, HEVC encoding. v2.0.0, `priority: high`. | ✅ Registered |
| `aoa-html-builder` | `.agents/skills/aoa-html-builder.md` | Mermaid-based architecture disclosure HTML generator — heredoc workaround, classDef patterns, 7-diagram layout, particle JS, benchmark cards, arm capability tables. | ✅ Registered |
| `azazael-inference` | `.agents/skills/azazael-inference/SKILL.md` | Multi-provider AI inference — 11 free LLM providers, OpenAI-compatible API, NimClient, InferenceBusPublisher, provider registry. `created: 2026-06-06`. | ✅ Registered |
| `azazael-inference-integration` | `.agents/skills/azazael-inference-integration/SKILL.md` | 10-point integration strategy, P0-P2 implementations (MetaCluster LLM insights, adaptive routing, InferenceSubscriberWorm), audit findings. Parent `azazael-inference`. `created: 2026-06-06`. | ✅ Registered |
| `azazael-inference-worms` | `.agents/skills/azazael-inference-worms/SKILL.md` | InferenceWorm (provider-agnostic) + NimInferenceWorm (multi-provider). Parent `azazael-inference`. `created: 2026-06-06`. | ✅ Registered |
| `investigation-990-forensics` | `.agents/skills/investigation-990-forensics.md` | Nonprofit Form 990 forensic analysis — Schedule D/L detection, compensation inversion, z-score analysis. Distilled from the BCC investigation. `auto_load: false`. | ✅ Registered |
| `investigation-board-governance` | `.agents/skills/investigation-board-governance.md` | Board governance forensics — conflict-of-interest detection, board composition mapping, hidden network analysis, Schedule L cross-referencing. Distilled from the BCC investigation. `auto_load: false`. | ✅ Registered |
| `investigation-document-construction` | `.agents/skills/investigation-document-construction.md` | HTML evidence document construction standards — citations, cross-referencing, styling, evidence anchoring, deliverable taxonomy (60+ docs). `auto_load: false`. | ✅ Registered |
| `investigation-evidence-location` | `.agents/skills/investigation-evidence-location.md` | Evidence location + gap management — IRC § 6104(d), FOIA/Right-to-Know, blocked-portal workarounds, gap classification. `auto_load: false`. | ✅ Registered |
| `investigation-financial-tracing` | `.agents/skills/investigation-financial-tracing.md` | Nonprofit financial anomaly detection — Z-score, 990 forensics, investment tracing, CCBHC regime-change analysis. Created August 1, 2026. | ✅ Registered |
| `investigation-legal-referral` | `.agents/skills/investigation-legal-referral.md` | Legal referral construction — FCA qui tam packaging, IRS fraud referral (13909/211/3949-A), PA Ethics Act, multi-agency submission. `auto_load: false`. | ✅ Registered |
| `investigation-osint` | `.agents/skills/investigation-osint.md` | OSINT techniques — web scraping, API discovery, blocked-portal workarounds, CAPTCHA bypass documentation, OSINT toolkit. `auto_load: false`. | ✅ Registered |
| `investigation-people-discovery` | `.agents/skills/investigation-people-discovery.md` | Board member & key person employer verification — 14-channel discovery protocol. Distilled from the BCC investigation (23 people, 34 data sources). Created August 1, 2026. | ✅ Registered |
| `investigation-regulatory-crossref` | `.agents/skills/investigation-regulatory-crossref.md` | Multi-agency regulatory cross-referencing — FINRA, IRS, HUD, SAMHSA, state ethics, charitable trusts. Created August 1, 2026. | ✅ Registered |
| `investigation-regulatory-licenses` | `.agents/skills/investigation-regulatory-licenses.md` | Regulatory license investigation — FINRA BrokerCheck, PA PALS, license revocation procedures. Distilled from the BCC investigation. `auto_load: false`. | ✅ Registered |
| `investigation-channel-map` | `.agents/skills/investigation-channel-map.md` | Master channel register — which portals/APIs work, blocked, exact workaround (search-engine failures, 503 recovery, CAPTCHA-gated ports, keyless JSON APIs). Generalized from `bcc-channel-register`. `auto_load: false`. | ✅ Registered |
| `investigation-990-data-access` | `.agents/skills/investigation-990-data-access.md` | Form 990 data access — ProPublica JSON endpoints vs JS-rendered `/full`, IRS bulk-XML 302/404, EIN-keyed lookups. Generalized from `bcc-propublica-990`. `auto_load: false`. | ✅ Registered |
| `investigation-survey-enumeration` | `.agents/skills/investigation-survey-enumeration.md` | Complete survey-portal enumeration — EVERY record, verbatim official-field classification, keyword traps, published-correction records. Generalized from `bcc-ddap-portal-enumeration`. `auto_load: false`. | ✅ Registered |
| `investigation-provider-registry` | `.agents/skills/investigation-provider-registry.md` | Provider-registry lookups — keyless API (CMS NPI), hygiene audits (stale official, address drift, taxonomy gaps). Generalized from `bcc-npi-registry`. `auto_load: false`. | ✅ Registered |
| `investigation-server-extraction` | `.agents/skills/investigation-server-extraction.md` | Server-rendered extraction when fetchers fail — sitemap-first inventory, curl + strip-script/style, browser fallback, identity check. Generalized from `bcc-website-extraction`. `auto_load: false`. | ✅ Registered |
| `investigation-fetch-verification` | `.agents/skills/investigation-fetch-verification.md` | Fetch accuracy discipline — persist raw, match keywords to real phrasing, browser spot-check, corrections register (C1–C4). Generalized from `scripted-fetch-verification`. `auto_load: false`. | ✅ Registered |
| `aoa-kali-arm` | `.agents/skills/aoa-kali-arm.md` | AOA Kali Toolchain arm index — 39 verified Kali tools over WSL as 1:1 AOA capabilities, dry-run-safe bridge, azazael-bin-* cross-refs; 9 arms / 71 caps. `auto_load: false`. | ✅ Registered |
| `html-render-verification` | `.agents/skills/html-render-verification.md` | HTML render verification via CDP harness — structural audit cannot catch JS-level defects (literal-`\n` join + unterminated multi-line string REAL INCIDENTS), trap catalog, fix-then-reverify. `auto_load: false`. | ✅ Registered |
| `corpus-reference-integrity` | `.agents/skills/corpus-reference-integrity.md` | Phantom-reference sweep of doc corpora vs real trees — false-positive discipline, existence-proof verification, make-them-real two-location creation, dated corrections. `auto_load: false`. | ✅ Registered |
| `aoa-artifact-cross-check` | `.agents/skills/aoa-artifact-cross-check.md` | Four-surface artifact consistency (registry ↔ audit map ↔ diagrams ↔ audit JSON) — arm set, per-arm fields, capability NAMES, totals/families. `auto_load: false`. | ✅ Registered |
| `background-sweep-resilience` | `.agents/skills/background-sweep-resilience.md` | Crash-resilient long sweeps — per-file try/except, log + resume-from-crash-point, dedup/win-path gotchas. Proven on the 2,754-file CDP sweep. `auto_load: false`. | ✅ Registered |
| `builder-status-discipline` | `.agents/skills/builder-status-discipline.md` | Producer-status maps (canonical / legacy-clean / non-writing-stub) for multi-builder codebases. `auto_load: false`. | ✅ Registered |
| `pre-action-gate-lite` | `.agents/skills/pre-action-gate-lite.md` | Fix-then-REVERIFY + corpus isolation scan before declaring a defect closed. `auto_load: false`. | ✅ Registered |
| `azazael-catalog-reconciliation` | `skills/azazael-catalog-reconciliation.md` | Catalog numbering reconciliation pattern — master-table-as-truth, bucket-sum verification, cascading-undercount trap (encodes the 2026-09-02 1,238→1,239 / core 149→151 fix). `auto_load: false`. | ✅ Created |
| `bcc-*` family (10) — see note | intentionally NOT in this catalog | Case-scoped BCC investigation skills (`bcc-forensic-extraction`, `bcc-investigation`, `bcc-legal-framework`, `bcc-owl-framework`, `bcc-ddap-portal-enumeration`, `bcc-npi-registry`, `bcc-propublica-990`, `bcc-website-extraction`, `bcc-channel-register`, `scripted-fetch-verification`) — indexed at `BCC_Investigation/skills/INDEX.md` on the gen-2 mirror, off-project by design. Decision recorded 2026-09-02: case-specific content, no YAML frontmatter, lives only on G:. The generalized methodology distilled from the case IS registered above as `investigation-*` (#1230–#1239 and #1241–#1246). | ⚠️ EXCLUDED BY DESIGN |

## New Skills — Created September 1, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-archive-restore` | `skills/azazael-archive-restore.md` | Archive-restore provenance pattern — copy-don't-move, generation labels, byte-verify (robocopy + SHA-256 + cmp), inherit-defect documentation in provenance README, layered sanity passes (compileall → safe-import list → guarded dry-run). Encodes Session 28's restored trees (AOA gen 1, Libra_Desktop BCC superset, META Z), including the MSYS robocopy path bug, the MILESTONE.py 0x97 and cain/* os.unlink inherited defects, and the exFAT cluster-slack size trap. `auto_load: false`. | ✅ Created |

## New Skills — Created August 31, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-kali-graph-protocol` | `skills/azazael-kali-graph-protocol.md` | Established Kali → atlas graph protocol — rsync mirror, `.git` boundary sealing the home-gitignore leak, `go/` + venv exclusions, `extract` (NOT `update`) → cluster-only → tree → cosmos. Encodes 4 hours of stalled-run root causes; working state = 2,004 files scanned → 41,524 nodes in ~3 min. `auto_load: false`. | ✅ Created |

## New Skills — Created August 23, 2026

| Skill | Path | Purpose | Priority |
|-------|------|---------|----------|
| `azazael-pkg-*` (968) | `skills/azazael-pkg-*.md` | Callable skills for Kali Python 3.13.12 system packages — CLI entry points + Python API invocation patterns. Generated from `importlib.metadata` (see `skills_staging/generate_kali_pkg_skills.py`). | Merged |
| `azazael-pkg314t-*` (74) | `skills/azazael-pkg314t-*.md` | Callable skills for the Azazael Python 3.14.6 (3.14t) environment — CLI entry points + Python API invocation patterns. Generated from `importlib.metadata` (see `skills_staging/generate_kali_pkg_skills.py`). | Merged |
| `azazael-bin-*` (46) | `skills/azazael-bin-*.md` | Callable skills for binary/CLI tools (Kali binaries + OSINT + AI/ML) — canonical invocations with live version/status. Generated from `skills_staging/binary_manifest.py` + `generate_bin_skills.py`. | Merged |

---

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
| `azazael-venv-tooling-policy` | `skills/azazael-venv-tooling-policy.md` | Dual-venv policy — 3.14t default stack, `venv-313-tools/` fallback for cp314t wheel-gap tools. Verified version table (splink/kuzu/rustworkx/chromadb/graphiti), API gotchas (kuzu dict params, rustworkx PyDiGraph, splink 4.0 namespaces), and smoke-test pattern. Proven 2026-09-05. | ✅ Created |
| `azazael-embed-link-sna` | `skills/azazael-embed-link-sna.md` | Lead-layer network analysis — chromadb embeddings vs TF-IDF to isolate embedding-only doc links, SNA hub ranking (degree + rustworkx PageRank), pyvis lead viewer, and hubs→gap-ID anchoring. Proven 2026-09-05 (211 links, 386-edge graph, 10 hubs). | ✅ Created |
| `azazael-gap-index-anchoring` | `skills/azazael-gap-index-anchoring.md` | Machine-readable gap-index maintenance — canonical JSON + rendered table lockstep in the gaps doc (`build_gap_index.py`: extract/write/anchors), semantic freshness checks that never rewrite a healthy doc (byte-compare false-positive trap), hub anchor-line verification (10 hub docs × 3 anchors, 0 dangling, 2026-09-05). Related: `corpus-reference-integrity`, `html-render-verification`. | ✅ Created |

## New Skills — Future Development

Based on the May 29, 2026 session findings, these skills should be created:

| Proposed Skill | Purpose | Priority |
|---------------|---------|----------|
| `azazael-dedup` | Deduplication procedure — MD5 hash comparison, shim creation, file cleanup | High |
| `azazael-shims` | Deprecation shim pattern, UserWarning usage, testing procedure | High |
| `azazael-g-sync` | G: drive sync procedure — what to copy, when, verification | Medium |
| `azazael-separation` | Monolith separation plan — 6 layers, 27 programs, migration steps | High |

---

## Reconciliation — Measured 2026-09-16 (the summary above was stale)

Counted from disk, not from a prior session's number: the cascade undercount is
silent, so only a fresh count is trustworthy (`skill("azazael-catalog-reconciliation")`).

| Source | Count |
|---|---|
| `.agents/skills` entries (mirror) | **1,261** = 1,224 dirs with `SKILL.md` + 37 flat legacy `.md` |
| `skills/` entries (canonical) | **1,226** files = 1,225 skill files + `__init__.py` |
| Rows in the Skill Quick Reference table | **1,259** |
| Inventory Summary claim (this file) | 1,224 — **stale, undercounts its own table by 35** |

Bucket-sum for the mirror, by name prefix:

```
968 azazael-pkg-*  +  74 azazael-pkg314t-*  +  46 azazael-bin-*  +  139 azazael-* core
  +  34 non-azazael (aoa-*, investigation-*, pre-action-gate-lite, misc)
  = 1,261   matches the mirror listing exactly
```

Per the reconciliation rule the **table wins**, so the Inventory Summary should read
**1,259**, not 1,224. The residual 2-entry gap between the table (1,259) and the
mirror (1,261) is named rather than rounded away: the likely cause is the 37 flat
legacy files, some of which (`azazael-catalog-reconciliation.md`,
`pre-action-gate-lite.md`) exist only in flat form and may not all appear as rows.

**New since the Sep-14 recount:** `azazael-mesh-resilience-primitives` (2026-09-16) —
canonical `skills/azazael-mesh-resilience-primitives.md`, mirrored to
`.agents/skills/azazael-mesh-resilience-primitives/SKILL.md`. Documents the four mesh
resilience primitives (fencing tokens, the silent-failure ledger, liveness
obligations, store tombstones) and the method that produced them. The next full table
regeneration must add its row and bump the total **in the same edit** — a row added
without the count bump is exactly how the cascade starts.
