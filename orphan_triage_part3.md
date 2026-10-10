# Orphan triage — part 3 of 3 (slice `orphans[261:392]`, 131 idents)

Coordinator rule set, applied literally:

1. `if __name__ == "__main__"` **or** a CLI framework (argparse/click/typer) → **SUBAPP-ENTRY**
2. else a package `__init__.py` whose body is docstring / `__all__` / re-export only → **FACADE**
3. else nothing anywhere imports it (`no_importer`) → **DEAD**
4. else (in the orphan set but something imports it) → **UNCLEAR** — a dead cluster; a human call

Header note: the assignment named four fields to record but specified a five-column
header. `in_no_importer` is added as a sixth column so no recorder field is dropped.

| ident | file | class | has_main | purpose | in_no_importer |
|---|---|---|---|---|---|
| ORCHESTRATION.ml_platforms.run_qanalysis_multi | src/ORCHESTRATION/ml_platforms/run_qanalysis_multi.py | DEAD | no | (no docstring) | yes |
| ORCHESTRATION.ml_platforms.unified_analysis | src/ORCHESTRATION/ml_platforms/unified_analysis.py | SUBAPP-ENTRY | yes | Unified Analysis — module for ml_platforms functionality | yes |
| ORCHESTRATION.ml_platforms.universal_converter | src/ORCHESTRATION/ml_platforms/universal_converter.py | SUBAPP-ENTRY | yes | Universal Converter — module for ml_platforms functionality | yes |
| ORCHESTRATION.ml_platforms.verify_moe | src/ORCHESTRATION/ml_platforms/verify_moe.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| ORCHESTRATION.scripts | src/ORCHESTRATION/scripts/__init__.py | FACADE | no | (no docstring) | yes |
| ORCHESTRATION.scripts.azazael_cli | src/ORCHESTRATION/scripts/azazael_cli.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| ORCHESTRATION.scripts.azazael_wsa | src/ORCHESTRATION/scripts/azazael_wsa.py | SUBAPP-ENTRY | yes | Azazael WSA Integration Module — interoperability with Windows Subsystem for Android | yes |
| ORCHESTRATION.scripts.bat_analysis | src/ORCHESTRATION/scripts/bat_analysis.py | SUBAPP-ENTRY | yes | Bat Analysis — module for scripts functionality | yes |
| ORCHESTRATION.scripts.check_links | src/ORCHESTRATION/scripts/check_links.py | SUBAPP-ENTRY | yes | Check Links — module for scripts functionality | yes |
| ORCHESTRATION.scripts.complete_module_analysis | src/ORCHESTRATION/scripts/complete_module_analysis.py | SUBAPP-ENTRY | yes | Comprehensive Analysis of ALL Python Modules on the System Drive | yes |
| ORCHESTRATION.scripts.comprehensive_analysis | src/ORCHESTRATION/scripts/comprehensive_analysis.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| ORCHESTRATION.scripts.consistency_checker | src/ORCHESTRATION/scripts/consistency_checker.py | SUBAPP-ENTRY | yes | Consistency Checker for Azazael Documentation | yes |
| ORCHESTRATION.scripts.fix_syntax_errors | src/ORCHESTRATION/scripts/fix_syntax_errors.py | SUBAPP-ENTRY | yes | Fix Syntax Errors in Azazael Modules Only | yes |
| ORCHESTRATION.scripts.generate_docs_index | src/ORCHESTRATION/scripts/generate_docs_index.py | SUBAPP-ENTRY | yes | Generate Docs Index — module for scripts functionality | yes |
| ORCHESTRATION.scripts.generate_docstrings | src/ORCHESTRATION/scripts/generate_docstrings.py | SUBAPP-ENTRY | yes | Auto-Generate Docstrings for Python Modules | yes |
| ORCHESTRATION.scripts.improve_bat_files | src/ORCHESTRATION/scripts/improve_bat_files.py | SUBAPP-ENTRY | yes | Improve All BAT Files with Standardized Template | yes |
| ORCHESTRATION.scripts.test_enhancements | src/ORCHESTRATION/scripts/test_enhancements.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| ORCHESTRATION.scripts.validate_docs | src/ORCHESTRATION/scripts/validate_docs.py | SUBAPP-ENTRY | yes | Validate Docs — module for scripts functionality | yes |
| ORCHESTRATION.scripts.web_dashboard | src/ORCHESTRATION/scripts/web_dashboard.py | SUBAPP-ENTRY | yes | Azazael Web Dashboard | yes |
| PSYCHE | src/PSYCHE/__init__.py | FACADE | no | PSYCHE — person psychology as an editable logical framework | no |
| PSYCHE.affect | src/PSYCHE/affect.py | UNCLEAR | no | PSYCHE Phase 1 — affect: PAD space, OCC appraisal, regulation, TD bridge | no |
| PSYCHE.artifact | src/PSYCHE/artifact.py | UNCLEAR | no | PSYCHE Phase 4 — artifact composition + CAIN archetype readout (H5) | no |
| PSYCHE.distill | src/PSYCHE/distill.py | UNCLEAR | no | PSYCHE Phase 3 — distillation on frozen theta + choice-trait identification | no |
| PSYCHE.evaluate | src/PSYCHE/evaluate.py | UNCLEAR | no | PSYCHE Phase 5 — fidelity harness: the program merge gate | no |
| PSYCHE.identify | src/PSYCHE/identify.py | UNCLEAR | no | PSYCHE Phase 2 — identification: behavior in, traits out (H3) | no |
| PSYCHE.traits | src/PSYCHE/traits.py | UNCLEAR | no | PSYCHE Phase 0 — trait vector: OCEAN + Honesty-Humility, scored, editable | no |
| QL_ANALYSIS | src/QL_ANALYSIS.py | SUBAPP-ENTRY | yes | QL Analysis — Thin wrapper around AZAZAEL_TOOLKIT canonical version | no |
| QL_FILE_OPTIMIZER | src/QL_FILE_OPTIMIZER.py | SUBAPP-ENTRY | yes | QLearning File Optimizer — Q-learning tables for file-deletion decisions | no |
| REAL_FRAMEWORK_TEST | src/REAL_FRAMEWORK_TEST.py | SUBAPP-ENTRY | yes | AZAZAEL REAL FRAMEWORK TEST v1.0 — real imports and tests, no simulation | no |
| SCRIPTS | src/SCRIPTS/__init__.py | FACADE | no | (no docstring) | yes |
| SCRIPTS._reconstruct_error214 | src/SCRIPTS/_reconstruct_error214.py | SUBAPP-ENTRY | yes | _reconstruct_error214.py — Replay Error #214 destructive patterns through the gate | yes |
| SCRIPTS.auto_sync | src/SCRIPTS/auto_sync.py | SUBAPP-ENTRY | yes | auto_sync.py — RULE 0R-A polling daemon for automatic skill synchronization | yes |
| SCRIPTS.bootstrap | src/SCRIPTS/bootstrap.py | DEAD | no | Azazael Bootstrapper v2.0 - With Dynamic Logging | yes |
| SCRIPTS.enforce_pre_action_gate | src/SCRIPTS/enforce_pre_action_gate.py | SUBAPP-ENTRY | yes | enforce_pre_action_gate.py — Programmatic enforcement of the pre-action gate | yes |
| SCRIPTS.environ_updater | src/SCRIPTS/environ_updater.py | SUBAPP-ENTRY | yes | Azazael Environment with ML Imbuement | yes |
| SCRIPTS.fix_bare_excepts | src/SCRIPTS/fix_bare_excepts.py | SUBAPP-ENTRY | yes | fix_bare_excepts.py — AST-aware bare except: fixer | yes |
| SCRIPTS.gate_str_replace | src/SCRIPTS/gate_str_replace.py | SUBAPP-ENTRY | yes | gate_str_replace.py — Fully gated str_replace pipeline | yes |
| SCRIPTS.gate_write_file | src/SCRIPTS/gate_write_file.py | SUBAPP-ENTRY | yes | gate_write_file.py — Fully gated write_file pipeline | yes |
| SCRIPTS.gated_edit | src/SCRIPTS/gated_edit.py | SUBAPP-ENTRY | yes | gated_edit.py — Basher-compatible single-command wrapper for gate_str_replace.py | yes |
| SCRIPTS.generate_tool_skills | src/SCRIPTS/generate_tool_skills.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| SCRIPTS.lsp_diagnosis | src/SCRIPTS/lsp_diagnosis.py | DEAD | no | LSP & Environment Diagnosis for Azazael | yes |
| SCRIPTS.monitor_learning | src/SCRIPTS/monitor_learning.py | SUBAPP-ENTRY | yes | monitor_learning.py - Health monitor for the scheduled learning loops | yes |
| SCRIPTS.parallel_compliance_scanner | src/SCRIPTS/parallel_compliance_scanner.py | SUBAPP-ENTRY | yes | Parallel Compliance Scanner — CLI tool for RULE 0Z-F compliance | yes |
| SCRIPTS.request_auth | src/SCRIPTS/request_auth.py | SUBAPP-ENTRY | yes | request_auth.py -- Programmatic PRE-ACTION GATE CLI (Gemini-Architected v3) | yes |
| SCRIPTS.run_test_generate_telemetry | src/SCRIPTS/run_test_generate_telemetry.py | SUBAPP-ENTRY | yes | Standalone test runner for generate_telemetry.py — RULE 0Z-F telemetry export | yes |
| SCRIPTS.session_start | src/SCRIPTS/session_start.py | SUBAPP-ENTRY | yes | session_start.py — Unified Azazael session startup | yes |
| SCRIPTS.session_start_check | src/SCRIPTS/session_start_check.py | SUBAPP-ENTRY | yes | session_start_check.py - One-shot startup verification | yes |
| SCRIPTS.sync_canonical_docs | src/SCRIPTS/sync_canonical_docs.py | SUBAPP-ENTRY | yes | sync_canonical_docs.py — RULE 0Z-J: Canonical Document Sync & Drift Detection | yes |
| SCRIPTS.sync_skills | src/SCRIPTS/sync_skills.py | SUBAPP-ENTRY | yes | sync_skills.py — Sync azazael/skills/*.md to .agents/skills/<name>/SKILL.md | yes |
| SCRIPTS.test_auto_sync | src/SCRIPTS/test_auto_sync.py | SUBAPP-ENTRY | yes | Unit tests for auto_sync.py — RULE 0R-A polling daemon | yes |
| SCRIPTS.test_dynamic_logging | src/SCRIPTS/test_dynamic_logging.py | DEAD | no | Test Dynamic Logging System | yes |
| SCRIPTS.test_generate_telemetry | src/SCRIPTS/test_generate_telemetry.py | SUBAPP-ENTRY | yes | Integration tests for generate_telemetry.py — RULE 0Z-F telemetry export | yes |
| SCRIPTS.test_rule_0zf_consistency | src/SCRIPTS/test_rule_0zf_consistency.py | SUBAPP-ENTRY | yes | RULE 0Z-F Consistency Verification Test | yes |
| SCRIPTS.test_rule_0zf_integration | src/SCRIPTS/test_rule_0zf_integration.py | SUBAPP-ENTRY | yes | RULE 0Z-F Integration Test — Validates PreActionGate detects and reverts violations | yes |
| SCRIPTS.test_rule_0zf_telemetry | src/SCRIPTS/test_rule_0zf_telemetry.py | SUBAPP-ENTRY | yes | RULE 0Z-F Telemetry Counter Tests | yes |
| SCRIPTS.test_startup_step4_8 | src/SCRIPTS/test_startup_step4_8.py | SUBAPP-ENTRY | yes | Startup Step 4.8 Validation Test — Verifies RULE 0Z-F is enforced at session startup | yes |
| SHORTCUTS | src/SHORTCUTS/__init__.py | FACADE | no | Azazael SHORTCUTS - Batch automation scripts. | no |
| TELEMETRYZ | src/TELEMETRYZ.py | SUBAPP-ENTRY | yes | TELEMETRYZ - Performance Tracing for Azazael Ecosystem | no |
| TOOLS | src/TOOLS/__init__.py | FACADE | no | AZAZAEL Tools — archive, logging, diagnostics, comprehensive fix, launcher. | yes |
| TOOLS.AzazaelDynamicLogger | src/TOOLS/AzazaelDynamicLogger.py | DEAD | no | Azazael Dynamic Logger v1.0 — Real-time, persistent logging with automatic flush | yes |
| TOOLS.COMPREHENSIVE_FIX | src/TOOLS/COMPREHENSIVE_FIX.py | DEAD | no | AZAZAEL COMPREHENSIVE FIX v1.0 — LSP error diagnosis | yes |
| TOOLS.PythonMapper_Quick | src/TOOLS/PythonMapper_Quick.py | SUBAPP-ENTRY | yes | Python System Quick Mapper - Fast system scan for Python installations. | yes |
| TOOLS.PythonSystemMapper | src/TOOLS/PythonSystemMapper.py | SUBAPP-ENTRY | yes | Python System Mapper — Maps all Python installations and their relationships | yes |
| TOOLS.PythonSystemMapper_Full | src/TOOLS/PythonSystemMapper_Full.py | SUBAPP-ENTRY | yes | Python System Mapper - Full System Scan | yes |
| TOOLS.archive_system | src/TOOLS/archive_system.py | SUBAPP-ENTRY | yes | AZAZAEL Archive System | yes |
| TOOLS.azazael_toolkit | src/TOOLS/azazael_toolkit.py | DEAD | no | DEPRECATION SHIM — Re-exports from canonical location. | yes |
| TOOLS.debug_runner | src/TOOLS/debug_runner.py | SUBAPP-ENTRY | yes | Azazael .debug Multi-Agent Test Runner | yes |
| TOOLS.qwythos_proxy | src/TOOLS/qwythos_proxy.py | SUBAPP-ENTRY | yes | Qwythos XML tool-call translation proxy (stdlib only). | yes |
| TRIMZ | src/TRIMZ.py | SUBAPP-ENTRY | yes | TRIMZ - BIBL-Conjunctive Content Trimmer | no |
| UTILITIES | src/UTILITIES/__init__.py | FACADE | no | Azazael UTILITIES - Cross-cutting tools and launchers. | yes |
| UTILITIES.AzazaelDynamicLogger | src/UTILITIES/AzazaelDynamicLogger.py | DEAD | no | Azazael Dynamic Logger v1.0 - Real-time persistent logging | yes |
| UTILITIES.KLINK | src/UTILITIES/KLINK/__init__.py | FACADE | no | Azazael UTILITIES - KLINK CLI launcher. | yes |
| UTILITIES.KLINK.klink | src/UTILITIES/KLINK/klink.py | SUBAPP-ENTRY | yes | KLINK - Azazael Ecosystem Unified Command Launcher | yes |
| UTILITIES.Loggers | src/UTILITIES/Loggers/__init__.py | FACADE | no | (no docstring) | yes |
| UTILITIES.PERSEPHONE | src/UTILITIES/PERSEPHONE/__init__.py | FACADE | no | Azazael PERSEPHONE - Cross-platform utilities. | yes |
| UTILITIES.PERSEPHONE.bin | src/UTILITIES/PERSEPHONE/bin/__init__.py | FACADE | no | (no docstring) | yes |
| UTILITIES.PERSEPHONE.bin.persephone_cli | src/UTILITIES/PERSEPHONE/bin/persephone_cli.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| UTILITIES.PERSEPHONE.bin.setup_wizard | src/UTILITIES/PERSEPHONE/bin/setup_wizard.py | SUBAPP-ENTRY | yes | (no docstring) | yes |
| UTILITIES.PERSEPHONE.lib | src/UTILITIES/PERSEPHONE/lib/__init__.py | FACADE | no | PERSEPHONE Library Package | yes |
| UTILITIES.PERSEPHONE.lib.environment | src/UTILITIES/PERSEPHONE/lib/environment.py | SUBAPP-ENTRY | yes | Environment Manager for PERSEPHONE. | yes |
| UTILITIES.PERSEPHONE.lib.path_manager | src/UTILITIES/PERSEPHONE/lib/path_manager.py | SUBAPP-ENTRY | yes | Path Manager for PERSEPHONE. | yes |
| UTILITIES.PERSEPHONE.lib.sync_manager | src/UTILITIES/PERSEPHONE/lib/sync_manager.py | SUBAPP-ENTRY | yes | Sync Manager for PERSEPHONE. | yes |
| UTILITIES.PERSEPHONE.persephone | src/UTILITIES/PERSEPHONE/persephone.py | SUBAPP-ENTRY | yes | PERSEPHONE - Cross-Platform WSL Utilities | yes |
| UTILITIES.PERSEPHONE.version | src/UTILITIES/PERSEPHONE/version.py | DEAD | no | (no docstring) | yes |
| UTILITIES.POINDEXTER | src/UTILITIES/POINDEXTER/__init__.py | FACADE | no | Azazael POINDEXTER - Mathematical indexer. | yes |
| UTILITIES.POINDEXTER.POINDEXTER | src/UTILITIES/POINDEXTER/POINDEXTER.py | SUBAPP-ENTRY | yes | POINDEXTER - Mathematical Protocol Indexer | yes |
| UTILITIES.TARBABY | src/UTILITIES/TARBABY/__init__.py | FACADE | no | Azazael TARBABY - Binary builder. | yes |
| UTILITIES.TARBABY.TARBABY | src/UTILITIES/TARBABY/TARBABY.py | SUBAPP-ENTRY | yes | TARBABY - Binary Compatibility & Version Manager | yes |
| UTILITIES.TARBABY.tarbaby_enhanced | src/UTILITIES/TARBABY/tarbaby_enhanced.py | SUBAPP-ENTRY | yes | TARBABY Enhanced - Binary Compatibility & Conflict Resolution | yes |
| UTILITIES.TERENCE | src/UTILITIES/TERENCE/__init__.py | FACADE | no | Azazael TERENCE - Error resolution protocol. | yes |
| UTILITIES.TERENCE.TERENCE | src/UTILITIES/TERENCE/TERENCE.py | SUBAPP-ENTRY | yes | TERENCE - Error Resolution Protocol | yes |
| UTILITIES.TERENCE.terence_enhanced | src/UTILITIES/TERENCE/terence_enhanced.py | SUBAPP-ENTRY | yes | TERENCE Enhanced - Conflict Incompatability Resolution Protocol | yes |
| UVZ | src/UVZ.py | SUBAPP-ENTRY | yes | UVZ - uv Integration Layer for Azazael Ecosystem | yes |
| azazael_pygame | src/azazael_pygame.py | SUBAPP-ENTRY | yes | Azazael Visualizer - PyGame Version | yes |
| azazael_toolkit | src/azazael_toolkit.py | SUBAPP-ENTRY | yes | AZAZAEL TOOLKIT - MASTER LAUNCHER v2.0 | no |
| chain_of_action | src/chain_of_action.py | SUBAPP-ENTRY | yes | AZAZAEL CHAIN-OF-ACTION AUTOMATION SCRIPT — Type 1-5 Workflow Implementation | yes |
| enrichment_display | src/enrichment_display.py | UNCLEAR | no | ENRICHMENT DISPLAY PROTOCOLS — animations for enriched data in the CODEX ecosystem | no |
| environment_manager | src/environment_manager.py | SUBAPP-ENTRY | yes | Environment Manager — Thin wrapper around AZAZAEL_TOOLKIT canonical version | no |
| eve_unleashed | src/eve_unleashed/__init__.py | FACADE | no | Eve Unleashed - Azazael Inference Engine | yes |
| eve_unleashed.cache | src/eve_unleashed/cache.py | UNCLEAR | no | Eve Unleashed — Inference Cache (LRU with TTL) | yes |
| eve_unleashed.cli | src/eve_unleashed/cli.py | SUBAPP-ENTRY | yes | Eve Unleashed CLI | yes |
| eve_unleashed.config | src/eve_unleashed/config.py | UNCLEAR | no | Eve Unleashed Configuration — device, batch size, precision, caching | yes |
| eve_unleashed.core | src/eve_unleashed/core.py | UNCLEAR | no | Eve Unleashed Core — model loading, inference result types, framework detection | yes |
| eve_unleashed.engine | src/eve_unleashed/engine.py | UNCLEAR | no | Eve Unleashed Inference Engine | yes |
| eve_unleashed.model_registry | src/eve_unleashed/model_registry.py | UNCLEAR | no | Eve Unleashed Model Registry — cross-project model tracking and statistics | yes |
| eve_unleashed.models | src/eve_unleashed/models/__init__.py | FACADE | no | Eve Unleashed — Model Architectures | yes |
| eve_unleashed.models.qwen35_ssm | src/eve_unleashed/models/qwen35_ssm.py | UNCLEAR | no | Eve Unleashed — Qwen35 SSM Hybrid Model | yes |
| eve_unleashed.streaming | src/eve_unleashed/streaming.py | UNCLEAR | no | Eve Unleashed — Streaming Inference (async generator) | yes |
| eve_unleashed.utils | src/eve_unleashed/utils.py | UNCLEAR | no | Eve Unleashed Utilities — tensor prep, postprocessing, shape validation | yes |
| math_certainty | src/math_certainty.py | SUBAPP-ENTRY | yes | Math Certainty — Thin wrapper around AZAZAEL_TOOLKIT canonical version | no |
| matrix_animation | src/matrix_animation.py | UNCLEAR | no | Azazael Matrix Cascade Animation | no |
| memory_status | src/memory_status.py | SUBAPP-ENTRY | yes | Memory Status Reporter - Unified Memory System Initializer | yes |
| performance_monitor | src/performance_monitor.py | SUBAPP-ENTRY | yes | PerformanceMonitor — Cross-Project System Monitoring | no |
| persistent_memory | src/persistent_memory.py | SUBAPP-ENTRY | yes | Persistent Memory - SQL Database Connection Module | yes |
| session_memory | src/session_memory.py | SUBAPP-ENTRY | yes | Session Memory — Persistent Cross-Session Learning Database | no |
| tests | src/tests/__init__.py | FACADE | no | (no docstring) | yes |
| tests.test_ecosystem | src/tests/test_ecosystem.py | SUBAPP-ENTRY | yes | Azazael Production Unit Tests | yes |
| tests.test_evolution_accuracy | src/tests/test_evolution_accuracy.py | SUBAPP-ENTRY | yes | Accuracy/regression tests for the evolution subsystem (fixed 2026-09-08) | yes |
| tests.test_learning_loop | src/tests/test_learning_loop.py | SUBAPP-ENTRY | yes | Regression tests for the autonomous learning loop (fixed 2026-09-07) | yes |
| tests.test_ml_autodiff | src/tests/test_ml_autodiff.py | SUBAPP-ENTRY | yes | Unit tests for ML.autodiff - first-principles automatic differentiation | yes |
| tests.test_ml_dream | src/tests/test_ml_dream.py | SUBAPP-ENTRY | yes | Unit tests for ML.trace_consolidator - offline trace consolidation | yes |
| tests.test_ml_estimators | src/tests/test_ml_estimators.py | SUBAPP-ENTRY | yes | Unit tests for ML.estimators - native wrappers for eight estimator families | yes |
| tests.test_ml_evolve | src/tests/test_ml_evolve.py | SUBAPP-ENTRY | yes | Unit tests for ML.nsga_tuner - NSGA-II tuning of agent hyperparameters | yes |
| tests.test_ml_gosp | src/tests/test_ml_gosp.py | SUBAPP-ENTRY | yes | Unit tests for ML.gosp (online session-outcome learner) and ML.torch_bridge | yes |
| tests.test_ml_metacog | src/tests/test_ml_metacog.py | SUBAPP-ENTRY | yes | Unit tests for ML.step_monitor - online stall/loop monitor | yes |
| tests.test_ml_nsga | src/tests/test_ml_nsga.py | SUBAPP-ENTRY | yes | Unit tests for ML.nsga - NSGA-II multi-objective optimizer | yes |
| tests.test_nuclei_bridge | src/tests/test_nuclei_bridge.py | SUBAPP-ENTRY | yes | Unit tests for CORE/WORMS/expansion/nuclei.py - NucleiBridge worm | yes |
| tests.test_worm_registry | src/tests/test_worm_registry.py | SUBAPP-ENTRY | yes | Unit tests for worm_registry.py — Centralized Worm Registry & Spawn Diversity Engine | yes |
| tmp_verify | src/tmp_verify.py | DEAD | no | (no docstring) | yes |
| update_docs_paths | src/update_docs_paths.py | SUBAPP-ENTRY | yes | Update Docs Paths — Thin wrapper around AZAZAEL_TOOLKIT canonical version | no |
| verify_all | src/verify_all.py | SUBAPP-ENTRY | yes | verify_all.py — CI-style verification runner for Azazael | yes |

counts: SUBAPP-ENTRY=88 DEAD=10 FACADE=17 UNCLEAR=16
