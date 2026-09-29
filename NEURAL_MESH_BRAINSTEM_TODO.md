# NEURAL MESH BRAINSTEM — PLAYING-FIELD TODO

> ## SUPERSEDED — read `NEURAL_MESH_FORENSIC_2026-09-29.md` first
>
> This document is a **dated record of what was believed on its date**. Its
> central evidence table is now known to be wrong in a way that matters, and
> the data it cites has been removed from the live ledger.
>
> Specifically, the `8000.0` latencies below were **not** a timeout signature.
> They were the eBPF collection window, hardcoded into a route record by
> `scripts/spine_cycle_apply.py` and written as if it were a route duration.
> The sync-path bug this document attributes them to was real and was fixed in
> `56c15679`, but these numbers never measured it. The per-route counters were
> an unseparable mix of that alert count and real `wsl echo` probes. All of it
> was removed on 2026-09-29 and the genuine ~95 ms samples preserved.
>
> G2.1 is also marked **done** below, and was not: `invalidate_q` was a total
> no-op until 2026-09-29, because every read path merged the count back with
> `max()` and undid the reduction on the next save. The journal counted
> invalidations that never happened. See the forensic for the fix and for the
> three further stores that had the same defect.

**Date:** 2026-09-16
**Scope:** `CORE/spine_registry.py` (the Q brainstem), `CORE/WORMS/expansion/mesh.py` (route
learning), `CORE/WORMS/expansion/spine.py` (ranking consumers), `tests/conftest.py` (isolation).
**Method:** read the live artifacts, not the code's claims about them. Every number below was
taken from `~/.azazael/spine_state.json` (208 333 bytes, `saved_at 2026-09-16T02:05:06`) and from
a fresh import of the live module.

---

## 0. How to use this document

Each item is a checkbox with a **pre-flight** block. A pre-flight must be answered *before* the
change and re-answered *after*; the second answer is what makes the item done.

| Field | Meaning |
|---|---|
| **EVIDENCE** | the measurement that justifies the work — no item exists without one |
| **CLAIM** | the falsifiable statement the change is supposed to make true |
| **FALSIFY** | the observation that would prove the claim wrong |
| **REPRO** | how to reproduce the current (broken) behaviour, pre-change |
| **VERIFY** | the check that distinguishes fixed from merely edited |
| **BLAST** | what else reads this |

---

## 1. The playing field, as measured

I went looking for the gem stones rather than the bug list. Four measurements reframe the whole
subsystem; a fifth is the reason the first four stayed invisible.

### The census

| Quantity | Value |
|---|---|
| Q-weights live | **76** |
| Q-update counts live | **70** (⇒ **6 keys carry a weight and no count**) |
| Keys pinned at the clip (\|q\| > 0.999999) | **29 of 76 = 38 %** |
| Keys pinned at the clip in the *last saved* state | **3** |
| Active keys' pull counts | 21 – 31 |
| `_Q_ALPHA_BASE` | 0.2, adaptive, clamped to [0.05, 0.5] |
| Default `_Q_VARIANCE` for an unmeasured key | 0.25 ⇒ **alpha = 0.4** |

That 3 → 29 delta is the whole story in one number: **saturation went from 4 % to 38 % inside a
single process lifetime.** It is not a steady state. It is a trend, and it is still running.

---

## 2. GEM STONE G1 — the brainstem saturates before it can rank anything

**EVIDENCE.** With the default variance (0.25) the adaptive alpha is 0.4. A key starting at
neutral therefore reaches **0.99999 in 22 pulls**:

```
q = q + a*(reward - q),  a = 0.4,  reward = +1
n = 22  ->  q = 0.999989
```

The mesh's live keys have 21–31 pulls. The arithmetic and the data agree to the pull.

**CLAIM.** `q_order()` — the function that decides which worm a nature cluster runs first —
sorts primarily on a value that is a **plateau** for 38 % of the table. For the most-used worms,
the sort key carries no information, so ordering is decided by the scar band and by input order.

