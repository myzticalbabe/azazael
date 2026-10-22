# Bypass Forensic Audit — 2026-10-22

**Authorization:** user order, verbatim: "forensicallt investigate audit every everything that has been bypasses and redo with precision as per mandate" (PRECISION-NOT-BYPASS, AGENTS.md).

**Scope:** every suppression / bypass / silencing mechanism in the repo: ALLOW_* commit-gate constants, gate weakening in history, ratchet baseline edits, `# scanner:ignore` suppressions, test skips, and the by-design non-blocking surfaces.

**Redo standard:** a bypass is redone with precision — the suppressed claim must carry its scope, classification, and evidence. Where the swallow is semantically wrong, fix structurally. Where the swallow is a designed bound, the marker must state that bound, verified from the bytes — never whitewash. By-design and impossible classes are disclosed, not redone.

---

## 1. Method (probes, all live, evidence via tools)

| Layer | Probe | Result |
|---|---|---|
| Commit messages | `git log` with `--grep` for ALLOW_BULK_COMMIT / ALLOW_CLAIM_GUARD / `bypass` / `no-verify` | **0 hits each**. First run carried a pwsh line-continuation backtick that silenced the probe (bake row 19); clean re-run before trusting the zero. |
| ALLOW_BULK usage | full-repo source grep + history | exactly **one** real use, commit `fd777aed`, whose body carries the literal `BULK-JUSTIFICATION:` line — the gate semantics define this as a legitimate declaration, not a bypass. |
| .githooks history | `git log` on `.githooks/` | 15 commits, **all gate-additive** (new checks / tightened thresholds). No cap lowering in history. |
| Ratchet baseline | history of `logs/anti_pattern_baseline.json` | every rebaseline carries a justification message (documented new-code landings, 2026-10-15 → 2026-10-21). Baseline is src-scoped by design. |
| Suppression inventory | fresh classification from `src/CORE/compliance/scanner.py` mechanics, not `SWALLOW_INVENTORY.md` (its 2,994-row section is a **superseded snapshot**) | see §2. |
| Test skips | static grep + spot reads of skip premises | see §4. |

Scanner mechanics pinned before classification (verified from source, not inferred): marker value `# scanner:ignore` matched by line number; an `except` is flagged only when its body is a SINGLE statement; bare `pass` → `silent_except_pass`, bare/constant return → `except_return_default`; a **computed** return (`return exc.errno == errno.EPERM`) is not flagged; marker matched on the statement's line, so cause text must sit on the same line.

## 2. Suppression classification (fresh, 2026-10-22)

| Class | Count | Meaning |
|---|---|---|
| (a) bare suppressions | **23 chip-sites** | marker with no stated cause; redone this pass (§3). Subagent census reported 22 — off-by-one reconciled: the two identical `test_cross_domain_integration.py` cleanup chips (822/827) were counted once. From-bytes tally stands. |
| (b) redundant markers | **53** | markers suppressing findings that cannot fire (chips on `open(..., encoding=)` for open_no_encoding; never-waited `Popen` (rule skips it); rule-skipped statements). Queued, Wave 2. |
| (c) justified | 9 | markers that already carry a real cause (e.g. `conftest.py:146`, `chain_watchdog.py:65`). Left as-is; `chain_watchdog.py:65`'s marker order is cosmetic. |

Specimen executed do-not-fix: `tools/swallow_inventory.py:356`.

> **Wave-2 supersession of this table:** the (a)/(b)/(c) tally above is the wave-1 hand classification. The executed per-line census (§6) supersedes it with measured verdicts: **pre-redo 112 chips / 42 files → load_bearing 83 / redundant_b 25 / invalid_variant 4; post-redo 92 / 32 files → 83 / 5 / 4, BARE = 0.** Counts below the census runs are measured, not tallied.

## 3. Wave 1 — the 23 (a)-sites redone (landed)

Cause text format: `# scanner:ignore -- <verified bound>` on the statement line (precedent `conftest.py:146`). One site was a **structural** fix because the swallow was semantically wrong, not merely undocumented.

