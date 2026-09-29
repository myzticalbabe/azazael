> ## SUPERSEDED — read `NEURAL_MESH_FORENSIC_2026-09-29.md` first
>
> This document is a **dated record of what was believed on its date**. Its
> numbers are historical and several are now known to be wrong. Nothing marked
> it as superseded, so an undated reader would draw current conclusions from a
> snapshot — the exact "confidently-incomplete artifact" failure this project
> already has a skill for.
>
> Concretely, claims below that are **no longer true**:
> - the global quarantine item store is **present** (`spine_registry.py:521`);
> - the gossip signer allowlist is **present** and has a CLI
>   (`scripts/mesh_trusted_key.py`);
> - route-outcome censoring is **present but was inert** — see §1 of the
>   current forensic;
> - the worm census figures are from their measurement dates, not today.
>
> Kept for provenance. Do not cite without the date.

---

# Neural Mesh × Live Monitor — Reconciliation (2026-09-24, fresh audit)

**Scope:** the neural mesh subsystem (`NEURAL_MESH_*.json/md`, `state/mesh_cycle.json`,
`tools/mesh_function_preflight.py`) and the live-monitor subsystem
(`scripts/live_monitor.py`, `tools/command_center.py` → `dashboard/command_center.*`,
`tools/render_monitors.py` + `tools/monitor_data.py` → `dashboard/monitor_*.html`).
**Trigger:** new algorithm modules landed 2026-09-24 (`algorithm_qualification.py`,
`meta_evolution.py`, `WORMS/expansion/diversity.py`, `WORMS/expansion/policy_optimization.py`,
`state/algorithm_lab/`, `state/meta_evolution/`), so every earlier number in either
subsystem is a claim until re-measured. Every value below is measured today, by an
instrument named inline. Times are local (UTC-4); state JSON stamps are UTC.

---

## 1. Method

| Instrument | Question it answers | Shares failing machinery with |
|---|---|---|
| AST census (`ast.parse`, no imports) | how many registrations exist **on disk** | nothing — second opinion |
| `state/mesh_cycle.json` (in-artifact `at`) | what the fleet **ran** last cycle | the mesh itself |
| `tools/artifact_freshness.py` | are derived maps newer than their sources | nothing — mtime arithmetic |
| render stamps + mtimes on `dashboard/*` | what the monitors **show** and when | nothing |
| grep of reader sets | who consumes the new algo state | nothing |
| `state/meta_evolution/current.json` | what the new algo concluded | the new algo |

## 2. The shared number: the worm fleet census, reconciled

Six numbers are in circulation. They are **four instruments at four times**, not one
contradiction — and one of them is a deliberate frozen baseline.

| Value | Instrument | Measured | What it actually counts |
|---|---|---|---|
| **313** decorated classes (310 distinct) | AST `@register_worm` on ClassDef | 09-24, live tree | registrations that exist in source |
| — of which **78** `generated/Gen*` | AST bucketed by path | 09-24 | generated/staging worms |
| — of which **235** hand-written | AST minus generated | 09-24 | the hand fleet on disk |
| **9** programmatic `register_worm()` calls | AST Call not in decorator position | 09-24 | registrations outside decorators |
| **248** worms / **36** natures | `mesh_cycle.json` `discovered` (`NatureClusterManager.discover_all_natures`) | cycle at 09-24 14:04 | worms mapped into nature clusters |
| **232** classes / **36** categories | `WORM_REGISTRY` after `discover_worms()` | audit 2026-09-22 | registry classes, that day |
| **226** worms / **35** categories | `dashboard/monitor_azazael.html` footer + card | rendered **2026-09-16 02:07** | registry classes, 8 days ago |
| **108** | `command_center.json` `bench.azazael.total_worms` | frozen 2026-08-27 **by design** | drift reference, not a census |

**Reconciled statement:** on 2026-09-24 the fleet **runs 248 worms across 36 registry
categories** (`mesh_cycle.json` 14:04, `ok 248 / fail 0`, complete). The `226/35` on the
azazael monitor is a **dated render (09-16)**, not a current claim; `232/36` is the
audit's registry reading on 09-22; `108` is the intentionally frozen bench baseline
(`_meta.baseline_keys_not_rewritten`). The `LIVE_MONITOR_RESTRUCTURE_TODO.md`
verification rows ("Registry integrity ✅ 226 worms / 35 categories") are honest
**records of 09-15/16 measurements**, not stale claims — but they read as current
anywhere they are quoted without their date.

