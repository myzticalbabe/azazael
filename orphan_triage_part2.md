# Orphan worklist triage — part 2 of 3 (orphans[130:261])

Slice = `orphans[130:261]` from `state/orphan_scan.json`, in slice order. 131 idents.

Evidence basis, so the columns are checkable:

- `has_main` = **yes** only when an `if __name__ == "__main__"` line was actually
  observed for that file in a bulk ripgrep over `src/` (that search hit its
  250-result global cap, so `no` means *not observed*, not *proved absent*).
- `class` SUBAPP-ENTRY also when argparse/click/typer was observed even if no
  main guard was.
- `purpose` is the module docstring where the file was opened; `(not read)` means
  the file was identified only from the bulk searches and was **not** opened, so
  no docstring claim is made for it.
- `in_no_importer` = ident also appears in the `no_importer` list in the JSON.

| ident | file | class | has_main | purpose |
|---|---|---|---|---|
| CODEX.generate_session_cain | src/CODEX/generate_session_cain.py | SUBAPP-ENTRY | yes | (not read) |
| CODEX.inject_cain_20260930 | src/CODEX/inject_cain_20260930.py | SUBAPP-ENTRY | yes | (not read) |
| CODEX.inject_session_cain | src/CODEX/inject_session_cain.py | SUBAPP-ENTRY | yes | (not read) |
| COMPREHENSIVE_FIX | src/COMPREHENSIVE_FIX.py | SUBAPP-ENTRY | yes | (not read) |
| DAEMONS.check_parallax | src/DAEMONS/check_parallax.py | SUBAPP-ENTRY | yes | (not read) |
| DAEMONS.install_parallax_startup | src/DAEMONS/install_parallax_startup.py | SUBAPP-ENTRY | yes | (not read) |
| DAEMONS.parallax_validator | src/DAEMONS/parallax_validator.py | SUBAPP-ENTRY | yes | (not read) |
| DOCKERZ | src/DOCKERZ.py | SUBAPP-ENTRY | yes | (not read) |
| ECOSYSTEM_HEALTH_CHECK | src/ECOSYSTEM_HEALTH_CHECK.py | SUBAPP-ENTRY | yes | (not read) |
| ERRORZ | src/ERRORZ.py | SUBAPP-ENTRY | yes | (not read) |
| FILE_MANIFEST_GENERATOR | src/FILE_MANIFEST_GENERATOR.py | SUBAPP-ENTRY | yes | (not read) |
| HEALTHZ | src/HEALTHZ.py | SUBAPP-ENTRY | yes | (not read) |
| HORUS_INTEGRATION | src/HORUS_INTEGRATION.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA | src/HYDRA/__init__.py | FACADE | no | "Azazael HYDRA - Adaptive ML cluster processing." |
| HYDRA.hydra_launcher | src/HYDRA/hydra_launcher.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.hydra_protocols | src/HYDRA/hydra_protocols.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.ml_platforms | src/HYDRA/ml_platforms/__init__.py | FACADE | no | (not read) |
| HYDRA.ml_platforms.PERMANENT_LOAD | src/HYDRA/ml_platforms/PERMANENT_LOAD.py | DEAD | no | "Permanent Load" |
| HYDRA.ml_platforms.config | src/HYDRA/ml_platforms/config.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.ml_platforms.harness | src/HYDRA/ml_platforms/harness.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.ml_platforms.health_monitor | src/HYDRA/ml_platforms/health_monitor.py | FACADE | no | "DEPRECATION SHIM: health_monitor.py — canonical is src/ORCHESTRATION/ml_platforms/health_monitor.py; this shim re-exports all public API" |
| HYDRA.ml_platforms.launcher | src/HYDRA/ml_platforms/launcher.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.ml_test | src/HYDRA/ml_test.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA.pipeline_specs | src/HYDRA/pipeline_specs.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRAMETA | src/HYDRAMETA.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRAMETA_UV | src/HYDRAMETA_UV.py | SUBAPP-ENTRY | yes | (not read) |
| HYDRA_CONTAINER | src/HYDRA_CONTAINER.py | SUBAPP-ENTRY | yes | (not read) |
| INTERPRETERS | src/INTERPRETERS/__init__.py | SUBAPP-ENTRY | yes | (not read) |
| INTERPRETERS.go_runner | src/INTERPRETERS/go_runner.py | SUBAPP-ENTRY | yes | (not read) |
| INTERPRETERS.rust_runner | src/INTERPRETERS/rust_runner.py | SUBAPP-ENTRY | yes | (not read) |
| META | src/META/__init__.py | FACADE | no | (no docstring; file is empty — package marker only) |
| META.DOCKERZ | src/META/DOCKERZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.DebugZ | src/META/DebugZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.DistillZ | src/META/DistillZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.ERRORZ | src/META/ERRORZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.FleetZ | src/META/FleetZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.HEALTHZ | src/META/HEALTHZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.HYDRAMETA | src/META/HYDRAMETA.py | SUBAPP-ENTRY | yes | (not read) |
| META.HYDRAMETA_UV | src/META/HYDRAMETA_UV.py | SUBAPP-ENTRY | yes | (not read) |
| META.HYDRA_CONTAINER | src/META/HYDRA_CONTAINER.py | SUBAPP-ENTRY | yes | (not read) |
| META.InferenceBridge | src/META/InferenceBridge.py | DEAD | no | "InferenceBridge — llama-server bridge for worm-fleet intelligence (Tier P0)... consumed by ORCHESTRATION/hydra_bridge.py" |
| META.METAWORMS | src/META/METAWORMS.py | SUBAPP-ENTRY | yes | (not read) |
| META.METAWORMS_ENRICHED | src/META/METAWORMS_ENRICHED.py | SUBAPP-ENTRY | yes | (not read) |
| META.METAWORMS_POPUP | src/META/METAWORMS_POPUP.py | SUBAPP-ENTRY | yes | (not read) |
| META.METRICZ | src/META/METRICZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.OPTIMIZ | src/META/OPTIMIZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.TELEMETRYZ | src/META/TELEMETRYZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.TRIMZ | src/META/TRIMZ.py | SUBAPP-ENTRY | yes | (not read) |
| META.UVZ | src/META/UVZ.py | SUBAPP-ENTRY | yes | (not read) |
| METAWORMS | src/METAWORMS.py | FACADE | no | "METAWORMS — DEPRECATED SHIM; all implementations moved to METAWORMS_ENRICHED.py, all classes re-exported from METAWORMS_ENRICHED" |
| METAWORMS_ENRICHED | src/METAWORMS_ENRICHED.py | SUBAPP-ENTRY | yes | (not read) |
| METAWORMS_POPUP | src/METAWORMS_POPUP.py | SUBAPP-ENTRY | yes | (not read) |
| METRICZ | src/METRICZ.py | SUBAPP-ENTRY | yes | (not read) |
| MISSING_TOOLS | src/MISSING_TOOLS.py | SUBAPP-ENTRY | yes | (not read) |
| ML | src/ML/__init__.py | FACADE | no | "Native azazael ML package. Owns the eight classical estimator families behind one uniform interface." (re-exports from ML.estimators) |
| ML.autodiff | src/ML/autodiff.py | DEAD | no | "First-principles automatic differentiation. Reverse-mode via mygrad; forward-mode dual numbers + complex-step; SGD/Momentum/Adam from first principles." |
| ML.dream | src/ML/dream.py | FACADE | no | "DEPRECATED shim — ML.dream renamed to ML.trace_consolidator (2026-10-10)" |
| ML.estimators | src/ML/estimators.py | DEAD | no | "Native azazael wrappers for the eight classical estimator families" |
| ML.evolve | src/ML/evolve.py | FACADE | no | "DEPRECATED shim — ML.evolve renamed to ML.nsga_tuner (2026-10-10)" |
| ML.gosp | src/ML/gosp.py | DEAD | no | "Online session-outcome learner (GOSP). DictVectorizer + GradientBoostingClassifier refit with warm_start." |
| ML.metacog | src/ML/metacog.py | FACADE | no | "DEPRECATED shim — ML.metacog renamed to ML.step_monitor (2026-10-10)" |
| ML.nsga | src/ML/nsga.py | DEAD | no | "NSGA-II multi-objective optimizer (Deb et al., 2002), from first principles on numpy" |
| ML.nsga_tuner | src/ML/nsga_tuner.py | DEAD | no | "Evolve azazael: NSGA-II tuning of EffGen agent hyperparameters" |
| ML.step_monitor | src/ML/step_monitor.py | DEAD | no | "Online metacognition monitor: watches a live agent step stream and raises stall/loop verdicts" |
| ML.torch_bridge | src/ML/torch_bridge.py | DEAD | no | "Optional torch bridge. torch is neither installed nor importable on this box; everything here is lazy." |
| ML.trace_consolidator | src/ML/trace_consolidator.py | DEAD | no | "Dreaming: offline consolidation of session traces into durable patterns" |
| OPTIMIZ | src/OPTIMIZ.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION | src/ORCHESTRATION/__init__.py | FACADE | no | "Azazael ORCHESTRATION - Ecosystem orchestration and integration." (re-exports listed in __all__) |
| ORCHESTRATION.ADLP_FusionCore | src/ORCHESTRATION/ADLP_FusionCore.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ADLP_MLOrchestrator | src/ORCHESTRATION/ADLP_MLOrchestrator.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ADLP_SystemTools | src/ORCHESTRATION/ADLP_SystemTools.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.AssistantLogProtocol | src/ORCHESTRATION/AssistantLogProtocol.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.AssistantLogProtocol_Enhanced | src/ORCHESTRATION/AssistantLogProtocol_Enhanced.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.BIBL | src/ORCHESTRATION/BIBL/__init__.py | FACADE | no | (no docstring; file is empty — package marker only) |
| ORCHESTRATION.BIBL.bibl_crawler | src/ORCHESTRATION/BIBL/bibl_crawler.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.BIBL.bibl_map | src/ORCHESTRATION/BIBL/bibl_map.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ECOSYSTEM_CRAWLER_LAUNCHER | src/ORCHESTRATION/ECOSYSTEM_CRAWLER_LAUNCHER.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ECOSYSTEM_OPTIMIZER | src/ORCHESTRATION/ECOSYSTEM_OPTIMIZER.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.FusionHealer | src/ORCHESTRATION/FusionHealer.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.HORUS | src/ORCHESTRATION/HORUS.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.HORUS_LIVE_MONITOR | src/ORCHESTRATION/HORUS_LIVE_MONITOR.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.HYDRA | src/ORCHESTRATION/HYDRA.py | SUBAPP-ENTRY | no | (not read) |
| ORCHESTRATION.HYDRA_ANALYZER | src/ORCHESTRATION/HYDRA_ANALYZER.py | DEAD | no | "HYDRA Cluster - Comprehensive Analysis Generator / Creates colorful rich representations for video production" |
| ORCHESTRATION.HYDRA_ANALYZER_V2 | src/ORCHESTRATION/HYDRA_ANALYZER_V2.py | DEAD | no | "HYDRA Cluster - Comprehensive Analysis Generator V2 / With animated graphics and detailed technical distinctions" |
| ORCHESTRATION.INTEROPERABILITY_ANALYSIS | src/ORCHESTRATION/INTEROPERABILITY_ANALYSIS.py | DEAD | no | "MATHEMATICAL INTEROPERABILITY ANALYSIS — formal exploration of Azazael ecosystem interoperability (Interface Compatibility Matrix, Data Flow Analysis, Protocol Dependency Graphs, Cross-System Coupling Coefficients)" |
| ORCHESTRATION.MathCertainty | src/ORCHESTRATION/MathCertainty.py | DEAD | no | "Mathematical Certainty Proving System (MCPS) — mathematical certainty, proof verification, and log accuracy checking." |
| ORCHESTRATION.SelfImprovingGUI | src/ORCHESTRATION/SelfImprovingGUI.py | DEAD | no | "Self-Improving GUI with ML Clustering & Worm Visualization — standalone GUI using ML clustering for dynamic self-improvement and robustness." |
| ORCHESTRATION.SystemManager | src/ORCHESTRATION/SystemManager.py | DEAD | no | "System Manager - Full System Management Suite — comprehensive system management using all crawlers and tools." |
| ORCHESTRATION.SystemManagerGUI | src/ORCHESTRATION/SystemManagerGUI.py | DEAD | no | "System Manager GUI with Worm Visualization + ADLP Integration — GUI with directory structure visualization + full logging to ADLP." |
| ORCHESTRATION.TARBABY | src/ORCHESTRATION/TARBABY.py | SUBAPP-ENTRY | no | (not read) |
| ORCHESTRATION.TEST | src/ORCHESTRATION/TEST/__init__.py | FACADE | no | (no docstring; file contains only a coding comment) |
| ORCHESTRATION.TEST.ECOSYSTEM_TEST | src/ORCHESTRATION/TEST/ECOSYSTEM_TEST.py | DEAD | no | "ECOSYSTEM TEST SCRIPT — Tests TERENCE error resolution and activates HYDRA cluster" (a test script, not a production entry) |
| ORCHESTRATION.TotalFusion | src/ORCHESTRATION/TotalFusion.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.hydra_bridge | src/ORCHESTRATION/hydra_bridge.py | SUBAPP-ENTRY | no | (not read) |
| ORCHESTRATION.ml_platforms | src/ORCHESTRATION/ml_platforms/__init__.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ml_platforms.auto_install | src/ORCHESTRATION/ml_platforms/auto_install.py | DEAD | no | "Auto Install for ml_platforms — automatically installs missing packages using uv. Usage: python auto_install.py" |
| ORCHESTRATION.ml_platforms.autoload | src/ORCHESTRATION/ml_platforms/autoload.py | DEAD | no | "Autoload — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.changelog | src/ORCHESTRATION/ml_platforms/changelog.py | DEAD | no | "Changelog — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.config | src/ORCHESTRATION/ml_platforms/config.py | DEAD | no | "Auto-Discovering Configuration Manager with Live Lexicon Updates — discovers all modules in ml_platforms/, extracts documentation, keeps the BIBL lexicon current" |
| ORCHESTRATION.ml_platforms.cross_platform_analysis | src/ORCHESTRATION/ml_platforms/cross_platform_analysis.py | DEAD | no | "Cross Platform Analysis — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.diagnostics | src/ORCHESTRATION/ml_platforms/diagnostics.py | DEAD | no | "Diagnostics — module for ml_platforms functionality (check_platform_status, list_workflows)." |
| ORCHESTRATION.ml_platforms.framework_activator | src/ORCHESTRATION/ml_platforms/framework_activator.py | SUBAPP-ENTRY | no | (not read) |
| ORCHESTRATION.ml_platforms.harness | src/ORCHESTRATION/ml_platforms/harness.py | SUBAPP-ENTRY | yes | (not read) |
| ORCHESTRATION.ml_platforms.health_monitor | src/ORCHESTRATION/ml_platforms/health_monitor.py | DEAD | no | "Platform Health Monitor for ML Installations — real-time monitoring, issue detection, and automatic remediation." |
| ORCHESTRATION.ml_platforms.improvements | src/ORCHESTRATION/ml_platforms/improvements/__init__.py | FACADE | no | "  Init  — module for improvements functionality." (package marker) |
| ORCHESTRATION.ml_platforms.improvements.deep_learning_qlearning | src/ORCHESTRATION/ml_platforms/improvements/deep_learning_qlearning.py | DEAD | no | "Deep Learning Q-Learning Table Module — Q-Learning for deep learning framework selection with tabular state-action values (dense Q-table, experience replay, target network, double Q-learning)" |
| ORCHESTRATION.ml_platforms.improvements.enhanced_qlearning | src/ORCHESTRATION/ml_platforms/improvements/enhanced_qlearning.py | DEAD | no | "Enhanced Q-Learning Module — multi-agent Q-learning, sum-tree prioritized replay, JIT-compiled updates, Optuna auto-tuning" |
| ORCHESTRATION.ml_platforms.improvements.metrics_tracker | src/ORCHESTRATION/ml_platforms/improvements/metrics_tracker.py | SUBAPP-ENTRY | no | (not read) |
| ORCHESTRATION.ml_platforms.improvements.ml_integration | src/ORCHESTRATION/ml_platforms/improvements/ml_integration.py | DEAD | no | "Azazael ML Integration System — groups frameworks and platforms for successive computation" |
| ORCHESTRATION.ml_platforms.improvements.mlflow_integration | src/ORCHESTRATION/ml_platforms/improvements/mlflow_integration.py | DEAD | no | "Mlflow Integration — module for improvements functionality (log_params, log_metrics, start_run, end_run)." |
| ORCHESTRATION.ml_platforms.improvements.onnx_integration | src/ORCHESTRATION/ml_platforms/improvements/onnx_integration.py | DEAD | no | "ONNX Export Utilities — solves unstable ONNX export (27/27 platforms affected); unified export for any ML framework" |
| ORCHESTRATION.ml_platforms.improvements.qlearning_table | src/ORCHESTRATION/ml_platforms/improvements/qlearning_table.py | DEAD | no | "Qlearning Table — module for improvements functionality (benchmark_framework, push, sample, update_priorities)." |
| ORCHESTRATION.ml_platforms.improvements.qualitative_improvements | src/ORCHESTRATION/ml_platforms/improvements/qualitative_improvements.py | DEAD | no | "Azazael Qualitative Improvements — neural predictions, ensemble methods, real-time alerts, interactive dashboard, A/B testing, context awareness" |
| ORCHESTRATION.ml_platforms.improvements.ray_integration | src/ORCHESTRATION/ml_platforms/improvements/ray_integration.py | DEAD | no | "Ray Integration — module for improvements functionality (parallel_map, distributed_train)." |
| ORCHESTRATION.ml_platforms.improvements.strategic_intelligence | src/ORCHESTRATION/ml_platforms/improvements/strategic_intelligence.py | DEAD | no | "Azazael Strategic Intelligence System — adaptive framework selection, smart import prediction, performance profiling, auto-documentation, workflow learning" |
| ORCHESTRATION.ml_platforms.improvements.tensor_utils | src/ORCHESTRATION/ml_platforms/improvements/tensor_utils.py | DEAD | no | "Tensor Utils — module for improvements functionality (to_tensor, from_tensor, detect_framework)." |
| ORCHESTRATION.ml_platforms.improvements.vectorize_utils | src/ORCHESTRATION/ml_platforms/improvements/vectorize_utils.py | DEAD | no | "Vectorize Utils — module for improvements functionality (vmap, jit, grad, double)." |
| ORCHESTRATION.ml_platforms.improvements.weakness_testing | src/ORCHESTRATION/ml_platforms/improvements/weakness_testing.py | DEAD | no | "Azazael Comprehensive Weakness Testing & Hardening — systematically tests ML operations to find and fix weaknesses" |
| ORCHESTRATION.ml_platforms.install_improvements | src/ORCHESTRATION/ml_platforms/install_improvements.py | DEAD | no | "Install Improvements — module for ml_platforms functionality (run_pip_install, main)." |
| ORCHESTRATION.ml_platforms.install_light | src/ORCHESTRATION/ml_platforms/install_light.py | DEAD | no | "Install Light — module for ml_platforms functionality (install, main)." |
| ORCHESTRATION.ml_platforms.install_manager | src/ORCHESTRATION/ml_platforms/install_manager.py | DEAD | no | "ML Platform Installation Manager — unified installer with version compatibility, conflict resolution, and rollback support." |
| ORCHESTRATION.ml_platforms.installation_debug | src/ORCHESTRATION/ml_platforms/installation_debug.py | DEAD | no | "Installation Debug — module for ml_platforms functionality (diagnose_and_fix, check_all, check_cuda, check_tensorboard)." |
| ORCHESTRATION.ml_platforms.jax_analysis | src/ORCHESTRATION/ml_platforms/jax_analysis.py | DEAD | no | "Jax Analysis — module for ml_platforms functionality (jax_score, jax_critique, functional_composition_score)." |
| ORCHESTRATION.ml_platforms.launcher | src/ORCHESTRATION/ml_platforms/launcher.py | DEAD | no | "Launcher — module for ml_platforms functionality (main)." |
| ORCHESTRATION.ml_platforms.lm_studio_autoload | src/ORCHESTRATION/ml_platforms/lm_studio_autoload.py | DEAD | no | "Lm Studio Autoload — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.lm_studio_client | src/ORCHESTRATION/ml_platforms/lm_studio_client.py | DEAD | no | "LM Studio Local LLM Integration — connects Azazael to local LLMs via LM Studio or Ollama." |
| ORCHESTRATION.ml_platforms.lm_studio_integration | src/ORCHESTRATION/ml_platforms/lm_studio_integration.py | DEAD | no | "LM Studio Integration - Local Only — access ML platforms directly, no OpenAI, no internet needed." |
| ORCHESTRATION.ml_platforms.lm_studio_server | src/ORCHESTRATION/ml_platforms/lm_studio_server.py | DEAD | no | "Lm Studio Server — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.openinterpreter_startup | src/ORCHESTRATION/ml_platforms/openinterpreter_startup.py | DEAD | no | "Openinterpreter Startup — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.run_qanalysis | src/ORCHESTRATION/ml_platforms/run_qanalysis.py | DEAD | no | "Run Qanalysis — module for ml_platforms functionality." |
| ORCHESTRATION.ml_platforms.run_qanalysis_full | src/ORCHESTRATION/ml_platforms/run_qanalysis_full.py | DEAD | no | "Full Convergence Q-Learning Analysis — runs 100 iterations for complete convergence" |

