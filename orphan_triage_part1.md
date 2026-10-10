# Orphan triage — part 1 of 3 (worker 1)

Slice: `orphans[0:130]` of `state/orphan_scan.json` (392 orphans total, 130 in this slice).

## Method and limits (read before using the table)

- `class` follows the coordinator's vocabulary exactly: SUBAPP-ENTRY / DEAD / FACADE / UNCLEAR.
- **`code_search` (ripgrep) is non-functional in this worker's environment** — it returned
  0 matches for every query, including patterns known to exist. So `has_main` could NOT be
  obtained by grepping for the `if __name__ == "__main__"` block, which sits at the END of
  a file. `has_main` here means: **the first 12–18 lines show an interpreter shebang
  (`#!/usr/bin/env python3`) and/or a `Usage:` block naming the file, or a CLI-parser
  import.** It is therefore evidence of script intent, not proof of a `__main__` block.
  Where the head showed none of those, `has_main` reads `no` and the row's true status may
  be a script whose entry block is below the window — those rows are marked UNCLEAR unless
  a different signal settles them.
- `in_no_importer` is a transcription of the `no_importer` array in `orphan_scan.json`.
- Paths are repo-relative. `purpose` is the module docstring's first line, verbatim or
  lightly trimmed; `(no docstring)` means the module has none (not that none was read).
- **The dominant real pattern in this slice is a SUB-APP, not dead code.** `src/AOA/`,
  `src/CODEX/`, `src/AZAZAEL_TOOLKIT/` and `src/CLI/` are self-contained applications with
  their own entry points, so every module inside them reports as unreachable from the four
  scanned entry points. This is the scan caveat stated in `STRUCTURAL_FLAWS_315T.md` S1:
  the 392 are a worklist, and for these three directories most rows are live code that the
  scan simply cannot see. `UNCLEAR` below is overwhelmingly "internal module of a live
  sub-app, no own entry point" — not a defect verdict.

