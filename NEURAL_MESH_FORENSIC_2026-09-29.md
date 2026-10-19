# Neural Mesh Forensic — 2026-09-29

> **3.14 RETIRED 2026-10-19** — this forensic ran on `venv-314t`. Production is
> now the 3.15t venv (`C:\Azazael\.venvs\py315t`); the only sanctioned 3.14
> runtime is `C:\Azazael\.venvs\py314m`. Measurements below remain valid as a
> record of that date, not as a description of the current runtime.

**Status: CURRENT. This document supersedes every `NEURAL_MESH_*` audit listed
under "Supersedes" below.** Those documents remain on disk as dated records of
what was believed on their date. Their numbers are NOT current, and reading one
today will produce confidently wrong conclusions — see §6.

**Host:** Windows 11 (`C:/Users/clint/azazael`) · **Interpreter:** `venv-314t`
(Python 3.14.7) · **Revision at time of writing:** `bc4d51db`

**Method:** the live tree, the live runtime state, and the live git history.
Every number below was measured today with an instrument named inline. No
generated snapshot or cached census was trusted.

---

## 0. The finding that mattered

Every instrument the project owns reported the mesh as healthy. The code was
present. The artifacts were fresh. The type gate counted files. The suite had
a test *for the very mechanism in question*. And that test was **red**.

The live ledger said:

```
entries with a censored counter: 0   (of 492)
route failures on the ledger:   180  (wsl2-ubuntu 117, wsl2-kali 63)
```

Zero. Not low — zero, ever. A mechanism had shipped, been reviewed, been
documented with a docstring explaining precisely why it existed, and **had
never executed once in production.**

That is the class this document is about:

> **Code that exists, is documented, and has never run is worse than code that
> is absent** — because it silences the followup. A missing feature produces a
> ticket. A present-but-inert feature produces a false all-clear.

Three separate mechanisms were suppressing that signal, and each is now fixed.

---

## 1. Route censoring never executed

**The mechanism.** `record_outcome(..., censored=True)` exists to keep
infrastructure noise out of the policy estimate: a refused connection because
no listener is running is *not* a bad route. Shipped 2026-09-27/28.

**Why it never ran — three independent causes:**

| # | Cause | Evidence |
|---|---|---|
| 1 | `MeshRouterWorm.send()` routed its censored case **around its own `record_route_result` seam**, calling `record_outcome` inline | `mesh.py` `send()` else-branch (pre-fix) |
| 2 | `record_route_result` had **no `censored` parameter**, so the seam could not express what it was asked to record | signature was `(dst_env, success, duration_ms=0.0)` |
| 3 | The test that pinned all of this was **failing in the committed tree** | `test_mesh_transport_e2e::test_router_learns_only_learnable_outcomes` |

**The red test was the only thing pointing at it.** It is now green, and it is
backed by `tests/test_route_censoring.py` (14 tests, verified to fail against
the pre-fix code).

---

## 2. The cycle manufactured route verdicts

`SpineCycleWorm._mesh_route_feedback` phase 1 settled the route it had proposed
the previous cycle from `_nature_success_rate(dst)` — **the health of the worms
on the far side** — and wrote that number into the route Q-table as the route's
verdict.

Phase 2 always proposes to the *least-healthy* nature and **never delivers on
it**. So every cycle manufactured a standing verdict for a route that had never
been used, and nothing could clear it: a deprioritised route is never re-chosen,
so it never produces the successes that would raise it. This is playing-field
TODO G2's self-sustaining penalty, produced by the loop built to close it.

**Fixed:** the cycle now *reads* the ledger and reports. It never writes. One
writer per fact — `send()` records a delivery, the cycle observes it.

---

## 3. eBPF kernel telemetry was written as a route verdict

`scripts/spine_cycle_apply.py` runs **hourly** (`schtasks /tn AzazaelSpineCycle`,
`chain_controller.py` 3600s). It wrote:

```python
m.record_route_result(env, n_alerts == 0, 8000.0)
```

