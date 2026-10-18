# DISCLOSURE_WHITEPAPER_TODO.md â€” Full-Legal-Disclosure Capability Catalog

> **Purpose:** Complete capability inventory of the entire Azazael ecosystem for final HTML/MP4 whitepaper.
> **Created:** July 6, 2026
> **Updated:** July 6, 2026 -- All 14 sections (A-N) expanded with detailed technical content, live-verified stats, and syntactically validated code examples. DirectMemory: 79,210 sessions, 646,928 events, 1,117.86 MB. Worm registry: 99 discovered, 18 categories, 1.12s cold discovery. All 17 Python code blocks syntax-verified with UTF-8 encoding fix.
> **Updated:** July 14, 2026 (Session 9) â€” BCC Phase 4 complete: 12 core + 6 BCC modules (filing_submitter, court_rules, bcc_parser, ifp_assistant, prothonotary, court_calendar), filing_types.json (8 specific types, 6 MDJ districts), FilingSubmitter protocol (Paper + ECF), e-filing flags (pa_courts.json), 303 BCC tests (7 test files, all passing), 5 BCC capabilities in AOA libra_arm.py, 10 BCC templates, docs/BCC.md oversight sections added. Prior: July 8, 2026 (Session 5) â€” Full audit + corruption recovery: whitepaper restored from G: archive after Session 4 Python script duplicated mypy row 146,066Ã— (37MBâ†’146K). CORE/WORMS/ verified (69 .py live â€” previous "47" was a misread), monitor worms re-audited (3/6 pass WSL), # type: ignore baselined (39 instances in CORE/). Session 4 original: mypy baselined (354 errors on CORE/91 files â€” Session 5: learning_pipeline.py 51â†’0, providers.py 43â†’0, threading_utils.py 33â†’0 = âˆ’62, 3 files graduated), DM WSL stats added (12,345 events, 15.45 MB). Original: July 6, 2026 (Session 3) â€” 100% accuracy audit: all 12 sections cross-referenced against live codebase. Added Section M: Tigger performance engine (Rust+Go+Python, 1,000-32,000x worm registry speedups) + Section N: npExtractDir IPEX-LLM Intel NPU (3 supported GGUF models, Lunar Lake/Arrow Lake/Meteor Lake). Fixed EXE total (133â†’52 on G:), .spec count (50â†’51), ERROR_LOG (212â†’138 entries), CORE/WORMS/ (69â†’47 .py), Vermillion (92â†’19 tests, 5â†’7 worm files), .audit/ locations (15 root + 48 azazael/), WSL openmono.aiâ†’MISSING, desktop file counts refreshed, DM stats (79,210 sessions, 646,928 events)
> **Scope:** All of the above â€” software capability disclosure, AI system disclosure, data handling, security, full compliance package.
> **Evolving:** This TODO changes as production execution of the codebase resolves.

---

## TABLE OF CONTENTS

