---
name: azazael-mesh-resilience-primitives
description: The four mesh resilience primitives built from the 2026-09-16 per-function
  audit and brainstem playing-field work -- fencing tokens, the silent-failure
  ledger, liveness obligations, and store tombstones. Covers where each lives, the
  invariant it enforces, which paths it must cover (write paths, not just merge
  paths), and the method that produced them.
metadata:
  category: neural-mesh
  project: azazael
  auto_load: false
  version: 1.0.0
  created: 2026-09-16
---

# Azazael Mesh Resilience Primitives

Four primitives, each promoted from a *recurring defect shape* rather than written
from a design. The rule that produced them: **a fix applied N times is a fix that
will be forgotten N times** -- when the same defect appears at more than one call
site, the correction belongs in a primitive, not in N call sites.

Every one of the four defects these came from was **silent**: no traceback, no log
line, no red monitor. Each reported success without establishing the precondition
for it. That shared signature, not the individual bugs, is what the primitives
address.

---

## 1. `fencing.py` -- fencing tokens for in-process shared state

**File:** `src/CORE/WORMS/expansion/fencing.py`

Kleppmann fencing tokens, reapplied from distributed locks to **in-process shared
state**. A writer mints a monotonic token before starting work, works *unlocked*,
and only the commit path writes; a stale token cannot commit. A zombie writer's
result becomes unrepresentable rather than merely discouraged.

**Deliberately process-wide**, not per-instance: the defect it was built for was
two *instances* of the same engine racing, which an instance lock cannot see.

Never blocks and never raises. `fence_report()` exposes contention as a trend, and
is one of only two places in the mesh that record a *negative* (see section 3).

## 2. `silence.py` -- the silent-failure ledger

**File:** `src/CORE/WORMS/expansion/silence.py`

A bare `pass` in an exception handler destroys a **measurement**: "the fabric
healed" and "the fabric failed to load its learning every start for a week" are
byte-identical from the outside. 118 such handlers existed in the mesh.

Two moves beyond a plain counter:

* **signature clustering is the alarm.** A rising count is a flaky peer; a **new
  exception type** is an unpredicted failure mode. The count alone cannot tell
  them apart.
* **budgets make "graceful" checkable.** `budget=0` states that this failure is a
  fault, not a grace.

Bounded at 24 signatures and 512 tags.

## 3. `liveness.py` -- obligations with deadlines

**File:** `src/CORE/WORMS/expansion/liveness.py`

All four defects from the mesh audit were events that did **not** happen, and every
existing monitor was occurrence-driven. More occurrence telemetry is *structurally
incapable* of catching them. The missing primitive is a **liveness obligation**: a
named expectation with a deadline, minted by the code that should cause it and
discharged when it fires.

Three kinds of miss: `unfulfilled`, `silent`, `never_beaten`. `observable` is
reported **beside** `healthy`, because green with nothing declared is UNKNOWN, not
an all-clear.

**`overdue()` is idempotent on purpose.** A first implementation *consumed* each
miss, so a monitor polling every 60s saw a fault once and health afterwards --
output that decays is indistinguishable from a system that repaired itself, which
is the exact defect class this primitive exists to remove.

## 4. Store tombstones -- making deletion representable

**File:** `src/CORE/spine_registry.py` (`_PURGED_KEYS`, `purge_fixtures`,
`audit_state`, `purged_blocked_writes`)

The spine store is **monotone**: every read merges and every write merges first, so
it can say "this key has a value" and cannot say "this key is gone". Observed, not
theorised: `purge_fixtures()` removed 56 entries and the next save restored all 14
fixture keys. Deletion was not buggy, it was *unrepresentable*.

A tombstone records the removal as a fact. The hard part is not the tombstone, it
is its **scope**:

| Path class | What a guard there achieves |
|---|---|
| merge (disk load, gossip merge) | holds against the filesystem and against peers |
| **write** (`record_outcome`, the Q kernel) | holds against **this process** |

Merge-only enforcement was the first implementation, and it left a live
`record_outcome` able to re-create a purged key and the next save to write it back
out. Both classes are required.

Guards are placed at **choke points, one per table** -- `_q_observe_unlocked` for Q
(all three reinforce forms reduce to it, so `dream_reinforce` is covered without a
guard of its own) and `record_outcome` for the homeostat. Refused writes are
**counted** (`purged_blocked_writes()`), never swallowed: a tombstone that keeps
having to refuse writes is a fixture still being exercised, which is a finding
about the caller.

---

## Method -- the five steps that produced these

1. **Measure the artifact before reading the code.** For any subsystem with a
   persisted table, read the table first. It accumulates the consequences of every
   past decision; the code shows only the current one. (How the Q table was caught
   saturated at 38% and *flat* at once, from the same root cause.)
2. **Calibrate the instrument before acting on its reading.** 4 of 21 audit probes
   were miscalibrated on first run; acting first would have manufactured 13 fake
   "unbounded loop" fixes.
3. **Sort by consequence-if-live, not by count.** `PF02`+`PF04` (1,799 findings)
   were review cost; the 764 findings describing functions the mesh cannot test,
   reach, or see failing produced *every* real defect.
4. **Guard at the narrowest point every violator must cross**, and enumerate the
   paths that can *violate* an invariant rather than the paths that can *propagate* it.
5. **Test the guard by removing it.** Ship the test that disables the predicate and
   shows the defect returning. An assertion that is satisfied by the defect is not a
   test of the fix -- this happened, in this exact body of work: a distinctness
   assertion passed on the broken code, and only reverting the fix surfaced that
   *magnitude*, not distinctness, was the discriminator.

## Documenting corrections

Corrections carry their own provenance. When a canonical figure is superseded, say
what it was and why it moved; a corrected number with no record of its predecessor
is indistinguishable from a number that was always right, and teaches nobody how the
document came to be wrong.

## Related

* `azazael-catalog-reconciliation` -- the internal-contradiction check applied to
  `SKILLS_CATALOG.md` (a document that disagrees with itself is stale regardless of
  what the world says)
* `azazael-worms-core`, `azazael-architecture` -- where these primitives sit in the
  mesh
* `NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md`,
  `NEURAL_MESH_BRAINSTEM_TODO.md` -- the audits that produced them
* `data/training/neural_mesh_consolidation_2026-09-16.jsonl` -- reasoning traces
