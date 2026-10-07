# AOA Architecture Audit — does the Quartet still describe this system?

**Date:** 2026-09-14 · **Scope:** `src/AOA` (Armorie-of-Anubis umbrella orchestrator)
**Runtime:** `python3.14t` (free-threaded), hybrid site-packages
**Method:** measured against the live registry, not against the docs. Every
number below was read from a running process on this machine today. Where a
documented claim could not be reproduced, it is marked as such.

---

## 0. Verdict

The Quartet architecture is **still the right idea** — four reasoning pillars
with a shared orchestration and memory layer — but it is **no longer an
accurate description of the system**, in three specific ways:

1. **The quartet is now a minority of the capability surface.** The four
   quartet arms expose 22 capabilities; the five "support" arms expose **49**.
   One support arm (Kali, 40) is **1.8× the entire quartet**.
2. **The mesh expanded underneath the quartet, not alongside it.** 226 worms
   across 35 categories and 26 natures are reachable through exactly **four**
   capability names. That is a fan-in of ~57:1 and it is the real integration
   bottleneck — not the absence of arms.
3. **There are two routing planes and they do not compose.** The mesh router
   *learns and consumes* route weights; the AOA cross-arm router executes a
   static DAG and has **zero** references to that signal. The most valuable
   thing the mesh learned today (`windows>g_archive`, q=+0.975, 6/6) is
   invisible to the layer that decides which arm runs.

Recommendation: keep the four pillars, and **re-found AOA on one routing plane
with typed edges and role-based strata** (§4). The single highest-value change
is not a new arm — it is letting the AOA router read the routing signal the
mesh already produces.

---

## 1. Measured inventory

| arm | category | caps | capability names |
|---|---|---|---|
| azazael | quartet | 4 | `discover_worms`, `run_cluster`, `run_metacluster`, `get_status` |
| libra | quartet | 11 | `list_templates`, `generate_document`, `get_filing_types`, `calculate_fees`, `calculate_deadline`, `check_berks_rules`, `calculate_berks_fees`, … |
| codex | quartet | 3 | `render_video`, `render_mermaid`, `get_status` |
| eve | quartet | 4 | `select_model`, `run_benchmark`, `run_inference`, `get_status` |
| pams | support | 3 | `record_event`, `get_memories`, `get_status` |
| kali | support | 40 | `amass`, `bettercap`, `dirb`, `dnsx`, `ffuf`, `hashcat`, `hydra`, … |
| perfmon | support | 2 | `get_metrics`, `get_status` |
| agent_selector | support | 2 | `select_agent`, `get_status` |
| llama | support | 2 | `infer`, `get_status` |

```
capability surface : 71 total  (quartet 22 · support 49)
arms               : 9 registered, init 9/9
mesh beneath azazael: 226 worms · 35 categories · 26 natures · 5 learned routes
```

**Read that table as a capability budget.** The layer labelled "support" holds
69% of the executable surface, and Kali alone out-weighs the quartet. The
`quartet`/`support` split is a *provenance* label (who was built when), not a
functional one, and it is now misleading in the same way `reg=` was in the
Lilith panel.

---

## 2. Claim verification: the five documented enhancements

`AOA_MILESTONE.json` lists five architecture enhancements. Checked each against
the code:

| # | claim | documented | **actual** |
|---|---|---|---|
| 1 | Unified Data Ontology (`QuartetTypes`) | planned | **accurate** — no `QuartetTypes` or equivalent exists anywhere in the tree |
| 2 | Cross-Pillar **Async Message Queue** | implemented | **overstated** — `EventBus.publish()` dispatches **synchronously, inline**; it is pub/sub, not a queue. No threads, no async, no delivery guarantee |
| 3 | Global PAMS as core memory layer | implemented | **accurate** — `PamsArm` + `CORE/PamsRecorder` are wired into the mesh |
| 4 | DAG orchestration engine | implemented | **partly** — the DAG and topological execution exist, but "conditional cross-Arm dependencies" do not: no predicates, no retries, no compensation on failure |
| 5 | Unified Session Milestone Tracking | implemented | **was non-functional** — `SessionManager.save_session()` had **no caller**; `~/.aoa/sessions/` did not exist. Wired today (see §2.1) |

Plus one number that is not an enhancement but a headline metric:

```
documented in AOA_MILESTONE.json : total_routes 56  · quartet_routes 12
live capability surface          : total       71  · quartet       22
```

`56` and `12` were hand-authored documentation with **no producer**, printed by
the AOA wallboard as `ROUTES 56 total (12 quartet)` next to live workflow data.
The panel now derives the surface from the registry and shows the documented
figure beside it as `doc 56/12 stale`.

### 2.1 Two secondary defects found while verifying

* **`EventBus.publish()` swallows every subscriber exception** with a bare
  `except: pass`. A subscriber that raises is *silently* never delivered to —
  the same "failure rendered as success" shape as everything else in this
  audit series. With 9 arms subscribing, one broken consumer is invisible.
* **`SessionManager.save_session()` had zero callers**, so the "state
  persistence" half of claim 5 did not run. The benchmark workflow now records
  init outcomes, every step with its **measured** duration (enabled by making
  `CrossArmRouter` return the `started_at`/`completed_at` it was already
  stamping), and the verdict.

---

## 3. The seven structural gaps

Each with the evidence that establishes it.

### G1 — Two routing planes that do not compose *(highest value)*

```
mesh plane : MeshRouterWorm.route() → computes effective_weight from learned q   ← adaptive
AOA  plane : CrossArmRouter.execute_workflow() → static DAG, zero q references   ← blind
```

`grep q_weight|Q_|spine src/AOA/core/router.py` → **no matches.**
Meanwhile the mesh has learned, and is acting on, real routing preference:

| route | q | effective_weight | ok/fail | last_ms |
|---|---|---|---|---|
| `windows>g_archive` | **+0.9746** | 1.975 | **6 / 0** | 55.5 |
| `windows>windows` | +0.8200 | 1.820 | 3 / 0 | 9.7 |
| `windows>wsl2-kali` | +0.7000 | 1.700 | 2 / 0 | 120.2 |
| `windows>wsl2-ubuntu` | +0.2376 | 1.238 | 3 / 1 | 8000.0 |
| `windows>mesh` | **−0.9550** | 0.100 (floor) | **0 / 5** | 0.0 |

The mesh has learned *prefer the G: archive; avoid the mesh*. That knowledge is
persisted, versioned and tested (`spine_registry.get_route_usage()`, consumed by
`spine.py` for telemetry) — and the AOA router cannot see it. **The learning
exists; the governance does not.**

### G2 — A synchronous bus above an asynchronous mesh

`EventBus.publish()` calls each subscriber callback inline, under no queue. The
measured consequence, from today's benchmark run:

```
llama.get_status   4748.9 ms
whole workflow     4881.2 ms      → one arm's status call = 97.3% of the run
```

Nine arms dispatched inline means the slowest arm sets the pace of every
publisher. The mesh beneath is free-threaded and concurrent; the orchestration
above it is a serial call chain.

### G3 — The mesh is reachable through four names

`discover_worms`, `run_cluster`, `run_metacluster`, `get_status` — 226 worms,
35 categories, 26 natures behind four capabilities with no parameterisation by
nature. So the mesh cannot be *addressed*: routing cannot target
`nature:security` or `nature:engram`, only "the mesh". Every cross-arm route to
azazael collapses onto one opaque hop, which is precisely why
`route:windows>mesh` is the one route that fails 5/5 — it is the route that can
only be taken wholesale.

### G4 — No typed contracts between arms

Claim 1 is still unimplemented and it is the prerequisite for G1 and G5: the
workflow passes `payload={}`, hands back untyped `result["data"]`, and every
consumer does `.get("worm_count", d.get("total_worms", "?"))` — guessing at
shape. Nine arms × N capabilities with no schema is where the
`worm_count`/`total_worms` duplication comes from.

### G5 — Categories that no longer describe function

`quartet`/`support` is provenance. By function the nine arms span six roles:
reasoning (azazael), production (codex), transaction/compliance (libra),
selection (eve **and** agent_selector — overlapping, `select_model` vs
`select_agent`), memory (pams), toolchain (kali, 40), infrastructure (perfmon,
llama). Two roles exist twice; three arms are infrastructure. The label tells a
reader nothing about what an arm is for.

### G6 — The DAG has no failure semantics

