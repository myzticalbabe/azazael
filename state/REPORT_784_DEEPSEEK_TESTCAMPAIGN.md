# Engram #784 — DEEPSEEK TEST-CAMPAIGN: report

**Model ID**: `DeepSeek V4.1 Flash Fast`
**Repository root**: `C:/Azazael/azazael` (`git rev-parse --show-toplevel`)
**Branch**: `migration/baseline-20261001`
**SHAs**: `8d6fb28f` (baseline re-record, from #770) · `f86dd681` (this lane's four test files)

## P0 — #770 confirmed landed, without redoing

#770 (training-intake edge) was closed in this session first, as its brief requires. Its
full-suite red inventory is in `state/REPORT_770_DEEPSEEK_INTAKE.md` (`c38d9e64`), including the
stale anti-pattern baseline fixed as `8d6fb28f`. Nothing was re-implemented here; this lane is
additive and touches `tests/` only.

## Comparison harvest — the pre-registered baseline was wrong twice

Measured before writing anything, because a pre-registered number is an instrument too.

| technique | baseline (pre-registered 2026-10-15) | new result | delta |
|---|---|---|---|
| PBT files | **0** | **3** files, 21 tests (`@given`); strict count was **1** before | +2 files / +20 tests; **the baseline was wrong, not merely low** |
| race-test files | **0** | **+1** file, 5 tests; strict `Barrier` count was **4** before, 15 files mentioned `ThreadPoolExecutor`/`Barrier` | +1 file; **the baseline was wrong** |
| mutation score | **UNMEASURED** | **0.875 (14/16)** on the SparseMoE region, then **16/16** after both survivors were closed | first measurement ever recorded for this module |
| metamorphic relations | not a category in this tree | **+1** file, 9 stated relations (R1–R9) | new technique present |
| fault-injection drills | **0** | **+1** file, 5 drills | new technique present |
| differential runs | **0** | **1** run: 39 tests × 2 interpreters | **0 divergence** |
| fuzz targets | **0** | **0** | ruled, named precondition (below) |
| contract annotations | **0** | **0** | ruled, named precondition (below) |

The two wrong baselines are the finding, not a footnote: "PBT files 0" says *absent* and would
have justified introducing the technique, while the measured 1 says *present at near-zero
coverage* and justifies raising it. Two different tasks, and only the second is true.

## Phase results

### M — mutation pilot: **executed**, score 0.875 → 16/16

Used the tree's own stdlib mutation tester (`scripts/mutate.py`), **not** Cosmic Ray. Evidence the
alternative existed: `pip download cosmic-ray` fetched `cosmic_ray-8.7.0-py3-none-any.whl`. It was
declined because `mutate.py` already writes `state/mutation_summary.json`, which `live_monitor.py`
and `command_center.py` **consume** — a second instrument would fork the score across two files
while the monitors kept reading the stale one. Deviation recorded rather than silent.

Restricted to the 56 sites inside `SparseMoE` (lines 395–709) because the whole file has 322 sites
and the new suite covers only that class: a default run would have reported unrelated code as
surviving mutants, manufacturing false test gaps.

**Survivors, both owned and both closed with a named test:**

| survivor | why it lived | closing test | now |
|---|---|---|---|
| `arith-flip Mult @ 413:21` (`gap = max(1, 2 * d_model)`) | nothing asserted the expert geometry — and `param_count` **cannot**: it is computed *from* the shapes, so it agrees with any width built | `test_closes_mutant_413_the_expert_hidden_width_is_twice_d_model` | **killed** |
| `compare-flip Gt @ 561:29` (`counts[i] > target`) | nothing measured the **sign** of the nudge. `load_balanced` is derived from the PRE-nudge snapshot, so an inverted signal reports identical numbers — worse than no balancing, since it deepens collapse every step | `test_closes_mutant_561_the_nudge_moves_the_gate_toward_balance` | **killed** |

Re-run proof: `mutate: 2/2 killed (score 1.0)`. Target SHA verified identical before and after
every run (`376149dc…`), with no leftover `.mutate-backup`.

### P — Hypothesis PBT: **executed**, 21 tests

Pure targets only, per the brief: the MoE routing algebra, `load_entropy_normalised`, `_softmax`,
and the NEXUS gate. The strongest property is an **oracle**, not a bound: `forward`'s reported
`aux_loss` is re-derived from a fresh `route()` call as `n * Σ f_i·p_i` and compared, so a loss
detached from the routing it names cannot pass.

### C — races: **executed**, 5 tests

Barrier-synchronized (threads collide at one instant rather than drifting), repeated ×3, run on
py315t with the GIL off. Covers the `failure_ledger` stampede (no lost update), a concurrent reader
(no torn snapshot), a broken-lock probe, a temp-database store stampede, and `route` under
concurrency (read-only-after-construction is a claim, so it is tested).

### F — metamorphic relations: **executed**, 9 relations

Stated where no oracle exists: entropy insensitive to permutation, to uniform scaling and to
appended zeros; `forward` token-order equivariant; a duplicated token doubles its counts and
leaves aux unchanged; softmax permutation-**equivariant** (not invariant — that distinction is the
test); `balance_step(gamma=0)` is the identity; repeated measurement is idempotent; and the top-k
entropy floor the module's own docstring names.

### H — fault injection: **executed**, 5 drills

Temp copies only. The merge gate is fail-**safe**: a lane file with one corrupt line contributes
**zero** rows, and the test asserts the valid row is *absent*, because checking only that
`BAD_JSON` appears would pass on an implementation that kept the good half.

Two probes against the real store, run *before* writing assertions, moved where the fail-open
boundary is believed to be:

* a corrupt database file → `sqlite3.DatabaseError` from the **constructor**, no note recorded;
* a read-only database file → `sqlite3.OperationalError` from `record_event`, no note recorded.

So `LocalMemoryStore` is a **raising** API and the fail-open contract belongs to its caller.
`technique_runtime.record_link` is that caller: it absorbs the exception, returns `False` and calls
`note_failure` — now pinned by `test_record_link_fails_open_when_the_store_cannot_write`. Assuming
the store itself was fail-open would have been a claim about code nobody had run.

### E — differential: **executed**, 0 divergence

All four phase files on both interpreters:

| interpreter | version | GIL | hypothesis | result |
|---|---|---|---|---|
| `C:/Azazael/.venvs/py315t` | 3.15.0rc3 | **off** | 6.168.4 | **41 passed** |
| `C:/Users/clint/.../Python314/python.exe` | 3.14.7 | on | 6.168.3 | **39 passed** (pre-closeout), then 41 |

No behavioural divergence on these modules between the GIL and free-threaded builds.

### D and G — **ruled, not executed**, with named preconditions

Evidence gathered with `pip download --no-deps` against the production interpreter:

* `atheris` 3.0.0 — **sdist only** (needs a C toolchain build); Phase D not run.
* `crosshair-tool` 0.0.111 — **sdist only**; Phase G's SMT half not run.
* `pytation` — fails its own build-dependency resolution outright.
* `deal` 4.24.6 and `icontract` 2.7.3 — **wheels available**, so Phase G is one install away and is
  blocked by a *decision* (mutating the production venv), not by a missing capability.

## Errors hit (attested, including my own)

* **784-E1** — my PBT oracle inherited the source's *rounding*. `report()` rounds `max_entropy` to 4
  dp; I compared it to unrounded `log2(3)`. The first py315t run failed, and the failure was mine.
  Fixed by comparing to `round(math.log2(3), 4)` rather than by loosening the source.
* **784-E2** — two reader threads appended to **one** list, then I asserted that list was sorted.
  It records interleaved append order, not either reader's observation order. Fixed with one list
  per reader plus a non-vacuity check that each reader actually sampled.
* **784-E3** — the broken-lock probe called `failure_notes()`, which takes the same lock, so the
  probe raised from its own assertion line. Fixed by reading the counter directly while broken and
  checking the public view after restoring.
* **784-E4** — the store race test reused **one** temp database across repeats (pass 2 asserted 200
  while 400 existed). Fixed with a fresh database per repetition.
* **784-E5** — `import os` inside a test function, an anti-pattern this repo gates on. Moved to
  module scope before committing.

The pattern in E1–E4 is worth naming: every one was an assertion that could not observe its own
subject. That is the same defect class the mutation survivors came from.

## Limitations, stated rather than smoothed

* **306 of the file's 322 mutation sites were never sampled.** The score is 16/16 over a chosen 16,
  not over the module; the reported figure is a pilot, and calling it "the module's mutation score"
  would overstate it.
* **Phase D and G were not run** (see the ruling). A phase that did not run is a gap, reported here
  as one.
* The free-threaded leg is a **single** interpreter build; a second free-threaded build was not
  available to compare against.
* Race tests reduce, but cannot eliminate, the chance that a lost update goes unobserved. They are
  repeated ×3 with a barrier, which is stronger than a single pass and still not a proof.

## Standing rules this lane converts into (the closeout the brief asks for)

1. **PBT-required for pure functions** — any function with no clock, store or RNG at call time gets
   a property test; the aux-loss oracle is the template.
2. **Race tests for shared structures** — barrier-synchronized, repeated, one observer per asserted
   sequence, one reset fixture per repetition.
3. **Mutation gate on new modules** — pair the target region with the suite that covers it
   (`--only`), and close every survivor with a named test before calling the module tested.
4. **A pre-registered baseline is an instrument** — re-measure it before trusting it; two of eight
   numbers in this brief were wrong.
