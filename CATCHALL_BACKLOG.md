# Catch-All Refactoring Backlog (graphify-prioritized)

> Generated 2026-08-29 17:28 UTC · source: `scripts/check_no_catch_alls.py` + `graphify-out/graph.json`
>
> **Budget: 1241 over-broad catch-alls across 293 files** in `src/`+`scripts/` (guard `MAX_BROAD=1241`; CI `catchall-guard.yml` caps growth). Refactoring to specific handlers lowers the budget via `--max-broad`.
>
> **Checkpoint 2026-08-29 (live): 1091 broad / 0 bare.** All 6 P0 hubs resolved to `# noqa: BLE001` allow-markers (or narrowed) — `weakness_testing.py` (27), `OS_CONGRUENCY.py` (25), `dashboard.py` (25), `inference/providers.py` (21), `expansion/learning.py` (18), `Agent.py` (18), `CLUSTERWORMS.py` (17), `REVERSE_TOOLS.py` (15). These are deliberate per-handler judgments: weakness-harness capture, best-effort telemetry/winreg, non-fatal dashboard subsystems, provider-call degradation, task-boundary/PAMS records, cluster dynamic-resolution fallthrough + worm-execution error reporting, and install fall-through / tool-analysis isolation. `OS_CONGRUENCY.py` got 4 narrowed to specific types (`OSError`, `ValueError`, `subprocess.SubprocessError`). Guard passes (1091 ≤ 1241).

## How priority is ranked

| Factor | Meaning |
|---|---|
| **catch-all count** | handlers to fix in the file (the work) |
| **graph edge-centrality** | edges in the graphify graph touching this file (blast radius: how many other nodes the file is wired to) |
| **composite score** | `count*10 + log2(edges+1)`, capped — a big count *and* a hub ranks highest |

High-count, high-centrality files yield the most refactor value *and* the most test fallout — prioritize them, triage each handler to a specific exception or add an allowed marker if the broad catch is intentional.

## Priority tiers

### **P0 — 15+ handlers** (dense, likely hubs)

| Catch-alls | Graph-edges | Score | File |
|---|---:|---:|---|
| 27 | 143 | 277.2 | `src/ORCHESTRATION/ml_platforms/improvements/weakness_testing.py` |
| 25 | 94 | 256.6 | `src/CORE/WORMS/OS_CONGRUENCY.py` |
| 25 | 93 | 256.6 | `src/CORE/dashboard.py` |
| 21 | 306 | 218.3 | `src/CORE/inference/providers.py` |
| 18 | 212 | 187.7 | `src/CORE/WORMS/expansion/learning.py` |
| 18 | 132 | 187.1 | `src/CORE/Agent.py` |
| 17 | 177 | 177.5 | `src/CORE/WORMS/CLUSTERWORMS.py` |
| 16 | 113 | 166.8 | `src/CODEX/CODEX_Studio.py` |
| 15 | 68 | 156.1 | `src/CORE/WORMS/REVERSE_TOOLS.py` |

### **P1 — 10–14 handlers**

| Catch-alls | Graph-edges | Score | File |
|---|---:|---:|---|
| 13 | 59 | 135.9 | `src/REAL_FRAMEWORK_TEST.py` |
| 12 | 165 | 127.4 | `src/AZAZAEL_Inference_Studio.py` |
| 12 | 127 | 127.0 | `src/CORE/compliance/pre_action_gate.py` |
| 12 | 60 | 125.9 | `src/CORE/WORMS/BINARY_ANALYSIS_PARSE.py` |
| 12 | 59 | 125.9 | `src/AZAZAEL_TOOLKIT/REAL_FRAMEWORK_TEST.py` |
| 12 | 42 | 125.4 | `src/CORE/WORMS/BINARY_ANALYSIS_TOOLS.py` |
| 11 | 94 | 116.6 | `src/CORE/MemoryBus.py` |
| 11 | 57 | 115.9 | `src/ORCHESTRATION/scripts/test_enhancements.py` |
| 10 | 127 | 107.0 | `src/ORCHESTRATION/scripts/azazael_cli.py` |
| 10 | 102 | 106.7 | `src/CORE/worm_registry.py` |
| 10 | 36 | 105.2 | `src/ORCHESTRATION/TEST/ECOSYSTEM_TEST.py` |
| 10 | 5 | 102.6 | `src/ORCHESTRATION/ml_platforms/run_qanalysis_multi.py` |
| 10 | 1 | 101.0 | `src/ORCHESTRATION/ml_platforms/run_qanalysis.py` |

### **P2 — 6–9 handlers**

