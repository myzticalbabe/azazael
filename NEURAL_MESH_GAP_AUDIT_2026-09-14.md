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

# Neural Mesh — Full Architecture Gap Audit

**Date:** 2026-09-14
**Agent:** Buffy (Codebuff / deepseek-v4-flash)
**Scope:** `azazael/src/CORE/` neural mesh fabric — the 16 mesh natures, `spine_registry`,
`WORMS/expansion/spine.py`, the learning/plasticity layer, gossip + persistence.
**Method:** source read + authoritative runtime inventory + live-state inspection.
Every claim below is backed by a command in §6.

---

## 0. Verdict

The **organs are built; the nervous system is not yet conducting.**

The spine is genuinely good engineering: a lock-correct, restart-safe, atomic-write
feedback ledger with a reflex arc, a deliberator, a policy journal with revert, and a
gossip payload format. That layer is production-grade for a stdlib-only design.

But the *mesh* it feeds is **declarative, not computational**:

- The eight "learning" subsystems that give the mesh its name — synapse weights,
  MoE routing, attention, SSM, Hebbian/STDP/EWC plasticity, the autoencoder — are
  **heuristic scalars and frozen random tensors**, not trained anything.
- Three of the six `synapse` worms have **no caller and no consumer**: nothing
  reads an attention ranking, a MoE decision or an SSM state, and nothing feeds
  them real data (G1).*
- The two learning loops that *do* exist are **broken**: reward magnitude is destroyed
  before it reaches the brainstem (G2), and the route-learning entry point has **zero
  callers** (G3), so the entire route-learning path is decorative.
- Meanwhile **torch, faiss, chromadb, sentence-transformers, onnxruntime, numpy,
  numba, gymnasium, stable_baselines3, mygrad and transformers are all installed and
  importable on the repo interpreter** — and are used by *none* of the mesh fabric
  (G14).

So the gap is not "missing modules". The gap is **missing wiring and missing learning**.
The single highest-leverage move is not writing more worms — it is *forbidding* new
mesh worms until the existing 70 fabric worms are all reachable, all feeding the ledger,
and all learning from something with more resolution than a sign bit.

---

## 1. Authoritative inventory (runtime, not doc claims)

`discover_worms()` on the repo interpreter, 2026-09-14:

| Metric | Value |
|---|---|
| Total registered worms | **224** |
| Neural-mesh-fabric worms (16 natures) | **70** |
| Mesh natures | `mesh 5, synapse 6, engram 5, immune 5, axon 4, dendrite 4, glia 4, plasticity 4, consolidation 4, consensus 3, federated 3, servemesh 3, metabolic 3, thalamus 3, envmesh 6, xenomorph 8` |
| Largest non-fabric category | `security 24` |
| Discovery anomaly | **1× `worm_registered_overwrite`** during a single pass |

Live spine state (`~/.azazael/spine_state.json`, saved `2026-09-14T01:01:13`):

| Field | Value | Reading |
|---|---|---|
| `spine_map` nodes | 118 | topology publisher works |
| `homeostat` worms | 58 | **only 26% of 224 registered worms have ever reported an outcome** |
| `q_weights` | 58 | brainstem table is real but sparse |
| `scars` | 2 | reflex arc has fired in anger |
| `policy_journal` | 64 | appro. two-thirds of the 100-entry ceiling |
| gossip peers | **1** (`windows.json` only) | the mesh is a mesh of one |

Note the drift from the 2026-09-13 session doc (184 worms): the fleet grew ~40 in a day
while the mesh's own telemetry coverage stayed at 58. **Growth is outrunning wiring.**
*(2026-09-14 update: fleet at 226/35 after clean rebuilds; morning 181-map was a stale-cache
phantom — see worms skill. Gossip still single-peer; tracked as open gap.)*

---

## 2. What is actually real

Credit where due — these are not gaps:

- **`CORE/spine_registry.py`** — RLock-disciplined, bounded, atomic-write (`tmp` +
  `os.replace`), corrupt-file-tolerant, load-once guarded so cron processes merge
  instead of clobbering. Documented lock ordering (`HOMEOSTAT → SPINE`, never reverse).
- **Reflex arc** — 4-consecutive-failure threshold → cooldown ×3 (capped 3600s) +
  priority −1 + scar, journalled as `actor="reflex"` so `revert_policy()` can undo
  emergency measures. Graduated scar healing over 3 successes.
- **`_reinforce_q`** — EMA with **adaptive alpha from Welford running variance**
  (volatile keys learn faster, stable keys don't oscillate). This is a genuinely
  thoughtful touch.
- **Gossip merge** — strict-newer-wins so re-merging is idempotent; `env:worm` keys
  prevent cross-env collision; conservative Q adoption.
- **`_discover_worms_impl` + RLock + `_purge_worm_modules`** — the 09-13 free-threading
  fixes (unsynchronized discovery, torn cache, unfaithful repair) are correct.
- **`SpineCycleWorm` self-protection by category algebra** — registered `orchestration`,
  outside `RedQueenWorm.PROBE_NATURES`, so recursion is unrepresentable rather than
  guarded. That's the right instinct (see G16 for where it is *not* applied).

---

## 3. Gaps, tiered

### TIER 1 — Critical (the mesh is not doing what its name says)

**G1 — Declared-but-unconsumed fabric.**
`MoEDispatcherWorm`, `AttentionRouterWorm`, `SSMSequenceWorm` are registered and
imported in `expansion/__init__.py`, but **no code calls their real APIs**
(`dispatch()`, `attend()`, `ingest()`). Nothing reads an attention ranking, a MoE
decision or an SSM state; nothing hands them data. The only explicit cross-module
instantiation in the whole fabric is `spine.py:188 → SynapseWeightWorm()`. A
docstring in `dendrite.py:54` *refers* to a `MoEDispatcherWorm` pairing — the
pairing exists in prose only.

> **Correction (verified 2026-09-14, after this section was first written).** An
> earlier draft claimed these classes were "never instantiated anywhere". That was
> **overstated and is withdrawn.** `NatureCluster.execute()` does
> `get_worms_by_category(self.nature)` → `_get_or_create_instance()` → `cls()`
> (`NATURE_CLUSTERS.py:532, 745`), so *every* registered worm is constructed by the
> generic fleet sweep and its zero-arg `execute()` called. The classes were
> reachable; their **outputs were dropped and their inputs never supplied**. The
> precise defect is *no consumer and no data*, not *no construction* — and the same
> distinction applies to the wider expansion tree (a static "never constructed"
> scan over `expansion/` reports ~117 of 145 worms, which is a **false positive
> machine** for exactly this reason and must not be cited as a finding).

*Impact:* 3 of 6 synapse worms were inert in practice — constructed, `execute()`d
with no input, results discarded. The "attention" and "MoE" claims describe code
whose advanced entry points never ran. **Registered is not wired, and constructed is
not consumed — this is the audit's central finding.**

**G2 — Reward magnitude is destroyed before learning.**
`synapse.py` `SynapseWeightWorm.update()`:
```python
self._spine.record_outcome("synapse", f"{src}>{dst}", reward > 0, abs(reward) * 100)
```
The float reward collapses to a **boolean sign**, and `abs(reward) * 100` is passed as
`duration_ms` — i.e. a fabricated latency. `self._lr` and `self._gamma` are stored in
`__init__` and **never read**. So the class docstring's "batch Q-learning (TD updates
with gamma)" is not implemented anywhere: there is no temporal difference, no next-state,
no discounting. Every "learned" edge weight is quantized to ±1.
*Impact:* the learning substrate has 1 bit of resolution.

**G3 — Route learning is dead-ended.**
`MeshRouterWorm.record_route_result()` — the only writer of `route:*` Q keys — has
**no callers** in `src/`. Consequence: `route()` computes
`effective_weight = base_w * (1 + q)` with `q` always `0.0`, so the "learned weight"
is always exactly the static registered weight. The adaptive routing described in the
docstring cannot occur. Confirmed live: the persisted Q table contains `triage:*` keys
only — **no `route:*` key has ever existed**.
*Impact:* cross-env routing is static; the topology never adapts.

**G4 — The engram/vector layer is not vector.**
`VectorShardWorm.shard_for(mem_id)` maps `sha256(mem_id) % 3` to a shard name — there are
**no embeddings, no similarity, no index, no vectors** in the engram nature.
`RecallRouterWorm` does dict lookup, not semantic recall. `CoherenceValidatorWorm`
compares hash *sets* (exact-match only), so near-duplicate drift — the thing the repo's
own sync history is full of (unicode-dash corruption) — is invisible to it.
Meanwhile `CORE/embedding_backend.py` already produces real 768/1024/4096-dim vectors
with a disk cache and a self-tuning dimension optimizer, and **faiss + chromadb are
installed** (G14). The mesh simply doesn't call any of it.
*Impact:* "distributed memory coherence" is a hash-partition of ids, not associative memory.

**G5 — The SSM is a fixed linear filter wearing a Mamba costume.**
`SSMSequenceWorm` docstring claims "faithful approximation of S4/Mamba". In real
selective-scan S4/Mamba, `Δ`, `B`, `C` are **input-dependent linear projections**.
Here `_B` and `_C` are `Random(42).gauss(0, 0.1)` constants initialised once and
**never updated** — there is no learning rule touching them. With constant B, the
recurrence degenerates to a leaky integrator whose `_C` "projection" is a fixed random
dot product over hidden state. `execute()` calls `summarize()` and reports a complexity
class, not a result.
*Impact:* sequence modelling is claimed and absent.

**G6 — "Attention" has no queries, keys or values.**
`AttentionRouterWorm.attend()` softmaxes a **scalar per nature** derived from Q keys.
There is no token-level attention, no Q/K/V, no context conditioning
(`task_context` is accepted and ignored). Worse, `update_from_outcome()` writes a
`±0.1/±0.15` delta into the *same accumulator* that `attend()` overwrites with an
EMA of Q — so the two update paths double-count and partially cancel.
*Impact:* "cross-nature attention" is a priority re-rank in a costume.

**G7 — Plasticity kernels are computed and thrown away.**
`HebbianUpdaterWorm.update()` returns `w_new` **to the caller**; nothing persists it.
`STDPClockWorm.apply()` likewise. `ElasticConsolidationWorm` anchors into a private
dict that no training loop consults. So Hebbian / STDP / EWC exist as **pure functions
with no weight table to act on** — there is no parameter store at mesh level for them
to modify. The plasticity nature is a library of kernels, not a learning system.
*Impact:* no anti-forgetting, no spike-timing credit — because there is nothing to forget.

**G8 — No credit assignment across the mesh graph.**
Q is a **per-(nature,worm) scalar with no state and no successor**. A worm that fails
only because an upstream worm corrupted its input is blamed in full; the upstream worm
is not. There is no eligibility trace, no trace decay, no propagation over the
`SpineMapperWorm` edge graph. The topology is *published* (118 nodes, route edges) but
never used as a **credit-assignment graph**. The naming says "neural mesh"; the learning
is a bag of independent bandits.

### TIER 2 — High (correctness + trust)