**Slice 1 — `65e7b326`** (6 scripts, 9 sites)
| Site | Shape | Redo |
|---|---|---|
| `scripts/chain_watchdog.py:79` | `except Exception: return False` (ctypes OpenProcess probe) | cause: "probe semantics: a failed liveness query means alive-ness cannot be confirmed; False is the safe answer" |
| `scripts/chain_watchdog.py:83` | `except OSError: return False` on `os.kill(pid, 0)` | **structural**: `except OSError as exc: return exc.errno == errno.EPERM` + `import errno` — EPERM means the process exists (not ours) = **alive**; old code called it dead. Chip **erased** (computed return, no flag class). POSIX-only branch: zero delta on this host. |
| `scripts/chain_watchdog.py:99` | `except OSError: return None` (heartbeat stat) | cause: "an unreadable heartbeat IS the no-heartbeat signal; None is the designed marker" |
| `scripts/scrub_probe_telemetry.py:112` | `except (ValueError, TypeError): return None` (json.loads) | cause: "probe contract: unparseable payloads fall outside the census; None marks the row uncounted" |
| `scripts/diagnose_margin_gate.py:48` | `except Exception: return None` | cause: "probe contract: unparseable payload rows are skipped, never crash the diagnosis" |
| `scripts/prune_tensor_genome.py:64` | `except Exception: return None` (`_file_stamp` os.stat) | cause: "an unstat-able path counts as absent; None is the designed missing-stamp marker" |
| `scripts/run_db_monitor.py:40` | `except OSError: pass` (log append) | cause: "the line was already emitted to stdout above; file persistence is best-effort" |
| `scripts/run_db_monitor.py:87` | `except Exception: pass` (stop on Ctrl-C) | cause: "shutdown stop is best-effort; the process is exiting regardless" |
| `scripts/env_drift_alarm.py:48` | `except Exception: pass` (stream reconfigure) | cause: "console reconfigure is best-effort; a stream that refuses UTF-8 still runs the alarm" |

**Slice 2 — `83c05e01`** (4 files, 8 sites)
| Site | Shape | Redo |
|---|---|---|
| `scripts/promotion_signals.py:35` | `_read_json` | cause: "a missing/corrupt state file is 'no signal'; callers render None as the neutral part" |
| `scripts/promotion_signals.py:42` | `_age_h` (getmtime) | cause: "an unstat-able path has no age; None is the designed missing-age marker" |
| `scripts/promotion_signals.py:56` | mesh_cycle age probe | cause: "best-effort freshness probe; age_m stays None and the signal reports its unset/missing path" |
| `scripts/promotion_signals.py:152` | `combined()` product | cause: "documented tolerance: a non-numeric part value is skipped as neutral 1.0 (combined()'s contract)" |
| `scripts/observation_coverage.py:121` | `discover_worms()` | cause: "discovery failure falls back to the already-populated registry; the coverage report still renders" |
| `scripts/bcc_part7_officers.py:91` | amount parse | cause: "formatted/unparseable amount parses to 0; the officer row is retained either way" |
| `scripts/bcc_part7_officers.py:94` | other-amount parse | cause: "same parse-to-0 contract for the other-compensation column" |
| `tools/mesh_repaird.py:112` | `fromisoformat` | cause: "unparseable/missing last_at means the record never ran; leaving latest unset is the designed stale trigger" |

**Slice 3 — `c642bc69`** (conftest + 2 tests, 6 sites)
| Site | Shape | Redo |
|---|---|---|
| `conftest.py:170` | logreport telemetry | cause: "hook contract: logreport must never raise; telemetry append is best-effort" |
| `conftest.py:195` | `_pmb_suggest_for` | cause: "designed degrade: PMB unreachable means no suggestion (docstring: 'Returns text or ''')" |
| `conftest.py:262` | shadow-split guard | cause: "the shadow-split guard is advisory ('a warning, never a failure' per its own header); configure() must not raise" |
| `tests/test_evolution_helpers.py:108` | lock cleanup | cause: "best-effort lock cleanup in tmp_path; assertions already completed above" |
| `tests/test_cross_domain_integration.py:822` | os.remove | cause: "temp cleanup only; assertions already completed, residue in tmp is harmless" |
| `tests/test_cross_domain_integration.py:827` | -wal/-shm remove | cause: "-wal/-shm sidecars can still be locked right after close(); same cleanup-only bound" |

### Wave 1 verification (all live)
- `py_compile` — **13/13 OK** (3.15t interpreter).
- Bare-chip residue scan over the 13 files — **0 of the 23 remain bare**. The 4 line-final markers that still match the scan are non-(a) by class: `test_evolution_helpers.py:95` (b: `open` already carries `encoding=`), `test_cross_domain_integration.py:636` (b: redundant), `chain_watchdog.py:65` (c: reason present inline), `chain_watchdog.py:119` (b: `Popen` never waited — the rule skips it).
- `pytest tests/test_evolution_helpers.py` — **17/17 passed** (16 workers, --timeout=120).
- `tools/anti_pattern_gate.py --check` — **unchanged: 2220 findings / 727 files**, zero regression.
- Worktree dirt before commits was **exactly the 13 intended files** (porcelain-verified), foreign state untouched.
- All three commits passed the full gate battery (focus, index-drift, staged-scanner, canon, ratchet, mesh). Advisory transcript-ap5 FAIL disclosed below.

