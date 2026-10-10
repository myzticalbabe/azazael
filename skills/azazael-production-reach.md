---
name: azazael-production-reach
description: Prove a capability executes in production runtime, not just imports or registers — the 5-rung reach ladder, SHOULD-vs-ACTUAL audits, starvation remedies, and registry-hygiene rules distilled from the technique-runtime forensic (Oct 2026)
metadata:
  category: workflow
  project: azazael
  priority: high
  version: 1.0.0
  created: 2026-10-10
---

# Production-Reach Audit — from "wired" to "executed"

> Canonical skill content. Live copy: `.agents/skills/azazael-production-reach/SKILL.md`
> (kept in sync by hand until `sync_skills.py` covers it).

A capability is not in production because it imports, registers, or passes a
self-test. It is in production when **production traffic executes it and
leaves evidence in the live store**. Every claim below must be proven with a
named command, never asserted.

## The 5-rung reach ladder

| Rung | Claim | Proof (command) | Technique-runtime example (Oct 2026) |
|---|---|---|---|
| L0 | Importable | `importlib.import_module` on py315t, all 9 slices `ok` | slices load |
| L1 | Registered | `status(record=False)` → 181 rows | registry enumerates |
| L2 | Invoked manually | smoke-call adapters, all `verified: True` | my session's probes |
| L3 | Called by production code | import/call grep excluding tests/tools/docs | only 2 call sites (breaker, metacluster) |
| L4 | Evidenced in live store | row counts by source/event_type on `~/.azazael/memory_store.db` | **0 technique-link rows on 145k-row store** |
| L5 | Consumed | a reader/monitor/trainer acts on the rows | live_monitor block exists, monitor not scheduled |

**Rule: L0–L2 is "wired". L3–L5 is "reaching". Never report one as the other.**

## Method M1 — Registry-truth audit (SHOULD vs ACTUAL)

Run `Temp/opencode/forensic_hosts_v2.py` (registry-driven via `status()`).
Classify every `where`: `no-host` (declared gap) | module-path (`MOD:sym`,
resolve via importlib + hasattr walk) | path-style (`src/...`, probe file +
AST symbols without importing) | prose (hygiene issue, not a host).
Deep-resolve refinements: search module classes for methods (`Class.method`),
split `/`-alternatives, never count prose as missing hosts (v1 false-positive
lesson). Target state: SHOULD == ACTUALLY with zero missing.

## Method M2 — Caller-chain map

Grep `from CORE.technique_runtime import` + `technique_runtime.(run_all|
status|verify_boundary|reflect_on_failure|record_link|fleet_link_health)`
across `src/`, `tests/`, `tools/`, `scripts/`, `dashboard/`. Classify each hit:
production path | test-only | tool/manual | docstring. Then grep each host
method the same way (defs + adapter calls + other). A host called only by
adapters, whose adapters run only via `run_all`, which nothing calls, is
**L2-capped** no matter how green its tests are.

## Method M3 — Live-store evidence

On the canonical store (`~/.azazael/memory_store.db`, home-based so every
tree shares it): count rows by `source`/`event_type` for the feature's
markers (link rows, adapter write-loop rows, hook rows). Zero rows on a large
growing store = starved, not broken. Cross-check `fleet_link_health()`.

## Method M4 — Single-row probes

Before claiming a path works, fire it once with an attributable marker
(`record_link('forensic-probe', ...)` / `verify_boundary('forensic-probe')`)
and read the rows back. One probe row beats any amount of code reading.
Probes are safe: sources are namespaced, writes are single rows.

## Method M5 — Host-remediation pattern (outlier absorption)

Move the mechanism into the owning host as a method, leave a registration
shim + boundary write in the adapter, fix the `where` to the real symbol:
1. Add `Host.method` with `# Host-remediated from ... (Pn)` comment.
2. Adapter body becomes `return _store().method(...)` (+ gated `_write` kept).
3. Update the `register` `where` to `CORE.mod:Host.method` — stale targets
   are ledger lies (batch-4 fixed 10).
4. Smoke all shims live on py315t; `py_compile` both files; leave uncommitted
   without an explicit commit order. 2–3 EPs per batch.

## Method M6 — Starvation remedies (L3–L5 gaps)

- **No callers**: wire ONE real production call site (boundary into an
  existing failure path, like breaker-DLQ / metacluster-error), fail-open.
- **Conditional-only callers**: add an unconditional heartbeat (scheduled
  `run_all(record=False)` or monitor tick) so L4 evidence exists even when
  nothing fails. Note: `Azazael-Chain` runs the **stale mirror tree**
  (`C:/Users/clint/azazael`), not production — wrong-tree scheduled traffic
  is a finding, not coverage.
- **ALLOW_WRITES=False default**: write loops can never deposit in
  production; learning loops (reflect→lesson→recall) cannot close until the
  write policy is decided explicitly.
- **No-host ladder**: real host → `no-host:` + blocker note (M-row pattern:
  defer with named blocker, never bulk-theater) → prose backlog.

## Method M7 — Engram-gate handling

A `mem_save` that surfaces candidates blocks ALL non-memory tools (including
`pmb_*` and `bash`) until judged. Judge every candidate (`related` unless a
real contradiction, with reason); duplicate `judgment_id`s may hide one —
use `mem_compare` + `mem_judge` on the leftover `rel-*`, then wait out the
~60s eval TTL doing exempt `mem_search` work before retrying.

## Anti-patterns

| Looks like production | Actually is |
|---|---|
| 181 registered adapters, green self-test | L2-capped: zero production/test/tool callers of `run_all`/`status` |
| `where` naming a real module | method lives on a class; module-level import would fail — write `Class.method` |
| `where` with `+`, `(...)`, `/` compounds | prose, unresolvable — split to the primary invoked symbol |
| Monitor reads the rows | monitor is a manual double-click loop, no schedule — reader unreached too |
| Scheduled task Running | verify the task's path: stale-mirror execution is wrong-tree traffic |
| Adapters return `verified: True` | honesty about a probe (e.g. `probe=False`) is not engagement |
