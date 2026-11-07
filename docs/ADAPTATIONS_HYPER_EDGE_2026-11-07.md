# Hyper-edge adaptations — measured inventory first, then proposals

Written 2026-11-07 at HEAD c37fee5e. Every "have" below is a grep, every
"don't have" is a grep that returned nothing. Proposals say what failure they
remove and what proves them.

## 1. What the tree actually has (measured)

| capability | where | real or wrapper |
| --- | --- | --- |
| 8 estimator families behind one factory | `src/ML/estimators.py` | **sklearn wrappers**, lazy-imported per call (`_linear_regression` -> `sklearn.linear_model.LinearRegression`) |
| NSGA-II (non-dominated sort, crowding, SBX, mutation) | `src/ML/nsga.py` | **native**, numpy only |
| reverse + forward autodiff | `src/ML/autodiff.py` | **native** (`Dual`, `backprop_grad`) |
| GOSP online session-outcome learner | `src/ML/gosp.py` | sklearn `DictVectorizer + GradientBoostingClassifier`, `warm_start` refits, lock-guarded |
| trace consolidation / step monitor / torch bridge | `src/ML/trace_consolidator.py`, `step_monitor.py`, `torch_bridge.py` | native glue |
| Q-learning (Q-table, epsilon-greedy) | `src/AZAZAEL_TOOLKIT/QL_ANALYSIS.py` | **real but unwired**: only a TOOLBELTZ probe calls it (`src/CORE/WORMS/TOOLBELTZ.py:114`) |
| genetic algorithm over worm genomes | `src/eve_unleashed/self_modifying_worms.py:124` | **native**, used by Eve |
| linear forecast per resource | `src/eve_unleashed/predictive_worms.py:36` | native least-squares |
| Bayesian era test (Cranium, replaces SPRT) | `src/CORE/WORMS/expansion/evidence.py` | native posterior `P(mu>x)` |
| **RANI** | `docs/PROJECT_MAP.md:57` — "RANI-VL Framework (`EveUnleashed_Selector/`)" | **not in this repo.** `grep -rnw 'RANI\|Rani\|rani' src/` returns **0**. It is a separate desktop project; the earlier 21 "rani" hits were substrings of `granite` and `Cranium`. |

**Answer in one line:** ML yes (partly native, partly sklearn wrappers); RL is
present as an unwired Q-table, not as a control loop; RANI is a sibling
framework outside `azazael/src`, so nothing in Eve is RANI-native today.

## 2. Adaptations, ranked by failure removed per unit price

### A1 — RANI-native: the ladder becomes a bandit, not a heuristic (**build first**)
Seven rungs are seven arms. Per host, keep counts and mean cost
(`answered=1/0`, rung index = cost proxy) and pick by UCB1 with an epsilon
floor; a rung that has failed *k* times for a host stops being tried (this is
the named gap **inhibition**, L4-a, and it makes `intuition` a policy instead
of a lookup). Native: ~80 lines, no dependency, experience = the live log Eve
already writes.
Failure removed: every fetch pays the same rung order regardless of what that
host did last time.
Proof: host fixture with 3 `blocked` render answers -> rung order skips
`render`; fresh host -> unchanged order; reward table reproduced from
`state/eve_live.jsonl`.

### A2 — wire the Q-table that already exists (**cheapest**)
`QL_ANALYSIS.py` implements state->action Q with epsilon-greedy and is called by
nothing but a probe. Give it the board as its environment: state = (lane, task
kind), action = which lane takes it, reward = retired on first attempt, 0 for
blocked, negative for an expired lease. The board already stores every one of
those outcomes (`lane_task_state`), so the replay set exists.
Failure removed: dispatch by convention instead of by measured routing success.
Proof: replay the last 200 retired rows offline; print mean reward of the
Q-chosen lane vs the actual lane. No live change until the replay is positive.

