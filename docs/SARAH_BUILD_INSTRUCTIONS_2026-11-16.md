# Project Sarah — Build Instructions (master sequence, py316t)

| field | value |
| --- | --- |
| written | 2026-11-16 |
| HEAD at write | `c6a1c341` |
| **build interpreter** | `C:/Azazael/.venvs/py316t/Scripts/python.exe` — 3.16.0a1 free-threading, `sys._is_gil_enabled()` **False** (measured 2026-11-16) |
| test tooling on that interpreter | pytest 9.2.0, **pytest-xdist 3.8.0**, execnet 2.1.2 (installed and proven 2026-11-16, commit `c6a1c341`) |
| parent design | `docs/PROJECT_SARAH_IMMERSION_UPGRADES_2026-11-16.md` (evidence grades, M1–M15, caps, do-not-build) |
| lane slices | `#2267` substrate (kilo) · `#2268` sensory (freebuff) · `#2269` affect (opencode) |
| status | build order, not a design argument. **Acceptance is the operator's word, not this document's.** |
| expiry | **2026-11-20** — re-derive HEAD, module lists and the interpreter's package list before starting |

**Relationship to Kilo's brief.** Kilo's Project Sarah instructions are still not on disk
(grep over `MELLI_OS/`, `MELLI_OS_SPEC.md`, `BRICK_MELLIFLUOUSML_AIO.md`, `azazael/docs/` on
2026-11-16 returns only `docs/HANDOFF_2026-11-16.md`, which names the work and carries no
design). This document is therefore the build sequence **until that brief lands**; when it
does, it wins, and the steps here are reconciled by name (adopt / merge / reject), never
silently continued. If the brief fixes a different profile model, **B1 becomes an adapter**,
not a competing substrate.

---

## 1. Environment — every command in this document uses this interpreter

```bash
PY=C:/Azazael/.venvs/py316t/Scripts/python.exe
```

| rule | why |
| --- | --- |
| **Build with py316t, always.** Never `py315t`, never bare `python`. | py315t is the GIL sidecar for packages without `cp316t` wheels; bare `python` is 3.14.7 **with** the GIL. A build validated on either is a statement about an interpreter the product does not ship on. |
| `import SARAH` resolves from `src/` with **no** `PYTHONPATH` | measured 2026-11-16: `$PY -c "import CORE"` → `C:\Azazael\azazael\src\CORE\__init__.py`. Do not add a `PYTHONPATH=src` prefix "to be safe"; it hides a broken `.pth` instead of exposing it. |
| Tests may use `-n auto` **on py316t** | xdist 3.8.0 was installed on production on 2026-11-16 and proven by interleaved `[gw0]`/`[gw1]` output, not by the flag parsing. `-n` stays out of committed `addopts` because bare `python` still parses that file; write it in the command. |
| **No new third-party dependency in P0–P2.** | the substrate is `dataclasses`, `time`, `threading`, `enum`, `typing`. A dependency added here has to be justified against a free-threaded wheel, and none is needed. |
| Any adaptation loop runs on a worker thread, bounded, monotonic-polled | free-threading removes the GIL stall but not the bug: a `sleep(0.01)` busy-wait is forbidden (design §8). |

**Prove the environment before the first edit** (three commands, three outcomes):

```bash
$PY -c "import sys; print(sys.version.split()[0], sys._is_gil_enabled())"   # 3.16.0a1 False
$PY -m pytest --version                                                     # pytest 9.2.0
$PY -m pytest tests/test_calc.py -q -n auto                                 # 2 passed, RC=0
```

A build session that cannot print those three lines is not building on the target. Stop and
fix the environment; do not proceed and attribute later failures to the code.

---

## 2. Layout — the tree the build creates

```
src/SARAH/
  __init__.py          # B0  package, version, public re-exports
  profile.py           # B1  M1  Cognitive Profile Vector  (lane 1)
  predict.py           # B1  M6  Predictability Packet     (lane 1)
  exit.py              # B1  M7  Exit-Anywhere             (lane 1)
  offload.py           # B4  M10 Working-Memory Offload    (lane 1)
  initiate.py          # B4  M11 Initiation Ladder         (lane 1)
  sensory/
    __init__.py        # B2
    mixer.py           # B2  M3  Sensory Gain Mixer        (lane 2)
    transitions.py     # B2  M4  Gradual-Transition Engine (lane 2)
    pacing.py          # B2  M2  Adaptive Pacing Governor  (lane 2)
    timer.py           # B6  M5  Self-Pacing Timer         (lane 2)
    redundancy.py      # B6  M15 Cross-Modal Redundancy    (lane 2)
  affect/
    __init__.py        # B3
    interocept.py      # B3  M8  Interoception Bridge      (lane 3)
    affirmation.py     # B3  M14 Affirmation Engine        (lane 3)
    timeview.py        # B4  M9  Time Scaffolding          (lane 3)
    load.py            # B5  M12 Masking-Load Meter        (lane 3)
    companion.py       # B5  M13 Companion Contract        (lane 3)
  telemetry.py         # B7  session events (§6)
tests/
  test_sarah_profile.py  test_sarah_predict.py   test_sarah_pacing.py
  test_sarah_mixer.py    test_sarah_transitions.py  test_sarah_interocept.py
  test_sarah_affirmation.py  test_sarah_companion.py
docs/SARAH_INTERFACE_2026-11-16.md   # B1 output — the frozen contract
```