**FALSIFY.** If the 29 clipped keys were separated by *something real*, the ordering would still
be meaningful. They are not: they are equal to within 1e-5, and the value of a key with 31
all-positive pulls is indistinguishable from one with 10.

**REPRO.**
```python
from CORE import spine_registry as sr
q, c = sr.get_q_weights(), sr.get_q_update_counts()
sat = [k for k, v in q.items() if abs(v) > 0.999999]
print(len(sat), "of", len(q))          # 29 of 76
print(sorted(c[k] for k in sat))       # pulls behind those ties: 10 .. 31
```

**THE INSIGHT.** The adaptive-alpha feature (`_Q_ALPHA_BASE`, "G2") was added so that volatile
keys learn faster. It achieves that — and it is self-defeating. High variance selects a *higher*
alpha, which drives the key to the clip *sooner*, which is a state in which the key can no longer
express the variance that selected the alpha. **The feature that was added to make volatile keys
responsive is the precise mechanism that erases them.** The clip is not a safety rail here; it is
the attractor, and the adaptive alpha accelerates the fall.

**THE FIX (minimal, principled).** Rank on an **evidence-shrunk** value, not the raw EMA:

```
q_eff = q * n / (n + K)          # K = 8
```

A key with 4 pulls at −1.0 contributes −0.33; a key with 40 pulls at −0.9 contributes −0.75.
Shrinkage is the standard Laplace/Jeffreys answer to "how much do I trust a mean from n
observations", and it makes three problems collapse into one fix: the plateau becomes a ranking
(the top of the table now fans out by evidence), the pull count becomes load-bearing (so losing
one is visibly a lost *ranking*, not a silent 0.0), and selection no longer needs a separate
"minimum pulls" quota bolted on beside Q.

- [ ] **G1.1** Add `q_effective(nature, worm)` + a bulk `get_q_effective()` that shrinks by pull count.
- [ ] **G1.2** Rank `q_order()` on the shrunk value; keep the raw value readable and *documented as raw*.
- [ ] **G1.3** Make `get_route_usage()["effective_weight"]` derive from the shrunk value so the telemetry
      reports the weight routing would actually use (its docstring currently promises this and does not deliver it).
- [ ] **G1.4** Regression test: a 4-pull −1.0 key must rank **above** a 40-pull −0.9 key. Pre-fix both
      are in the same band and the assertion fails.

> **PRE-FLIGHT**
> - EVIDENCE: 29/76 at clip; 22 pulls at alpha 0.4 reaches 0.99999; live pulls are 21–31.
> - CLAIM: shrinking by `n/(n+K)` restores a strict ordering among the clipped keys.
> - FALSIFY: the shrunk ordering still produces the observed ties (e.g. K is so small it does not
>   separate 21 from 31).
> - REPRO: above snippet; then assert the top-band keys are distinct under `q_effective`.
> - VERIFY: pre-fix assertion fails, post-fix passes, and `q_order` output for a synthetic
>   clipped set is deterministic and evidence-ordered.
> - BLAST: `CORE/dashboard.py`, `AOA/aoa_monitor.py`, `expansion/synapse.py`, `expansion/spine.py`
>   (all read `get_q_weights`), `tools/render_monitors.py` (RL card).

---

## 3. GEM STONE G2 — the ledger cannot forget, so a fixed fault is a permanent penalty

> **STALE — see the header.** The table below is the fabricated record, not a
> measurement. The `8000.0` column is an eBPF collection window; the counters
> are an unseparable mix of an alert count and real probes. Removed from the
> live ledger 2026-09-29.

**EVIDENCE.** Three routes, from the live table:

| route | successes | failures | q | effective_weight | last_ms |
|---|---|---|---|---|---|
| `windows>wsl2-kali` | 34 | 12 | **+0.9958** | 1.9958 | 8000.0 |
| `windows>wsl2-ubuntu` | 30 | 30 | **−0.2708** | 0.7292 | 8000.0 |
| `windows>mesh` | 0 | 27 | **−1.0000** | 0.1000 | 0.0 |