### A3 — GOSP scores the queue instead of the prose (**medium**)
`SessionOutcomeLearner` already refits online on feature dicts + an outcome
label. Feed it board-row features (age, action verb, lane, has-brief,
has-acceptance-command) and the label "retired done". Its output ranks the
queue *for a human decision*, never auto-retires — a learner that closes other
lanes' rows is a wrecking ball, and `mend.py:48` already carries that rule.
Failure removed: queues ordered by age, where the oldest row is often the one
nobody can execute.

### A4 — Cranium instead of vibes for "did this adaptation help?" (**cheap, honest**)
`evidence.py`'s Cranium answers `P(mu > baseline)` from era-labelled
observations. Point it at the live log: era = before/after an adaptation,
observation = per-event success (rung answered, test passed). An adaptation
stays only if the posterior clears a stated threshold; otherwise it is reverted
with its number, which is the same discipline the improvement doc asks for.
Failure removed: keeping changes because they felt right at 23:00.

### A5 — self-play gym: the bypass kit as adversary for the ladder (**creative**)
`bypass_kit.run_suite()` already mutates inputs against Eve's own parsers. Run
it as the *generator*: for each mutated body (truncated, gzipped, charset-
mangled, marker-stripped), check that `detect_challenge` still names the wall
correctly and that extraction still fails closed. That is a labelled dataset
produced offline, with zero network, training the detector's thresholds rather
than hand-picking them.
Failure removed: detection thresholds nobody can justify (today they sit in the
`0.89/0.70` gap, measured once on one corpus).
Proof: N generated pairs, confusion matrix printed; a detector change ships
only with the matrix beside it.

### A6 — dream() writes through the trace consolidator (**closes L4-c**)
`ML/trace_consolidator.py` already merges traces. `intuition.dream()` recomputes
priors from scratch each call; instead it should consolidate the stream into
durable rules (40 identical `plain` answers -> one prior fact) via the existing
consolidator plus one PMB `record_fact`. Native reuse, not a new subsystem.
Failure removed: consolidation stays a named gap while its part already exists.

### A7 — NSGA-II over restart-instruction variants (**only with a real objective**)
Three objectives: gate PASS count, board availability after one hour, mean
time-to-first-claim. Population = variants of the restart block. Reject this
until the objectives have measured baselines — optimizing prose against proxy
metrics is how a doc gets worse while its score improves.

## 3. Refusals (keep the boundary)

- **No learned model deciding refusals or gates.** A gate that a learner can
  talk out of is not a gate.
- **No cloud training on repo content.** Every adaptation above is local and
  derived from the event stream.
- **No RL on the fetch ladder's real targets as the training signal** beyond
  what Eve already fetches on request: the bandit learns from Eve's own
  attempts, it does not go prospecting to generate experience.
- **RANI stays where it lives** unless its code is brought in deliberately:
  naming a local bandit "RANI" while the framework lives in another project is
  how a tree acquires a claim it cannot back.

## 4. Wave 2 — more adaptations (A8–A18)

The first wave made Eve learn *from its own traffic*. This wave makes it learn
*without touching a target*, which is the only way the learning gets big enough
to matter.

**A8 — `arena.py`: a replayable environment (build this before any learner).**
A deterministic `step(event)` over the live log: same stream in, same decisions
out, no network. Every learner below is untestable without it, and tonight's
only stream is 17 events (`state/eve_e2e_2026-11-07.jsonl`) — small enough to
prove the replay is exact before it is used to train anything.
Failure removed: "it learned something" with no way to re-run the run.

**A9 — Common Crawl is the offline gym.** The ring already fetches
`collinfo -> index -> byte-range WARC`; the same WARCs are a labelled corpus of
real pages at scale: clean bodies, truncated bodies, charset-mangled bodies,
soft-404s, consent walls. Run `detect_challenge` over a sample and you have a
confusion matrix over thousands of pages with **zero requests to any host**.
Failure removed: thresholds justified by one corpus measured once.

**A10 — Wayback as a drift dataset.** The same URL across N snapshots is a
supervised "did this page change" set, which is exactly what `watch` and
`debunk` need and have never had. Label = structural diff between adjacent
captures; features = what `debunk` already extracts.

