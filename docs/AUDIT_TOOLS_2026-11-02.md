# AUDIT — `tools/` (2026-11-02)

**Auditor:** 8 of 18, full-audit fan-out. **Mode:** read-only. **Nothing was executed.**

## 0. Coverage — read this before any verdict below

`ls tools/` reported **331 entries** (measured by the coordinator earlier this
session). `list_directory` returned the full file listing plus **7 subdirectories**
(`blender_session_20260930`, `data`, `graphify-out`, `graph_semantic`, `procdump`,
`swarm_arena`, `__pycache__`).

| What I did | Count |
|---|---|
| Files **read** (whole or partial) | **4** |
| Files **searched** directory-wide (3 queries) | all |
| Files **listed only** | ~327 |

**Read fraction: ~1.2% of files, 0% executed.** The sample is not random: it is
weighted to the gate and hook chain, which is the only part of `tools/` that can
silently certify the rest of the tree. Everything below is either a `file:line`
fact or is marked **UNKNOWN**. Treat the inventory in §1 as **names and counts**,
not as behaviour.

Files read: `claim_guard.py` (55/268), `evidence_gate.py` (45/581),
`.githooks/pre-commit` (60/667), `.githooks/prepare-commit-msg` (40/108).
`receipt_guard.py` was read in full by the coordinator in an earlier slice
(and its `--selftest` was executed there: 14 cases, 0 failures).

---

## 1. Inventory by group

Counts are from the directory listing, not from reading.

| Group | ~n | Examples |
|---|---|---|
| **Gates / enforcement** | ~45 | `preflight_all.py`, `anti_pattern_gate.py`, `evidence_gate.py`, `staged_scanner_gate.py`, `canon_drift_check.py`, `git_merge_gate.py`, `claim_guard.py`, `receipt_guard.py`, `type_check_gate.py`, `failure_evidence_gate.py`, `unresolved_ratchet.py`, `aggregate_suite_gate.py`, `anchor_runtime_gate.py`, `paradigm_gate.py`, `task_shape_check.py`, `permission_seeking_guard.py`, `prepare_guard.py` |
| **MCP / memory stack** | ~17 | `mcp_startup_gate.py`, `mcp_eight_verify.py`, `supervisor_mcp.py`, `pmb_floor_proxy.py`, `pmb_client.py`, `engram_supervise.py`, `session_start.py`, `hook_dispatch.py` |
| **CAIN one-off scripts** | **33** | `cain_basis.py` … `cain_words_next_to_marks.py` |
| **HYDRA** | 9 | `hydra_api.py`, `hydra_client.py`, `hydra_test.py`, … |
| **Renderers / dashboards** | ~12 | `render_*.py`, `monitor_*.py`, `flask_dashboard.py`, `streamlit_dashboard.py`, `command_center.py` |
| **SOTA / harvest** | ~14 | `sota_*.py`, `harvest_*.py` |
| **Tier/version migration** | ~8 | `install_*_315t.py`, `repoint_315t.py`, `converge_315.py` |
| **Benchmarks** | ~14 | `benchmark_frameworks.py`, `accelerator_bench.py`, `live_rebalance_repro*.py` (3 copies) |
| **Committed non-source** | 3 | `supervisor_mcp.py.bak-20261029-freebuff`, `go_census.exe`, `boundary_policy.json` |

---

## 2. The gate chain — what is actually wired

This is the part I can state with evidence, because the hooks declare it.

### `.githooks/prepare-commit-msg` → `claim_guard.py` (RULE 0B-E)

Wired, and — unusually — with a **false-positive control measured before wiring**:

> "this guard was run against the 40 most recent real commit messages in this
> repo and flagged ZERO" — `prepare-commit-msg:30-33`

The hook also records a defect that is now canon: the guard was first placed in
`pre-commit`, where `git commit -m` writes `COMMIT_EDITMSG` *after* the hook runs,
so it read a stale file and **an overclaiming commit landed as `94970d9e`**
(`prepare-commit-msg:19-25`). That is a gate that manufactured false confidence,
and it is documented rather than memory-holed.

### `.githooks/pre-commit` → 8 checks

From the header (`pre-commit:6-21`) and the stanza order:

1. `scripts/commit_gate.py` — bulk-diff focus
2. `tools/test_paradigm_gate.py` — blocking
3. `tools/index_drift_check.py` — stale-index guard
4. `tools/staged_scanner_gate.py` — staged NEW anti-patterns
5. `tools/canon_drift_check.py --check`
6. `tools/anti_pattern_gate.py --check` — repo-wide ratchet vs `logs/anti_pattern_baseline.json`
7. `tools/preflight_all.py --check` — "unified gate registry", blocking
8. `tools/agent_orders_sync.py --check` — generated instruction blocks