| Catch-alls | Graph-edges | Score | File |
|---|---:|---:|---|
| 9 | 159 | 97.3 | `src/CORE/WORMS/NATURE_CLUSTERS.py` |
| 9 | 143 | 97.2 | `src/ORCHESTRATION/ml_platforms/universal_converter.py` |
| 9 | 117 | 96.9 | `src/UTILITIES/TARBABY/tarbaby_enhanced.py` |
| 9 | 102 | 96.7 | `src/META/TRIMZ.py` |
| 9 | 76 | 96.3 | `src/CORE/compliance/heuristic_recorder.py` |
| 9 | 75 | 96.2 | `src/CORE/WORMS/WORMZ_ML.py` |
| 9 | 53 | 95.8 | `src/memory_status.py` |
| 9 | 49 | 95.6 | `src/ORCHESTRATION/TotalFusion.py` |
| 9 | 46 | 95.6 | `src/CORE/PamsRecorder.py` |
| 9 | 21 | 94.5 | `scripts/check_tooling.py` |
| 9 | 17 | 94.2 | `src/CORE/inference/cloud_tab.py` |
| 8 | 157 | 87.3 | `src/CORE/audit_trail.py` |
| 8 | 156 | 87.3 | `src/CORE/local_memory.py` |
| 8 | 109 | 86.8 | `src/TRIMZ.py` |
| 8 | 94 | 86.6 | `src/CORE/sb3_agent.py` |
| 8 | 89 | 86.5 | `src/CORE/WORMS/PARALLEL_INFERENCE_WORM.py` |
| 8 | 85 | 86.4 | `src/CORE/compliance/scanner.py` |
| 8 | 74 | 86.2 | `src/CORE/WORMS/SMARTDISK.py` |
| 8 | 72 | 86.2 | `src/METRICZ.py` |
| 8 | 69 | 86.1 | `src/META/METAWORMS.py` |
| 8 | 69 | 86.1 | `src/META/METRICZ.py` |
| 8 | 61 | 86.0 | `src/CORE/WORMS/expansion/session_state.py` |
| 8 | 61 | 86.0 | `src/HYDRA/hydra_launcher.py` |
| 8 | 53 | 85.8 | `src/CORE/WORMS/expansion/container.py` |
| 8 | 45 | 85.5 | `src/CORE/STRESS_TEST.py` |
| 8 | 43 | 85.5 | `src/eve_unleashed/cli.py` |
| 8 | 39 | 85.3 | `src/CORE/health_server.py` |
| 7 | 115 | 76.9 | `src/CORE/postgres_memory.py` |
| 7 | 108 | 76.8 | `src/eve_unleashed/engine.py` |
| 7 | 107 | 76.8 | `src/SCRIPTS/sentinel_gate.py` |
| 7 | 93 | 76.6 | `src/CORE/NeuralPipeline.py` |
| 7 | 90 | 76.5 | `src/CORE/AgentPool.py` |
| 7 | 89 | 76.5 | `src/tests/test_ecosystem.py` |
| 7 | 88 | 76.5 | `src/CODEX/CORE/AUTO_DOWNLOADER.py` |
| 7 | 80 | 76.3 | `src/META/METAWORMS_ENRICHED.py` |
| 7 | 71 | 76.2 | `src/CORE/WORMS/expansion/db_monitor.py` |
| 7 | 33 | 75.1 | `src/CORE/doctor.py` |
| 7 | 33 | 75.1 | `src/CORE/WORMS/DIAGNOSTIC_WORM.py` |
| 7 | 32 | 75.0 | `src/CORE/data_retention.py` |
| 7 | 27 | 74.8 | `src/CORE/backup.py` |
| 6 | 211 | 67.7 | `src/CORE/freethreading.py` |
| 6 | 170 | 67.4 | `src/session_memory.py` |
| 6 | 101 | 66.7 | `src/CORE/WORMS/expansion/evolution.py` |
| 6 | 98 | 66.6 | `src/CORE/WORMS/CONCURRENCY.py` |
| 6 | 96 | 66.6 | `src/MISSING_TOOLS.py` |
| 6 | 83 | 66.4 | `src/CORE/compliance/orchestrator.py` |
| 6 | 79 | 66.3 | `src/CORE/WORMS/CLUSTER_INSPECTOR.py` |
| 6 | 72 | 66.2 | `src/CORE/inference_pool.py` |
| 6 | 68 | 66.1 | `src/CORE/WORMS/expansion/meta_cognition.py` |
| 6 | 66 | 66.1 | `src/ERRORZ.py` |
| 6 | 64 | 66.0 | `src/performance_monitor.py` |
| 6 | 60 | 65.9 | `src/CORE/WORMS/expansion/learning_grpo.py` |
| 6 | 59 | 65.9 | `src/META/ERRORZ.py` |
| 6 | 55 | 65.8 | `src/INTERPRETERS/rust_runner.py` |
| 6 | 54 | 65.8 | `src/INTERPRETERS/go_runner.py` |
| 6 | 53 | 65.8 | `src/ORCHESTRATION/ml_platforms/improvements/onnx_integration.py` |
| 6 | 42 | 65.4 | `src/ORCHESTRATION/ml_platforms/verify_moe.py` |
| 6 | 38 | 65.3 | `src/CLI/azazael_cli.py` |
| 6 | 32 | 65.0 | `src/CORE/notifier.py` |
| 6 | 4 | 62.3 | `scripts/update_header_and_render.py` |

