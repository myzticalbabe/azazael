---
name: azazael-stale-artifact-self-audit
description: Two defect classes that made this architecture report success while wrong — confidently-incomplete artifacts (cached/generated state answering for a tree it no longer describes) and unvalidated instruments (a metric used for destructive verdicts without a self-check). Load before trusting any generated count, census, probe or cache, and before acting on a similarity/score that can delete capability.
metadata:
  category: verification
  project: azazael
  priority: high
  auto_load: false
---

# Stale-Artifact and Unvalidated-Instrument Self-Audit

Both classes share one shape: **a number that is fast, plausible and wrong, with
nothing reporting a problem.** Every instance below was found by measuring the
claim against the thing it described, never by reading the claim.

## Class 1 — Confidently-incomplete artifact

Generated or cached state that answers confidently for a tree it no longer
describes. It is worse than missing state, because it is trusted.

Instances found (2026-09-18, all measured):

| Artifact | Claimed | Reality | Why the check missed it |
|---|---|---|---|
| `NEURAL_MESH_WIRE_OR_CUT.json` | 117 rows, 0 undeclared | PF16 live = 113, then **174** | generated 09-16; test was RED with 4 undeclared rows |
| PF16 probe itself | bare-name uses | counted **tests** as production reachability | docstring promised "outside tests" and never returned it; 62 functions looked wired with no production caller |
| `worm_registry_cache.pkl` | fresh (mtime OK) | held **111 of 229** worms, 24 of 35 categories | mtime-only freshness; a scan built from unchanged sources is self-consistently "fresh" |
| `test_worm_registry_cache_freshness.py` | passing contract | module had no `_registry_fingerprint` at all | 6 tests red; the spec was written 09-14 and never implemented |
| `AZAZAEL_LOCAL_MODEL_OPERATOR_TODO` counts | 17 records | **15** — 2 were a different task | `--rescore-all` scored them against the wrong ground truth |

**Rule 1 — separate currency from safety.** "Does this artifact match its
sources?" and "may this artifact be served at all?" are different questions. A
cache can be perfectly current and still be missing half the fleet. Implement
them as two predicates (`_is_cache_fresh` vs `_load_cache_readonly`), not one.

**Rule 2 — make the artifact self-report its coverage.** `save_cache` records
`_coverage = {declared_on_disk, registered, excluded_unpicklable, complete}` and
refuses to call a partial scan complete. An artifact that cannot state what it
covers cannot be audited.

**Rule 3 — get a second opinion that does not share the failing machinery.**
`_count_declared_worms()` counts `@register_worm` decorators by TEXT, not by
importing, precisely because the failure it guards against is an import-time
undercount. Re-running the same machinery to check itself proves nothing.

**Rule 4 — a guard that cannot fail is worse than no guard.** The first version
of the coverage guard used `re.compile(r"^\s*@register_worm\b")` without
`MULTILINE`, so `^` anchored to the start of the string, the count came back 0,
and `registered >= 0` passed vacuously for every cache including an empty one.
Pin every guard with a test that fails when the guard is disabled.

**Rule 5 — an exception swallowed as "non-fatal" is a stale artifact factory.**
`discover_worms` wrapped `save_cache()` in `except Exception: pass`. Any
unpicklable entry (`test_worm_registry.test_concurrent_registry_reads.<locals>.
ReadTestWorm`) raised `PicklingError`, the save never happened, and the OLD
cache kept answering. Failure is now logged, and unpicklable entries are
excluded per-entry instead of failing the whole save.

## Class 2 — Unvalidated instrument

A metric used to make a destructive decision, with no check that it
discriminates on cases whose answer is known.

The case: `DedupAnalyzer` compared worm method-name sets by Jaccard.
`Jaccard({x}, {x})` is **1.0**, so any two worms sharing one generic verb
(`execute` alone on **86 of 202**) scored `exact_signature` at 1.0. Measured on
the live fleet: **1529 pairs reached the threshold and 1529 were rejected by the
calibration — every single one a false positive.**

`BlackQueenWorm` consumed that score to decide retirements and proposed retiring
**35 worms, including `EvolutionEngine`, `DreamingModule`, `GeneticOptimizer`
and `HypnagogicSynthesizer`**, in favour of unrelated security and profiling
worms. A retirement sets `lifecycle_state='retired'`, which `NatureCluster`
honours — so the learning subsystem would have left the pipeline. **No test
constrained that contract at all.**

**Rule 6 — an instrument that judges must pass control pairs first.** Three
controls, each pinning one rule, both directions:
`interface_only` (must NOT match), `same_name_different_work` (must NOT match),
`genuine_twins` (MUST match at 1.0 — otherwise the rules are too strict and real
duplicates are missed).

**Rule 7 — "cannot verify" is a failure, not a pass.** `BlackQueenWorm.propose()`
calls `_metric_check()` first and returns
`similarity_metric_failed_self_check` rather than acting when the comparator
cannot be validated. An unreadable tree yields no implementation tokens, so the
`genuine_twins` control fails and the verdict is refused.

**Rule 8 — never let one mechanism both detect and delete.** Detection
(`candidates()`) is the backlog view; deletion (`propose()`) is the decision.
Guards that stop a bad action belong in the decision, not the report.

**Rule 9 — parallel implementations are not duplicates.** `WslUbuntuWorm` and
`WslKaliWorm` share a method set *by construction*; they are one bridge per
environment the mesh must run in (`W11`, `WSL2-Ubuntu`, `WSL2-Kali`, `Bare`,
`G:`). `propose(force=True)` selected `WslKaliWorm` as covered by
`WslUbuntuWorm` — a different distro. Retiring it removes that environment's
ability to run the mesh. See `BlackQueenWorm.ENV_PARALLEL_CATEGORIES`.

## Procedure

```bash
# 1. Is the fleet complete? (the one that silently halved it)
python -c "from CORE.worm_registry_cache import cache_status;import json;print(json.dumps(cache_status(),indent=1))"
#    coverage.complete must be true; registered should exceed declared_on_disk

# 2. Is the census current?
python -m tools.mesh_function_preflight --summary     # compare to the tracked table
pytest tests/test_mesh_wire_or_cut.py -q              # red means undeclared rows

# 3. Can the comparator be trusted before it deletes anything?
python -c "from CORE.worm_governance import DedupAnalyzer;import json;print(json.dumps(DedupAnalyzer().self_check(live=True),indent=1))"
#    trustworthy must be true; live.rejected_by_calibration shows the false-positive mass

# 4. Are the tests green for the file, and green in the batch?
pytest <file> -q && pytest <file> <other> -q
#    a file that passes alone and fails in a batch is polling state through the
#    registry, the spine or a shared cache
```

## The two questions to ask of any number

1. **When was this measured, and against what?** If the answer is a stored
   artifact, re-measure before acting.
2. **What did it do on the cases whose answer I already know?** If that was never
   checked, the number is not evidence yet.
