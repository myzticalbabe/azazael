# EVOLVE-TO-RESOLVE — train on live experience, never on simulation

**Standing order, 2026-11-07.** Eve was designed to evolve and had never been
trained. The first training runs bought these nine rules, each with the failure
that paid for it. They govern every training loop on this tree: worm genomes,
fetch policy, intuition priors, adversarial kits.

## The nine rules

### E2R-1 — Train on live experience, never on simulated fitness

The first evolution ran 10 generations against a simulated fitness model:
best 0.8556 → 0.8817, mean 0.7416 → 0.8323 — and taught nothing, because the
simulator cannot surprise. The first live run discovered a real captcha-wall
on wikipedia, formed real priors, and moved dream hit-rate 0.333 → 0.438.
A simulator exercises the machinery; only live outcomes train the system.

### E2R-2 — Intuition is weightless; the log is the training set

`intuition.py` carries no stored weights by design — every answer is recomputed
from the fetch stream, and `dream()` replays guess/answer pairs to score
itself. An untrained Eve answers `unknown` to everything, and that is correct:
there is no prior. Training Eve therefore means **feeding it experience**
(live fetch events into the log), never tuning a parameter. A training run that
leaves the log empty trained nothing, whatever its fitness curve says.

### E2R-3 — Fitness is 100% live-measured, with the mapping written down

Every fitness component must name its instrument: held-rate from
`bypass_kit.run_suite()`, wall time from `perf_counter`, peak bytes from
`tracemalloc`, ok/blocked from the ladder's own outcome dicts. And every
genome→policy mapping must be documented in the run: which gene gates which
decision (min_confidence → trust a blocked guess, aggressiveness → retry
budget, cooldown → politeness delay, budget → cost cap). A fitness number
whose mapping is not written down is a story, not a measurement.

### E2R-4 — Bound the harness, never the product

The live ladder is slow on walled hosts by design (render 45 s, stealth,
archive waits) — that slowness is product behavior and must not be "fixed"
for training. Bounds live in the trainer only: a 40 s per-fetch thread cap,
a 1.0 s politeness cap, a retry threshold. The ladder source is untouched.
A training speedup that edits the product is a benchmark gaming itself.

### E2R-5 — Dream hit-rate is the training metric

Report `dream()` pairs + hit-rate every generation, from the same log the
intuition reads. A `hit` is AGREEMENT (2026-11-07): the verdict matches
(guess/ok or blocked/blocked) AND the rung matches when one was predicted.
A blocked guess that meets a blocked answer is a hit -- the lineage correctly
predicted the wall. Guesses logged without a verdict keep the old rule (ok +
rung match) so old logs still read. Quote the denominator (pairs) with the
rate, or the number is HED-9's lie.

### E2R-6 — Selection needs variance; saturate the adversary, not the population

Five live generations held every bypass case (363/363 → 264/264) with zero
bypassed: the entire fitness gradient came from cost, and further generations
could only learn to sweep less. When walls hold at 100%, the next signal
comes from **harder adversarial cases in the kit** (+13: tab/newline smuggles,
UNC/ADS/trailing-dot paths, fullwidth/combining unicode, spoof variants —
46/46 held), not from more breeding. A flat gradient is information about
the environment, never a reason to run longer.

### E2R-7 — Inherit, don't reseed

A fresh random seed per invocation is re-seeding, not evolution: gen-1's
evolved population died in a dead process because only the log persisted.
Persist the population (`WormDNA.to_dict` / `from_dict`) between runs and
reload it; the log carries experience across runs, the population file
carries heredity. One of them missing means one of the two inheritances
is broken — say which.

### E2R-8 — Findings are recorded, parsers are never auto-patched

The bypass-kit contract, unchanged: a BYPASSED case is a finding — record it,
fix the parser by hand, re-run. A training loop that patches parsers to
raise its own score is the oldest fraud in machine learning. This rule has
no exception and no flag.

### E2R-9 — Developed instruments only

The live loop runs through `eve bypass` / `eve e2e` (live-logged) and
`GeneticAlgorithm` (select/breed/cull) — never a hand-rolled harness in
`/tmp`, never a reinvented clone/fork/push workflow when the pack already
defines one. A reimplementation that behaves identically is still a fork,
and a fork is where fixes go to be forgotten. (Witness, 2026-11-07: a
hand-rolled evolve script and a hand-rolled PR workflow were both retired
the same day in favor of the developed ones.)

## Verify this canon

```
python tools/agent_orders_sync.py --check   # block byte-identical in every lane file
python -m eve_unleashed.cli bypass          # the developed instrument still runs
```