An **eBPF syscall-alert count**, recorded as whether the route delivers, with
the **8s collection window hardcoded as if it were a route latency**. This was
the dominant writer of the live route ledger, and the source of the
alternating `[95ms, 8000ms]` history that the 09-16 audit had flagged as a
"timeout signature" without identifying the writer.

**Fixed:** kernel telemetry still trains the homeostat, under its own
`ebpf` namespace, where it cannot move a route weight.

**Live repair applied:** the two routes' manufactured penalties were discounted
with `invalidate_q(factor=0.0)`. Their `q_effective` is now `0.0000` — neutral,
re-learning from honest evidence. The raw `q` is preserved, per that function's
"discount, do not erase" contract.

---

## 4. A malformed key, and an unvalidated model in the write path

The live ledger carried `route:windows>route` (2 successes, dated 2026-09-17) —
a route whose destination is literally the string `route`.

**Root cause:** `spine_cycle_apply.py` builds its candidate order from
`GemmaDriverWorm.rank_trials(...)`, which is **model output**, and passed the
result straight into `record_route_result()` as a destination name. A
hallucinated entry became a real key in the brainstem.

**Fixed, in two places:**
- upstream: the ranked order is filtered to the declared candidates, and drops
  are logged rather than silently accepted;
- at the seam: `record_route_result()` refuses an empty dst, a dst containing
  `>`, or one colliding with a ledger namespace.

The key was purged from the live ledger and **tombstoned**, so it cannot be
re-adopted by a merge.

---

## 5. `invalidate_q()` was a no-op that reported success

Found while applying §3's repair, and outside the original scope. Reported
because it is the same failure class as §0, one layer down.

Every read path merges counters with `max()` — which is what makes N parallel
save-then-exit jobs compose instead of clobbering each other. It also means a
count can never go **down**. And `invalidate_q()`'s entire job is discounting
evidence whose cause was fixed.

Reproduced on an isolated store, before the fix:

```
invalidate_q said : evidence_to = 0
in memory now     : n = 0
after save (mem)  : n = 100
on DISK           : n = 100
```

It set the count, journalled `q_invalidated`, emitted a spine event, and then
`save_spine_state()`'s `_merge_disk_state()` folded the old number straight back
over it. **The journal and the monitors were counting invalidations that did not
happen.**

**Fixed** with an evidence *floor* — the same shape of fact as the existing
purge tombstone, but for a reduction. Persisted, bounded, and honoured on all
three read paths (`_merge_disk_state`, `load_spine_state`, `merge_spine_gossip`)
so a peer cannot resurrect a discounted count either. It is a watermark on
*restoration*, not a lock on learning: a genuine new observation still raises
the count.

This added an optional `q_evidence_floor` key to `spine_state.json`. Additive;
a store written before the fix reads it as absent.

---

## 6. The audit trail was itself confidently-incomplete

Six `NEURAL_MESH_*` documents plus `FORENSIC_FOLLOWUPS_2026-09-28.md` each
carry their own numbers, each written on its date, and **nothing marked a newer
audit as superseding an older one.**

`NEURAL_MESH_GAP_AUDIT_2026-09-14.md`, read today, states correctly and
uselessly that the global quarantine store does not exist. It does. A reader
with no date discipline would draw a false conclusion from a document that was
true when written.

**Fixed:** every superseded document now carries a header naming this one.

---

## 7. What the previous forensics got right

Credit where due. The 2026-09-28 forensic was high quality, and its blocked
items have all since landed:

