# HYPER-EDGE CONFORMITY ROADMAP — all subtrees, native 3.16t, platform-agnostic

**Date:** 2026-11-12. **Status:** plan, not started.
All numbers below were measured today with the commands named in §1. A number
re-quoted without its command is a recollection, not a reading.

## 1. Measured baseline (the tree as it is)

- **32 `Project_*` subtrees** in `C:/Azazael/azazael` (`ls -d Project_*/` → 37
  dirs total; 32 carry the `Project_` prefix, 5 are lanes/helpers).
- **Parse state: clean everywhere.** `ast_audit.py --root <each>` → `syntax_err=0`
  on all 37. The table below is the last line of each audit run.
- **Test coverage by name: near zero.** `grep -rl "Project_X" tests/*.py` finds
  tests for only 6 of 32 subtrees (FLAMING_SWORD 4, ELIZA 4, Nurse_Ratchet 3,
  LUCY 1, FLAME 1, CRADLE 1). The Eve suites (`test_eve_mcml*`,
  `test_eve_net_genome`, `test_hyper_edge`) cover `src/`, not `Project_*`.
- **Interpreters (both live, both free-threaded):**
  - `C:/Azazael/.venvs/py316t/Scripts/python.exe` → 3.16.0a1,
    `sys._is_gil_enabled() = False`, `Py_GIL_DISABLED = 1`. **This is native.**
  - `C:/Azazael/.venvs/py315t/Scripts/python.exe` → 3.15.0rc3,
    `sys._is_gil_enabled() = False` — also free-threaded; its job is
    *dependency fallback* (packages without `cp316t` wheels), not "the GIL
    interpreter". Bare `python` on PATH is 3.14.7 **with** the GIL: legacy,
    never the test interpreter.
  - Conformance gates already run on their audit of what is reachable:
    `mcp_startup_gate.py` (PASS=9 WARN=1 measured 2026-11-12),
    `krampus_conformance.py` (15/15 tools × 3 lanes).

### 1.1 Subtree table (files tracked / py files / ast-audit last line, abridged)

| subtree | tracked | py | parse | notable load |
|---|---|---|---|---|
| ELIZA | 1267 | 1238 | ok | 739k LOC · except_pass 1301 · except_continue 170 · dupgroups 642 · orphans 5282 |
| CODEX_VideoEngine | 530 | 92 | ok | 36k LOC · orphans 73 |
| Scribe | 248 | 20 | ok | clean |
| EcosystemOrchestrator | 196 | 85 | ok | 38k LOC · dupgroups 1 |
| Nurse_Ratchet | 61 | 32 | ok | except_continue 2 |
| FLAMING_SWORD | 29 | 15 | ok | except_continue 8 |
| SHARDEX | 29 | 13 | ok | clean |
| HYDRA_MLCluster | 28 | 11 | ok | clean |
| PERSEPHONE_Sync | 25 | 10 | ok | clean |
| PSYCHE_Consciousness | 21 | 14 | ok | clean |
| Compliance | 21 | 14 | ok | clean |
| CRADLE | 20 | 8 | ok | clean |
| MultiProviderInference | 18 | 13 | ok | clean |
| FLAME | 15 | 4 | ok | clean |
| KLINK_Protocol | 15 | 2 | ok | clean |
| NeuralWiring | 15 | 10 | ok | orphans 10 |
| ShardEngine | 13 | 5 | ok | clean |
| TERENCE_Oracle | 12 | 3 | ok | markers 6 |
| TARBABY_FileSearch | 12 | 3 | ok | clean |
| Rendering_Pipeline | 11 | 6 | ok | 97 LOC — stub? |
| PolyglotInterpreters | 11 | 6 | ok | clean |
| GAMORA | 8 | 6 | ok | except_pass 3 |
| POINDEXTER_Indexer | 8 | 2 | ok | clean |
| FreeThreadedRuntime | 7 | 2 | ok | clean |
| Loggers_Telemetry | 6 | 1 | ok | 25 LOC — stub? |
| LUCY | 3 | 2 | ok | clean |
| Oxenford | 2 | 1 | ok | clean |
| WASM_Compiler | 11 | **0** | ok (empty) | non-Python contents |
| JAEGER | 10 | **0** | ok (empty) | non-Python contents |
| HORUS_Monitoring | 10 | **0** | ok (empty) | non-Python contents |
| RustAccelerator | 9 | **0** | ok (empty) | non-Python contents |
| BIBL_Bibliographic | 6 | **0** | ok (empty) | docs only? |
| PAMS_Daemon | 5 | **0** | ok (empty) | docs only? |
| NSGA_Optimizer | 5 | **0** | ok (empty) | docs only? |
| ML_Platform_Integration | 5 | **0** | ok (empty) | docs only? |
| GOSP_Governance | 5 | **0** | ok (empty) | docs only? |
| AutoDiffEngine | 5 | **0** | ok (empty) | docs only? |

