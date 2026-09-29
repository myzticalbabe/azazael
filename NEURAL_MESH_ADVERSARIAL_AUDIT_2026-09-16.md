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

# Neural Mesh — Adversarial Audit: Red Queen, Red Teams, and the Unbuilt Colour Queens

**Date:** 2026-09-16
**Agent:** Buffy (Codebuff / deepseek-v4-flash)
**Scope:** the mesh's adversarial layer (`RedQueenWorm`, the probe loop, the
quarantine path), the fabric's *unwired* organ surface, and the colour
queen / colour team constructs (`rainbow_queens_test/`, `HAT_TAXONOMY.md`,
`worm_governance.py`).
**Method:** source read + runtime probes with an **isolated HOME** (`C:\tmp_rq_home`)
so nothing below wrote the live spine store; plus a static AST reachability scan
and a regenerated probe census. Every number is reproducible from §7.

---

## 0. Verdict

**The Red Queen runs, protects the right organs, and keeps honest books — and it
is not a red team.**

It probes with a zero-argument `execute()` on a **freshly constructed instance**,
and every fabric worm's `execute()` returns `{"success": True}` on every path. In
the measured sweep that is **14 probes, 14 successes, 0 failures**. A red team
that structurally cannot observe a failure produces no adversarial pressure; what
it actually produces is a **standing +1 reward injection** for a fixed, arbitrary
subset of worms (§2.2).

The quarantine its findings are supposed to feed **does not gate anything**:
`order_quarantine()` builds a fresh `QuarantineWorm()`, writes to it, drops it, and
`is_quarantined()` has **zero callers anywhere in the tree**. The mesh's own
dashboard reads the *vote ledger*; nothing in the execution path reads the
*quarantine state* (§2.5).

Separately, **35 of 67 classes in the 16 fabric modules are never instantiated
outside their own file**. Four natures — `axon`, `dendrite`, `consolidation`, and
`engram` — are **100 % orphan**. These are organs with afferent and efferent nerves
severed on both ends.

And the colour layer is an island: `rainbow_queens_test/` contains four colour
queens and an eight-team taxonomy with **no consumer in `azazael/` or at the repo
root**. It is a correct, well-sourced, fully tested *taxonomy* with no behaviour
attached to it.

The "legitimate service" test the brief names is the right instrument, and it is
not currently being applied: the mesh has no mechanism that can *retire* a worm.
It can grow (Morphogenesis), it can flag (silence / liveness ledgers), it can
demote (reflex arc). It cannot lose. That absence is why the orphan surface is
52 % and rising, and it is exactly the gap the **Black Queen** and **Gray Queen**
describe.

---

## 1. Measured playing field

### 1.1 Colour-queen harness (static)

| Artifact | Content | Consumers in `azazael/` | Verdict |
|---|---|---|---|
| `rainbow_queens_test/queens.py` | `RedQueenLoop`, `BlackQueenLoss`, `GrayQueenDrift`, `ArtificialBeeColony` | **0** | isolated |
| `rainbow_queens_test/teams.py` | `TEAMS` = 8 teams (red, blue, yellow, purple, orange, green, black, white), frozen dataclasses, sourced | **0** | dead taxonomy |
| `rainbow_queens_test/test_rainbow.py` | 6 tests incl. `test_no_requeen_anywhere` | not collected by `azazael/pytest.ini` | out of the suite |
| `HAT_TAXONOMY.md` | White / Red / Cerulean **hat** axis (authorization, not team) | n/a | different axis |
| `CORE/worm_governance.py` | `WormGovernor`, naming/dedup/lifecycle, 1042 lines | only `error_triage.py` keyword match | organ, no runtime consumer |
| `CORE/WORMS/expansion/spine.py` `RedQueenWorm` | the operational adversarial driver | `SpineCycleWorm` | live |

The harness's own docstring is a specification, not an implementation:
*"BlackQueenLoss: drop costly leaky gene if community provides it"*,
*"GrayQueenDrift: neutral-first dependency → excess capacity → loss fixes by drift
→ entrenched"*, *"ArtificialBeeColony: base has NO queen"*. None of those three
mechanisms exists anywhere in the mesh.

### 1.2 Red Queen — the measured sweep