### **P3 — 2–5 handlers**

| Catch-alls | Graph-edges | Score | File |
|---|---:|---:|---|
| 5 | 108 | 56.8 | `src/CORE/WORMS/expansion/dreaming.py` |
| 5 | 107 | 56.8 | `src/CORE/WORMS/METACLUSTER.py` |
| 5 | 90 | 56.5 | `src/CORE/WORMS/expansion/learning_pipeline.py` |
| 5 | 90 | 56.5 | `src/UTILITIES/KLINK/klink.py` |
| 5 | 88 | 56.5 | `src/ORCHESTRATION/scripts/comprehensive_analysis.py` |
| 5 | 84 | 56.4 | `src/HYDRAMETA.py` |
| 5 | 84 | 56.4 | `src/META/HYDRAMETA.py` |
| 5 | 54 | 55.8 | `src/CORE/WORMS/expansion/backup.py` |
| 5 | 52 | 55.7 | `src/CODEX/VIDEOS/generate_dashboard_video.py` |
| 5 | 44 | 55.5 | `src/CORE/sentinel_enforcer.py` |
| 5 | 39 | 55.3 | `src/HYDRA/hydra_protocols.py` |
| 5 | 33 | 55.1 | `src/HYDRA/ml_platforms/harness.py` |
| 5 | 33 | 55.1 | `src/ORCHESTRATION/ml_platforms/harness.py` |
| 5 | 26 | 54.8 | `scripts/build_all_concurrent.py` |
| 5 | 18 | 54.2 | `src/CORE/WORMS/OMNI_WORM.py` |
| 5 | 3 | 52.0 | `src/ORCHESTRATION/ml_platforms/run_qanalysis_full.py` |
| 4 | 120 | 46.9 | `src/CORE/inference/parallel.py` |
| 4 | 108 | 46.8 | `src/CORE/WORMS/expansion/scheduling.py` |
| 4 | 104 | 46.7 | `src/CORE/web_dashboard.py` |
| 4 | 102 | 46.7 | `src/CORE/workflow.py` |
| 4 | 91 | 46.5 | `src/ORCHESTRATION/SystemManagerGUI.py` |
| 4 | 89 | 46.5 | `src/ORCHESTRATION/SystemManager.py` |
| 4 | 84 | 46.4 | `src/METAWORMS_ENRICHED.py` |
| 4 | 76 | 46.3 | `src/CORE/WORMS/SYSTEMZ_ML.py` |
| 4 | 67 | 46.1 | `src/HYDRAMETA_UV.py` |
| 4 | 66 | 46.1 | `src/META/HYDRAMETA_UV.py` |
| 4 | 59 | 45.9 | `src/CORE/azazael_ctl.py` |
| 4 | 57 | 45.9 | `src/CORE/WORMS/expansion/communication.py` |
| 4 | 55 | 45.8 | `src/CORE/WORMS/expansion/security.py` |
| 4 | 54 | 45.8 | `src/CORE/cd2_verifier.py` |
| 4 | 54 | 45.8 | `src/SCRIPTS/environ_updater.py` |
| 4 | 45 | 45.5 | `src/DAEMONS/parallax_validator.py` |
| 4 | 44 | 45.5 | `src/CORE/agent_registry.py` |
| 4 | 35 | 45.2 | `src/CORE/WORMS/CODEX_TOOLS.py` |
| 4 | 34 | 45.1 | `src/CORE/WORMS/WORM_SELECTOR.py` |
| 4 | 33 | 45.1 | `src/eve_unleashed/core.py` |
| 4 | 31 | 45.0 | `src/UTILITIES/TERENCE/TERENCE.py` |
| 4 | 28 | 44.9 | `src/CORE/ERROR_SCAN_WORM.py` |
| 4 | 26 | 44.8 | `src/CORE/WORMS/ERROR_SCAN_WORM.py` |
| 4 | 22 | 44.5 | `src/AZAZAEL_TOOLKIT/COMPREHENSIVE_FIX.py` |
| 4 | 21 | 44.5 | `src/TOOLS/COMPREHENSIVE_FIX.py` |
| 4 | 15 | 44.0 | `src/CORE/NODE.py` |
| 4 | 14 | 43.9 | `src/ORCHESTRATION/scripts/run_tests.py` |
| 4 | 6 | 42.8 | `src/CORE/WORMS/HEALING_WORM.py` |
| 3 | 98 | 36.6 | `src/CORE/WORMS/WORMZ.py` |
| 3 | 97 | 36.6 | `src/CORE/direct_memory.py` |
| 3 | 91 | 36.5 | `src/CORE/compliance/governance.py` |
| 3 | 68 | 36.1 | `src/CORE/FREETHREAD_UPGRADE.py` |
| 3 | 59 | 35.9 | `src/TOOLS/debug_runner.py` |
| 3 | 57 | 35.9 | `src/CORE/inference/threaded.py` |
| 3 | 56 | 35.8 | `src/CORE/inference/api_client.py` |
| 3 | 52 | 35.7 | `src/CORE/cd4_pipeline.py` |
| 3 | 52 | 35.7 | `src/CORE/WORMS/CROSS_NATURE_ROUTER.py` |
| 3 | 52 | 35.7 | `src/CORE/WORMS/DEPENDZ.py` |
| 3 | 51 | 35.7 | `src/CORE/WORMS/INFERENCE_SUBSCRIBER.py` |
| 3 | 50 | 35.7 | `src/CORE/inference/sequential_analyzer.py` |
| 3 | 50 | 35.7 | `src/CORE/WORMS/expansion/migration.py` |
| 3 | 47 | 35.6 | `src/CORE/circuit_breaker.py` |
| 3 | 44 | 35.5 | `src/AzazaelDynamicLogger.py` |
| 3 | 44 | 35.5 | `src/AZAZAEL_TOOLKIT/AzazaelDynamicLogger.py` |
| 3 | 44 | 35.5 | `src/TOOLS/AzazaelDynamicLogger.py` |
| 3 | 41 | 35.4 | `src/ORCHESTRATION/hydra_bridge.py` |
| 3 | 37 | 35.2 | `src/SCRIPTS/sync_skills.py` |
| 3 | 34 | 35.1 | `src/HEALTHZ.py` |
| 3 | 34 | 35.1 | `src/CORE/WORMS/expansion/race_detector.py` |
| 3 | 34 | 35.1 | `src/ORCHESTRATION/FusionHealer.py` |
| 3 | 31 | 35.0 | `src/META/HEALTHZ.py` |
| 3 | 30 | 35.0 | `src/CORE/PamsBusBridge.py` |
| 3 | 29 | 34.9 | `src/SCRIPTS/gate_bash.py` |
| 3 | 28 | 34.9 | `src/CORE/startup_warm.py` |
| 3 | 26 | 34.8 | `src/INTERPRETERS/__init__.py` |
| 3 | 19 | 34.3 | `src/SCRIPTS/gate_str_replace.py` |
| 3 | 15 | 34.0 | `src/CODEX/TESTING/PERFORMANCE/test_performance.py` |
| 3 | 12 | 33.7 | `src/CORE/inference/inference_cache.py` |
| 2 | 167 | 27.4 | `src/ORCHESTRATION/HORUS.py` |
| 2 | 130 | 27.0 | `src/CORE/metrics.py` |
| 2 | 122 | 26.9 | `src/ORCHESTRATION/ADLP_SystemTools.py` |
| 2 | 102 | 26.7 | `src/ORCHESTRATION/scripts/bat_analysis.py` |
| 2 | 101 | 26.7 | `src/HYDRA/ml_platforms/config.py` |
| 2 | 101 | 26.7 | `src/ORCHESTRATION/ml_platforms/config.py` |
| 2 | 98 | 26.6 | `src/ORCHESTRATION/scripts/validate_docs.py` |
| 2 | 96 | 26.6 | `src/ORCHESTRATION/TARBABY.py` |
| 2 | 95 | 26.6 | `src/UTILITIES/TARBABY/TARBABY.py` |
| 2 | 88 | 26.5 | `src/CORE/codebuff_tracker.py` |
| 2 | 83 | 26.4 | `src/CORE/inference/hyper_optimizer.py` |
| 2 | 77 | 26.3 | `src/UTILITIES/TERENCE/terence_enhanced.py` |
| 2 | 63 | 26.0 | `src/ORCHESTRATION/scripts/complete_module_analysis.py` |
| 2 | 61 | 26.0 | `src/META/MetaWormSpawner.py` |
| 2 | 61 | 26.0 | `src/ORCHESTRATION/SelfImprovingGUI.py` |
| 2 | 60 | 25.9 | `src/CORE/FreeThreadedAgent.py` |
| 2 | 56 | 25.8 | `src/TELEMETRYZ.py` |
| 2 | 51 | 25.7 | `src/CORE/WORMS/expansion/telemetry.py` |
| 2 | 51 | 25.7 | `src/META/TELEMETRYZ.py` |
| 2 | 50 | 25.7 | `src/CORE/compliance/validating.py` |
| 2 | 50 | 25.7 | `src/CORE/WORMS/expansion/visualization.py` |
| 2 | 48 | 25.6 | `scripts/db_health.py` |
| 2 | 47 | 25.6 | `src/CORE/WORMS/expansion/error_recovery.py` |
| 2 | 44 | 25.5 | `src/ORCHESTRATION/ml_platforms/install_manager.py` |
| 2 | 43 | 25.5 | `src/CORE/WORMS/VIDEO_ANALYZER_WORM.py` |
| 2 | 43 | 25.5 | `src/CORE/WORMS/expansion/config.py` |
| 2 | 41 | 25.4 | `src/ORCHESTRATION/ECOSYSTEM_OPTIMIZER.py` |
| 2 | 38 | 25.3 | `src/CORE/WORMS/CAIN_WORM.py` |
| 2 | 34 | 25.1 | `src/CODEX/VIDEOS/compress_video.py` |
| 2 | 32 | 25.0 | `src/CORE/azazael_logging.py` |
| 2 | 32 | 25.0 | `src/CORE/WORMS/NETWORXZ.py` |
| 2 | 32 | 25.0 | `src/ORCHESTRATION/HYDRA_ANALYZER.py` |
| 2 | 31 | 25.0 | `scripts/scenario_a_full_pipeline.py` |
| 2 | 30 | 25.0 | `scripts/pre_build_check.py` |
| 2 | 29 | 24.9 | `src/CORE/graph_artifacts.py` |
| 2 | 29 | 24.9 | `src/CORE/WORMS/CLOCKZ.py` |
| 2 | 26 | 24.8 | `src/CORE/audit_repair.py` |
| 2 | 25 | 24.7 | `src/CORE/cli_memory.py` |
| 2 | 24 | 24.6 | `scripts/scenario_b_compressed_pipeline.py` |
| 2 | 23 | 24.6 | `src/DAEMONS/install_parallax_startup.py` |
| 2 | 22 | 24.5 | `src/ECOSYSTEM_HEALTH_CHECK.py` |
| 2 | 22 | 24.5 | `scripts/scenario_c_distillation_pipeline.py` |
| 2 | 21 | 24.5 | `scripts/check_314t_compat.py` |
| 2 | 20 | 24.4 | `src/CORE/WORMS/MORPHING_WORM_V2.py` |
| 2 | 20 | 24.4 | `src/ORCHESTRATION/HORUS_LIVE_MONITOR.py` |
| 2 | 19 | 24.3 | `src/SCRIPTS/gate_write_file.py` |
| 2 | 15 | 24.0 | `src/CODEX/VIDEOS/progress_bar.py` |
| 2 | 11 | 23.6 | `src/CORE/rollback.py` |
| 2 | 11 | 23.6 | `src/SCRIPTS/gated_edit.py` |
| 2 | 10 | 23.5 | `src/ORCHESTRATION/ml_platforms/lm_studio_integration.py` |
| 2 | 8 | 23.2 | `src/CODEX/POPUPS/POPUP_RICH.py` |
| 2 | 5 | 22.6 | `src/ORCHESTRATION/scripts/generate_docstrings.py` |
| 2 | 5 | 22.6 | `scripts/generate_dashboard.py` |
| 2 | 3 | 22.0 | `scripts/run_training_orchestrator.py` |
| 2 | 2 | 21.6 | `src/HYDRA/ml_platforms/PERMANENT_LOAD.py` |
| 2 | 2 | 21.6 | `src/SCRIPTS/session_start.py` |
| 2 | 1 | 21.0 | `src/CODEX/VIDEOS/create_scrolling_video.py` |