`execute_workflow()` marks a step FAILED and keeps going. There is no retry, no
per-step timeout, no compensation, no policy for "step 3 failed, so step 4's
result is meaningless". With 9 steps and one arm holding 97% of the wall time,
this is not theoretical.

### G7 — Observability with no provenance contract

Established across this session and now largely fixed for the panels: values
were displayed with no age or derivation, artifacts had no producers, and
"missing" rendered as `0`. The **contract** that should hold for every value on
every surface: *derived or absent, dated, and attributable to a source.*

---

## 4. Proposed AOA v2 — one plane, typed edges, role strata

Keep the four pillars. Change what the orchestrator *is*: from a hub that calls
arms to a **routing plane over a typed capability graph**.

```
                    ┌──────────────────────────────────────────┐
  Plane 4  POLICY   │ selection policy (eve ⊕ agent_selector)  │
                    │ DAG failure policy · budget · retries    │
                    └────────────────────┬─────────────────────┘
                                         │
  Plane 3  ROUTE    ┌────────────────────┴─────────────────────┐
                    │ ADAPTIVE ROUTER   (reads q, not a fixed  │
                    │ DAG) · hop cost · returns· timeouts      │
                    └───┬──────────────┬──────────────┬────────┘
                        │              │              │
  Plane 2  CONTRACT ┌───┴───┐   ┌──────┴─────┐  ┌─────┴──────┐
                   │ Quartet│   │ Capability │  │  Provenance│
                   │ Types  │   │  facets    │  │  envelope  │
                   └───┬────┘   └──────┬─────┘  └─────┬──────┘
                       │               │              │
  Plane 1  BROKER  ┌───┴───────────────┴──────────────┴──────┐
                   │ async broker: bounded per-arm queues,    │
                   │ isolation, timeout, no inline dispatch   │
                   └───┬───────┬───────┬───────┬───────┬──────┘
                       │       │       │       │       │
  Plane 0  ARMS   reason  produce  transact  memory  toolchain   infrastructure
                 (azazael)(codex)  (libra)   (pams)   (kali)    (perfmon, llama)
                                                        + selection (policy plane)
```

### Plane 2 — Typed contracts first (unblocks everything)

Finish `QuartetTypes` as a single module of Pydantic/dataclass models, one per
capability, with a registry mapping `(arm, capability) → request/response type`.
Add an envelope every arm must return:

```python
@dataclass
class ArmResult:
    status: str                  # ok | error | timeout | refused
    data: dict                   # schema-validated against the capability
    produced_at: str             # when the DATA is from (not when read)
    source: str                  # arm + capability that produced it
    duration_ms: float
    stale_after_s: float | None  # the producer declares its own freshness bound
```

`produced_at` + `stale_after_s` is the G7 contract enforced structurally: an
arm cannot hand back an undated number, and a consumer can decide freshness
without knowing the producer.

**Acceptance:** every capability round-trips a validated model; a missing
required field raises at the boundary rather than becoming `.get(..., "?")`.

### Plane 1 — Async broker (replaces the synchronous bus)

`EventBus.publish()` currently dispatches inline and swallows exceptions. The
replacement: bounded per-arm queues, a worker per arm (the runtime is
free-threaded — this is what it is for), explicit timeout, and **errors
delivered, not discarded**. Keep the existing `publish`/`subscribe` API as a
thin façade so no arm changes.

**Acceptance:** the 4748.9 ms `llama.get_status` no longer extends any other
arm's publish; a raising subscriber produces a visible `arm.error` event
(instead of `except: pass` today).

### Plane 3 — One adaptive router

Extend the route key space from `route:<env>><env>` to also carry arm hops
(`arm:<from>><to>`), and have `CrossArmRouter` consult `get_route_usage()` when
choosing between candidate arms for a capability. Keep the DAG as the *declared*
shape, but allow *elastic* edges: where two arms can satisfy a capability, pick
by `effective_weight` — exactly the formula `MeshRouterWorm.route()` already
applies, so both planes agree by construction.

The learned table already contains the decision rule the AOA router lacks:
`windows>g_archive` (q=+0.975, 6/0, 55 ms) over `windows>mesh` (q=−0.955, 0/5).

**Acceptance:** with two arms offering a capability, the router selects the
higher-`effective_weight` one; simulating `mesh` at q=−0.955 makes the router
avoid it.

