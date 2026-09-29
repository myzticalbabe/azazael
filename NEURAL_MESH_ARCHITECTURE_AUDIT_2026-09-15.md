> ## SUPERSEDED — read `NEURAL_MESH_FORENSIC_2026-09-29.md` first
>
> This document is a **dated record of what was believed on its date**. Its
> numbers are historical and several are now known to be wrong. Nothing marked
> it as superseded, so an undated reader would draw current conclusions from a
> snapshot — the exact "confidently-incomplete artifact" failure this project
> already has a skill for.
>
> Concretely, claims below that are **no longer true**:
> - the global quarantine item store is **present** (`spine_registry.py:521`);
> - the gossip signer allowlist is **present** and has a CLI
>   (`scripts/mesh_trusted_key.py`);
> - route-outcome censoring is **present but was inert** — see §1 of the
>   current forensic;
> - the worm census figures are from their measurement dates, not today.
>
> Kept for provenance. Do not cite without the date.

---

# Neural Mesh Architecture Audit — 2026-09-15

**Scope:** the 8 mesh-fabric natures (`CORE/WORMS/expansion/{mesh,synapse,consensus,engram,federated,servemesh,immune,xenomorph}.py`), the spine layer (`CORE/spine_registry.py`, `CORE/WORMS/expansion/spine.py`), and their wiring through `CORE/WORMS/NATURE_CLUSTERS.py` and `CORE/startup_warm.py`.

**Method:** read the fabric and spine modules end-to-end, then traced every fabric API to its callers (or to the absence of callers) across `src/`. Findings were confirmed against the live registry (223 worms / 35 categories) and a 194-test regression run.

---

## 0. Baseline correction — the 2026-09-13 session doc is stale

The previous session insight (`azazael/SESSION_INSIGHTS_2026-09-13_NEURAL_MESH.md`) describes the spine as it was at G1–G5 + LEAP A/B/C. The spine has grown well past that: Ed25519-signed gossip with monotonic `seq` anti-replay and TOFU key pinning, recency-wins merge, scar/reflex arc, adaptive-alpha Q with Welford variance, compacting `_POLICY_LATEST`, route-usage telemetry, and an anomaly model carried in the signed envelope. `restore_spine_state()` is now wired into `startup_warm`, and `start_spine_heart()` beats the cycle autonomously with `apply=True`.

**All four "open threads" in that document are closed.** The findings below are therefore *not* a re-audit of the spine — they are concentrated in the **fabric** natures, which never received the corresponding engineering.

---

## 1. Findings

Severity: **S1** broken safety claim · **S2** state loss / correlation break · **S3** unreachable capability · **S4** hygiene.

