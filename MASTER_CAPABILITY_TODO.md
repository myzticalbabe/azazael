# AZAZAEL — Master Capability TODO (Consolidated from DISCLOSURE_WHITEPAPER_TODO.md)

> **3.14 RETIRED 2026-10-19** — 3.14t is no longer a runtime in this project;
> production is the 3.15t venv (`C:\Azazael\.venvs\py315t`), and the only
> sanctioned 3.14 runtime is `C:\Azazael\.venvs\py314m` (3.14.5 GIL). Capability
> rows below describe the state on their date.

> **Created:** July 9, 2026 — Synthesized from all 14 sections (A-N) of DISCLOSURE_WHITEPAPER_TODO.md
> **Scope:** Complete production action plan incorporating all disclosed capabilities
> **Priority:** P0 = Critical/Must-do, P1 = High, P2 = Medium, P3 = Nice-to-have
> **Stat:** ✅ = Done, ⬜ = Not started, ⚠️ = In progress/Blocked

---

## TABLE OF CONTENTS

1. [FOUNDATIONS — Worm Fleet & Cluster Architecture](#1-foundations--worm-fleet--cluster-architecture)
2. [CORE INFRA — Memory, Inference & Compliance](#2-core-infra--memory-inference--compliance)
3. [BUILD & DEPLOY — EXE Pipeline & Standalone Suite](#3-build--deploy--exe-pipeline--standalone-suite)
4. [DESKTOP ECOSYSTEM — 13 Projects](#4-desktop-ecosystem--13-projects)
5. [AI/ML SYSTEMS — Providers, Agents & Neural Training](#5-aiml-systems--providers-agents--neural-training)
6. [DATA & PRIVACY — Security Audit & Remediation](#6-data--privacy--security-audit--remediation)
7. [SECURITY & COMPLIANCE — Gates, Worms & Mandates](#7-security--compliance--gates-worms--mandates)
8. [CROSS-PROJECT — Sync, Bridges & Integration](#8-cross-project--sync-bridges--integration)
9. [WHITEPAPER — Video Pipeline & CAIN Rendering](#9-whitepaper--video-pipeline--cain-rendering)
10. [SIBLING PILLARS — GOSP, Vermillion, VLP, Tigger, npExtractDir](#10-sibling-pillars--gosp-vermillion-vlp-tigger-npextractdir)

---

## 1. FOUNDATIONS — Worm Fleet & Cluster Architecture

> **Source sections:** A1, A2, E4; CODEBASE_AUDIT_TODO Steps 3-7, 9

| # | Task | Priority | Status |
|---|------|----------|--------|
| 1.1 | **Worm API standardization** — Add `get_summary()`/`get_status()` to 42 worms lacking BaseWormMixin inspection API | P0 | ⬜ |
| 1.2 | Fix 44 instantiation errors (missing constructor args, import errors) across 86 failing worms | P0 | ⬜ |
| 1.3 | Runtime execution testing for top-18 passing worms with real workloads | P1 | ⬜ |
| 1.4 | WSL compatibility audit — 8 categories have ZERO passing worms on WSL | P1 | ⬜ |
| 1.5 | Register 25 unregistered worms from vermillion_lightfury, native Rust, and stale refs | P2 | ⬜ |
| 1.6 | Cross-reference worm descriptions with actual behavior | P2 | ⬜ |
| 1.7 | ClusterWORMZ v2.2.0 — disclosure review + integration tests for parallel execution | P1 | ⬜ |
| 1.8 | MetaCluster — integration tests for cross-nature orchestration (70 routes, 594 paths) | P1 | ⬜ |
| 1.9 | FreeThreadPool — work-stealing optimization, verify cpu_count auto-scale | P2 | ⬜ |
| 1.10 | CircuitBreaker — dead letter queue integration testing | P2 | ⬜ |
| 1.11 | CurativePool — 3-pool (Validation/Audit/Feedback) runtime testing with CAIN | P1 | ⬜ |
| 1.12 | Error recovery — timeout handling, partial failure, retry with exponential backoff | P1 | ⬜ |
| 1.13 | Registry validation at startup (detect missing deps, circular imports) | P2 | ⬜ |
| 1.14 | Worm dependency graph visualization via Mermaid | P3 | ⬜ |
| 1.15 | Workflow DSL for defining multi-step orchestration | P3 | ⬜ |

---

## 2. CORE INFRA — Memory, Inference & Compliance

> **Source sections:** A3, A4, A5, A6, E1-E4

| # | Task | Priority | Status |
|---|------|----------|--------|
| 2.1 | **AuditTrail** — disclosure review + Merkle proof verification | P0 | ⬜ |
| 2.2 | **LocalMemoryStore** — FTS5 query performance audit | P1 | ⬜ |
| 2.3 | **PamsRecorder v2.0** — 4-layer fallback chain validation | P1 | ⬜ |
| 2.4 | **MemoryBus v1.1.0** — persistent fallback queue testing | P1 | ⬜ |
| 2.5 | **Session Mappings (CD2)** — cross-ledger DM↔AJ correlation testing | P1 | ⬜ |
| 2.6 | **providers.py** — disclosure review of all 23 providers + failover | P0 | ⬜ |
| 2.7 | Document AI regulatory items: external APIs, prompts, models, failover, cache | P0 | ⬜ |
| 2.8 | **InferenceWorm** — provider-agnostic auto-select testing | P1 | ⬜ |
| 2.9 | **ParallelInferenceWorm** — local model benchmarking suite | P2 | ⬜ |
| 2.10 | **InferenceSubscriberWorm** — MemoryBus→LLM anomaly detection testing | P2 | ⬜ |
| 2.11 | Compliance infra disclosure review (sentinel_gate, pre_action_gate, orchestrator, scanner) | P0 | ⬜ |
| 2.12 | gate_str_replace / gate_write_file / heuristic_recorder / telemetry disclosure review | P1 | ⬜ |
| 2.13 | azazael_ctl unified CLI — validate all 4 subcommand groups + 6 commands | P1 | ⬜ |
| 2.14 | 5-environment sync pipeline — validate sync_all, sync_canonical_docs, sync_skills, auto_sync | P1 | ⬜ |
| 2.15 | Session lifecycle tools — validate session_start + check_tooling + environ_updater | P1 | ⬜ |
| 2.16 | CODEX subsystem — disclosure review of 67 total items (24 VIDEOS, 19 templates, 9 core) | P1 | ⬜ |
| 2.17 | METAWORMS (METAZ/DEPENDZ/VALIDZ) — worm analysis system testing | P2 | ⬜ |
| 2.18 | HYDRAMETA / HYDRAMETA_UV — multi-headed optimization testing | P2 | ⬜ |
| 2.19 | Centralized configuration (YAML/TOML azazael.yaml at project root) | P2 | ⬜ |
| 2.20 | Import hygiene — autoflake on all .py files, remove unused imports | P2 | ⬜ |
| 2.21 | Standardize error handling — remove bare `except:` clauses | P2 | ⬜ |

---

## 3. BUILD & DEPLOY — EXE Pipeline & Standalone Suite

> **Source section:** B (52 EXEs, Nuitka pipeline); CODEBASE_AUDIT_TODO Steps 10-11

| # | Task | Priority | Status |
|---|------|----------|--------|
| 3.1 | **Fix Nuitka CompiledFrameType.c _PyStackRef error on Python 3.14.6t** — ALL EXEs blocked | P0 | ⚠️ BLOCKED |
| 3.2 | Develop 4th Nuitka patch for CompiledFrameType.c (_PyStackRef struct API) | P0 | ⬜ |
| 3.3 | Full --help test on all 51 CLI-capable EXEs | P1 | ⬜ |
| 3.4 | Core functionality test on all 52 EXEs (requires specific inputs) | P2 | ⬜ |
| 3.5 | Create .spec files for vermillion_lightfury (7 worms), AOA (9 arms), Libra (11 modules), EveUnleashed | P1 | ⬜ |
| 3.6 | Nuitka rebuild of ALL 52 EXEs with current Python 3.14.6t | P0 | ⚠️ BLOCKED |
| 3.7 | New EXE targets: AOA_314t.exe, Libra_314t.exe, and all Desktop project standalones | P1 | ⬜ |
| 3.8 | Build output verification: run `./EXE --help` after build | P2 | ⬜ |
| 3.9 | Fix CLUSTERWORMS EXE "Worm registry not available" (CORE.* import resolution in onefile) | P1 | ⬜ |
| 3.10 | Docker container for reproducible builds | P3 | ⬜ |
| 3.11 | Scheduled cluster runs (cron / Windows Task Scheduler) | P3 | ⬜ |
| 3.12 | Pre-build validation script: check Python 3.14t, verify source, check tkinter/CORE imports | P2 | ⬜ |

---

## 4. DESKTOP ECOSYSTEM — 13 Projects

> **Source section:** C (AOA, Libra, EveUnleashed, LlamaServer, PAMS, PerfMon, AgentSelector, etc.)

| # | Task | Priority | Status |
|---|------|----------|--------|
| 4.1 | **AOA — Make fully executable**: initialize all 9 arms, verify key capabilities (P0-P2 per arm) | P0 | ⬜ |
| 4.2 | AOA Azazael arm — discover_worms, run_cluster, get_status runtime test | P0 | ⬜ |
| 4.3 | AOA Libra arm — list_templates, generate_document, calculate_fees runtime test | P0 | ⬜ |
| 4.4 | AOA CODEX arm — render_mermaid, get_status runtime test | P1 | ⬜ |
| 4.5 | AOA PAMS arm — record_event, query_memories runtime test | P1 | ⬜ |
| 4.6 | AOA EveUnleashed arm — select_model, run_inference runtime test | P1 | ⬜ |
| 4.7 | AOA — Fix EventPriority.MEDIUM crash + CLI 0-arms bug | P0 | ⬜ |
| 4.8 | AOA — Full session lifecycle integration test (INIT→DISCOVERY→...→SHUTDOWN) | P1 | ⬜ |
| 4.9 | AOA — Cross-arm event flow: PerfMon→PAMS→Azazael→CODEX→MP4 | P1 | ⬜ |
| 4.10 | AOA — CLI integration: cmd_init → cmd_arms_list → verify 9 arms | P1 | ⬜ |
| 4.11 | AOA — Nuitka .exe build for umbrella orchestrator (AOA_314t.exe) | P1 | ⬜ |
| 4.12 | AOA — disclosure rebuild pipeline: benchmark_data.json→HTML→MP4→distribute | P2 | ⬜ |
| 4.13 | **Libra** — 11 modules disclosure review + CLI testing | P1 | ⬜ |
| 4.14 | **EveUnleashed** — adversarial agent subsystem (5 files) runtime testing | P1 | ⬜ |
| 4.15 | EveUnleashed — full inference pipeline testing across all backends | P2 | ⬜ |
| 4.16 | **LlamaServer** — 4 backend validation (Jan, Rust, Intel SYCL, NPU) | P1 | ⬜ |
| 4.17 | **PAMS** — server startup + health check + benchmark automation | P1 | ⬜ |
| 4.18 | **PerformanceMonitor** — 5-service orchestration validation (Flask, Go, Rust, Tkinter, HTML) | P2 | ⬜ |
| 4.19 | **Ultimate_Agent_Selector** — implement 10 planned agent types (currently only __init__.py) | P3 | ⬜ |
| 4.20 | **WSL_CrossExplorer** — cross-environment file transfer testing | P2 | ⬜ |

---

## 5. AI/ML SYSTEMS — Providers, Agents & Neural Training

> **Source sections:** E1-E4, N

| # | Task | Priority | Status |
|---|------|----------|--------|
| 5.1 | **AI Regulatory Disclosure Package** — DPA status, data residency, model versions, usage tracking for all 13 cloud providers | P0 | ⬜ |
| 5.2 | NVIDIA NIM API key acquisition (only provider missing from 15 configured) | P1 | ⬜ |
| 5.3 | SecretRotator worm — activate credential rotation automation | P1 | ⬜ |
| 5.4 | Agent autonomy boundaries — define and document | P0 | ⬜ |
| 5.5 | Agent decision logging — validate DirectMemory agent learning loop (record_decision, record_lesson, set_goal) | P1 | ⬜ |
| 5.6 | Agent failure modes catalog | P1 | ⬜ |
| 5.7 | Human oversight mechanisms for autonomous agent actions | P0 | ⬜ |
| 5.8 | **NeuralPipeline** (766L) — 6-step ML orchestrator (GRPO/PPO) testing | P1 | ⬜ |
| 5.9 | **DreamingModule** (994L) — offline policy simulation testing | P2 | ⬜ |
| 5.10 | **MetaCognitionWorm** (849L) — self-reflection engine testing | P2 | ⬜ |
| 5.11 | **SB3 Agent** (840L) — PPO training on LocalMemoryStore data | P2 | ⬜ |
| 5.12 | **GRPO Learning** (621L) — DeepSeek-style group-relative optimization | P2 | ⬜ |
| 5.13 | **Q-Learning stack** (2,366L across 3 files) — HW-aware RL testing | P3 | ⬜ |
| 5.14 | **ADLP FusionCore** (227L) + **FusionHealer** (227L) + **TotalFusion** (371L) — cross-module fusion testing | P2 | ⬜ |
| 5.15 | **CurativePool** decision audit trail — log all ScopeValidator/NecessityJudge decisions | P1 | ⬜ |
| 5.16 | CAIN accountability reports — generate per session | P2 | ⬜ |
| 5.17 | Archetypal alignment verification for sensitive operations | P3 | ⬜ |
| 5.18 | **npExtractDir** — Intel IPEX-LLM NPU inference testing (3 GGUF models) | P2 | ⬜ |
| 5.19 | Training data provenance documentation | P1 | ⬜ |
| 5.20 | Model versioning (ModelVersioner worm activation) | P2 | ⬜ |

---

## 6. DATA & PRIVACY — Security Audit & Remediation

> **Source section:** F (F1-F9 Privacy Risk Summary)

| # | Task | Priority | Status |
|---|------|----------|--------|
| 6.1 | **API keys in plaintext** — implement encryption for ~/.env and ~/.azazael/*_config.json | P0 | ⬜ |
| 6.2 | **OPENAI_API_KEY in SCons debug** — scrub from git history (packages/azazael-core/cli.onefile-build/scons-debug.py) | P0 | ⬜ |
| 6.3 | **Username in paths** — implement path sanitization for `C:\Users\clint\...` in 1.12 GB SQLite + 63 JSONL files | P1 | ⬜ |
| 6.4 | **No encryption at rest** — recommend/implement BitLocker or SQLite encryption extension | P1 | ⬜ |
| 6.5 | **1,396 orphaned sessions** — run close_stale_sessions/session_gc; define retention policy | P1 | ⬜ |
| 6.6 | **Prompt exposure in DB** — implement automated purging of sensitive inference data | P2 | ⬜ |
| 6.7 | Data inventory — document complete: 1 shared DB, 63 audit files, 12 config files | P1 | ✅ Verified |
| 6.8 | Access controls audit — filesystem permissions review | P1 | ⬜ |
| 6.9 | Cross-border data flow documentation (13 providers, 6 jurisdictions) | P1 | ⬜ |
| 6.10 | PAMS localhost HTTP — acceptable for now; plan TLS if exposed externally | P3 | ⬜ |

---

## 7. SECURITY & COMPLIANCE — Gates, Worms & Mandates

> **Source section:** G (G1-G5)

| # | Task | Priority | Status |
|---|------|----------|--------|
| 7.1 | **FormalVerifier RULE 0J fix** — "PRE-ACTION GATE assertion required" failure | P0 | ⚠️ 1 failure |
| 7.2 | Fix 352 AST scanner findings across 93 files (299 import_inside_function, 25 unicode_emoji, 16 hardcoded paths, etc.) | P1 | ⬜ |
| 7.3 | **Security worms** — test VulnScanner, CertMonitor, FirewallAudit, PermissionScanner, RaceConditionDetector (all untested) | P1 | ⬜ |
| 7.4 | **MetasploitBridge** — Kali integration testing with checkpoint rollback | P2 | ⬜ |
| 7.5 | **NmapScanner** — WSL-dispatched scanning with VulnScanner cross-reference | P2 | ⬜ |
| 7.6 | **enforcement_harness.py** — test ComplianceError(RuntimeError) violation handler | P1 | ⬜ |
| 7.7 | **ComplianceAuditor** — standalone audit engine testing | P2 | ⬜ |
| 7.8 | **session_mappings.py (CD2)** — cross-ledger DM↔AJ correlation testing | P2 | ⬜ |
| 7.9 | **dual_ledger.py** — dual-ledger cross-validation and anomaly detection | P2 | ⬜ |
| 7.10 | **compliance_metrics.py** — scoring and threshold monitoring | P2 | ⬜ |
| 7.11 | **heuristic_recorder.py** — error pattern catalog testing | P2 | ⬜ |
| 7.12 | Mandate automation — convert 24 manual RULEs to programmatic enforcement where feasible | P3 | ⬜ |

---

## 8. CROSS-PROJECT — Sync, Bridges & Integration

> **Source section:** H (H1-H2)

| # | Task | Priority | Status |
|---|------|----------|--------|
| 8.1 | **5-environment sync pipeline** — disclosure review + validation (sync_all, sync_canonical_docs, sync_skills, auto_sync) | P1 | ⬜ |
| 8.2 | Cross-environment data flow documentation (Windows↔WSL↔G:↔Desktop↔Kali) | P1 | ⬜ |
| 8.3 | **Tigger bridge** — Rust pyo3 extension testing (get_worm_count, find_worm, etc.) | P2 | ⬜ |
| 8.4 | Tigger Go cross-pillar sync — Phase 2 implementation | P3 | ⬜ |
| 8.5 | **Vermillion↔Kali bridge** — SharedDirManager cross-environment testing | P2 | ⬜ |
| 8.6 | Vermillion CI pipeline — pytest.ini + regression_guard.py integration | P2 | ⬜ |
| 8.7 | **GOSP bridge** — 7-tier semantic pipeline + 9 CLI commands testing | P3 | ⬜ |
| 8.8 | **WSL2 projects** — disclosure review of all 9 projects (azazael mirror, llama.cpp, open-interpreter, models, workspace, scripts, go, intel) | P1 | ⬜ |
| 8.9 | **openmono.ai** — locate or recreate .NET 10.0 AI platform on WSL (currently MISSING) | P3 | ⬜ |
| 8.10 | WSL2 model registry — update model inventory (Qwen3-VL, Gemma 4, Eve-V2, new models) | P2 | ⬜ |

---

## 9. WHITEPAPER — Video Pipeline & CAIN Rendering

> **Source sections:** A7, I

| # | Task | Priority | Status |
|---|------|----------|--------|
| 9.1 | **CODEX directory** — disclosure review of 67 total items | P1 | ⬜ |
| 9.2 | VIDEOS/ scripts — validate create_video, generate_matrix_video, compress_video | P1 | ⬜ |
| 9.3 | CAPABILITIES/ templates — audit 19 HTML templates | P2 | ⬜ |
| 9.4 | **CAIN framework** — 75-panel psychoanalysis disclosure review | P1 | ⬜ |
| 9.5 | CAIN video pipeline — Puppeteer capture validation + HEVC 1080p encoding | P1 | ⬜ |
| 9.6 | Template system — audit 31+ HTML templates across 5 visualization formats | P2 | ⬜ |
| 9.7 | BIBL terminology index builder + HORUS ML grouping monitor disclosure review | P3 | ⬜ |
| 9.8 | DISCLOSURE_WHITEPAPER_TODO.md → MP4 rendering via capture_disclosure.js | P2 | ⬜ |
| 9.9 | Whitepaper production pipeline documentation (MD→HTML→Puppeteer→MP4) | P2 | ⬜ |

---

## 10. SIBLING PILLARS — GOSP, Vermillion, VLP, Tigger, npExtractDir

> **Source sections:** J, K, L, M, N

| # | Task | Priority | Status |
|---|------|----------|--------|
| 10.1 | **GOSP** — Gossamer Oxford Semantical Parser disclosure review + 7-tier pipeline testing | P3 | ⬜ |
| 10.2 | GOSP Rust core — 338-line semantic parser benchmarking | P3 | ⬜ |
| 10.3 | **Vermillion LightFury** — disclosure review + Kali integration testing | P2 | ⬜ |
| 10.4 | Vermillion — 332/332 test suite validation + regression_guard.py | P2 | ⬜ |
| 10.5 | **VLP** — Verifiable Lie Protocol disclosure review + 15-layer verification testing | P2 | ⬜ |
| 10.6 | **Tigger** — Native performance engine 1,000-46,700x benchmarking | P2 | ⬜ |
| 10.7 | Tigger Rust pyo3 extension — compile-time manifest embedding validation | P2 | ⬜ |
| 10.8 | **npExtractDir** — IPEX-LLM Intel NPU with 3 GGUF models (Lunar Lake/Arrow Lake/Meteor Lake) testing | P2 | ⬜ |

---

## 📊 PRIORITY SUMMARY

| Priority | Count | Key Items |
|----------|-------|-----------|
| **P0 (Critical)** | 12 | Worm API standardization, Nuitka fix, AOA fully executable, AI regulatory disclosure, Agent boundaries, API key encryption, OPENAI_API_KEY scrub, FormalVerifier fix, Memory/Inference/Compliance disclosure reviews |
| **P1 (High)** | 42 | Cluster architecture testing, CODEX disclosure, EXE testing, Desktop project validation, Sync pipeline, Security worm testing, CAIN pipeline, Data privacy remediation |
| **P2 (Medium)** | 33 | Performance optimization, Q-learning stack, Cross-pillar bridges, npExtractDir, VLP, Tigger benchmarking, Template auditing |
| **P3 (Nice-to-have)** | 11 | Workflow DSL, Docker builds, GOSP 7-tier, openmono.ai recovery, Mandate automation |

**Total items:** 98

---

## 📋 BLOCKED ITEMS

| # | Item | Blocker | Workaround |
|---|------|---------|------------|
| 3.1 | Nuitka rebuild all 52 EXEs | CompiledFrameType.c _PyStackRef error on Python 3.14.6t | Develop 4th Nuitka patch |
| 3.2 | New EXE targets (AOA, Libra, EveUnleashed) | Same Nuitka blocker | Same as above |

---

## 📁 Related Documents

- `azazael/DISCLOSURE_WHITEPAPER_TODO.md` — Source: Full capability catalog (14 sections, 146K chars)
- `azazael/CODEBASE_AUDIT_TODO.md` — Companion: Architecture audit + 12-step production plan
- `azazael/LESSONS_MASTER.md` — 57 lessons across 12 domains
- `azazael/ERROR_LOG.md` — 54+ recorded errors with root causes
- `azazael/PRODUCTION_TODO.md` — (Archived) Original production gaps
- `disclosure_render.html` — HTML rendering of disclosure whitepaper
- `build_disclosure_html.py` — MD→HTML converter script
- `capture_disclosure.js` — Puppeteer MP4 video renderer