Working-directory note worth keeping: check 5 runs on **every** commit including
doc-only ones, and the hook says why — "A check that is skipped when it is
inconvenient is the defect this hook exists to stop" (`pre-commit:27-28`).

### `.githooks/pre-push` → `tools/git_merge_gate.py --pre-push`

Corroborated by this session's `preflight_all.py` output:
`[preflight] push hook: OK -- the push hook runs the merge gate`.

### Interpreter pinning

`pre-commit:38-50` pins `C:/Azazael/.venvs/py315t/Scripts/python.exe` and falls
back through py315 → py314m → `python3.15t` → `python3`, with the measured reason
stated: an unpinned `python` resolved to **3.13.14 from WindowsApps**. Every gate
runs on `$PY`, never bare `python`. This is correct practice and should survive
any extraction.

---

## 3. Negative controls — the tree is unusually good at this

A directory-wide search for `selftest|self_test|self-test|negative control`
returned **113 matches**. These tools ship an executable control, by `file:line`:

| Tool | Control entry point |
|---|---|
| `claim_guard.py` | `:192` `selftest()` — "11-case selftest" per the hook header |
| `receipt_guard.py` | `:271` `selftest()` — 14 cases incl. positive control (measured: 0 failures) |
| `boundary_policy.py` | `:135` — "Positive AND negative controls: an oracle that never fires is unvalidated" |
| `adoption_census.py` | `:829` — three named negative controls A/B/C (`:873`, `:882`, `:903`) |
| `metthew_families.py` | `:604` `selftest()` — "every control, both directions"; F3 refuses a family with no control (`:253`) |
| `task_shape_check.py` | `:324` — T3 "control-present" fails a doc with no negative control (`:147`) |
| `mcp_eight_verify.py` | `:641` — "the negative control: a bogus command MUST fail the same probe" |
| `swallow_inventory.py` | `:409` — fixture contains one of every swallow; `m` is itself the control (`:420-434`) |
| `sword_2600.py` | `:886`, controls at `:939`, `:945`, `:983` (refusal cases) |
| `yggdrasil_census.py` | `:2689` — "a classifier that calls everything…" (`:2963`) |
| `terence_invariants.py` | `:1250` — runs every control; `:1007` states the rule; `:1134` honestly says `gate_timing` cannot be validated by one |
| `bible_ship.py` | `:665`; `platform_claims.py` `:276`; `inference_sentinel.py` `:324`; `second_opinion.py` `:221`; `at_risk_register.py` `:553`; `tree_sitter_census.py` `:183`; `yggdrasil_atlas.py` `:823`; `agent_eval.py` `:166`; `fix_swallows.py` `:448`; `supervisor_mcp.py` `:1348` |

**Verdict on §3: PASS.** RULE 0B-C is implemented in this directory, not merely
cited. `terence_invariants.py:1134` even refuses to claim a control for an oracle
that reports an absence — the exact distinction that usually gets flattened.

---

## 4. Declared enforcement wired to nothing

| Item | State | Evidence |
|---|---|---|
| `receipt_guard.py` (subagent guard G2) | **UNWIRED by design** | Its own docstring says so; a directory-wide search for `receipt_guard` returns only the file itself. No hook, no board call. It refuses nothing today. |
| `claim_guard.py` | Wired — but only since 2026-10-17 | `prepare-commit-msg:5-8`: the tool existed and worked while "NOTHING EVER RAN IT". Canon named its own enforcement and nothing invoked it for months. |
| `permission_seeking_guard.py` | **UNKNOWN** | File exists; I did not read it and did not find a caller. It overlaps `transcript_ap5_gate.py`, which `preflight_all.py` runs advisory-only and non-blocking. |
| `nurse_ratchet_release_gate.py` | **UNKNOWN** | Present in `tools/`; also a `tools/eliza_release_gate.py` exists inside `Project_ELIZA/`. Two release gates, ownership unclear. |
| `evidence_gate.py` | Wired via `preflight_all.py` | Ran in this session: `[PASS] evidence-gate 30.43s` |

**The pattern to carry forward:** this tree has repeatedly written a correct
enforcement tool and then not called it (`claim_guard` for months, `receipt_guard`
now). A tool in `tools/` is not a control. `preflight_all.py` is the only place
that can say which of the ~45 gates is actually invoked, and it is itself a
hand-maintained registry.

---

## 5. Duplicates and superseded implementations