counts: SUBAPP-ENTRY=68 DEAD=50 FACADE=13 UNCLEAR=0

## in_no_importer

The assignment asked for `in_no_importer` per row, but the fixed table header it
also specified has no column for it. Rather than drop the field, it is recorded
here as an explicit set — exhaustive, so every row in the table can be resolved.

**In the JSON's `no_importer` list (102 of 131 rows):**

`CODEX.generate_session_cain`, `CODEX.inject_cain_20260930`,
`CODEX.inject_session_cain`, `DAEMONS.check_parallax`,
`DAEMONS.install_parallax_startup`, `DAEMONS.parallax_validator`, `DOCKERZ`,
`ERRORZ`, `HYDRAMETA_UV`, `HYDRA_CONTAINER`, `META`, `META.DOCKERZ`,
`META.DebugZ`, `META.DistillZ`, `META.ERRORZ`, `META.FleetZ`, `META.HEALTHZ`,
`META.HYDRAMETA`, `META.HYDRAMETA_UV`, `META.HYDRA_CONTAINER`,
`META.InferenceBridge`, `META.METAWORMS`, `META.METAWORMS_ENRICHED`,
`META.METAWORMS_POPUP`, `META.METRICZ`, `META.OPTIMIZ`, `META.TELEMETRYZ`,
`META.TRIMZ`, `META.UVZ`, `METAWORMS_POPUP`, `MISSING_TOOLS`, `ML`,
`ML.autodiff`, `ML.dream`, `ML.evolve`, `ML.gosp`, `ML.metacog`,
`ML.torch_bridge`, `ORCHESTRATION`, `ORCHESTRATION.ADLP_FusionCore`,
`ORCHESTRATION.ADLP_MLOrchestrator`, `ORCHESTRATION.ADLP_SystemTools`,
`ORCHESTRATION.AssistantLogProtocol`,
`ORCHESTRATION.AssistantLogProtocol_Enhanced`, `ORCHESTRATION.BIBL`,
`ORCHESTRATION.BIBL.bibl_crawler`, `ORCHESTRATION.BIBL.bibl_map`,
`ORCHESTRATION.ECOSYSTEM_CRAWLER_LAUNCHER`,
`ORCHESTRATION.ECOSYSTEM_OPTIMIZER`, `ORCHESTRATION.FusionHealer`,
`ORCHESTRATION.HORUS`, `ORCHESTRATION.HORUS_LIVE_MONITOR`,
`ORCHESTRATION.HYDRA`, `ORCHESTRATION.HYDRA_ANALYZER`,
`ORCHESTRATION.HYDRA_ANALYZER_V2`, `ORCHESTRATION.INTEROPERABILITY_ANALYSIS`,
`ORCHESTRATION.MathCertainty`, `ORCHESTRATION.SelfImprovingGUI`,
`ORCHESTRATION.SystemManager`, `ORCHESTRATION.SystemManagerGUI`,
`ORCHESTRATION.TARBABY`, `ORCHESTRATION.TEST`,
`ORCHESTRATION.TEST.ECOSYSTEM_TEST`, `ORCHESTRATION.TotalFusion`,
`ORCHESTRATION.hydra_bridge`, `ORCHESTRATION.ml_platforms`,
`ORCHESTRATION.ml_platforms.auto_install`,
`ORCHESTRATION.ml_platforms.autoload`,
`ORCHESTRATION.ml_platforms.changelog`,
`ORCHESTRATION.ml_platforms.config`,
`ORCHESTRATION.ml_platforms.cross_platform_analysis`,
`ORCHESTRATION.ml_platforms.diagnostics`,
`ORCHESTRATION.ml_platforms.framework_activator`,
`ORCHESTRATION.ml_platforms.harness`,
`ORCHESTRATION.ml_platforms.health_monitor`,
`ORCHESTRATION.ml_platforms.improvements`,
`ORCHESTRATION.ml_platforms.improvements.deep_learning_qlearning`,
`ORCHESTRATION.ml_platforms.improvements.enhanced_qlearning`,
`ORCHESTRATION.ml_platforms.improvements.metrics_tracker`,
`ORCHESTRATION.ml_platforms.improvements.ml_integration`,
`ORCHESTRATION.ml_platforms.improvements.mlflow_integration`,
`ORCHESTRATION.ml_platforms.improvements.onnx_integration`,
`ORCHESTRATION.ml_platforms.improvements.qlearning_table`,
`ORCHESTRATION.ml_platforms.improvements.qualitative_improvements`,
`ORCHESTRATION.ml_platforms.improvements.ray_integration`,
`ORCHESTRATION.ml_platforms.improvements.strategic_intelligence`,
`ORCHESTRATION.ml_platforms.improvements.tensor_utils`,
`ORCHESTRATION.ml_platforms.improvements.vectorize_utils`,
`ORCHESTRATION.ml_platforms.improvements.weakness_testing`,
`ORCHESTRATION.ml_platforms.install_improvements`,
`ORCHESTRATION.ml_platforms.install_light`,
`ORCHESTRATION.ml_platforms.install_manager`,
`ORCHESTRATION.ml_platforms.installation_debug`,
`ORCHESTRATION.ml_platforms.jax_analysis`,
`ORCHESTRATION.ml_platforms.launcher`,
`ORCHESTRATION.ml_platforms.lm_studio_autoload`,
`ORCHESTRATION.ml_platforms.lm_studio_client`,
`ORCHESTRATION.ml_platforms.lm_studio_integration`,
`ORCHESTRATION.ml_platforms.lm_studio_server`,
`ORCHESTRATION.ml_platforms.openinterpreter_startup`,
`ORCHESTRATION.ml_platforms.run_qanalysis`,
`ORCHESTRATION.ml_platforms.run_qanalysis_full`