### **P4 — 1 handler**

| Catch-alls | Graph-edges | Score | File |
|---|---:|---:|---|
| 1 | 97 | 16.6 | `src/ORCHESTRATION/scripts/azazael_wsa.py` |
| 1 | 88 | 16.5 | `src/CORE/config.py` |
| 1 | 79 | 16.3 | `src/DOCKERZ.py` |
| 1 | 78 | 16.3 | `src/ORCHESTRATION/HYDRA.py` |
| 1 | 77 | 16.3 | `src/CORE/WORMS/dead_letter_queue.py` |
| 1 | 76 | 16.3 | `src/META/DOCKERZ.py` |
| 1 | 70 | 16.1 | `src/CORE/WORMS/BINARY_ANALYSIS.py` |
| 1 | 67 | 16.1 | `src/CORE/compliance/state_machine.py` |
| 1 | 64 | 16.0 | `src/UTILITIES/PERSEPHONE/persephone.py` |
| 1 | 62 | 16.0 | `src/UVZ.py` |
| 1 | 62 | 16.0 | `src/META/UVZ.py` |
| 1 | 57 | 15.9 | `src/ORCHESTRATION/ml_platforms/health_monitor.py` |
| 1 | 57 | 15.9 | `scripts/sync_g_drive.py` |
| 1 | 56 | 15.8 | `src/ORCHESTRATION/ADLP_MLOrchestrator.py` |
| 1 | 53 | 15.8 | `src/CORE/inference/nim_client.py` |
| 1 | 52 | 15.7 | `src/CORE/WORMS/expansion/profiling.py` |
| 1 | 51 | 15.7 | `scripts/sync_all.py` |
| 1 | 50 | 15.7 | `src/CORE/cli_crossref.py` |
| 1 | 47 | 15.6 | `src/ORCHESTRATION/ml_platforms/improvements/ml_integration.py` |
| 1 | 45 | 15.5 | `src/CORE/inference/query_loop.py` |
| 1 | 45 | 15.5 | `scripts/desktop_projects_reference_check.py` |
| 1 | 44 | 15.5 | `src/CORE/compliance/telemetry.py` |
| 1 | 44 | 15.5 | `src/ORCHESTRATION/ADLP_FusionCore.py` |
| 1 | 44 | 15.5 | `src/TOOLS/PythonSystemMapper.py` |
| 1 | 44 | 15.5 | `src/UTILITIES/PERSEPHONE/lib/sync_manager.py` |
| 1 | 43 | 15.5 | `src/CORE/WORMS/MORPHING_WORM.py` |
| 1 | 43 | 15.5 | `src/TOOLS/PythonSystemMapper_Full.py` |
| 1 | 39 | 15.3 | `scripts/modernize_types.py` |
| 1 | 38 | 15.3 | `src/CORE/cd3_exporter.py` |
| 1 | 38 | 15.3 | `src/CORE/WORMS/SYSTEMZ.py` |
| 1 | 34 | 15.1 | `src/CODEX/VIDEOS/create_dual_pane_popup.py` |
| 1 | 33 | 15.1 | `src/CORE/WORMS/METAZ.py` |
| 1 | 32 | 15.0 | `src/CODEX/VIDEOS/create_azazael_educational_video.py` |
| 1 | 31 | 15.0 | `src/chain_of_action.py` |
| 1 | 27 | 14.8 | `src/CORE/worm_registry_cache.py` |
| 1 | 27 | 14.8 | `scripts/reencode_large_videos.py` |
| 1 | 26 | 14.8 | `src/CORE/WORM_FLEET.py` |
| 1 | 26 | 14.8 | `src/ORCHESTRATION/ml_platforms/lm_studio_server.py` |
| 1 | 25 | 14.7 | `src/CODEX/build_bcc_cain_alternate.py` |
| 1 | 25 | 14.7 | `src/SCRIPTS/auto_sync.py` |
| 1 | 24 | 14.6 | `src/CORE/WORMS/WORM_FLEET.py` |
| 1 | 22 | 14.5 | `src/CORE/cli_audit.py` |
| 1 | 21 | 14.5 | `src/UTILITIES/AzazaelDynamicLogger.py` |
| 1 | 21 | 14.5 | `scripts/audit_html.py` |
| 1 | 20 | 14.4 | `scripts/benchmark_wal_docker.py` |
| 1 | 19 | 14.3 | `src/eve_unleashed/streaming.py` |
| 1 | 16 | 14.1 | `src/CODEX/CORE/CAIN_ANALYZER.py` |
| 1 | 16 | 14.1 | `src/HYDRA/ml_test.py` |
| 1 | 16 | 14.1 | `src/SCRIPTS/run_test_generate_telemetry.py` |
| 1 | 11 | 13.6 | `src/CORE/WORMS/OMNI_WORM_V2.py` |
| 1 | 11 | 13.6 | `src/DAEMONS/check_parallax.py` |
| 1 | 11 | 13.6 | `src/SCRIPTS/test_rule_0zf_integration.py` |
| 1 | 11 | 13.6 | `scripts/autoflake_314t.py` |
| 1 | 10 | 13.5 | `src/CORE/inference/bus_utils.py` |
| 1 | 10 | 13.5 | `src/ORCHESTRATION/scripts/improve_bat_files.py` |
| 1 | 9 | 13.3 | `src/TOOLS/PythonMapper_Quick.py` |
| 1 | 8 | 13.2 | `src/ORCHESTRATION/ml_platforms/auto_install.py` |
| 1 | 8 | 13.2 | `src/ORCHESTRATION/scripts/fix_syntax_errors.py` |
| 1 | 7 | 13.0 | `src/CODEX/VIDEOS/make_video_v2.py` |
| 1 | 6 | 12.8 | `src/CORE/xref_auto_link.py` |
| 1 | 5 | 12.6 | `scripts/make_launcher_icons.py` |
| 1 | 4 | 12.3 | `src/FILE_MANIFEST_GENERATOR.py` |
| 1 | 4 | 12.3 | `src/CODEX/inject_session_cain.py` |
| 1 | 4 | 12.3 | `src/CODEX/VIDEOS/create_video.py` |
| 1 | 3 | 12.0 | `src/CODEX/VIDEOS/make_video_quad.py` |
| 1 | 3 | 12.0 | `src/CODEX/VIDEOS/make_video_v3.py` |
| 1 | 3 | 12.0 | `src/CODEX/VIDEOS/make_video_vibrant.py` |
| 1 | 3 | 12.0 | `src/CODEX/VIDEOS/make_video_zip.py` |
| 1 | 3 | 12.0 | `src/CODEX/VIDEOS/make_video_zipper.py` |
| 1 | 2 | 11.6 | `src/CORE/xref_webhook.py` |
| 1 | 2 | 11.6 | `src/ORCHESTRATION/ml_platforms/lm_studio_autoload.py` |
| 1 | 2 | 11.6 | `src/ORCHESTRATION/ml_platforms/openinterpreter_startup.py` |
| 1 | 1 | 11.0 | `src/azazael_toolkit.py` |
| 1 | 1 | 11.0 | `src/CODEX/POPUPS/POPUP_BUGFREE.py` |
| 1 | 1 | 11.0 | `src/CODEX/VIDEOS/make_video.py` |
| 1 | 1 | 11.0 | `src/CODEX/VIDEOS/make_video_docs.py` |
| 1 | 1 | 11.0 | `src/SCRIPTS/lsp_diagnosis.py` |
| 1 | 0 | 10.0 | `src/AZAZAEL_TOOLKIT/update_docs_paths.py` |
| 1 | 0 | 10.0 | `src/ORCHESTRATION/ml_platforms/autoload.py` |
| 1 | 0 | 10.0 | `src/SCRIPTS/bootstrap.py` |

