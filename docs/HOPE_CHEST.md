# HOPE CHEST — priced future work, kept stocked fresh

**Last stocked:** 2026-11-07 (session: AETHER upgrades A-1..A-6, see below).
**Refresh rule:** every session re-stocks this chest — mark LANDED with the
commit hash, re-price anything whose size changed, and add newly discovered
gaps. A chest that is not re-stocked is stale, and stale is forbidden.
**Prices:** XS (<15 lines) · S (<50 lines + tests) · M (<150 lines + tests) ·
L (multi-file or box work). Price is cost-to-land, paid in full on landing.

## STOCKED — recall layer (morph-space)

| # | Item | Price | Status |
|---|------|-------|--------|
| H-01 | Shape gene: `shape` on WormDNA, fitter-parent inheritance, 5% morph mutation | M | LANDED (commit below) |
| H-02 | Icosahedron hub: 12 slots / deg 5 / diam 3 | S | LANDED (commit below) |
| H-03 | Weighted edges: Dijkstra recall, uniform weights reproduce BFS exactly | M | LANDED (commit below) |
| H-04 | Persist ShapeStore: `to_dict`/`from_dict` | S | LANDED (commit below) |
| H-05 | Transmogrify guardrails: `max_diameter` + `min_girth` (girth via edge-avoiding BFS) | S | LANDED (commit below) |
| H-06 | Transmogrify engine: MUTATE / TRANSMOGRIFY / TRANSSUBSTANTIATE / SWARM | M | LANDED (commit below) |
| H-12 | CONJOIN + SEPARATE: merge two stores, split one by predicate | S | LANDED (commit below) |
| H-13 | DISSOLVE: delete entries, unregister dead solids (registry rot kills morph-spaces) | XS | LANDED (commit below) |
| H-14 | FERMENT: salience-weighted decay so the solid holds living memory | M | LANDED (commit below) |
| H-15 | MULTIPLY: grow/shrink the swarm with rebalancing | M | LANDED (commit below) |
| H-16 | PROJECTION in all forms: JSON + frozen .py + chronicle | S | LANDED (commit below) |
| H-17 | Micro-swarms: heterogeneous solids, shard-local morph/ferment, assemble_swarm | M | LANDED (commit below) |
| H-18 | Bibles: RULE 0Z-Q tapestry rule, E2R-5 agreement fix, 60-target sync clean | S | LANDED (commit below) |
| A-1 | Gate replays the live log: dream agreement holds the floor | S | LANDED (commit below) |
| A-2 | Floors retune from evidence, refuse on noise (<20 pairs) | S | LANDED (commit below) |
| A-3 | Findings ledger: new -> persisting -> fixed, re-verified every run | M | LANDED (commit below) |
| A-4 | Adversarial auditors: sabotaged verdicts the gate must catch | S | LANDED (commit below) |
| A-5 | Verdict projection: machine JSON + human chronicle + history rows | S | LANDED (commit below) |
| A-6 | Heterogeneous verification swarm: per-domain checks, one rolled verdict | M | LANDED (commit below) |

## STOCKED — training loop

| # | Item | Price | Status |
|---|------|-------|--------|
| H-07 | Unlock render/stealth rungs: playwright+chromium+curl_cffi live under py316t | M | LANDED (commit below) |
| H-08 | Dream agreement metric: blocked-blocked counts; stateless legacy logs keep old rule | S | LANDED (commit below) |
| H-09 | Pop 4→8 (trainer + CLI defaults); calibration map from measured rung hit-rates | S | LANDED (commit below) |

## STOCKED — upstream / box / ledger

| # | Item | Price | Status |
|---|------|-------|--------|
| H-10 | Push pythran issue from draft to filed; watch Pillow #10455 for review | S | STOCKED (draft not found under docs/ — needs its location) |
| H-11 | Record outcomes batch | XS | LANDED (standing rule: every landing commits its chest line) |

## LANDED — paid in full

| Item | Evidence |
|------|----------|
| `eve train` + Lillith tuner | commit `c0216f02` — 9 tests green, live gen-5 proof best 0.7385 |
| Inspiration trio: teacher bias + hunch crossover + dream-to-gene flow | commit below — 18 trainer + 11 recall tests green |
| Transmogrify engine: validated solid registration, degree-preserving mutation, re-homing, hypercube swarm | commit below — 16 recall + 18 trainer tests green |
| PROJECTION: `cast_projection`/`write_projection` — JSON reloads anywhere, .py rebuilds with no trainer, .md records lineage | commit below — 19 recall + 18 trainer tests green |
| Full lifecycle: conjoin/separate, dissolve_key/unregister_shape (builtins refuse), ferment (dict or callable salience), swarm grow/shrink/rebalance without loss | commit below — 26 recall + 18 trainer tests green |
| Recall depth (H-02..H-05): icosahedron pinned, girth, guardrails, Dijkstra, persist | commit below — 33 recall tests green |
| Evolution depth (H-01/H-08/H-09): shape gene + fitter inheritance, agreement metric, calibration, pop 8 | commit below — 25 trainer + intuition tests green |
| E2E `eve train --gens 2 --pop 4` live: gen1 best 0.8332 dream 0.708, gen2 best 0.8316 dream 0.771 | this session, isolated paths |
| Micro-swarm assay (64 keys): hypercube-32x2 64 visits/hops 5, dodeca-x4 80/5, petersen-x8 80/hops 2 | this session — hops fall as solids shrink |
| Bibles: RULE 0Z-Q (knit/unknit), E2R-5 source + pointer fixed, sync 60 targets 0 problems | commits below |
| Rungs unlocked (H-07): playwright/chromium render + curl_cffi stealth proven live | this session |
| Shape-parametric recall, 6 solids + morph_store | commit `a0feb600` — 11 recall + 9 trainer tests green |
| EVOLVE-TO-RESOLVE canon (RULE 0Z-P) | commit `abd5c95a` — 67 targets in sync |