**`8 000 ms` is not a duration, it is a timeout signature.** Those failures are the recorded trace
of `sync_wsl_to_kali`'s doubled-path bug — the bug fixed in commit `56c15679` *yesterday*. The
ledger has no way to learn that its cause is gone.

**CLAIM.** A penalty outlives its cause, and cannot be cleared by the route that carries it,
because a deprioritised route is never re-chosen. This is a **self-sustaining** penalty: the
lower the weight, the fewer attempts, the longer the penalty lasts.

**FALSIFY.** If some mechanism already re-tries a penalised route on a schedule (a probe, a
canary, a decay), this is a non-finding.

**REPRO.** `get_route_usage()` → `windows>wsl2-ubuntu` is below neutral on evidence that predates
the fix; `windows>mesh` sits at the floor on 27/27 failures and no code anywhere re-tests it.

**THE INSIGHT — and this is the gem.** The module's own `get_q_updates` docstring already names
this failure mode: *"Any selector that ranks on Q therefore starves untried arms permanently: they
score 0, are never chosen, and so are never scored (the cold-start collapse four live inference
providers independently flagged)."* Someone saw it clearly. They solved **one half** — the
*never-tried* arm — by exposing the pull count.

They missed the other half, which is strictly worse: the ***tried-then-broken-then-fixed*** arm.
A never-tried arm scores neutral 0 and only needs a quota. A *fixed* arm carries a **negative**
score that is exactly as stale as the bug, and no quota helps it because it does not need a
chance, it needs its *history invalidated*. The two halves look like one problem and are not.

**THE FIX.** Make invalidation a first-class, journalled act:

- [ ] **G2.1** `invalidate_q(key, reason)` — halves a key's evidence and returns toward neutral,
      writing a `policy_journal` entry and a `route_invalidated` spine event. Halving (not zeroing)
      is deliberate: the old evidence was *true when recorded*, so it should be discounted, not erased.
- [ ] **G2.2** Call it from the one real site this session created: the `sync_wsl_to_kali` fix, so the
      route it penalised is offered again.
- [ ] **G2.3** Test: after invalidation, a route at −0.27 on 60 pulls must outrank its own pre-fix self,
      and the journal must record the reason.

> **PRE-FLIGHT**
> - EVIDENCE: `wsl2-ubuntu` below neutral on 8 000 ms timeouts caused by a bug fixed in `56c15679`.
> - CLAIM: halving evidence moves a penalised key back into contention while keeping its history.
> - FALSIFY: after two invalidation halvings the key still cannot outrank a fresh neutral peer.
> - REPRO: `get_route_usage()` before/after; assert q_effective rises and journal length grows by 1.
> - VERIFY: pre-fix there is no such API at all (`AttributeError`), post-fix the ordering changes.
> - BLAST: `revert_policy()` (journal is shared), monitors (new event type), gossip merge (halved
>   counts propagate under the existing MAX rule — check that MAX does not undo a halving).

---

## 3b. GEM STONE G6 — one parameter, two incompatible conventions: the table is saturated AND flat at once

**EVIDENCE.** The live `synapse:` sub-table:

```
synapse edges: 31
DISTINCT VALUES: 3
histogram: {+0.0909: 25, +0.9999: 4, +0.0898: 2}
```

A 31-edge routing table with **three** distinct values cannot route. `top_edges(10)` sorts on
those values, so it returns insertion order for 25 of its 31 inputs, and `MoEDispatcherWorm`
weights experts by `0.05 + scores[e] * (1 + q)` — a constant added to two thirds of the fleet.

**ROOT CAUSE.** `SynapseWeightWorm.update()` computes a TD **error** and hands it to the brainstem
as `reward=`:

```python
td_error = reward + self._gamma * next_value - current      # a DELTA
...
record_outcome("synapse", key, td_error > 0.0, duration_ms,
               reward=self._lr * td_error)                  # passed as a TARGET
```