## 4. Test skips — dead-premise queue

Dead-premise skips awaiting re-derivation under the current interpreter regime (3.15t; the 3.14t regime they encode is retired):

1. `tests/test_cluster_worms.py:35` — **done** (`1986ef1e` 2026-10-22): the recorded premise ("3.14t C extension") was falsified against live bytes; label corrected in place, guard retained (a labeled guard, not a skip).
2. `tests/test_worm_regression.py:173` — **done** (`1986ef1e`): same falsified-premise correction.
3. `tests/test_worm_imports.py:41` — queued: re-derive the premise under 3.15t, then remove the skip or replace it with the true current bound.

All other skips found classify as environment/data-version premises (documented in their `reason=`), not silencing bypasses — no skip-without-cause pattern found.

## 5. By-design surfaces — disclosed, NOT redone

- **transcript_ap5 gate (advisory, post-hoc)** — no assistant-output hook exists in the plugin surface; the gate necessarily runs AFTER emission and can only make visible, never prevent. Observed advisory FAIL every run today against pre-existing findings (session `ses_eb6edc41`, 2). Non-blocking by construction.
- **PAMS outcome observer (check 6)** — deliberately non-blocking: its exit code is ignored so a memory side-effect can never reject a commit.
- **Mesh ledger "carried" rows** — prior `accepted_gap` statuses carried forward are designed behavior of the wire-or-cut preflight.
- **Ratchet src-only asymmetry** — the whole-tree ratchet scans `src/` only; findings outside `src/` are covered instead by the per-file staged check (this asymmetry is exactly why Waves target non-src files through the staged gate).
- **`SWALLOW_INVENTORY.md`** — 2,994-row section is a superseded snapshot; kept for lineage, never consulted as a live count.

## 6. Wave 2 — executed (2026-10-22, this pass)

### 6.1 Census instrument lineage (v4 = executed decision authority)

