# Graph Report - azazael\output\graphify_atlas\vermillion_lightfury  (2026-08-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 724 nodes · 1083 edges · 51 communities (42 shown, 9 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 107 edges (avg confidence: 0.64)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7a6494dc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]

## God Nodes (most connected - your core abstractions)
1. `KaliHealth` - 40 edges
2. `MetasploitBridge` - 29 edges
3. `NmapScanner` - 29 edges
4. `ThreadSafeWormMixin` - 27 edges
5. `WSLRecovery` - 26 edges
6. `KaliUnresponsiveError` - 16 edges
7. `TestF11MixedSlashRegex` - 15 edges
8. `SharedDirManager` - 14 edges
9. `BenchmarkWorm` - 14 edges
10. `DriveStatus` - 13 edges

## Surprising Connections (you probably didn't know these)
- `NmapScanner` --conceptually_related_to--> `Quartet Architecture`  [INFERRED]
  worms/nmap_scanner.py → ARCHITECTURE_CONTEXT.txt
- `test_F9_f11_regex_catches_canonical_bug_rejects_safe_code()` --calls--> `has_f11_anti_pattern()`  [INFERRED]
  tests/test_full_execution_smoke.py → config/f11_patterns.py
- `SharedDirManager` --uses--> `WSLRecovery`  [INFERRED]
  config/shared_dir.py → worms/wsl_recovery.py
- `SharedDirManager` --uses--> `KaliUnresponsiveError`  [INFERRED]
  config/shared_dir.py → worms/exceptions.py
- `test_F8_shared_dir_manager_ensure_directories_returns_dict_with_int_counts()` --calls--> `SharedDirManager`  [INFERRED]
  tests/test_full_execution_smoke.py → config/shared_dir.py

