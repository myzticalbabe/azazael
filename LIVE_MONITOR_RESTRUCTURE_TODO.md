# Live Monitor Restructure — TODO

**Opened:** 2026-09-15
**Trigger:** the neural-mesh work in `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-15.md`
(spine brainstem, fabric natures, quorum ledger, HLC, morphogenesis pen) moved the
system well past what every live monitor was written against. The monitors now
describe an architecture that no longer exists, and the two fastest-moving tiers —
**ML** and **RL** — have no monitor at all.

**Rule for this file:** no monitor may display a hard-coded constant that the mesh
computes. Every number on a monitor must be read from a live source
(`spine_registry`, `NATURE_DEFINITIONS`, or a `state/*.json` artifact). Where a value
cannot be read, the monitor says `unknown` — it does not guess.

---

## 1. Investigation — what exists, and what is stale

### 1.1 Monitor inventory

| Monitor | Size | Reads | Verdict |
|---|---|---|---|
| `tools/render_monitors.py` → `dashboard/monitor_{azazael,exmachina,lilith}.html` | 37 KB | `spine_registry` (Q, scars, homeostat, spine_map, events, policy journal) + `worm_registry` + `state/organ_*.json` | **Only mesh-aware monitor. Missing all of passes 2–3.** |
| `scripts/live_monitor.py` | 107 KB | evolution DB, AOA, run100, QD grid, SB3 | **Zero mesh awareness.** Predates the mesh. |
| `scripts/exmachina_live_monitor.py` | 67 KB | Ex Machina organs | Epistemic tier only. |
| `scripts/lilith_live_monitor.py` | 20 KB | Lilith hive | Queen only. |
| `scripts/live_monitor_web.py` | 9 KB | serves a monitor over HTTP | Transport only. |
| `scripts/monitor_learning.py`, `scripts/berks_monitor.py`, `scripts/threat_monitor.py` | 9–15 KB | learning / BCC / threat | Narrow, single-purpose. |
| `src/CORE/dashboard.py` | 34 KB | — | **Zero mesh awareness** (no reference to `spine_registry`, `NATURE`, or `fabric`). |
| `tools/gephi_mesh_pipeline.py` | 26 KB | `NATURE_DEFINITIONS`, `spine_registry` | Graph export, not a live monitor. Holds the only correct `NATURE_COLORS`. |

### 1.2 Stale claims currently on screen (each is a live bug)

`monitor_lilith.html` and `monitor_azazael.html` print constants that the mesh now
computes, so they contradict the running system:

