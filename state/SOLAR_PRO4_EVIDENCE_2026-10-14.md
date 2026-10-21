# SOLAR PRO 4 evidence sweep — 2026-10-14

Read-only max-parallel evidence sweep over orphan + PARTIAL technique rows.
Lane owner: SOLAR PRO 4 (Buffy). Rules: engram #591 (TRI-AGENT PROTOCOL) + #599 (this lane).

## Inputs (read-only)

- `state/orphan_scan.json` — 392 orphan idents, entry_points=['CORE', 'CORE.health_server', 'ORCHESTRATION.scripts.run_tests']
- `state/ORPHAN_TRIAGE_315T.md` — coordinator-merged class for all 392 orphans
- `state/SOTA_TECHNIQUE_CODEBASE_MAP.md` — 141 technique rows; 121 PARTIAL
- `state/adoption_census.json` — 141 rows; tally={'NO-TARGET': 23, 'HOST-COMPOSED': 13, 'ADOPTED': 93, 'EXERCISE-ONLY': 12}
- whole `src/` tree (production import scan, tests excluded)

## Slice arithmetic

Per engram #599 the sweep is 392 orphans + 124 PARTIAL = 516 rows, with orphans split
201/99/52/40. On-disk reconciliation:

- Orphans: **392** in `orphan_scan.json:orphans`, all 392 carry a triage class.
  By class: SUBAPP-ENTRY=201, DEAD=99, FACADE=52, UNCLEAR=40. Matches record's 201/99/52/40.
- PARTIAL technique rows: **121** in `SOTA_TECHNIQUE_CODEBASE_MAP.md` (table rows whose coverage column = PARTIAL).

### Discrepancy noted (recorded, not resolved here)

The lane record #599 states **124 PARTIAL** (written twice: '124 PARTIAL with file-line
proof' and 'PARTIAL 124' in the slice arithmetic). The on-disk authority file
`SOTA_TECHNIQUE_CODEBASE_MAP.md` contains **121** PARTIAL table rows (its own legend
says 'PARTIAL 121'; the table has 121). The number 124 matches `adoption_census.json`
`built_count` (ADOPTED 106 + HOST-COMPOSED 8 + EXERCISEONLY 10 = 124), which is a
**different concept** (techniques that have any code) than the SOTA map's PARTIAL
count (techniques with a partial host module). The record conflated the two. This sweep
uses the authority file's actual 121 PARTIAL rows. Net: sweep covers 392 + 121 = 513
rows, not 516. The 3-row gap is a record-arithmetic issue, not a missing-data issue.

## Orphan slice (392 rows)