and the brainstem applies it as an EMA **target**:

```python
q = q + adaptive_alpha * (reward - q)      # reward is the value q converges TO
```

So `q` does not accumulate the TD error — it is **dragged toward a number near zero** every
update. With `lr * td_error ≈ 0.09`, every edge converges to `0.09` regardless of what it did.
The step size (a *delta*) is being used as the attractor (a *target*).

**The two caller families are wrong in opposite directions, from one cause:**

| caller | passes | convention the EMA applies | result |
|---|---|---|---|
| boolean sign (+1/−1) | `reward = ±1` | `q → ±1` | **saturates at the clip in 22 pulls** (G1) |
| `SynapseWeightWorm` | `reward = lr × TD error` | `q → lr × TD error` | **collapses to ≈0.09, all edges equal** |

The brainstem's own docstring states the contract the TD caller relies on — *"callers that
computed a real learning signal (a TD error, a shaped reward) pass it here so magnitude survives
*the hand-off*"* — and the implementation does something else. **`record_outcome` advertises
delta semantics and implements target semantics.** That is why the two call sites disagree: each
reads a different half of the same docstring, and neither is wrong about the half it read.

**FALSIFY.** If the 25 edges at `+0.0909` had genuinely converged to the same value through
independent evidence, their pull counts would be the same — they are (21), and so are the two at
`+0.0898`, which differ *only* because their reward magnitudes differ slightly. A converged-to-a-
constant table is the signature of a target being fed a near-constant, not of learning.

**THE INSIGHT — the biggest one on this field.** The `reward` parameter has to mean **one** thing.
It is currently a *target*, and the correct fix for a TD learner is not to reshape the number but
to name the other operation:

```
q := q + alpha * (target - q)      # target semantics  — for the sign callers
q := q + alpha * delta             # delta  semantics  — for a TD error
```

These are the same update *only when `target = q + delta`*. So the fix is to expose the delta form
explicitly (`record_outcome(..., delta=)`) and let `SynapseWeightWorm` pass `delta = lr * td_error`,
which is the textbook `Q += α · TD-error`. This also dissolves G1's saturation at the root: the
sign callers are the only ones that *should* be saturating, and once the TD family stops pretending
to be a target, the two can be reasoned about separately — and shrinkage (G1) is what makes the
sign family's saturation harmless.

- [ ] **G6.1** `record_outcome(..., delta=)` → `q += alpha * delta`, clamped, same lock discipline.
- [ ] **G6.2** `SynapseWeightWorm.update()` passes `delta=self._lr * td_error` (textbook TD) and stops
      overwriting the value it just read.
- [ ] **G6.3** Test: 20 diverse TD updates must leave 20 **distinct** edge weights; pre-fix they collapse
      to one value. This is the assertion that would have caught it.
- [ ] **G6.4** Test: a positive-mean TD sequence must drive the edge weight *up monotonically*, not toward `lr·δ`.

> **PRE-FLIGHT**
> - EVIDENCE: 31 edges → 3 distinct values; 25 at +0.0909; `reward=self._lr * td_error` at `synapse.py:95`;
>   EMA reads `reward` as the target at `spine_registry.py:1044`.
> - CLAIM: delta semantics restore discrimination (distinct weights for distinct edge histories).
> - FALSIFY: 20 diverse TD updates still produce < 20 distinct weights.
> - REPRO: `len({round(v,4) for k,v in get_q_weights().items() if k.startswith('synapse:')})` → **3**.
> - VERIFY: pre-fix the distinctness assertion fails; post-fix it passes, and the sign-caller path
>   is unchanged (23 existing spine tests still green).
> - BLAST: `MoEDispatcherWorm` (expert weights), `AttentionRouterWorm`, `top_edges()`, the RL monitor,
>   and `SynapseWeightWorm`'s own `stats()`.

---

## 4. GEM STONE G3 — the live brainstem is contaminated, and nothing can tell

