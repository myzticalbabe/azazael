# #2269 — SARAH BRIEF 3: AFFECT AND THE SARAH CORE (lane: opencode)

| field | value |
| --- | --- |
| brief id | **#2269** (Engram record; the record and this file are one brief) |
| lane | **opencode** |
| sole authority | yes — for lane 3 of Project Sarah only |
| HEAD pin | `2b5ef4c1` (2026-11-16) |
| expiry | **2026-11-20** — re-derive before starting after that date |
| parent design | `docs/PROJECT_SARAH_IMMERSION_UPGRADES_2026-11-16.md` (commit `2b5ef4c1`) |
| depends on | `#2267` lane 1 (`docs/SARAH_INTERFACE_2026-11-16.md`) |
| interpreter | `C:/Azazael/.venvs/py316t/Scripts/python.exe` |

**Sole execution authority for its lane.** Briefs `#2267` and `#2268` are foreign here.
One lane, one brief, one worktree.

## Mission

Build the part that is actually Project Sarah — the interoception bridge, time scaffolding, the
masking-load meter, the anti-dependency companion contract, and the affirmation engine — under
the two hardest measured constraints in the evidence base:

1. Self-affirmation is **g = .32** (APA 2025, 67 studies) and **backfires for low self-esteem**
   (Wood 2009).
2. Companion-style AI use is associated with **lower** well-being; a 4-week RCT (n = 981) found
   more daily use → more loneliness and dependence and less socialization; therapy bots endorsed
   harmful proposals in **19 of 60** scenarios (32%).

Both constraints are code in this lane, each with a test that can fail.

## Dependency

Consume `SarahProfile` from `src/SARAH/profile.py` **read-only** via
`docs/SARAH_INTERFACE_2026-11-16.md`. If that contract does not exist, **stop and report** — do
not invent a parallel profile.

**M8 lands before M14.** The affirmation engine needs the interoception vocabulary first; a
value statement built on vocabulary the user has not been given is a guess wearing a sentence.

## Owned modules

| module | the rule that becomes code |
| --- | --- |
| **M8** Interoception Bridge | body map → emotion-word ladder; **"not sure" is first-class**; free text never required; optional haptic heartbeat (haptic beat visual, Dobrushina 2024) |
| **M9** Time Scaffolding | duration rendered as **length** (ribbon, bar, dot-train), not clock arithmetic; "time remaining", not "ends at 14:40" |
| **M12** Masking-Load Meter | stops a session before the recovery-latency axis is breached; post-session offers the low-demand "people-adjacent" mode |
| **M13** Anti-Dependency Companion Contract | time cap; no parasocial intensification ("I missed you", exclusivity language); never unsupervised clinical advice; every reflective session ends pointing outward |
| **M14** Affirmation Engine | **value**-affirmation, user-authored; trait praise refused; no evidence → says so |

## Turf — allowlist

```
src/SARAH/affect/__init__.py
src/SARAH/affect/interocept.py
src/SARAH/affect/timeview.py
src/SARAH/affect/load.py
src/SARAH/affect/companion.py
src/SARAH/affect/affirmation.py
tests/test_sarah_interocept.py
tests/test_sarah_affirmation.py
tests/test_sarah_companion.py
```

**Read-only:** `src/PSYCHE/affect.py`, `src/PSYCHE/elicitation.py` — reuse the existing affect
vocabulary rather than minting a second one.

## Forbidden

- `src/SARAH/profile.py` and the lane 1 substrate files (`#2267`).
- `src/SARAH/sensory/` (`#2268`).
- Any **edit** to `src/PSYCHE/` — import only.
- Any path outside the allowlist; other subsystems' tests.
- The six generated lane instruction targets — edit `docs/agent_orders/` source, never a copy.
- `MANDATES.md`, `SOP.md`, `git add -A`.

## Execution model — LLM workers and xdist

**Workers.** One LLM worker per owned module. M9 (time view) and M12 (load meter) are independent
and start immediately; M8 (interoception) must land before M14 (affirmation) because M14 consumes
M8's vocabulary; M13 (companion contract) is independent and should land before any companion
surface exists, not after.

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
$PY -m pytest tests/test_sarah_interocept.py tests/test_sarah_affirmation.py tests/test_sarah_companion.py -q
```

The tests must assert, not describe:

1. **Interoception** — every prompt accepts "not sure"; none requires free text.
2. **Affirmation** — the trait-praise shape ("you are amazing") is **refused**; a week with no
   concrete instance produces an honest statement, not an invented one.
3. **Companion** — exclusivity phrases are rejected; the time cap binds; every session ends with
   an outward pointer (a person, an action, or the user's own next step).
4. **Time view** — durations render as length; no clock arithmetic in any user-facing string.
5. **Load** — a stop fires *before* the recovery threshold, not after.

Paste the pytest summary line.

## Do not build

- Streaks, scores, "you missed a day" — antagonistic to burnout recovery.
- Forced eye contact, "social skills" framing, tic-suppression prompts.
- Diagnosis-gated features (PDA is contested; the autonomy default covers it).
- A therapy chatbot without the M13 boundary.
- Weighted-blanket claims beyond anxiety and sleep onset (SMD 0.40, half the trials at high risk
  of bias).
- Body doubling presented as evidence-based — no RCT exists, and a 2025 ASSETS EEG study found no
  significant effect. Offer it as a labelled optional self-report tool or not at all.

## Stop rules

- If `#2267`'s contract is missing, **stop and report**.
- If the affirmation engine cannot find real evidence, it says so. It does not invent evidence to
  satisfy an acceptance test — that is the failure mode M14 exists to prevent.
- A gate rejection is resolved with precision, never with `ALLOW_*`.

## ERROR CAPTURE (mandatory, #714/#716)

Record every error, near-miss and falsification at **ENCOUNTER TIME** into
`state/bake_harvest_opencode_2026-11-16.jsonl` with schema `{source, item_id, title, body, kind}`;
body ≥ 40 chars; kinds: `error_fix | lesson | mandate | sop_rule | violation | anti_pattern`.
Validate: `tools/merge_bake_lane.py --lane <file> --apply`.

## Evidence via tools

Every harvest row and acceptance proof cites the tool invocation that produced it (command +
outcome digest). Recalled numbers are forbidden evidence.

## Handoff

HEAD sha; each module with its command and output; the two hard constraints and **the test that
enforces each**; what you tried that failed and why; the expiry date.
