# Skill: azazael-release-gate

# Azazael Release Gate — pre-ship checklist for this tree

> Adapted from addyosmani/agent-skills `shipping-and-launch` (generic web
> lifecycle) to azazael's actual gates. Web items (Core Web Vitals, CSP,
> CDN) do not apply here and are replaced with the loop's own guards.

---

## Trigger

Use when preparing to ship, promote, or declare anything done: model
promotions, gate changes, retention/migration edits, sync pattern changes,
new worms, or answering "is azazael fully fixed and functional".

## Gate 1 — Tests (blocking)

- [ ] `pytest tests/ --collect-only -q`: 0 collection errors
- [ ] Full suite (or the affected area): no new failures vs baseline
- [ ] New/changed behavior carries its own tests (paired positive+negative
  cases — a test passing against broken and fixed code proves nothing)

## Gate 2 — Benchmarks (blocking)

- [ ] `scripts/benchmark_evolution.py`: 13/13 two runs in a row (flakes
  are fixed, never re-run into silence)
- [ ] No check edited to make it pass — checks change only with a
  measured false-positive/false-negative diagnosis on file

## Gate 3 — Loop invariants (blocking)

- [ ] Champion on disk == config in use (`applied=True`)
- [ ] Promotion evidence exists for any claimed improvement (paired
  deltas, seeds >= 3, persist=False expeditions don't count as production)
- [ ] Morph rotation state read, not assumed (`morph_policy.json`:
  paused/retired/undetermined — forcing trials against a pause is noise)
- [ ] Conftest isolation intact (no test writes prod DB/spine/log)

## Gate 4 — Data safety (blocking)

- [ ] Destructive ops have backup-first ordering (retention) or explicit
  `--apply --i-understand` double flags (pilot)
- [ ] Protected events untouched: `evolution_result`, `evolution_promotion`
- [ ] Rollback artifact exists: `.prev` files, `.bak` globs, G: snapshot

## Gate 5 — Fleet & mirrors

- [ ] `sync_all.py --status`: ALL SYNCED (fix patterns, not exclusions —
  the AOA gap was a missing pattern, not an exception)
- [ ] G: snapshot current (`.last_sync` today) after tree changes
- [ ] Chain Running; PAMS answering; Ollama fleet intact after model ops
- [ ] No orphaned processes from the work (flet rule: supervised or dead)

## Gate 6 — Rollback plan (blocking)

- [ ] Revert path named: which commit/patch/backup restores prior state
- [ ] Promotion rollback: `.prev2` chain intact (`PROMOTE_JSON` rotation)
- [ ] Canary state known (armed/held/failed) before touching promotion code

## Non-blocking (record, don't gate)

- Store size vs quota (report; trim on schedule, not by hand)
- Queue depth (`memorybus_queue` unflushed count)
- VHDX / Docker / archive hygiene (separate workstreams)

## Verification

```
python -m pytest tests/ --collect-only -q          # Gate 1 (fast)
python scripts/benchmark_evolution.py              # Gate 2 (minutes, x2)
python azazael/scripts/sync_all.py --status        # Gate 5
```

## Red flags

- Editing a check to make it green without a misfire diagnosis
- Re-running a flaky gate until it passes
- Deleting history the ledger still references (distill first, then trim)
- Wiring a caller to an unwired mechanism without its monitor
- Claiming a verdict from one run (seeds >= 3 or it didn't happen)