**EVIDENCE.** `~/.azazael/spine_state.json` contains **14** keys that are test fixtures, sitting in
the **same namespaces as production worms** (counted post-fix by `audit_state()`, which is the
report that did not exist before this work — my first pass at this table by hand found 10, and the
instrument found 14, which is the argument for having the instrument):

| key | q | count |
|---|---|---|
| `mesh:BadWorm` | **−0.850000** | **MISSING** |
| `mesh:T0` | −0.9217 | 4 |
| `mesh:W0` | −0.3500 | 3 |
| `mesh:W1` | +0.7000 | 2 |
| `mesh:W2` | +0.4000 | 1 |
| `mesh:W3` | −0.4000 | 1 |
| `mesh:W` | +0.4000 | 1 |
| `mesh:T1` / `mesh:T2` | **+0.9217** | 4 |
| `mesh:ReflexTestWorm` | +0.4000 | 5 |
| `immune:W0` / `immune:W1` | −0.30 / +0.70 | 2 / 2 |
| `learning:W0` / `learning:W1` | +0.30 / +0.85 | 2 / 3 |

`audit_state()` reports **62 measured / 14 fabricated / 0 bootstrapped / 0 unwitnessed** on the
live store, and `trustworthy: false` — which is the honest answer and the first time it has been
answerable at all.

`mesh:T1` and `mesh:T2` sitting at **+0.9217** while `mesh:T0` sits at **−0.9217** is the fixture
signature in its purest form: an exact mirror-image triple produced by a test that records success,
then failure, on the same synthetic key.

`mesh:BadWorm` is exactly **−0.850000** — a literal. The EMA cannot produce it: from neutral, at
any alpha in [0.05, 0.5], the reachable points after n pulls are `1 − (1−a)^n`, and 0.85 is not
among them for small n. It also carries **no pull count**, so `get_q_updates("mesh", "BadWorm")`
returns 0 while `get_q_weight("mesh", "BadWorm")` returns a strong negative. And it ranks in
`q_order("mesh", ...)` beside `MeshRouterWorm`, `GossipSyncWorm`, `PartitionHealerWorm`,
`EnvBeaconWorm`.

**Correction, recorded rather than quietly edited.** My first cut of this section listed
`diagnostic:ChaosWorm` and `learning:EvolutionEngine` among the fabricated keys on the grounds that
they carry no pull count. They are **real**: `ChaosWorm` lives in `expansion/chaos.py` and
`EvolutionEngine` in `expansion/evolution.py`, both in the 226-worm registry. The classifier was
wrong, not the data. The rule it taught: *a name-shape heuristic must be checked against the
registry before it is allowed to call something fabricated.* `mesh:ReflexTestWorm` is also absent
from the registry and is a **test fixture** (`tests/test_spine_mesh.py:613`), so the registry is
necessary but not sufficient — a name can be real, invented, or both, and only an explicit
declaration settles it.

A naive "worm not in WORM_REGISTRY" probe over-flags badly here (48 false positives): the
`synapse:`, `route:`, `aoa_route:` and `monitor:` natures key on **edges and sites**, not worms —
`synapse:mesh>MeshRouterWorm` has no registry entry and never will. The classification therefore
has to be scoped by nature as well as by name.

**`tests/conftest.py` already documents this happening.** Verbatim, from the isolation fixture
added in `e67c5f6d`:

> *running `tests/test_spine_mesh.py` against a live 76-record homeostat replaced it with synthetic
> fixtures (`mesh:W0`, `learning:W1`) — hours of accumulated learning, gone, with no error.*

**The store I am reading is that store.** 76 records, containing `mesh:W0` and `learning:W1`. The
fixture fixed the *mechanism* for future runs. Nothing purged the *damage*, and there is no marker
that distinguishes a fabricated key from a measured one.

**CLAIM.** Isolation is not cleanup. A store that can accumulate fabricated keys with no
provenance marker will always be one test run from being untrustworthy, and cannot tell you
afterwards.