**Honest residual:** 235 hand-written decorated + 9 programmatic ≈ 244 registration
sites on disk vs 248 discovered in-cluster, and 3 class names are defined twice
(`FastErrorScanner`, `WormFleet`, `ABTestRunner`). The last few identities can only be
itemized from the registry's own inventory (`worm_registry` discovery report), which is
a follow-up, not a discrepancy of consequence.

**Vocabulary drift (fixed by stating it):** the two subsystems use three words for two
things. The monitor render says "35 categories" on one card and "35 natures" in the
footer of the same page. The mesh measures **36 registry categories** but
`NATURE_DEFINITIONS` declares **26 natures**, and `mesh_cycle.json`'s `natures` map has
**36** entries — those are categories. Proposal: "category" = registry category (36),
"nature" = `NATURE_DEFINITIONS` entry (26), and `mesh_cycle.natures` renamed
`by_category` at the next schema bump.

## 3. Mesh wiring census vs the new code — all derived artifacts are stale

`tools/artifact_freshness.py` (run today): **FAIL — 8 stale artifacts, 38 newer
sources**, and it names the new algos (`src/CORE/meta_evolution.py`,
`src/CORE/algorithm_qualification.py`, …) as the newer sources.

| Artifact | Written | Status vs newest source (`scripts/chain_controller.py` 09-24 15:43) |
|---|---|---|
| `NEURAL_MESH_WIRE_OR_CUT.json` (163 findings: 62 `dispatched`, 101 `pending`) | 09-22 16:26 | **STALE** (38 newer sources) |
| `NEURAL_MESH_WIRE_OR_CUT_WORKLIST.md` (101 rows) | 09-22 16:26 | **STALE** |
| `NEURAL_MESH_INTEGRATION_MAP.json` (pending 101; dispositions 5/28/49/19) | 09-22 14:59 | **STALE** |
| `NEURAL_MESH_FUNCTION_TODO.md` | 09-22 15:15 | **STALE** |
| `NEURAL_MESH_INTEROP.mmd`, `logs/capability_wiring_dataset.jsonl` | 09-22 | **STALE** |
| `graphify-out/graph.json`, `GRAPH_REPORT.md` | — | **STALE** (10 newer) |
| `NEURAL_MESH_ENTRENCHMENT.json` (orphans 101, `total_declared` 163, `census_at` 09-22) | 09-24 13:45 | internally consistent (orphans == the 101 `pending` set exactly), but built on the 09-22 census |

Consequences measured, not inferred:

1. **The PF16 census has never seen the new modules.** Their functions are not in the
   163 findings; the `pending` count will grow at the next `--verdict` run. Do not cut
   any row of the 09-22 table on the assumption it covers today's tree.
2. **Mesh-side internal drift (audit vs its own artifact):**
   `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` §4.1 header says **164 / pending 102**;
   the regenerated artifact and the audit's own later text say **163 / 101**. The
   163/101 figures are the measured ones; the §4.1 header row is the stale one.
3. The mesh-side artifacts are otherwise mutually consistent: `ENTRENCHMENT.orphans` (101)
   is exactly the `pending` set; `INTEGRATION_MAP.pending` = 101; worklist = 101 rows
   (44 `test_reached_only` + 57 `no_reference_anywhere`).

## 4. The new algos: running, but unmeshed and unmonitored

Measured reader sets:

| Question | Measurement | Verdict |
|---|---|---|
| Do the new modules register worms? | `register_worm` occurrences: 0 in all four modules | **unmeshed** — absent from fleet census, natures, and `run_mesh_cycle.py` dispatch |
| Does any monitor read their state? | `algorithm_lab\|meta_evolution` matches in `command_center.py`, `monitor_data.py`, `live_monitor.py`, all `dashboard/*.html`: **0** | **unmonitored** — no screen shows them |
| Do they run? | `scripts/chain_controller.py:36` schedules `meta_evolution_cycle.py` (`meta` job); `algorithm_lab_cycle.py` writes `state/algorithm_lab/*` | yes, on the chain |
| Is their state fresh? | `state/algorithm_lab/current.json` 09-24 18:45Z; `state/meta_evolution/current.json` 09-24 19:35Z; 1.5 MB `meta_evolution/proof.json` | fresher than both the mesh cycle (14:04) and the command center (13:43) |

This is the exact failure class `LIVE_MONITOR_RESTRUCTURE_TODO.md` §1.3 exists to
prevent ("state that exists but no monitor reads") — repeated one tier up: the
algorithm laboratory and the meta-evolution control plane are the two newest live
subsystems and **neither the mesh census nor a single monitor knows they exist**.

## 5. Cross-system finding the new algo already produced (actionable)

