# TERENCE Work Order — Full Codebase Scope (2026-09-10)

Source: three parallel codebase audits (architecture, health/debt, loop-gaps)
plus five verified fixes committed 2026-09-09/10. This file is the scope;
the reasoning behind each item lives in `thought_process` store rows
(source `ReasoningTrace` / `EvolutionCycle`, session tags below) so the
learning loop trains on it. Terence must read those rows for context
before touching a file: query `event_type='thought_process'`, newest first.

## How Terence gets what it needs

- Code index: `git -C C:\Users\clint\azazael ls-files '*.py'` (tracked set).
- Live health: `scripts/live_monitor.py` render; `logs/*.log` tails.
- Training data: store `thought_process` rows (reasoning + success flags).
- Verification per fix, in order: (1) `py_compile` the file, (2) run the
  nearest `tests/test_<module>.py` if one exists, (3) `git diff --stat`
  review. Any failure rolls back (see capability upgrade below).
- Outcome recording: every applied fix MUST append a `thought_process`
  row (task, reasoning, success=verify-passed). That is the learning
  loop — DPO pairs successes vs failures automatically.

## Class A — mechanical, Terence-eligible now (verify each)

A1. `src/UTILITIES/TERENCE/TERENCE.py` "Empty try block" rule emits
    `try: ... except Exception: pass` — the tool teaches the anti-pattern
    (debt report §1). Fix the RULE to emit `except Exception as e:` +
    `print/logging` line. Session: 2026-09-10-loop.
A2. `src/UTILITIES/TERENCE/terence_enhanced.py:439` generates
    `# TODO: Resolve ...` into the codebase. Change the template to emit
    a tracked work item (or stop emitting TODOs).
A3. `src/CORE/enforcement_harness.py:166` `# TODO: fix this later`
    inside its own compliance self-test. Resolve or exempt explicitly.
A4. `src/ORCHESTRATION/ml_platforms/improvements/qlearning_table.py:962`
    doc generator emits `(TODO: add link)` as finished docs. Finish the
    link or drop the placeholder text.
A5. Bare `except:` real sites (only 2 in code, rest are strings/docs):
    `src/AOA/core/event_bus.py:50` (add logging + DLQ counter, never
    silent), `src/CODEX/VIDEOS/create_reference_video.py:563` (narrow to
    `except Exception`). Skip intentional+commented
    `src/CORE/direct_memory.py:273-275` (narrow only if trivially safe).
A6. `src/CORE/WORMS/expansion/learning_grpo.py:366` TODO + private-DB
    tombstoning + silent swallow. SWALLOW FIXED 2026-09-10 (now logs);
    remaining: add the public delete API to LocalMemoryStore and route
    the tombstone through it.

## Class B — judgment required (agent approval, fix shapes given)

B1. `exec()` on formatted strings:
    `src/CORE/WORMS/CONCURRENCY.py:251,285-286`,
    `src/INTERPRETERS/__init__.py:52`,
    `src/ORCHESTRATION/scripts/run_tests.py:46`,
    `src/ORCHESTRATION/scripts/comprehensive_analysis.py:241`,
    `src/ORCHESTRATION/ml_platforms/lm_studio_server.py:206`.
    Shape: allowlist module/class names, replace exec with importlib.
B2. Unvalidated `pickle.load` (RCE on poisoned cache):
    `src/CORE/worm_registry_cache.py:102,128,223`,
    `src/UTILITIES/TARBABY/tarbaby_enhanced.py:311,676`,
    `src/UTILITIES/TARBABY/TARBABY.py:143,361`,
    `src/CORE/WORMS/SMARTDISK.py:586`,
    `src/CORE/WORMS/WORMZ_ML.py:447`,
    `src/CORE/WORMS/SYSTEMZ_ML.py:466`.
    Shape: hash-pin cache files (sha256 sidecar) or migrate to json.