**A11 — cost-aware policy, not just a bandit.** Rungs differ in latency and
bytes, not only in success. Score each arm by expected value per second using
measured per-rung costs from the log; `ML/autodiff.Dual` gives the derivative of
that score against a threshold, so thresholds move by gradient rather than by
hand.

**A12 — NSGA-II over rung policies, replayed.** Population = rung orderings and
suppression rules; objectives = answer rate, mean latency, wall-trigger rate;
evaluated **offline against the recorded log**, so the Pareto front costs
nothing and ships only as a diff to A1's policy.

**A13 — provider-choice distillation.** `websearch.PROVIDERS` is five keyless
APIs and the tree already mandates six-API fanout. Learn which provider answers
which prompt shape (question, citation, book, paper, code) and fan out to two,
not five: a `ML/estimators` classifier is the right size for this, and it
directly cuts the cost the 6-API mandate pays on every analysis.

**A14 — persist the failure ledger before using it as labels.**
`src/CORE/failure_ledger.py` is 64 lines and `failure_notes()` returns a
process-local `Dict[str,int]` — every failure dies with the process. Give it a
JSONL sink (same shape as the live log), then `mend scan` can order work by
where failures actually cluster.
Failure removed: the tree's most honest signal is currently thrown away at exit.

**A15 — Cranium per lane.** Posterior that a lane's next claim will be
retired-done, from its own history; feeds A2's dispatch as a prior instead of a
cold Q-table.

**A16 — fit memory decay instead of hardcoding it.** `pams_evolution` carries
`SEVERITY_WEIGHT` and per-event `factors`; the decay constants are literals.
Fit them against what was actually recalled later (PMB `recall` hits) rather
than asserting them.

**A17 — adversarial self-play on our own documents.** `oracle` vs `rebuttal` on
the tree's own docs: one drafts a claim, the other must cite or refute, reward
= the citation survives `factcheck`. Fully offline, and it trains the pair that
is supposed to catch bad claims.

**A18 — RANI only by provenance.** If the sibling framework is adopted, it
arrives as a declared import with a provenance file naming the source project
and commit — never as a local bandit wearing its name.

## 5. Prospecting — the rule I stated was too broad; here is the precise one

"Prospecting" conflates three different activities. Only the third is refused.

**(1) Prospecting our own systems — yes, already doing it.** The tree, the live
log, the board, the bake lane, the failure ledger, WSL and Kali mirrors. This is
where every adaptation above gets its first data.

**(2) Prospecting consented corpora and APIs — yes, within their terms.** Common
Crawl, Wayback, Wikipedia, OpenLibrary, Crossref, Stack Exchange and LOC are
published *for* machine use; Eve's `PROVIDERS` tuple is literally that list.
Using them at their stated rate limits is not evasion, it is the intended use,
and A9/A10 are built on exactly that.

**(3) Automated probing of hosts that did not invite us — no.** Four reasons,
in order of weight:

1. **The reward would be the wrong thing.** If experience is generated by
   hitting unfamiliar hosts, the only signal available is "did we get past the
   check" — so the learner optimizes evasion, which is the boundary already
   drawn. A bandit trained on that learns to be a scanner with good manners.
2. **Consent and terms.** A host that publishes no API, no crawl policy and no
   invitation has not agreed to be a training target; robots/ToS are the
   instrument by which that is expressed.
3. **Traffic is indistinguishable from an attack at volume.** Eve's whole point
   is that a wall gets *named*, not defeated. Generating traffic to farm
   experience puts Eve on the wrong side of that distinction operationally.
4. **It poisons the corpus the thresholds were measured on.** The floor
   thresholds (0.89/0.70) and the challenge detector are calibrated against this
   corpus; mass probing adds noise to the very store that grades the answer.

So the correct statement is not "no prospecting". It is: **prospect where
consent exists — your own systems and the published corpora — and never let a
reward be "we defeated a check".** A9 and A10 are the payoff: petabytes of
already-crawled, license-permitting pages, with no request to a target and no
evasion in the objective.