## Communities (51 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (39): Verify Kali WSL is reachable. Attempts auto-recovery if not.          Shared ded, verify_kali_responsive(), Exception, NmapHost.open_port_count returns the count of ports with state='open'., test_D6b_NmapHost_open_port_count(), KaliUnresponsiveError, Raised when Kali WSL is unresponsive and auto-recovery failed.      All worms th, BaseWormMixin (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (22): BaseWormMixin, main(), A single recovery action performed., Complete WSL recovery assessment., Worm that monitors and recovers WSL2 distros.      Integrates with:     - KaliHe, Execute a command inside a WSL distro. Direct when native+Kali, WSL wrapper othe, Execute a Windows command (wsl.exe management commands).          On Kali WSL, b, Parse 'wsl --list --verbose' output into a dict of distro info. (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (21): main(), MetasploitBridge, Active Metasploit session., Worm that executes Metasploit exploits inside Kali WSL from Windows Azazael., Execute a command on Kali. Direct when running natively, WSL wrapper from Window, Verify Kali WSL is reachable. Attempts auto-recovery if not.          Delegates, Delete .rc resource scripts older than max_age_hours from shared dir.          D, Record to PAMS memory. (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (20): BaseWormMixin, KaliHealth, KaliHealthStatus, main(), Complete Kali health assessment., Worm that monitors Kali WSL health across all three dimensions:     host drive s, Load previous health check history., Save health check history. (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (28): fake_wsl_output(), _fresh_pillars(), _install_happy_pillars(), _install_stopped_ubuntu_pillars(), Build a list of (Pillar-instance, path-or-probe) tuples pointing at     tmp_path, Replace `mod.ALL_PILLARS` with a tuple of tmp-path fixtures and stub     the WSL, Same fixture layout as _install_happy_pillars but with UBUNTU     bridge=False (, Start all patches, call main(args), stop in finally. Returns rc. (+20 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (35): benchmark_completed, benchmark_started, avg_ms, error, function, max_ms, min_ms, module (+27 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (30): purge_stale_rc_scripts(), Module-level PAMS recorder for purge_stale_rc_scripts() (Phase 11.3 N2 nit)., Delete .rc resource scripts older than max_age_hours from a directory.      Shar, _record_pams_purge(), ``purge_stale_rc_scripts`` on a nonexistent log_dir returns 0 (int)., test_F7_purge_stale_rc_scripts_handles_nonexistent_log_dir(), fresh_rc(), no_pams() (+22 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (24): ``ensure_directories`` returns a dict with int counts (created/existing/failed), ``has_f11_anti_pattern`` catches the F11 canonical bug, rejects safe f-strings., ``regression_guard --help`` exposes ``--exclude-functions`` + ``--explain-exclud, ``benchmark_all`` produces a valid benchmark_history entry on append-history run, ``worms.__init__`` re-exports all 6 public names., ``exceptions.KaliUnresponsiveError`` importable + instantiable., NmapScanner constructs + allocates ``self._lock`` via mixin chain., KaliHealth constructs + allocates ``self._lock``. (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.11
Nodes (22): _concurrent_instantiate(), T1: 10 threads barrier-sync-instantiate ``class_name``. All must succeed., T2: No two of the 50 concurrently-constructed instances share a `_lock`.      Th, T3: barrier-sync 50 workers, then verify each recorded a unique ``ident``., T4: Wall-clock budget. Exceeding 3 s for 50 instantiations is the deadlock     o, T5: After the barrier race, sequential instantiation must yield fresh     ``_loc, T6: 10/10 distinct ``_session_id`` per worm under barrier-sync.      Format: ``Y, T6b: 50/50 distinct ``_session_id`` across all 5 worms × 10 threads.      Combin (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (16): _module_path_constants(), _E_DRIVE / _C_DRIVE / _G_DRIVE are all different strings., Iterate every module's module-level attributes and return     (module_name, attr, For every ``*_DIR`` / ``*_PATH`` / ``*_DRIVE`` module-level string     attribute, worms.kali_health.KALI_VHDX_PATH matches the canonical cross-platform form., worms.wsl_recovery.KALI_VHDX_PATH matches the canonical cross-platform form., DriveStatus.drive_letter is always ``"E:"`` (symbolic, NOT the     resolved moun, On a Linux CI host, ``_IS_WINDOWS`` is False. (+8 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (7): find_f11_anti_patterns(), has_f11_anti_pattern(), Return True if `line` contains an F11-shape mixed-slash f-string.      Convenien, Scan a source string and return ``[(line_no, line_text), ...]`` for     every li, Single entry point so all 12 cases above share the same call site., Pins the contract of `has_f11_anti_pattern()` exactly., TestF11MixedSlashRegex

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (21): _has_user_visible_error(), Each worm's no-args CLI includes a 'v<digit>.<digit>.<digit>' version string., `python -m worms.kali_health check --json` returns valid parseable JSON., `python -m worms.X --help` either exits 0 OR prints `--help` content., `--help` prints argparse usage block with module name., `python -m worms.X nonexistent_cmd` produces a clear user-visible error.      Ac, No `password=XXXXXXXX` (with 8+ chars), `secret=`, `api_key=`,     `token=`, `be, For each worm:       - no args -> rc=0       - --help -> rc=0 OR stdout has usag (+13 more)

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (12): _mount_line(), Lines with fewer than 3 fields are skipped (don't crash the         overall pars, Covers longest-prefix + root + boundary cases for the     _resolve_linux_fstype(, Drive _resolve_linux_fstype() with a synthetic /proc/mounts., A query that matches a mount point exactly returns its fstype., A path that is a descendant of a mount point returns that mount's         fstype, When two mountpoints could match, the LONGER match must win., When only '/' is in /proc/mounts, any descendant path inherits         root's fs (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.14
Nodes (12): ThreadSafeWormMixin, BaseWormMixin, BenchmarkWorm, main(), Record execution telemetry to PAMS if available., Load run count from existing benchmark_history.json.          Uses line-based co, Check benchmark_history.json size and surface alerts via PAMS.          Warns wh, Record a history-size alert to PAMS. (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.21
Nodes (16): Benchmark Runner, Build Pipeline, SharedDirManager, Quartet Architecture, append_to_history(), assert_dashboard_title_consistency(), generate_dashboard(), Append this run to benchmark_history.json, cap at MAX_HISTORY. (+8 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (9): main(), Execute a shell command inside a WSL distro.          When running natively on K, Create all shared subdirectories.          Returns status dict with created/exis, Verify the shared directory is accessible from all environments.          Return, Translate paths between Windows and WSL.          Args:             path: Path t, Get paths to shared directory in all formats., Run full setup: create dirs + verify access.          Returns comprehensive stat, Manages the G:\\azazael_shared\\ cross-platform directory.      Ensures director (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (14): 100 concurrent threads barrier-sync-instantiate a class; expect     100/100 dis, KaliHealth.check() under high-concurrency stress on ONE instance.      Headlin, The 6-digit µs field (between the 6-digit HHMMSS and the 8-hex suffix)     must, The 8-char hex suffix after the underscore MUST be lowercase hex., If a worm's get_summary() returns a 'session_id' field, it MUST     match the i, Skip test if not running on Python 3.14t free-threaded., Every instantiation across 1000 sequential calls produces a 31-char     session, _require_314t() (+6 more)

### Community 17 - "Community 17"
Cohesion: 0.19
Nodes (14): Each worm's CLI prints the ``WormName vVERSION \u2014 Vermillion LightFury``, KaliHealth `quick` subcommand is the simplest non-default CLI path.      No WSL/, WSLRecovery `status` subcommand prints distro states without WSL.      Even on a, NmapScanner `scan 127.0.0.1` end-to-end (with clean env) \u2014 validates     th, Cross-worm sanity check: none of the worms emit     ``RuntimeWarning: ... found, Invoke ``python -m module_path`` as a subprocess from project root.      Returns, Each worm's ``python -m worms.X`` with no args returns exit code 0.      The no-, _run_cli_subprocess() (+6 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (7): win_path must be exactly what os.path.join(_SHARED_DIR,         'metasploit_logs, Both wsl_path and win_path must end with the same .rc filename —         the joi, End-to-end invariant: across 5 isolated calls (warm), every         output path, Invariant guards for MetasploitBridge._save_resource_script() path     construct, Build a MetasploitBridge instance against the patched paths., Given a properly-formed _WSL_SCRIPT_DIR (forward-slashes only),         the cons, TestWslPathAsymmetry

### Community 19 - "Community 19"
Cohesion: 0.21
Nodes (13): main(), Pillar, PillarReport, _probe_drvfs_writable(), _probe_path(), _probe_ubuntu_bridge(), _probe_wsl(), Probe `path` for fs-level existence and report vermillion_present when     `path (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.17
Nodes (14): WSLDistroStatus.alert_level cascade:         state == "Crashed"              → c, # NOTE: source uses EXCLUSIVE `>` (not `>=`), so values EXACTLY at the, A 10,000-character target argument MUST NOT crash the worm CLI.      Real-world:, Unicode arguments MUST NOT crash the worm CLI with import errors.      Real-worl, Empty-string arguments MUST NOT crash the worm CLI with import errors., ``python -m worms.kali_health check --json`` MUST return valid JSON     when the, Phase 13.9 SF6b regression guard for the new subcommand surface.      Locks down, _run_subproc() (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.19
Nodes (12): _concurrent_execute(), S1: 10 NmapScanner instances barrier-sync-call ``scan()``.      The per-worm ``s, S2: 1 KaliHealth() instance × 10 concurrent ``check()`` calls.      The HEADLINE, S3: 10 SharedDirManager instantiations under barrier race — verify     no deadlo, S4: All 5 worms × 2 barrier threads each — every worker calls     ``get_summary(, S5 (T5-analogue for execution): After a 4-thread barrier race, a     SEQUENTIAL, Barrier-sync ``n`` threads each calling ``module.class().method(*args, **kwargs), test_S1_nmap_scan_concurrent_total_scans_counter_serialization() (+4 more)

### Community 22 - "Community 22"
Cohesion: 0.18
Nodes (12): _find_dangerous_capture(), _iter_python_scripts(), Return (file, line_no, matched_line) for every dangerous capture pattern.      H, F1 (Phase 11.8): No file in the project uses ``python3 ... > file; echo $?``, F2: Specific regression check against regression_guard.py — the     canonical Ph, F3: Project python orchestration code prefers subprocess.run() over     os.syste, F4: The Phase 11.7 exit-code lesson must be discoverable from     MILESTONE.md (, Yield all source files potentially containing shell exit-code patterns.      Sco (+4 more)

### Community 23 - "Community 23"
Cohesion: 0.15
Nodes (12): Hypothesis-driven: for ANY finite float in [-1000, +10000], the     source rule, Hypothesis-driven discovery (Phase 13.5): a NaN/Infinity free_gb     MUST NOT si, dataclasses.replace bypasses __init__ — if any future post-init     validation i, On 3.14t free-threading, generating 200 DriveStatus instances across     a wide, Each free_gb value must map to its expected alert_level per the     source rule, test_SF1_free_gb_discrete_boundary_scan(), test_SF1_hypothesis_free_gb_invariants(), test_SF7_nan_inf_free_gb_must_not_silently_fall_through_to_ok() (+4 more)

### Community 24 - "Community 24"
Cohesion: 0.26
Nodes (11): aggregate_per_function(), check_guard(), load_history(), main(), parse_args(), _parse_exclude_functions(), Aggregate per (module, function) across all history entries, preserving order., Return list of failures: [(module, function, latest_ms, prior_mean_ms, drift_pct (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.18
Nodes (10): AST-based static guard: NO bare ``from exceptions import`` or     ``import excep, After worms import cleanly, all 6 main classes instantiate successfully     and, Sanity: each worm + shared_dir module has a non-trivial docstring     (catches a, Every worm + config module imports WITHOUT ModuleNotFoundError or ImportError., The canonical exceptions module is ``worms.exceptions`` and exports     the plat, test_all_classes_instantiate_with_31_char_session_id(), test_all_worm_modules_import_cleanly(), test_no_bare_exceptions_imports_in_source() (+2 more)

### Community 26 - "Community 26"
Cohesion: 0.28
Nodes (8): _field_default(), _get_dataclasses_to_test(), For every dataclass that successfully instantiates:         • to_dict()  returns, DriveStatus.alert_level:         free_gb <= 1.0  -> critical         free_gb <=, Return a type-aware default value for the dataclass field.      Tries (in order), Discover every dataclass in every worm module., test_D1_D2_D3_every_to_dict_is_json_serializable(), test_D4_DriveStatus_alert_level_threshold_logic()

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (8): KaliProcessStatus.alert_level:         ram_used_pct > 90 -> critical         ram, KaliHealthStatus.overall_health:         any critical -> critical; any warning -, test_D5b_KaliProcessStatus_alert_level_threshold_logic(), test_D6_KaliHealthStatus_overall_health_aggregation(), KaliProcessStatus.alert_level RAM-only threshold cascade:     ram_used_pct > 90, test_SF5_process_alert_levels(), KaliProcessStatus, Kali WSL resource usage snapshot.

### Community 28 - "Community 28"
Cohesion: 0.22
Nodes (8): VHDXStatus.alert_level:         abs(growth_mb_since_last) > 500 -> warning, test_D5_VHDXStatus_alert_level_threshold_logic(), VHDXStatus.alert_level MUST apply ``abs()`` to growth_mb_since_last.      If a f, ``abs(growth_mb) > 500`` is the source rule. If a refactor drops     the abs(),, test_SF2_growth_mb_positive_and_negative(), test_SF2_hypothesis_growth_mb_abs_invariant(), VHDX file health snapshot., VHDXStatus

### Community 29 - "Community 29"
Cohesion: 0.38
Nodes (6): When --explain-exclude is set, the rationale text is emitted to stderr.      Pin, Load the real benchmark history and force a HARD drift on (module, function)., Run regression_guard with --explain-exclude, assert no '()()' in stderr.      Fo, _synthetic_history_with_forced_drift(), test_explain_exclude_includes_rationale(), test_explain_exclude_print_format_no_double_parens()

### Community 30 - "Community 30"
Cohesion: 0.38
Nodes (6): extract_json(), main(), ollama_execution_benchmark.py — Ollama models EXECUTE vermillion_lightfury + aza, Execute a prompt through Ollama and measure performance., Try to extract a JSON object from model output., run_ollama()

### Community 31 - "Community 31"
Cohesion: 0.38
Nodes (6): capture_frames(), encode_mp4(), main(), render_complete_reference_mp4.py — Capture AZAZAEL_COMPLETE_REFERENCE.html as sc, Encode frames to MP4 using ffmpeg., Use Playwright to scroll and capture frames. Waits for Mermaid diagrams to rende

### Community 32 - "Community 32"
Cohesion: 0.38
Nodes (6): capture_frames(), encode_mp4(), main(), render_dashboard_mp4.py — Capture QUARTET_DASHBOARD.html as scrolling MP4.  Uses, Encode frames to MP4 using ffmpeg., Use Playwright to scroll the dashboard and capture frames.

### Community 33 - "Community 33"
Cohesion: 0.29
Nodes (6): Validate VHDXFsckResult.alert_level source rule cascade for cases     where curr, Phase 13.5 discovery artifact: errors_found=-1 should escalate to     "critical", test_SF3_vhdx_fsck_alert_levels_operational_failure_discovery(), test_SF3_vhdx_fsck_alert_levels_validated(), Result of an e2fsck filesystem check on the Kali VHDX., VHDXFsckResult

### Community 34 - "Community 34"
Cohesion: 0.5
Nodes (4): _audit_imports_sessionstart(), _audit_no_bare_exceptions_imports(), Sessionstart autouse fixture - runs ONCE at pytest session start.      Phase 13., Walk every .py file in worms/, config/, tests/ via ``ast.parse()`` +     ``ast.w

### Community 35 - "Community 35"
Cohesion: 0.5
Nodes (3): benchmark, models, timestamp

## Knowledge Gaps
- **40 isolated node(s):** `benchmark_started`, `benchmark_completed`, `cpu_count`, `cpu_percent`, `ram_total_gb` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `KaliHealth` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 33`, `Community 7`, `Community 12`, `Community 13`, `Community 21`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `ThreadSafeWormMixin` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 33`, `Community 13`, `Community 23`, `Community 27`, `Community 28`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `DriveStatus` connect `Community 23` to `Community 0`, `Community 3`, `Community 9`, `Community 26`, `Community 27`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `KaliHealth` (e.g. with `TestResolveLinuxFstype` and `ThreadSafeWormMixin`) actually correct?**
  _`KaliHealth` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `MetasploitBridge` (e.g. with `ThreadSafeWormMixin` and `KaliUnresponsiveError`) actually correct?**
  _`MetasploitBridge` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `NmapScanner` (e.g. with `BaseWormMixin` and `ExploitResult`) actually correct?**
  _`NmapScanner` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `ThreadSafeWormMixin` (e.g. with `BaseWormMixin` and `BenchmarkWorm`) actually correct?**
  _`ThreadSafeWormMixin` has 24 INFERRED edges - model-reasoned connections that need verification._