| Cluster | Count | Finding |
|---|---|---|
| `cain_*.py` | **33** | A one-off script pile, not a subsystem. Explicit version chains: `cain_complete.py` / `cain_complete2.py`; `cain_legal_all` / `_cells` / `_final` / `_last`; `cain_last3` / `cain_last_figs`; `cain_recalc` / `cain_reconcile`. Almost all are single-purpose edits to one analysis. **Recommendation: this is the single largest reducible mass in `tools/`.** |
| `live_rebalance_repro.py` / `_round5` / `_round6` | 3 | Three copies of one reproduction; `_round6` and `_round5` both `import CORE.WORMS.expansion.cutting_edge_model` (`:46`/`:44`). |
| PMB observation | 4 | `pmb_capture`, `pmb_observe_transcript`, `pmb_session_observe`, `pmb_e2e_check` — overlapping purposes, **UNKNOWN** which is canonical. |
| Tests living in `tools/` | 3 | `test_supervisor_load.py`, `test_supervisor_contract.py`, `test_verify_engram_mcp_siblings.py` — not under `tests/`. |
| Committed junk | 3 | `supervisor_mcp.py.bak-20261029-freebuff` (a `.bak` that `.gitignore`'s `*.bak` rule does **not** match, because the name ends `-freebuff`), `go_census.exe` (a compiled binary), `__pycache__/` present. |

`receipt_guard.py` vs `claim_guard.py` are **not** duplicates: one inspects a
completion receipt, the other inspects claim text. They are complementary halves
of RULE 0B-E.

---

## 6. What breaks if `src/CORE` is absent

A directory-wide search for `from CORE|import CORE|from src.` returned **88
matches**. Confirmed importers include:

`accelerator_sidecar.py:49`, `anchor_runtime_gate.py:40,49,58,59`,
`anti_pattern_gate.py:123`, `backtrack_metric.py:257`, `bake_row.py:115`,
`canon_drift_check.py:77`, `dependency_graph.py:25`,
`cutting_edge_ablation_matrix.py:50,98,99`, `expand_bake_pilot.py:14,15`,
`evidence_gate.py:53`, `fix_swallows.py:463`, `gephi_mesh_pipeline.py:123,132,143`,
`evolution_chain_audit.py:145`, `evolution_backfill.py:58`, `mesh_repaird.py:97`,
`mete_reflect_20260930.py:54`, `live_record_probe_315t.py:88,164`,
`probe_intake_fitness_798.py:37,38`, `live_rebalance_repro*.py`,
`monitor_data.py` (10+ sites), `rotate_secret.py:28`, `self_modify.py:275`,
`second_opinion.py:93`, `staged_scanner_gate.py:70,89`, `swallow_inventory.py:140`,
`tideproof_adversarial.py:107`, `transcript_ap5_gate.py:100`,
`terence_invariants.py:233,334,1161,1969,2409`, `trace_intake_798.py:30,31,98`,
`vlp_reflect_20260930.py:18`, `swarm_arena/arena.py:159`, plus 7 `harvest_*.py`
calling `CORE.sentinel_enforcer.permit_here`.

**The finding that matters for publishing:** **three of the eight wired
pre-commit checks import `src/CORE`** —

- `anti_pattern_gate.py:123` → `CORE.compliance.scanner.ASTAntiPatternScanner`
- `staged_scanner_gate.py:70` → same scanner
- `evidence_gate.py:53` → `CORE.WORMS.expansion.config.SecretRotator`

So the gate chain is **not extractable as a standalone repo** without vendoring
the compliance scanner and `SecretRotator`. This independently confirms
`azazael-forensics/CAPABILITIES.md`, which moved `anti_pattern_gate` to its
"coupled — imports CORE" list after a sieve caught it.

Note also the split personality: `evidence_gate.py`'s header argues that a
status field must never be trusted and every check must re-derive from source
(`:16-27`), while `:53` imports the very module whose `rotate_secret` had zero
call sites and returned `success: True` — the example the docstring opens with.
The import is legitimate (it is inspecting that control), but it means the gate
cannot run where `CORE` does not exist.

---

## 7. What I did not do

- Did not read 327 of ~331 files. Counts in §1 are **names**, not verified behaviour.
- Did not execute anything — no `--selftest`, no gate run. Every "wired" claim comes from the hook files' own text, corroborated once by this session's `preflight_all.py` output quoted by the coordinator.
- Did not verify whether `permission_seeking_guard.py` or `nurse_ratchet_release_gate.py` have callers. Both marked **UNKNOWN**.
- Did not inspect the 7 subdirectories (`swarm_arena`, `procdump`, `data`, `graphify-out`, `graph_semantic`, `blender_session_20260930`, `__pycache__`).
- Instrument caveat for the next auditor: `code_search` returns **exit 2 with 0 matches** when scoped to the home directory, but works correctly scoped to a repo directory. A zero from it outside a repo dir is not evidence of absence.

---

*Read-only. No file under `tools/` was edited by this auditor. Every claim above
carries a `file:line` or is explicitly marked UNKNOWN / listed-only.*
