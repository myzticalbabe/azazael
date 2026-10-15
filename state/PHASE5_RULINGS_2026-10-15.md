# PHASE 5 RULINGS — #640 (EP417 seam) + #636 (ablation dynamic-load)

Execution of engram #721 item 5. Both items were "analyse and rule"; this file is
the ruling. Code landings are in commit **8a129987**.

---

## #640 — EP417 seam analysis: **WIRED. No seam work needed.**

**What EP417 is.** `state/sota_batches/batch02/` records it as *"EP417 — S-RCT
agentic experimentation (2608.02345)"*: simulated-trial rollout vetting, pre-period
calibration, and a within-subject A/B comparison.

**Measurement (not inference).** EP417 was initially invisible because the
exercise-only audit lists only symbols with NO module-qualified reference outside
`technique_wiring/`. EP417 is absent from those 29 rows, which is the *positive*
signal. Grepping the code for the technique name finds a real, two-sided seam:

| Side | Location | Role |
|---|---|---|
| Registration / exercise | `src/CORE/technique_wiring/_l3_verify.py:456` | `"""S-RCT: pre-period calibration + within-subject variance cut."""` |
| Registration binding | `src/CORE/technique_wiring/_l3_verify.py:638` | registers `"CORE.verification_gate:preperiod_calibrate"` as EP417's mechanism |
| **Production seam (calibration half)** | `src/CORE/verification_gate.py:541` `preperiod_calibrate()` | least-squares scale+bias over pre-period predicted/actual pairs; reports the squared-error cut |
| **Production call site** | `src/CORE/verification_gate.py:483` | `_cal = preperiod_calibrate(_x, _y)` — the gate's own predicted (explorer) / actual (validator) pair, on the SAME id-join the divergence check uses |
| Production seam (variance half) | `src/CORE/verification_gate.py:572` `within_subject_compare()` | paired differences for the within-subject arm |

**Why this is a seam and not a dangling report.** The in-tree comment at
`verification_gate.py:461` states the history precisely: `preperiod_calibrate` was
registered as EP417's mechanism with **zero callers repo-wide**, and was then
*absorbed* — the gate already holds exactly the pair the fit needs, so the fit runs
on real gate data and its result enters `reasons`, i.e. the gate's **verdict**, and
(through the EP446 hook) the **audited evidence**. A technique whose output reaches
a verdict and the audit trail is wired.

**Ruling.** EP417 is ADOPTED and already production-wired. It must **not** be
retired, and no new seam should be manufactured — adding a caller would recreate
the "function nothing calls" defect this campaign removes. It must also not appear
in the BLIND-22 proposal list (`state/BLIND22_PROPOSALS_2026-10-15.md`); it does
not.

---

## #636 — ablation dynamic-load ruling: **KEEP dynamic. Correct the comment.**

**What the code did.** `src/CORE/NeuralPipeline.py` imported the model in a
function-level `try/except ImportError`, with `CuttingEdgeModel = None` on failure,
under this comment:

> `# Lazy import: cutting_edge_model.py is not yet committed. When present, ...`

**Measurement.** Three claims were checked, and one of them was false:

| Claim | Measurement |
|---|---|
| "not yet committed" | **FALSE.** `git ls-files --error-unmatch src/CORE/WORMS/expansion/cutting_edge_model.py` resolves it; `git status --porcelain` for it is empty (tracked, clean); the file is 119,051 bytes dated Oct 14 11:28. |
| it imports | **TRUE.** `import CORE.WORMS.expansion.cutting_edge_model` succeeds and exposes both `CuttingEdgeModel` and `CuttingEdgeConfig`. |
| the import is USED | **FALSE before this change.** Grepping the whole tree, `NeuralPipeline` matched only its own import block (lines 136–147) — no construction, no routing, no `enable_cutting_edge`. The backend was reachable only from tests. |

**Ruling: KEEP the dynamic load — but for the real reason.** The laziness is not
about availability (the module is present); it is about the **registration side
effect**. Importing the module executes its `@register_worm` decorator, so a
module-scope import would register `CuttingEdgeModel` at *collection* time for
every pipeline, including the ones that never opted in. That is measured, not
argued: `tests/test_neural_pipeline_cutting_edge.py::test_default_pipeline_does_not_build_the_model`
asserts *"off means the module is never imported"*, and it passes.

**The fallback is fail-open and stays that way.** `CuttingEdgeModel = None` on
`ImportError` means constructing a pipeline never depends on the optional module.
Only the *opt-in* path needs it, and that path now raises a `RuntimeError` naming
both the missing module and the env var rather than failing later with an
`AttributeError` on `None`.

**Actions taken (commit 8a129987).**
1. The stale "not yet committed" comment is replaced with the measured reason, so
   the next reader does not conclude the ablation is unavailable.
2. `COMPONENTS` joins the import, for `ablate_cutting_edge`'s validation.
3. The three missing attributes/methods are implemented: `use_cutting_edge`,
   `cutting_edge_config` (mapping **or** a ready `CuttingEdgeConfig`),
   `opt_in_from_env()`, `cutting_edge_switches`, the lazily built and **cached**
   `cutting_edge_model`, and `ablate_cutting_edge()`.

**Why caching is part of the ruling.** `test_f_the_accumulated_bias_persists_into_the_next_run`
proves the model is built ONCE and reused: run 2's pre-loop routing equals run 1's
post-loop routing exactly, because `gate_bias` is mutated in place and the model is
cached on the pipeline. A per-run rebuild would reset the bias and silently change
what the ablation study measures, so the cache is a correctness property, not an
optimisation.

---

## Standing error-capture (policy #716)

| Mistake | Caught by | Fix | Outcome |
|---|---|---|---|
| Invented a `train_records` guard the contract does not impose | the 2 failures sharing one cause (`No training data found for source=SystemZ` where the test passed features directly) | removed the guard | 16/16 |
| `dict(cutting_edge_config)` on a `CuttingEdgeConfig` instance | `TypeError: 'CuttingEdgeConfig' object is not iterable` in 2 tests | accept either a mapping or an object; keep the object so a caller's validated config is not re-derived | fixed |
| Hard-coded `timeout=60.0` in the pool step | `test_a_timed_out_step_reports_a_reason_and_no_delta` got a *successful* step from a 50 ms deadline | forward the caller's `timeout` | fixed |
| `registration_skipped` set only in the else-branch of the trained path | `test_c_an_untrained_run_files_no_model_version` (the no-MoE *skipped* branch) | moved the report out of the branch, after the trained decision | 17/17 |
| A large `python - <<'PY'` heredoc with `"""` payloads was truncated / CRLF-mangled by the shell, so a 12-edit patch silently never ran | the script reported `SyntaxError: unterminated triple-quoted string literal` | wrote the patch as a FILE and ran it with an absolute path from the repo cwd | see lane rows |

## Verification for this ruling

* `tests/test_neural_pipeline_cutting_edge.py` — **16/16**
* `tests/test_cutting_edge_production_fixes.py` — **17/17** (was 12 passed / 5 failed: measured identical before and after the first pass, so the first pass caused **no regression**, and completing the wiring closed all five)
* Cutting-edge family (7 files, incl. `test_cutting_edge_model`, `test_nulls_masks`, `test_learning_rl_keys`, `test_learning_worms`, `test_replay_failed`) — **137 passed** on python **3.14.7** and on the **3.15t** venv (`C:/Azazael/.venvs/py315t`)
* Ratchet delta-zero (2670 = 2670); staged scanner, canon drift, mesh — all green