**FALSIFY.** If the `W0…W3/T0` keys are real production worms, this is a non-finding. They are not:
`BadWorm` exists only under `tests/`, and the others are created by `test_spine_mesh.py`.

**THE INSIGHT.** The fixture in `conftest.py` reasons correctly about *containment* — "a test must
not be able to damage the machine it is testing" — and then stops at the boundary. Containment
prevents **new** damage; it says nothing about **existing** damage, and it leaves the evidence of
past damage indistinguishable from production data. The missing third leg is *provenance*: a key
needs to know whether it was observed or fabricated, so that the question "is my brainstem
trustworthy" is answerable after the fact instead of only before the next run.

- [ ] **G3.1** Declare a fixture namespace (`TEST_WORMS` / `TEST_WORM_TAG`) and a `purge_fixtures()`
      that returns what it removed. Removal is *reported*, never silent.
- [ ] **G3.2** `audit_state()` — classify every key as `measured` / `unmeasured` / `fabricated`, so the
      live store's trustworthiness is a number instead of an inference.
- [ ] **G3.3** Test: a store seeded with `mesh:W0` + a real worm must report exactly one fabricated key
      and must not lose the real one.

> **PRE-FLIGHT**
> - EVIDENCE: 10 fixture keys in the live store; `mesh:BadWorm` at an unreachable −0.85 with no count;
>   `conftest.py` documents the clobber and names the same two keys.
> - CLAIM: provenance classification separates fabricated from measured keys without touching real data.
> - FALSIFY: a real worm is classified `fabricated` (would show as a false positive on the live store).
> - REPRO: `audit_state()` pre-fix does not exist; post-fix it reports 10 fabricated of 76.
> - VERIFY: pre-fix `AttributeError`; post-fix the count matches the table above and
>   `purge_fixtures()` leaves 66 keys with all five production mesh worms intact.
> - BLAST: homeostat, scars, quarantine_votes (`quarantine:BadWorm`, `mesh:T0`) — all carry the
>   same fixture keys and need the same treatment or they will simply re-seed Q.

---

## 5. GEM STONE G4 — a missing migration, not a missing feature

**EVIDENCE.** Six keys carry a weight with **no count and no variance**:

| key | q | count | variance |
|---|---|---|---|
| `route:windows>windows` | +0.999910 | **MISSING** | **MISSING** |
| `route:windows>g_archive` | +0.999771 | **MISSING** | **MISSING** |
| `learning:EvolutionEngine` | +0.640000 | **MISSING** | **MISSING** |
| `aoa_route:get_status>probe` | +0.850000 | **MISSING** | **MISSING** |
| `diagnostic:ChaosWorm` | −0.143156 | **MISSING** | **MISSING** |
| `mesh:BadWorm` | −0.850000 | **MISSING** | **MISSING** |

`git log -S "_Q_UPDATE_COUNTS"` puts the count table in **`e67c5f6d`** — the same commit that added
`"q_update_counts"` to the save payload, and the same commit that added the test isolation. So: a
new field was added to a **persisted schema** in the same change that started writing it, with no
backfill for rows that already existed. `__version__` is still `"1.0.0"`.

**CLAIM.** The pre-existing rows are not "unmeasured" — they are *the oldest and most-measured* rows
in the store, and the migration erased the evidence of it. `route:windows>windows` has **27 recorded
successes** in `get_route_usage()` and a pull count of **zero**.

**FALSIFY.** If `record_route_result` does not route through `record_outcome` → `_reinforce_q`, the
count would legitimately be absent. It does; verified at `mesh.py:203`.

**THE INSIGHT.** This is the highest-leverage find of the five, because it is *generic*. The
`get_q_updates` docstring exists specifically to make "proven neutral" distinguishable from
"never measured" — and the field it added reports **never measured** for the two routes with the
most successes in the system. A schema change with no backfill does not lose data; it **relabels**
it, which is worse, because the consumer has no way to tell that the label is a lie. And because
nothing versioned the payload, there is no migration hook to hang a backfill on.

