# Interpreter self-maintenance — the three missing pieces (2026-11-07)

**Owner:** freebuff lane. **Tool:** `tools/interp_cycle.py` (one file, four
subcommands). **Knobs:** `config/defaults.json` → `interp.*`.
**Tests:** `tests/test_interp_cycle.py` (pure logic; live legs run via the tool).

## Why this exists

The repo evolve loop tunes repo knobs. It cannot see upstream CPython defects,
compile C, or restart onto a new engine. Those three gaps are now commands:

| gap | subcommand | cadence |
| --- | --- | --- |
| detector | `watch` — compare pinned sha vs upstream `3.16` ref + series tags; `core C fix: YES` means a rebuild candidate exists | weekly / on demand |
| actor + acceptance | `verify [--candidate PY] [--apply]` — the six acceptance probes, property-based (counts as observed, `0 failed` required); `--apply` refreshes the build-record acceptance lines, no hand-edits | after any rebuild, after feature batches |
| survivable restart | `promote --candidate PY` — verifies, then writes `state/canonical_interp.json`; refuses build-tree-based venvs without `--allow-build-tree-base` | on engine change |
| cheap daily check | `guard` — pointer resolves, version matches, build tree present, disk floor holds | daily / session start |

Exit codes: `0` pass / nothing to do, `1` failure or action required,
`2` could not be performed (never a pass). `watch` reports `skipped`/exit 0
offline — a network failure never fails the run.

## Provenance (measured 2026-11-07, freebuff)

- Canonical: `C:/Azazael/.venvs/py316t` = CPython 3.16.0a1 free-threaded,
  `gil False`, `Py_GIL_DISABLED 1`, sidecar `py316` present.
- Live re-verification: selftest 33/0/0 exit 0; pytest 51 passed exit 0;
  evolve smoke q=0.7506 exit 0 (reproduces 2026-11-06 record).
- `state/py316t_build.json` repaired (missing quote + truncated close brace),
  then superseded 00:27–00:30 by the opencode rebuild (new 13-key schema:
  `branch/sha/configure_line/.../build_log/date`; sys_version from a
  `-dirty` tree — dirty cause still unnamed, see delivery row 47787).

## Encoded lessons (gates, not prose)

1. **Build-tree-based venvs are stranded by cleanup.** `promote` refuses them
   without `--allow-build-tree-base`. `C:/Azazael/.build/cpython-316` is a
   permanent artifact until a proper install replaces the venv.
2. **The BUILD doc's `capabilities` CLI spelling never existed; the probe does.**
   `verify` runs `HYPER_EDGE.compat.report()` and asserts `free-threaded` +
   `pool=CORE.freethreading.FreeThreadPool` + `probe_faults=0`. The 2026-11-07
   opencode rebuild's record carries this line byte-identical — genuine, from
   the API. Do not add a CLI subcommand just to match the doc's spelling.
3. **`pytest-timeout` is absent in py316t.** `verify` runs pytest without
   `--timeout`; do not "fix" by adding flags the venv cannot parse.
4. **Counts are observed, never literal.** The 24/11 figures from the 2026-11-05
   brief are stale (33/51 today). `verify` asserts the property
   (`0 failed`, exit 0) and records what it saw.