Isolated HOME, `PROBE_LIMIT=2` per nature:

```
env=windows capable={'ok': True, 'reasons': [], 'cpu': 16, 'ram_gb': 16.5}
EnvBeaconWorm().peers() -> {'peers': []}
_queen_check -> queen_interim
PROBE mesh       probed=2 failures=0 protected_skipped=['MeshRouterWorm','SpineMapperWorm']   [5.1s]
PROBE synapse    probed=2 failures=0 protected_skipped=['HomeostatWorm']                      [0.0s]
PROBE immune     probed=2 failures=0 protected_skipped=['AutoencoderAnomalyWorm']             [0.0s]
PROBE consensus  probed=2 failures=0 protected_skipped=[]                                     [0.0s]
PROBE federated  probed=2 failures=0 protected_skipped=[]                                     [0.0s]
PROBE servemesh  probed=2 failures=0 protected_skipped=[]                                     [0.0s]
PROBE engram     probed=2 failures=0 protected_skipped=['MorphogenesisWorm']                  [0.0s]
quarantine order: []
```

### 1.3 Census regenerated today (`tools/mesh_function_preflight.py --summary`)

| probe | today | recorded 2026-09-16 (earlier pass) | direction |
|---|---|---|---|
| functions in scope | 1453 | 1411 | +42 |
| PF17 (no test reaches it) | **550** | 530 | **worse** |
| PF16 (nothing references it) | **121** | 114 | **worse** |
| PF14 (catches `Exception` alone) | 318 | 300 | worse |
| PF15 (swallows the evidence) | 125 | 118 | worse |
| PF18 (writes module-level state) | 15 | 15 | flat |
| CLEAN | 88 | 88 | flat |

The debt is not being repaid faster than it is being added. Wire-or-cut table:
**117 pending, 0 wired, 0 retired.**

### 1.4 Live brainstem (read-only)

49 Q keys, 49 update counts, 0 saturated, `fabricated_share 0.0204`,
`trustworthy: false`, gossip `seq 7`, `seq_seen []`, `keys []`, one peer file
(`windows.json`). `spine_map.nodes = 0` in the persisted store. So: a
single-environment mesh whose gossip channel has never carried a key.

---

## 2. Does the Red Queen work correctly?

### What is genuinely correct (credit, measured)

- **Governor protection works.** `is_protected_worm()` skipped `MeshRouterWorm`,
  `SpineMapperWorm`, `HomeostatWorm`, `AutoencoderAnomalyWorm`,
  `MorphogenesisWorm` — exactly the regulators, by declared nature *and* by tag,
  regardless of which nature hosts them. Registration **raises** on a
  governor/nature mismatch, so `_guess_category`'s keyword chains cannot
  re-file a regulator into a probed nature. This is the audit's best-built
  invariant.
- **Queen election is honest.** `queen_interim` on Windows, and
  `role.startswith("queen")` is true for both `queen_full` and `queen_interim`,
  so probes are not silently disabled on a degraded host; with `peers == []`
  no false follower is declared either.
- **Per-member probe timeout is enforced.** A hung member becomes a recorded
  failure instead of a hung regulator.
- **The distinct-env quorum ledger is real** (`spine_registry.cast_quarantine_vote`,
  persisted + gossiped + replay-guarded), and the local-majority hole it closed
  on 2026-09-15 was a genuine bug.

That is a well-built supervisory loop. The defect is in what it supervises with.

### R1 — The probe is a happy path, so the red team cannot fail anything (HIGH)

```python
def _run(cls=cls, box=box) -> None:
    try:
        box["result"] = cls().execute()          # zero arguments, fresh instance
    except Exception as exc:
        box["error"] = exc
```

No hostile input, no boundary condition, no fault injection, no state carry-over.
Every probe target's `execute()` is a counter-report that returns `success: True`
unconditionally — read directly in `axon.py`, `dendrite.py`, `thalamus.py`,
`glia.py`, `consolidation.py`, and confirmed empirically: **0 failures in 14
probes**.

The probe can therefore detect exactly two things: **raises** and **hangs**.
*"Runs hostile read-only probes"* is false as written; it runs *scheduled
availability checks*. The red team's only working detector is a crash detector,
and the mesh already has `HEALTHZ` / `ERRORZ` / the diagnostic nature for that.

