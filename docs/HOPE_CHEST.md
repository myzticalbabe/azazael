# HOPE CHEST — priced future work, kept stocked fresh

**Last stocked:** 2026-11-07 (session: morph-space landed as `a0feb600`).
**Refresh rule:** every session re-stocks this chest — mark LANDED with the
commit hash, re-price anything whose size changed, and add newly discovered
gaps. A chest that is not re-stocked is stale, and stale is forbidden.
**Prices:** XS (<15 lines) · S (<50 lines + tests) · M (<150 lines + tests) ·
L (multi-file or box work). Price is cost-to-land, paid in full on landing.

## STOCKED — recall layer (morph-space)

| # | Item | Price | Status |
|---|------|-------|--------|
| H-01 | Lillith tunes the shape: `shape` as a genome gene, selection picks the solid per phase | M | STOCKED |
| H-02 | Icosahedron hub: 12 slots / deg 5 / diam 3 (promised NEXT in `dodeca_recall.py`) | S | STOCKED |
| H-03 | Weighted edges: rung-aware costs + Dijkstra recall, gated behind `weighted=True` | M | STOCKED |
| H-04 | Persist ShapeStore: `to_dict`/`from_dict` snapshot beside the pop file | S | STOCKED |
| H-05 | Transmogrify guardrails: diameter ceiling + girth floor on evolved solids | S | STOCKED |
| H-06 | Transmogrify engine (designed, unlanded): MUTATE / TRANSMOGRIFY / TRANSSUBSTANTIATE / SWARM | M | STOCKED |

## STOCKED — training loop

| # | Item | Price | Status |
|---|------|-------|--------|
| H-07 | Unlock render/stealth rungs: install playwright + curl_cffi under py316t, verify live e2e | M | STOCKED |
| H-08 | Fix the dream metric: blocked guesses cannot hit (ceiling ~0.5 on current URL set) | S | STOCKED |
| H-09 | Scale pop 4→8 after H-08; calibrate confidences from dream bins, not fixed 0.9/0.7 | S | STOCKED |

## STOCKED — upstream / box / ledger

| # | Item | Price | Status |
|---|------|-------|--------|
| H-10 | Push pythran issue from draft to filed; watch Pillow #10455 for review | S | STOCKED |
| H-11 | Record outcomes batch (recall landing + morph-space + stale-method replacements) | XS | STOCKED |

## LANDED — paid in full

| Item | Evidence |
|------|----------|
| `eve train` + Lillith tuner | commit `c0216f02` — 9 tests green, live gen-5 proof best 0.7385 |
| Inspiration trio: teacher bias + hunch crossover + dream-to-gene flow | commit below — 18 trainer + 11 recall tests green |
| Shape-parametric recall, 6 solids + morph_store | commit `a0feb600` — 11 recall + 9 trainer tests green |
| EVOLVE-TO-RESOLVE canon (RULE 0Z-P) | commit `abd5c95a` — 67 targets in sync |