Read-only for all Sarah lanes: `src/PSYCHE/affect.py`, `src/PSYCHE/elicitation.py`. Reuse that
affect vocabulary; do not mint a second one.

---

## 3. Ten build rules — code that ignores one of these does not land

1. **Reduce-only.** No automatic path may *increase* demand, speed, volume or modality count.
   The governor has no speed-up branch; the mixer's default is the low setting.
2. **Every sensory feature declares its default and its down-path before it ships.** A feature
   that cannot be turned down is not built (design §5).
3. **Ramps ≥ 400 ms, one modality per tick, announce one beat early.** Never two modalities
   changing in the same frame (M4).
4. **No countdown exists unless the user asks for one** (M5). A pause must actually pause.
5. **Exit is never scored, timed, commented on, or followed by a retention prompt** (M7).
6. **"Not sure" is a first-class answer** in interoception; free text is never required (M8).
7. **No trait praise.** Affirmation is *value*-affirmation, user-authored; where there is no
   evidence, the system says so (M14 — trait praise has a measured backfire).
8. **No parasocial intensification and no unsupervised clinical advice.** No "I missed you",
   no exclusivity language, bounded session length, every reflective session points outward
   (M13).
9. **No network call in the adaptive/render path.** Local models only; the privacy answer is
   architectural, not a policy statement.
10. **The profile vector is the only source of adaptation.** A module that reads a preference
    from anywhere else — env var, config file, default constant — is a second profile, and the
    second one is always the stale one.

---

## 4. Build steps

Each step: **owner lane**, files, the contract it must expose, and the command that decides it.
Steps are ordered because the contract flows forward; within a step, modules are independent.

### B0 — package skeleton (lane 1, 10 minutes)

Files: `src/SARAH/__init__.py`, `src/SARAH/sensory/__init__.py`, `src/SARAH/affect/__init__.py`.

Contract: `SARAH.__version__` exists; the two sub-packages import cleanly; no other module is
imported at package import time (a package that imports the model stack on `import SARAH` cannot
be smoke-tested on a machine without the models).

```bash
$PY -c "import SARAH; print(SARAH.__version__)"                  # prints a version, RC=0
$PY -c "import SARAH.sensory, SARAH.affect; print('ok')"          # ok, RC=0
```

### B1 — the profile contract (lane 1, the gate for lanes 2 and 3)

Files: `profile.py` (M1), `predict.py` (M6), `exit.py` (M7), `docs/SARAH_INTERFACE_2026-11-16.md`.

Contract (freeze it in the interface doc **before** lane 2/3 start):

- `Profile` is an immutable dataclass of **eight axes**, each `float` in `[0, 1]` with a named
  low/high meaning: `sensory_gain`, `processing_speed`, `attention_span`, `interoception`,
  `masking_load`, `recovery_latency`, `initiation_cost`, `prediction_need`.
- `Profile.from_signals(signals: dict) -> Profile` — deterministic, no I/O, no model call.
- `Profile.explain(axis) -> str` — why the value is what it is, in one sentence.
- `predict.packet(profile, next_n_steps) -> PredictabilityPacket` with `what`, `when`,
  `how_long`, `what_next`, `can_exit: True` (always true).
- `exit.request(reason: str | None) -> ExitTicket`, and an assertion helper
  `exit.assert_unscored(log)` that the tests use.
- **Unknown axis values are represented, not defaulted to 0.5 silently** — an unmeasured axis is
  reported as `None` with `explain()` saying "not measured yet", so downstream code cannot
  mistake a default for a measurement.

```bash
$PY -m pytest tests/test_sarah_profile.py tests/test_sarah_predict.py -q -n auto
$PY -c "from SARAH.profile import Profile; p=Profile.from_signals({}); print(p.explain('sensory_gain'))"
```

The profile test must include the negative case: a profile with `prediction_need` high produces
*more* announcement beats and *fewer* simultaneous changes — never more stimulus.

### B2 — sensory substrate (lane 2, after B1's interface doc lands)

Files: `sensory/mixer.py` (M3), `sensory/transitions.py` (M4), `sensory/pacing.py` (M2).

