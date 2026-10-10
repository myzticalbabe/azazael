# EVIDENCE.md — the artefacts behind this repo's numbers

Written 2026-10-10 to close flaw **S6** ("Evidence lives outside version control") in
`STRUCTURAL_FLAWS_315T.md`: the files that justify this repo's adoption, reachability
and suite claims lived under the gitignored `state/`, so a claim in a commit message
had nothing inside the repository to check it against.

`.gitignore` now un-ignores exactly **three** files — not `state/` itself, because most
of that directory is live runtime state that must never be reverted by a checkout.

Every count below was **read out of the artefact in front of it**, not recalled. The
command regenerates the file; if a number here ever disagrees with the file, the file
is the authority.

| artefact | claim it supports | how to regenerate |
|---|---|---|
| `state/adoption_census.json` | T-15: how many catalogued techniques have a caller in a **different production module** — an exercise-only caller scores zero. Read in it: `rows` 141, `adoption_score` 99, `in_production` 114, `built_count` 118; tally `ADOPTED` 99 / `HOST-COMPOSED` 15 / `EXERCISE-ONLY` 4 / `NO-TARGET` 23 (sums to 141). | `python tools/adoption_census.py --json state/adoption_census.json` |
| `state/orphan_scan.json` | which of `src/`'s modules no shipped entry point reaches. Read in it: `n_modules` 701, `n_reachable` 309. | `python tools/orphan_scan.py --json state/orphan_scan.json` |
| `state/suite_baseline.jsonl` | the green-suite claim (flaw S7). One JSON record per batch. Read in it: batches 0–13 covering 264 test files, with **batch 6 recorded twice** — first `returncode` 1 (`2 failed, 275 passed`, the two `tests/test_mesh_wire_or_cut.py` failures) and then `returncode` 0 (`277 passed, 1 skipped`) after the fix. The failed record is kept on purpose: a retried batch that erases its own failure is not evidence. | `python tools/suite_baseline.py` (resumes — only batches that are not green are re-run) |

## The counters, and what makes each able to fail

A number is only as good as the instrument's controls, so the adoption census ships its
own and they are part of the evidence:

```
python tools/adoption_census.py --self-test
```

- **positive control** — `merge_sops` must be found at `tools/canon_drift_check.py`; a
  miss means the tool cannot see a caller it is known to have.
- **negative control A** — a docstring `Usage:` line must NOT be counted as a call site,
  or the count is prose-inflated.
- **negative control B** — at least one row must score `EXERCISE-ONLY`, or the tool
  cannot tell the exercise layer apart from production at all.
- **control C, both ways** — the qualified symbol `CascadeRouter.route` must match
  **nothing** in `scripts/fetch_990_series.py` (whose prose contains "full_text route is
  the practical extraction path"), and must match the real `router.route(...)` call in
  `src/CORE/technique_wiring/_l5_dispatch.py`.

## Not tracked here, and why

- **`state/sota_batches/batch06/`** — the re-check docs, and the technique map
  (`technique_codebase_map.json`) every adoption number is bounded by (flaw S5). These
  resolve to `<repo-parent>/state/sota_batches/batch06/`, i.e. **outside this
  repository**: `azazael/state/sota_batches/**` matches zero files. No `.gitignore` rule
  in this repo can reach them; they must be copied in before they can be tracked.
- **The rest of `state/`** — live runtime state, ignored deliberately (see the
  "Runtime-state buckets" and `evolved_rl_params` comments in `.gitignore`).
- `state/THEATER_REMOVAL_TASKS_2026-10-10.md`, `state/WIRE_DECISIONS_2026-10-10.md` and
  `state/ACTION_REGISTRY_2026-10-10.md` are **cited as evidence** by
  `STRUCTURAL_FLAWS_315T.md` but are still ignored — they were not in the named set for
  this change. Add them the same way if the removal and wiring record also has to be
  reproducible from a clone.

## Discrepancy worth knowing

`STRUCTURAL_FLAWS_315T.md` §S7 says "batch 7 found 2 real failures". The journal records
those two failures in **batch 6** (`returncode: 1`). The artefact is the authority here;
the prose is off by one batch.