| ident | file | class | has_main | purpose |
|---|---|---|---|---|
| ANIMATION_PROTOCOLS | src/ANIMATION_PROTOCOLS.py | DEAD | no | Comprehensive guide for animating results in the Azazael Ecosystem (constants only) |
| AOA | src/AOA/__init__.py | FACADE | no | AOA — Armorie-of-Anubis Umbrella Orchestrator |
| AOA.aoa_monitor | src/AOA/aoa_monitor.py | SUBAPP-ENTRY | yes | AOA live wallboard — umbrella orchestrator, full screen (argparse, --once/--refresh) |
| AOA.arms | src/AOA/arms/__init__.py | FACADE | no | AOA Arms - Adapter wrappers for all Quartet and support sub-systems |
| AOA.arms.azazael_arm | src/AOA/arms/azazael_arm.py | UNCLEAR | no | Azazael Arm - Adapter for the 77-worm neural mesh system (internal arm, relative-imported) |
| AOA.arms.codex_arm | src/AOA/arms/codex_arm.py | UNCLEAR | no | CODEX Arm - Adapter for video generation and rendering system |
| AOA.arms.eve_arm | src/AOA/arms/eve_arm.py | UNCLEAR | no | EveUnleashed Arm - Adapter for AI model selection and inferencing |
| AOA.arms.kali_arm | src/AOA/arms/kali_arm.py | UNCLEAR | no | Kali Toolchain Arm — Adapter for the Kali Linux security/OSINT toolset over WSL |
| AOA.arms.libra_arm | src/AOA/arms/libra_arm.py | UNCLEAR | no | Libra Arm - Adapter for legal document automation system |
| AOA.arms.support_arms | src/AOA/arms/support_arms.py | UNCLEAR | no | Support Arms - Adapters for infrastructure sub-systems |
| AOA.build | src/AOA/build.py | DEAD | no | (no docstring) one-shot benchmark_data.json -> HTML generator |
| AOA.build_disclosure | src/AOA/build_disclosure.py | DEAD | no | (no docstring) one-shot disclosure HTML generator |
| AOA.build_final | src/AOA/build_final.py | DEAD | no | (no docstring) one-shot HTML generator |
| AOA.cli | src/AOA/cli/__init__.py | FACADE | no | AOA CLI — Unified command-line interface for all Arms |
| AOA.cli.aoa_cli | src/AOA/cli/aoa_cli.py | SUBAPP-ENTRY | yes | AOA CLI — Unified command-line interface for the Armorie-of-Anubis (`aoa init/arms/run`) |
| AOA.conftest | src/AOA/conftest.py | DEAD | no | AOA conftest — pytest configuration (collect_ignore only) |
| AOA.core | src/AOA/core/__init__.py | FACADE | no | AOA Core — Arm Registry, EventBus, Session Manager, Cross-Arm Router |
| AOA.core.arm_registry | src/AOA/core/arm_registry.py | UNCLEAR | no | AOA Arm Registry — Registration and discovery of all neural architecture Arms |
| AOA.core.contracts | src/AOA/core/contracts.py | UNCLEAR | no | AOA typed contracts -- the provenance envelope for Arm results |
| AOA.core.delegation_spec | src/AOA/core/delegation_spec.py | UNCLEAR | no | AOA delegation spec — the 4-tuple subagent contract (AOrchestra) |
| AOA.core.event_bus | src/AOA/core/event_bus.py | UNCLEAR | no | AOA EventBus - Cross-Arm pub/sub messaging system |
| AOA.core.router | src/AOA/core/router.py | UNCLEAR | no | AOA Cross-Arm Router -- DAG-based workflow orchestration across Arms |
| AOA.core.session_manager | src/AOA/core/session_manager.py | UNCLEAR | no | AOA Session Manager - Milestone tracking and cross-session state |
| AOA.gen_html | src/AOA/gen_html.py | DEAD | no | (no docstring) one-shot HTML generator |
| AOA.inject | src/AOA/inject.py | DEAD | no | Inject additional Mermaid diagrams and content into AOA_STRUCTURE.html |
| AOA.rebuild_html | src/AOA/rebuild_html.py | DEAD | no | (no docstring) one-shot; hardcodes C:/Users/clint/Desktop/AOA/ |
| AOA.refresh_aoa_data | src/AOA/refresh_aoa_data.py | SUBAPP-ENTRY | yes | Repopulate the AOA data artifacts from the live system (shebang script) |
| AOA.refresh_oa_data | src/AOA/refresh_oa_data.py | SUBAPP-ENTRY | yes | Repopulate the AOA data artifacts from the live system (duplicate of refresh_aoa_data) |
| AOA.test_arm_exports | src/AOA/test_arm_exports.py | DEAD | no | AOA arm export regression test — never collected (lives under src/, suite runs tests/) |
| AOA.test_benchmark_workflow | src/AOA/test_benchmark_workflow.py | DEAD | no | AOA Benchmark Workflow — runnable script, explicitly ignored by AOA/conftest.py |
| AOA.test_cross_arm | src/AOA/test_cross_arm.py | DEAD | no | AOA Cross-Arm Integration Test — runnable script, ignored by conftest |
| AUTO_DOC_GENERATOR | src/AUTO_DOC_GENERATOR.py | SUBAPP-ENTRY | yes | Auto Documentation Generator (shebang) |
| AZAZAEL_Inference_Studio | src/AZAZAEL_Inference_Studio.py | SUBAPP-ENTRY | yes | AZAZAEL Inference Studio v5.0 — Professional Local Inferencing Engine (GUI app, 1734 lines) |
| AZAZAEL_TOOLKIT | src/AZAZAEL_TOOLKIT/__init__.py | FACADE | no | (no docstring) empty package init |
| AZAZAEL_TOOLKIT.AzazaelDynamicLogger | src/AZAZAEL_TOOLKIT/AzazaelDynamicLogger.py | DEAD | no | Azazael Dynamic Logger v1.0 |
| AZAZAEL_TOOLKIT.COMPREHENSIVE_FIX | src/AZAZAEL_TOOLKIT/COMPREHENSIVE_FIX.py | SUBAPP-ENTRY | yes | AZAZAEL COMPREHENSIVE FIX v1.0 (shebang) |
| AZAZAEL_TOOLKIT.QL_ANALYSIS | src/AZAZAEL_TOOLKIT/QL_ANALYSIS.py | SUBAPP-ENTRY | yes | AZAZAEL SOLUTION ANALYZER v1.0 — Q-Learning analysis of fix strategies (shebang) |
| AZAZAEL_TOOLKIT.REAL_FRAMEWORK_TEST | src/AZAZAEL_TOOLKIT/REAL_FRAMEWORK_TEST.py | SUBAPP-ENTRY | yes | AZAZAEL REAL FRAMEWORK TEST v1.0 (shebang) |
| AZAZAEL_TOOLKIT.azazael_toolkit | src/AZAZAEL_TOOLKIT/azazael_toolkit.py | SUBAPP-ENTRY | yes | AZAZAEL TOOLKIT - MASTER LAUNCHER v1.0 (shebang) |
| AZAZAEL_TOOLKIT.environment_manager | src/AZAZAEL_TOOLKIT/environment_manager.py | DEAD | no | Azazael Environment Manager v2.0 |
| AZAZAEL_TOOLKIT.math_certainty | src/AZAZAEL_TOOLKIT/math_certainty.py | SUBAPP-ENTRY | yes | MATHEMATICAL CERTAINTY CALCULATOR — binary comparison analysis (shebang) |
| AZAZAEL_TOOLKIT.update_docs_paths | src/AZAZAEL_TOOLKIT/update_docs_paths.py | SUBAPP-ENTRY | yes | Documentation Updater - Updates all paths for C:\Azazael migration (shebang) |
| AzazaelDynamicLogger | src/AzazaelDynamicLogger.py | DEAD | no | Azazael Dynamic Logger v1.0 (near-duplicate of AZAZAEL_TOOLKIT copy) |
| CHANGELOG_GENERATOR | src/CHANGELOG_GENERATOR.py | SUBAPP-ENTRY | yes | Change Log Generator (shebang; canonical source for the CODEX shim) |
| CLI | src/CLI/__init__.py | FACADE | no | Azazael CLI - Command-line interface for ecosystem. |
| CLI.azazael_cli | src/CLI/azazael_cli.py | SUBAPP-ENTRY | yes | AZAZAEL CLI v1 - Terminal Interface for Azazael Ecosystem (interactive CLI) |
| CODEX | src/CODEX/__init__.py | FACADE | no | Azazael CODEX - Documentation and reference archive. |
| CODEX.CODEX_Studio | src/CODEX/CODEX_Studio.py | SUBAPP-ENTRY | yes | CODEX Studio — Standalone Desktop Application, HTML → MP4/WMV (GUI + --cli) |
| CODEX.CORE | src/CODEX/CORE/__init__.py | FACADE | no | (no docstring) empty package init |
| CODEX.CORE.ANIMATION_PROTOCOLS | src/CODEX/CORE/ANIMATION_PROTOCOLS.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/ANIMATION_PROTOCOLS.py |
| CODEX.CORE.AUTO_DOC_GENERATOR | src/CODEX/CORE/AUTO_DOC_GENERATOR.py | SUBAPP-ENTRY | yes | Auto Documentation Generator (shebang; copy of the root module) |
| CODEX.CORE.AUTO_DOWNLOADER | src/CODEX/CORE/AUTO_DOWNLOADER.py | SUBAPP-ENTRY | yes | AZAZAEL Auto-Downloader Module — persistent ML framework installer (shebang) |
| CODEX.CORE.CAIN_ANALYZER | src/CODEX/CORE/CAIN_ANALYZER.py | SUBAPP-ENTRY | yes | CAIN_ANALYZER — Standalone CLI for the CAIN Psychoanalysis Framework |
| CODEX.CORE.CHANGELOG_GENERATOR | src/CODEX/CORE/CHANGELOG_GENERATOR.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/CHANGELOG_GENERATOR.py |
| CODEX.CORE.ECOSYSTEM_HEALTH_CHECK | src/CODEX/CORE/ECOSYSTEM_HEALTH_CHECK.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/ECOSYSTEM_HEALTH_CHECK.py |
| CODEX.CORE.FILE_MANIFEST_GENERATOR | src/CODEX/CORE/FILE_MANIFEST_GENERATOR.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/FILE_MANIFEST_GENERATOR.py |
| CODEX.CORE.HORUS_INTEGRATION | src/CODEX/CORE/HORUS_INTEGRATION.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/HORUS_INTEGRATION.py |
| CODEX.CORE.QL_FILE_OPTIMIZER | src/CODEX/CORE/QL_FILE_OPTIMIZER.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/QL_FILE_OPTIMIZER.py |
| CODEX.CORE.ascii_flowchart | src/CODEX/CORE/ascii_flowchart.py | SUBAPP-ENTRY | yes | Azazael ASCII Flowchart Generator (shebang) |
| CODEX.CORE.azazael_pygame | src/CODEX/CORE/azazael_pygame.py | UNCLEAR | no | Azazael Visualizer - PyGame Version (GUI app; no shebang/CLI in head) |
| CODEX.CORE.emoji_maker | src/CODEX/CORE/emoji_maker.py | SUBAPP-ENTRY | yes | Azazael Dynamic Emotional Emoji Generator (shebang) |
| CODEX.CORE.enhanced_animations | src/CODEX/CORE/enhanced_animations.py | SUBAPP-ENTRY | yes | Azazael Enhanced CSS Animations — 30+ animations by category (shebang) |
| CODEX.CORE.enrichment_display | src/CODEX/CORE/enrichment_display.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/enrichment_display.py |
| CODEX.CORE.matrix_animation | src/CODEX/CORE/matrix_animation.py | FACADE | no | DEPRECATION SHIM — re-exports canonical src/matrix_animation.py |
| CODEX.DOCUMENTATION | src/CODEX/DOCUMENTATION/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.POPUPS.POPUP_ALL_11 | src/CODEX/POPUPS/POPUP_ALL_11.py | UNCLEAR | no | POPUP - ALL 11 Azazael SYSTEMS (tkinter dialog) |
| CODEX.POPUPS.POPUP_BUGFREE | src/CODEX/POPUPS/POPUP_BUGFREE.py | UNCLEAR | no | Bug-free popup display (tkinter dialog) |
| CODEX.POPUPS.POPUP_CLICKABLE | src/CODEX/POPUPS/POPUP_CLICKABLE.py | UNCLEAR | no | Azazael Popup - Clickable with Details (tkinter dialog) |
| CODEX.POPUPS.POPUP_DETAILED | src/CODEX/POPUPS/POPUP_DETAILED.py | UNCLEAR | no | Azazael Ecosystem - Clean Informative Popup (tkinter dialog) |
| CODEX.POPUPS.POPUP_DISPLAY | src/CODEX/POPUPS/POPUP_DISPLAY.py | UNCLEAR | no | HYDRA Cluster Results Popup (tkinter dialog) |
| CODEX.POPUPS.POPUP_IMMERSIVE | src/CODEX/POPUPS/POPUP_IMMERSIVE.py | UNCLEAR | no | Azazael IMMERSIVE POPUP (tkinter dialog) |
| CODEX.POPUPS.POPUP_RICH | src/CODEX/POPUPS/POPUP_RICH.py | UNCLEAR | no | Rich graphics popup display (tkinter dialog) |
| CODEX.POPUPS.POPUP_SIMPLE | src/CODEX/POPUPS/POPUP_SIMPLE.py | UNCLEAR | no | Simple popup display for results (tkinter dialog) |
| CODEX.POPUPS.POPUP_WORKING | src/CODEX/POPUPS/POPUP_WORKING.py | UNCLEAR | no | Azazael Ecosystem - Working Clickable Popup (tkinter dialog) |
| CODEX.SESSION_TEMPLATE.generators.batch_generator | src/CODEX/SESSION_TEMPLATE/generators/batch_generator.py | SUBAPP-ENTRY | yes | Batch Template Generator - run templates individually, in multiples, or all |
| CODEX.SESSION_TEMPLATE.generators.batch_recorder | src/CODEX/SESSION_TEMPLATE/generators/batch_recorder.py | SUBAPP-ENTRY | yes | Batch Recorder - record templates to MP4 individually or all |
| CODEX.SESSION_TEMPLATE.generators.generate_failure_report | src/CODEX/SESSION_TEMPLATE/generators/generate_failure_report.py | SUBAPP-ENTRY | yes | Automated Failure Report Generator with vertical scroll layout (shebang) |
| CODEX.SESSION_TEMPLATE.generators.generate_session_report | src/CODEX/SESSION_TEMPLATE/generators/generate_session_report.py | SUBAPP-ENTRY | yes | Automated Session Report Generator - Video Production Techniques Style (shebang) |
| CODEX.SESSION_TEMPLATE.generators.unified_generator | src/CODEX/SESSION_TEMPLATE/generators/unified_generator.py | SUBAPP-ENTRY | yes | Unified Generator - HTML reports in 9 consequence template styles (5577 lines) |
| CODEX.TESTING | src/CODEX/TESTING/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.TESTING.INTEGRATION | src/CODEX/TESTING/INTEGRATION/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.TESTING.INTEGRATION.test_ecosystem_integration | src/CODEX/TESTING/INTEGRATION/test_ecosystem_integration.py | DEAD | no | Integration Tests for Azazael Ecosystem — not collected (under src/, not tests/) |
| CODEX.TESTING.PERFORMANCE | src/CODEX/TESTING/PERFORMANCE/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.TESTING.PERFORMANCE.test_performance | src/CODEX/TESTING/PERFORMANCE/test_performance.py | DEAD | no | Performance Benchmarks for Azazael Ecosystem — not collected |
| CODEX.TESTING.UNIT | src/CODEX/TESTING/UNIT/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.TESTING.UNIT.test_hydra | src/CODEX/TESTING/UNIT/test_hydra.py | DEAD | no | Unit Tests for HYDRA — not collected |
| CODEX.TESTING.UNIT.test_metaworms | src/CODEX/TESTING/UNIT/test_metaworms.py | DEAD | no | Unit Tests for METAWORMS — not collected |
| CODEX.TESTING.UNIT.test_wormz | src/CODEX/TESTING/UNIT/test_wormz.py | DEAD | no | Unit Tests for WORMZ — not collected |
| CODEX.TESTING.conftest | src/CODEX/TESTING/conftest.py | DEAD | no | Unit Test Configuration and Conftest — not collected |
| CODEX.VIDEOS | src/CODEX/VIDEOS/__init__.py | FACADE | no | (comment only) empty package init |
| CODEX.VIDEOS.compress_video | src/CODEX/VIDEOS/compress_video.py | SUBAPP-ENTRY | yes | Azazael Video Compressor - optimized encoding pipeline (shebang, Usage) |
| CODEX.VIDEOS.create_azazael_educational_video | src/CODEX/VIDEOS/create_azazael_educational_video.py | SUBAPP-ENTRY | yes | Azazael Educational Video Generator v1.0 (shebang) |
| CODEX.VIDEOS.create_dual_pane_popup | src/CODEX/VIDEOS/create_dual_pane_popup.py | SUBAPP-ENTRY | yes | Dual-Pane Popup Display for Azazael Cluster (Usage: python <file>) |
| CODEX.VIDEOS.create_dual_pane_video | src/CODEX/VIDEOS/create_dual_pane_video.py | SUBAPP-ENTRY | yes | Dual-Pane Video Generator for Azazael Ecosystem (Usage: python <file>) |
| CODEX.VIDEOS.create_reference_video | src/CODEX/VIDEOS/create_reference_video.py | SUBAPP-ENTRY | yes | Azazael Documentation Video Generator (shebang) |
| CODEX.VIDEOS.create_scrolling_video | src/CODEX/VIDEOS/create_scrolling_video.py | SUBAPP-ENTRY | yes | Azazael Reference Scrolling Video Generator (shebang) |
| CODEX.VIDEOS.create_video | src/CODEX/VIDEOS/create_video.py | UNCLEAR | no | MP4 Video Generator for Azazael Ecosystem Overview (moviepy/ffmpeg; no shebang in head) |
| CODEX.VIDEOS.generate_dashboard_video | src/CODEX/VIDEOS/generate_dashboard_video.py | SUBAPP-ENTRY | yes | CODEX Dashboard Video Generator v2.0 (shebang, 1227 lines) |
| CODEX.VIDEOS.generate_matrix_video | src/CODEX/VIDEOS/generate_matrix_video.py | SUBAPP-ENTRY | yes | Azazael Matrix-Style Video Generator (shebang) |
| CODEX.VIDEOS.generate_video | src/CODEX/VIDEOS/generate_video.py | SUBAPP-ENTRY | yes | Azazael Technical Video Generator (shebang) |
| CODEX.VIDEOS.generate_video_v2 | src/CODEX/VIDEOS/generate_video_v2.py | SUBAPP-ENTRY | yes | Azazael Dynamic Video Generator v2.0 (shebang) |
| CODEX.VIDEOS.make_video | src/CODEX/VIDEOS/make_video.py | SUBAPP-ENTRY | yes | Azazael Scrolling Video Generator (shebang) |
| CODEX.VIDEOS.make_video_docs | src/CODEX/VIDEOS/make_video_docs.py | SUBAPP-ENTRY | yes | Azazael Reference Video - Double Column Scrolling (shebang) |
| CODEX.VIDEOS.make_video_quad | src/CODEX/VIDEOS/make_video_quad.py | SUBAPP-ENTRY | yes | Azazael 4-Quadrant Scrolling Video - Vibrant & Whimsical (shebang) |
| CODEX.VIDEOS.make_video_v2 | src/CODEX/VIDEOS/make_video_v2.py | SUBAPP-ENTRY | yes | Azazael Scrolling Video Generator - Enhanced Version (shebang) |
| CODEX.VIDEOS.make_video_v3 | src/CODEX/VIDEOS/make_video_v3.py | SUBAPP-ENTRY | yes | Azazael Scrolling Video - Full Screen Double Column Version (shebang) |
| CODEX.VIDEOS.make_video_vibrant | src/CODEX/VIDEOS/make_video_vibrant.py | SUBAPP-ENTRY | yes | Azazael Reference Video - Vibrant Single Column (shebang, 1427 lines) |
| CODEX.VIDEOS.make_video_zip | src/CODEX/VIDEOS/make_video_zip.py | SUBAPP-ENTRY | yes | Azazael Video - Big Keywords Zipper Pattern (shebang) |
| CODEX.VIDEOS.make_video_zipper | src/CODEX/VIDEOS/make_video_zipper.py | SUBAPP-ENTRY | yes | Azazael Scrolling Video - Interleaved Zipper Double Column (shebang) |
| CODEX.VIDEOS.progress_bar | src/CODEX/VIDEOS/progress_bar.py | DEAD | no | CODEX Progress Bar — ffmpeg progress wrapper; imported as a library (`from progress_bar import ...`) |
| CODEX.VIDEOS.video_popup | src/CODEX/VIDEOS/video_popup.py | UNCLEAR | no | (no docstring) tkinter video popup, 31 lines |
| CODEX.build_bcc_cain_alternate | src/CODEX/build_bcc_cain_alternate.py | SUBAPP-ENTRY | yes | Build BCC-populated CAIN analysis — all template sections replaced with BCC data |
| CODEX.cain_apply_emoji_20260930 | src/CODEX/cain_apply_emoji_20260930.py | DEAD | no | Adopt my own emoji — template emoji replaced with session's own (one-shot) |
| CODEX.cain_archetypes_all_20260930 | src/CODEX/cain_archetypes_all_20260930.py | DEAD | no | Every archetype, every field, analysed to my behaviour (one-shot) |
| CODEX.cain_fill_all_20260930 | src/CODEX/cain_fill_all_20260930.py | DEAD | no | Fill EVERY remaining slot. Counts measured, not asserted (one-shot) |
| CODEX.cain_fill_sections_20260930 | src/CODEX/cain_fill_sections_20260930.py | DEAD | no | Fill ALL 28 h2 sections. Denominator is the TEMPLATE'S OWN (one-shot) |
| CODEX.cain_house_style_20260930 | src/CODEX/cain_house_style_20260930.py | DEAD | no | Conform my archetypes to house style (one-shot) |
| CODEX.cain_meta_reflect_20260930 | src/CODEX/cain_meta_reflect_20260930.py | DEAD | no | META REFLECT — what is mine vs what the template asserted (one-shot) |
| CODEX.cain_pecuniary_20260930 | src/CODEX/cain_pecuniary_20260930.py | DEAD | no | PECUNIARY LOSS — rederived from scratch. NO CAIN INPUTS USED (one-shot) |
| CODEX.cain_precheck_20260930 | src/CODEX/cain_precheck_20260930.py | DEAD | no | Double-check the analysis against the record, then render to MP4 (one-shot) |
| CODEX.cain_rebuild_final | src/CODEX/cain_rebuild_final.py | DEAD | no | One clean pass: template in, filled document out (one-shot) |
| CODEX.cain_redo | src/CODEX/cain_redo.py | DEAD | no | Rebuild the analysis. One pass, from the template (one-shot) |
| CODEX.cain_render_20260930 | src/CODEX/cain_render_20260930.py | DEAD | no | Fix the span, add scroll-driven reveals, then record the standard (one-shot) |
| CODEX.cain_validate_20260930 | src/CODEX/cain_validate_20260930.py | DEAD | no | Validate the rendered document — structural, encoding, content (one-shot) |
| CODEX.comprehensive.COMPLETE_SYSTEMS_ANALYSIS | src/CODEX/comprehensive/COMPLETE_SYSTEMS_ANALYSIS.py | DEAD | no | COMPLETE Azazael ECOSYSTEM SYSTEMS ANALYSIS (one-shot report generator) |
| CODEX.comprehensive.FULL_ECOSYSTEM_ANALYSIS | src/CODEX/comprehensive/FULL_ECOSYSTEM_ANALYSIS.py | DEAD | no | FULL Azazael ECOSYSTEM ANALYSIS (one-shot; paths are 2026-02-11 snapshots) |
| CODEX.comprehensive.GENERATE_ALL_11 | src/CODEX/comprehensive/GENERATE_ALL_11.py | DEAD | no | COMPLETE Azazael ECOSYSTEM - ALL SYSTEMS (one-shot) |
| CODEX.comprehensive.GENERATE_HTML | src/CODEX/comprehensive/GENERATE_HTML.py | DEAD | no | COMPREHENSIVE Azazael ECOSYSTEM - HTML REPORT (one-shot) |
| CODEX.comprehensive.GENERATE_RICH_HTML | src/CODEX/comprehensive/GENERATE_RICH_HTML.py | DEAD | no | COMPLETE Azazael ECOSYSTEM - RICH HTML REPORT (one-shot; module-level def only) |
| CODEX.comprehensive.TWITLER_ANALYSIS | src/CODEX/comprehensive/TWITLER_ANALYSIS.py | DEAD | no | TWITLER - System Information & Notification System (one-shot data dict) |