**Legitimate service:** none, as configured. A heartbeat already exists in the
fabric (`PartitionHealerWorm`, `EnvBeaconWorm`, `SystemZ`).

### R2 — Probe feedback is a standing popularity pump for the first-N worms (HIGH)

```python
if _spine is not None:
    _spine.record_outcome(nat, name, ok, ms, err or None)   # ok is True by construction
```

Selection is `for name, info in WORM_REGISTRY.items()` — **dict insertion order**,
truncated to `limit`. So the same worms are probed every cycle, every cycle they
are recorded as successes, and `record_outcome` reinforces Q toward +1. Q ordering
is healthy-first (`q_order` → `NatureCluster.execute`), so the probed worms are
promoted into production scheduling *for having passed a test that cannot fail*.

The bias is unconditional and one-directional: probe targets receive a free
positive baseline every cycle; the ~200 non-targets receive nothing. `Q` is
therefore not "how well does this worm do its job" — for the probed subset it is
partly "how often was it probed".

This is the mechanism, verifiable from the code alone; it does not require
inferring causation from the live table, though the live table is consistent with
it (the fabric-neutral `mesh:`/`immune:` keys sit at the top of `q_effective`).

### R3 — A non-dict result is recorded as a pass (MEDIUM)

```python
r = box.get("result")
if not isinstance(r, dict):
    r = {"success": True}        # spine.py:558
```

A worm whose `execute()` returns `None`, a string, a list, or a number is
**PASS**. A red team that rewards malformed output is inverted at exactly the
point it is supposed to be strict. The correct disposition is the opposite:
non-dict output is a contract violation, and a contract violation is a failure.

### R4 — Coverage is fixed at ≤28 of 226 worms and never rotates (MEDIUM)

`PROBE_LIMIT = 4` × 7 `PROBE_NATURES`, minus protected skips → in practice
**25–28 worms of 226 (≈12 %)**, always the same ones, chosen by registration
order. A worm is not probed because it is risky, newly changed, low-evidence, or
stale — only because it was discovered early.

The 09-14 commit series advertises "curiosity-ranked probes"; there is no ranking
in `pressure_probe()`. A prioritised queue over (`q_evidence`, `scars`,
`last_probed_at`, `changed_since`) would be ~20 lines and is the single cheapest
upgrade to the red team's actual coverage.

### R5 — Quarantine is a no-op at the point of use (HIGH)

```python
voter = QuorumVoterWorm(quorum=self.QUORUM)
qz = QuarantineWorm()                    # spine.py:582 — fresh, local, ephemeral
...
if vote.get("decided"):
    qz.quarantine(worm, f"fail_rate={fail_rate:.2f}")
    ...
# function returns; `qz` is garbage-collected with the record inside it
```

`QuarantineWorm` holds `self._quarantined: dict` per instance. `is_quarantined()`
has **zero callers in the tree** (§7). `CLUSTERWORMS`, `NATURE_CLUSTERS` and
`worm_registry` contain **no** quarantine filter — the only textual match is a
`"purpose"` description string. `MorphogenesisWorm.promote()` repeats the same
pattern at `spine.py:2685`.

So the architecture's advertised containment — *"Isolate from execution pipeline /
Record in quarantine ledger"* — is **write-only to a dead object**. What survives
is the *vote* (dashboard renders it) and a `quarantine_ordered` spine event. The
worm keeps executing.

This is the same defect family as the four silent findings of the 09-14 audit:
**the code reports isolation without having established it.**

### R6 — On a single-env host the quarantine verdict is unreachable (MEDIUM)

Quorum counts **distinct envs** (correct safety intent: one env must never
quarantine alone). With `peers == []`, `order_quarantine()` returns `[]` —
**measured**. Combined with R5 and `QUARANTINE_MIN_FAILURES = 3`, the entire
adversarial → quarantine path is unreachable on this machine. The only observable
output of red teaming here is ledger rows.

The intent is right; the consequence — quarantine is untested, unexercised, and
therefore *unknown* — is not. There needs to be a declared single-env operator
channel for quarantine (the codebase already has this exact pattern: `force=True`
for `request_moult` and for `promote`), so the path is exercisable without
weakening the multi-env rule.

