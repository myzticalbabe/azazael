# Neural Loop Reengineering — 2026-09-21

**What this session was:** the system's learning was scheduled as a flat table of
fifteen independent jobs. It was reengineered into a single causal loop over the
neural substrate, run live for an hour, and every defect that surfaced was fixed.
This is the record of what was built, what broke, and what each fix rests on.

---

## 1. The architectural defect

Learning was a **job table**, not a loop:

```python
JOBS = { "spine": (3600, ...), "wiring": (1800, ...), "hyperopt": (3600, ...),
         "dream": (900, ...), "evolution": (900, ...), "train": (900, ...), ... }
```

Each entry had its own interval, each raced for one execution slot, and the
winner was chosen by *most overdue, ties broken alphabetically*. Nothing made one
job's **output** the next job's **input**. So a fire could run fifteen jobs,
change nothing durable, and report success — and "ran" and "learned" were the
same word in every log.

A neural loop is a causal sequence with data dependencies:

```
load → perceive → credit → plasticity → route → act → grade
     → consolidate → prune → grow → l1 → l2 → persist → verify
```

`route` cannot run without the weights `plasticity` wrote; `grade` cannot run
without the executions `act` produced; `verify` is the closure that makes
"nothing changed" a **failure**.

**Built:** `src/CORE/neural_loop.py` (+ `scripts/neural_loop.py`,
`scripts/neural_loop_monitor.py`, `tests/test_neural_loop.py`).

---

## 2. The four findings that decided the outcome

### 2.1 The loop was learning and then throwing it away

Run 1 moved the table **56 → 264 edges** in memory and wrote 232 graded outcomes.
A fresh process then read **56 edges**. Nothing called `save_spine_state()` — even
though the spine's own cycle documents persistence as step 4 of its flow and does
it. `verify` compared in-memory state to in-memory state, so it declared success.

→ added the **`persist`** stage before `verify`, and made `verify` read the
**disk** independently. A cycle whose learning is not on disk has not closed.

### 2.2 The reward signal is a prior where there is no evidence

`spawn_credit` reports a Wilson lower bound over 234 organs: 41 distinct values,
spread 0.1228, clustered 0.94–0.98. Writing that **absolute level** into the
weights pulls every organ toward the population mean — homogenising the table
into exactly the failure the Q-table's own history records ("31 edges collapsed
to 3 distinct values, 25 at exactly +0.0909").

→ `plasticity` writes the **advantage** (`reward − mean`), so the update changes
sign with the organ's standing, and refuses any organ below `MIN_EVIDENCE = 3`
individual observations, because a bound on one observation is not a measurement
of that organ.

**Measured result:** the table went 56 → 264 edges with **distinct 12 → 59** —
more discriminating, not less.

### 2.3 A dead holder's lock could only be released by the process it blocked

`~/.azazael/graph_refresh.running` was written at 12:06 by a refresh whose worker
had died. At 12:38 it still read "in flight", because the guard trusts the
marker's **mtime** for three hours and the only thing that clears it is
`graph_refresh_no_llm.py`'s `finally:` — *the very script the guard refuses to
launch*. The chain re-fired every 60 seconds for half an hour, running its whole
job set and changing nothing.

→ the marker now records the **child's pid**, and the guard checks that the owner
is alive before honouring it. Six cases verified: dead pid, live pid, inside the
grace window, the legacy time-only format, past the deadline, and no marker.

### 2.4 The gate promoted genomes on noise

With `L1_MARGIN = 0.0`, three genomes were promoted on paired deltas of
`+0.000555`, `+0.000272` and `+0.000111` while the credit signal's population
spread was **0.1228** — winning on 0.09% of the spread. A streak does not filter
that: the search offers twelve fresh children per cycle, so a handful of
near-ties just above the incumbent assembles a streak out of noise.

→ `L1_MARGIN` is now a **minimum effect size** (default 0.002, added to the
hyperopt `PARAM_SPACE` so L2 calibrates it). After the fix, `l1` reports
`best_delta=None` — no candidate clears the floor.

---

## 3. Defects in my own code, and how each surfaced

Every one of these was found by *running* something, not by reading it. They are
recorded because the pattern is the point: the failure mode of this work is a
change that looks right and reports success.

| # | Defect | Found by |
|---|---|---|
| 1 | `getattr(reg, "nature")` on registry entries that are **dicts** with `category` → resolved **0 of 234** organs, so the loop could not key a single write | running the loop |
| 2 | Guessed `spine.opportunity_patterns()`; it is `MorphogenesisWorm.morph()` | running the loop |
| 3 | `persist`/`verify` judged "changed" on **edge count**, which cannot see a nudge to an existing edge | the monitor's first cycle |
| 4 | Wrote a 7.5e-9 update, called it `changed`, and `verify` (tolerance 1e-6) failed it for "a change the weights deny" — **two tolerances for one question** | a unit test |
| 5 | `l2` called `step(apply_promotion=False)`, which still appends a **lineage row** — a durable write inside a "dry run" | the dry-run contract test |
| 6 | `prune` reported `blocked` on every cycle even when there was nothing to forget, training a reader to ignore the blocked column | reading the 7-cycle report |
| 7 | I claimed the Q-table was "empty, 0 edges" after reading the **private dict**; the getter restores 56. My measurement was wrong, not the system | self-correction |
| 8 | The monitor compared edge counts and produced a false `NOT-DURABLE` on a real, persisted update | running the monitor |
| 9 | A process-kill filter matched its own shell and killed itself | running the command |