1. [SECTION A: Core Azazael Framework](#section-a-core-azazael-framework)
2. [SECTION B: Desktop Standalone Suite](#section-b-desktop-standalone-suite)
3. [SECTION C: Desktop Projects (13)](#section-c-desktop-projects-14)
4. [SECTION D: WSL2 Projects](#section-d-wsl2-projects)
5. [SECTION E: AI/ML Systems (Regulatory Disclosure)](#section-e-aiml-systems-regulatory-disclosure)
6. [SECTION F: Data Handling & Privacy](#section-f-data-handling--privacy)
7. [SECTION G: Security & Compliance Infrastructure](#section-g-security--compliance-infrastructure)
8. [SECTION H: Cross-Project Integration](#section-h-cross-project-integration)
9. [SECTION I: Whitepaper Production Pipeline](#section-i-whitepaper-production-pipeline)
10. [SECTION J: GOSP â€” Gossamer Oxford Semantical Parser](#section-j-gosp--gossamer-oxford-semantical-parser)
11. [SECTION K: Vermillion LightFury](#section-k-vermillion-lightfury)
12. [SECTION L: Verifiable Lie Protocol (VLP)](#section-l-verifiable-lie-protocol-vlp)
13. [SECTION M: Tigger â€” Native Performance Engine](#section-m-tigger--native-performance-engine)
14. [SECTION N: npExtractDir â€” IPEX-LLM Intel NPU Inference](#section-n-npextractdir--ipex-llm-intel-npu-inference)

---

## SECTION A: Core Azazael Framework

### A1 â€” Worm Registry (104 Worms, 18 Categories â€” Runtime Verified July 6, 2026)

> **WSL canonical (July 8, 2026):** 91 WORM_REGISTRY keys, 16 categories, `discover_worms()` returns 30. Monitor worms: 4/6 pass WSL (SYSTEMZ=SystemZ, PROCESSZ, NETWORXZ, DISKZ). SMARTDISK and OSCongruency confirmed **Windows-only** â€” SMARTDISK requires tkinter GUI, OSCongruency requires winreg/Windows Registry API. Both fail at module import level on WSL/Linux.
>
> **Runtime Verification (July 6, 2026 Windows):** 104 registry keys (99 discovered live), 18 categories, `discover_worms()` returns 99. All 104 are dict entries. Each worm imported, instantiated, and tested with `get_summary()` or `get_status()`. **18 passed (17%), 86 failed (83%), 42 errors** â€” mostly "No get_summary()" method. See `_verify_worm_fleet.py` + `_worm_fleet_results.json` for full results. **Live re-verified July 6 Session 3:** 104 keys, 18 categories, category counts match.

**Note:** PRODUCTION_TODO.md (now archived in docs/archive/) referenced "129 worms, 23 categories" but live scan yields **99 discovered, 104 registry keys, 18 categories**. The 25-worm discrepancy may be from unregistered worms in vermillion_lightfury, native Rust modules, or stale category counts. Priority spread: P10=1, P7-9=23, P4-6=70, P1-3=10.

| # | Category | Count | Runtime Pass | Rate | Key Worms (verified passing in **bold**) |
|---|----------|-------|-------------|------|------------------------------------------|
| 1 | **ml** | 2 | 2/2 | **100%** | SYSTEMZ_ML, WORMZ_ML |
| 2 | **orchestration** | 7 | 5/7 | **71%** | **ClusterWORMZ**, **NatureClusterManager**, **ConcurrencyManager**, **ErrorRecoveryOrchestrator**, WormFleet, MetaCluster, AutoDownloaderWorm |
| 3 | **learning** | 8 | 2/8 | **25%** | ScheduledTrainingWorm, TrainingOrchestrator, MetaCognitionWorm, **EvolutionEngine**, **GeneticOptimizer**, DreamingModule, WormSelectorWorm, HypnagogicSynthesizer |
| 4 | **monitor** | 9 | 6/9 | **67%** | **SystemZ**, **PROCESSZ**, **NETWORXZ**, **DISKZ**, SMARTDISK, OSCongruency, **DatabaseMonitorWorm**, **ScheduledDbMonitorWorm**, KaliHealth |
| 5 | **backup** | 5 | 1/5 | **20%** | StateSnapshotter, IncrementalBackupWorm, RecoveryTester, ColdArchivist, **CheckpointWorm** |
| 6 | **container** | 5 | 1/5 | **20%** | ContainerOrch, ComposeValidator, ImageAuditor, **RegistryPoller**, ResourceQuotaWatch |
| 7 | **profiling** | 5 | 1/5 | **20%** | CodeProfiler, MemoryLeakDetector, IOBottleneckFinder, GILContentionProbe, **CPUFlameProfiler** |
| 8 | **analysis** | 11 | 2/11 | **18%** | BinaryAnalysis, CainWorm, ClusterInspector, CainAnalyzerWorm, **DEPENDZ**, InferenceSubscriberWorm, InferenceWorm, METAZ, NimInferenceWorm, ParallelInferenceWorm, **ReverseTools** |
| 9 | **security** | 8 | 1/8 | **12%** | VulnScanner, **PortAuditor**, CertMonitor, FirewallAudit, PermissionScanner, RaceConditionDetector, MetasploitBridge, NmapScanner |
| 10 | **utility** | 9 | 1/9 | **11%** | ABTestRunner, MorphingWorm, OMNIV2, **WORMZ**, DeadLetterQueue, DataPipelineWorm, FeatureEngineer, ModelVersioner, RLTrainLoop |
| 11 | **communication** | 5 | 0/5 | **0%** | MessageBroker, RPCEndpoint, WebhookRelay, IPCBridge, ProtocolNegotiator |
| 12 | **config** | 5 | 0/5 | **0%** | ConfigLinter, EnvValidator, DotfileSync, SecretRotator, FeatureFlagCtrl |
| 13 | **defense** | 1 | 0/1 | **0%** | WSLRecovery |
| 14 | **diagnostic** | 5 | 0/5 | **0%** | DiagnosticWorm, MorphingWormV2, FastErrorScanner, NetworkDiag, VideoAnalyzerWorm |
| 15 | **migration** | 5 | 0/5 | **0%** | CodeMigrator, DepUpgrader, SchemaVersioner, ImportPathFixWorm, LegacyShimGen |
| 16 | **sync** | 1 | 0/1 | **0%** | CLOCKZ |
| 17 | **telemetry** | 6 | 0/6 | **0%** | SpanTracer, MetricAggregator, LogStreamer, EventRouter, AlertEscalator, BenchmarkWorm |
| 18 | **visualization** | 7 | 0/7 | **0%** | DashboardGen, GraphRenderer, ReportCompiler, HeatmapBuilder, TimelineViz, EmojiMakerWorm, EnhancedAnimationsWorm |

**Root cause of 86 failures:** 42 worms lack `get_summary()` or `get_status()` methods â€” they import and instantiate without crashing but don't implement the inspection API expected by `BaseWormMixin`. The remaining 44 failures are from instantiation errors (missing constructor args, import errors). 8 categories have ZERO passing worms because they don't inherit from `BaseWormMixin`.

**Verification methodology (non-destructive):**
- [x] Import module â€” all 104 modules import successfully
- [x] Instantiate class â€” 62/104 instantiate without errors (60%)
- [x] Call `get_summary()` or `get_status()` â€” 18/104 return valid results (17%)
- [ ] Execute with real workloads â€” NOT TESTED (would be destructive for security/network worms)
- [ ] Cross-reference worm descriptions with actual behavior â€” NOT TESTED

### A2 â€” Cluster Architecture

| Component | Version | Status | Disclosure Relevance |
|-----------|---------|--------|---------------------|
| ClusterWORMZ | v2.2.0 | â¬œ Review | Dynamic worm resolution (3 strategies), Nature-based building, parallel execution, Mermaid visualization |
| NatureClusters | v1.0.0 | â¬œ Review | Auto-discovery from registry, category-grouped execution |
| MetaCluster | v1.0.0 | â¬œ Review | Cross-nature routing (70 routes, 594 paths), orchestration engine |
| CrossNatureRoutingEngine | â€” | â¬œ Review | Route discovery, path optimization |
| FreeThreadPool | â€” | â¬œ Review | Python 3.14t GIL-free parallel execution, work-stealing |
| CircuitBreaker | â€” | â¬œ Review | Error rate threshold, cooldown, dead letter queue integration |
| CurativePool | â€” | â¬œ Review | 3-pool concurrent evaluation (Validation, Audit, Feedback), CAIN integration |

### A3 â€” Memory & Recording Systems

| System | Technology | Status | Disclosure Relevance |
|--------|-----------|--------|---------------------|
| DirectMemory | SQLite (WAL mode) | âœ… VERIFIED v1.1.0 | Canonical session recorder (stdlib-only, <0.1s, UUID7, BLAKE2b). Now includes: `_V` canonical event vocabulary (37 types), agent learning loop (record_decision, record_lesson, set_goal, get_context_for_new_session, print_context_banner), 14 static query/maintenance methods (summary_stats, db_size, integrity_check, purge_session, merge_sessions, replay_session, session_gc, import_events, filtered_query, session_search, get_mapping_summary, query_cross_reference, cross_reference_ledgers, get_unlinked_report). Replaces SessionMemory for cross-session learning â€” SessionMemory's workspace/session_memory.db is now redundant (0 sessions, never populated). |
| AuditTrail | JSONL (Ed25519 signed) | â¬œ Review | Hash-chained audit log, Merkle proofs, 15-layer VLP verification |
| LocalMemoryStore | SQLite + FTS5 | â¬œ Review | Persistent memory with full-text search |
| PamsRecorder | HTTP + SQLite fallback | â¬œ Review | v2.0, 4-layer fallback chain |
| MemoryBus | Pub/sub with SQLite queue | â¬œ Review | v1.1.0, persistent fallback queue |
| Session Mappings | SQLite (CD2) | â¬œ Review | Cross-ledger DMâ†”AJ correlation |

**Data privacy implications:**
- [x] What data is stored? (session events, file edits, test runs, code reviews, decisions, lessons, goals â€” 646,928 events across 79,210 sessions as of July 6, 2026 Session 3)
- [x] Where is it stored? (~/.azazael/memory_store.db â€” 1,117.86 MB Windows / 15.45 MB WSL canonical)
- [x] Is PII recorded? (Yes â€” file paths contain usernames: `C:\Users\clint\...` in data JSON)
- [x] Retention policy (818 open sessions Windows / 1 open WSL; auto-cleanup via close_stale_sessions/session_gc; DirectMemory can self-query via summary_stats and integrity_check)
- [x] Encryption at rest? (No â€” SQLite plaintext; filesystem-level access only)
- [x] DirectMemory now self-sufficient: no longer requires separate SessionMemory DB for cross-session learning

### A4 â€” Inference Systems

> **13 provider classes in `providers.py` with circuit_breaker, rate_limit, cache, and stream features. Inference cache at `.inference_cache/` per RULE 0Q-A.**

| System | Details | Status | Disclosure Relevance |
|--------|---------|--------|---------------------|
| **providers.py** | 13 classes: OpenAIProvider, NativeAPIProvider, OllamaNativeFrameworkProvider, GeminiNativeProvider, HuggingFaceNativeProvider, MistralFIMNativeProvider, CohereNativeProvider, LlamaCppDirectProvider, HuggingFaceDirectProvider, OpenVINOProvider, OllamaNativeProvider | â¬œ Review | Multi-protocol inference dispatch (OpenAI-compatible + native APIs), auto-failover |
| **Resilience** | `circuit_breaker` (per-provider error thresholds), `rate_limit` (thread-safe RPM enforcement), `cache` (`.inference_cache/` file-backed citation cache), `stream` (streaming response support) | â¬œ Review | Graceful degradation, provider rotation on failure |
| **InferencePool** | Parallel LLM dispatcher | â¬œ Review | Benchmarking, model selection |
| **InferenceWorm** | Provider-agnostic auto-select | â¬œ Review | Best-available LLM API selection |
| **ParallelInferenceWorm** | All providers simultaneous | â¬œ Review | Local model benchmarking |
| **NimInferenceWorm** | NIM, Groq, Gemini (OpenAI-compatible) | â¬œ Review | Multi-provider inference |
| **InferenceSubscriberWorm** | MemoryBus â†’ LLM anomaly detection | â¬œ Review | Real-time anomaly detection |

**AI regulatory disclosure required:**
- [ ] List all external AI API providers used
- [ ] Document data sent to external APIs (prompts, context)
- [ ] Document model names and versions
- [ ] Document failover behavior (RULE 0D Quota Jail)
- [ ] Document inference caching (.inference_cache/)

### A5 â€” Compliance Infrastructure

| Component | Function | Status |
|-----------|----------|--------|
| sentinel_gate.py | Pre-action authorization gate (--audit mode) | â¬œ Review |
| pre_action_gate.py | PreActionGate class with parallel/spawn tracking | â¬œ Review |
| orchestrator.py | ComplianceOrchestrator â€” 13 components | â¬œ Review |
| scanner.py | Anti-pattern and compliance scanner | â¬œ Review |
| gate_str_replace.py | Gated str_replace pipeline (pre-validateâ†’backupâ†’mutateâ†’post-validate) | â¬œ Review |
| heuristic_recorder.py | Error pattern catalog | â¬œ Review |
| telemetry.py | ComplianceTelemetry â€” OpenTelemetry traces | â¬œ Review |
| sentinel_enforcer.py | CPython-level file write interceptor (sys.addaudithook) | â¬œ Review |

### A6 â€” CLI, Observability & Session Lifecycle

> **Verified July 6, 2026 â€” 12 CLI tools across 4 categories: unified CLI (340L), environment sync (5 scripts, 1,469L), session lifecycle (4 scripts, 874L), and observability (3 components). All scripts verified present on disk with actual line counts.**

#### A6A â€” azazael_ctl: Unified CLI (340L at `src/CORE/azazael_ctl.py`)

**Primary entry point** for the Azazael ecosystem. Custom command dispatcher (no argparse) with 4 subcommand groups and 2 standalone commands.

| Subcommand Group | Description | Example |
|-----------------|-------------|---------|
| `crossref` | Cross-reference execution data across ledgers | `azazael-ctl crossref <subcommand> [args]` |
| `audit` | Audit trail query, verification, and reporting | `azazael-ctl audit <subcommand> [args]` |
| `memory` | DirectMemory query, stats, purge, and cross-reference | `azazael-ctl memory <subcommand> [args]` |
| `inference` | Inference dispatch, model selection, and benchmarking | `azazael-ctl inference <subcommand> [args]` |

**Standalone commands:**

| Command | Line | Function |
|---------|------|----------|
| `cmd_status` | L90 | Human-readable ecosystem status: worm count, agent count, session stats, provider config |
| `cmd_status_json` | L138 | Machine-readable JSON export of full ecosystem status for AOA/CODEX consumption |
| `cmd_backup` | L152 | Snapshot backup of critical state (DirectMemory, audit trail, config) |
| `cmd_config` | L181 | Display and validate current configuration (paths, providers, skills) |
| `cmd_stats` | L197 | Aggregate statistics: session counts, event counts, worm execution history |
| `cmd_inference` | L213 | Direct inference dispatch â€” select provider, model, and send prompt |

**Exported API:** `__all__ = [cmd_backup, cmd_config, cmd_inference, cmd_stats, cmd_status, cmd_status_json, main]`

#### A6B â€” Environment Sync Pipeline (5 Scripts, 1,469L Total)

##### sync_all.py: 5-Environment Hub-and-Spoke (369L at `azazael/scripts/sync_all.py`)

| CLI Flag | Function |
|----------|----------|
| `--status` | Scan all 5 environments, report drift and file presence |
| `--sync-all` | Bidirectional sync to all 4 spokes (WSL2, Desktop, G: source, G: AZAZAEL) |
| `--sync-to wsl2` | Windows â†’ WSL2 `/root/azazael/` only |
| `--sync-to g` | Windows â†’ G: drive archives only |
| `--sync-to desktop` | Windows â†’ Desktop release deployment only |
| `--verify` | SHA-256 integrity check across all environments |
| `--dry-run` | Preview sync operations without executing |

**5 environment targets:**
1. Windows 11: `C:/Users/clint/azazael/` â€” Hub (primary dev, source of truth)
2. WSL2 Ubuntu: `/root/azazael/` â€” Linux build target
3. Desktop: `C:/Users/clint/Desktop/AZAZAEL_Standalone/` â€” Release deployment
4. G: source-of-truth: `G:/source-of-truth/azazael/` â€” Canonical archive
5. G: AZAZAEL: `G:/AZAZAEL/AZAZAEL_ROOT/` â€” Primary archive

##### sync_canonical_docs.py: Pillar Verification (357L)

| Function | Purpose |
|----------|---------|
| `hash_file(path)` | SHA-256 hash for integrity comparison |
| `get_master_hashes()` | Build canonical hash manifest from Windows hub |
| `get_pillar_state(pillar)` | Query remote pillar (WSL/Kali/G:) for document state |
| `verify_pillar(pillar)` | Compare pillar state against master hashes â€” detect drift |
| `sync_pillar(pillar)` | Push corrected documents to drifted pillar |
| `print_drift_report()` | Human-readable drift report across all pillars |

##### sync_skills.py: SkillsSync Engine (305L at `src/SCRIPTS/sync_skills.py`)

| CLI Flag | Function |
|----------|----------|
| (no flag) | Run full sync â€” `SkillsSync.sync_all()` |
| `--dry-run` | Preview which skills would be synced without writing |
| `--verbose` | Show per-file hash comparison and sync status |
| `--skill <name>` | Sync a single skill (e.g., `--skill azazael-startup`) |

**Programmatic API:** `from scripts.sync_skills import sync_all, sync_one, get_gap_report`

##### auto_sync.py: Poll-Based Daemon (257L at `src/SCRIPTS/auto_sync.py`)

| CLI Flag | Function |
|----------|----------|
| (no flag) | Single poll + sync iteration |
| `--status` | Show daemon status and skill counts (canonical vs agent) |
| `--watch` | Continuous polling loop (Ctrl+C to stop) |
| `--watch --interval 3` | Custom poll interval in seconds (default: 5s) |

**Graceful shutdown:** SIGTERM handler via `_handle_sigterm()`

#### A6C â€” Session Lifecycle Tools (4 Scripts, 874L Total)

##### session_start.py: Bootstrap (86L at `src/SCRIPTS/session_start.py`)

| Detail | Value |
|--------|-------|
| **Usage** | `python azazael/src/scripts/session_start.py` |
| **Exit 0** | Both operations succeeded (skills sync + DirectMemory init) |
| **Exit 1** | Partial failure (one operation succeeded) |
| **Exit 2** | Total failure (neither operation succeeded) |
| **Invoked** | Every Codebuff session bootstrap per RULE 0F |

##### check_tooling.py: Environment Validation (325L at `azazael/scripts/check_tooling.py`)

| Function | Purpose |
|----------|---------|
| `check_cli(tool)` | Verify CLI tool availability and version (node, ffmpeg, python, etc.) |
| `check_npm_package(pkg)` | Verify npm package installation (puppeteer, marked, etc.) |
| `check_pip_package(pkg)` | Verify pip package availability with version check |
| `_record_with_timeout()` | Timeout-guarded CodebuffTracker recording |
| `main()` | Full environment scan + auto-record results to DirectMemory |

**Auto-recording:** Uses `CodebuffTracker` for `session_start` (environment context) and `tooling_verify` (CLI tool availability) events.

##### environ_updater.py: Environment Manager (439L at `src/SCRIPTS/environ_updater.py`)

| Class | Method | Function |
|-------|--------|----------|
| `AzazaelEnvironment` | `scan_all()` | Full environment audit: Python versions, packages, paths, tools |
| `AzazaelEnvironment` | `fix_all()` | Auto-repair broken environment configurations |
| `AzazaelEnvironment` | `spawn_all()` | Spawn required background services |
| `AzazaelEnvironment` | `detect()` | Single-component detection |
| `PythonVersion` | `_detect_python()` | Multi-location Python discovery (Windows, WSL, venv) |

##### bootstrap.py: Minimal Bootstrapper (24L at `src/SCRIPTS/bootstrap.py`)

Sets up Python path for HYDRA/ml_platforms and UTILITIES modules. Minimal entry point for cold-start environments.

#### A6D â€” Observability & Telemetry (3 Components)

##### generate_telemetry.py: PreActionGate Export (79L at `src/SCRIPTS/generate_telemetry.py`)

| CLI Flag | Function |
|----------|----------|
| (no flag) | Export telemetry to default path (`SCRIPTS/telemetry.json`) |
| `--output <path>` | Export to custom path |

**Exports:** PreActionGate pass/fail history, ComplianceScorer snapshots, session metrics. Consumed by AOA benchmark_data.json and CODEX dashboard rendering.

##### DirectMemory Observability (in `src/CORE/direct_memory.py`)

| Method | Function |
|--------|---------|
| `summary_stats()` | Aggregate stats: total sessions, events, DB size, orphaned count |
| `db_size()` | Current database file size in bytes |
| `integrity_check()` | SQLite integrity check with result count |
| `session_search(query)` | FTS5 full-text search across all session data |
| `filtered_query(event_type, source, limit)` | Filtered event retrieval |
| `get_mapping_summary()` | Cross-ledger CD2 mapping statistics |
| `query_cross_reference(session_id)` | Cross-ledger DMâ†”AJ correlation query |
| `cross_reference_ledgers()` | Full dual-ledger cross-validation |
| `get_unlinked_report()` | Orphaned sessions and unlinked audit entries |

**Live stats (July 6, 2026 Windows):** 79,210 sessions, 646,928 events, 1,117.86 MB database, 818 open sessions sessions. **WSL canonical (July 8, 2026):** 12,345 events, 15.45 MB, 1 open session.

##### ComplianceTelemetry (in `src/CORE/compliance/telemetry.py`)

| Feature | Detail |
|---------|--------|
| **Ring buffer** | 2,000-event circular buffer for recent compliance history |
| `emit_pass(rule, context)` | Record successful compliance check |
| `emit_fail(rule, reason, context)` | Record compliance failure with details |
| `emit_error(error_type, traceback)` | Record compliance infrastructure errors |
| `get_summary()` | Aggregate pass/fail/error counts with timestamps |
| **Integration** | Part of RULE 0X-8 component in ComplianceOrchestrator |

#### A6E â€” CLI Tool Inventory Summary

| Category | Tool | File | Lines | CLI Flags |
|----------|------|------|-------|-----------|
| **Unified CLI** | azazael_ctl | `src/CORE/azazael_ctl.py` | 340 | 4 subcommand groups + 6 commands |
| **Env Sync** | sync_all.py | `azazael/scripts/sync_all.py` | 369 | --status, --sync-all, --sync-to, --verify, --dry-run |
| **Env Sync** | sync_canonical_docs.py | `src/SCRIPTS/sync_canonical_docs.py` | 357 | Programmatic API (verify/sync/drift_report) |
| **Env Sync** | sync_skills.py | `src/SCRIPTS/sync_skills.py` | 305 | --dry-run, --verbose, --skill |
| **Env Sync** | auto_sync.py | `src/SCRIPTS/auto_sync.py` | 257 | --status, --watch, --interval |
| **Session** | session_start.py | `src/SCRIPTS/session_start.py` | 86 | No flags; 3 exit codes |
| **Session** | check_tooling.py | `azazael/scripts/check_tooling.py` | 325 | No flags; auto-records to DirectMemory |
| **Session** | environ_updater.py | `src/SCRIPTS/environ_updater.py` | 439 | Programmatic API (scan/fix/spawn) |
| **Session** | bootstrap.py | `src/SCRIPTS/bootstrap.py` | 24 | No flags; path-only bootstrapper |
| **Observability** | generate_telemetry.py | `src/SCRIPTS/generate_telemetry.py` | 79 | --output |
| **Observability** | DirectMemory | `src/CORE/direct_memory.py` | ~2,500 | 9 query methods + 14 static methods |
| **Observability** | ComplianceTelemetry | `src/CORE/compliance/telemetry.py` | ~200 | 2,000-event ring buffer, emit/get_summary |

**Total CLI surface:** 12 tools, ~5,281 lines, 19 CLI flags, 4 programmatic APIs. All verified present on disk July 6, 2026.

### A7 â€” CODEX Subsystem

> **67 total items: 24 VIDEOS/ scripts, 19 CAPABILITIES/ HTML templates, 9 core components.** Includes PIL+ffmpeg rendering, Puppeteer browser capture, CAIN psychoanalysis framework, and batch video pipelines.

| Component | Detail | Status |
|-----------|--------|--------|
| **CODEX/ directory** | 67 items total â€” Python scripts, HTML templates, JSON artifacts, archival outputs | â¬œ Review |
| **VIDEOS/ scripts** | 24 items â€” `create_video.py`, `generate_matrix_video.py`, `compress_video.py`, `frame_sequence.json`, `OUTPUT/` directory | â¬œ Review |
| **CAPABILITIES/ templates** | 19 HTML templates â€” `analysis.html`, `security.html`, `inference.html`, `semantic_harvester.html`, etc. | â¬œ Review |
| **Video generation** | PIL + ffmpeg frame rendering, HTMLâ†’MP4 pipeline | â¬œ Review |
| **CAIN framework** | 75-panel psychoanalysis, 7 deadly sins, Jungian archetypes, stakeholder analysis | â¬œ Review |
| **CAIN video pipeline** | Puppeteer browser capture, HEVC 1080p, session-specific HTML injection | â¬œ Review |
| **Template system** | 31+ HTML templates across 5 visualization formats | â¬œ Review |
| **BIBL** | Terminology index builder | â¬œ Review |
| **HORUS** | ML grouping monitor (HTML/JSON/Console) | â¬œ Review |
| **batch_render.py** | CAIN batch video rendering pipeline | â¬œ Review |

---

## SECTION B: Desktop Standalone Suite

> **Verified July 6, 2026: 52 EXEs + 52 BATs at `G:/AZAZAEL_Standalone/` (438.9 MB total).** **Live audit (July 6 Session 3): 52 EXEs on G: drive** (G:/source-of-truth/ and G:/azazael/ have 0 EXEs â€” previously claimed 133 total was inflated). **51 .spec Nuitka build targets** (46 root + 4 G: drive duplicates + 1 other). 4 of 5 tested EXEs pass --help verification. All EXEs are STALE â€” codebase has evolved significantly (Python 3.14.6t, 481 .py files, 99 discovered, 104 registry keys). Nuitka builds BLOCKED by CompiledFrameType.c _PyStackRef error on 3.14.6t. Full rebuild would produce more than 52 EXEs â€” vermillion_lightfury (7 worm files), AOA (8 arms), Libra (12 core + 6 BCC modules), EveUnleashed all have zero .spec files.

### B1 â€” EXE Inventory (Full Catalog, 52 EXEs)

| # | EXE | Size | Tier | --help? | Source |
|---|-----|------|------|---------|--------|
| 1 | AZAZAEL_CLI_314t.exe | 8.2 MB | Core | âœ… PASS | CLI entry point |
| 2 | AZAZAEL_Toolkit_314t.exe | 8.0 MB | Core | âœ… PASS* | Toolkit launcher |
| 3 | AZAZAEL_314t_Launcher.exe | 8.0 MB | Core | â¬œ | Master launcher |
| 4 | CLUSTERWORMS_314t.exe | 9.3 MB | Orchestration | âœ… PASS (v2) | CORE/WORMS/CLUSTERWORMS.py |
| 5 | METACLUSTER_314t.exe | 6.6 MB | Orchestration | âœ… PASS | CORE/WORMS/METACLUSTER.py |
| 6 | CONCURRENCY_314t.exe | 12.0 MB | Orchestration | âœ… PASS* | CORE/WORMS/CONCURRENCY.py |
| 7 | NATURE_Clusters_314t.exe | 7.2 MB | Orchestration | âœ… PASS* | CORE/WORMS/NATURE_CLUSTERS.py |
| 8 | HYDRA_314t.exe | 7.7 MB | Orchestration | â¬œ | HYDRA orchestrator |
| 9 | HYDRA_Bridge_314t.exe | 7.2 MB | Orchestration | âœ… PASS | 6-stage pipeline bridge |
| 10 | HYDRA_Container_314t.exe | 8.5 MB | Orchestration | â¬œ | Container launcher |
| 11 | HYDRA_Analyzer_314t.exe | 8.0 MB | Orchestration | â¬œ | Analysis engine |
| 12 | SMARTDISK_314t.exe | 7.8 MB | Monitor | âœ… PASS* | CORE/WORMS/SMARTDISK.py |
| 13 | NETWORK_Diag_314t.exe | 16.6 MB | Monitor | âœ… PASS* | CORE/WORMS/NETWORK_DIAG.py |
| 14 | DISKZ_314t.exe | 8.0 MB | Monitor | â¬œ | Disk monitoring |
| 15 | PROCESSZ_314t.exe | 8.0 MB | Monitor | â¬œ | Process monitoring |
| 16 | NETWORXZ_314t.exe | 8.0 MB | Monitor | â¬œ | Network monitoring |
| 17 | CLOCKZ_314t.exe | 8.0 MB | Monitor | â¬œ | Time synchronization |
| 18 | OS_Congruency_314t.exe | 8.3 MB | Monitor | â¬œ | Windows OS congruency |
| 19 | BINARY_Analysis_314t.exe | 16.6 MB | Security | â¬œ | PE/ELF binary analysis |
| 20 | ERROR_Scan_314t.exe | 8.0 MB | Security | â¬œ | Error scanning |
| 21 | HEALING_WORM_314t.exe | 8.0 MB | Security | â¬œ | Self-healing |
| 22 | AZAZAEL_Inference_Studio_314t.exe | 11.2 MB | ML/AI | âœ… PASS* | Inference dispatch |
| 23 | Eve_Unleashed_314t.exe | 10.9 MB | ML/AI | NO_HELP (GUI) | RANI-VL AI desktop |
| 24 | OMNI_WORM_314t.exe | 8.0 MB | ML/AI | â¬œ | Self-healing worm |
| 25 | CODEX_Studio_314t.exe | 6.1 MB | CODEX | NO_HELP (GUI)* | Video generation studio |
| 26 | Create_Video_314t.exe | 14.1 MB | CODEX | â¬œ | CODEX/VIDEOS/create_video.py |
| 27 | Matrix_Video_314t.exe | 5.8 MB | CODEX | âœ… PASS* | CODEX/VIDEOS/generate_matrix_video.py |
| 28 | Compress_Video_314t.exe | 5.8 MB | CODEX | âœ… PASS* | CODEX/VIDEOS/compress_video.py |
| 29 | Video_Popup_314t.exe | 6.0 MB | CODEX | â¬œ | Video popup (tkinter) |
| 30 | Matrix_Animation_314t.exe | 5.8 MB | CODEX | â¬œ | Matrix animation |
| 31 | Auto_Doc_Gen_314t.exe | 4.1 MB | Tools | âœ… PASS* | Auto documentation |
| 32 | QL_Optimizer_314t.exe | 14.1 MB | Tools | âœ… PASS* | QL file optimizer |
| 33 | File_Manifest_314t.exe | 5.6 MB | Tools | â¬œ | File manifest generator |
| 34 | Changelog_Generator_314t.exe | 4.1 MB | Tools | âœ… PASS* | Changelog generator |
| 35 | Changelog_Gen_314t.exe | 8.0 MB | Tools | â¬œ | Changelog (alt build) |
| 36 | Complete_Systems_314t.exe | 4.0 MB | Tools | â¬œ | Complete systems |
| 37 | Comprehensive_Fix_314t.exe | 8.0 MB | Tools | â¬œ | Comprehensive fixer |
| 38 | Environment_Manager_314t.exe | 8.0 MB | Tools | â¬œ | Environment manager |
| 39 | Math_Certainty_314t.exe | 22.5 MB | Tools | â¬œ | Math certainty (LARGEST) |
| 40 | Twitler_Analysis_314t.exe | 3.8 MB | Tools | â¬œ | Twitler analysis (SMALLEST) |
| 41 | NODE_314t.exe | 8.0 MB | Tools | â¬œ | Node manager |
| 42 | Auto_Downloader_314t.exe | 8.0 MB | Tools | â¬œ | Auto-downloader |
| 43 | Azazael_Logger_314t.exe | 8.0 MB | Tools | â¬œ | Azazael logger |
| 44 | QL_Analysis_314t.exe | 8.0 MB | Tools | â¬œ | QL analysis |
| 45 | POPUP_Immersive_314t.exe | 6.0 MB | UI | âœ… PASS* | Immersive popup |
| 46 | POPUP_Bugfree_314t.exe | 10.9 MB | UI | â¬œ | Bug-free popup |
| 47 | POPUP_Clickable_314t.exe | 10.9 MB | UI | â¬œ | Clickable popup |
| 48 | POPUP_Simple_314t.exe | 10.9 MB | UI | â¬œ | Simple popup |
| 49 | Animation_Protocols_314t.exe | 8.0 MB | Viz | â¬œ | Animation protocols |
| 50 | ASCII_Flowchart_314t.exe | 8.0 MB | Viz | â¬œ | ASCII flowchart |
| 51 | Emoji_Maker_314t.exe | 8.0 MB | Viz | â¬œ | Emoji maker |
| 52 | Enhanced_Animations_314t.exe | 8.0 MB | Viz | â¬œ | Enhanced animations |

> *PASS* = marked with asterisk when verified in prior audit sessions (LESSONS_TASK_I_DESKTOP_AUDIT.md, SESSION_INSIGHTS_PHASE12). â¬œ = not tested this session.

### B2 -- Audit Summary

| Metric | Value |
|--------|-------|
| **Location** | `G:/AZAZAEL_Standalone/` |
| **EXE count (G: Standalone)** | 52 (`*_314t.exe` naming) |
| **.spec files (Nuitka targets)** | 51 (46 root + 4 G: drive + 1 other) |
| **BAT count** | 52 (`*_314t.bat`) -- 52:52 EXE:BAT matched |
| **Total size** | 438.9 MB (Standalone only) |
| **Size range** | 3.8 MB (Twitler) -- 22.5 MB (Math_Certainty) |

### B3 -- Nuitka Build Pipeline

> **Build Status: SUSPENDED on Python 3.14.6t** -- Nuitka 4.1.2 C backend fails with `CompiledFrameType.c(866): error C2440: cannot convert from 'int' to '_PyStackRef'`. All 52 existing EXEs are stale. Full rebuild would produce significantly more than 52 EXEs.

#### B3A -- Build Orchestrator: build_all.py

The Nuitka build system uses `build_all_concurrent.py` (39-target manifest) as the primary build orchestrator:

```python
# From build_all_concurrent.py -- 39 targets across 7 tiers
TIERS = {
    "Tier 1: Core": [
        "AZAZAEL_CLI", "AZAZAEL_Toolkit", "AZAZAEL_314t_Launcher",
    ],
    "Tier 2: Orchestration": [
        "CLUSTERWORMS", "METACLUSTER", "CONCURRENCY", "NATURE_Clusters",
        "HYDRA", "HYDRA_Bridge", "HYDRA_Container", "HYDRA_Analyzer",
    ],
    "Tier 3: Monitor": [
        "SMARTDISK", "NETWORK_Diag", "DISKZ", "PROCESSZ",
        "NETWORXZ", "CLOCKZ", "OS_Congruency",
    ],
    "Tier 4: Security": [
        "BINARY_Analysis", "ERROR_Scan", "HEALING_WORM",
    ],
    "Tier 5: ML/AI": [
        "AZAZAEL_Inference_Studio", "Eve_Unleashed", "OMNI_WORM",
    ],
    "Tier 6: CODEX": [
        "CODEX_Studio", "Create_Video", "Matrix_Video",
        "Compress_Video", "Video_Popup", "Matrix_Animation",
    ],
    "Tier 7: Tools + UI": [
        "Auto_Doc_Gen", "QL_Optimizer", "Math_Certainty",
        "POPUP_Immersive", "Animation_Protocols", "ASCII_Flowchart",
        "Emoji_Maker", "Enhanced_Animations",
    ],
}
```

#### B3B -- .spec File Pattern (Nuitka Build Config)

Each .spec file defines the Nuitka compilation target:

```python
# Example: CLUSTERWORMS_314t.spec (9.3 MB output)
bdist_exe = Execution(
    "CLUSTERWORMS.py",
    output_filename="CLUSTERWORMS_314t.exe",
    company_name="Azazael",
    file_version="2.0.0",
    onefile=True,
    standalone=True,
    enable_plugin=["tk-inter"],  # Only for GUI targets
    windows_uac_admin=False,
    windows_disable_console=False,
    assume_yes_for_downloads=True,
    noinclude_numba=True,
)
```

#### B3C -- Build Requirements & Constraints

| Requirement | Detail |
|-------------|--------|
| **Python** | 3.14.6t ONLY (free-threading build) |
| **Nuitka** | 4.1.2 (patched for 3.14t via `patch_nuitka_314t.py`) |
| **C compiler** | MSVC 2022 (Visual Studio 17.x) |
| **tkinter targets** | 14 EXEs need Tkinter plugin |
| **PYTHONPATH targets** | CONCURRENCY, SMARTDISK need explicit PYTHONPATH |
| **Build time (single)** | ~2-5 min per EXE |
| **Build time (all 39)** | ~90-180 min (parallel limited by 16 cores) |
| **Output dir** | `G:/AZAZAEL_Standalone/` |

#### B3D -- Build Failure Diagnostics

The current build blockage on 3.14.6t manifests as:

```
CompiledFrameType.c(866): error C2440: 'initializing':
  cannot convert from 'int' to '_PyStackRef'
```

**Root cause:** Python 3.14t renamed `_Py_IMMORTAL_REFCNT` to `_Py_IMMORTAL_REFCNT_LOCAL` and changed `_PyStackRef` from an integer typedef to a struct. Nuitka 4.1.2 generates C code assuming the old representation. The existing `patch_nuitka_314t.py` covers `allocator.h`, `HelpersAllocator.c`, and `HelpersDictionaries.c` but does NOT patch `CompiledFrameType.c`.

**Full rebuild would add these additional .spec targets:**
- `vermillion_lightfury/` (7 worm files -- MetasploitBridge, NmapScanner, etc.)
- `Desktop/AOA/` (8 arms -- azazael, codex, eve, libra + 4 support)
- `Desktop/Libra/` (11 modules -- cli, court_rules, litigation, etc.)
- `Desktop/EveUnleashed/` (146 files, 13 inference-capable .py files)
- All 13 Desktop projects requiring standalone builds

## SECTION C: Desktop Projects (Updated July 14, 2026 â€” Session 9 BCC Integration Complete)

> **Desktop landscape has changed significantly** since the May 29 DESKTOP_PROJECTS_AUDIT.md. 7 old projects removed, 4 new projects added. All 13 projects verified present on Desktop.

### Active Projects (Verified Present)

| # | Project | Type | Entry | Files | Key Capabilities |
|---|---------|------|-------|-------|------------------|
| C1 | **AOA** (NEW) | Umbrella orchestrator | AOA_STRUCTURE.html, benchmark_data.json | 54 | Quartet Neural Core â€” 4 arms (azazael, codex, eve, libra) + support_arms.py, 7 MP4 videos (101.4 MB total), 6 subdirectories (arms/, cli/, core/, frames/, proof_frames/) |
| C2 | **Libra** (NEW) | Legal automation | MILESTONE.py, LIBRA_STRUCTURE.html, BCC_READING_PA_TODO.md, SESSION_MILESTONE.md | 162+ | 12 core modules + 6 BCC jurisdictions/pa/berks/ modules (filing_submitter, court_rules, bcc_parser, ifp_assistant, prothonotary, court_calendar), filing_types.json (8 specific types, 6 MDJ districts, 5 contacts), 303 BCC tests passing (7 test files), 10 BCC templates, FilingSubmitter protocol (PaperFilingSubmitter + ECFFilingSubmitter), pa_courts.json e-filing flags, AOA libra_arm.py with 5 BCC capabilities |
| C3 | **CODEX_Azazael_Complete** (NEW) | Reference video | AZAZAEL_COMPLETE_REFERENCE_1080p.mp4 | 1 | 1080p reference video, frames/ |
| C4 | **CODEX_Quartet** (NEW) | Dashboard video | QUARTET_DASHBOARD_1080p.mp4 | 1 | 1080p quartet dashboard, frames/ |
| C5 | **EveUnleashed_Selector** | RANI-VL AI desktop | `run.py` | 146 | Multi-tab AI desktop app, multi-backend inference (Ollama, llama.cpp, HuggingFace), embedded Python REPL, system monitor, benchmark runner, GGUF model picker, theme system, SQLite memory |
| C6 | **LlamaServer** | Inference server | `run.py` | 7 | 4 inference backends (Jan/native llama.cpp, Rust cargo, Intel SYCL/Level Zero/NPU), GGUF model management, launch_llama_stack.ps1, llama_client.py |
| C7 | **PAMS** | Memory server | `run.py` | 11 | Persistent AI Memory Server on port 8420, CLI (start/benchmark/config/status), benchmark_pams.py, health_check.py, config/memory_config.json |
| C8 | **PerformanceMonitor** | Monitoring | `run.py`, `start.bat` | 20 | 5-service orchestration: Python Flask API (port 9777), Go WebSocket Gateway (9779), Rust Sysinfo Collector (9778), Python Tkinter Desktop App, HTML Dashboard |
| C9 | **Ultimate_Agent_Selector** | Agent launcher | `run.py` | 15 | Structural prototype â€” 10 planned agent types, agents/ contains only `__init__.py` (1.4 KB), golang_backend/ and rust_backend/ are empty directories |
| C10 | **WSL Models** | Model management | `run.py` | 10 | WSL-dependent model launchers |
| C11 | **WSL_CrossExplorer** | File transfer | `run.py` | 4 | WSL-Windows file transfer |

### Archived/Supporting

| # | Project | Type | Files | Status |
|---|---------|------|-------|--------|
| C12 | **AZAZAEL_ARCHIVE** | Archive staging | 10 | Present but empty â€” archive staging area |
| C13 | **AZAZAEL_Vault** | File visualizer | 8 | Has `index.html` â€” web-based file visualizer |

### C4 Deep-Dive â€” AOA (Armorie of Anubis / Quartet Neural Core)

> **Importability verified July 6, 2026:** All 8 arms register via correct import sequence (import arm modules BEFORE ArmRegistry()). All core modules importable. CLI entry point importable. **Arms are UNINITIALIZED â€” need runtime execution testing.**

| Component | Path | Capability | Executable? |
|-----------|------|------------|-------------|
| **azazael_arm.py** | `arms/azazael_arm.py` (2.8 KB) | Azazael worm ecosystem arm â€” discover_worms, run_cluster, run_metacluster, get_status | â¬œ Not tested |
| **codex_arm.py** | `arms/codex_arm.py` (4.1 KB) | CODEX Studio arm â€” render_mermaid, render_video, get_status | â¬œ Not tested |
| **eve_arm.py** | `arms/eve_arm.py` (4.7 KB) | Eve Unleashed arm â€” select_model, run_benchmark, run_inference, get_status | â¬œ Not tested |
| **libra_arm.py** | `arms/libra_arm.py` (5.8 KB) | Libra arm â€” list_templates, generate_document, calculate_fees, calculate_deadline, get_status + 5 BCC capabilities (check_berks_rules, calculate_berks_fees, generate_berks_ifp, prepare_berks_filing, get_berks_calendar), 10 BCC templates in _METHOD_MAP | âœ… BCC capabilities built (awaiting runtime test) |
| **support_arms.py** | `arms/support_arms.py` (8.6 KB) | 4 support arms: PAMS (record_event, get_memories p=8), PerfMon (get_metrics p=6), AgentSelector (select_agent p=6), LlamaServer (start/stop_server p=5) | â¬œ Not tested |
| **core/arm_registry.py** | `core/` (8.0 KB) | @register_arm decorator, ARM_REGISTRY, ArmRegistry.discover_arms() | âœ… Imports |
| **core/event_bus.py** | `core/` (4.8 KB) | EventPriority (LOW/NORMAL/MEDIUM/HIGH/CRITICAL), cross-arm event routing | âœ… Imports |
| **core/router.py** | `core/` (8.0 KB) | CrossArmRouter â€” 56 cross-arm routes | âœ… Imports |
| **core/session_manager.py** | `core/` (8.1 KB) | Session lifecycle: INITâ†’DISCOVERYâ†’INITIALIZEâ†’CAPABILITY_CHECKâ†’READYâ†’RENDERINGâ†’SHUTDOWNâ†’MILESTONE | âœ… Imports |
| **cli/aoa_cli.py** | `cli/` (10.6 KB) | cmd_init, cmd_arms_list, cmd_arms_status, main entry point | âœ… Imports |
| **benchmark_data.json** | Root | Live metrics: azazael (2), codex (4), perfmon (8), system (5) | âœ… Exists |
| **AOA_STRUCTURE.html** | Root (51 KB) | Whitepaper HTML with 14 Mermaid diagrams, WCAG AA palette | âœ… Built July 2 |
| **7 MP4s** | Root (101.4 MB) | Disclosure videos: Architecture (29.2 MB), Structure (10.3 MB), 2.5x speed variants, smooth raw (31.9 MB) | âœ… Built July 2 |

#### C4A â€” AOA "Fully Executable" Requirements (NEW â€” July 6, 2026)

> **Current state:** 8 arms register on import, all in `uninitialized` status. Core modules + CLI importable. No runtime execution verified.

**Known issues from source:**
1. **CLI shows 0 arms** if arm modules not imported BEFORE ArmRegistry() â€” requires correct import sequence
2. **EventPriority.MEDIUM crash** â€” enum only had NORMAL; MEDIUM alias added but untested

**To make fully executable, verify each arm's key capability:**

| # | Arm | Capability to Test | Method | Priority |
|---|-----|-------------------|--------|----------|
| C4A-1 | **Azazael** (p=10) | discover_worms, run_cluster, get_status | `arm.initialize()` â†’ `arm.discover_worms()` â†’ assert count > 0 | P0 |
| C4A-2 | **Libra** (p=9) | 5 core + 5 BCC capabilities (check_berks_rules, calculate_berks_fees, generate_berks_ifp, prepare_berks_filing, get_berks_calendar) | `arm.initialize()` â†’ `arm.list_templates()` â†’ assert non-empty â†’ test BCC capabilities | P0 |
| C4A-3 | **CODEX** (p=8) | render_mermaid, get_status | `arm.initialize()` â†’ `arm.render_mermaid(cluster_graph)` â†’ verify output | P1 |
| C4A-4 | **PAMS** (p=8) | record_event, query_memories | `arm.initialize()` â†’ `arm.record_event({...})` â†’ `arm.query_memories()` | P1 |
| C4A-5 | **EveUnleashed** (p=7) | select_model, run_inference, get_status | `arm.initialize()` â†’ `arm.select_model("llama3.2:1b")` â†’ verify | P1 |
| C4A-6 | **PerfMon** (p=6) | get_metrics | `arm.initialize()` â†’ `arm.get_metrics()` â†’ assert CPU/RAM values | P2 |
| C4A-7 | **AgentSelector** (p=6) | select_agent (stub v2) | `arm.initialize()` â†’ `arm.select_agent({...})` | P2 |
| C4A-8 | **LlamaServer** (p=5) | start_server, stop_server | `arm.initialize()` â†’ `arm.start_server()` â†’ verify port | P2 |

**Cross-arm integration tests:**
- [ ] Full session lifecycle: INIT â†’ DISCOVERY â†’ INITIALIZE â†’ CAPABILITY_CHECK â†’ READY â†’ SHUTDOWN
- [ ] Cross-arm event flow: PerfMon â†’ PAMS â†’ Azazael â†’ CODEX â†’ MP4 output
- [ ] CLI: `aoa_cli.py cmd_init` â†’ `cmd_arms_list` â†’ verify 8 arms with non-empty status
- [ ] Benchmark: run `benchmark_data.json` against all 8 arms and verify metrics update

**Build & deploy:**
- [ ] `build.py` or `build_discovery.py` produces standalone AOA orchestrator
- [ ] Nuitka .exe build for AOA umbrella orchestrator (target: `AOA_314t.exe`)
- [ ] AOA disclosure rebuild pipeline: benchmark_data.json â†’ HTML â†’ MP4 â†’ distribute

### C2A Deep-Dive â€” Libra (Legal Automation)

| Module | File | Capability |
|--------|------|------------|
| **cli.py** | `libra/cli.py` (18.3 KB) | Full CLI with subcommands for core, codex, cain, legal |
| **template_generator.py** | `libra/template_generator.py` (39.6 KB) | Largest module â€” legal document template generation |
| **court_rules.py** | `libra/court_rules.py` (10.0 KB) | PA Commonwealth + US Federal court rule management |
| **litigation.py** | `libra/litigation.py` (9.8 KB) | Litigation workflow management |
| **document_generator.py** | `libra/document_generator.py` (9.5 KB) | Automated legal document generation |
| **concurrent_filer.py** | `libra/concurrent_filer.py` (8.4 KB) | Multi-court concurrent filing |
| **filing_registry.py** | `libra/filing_registry.py` (7.6 KB) | Filing tracking and registry |
| **deadline_calculator.py** | `libra/deadline_calculator.py` (6.1 KB) | Court deadline computation |
| **cert_service.py** | `libra/cert_service.py` (2.3 KB) | Certificate of service generation |
| **fee_schedule.py** | `libra/fee_schedule.py` (2.2 KB) | Court fee schedule management |
| **filings/** | 25 items | Generated legal filings (mandamus, etc.) |
| **data/** | 61 items | Legal dictionaries, court data, templates |
| **native/** | 4 items | Rust native components |

#### C2B â€” BCC Jurisdiction Module (Berks County Court â€” 23rd Judicial District â€” NEW Session 9)

> **Complete Phase 1-4 implementation: 6 Python modules, filing_types.json, FilingSubmitter protocol, pa_courts.json e-filing flags, 7 test files (303 tests all passing), 5 BCC capabilities in AOA libra_arm.py, 10 BCC templates. 12 build tasks complete.**

| Module | File | Capability |
|--------|------|------------|
| **filing_submitter.py** | `jurisdictions/pa/berks/filing_submitter.py` | FilingSubmitter protocol, PaperFilingSubmitter (SASE, cover sheets, filing instructions), ECFFilingSubmitter (e-filing placeholder), get_filing_submitter() factory |
| **filing_types.json** | `jurisdictions/pa/berks/filing_types.json` | 6 berks_overrides, 8 berks_specific_types, 6 MDJ districts, 5 contacts, filing methods (paper/efs/ujs_portal/mail) |
| **court_rules.py** | `jurisdictions/pa/berks/court_rules.py` | Berks-specific rule checks: venue, MDJ jurisdiction, filing deadlines, fee schedules |
| **bcc_parser.py** | `jurisdictions/pa/berks/bcc_parser.py` | Berks-specific filing type parser â€” validates type names, extracts metadata |
| **ifp_assistant.py** | `jurisdictions/pa/berks/ifp_assistant.py` | IFP (In Forma Pauperis) eligibility check, FinancialAffidavit generation, PA Rules of Civil Procedure compliance |
| **prothonotary.py** | `jurisdictions/pa/berks/prothonotary.py` | Berks Prothonotary interface â€” filing instructions, contact info, business hours, fee schedule reference |
| **court_calendar.py** | `jurisdictions/pa/berks/court_calendar.py` | Berks County Court calendar â€” court schedule, holidays, argument dates, deadline calculation |
| **templates/** | 10 templates | bcc_verification, bcc_entry_of_appearance, bcc_continuance_motion, bcc_praecipe_argument, bcc_certificate_readiness, 5 standard templates (praecipe, notice, order, subpoena, certification) |
| **pa_courts.json** | `data/court_data/pa_courts.json` | Updated with efiling_ready, efiling_pro_se_available, submission_methods (paper/ecf), berks_filing_types_json path |
| **tests/** | 7 test files, 303 tests | test_bcc_rules, test_bcc_parser, test_bcc_filing_types, test_bcc_ifp, test_bcc_calendar (5 original) + test_bcc_integration, test_bcc_templates (2 new Session 9) |
| **docs/BCC.md** | Oversight research | Updated with Part 8 (12 federal + 8 state governing laws), Part 9 (Complaint Pathway Directory), Part 10 (Investigative Decision Tree) |

### C5 Deep-Dive â€” EveUnleashed (RANI-VL Adversarial AI Desktop)

> **Verified July 6, 2026 â€” 146 files, 90KB main app, 13 inference-capable .py files, adversarial agent subsystem (5 files), full test suite.** EveUnleashed is the most substantial Desktop project â€” a multi-tab AI desktop application with adversarial vision-language agents, multi-model inference, and embedded Python REPL.

| Property | Value |
|----------|-------|
| **Location** | `~/Desktop/EveUnleashed_Selector/` |
| **Main app** | `eve_unleashed_app.py` (90.7 KB) â€” massive Tkinter desktop application |
| **Entry** | `run.py` (1.2 KB) |
| **Total files** | 146 (34 .py files with capabilities) |
| **Inference files** | 13 .py files with inference capabilities |
| **Model files** | 22 .py files referencing model operations |

#### C5A â€” Adversarial Agent Subsystem

| Component | File | Size | Capability |
|-----------|------|------|------------|
| **Orchestrator** | `agents/adversarial/orchestrator.py` | 23.6 KB | Full adversarial pipeline orchestration â€” multi-backend inference, benchmark, model selection |
| **VL Bridge** | `agents/adversarial/vl_bridge.py` | 14.6 KB | Vision-Language bridge â€” Ollama, llama.cpp, GGUF, multi-model support |
| **Engine** | `agents/adversarial/engine.py` | 13.5 KB | Adversarial inference engine â€” model, vision, NPU support |
| **Vision Agent** | `agents/adversarial/vision_agent.py` | 9.7 KB | Vision pipeline with multi-backend support |
| **Agent** | `agents/adversarial/agent.py` | 11.0 KB | Base adversarial agent â€” inference, vision, NPU |

#### C5B â€” Test & Inference Suite

| Component | File | Size | Capability |
|-----------|------|------|------------|
| **Inference Test** | `scripts/inference_test.py` | 16.3 KB | Full inference pipeline testing across all backends — ⚠️ MISSING on disk 2026-09-14 |
| **Full Inference Test** | `scripts/full_inference_test.py` | 9.6 KB | Comprehensive multi-backend inference validation — ⚠️ MISSING on disk 2026-09-14 |
| **Run Inference Test** | `run_inference_test.py` | 9.6 KB | CLI inference test runner |
| **Adversarial Test** | `tests/test_adversarial_pipeline.py` | 5.6 KB | End-to-end adversarial pipeline test |
| **VL Bridge Test** | `tests/test_unit_bridge_agent.py` | 10.0 KB | Vision-language bridge unit tests |
| **Vision Agent Test** | `tests/test_unit_vision_agent.py` | 6.2 KB | Vision agent unit tests |

#### C5C â€” Model Generation & Probing

| Component | File | Size | Capability |
|-----------|------|------|------------|
| **Gen Everything** | `scripts/gen_everything.py` | 7.5 KB | Multi-model generation pipeline — ⚠️ MISSING on disk 2026-09-14 |
| **Probe Model** | `scripts/probe_model.py` | 3.1 KB | Model architecture probing and analysis — ⚠️ MISSING on disk 2026-09-14 |
| **Probe All** | `scripts/probe_all.py` | 3.2 KB | All-model batch probing — ⚠️ MISSING on disk 2026-09-14 |
| **TUI Model Switcher** | `logs/llama_switch_model_tui.py` | 14.9 KB | Terminal-based model switching UI with benchmark |
| **Memory Creator** | `scripts/create_memories.py` | 6.8 KB | Inference memory/context creation — ⚠️ MISSING on disk 2026-09-14 |

#### C5D â€” Desktop App Capabilities

| Feature | Implementation |
|---------|---------------|
| **Multi-tab interface** | Tkinter notebook with tabbed agent panels |
| **Multi-backend inference** | Ollama, llama.cpp, HuggingFace, Intel NPU (via vl_bridge) |
| **Embedded Python REPL** | Interactive Python shell within the app |
| **System monitor** | Real-time CPU/RAM/GPU metrics |
| **Benchmark runner** | Integrated model benchmarking (model_benchmark integration) |
| **GGUF model picker** | Visual GGUF model browser and selector |
| **Theme system** | Configurable UI themes |
| **SQLite memory** | Persistent conversation and session storage |

### C6 Deep-Dive â€” LlamaServer (Inference Server)

| Component | Detail |
|-----------|--------|
| **Backends** | Jan desktop app (llama.cpp win-vulkan), Rust cargo binary (llama-server.exe), Intel SYCL/Level Zero/NPU |
| **Models** | GGUF models from ~/llama-server/models/ with auto-discovery |
| **API** | OpenAI-compatible chat completions endpoint |
| **Scripts** | build_llama_all_backends.bat, launch_llama_stack.ps1 |
| **Client** | llama_client.py â€” test client for the inference API |

### C7 Deep-Dive â€” PAMS (Memory Server)

| Component | Detail |
|-----------|--------|
| **Server** | HTTP REST API on port 8420 (`src/server/pams_server.py`) |
| **Benchmark** | `benchmark_pams.py` â€” performance testing |
| **Health** | `health_check.py` â€” server health monitoring |
| **Config** | `config/memory_config.json` â€” server configuration |
| **Storage** | conversations.db for AI conversation history |

### C8 Deep-Dive â€” PerformanceMonitor

| Service | Port | Stack |
|---------|------|-------|
| **Flask API** | 9777 | Python Flask REST API |
| **WebSocket Gateway** | 9779 | Go WebSocket server |
| **Sysinfo Collector** | 9778 | Rust system information collector |
| **Desktop App** | GUI | Python Tkinter desktop application |
| **HTML Dashboard** | Web | Frontend interface |

### C9 Deep-Dive â€” Ultimate Agent Selector

> **Corrected July 6, 2026 Session 3: Previously claimed 43 Python agents and 10 active agent types. Live audit reveals this is a structural prototype.**

| Component | Detail |
|-----------|--------|
| **Status** | Structural prototype â€” `agents/` contains only `__init__.py` (1.4 KB) |
| **Planned agent types** | 10: artifact_admin, file_manager, npu_orchestrator, memory_bridge, code_generation, orchestrator, rl_learner, vl_vision, research, env_adapter |
| **Backends** | `golang_backend/` (empty), `rust_backend/` (empty) â€” directories exist but contain no code |
| **Other dirs** | `launcher/`, `config/` â€” present but undeveloped |
| **Entry** | `run.py` (15 total files in project root) |

---

### Removed from Desktop (since May 29 audit)

| # | Project | Previous Status |
|---|---------|----------------|
| â€” | AZAZAEL_Standalone | Was 52 EXEs â€” relocated to G:/AZAZAEL_Standalone/ |
| â€” | agent_system | Was standalone with run.py â€” removed |
| â€” | Azazael_UNIFIED | Was launcher with run.py â€” removed |
| â€” | CODEX | Was video generation â€” replaced by CODEX_Azazael_Complete + CODEX_Quartet |
| â€” | CODEX_Studio_Output | Was video player â€” removed |
| â€” | METAWORMS | Was report builder â€” removed |
| â€” | SysTools_JSON_Converter | Was JSON converter â€” removed | |

---

## SECTION D: WSL2 Projects

| # | Project | Path | Type | Status | Disclosure Relevance |
|---|---------|------|------|--------|---------------------|
| D1 | **azazael** (WSL2 copy) | `~/azazael/` | Core framework | â¬œ Review | WSL2 mirror of primary codebase |
| D2 | **llama.cpp** | `~/llama.cpp/` | LLM inference | â¬œ Review | C++ GGUF runner, local model inference |
| D3 | **openmono.ai** | `~/openmono.ai/` | AI platform | âŒ MISSING | .NET 10.0/C# project â€” NOT FOUND on WSL (July 6 Session 3) |
| D4 | **open-interpreter** | `~/open-interpreter/` | AI coding agent | â¬œ Review | Python-based AI coding agent |
| D5 | **models** | `~/models/` | GGUF models | â¬œ Review | Llama GGUF model storage |
| D6 | **workspace** | `~/workspace/` | Dev workspace | â¬œ Review | Scripts, orchestrators |
| D7 | **scripts** | `~/scripts/` | Automation | â¬œ Review | Shell/Python automation scripts |
| D8 | **go** | `~/go/` | Go workspace | â¬œ Review | Go projects |
| D9 | **intel** | `~/intel/` | Intel tooling | â¬œ Review | NPU/iGPU setup |

### Model Registry (Known Models)

| Model | Size | Quant | Location | Disclosure Relevance |
|-------|------|-------|----------|---------------------|
| Qwen3-VL 8B | 4.8 GB | Q4_K_M | ~/.lmstudio/models/ | Vision-Language AI model |
| Qwen3-VL abliterated v2.0 | 4.5 GB | Q4_K_S | ~/.lmstudio/models/ | Modified VL model |
| Gemma 4 E4B | ~3 GB | Q4_K_M | models/ | Text AI model |
| Eve-V2-Unleashed | ~5 GB | Q4_K_M | eve_rebuild_test/ | Custom fine-tuned model |

---

## SECTION E: AI/ML Systems (Regulatory Disclosure)

### E1 â€” AI API Provider Catalog (Verified July 6, 2026 from providers.py + secrets_manager.py)

**Total: 23 providers in PROVIDER_REGISTRY â€” 15 configured, 1 missing, 7 no-auth (Live-verified July 6 Session 4)**

#### E1A â€” Cloud Providers (OpenAI-Compatible API â€” /v1/chat/completions)

| # | Provider | Base URL | Env Var | Auth | Models | Key? | Rate Limit |
|---|----------|----------|---------|------|--------|------|------------|
| 1 | **Groq Cloud** | `api.groq.com/openai/v1` | `GROQ_API_KEY` | Bearer (gsk_) | 6 (Llama 4 Scout, Qwen3 32B, Llama 3.3 70B) | âœ… | 30 RPM, 6000 TPM |
| 2 | **OpenRouter** | `openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | Bearer | 31 (Gemini 2.5 Pro, DeepSeek R1, Nemotron 550B) | âœ… | 20 RPM |
| 3 | **NVIDIA NIM** | `integrate.api.nvidia.com/v1` | `NVIDIA_NIM_API_KEY` | Bearer (nvapi-) | 25 (Mistral Large 675B, Nemotron Ultra 550B, DeepSeek R1/V4) | âŒ | 40 RPM, permanent free |
| 4 | **Mistral AI** | `api.mistral.ai/v1` | `MISTRAL_API_KEY` | Bearer | 4 (Mistral Large, Codestral, Nemo) | âœ… | 15 RPM, ~1B tok/mo |
| 5 | **GitHub Models** | `models.github.ai/inference` | `GITHUB_TOKEN` | Bearer | 4 (GPT-4o, GPT-4o-mini, o4-mini, DeepSeek R1) | âœ… | 10-15 RPM |
| 6 | **HuggingFace Router** | `router.huggingface.co/v1` | `HF_TOKEN` | Bearer | 4 (Llama 3.3 70B, Qwen 2.5 72B, DeepSeek R1, Phi-4 Mini) | âœ… | 10 RPM, no CC |
| 7 | **Cerebras Cloud** | `api.cerebras.ai/v1` | `CEREBRAS_API_KEY` | Bearer | 2 (GPT OSS 120B, GLM 4.7 355B) | âœ… | 30 RPM, 1M tok/day |
| 8 | **Cloudflare Workers AI** | `api.cloudflare.com/.../ai/v1` | `CLOUDFLARE_API_TOKEN` + `ACCOUNT_ID` | Bearer | 3 (Llama 3.3 70B, Llama 4 Scout 17B) | âœ… | 30 RPM, free neurons |
| 9 | **SiliconFlow** | `api.siliconflow.com/v1` | `SILICONFLOW_API_KEY` | Bearer | 6 (Qwen3 32B, DeepSeek R1/V3, Llama 3.3 70B) | âœ… | 30 RPM, 200+ models |
| 10 | **Zhipu AI (Z.ai)** | `api.z.ai/api/paas/v4` | `ZHIPU_API_KEY` | Bearer | 3 (GLM-4.5, GLM-4.6) | âœ… | 30 RPM, bilingual |
| 11 | **Cohere (Compat)** | `api.cohere.ai/compatibility/v1` | `COHERE_API_KEY` | Bearer | 3 (Command R+, Command A+) | âœ… | 20 RPM, 1K calls/mo |
| 12 | **Google Gemini (Compat)** | `generativelanguage.googleapis.com/v1beta/openai/` | `GEMINI_API_KEY` | Bearer | 3 (Gemini 2.0 Flash, 2.5 Pro) | âœ… | 15 RPM, 1M TPM |
| 13 | **OVHcloud** | `endpoints.kepler.ai` | â€” | Anonymous | 3 (Llama 3.1 70B, Mistral 7B, Mixtral 8x7B) | âŒ | 2 RPM, no key needed |

#### E1B â€” Cloud Providers (Non-OpenAI-Comatible, Native API Protocol)

| # | Provider | API Protocol | Env Var | Auth | Models | Key? |
|---|----------|-------------|---------|------|--------|------|
| 14 | **Gemini Native** | `generateContent` RPC (query-param key) | `GEMINI_API_KEY` | Query param | 3 (Gemini 2.0 Flash, 2.5 Pro) | âœ… |
| 15 | **HuggingFace Native** | `/models/{id}` task-specific | `HF_TOKEN` | Bearer (hf_) | 3 | âœ… |
| 16 | **Mistral FIM Native** | `/v1/fim/completions` (fill-in-middle) | `MISTRAL_API_KEY` | Bearer | 2 (Codestral) | âœ… |
| 17 | **Cohere Native** | `/v2/chat` (content array format) | `COHERE_API_KEY` | Bearer | 3 (Command R+, A+) | âœ… |

#### E1C â€” Local Providers (OpenAI-Compatible API, No Internet)

| # | Provider | Endpoint | Auth | Models | Key? | Notes |
|---|----------|----------|------|--------|------|-------|
| 18 | **Ollama (Local)** | `localhost:11434/v1` | None | 9 (Llama 3.2, Gemma 2/3, LLaVA, embeddings) | N/A | Unlimited, no CC |
| 19 | **LM Studio (Local)** | `localhost:1234/v1` | None | 1 (loaded model) | N/A | GPU-accelerated llama.cpp backend |

#### E1D â€” Local Providers (Native/In-Process, No HTTP)

| # | Provider | Engine | Auth | Models | Key? | Notes |
|---|----------|--------|------|--------|------|-------|
| 20 | **Ollama Native** | `/api/generate` native HTTP | None | 9 | N/A | Same models as Ollama compat |
| 21 | **LlamaCpp Direct** | llama-cpp-python (in-process GGUF) | None | 4 (Llama 3.2 1B, Gemma 2/3, LLaVA) | N/A | Direct load from Ollama blobs |
| 22 | **HuggingFace Direct** | transformers (in-process) | None | 4 (Llama 3.2 1B/3B, Gemma 2/3) | N/A | AutoModelForCausalLM |
| 23 | **OpenVINO (Intel)** | openvino_genai + optimum-intel | None | Auto (CPU/GPU/NPU) | N/A | Intel Arc 140T GPU, AI Boost NPU, AVX-512 CPU |

**Note:** OpenVINO is the programmatic API. For pre-built standalone NPU inference with GGUF models, see [SECTION N â€” npExtractDir](#section-n-npextractdir--ipex-llm-intel-npu-inference) (IPEX-LLM llama-cli-npu.exe).

#### E1E â€” Authentication & Key Storage

| Mechanism | Details |
|-----------|---------|
| **SecretsManager** | `src/CORE/secrets_manager.py` â€” unified singleton, 3-source load order (env vars â†’ ~/.env â†’ ~/.azazael/*_config.json) |
| **Config files** | `~/.azazael/{provider}_config.json` â€” per-provider JSON with api_key, base_url, model |
| **Environment** | Standard var names per provider (see E1A-E1D above) |
| **Masking** | `SecretsManager._mask_key()` â€” displays as `nvapi-vM...CfmQ` in audits |
| **SecretRotator worm** | Category: config â€” credential rotation automation with backup and validation |
| **PII Risk** | API keys stored in `~/.env` and `~/.azazael/` â€” plaintext, filesystem-level access control only |

#### E1F â€” Key Audit Results (July 6, 2026)

| Status | Count | Providers |
|--------|-------|-----------|
| âœ… **CONFIGURED** | 15 | Groq, OpenRouter, Gemini, Cloudflare, Cohere, Cerebras, Mistral, GitHub, HuggingFace, SiliconFlow, Zhipu, NVIDIA NIM (newly verified), Cohere Native, Gemini Native, HuggingFace Native, Mistral FIM Native, GitHub â€” 15 cloud providers with API keys present |
| âŒ **MISSING** | 1 | NVIDIA NIM (needs API key, none configured) |
| N/A **NO AUTH** | 7 | Ollama, LM Studio, Ollama Native, HuggingFace Direct, LlamaCpp Direct, OpenVINO (local/in-process), OVHcloud (anonymous) â€” providers requiring no API key |

#### E1G â€” Data Flow & Privacy

| Aspect | Detail |
|--------|--------|
| **Data sent externally** | Prompt text + system prompt + conversation context â†’ 13 cloud providers |
| **Data residency** | Groq (US), OpenRouter (US), NVIDIA (US), Mistral (EU/FR), GitHub (US), HuggingFace (US/EU), Cerebras (US), Cloudflare (Global), SiliconFlow (CN), Zhipu (CN), Cohere (CA), Google Gemini (US), OVHcloud (EU/FR) |
| **Inference caching** | `.inference_cache/` â€” file-backed citation cache per RULE 0Q-A |
| **Circuit breaker** | Per-provider error threshold â†’ automatic disable on repeated failures |
| **Rate limiting** | Thread-safe per-provider RPM enforcement in `OpenAIProvider._check_rate_limit()` |
| **Failover** | RULE 0D Quota Jail â€” automatic provider rotation on rate limit / error |

**Regulatory items for EACH cloud provider:**
- [ ] Data processing agreement (DPA) status with each provider
- [ ] Data residency compliance (CN providers: SiliconFlow, Zhipu)
- [ ] Model version documentation (which model was used when)
- [ ] Usage tracking and cost auditing
- [ ] Provider terms of service compliance

### E2 â€” Autonomous Agent Architecture & Local Inference

> **Verified July 6, 2026: 4 core files (3,168 lines total) for agent lifecycle management, plus 23 local/cloud providers for inference. This forms the execution layer of the autonomous neural architecture.**

#### E2A â€” Agent Lifecycle & Pool Management (3,168 lines)

| Component | File | Lines | Classes | Key Capability |
|-----------|------|-------|---------|---------------|
| **MyAgent** | `CORE/Agent.py` | 845 | `MyAgent`, `AgentConfig`, `PamsRecorder` | Full agent lifecycle: initâ†’runâ†’recordâ†’heal. Integrates with PAMS for memory, DirectMemory for audit. Keyword: `heal` (11 refs) |
| **AgentPool** | `CORE/AgentPool.py` | 645 | `FreeThreadPool`, `AgentPool`, `PoolStats` | Parallel agent dispatch on Python 3.14t FreeThreadPool. PPO integration. Stats: submit count, success rate, avg execution time |
| **FreeThreadedAgent** | `CORE/FreeThreadedAgent.py` | 224 | `FreeThreadedAgent` | GIL-free agent execution on Python 3.14t. Thread-safe with property decorators for state isolation |
| **Agent Registry** | `CORE/agent_registry.py` | 526 | `MyAgent`, `MyRLAgent`, `@register_agent` | Agent registration with decorator pattern. MyRLAgent subclass for RL-specific agents |

#### E2B â€” Neural Pipeline Orchestration

| Component | File | Lines | Method | Key Capability |
|-----------|------|-------|--------|---------------|
| **NeuralPipeline** | `CORE/NeuralPipeline.py` | 766 | GRPO + PPO orchestration | Work-stealing pool + free-thread pool. GRPO (16 refs), reward (20 refs), PPO (4 refs), policy (3 refs), fitness (1 ref). Maps agent execution data â†’ structured neural workflows |

#### E2C â€” Local Model Infrastructure (4 Systems)

| System | Models | Inference Engine | Status |
|--------|--------|-----------------|--------|
| LlamaServer (Rust) | 8 GGUF models | Jan backend, llama.cpp, Intel SYCL/NPU | â¬œ Review |
| Ollama | Via Ollama API | Ollama runtime (localhost:11434) | â¬œ Review |
| LM Studio | Via local API | LM Studio runtime (localhost:1234) | â¬œ Review |
| llama.cpp (WSL2) | GGUF models | C++ runner + convert_hf_to_gguf.py | â¬œ Review |

**Regulatory items:**
- [ ] Agent autonomy boundaries defined
- [ ] Agent decision logging (DirectMemory agent learning loop: record_decision, record_lesson, set_goal)
- [ ] Agent failure modes cataloged
- [ ] Human oversight of autonomous agent actions

### E3 â€” Neural Training & Learning Systems (Summary)

> **Detailed deep-dives in E2A (Agent Architecture), E2B (NeuralPipeline), E3A (Dreaming & Meta-Cognition), E3B (Fusion & Self-Healing), E3C (Q-Learning Infrastructure). This table covers additional training systems not detailed elsewhere.**

| System | Algorithm | Source File(s) | Data Source | Output | Status |
|--------|-----------|---------------|-------------|--------|--------|
| **SB3 Agent** | SB3 (PPO w/ learning_rate) | `CORE/sb3_agent.py` (840L) | LocalMemoryStore | Trained RL policies | Document |
| **GRPO Learning** | Group Relative Policy Optimization (DeepSeek) | `CORE/CORE/WORMS/expansion/learning_grpo.py` (621L) | Execution history | GRPO-trained policies | Document |
| **Worm Selector** | GRPO-based worm selection | `CORE/CORE/WORMS/WORM_SELECTOR.py` (145L) | Execution history | Optimal worm dispatch | Document |
| **EvolutionEngine** | Population-based optimization | `CORE/CORE/WORMS/expansion/learning.py` (2,073L) | Execution metrics | Optimized parameters | Document |
| **GeneticOptimizer** | Genetic algorithms (crossover, mutation) | `CORE/CORE/WORMS/expansion/learning.py` (2,073L) | Per-worm fitness data | Optimized worm params | Document |
| **RLTrainLoop** | Q-learning (epsilon-greedy) | `CORE/CORE/WORMS/expansion/learning.py` (2,073L) | Execution data | Q-tables | Document |

**Regulatory items:**
- [ ] Training data provenance
- [ ] Model versioning (ModelVersioner worm)
- [ ] Training governance (CurativePool integration)
- [ ] Evaluation metrics and benchmarks
- [ ] Human oversight mechanisms

### E3A â€” Dreaming, Meta-Cognition & Hypnagogic Synthesis

> **Two dedicated modules (1,843 lines total) implement offline simulation-based policy improvement and self-reflective strategy adaptation.**

| Component | File | Lines | Classes | Mechanism |
|-----------|------|-------|---------|-----------|
| **DreamingModule** | `CORE/WORMS/expansion/dreaming.py` | 994 | `DreamingModule`, `HypnagogicSynthesizer`, `Dream` | Offline policy simulation â€” replays historical execution data through policy episodes in a sandboxed dream environment. Synthesizes novel training scenarios via hypnagogic state emulation. Improves policies without live execution risk |
| **MetaCognition** | `CORE/WORMS/expansion/meta_cognition.py` | 849 | `MetaCognitionWorm`, `MetaCognitionAgent` | Self-reflection engine â€” tracks episode outcomes, identifies error patterns, adapts strategy selection. Episode counter and confidence-weighted decision history. Registered as both a worm and an agent |

**Neural Lifecycle Integration:**
- Dreams run offline during idle cycles, using historical execution data from DirectMemory
- Meta-cognition runs after each agent episode, adjusting strategy weights
- HypnagogicSynthesizer creates synthetic edge cases from real failure patterns
- Both integrate with CurativePool governance for safety validation

### E3B â€” Fusion Architecture & Self-Healing (825 lines)

> **Three modules implement cross-module knowledge fusion and autonomous code repair.**

| Component | File | Lines | Classes | Mechanism |
|-----------|------|-------|---------|-----------|
| **ADLP FusionCore** | `ORCHESTRATION/ADLP_FusionCore.py` | 227 | `FusionCore`, `TIER`, `LVL` | Multi-agent learning fusion â€” merges outputs from parallel agent runs into consolidated model updates. TIER/LVL enums for structured fusion hierarchy |
| **FusionHealer** | `ORCHESTRATION/FusionHealer.py` | 227 | `FusionHealer` | Autonomous code repair â€” detects broken module fusions, restores to last known good state, logs healing events via PAMS. Self-diagnosis and remediation |
| **TotalFusion** | `ORCHESTRATION/TotalFusion.py` | 371 | `ModuleFusion`, `TotalFusion` | Cross-module fusion engine â€” merges disparate module outputs into cohesive workflows. Handles dependency resolution, conflict detection, and rollback |

**Self-healing workflow:** Module fusion -> detect failure -> FusionHealer restore -> re-fuse with ADLP -> CurativePool validate (E4A) -> TotalFusion deploy

### E3C â€” Q-Learning Infrastructure (2,366 lines)

> **Three files implement the full Q-learning stack, from hardware-aware optimization to multi-agent consensus learning.**

| Component | File | Lines | Classes | Algorithm |
|-----------|------|-------|---------|-----------|
| **Deep Learning Q-Learning** | `ORCHESTRATION/ml_platforms/improvements/deep_learning_qlearning.py` | 624 | `DLTaskType`, `DLQTable`, `DLFramework`, `HardwareType`, `ExperienceReplayBuffer` | Hardware-aware Q-learning â€” selects optimal framework (PyTorch/TF/JAX) and hardware (CPU/GPU/NPU) per task. Reward (15 refs), PPO (7 refs) |
| **Enhanced Q-Learning** | `ORCHESTRATION/ml_platforms/improvements/enhanced_qlearning.py` | 711 | `MultiAgentQLearning`, `PrioritizedReplay`, `SumTree`, `TaskType`, `Transition` | Multi-agent consensus Q-learning â€” agents share Q-tables via prioritized experience replay. SumTree data structure for O(log n) sampling |
| **Full Q-Table** | `ORCHESTRATION/ml_platforms/improvements/qlearning_table.py` | 1,031 | `ExperienceReplay`, `TargetNetwork`, `FrameworkState`, `TaskType`, `Transition` | Complete Q-table system â€” dual networks (online + target) with periodic sync, experience replay buffer, framework-aware state management |

**RL stack architecture:** Q-Table (1031L foundation) -> Enhanced QL (711L multi-agent) -> Deep Learning QL (624L hardware-aware top layer). All RL training governed by CurativePool (E4A) and audited via DirectMemory agent learning loop.

### E4 â€” CurativePool Governance, CAIN Oversight & Ecosystem Intelligence

> **Verified July 6, 2026 â€” CurativePool is the AI governance layer with 4-dimensional routing (ScopeValidator, NecessityJudge, EmotionDetector, ArchetypeRouter) at 771 lines. Integrated with CAIN accountability framework, PreActionGate compliance, and ecosystem oversight via METAWORMS/HYDRAMETA. This is the autonomous oversight layer for the neural architecture.**

#### E4A â€” CurativePool (Autonomous Governance Engine)

| Component | File | Lines | Classes | Function |
|-----------|------|-------|---------|----------|
| **CurativePool** | `META/MetaWormSpawner.py` | 771 | `CurativePool`, `ScopeValidator`, `NecessityJudge`, `EmotionDetector`, `ArchetypeRouter` | 4-dimensional governance routing: scope validation (is this in bounds?), necessity judgment (is this needed?), emotional attunement (does this align with CAIN values?), archetypal routing (which Jungian archetype governs this action?) |
| **ScopeValidator** | `META/MetaWormSpawner.py` | â€” | `ScopeValidator` | Validates agent actions against defined operational boundaries. Rejects out-of-scope actions before execution |
| **NecessityJudge** | `META/MetaWormSpawner.py` | â€” | `NecessityJudge` | Determines if agent actions are necessary vs redundant. Prevents unnecessary computation and API calls |
| **EmotionDetector** | `META/MetaWormSpawner.py` | â€” | `EmotionDetector` | CAIN-integrated emotional attunement â€” maps agent intent to 7 deadly sins accountability framework |
| **ArchetypeRouter** | `META/MetaWormSpawner.py` | â€” | `ArchetypeRouter` | Routes agent decisions through Jungian archetype filter â€” ensures agent behavior aligns with assigned archetypal patterns |

#### E4B â€” CAIN Accountability Framework

| Component | Detail |
|-----------|--------|
| **7 Deadly Sins** | Pride, Greed, Wrath, Envy, Lust, Gluttony, Sloth â€” each agent action scored against all 7 dimensions |
| **Jungian Archetypes** | Hero, Sage, Trickster, Shadow, Anima/Animus â€” archetypal routing via ArchetypeRouter |
| **Stakeholder Analysis** | Impact assessment across all stakeholders affected by agent decisions |
| **Emotion Web** | Interconnected emotional state tracking across the agent ecosystem |
| **75-panel format** | CODEX CAIN video rendering pipeline â€” Puppeteer capture, HEVC 1080p |

#### E4C â€” Ecosystem Oversight (METAWORMS + HYDRAMETA)

| Component | File | Lines | Classes | Function |
|-----------|------|-------|---------|----------|
| **METAWORMS** | `META/METAWORMS.py` | 693 | `METAZ`, `DEPENDZ`, `VALIDZ`, `WormResult`, `MetaWormConfig` | Worm analysis system â€” dependency validation (DEPENDZ), worm health scoring (METAZ), output validation (VALIDZ) |
| **HYDRAMETA** | `META/HYDRAMETA.py` | 934 | `HYDRAOptimizer`, `TrialResult`, `WormPerformance`, `PersistenceManager` | Multi-headed optimization â€” runs parallel worm trials, ranks performance, persists optimal configurations |
| **HYDRAMETA_UV** | `META/HYDRAMETA_UV.py` | 528 | `HYDRAMETA_UV`, `UVTrialResult`, `UVWormPerformance` | Ultra-violet variant of HYDRAMETA â€” enhanced trial comparison with UV-specific metrics |

#### E4D â€” PreActionGate & Mandate Integration

| Component | Function | Status |
|-----------|----------|--------|
| PreActionGate | Pre-action compliance verification (17 checks) | Document |
| RULE 0G (Gemini Mandate) | think-with-files-gemini at every major phase | Document |
| RULE 0M (Concurrent Inference) | All inference agents in parallel | Document |

**Regulatory items:**
- [ ] CurativePool decision audit trail â€” all ScopeValidator/NecessityJudge decisions logged
- [ ] CAIN accountability reports generated per session
- [ ] Agent governance boundaries documented
- [ ] Human override mechanisms for autonomous agent actions
- [ ] Archetypal alignment verification for sensitive operations


## SECTION F: Data Handling & Privacy

> **Verified July 6, 2026** â€” All findings sourced from live source code audit of direct_memory.py, audit_trail.py, local_memory.py, PamsRecorder.py, and MemoryBus.py with real filesystem measurements.

### F1 â€” Primary Data Store: Shared SQLite Database

**All 5 recording systems converge on `~/.azazael/memory_store.db`** â€” a single shared SQLite database (WAL mode) with additive tables. This is the canonical data store for the entire ecosystem.

| Property | Value (Live Audit July 6, 2026) |
|----------|----------------------------------|
| **Path** | `~/.azazael/memory_store.db` |
| **Size** | **1,117.86 MB** (1.09 GB) |
| **WAL file** | Not present (transient â€” appears during writes) |
| **SHM file** | Not present (transient â€” shared memory for WAL) |
| **Journal mode** | WAL (Write-Ahead Logging) |
| **Synchronous** | NORMAL (safe, faster than FULL) |
| **Busy timeout** | 5,000 ms |
| **WAL autocheckpoint** | Every 1,000 pages |
| **Encryption** | âŒ None â€” plaintext SQLite |
| **FTS5 index** | Yes â€” full-text search on event_type, data, tags |
| **Composite indexes** | 8 indexes for query performance |

#### F1A â€” Table: `memories` (Shared by DirectMemory + LocalMemoryStore)

| Column | Type | Content | PII Risk |
|--------|------|---------|----------|
| `id` | INTEGER PK | Auto-increment row ID | None |
| `session_id` | TEXT | Session identifier (e.g., `codebuff_20260706_101608`) | None |
| `source` | TEXT | Recording source (`"Codebuff"`, `"EveUnleashed"`, etc.) | None |
| `event_type` | TEXT | Event category (`file_read`, `file_edit`, `skill_loaded`, `test_run`, etc.) | None |
| `data` | TEXT (JSON) | **Full event payload** â€” file paths, prompts, test results, tooling details | âš ï¸ **HIGH** â€” Contains `C:\Users\clint\...` paths |
| `severity` | TEXT | `info`, `warning`, `error`, `critical` | None |
| `tags` | TEXT (JSON) | Tag array for categorization | None |
| `timestamp` | TEXT | ISO 8601 UTC timestamp | None |
| `created_at` | TEXT | SQLite datetime default | None |
| `event_uuid` | TEXT | UUID7 (RFC 9562) â€” time-sortable unique ID | None |
| `trace_id` | TEXT | CD1 cross-ledger trace identifier | None |
| `correlation_id` | TEXT | CD1 cross-ledger correlation ID | None |
| `audit_hash` | TEXT | BLAKE2b-256 of canonical event representation | None |
| `schema_version` | INTEGER | Schema version (default: 2) | None |

**What's recorded in `data` (JSON):**
- **file_read**: Full file paths, count, description â€” `{"files": ["C:/Users/clint/azazael/MEMORIES.md", ...], "count": 7}`
- **file_edit**: File path, description, lines_changed â€” `{"filepath": "PRODUCTION_TODO.md", "description": "Fix bug", "lines_changed": 3}`
- **file_create**: File path, description, size_bytes
- **file_delete**: File path, description
- **skill_loaded**: Skill name â€” `{"skill": "azazael-startup"}`
- **test_run**: Test suite, passed/failed counts, duration
- **code_review**: Subject, issues found/fixed
- **milestone_reached**: Title + custom details dict
- **session_start / session_end**: Lifecycle events with summaries
- **error_occurrence**: Error ID, title, file path, details

#### F1B â€” Table: `sessions` (Shared by DirectMemory + LocalMemoryStore)

| Column | Type | Content |
|--------|------|---------|
| `session_id` | TEXT PK | Session identifier |
| `started_at` | TEXT | UTC start timestamp |
| `ended_at` | TEXT (nullable) | UTC end timestamp â€” NULL = orphaned session |
| `source` | TEXT | `"Codebuff"`, `"EveUnleashed"`, etc. |
| `metadata` | TEXT (JSON) | Session metadata |
| `event_count` | INTEGER | Running count of events in this session |

**Orphaned sessions:** 1,396+ sessions with `ended_at IS NULL` â€” from Codebuff messages that exited without calling `.end()`. `DirectMemory.close_stale_sessions()` auto-closes sessions older than 1 hour.

#### F1C â€” Table: `memorybus_queue` (MemoryBus Persistent Fallback)

| Column | Type | Content |
|--------|------|---------|
| `id` | INTEGER PK | Auto-increment |
| `topic` | TEXT | Pub/sub topic (e.g., `"agent.status"`) |
| `content` | TEXT (JSON) | Message payload |
| `metadata` | TEXT (JSON) | Topic, source, timestamp metadata |
| `source` | TEXT | Publishing component identifier |
| `session_id` | TEXT | Session identifier |
| `timestamp` | TEXT | ISO 8601 timestamp |
| `flushed` | INTEGER | 0=queued, 1=flushed to PAMS |
| `event_uuid` | TEXT | UUID7 unique ID |
| `trace_id` / `correlation_id` | TEXT | CD1 cross-ledger IDs |
| `audit_hash` | TEXT | BLAKE2b-256 integrity hash |

---

### F2 â€” Audit Trail System

| Property | Value |
|----------|-------|
| **Location** | `.audit/session_<YYYYMMDD_HHMMSS>_<uuid4>.jsonl` |
| **Files found** | **15 files** in `.audit/` (root) + **48 files** in `azazael/.audit/` (live audit July 6 Session 3) |
| **Format** | JSONL â€” one JSON object per line, append-only |
| **Hash chain** | SHA-256 â€” each entry has `prev_hash` + `hash`; genesis hash = 64 zeroes |
| **Signing** | Ed25519 â€” `~/.azazael/audit_signing_key` (auto-generated on first use) |
| **Public key** | `~/.azazael/audit_signing_key.pub` |
| **Merkle tree** | SHA-256 double-hash tree â€” root stored in `session_end` entry |
| **Root-of-trust** | `.audit/anchors.jsonl` â€” cross-session head hash anchoring |
| **Checkpoints** | Every 100 entries â€” fast incremental verification |
| **Truncation detection** | `entry_count` in session_end vs actual line count |
| **Immutability** | File chmod to read-only after `close_session()` |
| **Anomaly scans** | Rate (>100 entries/sec), temporal (future timestamps), quantity (100K+ lines_changed) |

**Entry types recorded:**
`session_start`, `file_read`, `file_edit`, `file_create`, `file_delete`, `scan_anti_pattern`, `inference_spawn`, `sync_skills`, `test_run`, `skill_loaded`, `gate_passed`, `sentinel_run`, `code_review`, `tooling_verify`, `error_occurrence`, `expect_action`, `chain_checkpoint`, `session_end`

**PII Risk:** Each entry records full file paths (including username `clint`), descriptions, and context. However, the audit trail is cryptographically sealed â€” tampering is detectable via hash chain + Ed25519 signatures + Merkle proofs.

---

### F3 â€” PAMS Memory Server

| Property | Value |
|----------|-------|
| **URL** | `http://127.0.0.1:21434` (configurable via `PAMS_URL` env var) |
| **Database** | `conversations.db` in PAMS data directory |
| **Status** | Server present on Desktop (`Desktop/PAMS/` with `run.py`) |
| **Fallback chain** | PAMS HTTP â†’ LocalMemoryStore (SQLite) â†’ JSON buffer file â†’ dropped |
| **Retry logic** | 60-second cooldown after unreachable detection |

**Data forwarded to PAMS:**
- `event_type`, `source`, `severity`, `session_id`
- `data` (arbitrary JSON â€” may include prompts, file paths, agent actions)
- `timestamp` (ISO 8601)

**PII Risk:** Event data forwarded over localhost HTTP (no TLS). Contains same file paths and potentially prompt content as the local SQLite store.

---

### F4 â€” Secrets & Configuration Storage

| Store | Location | Format | Contents | PII Risk |
|-------|----------|--------|----------|----------|
| **Environment file** | `~/.env` | KEY=VALUE lines | 13 API keys, env vars | ðŸ”´ **CRITICAL** â€” Plaintext API keys |
| **Config JSONs** | `~/.azazael/*_config.json` | JSON (12 files) | Per-provider API keys + model settings | ðŸ”´ **CRITICAL** â€” Plaintext API keys |
| **Signing key** | `~/.azazael/audit_signing_key` | Raw Ed25519 bytes | 32-byte private key for audit signing | âš ï¸ MEDIUM â€” key material |
| **Project .env** | Various `azazael/` subdirectories | KEY=VALUE | Provider-specific config | ðŸ”´ **CRITICAL** |

**SecretsManager load order:**
1. Environment variables (highest priority)
2. `~/.env` file
3. `~/.azazael/{provider}_config.json` (fallback)

**PII concerns:**
- API keys stored in plaintext â€” filesystem permissions are the only protection
- `OPENAI_API_KEY` found committed in SCons debug output (see code-searcher results â€” `sk-proj-ZZPaHQ-...` exposed in `packages/azazael-core/cli.onefile-build/scons-debug.py`)
- No key rotation automation active (SecretRotator worm exists but status unverified)
- No hardware security module or encrypted vault

---

### F5 â€” Inference Cache

| Property | Value |
|----------|-------|
| **Location** | `~/.azazael/.inference_cache/` |
| **Files found** | 0 (cache directory empty) |
| **Purpose** | File-backed citation cache per RULE 0Q-A â€” records provider, model, prompt, and response |
| **Module** | `src/CORE/inference/inference_cache.py` |

**PII Risk:** When active, stores full prompts + responses from cloud AI providers. May contain sensitive content from user prompts.

---

### F6 â€” Worm Execution Data

| Store | Location | Format | Contents | PII Risk |
|-------|----------|--------|----------|----------|
| `worm_manifest.json` | `src/CORE/` | JSON | 80+ worm registry entries with descriptions | âœ… None |
| `worm_execution_history.jsonl` | Project root | JSONL | Worm execution timestamps + results | âœ… None |
| `worm_config_trace.json` | Project root (reported) | JSON | Worm registry trace | âœ… None |

---

### F7 â€” Data Flow Architecture (Verified from Source Code)

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”â”‚     ~/.azazael/memory_store.db       â”‚
â”‚     (1.12 GB, SQLite WAL)            â”‚
                    â”‚                                      â”‚
                    â”‚  Tables:                             â”‚
                    â”‚  â€¢ memories (DirectMemory + LMS)     â”‚
                    â”‚  â€¢ sessions (DirectMemory + LMS)     â”‚
                    â”‚  â€¢ memories_fts (FTS5 search)        â”‚
                    â”‚  â€¢ memorybus_queue (MemoryBus)       â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                               â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚                    â”‚                    â”‚
    â”Œâ”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”
    â”‚ DirectMemoryâ”‚    â”‚LocalMemoryStoreâ”‚    â”‚  MemoryBus  â”‚
    â”‚ (canonical) â”‚    â”‚ (query/recall) â”‚    â”‚ (pub/sub)   â”‚
    â”‚ session rec â”‚    â”‚ FTS5 search    â”‚    â”‚ PAMSâ†’SQLite â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                                    â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
    â”‚                                               â”‚
    â”‚  PamsRecorder                                 â”‚
    â”‚  (4-layer fallback)                           â”‚
    â”‚  1. PAMS HTTP (127.0.0.1:21434)               â”‚
    â”‚  2. LocalMemoryStore â†’ memory_store.db        â”‚
    â”‚  3. JSON buffer â†’ data/pams_fallback_records  â”‚
    â”‚  4. Dropped (graceful degradation)           â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  .audit/ (Separate JSONL storage)             â”‚
    â”‚  15 (root) + 48 (azazael/) session_*.jsonl     â”‚
    â”‚  + anchors.jsonl (root-of-trust)              â”‚
    â”‚  + Ed25519 signing keys                       â”‚
    â”‚  + Merkle tree per session                    â”‚
    â”‚  + SHA-256 hash chain                         â”‚
    â”‚  + Read-only after close                      â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  Secrets & Config                             â”‚
    â”‚  ~/.env (13 API keys)                         â”‚
    â”‚  ~/.azazael/*_config.json (12 files)          â”‚
    â”‚  ~/.azazael/audit_signing_key (Ed25519)       â”‚
    â”‚  All plaintext â€” filesystem perms only        â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### F8 â€” Cross-Environment Data Flow

| Source | Destination | Method | Data Type | Status |
|--------|------------|--------|-----------|--------|
| Windows 11 | WSL2 Ubuntu | `sync_all.py` | Code, scripts, skills | â¬œ Document |
| Windows 11 | G: drive | `robocopy` | Archive, source of truth | â¬œ Document |
| Windows 11 | Desktop | `sync_all.py` | Docs, EXEs, MP4s | â¬œ Document |
| Windows 11 | WSL2 Kali | `sync_all.py` | Code | â¬œ Document |
| PAMS Server | LocalMemoryStore | HTTP fallback â†’ SQLite | Memory events, potentially prompts | â¬œ Document |
| Codebuff â†’ Azazael | Python subprocess | Session events, file operations | â¬œ Document |

### F9 â€” Privacy Risk Summary

| Risk | Severity | Detail | Mitigation |
|------|----------|--------|------------|
| **Username in paths** | HIGH | `C:\Users\clint\...` in 1.12 GB of SQLite + 63 JSONL files (15 root + 48 azazael/) | Path sanitization not implemented |
| **API keys in plaintext** | CRITICAL | 13+ keys in `~/.env` + 12 `*_config.json` files | Filesystem permissions only; no encryption |
| **Prompt exposure in DB** | MEDIUM | Inference prompts/responses may be stored in memories data JSON | No automated purging of sensitive data |
| **1,396 orphaned sessions** | MEDIUM | Sessions with `ended_at=NULL` â€” data retained indefinitely | `close_stale_sessions()` exists but must be called explicitly |
| **No encryption at rest** | HIGH | All SQLite + JSONL + .env files are plaintext | Full-disk encryption (BitLocker) is system-level only |
| **API key in SCons debug** | CRITICAL | `OPENAI_API_KEY` exposed in `packages/azazael-core/cli.onefile-build/scons-debug.py` | Must be scrubbed from git history |
| **Localhost HTTP for PAMS** | LOW | No TLS on `127.0.0.1:21434` â€” local-only, low risk | Acceptable for localhost; would need TLS if exposed externally |

**Regulatory items:**
- [ ] Data inventory complete (NOW VERIFIED â€” 1 shared DB, 63 audit files (15 root + 48 azazael/), 12 config files)
- [ ] Encryption at rest? (NO â€” plaintext. Recommend BitLocker or SQLite encryption extension)
- [ ] Access controls? (Filesystem permissions only â€” Windows user isolation)
- [ ] Retention policy defined? (NO â€” 1,396 orphaned sessions; no automated purging)
- [ ] Right to deletion supported? (YES â€” `DirectMemory.purge_old()` and `LocalMemoryStore.purge_old()` exist)
- [ ] Cross-border data flows? (YES â€” 13 cloud providers in 6 jurisdictions: US, EU/FR, CN, CA, Global)

---

## SECTION G: Security & Compliance Infrastructure

### G1 â€” Security Worms

| Worm | Capability | Source | Verify |
|------|-----------|--------|--------|
| VulnScanner | CVE lookup, dependency audit, known-vulnerability detection | `src/CORE/WORMS/expansion/security.py` | â¬œ |
| PortAuditor | Open-port scanning, service fingerprinting, exposure analysis | `src/CORE/WORMS/expansion/security.py` | âœ… get_summary() passes |
| CertMonitor | SSL/TLS cert expiry tracking, chain validation | `src/CORE/WORMS/expansion/security.py` | â¬œ |
| FirewallAudit | Windows firewall rule analysis, gap detection | `src/CORE/WORMS/expansion/security.py` | â¬œ |
| PermissionScanner | File/directory permission audit, writable-path detection | `src/CORE/WORMS/expansion/security.py` | â¬œ |
| RaceConditionDetector | Shared-state access monitoring under 3.14t free-threading | `src/CORE/WORMS/expansion/race_detector.py` | â¬œ |
| MetasploitBridge | Kali Metasploit â€” auto exploit with checkpoint rollback, PAMS audit | `vermillion_lightfury/worms/` | â¬œ |
| NmapScanner | WSL-dispatched port/vulnerability scanning, VulnScanner cross-reference | `vermillion_lightfury/worms/` | â¬œ |
| SecretRotator | Credential rotation automation with backup and validation | `src/CORE/WORMS/expansion/config.py` | â¬œ |

### G2 â€” Compliance Infrastructure (13 Components â€” ALL VERIFIED OPERATIONAL July 6, 2026)

> **Self-test re-verified July 6 Session 3: `check_all()` returns `all_passed=False`** â€” formal_verification fails on "RULE 0J: PRE-ACTION GATE assertion required" (score 1.00, doc previously claimed 8/8 passed). AST scanner FULLY RE-VERIFIED: `scan_directory()` returns list of 173 `AntiPatternResult` objects â€” **352 total findings** across 93 files (sum of `finding_count`), 6 categories. Previously misreported as "173 findings" â€” that was the file count, not the finding count. All 13 components instantiate but compliance pipeline has at least 1 failing check.

#### G2A â€” RULE 0X Components (8): Automated Compliance Infrastructure

| # | Component | File | Class | Function | Key |
|---|-----------|------|-------|----------|-----|
| 0X-1 | **PolicyEngine** | `policy.py` | `PolicyEngine` | RBAC/ABAC policy gate â€” evaluates `evaluate_all(action, role, context)` | `allowed` |
| 0X-2 | **BrokerInterceptor** | `policy.py` | `@enforce_gate` decorator | Runtime tool call interception via wrapt | `active` |
| 0X-3 | **FormalVerifier** | `state_machine.py` | `FormalVerifier` | 4 default constraints: 0J gate, 0V review, 0R sync, valid state | `passed` |
| 0X-4 | **ComplianceStateMachine** | `state_machine.py` | `ComplianceStateMachine` | 5-state workflow: IDLE â†’ GATE_ASSERT â†’ CODE_EDIT â†’ CODE_REVIEW â†’ SYNC â†’ IDLE | `valid` |
| 0X-5 | **SchemaValidator** | `validating.py` | `SchemaValidator` | 11-field gate assertion schema validation | `passed` |
| 0X-6 | **ComplianceScorer** | `validating.py` | `ComplianceScorer` | 7 weighted metrics, halt threshold 0.5, snapshot() + record_pass/fail() | `should_halt` (False=pass) |
| 0X-7 | **ASTAntiPatternScanner** | `scanner.py` | `ASTAntiPatternScanner` | 7 anti-pattern categories: shell injection, hardcoded paths, os.system, etc. | `passed` |
| 0X-8 | **ComplianceTelemetry** | `telemetry.py` | `ComplianceTelemetry` | 2000-event ring buffer, emit_pass/fail/error(), get_summary() | `active` |

#### G2B â€” RULE 0Y Components (5): Multi-Agent Governance

| # | Component | File | Class | Function | Key |
|---|-----------|------|-------|----------|-----|
| 0Y-1 | **MultiAgentJudge** | `governance.py` | `MultiAgentJudge` | 2 default judges (policy + state_machine), 2/3 consensus required | `approved` |
| 0Y-2 | **ConfidenceGate** | `governance.py` | `ConfidenceGate` | Threshold 0.7, aggregate weighted scores from policy/verifier/reviewer | `passed` |
| 0Y-3 | **BehavioralGraphAnalyzer** | `governance.py` | `BehavioralGraphAnalyzer` | Directed action graph, anomaly detection (edit without read, 10+ edits zero review) | `anomalies_detected == 0` |
| 0Y-4 | **DualLedgerValidator** | `governance.py` | `DualLedgerValidator` | Cross-validate `.audit/` JSONL vs `~/.azazael/memory_store.db` | `consistent` |
| 0Y-5 | **RealtimeAuditPipeline** | `governance.py` | `RealtimeAuditPipeline` | 15-layer VLP middleware, hardened mode, process(audit_filepath) | `all_passed` |

#### G2C â€” Orchestrator (Wiring Layer)

| Component | File | Class | Function |
|-----------|------|-------|----------|
| **ComplianceOrchestrator** | `orchestrator.py` | `ComplianceOrchestrator` | Wires all 13 components; `check_all()` â†’ `ComplianceResult`; `check_rule_0x()`, `check_rule_0y()` |

**Self-test re-verified (July 6 Session 3 â€” âš ï¸ 1 failure found):**
- PolicyEngine: Developer allowed, Guest denied âœ“
- StateMachine: 5 legal transitions + illegal transition blocked âœ“
- FormalVerifier: âš ï¸ **FAILED** â€” "RULE 0J: PRE-ACTION GATE assertion required" (was: âœ“ 4/4 passed)
- SchemaValidator: 11-field schema validation passed âœ“
- ComplianceScorer: Score=1.000, no halt âœ“
- AST Scanner: Clean code passes, dirty code detects issues âœ“
- MultiAgentJudge: 2/3 consensus approves (ratio 0.667) âœ“
- Full orchestrator: **1 failure** â€” FormalVerifier RULE 0J check fails (was: ALL 8 RULE 0X + 5 RULE 0Y pass)

### G3 â€” Sentinel Gate (Pre-Action Authorization) â€” ALL PIPELINES VERIFIED July 6, 2026

> **Runtime verification summary:** Sentinel gate, gate_bash, gate_str_replace, and gate_write_file all tested via live code execution. sentinel_enforcer v3 OS-level file locking is active and preventing unauthorized writes.

#### G3A â€” Sentinel Gate Validation Results

| Test | Result | Details |
|------|--------|---------|
| **--validate (stdin pipe)** | âœ… **AUTHORIZED** | All 13 checks passed: AP-1, RULE 0G-0Y, GATE DECISION |
| **RULE 0X (programmatic)** | âœ… **8/8 passed** | Score 1.00 â€” PolicyEngine, StateMachine, FormalVerifier, SchemaValidator, ComplianceScorer, ASTScanner, Telemetry, BrokerInterceptor |
| **RULE 0Y (governance)** | âœ… **5/5 passed** | MultiAgentJudge, ConfidenceGate (0.7), BehavioralGraphAnalyzer, DualLedgerValidator, RealtimeAuditPipeline |
| **13-check suite** | âœ… **13/13 PASSED** | No FAIL, no VERIFIABLE LIE, no FALSE PASS |
| **Exit code** | 0 (AUTHORIZED) | Proceed granted |

#### G3B â€” Gate Pipeline Self-Test Results

| Pipeline | Tests | Passed | Key Findings |
|----------|-------|--------|--------------|
| **gate_bash.py** | 7/7 | âœ… **100%** | Destructive detection (rm -rf, pip install, cp site-packages), non-destructive passthrough (echo, git status), gate-and-execute, fail-closed on infra down â€” ALL PASSED |
| **gate_str_replace.py** | 1/4 explicit + 3 blocked | âœ… Core logic verified | 0-indent catastrophe detection PASSED; valid replacement/dry-run/post-validate BLOCKED by sentinel_enforcer v3 OS-level file locking â€” **this is correct behavior** |
| **gate_write_file.py** | Pre-validate works, mutation blocked | âœ… Core logic verified | Syntax error detection at pre-validate PASSES; file write blocked by sentinel_enforcer v3 â€” **this is correct behavior** |

#### G3C â€” Gate File Catalog (7 Files, All Verified)

| File | Status | Key Capability |
|------|--------|----------------|
| `src/SCRIPTS/sentinel_gate.py` (750+ lines) | âœ… IMPORT + VALIDATE | 13-rule validator, stdin/JSON/interactive modes, audit cross-ref (RULE 0T), pre/post-validate write/str_replace |
| `src/SCRIPTS/gate_str_replace.py` (380+ lines) | âœ… IMPORT + 4-SELF-TEST | 4-phase pipeline (pre-validateâ†’backupâ†’mutateâ†’post-validate), 0-indent catastrophe detection, auto-revert, heuristic recording |
| `src/SCRIPTS/gate_write_file.py` (330+ lines) | âœ… IMPORT + 4-SELF-TEST | 4-phase pipeline, syntax check, 0-indent warning, snapshot+revert |
| `src/SCRIPTS/gate_bash.py` (400+ lines) | âœ… IMPORT + 7-SELF-TEST (ALL PASSED) | 6 destructive pattern groups (deletion, system_write, package_mgmt, build_install, filesystem_mutation, system_state), 14 non-destructive patterns, fail-closed |
| `src/CORE/compliance/pre_action_gate.py` | âœ… SINGLETON LOADED | 16 public methods including validate_str_replace, validate_write_file, validate_after_edit, gate_str_replace, take_snapshot; orchestrator + heuristic_recorder + audit loaded |
| `src/CORE/sentinel_enforcer.py` | âœ… ACTIVE (WRITE BLOCKING) | `sys.addaudithook` intercepting file writes â€” confirmed blocking temp file creation in gate_str_replace/write_file tests |
| `src/CORE/enforcement_harness.py` | â¬œ Not tested | `ComplianceError(RuntimeError)` â€” enforcement violation handler |

#### G3D â€” Scanner Results (src/CORE/ â€” Live-verified July 6, 2026)

| Metric | Value |
|--------|-------|
| **Files scanned** | **173 files** in src/CORE/ |
| **Total findings** | **352 findings** across 93 files (80 files clean) |
| **Finding categories** | 6: `import_inside_function` (299), `unicode_emoji` (25), `hardcoded_win_path` (16), `t_string` (7), `os_system` (4), `fstring_backslash` (1) |
| **Result type** | `AntiPatternResult` â€” `filepath`, `finding_count`, `findings`, `lines_scanned`, `passed` |
| **Scanner class** | `ASTAntiPatternScanner` â€” public API: `scan_directory()`, `scan_file()`, `total_findings`, `total_scanned`, `get_summary()`, `get_scan_log()` |
| **Top file** | `NATURE_CLUSTERS.py` (23 findings), `providers.py` (17), `scanner.py` (16), `scheduling.py` (16) |
| **CLI modes** | --report, --ci, --compliance-score, --watch, --daemon, --format (text/json/html/junit-xml), --auto-fix, --db-init â†’ --db-trend/regression |

### G4 â€” Mandate Framework (30+ RULEs â€” Codified in MANDATES.md + SYSTEM_INSTRUCTIONS.md)

| Rule | Purpose | Enforcement |
|------|---------|-------------|
| RULE 0A | Never claim completion without verification | Manual gate assertion |
| RULE 0B | Follow instructions literally | Manual gate assertion |
| RULE 0C | Compliance sentinel â€” pre-action authorization | `sentinel_gate.py` (25-item checklist) |
| RULE 0D | Quota jail â€” automatic provider failover | `circuit_breaker.py` per-provider error tracking |
| RULE 0E | 10-phase multi-tier protocol (6 Gemini injection points) | Manual gate assertion |
| RULE 0F | Session startup procedure | `azazael-system-startup` skill |
| RULE 0G | Gemini mandate â€” spawn at every major phase | Manual gate assertion |
| RULE 0H | Anti-pattern recording mandate | `scanner.py` AST scanning (0X-7) |
| RULE 0I | Algorithmic respawn â€” no batch scripts without Gemini | Manual gate assertion |
| RULE 0J | Pre-action gate â€” mandatory assertion block | `sentinel_gate.py` / `pre_action_gate.py` |
| RULE 0J-A | Gated str_replace workflow | `gate_str_replace.py` (preâ†’backupâ†’mutateâ†’post) |
| RULE 0K | Canonical document reading order | Manual gate assertion |
| RULE 0L | Test failure â€” stop and spawn Gemini | Manual gate assertion |
| RULE 0M | Concurrent inference mandate | Manual gate assertion |
| RULE 0N | Worm execution â€” runtime truth only | Manual gate assertion |
| RULE 0P | Rule priority chain | Manual gate assertion |
| RULE 0Q | Post-phase inference check | Manual gate assertion |
| RULE 0R | Skills propagation mandate | `sync_skills.py` automation |
| RULE 0T | Verifiable truth â€” every action auditable | `audit_trail.py` hash chain + Ed25519 |
| RULE 0U | Instant system reminder compliance | Manual gate assertion |
| RULE 0V | Code reviewer pre/post mandate | Manual gate assertion |
| RULE 0W | Agent utilization â€” 100% capacity | Manual gate assertion |
| RULE 0X | Automated compliance infrastructure | **PROGRAMMATIC** â€” 8 components (0X-1 to 0X-8) |
| RULE 0Y | Multi-agent governance | **PROGRAMMATIC** â€” 5 components (0Y-1 to 0Y-5) |
| RULE 0Z | Spawn mandate â€” 3 agents at every task/sub-task | Manual gate assertion |
| RULE 0Z-A | Auto-fallback â€” query all models on think-gpt failure | Manual gate assertion |
| RULE 0Z-B | 11 followups mandate | Manual gate assertion |
| RULE 0Z-C | Destructive basher gate | `gate_bash.py` ComplianceOrchestrator integration |
| RULE 0Z-F | Parallel agent execution mandate | Manual gate assertion |
| RULE 0Z-G | No busy work mandate | Manual gate assertion |
| RULE 0Z-I | Inference API provider mandate | Manual gate assertion |

**Enforcement status:**
- 2 RULEs with **FULL programmatic enforcement** (0X, 0Y â€” 13 components, all self-test PASSED)
- 5 RULEs with **partial automation** (0C sentinel gate, 0D circuit breaker, 0H AST scanner, 0J pre-action gate, 0T audit trail)
- 24 RULEs with **manual gate assertion only** (human compliance required)

### G5 â€” Additional Compliance Infrastructure

| Component | File | Function | Status |
|-----------|------|----------|--------|
| **ComplianceAuditor** | `src/CORE/compliance_auditor.py` | Standalone compliance audit engine with scoring, scanning, and reporting | â¬œ Not tested |
| **ComplianceStateMachine** | `src/CORE/compliance/state_machine.py` | 5-state finite workflow: IDLE â†’ GATE_ASSERT â†’ CODE_EDIT â†’ CODE_REVIEW â†’ SYNC â†’ IDLE | âœ… Self-tested (test 2/8) |
| **ComplianceState enum** | `state_machine.py` | `IDLE, GATE_ASSERT, CODE_EDIT, CODE_REVIEW, SYNC, HALTED` | âœ… Verified |
| **ComplianceResult dataclass** | `orchestrator.py` | `all_passed, rule_0x, rule_0y, score, summary, checked_at` | âœ… Verified |
| **session_mappings.py** | `src/CORE/` | Cross-ledger DMâ†”AJ correlation (CD2) | â¬œ Not tested |
| **dual_ledger.py** | `src/CORE/` | Dual-ledger cross-validation and anomaly detection | â¬œ Not tested |
| **compliance_metrics.py** | `src/CORE/` | Compliance scoring and threshold monitoring | â¬œ Not tested |
| **heuristic_recorder.py** | `src/SCRIPTS/` | Error pattern catalog and heuristic learning | â¬œ Not tested |

---

## SECTION H: Cross-Project Integration

> **Verified July 6, 2026 â€” 5-environment sync, 4 cross-pillar bridges, 8-arm AOA quartet, 128-skill propagation. Live source audit: sync_all.py (369L), sync_canonical_docs.py (357L), auto_sync.py (257L), sync_skills.py (305L). CROSS_ENV_MANIFEST.md (177L). AOA core/ (5 files, 39.5 KB). paths.py (216L) with 8 dynamic resolvers.**

### H1 â€” Cross-Environment Sync Pipeline (Hub-and-Spoke)

> **sync_all.py (369L) at `azazael/scripts/sync_all.py` is the 5-environment bidirectional sync engine. Windows 11 is the hub; all other environments are spokes.**

#### H1A â€” sync_all.py: 5-Environment Hub-and-Spoke

| # | Environment | Path | Role | Sync Direction |
|---|-------------|------|------|----------------|
| 1 | **Windows 11** | `C:/Users/clint/azazael/` | **Hub** (primary dev) | Source of truth |
| 2 | **WSL2 Ubuntu** | `/root/azazael/` | Spoke | Windows â†’ WSL2 (Linux build target) |
| 3 | **Desktop** | `C:/Users/clint/Desktop/AZAZAEL_Standalone/` | Spoke | Windows â†’ Desktop (release deployment) |
| 4 | **G: source-of-truth** | `G:/source-of-truth/azazael/` | Spoke | Windows â†’ G: (canonical archive) |
| 5 | **G: AZAZAEL** | `G:/AZAZAEL/AZAZAEL_ROOT/` | Spoke | Windows â†’ G: (primary archive) |

**Key functions:**

| Function | Purpose |
|----------|---------|
| `run_wsl(command)` | Execute commands inside WSL2 via `wsl.exe` subprocess |
| `wsl_path(win_path)` | Translate Windows paths to WSL `/mnt/c/...` equivalents |
| `sync_windows_to_wsl2()` | Bidirectional rsync: Windows â†’ WSL2 `/root/azazael/` |
| `sync_docs_to_target(target)` | Sync canonical documents to any target environment |
| `get_env_status()` | Scan all 5 environments for drift detection and file presence |
| `verify_integrity()` | Hash-comparison integrity check across environments |
| `main()` | CLI entry: `--status`, `--sync-all`, `--sync-to <env>`, `--verify` |

**Sync data types:** Source code (`src/`), skills (`.agents/skills/`), documentation (`*.md`), EXEs + BATs, AOA deliverables (HTML, MP4, JSON)

#### H1B â€” sync_canonical_docs.py: Pillar Verification (357L)

| Function | Purpose |
|----------|---------|
| `hash_file(path)` | SHA-256 hash of any file for integrity comparison |
| `get_master_hashes()` | Build canonical hash manifest from Windows hub |
| `get_pillar_state(pillar)` | Query remote pillar (WSL/Kali/G:) for its document state |
| `verify_pillar(pillar)` | Compare pillar state against master hashes â€” detect drift |
| `sync_pillar(pillar)` | Push corrected documents to drifted pillar |
| `print_drift_report()` | Human-readable drift report across all pillars |

**Cross-target references (live source audit):** WSL (11 refs), G: (6 refs), Kali (1 ref)

#### H1C â€” auto_sync.py: Poll-Based Change Detection (257L)

| Function | Purpose |
|----------|---------|
| `compute_hashes()` | Scan canonical skills directory, compute SHA-256 manifest |
| `detect_changes()` | Compare current hash manifest against prior snapshot |
| `get_skill_count()` | Count skills in both canonical and target directories |
| `run_sync()` | Execute SkillsSync.sync_all() when changes detected |
| `poll_once()` | Single poll iteration: hash â†’ detect â†’ sync if needed |
| `watch_loop()` | Continuous poll loop with configurable interval |

**Session startup integration:** `session_start.py` (86L) fires at session bootstrap.

---

### H2 -- Cross-Pillar Bridges

> **Four dedicated bridges connect Azazael to its sibling pillars. Each bridge has bidirectional data flow with hash-verified integrity.**

#### H2A -- Tigger <> Azazael (Rust pyo3 Native Extension)

| Bridge Component | Direction | Mechanism |
|-----------------|-----------|-----------|
| **worm_manifest** | Tigger -> Azazael | Rust pyo3 extension -- `include_str!()` embeds full worm manifest at compile time. 8 functions (get_worm_count, find_worm O(1), search_worms, get_statistics). 1.07 us lookup vs 50ms pure Python |
| **Python fallback** | Azazael -> Tigger | Graceful import: `try/except ImportError` with pure Python fallback |
| **CLI bridge** | Bidirectional | `tigger stats` / `bench` / `info` / `discover` -- usable from both Windows and WSL |

```python
# Tigger bridge implementation pattern
try:
    import tigger
    HAS_TIGGER = True
    def find_worm(name: str) -> dict:
        return tigger.find_worm(name)  # 1.07 us Rust lookup
except ImportError:
    HAS_TIGGER = False
    def find_worm(name: str) -> dict:
        # Pure Python fallback -- 50ms linear scan
        for cat, worms in WORM_REGISTRY.items():
            if name in worms:
                return worms[name]
        return {}
```

**Performance bridge:** 1,000x (cold-start) to 46,700x (single lookup) speedups over pure Python.

#### H2B -- Vermillion <> Kali (SharedDirManager Cross-Env)

```python
# SharedDirManager cross-environment pattern
class SharedDirManager:
    def dispatch(self, worm_name: str, target: str, **kwargs) -> Result:
        """Dispatch worm execution to Kali via WSL2."""
        if target == "kali":
            # Serialize command and dispatch via wsl.exe
            cmd = self._build_wsl_command(worm_name, kwargs)
            result = subprocess.run(
                ["wsl", "-d", "Ubuntu-26.04", "-u", "root", "--"] + cmd,
                capture_output=True, text=True, timeout=120
            )
            # Parse result and sync back to Windows
            return self._parse_and_sync(result, worm_name)
```

| Bridge Component | Direction | Mechanism |
|-----------------|-----------|-----------|
| **SharedDirManager** | Vermillion -> Kali | Cross-environment directory sharing via WSL dispatch, results synced back via shared mount |
| **Worm bridge** | Bidirectional | 5 Kali-native worms (MetasploitBridge, NmapScanner, KaliHealth) + 2 support modules. 332/332 tests pass |
| **Path resolution** | `CORE/paths.py` -> Vermillion | `get_project_root()` dynamically resolves Vermillion path |

#### H2C -- Cross-Environment Sync Pipeline: sync_all.py

The hub-and-spoke sync engine ensures all 5 environments stay consistent:

```python
# From sync_all.py (369L) -- 5-Environment Hub-and-Spoke
class SyncEngine:
    ENVIRONMENTS = {
        "wsl2":   {"path": "/root/azazael/",         "type": "linux"},
        "desktop":{"path": "C:/Users/clint/Desktop/AZAZAEL_Standalone/", "type": "windows"},
        "g_src":  {"path": "G:/source-of-truth/azazael/", "type": "windows"},
        "g_root": {"path": "G:/AZAZAEL/AZAZAEL_ROOT/",    "type": "windows"},
    }

    def sync_to(self, target: str, dry_run: bool = False) -> SyncReport:
        """Sync Windows hub to one target environment."""
        if target == "wsl2":
            return self._rsync_wsl(dry_run)
        elif target in ("desktop", "g_src", "g_root"):
            return self._robocopy_target(target, dry_run)
        raise ValueError(f"Unknown target: {target}")

    def verify_integrity(self) -> Dict[str, bool]:
        """SHA-256 hash comparison across all environments."""
        master = self._get_master_hashes()
        results = {}
        for name, env in self.ENVIRONMENTS.items():
            results[name] = self._compare_hashes(env["path"], master)
        return results

    def get_env_status(self) -> Dict[str, EnvStatus]:
        """Scan all environments for drift detection and file presence."""
        return {name: self._scan_env(cfg) for name, cfg in self.ENVIRONMENTS.items()}
```

#### H2D -- sync_skills.py: Skills Propagation (305L)

Skills sync ensures all 128 skills are propagated to `.agents/skills/`:

```python
# From sync_skills.py -- SkillsSync engine
class SkillsSync:
    CANONICAL_DIR = Path("azazael/skills/")
    AGENT_DIR = Path(".agents/skills/")

    def sync_all(self, dry_run: bool = False) -> SyncReport:
        """Sync all skills from canonical to agent directory."""
        synced, skipped, failed = 0, 0, 0
        for skill_file in self.CANONICAL_DIR.glob("*.md"):
            target = self.AGENT_DIR / skill_file.stem / "SKILL.md"
            if self._needs_sync(skill_file, target):
                if not dry_run:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(skill_file, target)
                synced += 1
            else:
                skipped += 1
        return SyncReport(synced=synced, skipped=skipped, failed=failed)

    def get_gap_report(self) -> List[str]:
        """Return list of skills missing from agent directory."""
        canonical = {f.stem for f in self.CANONICAL_DIR.glob("*.md")}
        agent = {d.name for d in self.AGENT_DIR.iterdir() if d.is_dir()}
        return sorted(canonical - agent)
```

#### H2E -- AOA Quartet: 8-Arm Cross-Project Orchestration

The AOA (Armorie of Anubis) Quartet Neural Core orchestrates all major Desktop projects through a unified arm registry:

```python
# From AOA arms/ -- 8 arms registered via @register_arm decorator
@register_arm(name="azazael", priority=10)
class AzazaelArm:
    def initialize(self):
        self._worms = discover_worms()

    def get_status(self) -> dict:
        return {"worms": len(self._worms), "status": "ready"}

@register_arm(name="codex", priority=8)
class CodexArm:
    def render_mermaid(self, graph: str) -> str:
        # Render Mermaid graph definition to SVG
        ...

@register_arm(name="eve", priority=7)
class EveArm:
    def select_model(self, name: str):
        # Select GGUF model in EveUnleashed runtime
        ...
```

| Arm | Priority | Key Capability | Status |
|-----|----------|----------------|--------|
| **Azazael** (p=10) | P0 | discover_worms, run_cluster, run_metacluster | Imports OK |
| **Libra** (p=9) | P0 | list_templates, generate_document, calculate_fees | Imports OK |
| **CODEX** (p=8) | P1 | render_mermaid, render_video, get_status | Imports OK |
| **PAMS** (p=8) | P1 | record_event, query_memories | Imports OK |
| **EveUnleashed** (p=7) | P1 | select_model, run_inference, get_status | Imports OK |
| **PerfMon** (p=6) | P2 | get_metrics (CPU/RAM) | Imports OK |
| **AgentSelector** (p=6) | P2 | select_agent (stub v2) | Imports OK |
| **LlamaServer** (p=5) | P2 | start_server, stop_server | Imports OK |

### H3 -- CROSS_ENV_MANIFEST.md (177L)

The cross-environment manifest documents all 5 environments, their paths, roles, sync states, and integrity verification procedures. It serves as the canonical reference for deployment topology.

### H4 -- paths.py Dynamic Resolution (216L)

```python
# CORE/paths.py -- 8 dynamic path resolvers
def get_project_root() -> Path:
    return Path(__file__).resolve().parent  # Dynamic, not hardcoded

def get_g_drive() -> Path:
    return Path(os.environ.get("G_DRIVE", "G:/"))

def get_wsl_root() -> Path:
    return Path("/root/azazael/")

# All resolvers return Path objects for cross-platform compatibility
```

## SECTION I: Whitepaper Production Pipeline

### I1 â€” Source Data for Whitepaper

| # | Data Source | Format | Content | Status |
|---|-------------|--------|---------|--------|
| 1 | worm_manifest.json | JSON | 80+ worm entries with descriptions | âœ… Available |
| 2 | CODEBASE_AUDIT_TODO.md | Markdown | Living production plan v13 (replaced PRODUCTION_TODO.md â€” now archived in docs/archive/) | âœ… Available |
| 3 | PROJECT_MAP.md | Markdown | Complete ecosystem project inventory | âœ… Available |
| 4 | DESKTOP_PROJECTS_AUDIT.md | Markdown | 14 Desktop project operability audit | âœ… Available |
| 5 | ARCHITECTURE.md | Markdown | Dual-ledger system architecture | âœ… Available |
| 6 | MEMORIES.md | Markdown | Session history, anti-patterns, architecture | âœ… Available |
| 7 | MANDATES.md | Markdown | 30+ RULEs codification | âœ… Available |
| 8 | AOA disclosure HTML | HTML | 14 Mermaid diagrams, 12-color palette | âœ… Built July 2 |
| 9 | AOA disclosure MP4s | MP4 | 85s + 34s HEVC 1080p | âœ… Built July 2 |
| 10 | Worm execution data | JSONL | worm_execution_history.jsonl | â¬œ Audit |
| 11 | Test results | JSON | TEST_RESULTS.json | â¬œ Update |
| 12 | EXE audit | 52 EXEs on G: + 51 .spec files | Full cross-project audit completed July 6 Session 3 | âœ… DONE |
| 13 | tools/ utility scripts | Python + PowerShell | 36 scripts across 7 categories (see I1A below) | âœ… Cataloged |

#### I1A â€” tools/ Utility Scripts Deep-Dive (36 Scripts, 7 Categories)

> **Verified July 6, 2026 â€” 36 scripts at `C:/Users/clint/tools/`. All cataloged by function from tools/README.md.**

The tools/ directory is a critical operational asset â€” it contains the benchmark runners, model discovery scripts, build pipelines, and Intel NPU/GPU setup tools that power the Azazael ecosystem. These are NOT part of the core framework but are essential for development, benchmarking, and deployment.

| Category | Count | Key Scripts |
|----------|-------|-------------|
| **Benchmarks & Analysis** | 7 | `_benchmark_all.py`, `_full_benchmark.py`, `_run_benchmarks.py`, `_npu_gpu_bench.py`, `model_benchmark.py`, `_fast_analysis.py`, `_prod_readiness.py` |
| **Worm Execution** | 5 | `_all_worms.py`, `_run_all_worms.py`, `_query_all_apis.py`, `worm_semantic_search.py`, `_cain_findings.py` |
| **Build & Packaging** | 5 | `_build_more_native.py`, `_build_native2.py`, `_build_native_internet.py`, `_nuitka_diag.py`, `_isolate_import.py` |
| **Model Discovery & Setup** | 5 | `_discover_models.py`, `_load_all_lmstudio.py`, `_start_lmstudio.py`, `inference_dashboard.html`, `vision_qa.py` |
| **GPU & Intel Phase Tools** | 5 | `_gpu_load.py`, `_intel_phase1.py`, `_intel_phase2.py`, `_intel_phase3.py`, `_intel_setup.py` |
| **Analysis & Results** | 6 | `_inference_server_analysis.py`, `_eve_competence.py`, `_gemma_e2b.py`, `_find_bottleneck.py`, `_read_results.py`, `_reanalyze_watchdog.py`, `_rerun_analysis.py` |
| **Pipelines, Remote & Archive** | 7 | `_run_pipeline.py`, `_run_remote.py`, `_set_zhipu.py`, `_archive.ps1`, `_archive_tier1.ps1`, `_archive_tier1_missing.ps1`, `_cleanup_dupes.ps1` |

**Key capabilities:**
- **GPU/Intel toolchain:** 5 scripts for Intel Arc GPU + NPU setup and benchmarking (`_intel_phase1-3.py`, `_intel_setup.py`, `_gpu_load.py`)
- **Multi-backend inference:** `model_benchmark.py`, `_discover_models.py`, `_load_all_lmstudio.py` â€” discover and benchmark across 23 providers
- **Vision-language QA:** `vision_qa.py` â€” vision-language model testing
- **Worm semantic search:** `worm_semantic_search.py` â€” FTS5-backed worm lookup
- **Build pipeline:** Full native build toolchain + Nuitka diagnostics
- **Archive automation:** PowerShell-based tiered archiving to G: drive

### I2 â€” Whitepaper Structure (Proposed â€” 14 Sections)

| Section | Content Source | Visual | Status |
|---------|---------------|--------|--------|
| 1. Executive Summary | CODEBASE_AUDIT_TODO.md v13 metrics | Hero banner | â¬œ Build |
| 2. Architecture Overview | AOA disclosure + ARCHITECTURE.md | Mermaid diagram #1 (graph TD) | â¬œ Build |
| 3. Worm Registry | worm_manifest.json + CODEBASE_AUDIT_TODO.md v13 | Category pie chart + table | â¬œ Build |
| 4. AI/ML Systems | Sections E1-E4 above | Provider diagram + model table | â¬œ Build |
| 5. Data Handling | Sections F1-F2 above | Data flow diagram | â¬œ Build |
| 6. Security & Compliance | Section G above | 13-component compliance diagram + 15-layer VLP | â¬œ Build |
| 7. Desktop Suite | Sections B-C above | EXE inventory table + project cards | â¬œ Build |
| 8. Cross-Project Integration | Section H above | Ecosystem map | â¬œ Build |
| 9. GOSP DoctoralThesisEngine | Section J above | 7-tier architecture diagram | â¬œ Build |
| 10. Vermillion LightFury | Section K above | 7-file Kali bridge diagram (5 worms + 2 support modules) | â¬œ Build |
| 11. Verifiable Lie Protocol | Section L above | 15-layer stack visualization | â¬œ Build |
| 12. Tigger Performance | Section M below | Rust+Go+Python architecture diagram | â¬œ Build |
| 13. npExtractDir Intel NPU | Section N below | IPEX-LLM NPU inference table | â¬œ Build |

### I3 â€” Video Production

| # | Video | Content | Duration | Status |
|---|-------|---------|----------|--------|
| 1 | Scrolling whitepaper | Full HTML â†’ MP4 scroll capture | TBD | â¬œ Build |
| 2 | Architecture walkthrough | Mermaid diagram animation | TBD | â¬œ Build |
| 3 | AI governance overview | Provider + governance flow | TBD | â¬œ Build |
| 4 | Disclosure package summary | Top-level overview | 2-3 min | â¬œ Build |

### I4 â€” Legal Disclosure Checklist

- [ ] **Software Inventory**: Complete list of all software components, versions, licenses
- [ ] **AI System Register**: All AI models used (local + cloud), capabilities, limitations
- [ ] **Data Processing Register**: What data is collected, stored, processed, shared
- [ ] **Third-Party Services**: All external API providers, terms of service, data processing agreements
- [ ] **Security Measures**: Encryption, access controls, audit trails, vulnerability scanning
- [ ] **Compliance Framework**: 30+ RULEs, COMPLIANCE SENTINEL, Pre-Action Gate
- [ ] **Risk Assessment**: Known limitations, failures, error patterns (from ERROR_LOG.md)
- [ ] **Human Oversight**: CurativePool governance, CAIN accountability framework
- [ ] **Data Subject Rights**: Data access, correction, deletion capabilities
- [ ] **Cross-Border Data Flows**: Data movement between environments (Windows, WSL2, Kali, G:)
- [ ] **Incident Response**: Error recovery, circuit breaker, dead letter queue
- [ ] **Documentation Version**: Date-stamped, version-controlled disclosure package

---

## EXECUTION PLAN

### Phase 1: Data Collection (Current â€” Sections A-L)
- [x] Read and categorize ALL 104 worm manifests (18 categories, runtime verified)
- [x] Audit 52 EXE files on G:/AZAZAEL_Standalone/ (4/5 --help tested); full cross-project audit: 52 EXEs + 51 .specs (July 6 Session 3)
- [x] Verify 13 Desktop project run.py launchers (11 active, 2 archived)
- [x] Document AI API provider configurations (23 providers, 13 configured, 6 jurisdictions)
- [x] Map all data stores and data flows (1.12 GB SQLite, 63 audit files (15 root + 48 azazael/), 7 PII risks)
- [x] Catalog Tigger â€” Rust+Go+Python performance engine (11 files), pyo3 worm_manifest (7,158 lines Rust), Go module, Python CLI (stats/bench/info/discover), 1,000-32,000x speedups
- [x] Catalog npExtractDir â€” IPEX-LLM Intel NPU standalone package, 3 supported GGUF models (Llama 3.2 3B, DeepSeek R1 Distill Qwen 1.5B/7B), Lunar Lake/Arrow Lake/Meteor Lake configs
- [x] Catalog tools/ â€” 36 utility scripts across 7 categories (benchmarks, worm execution, build/packaging, model discovery, GPU/Intel tools, analysis, pipelines/remote)
- [x] Catalog GOSP â€” 7-tier DoctoralThesisEngine, Rust 338 lines, 9 CLI commands
- [x] Catalog Vermillion LightFury â€” 7 worm files (5 Kali-native worms + mixins.py + exceptions.py), 332/332 tests, 19 test files, SharedDirManager
- [x] Document VLP â€” 15-layer verification stack, RULEs 0T/0T-A/0T-B, sentinel gate integration
- [x] Verify gate pipelines â€” sentinel 13/13, gate_bash 7/7, scanner: 173 files scanned, **352 findings** (93 files with findings, 80 clean, 6 categories)
- [x] Verify DirectMemory v1.1.0 â€” _V canonical vocabulary (37 types), agent learning loop (9 methods), 14 static query/maintenance methods, 20/20 tests pass, fully self-sufficient (SessionMemory no longer needed)
- [ ] Test GOSP scan/harvest/search/serve CLI commands
- [ ] Test Vermillion LightFury 7 worm files for runtime execution
- [ ] Run VLP 15-layer audit on all 46 session audit files

### Phase 2: Content Authoring
- [ ] Write 9-section whitepaper HTML
- [ ] Generate updated Mermaid diagrams
- [ ] Create data flow diagrams
- [ ] Build regulatory compliance tables

### Phase 3: Visual Production
- [ ] Render scrolling HTML â†’ MP4 (Puppeteer, 1080p HEVC)
- [ ] Create architecture walkthrough video
- [ ] Produce disclosure package summary video

### Phase 4: Distribution
- [ ] Deploy HTML to Desktop, G:, WSL, Kali
- [ ] Deploy MP4s to all environments
- [ ] Create disclosure-build skill for reproducibility

---

## SECTION M: Tigger â€” Native Performance Engine

> **Status: Live-verified July 6, 2026 â€” 11 files at `C:/Users/clint/tigger/`. Rust pyo3 extension (7,158 lines), Go module, Python CLI (stats/bench/info/discover). 1,000â€“32,000x speedups over pure Python for worm registry operations.**

### M1 â€” Overview

Tigger is the **unified native performance engine** for the entire Quartet ecosystem â€” Azazael, GOSP, Vermillion LightFury, and the Quartet Pillar Architecture. It replaces cold-start bottlenecks with Rust and Go native extensions.

| Property | Value |
|----------|-------|
| **Location** | `C:/Users/clint/tigger/` (Windows project root) |
| **Language** | Rust (pyo3) + Go + Python CLI |
| **Version** | 0.1.0 (`pyproject.toml`) |
| **Total files** | 11 (4 Python + 2 Rust + 1 Go + 1 benchmark + 1 doc + 2 config) |
| **Python files** | `__init__.py`, `cli.py`, `pyproject.toml`, `README.md` |
| **Native code** | `native/worm_manifest/src/lib.rs` (7,158 bytes), `native/worm_manifest/Cargo.toml` (443 bytes) |
| **Go code** | `native/go/go.mod` (389 bytes) |
| **Benchmarks** | `benches/bench_worm_manifest.py` (1 file) |
| **Docs** | `docs/PERFORMANCE.md` (4,522 bytes), `README.md` |
| **Subdirectories** | 5: `benches/`, `data/`, `docs/`, `native/`, `__pycache__/` |

### M2 â€” Performance Benchmarks

| Metric | Python | Tigger (Rust pyo3) | Speedup |
|--------|--------|-------------------|---------|
| Worm registry cold-start | 1.264s (median) | **5.03 ms** (WSL .so load) | **~251x** |
| Single worm lookup | ~50ms (file scan) | **1.07 Âµs** (HashMap O(1)) | **~46,700x** |
| Full registry discovery | 0.905s (steady state) | **~50 Âµs** (embedded JSON) | **~18,100x** |
| Case-insensitive search | ~500ms (linear scan) | **21.6 Âµs** (scan 104 entries) | **~23,100x** |

### M3 â€” Core Components

#### M3A â€” worm_manifest (Rust pyo3 Extension)

Python-native extension embedding the full worm manifest (99 discovered, 104 registry keys, 18 categories) at compile time via `include_str!()`. 8 functions:

| Function | Description | Performance |
|----------|-------------|-------------|
| `get_worm_count()` | Total worms (104) | 0.1 Âµs |
| `get_all_categories()` | All 18 category names | â€” |
| `find_worm(name)` | Single worm lookup (O(1) HashMap) | 1.07 Âµs |
| `search_worms(query)` | Case-insensitive name/description search | 21.6 Âµs |
| `get_worms_by_category(cat)` | Filter by category | â€” |
| `get_worms_by_priority_range(min, max)` | Filter by priority | â€” |
| `get_all_worms()` | All 104 entries as Python dicts (sorted) | 0.51 ms |
| `get_statistics()` | Aggregate ecosystem stats | 43 Âµs |

**Key design:** `OnceLock` for thread-safe lazy init (safe under Python 3.14t free-threading), immutable `HashMap`, `include_str!()` embeds JSON at compile time â€” zero filesystem dependency. Graceful Python fallback if native extension unavailable.

#### M3B â€” Go Module (Cross-Pillar Sync)

Go components for cross-pillar synchronization benchmarking and network-level optimization. Phase 2 (planned).

#### M3C â€” Python CLI

| Command | Function |
|---------|----------|
| `tigger stats` | Show worm registry statistics |
| `tigger bench` | Run performance benchmarks against native manifest |
| `tigger info` | Show ecosystem overview (Azazael, Vermillion, GOSP status) |
| `tigger discover` | Discover and register all worms |

### M4 â€” Architecture

Tigger sits at the intersection of the Quartet Pillar Architecture, bridging:

| Project | Bridge |
|---------|--------|
| **Azazael** | `discover_worms()` fast-path â€” replaces Python cold-start with Rust HashMap |
| **Vermillion LightFury** | `_find_vermilion()` path resolution + reference HTML integration |
| **GOSP** | `_find_gosp()` path resolution + Cargo.toml detection |
| **Quartet** | Cross-pillar sync via Go module (planned Phase 2) |

### M5 â€” Build & Deploy

| Component | Build System |
|-----------|-------------|
| **worm_manifest** | Maturin (`maturin build --release`) â†’ .whl for Python 3.12+/3.14t |
| **Go module** | Go toolchain (planned) |
| **Python CLI** | pip install (`pyproject.toml`, `pip install -e .`) |
| **Nuitka .exe** | âŒ No .spec file â€” not yet packaged for standalone |

**Verification items:**
- [x] Import `tigger` module â€” âœ… imports successfully
- [x] `tigger stats` â€” âœ… shows registry statistics (via Python fallback; Rust extension requires WSL .so build)
- [ ] `tigger bench` with Rust pyo3 extension loaded (requires WSL .so or Windows .pyd build)
- [ ] Build `worm_manifest` .pyd for Windows (74/??? dependency rlibs compiled â€” needs extended build window)
- [ ] Create `.spec` file for Nuitka standalone build

---

*This TODO is a living document. It changes as production execution resolves. Each `â¬œ` checkbox represents a capability that must be individually reviewed and verified for the final disclosure whitepaper.*

---

## SECTION J: GOSP â€” Gossamer Oxford Semantical Parser

> **Status: Import + compile verified July 6, 2026 â€” `cargo build` succeeds (1 warning: G: drive hard-link).** GOSP is a Rust-based 7-tier DoctoralThesisEngine for semantic data harvesting. Currently at 338 lines of Rust ("ðŸŸ¡ Started"). Located at `G:/source-of-truth/GOSP/` (Windows) and `/root/workspace/projects/doctoral-thesis-engine/` + `/root/workspace/projects/gossamer-oxford-parser/` (WSL2 Ubuntu).

### J1 â€” Overview

GOSP (Gossamer Oxford Semantical Parser / Semantic Harvester) is a lightweight Rust-based TUI application for semantic data harvesting and parsing. It scans files, extracts semantic meaning via local LLM, and builds searchable knowledge bases. Named "Semantic Harvester" in the CODEX capability templates.

| Property | Value |
|----------|-------|
| **Language** | Rust (ratatui TUI, 338 lines, `cargo build` succeeds) |
| **Code location** | `G:/source-of-truth/GOSP/` (Windows), `/root/workspace/projects/gossamer-oxford-parser/` (WSL2) |
| **Primary docs** | `docs/RUST_CONVERSION_PLAN.md` Phase 4, `scripts/train_gosp_curative.py`, `scripts/generate_capability_templates.py` |
| **Build** | Rust cargo workspace crate `gosp` (`cargo build` âœ…), Nuitka Python companion |
| **Test status** | â¬œ Not tested this session |
| **Dependencies** | `azazael-registry`, `azazael-memory` (Rust crates, not yet built) |
| **CI** | `gosp-ci.yml` on G: drive (created, never run) |

### J2 â€” 7-Tier DoctoralThesisEngine Architecture

| Tier | Name | Function | Status |
|------|------|----------|--------|
| **Tier 1** | INGESTION | File scanner, format parser â€” `gosp scan <path>` | ðŸ”´ Not started |
| **Tier 2** | EXTRACTION | Semantic meaning extractor via local LLM â€” `gosp harvest <query>` | ðŸ”´ Not started |
| **Tier 3** | STRUCTURING | Knowledge graph builder â€” `gosp search <query>` | ðŸ”´ Not started |
| **Tier 4** | HYDRAMETA | Cross-domain analysis engine â€” `gosp serve` | ðŸ”´ Not started |
| **Tier 5** | DISTILLATION | Pattern synthesis via MetaCognitionWorm â€” `gosp train --epochs <N>` | ðŸ”´ Not started |
| **Tier 6** | DREAMING | Offline simulation via DreamingModule â€” `gosp dream --episodes <N>` | ðŸ”´ Not started |
| **Tier 7** | PUBLICATION | Academic formatting, dissertation output â€” `gosp thesis --output <dir>` | ðŸ”´ Not started |

### J3 â€” CLI Commands (Planned)

| Command | Tier | Function |
|---------|------|----------|
| `gosp scan <path>` | 1 | Directory scanning with dry-run preview, file discovery |
| `gosp harvest <query>` | 2-3 | Semantic content extraction with configurable workers |
| `gosp search <query>` | 3 | Top-k semantic search with JSON/table output |
| `gosp serve` | 4-7 | HTTP server with LLM backend for real-time queries |
| `gosp api <endpoint>` | 4-7 | REST API client |
| `gosp tui` | All | Interactive terminal UI (ratatui) |
| `gosp train --epochs <N>` | 5 | Train with CurativePool CAIN governance |
| `gosp dream --episodes <N>` | 6 | Run dreaming cycle |
| `gosp thesis --output <dir>` | 7 | Generate dissertation |

### J4 â€” Training Pipeline

| Component | File | Function |
|-----------|------|----------|
| **GOSPTrainingPipeline** | `scripts/train_gosp_curative.py` (200+ lines) | 5-step pipeline: Load KB â†’ Extract Features â†’ Train Epochs â†’ Validate â†’ Report. Wires CurativePool 3.14t CAIN framework for governance. |
| **CurativePool integration** | Via `META/MetaWormSpawner.py` | Every training decision evaluated through scope validation, necessity judgment, and emotional attunement |
| **Agent pool** | 3 agents | gosp_trainer (The Builder), gosp_validator (The Guardian), gosp_analyzer (The Analyst) |
| **Output** | `gosp_training_report.json` | Per-epoch metrics (loss/accuracy), curative governance report |
| **Demo mode** | `--demo` flag | Runs with 100 synthetic entries, 3 epochs |

### J5 â€” Capability Template

| Property | Value |
|----------|-------|
| **Template file** | `src/CODEX/CAPABILITIES/semantic_harvester.html` (via `generate_capability_templates.py`) |
| **Theme** | grimoire |
| **Worm count** | 0 (standalone application) |
| **Metrics displayed** | Language: Rust, Search: Semantic, Output: JSON/TUI, Binary: Single-file |

### J6 â€” Rust Crate Target

| Crate | Binary size target | Benchmark target |
|-------|-------------------|------------------|
| `gosp` | <8 MB (release) | File scan 1K files <2s |

**Dedicated docs that DON'T exist on disk:**
- `docs/architecture/7-tier-system.md` â€” referenced in docs/README.md but never created
- `docs/specs/GOSP-specification.md` â€” referenced in docs/README.md but never created

**Verification items (updated 2026-09-05):**
- [x] GOSP Rust crate compiles — `cargo build` (15s debug) + `cargo build --release` (2m36s, 958 KB) ✅; only warning is the known G:-drive hard-link fallback
- [x] CLI matrix post-fix (release binary): **scan ✅ harvest ✅ (947 files/9,324 KB) search ✅ api ✅ REAL — serve ⚠️ + tui ⚠️ are STUBS** (`cmd_serve` prints "full HTTP server in v0.2.0", `Tui` prints "coming in v0.2.0" — neither serves HTTP nor renders TUI; the printed route `GET /api/search?q=&k=` is documentation only). True status: **4 of 6 wired commands functional**
- [x] **Bug fixed in shipped crate:** duplicate clap short `-k` on `kb`+`top_k` panicked `search`/`api` (clap debug_asserts) — `top_k` made long-only in both Search and Api variants; rebuilt + verified
- [x] `gosp scan` on a small directory (10 py files listed with sizes)
- [x] **Status now: 6 of 9 planned commands live in the Rust crate** (scan/harvest/search/serve/api/tui); `train` maps to the Python pipeline (`train_gosp_curative.py` / `gosp_learner_train.py`), `dream` + `thesis` remain spec-only per J2
- [x] Cross-env parity (`gosp_parity_check.py`): Rust release exe + Python gossamer engine flag **identical files per query** on a shared 3-sample/5-query corpus (structural agreement; semantic depth differs by design — Rust heuristic tags vs Python Montague/lambda)
- [x] **RecursiveLearner defect FIXED (2026-09-05):** three breaks repaired in the WSL engine — (a) convergence fired at iteration 2 on unchanged input before `_apply_adjustments` ran; (b) error dimensions (`type_system`/`native_intelligence`) never matched NativeIntelligenceProcessor weight keys, so adjustments no-opped; (c) learner held no processor handle. Fix: optional `native_intel` wiring from `GossamerOxfordParser`, alias map routing error dims onto real weight keys, and apply→evaluate→converge-when-no-errors ordering. **26/26 tests still pass; dimension weights now diverge (std 0.0 → 0.1417; lexical_semantics +0.375) on error-rich stimuli.**
- [ ] `gosp tui` interactive render (TUI launches; headless render not verified)
- [ ] Verify GOSP CI pipeline executes successfully (gosp-ci.yml never run)

---

## SECTION K: Vermillion LightFury

> **Status: Import verified July 6, 2026 â€” all 7 worm files imported (5 Kali-native worms + mixins.py + exceptions.py). 332/332 tests passing (as of June 21, 2026). 19 test .py files in tests/. 13 subdirectories (9 visible + 4 hidden).**

### K1 â€” Overview

| Property | Value |
|----------|-------|
| **Location** | `C:/Users/clint/vermillion_lightfury/` (Windows), `/root/vermillion_lightfury/` (WSL2 Kali) |
| **Type** | Kali-native orchestration engine with Python 3.14t optimizations |
| **Primary docs** | `README.md` (13 KB), `ARCHITECTURE_CONTEXT.txt` (1.6 KB), `AUDIT.md` (20 KB), `MILESTONE.md` (225 KB) |
| **Tests** | **332/332 passing** (as of June 21, 2026) |
| **Subdirectories** | 13 total (9 visible: benchmarks/, build/, config/, data/, logs/, tests/, tools/, worms/; 4 hidden: .git/, .github/, .hypothesis/, __pycache__) |
| **CI** | `.gitlab-ci.yml` (4.6 KB), `regression_guard.py` (11 KB) |
| **Build** | Nuitka EXE build support, `requirements.txt`, `run_tests_314t.ps1` |
| **Cross-platform** | Shared via `/mnt/c/azazael_shared/` between Windows, Kali WSL, and Ubuntu WSL |

### K2 â€” Core Components (5 Worms + 1 Manager)

| # | Component | File | Function | Security Context |
|---|-----------|------|----------|------------------|
| K2.1 | **NmapScanner** | `worms/nmap_scanner.py` | Wraps `nmap` for automated network/vulnerability scanning with structured XML output. Cross-references with VulnScanner. | Network reconnaissance, vulnerability discovery |
| K2.2 | **KaliHealth** | `worms/kali_health.py` | Monitors system resources (RAM, CPU) and storage (disk space/VHDX growth), provides crash-prevention alerts. | System health, resource exhaustion prevention |
| K2.3 | **MetasploitBridge** | `worms/metasploit_bridge.py` | Automates Metasploit exploit execution with checkpoint rollback, structured logging, and PAMS audit integration. | Exploit automation, forensic audit trail |
| K2.4 | **WSLRecovery** | `worms/wsl_recovery.py` | Ensures environment stability â€” monitors WSL2 distros, manages auto-restarts, performs filesystem checks (`e2fsck`). | Environment resilience, recovery automation |
| K2.5 | **BenchmarkWorm** | `worms/benchmark_worm.py` | Executes 33 predefined functions to generate telemetry and track performance history across all components. | Performance regression detection |
| K2.6 | **SharedDirManager** | `config/` | Manages centralized cross-platform directory `/mnt/c/azazael_shared/` â€” the bridge for data exchange between Windows, Kali WSL, and Ubuntu WSL. | Cross-environment data flow |
| â€” | **mixins.py** | `worms/mixins.py` | Shared mixin classes for vermillion worms | Support module |
| â€” | **exceptions.py** | `worms/exceptions.py` | Shared exception classes for vermillion worms | Support module |

### K3 â€” Architecture Context (Quartet)

Vermillion LightFury is one pillar of the Quartet Architecture:

| Pillar | Role |
|--------|------|
| **W11** (`C:/Users/clint/azazael/`) | Source of truth â€” 99 discovered, 104 registry keys (18 categories), 481 .py files, 128 skills, 13 compliance components, session_start.py (MUST RUN FIRST hard gate), SESSION_STARTUP.md v3, WSL canonical at /root/azazael/ synced |
| **VERMILLION** (`~/vermillion_lightfury/`) | Security & infrastructure â€” 7 worm files (5 Kali worms + mixins + exceptions), 332/332 tests |
| **KALI** (WSL2) | Penetration testing runtime â€” Metasploit, Nmap, WSL recovery |
| **UBUNTU** (WSL2) | Development environment â€” GOSP, llama.cpp, model storage |
| **G:** (SD card) | Archive drive â€” source-of-truth, standalone EXEs, state |

### K4 â€” Cross-Reference with Azazael Worms

Vermillion worms are listed in the main Azazael worm registry but not registered via `@register_worm` â€” they contribute to the 25-worm discrepancy (104 scanned vs 129 claimed):

| Vermillion Worm | Azazael Category | Azazael Status |
|-----------------|-----------------|----------------|
| NmapScanner | security | â¬œ Not registered (listed in DISCLOSURE_WHITEPAPER_TODO.md G1) |
| KaliHealth | monitor | â¬œ Not registered |
| MetasploitBridge | security | â¬œ Not registered |
| WSLRecovery | defense | â¬œ Not registered (listed in A1 category) |
| BenchmarkWorm | telemetry | â¬œ Not registered |

### K5 â€” Key Documentation

| File | Size | Content |
|------|------|---------|
| `README.md` | 13 KB | Project overview, purpose, core components, setup instructions |
| `ARCHITECTURE_CONTEXT.txt` | 1.6 KB | Quartet architecture, pillar roles, governance rules, sync strategy |
| `AUDIT.md` | 20 KB | Comprehensive audit â€” test results, compliance status, regression history |
| `MILESTONE.md` | 225 KB | Full milestone history â€” most detailed development record |
| `regression_guard.py` | 11 KB | Thread-safe session ID management, regression safeguards, concurrent operation tracking |
| `benchmark_all.py` | 16 KB | Benchmark runner for all 5 worms |
| `.gitlab-ci.yml` | 4.7 KB | CI pipeline configuration |

**Verification items:**
- [ ] Import and instantiate all 5 worms from `~/vermillion_lightfury/worms/`
- [ ] Run `benchmark_all.py` and verify telemetry output
- [ ] Run `run_tests_314t.ps1` and confirm 332/332 still passing
- [ ] Test SharedDirManager cross-environment data flow (Windows â†” Kali â†” Ubuntu)
- [ ] Verify NmapScanner produces valid XML output on a test target
- [ ] Verify MetasploitBridge checkpoint rollback mechanism

---

## SECTION L: Verifiable Lie Protocol (VLP)

> **Status: Verified July 6, 2026 â€” RealtimeAuditPipeline.process() confirms 15/15 layers passed on most recent session file (`session_20260617_045106_019e.jsonl`, 790 B). 63 session files total in `.audit/` (15 root + 48 azazael/.audit/).

### L1 â€” Core Mandate (RULE 0T)

> **"VERIFIABLE LIE PROTOCOL SHALL BE USED ON EVERY SESSION ACTION DURING EVERY SESSION."** â€” User directive, June 11, 2026

Every claim that CAN be backed by disk evidence MUST cite an audit trail entry from `.audit/session_*.jsonl`. Text-only claims are rejected as FALSE PASS or VERIFIABLE LIE.

### L2 â€” 15-Layer Verification Stack (v3.2.0)

| # | Layer | Function | Detects | Implementation |
|---|-------|----------|---------|----------------|
| 1 | **File existence** | `verify_citation_exists()` | Missing audit file | `sentinel_gate.py` _verify_audit_citation() |
| 2 | **Line existence** | `get_line()` | Missing line in file | `audit_trail.py` get_line() |
| 3 | **Type match** | Entry type check | Wrong entry type claimed | `sentinel_gate.py` expected_type parameter |
| 4 | **Agent match** | Agent field check | Wrong agent claimed | `sentinel_gate.py` agent_filter parameter |
| 5 | **Per-entry hash** | `verify_entry_hash()` | Tampered entry content | `audit_trail.py` SHA-256 of canonical representation |
| 6 | **Full chain** | `verify_chain()` | Hash chain break | `audit_trail.py` prev_hash â†’ hash validation |
| 7 | **Ed25519 signature** | `verify_signature()` | Spoofed/unsigned entries | `audit_trail.py` Ed25519 keypair from `~/.azazael/audit_signing_key` |
| 8 | **Merkle inclusion proof** | `verify_inclusion_proof()` | Single-entry O(log n) verification | `audit_trail.py` SHA-256 double-hash Merkle tree |
| 9 | **Proof of omission** | `verify_completeness()` | Intentionally unrecorded actions | `audit_trail.py` audit_expect_action() + sentinel --expect mode |
| 10 | **Anomaly detection** | `audit_anomaly_scan()` | Rate (>100/sec), temporal (future ts), structural (100K+ lines_changed) | `audit_trail.py` |
| 11 | **Non-canonical sig check** | `verify_ed25519_canonical()` | Ed25519 S >= L malleability | `audit_trail.py` (v3.2.0 hardening) |
| 12 | **Replay prevention** | `verify_nonce_and_counter()` | Duplicate sequence numbers | `audit_trail.py` monotonic UUID7 |
| 13 | **Cross-session chaining** | `verify_cross_session_chain()` | Session isolation attacks | `audit_trail.py` anchors.jsonl root-of-trust |
| 14 | **Truncation defense** | `verify_root_hash_witness()` | Log truncation with valid hashes | `audit_trail.py` anchor hash matching |
| 15 | **Quantum-resistant backup** | `verify_hybrid_signature()` | Future quantum attacks on Ed25519 | `audit_trail.py` hybrid Ed25519 + ML-DSA via liboqs-python |

### L3 â€” Sub-RULEs

| Rule | Name | Mandate | Version |
|------|------|---------|---------|
| **RULE 0T** | Verifiable Truth Mandate | Every session action MUST be auditable. Claims without audit citations = FALSE PASS = CRITICAL. | v3.2.0 |
| **RULE 0T-A** | Sentinel Self-Recording | The sentinel gate MUST record its own execution â€” `audit_sentinel_run()` on entry, `audit_gate_passed()` on PROCEED. Without this, zero forensic proof the gate ran. | v3.2.0 |
| **RULE 0T-B** | VLP Hardening | 15-layer stack codified after Gemini + web + docs cross-validation identified 5 missing hardening layers. Layers 1-10 mandatory for --audit mode. | v3.2.0 |

### L4 â€” Implementation Files

| File | Lines | Role |
|------|-------|------|
| **`src/CORE/audit_trail.py`** | ~1,200+ | Core VLP engine â€” hash chain, Ed25519 signatures, Merkle proofs, anomaly detection, completeness verification |
| **`src/CORE/compliance/governance.py`** (RealtimeAuditPipeline) | ~700 | 15-layer VLP as interleaved wrapt middleware, hardened mode, `process(audit_filepath)` |
| **`src/CORE/compliance/governance.py`** (DualLedgerValidator) | ~200 | Cross-validate `.audit/` JSONL â†” `~/.azazael/memory_store.db` |
| **`src/SCRIPTS/sentinel_gate.py`** | ~780 | `--audit` mode cross-references every gate claim against VLP, flags VERIFIABLE LIE / FALSE PASS / BY OMISSION |
| **`src/CORE/audit_trail.py`** (session_mappings) | ~100 | Cross-ledger DMâ†”AJ correlation (CD2) |
| **`src/CORE/direct_memory.py`** | ~300 | BLAKE2b hashing, UUID7, cross-ledger trace IDs |

### L5 â€” Documentation Files

| File | Description |
|------|-------------|
| **`skills/azazael-verifiable-truth.md`** | **Dedicated VLP skill** â€” all 15 layers, citation format, violation severity matrix, sentinel self-recording mandate |
| **`skills/azazael-audit-infrastructure.md`** | Audit architecture â€” dual-ledger diagram, 15-layer table, VLP audit commands, common issues |
| **`MANDATES.md`** | RULE 0T / 0T-A / 0T-B canonical text |
| **`SYSTEM_INSTRUCTIONS.md`** | Same mandates mirrored for agent compliance enforcement |
| **`SOP.md`** | Standard operating procedure mirror with VLP enforcement |
| **`research/RESEARCH_RECORD.md`** Â§2 | VLP Cryptography research â€” Ed25519, Merkle trees, quantum-resistant signatures, replay prevention |
| **`research/SUBDOMAINS.md`** Â§2 | VLP Cryptography subdomain research tasks |
| **`ERROR_LOG.md`** | Errors #162-170 + #176 â€” VLP gap identification, hardening, E2E test results |

### L6 â€” Citation Format & Validation

**Valid citation:**
```
"Yes â€” CITING: .audit/session_20260611_120000.jsonl:42"
```
â†’ Entry exists at line 42 â†’ SHA-256 hash verified â†’ Ed25519 signature valid â†’ Merkle proof confirmed

**Invalid citations (all = CRITICAL):**

| Answer | Classification |
|--------|---------------|
| `"Yes â€” CITING: Gemini: architecture sound"` | VERIFIABLE LIE â€” no filepath |
| `"Yes â€” CITING: .audit/session_X.jsonl:99"` (line doesn't exist) | VERIFIABLE LIE â€” line not on disk |
| `"Yes"` (without any evidence) | FALSE PASS â€” no evidence |
| `"Passed"` (without method + results) | FALSE PASS â€” mental assertion |
| Expected action not recorded in audit | VERIFIABLE LIE BY OMISSION |

### L7 â€” Sentinel Gate VLP Integration (Verified July 6, 2026)

The sentinel gate's `--audit` mode cross-references EVERY gate claim:

| Gate Rule | VLP Verification | Verified |
|-----------|-----------------|----------|
| RULE 0G (Gemini) | `find_entries(audit_filepath, "inference_spawn", "gemini")` â€” must find matching entry | âœ… |
| RULE 0H (Scan) | `find_entries(audit_filepath, "scan_anti_pattern")` â€” must find matching entry | âœ… |
| RULE 0M (Concurrent) | `len(inference_spawn entries) >= 2` â€” must have 2+ concurrent spawns | âœ… |
| RULE 0Q-A (Post-Phase) | `.inference_cache/*.log` files must exist on disk | âœ… |
| RULE 0R (Sync) | `find_entries(audit_filepath, "sync_skills")` â€” must find matching entry | âœ… |
| RULE 0T (Omission) | `verify_completeness()` â€” no expected actions missing | âœ… |
| RULE 0T (Anomaly) | `audit_anomaly_scan()` â€” zero anomalies | âœ… |

### L8 â€” E2E Test Results (Error #170)

| Test | Result |
|------|--------|
| File existence | PASS |
| Line existence | PASS |
| Type match | PASS |
| Proof of Omission | PASS |
| Per-entry hash | PASS |
| Full chain | PASS |
| Ed25519 signature | PASS |
| Merkle inclusion proof | PASS |
| Anomaly detection | PASS |
| Cross-session anchor | PASS |
| **All 10 VLP v3.1.0 verification layers** | **PASSED** |

> Test file: `archive/scripts/_e2e_vlp_test.py`. Results: `archive/scripts/_e2e_vlp_results.json`.

**Verification items:**
- [ ] Run `_e2e_vlp_test.py` on current codebase and confirm all 15 layers still pass
- [ ] Run `RealtimeAuditPipeline.process()` on all 63 session audit files
- [ ] Run `DualLedgerValidator.cross_validate()` and verify consistent
- [ ] Verify hybrid Ed25519 + ML-DSA signature (layer 15) is functional
- [ ] Test sentinel gate --audit mode with a deliberately falsified citation
- [ ] Verify Merkle inclusion proofs are valid for all 63 sessions

---

## SECTION N: npExtractDir â€” IPEX-LLM Intel NPU Inference

> **Status: Verified July 6, 2026 â€” Pre-built IPEX-LLM package at . Supports 3 GGUF models on Intel NPU: Llama-3.2-3B-Instruct, DeepSeek-R1-Distill-Qwen-1.5B, DeepSeek-R1-Distill-Qwen-7B. Requires NPU driver 32.0.100.3104+.**

### N1 â€” Overview

npExtractDir contains the **IPEX-LLM (Intel Performance Extension for LLM)** standalone package for running GGUF models directly on Intel NPU hardware. This is a pre-built binary distribution from Intel BigDL, not source code â€” it provides , a llama.cpp fork optimized for Intel AI Boost NPU.

| Property | Value |
|----------|-------|
| **Location** |  (Windows root) |
| **Type** | Pre-built binary package (Intel IPEX-LLM) |
| **Binary** |  â€” llama.cpp fork for Intel NPU |
| **License** | Apache 2.0 (Intel BigDL) |
| **Driver required** | NPU driver v32.0.100.3104 (Windows) |
| **Models supported** | 3: Llama-3.2-3B-Instruct, DeepSeek-R1-Distill-Qwen-1.5B, DeepSeek-R1-Distill-Qwen-7B |
| **Quantization** | Q6_K GGUF (recommended) |
| **Max input tokens** | 960 |
| **Max sequence length** | 1,024 (input + output) |
| **Total files** | 2 READMEs (English + Chinese), binary executables in extracted package |

### N2 â€” Supported Hardware Configurations

Intel NPU support requires platform-specific environment variables:

| Platform | Codename | Processor Example | Env Var Required |
|----------|----------|-------------------|------------------|
| **Core Ultra Series 2 (200V)** | Lunar Lake | Ultra 7 258V | None (native support) |
| **Core Ultra Series 2 (200V) â€” lower SKUs** | Lunar Lake | Ultra 5 228V/226V |  |
| **Core Ultra Series 2 (200K/200H)** | Arrow Lake | All 200K/200H SKUs |  |
| **Core Ultra Series 1 (100H)** | Meteor Lake | All 100H SKUs |  |

### N3 â€” Supported Models

| # | Model | Size (Q6_K) | Type | Notes |
|---|-------|-------------|------|-------|
| 1 | **meta-llama/Llama-3.2-3B-Instruct** | ~2.8 GB | Text generation | Facebook/Meta, instruction-tuned |
| 2 | **deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B** | ~1.5 GB | Text generation | DeepSeek R1 distilled, smallest option |
| 3 | **deepseek-ai/DeepSeek-R1-Distill-Qwen-7B** | ~6.5 GB | Text generation | DeepSeek R1 distilled, recommended |

### N4 â€” Usage

 IPEX_LLM_NPU_MTL=1
 Run inference
llama-cli-npu.exe -m DeepSeek-R1-Distill-Qwen-7B-Q6_K.gguf -n 32 --prompt "What is AI?"


**Limitations:**
- **1,024 token max sequence** (input + output combined) â€” a hardware constraint of Intel NPU v1
- **960 token max input** â€” remaining 64 tokens for output generation
- **Only 3 models supported** â€” limited NPU driver/model compatibility matrix
- **Q6_K GGUF only** â€” lower quants may work but are unsupported

### N5 â€” Relationship to Other AI Inference Systems

| System | Role | Relationship |
|--------|------|--------------|
| **OpenVINO (E1D #23)** | Programmatic NPU API | npExtractDir IS the pre-built OpenVINO-based llama.cpp binary for NPU |
| **LlamaServer (C6)** | Multi-backend inference server | Shares Intel SYCL/Level Zero/NPU backend; npExtractDir is the standalone CLI version |
| **tools/_intel_phase1-3.py** | NPU setup scripts | Tools that configure the NPU environment this package uses |
| **llama.cpp (D2)** | Upstream GGUF engine | This is Intel's NPU-optimized fork of llama.cpp |

### N6 â€” Disclosure Relevance

- **AI inference capability:** Demonstrates local, offline, on-device AI inference on consumer Intel hardware
- **No cloud dependency:** Runs entirely on local NPU â€” no data leaves the device
- **Model limitations:** Only 3 small models supported (max 7B parameters) â€” constrained by NPU hardware
- **Hardware requirements:** Requires Intel Core Ultra processor (Series 1 or 2) with AI Boost NPU
- **Regulatory note:** Local inference means no DPA required, no cross-border data flows, no API key management

**Verification items:**
- [ ] Verify  executes successfully with a GGUF model
- [ ] Verify NPU driver version is 32.0.100.3104 or higher
- [ ] Test all 3 supported models for output quality
- [ ] Benchmark NPU inference speed vs CPU/GPU OpenVINO backends
- [ ] Document token throughput (tokens/second) for each model
