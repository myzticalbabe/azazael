# NEURAL MESH — PRIORITIES, relisted 2026-09-29

Relisted from measured state, not from the previous list. Three items on the
old list were wrong and are corrected below; two are now closed.

Every number here was read from the live tree or the live ledger on
2026-09-29. Where a claim could not be measured it says so rather than
carrying the old figure forward.

---

## Closed today

**Fabricated route telemetry — removed and now stable.**
The `8000.0ms` eBPF collection window, the interleaved alert/probe counters and
the malformed `route:windows>route` key are gone from `~/.azazael/spine_state.json`.
Verified across three consecutive save/load cycles: 10 genuine ~95ms samples
per wsl2 route preserved, zero `8000.0` samples anywhere, counters at 0 and
pinned by a watermark that survives the fold-in.

**The graph — rebuilt and scoped.**
28,279 files / 451,307 nodes / 638 MB → **3,121 / 47,273 / 46 MB**, rebuild
31 min → **75 s**. Top hubs are `InferenceEngine`, `SpineCycleWorm`,
`NatureCluster`, `LocalMemoryStore`, `DirectMemory`. Both freshness gates are
green: `artifact_freshness` exits 0 on all 8 derived artifacts, and
`capability_liveness` exits 0 with `invalidation_persisted` and
`route_ledger_writers` reporting `ok`.

---

## P0 — the "reduction reads as absence" shape is fixed in four places and is not yet a class

Four stores in the brainstem shared one defect: the read paths fold the saved
file back in before every write, so **a value assigned downward in a monotone
store loses on the next save.**

| store | reduction | what undid it | status |
|---|---|---|---|
| fixtures | `purge_fixtures` | re-adopted from disk | tombstoned |
| Q evidence | `invalidate_q` | `max()` on the count | evidence floor |
| homeostat counters | counter reset | `max()` on successes/failures | counter floor |
| Q table | `cap_q_tables` | ranked by evidence, so a floored key sorted first | floored keys sort last |
| prune stage | `_stage_prune` | called count 0 "dead" | skips floored keys |

Five, not four. The fifth was found *after* the first four were fixed, because
fixing a reduction is what made the key look absent to the pruner: the routes
restored at 09:47 were tombstoned `neural_loop_prune` by 10:05.

This is a shape, not a bug, and nothing yet prevents the sixth. A store where
a reduction is indistinguishable from absence will reproduce it. Worth a
checker that scans for the shape — a write that lowers a value in a store whose
read path merges with `max()`, with no watermark alongside it — rather than
five more fixes discovered one symptom at a time.

## P1 — 995 lines exist only in WSL and in no commit

The old list said "~326 lines in 4 files". That was wrong on both count and
framing. Measured by md5 across `src/ scripts/ tools/ tests/`:

- **5 files, 995 lines, present in WSL and absent from Windows entirely:**
  `tests/test_chain_refactor.py` (285), `tests/test_session_operations.py` (312),
  `tests/test_chain_lock.py` (205), `scripts/run_full_pass.py` (131),
  `tests/test_morphing_learn.py` (62).
- **212 further files differ**, and the sampled direction is **Windows ahead**
  (`spine_registry.py` 3761 vs 4008, `direct_memory.py` 1994 vs 2010). The WSL
  tree is stale, not holding work.

Order matters and the reason is the `G:` item below: commit the 5 WSL-only
files first, because they are the only unambiguously lost work. Only then
reconcile the 212, per file and in the direction the diff shows.

## P2 — reset exposure has no guard

28 `reset:` entries in the reflog. One at **04:02 today** to `HEAD~1`, after
which 620+ files were dirty and three modules were gone; recovery was manual
(`73ee26af`, "Restore three modules lost by the hard reset"). A reminder does
not survive a bad night. A pre-command check that refuses `reset --hard` /
`reset HEAD~1` when the tree is dirty or unpushed commits exist is the fix.

## P3 — the green-suite claim is still false

`logs/suite_run_20260929e.log` is `passed=3965 failed=25`, and there is no
suite evidence for the current revision. What today's work actually ran:
318 passed across 15 affected suites, then 115 and 124 across the
neural-mesh subset — with 2 failures (`test_nature_cluster_emits_spans`,
`TestGRPOTrainer::test_get_policy_all_contexts`) that I confirmed fail
identically at `HEAD`, so they are pre-existing and not mine. That is evidence
about the suites I touched, and no evidence at all about the other 3,900.

## P4 — `G:/source-of-truth/azazael` is unversioned and still a sync target

`git rev-parse` there returns `fatal: not a git repository`. A blind
`sync_all.py` push would publish a regressed revision to the "source of
truth" with no history to recover from. **HOLD** until P1 is done and the
target is either initialised as a repo or taken out of the push set.

## P5 — a duplicate module with no generator

`scripts/monitor_learning.py` and `src/SCRIPTS/monitor_learning.py` are
byte-identical (both md5 `4345f07971f7fe03bfbc09dca7f2f83e`) and nothing
generates one from the other. Deliberately left undecided: which copy is
canonical is a call for whoever owns it, and both are referenced.

## P6 — 109 pending functions, 0 wired, 0 retired

From the regenerated wire-or-cut table: 171 unreferenced, of which 62
dispatched and **109 pending** — 56 with no reference anywhere, 53 reached only
by tests. The table is measured and current; the backlog has not moved.

## P7 — `route_censoring` is unproven, and that is the honest state

`capability_liveness` reports `unproven`, not `ok`: no unreachable peer has
been observed since the fix, so there is nothing to attribute. The
capability exists, the failure mode has not recurred, and neither fact is
evidence that the capability is why. Settling it needs one unreachable peer,
or a `--since` window in which one occurred. Not a code defect — an evidence
gap, and it should not be closed by assertion.

## P8 — the tree is being written while it is being worked on

40 files were dirty from live `chain_controller` jobs during this session, and
the `meta` job is what purged the restored routes at 10:05. Every commit today
was path-scoped for that reason. Worth deciding whether those jobs should run
with `--allow-mutations` against a working tree at all.

## P9 — graphify skill/package version skew

`graphify_interpreter.resolve_graphify_python()` warns on every refresh: skill
0.9.55 against package 0.9.50. It resolves and runs correctly, so this is not
blocking, but the mismatch is reported on every pass and nobody has acted on it
because it is only a warning.

---

## Deliberately untouched

- **Firewall rule for TCP 18210** — needs admin and an explicit go-ahead.
- **The duplicate-module decision (P5)** — the call belongs to its owner.
- **`git push` / `sync_all.py` to `G:`** — see P4.