**G9 — Gossip is unauthenticated and therefore hijackable.**
`merge_spine_gossip()` adopts a peer record on **timestamp comparison alone**, and
adopts an unknown key's Q-weight unconditionally. Anything that can write a file into
`~/.azazael/gossip/` can inject Q-weights into the brainstem and thereby **re-order worm
execution** (healthy-first ordering) across a restarted environment. There is no
signature, no HMAC, no per-env monotonic sequence number, and no rollback protection —
a captured old payload is a valid payload.
This is inconsistent with the project's own standard: `CORE/audit_trail.py` already
implements Ed25519 payload signing (`_sign_payload`, `verify_signature`), Merkle roots
and inclusion proofs. The mesh's own state exchange is the one trust boundary in the
system that has no provenance check.
*Impact:* a supply-chain / local-tamper vector against execution ordering.

**G10 — Restart replay can silently lose adaptations.**
`_POLICY_JOURNAL_MAX = 100`, and `_replay_policy_journal()` replays `list(_journal)`
in insertion order. Live journal is at **64/100**. The Homeostat deliberately mutates
process-global `WORM_REGISTRY` state that does not survive process death, so the journal
is the *only* durable record of learned policy. With 224 worms and a 100-entry ring,
once the ring wraps, the oldest worms' adaptations become **unreplayable forever** and
silently revert to decorator defaults on the next restart. `revert_policy()` also
mutates the journal in place, so an audit-then-revert changes replay semantics.
*Impact:* a scale-dependent silent regression that will appear as "the fleet randomly
got worse after a restart".

**G11 — Reflex mutates shared globals with no per-env or per-process scoping.**
The reflex arc (fires inside `record_outcome`, held under `_HOMEOSTAT_LOCK`) reaches
into `WORM_REGISTRY[worm]` and mutates `cooldown_seconds`/`priority` — the *same dict*
the rest of the process reads for scheduling. Emergency backoff is thus globally visible
instantly and irreversibly within the process; two concurrent incidents on the same worm
compound (×3 each time the counter re-crosses the threshold after a scar), bounded only
by the 3600s cap. There's no per-env key despite the multi-env design, and no decay of
the inflated cooldown back to baseline except a manual `revert_policy()`.
*Impact:* one flaky worm can be de-prioritised ecosystem-wide and stay that way.

**G12 — Only one test file covers the entire fabric.**
`tests/test_spine_mesh.py` (28 tests, passing) is the **only** test file matching
`spine|mesh`. 70 fabric worms across 16 natures — including the autoencoder, the SSM,
the Hebbian/STDP kernels, quorum, shard routing and the federated aggregator — have no
test coverage. G1/G2/G3 survived a documented 85/85 green batch precisely because
nothing asserts that the synapse layer is reachable or that reward magnitude survives
the hand-off.
*Impact:* the gap class that matters (wiring + learning fidelity) is untested by construction.

### TIER 3 — Medium (capability left on the floor)

**G13 — The tiny autoencoder is hand-rolled while torch sits installed.**
`immune.py:191 AutoencoderAnomalyWorm` is a real 8→4→8 tanh MLP with random init
`Random(42)`, `lr=0.01`, and the comment *"no torch dependency"*. It is the only genuine
neural network in the fabric — 12 free parameters, random-seeded, per-instance, not
persisted, not shared with the mesh. It's a nice stdlib demo and a poor anomaly detector.

**G14 — Installed ML stack is disconnected from the mesh.**
Importable on the repo interpreter: `torch, numpy, transformers, faiss, onnxruntime,
sentence_transformers, sklearn, chromadb, numba, gymnasium, stable_baselines3, mygrad,
mcp`. Missing: `jax, taichi, ray`. The mesh fabric imports **none** of them except a
handful of numpy uses in `cppn/loom/nerve/oracle/tensorgene`. The `ORCHESTRATION/ml_platforms`
and `eve_unleashed` trees own the tensor stack; the mesh never calls across.
*Impact:* the frontier capability is on the box, in the wrong process.

**G15 — Observability stops at counters.**
The mesh emits no spans. `CORE/cd3_exporter.py` ships a **SQLite span exporter with
`query_trace_by_id` / `query_unified_trace`**, and it is wired to nothing in the
fabric (`telemetry.py` has its own ad-hoc `start_span` into a private dict). So there is
no critical-path view of a fleet run, no parent/child structure, and Q-learning cannot
be grounded in traces. Caps (`_SPINE_EVENTS_MAX=200`, `_OUTCOME_EVENTS_MAX=200`) also
mean a 224-worm fleet evicts its own signal within one cycle, and there is **no
per-edge route-usage telemetry** at all (the 09-13 doc already flagged this as an open
thread).

