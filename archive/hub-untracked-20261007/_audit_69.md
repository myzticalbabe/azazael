---

## 9. AOA v2 Plane 1 — implemented 2026-09-14

Section 5 steps 1–4 of this audit are now implemented, tested, and live.

### 9.1 What shipped

| # | Change | File | Measured effect |
|---|--------|------|-----------------|
| 1 | `ArmResult` provenance envelope + warn-only validator | `src/AOA/core/contracts.py` (new) | Three-state staleness: fresh `False`, past-lifetime `True`, **undeclared `None`** |
| 2 | Envelope wired into `route_task` | `src/AOA/core/router.py` | Every result carries `produced_at`, `stale_after_s`, `age_s`, `is_stale`, `provenance` |
| 3 | Elastic capability selection | `src/AOA/core/router.py` | `route_task(None, cap)` ranks declaring arms by learned Q |
| 4 | Decision recording + replay log | `src/AOA/core/router.py` | Bounded log of reason, candidates, evidence, outcome |
| 5 | `get_q_updates()` accessor | `src/CORE/spine_registry.py` | Distinguishes never-tried from measured-neutral |
| 6 | `KaliArm` exported | `src/AOA/arms/__init__.py` | 41 tool capabilities became addressable |
| 7 | Panel `ROUTE` / `PROV` telemetry | `src/AOA/aoa_monitor.py` | Live routing + provenance + durability |

Live panel output:

```
ARMS   9 registered  init 9/9 in 10.1s
ROUTES slots 71 live (22 quartet)  doc 56/12 stale  workflow 9/9 fail=0 4391ms 0s ago  [#]
ROUTE  63 distinct caps (0 measured)  pick get_status->azazael cold_start  exec perfmon ok 102ms
PROV   provenance 1/1 undeclared  learned 0 durable / 1 in-process  PERSIST GAP: 1 write(s) not saved
```

### 9.2 The cold-start guard, and why Q alone was not enough

`get_q_weight()` returns **0.0 both for an arm that has never run and for one
that has settled neutral**. Ranking on Q alone therefore starves untried arms
permanently: they score 0, are never chosen, so they are never measured. Four
live inference providers independently identified this as the highest risk in
elastic selection (see `.inference_cache/20260914_134832_*.log`).

The guard is a minimum-pull quota: arms below `min_pulls` (default 30) are
exercised **first**, least-observed first. Coverage is guaranteed rather than
left to epsilon. `get_q_updates()` was added to `spine_registry` for this —
the count already existed as `_Q_UPDATE_COUNTS` (it drives the Welford
variance); it is now readable so "unknown" and "measured" are separable.

### 9.3 Feedback-loop bounds

The router both reads the Q table to select and writes outcomes back to it.
Three properties bound it, each from a review verdict:

1. A write happens **only after execution**, never at selection — a decision
   cannot influence the evidence used to score it (Gemini).
2. `spine_registry` reinforces by EMA with alpha clamped to `[0.05, 0.5]`, so
   no single outcome dominates.
3. Writes are capped per arm per hour (`max_writes_per_arm_per_hour`, default
   60), so one hot path cannot load the table (NVIDIA NIM).

Pinned calls also record outcomes. Withholding them is how
`record_route_result()` ended up with zero callers; a pinned execution is a
real observation of `(capability, arm)`, and since a pinned call never *reads*
Q it cannot form a loop.

**Deviation from a review suggestion, recorded deliberately:** NVIDIA advised
a 5 ms budget with fallback on the spine read. Measured: warm reads cost
**0.0018 ms each** (8 arms × 2 reads ≈ 0.03 ms); the 119.9 ms first-call cost
is one-time module import. A timeout on an in-process dict lookup would be
theatre. The real guard is the `try/except` fallback to static priority, which
is implemented and reports `degraded`.

### 9.4 GAP: routing learning is not durable

`aoa_route:` keys in the saved spine state: **0**. `route:` keys: **5**. No
file under `~/.azazael/` mentions `aoa_route` at all — while a routed call
in-process reports successful write-backs.

Both numbers are true. `_append_outcome_event()` appends to an **in-memory
per-thread ring**, and Q weights reach disk only when something calls
`save_spine_state()`. The spine cycle calls it, which is why `route:` keys
persist; nothing calls it after AOA routing.