### R7 — A hanging member becomes a permanent, self-renewing demotion (MEDIUM)

A hung probe is left as a daemon thread and recorded as a **failure**, every
cycle. The reflex arc fires at 4 consecutive failures (cooldown ×3, priority −1,
scar), and since the thread cannot be killed, **every subsequent probe re-creates
it**. One permanently-hanging member therefore:

1. holds a permanent ×3 cooldown and −1 priority,
2. leaks one daemon thread per probe per cycle (unbounded),
3. costs its full `PROBE_TIMEOUT_S` in wall time on every sweep.

Measured wall cost: `mesh` nature = **5.1 s for 2 worms** (`PartitionHealerWorm`
shells out to `wsl -l -v`). A full 28-probe sweep at that rate can exceed two
minutes inside a 300 s cycle, i.e. the red team can consume the cycle budget
available to the thing it is testing.

The fix is a declared `HUNG` state distinct from `FAILED` (a hang is an
*availability* fault, not a *correctness* fault), a per-member thread budget, and
a circuit that stops re-probing a known-hanging member until it is explicitly
re-enabled.

### R8 — Probing a fresh instance measures the constructor, not the worm (LOW–MEDIUM)

`cls()` per probe means no mesh state is ever exercised: no accumulated queue, no
warm cache, no partially-applied policy. The `ms` recorded as "production
latency" is a constructor + counter-report time. For the stateful organs this is
the opposite of a test — it is a guaranteed-pass exercise of the one path that has
no state.

**Ordering:** R5 (containment is a lie) → R1 (probe has no teeth) → R3 (inverted
strictness) → R2 (feedback bias) → R4/R7 (coverage and hangs) → R6 (no operator
channel) → R8.

---

## 3. Legitimate-service test, applied to the fabric

A worm exists legitimately when it (a) is reachable, (b) has a consumer for its
real API, and (c) changes something observable. Measured by AST: class
**instantiated or imported outside its own module** (re-export `__init__.py`
excluded).

| nature | classes | orphan | orphans |
|---|---|---|---|
| `axon` | 4 | **4** | MyelinSheathWorm, SaltatoryRouterWorm, SpikeEncoderWorm, LatencyCompensatorWorm |
| `dendrite` | 4 | **4** | DendriteAggregatorWorm, AttentionGateWorm, ContextConcatWorm, SensoryFuseWorm |
| `consolidation` | 4 | **4** | SharpWaveReplayWorm, SleepConsolidatorWorm, EngramIndexerWorm, DreamCriticWorm |
| `engram` | 5 | **5** | VectorShardWorm, RecallRouterWorm, CoherenceValidatorWorm, DreamConsolidatorWorm, `_VectorIndex` |
| `xenomorph` | 7 | **5** | OvomorphWorm, FacehuggerWorm, ChestbursterWorm, DroneWorm, ResinWorm |
| `envmesh` | 6 | **5** | WinBridgeWorm, WslUbuntuWorm, WslKaliWorm, GDriveLoomWorm, EnvBeaconV2Worm |
| `glia` | 4 | **3** | AstrocyteWorm, OligodendrocyteWorm, EpendymalWorm |
| `immune` | 5 | **3** | ImmuneSentinelWorm, AttestationWorm, SelfHealWorm |
| `thalamus` | 3 | 1 | SensoryRelayWorm |
| `synapse` | 5 | 1 | ActivationRouterWorm |
| **total** | **67** | **35 (52 %)** | |

Honest caveat, same as the prior audits: *orphan* here means **no direct consumer
of the class**, not *never constructed*. `NatureCluster.execute()` constructs
every registered worm and calls its zero-arg `execute()`, so each orphan is
swept and returns a counter report. That is precisely the point — the class runs,
the *capability* does not.

### 3.1 Incorrect builds found among the orphans

Not merely unwired; wrong or self-contradicting on inspection:

