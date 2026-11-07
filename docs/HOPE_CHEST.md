# HOPE CHEST — priced future work, kept stocked fresh

**Last stocked:** 2026-11-07 (session: native replay N-1 + per-rung U-2 + gap ledger seeding, see below). No cap: every gap gets a row.
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
| H-10 | Pythran draft: searched docs/ + tree, only vendored scipy hits; draft unfindable, ended-search recorded; native route proven via Cython instead (N-1) | S | CLOSED (ended-search + superseded, evidence below) |
| N-1 | Native replay: Cython kernel `_replay_cy` built with MSVC 14.51, parity vs dream tested, 6x on 20k pairs; pythran 0.19 present but its headers reject cl and no clang-cl on box (that verdict IS the pythran answer) | M | LANDED (commit below) |
| U-2 | Per-rung floors: leg holds the weakest qualifying rung (>=5 pairs), floor tuner writes global + rung floor | S | LANDED (commit below) |
| U-1 | Arm the floor: replay kilo's per-env logs (20+ pairs), run agreement_floor per env, A-1 goes strict | S | STOCKED (blocked on kilo logs) |
| U-4 | Lillith tunes the swarm: shard shapes as a genome, fitness = hop-depth + isolation misses | M | STOCKED (kilo turf) |
| U-5 | Web leg: second provider or honest single-source label on the verdict | M | STOCKED |
| U-6 | Cross-env convergence comparison at fixed seed 316 (needs kilo's rows) | M | STOCKED (blocked on kilo) |
| D-1 | Denominator-free 4 (esquire_capture, hook_evidence, one_click, pin_audit) — owning lanes | M | STOCKED (ledger tracks under hyper_edge) |
| D-2 | Golden-arrow 6 failed (2026-11-05 baseline, 537 files) — owning lanes | L | STOCKED |
| D-3 | servemesh:ModelShardServerWorm.verify token-only wired row (commit cc9dcf0a predates this session; never rebaseline foreign debt) | S | STOCKED (ledger new; owner: servemesh lane) |
| D-4 | Credential rotation: 0 rotations recorded (absence of evidence, not freshness) | S | STOCKED (ledger new under evidence_gate) |
| D-5 | orphan interp.* knobs x6 + bypass_reader + fallback_drift (pre-existing, not this session) | S | STOCKED |
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
| Forensics 2026-11-07T17:08Z: 5 legs, ast_audit ok (5662 parsed, 0 syntax), kernel NATIVE-WITH-PARITY, verdict FAIL (evidence_gate wired_claims + rotation; hyper_edge only via claim_agreement BLIND, no live log) | this session |
| Seeded: logs/verdict.md rewritten, verdict_history.jsonl row 1, aether_findings ledger new=2 (evidence_gate, hyper_edge) | this session, gitignored logs/ |
| Native build recipe (this box): MSVC 14.51 + SDK 10.0.26100.0 + C:/Azazael/.py316t headers; cython -3 _replay_cy.pyx; cl //c //nologo //O2 //MD //EHsc -DPy_GIL_DISABLED=1; link //DLL //EXPORT:PyInit__replay_cy python316t.lib | this session, exit 0 |
| Rungs unlocked (H-07): playwright/chromium render + curl_cffi stealth proven live | this session |
| Shape-parametric recall, 6 solids + morph_store | commit `a0feb600` — 11 recall + 9 trainer tests green |
| EVOLVE-TO-RESOLVE canon (RULE 0Z-P) | commit `abd5c95a` — 67 targets in sync |