Consequence: AOA routing learning does not survive its process, so it will
read as empty forever until routing runs inside a cycle that saves, or the
router's outcomes are folded into one. This is the same "written but never
made durable" class as the rest of this audit, so it is reported as a **gap**
on the panel (`PERSIST GAP`) rather than as `0 learned` — "0 learned" reads as
"nothing has run", which is a different and wrong claim.

The probe measures durability from the **saved snapshot on disk**, not the
live Q dict. Reading the live dict would report 1 seconds after a write-back
and imply durability that does not exist. `tests/test_aoa_routing_telemetry.py`
pins this invariant by source guard.

### 9.5 Finding: an arm was invisible to routing

`KaliArm` was registered by `@register_arm`, imports cleanly, and works — but
`arms/__init__.py` never imported its module. `@register_arm` fires on import,
so `arm_id="kali"` was absent from `ARM_REGISTRY`: it could not be
initialized, pinned, or found by elastic capability routing. It carries one
capability per mapped tool, so it was the **largest capability surface in the
system** and entirely unreachable.

`test_arm_exports.py` had been asserting the export and failing since
2026-09-11. A permanently-red test is one nobody reads.

Exporting it surfaced a second, unrelated stale claim: the same test asserted
`len(KALI_TOOLS) >= 41`. Measured: `kali_arm.py` has **a single commit** and it
contains **zero** matches for `httpx|seclists`, so 41 was never implemented.
`seclists` additionally cannot be an entry — `KALI_TOOLS` maps executable
names, each probed with `command -v` and run as `{tool} {args}`, whereas
seclists is a wordlist directory (`/usr/share/seclists` exists, there is no
`seclists` command). The guard is re-anchored at the true baseline (39) and
**strengthened** to assert structure (one capability per tool + `get_status`),
not merely loosened.

### 9.6 Label collision fixed

`ROUTES caps 71 live` and the new `ROUTE caps 63 addressable` used one noun for
two quantities: `_live_caps` sums each arm's capability *count* (71 slots
across 9 arms) while 63 is the number of *distinct* capability names. Both
were correct; together they read as one wrong one. Now `slots 71` vs
`63 distinct caps`.

### 9.7 Monitor reconciliation (all four)

| Monitor | Status vs the new reality |
|---------|---------------------------|
| **AOA** (`src/AOA/aoa_monitor.py`) | Extended with `ROUTE` + `PROV`; now reads `9 registered, init 9/9`, `kali ... caps=40 tools 39/39` |
| **Azazael** (`scripts/live_monitor.py`) | Reads `9 arm classes defined (9 re-exported)` — the gap is closed and reported |
| **Lilith** | Consistent: idle ALERT fires, `spawns=` disambiguated from registration |
| **EX MACHINA** | Consistent: age-aware, absent artifacts omitted rather than aged |

Panel probe safety: selection is exercised on `get_status` (8 candidates) but
**never executed** — `kali`'s `get_status` probes 39 tools over WSL and
`llama`'s shells out behind a 30 s timeout, and the router has no latency
model, only success/failure Q. Execution is exercised once on `get_metrics`,
which only `perfmon` declares, so the pick is deterministic and bounded.

### 9.8 Tests

`146 passed` across `test_cross_arm.py`, `test_benchmark_workflow.py`,
`test_arm_exports.py`, `test_aoa_session_audit.py`,
`test_aoa_data_freshness.py`, `test_aoa_elastic_routing.py` (39),
`test_aoa_routing_telemetry.py` (14), `test_monitor_verdict_accuracy.py`,
`test_threat_feed_freshness.py`, `test_startup_warm_wiring.py`.

Two defects were caught in my own work by these tests, and are recorded
because each was a real hole rather than a bad assertion:

* `_read_evidence` called `_spine()` **outside** its `try/except`, so a read
  failure propagated and killed routing — the precise outcome the degraded
  path exists to prevent. The documented contract ("a damaged ledger stops the
  router learning, never stops it routing") was not honoured by the code.
* `_frame` in the test helper joined an already-joined string, walking it
  character by character, which made every `assertIn` fail for a reason
  unrelated to the assertion. Fixed in the test, not by weakening it.

### 9.9 Still open (Plane 2 and beyond)

Unchanged from section 5: async event broker (sync `publish` blocks the
routing thread — flagged by NVIDIA, touches every subscriber), nature facets,
role strata replacing `quartet`/`support`, DAG failure semantics. Plus the new
item 9.4: fold AOA routing outcomes into a saving cycle.