Provenance: `git ls-files <dir> | wc -l`, `ast_audit.py --root <dir>`,
`grep -rl "Project_X" tests --include='*.py'`. The ast counts include untracked
worktree files (ELIZA's 5570 py vs 1238 tracked = adopted copies).

## 2. What "HYPER-EDGE conformity" means (machine-checked, not eloquence)

A subtree is conformant when all of these hold, each with its command:

1. **Native 3.16t.** Every run, test and probe uses the production interpreter;
   `sys._is_gil_enabled() is False` on the executing process. No bare `python`,
   no 3.14, no per-tool `sys.executable` guess that can drift.
2. **Parses.** `ast_audit.py --root <dir>` → `parsed == py`, `syntax_err == 0`
   (today: true for all 37).
3. **Has a smoke test.** At least one test file that imports the subtree's entry
   point and runs its smallest real behaviour. 26 of 32 subtrees have **zero**.
   Runs under `golden_arrow.py --file <test>` (one file, one process, its own
   wall bound). A known-debt subtree lands in `logs/golden_arrow_baseline.json`
   (debt model: printed every run, fails only under `--strict`; lists shrink).
4. **Passes the same gates as the core.** `anti_pattern_gate.py --check
   --tracked-only` (no NEW findings; deliberate ones baselined with the reason
   in the commit, as done for compat's win32 probe in `089aca24`),
   `reading_audit.py` (every artifact states its denominator),
   `settings_shadow.py`, `head_audit.py`, `deep_dive.py --forensics`.
5. **Surface is callable and proven.** Any subtree that exposes pickers,
   selectors or providers gets a conformer in the `krampus_conformance.py`
   shape: spawn the configured command, compare `tools/list` against the live
   surface — never trust the config's shape.
6. **Platform-agnostic.** No `C:\` or `/mnt/c` literals (paths from
   `pathlib` + env, per the `krampus_mcp.py REPO` pattern); Windows-only
   dependencies behind guarded imports with a *recorded* fallback (the
   `HYPER_EDGE/compat.py` pattern — absence is named, never silent);
   LF-safe files; tests pass on Windows, WSL Kali, and the bare host.

## 3. Roadmap

### Wave 0 — Foundation (one turn, unblocks everything else)

- [ ] Pin the interpreter contract in one place both lanes read: name
      `py316t` native, `py315t` dependency fallback, `python`=legacy. If this
      lives in three READMEs it will drift in three READMEs.
- [ ] Commit the per-subtree acceptance template: each wave's row names the
      smoke test, the ast line, the gate commands and their observed output.
- [ ] Decide the source-of-truth rule for the 8 new repos (default below) and
      write it once, in each repo's first commit.

Accept: the Wave 1 row can be copied verbatim.

### Wave 1 — The 8 live repos (highest leverage: they are public)

eliza · codex-video-engine · scribe · ecosystem-orchestrator · shardex ·
flaming-sword · hydra-mlcluster · persephone-sync

Per repo, in this order: smoke test → ast line → gates → CI.
Re-export the CI template from the monorepo's `.github/workflows/` so the
repos run the same `golden_arrow --staged` + `anti_pattern_gate --check
--tracked-only` that gated their content here. Until a repo's CI is green, the
monorepo directory stays canonical.

**Source-of-truth rule (default): monorepo → repos, one direction only.**
Sync is `git subtree split -P Project_X` re-run against the same path
(filter-repo is the extraction instrument; `subtree split` exceeded 300 s on a
29-file path on 2026-11-12 and is not the instrument). A repo that wants to
own its code posts a lane row declaring ownership; before that, in-repo edits
revert on sync.

Accept per repo: `pytest <smoke> -q` exit 0; ast `syntax_err=0`;
`anti_pattern_gate --check --tracked-only` exit 0; CI green on `main`.

### Wave 2 — In-monorepo Python subtrees (23 dirs, 1–248 files)

Order by size, largest first (biggest behaviour surface first):
Nurse_Ratchet → PSYCHE → Compliance → CRADLE → MultiProviderInference →
FLAME → KLINK → NeuralWiring → ShardEngine → TERENCE → TARBABY →
Rendering_Pipeline → PolyglotInterpreters → GAMORA → POINDEXTER →
FreeThreadedRuntime → Loggers → LUCY → Oxenford, each landing in slices of
≤8 files / ≤150 lines per commit (bulk gate), one board row per subtree.

Pre-known fixes (do not rediscover):
- ELIZA's shape (Wave 4) does not apply here; none of these carries debt.
- GAMORA: `except_pass 3` — convert to recorded fallbacks or baseline with
  the compat-style reason.
- FLAMING_SWORD: `except_continue 8`. Nurse_Ratchet: `except_continue 2`.
  TERENCE: 6 markers. NeuralWiring: 10 orphans. Rendering_Pipeline (97 LOC)
  and Loggers_Telemetry (25 LOC): verify stub vs real before writing tests.

Accept per subtree: same four commands as Wave 1.

### Wave 3 — Non-Python subtrees (11 dirs, 0 py files): retire or populate

WASM_Compiler · JAEGER · HORUS_Monitoring · RustAccelerator · BIBL ·
PAMS_Daemon · NSGA_Optimizer · ML_Platform_Integration · GOSP_Governance ·
AutoDiffEngine, plus the 0-py corners.

Each gets one row with a verdict, not a test: what the non-Python content is
(Rust? Go? docs? pointers?), whether a port exists elsewhere in the tree
(e.g. jaeger → `myzticalbabe/jaeger` repo; cradle → `myzticalbabe/cradle`),
and either a smoke that exercises it or a dated retirement note. A verdict
with no command is narrative; a row with no verdict keeps drifting.

### Wave 4 — ELIZA alone (1267 files, 739k LOC, the only red row)

Phase it: (a) ast is already clean — record the line; (b) shrink
`except_pass 1301` / `except_continue 170` by the same hoist-then-baseline
method used in `089aca24` (structural first, baselined remainder with per-site
reasons); (c) smoke test for the session entry point; (d) separate the
adopted trees from the ELIZA core so audits stop counting 5570 files for a
1238-file subtree (the `py=5570 vs tracked 1238` gap is itself a reading that
hides its count — HED-3/HED-9). Do not start Wave 4 inside another wave's
turn; it is a lane of its own.

### Wave 5 — Bare-metal proof (closes "platform-agnostic")

- Build 3.16t on p8 from source (`--disable-gil`), recreate the venv there.
- Cross-compile engram for linux (`GOOS=linux GOARCH=amd64`; source gap:
  the engram source is not vendored — locate it first, it is a blocker).
- Port the five units (pams, pmb daemon, floor proxy, supervisor, krampus)
  to systemd with `Restart=always`.
- Run the gates **on the bare host** and require the same PASS lines the
  Windows lanes print — including `krampus_metal_probe(all)` answering
  `is_bare_kernel: true`, which is the one reading Windows can never produce.
- Interp... (truncated 20887 chars)
