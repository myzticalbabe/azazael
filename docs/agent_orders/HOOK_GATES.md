# Commit-hook gate inventory (derived, not remembered)

`C:/Azazael/AGENTS.md` summarises the commit gates for every session, but that
file lives **outside every git repository** (`C:/Azazael` is not a repo;
`C:/Azazael/azazael` is, and its toplevel does not contain that file). A summary
that cannot be committed cannot be reviewed either, so the inventory it states
lives here, in the repo, next to the sources it describes.

Re-derive it; never quote it from memory:

```sh
grep '^# ─── Check' .githooks/pre-commit
```

## Blocking

| # | gate | what it reads |
|---|---|---|
| 1 | bulk-diff focus (`scripts/commit_gate.py --hook`) | the staged changeset: file count, changed lines |
| 1b | stale-index guard (`tools/index_drift_check.py`) | every staged path vs its worktree content |
| 2 | staged anti-patterns (`tools/staged_scanner_gate.py`) | each staged `.py` at `:0:` vs HEAD |
| 3 | canon drift (`tools/canon_drift_check.py`) | `skills/` source corpus vs `.agents/skills/` |
| 4 | anti-pattern ratchet (`tools/anti_pattern_gate.py --check`) | all of `src/` vs `logs/anti_pattern_baseline.json` |
| 5 | mesh wire-or-cut ledger (`tools/mesh_function_preflight.py --check`) | the wire/cut ledger |
| 6 | wire evidence (`tools/wire_evidence_audit.py`) | every `wired` declaration |
| 7b | testing paradigm G1 (`tools/test_paradigm_gate.py`) | new `src/` functions vs staged property tests |
| 8 | supervisor verdict (`tools/supervisor_mcp.py --verdict`) | engram doctor, conflicts, PMB liveness, PAMS |
| 10 | generated instruction blocks (`tools/agent_orders_sync.py --hook`) | the nine generated blocks in the lane instruction files vs `docs/agent_orders/*.md` |
| 9 | unified registry (`tools/preflight_all.py --check`) | re-runs the registry; runs last as the backstop |

## Advisory / non-blocking

- `tools/paradigm_gate.py --check` (blocking only under `PARADIGM_GATE_STRICT=1`)
- heredoc-pipe lint on shell files
- `tools/transcript_ap5_gate.py --limit 500` (reads assistant prose **after**
  emission: it can make a violation visible, never prevent it)
- `tools/pmb_session_observe.py --commit-ok` (memory side-effect; exit ignored)

## Two rules that bite when adding a stanza

1. **A stanza without a registry row fails the self-test.** `preflight_all.py
   --self-test` re-derives the hook's gate list from the hook text (non-comment,
   non-`echo` lines that run python) and reports
   `registry drift: ran-but-unregistered=[...]`.
2. **A `control=` name needs an implementation, not just a path.** A Gate row
   with `control_test=` but a `control=` name absent from `CONTROLS` fails with
   `names control '<name>' with no implementation`. `--run-controls` then
   executes the artifact for real.

Measured on 2026-10-30: eleven blocking stanzas, three advisory, one
non-blocking. The previous summary said "six checks, five blocking" — it had
been stale for six stanzas before that day, which is why the count is now
derived by command rather than written down.