**G16 — Self-protection is applied by category algebra in one place, not as a rule.**
`SpineCycleWorm` is protected from Red Queen recursion by being registered
`orchestration` (outside `PROBE_NATURES`). Elegant — and *only* there. The same class of
hazard (a worm that mutates the fleet's own policy being itself policy-mutated) applies
to `HomeostatWorm`, `SpineMapperWorm`, `MorphogenesisWorm`, `ConsolidationWorm` and
`AutoencoderAnomalyWorm`. There is no declared "fleet-authority" invariant, no
`PROTECTED_NATURES` set enforced at registration, and nothing prevents a future
`_guess_category` keyword addition (the heuristics at `worm_registry.py:532-600` are
long `any(kw in name_upper ...)` chains) from re-filing a governor into a probed nature.
*Impact:* the correct instinct exists once; the invariant is not enforced.

### TIER 4 — Latent (will bite as the fleet grows)

**G17 — Registry collision surfaces are open.**
Discovery emitted **1× `worm_registered_overwrite`** in a single clean pass. The
`source_file`-based skip means a same-named worm in a second subdir is silently skipped
(the 09-13 doc notes this), and `GossipSyncWorm` reportedly already collides between
`expansion/mesh.py` and a legacy shim. `_guess_category`/`_guess_cooldown` are
name-keyword heuristic chains — at 224 worms the fabrication risk (right class, wrong
nature/cooldown because no keyword matched) grows with every `ClassWormTooManyWords` name.

**G18 — `q_order()` is O(n²) and unbounded-hot.**
`q_order()` calls `worm_names.index(n)` inside a comprehension over the same list.
Called from `NatureCluster.execute()` on the scheduling path, per cluster, per cycle.

**G19 — "Metabolic" is not metabolic.**
`metabolic.py` (`PowerBudgetWorm`, `ThermalThrottleWorm`, `QuotaEnforcerWorm`) exists but
is not fed by real CPU/thermal telemetry (psutil is installed). Cost-aware routing is
therefore not cost-aware. Same shape as everything else: the organ exists, the afferent
nerve does not.

---

## 4. Untapped frontiers on **this machine**

Resource inventory taken 2026-09-14:

| Resource | Status | Mesh exploitation today |
|---|---|---|
| `torch` 2.9-era, `onnxruntime`, `numba` | installed, importable | **none** |
| `faiss`, `chromadb`, `sentence_transformers` | installed, importable | **none** |
| `transformers`, `sklearn`, `mygrad` | installed, importable | **none** |
| `gymnasium`, `stable_baselines3` | installed, importable | **none** (SB3 only in `CORE/sb3_agent.py`) |
| Ollama (9 local models, **19 GB** on disk) | running | 1 model used, for embeddings only |
| `nomic-embed-text`, `bge-m3`, `qwen3-embedding` | pulled | 1 of 3 used |
| `minicpm-v`, `moondream` (vision) | pulled | **no vision path exists** |
| `eve-unleashed` (custom model) | pulled | not called by the mesh |
| NVIDIA GPU / CUDA | **absent** (`nvidia-smi` missing, no `nvml.dll`) | n/a — ollama ships SYCL/CPU |
| Free-threading 3.14t | enabled by design | ledger is a global RLock on the hot path |

The frontier is therefore **not** "get a bigger model". It is: *the mesh has a full
numeric/AI stack one import away and keeps choosing heuristics.*

**F1 — Vector-native engram (highest leverage, lowest risk).**
Replace `VectorShardWorm`'s `sha256 % 3` with a real index: `embedding_backend.embed_text()`
→ `faiss.IndexHNSWFlat` (or `chromadb` for persistence). `RecallRouterWorm` becomes ANN
search with a real score; `CoherenceValidatorWorm` becomes a cosine-drift threshold able
to catch the near-duplicate corruption class that hash equality cannot. Reuses the
existing disk-cached embedder and the existing dim optimizer. This single change turns
"distributed memory coherence" from a metaphor into a memory.

**F2 — Real credit assignment: eligibility traces over the topology graph.**
Promote Q from per-worm scalar to per-**edge** `(src→dst)` with trace decay λ, and
propagate blame along the edges `SpineMapperWorm` already publishes. Grounds G8 without
new hardware. `mygrad` is installed if you want gradients; traces alone need nothing.
This is what makes the 118-node topology *load-bearing* instead of a dashboard artefact.

**F3 — Train the SSM instead of seeding it.**
The ledger already stores `hist_ms` (20 samples/worm) and the outcome event stream is a
natural time series. Fit `B`/`C` (and an input-dependent `Δ`) by gradient on
next-outcome / next-duration prediction. `torch` is installed and the model is ~100
parameters — CPU-feasible in seconds. That converts a decorative class into the first
component in the fabric that is *fitted to this machine's own behaviour*.

**F4 — Replace `_guess_category`/`_guess_cooldown` heuristics with a learned router.**
224 worms × 16 natures × a growing outcome ledger is exactly a contextual bandit.
Features already available: prompt/context length, `needs_vision`, env, Q, scar state,
observed duration. LinUCB or a small SB3 agent (both installed) replaces keyword-chain
filing — and keyword chains are precisely where G17's fabrication risk lives.

**F5 — Cross-modal path that uses the vision models already on disk.**
`minicpm-v` and `moondream` are pulled and idle. `MoEDispatcherWorm`'s `needs_vision`
flag does nothing but bump a static expert score — a stub. A real vision worm (document/
image triage for the investigation corpus in this repo) plus learned MoE gating would be
the first *new capability* rather than a re-parameterisation.

**F6 — Sign the gossip channel with the audit stack you already built.**
`audit_trail.py` has Ed25519, Merkle roots and inclusion proofs. Sign `export_spine_gossip()`
payloads, carry a per-env monotonic sequence, reject stale/rolled-back payloads. Closes
G9 and makes multi-env gossip trustworthy enough to actually enable (today: 1 peer).

**F7 — Emit OTel spans from `NatureCluster.execute()` via `cd3_exporter`.**
One hook gives critical-path analysis, parent/child structure and per-edge route usage
(the unfilled telemetry). Then Q-learning is grounded in traces instead of a scalar, and
the 200-event caps stop mattering because the SQLite exporter is the durable store.

**F8 — A "MeshArchitect" worm: make the topology itself the search space.**
Today the mesh *reports* its structure (`SpineMapperWorm` → 118 nodes) and *adapts
parameters* (cooldown/priority). Nothing proposes **structural** change: add/remove an
edge, split a cluster, retire a worm. With a real credit graph (F2) and traces (F7), a
worm can propose topology edits and be evaluated by the same ledger that judges
everything else. That is the difference between a self-tuning fleet and a
self-designing one — the actual frontier this machine has the parts for.

**F9 — Stop serialising the hot path.**
Every outcome takes a global `RLock`, and the reflex arc does a registry lookup inside
it. On 3.14t free-threading the right shape is per-thread shards (LongAdder-style) with
a single consumer draining a ring buffer. At 224 worms this is currently fine; it is the
first thing that will break at 10×.

---

## 5. Prioritised roadmap

| Priority | Action | Gap | Rationale |
|---|---|---|---|
| **P0** | ✅ Wire (or delete) `MoEDispatcherWorm`, `AttentionRouterWorm`, `SSMSequenceWorm`; add a test asserting every registered fabric worm is reachable from a caller | G1, G12 | Cheapest possible fix for the audit's central finding. Registered-but-dead is worse than absent: it inflates the count and the claims. **Done §6.1/§6.2.** |
| **P0** | ✅ Fix `SynapseWeightWorm.update()` to pass signed magnitude; remove or implement `lr`/`gamma` | G2, G8 | 3-line change; restores the only live learning signal to >1 bit. **Done §6.1.** |
| **P0** | ✅ Decide `record_route_result()`: call it from `MeshRouterWorm.route()`/transport, or delete the claim | G3 | Currently the routing docstring is false. **Done §6.2 — the first `route:*` key the table has ever held.** |
| **P1** | ✅ Vector-native engram over `embedding_backend` + `faiss`/`chromadb` | G4, G14, F1 | Highest capability-per-line in the whole list; reuses existing cache + dim optimizer. **Done §6.1.** |
| **P1** | ✅ Sign + sequence gossip; reject stale payloads | G9, F6 | Turns a tamper vector into a trust boundary; unblocks real multi-env. **Done §6.1.** |
| **P1** | ✅ Policy journal → latest-per-worm map (compacting), not a 100-entry ring | G10 | Removes a silent scale-dependent regression. **Done §6.3.** |
| **P2** | ✅ Eligibility traces over the mapper's edge graph | G8, F2 | Makes the 118-node topology load-bearing. **Done §6.2.** |
| **P2** | ✅ OTel spans from `NatureCluster.execute()` via `cd3_exporter`; per-edge route telemetry | G15, F7 | Prerequisite for principled learning and for trusting any of the above. **Done §6.2 (spans) + §6.3 (per-edge + per-route telemetry, §7 closed).** |
| **P2** | ✅ Persist + share a real (small) anomaly model; retire the frozen `Random(42)` nets | G5, G13 | The two frozen-random components become one fitted one. **§6.3: fitted by real backprop on both layers, persisted, wired. §6.4: carried over the gossip transport inside the signed envelope, adopted only when strictly better trained, shape-checked on arrival.** |
| **P2** | ✅ Give the metabolic trio an afferent nerve and a consumer | G19 | Symptom of the same shape as everything else: organ present, nerve absent. **§6.4: measured inert (zero callers, `sample_c()` → `None` on Windows, empty `spent`), then fed by psutil with estimates labelled as estimates.** |
| **P2** | ✅ Label heuristic-derived registry metadata; feed the guess the *defining* module | G17 | The guess was fed the module being *scanned*, so a re-export shim poisoned it. **§6.4: `utility` bucket 12 → 5, provenance flagged and countable.** Collision detection (`source_file` skip, same-name overwrite) remains open — but overwrite events measured **0** at 225 worms. |
| **P3** | ✅ `MeshArchitect` worm proposing topology edits | F8 | The actual frontier; needs P2 first. **Done §6.4 — propose-only by default, writes a revertible overlay, never mutates `NATURE_DEFINITIONS`, and is unprobeable by design.** |
| **P3** | ◐ Per-thread ledger shards; `q_order` without `.index()` | G18, F9 | Scale work, not correctness work — schedule before the fleet 10×'s again. **§6.3: `q_order` done, with a test asserting the new ranking is identical to the old form. Ledger sharding still open.** |
| **P3** | ✅ Declare `PROTECTED_NATURES` (fleet-authority invariant) enforced at registration | G16 | Generalise the one good instinct into an invariant. **Done §6.3 — and it was not latent, it was live.** |

---

## 6. Claim verification

| Claim | Evidence |
|---|---|
| 224 worms / 70 fabric worms / 16 natures | `discover_worms()` + `Counter(category)` on repo interpreter, 2026-09-14 |
| 1× `worm_registered_overwrite` in one pass | same run (log line `[registry] worm_registered_overwrite`) |
| 118 spine nodes, 58 homeostat, 58 Q, 2 scars, 64 journal | `~/.azazael/spine_state.json` (`saved_at 2026-09-14T01:01:13`) |
| Only `triage:*` Q keys — no `route:*` ever | same file, `q_weights` sample |
| Single gossip peer | `ls ~/.azazael/gossip/` → `windows.json` only |
| `MoEDispatcherWorm`/`AttentionRouterWorm` have no caller | `grep -rn` over `src/` → definition + `__init__.py` import + one docstring mention (`dendrite.py:54`). **Note:** they *are* constructed by the generic cluster sweep (`get_worms_by_category` → `cls()`), so this is a no-consumer finding, not a never-constructed one — see the G1 correction |
| `record_route_result` has no callers | `grep -rn record_route_result src/` → definition (`mesh.py:167`) only |
| Reward → boolean, `lr`/`gamma` unread | `expansion/synapse.py` `SynapseWeightWorm.update()` / `__init__` |
| SSM `B`/`C` = `Random(42)` constants, never updated | `expansion/synapse.py` `SSMSequenceWorm.__init__`; no writer found |
| Plasticity kernels return `w_new`, nothing stores it | `expansion/plasticity.py` all three classes |
| `sha256(mem_id) % 3` sharding, no vectors | `expansion/engram.py` `VectorShardWorm.shard_for` |
| Ed25519 signing exists but is not used by gossip | `CORE/audit_trail.py` `_sign_payload`/`verify_signature`; `export_spine_gossip` carries no signature |
| Only one mesh test file | `grep -rln "spine|mesh" tests/` → `test_spine_mesh.py` only |
| ML stack installed, unused by fabric | `importlib.util.find_spec` sweep: `torch/numpy/transformers/faiss/onnxruntime/sentence_transformers/sklearn/chromadb/numba/gymnasium/stable_baselines3/mygrad/mcp = True`; `jax/taichi/ray = False`. Fabric imports: only numpy in `cppn/loom/nerve/oracle/tensorgene` |
| No NVIDIA GPU | `nvidia-smi` → command not found; no `nvml.dll` |
| 9 local models, 19 GB | `~/.ollama/models/manifests/...`: `bge-m3, eve-unleashed, gemma2, gemma4, llama3.2, minicpm-v, moondream, nomic-embed-text, qwen3-embedding`; `du -sh blobs` → 19G |
| OTel exporter unwired | `grep -rn "cd3_exporter\|get_exporter\|start_span"` → only `cd3_exporter.py` itself + `telemetry.py:53` private span |
| `q_order` O(n²) | `spine_registry.py` `q_order()` uses `worm_names.index(n)` |

---

## 6.1 Remediation landed (2026-09-14, same session)

The four highest-priority items were implemented and verified in the repo:

| Gap | Change | Where |
|---|---|---|
| **G2** | `record_outcome()` gained an optional signed `reward` parameter and the brainstem now reinforces from that magnitude instead of the boolean sign; `SynapseWeightWorm.update()` computes a real `td_error = r + gamma*V(s') - V(s)` and hands over `lr * td_error`. `lr`/`gamma` are now read, and `stats()` exposes them plus the last TD error. | `CORE/spine_registry.py`, `expansion/synapse.py` |
| **G1** | `SpineCycleWorm` instantiates `AttentionRouterWorm`, `SSMSequenceWorm` and `MoEDispatcherWorm` and drives them from the live outcome stream in a new `synapse_routing` cycle stage (attention bias per nature scaled by success rate; SSM ingests the +/-1 outcome stream; MoE preference reported). `CROSS_NATURE_ROUTER` now uses the MoE ranking to pick the inference expert and feeds the outcome back into the shared Q-table. | `expansion/spine.py`, `CORE/WORMS/CROSS_NATURE_ROUTER.py` |
| **F1** | `VectorShardWorm` holds real embeddings + an ANN index with a `faiss → numpy → stdlib` fail-open chain (FlatIP exact for small corpora, HNSW above 512); `RecallRouterWorm` routes on semantic hits while keeping the id fast path; `CoherenceValidatorWorm` adds cosine drift detection; `DreamConsolidatorWorm` indexes kept dreams. | `expansion/engram.py` |
| **G9** | Gossip payloads carry a monotonic per-env `seq` and an Ed25519 signature + signer key (lazily via `audit_trail`, so the module stays stdlib-only). `merge_spine_gossip()` gates on replay (`seq` rollback), key pinning (TOFU per env) and signature, and reports `signature`/`policy`/`seq` so unauthenticated merges are observable. Policy is `strict` by default (`warn`/`off` via `AZAZAEL_GOSSIP_POLICY`); when crypto is unavailable `strict` degrades to seq-only **and says so** instead of implying authentication. Anti-replay state is persisted across restarts. | `CORE/spine_registry.py` |

**Verification of the remediation**

| Check | Result |
|---|---|
| `tests/test_spine_mesh.py` | **60 passed, 0 skipped** under Python 3.14t (was 44; +16 new tests — the last was skipping on the broken crypto install) |
| Batch: `test_spine_mesh + test_worm_lifecycle + test_worm_registry + test_nature_clusters_unit + test_cross_nature_orchestration` | **160 passed, 1 skipped, 0 failed** |
| Wider batch incl. `test_nature_clusters[_extended]`, `test_metacluster`, `test_worm_imports`, `test_startup_warm_wiring`, `test_clusterworms_unit` | 323 passed, 2 skipped, **1 pre-existing failure** (see below) |
| `py_compile` on all 7 changed files | clean |
| Live spine cycle | `synapse_routing` stage returns attention (top natures from the Q-table), sequence (`tokens=18, params_updated=17`) and a resolved MoE expert pair |
| Live engram | real Ollama embeddings + **faiss** backend; paraphrase query scored 0.6885 against the correct memory where the old code could only hash-match |
| `mypy` | runs under Python 3.14t — the earlier "cannot run" was a wrong-interpreter artifact, see the toolchain note below |

New tests added: explicit-consumer guard for the wired worms, cycle-drives-synapse-layer
with real data, reward-magnitude preservation + gamma-is-real, semantic search beats dict
lookup, shard-placement stability + recall routing, coherence drift classification,
MoE expert resolution, MoE feedback into the shared Q-table, SSM readout fitting,
dream indexing, gossip sequencing, replay rejection, key-change rejection, strict-policy
contract, and **signature plumbing under a stubbed crypto backend** (so the trust path is
verified deterministically even though the real backend is broken here).

*Pre-existing failure found and fixed during verification (not a regression):*
`test_worm_lifecycle.py::test_discover_loads_registry` asserted
`discover_worms() > 0`, but that function returns **0 on a latecomer call** by design
(`_discovery_done`, present in `HEAD:src/CORE/worm_registry.py:275`), so the test failed
whenever any earlier test in the same process had already discovered. It now asserts the
registry is populated, which is what its own docstring says it means.

**The crypto signalled inert, and this section previously recorded the wrong cause.
Corrected root cause and remediation below.**

*What I first reported (now withdrawn):* that `cryptography` 46.0.7 was a broken wheel
and `mypy` was broken via a missing `librt.internal`. Both diagnoses were artifacts of
running the **wrong interpreter**. This repo mandates **Python 3.14t**
(`pyproject.toml:10`) and `python3.14t.exe` is the launcher default; I had been probing
with the standard GIL build (`Py_GIL_DISABLED=0`). The `.cp314t-*.pyd` extensions were
correct all along.

*Actual findings:*
1. **`mypy` was never broken.** Under `python3.14t` it runs normally. Nothing to fix.
2. **The free-threaded interpreter lacked a C-ABI backend.** `site-packages` held
   `_cffi_backend.cp314.pyd` (GIL-only) with no `cp314t` counterpart, because the repo's
   required runtime had been side-loaded onto a GIL-native install. That is what made
   `cryptography` import-fail — an **incomplete** install, not a bad one.
3. **After that fix, a genuine, version-independent segfault remained:**
   `from cryptography.hazmat.primitives import serialization` **crashes the process
   (exit 139) on free-threaded 3.14.7**. Reproduced cleanly; `cryptography` **50.0.1
   segfaults identically**, so it is not a version bug, and the upgrade also violates
   `mlflow`/`msal` pins and was reverted.

*Remediation (both additive, without regressing the GIL build):*
- Installed the **`cffi` 2.1.1 `cp314t` wheel** so the mandated runtime has
  `_cffi_backend`, and **kept `_cffi_backend.cp314.pyd`** in place so the GIL build still
  works. The two C-ABI backends coexist by filename; neither was displaced.
- **Removed the segfaulting `serialization` module from the audit spine's critical
  path.** `CORE/audit_trail.py` only ever needed raw key bytes, so it now signs via
  `private_bytes_raw()` / `public_bytes_raw()` / `from_public_bytes()`, all of which
  avoid `serialization` entirely. The crash is gone from the critical path rather than
  papered over with a pin.

*Verified result:* `crypto_available=True` with **real Ed25519 keys and signatures
produced, no segfault** — so the Ed25519 / Merkle / non-repudiation layer of the VLP
audit stack is now **live**, and `AZAZAEL_GOSSIP_POLICY=strict` enforces actual
signatures rather than degrading to sequence-only. Suite under the mandated 3.14t
interpreter: **60 passed, 0 skipped** (the real-crypto gossip test now executes; it had
been skipping).

*Standing landmine, documented:* `serialization` (PEM I/O) **still segfaults on 3.14t**
and is genuinely required by two other modules (`parallax_validator` and the archive
provenance path). Those imports sit off the mesh's hot path so they are not fatal here,
but anything that touches them on 3.14t will kill the process instead of raising. This
should be filed upstream (CPython 3.14t × cryptography) and guarded with a subprocess
isolation or a feature-detect before first use.

## 6.2 Remediation, second pass (2026-09-14) — the orphan sweep

The first pass wired the three worms I had *named*. This pass asked the
mechanical question instead: **which registered organs have no caller?** A
static scan of every public method across the 61 `expansion/` modules found
**302 of 679 with zero callers outside their own file**. Most of that is
legitimate internal API — but it contained the exact defects the audit had
flagged by eye, plus more.

*Correction to my own method, again:* an earlier version of this audit implied
"never instantiated" was the test for an orphan. It is not, and a scan for that
reports 117/145 false positives, because `NatureCluster.execute()` constructs
every registered worm via `get_worms_by_category()` → `cls()`. **The real test
is "has no consumer", not "is never constructed".** The scan above uses the
right discriminator.

| Gap | What was actually wrong | Fix |
|---|---|---|
| **G7** | `SpineCycleWorm._apply_plasticity()` called `hebbian.update(0.0, pre, post)` — a **hardcoded zero weight** every cycle. Every delta was measured from zero and the returned `w_new` was discarded. The kernels were correct; **the weight store did not exist.** | New `PlasticityEngineWorm` + `EligibilityTraceTable`: persistent per-edge weights, real `STDPClockWorm.kernel(dt)` evaluated at the true inter-event timestamp, Hebbian co-activation, EWC anchoring, Ebbinghaus review scheduling, and neuromodulator gain. |
| **G3** | `MeshRouterWorm.record_route_result()` had **zero callers in the entire tree**, so `q` was permanently 0 and `effective_weight` always equalled the static weight. The mechanism was implemented, correct, and unreachable. | `_mesh_route_feedback()` in the cycle: settles the previous cycle's route against the observed fleet success rate, then proposes the next. |
| **F2** | Credit was a **stateless per-worm scalar**, so a delayed failure never reached the worm that set it up. | TD(λ) eligibility traces: `e ← γλ·e` with `w += lr·e·reward`, so one reward reaches every edge that contributed to it. `γλ < 1` guarantees traces vanish. |
| **Orphans (new)** | `ThalamicGateWorm.filter()`, `ArousalSwitchWorm.get_mode()`, `GossipSyncWorm.gossip()`, `Neuromodulator.modulations()`, `ElasticConsolidationWorm.anchor_task()/penalty()`, `ForgettingCurveWorm.next_review_hours()` — all registered, all uncalled. | Each now has a real consumer in the cycle or the plasticity engine. |
| **OTel (new)** | `cd3_exporter.configure_otel_tracing()` **raised on every call**: `BatchSpanProcessor` validates `max_export_batch_size ≤ max_queue_size` but *defaults the former to 512*, so passing only `max_queue_size=batch_size` (default 64) was always invalid. The project's entire OTel path was unreachable. | Set both from the same value; tolerate an already-installed provider. `NatureCluster.execute()` now exports a parent span + one child span per worm into `memory_store.db`. |

**Live evidence (not inference):**

| Probe | Observed |
|---|---|
| Route Q-table | `['route:windows>mesh']` — the **first `route:*` key the table has ever held**; `effective_weight` moved `1.0 → 0.6` (`q: -0.4`) between cycles |
| Weight store | `mesh->mesh w=0.138` persisted across `learn()` calls; second pass built on the stored value rather than from zero |
| Eligibility traces | `active_traces=1`, `trace 0.30324` over `7` events; decays and provably vanishes after 40 steps |
| Neuromodulation | `modulation 0.8672` — `Neuromodulator.modulations()` now has a caller |
| Forgetting curve | `next_review {hours: 16.6}`, `recall_at_horizon 0.5007` against a `0.5` threshold — the Ebbinghaus math checks out |
| Salience gate | `gate {applied: true, input: 10, kept: 10}` |
| OTel spans | `nature_cluster.execute` ×1 + `worm.execute` ×5, with `nature`/`worm`/`success`/`duration_ms` attributes |

**A failure mode I introduced and then caught:** my first salience gate was so
aggressive that it filtered the entire window, so the plasticity stage returned
`all_below_salience` and learned nothing — a silent regression, since the cycle
still reported success. The gate is now explicitly **advisory**: if it would
leave fewer than two events, it falls open to the ungated window. "Learn nothing,
forever" is worse than "learn from a quiet window". There is a test for exactly
this.

**Verification (Python 3.14t, the mandated runtime):**

| Check | Result |
|---|---|
| `test_spine_mesh.py` + `test_spine_mesh_wiring.py` (new) | **70 passed, 0 skipped** |
| `+ test_worm_lifecycle.py` + `test_worm_registry.py` | **104 passed, 0 skipped** |
| Nature/cross-nature/metacluster batch | **126 passed, 0 failed** |
| `py_compile` on all changed files | clean under 3.14t |

> A process note worth recording: several verification runs in this pass silently
executed on the **wrong interpreter** (a `[ -x $FT ] || FT=python` guard whose
path did not exist), so they fell back to the GIL build and the crypto test
skipped. The headline numbers above were re-taken with the interpreter path
verified (`GIL_DISABLED=1`, `CRYPTO_AVAILABLE=True`). Reporting a green suite
without confirming *which* runtime produced it is its own kind of false claim.

## 6.3 Remediation, third pass (2026-09-14) — state durability, telemetry, invariants

This pass took the roadmap's remaining P1–P3 rows, plus the §7 open thread.

The headline is not any one fix: it is that **the audit's own "latent" framing was wrong in
one case.** G16 was filed as *will bite as the fleet grows*. It was already biting.

| Gap | What was actually wrong | Fix |
|---|---|---|
| **G10** (P1) | `_POLICY_JOURNAL` is a bounded FIFO ring (`_POLICY_JOURNAL_MAX = 100`) and `worm_registry._replay_policy_journal()` reconstructs adapted cooldowns by replaying it on restart. That makes the *audit log* load-bearing for *state*: once the ring wraps, a worm whose last adaptation has been evicted silently reverts to its decorator default. **The failure only appears once the fleet is busy enough to wrap the ring**, which is why it was filed latent — and it was sitting at 64/100. | New compacting `_POLICY_LATEST` map (one entry per worm, last writer wins) is now the replay source; the ring remains the human-readable audit log. Persisted as `policy_latest` and restored with `setdefault` semantics so a mid-process `load_spine_state()` cannot roll a live adaptation back to the last saved value. |
| **§7** (P2 thread) | `SpineMapperWorm.map_topology()` published `"routes": []` on every node with the comment *"per-worm route edges filled below"* — **nothing ever filled them.** The mapper advertised telemetry it did not have. | Per-worm edges are now observed, from two real sources: the worm's learned Q and the outbound nature edges of its nature. Per-route usage is read back out of the homeostat ledger that `record_route_result()` writes (successes/failures/q/effective weight), published as `route_edge` events plus an `env:<dst>` node. The mapper takes the plasticity engine as `edge_source` and reports the top weighted edges. |
| **G13** | Four separate defects in one 12-parameter net: **`_W_dec` was never updated** (only the encoder was nudged, by a rule that ignored the tanh derivative and the decoder's own error path, so the "reconstruction" the threshold keyed off came from a matrix frozen at `Random(42)`); nothing was persisted; `_alerts` grew without bound; and `observe()` had **zero callers**, so it never ran at all. | Exact MSE gradients through both layers (`dL/dz = (x̂ − x)` back-propagated through tanh) with momentum; `export_model`/`import_model`/`save`/`load`; alerts bounded at 200; and the cycle now feeds it a bounded 8-feature ledger vector every tick. The alert decision was also re-ordered to be genuinely out-of-sample — the original took the threshold from a distribution that already contained the observation, letting one outlier raise its own threshold. |
| **G16** | No declared fleet-authority invariant. `SpineCycleWorm` escaped Red Queen probing only by being registered `orchestration`. **Measured: four regulators sit *inside* probed natures** — `HomeostatWorm`(synapse), `SpineMapperWorm`(mesh), `MeshRouterWorm`(mesh), `AutoencoderAnomalyWorm`(immune). `pressure_probe()` takes the first N worms of a nature in registration order, so **the queen was probing the organs that regulate the ledger its probes feed** — a closed feedback loop, not a future risk. | `PROTECTED_NATURES` (natures never probed) and `FLEET_GOVERNORS` (class → the one nature it may be registered under) are now declared, and registration **raises** on a mismatch — which is what stops `_guess_category`'s keyword chains from silently re-filing a governor. Governors are tagged at registration and `RedQueenWorm` skips them regardless of nature; the probe result reports `protected_skipped`. |
| **G18** | `q_order()` called `worm_names.index(n)` inside a comprehension over the same list — O(n²) on the scheduling path, per cluster, per cycle. | Precomputed first-seen positions. Tie-break semantics are byte-identical to the original expression (there is a test that asserts equality against the old implementation, not just a timing bound). |

**Live evidence (Python 3.14t, the mandated runtime):**

| Probe | Observed |
|---|---|
| Mapper telemetry | `worms=224, nature_edges=70, route_edges=1, worm_edges=3`; top edges `synapse->synapse 2.0`, `mesh->mesh 1.3533`, `mesh->synapse 0.116` |
| Per-worm edges | `AutoencoderAnomalyWorm` node carries `category=immune, q=0.4` and three real outbound edges (`immune->defense`, `->orchestration`, `->mesh`) — the field that used to be `[]` on all 224 nodes |
| Route telemetry | `route Q keys: ['route:windows>mesh']`; `proposed={'dst':'mesh','effective_weight':0.36,'q':-0.64}`, `settled={'success':False,'fleet_rate':0.0}` — the route's learned weight is visibly starving after observed failures |
| Anomaly detector | `obs=2, upd=2, err=0.7016`, metrics `[0.9919, 0.0081, 0.989, 0.1, 0.404, 1.0, 1.0, 0.0]` — bounded, and `route_health=0.0` correctly flags the failing route above |
| Protected governors | `is_protected_worm` → `True` for `HomeostatWorm`, `SpineMapperWorm`, `AutoencoderAnomalyWorm`; `pressure_probe("immune")` reports `protected_skipped=[AutoencoderAnomalyWorm]` |
| Policy memory | `get_policy_latest()` populated; the ring-wrap test evicts a target entry and asserts the adaptation still replays |

**Verification:**

| Check | Result |
|---|---|
| New `tests/test_spine_mesh_telemetry.py` | **13 passed** |
| `test_spine_mesh` + `_wiring` + `_telemetry` + `worm_lifecycle` + `worm_registry` | **117 passed, 0 failed** |
| nature/cross-nature/metacluster/clusterworms/imports/startup-warm batch | **290 passed, 2 skipped, 0 failed** |
| `py_compile` on all changed files | clean under 3.14t |

Changed: `CORE/spine_registry.py`, `CORE/worm_registry.py`, `CORE/WORMS/expansion/spine.py`,
`CORE/WORMS/expansion/immune.py`, new `tests/test_spine_mesh_telemetry.py`.

## 6.4 Remediation, fourth pass (2026-09-14) — re-measuring the "latent" tier

This pass existed because §6.3 ended with a lesson worth acting on: *"latent" is a
claim about the present, not a prediction.* G16 was filed latent and turned out to be an
active feedback loop. So every remaining Tier-4 item was measured rather than assumed.

### The re-measurement

| Gap | Filing | Measured 2026-09-14 | Verdict |
|---|---|---|---|
| **G10** | Latent — ring wrap will eventually revert adaptations | Journal on disk at **79 / 100** entries (was 64 earlier the same day) | **About to bite** — ~21 policy events from the first silent eviction. Already fixed in §6.3; the measurement now justifies the fix rather than merely describing it. |
| **G16** | Latent — "will bite as the fleet grows" | Four regulators sat inside probed natures; the Red Queen was probing its own afferent organs | **Live** — corrected in §6.3 |
| **G17** | Latent — heuristic fabrication risk grows with fleet size | Overwrite events = **0** (only 225 worms), *but* **12 worms were filed `utility` by the default branch**, including `DataPipelineWorm`, `FeatureEngineer`, `ModelVersioner`, `SchemaAwareFeatureExtractor` — all from `learning_*` modules | **Live (the fabrication half, not the collision half)** |
| **G18** | Latent — O(n²) scheduling path | Confirmed by inspection | Fixed in §6.3 |
| **G19** | Latent'ish — "the organ exists, the afferent nerve does not" | **Worse than filed.** All three worms had **zero callers**; `sample_c()` returned `None` on *every* call (its only sources are Linux sysfs paths and this host is Windows); `recommend_threads()` therefore reported `state: "unknown"` and returned the untouched default; `execute()` reported `{'spent': {}}` and `scopes: []` after a full session | **Live — the trio was inert, not merely unfed** |

Two of four were live and one was days from biting. The "latent" tier had a 75% hit rate.

### G17 root cause — the guess was fed the wrong module

The heuristic was not the problem; **its input was**. `_guess_category()` received the
module being *scanned*, not the module that *defines* the class. Those differ whenever a
class is reached through a re-export, and the deprecated `ECOSYSTEM_EXPANSION` shim
re-exports 50 worm classes. So `DataPipelineWorm` (defined in
`expansion/learning_pipeline.py`) was guessed from the name `"ECOSYSTEM_EXPANSION"`,
matched no rule, and fell into the `utility` default.

Fixed by feeding the guess `cls.__module__` and by adding a declared **module-prefix map**
(`learning_` → `learning`, `ml_` → `ml`, …) checked before the class-name keyword chains,
because a module name is declarative where a class name is merely descriptive. Measured
effect: **`utility` bucket 12 → 5**, and 7 of the 9 heuristic filings now resolve correctly.

Every guessed entry now carries `category_source: "heuristic"`,
`registration_source: "heuristic"` and the `category_hint_module` that produced it, plus a
`worm_auto_registered` log event. The fabricated-metadata population is countable instead of
invisible — and the disagreement between `module` (defining file) and
`category_hint_module` is exactly the signal that would have exposed this a year earlier.

### G19 fix — an afferent nerve, and an honest label on it

There is **no wattmeter and no temperature sensor available** here (no RAPL on Windows;
psutil 7.x exposes no `sensors_temperatures` on this host). So the fix does not invent
numbers:

* `PowerBudgetWorm.sample_load()` measures CPU utilisation, core count and load average via
  psutil (installed, never called), reporting `warm: False` on the first non-blocking
  sample instead of passing a baseline-less `0.0` off as an idle machine.
* `estimate_watts()` interpolates between idle and full draw and **always** returns
  `estimated: True` / `source: "load-proxy"`.
* `ThermalThrottleWorm` keeps the sysfs path, adds a psutil fallback, and when there is
  genuinely no sensor it falls back to a **load-based proxy** and says so (`source:
  "load-proxy"`) rather than collapsing "I cannot measure temperature" into `nominal`.
* All three have a real consumer in `SpineCycleWorm._metabolic_stage()`. The budget's `over`
  verdict now sheds load (Red Queen probe limit reduced to 1, reported); the quota gates the
  gossip **write** only, so throttling our visibility never blinds us to peers.

### F8 — `MeshArchitectWorm` (the frontier item)

Proposes **structural** edits instead of tuning scalars, and only from observed learning
signal: **strengthen** a strong edge into a healthy nature, **weaken** a negative edge or a
failing target, **declare** a learned edge that `NATURE_DEFINITIONS` never declared.

Safety shape, because this is the highest-blast-radius object in the mesh: `propose()` is
read-only and is what the cycle calls every tick; `apply()` writes to a **persistent
overlay** and never to `NATURE_DEFINITIONS` (a module constant shared by every cluster);
it is bounded and every proposal carries its evidence. It is registered `orchestration`,
declared in `FLEET_GOVERNORS`, and therefore unprobeable by the Red Queen. Wired into the
cycle as stage 2g, applying only when the cycle is called with `apply=True`.

The prerequisite the original audit stated — "needs F2 and per-edge telemetry first" — is
now met, which is why this could be built at all.

### A protocol bug found while wiring the quota gate

`SpineGossipWorm.exchange()` merged peer files and called the legacy `gossip_exchange()`
— the **only** code that writes our own payload — *only when it had found no peers*. An
env that discovered a single peer therefore stopped being visible to it: **gossip became
one-directional after the first successful discovery.** Merging is not a substitute for
publishing; both now always run, and `publish_skipped` makes a suppressed write observable.

### The shared anomaly model

The fitted detector now travels over the **existing signed envelope**: it is one more field
inside the canonical form, so it is covered by Ed25519, the seq gate and key pinning with
no new trust path, and editing it in transit produces `bad_signature` like any other field.
Adoption is **monotone** — strictly more observations wins, whoever produced it — which
prevents two envs overwriting each other forever, and a malformed model is shape-checked
and rejected before it can touch a peer's net.

**Live evidence (Python 3.14t):**

| Probe | Observed |
|---|---|
| Registry | `worms: 225` (includes `MeshArchitectWorm`), `heuristic-registered: 9`, `utility` bucket 12 → 5 |
| Metabolic | `cpu=0.0 cores=16 warm=False` → `spent=25.0 budget=65.0 over=False estimated=True source=load-proxy` |
| Thermal | `state=nominal source=load-proxy threads=16 throttling=False` |
| Quota | `{'scope': 'gossip_publish', 'allowed': True, 'used': 1, 'limit': 60}` — the first real use the organ has ever had |
| Topology (F8) | `proposed=5 applied=5 mutated_config=False`; e.g. `declare synapse->synapse w=2.0`, `strengthen immune->mesh w=0.595528` — each with the evidence that produced it |
| Anomaly sharing | `obs=1 upd=1 published=True`, `shared_model={'present': True, 'source': 'local', 'observations': 1}` |
| Gossip | `published=True exchanged=True` |

**Verification:**

| Check | Result |
|---|---|
| New `tests/test_spine_mesh_architect.py` | **16 passed** |
| spine suites (mesh + wiring + telemetry + architect) + lifecycle + registry | **133 passed, 0 failed** |
| nature/cross-nature/metacluster/clusterworms/imports/startup-warm batch | **290 passed, 2 skipped, 0 failed** |
| `py_compile` on all changed files | clean under 3.14t |

Changed: `CORE/spine_registry.py`, `CORE/worm_registry.py`,
`CORE/WORMS/expansion/spine.py`, `CORE/WORMS/expansion/metabolic.py`,
`CORE/WORMS/expansion/__init__.py`, new `tests/test_spine_mesh_architect.py`.

## 7. Open thread closed

`SpineMapperWorm` published nature-graph edges only, and per-worm route usage — *which edge
actually fired* — was unfilled telemetry. Noted 2026-09-13, still open on 2026-09-14, and
promoted to a P2 prerequisite because F2 (credit assignment) and F8 (topology search) both
consume that signal. **Closed in §6.3.**

One thing this pass taught that belongs in the doc rather than in a commit message:
**"latent" is a claim about the present, not a prediction.** G16 was filed as a future hazard
and turned out to be an active feedback loop — the Red Queen probing its own regulators. The
fleet was at 224 worms, not 2000. Anything in this document marked latent should be re-read as
*"I have not measured this yet"*, not as *"this is fine for now"*.

That lesson was then tested directly in §6.4 by measuring the whole tier: of the four
remaining latent items, **three were live** (G16, G17, G19) and one (G10) was at 79/100 — a
75% hit rate for a tier that reads as "not yet a problem".

If exactly one thing is fixed from this document, fix **G1**: the mesh's most
sophisticated-sounding components are the ones that never execute.

## 6.5 Fourth pass — environment, hot path, the HTML view, and the live monitors

Three threads this pass: fix the environment for good, take the ledger off the global lock, give
the mesh view an actual check — then audit the four live wallboards, which is where the most
consequential finding is.

### 6.5.1 Environment: a *class* of defect, not three incidents

§6.1 fixed `cryptography`. It was not one bug. Every native extension in the shared
`site-packages` is built for the **GIL** ABI (`*.cp314-*.pyd`) while the mandated interpreter is
**free-threaded** (`python3.14t.exe`). A GIL-built extension cannot load in that process, and the
failure surfaces differently per package — which is why it kept looking like unrelated breakage:

| Surface | Package | Symptom |
|---|---|---|
| segfault | `cryptography` (`.serialization`) | hard crash, no traceback |
| ImportError | `greenlet` (`_greenlet`) | `No module named 'greenlet._greenlet'` |
| ImportError | `numpy` (`_multiarray_umath`) | "bad install" advice from numpy itself |
| ImportError | `scikit-learn`, `scipy`, `pandas`, `orjson`, … | "install seems to be broken" |

Measured one process per module so crashes are attributable: **27 of 48 probed packages failed to
import.** After installing cp314t wheels where they exist, and restoring the cp314 builds
alongside (additively, so the standard interpreter keeps working), **8 remain**: `numba` (still
segfaults at its newest release; imported by exactly one file, inside a `try`) plus six packages
with no cp314t wheel published at all (`orjson`, `zstandard`, `brotli`, `fastuuid`,
`tree_sitter`, `tensorstore`) — **none of which the project imports**. `mygrad` also segfaults,
from `nnet/layers/gru.py`.

Worth recording: `numpy` fails at *import* and `scipy` reports its own install as broken. Both
point the reader at the package, and the package is fine. The defect is the interpreter/ABI
pairing.

**Two measurement errors I have to own**, because I nearly reported their output as findings:

- Running the probe with `cwd = site-packages` shadows imports, so `import PIL` / `import h5py`
  failed with "cannot import name `_imaging`" and "cannot import from inside the install
  directory". Both were my working directory, not the environment.
- A prose-level import loop using bare module names reported "61 worm modules unimportable".
  They are `CORE.WORMS.expansion.*` modules; the loop simply used the wrong import form.
  Discarded, not reported.

A restore step also needed correcting: restoring *every* GIL `.pyd` re-introduced old-ABI copies
(scipy 1.16) into freshly upgraded packages (scipy 1.18). The fix was to drop any `cp314` file
whose same-named `cp314t` twin exists — 324 removed.

### 6.5.2 F9 — the hot path, without changing a single learned number

`record_outcome()` took one process-wide `RLock`, and inside it did
`from CORE.worm_registry import WORM_REGISTRY` — an import plus a foreign subsystem's dict
access, held while every other worm's outcome waited.

Implemented as **key striping** rather than LongAdder-style per-thread counters. Per-thread
accumulators would make the Q-updates order-dependent, i.e. *different*; striping keeps exactly
one authoritative record per `nature:worm` mutated under exactly one lock, so every learned value
is bit-identical while unrelated worms stop contending. Supporting changes:

- the outcome ring (append-only, never read-modify-write — the true LongAdder case) is striped
  across 8 rings; every read merges, re-sorts and re-caps to `_OUTCOME_EVENTS_MAX`, so the public
  bound and the single-threaded depth are unchanged;
- the reflex arc now runs *outside* the stripe (it only needed `consec_fail` and `last_at`
  captured under it);
- `_SCARS` was mutated from the hot path and read by `q_order()`/views **with no lock at all** —
  survivable only because those writes happened to sit inside the global ledger lock. It has an
  explicit `_SCAR_LOCK` now.

Deadlock-freedom rests on one invariant, documented in the source: *holding any Q stripe implies
holding every homeostat stripe.* New `tests/test_spine_mesh_ledger_striping.py` (14 tests) proves
the values against the recurrence re-derived independently, proves no update is lost across 8
threads on disjoint keys, and drives readers against writers to prove the ordering.

### 6.5.3 The HTML view was silently dropping the route telemetry

`graphify-out/mesh_gephi_interactive.html` is the only interactive view of the mesh, and
`collect_q_edges()` ran a generic `split(":", 1)` over every ledger key. A learned route key
`route:windows>mesh` therefore became an edge from `nature:route` to `windows>mesh` — **neither of
which is a node**. vis.js drops edges with unknown endpoints without a word, so the routing the
mesh began learning in §6.2 was absent from the graph, while the page rendered and the generator
printed success.

Fixed: routes get their own collector and node type, and `resolve_edge_endpoints()` guarantees
every endpoint is a node, so a future key shape cannot re-introduce the hole. The generator emits
a sidecar manifest carrying `unresolved_edges`, and exposes `window.__mesh` so a browser can be
asked what it actually built.

Verification is `tools/verify_mesh_html.py` — headless Chrome over **raw CDP**. Playwright could
not be used at first because both of its entry points import `greenlet`; with greenlet's cp314t
wheel now installed that objection is gone, but raw CDP needs only `websocket-client` (already
present), so verification still adds no native dependency.

Result on the live artifact: **255 nodes, 89 edges, 0 unresolved, 0 console errors, 1 route edge
drawn.** The check has teeth — a negative control (`test_verifier_rejects_a_dangling_edge`)
injects the exact old defect and asserts the harness fails and names it.

Two things the browser check caught that nothing else would have:

- my own `improvedLayout: false` was placed at the top level; vis.js requires
  `layout.improvedLayout` and reported the invalid option as a **console error** — which is why
  console errors are now failures rather than a printed count;
- vis.js had been logging, on every single load, that it *could not position the network* at 255
  nodes. Permanent noise, fixed by moving the flag rather than muting it.

### 6.5.4 The live monitors — where the board and the system disagree

Four wallboards, all working and drivable with `--once`:

| Board | Entry point | Covers |
|---|---|---|
| Azazael | `scripts/live_monitor.py` | learning loop: EVO/META/STEER/TRAIN, 15 tracks |
| Ex Machina | `scripts/exmachina_live_monitor.py` | epistemic organs: 10 judged + 7 operators |
| AOA | `src/AOA/aoa_monitor.py` | 9 arms, milestones, Kali toolchain, bench |
| Lilith | `scripts/lilith_live_monitor.py` | xenomorph hive + 8 mesh natures |

**The finding that matters: Lilith's verdict line was a hardcoded literal.** It read
`OK: hive live, %s, G: up, no failures/24h` — with `role` the only variable. It *asserted* "hive
live" and "G: up" rather than deriving them. Underneath it, the frame showed all seven lifecycle
worms at `0/0 last=-- reg=0`: the hive had not executed once in 24 hours and the board said OK.

Worse, the liveness check keyed on `mesh["xenomorph"]["last"]` — the xenomorph **nature**, which
holds 8 worms including `RedQueenWorm` — so one unrelated worm running kept the verdict green
while the seven worms the section is *about* sat idle.

That is the same shape as everything else in this document: the signal was collected, and the
conclusion was written by hand next to it. Fixed — the verdict now measures liveness on exactly
the worms it displays, distinguishes *idle* from *partial*, and prints the values it read:

```
ALERT: hive idle: 0 of 7 lifecycle worms executed in 24h
```

Second: **the Azazael board printed `8 adapters import-ok`** for a count of exported `*Arm` names
obtained by `dir()`. The `import arms` failure path stored `_AOA_IMPORT["error"]` and **nothing
ever read it** — so a failed import rendered as `0 … import-ok`, or as a stale count labelled as
verified. It now says `8 arm classes exported` and surfaces the failure when there is one. (The
AOA board reports **9 registered arms**; the two boards were never measuring the same thing while
using language that reads as the same fact.)

Third, smaller: Lilith alone lacked `--no-color`, so the only board covering the hive could not be
driven headlessly or diffed without ANSI noise. Added.

**Not yet reconciled** — carried forward honestly rather than guessed at:

- Ex Machina prints `FUNNEL attempts 36 passes 10 promoted 62` — **more promotions than
  attempts** — and `VIGIL wealth 2305380417.64`. Both look like counters accumulated over a wider
  window than the one they are printed beside, or a ratio/sum confusion. Unverified.
- Azazael's `LOOPS evolution 1231.9m` (20.5 h) while Lilith and Ex Machina report ~20 min
  freshness for the same machine. One is measuring a different loop, or a stale artifact.
- AOA's `DETAIL … py3.14.6 no-GIL` — the interpreter is **3.14.7**. The string is not in
  `aoa_monitor.py`, so it is a cached probe result presented as current.
- The worm count read **225** at 11:16 and **223** at 11:47 the same day, with a registry that has
  since been stable across three consecutive runs. Not attributed.
- `reg=0` on every hive row is a **spawn count**, not registration — all 7 *are* registered, under
  cat `xenomorph`. Read as registration it looks like a fleet failure; it is not. The label is
  ambiguous and should be spelled out.

The monitors are the part of this system most likely to be believed without checking, which is
precisely why a hardcoded verdict line is the worst defect found in four passes.
## 6.6 Fifth pass — a *hybrid* interpreter stack (2026-09-14)

### 6.6.1 The real shape of the environment defect

Section 6.5.1 recorded three "incidents" (`greenlet`, `numpy`, `faiss` built for
the GIL and loaded by a free-threaded process). Measuring the whole stack showed
they are one structural problem, and it is worse than three packages.

```
.../Programs/Python/Python314/python.exe       ->  .cp314-win_amd64.pyd
.../Programs/Python/Python314/python3.14t.exe  ->  .cp314t-win_amd64.pyd
both resolve to ..../Python314/Lib/site-packages
```

The two interpreters **share one `site-packages`** and each recognises only its
own ABI suffix (`_imp.extension_suffixes()` confirms: FT looks for
`.cp314t-win_amd64.pyd`, GIL for `.cp314-win_amd64.pyd`). pip installs exactly
one build per package and *uninstalls the other*. So installing with either
interpreter can silently destroy the other's build, and **`pip list` shows the
same single healthy version either way**. At the start of this pass, 27 of 48
probed packages failed to import under 3.14t.

Two subclass failures, both invisible to `pip list`:

1. **Wrong-ABI binaries** — the extension simply is not found (`ModuleNotFoundError`),
   or found and faults.
2. **Hard crashes** — a GIL-built extension loaded by 3.14t can fault at C level.
   A segfault cannot be caught, which is why the documented
   `faiss → numpy → stdlib` fail-open chain never fired: the process dies before
   any handler runs. This also means **no `try/except` can guard it** — the
   runtime must be checked *before* the import.

### 6.6.2 Also measured: the environment's own inconsistencies

- `numpy` had been left **cp314-only**, so the *mandated* 3.14t interpreter could
  not import numpy at all. (`pip list` said `numpy 2.5.3`. Nothing was wrong with
  the version; the *binary* was for the other interpreter.)
- `pydantic-core 2.49.0` against `pydantic` requiring `==2.46.4` — a version
  skew introduced by installing ABI-specific wheels, which broke
  `openai → pydantic → pydantic_core` and with it the whole inference stack.
- `starlette 0.37.2` violated **both** `fastapi>=0.46.0` and `streamlit>=0.40.0`.
- `protobuf`'s abi3 `google._upb._message` **segfaults** under 3.14t. protobuf
  ships a pure-Python wheel for the same version; pip under 3.14t resolves to
  it. The pure wheel is correct on both interpreters, only slower — the right
  trade for a package on every import path.

### 6.6.3 The hybrid

Suffixes are distinct, so both builds can **coexist** in one directory and each
interpreter picks its own. For any package whose both-ABI wheels are the same
version, "all packages work" means: install the free-threaded build and overlay
the GIL build's compiled files next to it. Neither interpreter is sacrificed.

| tier | meaning | packages |
|---|---|---|
| `dual` | both ABIs at one version → install + overlay | numpy, scipy, pandas, scikit-learn, statsmodels, sympy, networkx, safetensors, xgboost, lightgbm, pyarrow, h5py, msgpack, ormsgpack, pydantic-core, MarkupSafe, rpds-py, lxml, PyYAML, cryptography, psutil, wrapt, regex, websockets, pillow, kiwisolver, contourpy, fonttools, matplotlib, pyopencl |
| `pure` | ABI-independent wheel, serves both | protobuf, plotly, tf2onnx |
| `ft-priority` | one ABI, but the builds' **untagged** DLLs differ → cannot share a directory; FT kept (mandated runtime) | torch, llvmlite, openvino |
| `gil-only` | no `cp314t` build exists upstream | numba, mygrad, onnxruntime, pywin32, psycopg2-binary, tokenizers, ray, orjson |
| unavailable | **no Python 3.14 wheel at all** | tensorflow, pygame |

The non-obvious rule, learned by breaking it: a tagged `.pyd` loads against the
**untagged** DLLs beside it (`libarrow.dll`, `torch/lib/*.dll`,
`llvmlite/binding/llvmlite.dll`). Those carry no ABI tag, so each wheel ships its
own, and overlaying `libarrow.dll` from the GIL wheel leaves the free-threaded
`lib.cp314t-win_amd64.pyd` linked against a GIL runtime — a bare segfault with
*both* ABI sets nominally present. The installer therefore overlays only files
whose *name* carries an ABI tag, and aborts the overlay entirely (keeping FT)
when untagged binaries differ in content between the two builds.

### 6.6.4 Result

| measure | before | after |
|---|---|---|
| 3.14t stack probe | 42/58, 1 critical failing | **55/68, all critical healthy** |
| packages importable on **both** interpreters | 3 | **30** |
| relevant test suites (mesh, ledger, registry, telemetry, HTML, architect) | 1 flaky | **158 passed, 0 failed** |

FT-critical set now clean: numpy, scipy, pandas, scikit-learn, **torch**, faiss,
protobuf, pydantic, lxml, psutil, cryptography, PIL, matplotlib, h5py, pyarrow.

### 6.6.5 Honest limits (not fixable by installing anything)

`tensorflow` (imported by 11 files) and `pygame` publish **no wheel for Python
3.14 at any version**, and `numba`/`mygrad`/`onnxruntime`/`pywin32`/`psycopg2`/
`tokenizers`/`ray` publish **no `cp314t` build**. numba's cp314t wheel does
exist and still faults, so mygrad — its dependent — cannot run under 3.14t
either. These are upstream gaps, recorded rather than papered over.

Because a fault cannot be caught, the three mygrad consumers
(`tests/autodiff_skills_check.py`, `tests/benchmark_autodiff_modes.py`,
`tests/test_optimizers_convergence.py`) now check
`sysconfig.get_config_var("Py_GIL_DISABLED")` and skip with an explicit message
**before** importing mygrad, instead of taking the interpreter down. Their
docstrings previously claimed mygrad 2.3.0 "on Python 3.14t free-threading";
that claim is superseded by this measurement and the guard says so.

### 6.6.6 Tools and reproduction

- `tools/install_dual_abi.py` — the hybrid installer. Resolves both ABIs for a
  pinned version, picks the tier, installs with the interpreter that can accept
  the wheel, overlays safely, detects conflicts, rolls back deterministically,
  and can verify both interpreters (`--verify`). Prints the tier per package.
- `tools/hybrid_stack_manifest.txt` — the pinned, tier-annotated package set.
- `tools/verify_python_stack.py` — imports the stack **one module per
  subprocess** (the only way to attribute a crash) and distinguishes
  `IMPORT-ERROR` from `CRASH`.

```bash
FT=.../Python314/python3.14t.exe
$FT tools/install_dual_abi.py --manifest tools/hybrid_stack_manifest.txt
$FT tools/install_dual_abi.py --manifest tools/hybrid_stack_manifest.txt --verify
$FT tools/verify_python_stack.py --all --json /tmp/stack.json
```

### 6.6.7 Regression found and fixed by the sweep

The wider sweep exposed a **flaky assertion in this session's own test**:
`test_ring_merges_across_threads_and_stays_capped` wrote 4 × 80 = 320 events
against a 200-entry cap and asserted every contributor survived. Above the cap
the ring keeps the newest N **by design**, so when one thread's block finished
first its whole contribution could legitimately age out — the test passed alone
and failed under load. It now writes exactly `_OUTCOME_EVENTS_MAX` events (so
"every contributor survives" follows from the contract) and a second test
covers overflow explicitly: the bound applies to the **merged** view, not per
shard, and the newest event must never be the one dropped.
## 6.7 Sixth pass — the four monitors, and the data underneath them

The monitors are the part of this system most likely to be **believed without
being checked**, so they were audited as claims rather than as code. Three of
the four carried defects of a single shape: *a claim that does not follow from
the data beneath it*. The fourth turned out to be the reference implementation
for avoiding exactly that.

### 6.7.1 Lilith — a verdict that was a literal

The header verdict asserted the hive was live. It was **a hardcoded literal**,
not a derivation: it stayed "live" regardless of what the HIVE section below it
reported. Worse, when it *was* wired to something it read the whole
`xenomorph` **nature** (8 worms, including `RedQueenWorm`), so one unrelated
worm running produced "live" while all seven lifecycle worms the section
actually displays were idle.

Also fixed: the `reg=` column was a **spawn count**, not a registration count.
All seven worms are registered; `reg=0` therefore read as a fleet registration
failure. It is now `spawns=` with an explicit legend on the frame.

```
before:  (verdict asserted liveness regardless of the rows beneath it)
         OvomorphWorm   0/0  last=--  reg=0
after:   ALERT: hive idle: 0 of 7 lifecycle worms executed in 24h
         OvomorphWorm   0/0  last=--  spawns=0
         (spawns = this process's spawn count, NOT registration; all 7 are registered)
```

### 6.7.2 Azazael — three claims that did not reconcile

* **Arm count.** `dir(arms)` only sees what `arms/__init__` re-exports, so
  `KaliArm` — defined, registered, running, listed by the AOA board — was
  reported as *unexported*. Counting moved to an AST read of the source.
* **The WORMGA board** was labelled `WORMS`, so `WORMS SYS 100%` sat next to
  the panel's own `SRV DOWN` line. Worse, the row had **no age**: it is a
  fitness leaderboard, now `(WORMGA eval, 22h old)`.
* **An unconditional "Training is live" verdict** printed on the same screen as
  the panel's own `STALE ... check Task Scheduler` line. The verdict is now
  derived from the freshness rows.

**One of these was my own regression.** My first arm-count fix globbed only
`arms/*_arm.py` and then explicitly skipped `support_arms.py` — which holds four
registered arms (`PamsArm`, `PerformanceMonitorArm`, `LlamaServerArm`,
`AgentSelectorArm`). It reported *5* arm classes while the AOA board listed *9*
arms, so two panels disagreed about the same subsystem. The skip was mine, the
disagreement was real, and it is now pinned by a test that recomputes the count
from the tree independently.

```
before:  AOA   ... import-ok
         WORMS SYS 100% ...  (no age)
         Verdict: Training is live
after:   AOA   9 arm classes defined (8 re-exported)  not in arms/__init__: kali_arm
                ms v1.1.0 x6  newest 76d  bench 19d ago eve14mdl
         WBOARD SYS 100% ...  (WORMGA eval, 22h old)
         Verdict: Training is stalled (every cycle stale): 4 loop(s) stale
```

### 6.7.3 AOA — a literal ladder, an age-less count, and a zero that was not a zero

* `SESS` printed the literal `INIT>DISCOVERY>INITIALIZE>READY`, so it claimed
  `READY` **even when init failed**. It is now derived from `init_results`
  (`READY` / `DEGRADED`).
* `AOA_MILESTONE.json` had **no producer at all** — only two readers — and was
  **75.7 days old** while the panel read as "now", because the count carried no
  age.
* A **missing** `~/.aoa/sessions` directory rendered as `sessions 0 on disk`.
  An unreadable number is not a zero. Nothing had ever written there.

```
before:  SESS  INIT>DISCOVERY>INITIALIZE>READY  ms-session aoa-sess-002
               6 milestones   sessions 0 on disk
after:   SESS  phase READY  sessions 1 on disk  ms-session aoa-sess-002
               6 milestones (newest 75.7d old)
```

### 6.7.4 EX MACHINA — the reference behaviour

No correctness fix was needed. It was already age-aware, and it already
documented the rule the other three were violating:

> *"Absent files are omitted rather than reported as infinitely old: a
> subsystem that was never wired is not the same as one that stopped."*

It also carries two signed notes recording earlier repairs of this same class
(`logs/morph_history.jsonl` and `proteus_allocator.json`: paths *no producer
writes*), which is the lesson the other three panels had not yet learned. Its
absent-artifact rule is now pinned by a test so it cannot regress.

### 6.7.5 The deeper finding: three artifacts had no producer

Fixing the panels exposed why their numbers had drifted: **the files were
never being written.**

| artifact | producer before | state found |
|---|---|---|
| `src/AOA/AOA_MILESTONE.json` | **none** (2 readers only) | hand-authored 2026-06-30, 75.7 d stale |
| `src/AOA/benchmark_data.json` | **none** | hand-authored, baseline dated 2026-08-27 |
| `~/.aoa/sessions/` | none called | directory did not exist |

Measured drift in `AOA_MILESTONE.json` (every descriptive claim):

| field | recorded | live |
|---|---|---|
| `adapter_arms` | 8 | **9** (`KaliArm` added, never recorded) |
| `arm_registry.py` | 220 lines | 246 |
| `event_bus.py` | 120 lines | 98 |
| `session_manager.py` | 230 lines | 212 |
| `router.py` | 210 lines | 374 |
| `aoa_cli.py` | 180 lines (**path gone**) | 568 (moved `core/` → `cli/`) |

`benchmark_data.json` still dated the machine as Python **3.14.6** and reported
`total_worms: 108` against a live **226**.

### 6.7.6 The rule that makes repopulation safe

`src/AOA/refresh_aoa_data.py` now repopulates from the live registry, and it
draws one line deliberately:

* **Descriptive** fields (arm roster, module paths + line counts, live machine
  readings) are refreshed from the live system every run.
* **Baseline / threshold** fields (`eve` t/s floors, and the worm count that
  drift is measured *against*) are **never rewritten**. Overwriting a baseline
  with the value it measures manufactures agreement instead of reporting it —
  the same failure, one level down. Instead the tool stamps when the baseline
  was taken (`_meta.baseline_date`) and records the live value *beside* it
  (`azazael.live_worm_count: 226` next to `total_worms: 108`), so the file
  itself now shows the drift rather than hiding it.
* **Recorded history** (`session.milestones`) is preserved verbatim. A
  descriptive refresh must not delete a real work log.

Run `python src/AOA/refresh_aoa_data.py --check` to report drift without
writing; without `--check` it rewrites in place and records a real session
through the project's own `SessionManager`.

### 6.7.7 Three defects introduced and caught inside this pass

Recorded because each is the same failure the pass was fixing:

1. **The refresh tool read zeros from an uninitialised registry.** An
   uninitialised arm answers `execute()` with `cpu_percent: 0` rather than
   raising, so the first `--check` run wanted to write `0` over every live
   machine reading — a *plausible* number, which is worse than an obvious one.
   Fixed by initialising the registry once, and by refusing to record a
   non-positive reading: a zero from a counter is not evidence.
2. **`_age_txt(age)` double-subtracted.** The helper takes an *epoch* and
   subtracts `time.time()` itself; handing it a duration produced `20635d` for
   a 76-day-old file. Fixed, and the epoch contract is now tested directly.
3. **File mtime is not the age of recorded history.** Once the artifacts *have*
   a producer, mtime moves on every refresh — so after the first successful
   run both panels announced "0d ago" for a 76-day-old milestone log and an
   18-day-old baseline. Both now age the artifact by the dates *inside* it
   (newest milestone timestamp; `_meta.baseline_date`).

### 6.7.8 A real weakness that fell out of (3)

Fixing the last one surfaced a genuine product bug rather than a test artefact:
`_AOA_IMPORT` was guarded by `if not _AOA_IMPORT`, which cached whatever the
**first** call happened to see — including a resolution against a different
directory, or a transient `ImportError` — and then reported that number for the
rest of the process. A stale claim wearing a live label.

The cache is now keyed on the directory it resolved against, and a failed
import is retried rather than latched. Pinned by a test that calls
`aoa_status()` against two different trees in one process and requires the
count to be re-derived.

### 6.7.9 Verification

```
tests/test_monitor_verdict_accuracy.py   19 tests (Lilith + Azazael + AOA line + cache)
tests/test_aoa_data_freshness.py         24 tests (AOA panel + refresh + EX MACHINA)
150 passed  across tests/{monitor_verdict_accuracy, aoa_data_freshness,
             monitor_artifact_paths, mesh_html_view, spine_mesh_ledger_striping,
             worm_registry_cache_freshness, spine_mesh, spine_mesh_telemetry}.py
```

Every panel line quoted above in the "after" form was read from a live
`--once` run under the mandated `python3.14t`, not from the source.

### 6.7.10 Open items

* `~/.aoa/sessions/` now holds **one** genuine session (this refresh). It grows
  only when something calls `SessionManager.save_session`; wiring it into the
  benchmark workflow would make it a real audit trail rather than a snapshot.
* `refresh_aoa_data.py` is **not** on a schedule. If it is not run, these files
  go stale again — which is at least now *visible*, since both panels age them
  by their own dates.
* AOA's HTML generators (`build.py`, `gen_html.py`) still read the machine and
  `eve` blocks from `benchmark_data.json`; they inherit the fixed descriptive
  values, but the baseline/threshold split is only enforced at the data layer.
### 6.7.11 Caught by re-running the suite: the view was *stale*, not wrong

Repopulating the AOA data changed live mesh state, and the wider suite then
failed `test_learned_routes_are_visible_in_the_view`. That test is one written
in this session, and it fired on a real inconsistency:

```
ledger (spine_state.json q_weights)      view (mesh_gephi_interactive.json)
route:windows>mesh        -0.500         drawn: route:windows>mesh  (1 edge)
route:windows>windows     +0.700
route:windows>g_archive   +0.975
route:windows>wsl2-ubuntu +0.700
route:windows>wsl2-kali   +0.700
```

Five learned routes in the ledger, one drawn. **The pipeline was not at
fault** — `resolve_edge_endpoints` already creates placeholder nodes for
non-nature hops, so the view *can* draw all five. The artifacts were simply
generated at 11:22, when only one route had been learned. The view was a
faithful picture of an older mesh, presented as the current one.

Regenerated (`--all`); the drawn set is now complete:

```
route:windows>mesh         -> nature:mesh          ROUTE Q=-0.500
route:windows>windows      -> hop:windows          ROUTE Q=+0.700
route:windows>g_archive    -> hop:g_archive        ROUTE Q=+0.975
route:windows>wsl2-ubuntu  -> hop:wsl2-ubuntu      ROUTE Q=+0.700
route:windows>wsl2-kali    -> hop:wsl2-kali        ROUTE Q=+0.700
17 implicit endpoints      (4 tests pass)
```

Two reporting gaps surfaced while doing it, both the same shape:

* **A default pipeline run rewrote the GEXF and silently left the interactive
  view stale** — and it is the interactive view the monitors read. It now
  prints `7. Interactive view NOT rewritten (last generated 2026-09-14 13:21)
  -- pass --html (or --all) to refresh the browser view`.
* **SVG rendering is skipped** (`graphviz dot` not on PATH). It reports
  `skipped` rather than failing quietly, which is correct behaviour, but it is
  an unwired output — tracked below.

The lesson this adds to the pass: *a stale artifact is not a wrong one, and
that is exactly why it is dangerous.* Nothing in the view was incorrect; it
was simply older than the ledger, with nothing on it saying so.
## 6.8 Seventh pass — the three follow-ups, and the sweep

### 6.8.1 Keeping the AOA artifacts fresh (scheduled)

`scripts/refresh_oa_data.bat` follows the repo's existing `schtasks` launcher
convention (documented `/Create` line in the header, `PY` resolution with
fallback, output appended to `logs/refresh_oa_data.log` so a silent failure is
visible). It runs `refresh_oa_data.py` on `python3.14t`, which is safe to
repeat: descriptive fields are recomputed, baselines are only *stamped*, and
recorded milestone history is left alone.

```
schtasks /Create /F /SC HOURLY /MO 6 /TN "AOA Data Refresh" ^
  /TR "C:\Users\clint\azazael\scripts\refresh_oa_data.bat"
```

### 6.8.2 `~/.aoa/sessions/` is now a real audit trail

`SessionManager.save_session()` had **no caller anywhere in the tree**, which is
why the directory did not exist and the panel correctly said `sessions DIR
MISSING`. `test_benchmark_workflow.py` now opens a session, records an init
milestone per arm **including FAILED ones**, records every workflow step, closes
with the verdict, and saves — reporting a save failure rather than swallowing it.

Recording a *duration* required a small fix underneath: the router stamped
`started_at` / `completed_at` on each step but did not return them, so every
step would have been logged as `0.0 ms`, which reads as *instant* rather than
*unmeasured*. Those two keys are now returned.

Measured result — a genuine, dated audit trail:

```
3fb63c8a.json  status=completed  name=AOA Benchmark Verification
  milestones=19  duration_total=4881.2ms
  perfmon  get_metrics   101.7ms
  llama    get_status   4748.9ms   <-- 97.3% of the whole run
  pams     record_event    4.6ms
```

### 6.8.3 The sweep — two real defects, and two non-findings

Swept every status-displaying script for the three shapes (hardcoded claims,
values with no age, missing rendered as zero).

**Real, and material — `threatmon.healthy` was a *presence* check:**

```python
healthy = feed_rows > 0        # before
```

A feed job that stops leaves the row count at its last value, so the tier
reports healthy on frozen data, indefinitely. Measured on this machine:

| feed file | age |
|---|---|
| `threat_triage_v2.json` | 14.2 h |
| `urlscan_corrob.json` | 13.6 h |
| `bcc_baseline.json` | 14.6 h |

The schedule is **hourly**; `feed_rows` was 19074; `healthy` was **True**. The
snapshot also stamped `timestamp` with the *read* time, dating 14-hour-old data
as "now". Now: `feed_at` / `feed_age_s` on the snapshot (the data's own age),
`healthy` requires freshness (`FEED_STALE_AFTER_S = 6 h`), and a
`threat-stalefeed` alert names the age and the limit.

```
before:  feed=19074 online=10 decided=20 ...              (healthy, 14h-old data)
after:   feed=19074 (13.6h old STALE) online=10 ... healthy=False
           ALERT threat-stalefeed: feed data is 13.6h old (limit 6h) -- the pull job has stalled
```

**Real, smaller — `berks_monitor.py` swallowed its own purpose.** The spine
writes that turn downtime into training signal were wrapped in
`except Exception: pass`, so the signal could stop accumulating while every run
still exited 0. Failures are now counted and reported:

```
WARN spine ledger not updated for N of M outcomes (...) -- downtime is NOT becoming training signal
```

**Non-findings, recorded as checked rather than "fixed":**

* `exmachina_health_alert.py` reads a state file with no age reference, but
  computes health *live* and uses the file only for transition detection, where
  staleness is harmless.
* `berks_monitor.py` and `threat_monitor.py` print values measured in-process,
  not read from a store.

**And the cheapest finding from the architecture audit** (§2.1 of
`AOA_ARCHITECTURE_AUDIT_2026-09-14.md`): `EventBus.publish()` dispatched
subscribers under a bare `except: pass`, so a raising consumer was silently
never delivered to. Delivery isolation is preserved, but failures are now
counted (`callback_error_count`, with event type, pattern, callback and
exception) and the workflow prints them. One test caught a flaw in the fix
itself: truncating `Class.method` from the right kept the class name and threw
away the identifying method, so the leaf is now preserved.

### 6.8.4 Verification

```
199 passed  across tests/{aoa_session_audit, threat_feed_freshness,
            aoa_data_freshness, monitor_verdict_accuracy, monitor_artifact_paths,
            mesh_html_view, spine_mesh, spine_mesh_ledger_striping,
            spine_mesh_telemetry, spine_mesh_wiring, spine_mesh_architect,
            worm_registry_cache_freshness}.py

benchmark workflow: 9/9 steps, 0 failures, EventBus subscriber errors: 0
```

### 6.8.5 Architecture follow-on

The AOA audit is written up separately in
`AOA_ARCHITECTURE_AUDIT_2026-09-14.md`. Headline: the Quartet framing is sound
but no longer descriptive — the four quartet arms expose 22 capabilities while
the five "support" arms expose 49, and 226 worms sit behind just four
capability names. The structural finding is that the **mesh routes adaptively
on learned Q while the AOA router executes a static DAG with zero references to
it** (`route:windows>g_archive` q=+0.975, 6/0 vs `route:windows>mesh` q=−0.955,
0/5). The proposed v2 keeps the four pillars and re-founds the orchestrator on
one routing plane over typed edges.