## Per-line detail — top 12 files (P0/P1)

### `src/ORCHESTRATION/ml_platforms/improvements/weakness_testing.py` (27 handlers, 143 graph-edges)

```python
    324  except Exception as e:
    365  except Exception as e:
    407  except Exception as e:
    452  except Exception as e:
    504  except Exception as e:
    546  except Exception as e:
    596  except Exception as e:
    643  except Exception as e:
    696  except Exception as e:
    737  except Exception as e:
    782  except Exception as e:
    823  except Exception as e:
    864  except Exception as e:
    902  except Exception as e:
    955  except Exception as e:
    995  except Exception as e:
   1029  except Exception as e:
   1076  except Exception as e:
   1108  except Exception as e:
    576  except Exception as e:
    583  except Exception as e:
    624  except Exception as e:
    631  except Exception as e:
    891  except Exception:
   1063  except Exception:
    684  except Exception as e:
    724  except Exception:
```

### `src/CORE/WORMS/OS_CONGRUENCY.py` (25 handlers, 94 graph-edges)

```python
    114  except Exception:
    128  except Exception as e:
    143  except Exception:
    160  except Exception:
    195  except Exception:
    219  except Exception:
    245  except Exception:
    295  except Exception:
    330  except Exception:
    339  except Exception:
    347  except Exception:
    450  except Exception:
    461  except Exception:
    474  except Exception:
    482  except Exception:
    508  except Exception:
    536  except Exception:
    553  except Exception as e:
    394  except Exception:
    418  except Exception:
    183  except Exception:
    235  except Exception:
    293  except Exception:
    506  except Exception:
    392  except Exception:
```

