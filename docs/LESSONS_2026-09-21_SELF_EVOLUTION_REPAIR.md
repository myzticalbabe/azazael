# LESSONS_2026-09-21: Making the Architecture Able to Learn On Itself

## Executive Summary

The system could not self-evolve, and the reason was not a missing learner. It
was that **the action log and the outcome log described different populations**,
so there was no join to learn from — and **the genotype was four floats with a
declared-closed search space**. This session built the missing half of each: a
causal key (`decision_id`) written by the decider and stamped on outcomes, and a
genotype whose state is the wiring of the whole fleet (L1).

Running the new machinery then found eleven defects **in this session's own
code**, three of which would have actively harmed the system: a latency penalty
that would have starved the busiest components, a fitness term that rewarded
shrinking the fleet, and a scrub predicate that would have tombstoned the
strongest evidence in the store. Every one of those was caught by *executing*
the code against live data, not by reading it.

The unifying rule, recorded below as L1: **a verdict the system cannot later
check is not evidence.** Three separate failures this month were the same
failure — a claim with no independent check behind it.

---

## Part 1 — What was actually wrong

### Lesson 1: The reward was a function of the state, so the oracle equalled a constant

**Discovered:** 2026-09-21, by measuring the RL task rather than reading it.

**Context:** `reward = f(severity)` while the state contained severity. Any policy
that reports the severity it was given scores identically, so the oracle cannot
distinguish policies and the genome cannot move. This is why "installed so many
tools" did not produce learning: the tools were fine, the objective was empty.

**Fix:** the reward is **post-hoc success**, which the state cannot contain at
decision time.

**Rule:** *If the reward can be computed from the state, the learner has nothing
to learn.*

---

### Lesson 2: Two taps, one decision — 13 chosen, 28 executed, overlap 1

**Discovered:** 2026-09-21, live.

```
CHOSEN   worms: 13 | newest 2026-09-20T23:10:45
EXECUTED worms: 28 | newest 2026-09-20T07:34:05
OVERLAP: 1  ['MetaCluster']
```

**Context:** The choice tap was written by `SpawnDiversityEngine`; the outcome tap
by `ClusterWORMZ`/`NATURE_CLUSTERS`. **Nothing joined them**, so 12 of 13 chosen
components had zero outcomes and 27 of 28 executed components were never chosen.
"Widen the telemetry" would not have helped: there was no join to widen.

**Fix:** `new_decision_id()` written by the decider, stamped on every outcome row,
plus `read_decisions()`/`read_outcome_decisions()` and an `attribution_mode`
property that reports `per-decision (causal)` **only** when ids actually match on
both sides — otherwise it stays honestly at `per-worm-type (statistical)`.

**Rule:** *One decision must be recorded twice, by both sides, under a shared key.
Anything else is two logs that resemble a join.*

---

### Lesson 3: 67% of the "which component did we choose" record was unit tests

**Discovered:** 2026-09-21, after scrubbing the *outcome* tap and finding the
*choice* tap still full of names that do not exist.

```
spawn_selected rows: 608
  408 from test fixtures (12 names, 0 registered)
  200 from MetaCluster (the only real component ever chosen)
```

**Context:** `pytest.ini` has `testpaths = tests`, so `src/tests/` runs only via
IDE discovery or a direct invocation — the runs nobody watches. It had **no
conftest**, and a conftest only covers its own directory subtree, so
`src/tests/test_worm_registry.py`'s fixture classes (`FleetOrch`, `NetDiag`,
`DivWorm`, …) called `record_spawn()` into the developer's live store.
`spawn_credit.chosen_but_never_run()` read that tap, and the morphogenesis
opportunity trigger read *that* — so the system was about to manufacture
specialists for twelve components that do not exist.

**Fix:** a **rootdir** `conftest.py` (not a conftest inside `src/tests/`), because
the defect is not "src/tests is special" but "a test directory anywhere is
unprotected".

