# Orphan worklist triage (392 rows) — coordinator-merged

Three workers each classified one disjoint slice of `state/orphan_scan.json`
(`orphans[0:130]`, `[130:261]`, `[261:392]`) against the same class vocabulary,
each writing its own part file so no two workers touched the same path. This
merges them verbatim and records what the coordinator VERIFIED afterwards.

| class | rows | meaning |
|---|---|---|
| SUBAPP-ENTRY | 201 | has `__main__` and/or argparse — a runnable app inside `src/`, unreachable only from the four shipped entry points |
| DEAD | 99 | no `__main__`, no CLI, nothing but tests/docs references it |
| FACADE | 52 | package `__init__` that only re-exports |
| UNCLEAR | 40 | not decidable from the file |
| **total** | **392** | |

**Read the largest class correctly.** 201/392 are SUBAPP-ENTRY, so
"392 orphans" is overwhelmingly *a routing and registration question*, not 392
pieces of dead code. `META/*` (18 sub-app clones), `ORCHESTRATION/ml_platforms/**`,
`AOA/**`, `CODEX/**`, `HYDRA/**` and eve_unleashed are applications that no shipped
entry point launches.

## Coordinator verification of the workers' claims

Worker 3 reported that `tools/orphan_scan.py` cannot see relative imports and
that `eve_unleashed.cache/config/core/engine` were therefore false positives.
Checked both halves:

- **The code claim is CORRECT.** `src/eve_unleashed/__init__.py:8-11` does
  `from .engine import InferenceEngine` / `from .core import ...` /
  `from .config import ...` / `from .cache import ...`.
- **The conclusion was one level off.** `eve_unleashed` (the package) is itself
  an orphan — nothing reachable imports it — and reachability is transitive from
  the entry points, so a facade's relative imports cannot confer reachability on
  its own siblings. "Unreachable" is the accurate verdict for those modules; what
  was actually wrong was the `no_importer` FLAG, which said "nothing imports
  this" when a sibling did.

**Scanner fixed anyway, because the defect was real for reachable packages:**
relative imports are now resolved (`.`, `..`, and `from . import member`).
Measured effect: import edges 13,131 -> 13,222, `no_importer` 330 -> 306,
`PERSEPHONE.lib` moved from orphan to reachable. Every control row that should
have changed, changed.

**Still invisible, by design:** a bare-name import made after a `sys.path` insert
(`sys.path.append(d); import engine`) cannot be distinguished from importing an
unrelated same-named module, so it stays out. `--dynamic` counts those files.

## Substantive findings the workers surfaced (recorded, not yet actioned)

1. **Tests under `src/` are never collected.** The suite runs `tests/`;
   `src/AOA/conftest.py` says so in its own docstring, and
   `src/AOA/test_arm_exports.py` records that it was written to prevent a
   regression that then RECURRED because it was not collected. Recorded as S11.
2. **Hardcoded absolute paths** survive in `src/AOA/rebuild_html.py`
   (`C:/Users/clint/Desktop/AOA/...`) — breaks on any other machine. S12.
3. **Duplicate modules** inflate the count: `AzazaelDynamicLogger` exists three
   times (`UTILITIES/`, `TOOLS/`, `src/`) and the two non-root copies are
   unreachable; `AOA/refresh_aoa_data.py` and `refresh_oa_data.py` are 414 lines
   each. S13.
4. **13 deprecation shims** in `CODEX/CORE/` name their canonical module in the
   docstring — a cleanup must keep the canonical target, not the shim.
5. **`META.InferenceBridge` contradicts the scanner**: it is in `no_importer`,
   but its docstring says it is consumed by `ORCHESTRATION/hydra_bridge.py`.
   Either the consumption is dynamic (invisible here) or the docstring is stale.
   Unresolved — flagged, not decided.
6. **A dangling import from the uncommitted theatre removal**: `demo_core.py:35`
   does `from CORE.PamsBusBridge import PamsBusBridge`, and
   `src/CORE/PamsBusBridge.py` is deleted in the working tree. It is inside a
   `try/except`, so it fails open — but the comment still claims it "will work if
   PAMS is available".

## Method caveats carried from the workers (do not over-read a row)

- Worker 1: `code_search` returned 0 matches for queries that certainly exist in
  this environment, so `has_main` was established by reading file heads and
  tails, not by grep. Its 24 UNCLEAR rows are internal modules of live sub-apps
  and are settled by an entry-point POLICY, not by more reading.
- Worker 2: the bulk grep hit its 250-result cap, so `has_main=no` means *not
  observed*, never *proved absent*.
- Worker 3: read every file's head AND tail, since a `__main__` guard can only
  hide at the end.
- `DEAD` from this scan means "unreachable as a module", NOT "unusable as a
  file": `run_qanalysis_multi.py`, `bootstrap.py` and `lsp_diagnosis.py` execute
  top-to-bottom at import with no guard and no CLI.

---
## Worker 1 slice

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

## Worker 2 slice

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

## Worker 3 slice

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
