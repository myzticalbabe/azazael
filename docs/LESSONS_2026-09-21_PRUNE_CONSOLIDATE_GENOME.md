# Lessons — prune, consolidate, genome audit (2026-09-21, round 2)

Follow-on to `LESSONS_2026-09-21_NEURAL_LOOP_REENGINEERING.md`. Three followups
were implemented, all three "widened" into real defects, and the round produced
**two more instances of the same shape**: a component that reports success while
the thing it claims to do does not happen.

The shape, stated once: **a component's report is not evidence about the world.**
Every defect below was found by reading the durable artifact (the state file, the
ledger, the lineage row) instead of the component's return value.

---

## 1. Prune — the stage that deleted nothing, and a cap that did not hold

### Before
`_stage_prune` reported `blocked: "no public Q-edge prune API"` on every cycle,
because `spine_registry` exposed no per-key Q prune. `purge_fixtures` removes
*declared fixture* keys and `cap_q_tables` drops by *capacity*; neither lets a
caller name the edges that should go.

### Fix
`spine_registry.purge_edges(keys, reason, persist, require_no_evidence=True)`.

Two load-bearing safety properties:
- **Evidence gate.** A key with any observed update OR any dream count is
  REFUSED, not removed, and the refusal is reported. "Carries no signal" and "is
  small" are different questions: the edges `plasticity` just created start near
  the neutral value *by construction*, so a magnitude threshold deletes the
  learning it was called after, one cycle after producing it.
- **Tombstone before persist.** Without it the removal is neither durable nor
  observable — the save path folds the disk in before writing, so the next save
  re-adopts every key just deleted.

### Widened into a real defect
`cap_q_tables` dropped keys **without tombstoning**. MEASURED, isolated store:

```
disk before: ['w:0','w:1','w:2','w:3','w:4','w:5']
cap dropped=3 in_memory=3
disk after : ['w:0','w:1','w:2','w:3','w:4','w:5']   <- all six, back
tombstoned: 0
```

A cap that reports `dropped=3` while the table stays at 6 is worse than no cap:
it makes the bound look enforced. Fixed by tombstoning each dropped key —
after the fix, `disk after: ['w:3','w:4','w:5']`, `tombstoned: 3`.

### Honest current state
On the live table: `scanned=264, candidates=0`. **Every one of the 264 edges
carries at least one observed update**, so the evidence gate correctly finds
nothing to forget. The capability is real and the report says "nothing to
forget: every edge carries evidence" — a *true* statement, unlike the old
permanent `blocked`.

---

## 2. Consolidate — the stage that could not have proved a delta

### Before
`_stage_consolidate` ran `dream_cycle.py` and returned the script's exit code.
Two independent problems:

1. `dream_cycle.py` was the one cycle script in the repo that did **not** call
   `save_spine_state()`. Siblings (`gossip_round`, `night_shift`, `evolve_loop`)
   all do.
2. The dream cycle's policy bridge does **not** reach `dream_reinforce()`. The
   only caller is `ConsolidationWorm.consolidate()`, and nothing invoked it.

MEASURED consequence: the live dream-count table was **empty** — 0 keys, 0
counts — for the entire life of the loop.

