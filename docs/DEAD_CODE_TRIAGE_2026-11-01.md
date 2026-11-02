# Dead-code triage — vulture, measured 2026-11-01

The board row that asked for this said "58 findings, use `vulture --fix` for safe removals". Both halves are measured and both are wrong, so this document reports instead of removing.

## The flag does not exist

`python -m vulture --help` lists `--make-whitelist` and `--min-confidence`, and **no `--fix`**. vulture is a reporter. Any instruction to "run vulture --fix" is an instruction that cannot execute; the removal would have had to be authored by hand, one finding at a time.

## The count is a function of `--min-confidence`, and 58 is not one of its values

| min-confidence | findings |
|---|---|
| 60 | 2067 |
| 80 | 73 |
| 100 | 46 |

`--min-confidence` defaults to 0 and there is no persistent config, so "58 findings" is whatever a previous session's command produced. Quoting a bare count without its confidence is how a 2,067-item report becomes a 58-item to-do.

## What the 80% set actually is

| kind | count |
|---|---|
| unused import | 27 |
| unreachable/unsatisfiable | 23 |
| unused variable | 22 |
| other | 1 |The 100% set, measured by kind: **22 `unused variable`, 18 `unreachable code after`, 3
`unsatisfiable condition`, 2 `unreachable expression`, 1 `redundant if-condition`** — 46 total.
Only the unreachable/unsatisfiable 24 are a *proof* about a branch; the 22 unused variables
are a proof only that no *name* in the scanned files reads them, which is false the moment
something is reached by `getattr`, a decorator, or a test.

The 60% tail is 2,067 findings and **282 of them are `unused attribute`**, of which **41 are
`unused attribute 'row_factory'`** on sqlite connections — a false positive by construction,
since `row_factory` is read by the `sqlite3` module and never by a name in this tree. That is
the class where a confidence threshold silently licenses breaking working code.

## Why nothing was deleted

1. A 73-item removal in one commit is not reviewable, and the row's own acceptance test (tests passing) is not currently runnable as a gate: `.github/workflows/` never fires (local-path remote) and `.githooks/pre-commit` does not run `tests/`.2. The 60% class contains **41** `unused attribute 'row_factory'` entries on sqlite
connections (measured, `grep -c` over the 60% output) — those are false positives by
construction, so the tool's confidence number cannot be used as the removal threshold.
3. A finding is evidence, not a verdict. The verdict needs a per-item read.

## The list (80% and above), for whoever does the per-item pass

