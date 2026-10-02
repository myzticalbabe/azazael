# genome_seed / schema-alternation: corrected diagnosis and resolution

Date: 2026-10-02. Resolves the fourth followup of the reconciliation session.
Resolution commit: `7bb1922e` (adoption).

## The claim being investigated

The originating report (`loop_integrity.json`, 2026-09-30) named the root cause
as: *"`genome_seed()` hashes every gene, so consecutive cycles are NOT the same
measurement and the arms are not comparable."*

Symptom: `state/loop_integrity.json` = DEGRADED, 0 promotions, "schema changed
on 91–98% of consecutive cycles across 2 arms (`by_session`,
`use_schema_features`)", SPRT blind with `n=0` on most cycles.

## Verdict: the named cause is wrong

`genome_seed(genes, salt)` (evolution_cycle.py) is **per-genome RNG
determinism**, not a measurement definition. It sha256-hashes the sorted
`key=value` pairs and seeds the eval RNG, so *the same genome scores the same
way in any process*. Two genomes that differ in their gene **values** getting
different seeds is the intended behaviour — that is what makes a genome a
reproducible measurement. It does not make two cycles incomparable.

The real mechanism is **search-space (schema) heterogeneity**, and it comes from
PROTEUS **Phase E Morph**:

- `morph_candidate_gene(cycle_index, ...)` is a **round-robin** over
  `MORPH_CANDIDATES` (`use_schema_features`, `by_session`), so it rotates a
  *fifth* gene into the search space every cycle.
- `morph_strip` removes the previous extra gene, so each cycle is a clean
  "4 + 1" factorial — deliberate, per `evolution_cycle.py`: *"Each cycle must be
  a clean 4 + 1 factorial or the per-gene verdict is confounded."*
- `_trainer_extra_kwargs` / `morph_trainer_kwargs` **forward a different kwarg**
  to the trainer per arm.

Consequence: across arms the **gene SET differs**, so the **fitness function is
genuinely a different function**. A gate that compares *consecutive* cycles is
comparing two different functions, and under a full round-robin it can never
accumulate a streak. Within one arm, differing values are exactly what the
search explores and `genome_seed` already makes them comparably deterministic.

So there were **two incompatible requirements**: Phase E requires schema
alternation; the promotion gate requires schema stability. Neither was wrong;
together they starved the gate.

## Resolution: key the gate on the search space (EV-4)

The fix is `schema_hash()` — the identity of the *search space* (the gene
**names**, not their values) — threaded through `_compute_streak` and
`_sprt_history`:

- a row from a different `schema_hash` is **skipped, not treated as a break**,
  so each arm assembles its own contiguous history out of the interleaved
  stream;
- `scan` is widened above `limit`, because skipping consumes budget and a
  6-row window under 100% alternation would only ever surface 3 same-arm rows;
- rows written before EV-4 carry no `schema_hash` and are treated as a
  **different** arm — fails closed.

This is the *third* instance of one recurring defect shape in the file:
`baseline_hash` (EV-2) fixed it when a mid-era baseline change let wins against
two references count as one streak; Cranium fixed it when an era change broke
the SPRT's evidence; EV-4 fixes it when the schema moves.

Validated by replay before adoption (`tools/evolution_backfill.py`): 500 stored
rows, `schema_hash` derived retroactively from `champion_genes` (498 backfilled,
2 already tagged, 0 UNKNOWN), real gate functions re-run — outcome
`any_promotable=TRUE`, `best_streak_seen 3/3`.

## Live evidence that the mechanism is now stabilised

`state/loop_integrity.json` (2026-10-01T16:16:55, hub):

| field | value |
|---|---|
| `current_alternation` | **0.0** (recent 12 cycles) |
| `current_schemas` | `["by_session"]` |
| `schema_alternation_rate` (all-time, 203 cycles) | 0.213 (was 0.91–0.98 at 45 cycles) |
| `by_session` arm | n=181, 180 comparable pairs, streak possible |
| `use_schema_features` arm | n=22, 21 comparable pairs, streak possible |

Remaining DEGRADED is `CURRENT NO PROMOTION: 0 promotions in the last 12
cycles` — a gate/streak condition, **not** schema thrash and **not**
`genome_seed`.

## The finding: the fix was uncommitted hub work

The fix and its instruments existed **only as uncommitted changes in the hub**
(`C:\Users\clint\azazael`):

- `scripts/evolution_cycle.py` — modified, **+387/−11**, untracked-in-history
  (never on any branch, including `origin/master` and `origin/r15/...`);
- `tools/evolution_progress.py`, `tools/evolution_backfill.py`,
  `tools/fitness_arm_liveness.py` — untracked (`??`).

The live tree (`C:\Azazael\azazael`) — the editable-install target — had none of
it, and `evolution_backfill.py` calls `evolution_cycle.schema_hash`, so the
pieces are a **coupled unit**: adopting the tools alone would have shipped a
broken instrument. This is the same failure class as the silent-origin-lag
defect fixed earlier the same day: work that cannot be seen by the tree that
needs it.

## Adopted (commit `7bb1922e`)

- `scripts/evolution_cycle.py`: EV-4 (`schema_hash`, schema-keyed
  `_compute_streak` / `_sprt_history`, `schema_hash`/`schema_gene` written into
  result rows); EV-5 (`FITNESS_ARM_VETO` objective-arm liveness); EV-6
  (`_extract_alert_pool`, select the alert arm by severity column); EV-7
  (`_loop_integrity_gate`, the loop's own current health gates promotion).
- `tools/evolution_progress.py`, `tools/evolution_backfill.py`,
  `tools/fitness_arm_liveness.py`.

Note: the uncommitted diff labels the schema change "EV-4" while the *tracked*
file already uses "EV-4" for the meta-search floor work — a **numbering
collision**, not a duplicate change. Both are present and distinct.

## Verification

- `python3.14t -m py_compile` on all four files: clean.
- `tests/test_evolution_gates.py test_evolution_helpers.py test_proteus_hooks.py
  test_proteus_organs.py`: **238 passed**.
- `tests/test_wiring_cycle.py test_learning_evolution.py
  test_learning_closure.py`: 124 passed, 4 failed — the 4 fail **identically on
  the pre-adoption committed file** (verified by checkout/restore), so they are
  pre-existing and unrelated.