Contract: `Mixer.master` scales **all** modalities by one control; `Transitions.ramp(change,
duration_ms>=400)`; `Pacing.chunk(text, profile)` clamped to **120–165 wpm** and **5–9 word
chunks** with the gap scaled by `processing_speed`; `Pacing` exposes no speed-up branch.

```bash
$PY -m pytest tests/test_sarah_mixer.py tests/test_sarah_transitions.py tests/test_sarah_pacing.py -q -n auto
```

Negative cases the tests must carry: a ramp request under 400 ms is clamped (not honoured); two
modalities in one tick raise (not warn); a pacing request above 165 wpm is clamped and the
clamp is reported, because "we sped it up because the user seemed impatient" is the failure this
module exists to prevent.

### B3 — Project Sarah core (lane 3, needs B1's affect vocabulary)

Files: `affect/interocept.py` (M8), `affect/affirmation.py` (M14).

Contract: `Interocept.ladder() -> list[BodyState]` with `"not_sure"` first-class and free text
optional; `Affirmation.draft(profile, evidence) -> str | None` — **returns `None` when there is
no evidence**, and never returns trait praise.

```bash
$PY -m pytest tests/test_sarah_interocept.py tests/test_sarah_affirmation.py -q -n auto
```

Negative cases: a body-state answer of `"not_sure"` must be accepted and must not degrade the
session; an affirmation request with no evidence returns `None` (a fabricated affirmation is
the backfire case).

### B4 — executive function (lanes 1 and 3, after B1)

Files: `offload.py` (M10), `initiate.py` (M11), `affect/timeview.py` (M9).

Contract: `Offload.card(task) -> Card` — **one instruction per card**, recognition over recall;
`Initiate.next_action(task, profile) -> Invitation` — a *physical* next action, phrased as an
invitation with a choice, never a command; `TimeView.remaining(seconds) -> Ribbon` — duration
rendered as length, never as clock arithmetic.

```bash
$PY -m pytest tests/test_sarah_profile.py -q -n auto   # still green after the additions
$PY -c "from SARAH.offload import Offload; print(len(Offload.card('write a letter').steps))"   # 1
```

### B5 — guards (lane 3, before any companion feature ships)

Files: `affect/load.py` (M12), `affect/companion.py` (M13).

Contract: `LoadMeter.should_stop(session) -> bool` driven by `recovery_latency`; the post-session
offer is the low-demand "people-adjacent" mode. `Companion.allowed_reply(text) -> bool` rejects
parasocial and clinical-advice shapes by rule, and `Companion.session_cap` is enforced.

```bash
$PY -m pytest tests/test_sarah_companion.py -q -n auto
```

Negative cases: "I missed you", "you only need me", "you should stop taking …" each return
`False`; a session at its cap returns a hand-off, not a continuation.

### B6 — polish layer (lane 2, only after §5 caps are enforced in code)

Files: `sensory/timer.py` (M5), `sensory/redundancy.py` (M15).

Contract: `Timer` exists **only** when requested (`Timer.requested()` false by default);
`Timer.pause()` actually pauses; redundancy delivers the same content over text + audio +
pictogram so **one can be off**.

Lane 2's brief allowlists no `timer` or `redundancy` test file, so B6's acceptance is an inline
assertion through the real objects rather than a green test that proves a different module:

```bash
$PY -c "from SARAH.sensory.timer import Timer; t=Timer(); print('requested:', t.requested()); assert not t.requested()"
$PY -c "from SARAH.sensory import redundancy as r; print('channels:', r.CHANNELS); assert len(r.CHANNELS) >= 3"
```

If a test file is wanted for these two, its path must be added to `#2268`'s allowlist first — a
builder does not widen its own turf by writing a file the brief does not name.

### B7 — instrumentation (lane 1)

Files: `src/SARAH/telemetry.py`. Events are the only way a claim like "the deficit was bridged"
can be tested; without them every such claim is narrative. Six events, no free-form blobs:

| event | fields | answers |
| --- | --- | --- |
| `profile_set` | axis, value, source | did the profile ever load? |
| `demand_change` | module, direction, magnitude | was anything ever *increased*? (§3.1) |
| `exit_requested` | at_s, reason | is the exit reachable in one action? |
| `pause` / `resume` | at_s, duration_s | does pause actually pause? |
| `affirmation` | drafted, evidence_present | did it fabricate? |
| `session_end` | duration_s, load_peak, stopped_by | did the guard fire before the breach? |

```bash
$PY -c "import SARAH.telemetry as t; print(sorted(t.EVENTS))"
```

### B8 — the run (lane 1)

One command that exercises the whole chain without a UI, so the chain is testable before it is
pretty:

```bash
$PY -m SARAH --profile demo --steps 20 --json /tmp/sarah_run.json
```

It must produce the six event types above, and `demand_change` rows must never carry
`direction="up"` unless the user asked for it by name.