### Fix
- `ConsolidationWorm.consolidate()` now persists when it reinforced, so every
  caller gets durability (including the fleet's `execute()`).
- `dream_cycle.py` persists, following the sibling idiom.
- `_stage_consolidate` now runs **both** the dream cycle and the offline Q
  channel, and reads the delta from two places that are not the worm's report:
  the dream-count table and the weights **on disk**.

### Widened into a defect in my own code
The first version saved when the worm's report said `reinforced > 0` — the
self-report shape the loop exists to stop trusting. A test with a worm that
reports `reinforced=5` and writes nothing caught it: the stage saved an unchanged
table and reported `changed=True`. Now it reads the evidence *before* deciding to
persist, and persists on the measured delta.

### Widened again: the channel is structurally unreachable
Live: `dreams=3, reinforced=0`. Probing the real `DreamingModule` output:

```
type=strategy_exploration  source=None              strategies=['conservative']  conf=0.112
type=pattern_grounded      source='pattern_memory'  conf=1.0
```

`consolidate()` requires `s.get("worm") or s.get("target")`. **Neither shape
names an organ.** `source` is a memory store, and no worm in the registry is
called `pattern_memory`. This is the exact shape of the `NucleiBridge` defect: a
component registered into a caller that asks for a field it cannot supply.

The wrong fix would be to map `source` into the Q key — that injects a fabricated
organ named `pattern_memory` into the brainstem, and a fabricated row is worse
than an unreachable channel. The fix taken instead is **visibility**: skips are
counted by reason, so every cycle now reports

```
skipped: {'no_organ_target': 9}
```

instead of a silent `reinforced: 0`. An inert channel and a healthy quiet channel
are no longer the same reading — which is the whole point.

---

## 3. Genome audit — "adapting" vs "maintaining a file"

`l1` reports a genome, a generation and a fitness. None of that says the search
is going anywhere. `CORE/wiring_audit.py` + `scripts/genome_adaptation_audit.py`
answer three questions with evidence.

Live result:

```
verdict: ADAPTING_ONE_AXIS
  fingerprint  wg-0bc2e0eaa0e15eb0   generation 3   parent wg-2b67d3a7640ca415
  paired_delta 0.000111              origin drop:SensoryRelayWorm
  axes live ['active']   dormant ['priority','budget_ms','cooldown_s']
  l1 rows=33  promotions=3  rejections=30
     14  no candidate beat the incumbent
      9  awaiting 3 consecutive wins (have 1)
      7  awaiting 3 consecutive wins (have 2)
  effector: registry=232  demoted_organs=24  natures_reordered=10  first-slot changed=3
```

So: the generation **does** advance, the effector **does** change real dispatch
order (24 organs demoted, 10 of 34 natures reordered) — and the search is
nonetheless **one-dimensional**. `priority`, `budget_ms` and `cooldown_s` are all
empty/zero, so every candidate has competed on "which organ to demote" while the
genome advertises four axes.

### Why it measures the effector through production code
The A/B resolves `WIRING_PROMOTED_PATH` to a missing file for the "without"
arm, so **the production ranking runs on both sides**. Re-implementing the
ranking key in the audit was the alternative and it is worse: two copies of one
formula is how telemetry comes to disagree with the thing it describes.

### The ledger had to be told apart first
`decide_execution_order` writes one `spawn_selected` row per worm. Calling it 464
times for an audit would inject phantom decisions into the one ledger that exists
to join choices to executions. Hence `record: bool = True` — a hypothetical
ranking must not appear as a decision that was taken, and the default keeps every
existing caller unchanged.

While doing this: `_append_lineage` in `wiring_cycle.py` sits in a `finally`, so a
dry run writes a lineage row too — and the row had **no field** distinguishing it
from a real cycle, so "how many cycles has this search had?" counted dry runs as
cycles. Rows now carry `apply`, and the audit reports
`applied_rows / dry_rows / unknown_apply_rows` (pre-field rows are reported as
unknown, never guessed at).

---

## 4. A fourth defect, found because the report was unparseable

The `--json` output had a log line in front of it. Checking the cause found L2
unable to write at all:

```
write failed hyperparams.json (unsupported operand type(s) for +: 'WindowsPath' and 'str')
promote FAILED to write C:\Users\clint\azazael\state\hyperopt\hyperparams.json
```

`_write_json` did `path + ".tmp"`, but `hyperopt.PARAMS_JSON` is a `Path`. The
read path had been made Path-tolerant; the write path had not. The exception was
caught and logged, so nothing raised — and `state/hyperopt/` held the lineage
ledger and `hyperparams.json.prev.json` but **not `hyperparams.json`**: L2 had
never once written a promotion.

After the fix, verified: `gen: 1`, `fingerprint hp-5c25bc9986afe483`,
`baseline_objective 0.65`, promoted `spine.cooldown_max_scale 4.0 -> 2.5`.

Same class as the 232 lost weight updates, one layer out.

---

## 5. One unexplained observation, recorded as such

A full apply cycle reported `act` failing with **rc=3221225477** (0xC0000005,
`STATUS_ACCESS_VIOLATION`) — a native crash, not a Python exception — after
writing 162 outcome rows. It has **not** reproduced: three subsequent runs were
clean (`run_mesh_cycle.py` directly ×2 → `ok=232 fail=0 rc=0`; a full cycle →
`verdict OK, act ok=232 rc=0`).

It is recorded rather than dismissed because it is the free-threading crash
class, and because pretending it was fixed would be a claim without evidence. If
it recurs, the discriminator is already in place: the stage reports the raw
`rc` and the executor's last `cycle ... ok=` summary line, so a native crash is
distinguishable from a Python failure.

---

## 6. One test failure, identified rather than waved away

`tests/test_spine_mesh.py` reports 1-2 failures in-suite (intermittent: 2, then
1, then 1, then 2 across four runs) and passes alone. Not caused by this round's
changes -- and the mechanism is now known rather than assumed.

Instrumented read-only with a throwaway pytest plugin (no source edits):

```
[DBG] EARLY RETURN: {'success': True, 'skipped': 'cycle_already_running_global',
                     'cycles': 0}  busy_locked=False global_locked=True
```

The cycle did not run. `SpineCycleWorm.run_cycle()` has a **process-global**
cross-instance gate, `_GLOBAL_CYCLE_GATE`, which correctly refuses a concurrent
cycle. It fires here because `tests/test_spine_mesh.py:120` starts **8 worker
threads**, and their overlap still holds the gate when
`test_spine_cycle_drives_synapse_layer_with_real_data` asserts a single cycle's
`synapse_routing`. The test is not concurrency-aware; the guard is behaving as
designed and is released in a `finally`.

Two things worth noting beyond "pre-existing":

* The refusal is **visible** (`skipped: cycle_already_running_global`, and both
  lock states were readable from outside), which is what made this diagnosable
  in minutes instead of being an unattributable red.
* `test_homeostat_apply_respects_bounds` joins it intermittently with the same
  signature, so the likely fix is `test_spine_mesh.py` joining its 8 threads
  before later tests assert on shared state -- a test-file change, deliberately
  not made here, because a green suite bought by loosening assertions is the
  failure mode this round is about.

## Verification

- `tests/test_learning_closure.py` — 20 tests: the evidence gate (refuses an
  observed key, refuses a dreamed-only key, overrides only on request), the
  durable cap (`dropped == 3` **and** 3 on disk after the next save), the
  prune stage's three outcomes, the consolidation delta (proved from the count
  table; a worm's claim not believed; the channel's failure surfacing), and the
  audit (dormant axes, dry-vs-applied history, a real reorder with **zero**
  ledger writes, `MAINTENANCE` vs `NO_GENOME`, `record=False`).
- Regression guard for the `Path` write bug in `tests/test_hyperopt.py`.
- Targeted suites: 104 passed (loop, wiring, closure, hyperopt, chain); 79
  passed + 2 skipped (spine tombstone/persistence/visibility/mesh-wiring, dream
  policy, wiring audit, startup-warm); 46 passed (brainstem playing field).
- `tests/test_spine_mesh.py`: 60 passed, 1 skipped, 1 intermittent failure
  identified above (not from this round).
- The full `tests/` sweep is 3546 tests and was not run to completion; the
  suites covering every file this round touched were run instead.
- Real apply cycle: `verdict OK`, `act ok=232 fail=0`, `grade` 232 new outcome
  rows, `persist` + `verify` changed with `durable: true`.

## The pattern, one line each

| Reported | Actually |
|---|---|
| `prune: blocked` forever | no prune API existed; when added, the neighbouring cap re-adopted its own drops |
| `consolidate: ok` | the offline channel had never been invoked; dream counts were empty |
| `reinforced: 0` | 9 suggestions skipped for a field the producer never emits |
| `l1: promoted/fitness` | one axis of four searched; three dimensions never expressed |
| `l2: promote-write-failed` | the durable parameter file had never existed |