counts: SUBAPP-ENTRY=45 DEAD=39 FACADE=22 UNCLEAR=24

## What this slice says beyond its own rows

1. **The largest single class is SUBAPP-ENTRY (45/130)** — and they are real, self-contained
   applications: CODEX Studio (GUI + `--cli`), the 21 `CODEX/VIDEOS` generators, the 9
   tkinter popups, the CAIN one-shot scripts, AZAZAEL_Inference_Studio (1734 lines), the AOA
   CLI and monitor, the AZAZAEL_TOOLKIT launchers. Treating these as "orphaned" is the
   scan's entry-point choice, not a defect in them.
2. **13 rows are explicit DEPRECATION SHIMs** in `CODEX/CORE/` (ANIMATION_PROTOCOLS,
   CHANGELOG_GENERATOR, ECOSYSTEM_HEALTH_CHECK, FILE_MANIFEST_GENERATOR, HORUS_INTEGRATION,
   QL_FILE_OPTIMIZER, enrichment_display, matrix_animation) whose docstrings name the
   canonical module they re-export. Those canonical modules are root-level (`src/*.py`), and
   six of that root set also appears in this slice's dependency chain — so the shims exist
   precisely so old `CODEX.CORE.*` import paths keep working. Any "remove the duplicate"
   action must keep the canonical target, not the shim.
