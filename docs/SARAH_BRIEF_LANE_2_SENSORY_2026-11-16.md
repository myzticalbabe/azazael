# #2268 — SARAH BRIEF 2: SENSORY SUBSTRATE (lane: freebuff)

| field | value |
| --- | --- |
| brief id | **#2268** (Engram record; the record and this file are one brief) |
| lane | **freebuff** |
| sole authority | yes — for lane 2 of Project Sarah only |
| HEAD pin | `2b5ef4c1` (2026-11-16) |
| expiry | **2026-11-20** — re-derive before starting after that date |
| parent design | `docs/PROJECT_SARAH_IMMERSION_UPGRADES_2026-11-16.md` (commit `2b5ef4c1`) |
| depends on | `#2267` lane 1, specifically `docs/SARAH_INTERFACE_2026-11-16.md` |
| interpreter | `C:/Azazael/.venvs/py316t/Scripts/python.exe` |

**Sole execution authority for its lane.** Briefs `#2267` and `#2269` are foreign here.
One lane, one brief, one worktree.

## Mission

Build the sensory substrate that makes immersion *tolerable* rather than maximal. This lane
implements the measured result that the **lowest**-rated XR condition was click-triggered spatial
audio (M = 2.97/5, 16 of 20 rating it low) and the **highest** was gradual multi-modal ramps with
optional vibrotactile/thermal (M = 4.43) — arXiv `2610.23833`.

Read parent doc §4 (M2, M3, M4, M5, M15) and §5 (levers and caps). The caps in §5 are code
requirements in this lane, not guidance.

## Dependency — read this before the first edit

You consume `SarahProfile` from `src/SARAH/profile.py` **read-only**, through
`docs/SARAH_INTERFACE_2026-11-16.md`. You must not modify `profile.py`.

**If that contract does not exist yet, stop and report the blocker by name.** Do not invent a
parallel profile and do not fork the dataclass into this package — a second profile is the exact
failure the substrate exists to prevent.

## Owned modules

| module | the rule that becomes code |
| --- | --- |
| **M2** Adaptive Pacing Governor | clamped to 120–165 wpm, 5–9 word chunks, gap scaled by `processing_speed`; may only **reduce** demand — there is no speed-up branch |
| **M3** Sensory Gain Mixer | one master control scales **all** modalities; a new sensory feature must declare its default before it ships; a feature that cannot be turned down does not land |
| **M4** Gradual-Transition Engine | every change ramps ≥ 400 ms; **never two modalities in the same tick**; every change announced one beat before it happens |
| **M5** Self-Pacing and Unlimited Time | no countdown exists unless the user asks; its pause must actually pause; XAUR 12a |
| **M15** Cross-Modal Redundancy | same content over text + audio + pictogram so one can be **off** — redundancy is not simultaneity |

## Turf — allowlist

```
src/SARAH/sensory/__init__.py
src/SARAH/sensory/pacing.py
src/SARAH/sensory/mixer.py
src/SARAH/sensory/transitions.py
src/SARAH/sensory/timer.py
src/SARAH/sensory/redundancy.py
tests/test_sarah_pacing.py
tests/test_sarah_mixer.py
tests/test_sarah_transitions.py
```

## Forbidden

- `src/SARAH/profile.py`, `predict.py`, `exit.py`, `offload.py`, `initiate.py` — lane 1 (`#2267`).
- `src/SARAH/affect/` — lane 3 (`#2269`).
- Any path outside the allowlist; other subsystems' tests.
- The six generated lane instruction targets — edit `docs/agent_orders/` source, never a copy.
- `MANDATES.md`, `SOP.md`, `git add -A`.

## Execution model — LLM workers and xdist

**Workers.** One LLM worker per owned module, in parallel: M2, M3, M4, M5 and M15 touch disjoint
files in the allowlist. M3 (the mixer) publishes the modality registry M4 and M15 read, so M3
lands first and the other four run alongside it. Nothing here blocks on lane 3.

**xdist is per-environment, measured 2026-11-16.** `-n auto` is opt-in and is **not** in the
committed addopts: a committed flag one interpreter cannot parse kills the run at argument
parsing, before collection, so nothing is reported at all.

| interpreter | xdist | how to run tests here |
| --- | --- | --- |
| `py316t` (production) | **absent** — `ModuleNotFoundError: No module named 'xdist'` | `-m pytest ... -q`, **never** with `-n` |
| `py315t` (GIL sidecar) | **3.8.0**, pytest 9.2.0 | `-m pytest ... -q -n auto` |

A command that dies on an unrecognised `-n` is a wrong command, not a red suite.

## Acceptance as commands

```bash
PY=C:/Azazael/.venvs/py316t/Scripts/python.exe
$PY -m pytest tests/test_sarah_pacing.py tests/test_sarah_mixer.py tests/test_sarah_transitions.py -q
```

The tests must assert, not describe:

1. **Pacing** — the clamp holds at both ends (120 and 165), and a "good" reading produces no
   faster output than a "poor" one.
2. **Transitions** — every ramp ≥ 400 ms; no recorded tick changed two modalities.
3. **Mixer** — the master control scales every declared modality; every feature registers a
   default; a feature registered with no turn-down path is rejected.
4. **Timer** — no timer is constructed without an explicit request; `pause()` emits no ticks.
5. **Redundancy** — with one channel switched off, the content still arrives by another.

Paste the pytest summary line, not a claim about it.

## Do not build

- A dyslexia font as a fix — meta-analysis 15 studies, N = 688, **g = −0.04, p = .5**. Ship
  letter-spacing and line-height instead (extra-large spacing improved speed and errors, 2021).
- Coloured overlays as treatment (Griffiths 2016; Suttle 2018 — not endorsable).
- VR-first anything: VR biofeedback was **no better than 2D** in a 2025 RCT.
- Flicker above 3 Hz, parallax, autoplay motion, abrupt light change.
- A single "accessibility mode" checkbox standing in for the eight axes.
- Surprise spatial panning — spatial audio is **user-initiated only**.

## Stop rules

- If `#2267`'s contract is missing, blocked, or names different axes, **stop and report**.
- A gate rejection is resolved with precision, never with `ALLOW_*`.
- One diagnostic pass, then report the command and its output.

## ERROR CAPTURE (mandatory, #714/#716)

Record every error, near-miss and falsification at **ENCOUNTER TIME** into
`state/bake_harvest_freebuff_2026-11-16.jsonl` with schema `{source, item_id, title, body, kind}`;
body ≥ 40 chars; kinds: `error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Validate: `tools/merge_bake_lane.py --lane <file> --apply`.

## Evidence via tools

Every harvest row and acceptance proof cites the tool invocation that produced it (command +
outcome digest). A row without provenance is narrative, not evidence.

## Handoff

HEAD sha; each module with its command and output; the caps you enforced and **where in code**;
what you tried that failed and why; the expiry date.