- [ ] **G4.1** Bump the state schema version and add `_migrate_state(payload) -> (payload, report)`.
- [ ] **G4.2** Backfill: a key with a weight and no count is `unknown`, **not** zero — record it as
      `unmeasured`, and make `q_effective` fall back to the key's homeostat totals when the count is absent
      (`successes + failures` is the evidence and it was there the whole time).
- [ ] **G4.3** Test: a v1 payload with the six countless keys must migrate to `count == successes + failures`
      from the homeostat, and the report must name every key it backfilled.

> **PRE-FLIGHT**
> - EVIDENCE: 76 weights vs 70 counts; `route:windows>windows` has 27 successes and count 0;
>   count table and payload field both land in `e67c5f6d`; `__version__` never moved.
> - CLAIM: the homeostat already holds the missing evidence, so the backfill is a re-derivation, not a guess.
> - FALSIFY: some count-less key has a homeostat record whose totals disagree with an independent
>   count of its outcome events.
> - REPRO: load a v1 payload; assert 6 keys have weight and no count.
> - VERIFY: the report names 6 keys; post-migration none of them reads as zero evidence; the two
>   `route:` keys recover their 27 / 32 pulls.
> - BLAST: gossip merge (`_stamp_newer` uses `last_at`, unaffected), monitors that render the RL card.

---

## 6. GEM STONE G5 — a declared range the arithmetic cannot visit

**EVIDENCE.** `effective_weight = clamp(base_w * (1 + q), 0.1, 5.0)`, with `q ∈ [-1, 1]`. The
factor is therefore `[0, 2]`. For the registered `base_w = 1.0` the function is
`clamp(u, 0.1, 2.0)` — **the `5.0` bound is unreachable in every live call site**, and
`get_route_usage`'s docstring advertises those bounds while claiming to report "the weight routing
would actually use". Two independent places (`mesh.py:196`, `spine_registry.py:1202`) carry the
same dead limit, so it is not one typo.

**CLAIM.** The advertised dynamic range is 50×; the arithmetic delivers 20×, and the top half of
that is a plateau under G1.

**FALSIFY.** If any caller registers `base_w > 2.5`, the cap becomes live. No caller does.

**THE INSIGHT.** A clamp whose bound is unreachable is not a neutral defect — it is a **false
statement about the system's own capacity**, and it is exactly the kind of claim a monitor or an
operator will read and believe. It belongs to the same family as the four silent defects from the
last audit: it *reports* a range it does not have.

- [ ] **G5.1** Derive the bound from `_Q_MIN/_Q_MAX` and `base_w` instead of hardcoding `5.0`, so the
      two cannot drift apart again.
- [ ] **G5.2** Correct the docstrings to state the reachable range.

> **PRE-FLIGHT**
> - EVIDENCE: `1.0 * (1 + q)` with `|q| ≤ 1`, compared against `min(5.0, ...)` in two files.
> - CLAIM: the bound is unreachable for every registered weight in the tree.
> - FALSIFY: a grep finds a registered weight > 2.5.
> - VERIFY: post-fix, the bound is a function of the inputs and a test asserts
>   `max_effective_weight(base_w=1.0) == 2.0`.

---

## 7. Honest exclusions

- **PF17 = 530 functions reached by no test.** Real, already tracked in
  `NEURAL_MESH_FUNCTION_TODO.md`, and out of scope here; naming it again would be padding.
- **The 3 365 uncommitted working-tree entries.** Almost all are `output/` frame churn and
  dashboard renders. Not this document's business, but it does mean `git status` cannot be used as
  a signal while it is this noisy.
- **`_SCARS` healing is not the same fix as invalidation.** The scar heel (G7, 3 consecutive
  successes) already exists and works. It does not help G2 because it requires *successes on the
  penalised key*, which is the thing the penalty prevents. I am not touching it.

---

## 8. Completion record