| # | Function | Defect | Evidence |
|---|---|---|---|
| B1 | `SleepConsolidatorWorm.sleep_cycle` | returns `{"snapshot": "g_archive"}` and snapshots nothing. Report-shaped success for work not done. | read; no writer to G: in the body |
| B2 | `AstrocyteWorm.sweep` | `f.name == "__pycache__"` sits inside `if f.is_file()` — unreachable, so the docstring's *"cleanup: `__pycache__`"* never happens for directories; `SAFE_SUFFIXES` is declared and unused. | read; predicate is dead |
| B3 | `EpendymalWorm.scan` | described as *"G: archive GC: stale loom outputs, dedup by hash"*; body only `os.path.exists` and reports `mode: "report-only"`. No GC, no dedup, no hash. | read |
| B4 | `OligodendrocyteWorm.execute` | calls `self.recommend()` with **defaults**, so the class always advises `AWQ-4bit` at 16 GB regardless of the host. | read |
| B5 | `MicrogliaWorm.check_path` | hardcoded `G:/source-of-truth/...` path (PF09 class), class-level mutable `_SIZE_DENSITY` (PF18 class), blanket `except Exception`. | read + census PF09/PF18 |
| B6 | `MoEDispatcherWorm.dispatch_cascade` | if every attempt raises, `answer`/`name` are unbound at the final `return` → `UnboundLocalError`; and the `"best_effort_last_expert"` note returns the last *successful* expert, not the last expert tried. Unreferenced (PF16). | read |
| B7 | `SensoryRelayWorm` | the "modality → cortex worm routing table" holds **strings** (`"SystemZ"`, `"RecallRouterWorm"`) that are never resolved, so the table cannot be validated, and nothing calls `relay()`. | read |
| B8 | `AttestationWorm.attest_file` | `xenomorph.py`'s module docstring names `AttestationWorm` as a gate on the lifecycle; `promote()`'s docstring names `QuarantineWorm`; **neither attest nor quarantine is consulted** — only the quorum vote is. | read + §7 |

B1, B3 and B8 are the same defect as R5: *a claimed control that is not in the
control path.*

---

## 4. The colour queens and colour teams: what actually exists

### 4.1 The two Red Queens do not know about each other

| | `spine.RedQueenWorm` | `rainbow_queens_test.queens.RedQueenLoop` |
|---|---|---|
| model | scheduled pressure loop | Van Valen ratchet: fixed evaluator within epoch, upgraded at the boundary |
| state | cycles, last probe | `attacker_skill`, `evaluator_strictness`, `epoch` |
| wired | yes (`SpineCycleWorm` stage) | no |
| adversarial? | claims to be, is not (§2 R1) | is not — it is a scalar ODE with no opponent |

The mesh implemented the **name**, and the harness implemented the **mechanism**,
in separate repositories of thought.

### 4.2 Team inventory — the mesh's coverage per colour

