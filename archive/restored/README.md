# archive/restored/ — Old-only functionality restored from G: (reference only)

> **Restored: September 1, 2026 (Session 28) + September 4, 2026 (Session 28 batch).** This is a **reference copy** — read-only, not wired into the codebase. It exists so the original functionality documented by the generation diff (Phase 9) can be inspected and compared against current code without touching the G: historical archive.

## Source & provenance

| Subfolder | Source | Generation | Files |
|---|---|---|---|
| `AOA/` | `G:\AZAZAEL\AOA` | gen 1 (original workspace) | 27 files / 247 KB (20 .py) |
| `Libra/` | `G:\AZAZAEL\Libra` | gen 1 (original workspace) | 154 files / 1.1 MB (43 .py) |
| `Libra_Desktop/` | `C:\Users\clint\Desktop\Libra` | **newest (Desktop, BCC-era superset)** | 328 files / 37.96 MB (86 .py) |
| `META_Z/` | `G:\AZAZAEL\AZAZAEL_ROOT\src\META\{DebugZ,DistillZ,InferenceBridge,FleetZ}.py` | gen 1 (also present in `src_src_divergent_backup_20260829\META\`) | 4 files / 96 KB |
| `EveUnleashed/` | `G:\AZAZAEL\EveUnleashed` | gen 1 (original workspace) | 15 .py (tree preserved) / ~181 KB |
| `EveUnleashed_Desktop/` | `C:\Users\clint\Desktop\EveUnleashed_Selector` | **newest (Desktop, evolved superset)** | 40 .py / 23 MB logical |
| `Build_tooling/` | `G:\AZAZAEL\AZAZAEL_ROOT\build\{build_all.py,regenerate_bats.py}` | gen 1 | 2 files / ~13 KB |
| `Misc_utilities/` | mixed (see per-file note below) | gen 1 + gen 2 | 7 files / ~20 KB |

**Sep-4 additions detail:** `EveUnleashed/` holds the 15 old-only EveUnleashed desktop-app modules (per GEN_DIFF_FINDINGS §EveUnleashed — the module basenames existed only in `G:\AZAZAEL\EveUnleashed` at scan time, absent from the current codebase). `EveUnleashed_Desktop/` is the **newest evolved superset** from `Desktop/EveUnleashed_Selector/` (40 .py / 330 files, 23 MB logical, robocopy 0 failed/0 mismatched, `dist/`+`coverage_html/`+`__pycache__`+`*.whl` excluded as third-party/regenerable); gen-1 vs Desktop comparison: `eve_unleashed_app.py` DIFFERS (90,719 vs 105,470 bytes — Desktop evolved), `scripts/probe_model.py` DIFFERS (Desktop = 3,080-byte fixed variant that compiles clean; gen-1 = 3,079-byte broken docstring), `scripts/server.py`/`llama_client.py`/`tkinter_app.py` IDENTICAL. `Build_tooling/` = the 2 old-only build scripts. `Misc_utilities/` = the 7 old-only misc modules with per-file sources: `sync_canonical_docs.py` ← gen 2 `G:\AZAZAEL_SOURCE_OF_TRUTH\src\SCRIPTS`; `_diagnose.py`, `_validate_fix.py`, `_debug_create.py` ← gen 1 `G:\AZAZAEL\AZAZAEL_ROOT`; `_pick_draft.py` ← gen 1 `G:\AZAZAEL\EveUnleashed\scripts`; `download_coder.py`, `fix_ps1_v2.py` ← gen 1 `G:\AZAZAEL\EveUnleashed\logs`.

- **AOA** also exists in gen 2 (`G:\AZAZAEL_SOURCE_OF_TRUTH\AOA`); gen 1 was chosen as it contains the superset (extra `aoa-disclosure-build.md`, `CROSS_ENV_MANIFEST.md`). The newer Desktop copy lives at `src/AOA/` (wired in as runnable — see `src/AOA/README.md`).
- **Libra** gen 1 (`G:\AZAZAEL\Libra`) is the base; **`Libra_Desktop/` is the superset** — hash-verified: 147 .py identical to gen 1, 6 differ (`template_generator.py`, `cli.py`, `document_generator.py`, `concurrent_filer.py`, `pa_courts.json`, `SESSION_MILESTONE.md`), **174 files new-only: the entire BCC layer** (`libra/jurisdictions/pa/berks/` — bcc_parser, court_calendar, court_rules, filing_submitter, ifp_assistant, prothonotary + templates; `claw_bot/`; `scrapers/` — irs_teos_bot, pa_campaign_finance, usaspending_api, session_milestone; `filings/BCC_Complaint/` real filing outputs incl. sweep CSVs).
- **META Z-modules** are byte-identical across the two gen-1 locations (`src/META` and `src_src_divergent_backup_20260829/META`); copied from `src/META`.

## What was excluded

- `AOA/*.mp4` — disclosure videos (59 MB, renders only; source kept on G:)
- `__pycache__/` everywhere
- `AOA/graphify-out/` (128 KB of graph artifacts, regenerable)
- `Libra_Desktop/output/test_video/` — tiny test render intermediates (17 files, ~200 KB; kept on Desktop)

## Why these are "old-only"

Per `C:\Users\clint\GEN_DIFF_FINDINGS.md` (Phase 9 of `SESSION_MILESTONE_2026-09-01.md`), these modules' basenames appear in archived generations but **nowhere** in the current codebase:

- **AOA arms orchestrator** (15 modules: `aoa_cli`, `arm_registry`, `router`, `session_manager`, `event_bus`, `eve_arm`, `codex_arm`, `libra_arm`, `azazael_arm`, `support_arms`, `inject`, `gen_html`, `rebuild_html`, `build_final`, `build_disclosure`) — documented in `.agents/skills/aoa-architecture.md` but the source tree exists only on G:.
- **Libra legal automation** (18 modules: `template_generator`, `court_rules`, `litigation`, `document_generator`, `filing_registry`, `deadline_calculator`, `fee_schedule`, `concurrent_filer`, `crawler`, `cert_service`, `memory`, `frames`, `encoder`, `capture`, `injector`, `hevc`, `dictionary`, `MILESTONE`) — zero trace in the current codebase.
- **META Z-modules** (`DebugZ`, `DistillZ`, `InferenceBridge`, `FleetZ`) — stable across 3 archived generations; absent from current `src/META/`.
- **EveUnleashed desktop app** (15 modules: `eve_unleashed_app`, `llama_switch_model_tui`, `vl_bridge`, `agent`, `server`, `vision_agent`, `gen_everything`, `create_memories`, `tkinter_app`, `probe_all`, `probe_model`, `llama_client`, `max_ctx`, `gen_launcher`, `module_G`) — basenames exist only in `G:\AZAZAEL\EveUnleashed` (x1 each) + evolved Desktop superset `EveUnleashed_Selector/`; absent from the current codebase.
- **Build tooling** (2: `build_all`, `regenerate_bats`) — old-only at `G:\AZAZAEL\AZAZAEL_ROOT\build`.
- **Misc utilities** (7: `sync_canonical_docs`, `_diagnose`, `_validate_fix`, `_pick_draft`, `_debug_create`, `download_coder`, `fix_ps1_v2`) — old-only across gen-1 root + EveUnleashed + gen-2 SCRIPTS.

## Verification (Sep-4 additions)

- EveUnleashed 15/15 SHA-256 MATCH to `G:\AZAZAEL\EveUnleashed` sources; Build_tooling 2/2 + Misc_utilities 7/7 SHA-256 MATCH to their listed sources — **all 24 byte-identical**.
- EveUnleashed_Desktop (Desktop superset): robocopy 0 failed / 0 mismatched; 40/40 .py count parity; 5/5 spot SHA-256 MATCH; **40/40 `py_compile` clean**.
- Sanity: 23/24 `py_compile` clean; `EveUnleashed/scripts/probe_model.py` (gen-1 copy) is the sole compile failure — **inherited** (its gen-1 source fails identically: `SyntaxError: unicodeescape … truncated \UXXXXXXXX` at the docstring's `C:\Users\clint` path — a Windows-path docstring written as a non-raw string). Reference-only; documented, not fixed. (The Desktop superset's `probe_model.py` is the fixed 3,080-byte variant — compiles clean.)
- Side-effect scan: 4 modules carry top-level network-adjacent imports (`llama_switch_model_tui.py`, `llama_client.py`, `server.py`, `build_all.py`) — import with care / guarded only; none delete files at import.
- G: originals and Desktop source untouched (copy, not move) — historical archive + live Desktop intact per standing directive.

## Verification

- META_Z: 4/4 byte-identical to source (`DebugZ.py` 33,466 · `DistillZ.py` 24,220 · `InferenceBridge.py` 18,290 · `FleetZ.py` 15,746).
- Robocopy: 0 failed, 0 mismatched for AOA, Libra (gen 1) and Libra_Desktop (328 files / 37.96 MB).
- Libra_Desktop spot hashes: 5/5 SHA-256 MATCH to Desktop source (`bcc_parser.py`, `filing_submitter.py`, `ifp_assistant.py`, `clawbot.py`, `usaspending_api.py`); 86/86 .py === Desktop count.
- G: originals and Desktop sources untouched (copy, not move) — historical archive intact per standing directive.

## Known caveats (Sep-4 additions)

- **`EveUnleashed/scripts/probe_model.py` will not byte-compile on Python 3.14.7** — docstring line 2 contains `C:\Users\clint` inside a **non-raw** regular string → `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes … truncated \UXXXXXXXX escape`. **Inherited, not introduced** (byte-identical to the `G:\AZAZAEL` source, which fails identically). The module is a model-probe helper; treat as read-only reference. Remedy if ever run: make the docstring a raw string locally, never on the restore.
- **`EveUnleashed/scripts/gen_everything.py` emits SyntaxWarnings** (`\D`, `\l`, `\P`, `\.` invalid escapes) — these are Windows/PowerShell path fragments inside single-quoted Python strings; **warnings only, compiles clean**; inherited from source.

## Known caveats (Session 28)

- **`Libra_Desktop/MILESTONE.py` will not byte-compile on Python 3.14.7** (syntax sanity pass: 85/86 .py clean). Root cause: a `0x97` byte (a Windows-1252 em-dash) with **no encoding declaration**, so `compileall`/`py_compile` rejects the file rather than assuming cp1252. This is **inherited, not introduced** — the file is byte-identical to its Desktop source, which fails identically. It is a standalone root milestone script, never imported by the `libra` package, so it does not affect the restored code's operability. If it ever needs to run: add a `# -*- coding: cp1252 -*-` declaration (or fix the em-dash) **without altering the source copy** — treat this restored file as read-only reference, like all of `archive/restored/`.

## Note on size

The G: sources appear large under `du` (e.g. Libra "26 MB") because of **exFAT cluster slack** (128 KB clusters): tiny files each consume a full cluster. Logical size is what was copied (~1.4 MB total for all three subsystems).