### `src/CORE/dashboard.py` (25 handlers, 93 graph-edges)

```python
    116  except Exception as e:
    139  except Exception as e:
    150  except Exception as e:
    156  except Exception as e:
    169  except Exception:
    183  except Exception:
    197  except Exception:
    209  except Exception:
    230  except Exception:
    251  except Exception:
    259  except Exception:
    346  except Exception as e:
    380  except Exception:
    392  except Exception as e:
    465  except Exception as e:
    524  except Exception:
    546  except Exception as e:
    598  except Exception:
    628  except Exception as e:
    652  except Exception as e:
    762  except Exception as e:
    776  except Exception as e:
    789  except Exception as e:
    799  except Exception:
    815  except Exception as e:
```

### `src/CORE/inference/providers.py` (21 handlers, 306 graph-edges)

```python
    825  except Exception as e:
    873  except Exception as e:
   1163  except Exception as e:
   1220  except Exception as e:
   1633  except Exception as e:
   1713  except Exception as e:
   1793  except Exception:
   1824  except Exception:
   1834  except Exception:
   2020  except Exception as e:
   2059  except Exception as e:
   2123  except Exception:
   2264  except Exception as e:
   2492  except Exception as e:
   2833  except Exception as e:
    820  except Exception:
   2304  except Exception as e:
   2364  except Exception:
   1905  except Exception:
   2362  except Exception:
   1941  except Exception:
```

