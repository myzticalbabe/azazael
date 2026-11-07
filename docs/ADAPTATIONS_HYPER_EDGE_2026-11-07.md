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