| ident | host_module | file | class | n_prod_call_sites | verdict | confidence |
|---|---|---|---|---|---|---|
| ANIMATION_PROTOCOLS | ANIMATION_PROTOCOLS | src\ANIMATION_PROTOCOLS.py | DEAD | 0 | DEAD | 0.9 |
| AOA | AOA | src\AOA\__init__.py | FACADE | 0 | FACADE | 0.85 |
| AOA.aoa_monitor | AOA | src\AOA\aoa_monitor.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AOA.arms | AOA | src\AOA\arms\__init__.py | FACADE | 0 | FACADE | 0.85 |
| AOA.arms.azazael_arm | AOA | src\AOA\arms\azazael_arm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.arms.codex_arm | AOA | src\AOA\arms\codex_arm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.arms.eve_arm | AOA | src\AOA\arms\eve_arm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.arms.kali_arm | AOA | src\AOA\arms\kali_arm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.arms.libra_arm | AOA | src\AOA\arms\libra_arm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.arms.support_arms | AOA | src\AOA\arms\support_arms.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.build | AOA | src\AOA\build.py | DEAD | 0 | DEAD | 0.9 |
| AOA.build_disclosure | AOA | src\AOA\build_disclosure.py | DEAD | 0 | DEAD | 0.9 |
| AOA.build_final | AOA | src\AOA\build_final.py | DEAD | 0 | DEAD | 0.9 |
| AOA.cli | AOA | src\AOA\cli\__init__.py | FACADE | 0 | FACADE | 0.85 |
| AOA.cli.aoa_cli | AOA | src\AOA\cli\aoa_cli.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AOA.conftest | AOA | src\AOA\conftest.py | DEAD | 0 | DEAD | 0.9 |
| AOA.core | AOA | src\AOA\core\__init__.py | FACADE | 0 | FACADE | 0.85 |
| AOA.core.arm_registry | AOA | src\AOA\core\arm_registry.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.core.contracts | AOA | src\AOA\core\contracts.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.core.delegation_spec | AOA | src\AOA\core\delegation_spec.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.core.event_bus | AOA | src\AOA\core\event_bus.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.core.router | AOA | src\AOA\core\router.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.core.session_manager | AOA | src\AOA\core\session_manager.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| AOA.gen_html | AOA | src\AOA\gen_html.py | DEAD | 0 | DEAD | 0.9 |
| AOA.inject | AOA | src\AOA\inject.py | DEAD | 0 | DEAD | 0.9 |
| AOA.rebuild_html | AOA | src\AOA\rebuild_html.py | DEAD | 0 | DEAD | 0.9 |
| AOA.refresh_aoa_data | AOA | src\AOA\refresh_aoa_data.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AOA.refresh_oa_data | AOA | src\AOA\refresh_oa_data.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AOA.test_arm_exports | AOA | src\AOA\test_arm_exports.py | DEAD | 0 | DEAD | 0.9 |
| AOA.test_benchmark_workflow | AOA | src\AOA\test_benchmark_workflow.py | DEAD | 0 | DEAD | 0.9 |
| AOA.test_cross_arm | AOA | src\AOA\test_cross_arm.py | DEAD | 0 | DEAD | 0.9 |
| AUTO_DOC_GENERATOR | AUTO_DOC_GENERATOR | src\AUTO_DOC_GENERATOR.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_Inference_Studio | AZAZAEL_Inference_Studio | src\AZAZAEL_Inference_Studio.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\__init__.py | FACADE | 0 | FACADE | 0.85 |
| AZAZAEL_TOOLKIT.AzazaelDynamicLogger | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\AzazaelDynamicLogger.py | DEAD | 0 | DEAD | 0.9 |
| AZAZAEL_TOOLKIT.COMPREHENSIVE_FIX | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\COMPREHENSIVE_FIX.py | SUBAPP-ENTRY | 2 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT.QL_ANALYSIS | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\QL_ANALYSIS.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT.REAL_FRAMEWORK_TEST | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\REAL_FRAMEWORK_TEST.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT.azazael_toolkit | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\azazael_toolkit.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT.environment_manager | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\environment_manager.py | DEAD | 0 | DEAD | 0.9 |
| AZAZAEL_TOOLKIT.math_certainty | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\math_certainty.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| AZAZAEL_TOOLKIT.update_docs_paths | AZAZAEL_TOOLKIT | src\AZAZAEL_TOOLKIT\update_docs_paths.py | SUBAPP-ENTRY | 0 | SUBAPP-ENTRY | 0.6 |
| AzazaelDynamicLogger | AzazaelDynamicLogger | src\AzazaelDynamicLogger.py | DEAD | 0 | DEAD | 0.9 |
| CHANGELOG_GENERATOR | CHANGELOG_GENERATOR | src\CHANGELOG_GENERATOR.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CLI | CLI | src\CLI\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CLI.azazael_cli | CLI | src\CLI\azazael_cli.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX | CODEX | src\CODEX\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CODEX_Studio | CODEX | src\CODEX\CODEX_Studio.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE | CODEX | src\CODEX\CORE\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.ANIMATION_PROTOCOLS | CODEX | src\CODEX\CORE\ANIMATION_PROTOCOLS.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.AUTO_DOC_GENERATOR | CODEX | src\CODEX\CORE\AUTO_DOC_GENERATOR.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.AUTO_DOWNLOADER | CODEX | src\CODEX\CORE\AUTO_DOWNLOADER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.CAIN_ANALYZER | CODEX | src\CODEX\CORE\CAIN_ANALYZER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.CHANGELOG_GENERATOR | CODEX | src\CODEX\CORE\CHANGELOG_GENERATOR.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.ECOSYSTEM_HEALTH_CHECK | CODEX | src\CODEX\CORE\ECOSYSTEM_HEALTH_CHECK.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.FILE_MANIFEST_GENERATOR | CODEX | src\CODEX\CORE\FILE_MANIFEST_GENERATOR.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.HORUS_INTEGRATION | CODEX | src\CODEX\CORE\HORUS_INTEGRATION.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.QL_FILE_OPTIMIZER | CODEX | src\CODEX\CORE\QL_FILE_OPTIMIZER.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.ascii_flowchart | CODEX | src\CODEX\CORE\ascii_flowchart.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.azazael_pygame | CODEX | src\CODEX\CORE\azazael_pygame.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.CORE.emoji_maker | CODEX | src\CODEX\CORE\emoji_maker.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.enhanced_animations | CODEX | src\CODEX\CORE\enhanced_animations.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.CORE.enrichment_display | CODEX | src\CODEX\CORE\enrichment_display.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.CORE.matrix_animation | CODEX | src\CODEX\CORE\matrix_animation.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.DOCUMENTATION | CODEX | src\CODEX\DOCUMENTATION\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.POPUPS.POPUP_ALL_11 | CODEX | src\CODEX\POPUPS\POPUP_ALL_11.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_BUGFREE | CODEX | src\CODEX\POPUPS\POPUP_BUGFREE.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_CLICKABLE | CODEX | src\CODEX\POPUPS\POPUP_CLICKABLE.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_DETAILED | CODEX | src\CODEX\POPUPS\POPUP_DETAILED.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_DISPLAY | CODEX | src\CODEX\POPUPS\POPUP_DISPLAY.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_IMMERSIVE | CODEX | src\CODEX\POPUPS\POPUP_IMMERSIVE.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_RICH | CODEX | src\CODEX\POPUPS\POPUP_RICH.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_SIMPLE | CODEX | src\CODEX\POPUPS\POPUP_SIMPLE.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.POPUPS.POPUP_WORKING | CODEX | src\CODEX\POPUPS\POPUP_WORKING.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.SESSION_TEMPLATE.generators.batch_generator | CODEX | src\CODEX\SESSION_TEMPLATE\generators\batch_generator.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.SESSION_TEMPLATE.generators.batch_recorder | CODEX | src\CODEX\SESSION_TEMPLATE\generators\batch_recorder.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.SESSION_TEMPLATE.generators.generate_failure_report | CODEX | src\CODEX\SESSION_TEMPLATE\generators\generate_failure_report.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.SESSION_TEMPLATE.generators.generate_session_report | CODEX | src\CODEX\SESSION_TEMPLATE\generators\generate_session_report.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.SESSION_TEMPLATE.generators.unified_generator | CODEX | src\CODEX\SESSION_TEMPLATE\generators\unified_generator.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.TESTING | CODEX | src\CODEX\TESTING\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.TESTING.INTEGRATION | CODEX | src\CODEX\TESTING\INTEGRATION\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.TESTING.INTEGRATION.test_ecosystem_integration | CODEX | src\CODEX\TESTING\INTEGRATION\test_ecosystem_integration.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.TESTING.PERFORMANCE | CODEX | src\CODEX\TESTING\PERFORMANCE\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.TESTING.PERFORMANCE.test_performance | CODEX | src\CODEX\TESTING\PERFORMANCE\test_performance.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.TESTING.UNIT | CODEX | src\CODEX\TESTING\UNIT\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.TESTING.UNIT.test_hydra | CODEX | src\CODEX\TESTING\UNIT\test_hydra.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.TESTING.UNIT.test_metaworms | CODEX | src\CODEX\TESTING\UNIT\test_metaworms.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.TESTING.UNIT.test_wormz | CODEX | src\CODEX\TESTING\UNIT\test_wormz.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.TESTING.conftest | CODEX | src\CODEX\TESTING\conftest.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.VIDEOS | CODEX | src\CODEX\VIDEOS\__init__.py | FACADE | 0 | FACADE | 0.85 |
| CODEX.VIDEOS.compress_video | CODEX | src\CODEX\VIDEOS\compress_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_azazael_educational_video | CODEX | src\CODEX\VIDEOS\create_azazael_educational_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_dual_pane_popup | CODEX | src\CODEX\VIDEOS\create_dual_pane_popup.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_dual_pane_video | CODEX | src\CODEX\VIDEOS\create_dual_pane_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_reference_video | CODEX | src\CODEX\VIDEOS\create_reference_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_scrolling_video | CODEX | src\CODEX\VIDEOS\create_scrolling_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.create_video | CODEX | src\CODEX\VIDEOS\create_video.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.VIDEOS.generate_dashboard_video | CODEX | src\CODEX\VIDEOS\generate_dashboard_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.generate_matrix_video | CODEX | src\CODEX\VIDEOS\generate_matrix_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.generate_video | CODEX | src\CODEX\VIDEOS\generate_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.generate_video_v2 | CODEX | src\CODEX\VIDEOS\generate_video_v2.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video | CODEX | src\CODEX\VIDEOS\make_video.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_docs | CODEX | src\CODEX\VIDEOS\make_video_docs.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_quad | CODEX | src\CODEX\VIDEOS\make_video_quad.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_v2 | CODEX | src\CODEX\VIDEOS\make_video_v2.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_v3 | CODEX | src\CODEX\VIDEOS\make_video_v3.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_vibrant | CODEX | src\CODEX\VIDEOS\make_video_vibrant.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_zip | CODEX | src\CODEX\VIDEOS\make_video_zip.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.make_video_zipper | CODEX | src\CODEX\VIDEOS\make_video_zipper.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.VIDEOS.progress_bar | CODEX | src\CODEX\VIDEOS\progress_bar.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.VIDEOS.video_popup | CODEX | src\CODEX\VIDEOS\video_popup.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| CODEX.build_bcc_cain_alternate | CODEX | src\CODEX\build_bcc_cain_alternate.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.cain_apply_emoji_20260930 | CODEX | src\CODEX\cain_apply_emoji_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_archetypes_all_20260930 | CODEX | src\CODEX\cain_archetypes_all_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_fill_all_20260930 | CODEX | src\CODEX\cain_fill_all_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_fill_sections_20260930 | CODEX | src\CODEX\cain_fill_sections_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_house_style_20260930 | CODEX | src\CODEX\cain_house_style_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_meta_reflect_20260930 | CODEX | src\CODEX\cain_meta_reflect_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_pecuniary_20260930 | CODEX | src\CODEX\cain_pecuniary_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_precheck_20260930 | CODEX | src\CODEX\cain_precheck_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_rebuild_final | CODEX | src\CODEX\cain_rebuild_final.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_redo | CODEX | src\CODEX\cain_redo.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_render_20260930 | CODEX | src\CODEX\cain_render_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.cain_validate_20260930 | CODEX | src\CODEX\cain_validate_20260930.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.COMPLETE_SYSTEMS_ANALYSIS | CODEX | src\CODEX\comprehensive\COMPLETE_SYSTEMS_ANALYSIS.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.FULL_ECOSYSTEM_ANALYSIS | CODEX | src\CODEX\comprehensive\FULL_ECOSYSTEM_ANALYSIS.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.GENERATE_ALL_11 | CODEX | src\CODEX\comprehensive\GENERATE_ALL_11.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.GENERATE_HTML | CODEX | src\CODEX\comprehensive\GENERATE_HTML.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.GENERATE_RICH_HTML | CODEX | src\CODEX\comprehensive\GENERATE_RICH_HTML.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.comprehensive.TWITLER_ANALYSIS | CODEX | src\CODEX\comprehensive\TWITLER_ANALYSIS.py | DEAD | 0 | DEAD | 0.9 |
| CODEX.generate_session_cain | CODEX | src\CODEX\generate_session_cain.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.inject_cain_20260930 | CODEX | src\CODEX\inject_cain_20260930.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| CODEX.inject_session_cain | CODEX | src\CODEX\inject_session_cain.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| COMPREHENSIVE_FIX | COMPREHENSIVE_FIX | src\COMPREHENSIVE_FIX.py | SUBAPP-ENTRY | 4 | SUBAPP-ENTRY | 0.9 |
| DAEMONS.check_parallax | DAEMONS | src\DAEMONS\check_parallax.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| DAEMONS.install_parallax_startup | DAEMONS | src\DAEMONS\install_parallax_startup.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| DAEMONS.parallax_validator | DAEMONS | src\DAEMONS\parallax_validator.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| DOCKERZ | DOCKERZ | src\DOCKERZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ECOSYSTEM_HEALTH_CHECK | ECOSYSTEM_HEALTH_CHECK | src\ECOSYSTEM_HEALTH_CHECK.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ERRORZ | ERRORZ | src\ERRORZ.py | SUBAPP-ENTRY | 2 | SUBAPP-ENTRY | 0.9 |
| FILE_MANIFEST_GENERATOR | FILE_MANIFEST_GENERATOR | src\FILE_MANIFEST_GENERATOR.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HEALTHZ | HEALTHZ | src\HEALTHZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HORUS_INTEGRATION | HORUS_INTEGRATION | src\HORUS_INTEGRATION.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA | HYDRA | src\HYDRA\__init__.py | FACADE | 0 | FACADE | 0.85 |
| HYDRA.hydra_launcher | HYDRA | src\HYDRA\hydra_launcher.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.hydra_protocols | HYDRA | src\HYDRA\hydra_protocols.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.ml_platforms | HYDRA | src\HYDRA\ml_platforms\__init__.py | FACADE | 0 | FACADE | 0.85 |
| HYDRA.ml_platforms.PERMANENT_LOAD | HYDRA | src\HYDRA\ml_platforms\PERMANENT_LOAD.py | DEAD | 0 | DEAD | 0.9 |
| HYDRA.ml_platforms.config | HYDRA | src\HYDRA\ml_platforms\config.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.ml_platforms.harness | HYDRA | src\HYDRA\ml_platforms\harness.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.ml_platforms.health_monitor | HYDRA | src\HYDRA\ml_platforms\health_monitor.py | FACADE | 0 | FACADE | 0.85 |
| HYDRA.ml_platforms.launcher | HYDRA | src\HYDRA\ml_platforms\launcher.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.ml_test | HYDRA | src\HYDRA\ml_test.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA.pipeline_specs | HYDRA | src\HYDRA\pipeline_specs.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRAMETA | HYDRAMETA | src\HYDRAMETA.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRAMETA_UV | HYDRAMETA_UV | src\HYDRAMETA_UV.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| HYDRA_CONTAINER | HYDRA_CONTAINER | src\HYDRA_CONTAINER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| INTERPRETERS | INTERPRETERS | src\INTERPRETERS\__init__.py | SUBAPP-ENTRY | 2 | SUBAPP-ENTRY | 0.9 |
| INTERPRETERS.go_runner | INTERPRETERS | src\INTERPRETERS\go_runner.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| INTERPRETERS.rust_runner | INTERPRETERS | src\INTERPRETERS\rust_runner.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META | META | src\META\__init__.py | FACADE | 0 | FACADE | 0.85 |
| META.DOCKERZ | META | src\META\DOCKERZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.DebugZ | META | src\META\DebugZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.DistillZ | META | src\META\DistillZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.ERRORZ | META | src\META\ERRORZ.py | SUBAPP-ENTRY | 2 | SUBAPP-ENTRY | 0.9 |
| META.FleetZ | META | src\META\FleetZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.HEALTHZ | META | src\META\HEALTHZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.HYDRAMETA | META | src\META\HYDRAMETA.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.HYDRAMETA_UV | META | src\META\HYDRAMETA_UV.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.HYDRA_CONTAINER | META | src\META\HYDRA_CONTAINER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.InferenceBridge | META | src\META\InferenceBridge.py | DEAD | 0 | DEAD | 0.9 |
| META.METAWORMS | META | src\META\METAWORMS.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.METAWORMS_ENRICHED | META | src\META\METAWORMS_ENRICHED.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.METAWORMS_POPUP | META | src\META\METAWORMS_POPUP.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.METRICZ | META | src\META\METRICZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.OPTIMIZ | META | src\META\OPTIMIZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.TELEMETRYZ | META | src\META\TELEMETRYZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.TRIMZ | META | src\META\TRIMZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| META.UVZ | META | src\META\UVZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| METAWORMS | METAWORMS | src\METAWORMS.py | FACADE | 0 | FACADE | 0.85 |
| METAWORMS_ENRICHED | METAWORMS_ENRICHED | src\METAWORMS_ENRICHED.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| METAWORMS_POPUP | METAWORMS_POPUP | src\METAWORMS_POPUP.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| METRICZ | METRICZ | src\METRICZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| MISSING_TOOLS | MISSING_TOOLS | src\MISSING_TOOLS.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ML | ML | src\ML\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ML.autodiff | ML | src\ML\autodiff.py | DEAD | 0 | DEAD | 0.9 |
| ML.dream | ML | src/ML/dream.py | FACADE | 0 | FACADE | 0.85 |
| ML.estimators | ML | src\ML\estimators.py | DEAD | 0 | DEAD | 0.9 |
| ML.evolve | ML | src/ML/evolve.py | FACADE | 0 | FACADE | 0.85 |
| ML.gosp | ML | src\ML\gosp.py | DEAD | 0 | DEAD | 0.9 |
| ML.metacog | ML | src/ML/metacog.py | FACADE | 0 | FACADE | 0.85 |
| ML.nsga | ML | src\ML\nsga.py | DEAD | 0 | DEAD | 0.9 |
| ML.nsga_tuner | ML | src\ML\nsga_tuner.py | DEAD | 0 | DEAD | 0.9 |
| ML.step_monitor | ML | src\ML\step_monitor.py | DEAD | 0 | DEAD | 0.9 |
| ML.torch_bridge | ML | src\ML\torch_bridge.py | DEAD | 0 | DEAD | 0.9 |
| ML.trace_consolidator | ML | src\ML\trace_consolidator.py | DEAD | 0 | DEAD | 0.9 |
| OPTIMIZ | OPTIMIZ | src\OPTIMIZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION | ORCHESTRATION | src\ORCHESTRATION\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ORCHESTRATION.ADLP_FusionCore | ORCHESTRATION | src\ORCHESTRATION\ADLP_FusionCore.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ADLP_MLOrchestrator | ORCHESTRATION | src\ORCHESTRATION\ADLP_MLOrchestrator.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ADLP_SystemTools | ORCHESTRATION | src\ORCHESTRATION\ADLP_SystemTools.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.AssistantLogProtocol | ORCHESTRATION | src\ORCHESTRATION\AssistantLogProtocol.py | SUBAPP-ENTRY | 4 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.AssistantLogProtocol_Enhanced | ORCHESTRATION | src\ORCHESTRATION\AssistantLogProtocol_Enhanced.py | SUBAPP-ENTRY | 4 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.BIBL | ORCHESTRATION | src\ORCHESTRATION\BIBL\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ORCHESTRATION.BIBL.bibl_crawler | ORCHESTRATION | src\ORCHESTRATION\BIBL\bibl_crawler.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.BIBL.bibl_map | ORCHESTRATION | src\ORCHESTRATION\BIBL\bibl_map.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ECOSYSTEM_CRAWLER_LAUNCHER | ORCHESTRATION | src\ORCHESTRATION\ECOSYSTEM_CRAWLER_LAUNCHER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ECOSYSTEM_OPTIMIZER | ORCHESTRATION | src\ORCHESTRATION\ECOSYSTEM_OPTIMIZER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.FusionHealer | ORCHESTRATION | src\ORCHESTRATION\FusionHealer.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.HORUS | ORCHESTRATION | src\ORCHESTRATION\HORUS.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.HORUS_LIVE_MONITOR | ORCHESTRATION | src\ORCHESTRATION\HORUS_LIVE_MONITOR.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.HYDRA | ORCHESTRATION | src\ORCHESTRATION\HYDRA.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.HYDRA_ANALYZER | ORCHESTRATION | src\ORCHESTRATION\HYDRA_ANALYZER.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.HYDRA_ANALYZER_V2 | ORCHESTRATION | src\ORCHESTRATION\HYDRA_ANALYZER_V2.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.INTEROPERABILITY_ANALYSIS | ORCHESTRATION | src\ORCHESTRATION\INTEROPERABILITY_ANALYSIS.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.MathCertainty | ORCHESTRATION | src\ORCHESTRATION\MathCertainty.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.SelfImprovingGUI | ORCHESTRATION | src\ORCHESTRATION\SelfImprovingGUI.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.SystemManager | ORCHESTRATION | src\ORCHESTRATION\SystemManager.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.SystemManagerGUI | ORCHESTRATION | src\ORCHESTRATION\SystemManagerGUI.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.TARBABY | ORCHESTRATION | src\ORCHESTRATION\TARBABY.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.TEST | ORCHESTRATION | src\ORCHESTRATION\TEST\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ORCHESTRATION.TEST.ECOSYSTEM_TEST | ORCHESTRATION | src\ORCHESTRATION\TEST\ECOSYSTEM_TEST.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.TotalFusion | ORCHESTRATION | src\ORCHESTRATION\TotalFusion.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.hydra_bridge | ORCHESTRATION | src\ORCHESTRATION\hydra_bridge.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\__init__.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.auto_install | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\auto_install.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.autoload | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\autoload.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.changelog | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\changelog.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.config | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\config.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.cross_platform_analysis | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\cross_platform_analysis.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.diagnostics | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\diagnostics.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.framework_activator | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\framework_activator.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.harness | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\harness.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.health_monitor | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\health_monitor.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ORCHESTRATION.ml_platforms.improvements.deep_learning_qlearning | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\deep_learning_qlearning.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.enhanced_qlearning | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\enhanced_qlearning.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.metrics_tracker | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\metrics_tracker.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.ml_integration | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\ml_integration.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.mlflow_integration | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\mlflow_integration.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.onnx_integration | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\onnx_integration.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.qlearning_table | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\qlearning_table.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.qualitative_improvements | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\qualitative_improvements.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.ray_integration | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\ray_integration.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.strategic_intelligence | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\strategic_intelligence.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.tensor_utils | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\tensor_utils.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.vectorize_utils | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\vectorize_utils.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.improvements.weakness_testing | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\improvements\weakness_testing.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.install_improvements | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\install_improvements.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.install_light | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\install_light.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.install_manager | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\install_manager.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.installation_debug | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\installation_debug.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.jax_analysis | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\jax_analysis.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.launcher | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\launcher.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.lm_studio_autoload | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\lm_studio_autoload.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.lm_studio_client | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\lm_studio_client.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.lm_studio_integration | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\lm_studio_integration.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.lm_studio_server | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\lm_studio_server.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.openinterpreter_startup | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\openinterpreter_startup.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.run_qanalysis | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\run_qanalysis.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.run_qanalysis_full | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\run_qanalysis_full.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.run_qanalysis_multi | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\run_qanalysis_multi.py | DEAD | 0 | DEAD | 0.9 |
| ORCHESTRATION.ml_platforms.unified_analysis | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\unified_analysis.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.universal_converter | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\universal_converter.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.ml_platforms.verify_moe | ORCHESTRATION | src\ORCHESTRATION\ml_platforms\verify_moe.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts | ORCHESTRATION | src\ORCHESTRATION\scripts\__init__.py | FACADE | 0 | FACADE | 0.85 |
| ORCHESTRATION.scripts.azazael_cli | ORCHESTRATION | src\ORCHESTRATION\scripts\azazael_cli.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.azazael_wsa | ORCHESTRATION | src\ORCHESTRATION\scripts\azazael_wsa.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.bat_analysis | ORCHESTRATION | src\ORCHESTRATION\scripts\bat_analysis.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.check_links | ORCHESTRATION | src\ORCHESTRATION\scripts\check_links.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.complete_module_analysis | ORCHESTRATION | src\ORCHESTRATION\scripts\complete_module_analysis.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.comprehensive_analysis | ORCHESTRATION | src\ORCHESTRATION\scripts\comprehensive_analysis.py | SUBAPP-ENTRY | 2 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.consistency_checker | ORCHESTRATION | src\ORCHESTRATION\scripts\consistency_checker.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.fix_syntax_errors | ORCHESTRATION | src\ORCHESTRATION\scripts\fix_syntax_errors.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.generate_docs_index | ORCHESTRATION | src\ORCHESTRATION\scripts\generate_docs_index.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.generate_docstrings | ORCHESTRATION | src\ORCHESTRATION\scripts\generate_docstrings.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.improve_bat_files | ORCHESTRATION | src\ORCHESTRATION\scripts\improve_bat_files.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.test_enhancements | ORCHESTRATION | src\ORCHESTRATION\scripts\test_enhancements.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.validate_docs | ORCHESTRATION | src\ORCHESTRATION\scripts\validate_docs.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| ORCHESTRATION.scripts.web_dashboard | ORCHESTRATION | src\ORCHESTRATION\scripts\web_dashboard.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| PSYCHE | PSYCHE | src\PSYCHE\__init__.py | FACADE | 0 | FACADE | 0.85 |
| PSYCHE.affect | PSYCHE | src\PSYCHE\affect.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| PSYCHE.artifact | PSYCHE | src\PSYCHE\artifact.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| PSYCHE.distill | PSYCHE | src\PSYCHE\distill.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| PSYCHE.evaluate | PSYCHE | src\PSYCHE\evaluate.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| PSYCHE.identify | PSYCHE | src\PSYCHE\identify.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| PSYCHE.traits | PSYCHE | src\PSYCHE\traits.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| QL_ANALYSIS | QL_ANALYSIS | src\QL_ANALYSIS.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| QL_FILE_OPTIMIZER | QL_FILE_OPTIMIZER | src\QL_FILE_OPTIMIZER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| REAL_FRAMEWORK_TEST | REAL_FRAMEWORK_TEST | src\REAL_FRAMEWORK_TEST.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS | SCRIPTS | src\SCRIPTS\__init__.py | FACADE | 0 | FACADE | 0.85 |
| SCRIPTS._reconstruct_error214 | SCRIPTS | src\SCRIPTS\_reconstruct_error214.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.auto_sync | SCRIPTS | src\SCRIPTS\auto_sync.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.bootstrap | SCRIPTS | src\SCRIPTS\bootstrap.py | DEAD | 0 | DEAD | 0.9 |
| SCRIPTS.enforce_pre_action_gate | SCRIPTS | src\SCRIPTS\enforce_pre_action_gate.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.environ_updater | SCRIPTS | src\SCRIPTS\environ_updater.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.fix_bare_excepts | SCRIPTS | src\SCRIPTS\fix_bare_excepts.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.gate_str_replace | SCRIPTS | src\SCRIPTS\gate_str_replace.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.gate_write_file | SCRIPTS | src\SCRIPTS\gate_write_file.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.gated_edit | SCRIPTS | src\SCRIPTS\gated_edit.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.generate_tool_skills | SCRIPTS | src\SCRIPTS\generate_tool_skills.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.lsp_diagnosis | SCRIPTS | src\SCRIPTS\lsp_diagnosis.py | DEAD | 0 | DEAD | 0.9 |
| SCRIPTS.monitor_learning | SCRIPTS | src\SCRIPTS\monitor_learning.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.parallel_compliance_scanner | SCRIPTS | src\SCRIPTS\parallel_compliance_scanner.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.request_auth | SCRIPTS | src\SCRIPTS\request_auth.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.run_test_generate_telemetry | SCRIPTS | src\SCRIPTS\run_test_generate_telemetry.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.session_start | SCRIPTS | src\SCRIPTS\session_start.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.session_start_check | SCRIPTS | src\SCRIPTS\session_start_check.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.sync_canonical_docs | SCRIPTS | src\SCRIPTS\sync_canonical_docs.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.sync_skills | SCRIPTS | src\SCRIPTS\sync_skills.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_auto_sync | SCRIPTS | src\SCRIPTS\test_auto_sync.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_dynamic_logging | SCRIPTS | src\SCRIPTS\test_dynamic_logging.py | DEAD | 0 | DEAD | 0.9 |
| SCRIPTS.test_generate_telemetry | SCRIPTS | src\SCRIPTS\test_generate_telemetry.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_rule_0zf_consistency | SCRIPTS | src\SCRIPTS\test_rule_0zf_consistency.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_rule_0zf_integration | SCRIPTS | src\SCRIPTS\test_rule_0zf_integration.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_rule_0zf_telemetry | SCRIPTS | src\SCRIPTS\test_rule_0zf_telemetry.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SCRIPTS.test_startup_step4_8 | SCRIPTS | src\SCRIPTS\test_startup_step4_8.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| SHORTCUTS | SHORTCUTS | src\SHORTCUTS\__init__.py | FACADE | 0 | FACADE | 0.85 |
| TELEMETRYZ | TELEMETRYZ | src\TELEMETRYZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS | TOOLS | src\TOOLS\__init__.py | FACADE | 0 | FACADE | 0.85 |
| TOOLS.AzazaelDynamicLogger | TOOLS | src\TOOLS\AzazaelDynamicLogger.py | DEAD | 0 | DEAD | 0.9 |
| TOOLS.COMPREHENSIVE_FIX | TOOLS | src\TOOLS\COMPREHENSIVE_FIX.py | DEAD | 0 | DEAD | 0.9 |
| TOOLS.PythonMapper_Quick | TOOLS | src\TOOLS\PythonMapper_Quick.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS.PythonSystemMapper | TOOLS | src\TOOLS\PythonSystemMapper.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS.PythonSystemMapper_Full | TOOLS | src\TOOLS\PythonSystemMapper_Full.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS.archive_system | TOOLS | src\TOOLS\archive_system.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS.azazael_toolkit | TOOLS | src\TOOLS\azazael_toolkit.py | DEAD | 0 | DEAD | 0.9 |
| TOOLS.debug_runner | TOOLS | src\TOOLS\debug_runner.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TOOLS.qwythos_proxy | TOOLS | src\TOOLS\qwythos_proxy.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| TRIMZ | TRIMZ | src\TRIMZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES | UTILITIES | src\UTILITIES\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.AzazaelDynamicLogger | UTILITIES | src/UTILITIES/AzazaelDynamicLogger.py | DEAD | 0 | DEAD | 0.9 |
| UTILITIES.KLINK | UTILITIES | src\UTILITIES\KLINK\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.KLINK.klink | UTILITIES | src\UTILITIES\KLINK\klink.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.Loggers | UTILITIES | src\UTILITIES\Loggers\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.PERSEPHONE | UTILITIES | src\UTILITIES\PERSEPHONE\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.PERSEPHONE.bin | UTILITIES | src\UTILITIES\PERSEPHONE\bin\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.PERSEPHONE.bin.persephone_cli | UTILITIES | src\UTILITIES\PERSEPHONE\bin\persephone_cli.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.bin.setup_wizard | UTILITIES | src\UTILITIES\PERSEPHONE\bin\setup_wizard.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.lib | UTILITIES | src\UTILITIES\PERSEPHONE\lib\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.PERSEPHONE.lib.environment | UTILITIES | src\UTILITIES\PERSEPHONE\lib\environment.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.lib.path_manager | UTILITIES | src\UTILITIES\PERSEPHONE\lib\path_manager.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.lib.sync_manager | UTILITIES | src\UTILITIES\PERSEPHONE\lib\sync_manager.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.persephone | UTILITIES | src\UTILITIES\PERSEPHONE\persephone.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.PERSEPHONE.version | UTILITIES | src\UTILITIES\PERSEPHONE\version.py | DEAD | 0 | DEAD | 0.9 |
| UTILITIES.POINDEXTER | UTILITIES | src\UTILITIES\POINDEXTER\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.POINDEXTER.POINDEXTER | UTILITIES | src\UTILITIES\POINDEXTER\POINDEXTER.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.TARBABY | UTILITIES | src\UTILITIES\TARBABY\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.TARBABY.TARBABY | UTILITIES | src\UTILITIES\TARBABY\TARBABY.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.TARBABY.tarbaby_enhanced | UTILITIES | src\UTILITIES\TARBABY\tarbaby_enhanced.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.TERENCE | UTILITIES | src\UTILITIES\TERENCE\__init__.py | FACADE | 0 | FACADE | 0.85 |
| UTILITIES.TERENCE.TERENCE | UTILITIES | src\UTILITIES\TERENCE\TERENCE.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UTILITIES.TERENCE.terence_enhanced | UTILITIES | src\UTILITIES\TERENCE\terence_enhanced.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| UVZ | UVZ | src\UVZ.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| azazael_pygame | azazael_pygame | src\azazael_pygame.py | SUBAPP-ENTRY | 4 | SUBAPP-ENTRY | 0.9 |
| azazael_toolkit | azazael_toolkit | src\azazael_toolkit.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| chain_of_action | chain_of_action | src\chain_of_action.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| enrichment_display | enrichment_display | src\enrichment_display.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| environment_manager | environment_manager | src\environment_manager.py | SUBAPP-ENTRY | 3 | SUBAPP-ENTRY | 0.9 |
| eve_unleashed | eve_unleashed | src\eve_unleashed\__init__.py | FACADE | 0 | FACADE | 0.85 |
| eve_unleashed.cache | eve_unleashed | src\eve_unleashed\cache.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.cli | eve_unleashed | src\eve_unleashed\cli.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| eve_unleashed.config | eve_unleashed | src\eve_unleashed\config.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.core | eve_unleashed | src\eve_unleashed\core.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.engine | eve_unleashed | src\eve_unleashed\engine.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.model_registry | eve_unleashed | src\eve_unleashed\model_registry.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.models | eve_unleashed | src\eve_unleashed\models\__init__.py | FACADE | 0 | FACADE | 0.85 |
| eve_unleashed.models.qwen35_ssm | eve_unleashed | src\eve_unleashed\models\qwen35_ssm.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.streaming | eve_unleashed | src\eve_unleashed\streaming.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| eve_unleashed.utils | eve_unleashed | src\eve_unleashed\utils.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| math_certainty | math_certainty | src\math_certainty.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| matrix_animation | matrix_animation | src\matrix_animation.py | UNCLEAR | 0 | UNCLEAR | 0.5 |
| memory_status | memory_status | src\memory_status.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| performance_monitor | performance_monitor | src\performance_monitor.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| persistent_memory | persistent_memory | src\persistent_memory.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| session_memory | session_memory | src\session_memory.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests | tests | src\tests\__init__.py | FACADE | 0 | FACADE | 0.85 |
| tests.test_ecosystem | tests | src\tests\test_ecosystem.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_evolution_accuracy | tests | src\tests\test_evolution_accuracy.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_learning_loop | tests | src\tests\test_learning_loop.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_autodiff | tests | src\tests\test_ml_autodiff.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_dream | tests | src\tests\test_ml_dream.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_estimators | tests | src\tests\test_ml_estimators.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_evolve | tests | src\tests\test_ml_evolve.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_gosp | tests | src\tests\test_ml_gosp.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_metacog | tests | src\tests\test_ml_metacog.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_ml_nsga | tests | src\tests\test_ml_nsga.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_nuclei_bridge | tests | src\tests\test_nuclei_bridge.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tests.test_worm_registry | tests | src\tests\test_worm_registry.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |
| tmp_verify | tmp_verify | src\tmp_verify.py | DEAD | 0 | DEAD | 0.9 |
| update_docs_paths | update_docs_paths | src\update_docs_paths.py | SUBAPP-ENTRY | 3 | SUBAPP-ENTRY | 0.9 |
| verify_all | verify_all | src\verify_all.py | SUBAPP-ENTRY | 1 | SUBAPP-ENTRY | 0.9 |