### `src/CORE/WORMS/expansion/learning.py` (18 handlers, 212 graph-edges)

```python
     39  except Exception:
    145  except Exception as e:
    173  except Exception:
    227  except Exception:
    469  except Exception:
    765  except Exception as e:
   1620  except Exception:
    301  except Exception:
    617  except Exception:
    693  except Exception:
    838  except Exception:
   1058  except Exception as e:
   1144  except Exception as e:
   1457  except Exception:
    203  except Exception:
    738  except Exception:
   1377  except Exception:
   1374  except Exception:
```

### `src/CORE/Agent.py` (18 handlers, 132 graph-edges)

```python
    291  except Exception as e:
    495  except Exception:
    654  except Exception:
    680  except Exception:
    700  except Exception:
    219  except Exception:
    241  except Exception:
    365  except Exception as e:
    529  except Exception:
    572  except Exception:
    622  except Exception:
    709  except Exception:
    717  except Exception:
    741  except Exception:
    757  except Exception:
    771  except Exception:
    278  except Exception:
    395  except Exception as e:
```

### `src/CORE/WORMS/CLUSTERWORMS.py` (17 handlers, 177 graph-edges)

```python
    450  except Exception as e:
    421  except Exception as e:
    435  except Exception:
    502  except Exception:
    654  except Exception as e:
    689  except Exception as e:
    805  except Exception as e:
    129  except Exception:
    479  except Exception as e:
    816  except Exception:
    903  except Exception:
   1095  except Exception:
   1205  except Exception:
     96  except Exception:
    110  except Exception:
    164  except Exception:
    957  except Exception as e:
```