B3. Subprocess without timeout (hang risk): `src/chain_of_action.py:37`
    (rsync), `src/AZAZAEL_TOOLKIT/environment_manager.py:22,43` (pip
    install), `src/CODEX/VIDEOS/create_scrolling_video.py:892` (ffmpeg),
    `src/DAEMONS/install_parallax_startup.py:89` (untracked Popen),
    `scripts/gephi_headless/run_headless.py:153,185` (javac/java),
    `scripts/video_frame_generator.py:175-180` (ffmpeg pipe, add
    communicate(timeout)). Shape: add `timeout=` + `TimeoutExpired`
    handling everywhere; pattern reference: `scripts/track_backfill.py:62`.
B4. Dead/duplicate modules (verify zero importers first via grep, then
    delete + record):
    - 12× `*.pre_gate_backup` files (sentinel leftovers; see audit list).
    - `src/CORE/WORM_FLEET.py` vs `src/CORE/WORMS/WORM_FLEET.py` (keep one).
    - `src/METAWORMS*.py` + `src/META/METAWORMS*.py` + MetaWormSpawner
      (3 copies; canonical CurativePool location wins).
    - `ABTestRunner` v1 stub `learning_ab.py:41` (v2 in learning_grpo).
    - `HYDRA/ml_platforms/health_monitor.py:13` shim, `CODEX/CORE/*` shims,
      `WORMS/ECOSYSTEM_EXPANSION.py:21` (all self-declared deprecated).
    - `scripts/bcc_*`, `tmp_bcc_*` (completed investigation; archive out).
B5. Memory-API sprawl (consolidate or document canonical):
    `local_memory` (canonical) vs `direct_memory` (legacy DB_PATH still
    used by retention) vs `postgres_memory` vs `MemoryBus` vs
    `session_memory`/`persistent_memory` vs `PamsRecorder`/`PamsBusBridge`
    vs `record_session`+`codebuff_tracker` (both self-declared DEPRECATED).
B6. Test gaps (write tests before Terence touches these areas):
    `data_retention`, `dream_policy_bridge`+cycles, `learning_grpo`,
    `evolution_cycle` (lifecycle only proven via logs),
    `live_monitor`/`nightly_maintenance`, PAMS bridge/merge/repair/watch,
    `embedding_backend`, `HYDRAMETA_UV`, `DOCKERZ`, `chain_of_action`.

## Class C — already fixed 2026-09-09/10 (Terence training data, do NOT redo)

C1. Scheduler-visible fatals (evolution/metacog/orchestrator): wrap
    entrypoints, FATAL banner + nonzero exit. Thought 903213.
C2. Q-table amnesia: loader FTS→exact lookup (18 states/67 actions
    resume), silent-False wiring made loud. Thought 903212.
C3. Synthetic training data honesty: mock rows flagged, real count zero.
C4. DPO cumulative hydration: `load_pairs()` — SB3 1→34 pairs/run.
C5. Holdout gate + canary rollback + 3-salt + era-pinned streaks + HOF
    margin reseed + `.prev` depth 2 + pool-era IDs. Thoughts 902916-17,
    902922-24, 903032-33.
C6. UV hardening: arity crash, double-append, preflight, timeouts,
    atomic writes, uuid ids. Thought 902918.
C7. Track 30-run floor + single-instance locks + RL tagging + backfill
    runner (145/145). Thoughts 902925, 903089.

## Proficiency ladder (100% = all rungs live)

1. Preview without touching (exists: `scan`/`preview`).
2. Per-fix backup + `py_compile` verify + rollback (TO BUILD — see
   capability upgrade spec in thought rows, session 2026-09-10-loop).
3. Nearest-test execution per fix (TO BUILD).
4. Outcome recording to `thought_process` (TO BUILD).
5. Coverage of Classes A→B in order, never B before its tests exist (B6).

## Explicitly out of scope

- `Graphify_Codebase_Atlas` (21GB, cold) — owner decision pending.
- FACEBOOK report/media dirt (~200 files, another author's work).
- Constraining meta-evolution's own choices (patience floor declined;
  null-experiment thought recorded).