**Verified:** running the polluting file with the redirect leaves the live store
byte-for-byte unchanged (608/4240 before and after); **without** it the same file
writes 24 rows.

**Rule:** *A test must not be able to write into the store it is testing — and the
protection has to be where tests are collected, not where they are written.*

---

### Lesson 4: An event that exists only on success cannot distinguish "never ran" from "refused"

**Discovered:** 2026-09-21, while chasing what looked like a timing failure.

**Context:** `spine_cycle` was recorded **only** on the success path, at the end of
a cycle. The autonomous heartbeat calls `run_cycle(apply=True)`; its stage-0
proprioception gate refuses outright when the self-image is stale. So **every beat
returned before running a single stage and recorded nothing**, and the worker
logged nothing on a non-success report. A heart that is refused every beat was
indistinguishable from a dead heart: zero events, ever.

**Fix:** `_record_beat(phase, ran, reason, extra)` records a beat **whether or not
it acted**, on every exit path.

**Rule:** *If a signal only appears on success, it cannot answer "is this running" —
which is the first question asked, and the one this project keeps paying for.*

---

### Lesson 5: A ring sized to one cycle holds no history

**Discovered:** 2026-09-21, when a beat that had just been written was missing from
the log.

**Context:** `_SPINE_EVENTS_MAX = 200`, and one observe cycle emits **~200 events**
(175 of them `nature_edge`). The ring evicted the beat that had just been added,
so the fix in Lesson 4 was invisible for the same reason the original defect was.

**Fix:** sized to 5000 (~25 cycles), measured rather than guessed.

**Rule:** *Size a ring buffer against the measured volume of one cycle, not against
a round number.*

---

## Part 2 — Defects this session's own code had (found by running it)

### Lesson 6: A cross-unit comparison inside a metric is a defect, not a penalty

Fleet median duration was **1.89 ms** while `SYSTEMZ` averaged **903× the fleet
median** — because it is the workload. A latency penalty therefore drove the three
busiest, most reliable components to the clamp floor (**−1.000**) and ranked
one-shot probes above them. It would have taught the scheduler to **starve the core
monitors**.

