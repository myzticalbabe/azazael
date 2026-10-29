# Session Improvements — 2026-10-29 (8 commits, all green)

Evidence: `git log --oneline -8` f3d38b20 → 26844848. Tree clean, sync PASS,
pytest 19 + 6 green, StagedScanner clean, paradigm 0, ratchet 951→950.

## What worked (keep)
1. **Fix-conformingly reflex.** Three gate rejections (bulk-focus, 2
   hardcoded-path + silent-except, G1 missing test, ratchet +3) were each
   fixed by changing the code, never by suppressing the gate. The ratchet
   now reads better than baseline as a side effect.
2. **Measure before routing.** The sweep table (python 0.0 → pwsh 228.2ms)
   replaced keyword guessing. Every router from here should spend measured
   numbers.
3. **One-file-per-commit for others' work.** The three foreign files landed
   separately with honest messages instead of being swept into a bulk.

## Improvements, ranked by payoff

### P1 — Close the remaining honesty gaps
1. **Go timing is still dishonest.** Rust was fixed (compile+run summed);
   `GoRunner.run_code` writes to a hashed file then `go run`s it — the
   write+compile cost is not separated from run in `duration_ms`. Split
   it the same way or the rust-vs-go comparison lies by one compile.
2. **`sweep.json` has no freshness check.** A stale table silently drives
   `route_lang`. Add `max_age_hours` + a warning when the sweep predates
   the runner code (mtime compare against INTERPRETERS/*.py).
3. **`morphed_registry.json` is git-ignored or committed?** Decide now.
   If winners are property, the registry is a deed book — it must be
   committed and synced. Currently unclear whether it lands in the tree.

### P2 — Harden the new seams
4. **Golden fixtures are hello-world only.** Agreement on a printed token
   proves the pipe works, not the contract. Add argv-echo, stdin-JSON,
   nonzero-exit, and stderr-shape goldens per language (the gateway pair
   already defines the behavioral bar).
5. **`pwsh_runner` module probes shell out twice** (probe + run). Cache
   the PSScriptAnalyzer/Pester presence per process; probes cost ~200ms+
   each at pwsh startup prices.
6. **`run_bash` (shell=True) still sits beside `ShRunner`.** Two bash
   paths is one too many. Deprecate `run_bash` to an explicit
   `run_shell_untrusted()` name so the argv-only default cannot be
   confused with the designated shell path.

### P3 — Process and docs
7. **`--sync-to` legs re-copy 2085 files every run.** Hash-compare before
   copy (mtime+size fast path, sha on mismatch) — tonight's three full
   re-syncs were minutes that content addressing would make seconds.
8. **Review doc lives in two places.** `MULTILINGUAL_SHARD_REVIEW` was
   written to `C:/Users/clint/` then copied to `docs/`. Write directly
   to the repo path; the copy step is a divergence risk.
9. **Kilo's evidence gate vs our commit gates diverge.** Kilo posts
   sha+quote+raw+2keys on the board; we pass StagedScanner+paradigm+
   ratchet locally. One checklist naming both, posted where kilo reads
   it, ends the "which gate?" confusion seen earlier tonight.
10. **Sweep on every runner change.** Make `--sweep` a pre-commit hook
    input when INTERPRETERS/* changes, so the table can never silently
    describe last month's toolchains.

## Suggested order
P1 items first (honesty), then P2 (seams), then P3 (process). Item 1+2
are a single session; item 6 is a rename with a deprecation shim.