---

## 4. Verified live results

**One full applying cycle** (46–51 s, every stage doing its real job):

```
perceive     observed=234  with_evidence=234
credit       232 natures resolved, 2 unresolved (SYSTEMZ, CUSTOM -- not registered)
plasticity   232 weight updates   (baseline 0.9517, spread 0.1228)
route        232 organs ordered
act          ok=232 rc=0          (fleet executed; was 231/1 before the NucleiBridge fix)
grade        new_outcome_rows=232 (independent re-read of the tap, not the executor's word)
consolidate  dream cycle rc=0
grow         patterns=0
l1           promoted=False (margin floor rejects ~1e-4 candidates)
l2           objective=0.65, canary checked
persist      edges_on_disk 56 -> 264
verify       edges 56->264, distinct 12->59, sig matched on disk
```

**A fresh process afterwards:** `memory=264, disk=264, distinct=59`.

**The monitored hour** (55 min, cycle every 240 s) — **12 cycles, all `OK`**:

```
cycle  1  OK  sig 81bd3a5a..->9b7eab8c..   50s
cycle  2  OK  sig 9b7eab8c..->23cc44a3..   45s
cycle  3  OK  sig 23cc44a3..->3fde62dd..   47s
cycle  4  OK  sig 3fde62dd..->951975d4..   48s
cycle  5  OK  sig 951975d4..->04400107..   46s
cycle  6  OK  sig 04400107..->fa247dae..   46s
cycle  7  OK  sig fa247dae..->4c236970..   53s
cycle  8  OK  sig 4c236970..->ede00487..   55s
cycle  9  OK  sig ede00487..->a974744e..   54s
cycle 10  OK  sig a974744e..->c079655e..   53s
cycle 11  OK  sig 97b5ce61..->21caaaa0..   50s
cycle 12  OK  sig 21caaaa0..->10ffc0c4..   49s
```

Every cycle moved the weight VALUES and persisted them. The edge count stayed at
264 throughout, which is exactly why the count-based durability check had to be
replaced: on this evidence, a count check would have called twelve real cycles
of learning a no-op.

**Concurrency, on the real schedule — both paths verified:**

| fire | collided with | `Last Result` | meaning |
|---|---|---|---|
| 13:33:01 | monitor cycle 4 | **3** | `BUSY` — refused to start a second cycle |
| 14:03:01 | nothing | **0** | ran, wrote `state/neural_loop_report.json`, verdict `OK` |

The single-flight lock both blocks when contended and permits when free. Without
it, two processes read-modify-write the same brain state and the second save
silently reverts the first while **both logs report success**.

**Cycle ledger:** 18 rows, 16 `OK`, 2 `INERT` (both from before the verdict fix,
when an applying cycle that changed nothing could still read as healthy).

**Schedule:** `Azazael-NeuralLoop`, every 30 minutes, on-battery allowed,
20-minute execution limit, report to `state/neural_loop_report.json`. The old
`Azazael-Chain` (60-second cron) is **Disabled**.

---

## 5. Exit codes are the interface

```
0  OK     -- at least one stage changed durable state
0  DRY    -- a dry run: no writes attempted (expected)
1  FAIL   -- a stage failed, or claimed a change the weights deny
2  INERT  -- an APPLY cycle ran and changed NOTHING
3  BUSY   -- another cycle holds the lock
```

`INERT` is non-zero on purpose. It is the specific outcome this work exists to
name: an applying cycle that ran everything and moved no weight. A caller that
treats exit 0 as "learning happened" is now correct.

---

## 6. What is still true

- **`prune` cannot write.** `spine_registry` exposes no public Q-edge prune;
  the stage reports candidates and refuses to delete. A magnitude-only prune
  would be actively wrong here, since the edges `plasticity` creates start near
  zero by construction.
- **`consolidate` runs the dream cycle but the loop does not verify a delta
  from it.** It is a real subsystem invocation with `changed` derived from the
  weights, so a dream that changes nothing is not counted as progress — but it
  is not yet proven to reinforce anything.
- **`grow` found 0 patterns.** The opportunity trigger reported "skipped 2
  chosen name(s) absent from the registry (bad records, not capability gaps)",
  which is the fix from the previous session working — the phantom gaps are
  gone, and so is the signal they were mistaken for.
- **The fleet executor is the long pole** (~40 s of a ~46 s cycle).
- **`tests/test_spine_mesh.py::test_spine_cycle_drives_synapse_layer_with_real_data`
  fails in its suite and passes alone.** Established as pre-existing and
  unrelated by A/B rather than assumed: it fails identically with and without
  this session's new test file in the run, and it still fails with **no loop
  running at all**. Both arms of that A/B had the monitor active, so a third run
  was done after the window closed to rule out contention with the loop's live
  writes — it failed there too, which is what makes "plain intra-suite
  order-dependence" the supported reading.