| Team | ISACA/Wright role | Mesh implementation | Status |
|---|---|---|---|
| **Red** | emulate adversary TTPs | `RedQueenWorm` | **present, no teeth** (§2) |
| **Blue** | monitor / detect / react | `AutoencoderAnomalyWorm` (wired), `ImmuneSentinelWorm` (**orphan**), `telemetry.SpanTracer`/`EventRouter`, monitors | scattered, no detection *contract* |
| **Yellow** | build secure, fix what red finds | `AttestationWorm` (**orphan**) | organ exists, unused |
| **Green** | integrate security early; automate for blue | `SpanTracer` / `cd3_exporter` exist | no automation bridge |
| **Orange** | train yellow on TTPs; perpetual offensive testing | **none** | **absent** |
| **Purple** | red + blue collaboration, open-book | **none** (the spine's own feedback loop is not a purple team) | **absent** |
| **Black** | threat intel to all teams | `ThreatIntelMonitorWorm` (security nature) | present, isolated from the cycle |
| **White** | governance, ROE, methodology | `worm_governance.WormGovernor` (1042 lines, **no runtime consumer**) | organ exists, unused |

### 4.3 Queen inventory — the evolutionary axes

| Queen | Mechanism (per harness docstring) | Mesh implementation |
|---|---|---|
| **Red** | persistent co-evolution; strictness ratchets | `RedQueenWorm` (mismatched, §4.1) |
| **Black** | selection-driven **loss** of a costly, leaky, essential function | **absent** — the mesh can only grow |
| **Gray** | drift-first: neutral loss fixes first, **purifying selection then entrenches** the dependency | **absent** — and this is the measured disease (§3) |
| **Scout (ABC)** | base has **no queen**: employed / onlooker / scout division of labour | **absent** — mesh scheduling is queen- and priority-centric |

The harness already asserts the invariant worth keeping:
`test_no_requeen_anywhere` — **`requeen` is not an operator**. Queens are
persistent roles; nothing replaces the object mid-race. That is consistent with
the mesh's lease model and should be carried forward as a stated invariant rather
than a test in an uncollected directory.

---

## 5. Bleeding edge: flesh out the missing colour queens and teams

Design rule applied to every proposal: **it must attach to an organ that already
exists** (so net new code is small), **it must have a named consumer**, and **it
must carry a falsifiable acceptance test**. No proposal is allowed to add an
orphan.

### 5.1 `BlackQueenWorm` — adaptive loss (the missing counterpart to Morphogenesis)

- **Service:** retire a worm whose function is provided by the community. The
  mesh today can generate specialists forever and can never lose one; that
  asymmetry is why 52 % of the fabric is uninstantiated.
- **Mechanism (from `BlackQueenLoss`):** loss requires cost **and** leak **and**
  community provision — i.e. retire only when (a) the worm's evidence is thin,
  (b) another registered worm's capability signature covers it, and (c) the
  quorum agrees.
- **Hooks that already exist:** `spine_registry.cast_quarantine_vote` (distinct-env
  verdict, verdict `"retire"`), `NEURAL_MESH_WIRE_OR_CUT.json` (`status: retired`
  **already has a declared-status schema and a test**, and 117 rows say `pending`).
- **Consumer:** the wire-or-cut table, and `RedQueenWorm.order_quarantine`'s
  successor. This is the mechanism that converts *pending* into a decision instead
  of a manual chore.
- **Acceptance:** a capability covered by another worm with `< N` evidence is
  proposed for retirement; the retirement is quorum-gated; `--verdict` re-run
  shows `retired > 0` with a reason for every row; false positives are measured
  by the `wired` count not dropping.

### 5.2 `GrayQueenWorm` — entrenchment detector (drift ratchet)

- **Service:** detect *neutral loss that has become entrenched*. Measured fact:
  a class with no caller stays registered, is swept, is tested by nothing, and
  therefore **cannot be fixed by observation** — the definition of the 35-class
  orphan surface.
- **Mechanism (from `GrayQueenDrift`):** the founding event is a *neutral* loss
  (a caller is removed in a refactor). Entrenchment is what follows: purifying
  selection keeps the class in the registry because "it's registered, so it must
  be used". The detector must fire on the **first** cycle a class becomes
  zero-caller, not after rot.
- **Hooks:** `tools/mesh_function_preflight.py` (deterministic, cheap, already
  emits PF16) → run per session, persist the census, **diff it** — the §4.3
  proposal from `NEURAL_MESH_FUNCTION_AUDIT_ANALYSIS_2026-09-16.md` that is still
  open today (PF16 went 114 → 121, so the trend is live).
- **Consumer:** the mesh monitor (an `entrenched` count with the delta), and
  `BlackQueenWorm` (it is the source of retirement candidates).
- **Acceptance:** the census is stored with a timestamp; a class that gains a
  caller leaves the list; a class that loses its last caller appears **the same
  session**; the report names the delta, not the total.

### 5.3 `ScoutBeeWorm` — queenless exploration quota (fixes R4/R2 at the root)

- **Service:** schedule probing by *ignorance*, not by registration order. The
  mesh's own `get_q_updates` docstring already names the cold-start collapse:
  *"any selector that ranks on Q therefore starves untried arms permanently."*
  The red team is a victim of it, not an exception to it.
- **Mechanism (from `ArtificialBeeColony`, which deliberately has no queen):**
  employed = the well-evidenced targets; onlooker = fitness-proportional;
  **scout = a forced quota of never-probed / long-unprobed arms**. The quota is
  the exploration term the schedule lacks.
- **Hooks:** `RedQueenWorm.pressure_probe` candidate selection (replace the
  insertion-order truncation), `get_q_updates` for the ignorance signal.
- **Acceptance:** over K cycles every eligible worm is probed at least once
  (coverage is a tracked set, not a constant); the probed set is **not** identical
  cycle to cycle; §2's R2 bias disappears because no fixed subset receives a
  guaranteed +1.

### 5.4 `PurpleTeamWorm` — red/blue pairing, and the by-product is a dataset

- **Service (ISACA: offensive testing + response, open-book collaboration):** pair
  every hostile probe with the blue layer's verdict on it. Outcome is a
  **labelled corpus**: probe → detected / not-detected. This is the only way the
  red team's output becomes *useful* rather than merely recorded.
- **Mechanism:** the probe emits the event through the telemetry spine
  (`telemetry.EventRouter` / `SpanTracer` / `cd3_exporter`, all present); the blue
  detectors (`AutoencoderAnomalyWorm`, monitor collectors) render a verdict on the
  same trace id; the pair is scored: **a probe blue does not notice is a detection
  gap** — a finding, not a success.
- **Consumer:** the ML/RL monitors already render anomaly scores and route
  health; the *detection-gap* count belongs beside them.
- **Acceptance:** a synthetic hostile event that blue fails to flag produces a
  `detection_gap` row. Today that row cannot exist, because nothing pairs the two
  layers.

### 5.5 `OrangeTeamWorm` — turn hostile probes into permanent tests

- **Service (ISACA/Wright: train yellow on TTPs, perpetual offensive testing):**
  every probe that produced a failure becomes a **regression test**. This attacks
  the largest measured signal in the whole census: **PF17 = 550 functions reached
  by no test**, up 20 in a day.
- **Mechanism:** a probe failure carries (worm, nature, error signature, input).
  That tuple is a test case. Derive it, write it, and keep it.
- **Consumer:** the test suite; the wire-or-cut table's `wired` status.
- **Acceptance:** probe→test conversion is deterministic and idempotent; a red
  finding without a corresponding test is reported as an open gap. **Note:** with
  R1 unfixed this produces nothing, which is precisely why R1 precedes it.

### 5.6 `YellowTeamWorm` — wire the orphan attestation into the build gate

- **Service:** the code that is about to be promoted (Morphogenesis) is compiled,
  hashed and attested **before** it can become discoverable.
- **Hook that already exists:** `immune.AttestationWorm.attest_file` — it already
  does `py_compile`, SHA-256 and a free-threading check. It is an **orphan**, and
  `promote()`'s docstring already claims attestation involvement.
- **Change:** one call in `MorphogenesisWorm.promote()` before the quorum.
- **Acceptance:** a staged file that fails `py_compile` cannot be promoted; the
  attestation digest appears in the promotion record. This closes B8 by making
  the docstring true instead of editing the docstring.

### 5.7 `WhiteTeamWorm` — give the governance organ a runtime consumer

- **Service:** ratify policy changes. The reflex arc mutates process-global
  `WORM_REGISTRY` (cooldown ×3, priority −1) and the policy journal is the only
  durable record; `revert_policy()` exists. Governance is therefore *required* and
  currently *manual*.
- **Hook that already exists:** `CORE/worm_governance.py` — `WormGovernor`,
  naming validation, dedup, lifecycle. 1042 lines, **no runtime consumer**.
- **Change:** every journaled policy mutation is ratified-or-rejected by
  `WormGovernor` before it is replayed, and the ratification is a signed spine
  event (the Ed25519 path is live since the 09-14 crypto fix).
- **Acceptance:** a policy change without a ratification record is refused on
  replay; `worm_governance` gains a real caller (PF16 for that module drops).

### 5.8 The Red Queen, corrected — and the ratchet brought home

Bring `RedQueenLoop`'s mechanism into `RedQueenWorm` instead of duplicating the
name:

- **Within an epoch the criterion is fixed** — so a probe result means something
  (no moving target).
- **At the boundary the criterion is upgraded only if the probed surface caught
  up** — the ratchet. Concretely: the probe generator escalates
  (mutation → malformed input → boundary values → resource pressure) and the
  blue detector's threshold escalates only after the detector passes the current
  grade. This is Iacob et al's controlled-utility evolution, and it is the
  difference between a scheduled health check and an arms race.
- **R1, R3, R7 compatibility:** hostile probe payloads are the *only* way `R1`
  stops being true; non-dict results must be `FAIL` (`R3`); `HUNG` must be a
  distinct state from `FAILED` (`R7`).
- **Invariant to carry over verbatim:** `requeen` is not an operator. Queens are
  persistent roles with leases; no replacement event. The harness asserts this;
  the mesh should state it.

### 5.9 What not to build

The brief's own rule — *these worms must perform legitimate service to exist* —
argues against adding eight new worms to a fleet where 35 of 67 fabric classes
already have no consumer. Every proposal above is therefore either a **hook into
an existing orphan** (5.6 Yellow, 5.7 White) or a **mechanism inside an existing
worm** (5.1–5.3 attach to the spine/registry; 5.4 is a telemetry pairing, not a
new organ). If a colour cannot name the existing organ it repairs, it should not
be built yet.

---

## 6. Recommended order

1. **R5** — make quarantine real: consult `is_quarantined(worm)` in
   `NatureCluster.execute()` / `WORM_REGISTRY` scheduling, and make the ledger
   shared (registry-backed) rather than per-instance. Without this, every
   adversarial finding is decorative.
2. **R3** — flip the `non-dict → success` default to `failure`.
3. **R6** — declare a single-env operator `force=` channel for quarantine, so the
   path is exercisable on one host (mirrors `request_moult`/`promote`).
4. **R1** — give probes hostile inputs and boundary payloads; grade them.
5. **R4 + 5.3** — replace insertion-order truncation with a scout quota so
   coverage rotates and R2's bias dissolves.
6. **R7** — `HUNG` as a distinct state, per-member thread budget, no re-probe of a
   known-hanging member until re-enabled.
7. **§3.1 B1/B3/B8** — either make the claimed controls real or delete the claims.
8. **5.6 / 5.7** — wire `AttestationWorm` into promotion and `WormGovernor` into
   policy replay. Cheapest possible repairs to two orphan organs.
9. **5.2 / 5.1** — entrenchment detection, then Black-Queen retirement, which
   together give the fleet the ability to *lose* — and retire the 117 `pending`
   rows by mechanism rather than by hand.
10. **5.4 / 5.5** — purple pairing and orange test-generation, once probes can
    fail at all.

---

## 7. Verification (every claim above is re-runnable)

```bash
cd azazael && PYTHONPATH=src python3.14t < <(cat <<'PY'
# R5 — quarantine has no consumer
import subprocess, sys
print(subprocess.run(["grep","-rn","is_quarantined","src","--include=*.py"],
                     capture_output=True, text=True).stdout)   # definition only
PY
)

# R1/R2/R4 — the probe sweep (isolated HOME; nothing touches the live store)
# see §1.2; run with USERPROFILE/HOME pointed at a scratch dir

# R3
grep -n "isinstance(r, dict)" -A 2 src/CORE/WORMS/expansion/spine.py   # -> :558

# R5 — the ephemeral quarantine object
sed -n '578,600p' src/CORE/WORMS/expansion/spine.py                    # -> :582

# R7 — hung thread, per -probe
grep -n "daemon=True" -B 4 -A 4 src/CORE/WORMS/expansion/spine.py

# Census / trend (§1.3)
PYTHONPATH=src python3.14t tools/mesh_function_preflight.py --summary
PYTHONPATH=src python3.14t tools/mesh_function_preflight.py --verdict   # 117 pending

# Orphan map (§3)
# AST scan: for each class in expansion/<nature>.py, count `ast.Name` loads in
# every other src file, excluding its own module and __init__.py.  35 of 67 = 0.

# Colour harness is an island (§1.1)
grep -rn "BlackQueenLoss\|GrayQueenDrift\|ArtificialBeeColony\|RedQueenLoop" \
     azazael/src azazael/tests        # -> no matches
```

**Honest exclusions.** (a) The `wired`/`orphan` classification is static and
name-based; a class reached only via `getattr` or a dynamic registry sweep reads
as orphan — that is *why* the §3 caveat is stated explicitly and why every
"orphan" line was read in the source rather than only counted. (b) The R2 bias is
argued from the code path (fixed set, unconditional `True`, one-directional
reward), not from a controlled A/B on the live table. (c) `spine_map.nodes = 0` in
the persisted store is reported as observed; I did not run the mapper to
distinguish "never published" from "published then reset".

*Audit performed by Buffy (Codebuff). Runtime claims taken with an isolated HOME;
the live spine store was read, never written.*
