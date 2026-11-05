# HYPER_EDGE — Python 3.16t Release Candidate 1

**Written 2026-11-05. Series: 3.16 — a NEW series, not a 3.15 point release.**
**Executed on: `Python 3.15.0candidate` (free-threaded, `.venvs/py315t`), 16 cores.**

### Series statement, before any number is quoted

3.16 is a new series. Nothing here claims 3.16 behaviour that was measured, because
3.16 does not exist yet: every reading in this document was taken on **3.15.0rc3
free-threaded**. What the RC therefore does is hold a 3.16 line **without a version
gate**, so that the day a 3.16t interpreter appears the package adopts it by
capability probe rather than by an edit. The 3.16-specific claims in Part II are
**design**, not measurements, and are labelled as such. Expiry for every number:
**2026-12-05**.

---

## Part I — The five defects this RC is distilled from

Each is a failure this tree actually paid for, and each is now represented in the
instruction set rather than in prose:

| # | Defect | Where it lived | What it cost |
|---|---|---|---|
| D1 | A split vote (3-2-1, top share 0.50) graded as a verdict | `tools/arena_llm_judge.py` | C4 reported PARTIAL; a dissenting minority was reported as agreement |
| D2 | Six identical verdicts at identical confidence 0.65 read as corroboration | judge swarm r8 | it is a prior, not six independent findings |
| D3 | An instrument that never ran, reported as clean | reading/blank-run paths | `ALL SYNCED` at 370 diffs + 286 missing |
| D4 | A truncated artefact answering for a tree it no longer described | golden_arrow report overwrite | a 1-file artifact where a 499-file reading was recorded |
| D5 | A setting that existed, was read, and was invisible to the check | `defaults_profile --check` | a quorum the engine refuses passed the gate (found while building this RC) |

D5 is included deliberately: it was discovered *by this work*, during wiring, and
the fix is part of the RC rather than a footnote.

## Part II — Adaptation without version gates

`compat.capabilities()` probes and reports:

```
HYPER_EDGE compat: python 3.15.0candidate (cpython) free-threaded | cpu=16 workers=16
| pool=CORE.freethreading.FreeThreadPool | live=free_threading,tomllib,exception_groups,
per_interpreter_gil,concurrent_interpreters | probe_faults=0
```

### Native adoption — nothing here is a second implementation

Every mechanism in this RC resolves to a component this tree already owns, and the
selftest proves the resolution rather than asserting it:

| concern | adopted from | how it is proved |
|---|---|---|
| thread pool + worker sizing | `CORE.freethreading.FreeThreadPool` (its docstring names itself canonical) | `pool=CORE.freethreading.FreeThreadPool` in the report; `parallel_map` order check |
| free-threading detection | `CORE.freethreading.is_free_threaded` | same report line; own probe is the fallback and a recorded fault if used |
| verdict tally / share | `tools/arena_llm_judge.grade_pin` | `tally agrees with arena_llm_judge 7 pin(s), 0 mismatch(es)` |
| settings | `tools/defaults_profile.read_default`, all four layers | `--check` / `--get` transcript below |
| evidence | `ARC/cain/arena_llm_judgments_r8*.json` (written by the judge) | `calls=42 round=r8` in the artifact header |

Only the ISA itself is new, and that is the part that did not exist: a private
ThreadPoolExecutor, a private quorum rule or a private settings reader would be a
shadow of a component already owned here (HED-8).

The probe set is `free_threading` (`sys._is_gil_enabled`), `tomllib`,
`exception_groups`, `per_interpreter_gil` (needs both `_is_gil_enabled` and
`concurrent.interpreters`), `concurrent_interpreters`. **No branch reads
`sys.version_info` to decide behaviour**; the only use of the version tuple is the
report string. Consequences, in order of certainty:

1. **Verified here:** the package runs on 3.15t free-threaded, `probe_faults=0`, and
   `parallel_map` returns results in input order at 16 workers.
2. **Verified here:** on a GIL build the same code runs and the report says
   `threaded (GIL)` instead of `free-threaded` — degradation is announced, never
   silently absorbed.