| On screen | Reality after the mesh work |
|---|---|
| `PROBE_NATURES: mesh, synapse, immune · limit: 4` | Probe coverage was widened to consensus / federated / servemesh / engram (audit #10). |
| `Lease 300s` | The leader lease is now **enforced** with expiry + term comparison, not just written (audit #7). |
| `Fallback bare > wsl2 > windows > kali` | `Lilith.FULL_ENVS` is keyed on the canonical 5-way env id (`wsl2-ubuntu` / `wsl2-kali`) (audit #4). |
| `quorum: 2/3 vote · min failures: 3` | Quorum is now counted over **distinct envs** from the persisting, gossiped `_QUARANTINE_VOTES` ledger (audit #1). A local 2/3 vote can no longer quarantine anything. |
| "No peers discovered yet" | Peers and the whole cross-env layer now live in `get_fabric_view()` / `get_quarantine_votes()` / `get_clock_skew_ms()` — all unread by every monitor. |

### 1.3 Capability gaps (state that exists but no monitor reads)

`spine_registry` exposes, and nothing renders:

- `get_fabric_view()` — the fabric natures' operational memory (13 worms: routing
  table, elected leader + term, shard catalogue, endpoint loads, forks, partitions).
- `get_quarantine_votes()` — the cross-env quarantine ledger (who voted, how many envs).
- `get_clock_skew_ms()` — the HLC skew diagnostic. **The mesh could not measure clock
  skew before this session**, and still nothing shows it.
- `get_anomaly_model()` / `get_anomaly_model_meta()` — the shared, signed anomaly model
  and which env trained it.
- `get_route_usage()` — route-usage telemetry.
- `get_q_updates()` — **the single most important missing readout.** `get_q_weight()`
  returns `0.0` for both "never tried" and "measured neutral", so a *starved* worm
  looks identical to a *settled* one on the current monitor. `get_q_updates()`
  separates them (documented in the function's own docstring as added 2026-09-14 for
  exactly this reason) and no monitor calls it.

State artifacts with **no monitor**: `state/mesh_cycle.json` (per-nature
worms/ok/fail/ms), `state/cycle_telemetry.jsonl` (cpu/mem/db/duration history).

### 1.4 The two missing tiers

**No ML monitor and no RL monitor exist.** The signal is real and already on disk,
it is simply unrendered:

| Tier | Live artifacts |
|---|---|
| **ML** | `tensor_genome.json` (gene values, usefulness, ρ, direction, bounds, samples), `tensor_genome.spec.json`, `tensor_genome.prune_report.json`, `tensor_model.json`, `tensor_gate_ab.json` (gate vs surrogate shipment quality, false promotions, decision), `qd_archive.json` (grid cells, fitness, behaviour), `mutation_summary.json` (mutants/killed/score/survivors), `budget_policy.json` (floor/value/ceiling per budget), `fitness_oracle.json` |
| **RL** | `evolved_rl_params.json` (learning_rate, epsilon, discount, epsilon_decay + fitness + holdout + oracle + SPRT llr + wins + margin), `grpo_policy.json` (β, lr, fitness, run id), `qd_archive.json` behaviour spread, `spine_registry.get_q_weights()` / `get_q_updates()` (the RL brainstem), `NeuralPipeline` lifecycle + DeadLetterQueue, `EvolutionEngine` (NSGA-II Pareto front) |

**Delivered in this pass:** §3 items 1–2 (both monitors). Everything else is open.

---

## 2. Colour convention (shared, so monitors read as one system)

`tools/gephi_mesh_pipeline.py` already owns the canonical nature palette. The two new
tiers get their own, chosen to match their actual semantics rather than for variety:

| Tier | Accent | Meaning |
|---|---|---|
| **ML** | cyan `#56d4dd` → teal `#1abc9c` | data / features / inference. A cold, steady palette: ML state should look *calm* unless the gate fails. |
| **RL** | purple `#bc8cff` → magenta `#ff7eb3`, amber `#d29922` for exploration | reward, gradient, exploration. Warm and high-contrast: RL is the volatile tier. |

Semantic states (already in the shared CSS): green = pass/healthy, amber = advisory /
warn, red = fail/blocked, purple = RL/reward, cyan = ML/data.

---

## 3. TODO

### P0 — new monitors (this pass)

- [x] **1. `dashboard/monitor_ml.html`** — ML tier. Gene genome, QD archive, fitness
      oracle, tensor gate A/B, mutation score, budget policy, model artefacts.
- [x] **2. `dashboard/monitor_rl.html`** — RL tier. Evolved params + bounds, holdout
      margin, oracle, SPRT LLR, GRPO policy, behaviour spread, Q brainstem (weights
      **and** update counts), NeuralPipeline/DLQ.

### P1 — make the existing monitors truthful  ✅ done this pass

- [x] **3. Kill the hard-coded constants.** Every row in §1.2 now reads live:
      probe coverage from `RedQueenWorm.PROBE_NATURES` (and `PROBE_LIMIT`,
      `QUARANTINE_MIN_FAILURES`, `QUARANTINE_FAIL_RATE`), lease from
      `Lilith.LEASE_SECONDS` + `FULL_ENVS` + `FALLBACK_ORDER` + the actual live
      lease, quorum from the `get_quarantine_votes()` ledger. The header badge
      no longer *asserts* `Health: ok` either — it is computed. The Kademlia
      card no longer says "No peers discovered yet" while the env beacons know
      about peers, and Queen role is derived from the lease (now the authority)
      instead of a stale `spine_mapped` event.
- [x] **4. Add the fabric panel** — `Fabric Operational State (#7)`: providers with
      persisted state, never-published list, elected leader + term, shard
      catalogue, endpoint loads. Plus `Cross-Env Quarantine Ledger` (decided /
      findings / voting envs) and `Cycle Telemetry` (`state/mesh_cycle.json`,
      which had no monitor at all).
- [x] **5. Show the pull counts.** The brainstem card now reports
      *measured / starved / seeded / settled-neutral* — and the starved rule is
      the spine's own (`weight == 0.0 && pulls == 0`), shared with the RL
      monitor so the two cannot disagree about what "starved" means.
- [x] **6. Clock-health card.** Accepted-peer skew, stamps observed, refusals,
      worst refused offset, drift bound, local node and current stamp. Building
      it immediately exposed three real defects — see §5.

### P2 — consolidate  ✅ done this pass

- [x] **7. One palette module** — `tools/monitor_theme.py`. `NATURE_COLORS` is
      imported from `gephi_mesh_pipeline.py` (with a local fallback) so a nature
      is the same colour on the graph and on every dashboard; an unmapped nature
      is visibly grey rather than a plausible invented hue.
- [x] **8. One data-collection module** — `tools/monitor_data.py`. Collectors,
      staleness helpers, the live mesh facts, and the fabric/quarantine/clock/Q
      readers all live there; `render_monitors.py` and `render_ml_rl_monitors.py`
      both import from it.
- [x] **9. Decide `src/CORE/dashboard.py`'s fate — kept and rebased.** It gained
      `_mesh_report()` / `render_mesh()` / `--mesh`, and mesh is folded into
      `get_report()`, so the text dashboard and the rendered HTML now read the same
      `spine_registry` facts instead of the text one going silent about the mesh.
- [x] **10. Mesh panel in `scripts/live_monitor.py`.** A `MESH` row from
      `state/mesh_cycle.json` (ok/fail, nature count, failing natures, retried,
      cpu/mem/db) with the `state/cycle_telemetry.jsonl` cpu tail drawn as a
      sparkline, plus a `mesh` row in `data["freshness"]` so its age reaches the
      `STALE` alert line and the one-line verdict — a panel alone would have left
      the verdict still able to say the system was healthy. Aged by the `at`
      *inside* the artifact, never by file mtime. 8 tests in
      `tests/test_monitor_verdict_accuracy.py::TestMeshPanelIsTruthful`.

      This immediately paid off: the board now reads
      `LOOPS ... mesh 2786.3m` and `STALE evolution, metacog/steer, dreaming,
      training, mesh >15 min`. The fleet cycle had been dead for ~46 h and the
      wallboard had said nothing, because it had no mesh row at all.

### P3 — liveness  ✅ done this pass

- [x] **11. Auto-refresh.** Every rendered monitor now carries
      `<meta http-equiv="refresh" content="60">` plus a `rendered <time>` stamp in
      the footer, so a page left open on a second screen stays current and a
      *screenshot* of one is still identifiable as one.
- [x] **12. Staleness warning.** `monitor_data.source_line()` puts the source
      artifact, its age and a `STALE` badge on every card that reads from disk
      (the `state/*.json` tiers), and `monitor_data.state_age()` dates a file by
      mtime so a file with no timestamp inside it is still dated. Verified live:
      `mesh_cycle.json` renders `46h ago` with a STALE badge rather than looking
      current.

### P4 — deferred (needs a design decision, not a patch)

- [x] **13.** Federated-aggregation hardening (audit §4 item 8) — **done**:
      dimensional validation (a contribution of the wrong shape is rejected, not
      silently averaged), staleness weighting (an old contribution counts for less),
      a trimmed/median style Byzantine-robust aggregate (a single extreme peer can
      no longer drag the result), and round ids so a replayed round is detectable.
      Covered by `tests/test_federated_robustness.py`. The federated card stays
      *advisory* until secure aggregation exists — the aggregate is now robust to a
      bad peer, not private from one.
- [ ] **14.** Safe path from `morph_policy.json` / `state/proteus_morph.jsonl` into a
      projection monitor (cost + noise make this a design question).

---

## 4. What building the monitors uncovered (fixed)

The two P0 monitors were built first, and building them against real data found
three defects that no test had caught. All three are fixed and covered.

### 4.1 `get_q_updates()` had no bulk form, and the miss was silent

The RL monitor's first cut called `sp.get_q_updates()` with no arguments. The
function is per-key (`get_q_updates(nature, worm)`), so it raised `TypeError` —
and the blanket `except Exception` around the spine read swallowed it. The card
then rendered **"0 measured"** for a populated brainstem *while naming
`spine_registry` as its source*. That is precisely the silent-degradation
failure this module's own docstring forbids, committed by an early version of
the module itself.

* Fixed: added `spine_registry.get_q_update_counts()` (bulk, read-only copy).
* Fixed: the card no longer degrades silently — a failed spine read renders a
  red `spine read failed: <TypeError…>` row and a `Q read failed` badge, and
  claims no counts.
* Found by: reading the rendered HTML, not by running the tests.

### 4.2 The Q-table was three tables and only one was persisted (real regression)

The most consequential find of the pass. `_Q_WEIGHTS`, `_Q_UPDATE_COUNTS` and
`_Q_VARIANCE` are all learned state; only `_Q_WEIGHTS` was ever saved, restored
or gossiped. So on **every restart**:

* `get_q_updates()` returned 0 for every key. Its own docstring says it exists
  so a selector can tell a *proven-neutral* arm (weight 0.0, pulls > 0) from a
  *never-tried* one (both 0) and apply a minimum-pull quota — with the counts
  gone, the quota re-explored proven arms forever and treated settled-neutral
  arms as untried. That is the cold-start collapse the counter was added to
  prevent, reintroduced at every boot.
* `_Q_VARIANCE` reset, so adaptive alpha (Welford) silently fell back to its
  `0.25` default and the learning-rate schedule restarted.

`spine_reset()` had the mirror bug: it cleared the weights and left the counts
and variance, producing a Q-table **empty of values and full of evidence** —
every arm instantly "proven".

* Fixed: `save_spine_state` / `load_spine_state` / `_merge_disk_state` now carry
  both extra tables (counts take MAX, matching the existing monotone-counter
  rule; variance is adopted only when absent).
* Fixed: counts travel in the signed gossip payload and merge by MAX, so a Q
  value adopted from a peer does not render as starved.
* Fixed: `spine_reset()` clears all three tables.
* Covered by `tests/test_spine_brainstem_persistence.py` (8 tests).
* Verified live: the RL brainstem card went from `0 measured` to
  `66 measured · 0 starved` once the round-trip was real.

### 4.3 Pre-existing test failures (unrelated to the mesh, fixed for completeness)

| Suite | Failure | Cause | Fix |
|---|---|---|---|
| `test_dlq.py` (5) | `FailingWorm` expected to fail | The fixture had **no methods at all**; the design deliberately returns `standby` for a healthy worm with no safe zero-arg entry point. The DLQ itself was fine — a worm whose `execute()` raises still populates it. | Gave the fixture a raising `execute()`, which is what "always fails" has to mean now. |
| `test_config_and_breaker.py` (2) | `python_version == "3.13"`, `output_dir == "Desktop/…"`, `monitor.timeout == 45` | Stale expectations: 3.14 free-threading migration, builds moved to the `G:` archive, and the asserted values (`45`/`3`/`defense`) belong to the **`security`** yaml block, not `monitor`. | Repinned against `CORE/config.py` and `azazael.yaml`, and added the `security` block plus a no-block fallback assertion so the test now proves the values are per-nature. |
| `test_circuit_breaker_integration.py` | `force_trip` missing | Test called an operator method that was never implemented. | Implemented in `CORE/circuit_breaker.py` (earlier pass). |

### 4.4 Verification (this pass)

| Check | Result |
|---|---|
| `test_spine_brainstem_persistence.py` (new, 8 tests) | ✅ 8/8 |
| `test_mesh_clock_convergence.py` (18 tests) | ✅ 18/18 |
| `test_dlq.py` + `test_config_and_breaker.py` | ✅ 61 passed |
| Mesh/spine suite (10 files) | ✅ 230 passed, 1 skipped |
| Registry integrity | ✅ 226 worms / 35 categories, idempotent, no generated worm registered |
| `dashboard/monitor_ml.html` | ✅ renders live (genome, QD, oracle, gate, mutation, budgets) |
| `dashboard/monitor_rl.html` | ✅ renders live (params, holdout, SPRT, GRPO, behaviour, brainstem) |

---

## 5. What the P1–P3 pass uncovered (fixed)

Making the existing monitors truthful meant reading state nothing had ever read,
and each of those reads found a defect. All four are fixed and covered.

### 5.1 The clock reported a refused stamp as skew (audit §5 item 3, now closed)

The new Clock Health card printed, on first render:

```
+30682668731722ms | peer clock skew | 24 observed | 24 refused
```

A refused stamp was recorded as `_max_remote_physical` **before** the drift
guard, so `skew_ms()` reported the very era the guard exists to reject — ~972
years, forever, indistinguishable from a real reading. The store behind it held
98 year-2999 stamps (`032472162000000-04631-windows`).

* `observe()` now keeps two separate signals: `skew_ms()` (accepted peers only)
  and `rejected_skew_ms()` (the worst refused stamp). The card shows both.
* Two further defects surfaced while proving it:
  * **`normalize_stamp()` guessed the epoch unit** (multiplied every numeric
    input by 1000), so a millisecond epoch became a wider number and, because
    the packed field is fixed-width, a stamp `unpack_stamp()` *cannot read*.
    Units are now detected by magnitude. `pack_stamp()` clamps too, so the
    module can no longer emit a stamp it cannot parse.
  * **A poisoned stamp still won merges** — the fabric field merge compared
    stamps with a raw `>`, bypassing the guard, and the guard covered only the
    candidate direction. A year-2999 field stamp beat every correct peer until
    real time reached year 2999. Now: a beyond-drift candidate never wins, and a
    beyond-drift *incumbent* loses to the first trustworthy write, so a poisoned
    record is repaired instead of frozen.
* `spine_registry.purge_implausible_stamps(dry_run=True)` is the opt-in operator
  tool for a store that already holds such stamps (they are harmless once
  refused, but they would ride in every gossip payload forever). It **repairs**
  rather than deletes — a record with no stamp would lose its next merge.
* Covered by `test_mesh_clock_poison.py` (12 tests, written from the real
  values found in the store).

### 5.2 A test suite was writing the developer's live spine store

Found while chasing the poison: `~/.azazael/spine_state.json` contained
synthetic fixtures (`mesh:W0`, `learning:W1`). `_STATE_FILE` isolation was
opt-in **per test file**, so `tests/test_spine_mesh.py` — which records outcomes
and then saves — replaced a live 76-record homeostat with test data.

* Fixed globally in `tests/conftest.py` (`_isolate_spine_state`, autouse),
  matching the existing containment-pen redirect: a test must not be able to
damage the machine it is testing, and "remember to patch this" is not a
  mechanism.
* Verified by hashing the real file around a full run of the offending suite:
  unchanged.
* **Consequence worth knowing:** the real store's accumulated homeostat was
  already overwritten by earlier leaking runs, and `~/.azazael/backups/` holds
  no snapshot of it. Nothing further is recoverable from local backups.

### 5.3 Two monitors disagreed about "starved"

The ML/RL monitor defined it as `weight == 0.0 && pulls == 0`; the mesh monitor
counted every zero-pull key, labelling eight *seeded* arms as starved. Same word,
two meanings, side by side — the exact failure the restructure exists to remove.
Both now use the spine's own definition and report *seeded* separately.

### 5.4 An AOA tripwire fired, deliberately updated

`test_the_machine_really_has_no_durable_aoa_route_keys_yet` asserted that AOA
routing write-backs were **not** durable. The store now holds two `aoa_route:`
keys, so routing learning *is* being saved. As that test's own docstring asks,
it was inverted rather than deleted (now
`test_the_machine_now_has_durable_aoa_route_keys`), so the opposite drift is
caught too. The AOA probe already read durability from the snapshot, so the
panel was correct — only the pinned finding had gone stale.

### 5.5 Verification (P1–P3 pass)

| Check | Result |
|---|---|
| `test_mesh_clock_poison.py` (new, 12 tests) | ✅ 12/12 |
| `test_mesh_clock_convergence.py` (updated) | ✅ 18/18 |
| Mesh/spine/AOA/DLQ/config suite (11 files) | ✅ 250 passed, 1 skipped |
| Elastic-routing + ledger-striping | ✅ 54 passed |
| Registry integrity | ✅ 226 worms / 35 categories, idempotent |
| Real store untouched by the suite | ✅ verified by hash before/after |
| All five monitors render | ✅ azazael, exmachina, lilith, ml, rl |
| Every shown constant is a live read | ✅ `PROBE_NATURES: mesh, synapse, immune, consensus, federated, servemesh, engram`; `quorum = 2 distinct envs`; `lease 300s` from `LEASE_SECONDS` |
| Starved rule agrees across monitors | ✅ both: 76 keys / 68 measured / 0 starved / 8 seeded |