**NOT in `no_importer` (29 rows — the scanner's "test-only" bucket):**

`COMPREHENSIVE_FIX`, `ECOSYSTEM_HEALTH_CHECK`, `FILE_MANIFEST_GENERATOR`,
`HEALTHZ`, `HORUS_INTEGRATION`, `HYDRA`, `HYDRA.hydra_launcher`,
`HYDRA.hydra_protocols`, `HYDRA.ml_platforms`,
`HYDRA.ml_platforms.PERMANENT_LOAD`, `HYDRA.ml_platforms.config`,
`HYDRA.ml_platforms.harness`, `HYDRA.ml_platforms.health_monitor`,
`HYDRA.ml_platforms.launcher`, `HYDRA.ml_test`, `HYDRA.pipeline_specs`,
`HYDRAMETA`, `INTERPRETERS`, `INTERPRETERS.go_runner`,
`INTERPRETERS.rust_runner`, `METAWORMS`, `METAWORMS_ENRICHED`, `METRICZ`,
`ML.estimators`, `ML.nsga`, `ML.nsga_tuner`, `ML.step_monitor`,
`ML.trace_consolidator`, `OPTIMIZ`

> Count check: 102 + 29 = 131. An earlier draft of this section said "85 + 46";
> those labels were arithmetic I had not actually counted and they were wrong.
> The enumerated rows above are the measured sets, and they sum to the slice.
>
> The 29-row "test-only" bucket is the more interesting one. Those modules *are*
> imported (by tests, which is why the scanner left them out of `no_importer`),
> yet nothing in production reaches them — and most of them are runnable
> sub-apps whose `class` column already reads SUBAPP-ENTRY (`COMPREHENSIVE_FIX`,
> `HYDRA.hydra_launcher`, `HYDRA.ml_test`, `HYDRAMETA`, `INTERPRETERS.*`,
> `METRICZ`, `METAWORMS_ENRICHED`, `OPTIMIZ`). A module that has a `__main__` and
> is imported only by tests is a tool, not dead code; the two buckets need
> different remedies.