- Probes v1/v2: discarded pre-adjudication — no built-in validators.
- Probe v3: **discarded, defect proven** — marker excision used `sa[:m.start()]`, which ate the line terminator and shifted every subsequent lineno by one (off-by-one shown on a diffed echo). Its numbers are never citable.
- Probe v4 (executed): per-line census; the sans-run removes exactly the marker token; canary (`lost_in_sans` must be empty) and positive control (removing `conftest.py:146`'s chip must surface exactly the pre-recorded `silent_except_pass` finding at line 146). **Pre-redo verdicts: 112 chips / 42 files → load_bearing 83 / redundant_b 25 / invalid_variant 4; `exposed_beyond` = 0 at every site; canary 0; HEAD stable.** (`wave2_census_v4.json` kept on disk as the pre-redo authority.)
- v4's auxiliary `positive_control_ok=false` was a **check-code bug, not a data bug** (the collected finding pairs adjudicate the instrument VALID): line 87 tested membership with a list literal `[146, "..."]` against tuple-stored pairs (always False); line 89 computed `with − sans` when the informative delta is `sans − with`. Both fixed (tuple literal; direction), and the control re-adjudicated **true** on the post-redo run (v5). Label nuances the probe's plain suffix split cannot see: a cause may sit BEFORE the marker on the same line (the class2 pass labels it `CAUSE-BEFORE`; the label classifier emitted 1 = `scripts/chain_watchdog.py:65`, verified labeled in truth), and `silent_except_pass` fires only on bare `except`, never `except <type>`.

### 6.2 Redo slices landed (2026-10-22)

| Commit | Slice | Contents |
|---|---|---|
| `1986ef1e` | skip labels | §4 items 1–2: falsified "3.14t C extension" premise labels corrected in 2 test files; guards retained. |
| `375405eb` | A — bare load_bearing cause-labeled | **20 bare chips → verified inline causes, 5 files**: 7 test-import sites (hoisting the function-level import would register a worm at collection; the sibling suite asserts the module unimported — full rationale lives in the suite docstrings), 11 cain sites (emoji literals are captured CAIN subject data / mapped entries, not decoration), 2 nativestack sites (strings are WinDbg `.sympath` advice, not repo paths). `py_compile` OK ×5 (3.15t); per-file marker counts unchanged (6/2/2/9/4). |
| `1ecb07e8` | B1 — bare dead erased | 5 bare chips whose class cannot fire: Popen-not-a-run-call ×2 (`scripts/chain_watchdog.py:119`, `scripts/launch_live_windows.py:49`), `open` already carrying `encoding=` ×2 (`test_cross_domain_integration.py:636` — compiled, never executed: module-level benchmark suite; `test_evolution_helpers.py:95`), rb-binary ×1 (`test_spine_mesh.py:487`). |
| `bfe115fd` | B2 — bare dead erased | 5 more (4 files): encoding-present `open` (`cain_recalc.py:77`), Popen (`comfyui_flux_headless.py:105`), typed-except (`gust_lite.py:125` — autopsied first: `except Exception as exc` whose body **records** the failure, `results.append({..., "error": str(exc)[:120]})`; no swallow → erase-only correct), binary open + Popen (`nativestack.py:56/:81`). |
| `20a3c4ff` | B3 — false claims erased | 10 cause-labeled dead chips + their attached cause texts erased, 6 files (`accelerator_sidecar.py:198/:212`, `agent_board.py:105/:217/:218`, `audit_append_stress.py:70`, `live_rebalance_repro.py:34`, `supervisor_mcp.py:124/:465`, `verify_engram_mcp.py:549`): each cause described a rule that cannot fire on that construct (`open_no_encoding` cannot fire on rb reads; `subprocess_no_timeout` skips `Popen`), while the operative bounds exist as code (`communicate(timeout=)`, `wait(timeout=900)`+kill, rb semantics). Keeping the chips would have preserved the lie that a suppression exists. |

Verification per slice: `py_compile` OK ×9 (B1/B2 files) and ×6 (B3 files) on 3.15t; the staged-scanner gate PASS per slice is the live per-file proof that the erasures surface zero findings.

### 6.3 Non-suppression reclassification (no action, disclosed)

8 chips are marker text as **prose**, not suppressions: markers inside string literals / doc prose — `tests/test_scanner.py:254`, `:291`, `tools/graph_semantic/semantic_layer.py:424`, `tools/swallow_inventory.py:206` (census class `invalid_variant`, classifier label META-STRING); and markers on prose-comment lines — `tools/encoding_audit.py:213`, `:242`, `tools/hook_dispatch.py:283`, `tools/swallow_inventory.py:22`. Remaining redundant pool after the 20 erasures = **5**: these 4 comment-prose rows + the executed do-not-fix specimen `tools/swallow_inventory.py:356` (§3; keep + disclose).

### 6.4 Post-redo census (v5, executed — every prediction matched)

The probe was retargeted to `wave2_census_v5.json` (pre-redo v4 preserved) with corrected control checks and run at HEAD `20a3c4ff`: **92 chips / 32 files → load_bearing 83 (82 CAUSE-AFTER + 1 CAUSE-BEFORE), redundant_b 5, invalid_variant 4; BARE = 0; canary 0; `positive_control_ok` TRUE; `ctrl_A_fresh_identical` TRUE; HEAD stable.** The label split comes from the executed classifier pass (`wave2_v4_class2.py` against v5): all 20 former-bare chips now carry verified inline causes, so the bare redo-queue is empty.

### 6.5 Remaining queue (beyond this pass)

1. `tests/test_worm_imports.py:41` dead-premise skip (§4 item 3) — re-derive under 3.15t, then remove or re-bound.
2. Optional cosmetic: normalize `scripts/chain_watchdog.py:65` marker order (the verified rationale precedes the marker on the same line — legal, truth-labeled; no urgency).
3. `SWALLOW_INVENTORY.md` regeneration as a separate lane (its snapshot is superseded per §5; never consulted as a live count).

## 7. Encounter-time evidence

Bake lane `state/bake_harvest_laneB_2026-10-22.jsonl` rows 18–20 record: the checkpoint-assert vs visible-bytes near-miss (row 18), the pwsh-backtick silenced-probe fix (row 19), and the whole-index bulk-gate collision with Lane C's mid-landing bundle where the precise response was hands-off waiting, never `ALLOW_BULK_COMMIT=1` (row 20). Lane merged with `tools/merge_bake_lane.py --apply`: **BASE=10974 ACCEPTED=20 MERGED=10994 DROPPED=0**. Wave-2 rows 21–25 were appended at encounter time and merged the same day: **ACCEPTED=25 MERGED=10999 DROPPED=0** (lane file committed with this REPORT in the artifacts slice).