Filled in only with a measurement taken **after** the change. No item is done because the file was
edited.

| Item | Status | Evidence |
|---|---|---|
| G1.1 – G1.4 | **done** | `get_q_effective` + `q_effective_from`; `q_order` and `route_weight` rank on the shrunk value; `get_route_usage` reports `evidence` + `q_effective` beside the weight. Live effect: `route:windows>mesh`, raw q −1.0000 on 4 pulls, moved from a floored weight **0.100 → 0.667** because 4 observations no longer read as a verdict. |
| G2.1 – G2.3 | **done** | `invalidate_q()` halves evidence, journals (`policy_latest[action] == "q_invalidated"`) and events; `MeshRouterWorm.invalidate_route()` is the router-level entry point. G2.2 partly deferred: `scripts/sync_all.py` has no `src` import path and the learned state is the router's, so the call belongs behind `invalidate_route` — which is declared `pending` in the wire-or-cut table rather than claimed wired. |
| G3.1 – G3.3 | **done** | `audit_state()` reports 14 fabricated of 76, `fabricated_share` 0.1842, `trustworthy: false`. `purge_fixtures()` removes and **reports** (never silent). `_FIXTURE_WORMS_WITNESSED` is separate from `_FIXTURE_WORMS` because `mesh:T0/T1/T2` are ORPHANED — no test or script creates them — and a rot-check that demanded a living fixture for every declared name would have failed rather than documented that. `purge_fixtures()` was deliberately **not** run against the live store: it is the one destructive action here and deleting the user's history is not this document's call. |
| G4.1 – G4.3 | **done, and observed running in production** | `_STATE_SCHEMA_VERSION = 2` + `_migrate_state()` on both read paths. Live proof: all six previously count-less keys now report `source=measured` with real evidence — `route:windows>windows` **0 → 27**, `route:windows>g_archive` **0 → 32**, `diagnostic:ChaosWorm` 42, `learning:EvolutionEngine` 3, `aoa_route:get_status>probe` 3. |
| G5.1 – G5.2 | **done** | One `route_weight()` for both call sites; `route_weight_range(1.0)` reports `max_reachable: 2.0` against `declared_max: 5.0`, and a test asserts the declared ceiling is reachable only by a q outside the clip. `get_q_effective` is wired into the RL card (PF16 confirms it is no longer unreferenced). |
| G6.1 – G6.4 | **done** | `record_outcome(..., delta=)` → `q += alpha*delta` via a shared kernel; `SynapseWeightWorm.update()` passes `delta=self._lr * td_error`. **Verified to fail pre-fix:** the regression test drives the real call site and reads **0.0364** against a required >0.3 (the target form's fixed point `lr·r/(1+lr)` vs the delta form's `r`). |

### Verification

- `py_compile` clean on all five changed sources.
- **431 passed, 1 skipped** across 21 suites (the 15 spine/mesh/aoa/federated suites + 5 monitor/dashboard suites, plus the new file's 30).
- Two pre-existing tests failed on first run and both were *legitimate* consequences, not noise: `test_q_order_preserves_ordering_semantics` pinned the old raw-Q sort key in its reference implementation (updated — it guards the O(n²)→O(n log n) rewrite, not the key), and `test_every_unreferenced_function_is_declared` correctly demanded wire-or-cut decisions for the new functions (regenerated).
- The new `tests/test_brainstem_playing_field.py` is 30 tests, and the one that matters was confirmed to **fail on the pre-fix source** rather than merely pass after it.

### Correction to a claim I made while working

I first wrote that `SynapseWeightWorm` keeping edges **distinct** was the regression test. It is not:
with distinct rewards, *both* conventions stay distinct, so a distinctness assertion passes on the
broken code. I only found that by deliberately reverting the fix and running it. The discriminator is
**magnitude**, because the two conventions have different fixed points (0.4 vs 0.0364). Worth
recording because it is the same trap as the probes in the previous audit: an assertion that is
satisfied by the defect is not a test of the fix.