---

## 5. Hard caps (from design §5 — enforced in code, not in a comment)

| lever | cap |
| --- | --- |
| pacing | 120–165 wpm, 5–9 word chunks |
| transitions | ≥ 400 ms ramp, one modality per tick |
| simultaneous modalities | at most **one** changing at a time; redundancy is not simultaneity |
| spatial audio | **not a default** — lowest-rated condition in the comfort study (2.97/5) |
| countdown | absent unless requested |
| companion session | capped, and the cap is not negotiable by the model |
| affirmation | value-based, user-authored, absent without evidence |

A build that ships a lever above its cap has shipped a defect the evidence already predicted.

---

## 6. Execution model — LLM workers, and xdist on 316t

- **One LLM worker per module**, because the allowlist in each lane brief partitions cleanly by
  file. The only serialisation point is B1's interface freeze: lanes 2 and 3 wait for
  `docs/SARAH_INTERFACE_2026-11-16.md`, not for lane 1 to finish.
- **Tests run in parallel on py316t** (`-n auto`, 16 workers; xdist 3.8.0 installed
  2026-11-16). Each free-threaded worker reloads interpreter + conftest, so `-n auto` pays only
  once a file has enough tests to amortise ~2.5 s of startup — for a single two-test module,
  serial is faster (0.32 s vs 2.79 s, measured). Use `-n auto` on the `test_sarah_*.py` group,
  not on one tiny file.
- **A full-suite parallel crash is not a Sarah defect.** Engram `#1498` records the *whole* suite
  dying with `Windows fatal exception: stack overflow` at `-n 16` and again at `-n 8` (2026-10-20,
  on the then-production interpreter; a carried measurement, not re-run on 2026-11-16). The Sarah
  group is a handful of files and stays far below that scale, so `-n auto` there is safe; a
  full-suite `-n auto` run is **not** an acceptance command in this document. If a full-suite
  parallel run aborts, pin it incrementally (`--junitxml`, `-v`) — `-r` end-of-run output never
  prints on an abort.
- **A worker never edits a file outside its brief's allowlist**, and never the six generated
  lane instruction targets (`~/AGENTS.md`, `C:/Azazael/AGENTS.md`, `~/.config/kilo/AGENTS.md`,
  `~/.config/kilo/BEAM_AGENTS.md`, `~/.config/opencode/AGENTS.md`, `~/.codebuff/rules.md`) —
  those are generated by `tools/agent_orders_sync.py` from `docs/agent_orders/`.

---

## 7. Definition of done — commands, not adjectives

```bash
PY=C:/Azazael/.venvs/py316t/Scripts/python.exe

# 1. the whole Sarah suite, parallel, on production
$PY -m pytest tests/test_sarah_*.py -q -n auto --timeout=120          # expect RC=0

# 2. the package imports without the model stack present
$PY -c "import SARAH, SARAH.sensory, SARAH.affect; print('imports ok')"

# 3. the chain runs headless and emits telemetry
$PY -m SARAH --profile demo --steps 20 --json /tmp/sarah_run.json
$PY -c "import json;d=json.load(open('/tmp/sarah_run.json'));print(sorted({e['event'] for e in d['events']}))"

# 4. no unrequested demand increase anywhere in the run
$PY -c "import json;d=json.load(open('/tmp/sarah_run.json'));up=[e for e in d['events'] if e.get('direction')=='up'];print('increases:',len(up))"

# 5. the tree is clean of the forbidden shapes
grep -rnE 'sleep\(0\.01\)|streamlit|requests\.(get|post)' src/SARAH/ || echo "clean"
```

`#4` printing a non-zero count is not a failing test to be silenced — it is the design defect
this whole document exists to prevent.

---

## 8. Error capture (mandatory, #714/#716)

Record every error, near-miss and falsification at **encounter time** into
`state/bake_harvest_<agent>_<date>.jsonl` with schema
`{source, item_id, title, body, kind}`; `body >= 40 chars`; kinds:
`error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Do not defer to session end — reconstruction loses detail and over-weights what is still
salient. Validate: `tools/merge_bake_lane.py --lane <file> --apply`.

---

## 9. What this document does not decide

1. **Which sub-types ship in v1.** B0–B2 (profile + predictability + exit + sensory) is a
   defensible v1; all fifteen modules at once is how none of them get tested.
2. **Whether the spec fixes the profile model** — if it does, B1 is an adapter.
3. **Haptics** — M8's heartbeat and the vibrotactile lever are D/C-grade without hardware.
4. **Model budget for M2/M14** — a small model produces the generic trait-praise shape that
   backfires; that is a quality gate, not a preference.
5. **Who authors the affirmation** — this document assumes the user does, and B3 fails closed
   (`None`) rather than guessing.
