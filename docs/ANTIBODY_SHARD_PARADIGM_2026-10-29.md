# Antibody Shards: errors that seek every instance of themselves (paradigm exploration, 2026-10-29)

Question: how do we shard each error into a self-seeking anti-body that finds
every exact instance of itself?

Short answer: the tree already owns 4 of the 5 organs. The missing one is
small — a signature-deriver that turns one observed failure into a probe.
Everything downstream (sweep, ratchet, immunity memory) exists and is gated.

## 1. The organs, measured in this tree

| Immune role | Existing organ | Evidence |
|---|---|---|
| Exposure log | `src/CORE/failure_ledger.py` — `note_failure(where, exc)` keys `where:ExcType` with counts, stdlib-only leaf, never raises, `_LOST_NOTES` so undercount is visible | 40+ call sites in INTERPRETERS/SHARDS alone; all D/E-series fixes record through it |
| Seeker fleet | `src/CORE/compliance/scanner.py` — regex + AST probes over `src/`, findings as `(line, category, snippet)` | 2,231 findings across 737 files; categories carry severity + fix text |
| Immune memory | `tools/anti_pattern_gate.py` — category-count baseline, fails on increase | This session twice drove new code back to exactly 2231 = baseline |
| Precedent: retired pathogens | `t_string`, `os_system`, `cls_new_factory` driven to zero and held there | A rule at zero baseline IS immunity memory — the infection is gone and the detector stays |
| Clonal selection (fitness) | `src/CORE/morphed_trainers.py` — NSGA-II front + `promote()` gate + collision-safe registry | Proposals compete; only measured winners persist; cross-host collisions keep both |

The gap: every scanner rule was hand-authored from an audit. Nothing derives a
probe FROM a single observed error instance. That derivation is the antibody.

## 2. The antibody, precisely

An antibody is a detector cloned from one error instance, not written from a
category. Structure (JSON-serializable — it is a shard payload):

```
{
  "signature": {            # stable identity of the error KIND
    "namespace": "sh_runner",       # module, never a line number
    "handler_role": "exec-fallback",# what the handler was doing
    "exc_type": "TimeoutExpired",   # or "none" for wrong-result bugs
    "message_shape": "The system cannot find ...",  # values abstracted
    "ast_shape": "ExceptHandler[Pass]"               # when structural
  },
  "probe": { "kind": "regex|ast", "pattern": "..." },  # synthesized
  "first_seen": "2026-10-29T…Z",    # from the ledger key's debut
  "instances": ["src/…:line", …],   # every exact match the sweep finds
  "status": "seeking|neutralized|immune"
}
```

Why not the ledger key as-is: today's keys embed line numbers
(`go_runner:L128`). Line numbers rot on every edit above them — an antibody
keyed that way attacks moved code and misses the error. The signature must use
the enclosing handler's role (function name), never its line. This is the same
lesson as the ratchet's category-counts design (identities over positions
invalidate on edit; counts don't).

## 3. Lifecycle (maps 1:1 onto the existing gates)

1. **Exposure.** A failure is recorded (`note_failure`) or found by hand, as
   the E-series was: bash-not-bash, seq-sum, pwsh message, stale routing.
2. **Cloning.** A deriver reads the ledger key + the handler source at `where`
   and synthesizes the narrowest probe that matches the instance: message
   regex first (cheap, e.g. `seq 1 20000` → `seq\s+1\s+20000`), AST shape when
   the bug is structural (e.g. `ExceptHandler` with single-`Pass` body —
   which is exactly how `silent_except_pass` already fires).
3. **Seeking.** The probe sweeps the tree on the same schedule as `--sweep`
   (a `--seek` analogue): cold recompute, JSON report, no handles.
4. **Neutralization.** Instances are fixed conformingly (change the code, never
   suppress the gate — the reflex this session proved twice).
5. **Immunity.** Count hits zero; the antibody is recorded at zero baseline.
   It keeps running. A reintroduction fails the gate the way tonight's
   `import_inside_function` +7 did — caught before commit, hoisted, re-green.

Each status transition is a ledger-noted, committable event. An antibody never
deletes itself: retired detectors are the memory.

## 4. First clonal line (from tonight's own errors)

| Antibody | Signature | Probe |
|---|---|---|
| `seq-range-mismatch` | work golden sums ≠ EXPECTED_SUM | work-tier agreement test (already built — it IS this antibody's seeker) |
| `dispatcher-not-the-language` | `shell=True` behind a language name | `shell\s*=\s*True` exists as a scanner rule, but scoped to injection; the antibody narrows it to dispatcher paths |
| `skip-contract-case` | toolchain message without lowercase "not found" | regex over `_no_toolchain` stderr strings vs the contract substring |
| `stale-table-routing` | `_measured_order` spends medians while stale | the MAX_AGE=-1 fallback test (already built — also an antibody seeker) |

Note what happened: E1's work-tier test and the stale-fallback test are
already antibodies in the precise sense defined here — detectors cloned from
observed instances that seek every recurrence. The paradigm names what the
session already did twice.

## 5. Shard fit (why "shard" is the right noun)

A shard is one capability contract with implementations behind a shared
JSON-serializable result shape, plus router + self-test (`src/SHARDS/`).
An antibody fits without new machinery:

- manifest entry: `{paths, langs: ["python"], canonical: "python"}` —
  antibodies are Python probes over the tree;
- `run`: execute probe, return instances as JSON;
- `self-test`: the probe matches its own first instance (a detector that
  cannot find its parent is a dead antibody — this is the self-seeking
  property made testable);
- router: error namespace → antibody shard, the same keyword top-1 shape as
  `route_shard`.

## 6. Deliberately not built yet (open questions for owner)

1. **Deriver automation.** Tonight cloning is manual (human reads the error,
   writes the probe). Full synthesis (ledger key → probe) needs a tool
   (`tools/antibody_derive.py`) and a false-positive budget: regex probes
   over-pursue, AST probes under-pursue. Pilot with manual cloning; automate
   only after five antibodies prove the shape.
2. **Sweep ownership.** Pre-commit (like the staged scanner) or scheduled
   (like `--sweep`)? Seeking is slower than categories — nightly `--seek`
   with pre-commit enforcement only for `immune`-status antibodies is the
   honest split: the past must not regress, the present may still be seeking.
3. **Antibody storage.** Candidates: `src/CORE/compliance/antibodies/*.json`
   (data, needs a loader) vs generated rule functions in the scanner (code,
   needs a generator). Data first — a JSON antibody the scanner loads is
   reviewable in a diff; generated code is not.
4. **Kilo's lane.** Kilo is attaching the first real `trained_reward` now.
   The symmetric question: does kilo also mint antibodies from training
   failures (diverged runs, NaN rewards), or do training-path antibodies stay
   local until the outer loop closes? Undecided — flagging, not blocking.

## 7. Minimal pilot (if approved)

1. One JSON antibody for `seq-range-mismatch` under
   `src/CORE/compliance/antibodies/`, loaded by the scanner as an extra rule.
2. `tools/antibody_derive.py --from "ledger-key"` that prints a candidate
   probe + the instances it finds (derive-only; promotion stays manual).
3. Status line in the session-improvements log when an antibody retires.

No new runtime, no new gate, no new dependency. Three files.
