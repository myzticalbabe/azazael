# Forensic Treatise: Eve Connectance Verification Method

Date: 2026-11-07. Scope: Eve turf (`src/eve_unleashed/`, `state/honey/`, Eve tests).
Status: method in force; numbers below measured on py316t 3.16.0a1t, free-threaded.

## 1. What is claimed (and what is not)

Claimed: every Eve connectance number is recomputable from source by a
stranger with one command; every verdict seals its inputs; the scheduled
sweep fails loudly naming the liar. NOT claimed: 100% error-free (a claim
without a command is recollection), anything outside Eve turf
(arc-container gaps and the Kali atlas are named foreign debt in PR #1).

## 2. The method, mapped to admissibility (Daubert)

1. **Testability.** Two negative controls mutate copies of the real
   manifest (`tests/test_eve_resweep.py`): a flipped blob digest FAILs
   naming seal+root; a bumped dodecahedron diameter FAILs naming
   solid.field. The native kernel asserts byte-equality with Python on
   all 7 solids (`tests/test_eve_native.py`).
2. **Known error rates.** Priced, not promised: Moore efficiency
   (petersen/complete-20 = 1.000, cube = 0.019), fault-stretch
   (ring 1.8, mesh 1.0, zero disconnects all solids), spectral gap
   ordering (petersen > dodeca > cycle). The product
   fault-stretch/moore-efficiency is the price column.
3. **Standards.** Refusal discipline (unknown solids refused naming the
   registry; empty funnels refused), chain-of-custody (blobs -> manifest
   -> proof -> audit, relative paths so a fresh clone replays), no
   silent success (unreadable manifests FAIL every chain; missing
   columns FAIL).
4. **Replay.** `PYTHONPATH=src python -m eve_unleashed.resweep`
   (exit 0/1). Build the kernel: `python tools/build_native.py
   src/eve_unleashed/_forensic_cy.pyx` (.pyx travels; .pyd is
   gitignored build output).

## 3. The common thread

One equation roofs all solids, regimes, laws:
`n <= 1 + d*((d-1)^k - 1)/(d-2)`. Every audit leg answers one question:
can this artifact be audited (denominator, self-visibility, states,
gaps)? The recursion terminates at hashes, which do not argue.

## 4. Residuals (honest, stapled)

- Spectral gap is measured but not yet embedded per-epoch; the manifest
  carries one snapshot.
- Retune thresholds are heuristic v0; Lillith has not moved them yet.
- Whole-tree tier still red on foreign legs (named in PR #1), which is
  why pushes declare `EVIDENCE_TIER_BYPASS=1` loudly instead of
  passing quietly.
