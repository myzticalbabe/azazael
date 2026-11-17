# SARAH — M1 Profile Interface (contract draft, 2026-11-16 build)

**Status: DRAFTED, NOT FROZEN.** This document was written 2026-11-17 by the
freebuff lane so lanes 2 and 3 have a named contract to code against. The B1
freeze verdict belongs to lane 1 (kilo, `Board-51707`); lane 1 owns `profile.py`
and this file, and nothing here should be read as that verdict having been
given. Until lane 1 says otherwise, treat this as the vocabulary actually
imported from `SARAH.profile`, which is the thing the tests assert.

Source of truth is code, not prose: `azazael/src/SARAH/profile.py`. This
document is a reading of it, verified by running the commands at the bottom.

---

## 1. The profile is eight axes, and eight is a promise

`SARAH.profile.AXES` is a tuple of exactly eight names in the order B1 states
them. Lanes 2 and 3 may rely on both the membership and the order.

| # | axis | low end | high end |
|---|------|---------|----------|
| 1 | `sensory_gain` | low sensitivity | high sensitivity / overload-prone |
| 2 | `processing_speed` | slow | fast |
| 3 | `attention_span` | short | long |
| 4 | `interoception` | low (signal hard to read) | high (signal clearly felt) |
| 5 | `masking_load` | low (little hidden effort) | high (heavy hidden effort) |
| 6 | `recovery_latency` | fast (returns quickly) | slow (needs long recovery) |
| 7 | `initiation_cost` | low (easy to start) | high (expensive to start) |
| 8 | `prediction_need` | low | high (needs announcement ahead of change) |

Every axis is a `float` in `[0.0, 1.0]` or `None`. There is no fifth state and
no free-text axis.

### Unknown is `None`, never `0.5`

An unmeasured axis is `None`, and `explain(axis)` returns
`"<axis>: not measured yet"`. A default of `0.5` is forbidden: it is
indistinguishable from a measurement, so downstream code cannot tell "we did
not measure this" from "we measured the middle", and the middle is exactly
where a wrong default hides. `__post_init__` rejects out-of-range floats
(`ValueError`) and non-numeric values (`TypeError`).

### Constructor surface

```python
Profile.from_signals(signals: dict[str, float | None], source: str = "probe") -> Profile
Profile.from_dict(data: dict) -> Profile          # filters unknowns, resolves aliases
profile.to_dict() -> dict[str, float | None]      # frozen 8 first, then extras
profile.explain(axis: str) -> str                 # one sentence, alias-tolerant
profile.axes() -> list[str]                       # the frozen 8, contract order
profile.all_axes() -> list[str]                   # the 8 + declared extras
```

`from_signals` is deterministic: no I/O, no model call. It resolves aliases,
ignores names from a different vocabulary (a caller bug is not a profile
crash), and re-validates after assignment so an out-of-range signal cannot
reach a profile. `Profile` is an alias of `SarahProfile`; there is one class
under two names, so B1's own smoke command resolves.

---

## 2. Pre-freeze spellings are aliases, not dead keys

The first build used five names that the contract does not. Three of them are
resolved on the way in and out; the other two are carried as declared extras
(§3). `AXIS_ALIASES`:

| pre-freeze name | contract name |
|---|---|
| `sustained_attention` | `attention_span` |
| `interoceptive_accuracy` | `interoception` |
| `initiation_threshold` | `initiation_cost` |

Aliases are applied in `from_signals`, `from_dict`, `explain`, and in the
clinical crosswalk's `seed_profile` / `merge`. Without that, a stored profile
or a stale table written in the old vocabulary would be filtered out as
unknown and the axis would read "not measured yet" while a value existed —
which is precisely how the mismatch stayed invisible.

---

## 3. Two extended axes are declared, not hidden

`EXTENDED_AXES = ("wm_span", "time_discrimination")`. They are outside the
freeze and stay outside it; they are listed here so nobody discovers them by
reading `to_dict()` and concludes the contract grew to ten.

- `wm_span` — working-memory span. Seeded by the crosswalk from F81.0
  (dyslexia) and F83 (dyspraxia); consumed by M10 `offload`.
- `time_discrimination` — duration perception. Seeded from F81.2
  (dyscalculia); consumed by M9 `affect/timeview`.

No contract axis measures what either of these measures, so dropping them
would lose the crosswalk's seeded values and the two modules that read them.
They are therefore carried, and `len(AXES) == 8` remains true.

---

## 4. The rest of B1's contract, as the contract states it

These two modules are named by B1 and **do not exist yet** (measured
2026-11-17: `src/SARAH/` holds `profile.py`, `telemetry.py`, and the
`sensory/`, `affect/`, `clinical/` package skeletons). The requirements below
are quoted so whoever writes them codes to the same promise.

- **`predict.packet(profile, next_n_steps) -> PredictabilityPacket`** with
  `what`, `when`, `how_long`, `what_next`, and `can_exit: True` — always true,
  never conditional on session state.
- **`exit.request(reason: str | None) -> ExitTicket`** and
  **`exit.assert_unscored(log)`**. Today the equivalent lives inside
  `profile.py` as `ExitPort.leave(reason) -> ExitTicket` and
  `ExitPort.assert_unscored(log)`; the module split is lane 1's. The rule the
  assertion enforces: an `exit_requested` event carries no `score`, no
  `rating`, and no `comment`.
- **The negative case B1 mandates:** a profile with `prediction_need` high
  produces *more* announcement beats and *fewer* simultaneous changes — never
  more stimulus. It cannot be tested until `predict.py` exists.

---

## 5. How this reading was verified

```bash
# from C:/Azazael/azazael, production interpreter
C:/Azazael/.venvs/py316t/Scripts/python.exe -u -m pytest \
    tests/test_sarah_profile.py tests/test_sarah_crosswalk.py -q --tb=short -r f --timeout=120
# 48 passed in 0.64s                                   (measured 2026-11-17, RC=0)

C:/Azazael/.venvs/py316t/Scripts/python.exe -c \
    "from SARAH.profile import Profile; p=Profile.from_signals({}); print(p.explain('sensory_gain'))"
# sensory_gain: not measured yet                        (measured 2026-11-17, RC=0)
```

`tests/test_sarah_profile.py` asserts the vocabulary itself: `AXES` equals the
contract tuple, `len(AXES) == 8`, every axis has a low/high meaning, the three
aliases resolve and the alias names are not themselves axes, unknown signals
are ignored, out-of-range values raise, `to_dict()` carries the frozen eight
first, and moving `prediction_need` moves no other axis.