**Fix:** latency is a *drift* question ("is this component slower than **it** used
to be?"), so it became `slow_regression()`; `reward` is success only.

**Rule:** *Comparing the duration of two components doing different work measures
the work, not the component.*

---

### Lesson 7: Sample size must be inside the reward

With raw success, a component that ran **once** and succeeded (1.0) outranked one
with **1236 successes in 1246 runs** (0.992).

**Fix:** the reward is a **confidence lower bound**, so evidence quantity is part
of the score.

**Rule:** *A rate without its denominator is not a measurement.*

---

### Lesson 8: Unobserved units scored as zero reward deleting them

The genome's fitness was a mean over organs, so an organ with no evidence counted
as `0.0` — which made **dropping it a free improvement** (the best candidate in a
live run was exactly "remove a component nobody has measured", Δ = +0.000276).
The genome would have shrunk toward the fifteen components that happen to have
data.

**Fix:** unknown ≠ 0; unmeasured organs are excluded from the mean and reported as
a separate coverage figure.

**Rule:** *If absence of evidence scores as bad evidence, the system will delete
what it has not looked at.*

---

### Lesson 9: Loose pattern matching silently shrinks the fleet

A rule meant to protect infrastructure used the regex `audit`, which also matches
`PortAuditor` — removing a legitimate domain component from the evolvable pool with
no error and no log. **Same disease as `search_space_closed`:** the search space
narrows silently.

**Fix:** the boundary is domain auditors (evolvable) vs loop auditors (not), encoded
explicitly, with tests asserting the legitimate names survive.

**Rule:** *An exclusion rule that cannot log what it excluded is a silent deletion.*

---

### Lesson 10: A principled-looking predicate can delete the best evidence

A scrub mode matching "name is not in the registry" flagged **`SYSTEMZ` — 1246
execution rows, 1236 successful, the busiest and most reliable component** —
because it is registered by a path that does not populate `WORM_REGISTRY`
(`discover_worms()` returns 232 of it). Applying it would have tombstoned the
strongest evidence in the store. It was caught **only because the tool is dry-run
by default**.

**Fix:** "phantom" now means *not registered* **AND** *never executed*; the default
tap for that predicate is the choice tap alone; and an unreadable outcome tap makes
the tool refuse rather than over-match.

**Rule:** *A destructive predicate needs a dry run and a second, independent
condition — and "delete what we cannot explain" is never one.*

---

### Lesson 11: Mutations the objective cannot see are null operations

Two of three mutation operators produced children that scored **identically to their
parents** (Δ exactly `0.0`) because fitness read only the `active` flag. A third of
the search was dead, and it looked like a policy that simply rejected everything.

Related: `priority` was absent from the objective, so the effector's entire
**ordering** dimension was unselectable.

**Fix:** only observable operators are used in the cycle (the excluded ones are
reported), and `ranked_credit` puts priority into the objective.

**Rule:** *If a mutation cannot change the score, it is not a mutation — it is a
random number generator.*

---

### Lesson 12: A diagnostic that names the wrong cause sends the operator to the wrong variable

`JevAdvisor.enabled` is `False` **both** when the kill switch is off **and** when no
key exists, so the CLI reported "`AZAZAEL_JEV_ENABLED` is off" for an **empty API
key**. The operator would have gone to the wrong variable.

The same class appeared twice more this session: a first smoke test read
`credit.by_worm` when the attribute is `credit.rewards` (so "observed = 0"), and an
A/B test of the opportunity trigger **could not discriminate** because a missing
`import os` made *both* arms fail for the author's reason.

**Rule:** *Verify the arm that should pass, before trusting the arm that should
fail.*

---

## Part 3 — Jev (TypeSafe) as a decision source

`~/jev-ultrafast` (Browser Use × TypeSafe) is a browser agent that **chooses
instead of generating**: it asks System One for a finite-choice answer
(`choice` + `confidence` + full `probabilities`) over an enumerated action space.

**Why it fits here, and only here.** Two properties:

1. **It cannot fabricate a candidate.** The action space is ours, so a wrong answer
   is a wrong pick from a known list — never a component that does not exist, which
   is exactly what went wrong in Lesson 3.
2. **Its verdict is gradeable.** Jev's own documentation states the principle this
   whole session is about: *"Independent checks, rather than the model's DONE
   choice, determine whether the demonstrated task succeeded."*

So it is bound as a **proposer whose proposals are scored by measured outcomes**,
never as a reward. Every answer is recorded under a `decision_id`; the outcome tap
grades it; `grade_choices()` reports accuracy — and reports **`None`** (not 0%)
when nothing has executed the advice, because an advisor whose advice was never
acted on has no accuracy.

**Boundaries encoded as code:**

| Boundary | Enforcement |
|---|---|
| Not in the dispatch path | `decide_execution_order` is hot and must never block on a network call; a test asserts `worm_registry.py` does not reference the advisor |
| Never the fitness | fitness stays measured success; the module documents why |
| Cannot invent a component | the response is validated against the offered set (argmax consistency, distribution covers exactly the candidates, finite, sums to 1) |
| Fail-open, visibly | no key / switch off / timeout / HTTP error / malformed answer → `None` **and** a recorded row naming the reason (`unavailable`, `error`, `invalid`, `refused`) |
| No new dependency | `urllib.request`, not `httpx`, so an optional call cannot make importing the fleet depend on a third party |

**Status: blocked on credentials, not on code.** `~/jev-ultrafast/.env` has
`TYPESAFE_API_KEY=` **empty** (verified: key name present, value length 0), so no
live call has been made. The adapter is tested (31 tests, stubbed transport) and its
fail-open path is verified live — the recorded row correctly reads
`outcome=unavailable`. One real request is the remaining step; `scripts/jev_advise.py`
is the entry point.

**The question it will answer** (measured): 232 components registered, 23 with any
evidence, **209 never observed**. Fitness can only select on what has been executed,
so choosing among those 209 is the highest-value decision available.

---

## Part 4 — Environment findings (not code defects)

| Finding | Detail |
|---|---|
| Memory store size | `~/.azazael/memory_store.db` is **426.8 MB** (threshold 400 MB) — the store the cycle reads each beat |
| Heartbeat gate | 5 of 7 artifacts now current; `graphify-out/graph.json` + `GRAPH_REPORT.md` stale by **90 newer sources** |
| Graph rebuild blocker | `graphify update` aborts on `invalid pdf header: b'<!DOC'` / `EOF marker not found`, and warns `skill is from graphify 0.9.55, package is 0.8.8` |
| `fs_hygiene --check` | **10 pre-existing regressions** (`.claude`, `__pycache__`, large graphify/backup files) — none created this session |
| `src/tests/` | One **pre-existing** order-dependent failure (`test_multiple_registrations`), in a directory the normal run never collects |
| `test_spine_mesh.py` | One **pre-existing** order-dependent failure — identical with and without this session's root conftest |

---

## Part 5 — The transferable rule

> **L1: A verdict the system cannot later check is not evidence.**

Three failures this month were the same failure: a claim with no independent check
behind it.

| Claim | Why it could not be checked | Now |
|---|---|---|
| "The policy is learning" | reward ≡ constant, so no policy differed | post-hoc success |
| "Component X was chosen" | choice tap and outcome tap described different populations | shared `decision_id` |
| "The heartbeat is running" | the event existed only on success | a beat is recorded on every path |
| "This organ is unused" | unobserved scored as zero | unknown ≠ 0 |
| "This name is a test artifact" | registry membership alone | not registered **and** never executed |
| "Jev's advice is good" | nothing graded it | outcomes joined by `decision_id`, ungraded reported |

---

## Deliverables

**Created**

| File | Purpose |
|---|---|
| `conftest.py` (rootdir) | store redirects for **every** test directory, not just `tests/` |
| `src/CORE/WORMS/expansion/jev_advisor.py` | Jev finite-choice advisor: validation, recording, outcome grading |
| `tests/test_jev_advisor.py` | 31 tests, stubbed transport, no network |
| `scripts/jev_advise.py` | `--ask` (records the decision) / `--grade` (independent check) |
| `scripts/scrub_probe_telemetry.py` | extended with `--unregistered` (dry-run default, backup first) |
| `docs/LESSONS_2026-09-21_SELF_EVOLUTION_REPAIR.md` | this document |
| `logs/repair_lessons_dataset_2026-09-21.jsonl` | machine-readable rows, one per lesson |

**Earlier in the same repair:** `spawn_credit.py` (the causal join), `wiring_genome.py`
(L1 genotype: 211 evolvable organs), `wiring_cycle.py` (L1 effector + canary +
lineage), `worm_telemetry.py` (one canonical outcome emitter), `observation_coverage.py`,
and the root-cause fix + scrub for the outcome tap.

**Verification**

| Check | Result |
|---|---|
| `test_jev_advisor.py` | 31 passed |
| Regression sweep (11 suites) | **413 passed, 3 skipped, 1 pre-existing order-dependent failure** |
| Same sweep without the new root conftest | identical result → the failure is not this session's |
| Live memory store | `spawn_selected=200 outcome=4240` unchanged across the whole sweep |
| Choice tap after scrub | 608 rows → **200** (all `MetaCluster`); 432 fixture rows tombstoned, backup written |
| `py_compile` | clean on every new/changed file |

**Still true:** the causal join has **no rows yet** — every existing choice predates
`decision_id`, and `\Azazael-Chain` remains `Disabled` with
`DisallowStartIfOnBatteries=true`. The loop is wired and tested; it is not turned on.