| # | Sev | Finding | Status |
|---|-----|---------|--------|
| 1 | S1 | Quarantine quorum was a structurally dead gate | **FIXED** |
| 2 | S2 | `SpineCycleWorm` could run concurrently with itself | **FIXED** |
| 3 | S1 | Morphogenesis output gate is orphaned *and* its quorum claim is unimplemented | **FIXED** (pass 2) |
| 4 | S2 | Four divergent env-id implementations (stale "mirrors") | **FIXED** |
| 5 | S2 | `_MESH_ENVS` never updated for the 5-way WSL split → live targets reported `hops = -1` | **FIXED** |
| 6 | S3 | 8 fabric worms' real APIs have no caller (consensus/federated/servemesh inert) | **FIXED** (pass 2) |
| 7 | S2 | No fabric operational state persisted (only the spine's *learning* was) | **FIXED** |
| 8 | S3 | Fabric state has no bounded-growth caps (spine does) | **FIXED** (pass 2) |
| 9 | S3 | Two gossip implementations; the fabric one lacks the trust model | **FIXED** (pass 2) |
| 10 | S2 | Leader election has no lease enforcement; queen is self-declared | **FIXED** (pass 3) |
| 11 | S3 | `FederatedAggregatorWorm` is a naive sample-weighted mean | partial (pass 2+3) |
| 12 | S3 | Servemesh has no health layer (load leaks; provider recovery is manual) | **FIXED** (pass 3) |
| 13 | S3 | Red Queen never probes 5 of the 8 fabric natures | **FIXED** (pass 3) |
| 14 | S4 | `mesh.describe_env()` Windows branch was dead code | **FIXED** |
| 15 | S4 | Unused imports / `__import__('os')` in `mesh.py` | **FIXED** |

---

## 2. Fixes implemented

### Finding #1 — quarantine quorum was unreachable

`RedQueenWorm.order_quarantine()` constructed a **fresh** `QuorumVoterWorm(quorum=2)` on every call and cast exactly one vote from the local env, then required `decided` (≥ 2 votes). One vote on a fresh in-memory voter can never reach two, so `QuarantineWorm.quarantine()` was unreachable — the safety rail was true in the docstring and dead in the code. Cross-env quorum was additionally impossible by construction: votes lived only in one process's memory and were never transported.

**Fix.** The authoritative tally moved into `CORE.spine_registry`:

- `cast_quarantine_vote(finding, env, verdict, quorum)` — dedups **per env** (an env changing its mind replaces its own vote; it cannot stuff the ballot) and decides on **distinct envs**.
- `get_quarantine_votes()` — read access.
- Included in the persistence payload **and** the signed gossip envelope, so a peer env's vote actually arrives in-process.

`QuorumVoterWorm.vote()` now reports the shared tally (`source: "spine_ledger"`) and keeps its instance dict as a mirror/fallback. `RedQueenWorm` needed no logic change — the gate simply became reachable, and it records the deciding envs in the `quarantine_ordered` event.

**Safety intent preserved:** one env still can never quarantine alone (verified by test); two distinct envs can.

### Finding #2 — `SpineCycleWorm` double-instance race

The autonomic heart (`startup_warm._spine_heart_worker`) owns one `SpineCycleWorm`. The class is registered `orchestration`, was **not** in `NatureCluster._NO_EXECUTE`, and exposes `execute() → run_cycle(apply=False)`. A generic nature sweep would therefore construct a *second* cycle. The guards meant to prevent this (`_busy`, `_throttled`, `_last_run_at`) are **instance attributes**, while everything the cycle touches is process-global — spine map, Q-weights, scars, policy journal, the new fabric/quarantine stores, and `spine_state.json`.

**Fix (two layers):**

- `spine.py` gains a module-level, non-reentrant `_GLOBAL_CYCLE_GATE`, acquired for the duration of `run_cycle()`; a second instance returns `{"skipped": "cycle_already_running_global"}`. The min-interval throttle deliberately stays **per-instance** — it is an optimization, and making it global would suppress legitimate cycles from independent callers.
- `SpineCycleWorm` added to `NatureCluster._NO_EXECUTE`, so the generic sweep reports standby instead of constructing ~20 organs it should not drive.

### Findings #4 / #5 — env identity

Env id is a primary key in at least six subsystems: spine-map nodes (`env:worm`), gossip drop filenames (`<env>.json`), Kademlia node ids, the gossip anti-replay table, route Q-keys (`src>dst`), and beacon peer sets. There were **five** implementations:

| Site | Before |
|------|--------|
| `envmesh.env_id_v2()` | 5-way (canonical) |
| `mesh._env_id()` | delegated to envmesh |
| `xenomorph._local_env()` | 3-way, "mirroring mesh._env_id" |
| `spine._local_env()` | 3-way, "mirror of mesh._env_id" |
| `spine_registry._local_env_name()` | 3-way, "same env-detection logic" |

The three copies stopped being mirrors when the 5-way split landed, so one host wrote state under two keys depending on which module wrote it, and gossip filenames could not be matched by Kademlia peer lookup.

**Fix.** New `CORE/env_id.py` is the single implementation (`env_id()`, `describe_env()`, `is_known_env()`, `VALID_ENVS`, `canonical_env()`; stdlib-only so `spine_registry` keeps its no-heavy-imports rule). All five sites now delegate. `AZAZAEL_ENV` override behaviour is now consistent across them.

Two couplings were repaired at the same time, because unifying the id would otherwise have *introduced* bugs:

- `Lilith.FULL_ENVS` held the pre-split `"wsl2"`; once `_local_env()` returned `wsl2-ubuntu`, every WSL host would have silently downgraded to an interim lease. Now includes both flavours.
- `mesh._MESH_ENVS` (a hard-coded tuple used as `dst_env in _MESH_ENVS`) is replaced by prefix-tolerant `is_known_env()`, so `wsl2-ubuntu` / `wsl2-kali` / legacy `wsl2` all report `hops = 1`.

### Finding #7 — fabric operational state was never persisted

`save_spine_state()` persisted the spine's learning but **nothing** persisted the fabric's operational state: routing tables, elected leader + term, quorum tallies, federated client submissions, model-shard catalogue, endpoint registry, partition history, beacons. All of it lived in per-instance dicts cached in `NatureCluster.instances`, so it was lost on every new `NatureClusterManager()` (i.e. every separate CLI/script process) and on restart.

**Fix.**

- `CORE/WORMS/expansion/fabric_state.py` — `hydrate()` / `publish()` helpers; additive hydration, full-snapshot publish, JSON-safe coercion of sets/tuples, never raises. `AZAZAEL_NO_FABRIC_STATE=1` disables both directions for tests.
- `CORE.spine_registry` gains `_FABRIC_STATE` (`publish_fabric_state`, `get_fabric_state`, `get_fabric_view`), bounded and included in persistence **and** the signed gossip envelope (per-provider recency-wins merge).
- Wired into 13 worms: `MeshRouterWorm`, `GossipSyncWorm`, `PartitionHealerWorm`, `EnvBeaconWorm`, `QuorumVoterWorm`, `LeaderElectorWorm`, `SplitBrainResolverWorm`, `FederatedAggregatorWorm`, `NASMeshSearcherWorm`, `RewardShaperMeshWorm`, `InferenceLoadBalancerWorm`, `ProviderFailoverMeshWorm`, `ModelShardServerWorm`.

**Deliberate exceptions — not everything in an instance is durable:**

- `InferenceLoadBalancerWorm._endpoints[*]["load"]` is an in-flight gauge; a restored non-zero load would strand capacity on an endpoint with no outstanding request. It is zeroed on hydrate (registry/`ok`/`fail` are kept).
- `ProviderFailoverMeshWorm._down` is this **host's** reachability observation, not fabric-wide truth, and there is no re-probe (finding #12). Persisting it would convert a transient outage into a permanent one, so only `_uses` is stored.
- `MeshRouterWorm._routes` keys were `(src, dst)` tuples, which cannot survive JSON. Keys are now `"src>dst"` — the same form the route Q-table already uses. (No external callers of `add_route` existed.)

### Findings #14 / #15 — `mesh.py` hygiene

`describe_env()`'s Windows branch was `try: virt = "hyperv_host" except: pass` — dead code that hard-coded the answer without checking Hyper-V, and it dropped the free-threading flag. It now delegates to `CORE.env_id.describe_env()`, which performs a real `HypervisorPresent` query and reports `ft`. Unused `time` / `hashlib` imports removed; `__import__('os')` replaced with a normal import.

---

## 2b. Follow-up pass (same day) — findings #3, #6, #8, #9, #12

### Finding #3 — the morphogenesis gate is now the only way in

Two defects compounded: the caller had zero callers, *and* the caller's body bypassed its own docstring (``morph(dry_run=False)`` then ``discover_worms()`` — no quarantine, no vote). Containment is now **structural**, not conventional:

- ``morph()`` writes into ``expansion/generated/_staging/``. The discovery walk skips that directory twice over — it holds no ``__init__.py`` and its name is ``_``-prefixed (``worm_registry._discover_worms_impl``). A staged file is not importable and not a worm.
- ``MorphogenesisWorm.staged()`` / ``.promote()`` are the gate. ``promote()`` quarantines the candidate with ``QuarantineWorm`` *while it is still invisible*, casts this env's ``promote`` vote through ``spine_registry.cast_quarantine_vote()`` (shared, persisted, gossiped, counted over **distinct envs**), and only on a decided vote moves the file into ``generated/``.
- ``force=True`` is the operator channel. It records an explicit ``operator`` vote (so the decision is auditable rather than invisible) and promotes without a second env — a gate that *can* be satisfied, unlike the dead one in finding #1.
- ``expansion/generated/__init__.py`` was added, so promotion is now genuinely meaningful: before it, the directory was not on the discovery path at all, which is why the old "auto-registers" claim was true and false at the same time depending on who you asked.
- ``SpineCycleWorm._process_morphogenesis_output(apply=…)`` is wired into ``run_cycle()`` as stage 2i. **Neither half writes unless ``apply=True``** — with ``apply=False`` the organ runs a *dry-run* morph (reporting ``would_stage``) and reports the pen depth from disk, so the deterministic default stays side-effect-free, matching ``_topology_stage``'s propose-only convention.

  That last point was a bug I introduced and then found: the first cut staged on *every* cycle, so any caller driving a plain ``run_cycle()`` — including the existing test suite — created source files inside the real project tree. Two fixes: staging now requires ``apply=True``, and ``AZAZAEL_GENERATED_DIR`` relocates the whole tree (``tests/conftest.py`` sets it to a session temp dir, which is the same override a read-only installed package needs). Verified: after a full suite run the real ``expansion/generated/`` contains only ``__init__.py``.
- Because ``generated/`` is now genuinely on the discovery path, the old claim becomes true in the *safe* direction: discovery is what a promoted file waits for, and it cannot happen for anything still in the pen.

### Finding #6 — the 8 unreachable worms now have real callers

``SpineCycleWorm._fabric_stage()`` (stage 2h) drives every one of them from a real source. Each sub-stage is independently best-effort, so a missing source degrades one organ and never the cycle.

| Organ | Real source it is now driven from |
|-------|-----------------------------------|
| ``InferenceLoadBalancerWorm`` | ``CORE.inference.providers.PROVIDER_REGISTRY`` — 20 real endpoints registered, then a real ``pick()``/``release()`` pair so the in-flight gauge returns |
| ``ProviderFailoverMeshWorm`` | ``mark_down``/``mark_up`` from per-provider credential presence; ``next_provider()`` consulted each cycle |
| ``ModelShardServerWorm`` | the on-disk model catalogue (``azazael_models``) — 16 real artifacts published, digest = size + 64 KiB header |
| ``LeaderElectorWorm`` | the task7 ``placement.json`` (with the elector's own bare→wsl2-ubuntu remap), falling back to live ``EnvBeaconWorm.peers()`` |
| ``SplitBrainResolverWorm`` | real forks from the gossip-merged shard catalogue (one model, two content digests) |
| ``PraetorianWorm`` | ``observe_term()`` fed the real elector term + real ``Lilith`` queen presence — the succession path previously never ran |
| ``RewardShaperMeshWorm`` | ``score()``/``weights()`` over the 6-provider chain; the DLQ now fills from real credential failures |
| ``NASMeshSearcherWorm`` | ``propose()``/``evaluate_batch()`` over per-env policy vectors built from the learned Q-table |
| ``FederatedAggregatorWorm`` | ``submit()``/``aggregate()`` (FedAvg) over the same real vectors |

**One trap worth recording.** The first cut of the credential signal marked ``lmstudio`` and ``ollama`` **down**, because both declare an ``env_var`` for a *localhost* endpoint whose key is optional — and ``llama_cpp_direct``/``openvino``/``huggingface_direct`` declare a model *path* under ``env_var``, not a credential. That would have removed working endpoints from the failover chain, i.e. caused the exact outage the stage exists to prevent. ``_provider_key_state()`` now reports a provider unusable only when it declares an ``env_var``, has a **non-empty non-loopback** ``base_url``, and that variable is unset; a CHAIN entry with no registry entry (e.g. ``llamaserver``) is omitted entirely, because no evidence is not evidence of absence.

### Finding #9 — one gossip model, trust-checked

``mesh.GossipSyncWorm`` moved from first-writer-wins to two paths: a **spine-shaped payload** is validated by ``spine_registry.check_gossip_trust`` (Ed25519 when available, monotonic ``seq`` anti-replay, TOFU key pinning) and an untrusted payload applies nothing; a **plain mapping** gets a per-key recency merge on ``at``/``updated_at``, where a timestamped value may replace an older one and an untimestamped value can only fill a gap. A *changed* value can now propagate, which first-writer-wins made impossible.

### Finding #8 — bounded growth in the fabric

``fabric_state.cap_list()`` / ``cap_map()`` are the shared eviction helpers (newest-kept, ``limit <= 0`` means unbounded, never raises), applied across the fabric stores — ``QuorumVoterWorm``, ``SplitBrainResolverWorm``, ``LeaderElectorWorm``, ``RewardShaperMeshWorm`` (scores **and** DLQ), ``InferenceLoadBalancerWorm``, ``ModelShardServerWorm``, ``FederatedAggregatorWorm``, ``NASMeshSearcherWorm``, ``GossipSyncWorm``, ``EnvBeaconWorm``.

### Findings #11 / #12 — partial

- **#11:** the fragility that actually bit — ``aggregate()`` iterating ragged per-env vectors — is gone: the stage builds every env's vector against a **common, sorted nature axis**, so the FedAvg input is rectangular by construction. Byzantine robustness (trimmed-mean/Krum), staleness weighting and secure aggregation are still absent.
- **#12:** ``mark_up``/``mark_down`` now have callers, so a provider that regains credentials returns to the chain. There is still no backoff or half-open re-probe; ``CORE/circuit_breaker.py`` implements exactly that machine and remains unused here.

---

## 2c. Third pass — findings #7 lease, #10 coverage, #12 health

The three items the follow-up pass's "recommended next order" named.

### Finding #7 — the leader lease is now the authority

`Lilith._lease_until` was written and never read, `claim()` re-claimed unconditionally, and `PraetorianWorm.observe_term()` computed `moult_eligible` / `needs_quorum` that nothing consumed. Three changes:

- **The lease is persisted and gossiped** (`PROVIDER = "Lilith"`, `_lease_env` / `_lease_until` / `_term`), which is what makes enforcement possible at all: a peer cannot defer to a lease it cannot see.
- **`claim()` now has an explicit authority order:** a *valid lease held by another env* outranks a local claim. The holder keeps the lease until it **expires**; a later claimer cannot depose a live queen by asserting a higher term. That single line is what stops a partitioned or restarted host from becoming an independent queen. Below it, the pre-existing rules are unchanged (bare-peer preference, then the capability gate).
- **Renewal is distinguished from election:** re-claiming your *own* unexpired lease keeps the term (a heartbeat); succeeding an expired or foreign lease bumps it.
- **Succession has an approval path.** `moult_eligible` now routes to `Lilith.request_moult()`, which requests through the shared distinct-env quorum — the same ledger used for quarantine and for morphogenesis promotion — with `force=True` as the auditable operator channel. The succession path still can't promote unilaterally, and now it *can* promote.

### Finding #10 — probe coverage

`PROBE_NATURES` went from `(mesh, synapse, immune)` to include `consensus`, `federated`, `servemesh`, `engram`, and `RedQueenWorm.execute()` now reports a per-nature `coverage` map so "what was actually probed" is observable rather than inferred from a constant.

**Two things had to be true before this was safe, and one was not:**

- Governors are already skipped by `is_protected_worm()`, so probing a nature that hosts a governor cannot feed the loop it regulates.
- But `FederatedAggregatorWorm.execute()` called `aggregate()` — which consumes every pending client submission and bumps the round counter. Probing `federated` would therefore have *destroyed real client state*. `execute()` is now a read-only summary, and aggregation is reachable only through `aggregate()`. This is a class of bug worth naming: **making an organ reachable can turn a previously-harmless summary method into a destructive one.**

### Finding #12 — servemesh health layer

Reuses `CORE/circuit_breaker.py` rather than inventing a second health machine (the finding's own recommendation).

| Defect | Fix |
|--------|-----|
| `pick()` incremented a counter only the *caller* could decrement; selection is `min(load, fail)`, so a caller that raised starved its endpoint for the process lifetime | Leases carry an acquisition time; `sweep()` reclaims them. Load is **recomputed** from the live leases instead of incremented, so it cannot drift. |
| `fail` was only a tiebreak, so a persistently failing endpoint stayed eligible | Per-endpoint `CircuitBreaker`; `pick()` prefers endpoints whose breaker is not OPEN, and an OPEN breaker **past its cooldown** becomes eligible again (the half-open retry), instead of being excluded forever |
| `mark_up()` had no caller, so recovery never happened | `reprobe()` performs a real reachability check, but only for providers `probe_due()` returns — i.e. after the cooldown — so probing is rate-limited by construction. Repeated failures widen the cooldown exponentially (`RECOVERY_BASE_S` → `RECOVERY_MAX_S`); a success resets it. |
| An all-down pool had no defined behaviour | `pick()` degrades to the full pool and flags `degraded_pool`: "no endpoint" is worse than "a sick one" |

**One subtlety that would have been a real bug.** A provider is marked down for *two different reasons* — a missing credential and unreachability — and a network probe only fixes the second. `reprobe()` would have issued an HTTP request to a keyless provider, received a **401**, and read it as "recovered", un-downing a provider that cannot serve. Failures now carry a reason, and `probe_due()` skips `credential_missing` entirely. The probe also treats any HTTP response (including 401/404) as reachable, because the question it answers is *is the host up*, not *can it serve a completion*.

---

## 2d. Deep dive — cross-env convergence (`CORE/hlc.py`)

With the directed list exhausted and every original finding closed or explicitly
partial, the remaining risk was not a missing feature but a **wrong assumption**
underneath the cross-env layer. The merge decided "whose value is newer" by
comparing `datetime.now().isoformat()` strings. Three things were wrong with
that, and all three failed silently — the merge simply picked the wrong side and
reported success.

| Assumption | Reality |
|---|---|
| Timestamps are comparable | `_now_iso()` is **naive local time**. An env on UTC-8 and one on UTC+0 emit strings that look comparable and are eight hours apart, so the newer write loses for eight hours. |
| Clocks can be trusted | A peer whose clock runs fast wins every tie forever; one whose clock is behind has its writes discarded indefinitely. The mesh had never *measured* skew, so skew-induced divergence was indistinguishable from a real disagreement. |
| String order implies causality | A lexicographic compare cannot express "this write happened after the write I just observed", so a read-modify-write is not ordered after the value it read. |

### What replaced it

`CORE/hlc.py` — a hybrid logical clock (Kulkarni et al., 2014; the same family
CockroachDB, MongoDB and Cosmos DB use for this job). Stdlib-only, so
`spine_registry` keeps its no-heavy-imports rule. Properties it buys the mesh:

* **Monotone even when the wall clock moves backwards** (NTP step, DST,
  suspend/resume) — it never returns a stamp it has already returned.
* **Causal**: after `observe(remote)`, every subsequent local stamp is strictly
  greater than the observed one, *regardless of clock skew*. This is the
  property a bare wall clock cannot provide, and therefore the one that made the
  old comparison invertable.
* **Deterministic tie-break** by node id, so two envs stamping the same
  millisecond still converge on the same winner without coordinating.
* **Lexicographically sortable** (fixed-width packed form), so it drops into the
  existing string comparisons and JSON persistence with **no format migration**.

### The bound that stops one bad clock poisoning the host

A naive HLC merge has a failure mode of its own: `observe()` on a peer stamp
from the year 2999 pulls the local clock with it, so *every future local stamp*
lands in that peer's era and the host's own writes look newer than everything
for years. This was not theoretical — the first cut of the convergence tests hit
it and cross-contaminated the whole test process.

`observe()` now clamps how far a remote stamp may pull the local clock forward
(`MAX_DRIFT_MS`, 5 minutes — the same knob CockroachDB calls `MaxOffset`). A
stamp beyond the window is **observed and reported** (`skew_ms()`,
`rejected()`) but not adopted, and the returned stamp is then deliberately *not*
causally after it: refusing to jump the clock by years is strictly better than
satisfying a broken peer. A stamp inside the window is adopted normally.

### Migration without a flag day

Every record that participates in a cross-env merge now carries **both** a
human-readable ISO field (`updated_at`, `last_at`, `at` — parsed and displayed
by existing callers) **and** an `hlc` sidecar. Ordering consults the sidecar via
`_rec_stamp` / `_stamp_newer`, which normalise both sides, so a legacy ISO-only
record still compares correctly during the upgrade window. Nothing that reads a
timestamp as a timestamp changed behaviour — which was the whole point of making
it additive. Two things this required care over:

1. **A pinned timestamp must pin the ordering.** `record_spine_node` derives the
   sidecar from an explicit `updated_at` when a caller supplies one, otherwise
   the pin would be silently ignored and the record ordered by "now" (this is
   what `test_gossip_merge_recency_wins` caught).
2. **The spine's `is_idle` gate and `_dt_ms` STDP timing** read `last_at` as ISO.
   Making the *stored* field HLC would have broken both, which is why the
   sidecar approach was chosen over reformatting the fields.

### Per-field merge (the data-loss half)

Fabric state was merged **per provider, wholesale**. Because the provider key is
shared by every env (each env's `Lilith`, `ModelShardServerWorm`… publishes under
the same name), a peer with a newer stamp erased the other env's fields
entirely — which is why a catalogue meant to hold two envs' shards could only
ever hold one. Records now carry one stamp **per attribute** and merge as a
field union keyed by HLC, so two envs each publishing a different subset
converge to the union.

### The brainstem was three tables and only one was persisted

Found by *building the new RL monitor*, not by any test. `_Q_WEIGHTS`,
`_Q_UPDATE_COUNTS` and `_Q_VARIANCE` are all learned state; only the weights were
saved, restored or gossiped. Every restart therefore reset the pull-count (so
`get_q_updates()` reported every key as never-tried, defeating the cold-start
guard it was added for) and reset the Welford variance (so adaptive alpha fell
back to its default and the learning-rate schedule restarted). `spine_reset()`
had the mirror bug — weights cleared, counts and variance left, producing a
Q-table empty of values and full of evidence. Both fixed; counts take MAX on
merge, matching the existing monotone-counter rule. Covered by
`tests/test_spine_brainstem_persistence.py`.

### Delivery consequence

The mesh had outgrown every monitor that described it, so two monitors were
built for the tiers that had none (**ML** and **RL**), and the restructure of
the existing ones is specified in `LIVE_MONITOR_RESTRUCTURE_TODO.md` — including
the hard-coded constants now contradicting the running system
(`PROBE_NATURES`, `Lease 300s`, the old 2/3 local quorum) and the fact that
`get_q_updates()` — the readout that distinguishes a *starved* worm from a
*settled* one — was called by no monitor at all.

---

## 3. Verification

| Check | Result |
|-------|--------|
| `tests/test_mesh_fabric_gaps.py` (pass 1, 20 tests covering #1/#2/#4/#5/#7/#14) | ✅ 20/20 |
| `tests/test_mesh_fabric_followups.py` (pass 2, 25 tests covering #3/#6/#8/#9/#11) | ✅ 25/25 |
| `tests/test_mesh_fabric_health.py` (pass 3, 24 tests covering #7/#10/#12/#13) | ✅ 24/24 |
| `test_spine_mesh + _architect + _ledger_striping + _telemetry + _wiring + cross_nature_orchestration + worm_registry + mesh_html_view + nature_clusters + startup_warm_wiring` (+ all three new files) | ✅ 298 passed, 1 skipped |
| Adjacent suites (`monitor_verdict_accuracy`, `worm_imports`, `registry_importable`, `provider_failover`, `nature_clusters_extended`) | ✅ 76 passed, 5 skipped |
| `test_circuit_breaker_integration.py::test_force_trip` | ❌ **pre-existing, unrelated** — the test calls `CircuitBreaker.force_trip()`, which was never implemented (see §5) |
| `test_circuit_breaker_integration.py::test_nature_cluster_parallel_timeout` | ❌ pre-existing, unrelated — parallel-timeout expectation in `NatureCluster._execute_parallel`, untouched by this work |
| Registry integrity after changes | ✅ 223 worms / 35 categories, second discovery pass returns 0 (idempotent, no collisions, **no generated worm registered**) |
| `py_compile` on all touched/new modules | ✅ clean |
| Live `run_cycle()` after fixes | ✅ `success: True`, reports `fabric` + `morphogenesis` |
| Containment probe | ✅ discovery descends into `generated`, never into `_staging` |
| `tests/test_mesh_clock_convergence.py` (deep dive, 18 tests: monotonicity, causality under skew, tie-break, normalisation, drift bound, per-field union, idempotency, legacy records, sidecar priority) | ✅ 18/18 |
| `tests/test_spine_brainstem_persistence.py` (deep dive, 8 tests: counts + variance round-trip, full reset, bulk accessor, starved vs proven-neutral, MAX merge, gossip) | ✅ 8/8 |
| Mesh/spine suite re-run after the brainstem change (10 files) | ✅ 230 passed, 1 skipped |
| Pre-existing failures fixed (`test_dlq.py` 5, `test_config_and_breaker.py` 2, `force_trip`) | ✅ 61 passed in those two files alone |
| Live RL brainstem card before/after the persistence fix | ✅ `0 measured` → **`66 measured · 0 starved`** |
| `dashboard/monitor_ml.html` + `dashboard/monitor_rl.html` | ✅ rendered from live artifacts (25 KB each), real values verified in the HTML |

The new test file isolates `spine_registry._STATE_FILE` and `_GOSSIP_DIR` to `tmp_path` per test, so the suite never reads or writes the developer's real `~/.azazael/spine_state.json`.

### Behavioural verification (excerpts)

```
A1 single env decided: False   env_count: 1   source: spine_ledger
A2 two envs decided:  True     envs: ['windows', 'wsl2-ubuntu']
A3 re-vote same env:  True     env_count: 2      # ballot not stuffed
A5 red queen single-env ordered: []              # safety intent preserved
A6 red queen cross-env ordered:  [{'worm': 'BadWorm', 'env_count': 2, ...}]
B2 while gate held:  cycle_already_running_global
D2 hydrated route weight: 2.5    D4 restored loads: {'lmstudio': 0}
D6 restored _down (should be empty): []
D7 restored: {'fabric_providers': 4, ...}
```

Pass 2 (live, isolated HOME):

```
discovery descends into: ['generated']
staging on discovery path: False              # pen is unreachable by import
morph(dry_run=False): {'generated': 1, 'staged': 1}
in staging: True   in generated: False        # morph cannot publish
single-env promote: {'staged': 1, 'promoted': 0, 'held': 1}
two-env promote:    {'staged': 1, 'promoted': 1, 'held': 0}
operator promote:   {'staged': 1, 'promoted': 1, 'held': 0}
cycle keys have fabric: True  morphogenesis: True
fabric.servemesh:   {'registered': 20, 'pick': 'groq', 'next_provider': 'llamaserver',
                     'providers_down': ['nim'], 'shards_published': 16}
fabric.consensus:   {'placement': {'trainer': 'wsl2-ubuntu', ...},
                     'leader': 'wsl2-ubuntu', 'term': 1,
                     'succession': {'moult_eligible': False, 'needs_quorum': True},
                     'forks_reported': 0}
fabric.federated:   {'reward_scored': 6, 'nas_proposals': 1, 'nas_evaluated': 1,
                     'federated_rounds': 1, 'federated_dim': 1}
```

`providers_down: ['nim']` is the corrected credential signal: only ``nvidia_nim``
(a remote provider whose key is unset) is withdrawn. ``ollama`` and ``lmstudio``
stay in the chain — see the trap recorded in §2b.

---

## 4. Remaining gaps

Items 3–10 below are all now closed (passes 2–3) and are kept only as the record of what was wrong. The live open list is in §5.

3. ~~**Morphogenesis gate is orphaned and unimplemented (S1).**~~ **CLOSED — §2b.** `SpineCycleWorm._process_morphogenesis_output()` has zero callers, so `self._morphogenesis` is built and unused. Worse, its docstring promises *"generate → quarantine → quorum vote → register; only 2/3 quorum approves"*, but the body calls `morph(dry_run=False)` then `discover_worms()` and asserts `registered = generated` — no quarantine, no vote, no gate. Generated source files would auto-register on the next discovery. This is the most serious open item: a claimed containment boundary that is both dead **and** a no-op.
4. ~~**8 fabric worms are unreachable (S3).**~~ **CLOSED — §2b.** `LeaderElectorWorm`, `SplitBrainResolverWorm`, `FederatedAggregatorWorm`, `NASMeshSearcherWorm`, `RewardShaperMeshWorm`, `InferenceLoadBalancerWorm`, `ModelShardServerWorm`, `ProviderFailoverMeshWorm` have no callers outside their own module and the package re-export. They are reachable only through the generic `_run_worm_method → execute()` path, which returns a *summary* — so the consensus, federated and servemesh natures are structurally present and functionally inert. `LeaderElectorWorm` is imported by `spine.py` and never instantiated, though `xenomorph`'s docstring claims the queen election consults it.
5. ~~**No bounded-growth caps in the fabric (S3).**~~ **CLOSED — §2b.** `QuorumVoterWorm._votes` (mirror), `SplitBrainResolverWorm._forks`, `PartitionHealerWorm._partitions`, `RewardShaperMeshWorm._dlq`, `MeshRouterWorm._routes`, `InferenceLoadBalancerWorm._endpoints` grow without bound in the long-lived heartbeat process. (The new `_FABRIC_STATE` and `_QUARANTINE_VOTES` stores *are* bounded.)
6. ~~**Two gossip implementations (S3).**~~ **CLOSED — §2b** (``GossipSyncWorm`` now wraps the spine's trust model rather than being deleted, because its plain-mapping path has callers the spine's envelope does not cover). `spine_registry` gossip is signed, seq-guarded and recency-merged. `mesh.GossipSyncWorm.gossip()` merges only `if k not in self._state` — first-writer-wins, no timestamps, no signature — so a *changed* value can never propagate. `SpineCycleWorm` calls it with a local Q snapshot, which therefore merges into a dict nothing reads: a semantic no-op that looks like learning in the cycle report.
7. ~~**Leader lease is decorative (S2).**~~ **CLOSED — §2c.** `Lilith.claim()` declares queen whenever no `"bare"` peer is visible and `_host_capable()` passes — no quorum, no term comparison. It writes `_lease_until` (`LEASE_SECONDS = 300`) and **no code ever reads it**; `claim()` re-claims unconditionally. A partitioned host becomes an independent queen, and `SplitBrainResolverWorm` only resolves *model* forks. `PraetorianWorm.observe_term()` (succession) has no callers.
8. **Federated aggregation is naive (S3).** *(rectangular input fixed in pass 2/3; Byzantine robustness, staleness weighting and secure aggregation remain open — see §5)* Sample-weighted mean with no Byzantine robustness (trimmed-mean/Krum), no staleness weighting, no dimensional validation (a shorter client raises `IndexError` while holding the lock), no DP/secure aggregation, and no round ids.
9. ~~**Servemesh has no health layer (S3).**~~ **CLOSED — §2c.** `pick()` increments load and depends on the caller calling `release()`; a raising caller starves that endpoint forever since selection is `min(load, fail)`. `mark_up()` is manual — no re-probe, no backoff, no half-open state — despite `CORE/circuit_breaker.py` implementing exactly that machine and being used elsewhere.
10. ~~**Probe coverage (S3).**~~ **CLOSED — §2c.** `PROTECTED_NATURES = {orchestration, xenomorph, plasticity}` and `RedQueenWorm.PROBE_NATURES = (mesh, synapse, immune)`, so consensus, federated, servemesh, engram and sync are never adversarially probed — the natures with the most mutable state and the fewest tests are the least pressure-tested.

### Recommended next order

All original findings are closed or explicitly partial. The next order is in §5 (Deep dive), which is where the work moved to once the directed list ran out.

---

## 5. Recommended next order

1. ~~**Monitor restructure, P1 of `LIVE_MONITOR_RESTRUCTURE_TODO.md`.**~~
   **DONE — §6.** P1–P3 landed: no monitor prints a constant the mesh computes,
   the fabric/quarantine/cycle panels exist, staleness is visible and every page
   auto-refreshes. Reading the state nothing had ever read found four more
   defects (§6), including a live clock defect worth more than the restructure.
2. **Federated-aggregation hardening** (§4 item 8): Byzantine robustness
   (trimmed-mean / Krum), staleness weighting, secure aggregation. Until then
   the federated card must render as advisory, which the new RL/ML monitors do.
3. ~~**Clock trust is measured but not yet acted on.**~~ **CLOSED — §6.1,** and it
   was worse than "not acted on": the diagnostic itself was wrong. A refused
   stamp was reported as skew (+30,682,668,693,692ms, ~972 years, permanently),
   a poisoned stamp could still win a merge and freeze a record until year 2999,
   and `normalize_stamp()` could emit a stamp `unpack_stamp()` cannot read. All
   three are fixed, the clock card shows accepted skew and refusals separately,
   and `purge_implausible_stamps()` repairs a store that already holds them.
4. **Land the deferred ledger work** (§4 item 11's staleness weighting is
   blocked on it): the spine's own persistence now carries counts and variance,
   but a *peer's* evidence is still merged by MAX of two incomparable
   observation sets. That is defensible now and will not be once two envs train
   different models.
5. **Give the drift bound an operator surface.** §6.1 makes a refused stamp
   harmless and countable, and the monitor now shows the count — but nothing
   *alerts* on it. A sustained refusal rate means a peer's clock is broken, and
   that should reach the alerting path rather than a dashboard card.

---

## 6. What the monitor pass found (the restructure paid for itself)

Making the existing monitors truthful (P1–P3 of
`LIVE_MONITOR_RESTRUCTURE_TODO.md`) meant reading live state that no monitor had
ever rendered. Each new read found a defect. Full detail is in that file's §5;
the mesh-side summary:

| # | Finding | Severity | Fixed |
|---|---|---|---|
| 1 | `HybridLogicalClock.observe()` recorded a **refused** stamp as `_max_remote_physical`, so `skew_ms()` reported the rejected era (+30,682,668,693,692ms ≈ 972 years) forever — indistinguishable from a real reading. A live store held **98 year-2999 stamps**. | S2 | ✅ `skew_ms()` = accepted peers only, new `rejected_skew_ms()` for refusals |
| 2 | `normalize_stamp()` multiplied **every** numeric input by 1000, so a millisecond epoch became a 16-digit value `unpack_stamp()` cannot parse — a stamp that is neither ordered nor recognised. `pack_stamp()` could emit one too. | S2 | ✅ unit detection by magnitude + serial clamp, so every emitted stamp is unpackable |
| 3 | A beyond-drift stamp **still won merges**: the fabric field merge used a raw `>` (bypassing the guard) and the guard covered only the candidate direction, so a year-2999 field stamp beat every correct peer until real time reached year 2999. | S1 | ✅ both directions guarded; a poisoned incumbent loses to the first trustworthy write, and `purge_implausible_stamps()` repairs a store |
| 4 | A mesh test suite **wrote the developer's live store** (`~/.azazael/spine_state.json`), replacing a 76-record homeostat with synthetic fixtures. Isolation was opt-in per test file. | S2 | ✅ global autouse redirect in `tests/conftest.py`; verified by hashing the real file around a full run |
| 5 | The HLC singleton's **adopted peer time leaked between tests**, so a merge test was order-dependent (`test_mesh_fabric_gaps.py::test_fabric_state_merges_by_recency` passed alone, failed after the clock-trust tests). Not a merge bug: `observe()` adopting a within-drift peer time is correct HLC behaviour, and `reset_remote_view()` deliberately will not un-monotone the clock. | S3 | ✅ each test gets a fresh `HybridLogicalClock` via an autouse fixture, so every assertion runs on a clock that has seen nothing |
| 6 | `scripts/live_monitor.py` — the primary wallboard a human looks at — had **zero mesh references**: no fleet-cycle row, no cycle age, no staleness. A fleet cycle that had been dead for ~46 h read as a healthy board. | S2 | ✅ `MESH` row (`state/mesh_cycle.json` + the `cycle_telemetry.jsonl` cpu tail) and a `mesh` freshness row, so its age reaches the `STALE` alert *and* the verdict |

Two structural items from §4 also closed in this pass: **#8 federated
aggregation** (dimensional validation, staleness weighting, a Byzantine-robust
trimmed aggregate and round ids — `tests/test_federated_robustness.py`) and
**`CORE/dashboard.py`**, which was rebased on `spine_registry`
(`--mesh` / `render_mesh()`) rather than retired.

Two further consistency repairs came out of the same pass: the two monitors
defined **"starved"** differently (now both use the spine's
`weight == 0.0 && pulls == 0`, with *seeded* reported separately), and an AOA
tripwire that pinned "routing learning is not durable" fired — routing outcomes
now persist, so it was inverted deliberately rather than deleted.

All of the above lands in the commit that closes this pass, together with the
monitor restructure (`LIVE_MONITOR_RESTRUCTURE_TODO.md` P1–P3) and the mesh
panel above.

---

*Audit performed by Buffy (Codebuff). Fixes verified against the live registry and the full mesh/spine test suite.*