| 09-28 finding | State on 2026-09-29 |
|---|---|
| Three-way tree divergence | **resolved** — `spine_registry.py` and `mesh_transport.py` byte-identical Win↔WSL |
| Gossip allowlist absent from Windows | landed (`_signer_is_known`, `spine_registry.py:2938+`) |
| Global quarantine store absent | landed (`_QUARANTINE_ITEMS`, `spine_registry.py:521`) |
| #6 "no trust/pin CLI exists" | landed — `scripts/mesh_trusted_key.py` |
| G1 brainstem saturation | **verified fixed on live data**, see below |
| G2 ledger cannot forget | forgetting curve landed; the route half is what §§2–3 fixed |
| #8 metacog false failures | landed (`metacog_cycle.py:135`) |
| #9 `cmd_maintain` has no seam | landed (`data_retention.py:961`) |
| #2 `state_saved` producer | found — `meta_cognition.py:684`; 4,005 rows / 316 MB, now capped at 50; store 984 MB → **226 MB** |

**G1 verified against live data**, not assumed:

| | 2026-09-16 | 2026-09-29 |
|---|---|---|
| Q keys | 76 | 492 |
| Saturated \|q\|>0.999999 | 29 (38%) | **3 (0.6%)** |
| Weight-without-count keys | 6 | **0** |
| Median pull count | 21–31 | **153** |

---

## 8. Standing rule

Added as `tools/capability_liveness.py`, because a rule nobody runs is a
sentiment.

> **For any capability added to suppress a failure mode, require a live counter
> that proves the failure mode stopped. A counter of zero is not neutral — it
> is the absence of evidence that the capability ever ran.**

The tool pairs each capability counter with the failure it suppresses, and
reports three non-failing states deliberately:

- `dormant` — the failure has not occurred, so a zero counter is correct;
- `unproven` — activity exists but cannot be attributed to the current code
  (use `--since <iso8601>` to attribute). **Without this state the tool would
  pin 181 pre-fix failures as a permanent failure, and a gate that cries wolf
  gets switched off.**

Current live status:

```
route_censoring            unproven   needs one unreachable peer to settle
invalidation_persisted     ok         2 evidence floors honoured
route_ledger_writers       ok         no hardcoded-period latency series
derived_artifacts_fresh    fail       8 stale artifacts
```

---

## 9. Open, not fixed

| # | Item | Status |
|---|---|---|
| 1 | **Destructive-reset exposure** — 27 resets in reflog, 4 after the 09-28 forensic said "commit early", including one to `HEAD~1`. 620 dirty files. A pre-commit hook exists but does not survive `reset --hard`. Commit `73ee26af` is titled *"Restore three modules lost by the hard reset."* | **needs a guard, not a reminder** |
| 2 | **Mirror sync half-done** — `data_retention.py` (142 lines), `mesh_listener.py` (99), `evolution_cycle.py` (57), `monitor_learning.py` (28) exist only in WSL. No commit contains them. `artifact_freshness.py` cannot see this: it compares artifacts to sources *inside* the Windows tree. | open |
| 3 | **Wire-or-cut is purely additive** — 106 pending, `wired: 0`, `retired: 0`, 47 `dead_candidate`. The backlog grew 101 → 106 across two days of forensics. | needs a decision mechanism |
| 4 | **8 derived artifacts stale** | refresh pending |
| 5 | **Duplicate module** — `src/SCRIPTS/monitor_learning.py` is byte-identical to `scripts/monitor_learning.py` (md5 `4345f07971f7fe03bfbc09dca7f2f83e`). Two hand-maintained copies, no generator. | open |
| 6 | **`G:/source-of-truth` is unversioned** (`fatal: not a git repository`) and still a `sync_all.py` push target. A blind sync now would publish a *regressed* revision. | **HOLD** |
| 7 | **Green-suite claim was false** — latest run `passed=3965 failed=25`. Now repaired for the type-check gate; a full re-run is still owed. | open |

---

## 10. Supersedes

These remain on disk as dated records. Their numbers are historical.

- `NEURAL_MESH_GAP_AUDIT_2026-09-14.md`
- `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-15.md`
- `NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`
- `NEURAL_MESH_ADVERSARIAL_AUDIT_2026-09-16.md`
- `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md`
- `NEURAL_MESH_LIVE_MONITOR_RECONCILIATION_2026-09-24.md`
- `FORENSIC_FOLLOWUPS_2026-09-28.md` (§7 records which of its items landed)