### `src/CODEX/CODEX_Studio.py` (16 handlers, 113 graph-edges)

```python
    542  except Exception:
   1266  except Exception:
    400  except Exception:
    935  except Exception as e:
   1087  except Exception as e:
   1197  except Exception as e:
   1373  except Exception:
    420  except Exception:
    441  except Exception:
    521  except Exception:
    549  except Exception:
    874  except Exception as e:
    308  except Exception:
    316  except Exception:
    339  except Exception:
   1097  except Exception:
```

### `src/CORE/WORMS/REVERSE_TOOLS.py` (15 handlers, 68 graph-edges)

```python
    272  except Exception:
    331  except Exception:
    397  except Exception as e:
    506  except Exception as e:
    716  except Exception as e:
    749  except Exception as e:
    760  except Exception as e:
    141  except Exception:
    288  except Exception:
    303  except Exception:
    368  except Exception:
    566  except Exception:
    629  except Exception:
    316  except Exception:
    195  except Exception:
```

### `src/REAL_FRAMEWORK_TEST.py` (13 handlers, 59 graph-edges)

```python
    381  except Exception:
    503  except Exception as e:
     58  except Exception:
     93  except Exception as e:
    152  except Exception as e:
    182  except Exception as e:
    231  except Exception as e:
    258  except Exception as e:
    287  except Exception as e:
    312  except Exception as e:
    352  except Exception as e:
    410  except Exception as e:
    436  except Exception as e:
```

### `src/AZAZAEL_Inference_Studio.py` (12 handlers, 165 graph-edges)

```python
     47  except Exception:
    259  except Exception:
    281  except Exception:
    296  except Exception:
    320  except Exception:
    394  except Exception:
   1149  except Exception:
   1652  except Exception:
   1715  except Exception:
    200  except Exception:
   1130  except Exception:
   1369  except Exception:
```

### `src/CORE/compliance/pre_action_gate.py` (12 handlers, 127 graph-edges)

```python
    104  except Exception:
    122  except Exception:
    130  except Exception:
    892  except Exception as e:
   1374  except Exception as e:
   1444  except Exception as e:
    199  except Exception:
    207  except Exception:
    928  except Exception as e:
   1152  except Exception as e:
   1159  except Exception:
   1248  except Exception as revert_err:
```

## By directory

| Dir | catch-alls |
|---|---:|
| `src` | 1196 |
| `scripts` | 45 |

---

_Regenerated by `tmp_backlog_scan.py`-driven report. To shrink budget: fix P0→P4, run `python scripts/check_no_catch_alls.py --max-broad <n>`, then raise `DEFAULT_MAX_BROAD` in the guard._