3. **A repeated real defect: five test files under `src/` are never collected.** `AOA/conftest.py`
   says so in its own docstring (it `collect_ignore`s two of them), and `CODEX/TESTING/*`
   holds six more under `src/` while the suite runs `tests/`. One of them,
   `AOA/test_arm_exports.py`, documents in its docstring that it was written to prevent a
   regression that then recurred because the test was not collected.
4. **`AOA/refresh_aoa_data.py` and `AOA/refresh_oa_data.py` are duplicates** (identical
   docstrings, 414 lines each); likewise `AzazaelDynamicLogger` exists twice (root and
   `AZAZAEL_TOOLKIT/`), and `AUTO_DOC_GENERATOR`/`emoji_maker`/`enhanced_animations` exist
   both at root and under `CODEX/CORE/`. Duplicates inflate the orphan count.
5. **Hardcoded absolute paths remain in three rows**: `AOA/rebuild_html.py`
   (`C:/Users/clint/Desktop/AOA/benchmark_data.json`), and `AOA/arms/codex_arm.py` /
   `AOA/arms/eve_arm.py` (`Path.home()/'azazael'/...` and `Path.home()/"Desktop"/"EveUnleashed_Selector"`),
   which will resolve to the wrong place on any other machine or user.

## Not classified / needs a second look

- The 24 UNCLEAR rows are almost all **internal modules of a live sub-app** (AOA core/arms,
  the 9 tkinter popups, `create_video`, `video_popup`, `azazael_pygame`). They have no own
  entry point and no importer visible to the scan, but they are reachable within their app.
  The decision that would settle them is a sub-app entry-point policy, not more reading.
- `has_main` for every row in this file rests on a head read (12–18 lines) because
  `code_search` was unavailable; a grep-capable run would firm up the ~24 UNCLEAR rows.
- Two rows could not be checked for a `__main__` block at all and were judged on docstring
  and structure: `CODEX.VIDEOS.video_popup` (31 lines, no docstring) and
  `CODEX.comprehensive.GENERATE_RICH_HTML` (module-level `def generate_rich_html()` only).