| file:line | finding | conf |
|---|---|---|
| `scripts/bcc_graphiti_temporal.py:78` | unreachable 'else' expression | 100% |
| `scripts/ddap_portal_enum.py:10` | unused import 'urljoin' | 90% |
| `scripts/ddap_portal_selenium.py:19` | unused import 'Service' | 90% |
| `scripts/meta_director.py:107` | unreachable code after 'return' | 100% |
| `scripts/modernize_types.py:27` | unused import 'TypingSet' | 90% |
| `scripts/pa_courts_pacfile_selenium.py:19` | unused import 'Service' | 90% |
| `scripts/pa_dos_entity_selenium.py:19` | unused import 'Service' | 90% |
| `scripts/pattern_catalog.py:18` | unused import 'islice' | 90% |
| `scripts/trace_adaptation.py:134` | unsatisfiable 'ternary' condition | 100% |
| `scripts/track_monitor.py:36` | unused import 'track_registry' | 90% |
| `scripts/video_frame_generator.py:19` | unused import 'draw_grid' | 90% |
| `scripts/video_frame_generator.py:19` | unused import 'draw_horizontal_gradient' | 90% |
| `src/CODEX/POPUPS/POPUP_WORKING.py:334` | unused variable 'target_fg' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_generator.py:92` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_generator.py:96` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_generator.py:102` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_generator.py:108` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_recorder.py:198` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_recorder.py:202` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_recorder.py:208` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/batch_recorder.py:214` | unreachable code after 'return' | 100% |
| `src/CODEX/SESSION_TEMPLATE/generators/unified_generator.py:5547` | unreachable code after 'return' | 100% |
| `src/CORE/azazael_logging.py:48` | unused import '_StdLogRecord' | 90% |
| `src/CORE/cd2_verifier.py:48` | unused import 'z3' | 90% |
| `src/CORE/cd3_exporter.py:95` | unused import '_SpanExportResultType' | 90% |
| `src/CORE/cd3_exporter.py:313` | unused variable 'timeout_millis' | 100% |
| `src/CORE/inference/nim_client.py:47` | unused import '_OpenAIClientType' | 90% |
| `src/CORE/inference/providers.py:1569` | unused variable 'response_data' | 100% |
| `src/CORE/logging.py:29` | unused import '_StdLogRecord' | 90% |
| `src/CORE/neural_loop.py:786` | unused variable 'expect_change' | 100% |
| `src/CORE/parallel/work_stealing.py:15` | unused import 'heapq' | 90% |
| `src/CORE/sb3_agent.py:57` | unused import '_SB3ModelT' | 90% |
| `src/CORE/sb3_agent.py:58` | unused import '_DataPipelineT' | 90% |
| `src/CORE/sb3_agent.py:58` | unused import '_ModelVersionT' | 90% |
| `src/CORE/sb3_agent.py:62` | unused import '_GymModuleT' | 90% |
| `src/CORE/threading_utils.py:56` | unused variable 'exc_val' | 100% |
| `src/CORE/threading_utils.py:57` | unused variable 'exc_tb' | 100% |
| `src/CORE/threading_utils.py:145` | unused variable 'exc_val' | 100% |
| `src/CORE/threading_utils.py:146` | unused variable 'exc_tb' | 100% |
| `src/CORE/threading_utils.py:175` | unused variable 'objtype' | 100% |
| `src/CORE/web_dashboard.py:1337` | unreachable code after 'return' | 100% |
| `src/CORE/WORMS/expansion/driver.py:211` | unreachable code after 'return' | 100% |
| `src/CORE/WORMS/expansion/jev_advisor.py:409` | unused variable 'page_all' | 100% |
| `src/CORE/WORMS/expansion/loom.py:121` | unused variable 'already_symmetric' | 100% |
| `src/CORE/WORMS/expansion/oracle.py:696` | unused variable 'era_keys' | 100% |
| `src/CORE/WORMS/expansion/schema_instruction_channel.py:12` | unused import 'get_type_hints' | 90% |
| `src/CORE/WORMS/expansion/schema_instruction_channel.py:12` | unused import 'Type' | 90% |
| `src/CORE/WORMS/expansion/security.py:111` | unused variable 'port_range' | 100% |
| `src/CORE/WORMS/expansion/servemesh.py:34` | unused import 'fabric_cap_list' | 90% |
| `src/eve_unleashed/interpreter_bridge.py:98` | unused import 'interpreter_pkg' | 90% |
| `src/META/DistillZ.py:204` | unreachable 'else' expression | 100% |
| `src/META/TELEMETRYZ.py:349` | unused variable 'module_pattern' | 100% |
| `src/ORCHESTRATION/BIBL/bibl_crawler.py:462` | unreachable code after 'return' | 100% |
| `src/ORCHESTRATION/ml_platforms/framework_activator.py:919` | unreachable code after 'return' | 100% |
| `src/ORCHESTRATION/ml_platforms/framework_activator.py:928` | unreachable code after 'return' | 100% |
| `src/ORCHESTRATION/ml_platforms/improvements/qlearning_table.py:903` | unused variable 'qlearning_path' | 100% |
| `src/ORCHESTRATION/ml_platforms/launcher.py:45` | unreachable code after 'return' | 100% |
| `src/ORCHESTRATION/scripts/generate_docstrings.py:82` | unreachable code after 'return' | 100% |
| `src/ORCHESTRATION/scripts/validate_docs.py:587` | unused variable 'base_readme' | 100% |
| `src/SCRIPTS/request_auth.py:331` | unused variable 'content_hint' | 100% |
| `src/SCRIPTS/test_generate_telemetry.py:84` | unused variable 'mock_gate' | 100% |
| `src/TELEMETRYZ.py:363` | unused variable 'module_pattern' | 100% |
| `src/TOOLS/debug_runner.py:404` | unreachable code after 'return' | 100% |
| `src/UTILITIES/PERSEPHONE/persephone.py:69` | unused import 'Azazael_VERSION' | 90% |
| `src/UTILITIES/PERSEPHONE/persephone.py:69` | unused import 'PERSEPHONE_VERSION' | 90% |
| `src/UTILITIES/PERSEPHONE/persephone.py:69` | unused import 'PROTOCOL_VERSION' | 90% |
| `tools/blender_session_20260930/blender_pebbles.py:318` | unused variable 'hair' | 100% |
| `tools/blender_session_20260930/blender_pebbles.py:382` | unused variable 'hair' | 100% |
| `tools/cain_law.py:67` | unsatisfiable 'ternary' condition | 100% |
| `tools/hook_dispatch.py:290` | redundant if-condition | 100% |
| `tools/nativestack.py:24` | unused import 'wintypes' | 90% |
| `tools/pytest_fixture_watch.py:84` | unused variable 'nextitem' | 100% |
| `tools/tree_sitter_census.py:136` | unsatisfiable 'ternary' condition | 100% |