3. **Not yet measurable (3.16 does not exist):** on 3.16t the new probes simply
   report `live`; no code path needs to change. If 3.16 moves a probe, the report
   loses a capability name and `probe_faults` stays 0 — i.e. the failure mode is a
   *quieter report*, not a crash. This is the design claim of the RC and it is
   falsifiable the day an interpreter lands: run `selftest`, read the `compat
   probes` line.

`parallel_map` is bounded by `default_workers()` (CPU count, capped), not by a
constant, so a 64-core host does not run 64 judge calls by accident.

## Part III — The admissibility microcode

Twelve ops, `0x01`–`0x0C`. Each answers one question about one reading and returns
one of `PASS`, `CUT`, `LEAD`, `BLIND`, `NO_QUORUM`. Rungs are ordered
`CUT < BLIND < LEAD < NO_QUORUM < VERIFIED` with `rung()` taking the **lowest**
state, so one refusal cannot be averaged away by eleven passes.

| op | name | question | legacy behaviour (3.15 and earlier) |
|---|---|---|---|
| 0x01 | TIER | is this tier A/B, or C/D? | **D mapped to LEAD but C was promoted on pairing alone** — defective, kept |
| 0x02 | GROUND | is the quote in the exhibit? | unverified quotes accepted |
| 0x03 | DENOM | does a population claim carry n/m and a denominator? | bare percentages accepted |
| 0x04 | UNIVERSE | does every negative name its universe? | "none found" accepted with no universe |
| 0x05 | QUORUM | does the top share clear quorum? | **`share >= quorum - 0.5` coercion: a 0.50 split passed a 0.66 quorum** — defective, kept |
| 0x06 | BLIND | did the instrument answer at all? | a blank run treated as empty |
| 0x07 | TRUNC | is a verdict-adjacent cut silent? | silent cuts accepted |
| 0x08 | PROVENANCE | does the claim carry command + digest? | prose accepted |
| 0x09 | STALE | is the reading inside its age bound? | off (limit 0): recorded, not enforced |
| 0x0A | REPRO | was the verdict reproduced on a re-draw? | single draw accepted |
| 0x0B | KNOB | is every setting read by at least one caller? | orphan knobs accepted |
| 0x0C | DISABLED | is the instrument enabled? | a disabled gate read as satisfied |

`isa` prints this table from code (`cli isa`), so the document cannot drift from the
implementation without the table changing.

## Part IV — Backward compatibility, proved not promised

Compatibility is a **flag on evaluation**, not a second codebase:
`microcode.evaluate(record, legacy=True)` reproduces the old semantics of every op,
including the two deliberately defective rows above. The selftest proves the
migration on the exact reading that caused D1:

```
[PASS] RC refuses a 0.50 split              rung=NO_QUORUM
[PASS] legacy mode reproduces the old coercion  legacy rung=VERIFIED (the defect
                                                being migrated away from)
```

That pair is the whole compatibility story: both behaviours are executable, and the
difference is visible in one line of output. A caller that must not change its
verdicts sets `legacy=True` and gets 3.15 semantics; everything else gets the RC.
There is no import shim, no `__getattr__` deprecation dance, no second package.

## Part V — Meta-evolution over recorded evidence

The evolved object is the **admissibility parameter set**, not code. Fitness comes
from replaying rows that already exist on disk — 42 judge calls in
`ARC/cain/arena_llm_judgments_r8.json` plus 6 in the C4 re-draw — so a genome
costs zero model calls and the run is reproducible.