### Plane 2b — Capability facets for the mesh

Stop exposing 226 worms as four names. Add `nature` as a routing facet:

```
azazael.run_cluster(nature="security")   # 40 Capabilities → routable addresses
azazael.run_cluster(nature="engram")
```

Natures are already first-class (26 of them, drawn in the mesh view). This turns
one opaque hop into ~26 addressable ones and is the prerequisite for G1 to have
anything useful to route between.

**Acceptance:** ≥1 cross-arm route key carries a nature facet; `route:windows>mesh`
stops being the only path into the mesh.

### Plane 4 — Role strata, and one selection policy

Recategorise by function (`reasoning`, `production`, `transaction`,
`selection`, `memory`, `toolchain`, `infrastructure`) and **merge the duplicate
selection role**: `eve.select_model` and `agent_selector.select_agent` are the
same decision at two layers. Keep both implementations if useful, but put one
`SelectionPolicy` interface in front so the choice is made once, observably.

### Plane 4b — DAG failure semantics

Per-step `timeout_s`, `retries`, `on_failure: fail | skip_dependents | fallback`
(where `fallback` names an alternate arm+capability). With elastic edges from
Plane 3 this composes: "if the preferred arm misses its timeout, re-route by
`effective_weight`."

---

## 5. Migration order (each step independently shippable)

| # | step | why first | effort | acceptance test |
|---|---|---|---|---|
| 1 | `QuartetTypes` + `ArmResult` envelope | unblocks 2, 3, 6 | M | capability round-trip validated; undated data rejected |
| 2 | Async broker behind the existing bus API | removes the 97%-of-runtime block | M | llama stall no longer serialises peers; subscriber errors surface |
| 3 | Router consults `get_route_usage()` | uses learning already paid for | S | higher-`effective_weight` arm wins a contested capability |
| 4 | Nature facets on azazael capabilities | gives routing something to address | M | a route key carries a nature facet |
| 5 | Role strata + one `SelectionPolicy` | removes duplicated decisions | S | `eve`/`agent_selector` decided through one interface |
| 6 | DAG timeouts / retries / fallback | failure semantics | M | injected timeout re-routes via fallback |
| 7 | Provenance contract on all surfaces | stops the drift class recurring | S | every panel value is derived-or-absent, dated, attributable |

Steps 3, 5 and 7 are small and high-yield. Step 1 is the one that gates the
rest, and it is the item the architecture has called "planned" since
**2026-06-30**.

---

## 6. What should NOT change

* **The four pillars.** The grouping is sound — reason, produce, transact,
  select. The problem is the *edge layer*, not the vertices.
* **`PAMS` as shared memory.** Wiring is real and working.
* **The mesh's own router.** `MeshRouterWorm.route()` is adaptive and correct;
  AOA should adopt its formula, not replace it.
* **The hybrid interpreter stack.** Verified working; not an architecture item.
* **The monitor honesty contract.** Established this session; extend it, don't
  re-litigate it.

---

## 7. Risks in doing this

* **Elastic routing makes the DAG non-deterministic.** Mitigation: keep the
  declared DAG authoritative and record the *actual* chosen route per step in
  the session milestones (now persisted), so a run is replayable from the log.
* **Async broker can hide ordering.** Mitigation: `correlation_id` already
  exists on `AOEvent`; require it and assert per-workflow ordering in tests.
* **Facets multiply route keys.** 226 worms × natures could explode the ledger.
  Mitigation: facet only at the nature level (26), not per-worm; the ledger
  already holds 43 Q-weights and must stay readable.
* **Typed contracts will break arms that return ad-hoc dicts.** Mitigation:
  validate in warn-only mode first and count violations, then flip to strict.

---

## 8. Immediate follow-ups from this audit

1. `AOA_STRUCTURE.html` and the AOA wallboard still render the documented
   56/12 — the wallboard now derives live and labels the doc figure; the HTML
   generator badge should do the same.
2. `EventBus.publish()`'s bare `except: pass` should at minimum count swallowed
   subscriber errors and expose the count on the wallboard (cheap, immediate).
3. `AOA_MILESTONE.json`'s five "enhancements" should carry the same provenance
   treatment as the rest of the file: a `verified_at` date and, for claim 2/4/5,
   the corrected status — since two of the five are not what they say.