## PARTIAL EP slice (121 rows)

| ep | technique | layer | host_module | file | symbol_lines | n_prod_call_sites | confidence |
|---|---|---|---|---|---|---|
| EP34 | Chain-of-Thought Prompting | L2 | CORE.skill_library | src/CORE/skill_library.py | protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75 | 0 | 0.85 |
| EP44 | ReAct reasoning+acting | L7 | CORE.structured_action | src/CORE/structured_action.py | semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78, observe@C:\Azazael\azazael\src\CORE\structured_action.py:60 | 0 | 0.85 |
| EP63 | RWKV Linear RNN | L0 | WORMS.expansion.synapse | src/WORMS/expansion/synapse.py | — | 0 | 0.4 |
| EP80 | Jamba Hybrid Transformer-Mamba | L0 | WORMS.expansion.synapse | src/WORMS/expansion/synapse.py | — | 0 | 0.4 |
| EP97 | DeepSeek-R1 Pure-RL Reasoning | L6 | CORE.dpo_losses | src/CORE/dpo_losses.py | dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:25, rappo_filter@C:\Azazael\azazael\src\CORE\dpo_losses.py:64 | 0 | 0.85 |
| EP105 | iStar implicit step rewards | L6 | CORE.dpo_losses | src/CORE/dpo_losses.py | dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:25, rappo_filter@C:\Azazael\azazael\src\CORE\dpo_losses.py:64 | 0 | 0.85 |
| EP106 | Neuro-Symbolic Dual Paradigm | L3 | CORE.cd2_verifier | src/CORE/cd2_verifier.py | — | 0 | 0.4 |
| EP113 | LaMer Meta-RL exploration | L6 | CORE.WORMS.expansion.reflexion | src/CORE/WORMS/expansion/reflexion.py | record_reflection@C:\Azazael\azazael\src\CORE\WORMS\expansion\reflexion.py:130, reflections_for@C:\Azazael\azazael\src\CORE\WORMS\expansion\reflexion.py:212 | 0 | 0.85 |
| EP120 | Reflexion Verbal RL | L1 | CORE.local_memory | src/CORE/local_memory.py | recall_recent@C:\Azazael\azazael\src\CORE\local_memory.py:1068 | 0 | 0.85 |
| EP122 | The Four Pillars of LLM Autonomous Agents | L0 | CORE.structured_action | src/CORE/structured_action.py | observe@C:\Azazael\azazael\src\CORE\structured_action.py:60, semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78 | 0 | 0.85 |
| EP125 | SWE-agent Agent-Computer Interface | L7 | CORE.structured_action | src/CORE/structured_action.py | observe@C:\Azazael\azazael\src\CORE\structured_action.py:60, semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78, record_asil@C:\Azazael\azazael\src\CORE\structured_action.py:149 | 0 | 0.85 |
| EP129 | Agent Failure Taxonomy | L4 | CORE.circuit_breaker | src/CORE/circuit_breaker.py | CircuitBreaker@C:\Azazael\azazael\src\CORE\circuit_breaker.py:111, DeadLetter@C:\Azazael\azazael\src\CORE\circuit_breaker.py:98 | 0 | 0.85 |
| EP130 | GAP graph-based planning | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66, eliminate_common_subgraphs@C:\Azazael\azazael\src\CORE\dispatch_plan.py:210 | 0 | 0.85 |
| EP131 | MUSE self-evolving agents | L1 | CORE.local_memory | src/CORE/local_memory.py | LocalMemoryStore@C:\Azazael\azazael\src\CORE\local_memory.py:229 | 0 | 0.85 |
| EP132 | How Autonomous LLM Agents Work | L7 | CORE.structured_action | src/CORE/structured_action.py | observe@C:\Azazael\azazael\src\CORE\structured_action.py:60, semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78, record_asil@C:\Azazael\azazael\src\CORE\structured_action.py:149 | 0 | 0.85 |
| EP135 | SoK agentic skills | L2 | CORE.skill_library | src/CORE/skill_library.py | protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75, commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117, family_index@C:\Azazael\azazael\src\CORE\skill_library.py:270 | 0 | 0.85 |
| EP139 | Mamba-3 sequence modeling | L0 | CORE.WORMS.expansion.synapse | src/CORE/WORMS/expansion/synapse.py | SSMSequenceWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\synapse.py:349 | 0 | 0.85 |
| EP142 | DR-Arena deep research arena | L3 | CORE.WORMS.expansion.arena | src/CORE/WORMS/expansion/arena.py | Arena@C:\Azazael\azazael\src\CORE\WORMS\expansion\arena.py:155, Environment@C:\Azazael\azazael\src\CORE\WORMS\expansion\arena.py:64, keeper_split@C:\Azazael\azazael\src\CORE\WORMS\expansion\arena.py:310 | 0 | 0.85 |
| EP144 | Evo-Memory self-evolving memory | L1 | CORE.WORMS.expansion.engram | src/CORE/WORMS/expansion/engram.py | DreamConsolidatorWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\engram.py:629 | 0 | 0.85 |
| EP146 | InfiAgent bounded context | L1 | CORE.local_memory | src/CORE/local_memory.py | recall_recent@C:\Azazael\azazael\src\CORE\local_memory.py:1068 | 0 | 0.85 |
| EP150 | Agentic Reasoning Survey | L2 | CORE.skill_library | src/CORE/skill_library.py | family_index@C:\Azazael\azazael\src\CORE\skill_library.py:270 | 0 | 0.85 |
| EP151 | MagicGUI-RMS GUI rewards | L6 | CORE.dpo_losses | src/CORE/dpo_losses.py | dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:25, ti_dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:37, inspo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:53, rappo_filter@C:\Azazael\azazael\src\CORE\dpo_losses.py:64 | 0 | 0.85 |
| EP152 | DeepVerifier rubric verification | L3 | CORE.verification_gate | src/CORE/verification_gate.py | verify_before_accept@C:\Azazael\azazael\src\CORE\verification_gate.py:444, margin_check@C:\Azazael\azazael\src\CORE\verification_gate.py:66, divergence_gate@C:\Azazael\azazael\src\CORE\verification_gate.py:184 | 0 | 0.85 |
| EP154 | FS-Researcher file-system agents | L1 | CORE.local_memory | src/CORE/local_memory.py | LocalMemoryStore@C:\Azazael\azazael\src\CORE\local_memory.py:229 | 0 | 0.85 |
| EP155 | Agentic Proposing skill synthesis | L2 | CORE.skill_library | src/CORE/skill_library.py | — | 0 | 0.4 |
| EP156 | Agent uncertainty quantification | L3 | CORE.verification_gate | src/CORE/verification_gate.py | margin_check@C:\Azazael\azazael\src\CORE\verification_gate.py:66 | 0 | 0.85 |
| EP157 | AgentHeLLM vehicle threat taxonomy | L3 | CORE.audit_trail | src/CORE/audit_trail.py | verify_chain@C:\Azazael\azazael\src\CORE\audit_trail.py:1137 | 0 | 0.85 |
| EP160 | AgentSys Hierarchical Memory Isolation | L1/L3 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP162 | Agent Skills Survey + Governance | L2 | CORE.skill_library | src/CORE/skill_library.py | commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117 | 0 | 0.85 |
| EP168 | Agentics 2.0 transduction algebra | L7 | CORE.structured_action | src/CORE/structured_action.py | semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78 | 0 | 0.85 |
| EP169 | Agentic AI Attack/Defense Survey | L3 | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP172 | Hyperagents Self-Modification | L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | Lifecycle@C:\Azazael\azazael\src\CORE\meta_evolution.py:102, choose_candidate@C:\Azazael\azazael\src\CORE\meta_evolution.py:194, improvement_proved@C:\Azazael\azazael\src\CORE\meta_evolution.py:287 | 0 | 0.85 |
| EP178 | CMAT Latent Consensus Transformer | L5 | CORE.WORMS.expansion.consensus | src/CORE/WORMS/expansion/consensus.py | QuorumVoterWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\consensus.py:56 | 0 | 0.85 |
| EP180 | Autogenesis protocol AGP/AGS | L2/L6 | CORE.skill_library | src/CORE/skill_library.py | — | 0 | 0.4 |
| EP186 | SGDe Harness Compilation | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66, eliminate_common_subgraphs@C:\Azazael\azazael\src\CORE\dispatch_plan.py:210 | 0 | 0.85 |
| EP187 | Hive logits cache + agent-aware scheduling | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | — | 0 | 0.4 |
| EP188 | Agent-World Evolving Training Arena | L4/L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | improvement_proved@C:\Azazael\azazael\src\CORE\meta_evolution.py:287 | 0 | 0.85 |
| EP191 | ReTAS Dialectical Alignment | L3/L6 | CORE.WORMS.expansion.meta_cognition | src/CORE/WORMS/expansion/meta_cognition.py | — | 0 | 0.4 |
| EP192 | Ontology Layer as External Memory | L1/L3 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP197 | Teaching AI Agents to Plan Like Humans | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66 | 0 | 0.85 |
| EP200 | Kwai Summary Attention | L0 | CORE.WORMS.expansion.synapse | src/CORE/WORMS/expansion/synapse.py | SSMSequenceWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\synapse.py:349 | 0 | 0.85 |
| EP201 | Nautile-370M Spectral Memory | L0/L6 | CORE.cascade | src/CORE/cascade.py | CascadeRouter@C:\Azazael\azazael\src\CORE\cascade.py:26 | 0 | 0.85 |
| EP203 | Operating-Layer Controls for Onchain Agents | L3 | CORE.compliance_auditor | src/CORE/compliance_auditor.py | — | 0 | 0.4 |
| EP208 | Bayesian Orchestration for Overconfident AI Agents | L5 | CORE.cascade | src/CORE/cascade.py | — | 0 | 0.4 |
| EP209 | SAGA workflow-atomic scheduling | L5 | CORE.freethreading | src/CORE/freethreading.py | — | 0 | 0.4 |
| EP213 | Dynamic Grounding Failures in Multi-Agent Negotiation | L7 | CORE.WORMS.expansion.delegation | src/CORE/WORMS/expansion/delegation.py | — | 0 | 0.4 |
| EP214 | ARISE Data-Flow Repair Graphs | L3 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | — | 0 | 0.4 |
| EP215 | Finding specialized AI agents in milliseconds | L5 | CORE.agent_registry | src/CORE/agent_registry.py | — | 0 | 0.4 |
| EP216 | ShadowMem Long-Horizon Threat Defense | L1 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP221 | ScrapMem Optical Forgetting | L1 | CORE.data_retention | src/CORE/data_retention.py | — | 0 | 0.4 |
| EP223 | Uno-Orchestra Parsimonious Agent Routing | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | — | 0 | 0.4 |
| EP227 | FlowAgent Continuous Tool Flow | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66 | 0 | 0.85 |
| EP228 | Capability-Preserving Evolution | L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | — | 0 | 0.4 |
| EP232 | Bystander Effect in Multi-Agent Reasoning | L5 | CORE.WORMS.expansion.consensus | src/CORE/WORMS/expansion/consensus.py | — | 0 | 0.4 |
| EP233 | Fixing AI memory with backward chaining | L1 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP234 | FATE Failure-Trajectory Safety Alignment | L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | — | 0 | 0.4 |
| EP235 | SAGE Self-Evolving Graph Memory | L1 | CORE.WORMS.expansion.engram | src/CORE/WORMS/expansion/engram.py | — | 0 | 0.4 |
| EP236 | AEvo Harnessed Meta-Editing | L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | — | 0 | 0.4 |
| EP238 | SepsisAgent Clinical World Model | L4 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | rehearse_dispatch@C:\Azazael\azazael\src\CORE\dispatch_plan.py:398 | 0 | 0.85 |
| EP240 | Orchard Agentic Modeling Framework | L6 | CORE.WORMS.expansion.container | src/CORE/WORMS/expansion/container.py | — | 0 | 0.4 |
| EP242 | EXG Experience Graphs | L1 | CORE.pattern_memory | src/CORE/pattern_memory.py | query_patterns@C:\Azazael\azazael\src\CORE\pattern_memory.py:61 | 0 | 0.85 |
| EP247 | PEEK Orientation Cache | L1 | CORE.data_retention | src/CORE/data_retention.py | enforce_type_caps@C:\Azazael\azazael\src\CORE\data_retention.py:472 | 0 | 0.85 |
| EP248 | Agent JIT compilation | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66 | 0 | 0.85 |
| EP249 | Mem-pi Generative Memory | L1 | CORE.WORMS.expansion.dreaming | src/CORE/WORMS/expansion/dreaming.py | — | 0 | 0.4 |
| EP250 | Compiled subterranean agents | L2 | CORE.skill_library | src/CORE/skill_library.py | protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75 | 0 | 0.85 |
| EP253 | MACA Structure-Guided Coordination | L5 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | — | 0 | 0.4 |
| EP255 | MUSE-Autoskill Self-Evolving Skill Lifecycle | L2 | CORE.skill_library | src/CORE/skill_library.py | commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117 | 0 | 0.85 |
| EP259 | ESPO Kill Switch for reasoning | L6 | CORE.WORMS.expansion.policy_optimization | src/CORE/WORMS/expansion/policy_optimization.py | — | 0 | 0.4 |
| EP262 | SCALE Self-Improving Web Agent | L6 | CORE.neural_loop | src/CORE/neural_loop.py | structural exploration@C:\Azazael\azazael\src\CORE\neural_loop.py:97 | 0 | 0.85 |
| EP265 | SkillSmith skill/tool co-evolution | L2 | CORE.skill_library | src/CORE/skill_library.py | family_index@C:\Azazael\azazael\src\CORE\skill_library.py:270 | 0 | 0.85 |
| EP266 | ALAR adaptive latent agentic reasoning | L7 | CORE.latent_refine | src/CORE/latent_refine.py | — | 0 | 0.4 |
| EP267 | CoMAP co-evolution | L4 | CORE.WORMS.expansion.dreaming | src/CORE/WORMS/expansion/dreaming.py | dream@C:\Azazael\azazael\src\CORE\WORMS\expansion\dreaming.py:209 | 0 | 0.85 |
| EP269 | Agent libOS | L3 | CORE.compliance.` (policy, state_machine, pre_action_gate, governance) + `CORE.structured_action | src/CORE/compliance/` (policy.py, state_machine.py, pre_action_gate.py, governance.py) + `CORE/structured_action.py | — | 0 | 0.4 |
| EP270 | Reasoning Primitive Induction | L2 | CORE.skill_library | src/CORE/skill_library.py | protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75 | 0 | 0.85 |
| EP271 | Steer locked AI with Agentic Monte Carlo | L6 | CORE.WORMS.expansion.allocation | src/CORE/WORMS/expansion/allocation.py | — | 0 | 0.4 |
| EP273 | Agentic Software Paradigm | L2/L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | Lifecycle@C:\Azazael\azazael\src\CORE\meta_evolution.py:102 | 0 | 0.85 |
| EP275 | Socratic-SWE Trace-Derived Skills | L2 | CORE.skill_library | src/CORE/skill_library.py | commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117 | 0 | 0.85 |
| EP276 | ThinkBooster test-time scaling | L0/L3 | CORE.inference_pool | src/CORE/inference_pool.py | InferencePool@C:\Azazael\azazael\src\CORE\inference_pool.py:125 | 0 | 0.85 |
| EP280 | Trajectory-Refined Distillation | L6 | PSYCHE.distill | src/PSYCHE/distill.py | — | 0 | 0.4 |
| EP289 | Five-Plane Runtime Governance | L3 | CORE.compliance.policy | src/CORE/compliance/policy.py | PolicyEngine@C:\Azazael\azazael\src\CORE\compliance\policy.py:173 | 0 | 0.85 |
| EP294 | RefGRPO Reflection Calibration | L3/L6 | CORE.WORMS.expansion.learning_grpo | src/CORE/WORMS/expansion/learning_grpo.py | GRPOTrainer@C:\Azazael\azazael\src\CORE\WORMS\expansion\learning_grpo.py:64 | 0 | 0.85 |
| EP298 | LLM-as-Code Agentic Programming | L5/L4 | CORE.workflow | src/CORE/workflow.py | WorkflowEngine@C:\Azazael\azazael\src\CORE\workflow.py:574 | 0 | 0.85 |
| EP301 | VeriGraph Verifiable Data Agents | L3 | CORE.audit_trail | src/CORE/audit_trail.py | verify_inclusion_proof@C:\Azazael\azazael\src\CORE\audit_trail.py:1097 | 0 | 0.85 |
| EP302 | Transferable interaction patterns for web agents | L2 | CORE.skill_library | src/CORE/skill_library.py | family_index@C:\Azazael\azazael\src\CORE\skill_library.py:270 | 0 | 0.85 |
| EP305 | Governing Agentic AI | L3 | CORE.compliance.policy | src/CORE/compliance/policy.py | PolicyEngine@C:\Azazael\azazael\src\CORE\compliance\policy.py:173 | 0 | 0.85 |
| EP307 | ENPIRE robot self-improvement | L4/L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | choose_candidate@C:\Azazael\azazael\src\CORE\meta_evolution.py:194 | 0 | 0.85 |
| EP308 | Giving AI Agents Mathematical Muscle Memory | L2/L0 | PSYCHE.distill | src/PSYCHE/distill.py | test_theta_frozen`@C:\Azazael\azazael\src\PSYCHE\distill.py:10 | 0 | 0.85 |
| EP309 | AutoRAS robust design | L6/L3 | CORE.meta_evolution | src/CORE/meta_evolution.py | improvement_proved@C:\Azazael\azazael\src\CORE\meta_evolution.py:287 | 0 | 0.85 |
| EP313 | ARTS agentic reasoning for tree search | L4/L6 | CORE.meta_evolution | src/CORE/meta_evolution.py | improvement_proved@C:\Azazael\azazael\src\CORE\meta_evolution.py:287 | 0 | 0.85 |
| EP318 | OpenThoughts-Agent Data Recipes | L6 | CORE.WORMS.expansion.learning_pipeline | src/CORE/WORMS/expansion/learning_pipeline.py | DataPipelineWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\learning_pipeline.py:56 | 0 | 0.85 |
| EP319 | TRUSTMEM Trustworthy Consolidation | L1+L3 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP327 | Agent safety is action alignment | L3 | CORE.structured_action | src/CORE/structured_action.py | semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78 | 0 | 0.85 |
| EP335 | WorldEvolver self-evolving world models | L4+L1 | CORE.dream_arena | src/CORE/dream_arena.py | compile_world@C:\Azazael\azazael\src\CORE\dream_arena.py:28 | 0 | 0.85 |
| EP336 | ACE Adaptive Context Elasticizer | L1 | CORE.local_memory | src/CORE/local_memory.py | — | 0 | 0.4 |
| EP337 | EnvProbe budgeted probing | L4+L3 | CORE.WORMS.expansion.spine | src/CORE/WORMS/expansion/spine.py | — | 0 | 0.4 |
| EP345 | AI agents retry from pivotal mistakes | L4 | CORE.dispatch_plan | src/CORE/dispatch_plan.py | — | 0 | 0.4 |
| EP347 | Auto AGI Compiler | L2 | CORE.skill_library | src/CORE/skill_library.py | commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117 | 0 | 0.85 |
| EP349 | LLM-as-a-Verifier continuous verification | L3+L5 | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP350 | Training AI agents without live environments | L6 | CORE.rubric_evolution | src/CORE/rubric_evolution.py | gate_distillation@C:\Azazael\azazael\src\CORE\rubric_evolution.py:89 | 0 | 0.85 |
| EP351 | Direct-OPD weak-to-strong distillation | L6 | CORE.rubric_evolution | src/CORE/rubric_evolution.py | gate_distillation@C:\Azazael\azazael\src\CORE\rubric_evolution.py:89 | 0 | 0.85 |
| EP352 | Hidden states predict AI agent failure | L3 | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP354 | EvoSOP Procedure Synthesis | L2 | CORE.skill_library | src/CORE/skill_library.py | protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75 | 0 | 0.85 |
| EP355 | RL Builds Compositional Reasoning | L6 | CORE.WORMS.expansion.learning_grpo | src/CORE/WORMS/expansion/learning_grpo.py | — | 0 | 0.4 |
| EP360 | How ARMOR stops AI reasoning collapse | L6 | CORE.WORMS.expansion.learning_grpo | src/CORE/WORMS/expansion/learning_grpo.py | — | 0 | 0.4 |
| EP361 | RIPO Riemannian isometric policy optimization | L6 | CORE.WORMS.expansion.learning_grpo | src/CORE/WORMS/expansion/learning_grpo.py | — | 0 | 0.4 |
| EP362 | Agentic-DPO | L6+L7 | CORE.dpo_losses | src/CORE/dpo_losses.py | dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:25 | 0 | 0.85 |
| EP363 | LOGOS living logic | L3+L0 | CORE.skill_library | src/CORE/skill_library.py | commit_gate@C:\Azazael\azazael\src\CORE\skill_library.py:117 | 0 | 0.85 |
| EP364 | Capability trees | L5 dispatch / L2 skills | CORE.skill_library | src/CORE/skill_library.py | — | 0 | 0.4 |
| EP370 | SLEUTH epistemic working memory | L1 memory / L3 verification | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP372 | UrbanAgent multi-agent profiling | L7 interfaces / L3 verification | CORE.WORMS.expansion.consensus | src/CORE/WORMS/expansion/consensus.py | QuorumVoterWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\consensus.py:56, SplitBrainResolverWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\consensus.py:277 | 0 | 0.85 |
| EP374 | TopoAgent topological reasoning | L5 dispatch | CORE.dispatch_plan | src/CORE/dispatch_plan.py | plan_dag@C:\Azazael\azazael\src\CORE\dispatch_plan.py:66 | 0 | 0.85 |
| EP375 | MGDT multimodal KG completion | L1 memory | CORE.WORMS.expansion.synapse | src/CORE/WORMS/expansion/synapse.py | MoEDispatcherWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\synapse.py:171, AttentionRouterWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\synapse.py:478, ActivationRouterWorm@C:\Azazael\azazael\src\CORE\WORMS\expansion\synapse.py:577 | 0 | 0.85 |
| EP382 | ETAS effect-typed agent language | L3 verification / L4 execution | CORE.structured_action | src/CORE/structured_action.py | semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78 | 0 | 0.85 |
| EP383 | Safety drift + action supervision | L3 verification | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP387 | Knowledge-centric self-improvement | L1 memory / L2 skills | CORE.skill_library | src/CORE/skill_library.py | — | 0 | 0.4 |
| EP388 | LatentMT latent reasoning | L7 interfaces / L6 evolution | CORE.latent_refine | src/CORE/latent_refine.py | refine@C:\Azazael\azazael\src\CORE\latent_refine.py:80 | 0 | 0.85 |
| EP389 | Supra Cognitive Modes routed memory | L1 memory / L5 dispatch | CORE.WORMS.expansion.engram | src/CORE/WORMS/expansion/engram.py | — | 0 | 0.4 |
| EP393 | AREX self-audit research loop | L4 execution / L3 verification | CORE.audit_trail | src/CORE/audit_trail.py | — | 0 | 0.4 |
| EP394 | Agentic context management | L1 memory | CORE.data_retention | src/CORE/data_retention.py | — | 0 | 0.4 |
| EP395 | ConsistencyGate write-time admission | L1 memory / L3 verification | CORE.verification_gate | src/CORE/verification_gate.py | — | 0 | 0.4 |
| EP402 | Frozen-LLM harness control | L3 verification / L6 evolution | CORE.meta_evolution | src/CORE/meta_evolution.py | — | 0 | 0.4 |

## Spot-checks (5 per slice, hand-verified)

### Orphan spot-checks

- **AOA.aoa_monitor** (SUBAPP-ENTRY, host=AOA, file=src\AOA\aoa_monitor.py): 1 prod call sites — live sub-app; unreachable only from the 3 scanned entry points. Verdict SUBAPP-ENTRY @ 0.9.
- **ANIMATION_PROTOCOLS** (DEAD, host=ANIMATION_PROTOCOLS, file=src\ANIMATION_PROTOCOLS.py): 0 prod call sites — no __main__, no CLI, nothing but tests/docs references it. Verdict DEAD @ 0.9.
- **AOA** (FACADE, host=AOA, file=src\AOA\__init__.py): 0 prod call sites — package __init__ re-export; reachability via sibling imports. Verdict FACADE @ 0.85.
- **AOA.arms.azazael_arm** (UNCLEAR, host=AOA, file=src\AOA\arms\azazael_arm.py): 0 prod call sites — not decidable from the file alone. Verdict UNCLEAR @ 0.5.
- **AOA.arms.codex_arm** (UNCLEAR, host=AOA, file=src\AOA\arms\codex_arm.py): 0 prod call sites — not decidable from the file alone. Verdict UNCLEAR @ 0.5.

### PARTIAL spot-checks

- **EP34 Chain-of-Thought Prompting** (LL2): target=CORE/skill_library.py :: protocol_artifact, host=CORE.skill_library, file=src/CORE/skill_library.py, symbols verified: protocol_artifact@C:\Azazael\azazael\src\CORE\skill_library.py:75, 0 prod callers. Confidence 0.85. 1/1 symbols verified
- **EP44 ReAct reasoning+acting** (LL7): target=CORE/structured_action.py :: semantic_action, observe, host=CORE.structured_action, file=src/CORE/structured_action.py, symbols verified: semantic_action@C:\Azazael\azazael\src\CORE\structured_action.py:78, observe@C:\Azazael\azazael\src\CORE\structured_action.py:60, 0 prod callers. Confidence 0.85. 2/2 symbols verified
- **EP63 RWKV Linear RNN** (LL0): target=`WORMS/expansion/synapse.py :: SSMSequenceWorm`, host=WORMS.expansion.synapse, file=src/WORMS/expansion/synapse.py, symbols verified: NOT FOUND, 0 prod callers. Confidence 0.4. symbol not found in named file
- **EP80 Jamba Hybrid Transformer-Mamba** (LL0): target=`WORMS/expansion/synapse.py :: SSMSequenceWorm`, host=WORMS.expansion.synapse, file=src/WORMS/expansion/synapse.py, symbols verified: NOT FOUND, 0 prod callers. Confidence 0.4. symbol not found in named file
- **EP97 DeepSeek-R1 Pure-RL Reasoning** (LL6): target=CORE/dpo_losses.py :: dpo_loss, rappo_filter, host=CORE.dpo_losses, file=src/CORE/dpo_losses.py, symbols verified: dpo_loss@C:\Azazael\azazael\src\CORE\dpo_losses.py:25, rappo_filter@C:\Azazael\azazael\src\CORE\dpo_losses.py:64, 0 prod callers. Confidence 0.85. 2/2 symbols verified

## Method notes

- Production import scan: single bulk `rg '^(import |from )' src/ --glob '!**/tests/**'` = 0 import-statement lines, 0 distinct modules.
- Every subprocess read used `encoding='utf-8', errors='replace'` (engram #591 rule 3).
- Test-only references excluded from `prod_call_sites` by the ripgrep glob mask.
- Orphan verdict inherits the coordinator-verified triage class; this sweep adds the
  production-call-site count as the file:line evidence layer.
- A row with zero prod call sites is NOT marked ADOPTED — it stays its triage/PARTIAL
  classification with confidence reflecting the evidence strength (engram #599: unknown
  provenance is never bridged by invention).

## Owner-file note

This sweep writes ONLY `state/SOLAR_PRO4_EVIDENCE_2026-10-14.jsonl` and
`state/SOLAR_PRO4_EVIDENCE_2026-10-14.md`. No edits to opencode's files (PARTIAL/orphan
dispositions), Kilo's files (ledger/evolution), or DeepSeek's files (tools/scripts/).

Generated: 2026-10-14. Rows: 513 (orphans 392 + PARTIAL 121).