- **Genome:** `quorum`, `max_age_days`, `truncation_strict`.
- **Objectives (maximised):** `verdicts`, `stability` (verdict survives the
  re-draw), `margin` (smallest distance from any pin's share to quorum — maximin).
- **Hard constraint:** no pin below quorum may obtain a verdict, **and** quorum
  must exceed 0.50 (at 0.50 a 3-2-1 split's top share equals quorum and obtains a
  verdict — measured by the selftest's own edge probe, which graded all 7 pins).
- **Selection:** Pareto filter, then maximin among equals. Deterministic for a seed.

### Result (10 generations, population 32, seed 20261105)

```
band: quorum must be > 0.50 (C4 must not pass) and <= 1.00 (C1 must pass)
frontier (1): q=0.7497 verdicts=6/7 stability=1.00 on 1 margin=0.250
shipped 0.66 -> q=0.6600 verdicts=6/7 stability=1.00 on 1 margin=0.160
chosen  -> q=0.7497 verdicts=6/7 stability=1.00 on 1 margin=0.250
overlay proposal: {"arena": {"quorum": 0.7497}}
inert genes (carried, not tuned): max_age_days (no row in this corpus constrains it);
  truncation_strict (no row in this corpus constrains it)
```

Read carefully, because three of these numbers are easy to over-claim:

- The **band is derived**, not configured: 0.50 is the highest share that must not
  pass (C4), 1.00 the lowest that must (the six unanimous pins). The engine was not
  told the answer; it read C4's tally.
- `chosen = 0.7497` is the maximin midpoint of that band, and it **agrees with the
  shipped 0.66** in the only sense that matters: both are inside the band, so the
  verdict set is identical (`verdicts=6/7`). The proposal buys **margin**, not
  verdicts — 0.250 against 0.160 — i.e. robustness to corpus movement, not a
  different ruling.
- `stability=1.00 on 1` is one comparable pin, not seven. The re-draw exists for
  C4 only; the "on 1" is printed so the number cannot be read as full coverage.
  (It printed `0.14` before the denominator was fixed — a perfect agreement scored
  as one-seventh, the same class of defect as D3.)
- Two genes are **inert on this corpus** and are reported with their values,
  explicitly not claimed as tuned. Padding a population with genes that do nothing
  is the same defect as an orphan knob (0x0B).

## Part VI — Wiring

**Settings, all four layers resolved and checked.** `quorum` is now refused by
`--check` outside `(0.5, 1.0]`, and layer 4 (`AZAZAEL_DEFAULT_<KEY>`) is folded into
the merged view before validation:

```
$ AZAZAEL_DEFAULT_ARENA_QUORUM=0.4 python tools/defaults_profile.py --check
DEFECT: arena.quorum must be a number in (0.5, 1.0] (0.5 or below cannot exclude a split vote)
EXIT=1
$ AZAZAEL_ENV=rc python tools/defaults_profile.py --get arena.quorum
0.7497
$ python tools/defaults_profile.py --get arena.quorum
0.66
```

**The engine reads the quorum in force** instead of a literal:

```
$ python -m HYPER_EDGE.cli evolve --evidence ... 
shipped quorum in force: 0.6600 via defaults_profile(windows)
$ AZAZAEL_ENV=rc python -m HYPER_EDGE.cli evolve --evidence ...
shipped quorum in force: 0.7497 via defaults_profile(rc)
```

**Adoption is opt-in by environment**, never a silent edit of the shipped default:
`evolve --apply rc` writes `config/defaults.rc.json` with a `_provenance` entry
naming the seed, the evidence file and its sha256. The shipped 0.66 is unchanged and
still valid, because a corpus-derived number belongs in the layer that names its
corpus.

## Part VII — Verification transcript

| command | exit | line that proves it |
|---|---|---|
| `python -m HYPER_EDGE.cli selftest` | 0 | `selftest: 24 check(s), 0 failed, 0 skipped` |
| `python -m HYPER_EDGE.cli evolve …` | 0 | `chosen -> q=0.7497 verdicts=6/7 stability=1.00 on 1 margin=0.250` |
| `AZAZAEL_ENV=rc python tools/defaults_profile.py --check` | 0 | names base **and** overlay |
| `AZAZAEL_DEFAULT_ARENA_QUORUM=0.4 … --check` | 1 | refuses the impossible quorum |
| `python tools/defaults_profile.py --get arena.quorum` | 0 | `0.66` |

The 24 selftest checks include **one negative control per op** (12), plus: 12 unique
codes, 12/12 legacy columns documented, a complete reading reaching VERIFIED, the
RC-vs-legacy split pair, `parallel_map` order, evolve determinism for a seed, the
0.50 edge refusal, the 0.50 quorum refused **at the rule** (not only by the band),
admissibility of the chosen genome, and agreement with the judge's own tally. Two of them **failed on first run** — `0x09` (its control
supplied no age limit, so it tested nothing) and the 0.50 edge (which graded a
split) — and both were fixed rather than relaxed.

```
selftest: 24 check(s), 0 failed, 0 skipped
```

## Part VIII — Microcode that repairs itself, and dreams that cannot buy a patch

**Measured 2026-11-05, interpreter `C:/Azazael/.venvs/py315t/Scripts/python.exe`, branch
`azazael-intel-ultra-9-evo`.** Every line below carries the command that produced it.

### VIII.1 A patch is a policy value with a receipt, not a rewrite

The ISA's predicate bodies are never rewritten at runtime; what may change is a
**declared knob** in `microcode.POLICY_CHOICES`. Admission is four gates, in order:

1. a **real failing case** in the control corpus, carrying `command` + `digest`;
2. the candidate **fixes** that case under replay;
3. it **regresses no passing case**;
4. the **least severe** admissible value wins (`skip` → `blind` → `cut`), so a repair
   cannot escalate to `cut` merely because `cut` also fixes the symptom.

The one admitted patch is the product of exactly that:

```
$ PYTHONPATH=src python -m HYPER_EDGE.cli patch --apply
patch 0x09.undated skip -> blind fixes=['0x09/12'] regressions=[]
patch=f22beb08ea36... digest=7b9e66ca2c0c... applied
$ python -m HYPER_EDGE.cli patches
7b9e66ca2c0c 0x09.undated skip -> blind fixes=['0x09/12']
chain: ok (1 entries, head 7b9e66ca2c0c)
```

`cut` was admissible too (`fixes=[] regressions=[]` is *not* what it reported: it was
reported as regressing the case that is supposed to stay `BLIND`). `cut` would have
asserted the artifact is inadmissible when the truth is that **the freshness question
was never asked** — the claim is about the instrument, not the world. `blind` is the
only value that says that, which is why severity order is a gate and not a taste.

### VIII.2 Why this file has two hashes per entry

The first version hashed `created` into the only identifier. The same proposal was
therefore `c8a5873550629894` when dry-run and `a6d7a81023ba29a2` fifteen minutes
later — an identity that drifts with the clock cannot be cited as evidence. Now
`patch` hashes the **content** (op, knob, old, new, fixes, regressions, corpus,
evidence, env) and is stable; `digest` hashes content **plus** position and creation
time, and is the chain link. Proof: the same proposal replayed one second apart prints
`patch=f22beb08ea36` twice, while `digest` moves. A repeated proposal is refused by
name (`patch f22beb08ea36 is already entry 1 of the ledger`), so the same repair
cannot be logged twice.

### VIII.3 Native AI: the model dreams, the ISA grades, evidence decides

`HYPER_EDGE.dream` asks the **local** OpenAI-compatible endpoint the judge swarm
already uses — no new dependency, no cloud key — for readings a naive reviewer would
accept and this microcode should not. Two measured runs, model
`Qwen3-4B-Instruct-2507-abliterated` served from `127.0.0.1:8081`:

| run | asked | graded | outcome |
| --- | --- | --- | --- |
| `hyper_edge_dreams.json` | 3 | 4 | all `CUT`; `0x0B` (orphan knob) fired on every dream |
| `hyper_edge_dreams_r2.json` | 4 | 4 | aims at `0x03`/`0x09`/`0x0A`; one hypothesis |

Run 1 is the interesting failure: the model nested `why` inside every `record`, and the
first version **discarded all three dreams over a field it had already been given as a
sibling**. A key outside the ISA is now dropped and named in `dropped_keys`; a dream is
graded on the keys it did use. Run 2 added the op table to the prompt and produced the
one line that matters:

```
hypothesis 0x09.undated blind -> cut separates ['quorum-not-reached:LEAD->CUT']
verdict: a_dream_is_not_evidence
```

That is a dream **proposing** the escalation VIII.1 refused. It stays a hypothesis:
to move the microcode a dream must be pinned into the control corpus with the command
and digest that produced its expected answer. `discriminate()` stamps every row, and
`selftest` fails if any stamp claims otherwise (`a dream cannot buy a patch`).

### VIII.4 Three defects the layer found in its own engine

| symptom | cause | repair |
| --- | --- | --- |
| `TypeError: int() argument must be ... not 'list'` killed the CLI | a dreamed record with `"draws": [1, 2]` and `reproduced: true`; `_repro` called `int()` unguarded | `evaluate` grades a faulting op `BLIND`, names it in `faults`, and the rung becomes `BLIND` unless a positive `CUT` already fired; `selftest` now proves it (`rung=BLIND faults=['0x0A']`) |
| a chain in a test ledger read `prev=<real head>` against `GENESIS` | `apply` read its head from the default ledger while appending to the ledger it was given | head is read from the same path it writes (`patches(log)`) |
| four environments reported `refused` after the fix landed | "no failing case" was classified as a rejected patch | distinct status `converged`: *every control case passes under the policy in force* |

An adversary could have stopped the instrument by malforming one field. That is the
case for grading faults at all: a refusal is a reading, a traceback is a blind spot.

### VIII.5 All environments, concurrently

```
$ PYTHONPATH=src python -m HYPER_EDGE.cli optimize --env windows,wsl,kali,rc --workers 4
windows      proposed   0x09.undated skip -> blind
wsl          proposed   0x09.undated skip -> blind
kali         proposed   0x09.undated skip -> blind
rc           proposed   0x09.undated skip -> blind
corpus: f8c26bf6f6b99b45 (shared by every environment in this run)
```

One proof per environment through `compat.parallel_map` (native
`CORE.freethreading.FreeThreadPool`), results in declared order. With the fix in force
the same command reports `converged` on all four. **Honesty line, not decoration:** every
environment proves the *same* corpus here, so this demonstrates concurrent evaluation
and per-environment policy isolation (`config/microcode.<env>.json`), not four
different bodies of evidence. An environment with no corpus reports `no_evidence`
(`BLIND`), and that path is pinned by a test.

### VIII.6 What was run

```
$ python -m HYPER_EDGE.cli selftest           # 31 check(s), 0 failed, 0 skipped
$ python -m pytest tests/test_hyper_edge.py -q -p no:xdist   # 22 passed
$ python tools/staged_scanner_gate.py <staged paths>         # recorded below
```

| proof | command | result |
| --- | --- | --- |
| patch admitted and ledgered | `cli patch --apply` | `applied`, `chain: ok (1 entries)` |
| duplicate refused | `cli patch --apply` (policy reverted in a copy) | `REFUSED: patch f22beb08ea36 is already entry 1` |
| clock-free identity | `cli patch` twice, 1 s apart | `patch=f22beb08ea36` both times |
| dreams graded | `cli dream --count 4` | `4 graded`, 1 hypothesis stamped |
| env concurrency | `cli optimize --env windows,wsl,kali,rc --workers 4` | 4 rows, declared order |
| fault graded | `selftest` | `rung=BLIND faults=['0x0A']` |

**Limitations.** No 16-core measurement of the parallel gain: `optimize` proves 4
environments over a 12-case corpus in milliseconds, so the concurrency argument here is
structural, not a speedup claim. Dream quality depends on the local model's size; a 4B
model needed the op table in the prompt to aim at more than one op. And a dream set is
**not** evidence: this section reports what the model proposed and what the ISA
answered, not that any proposal is correct.

## Part IX — What this is not

- **Not a 3.16 measurement.** No 3.16 interpreter exists on this host. The 3.16 line
  is a target reached by probe; its behaviour is unverified by construction.
- **Not a judge rewrite.** This RC scores and constrains readings; it does not call
  a model. The arena judge keeps its own quorum and now refuses a split instead of
  coercing it (commit `7f479cc4`).
- **Not a claim that 0.75 should ship.** The evidence supports a band, not a point.
  The point chosen maximises margin within the band; the shipped 0.66 sits inside
  it. Moving the default is a decision for a corpus that has more than one re-drawn
  pin.
- **Not exhaustive over `tools/`.** The truncation census (929 sites / 227 files)
  and reading audit (33/66 artefacts) are the instruments the `TRUNC` and `BLIND`
  ops encode; the RC consumes them, it does not replace them.

**Expiry:** 2026-12-05, or immediately on the arrival of any 3.16 interpreter —
re-run `selftest` and the evolve command, and re-measure the band on the current
corpus before quoting 0.7497 again.