`state/meta_evolution/current.json` (09-24 19:35Z) carries a live candidate defect:

```
path:     src/CORE/WORMS/expansion/db_monitor.py:300
code:     integrity_ok = integrity.get("ok", True)
detector: default_true · severity HIGH
why:      "a missing verification field reads as PASS"
lifecycle: idle → observe → select → blocked   (apply: false)
```

A fail-open default on a verification field — the "guard that cannot fail" class
(Rule 4, stale-artifact self-audit). It is visible in **neither** the neural mesh audits
**nor** any monitor. `apply: false` means the control plane correctly refused to
self-apply; the decision is the operator's.

## 6. Monitor-layer state, scored against its own rule

`LIVE_MONITOR_RESTRUCTURE_TODO.md` rule: *no monitor may display a hard-coded constant
that the mesh computes; unreadable values render `unknown`.*

| Surface | Measured state | Verdict |
|---|---|---|
| `dashboard/monitor_azazael.html` | footer `226 worms · 35 natures · 76 Q-keys (70 measured) · 12 fabric providers — rendered 2026-09-16T02:07:01`; mtime 09-20 | **8-day-old render on screen** showing `226/35` while the mesh runs `248/36` — the "stale claims on screen" class from its own §1.2 |
| `dashboard/command_center.json/html` | generated 09-24 13:43Z; mesh `248/248`, 36 natures, `at 13:41`, freshness ages + STALE flags for `evolution/metacog/dreaming/training`; DB `930 errors/7d`; chain disabled `last_result 267014` | **current and honest** — the best of the surfaces |
| `scripts/live_monitor.py` | `TRAIN_ALGOS` imported from `track_registry.ROTATION` (single source of truth) with a literal fallback tuple on import failure | mostly compliant; fallback is a guess where the rule says `unknown` |
| `state/algorithm_lab/*`, `state/meta_evolution/*` | fresh, produced every cycle | **no surface** (see §4) |

## 7. Reconciliation verdict

1. **The two subsystems do not contradict each other on facts — they contradict each
   other on time.** The mesh measures; the monitor renders; the renders stopped on
   09-16 while the mesh kept moving (226 → 232 → 248). Where both are current
   (command center vs `mesh_cycle.json`) they agree exactly: 248/248, 36.
2. **The new algorithms widened the gap in both directions**: unmeshed (not in the
   census the monitor reports) and unmonitored (not on any screen the mesh feeds).
3. **The mesh's derived census is one code-change-cycle behind** (8 stale artifacts,
   38 newer sources — tool-measured FAIL), so any wire-or-cut decision taken today on
   the 09-22 table is being taken on stale evidence.
4. **The new algo found a real mesh defect** (`db_monitor.py:300` fail-open) that
   neither side surfaced — the first concrete payoff of the algorithm lab, currently
   stuck at `blocked` with no owner.

## 8. Actions (in take order)

| # | Action | Owner side | Why first |
|---|---|---|---|
| 1 | Refresh the census: `python tools/mesh_function_preflight.py && … --verdict --triage --worklist` and `tools/nature_integration_map.py` (the tool's own remediation line) | mesh | every downstream decision reads these tables; do it before any wire-or-cut |
| 2 | Re-render the monitors (`render_monitors.py`, `command_center.py`) so screens show 248/36 with today's stamp | monitor | the 226/35 render is the live bug a passer-by will read |
| 3 | Fix `db_monitor.py:300` to fail closed (`integrity.get("ok", False)`) and record the disposition in the meta-evolution ledger | both | it is HIGH severity and already evidenced |
| 4 | Decide the new algos' mesh status — register as worms (e.g. `learning`/`optimization` category) or declare deliberate non-mesh services; either way add a monitor row for `state/algorithm_lab/*` and `state/meta_evolution/*` (freshness + open candidates) | both | closes the §4 gap in one decision |
| 5 | Correct `NEURAL_MESH_ARCHITECTURE_AUDIT_2026-09-22.md` §4.1 header 164/102 → 163/101 (the audit's own correction convention) | mesh | one line; stops the off-by-one propagating |
| 6 | Itemize registry identities once (decorator vs programmatic vs discovered; resolve the 3 duplicate class names) into `worm_registry`'s discovery report | mesh | closes the last census residual |
| 7 | Rename `mesh_cycle.natures` → `by_category` at the next schema bump and make the monitor footer say "categories" | both | ends the category/nature vocabulary drift |

---
*Method note: per the stale-artifact self-audit, no number above was copied from a
document; each was re-measured today against the thing it describes, and the residual
(§2) is stated rather than rounded away.*
